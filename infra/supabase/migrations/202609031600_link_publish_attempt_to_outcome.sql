-- Story 3.3: close 발행 트랜잭션에 outcome 생성을 연결한다(AD-20).
-- 202609021700의 publish_attempt(3-arg)/get_dashboard_snapshot()를 base로 create or replace한다
-- (같은 시그니처이므로 기존 revoke/grant는 그대로 유효).
-- publish_attempt는 batch_kind='close'일 때만, 기존 단일 트랜잭션 안에서 이번 attempt의 활성
-- candidate_tags를 (ticker,strategy)별로 순회하며 emit_open_command(Story 3.2)를 호출하고,
-- 완료 후 stage_status.outcome_tracking을 'success'로 갱신한다. 하나라도 예외를 내면 함수 전체가
-- rollback되어 candidate/tag 발행도 함께 취소된다. premarket/intraday는 이 로직을 건너뛴다(AD-15).
begin;

create or replace function public.publish_attempt(p_run_id uuid, p_fence_token bigint, p_lease_token uuid) returns jsonb
language plpgsql security definer set search_path = public as $$
declare
  r public.runs;
  logical_row public.logical_runs;
  tag_row record;
begin
  select * into r from runs where run_id = p_run_id; if not found then raise exception using message = 'RUN_NOT_FOUND'; end if;
  perform pg_advisory_xact_lock(hashtextextended(r.logical_run_key, 0));
  select * into r from runs where run_id = p_run_id for update; select * into logical_row from logical_runs where logical_run_key = r.logical_run_key for update;
  if logical_row.active_attempt_run_id is distinct from p_run_id or r.fence_token <> p_fence_token or r.lease_token <> p_lease_token or r.lease_expires_at <= now() then raise exception using message = 'STALE_FENCE_OR_LEASE'; end if;
  if r.status <> 'ready_to_publish' or r.stage_status->>'candidates' <> 'success' then raise exception using message = 'PUBLISH_GUARD_FAILED'; end if;
  if r.stage_status->>'tags' is distinct from 'success' then raise exception using message = 'TAGS_STAGE_NOT_COMPLETE'; end if;
  if exists (select 1 from candidates c where c.attempt_run_id = p_run_id and not exists (select 1 from candidate_source_contrib s where s.candidate_id = c.candidate_id and s.attempt_run_id = c.attempt_run_id)) or exists (select 1 from (select candidate_id, attempt_run_id, sum(contribution_weight) as total from candidate_source_contrib where attempt_run_id = p_run_id group by candidate_id, attempt_run_id) s where s.total <> 1) then raise exception using message = 'PUBLISH_PROVENANCE_GUARD_FAILED'; end if;
  if logical_row.canonical_success_run_id is not null then raise exception using message = 'CANONICAL_ALREADY_PUBLISHED'; end if;

  if logical_row.batch_kind = 'close' then
    for tag_row in
      select c.ticker as ticker, t.strategy as strategy
        from candidate_tags t
        join candidates c on c.candidate_id = t.candidate_id and c.attempt_run_id = t.attempt_run_id
        where t.attempt_run_id = p_run_id and t.status = 'active'
    loop
      perform public.emit_open_command(r.logical_run_key, tag_row.ticker, tag_row.strategy);
    end loop;
    update runs set stage_status = jsonb_set(stage_status, array['outcome_tracking'], to_jsonb('success'::text))
      where run_id = p_run_id;
  end if;

  update runs set status = 'published', finished_at = now() where run_id = p_run_id;
  update logical_runs set active_attempt_run_id = null, current_complete_run_id = p_run_id, canonical_success_run_id = case when batch_kind = 'close' then p_run_id else null end, published_at = now() where logical_run_key = r.logical_run_key;
  return jsonb_build_object('run_id', p_run_id, 'status', 'published', 'canonical_success_run_id', case when logical_row.batch_kind = 'close' then p_run_id else null end);
end $$;

create or replace function public.get_dashboard_snapshot()
returns jsonb
language plpgsql
security definer
stable
set search_path = public
as $$
declare
  complete_logical public.logical_runs%rowtype;
  complete_run public.runs%rowtype;
  latest_run public.runs%rowtype;
  latest_logical public.logical_runs%rowtype;
  candidate_count integer := 0;
  tag_count integer := 0;
  open_count integer := 0;
  has_complete boolean := false;
  has_latest boolean := false;
  has_outcome_tracking boolean := false;
