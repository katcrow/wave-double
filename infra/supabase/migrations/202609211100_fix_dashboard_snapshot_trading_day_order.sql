-- get_dashboard_snapshot()의 complete_snapshot 선정 기준이 published_at만 보고 trading_day를
-- 보지 않아서, 과거 trading_day의 logical_run이 나중에(재시도/백필로) publish_attempt를 통과해
-- published_at이 갱신되면 그 published_at이 당일 진짜 최신 complete run보다 최근으로 잡혀
-- complete_snapshot이 과거 거래일로 되돌아가는 결함이 있었다.
--
-- 실사례(2026-09-21): close:2026-09-18이 전략 I 태그 때문에 publish_attempt에서 계속
-- 롤백되다가(202609211000 패치로 원인 수정) 오늘 09:07 KST에 뒤늦게 재발행되면서
-- published_at이 오늘자 intraday:2026-09-21:08:30의 published_at(08:31 KST)보다 늦어졌다.
-- 그 결과 get_dashboard_snapshot()이 trading_day=2026-09-18인 close 발행을 오늘자보다
-- "더 최신"으로 골라, 프론트엔드 "오늘의 후보"가 금요일 후보(전략 I의 금요일 오후 잔존 태그
-- 포함)를 그대로 보여주는 문제로 이어졌다.
--
-- 수정: trading_day를 1순위 정렬 기준으로 삼아, 과거 거래일의 재발행이 당일 실제 최신
-- complete run을 절대 밀어낼 수 없게 한다.
begin;

create or replace function public.get_dashboard_snapshot() returns jsonb
language plpgsql stable security definer set search_path = public as $$
DECLARE
  complete_logical public.logical_runs%rowtype;
  complete_run public.runs%rowtype;
  latest_run public.runs%rowtype;
  latest_logical public.logical_runs%rowtype;
  candidate_count integer := 0;
  has_complete boolean := false;
  has_latest boolean := false;
BEGIN
  SELECT * INTO complete_logical
    FROM logical_runs
    WHERE current_complete_run_id IS NOT NULL
    ORDER BY trading_day DESC, published_at DESC NULLS LAST, logical_run_key DESC
    LIMIT 1;

  IF complete_logical.logical_run_key IS NOT NULL THEN
    SELECT * INTO complete_run FROM runs WHERE run_id = complete_logical.current_complete_run_id;
    IF complete_run.run_id IS NOT NULL THEN
      has_complete := true;
      SELECT count(*) INTO candidate_count FROM candidates WHERE attempt_run_id = complete_run.run_id;
    END IF;
  END IF;

  SELECT * INTO latest_run FROM runs ORDER BY started_at DESC, run_id DESC LIMIT 1;
  IF latest_run.run_id IS NOT NULL THEN
    has_latest := true;
    SELECT * INTO latest_logical FROM logical_runs WHERE logical_run_key = latest_run.logical_run_key;
  END IF;

  RETURN jsonb_build_object(
    'no_snapshot', NOT has_complete,
    'result_code', CASE WHEN has_complete THEN 'OK' ELSE 'NO_SNAPSHOT' END,
    'complete_snapshot', CASE WHEN NOT has_complete THEN NULL ELSE jsonb_build_object(
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
    ) END,
    'latest_attempt', CASE WHEN NOT has_latest THEN NULL ELSE jsonb_build_object(
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
    ) END,
    'latest_partial_run_id', CASE WHEN has_latest THEN latest_logical.latest_partial_run_id ELSE NULL END,
    'available_partial_sections', CASE WHEN has_complete THEN jsonb_build_array('candidates') ELSE '[]'::jsonb END,
    'missing_sections', CASE WHEN has_complete
      THEN jsonb_build_array('tags', 'supply_3day', 'market_supply', 'outcome_tracking')
      ELSE jsonb_build_array('candidates', 'tags', 'supply_3day', 'market_supply', 'outcome_tracking') END,
    'unprocessed_items', CASE WHEN has_latest THEN latest_run.unprocessed_count ELSE 0 END
  );
END;
$$;

comment on function public.get_dashboard_snapshot() is
  'trading_day를 1순위로 정렬해 complete_snapshot을 고른다(2026-09-21 patch). 과거 거래일 logical_run이
  뒤늦게 재발행돼 published_at이 갱신되더라도 당일 실제 최신 complete run을 밀어내지 못하게 한다.';

revoke execute on function public.get_dashboard_snapshot() from public;
grant execute on function public.get_dashboard_snapshot() to anon, authenticated, service_role;

commit;
