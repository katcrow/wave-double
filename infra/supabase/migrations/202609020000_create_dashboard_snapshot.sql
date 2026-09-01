-- Story 1.8: 대시보드 스냅샷 조회 API.
-- logical_runs/runs에 RLS를 활성화하고 공개 SELECT policy를 추가한다(1.9의 /runs 이력 화면이 직접 읽는 대상).
-- candidates/candidate_source_contrib는 202609011800에서 이미 RLS enable된 채 policy가 없어(deny-all) 그대로 두고,
-- get_dashboard_snapshot()만 security definer로 그 잠긴 테이블을 내부적으로 집계(count)해 후보 원본 행은 절대 반환하지 않는다
-- (리뷰 발견: 4개 테이블 모두를 공개하면 candidate ticker 상세 행이 RPC를 우회해 그대로 노출된다).
begin;

alter table public.logical_runs enable row level security;
alter table public.runs enable row level security;

drop policy if exists logical_runs_public_select on public.logical_runs;
create policy logical_runs_public_select on public.logical_runs
  for select to anon, authenticated using (true);

drop policy if exists runs_public_select on public.runs;
create policy runs_public_select on public.runs
  for select to anon, authenticated using (true);

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
  has_complete boolean := false;
  has_latest boolean := false;
begin
  -- complete_snapshot: 전역에서 published_at이 가장 최근인 logical_run의 current_complete_run_id 단일 run_id (AD-13).
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
    end if;
  end if;

  -- latest_attempt: 상태 무관, 전역에서 started_at이 가장 최근인 단일 run_id (AD-13).
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
        )
      )
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
    'available_partial_sections', case when has_complete then jsonb_build_array('candidates') else '[]'::jsonb end,
    'missing_sections', case when has_complete
      then jsonb_build_array('tags', 'supply_3day', 'market_supply', 'outcome_tracking')
      else jsonb_build_array('candidates', 'tags', 'supply_3day', 'market_supply', 'outcome_tracking') end,
    'unprocessed_items', case when has_latest then latest_run.unprocessed_count else 0 end
  );
end;
$$;

comment on function public.get_dashboard_snapshot() is
  'Story 1.8: 대시보드 스냅샷 조회 계약. complete_snapshot(최신 발행 run)과 latest_attempt(최신 attempt, 상태 무관)를 분리 반환하며, Epic 1 시점에는 candidates section만 채운다(AD-13).';

revoke execute on function public.get_dashboard_snapshot() from public;
grant execute on function public.get_dashboard_snapshot() to anon, authenticated, service_role;

commit;
