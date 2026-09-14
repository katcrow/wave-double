-- Supabase 무료 플랜(500MB) 용량 관리. 20분 간격 intraday 전환(202609141700)으로 하루
-- 배치 실행 횟수가 약 2배(37회/일)로 늘면서, attempt-scoped 테이블(candidates 계열)이
-- 예전보다 훨씬 빠르게 쌓이게 됐다.
--
-- 삭제 가능/금지 여부는 실제 조회 경로를 직접 추적해 확정했다(2026-09-14 조사):
--   - 배치 이력 화면(apps/web/app/runs/page.tsx)은 runs를 최근 100건만 조회한다.
--   - get_dashboard_snapshot()의 latest_attempt는 logical_runs 포인터가 아니라
--     `runs order by started_at desc limit 1`로 직접 찾는다(활성 run 판정에
--     active_attempt_run_id를 전혀 참조하지 않는다).
--   - get_today_disappeared_candidates/sync_vanished_tags/get_candidate_evidence/
--     get_market_supply는 전부 단일 run_id(오늘/최신 canonical)만 받는다 -- rolling
--     window 없음. 과거 attempt의 candidates류를 지워도 이 기능들엔 영향이 없다.
--   - candidate_outcome_win_rate_pf 등 승률/PF 뷰 체인은 candidate_outcome 전체 기간을
--     날짜 필터 없이 집계한다 -- outcome_events/outcome_observations/candidate_outcome/
--     outcome_strategy_rules(+history)/bias_events/daily_ohlcv/dispatch_request는
--     삭제 대상에서 절대 제외한다.
--
-- logical_runs.active_attempt_run_id는 "그 정확한 logical_run_key로 다시 start_attempt가
-- 들어올 때만" 의미가 있다(재시도 supersede 판정). intraday는 슬롯마다(날짜+분) 별도
-- logical_runs 행이라 하루만 지나도 같은 key로 재시도가 들어올 일이 없다 -- 그런데도 이
-- 컬럼을 무조건 보존 대상에 넣으면(단순 FK 회피 목적으로) 완료된 intraday run은 사실상
-- 영원히 이 포인터가 자기 자신을 가리켜 하나도 못 지우게 된다. 그래서 이 컬럼은 "삭제
-- 대상 run을 참조 중이면 먼저 NULL로 비우고" 지운다 -- canonical_success_run_id(발행
-- replay 판정)/current_complete_run_id(get_dashboard_snapshot·get_candidate_evidence·
-- get_market_supply가 실제로 참조)/latest_partial_run_id(부분발행 표시)는 삭제 대상에서
-- 항상 제외해 그대로 보존한다.
begin;

create or replace function public.purge_old_attempt_data(p_retention_days integer default 7)
returns jsonb
language plpgsql
security definer
set search_path = pg_catalog, public
as $$
declare
  v_cutoff timestamptz;
  v_protected_run_ids uuid[];
  v_target_run_ids uuid[];
  v_cleared_active_pointers integer := 0;
  v_deleted_tags integer := 0;
  v_deleted_supply3d integer := 0;
  v_deleted_source_contrib integer := 0;
  v_deleted_candidates integer := 0;
  v_deleted_market_supply integer := 0;
  v_updated_outbox integer := 0;
  v_deleted_runs integer := 0;
begin
  if p_retention_days <= 0 then
    raise exception using message = 'p_retention_days must be positive';
  end if;
  v_cutoff := now() - make_interval(days => p_retention_days);

  -- canonical_success_run_id/current_complete_run_id/latest_partial_run_id만 진짜
  -- 보존 대상이다(위 설명 참고). active_attempt_run_id는 여기 포함하지 않는다.
  select array_agg(run_id) into v_protected_run_ids
  from (
    select canonical_success_run_id as run_id from public.logical_runs where canonical_success_run_id is not null
    union
    select current_complete_run_id from public.logical_runs where current_complete_run_id is not null
    union
    select latest_partial_run_id from public.logical_runs where latest_partial_run_id is not null
  ) protected;

  select array_agg(run_id) into v_target_run_ids
  from public.runs
  where started_at < v_cutoff
    and (v_protected_run_ids is null or not (run_id = any(v_protected_run_ids)));

  if v_target_run_ids is null then
    return jsonb_build_object('cutoff', v_cutoff, 'purged_runs', 0);
  end if;

  update public.logical_runs set active_attempt_run_id = null
    where active_attempt_run_id = any(v_target_run_ids);
  get diagnostics v_cleared_active_pointers = row_count;

  delete from public.candidate_tags where attempt_run_id = any(v_target_run_ids);
  get diagnostics v_deleted_tags = row_count;

  delete from public.supply_3day where attempt_run_id = any(v_target_run_ids);
  get diagnostics v_deleted_supply3d = row_count;

  delete from public.candidate_source_contrib where attempt_run_id = any(v_target_run_ids);
  get diagnostics v_deleted_source_contrib = row_count;

  delete from public.candidates where attempt_run_id = any(v_target_run_ids);
  get diagnostics v_deleted_candidates = row_count;

  delete from public.market_supply where attempt_run_id = any(v_target_run_ids);
  get diagnostics v_deleted_market_supply = row_count;

  update public.dispatch_outbox set run_id = null where run_id = any(v_target_run_ids);
  get diagnostics v_updated_outbox = row_count;

  delete from public.runs where run_id = any(v_target_run_ids);
  get diagnostics v_deleted_runs = row_count;

  return jsonb_build_object(
    'cutoff', v_cutoff,
    'purged_runs', v_deleted_runs,
    'purged_candidates', v_deleted_candidates,
    'purged_candidate_source_contrib', v_deleted_source_contrib,
    'purged_candidate_tags', v_deleted_tags,
    'purged_supply_3day', v_deleted_supply3d,
    'purged_market_supply', v_deleted_market_supply,
    'unlinked_dispatch_outbox', v_updated_outbox,
    'cleared_active_attempt_pointers', v_cleared_active_pointers
  );
end;
$$;

comment on function public.purge_old_attempt_data(integer) is
  '무료 플랜 용량 관리(2026-09-14): retention_days(기본 7일)보다 오래됐고 logical_runs의 canonical_success_run_id/current_complete_run_id/latest_partial_run_id 어디에도 걸리지 않는 run과 그 run의 candidates/candidate_source_contrib/candidate_tags/supply_3day/market_supply를 지운다. active_attempt_run_id가 삭제 대상 run을 가리키면 먼저 NULL로 비운다(get_dashboard_snapshot은 이 컬럼을 안 쓰고 runs.started_at으로 최신 attempt를 직접 찾는다 -- 슬롯별 1회성인 intraday에서 이 컬럼을 보존 대상에 넣으면 완료된 run이 영원히 안 지워진다). outcome_events/outcome_observations/candidate_outcome/outcome_strategy_rules(+history)/bias_events/logical_runs/daily_ohlcv/dispatch_request는 절대 건드리지 않는다. GitHub Actions nightly-cleanup.yml이 매일 KST 21:00에 service_role로 호출한다.';

revoke execute on function public.purge_old_attempt_data(integer) from public, anon, authenticated;
grant execute on function public.purge_old_attempt_data(integer) to service_role;

commit;
