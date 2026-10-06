-- 2026-10-06: close 발행에서 당일 종가(daily_ohlcv)가 없는 태그 종목은 진입(OPEN)만 건너뛰고
-- 나머지 발행은 계속한다. 이전에는 emit_open_command의 MISSING_DAILY_OHLCV_CLOSE 예외가
-- publish_attempt 전체를 rollback해(Story 3.3/AD-20) 종일 거래정지 종목 하나 때문에 그날 close의
-- 후보·태그·다른 종목 진입·성과 추적이 모두 실패했다.
-- emit_open_command 자체의 계약(종가 부재 시 예외)은 그대로 두고, 호출 전에 publish_attempt가
-- 종가 존재를 확인한다. 건너뛴 종목은 반환값 skipped_open_commands에 남긴다.
-- 본문은 202610060200_catch_up_outcome_tracking_days.sql과 동일하고 태그 루프와 반환값만 바뀐다.
begin;

create or replace function public.publish_attempt(p_run_id uuid, p_fence_token bigint, p_lease_token uuid)
returns jsonb
language plpgsql
security definer
set search_path = public
as $$
declare
  r public.runs;
  logical_row public.logical_runs;
  tag_row record;
  track_row record;
  day_row record;
  v_day_result jsonb;
  suspended_transitions jsonb := '[]'::jsonb;
  tp_sl_transitions jsonb := '[]'::jsonb;
  skipped_open_commands jsonb := '[]'::jsonb;
begin
  select * into r from runs where run_id = p_run_id;
  if not found then raise exception using message = 'RUN_NOT_FOUND'; end if;
  perform pg_advisory_xact_lock(hashtextextended(r.logical_run_key, 0));
  select * into r from runs where run_id = p_run_id for update;
  select * into logical_row from logical_runs where logical_run_key = r.logical_run_key for update;
  if logical_row.active_attempt_run_id is distinct from p_run_id
     or r.fence_token <> p_fence_token or r.lease_token <> p_lease_token
     or r.lease_expires_at <= now() then
    raise exception using message = 'STALE_FENCE_OR_LEASE';
  end if;
  if r.status <> 'ready_to_publish' or r.stage_status->>'candidates' <> 'success' then
    raise exception using message = 'PUBLISH_GUARD_FAILED';
  end if;

  if r.stage_status->>'tags' is distinct from 'success' then
    raise exception using message = 'TAGS_STAGE_NOT_COMPLETE';
  end if;

  if coalesce(r.stage_status->>'supply_3day', 'pending') in ('pending', 'running') then
    raise exception using message = 'SUPPLY_3DAY_STAGE_NOT_COMPLETE';
  end if;
  if coalesce(r.stage_status->>'market_supply', 'pending') in ('pending', 'running') then
    raise exception using message = 'MARKET_SUPPLY_STAGE_NOT_COMPLETE';
  end if;

  if exists (
    select 1 from candidates c
    where c.attempt_run_id = p_run_id
      and not exists (
        select 1 from candidate_source_contrib s
        where s.candidate_id = c.candidate_id and s.attempt_run_id = c.attempt_run_id
      )
  ) or exists (
    select 1 from (
      select candidate_id, attempt_run_id, sum(contribution_weight) as total
      from candidate_source_contrib where attempt_run_id = p_run_id
      group by candidate_id, attempt_run_id
    ) s where s.total <> 1
  ) then
    raise exception using message = 'PUBLISH_PROVENANCE_GUARD_FAILED';
  end if;
  if logical_row.canonical_success_run_id is not null then
    raise exception using message = 'CANONICAL_ALREADY_PUBLISHED';
  end if;

  if logical_row.batch_kind = 'close' then
    for tag_row in
      select c.ticker as ticker, t.strategy as strategy
      from candidate_tags t
      join candidates c on c.candidate_id = t.candidate_id and c.attempt_run_id = t.attempt_run_id
      where t.attempt_run_id = p_run_id and t.status = 'active' and t.strategy <> 'I'
    loop
      -- 당일 종가가 없는 종목(종일 거래정지 등)은 진입가를 정할 수 없으므로 그 종목만 건너뛴다.
      -- emit_open_command는 여전히 MISSING_DAILY_OHLCV_CLOSE로 거부하지만, 한 종목 때문에
      -- 후보/태그/다른 종목 진입까지 포함한 close 발행 전체가 rollback되지 않게 여기서 거른다.
      if not exists (
        select 1 from public.daily_ohlcv d
        where d.ticker = tag_row.ticker and d.trading_day = logical_row.trading_day and d.close is not null
      ) then
        skipped_open_commands := skipped_open_commands || jsonb_build_array(jsonb_build_object(
          'ticker', tag_row.ticker, 'strategy', tag_row.strategy, 'reason', 'MISSING_DAILY_OHLCV_CLOSE'
        ));
        continue;
      end if;
      perform public.emit_open_command(r.logical_run_key, tag_row.ticker, tag_row.strategy);
    end loop;

    -- 종료되지 않은 outcome마다 아직 관측되지 않은 거래일(진입일 ~ 오늘)을 날짜순으로 처리한다.
    -- close가 publish되지 못한 날이나 일봉이 늦게 채워진 날도 다음 close에서 소급된다.
    for track_row in
      select outcome_id, ticker, entry_date from public.candidate_outcome
      where status not in ('TP', 'SL', 'TIMEOUT', 'DELISTED')
      order by outcome_id
      for update
    loop
      for day_row in
        select d.trading_day
        from public.daily_ohlcv d
        where d.ticker = track_row.ticker
          and d.trading_day >= track_row.entry_date
          and d.trading_day <= logical_row.trading_day
          and not exists (
            select 1 from public.outcome_observations ob
            where ob.outcome_id = track_row.outcome_id
              and ob.evaluation_trading_day = d.trading_day
          )
        order by d.trading_day
      loop
        v_day_result := public.track_outcome_day(r.logical_run_key, track_row.outcome_id, day_row.trading_day);
        if v_day_result->'suspended' is not null and jsonb_typeof(v_day_result->'suspended') = 'object' then
          suspended_transitions := suspended_transitions || jsonb_build_array(v_day_result->'suspended');
        end if;
        if v_day_result->'tp_sl' is not null and jsonb_typeof(v_day_result->'tp_sl') = 'object' then
          tp_sl_transitions := tp_sl_transitions || jsonb_build_array(v_day_result->'tp_sl');
          exit;
        end if;
      end loop;
    end loop;

    update runs set stage_status = jsonb_set(stage_status, array['outcome_tracking'], to_jsonb('success'::text))
    where run_id = p_run_id;
  end if;

  update runs set status = 'published', finished_at = now() where run_id = p_run_id;
  update logical_runs set active_attempt_run_id = null, current_complete_run_id = p_run_id,
    canonical_success_run_id = case when batch_kind = 'close' then p_run_id else null end,
    published_at = now() where logical_run_key = r.logical_run_key;
  return jsonb_build_object(
    'run_id', p_run_id, 'status', 'published',
    'canonical_success_run_id', case when logical_row.batch_kind = 'close' then p_run_id else null end,
    'suspended_transitions', suspended_transitions, 'tp_sl_transitions', tp_sl_transitions,
    'skipped_open_commands', skipped_open_commands
  );
end $$;

commit;
