-- backup-restore-drill.yml 전용 smoke 검증.
--
-- tests/sql/test_*.sql 파일들(sql-schema-tests가 도는 빈 disposable DB 전제)과 달리, 이
-- 스크립트는 실제 운영 백업을 복원한 DB에서 돈다 -- 행 개수나 구체적 값을 단언하면 실제
-- 데이터가 있을 때마다 깨진다(2026-09-14, test_dashboard_snapshot.sql의 "empty db" 단언이
-- 정확히 이 이유로 실패해 발견됨). 그래서 이 스크립트는 핵심 테이블/함수/RLS가 "존재하고
-- 정상 응답하는지"만 확인하고, 반환되는 데이터의 내용은 검증하지 않는다.
begin;

do $$
declare
  missing text;
  core_tables text[] := array[
    'logical_runs', 'runs', 'candidates', 'candidate_source_contrib', 'candidate_tags',
    'daily_ohlcv', 'supply_3day', 'market_supply', 'dispatch_outbox', 'dispatch_request',
    'trading_calendar', 'outcome_events', 'outcome_observations', 'candidate_outcome',
    'outcome_strategy_rules', 'outcome_strategy_rule_history', 'bias_events',
    'bias_event_by_source'
  ];
  t text;
begin
  foreach t in array core_tables loop
    if not exists (
      select 1 from information_schema.tables
      where table_schema = 'public' and table_name = t
    ) then
      missing := coalesce(missing || ', ', '') || t;
    end if;
  end loop;
  if missing is not null then
    raise exception 'restore drill smoke: missing core table(s): %', missing;
  end if;
end $$;

do $$
declare
  rls_disabled text;
  rls_tables text[] := array[
    'candidates', 'candidate_tags', 'candidate_outcome', 'outcome_events',
    'outcome_strategy_rules', 'daily_ohlcv'
  ];
  t text;
begin
  foreach t in array rls_tables loop
    if not exists (
      select 1 from pg_class c
      join pg_namespace n on n.oid = c.relnamespace
      where n.nspname = 'public' and c.relname = t and c.relrowsecurity
    ) then
      rls_disabled := coalesce(rls_disabled || ', ', '') || t;
    end if;
  end loop;
  if rls_disabled is not null then
    raise exception 'restore drill smoke: RLS not enabled on: %', rls_disabled;
  end if;
end $$;

do $$
declare
  snapshot jsonb;
begin
  snapshot := public.get_dashboard_snapshot();
  if snapshot is null then
    raise exception 'restore drill smoke: get_dashboard_snapshot returned null';
  end if;
  if not (snapshot ? 'result_code') then
    raise exception 'restore drill smoke: get_dashboard_snapshot shape unexpected: %', snapshot;
  end if;
end $$;

do $$
begin
  if has_table_privilege('anon', 'public.candidates', 'select')
     and not exists (
       select 1 from pg_class c
       join pg_namespace n on n.oid = c.relnamespace
       where n.nspname = 'public' and c.relname = 'candidates' and c.relrowsecurity
     ) then
    raise exception 'restore drill smoke: anon could read candidates directly (RLS disabled + grant present)';
  end if;
  if has_function_privilege('anon', 'public.get_candidate_evidence(uuid)'::regprocedure, 'execute') = false
     and has_function_privilege('authenticated', 'public.get_candidate_evidence(uuid)'::regprocedure, 'execute') = false then
    raise exception 'restore drill smoke: get_candidate_evidence is not callable by any browser-facing role (over-restricted after restore?)';
  end if;
end $$;

select 'PASS' as restore_drill_smoke_result;

rollback;