begin
  select * into complete_logical
    from logical_runs
    where current_complete_run_id is not null
    order by published_at desc nulls last, logical_run_key desc
    limit 1;

  if complete_logical.logical_run_key is not null then
    select * into complete_run from runs where run_id = complete_logical.current_complete_run_id;
    if complete_run.run_id is not null then
      has_complete := true;
      select count(*) into candidate_count from candidates where attempt_run_id = complete_run.run_id;
      select count(*) into tag_count from candidate_tags where attempt_run_id = complete_run.run_id;
      has_outcome_tracking := complete_logical.batch_kind = 'close' and complete_run.stage_status->>'outcome_tracking' = 'success';
      if has_outcome_tracking then
        select count(*) into open_count
          from outcome_events
          where logical_run_key = complete_run.logical_run_key and command_type = 'OPEN';
      end if;
    end if;
  end if;

  select * into latest_run from runs order by started_at desc, run_id desc limit 1;
  if latest_run.run_id is not null then
    has_latest := true;
    select * into latest_logical from logical_runs where logical_run_key = latest_run.logical_run_key;
  end if;

  return jsonb_build_object(
    'no_snapshot', not has_complete,
    'result_code', case when has_complete then 'OK' else 'NO_SNAPSHOT' end,
    'complete_snapshot', case when not has_complete then null else jsonb_build_object(
      'logical_run_key', complete_run.logical_run_key,
      'run_id', complete_run.run_id,
      'trading_day', complete_logical.trading_day,
      'batch_kind', complete_logical.batch_kind,
      'published_at', complete_logical.published_at,
      'sections', jsonb_build_object(
        'candidates', jsonb_build_object(
          'candidate_count', candidate_count,
          'truncated_count', complete_run.truncated_count,
          'original_count', complete_run.original_count,
          'excluded_count', complete_run.excluded_count
        ),
        'tags', jsonb_build_object(
          'tag_count', tag_count
        )
      ) || case when has_outcome_tracking then jsonb_build_object(
        'outcome_tracking', jsonb_build_object(
          'open_count', open_count
        )
      ) else '{}'::jsonb end
    ) end,
    'latest_attempt', case when not has_latest then null else jsonb_build_object(
      'run_id', latest_run.run_id,
      'logical_run_key', latest_run.logical_run_key,
      'trading_day', latest_logical.trading_day,
      'batch_kind', latest_logical.batch_kind,
      'status', latest_run.status,
      'trigger', latest_run.trigger,
      'started_at', latest_run.started_at,
      'finished_at', latest_run.finished_at,
      'stage_status', latest_run.stage_status,
      'unprocessed_count', latest_run.unprocessed_count,
      'truncated_count', latest_run.truncated_count,
      'original_count', latest_run.original_count,
      'excluded_count', latest_run.excluded_count
    ) end,
    'latest_partial_run_id', case when has_latest then latest_logical.latest_partial_run_id else null end,
    'available_partial_sections', case when has_complete then
        (case when has_outcome_tracking then jsonb_build_array('candidates', 'tags', 'outcome_tracking') else jsonb_build_array('candidates', 'tags') end)
      else '[]'::jsonb end,
    'missing_sections', case when has_complete then
        (case when has_outcome_tracking
          then jsonb_build_array('supply_3day', 'market_supply')
          else jsonb_build_array('supply_3day', 'market_supply', 'outcome_tracking') end)
      else jsonb_build_array('candidates', 'tags', 'supply_3day', 'market_supply', 'outcome_tracking') end,
    'unprocessed_items', case when has_latest then latest_run.unprocessed_count else 0 end
  );
end;
$$;

comment on function public.get_dashboard_snapshot() is
  'Story 1.8 + Story 2.5 + Story 3.3: 대시보드 스냅샷 조회 계약. complete_snapshot과 latest_attempt를 분리 반환하며, close 완료 attempt의 outcome_tracking(OPEN 발행 건수)을 반영한다(AD-13).';

commit;
