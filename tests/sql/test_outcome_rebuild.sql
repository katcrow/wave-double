-- Story 3.10: outcome projection 재구축 검증.
-- 결정적 샘플 장부(OPEN·SL·TP·TIMEOUT·SUSPENDED·CORRECTION 포함)를 직접 삽입한 뒤
-- rebuild_outcome_projection()을 호출하고, 자연 키 (ticker,strategy,entry_date)로 조인한
-- 비-identity 전 필드가 expected_projection(fixtures/outcome_rebuild/expected_projection.json과
-- 동일 데이터)과 정확히 일치하는지, 장부(outcome_events/outcome_observations)가 재생 후에도
-- 변경 없이 보존되는지(append-only 불변) 검증한다.
-- AD-19/NFR-4: outcome 테이블 전부는 장기 보존 대상이며, 이 fixtured 재생은 장부를 변경하지 않는다.
begin;

-- ── matrix: 이벤트 없음 → 재구축 후 candidate_outcome이 비워진 채 유지 ──────────
do $$
begin
  perform public.rebuild_outcome_projection();
  if (select count(*) from public.candidate_outcome) <> 0 then
    raise exception 'REBUILD[empty-ledger]: expected 0 rows, got %',
      (select count(*) from public.candidate_outcome);
  end if;
end $$;

do $$
declare
  v_event_count integer;
  v_obs_count integer;
begin
  -- ── fixture setup ──────────────────────────────────────────────────────────
  insert into public.logical_runs(logical_run_key, trading_day, batch_kind)
  values
    ('close:2099-06-01', date '2099-06-01', 'close'),
    ('close:2099-06-02', date '2099-06-02', 'close'),
    ('close:2099-06-03', date '2099-06-03', 'close'),
    ('close:2099-06-04', date '2099-06-04', 'close'),
    ('close:2099-07-15', date '2099-07-15', 'close'),
    ('close:2099-07-20', date '2099-07-20', 'close')
  on conflict (logical_run_key) do nothing;

  -- 100001/A: OPEN만 존재 → OPEN, exit null, cutoff 30, holding 0
  insert into public.outcome_events(event_id, ticker, strategy, command_type, logical_run_key, payload)
  values
    ('10000000-0000-0000-0000-000000000001', '100001', 'A', 'OPEN', 'close:2099-06-01',
     '{"entry_date":"2099-06-01","entry_price":100}'::jsonb);

  -- 100002/B: OPEN → SL (terminal)
  insert into public.outcome_events(event_id, ticker, strategy, command_type, logical_run_key, payload)
  values
    ('10000000-0000-0000-0000-000000000002', '100002', 'B', 'OPEN', 'close:2099-06-01',
     '{"entry_date":"2099-06-01","entry_price":200}'::jsonb),
    ('10000000-0000-0000-0000-000000000003', '100002', 'B', 'SL', 'close:2099-06-02',
     '{"trading_day":"2099-06-02","exit_price":194,"return_pct":-3.1,"holding_days":1}'::jsonb);

  -- 100003/C: OPEN → TP (terminal)
  insert into public.outcome_events(event_id, ticker, strategy, command_type, logical_run_key, payload)
  values
    ('10000000-0000-0000-0000-000000000004', '100003', 'C', 'OPEN', 'close:2099-06-01',
     '{"entry_date":"2099-06-01","entry_price":300}'::jsonb),
    ('10000000-0000-0000-0000-000000000005', '100003', 'C', 'TP', 'close:2099-06-02',
     '{"trading_day":"2099-06-02","exit_price":309,"return_pct":2.9,"holding_days":1}'::jsonb);

  -- 100004/A: OPEN만 존재 (두 번째 OPEN-only 케이스)
  insert into public.outcome_events(event_id, ticker, strategy, command_type, logical_run_key, payload)
  values
    ('10000000-0000-0000-0000-000000000006', '100004', 'A', 'OPEN', 'close:2099-06-01',
     '{"entry_date":"2099-06-01","entry_price":400}'::jsonb);

  -- 100005/B: OPEN → SUSPENDED → CORRECTION(OPEN 복귀, new_cutoff_n=15)
  insert into public.outcome_events(event_id, ticker, strategy, command_type, logical_run_key, payload)
  values
    ('10000000-0000-0000-0000-000000000007', '100005', 'B', 'OPEN', 'close:2099-06-01',
     '{"entry_date":"2099-06-01","entry_price":500}'::jsonb),
    ('10000000-0000-0000-0000-000000000008', '100005', 'B', 'SUSPENDED', 'close:2099-06-03',
     '{"trading_day":"2099-06-03","via_pricechk":false,"gap_pct":0.35}'::jsonb),
    ('10000000-0000-0000-0000-000000000009', '100005', 'B', 'CORRECTION', 'close:2099-06-04',
     '{"reason":"일봉 재확인 후 가격 조정 오탐 해제","outcome_id":"50000000-0000-0000-0000-000000000005","previous_status":"SUSPENDED","new_status":"OPEN","previous_cutoff_n":30,"new_cutoff_n":15}'::jsonb);

  -- 100006/C: OPEN → TIMEOUT → CORRECTION(DELISTED 종결)
  insert into public.outcome_events(event_id, ticker, strategy, command_type, logical_run_key, payload)
  values
    ('10000000-0000-0000-0000-00000000000a', '100006', 'C', 'OPEN', 'close:2099-06-01',
     '{"entry_date":"2099-06-01","entry_price":600}'::jsonb),
    ('10000000-0000-0000-0000-00000000000b', '100006', 'C', 'TIMEOUT', 'close:2099-07-15',
     '{"trading_day":"2099-07-15","exit_price":612,"return_pct":1.9,"holding_days":30}'::jsonb),
    ('10000000-0000-0000-0000-00000000000c', '100006', 'C', 'CORRECTION', 'close:2099-07-20',
     '{"reason":"상장폐지 확정","outcome_id":"60000000-0000-0000-0000-000000000006","previous_status":"TIMEOUT","new_status":"DELISTED","previous_exit_date":"2099-07-15","new_exit_date":"2099-07-20","previous_exit_price":612,"new_exit_price":610}'::jsonb);

  insert into public.outcome_observations(outcome_id, evaluation_trading_day, high, low, close, result_code)
  values
    ('10000100-0000-0000-0000-000000000001', date '2099-06-02', 101, 99, 100, 'NO_HIT'),
    ('10000200-0000-0000-0000-000000000002', date '2099-06-02', 205, 193, 194, 'SL_HIT'),
    ('10000300-0000-0000-0000-000000000003', date '2099-06-02', 310, 301, 305, 'TP_HIT'),
    ('10000500-0000-0000-0000-000000000005', date '2099-06-02', 510, 498, 500, 'NO_HIT'),
    ('10000500-0000-0000-0000-000000000005', date '2099-06-03', 512, 495, 502, 'NO_HIT'),
    ('10000600-0000-0000-0000-000000000006', date '2099-06-02', 601, 598, 599, 'NO_HIT'),
    ('10000600-0000-0000-0000-000000000006', date '2099-07-15', 615, 600, 612, 'TIMEOUT');

  -- ── ledger immutability: rebuild 전 장부 개수 고정 확인 ─────────────────────
  select count(*) into v_event_count from public.outcome_events;
  select count(*) into v_obs_count   from public.outcome_observations;
  if v_event_count <> 12 then raise exception 'pre-rebuild outcome_events count expected 12, got %', v_event_count; end if;
  if v_obs_count <> 7 then raise exception 'pre-rebuild outcome_observations count expected 7, got %', v_obs_count; end if;

  -- ── rebuild ────────────────────────────────────────────────────────────────
  perform public.rebuild_outcome_projection();

  -- ── AC1: 자연 키로 조인한 비-identity 전 필드가 기대 projection과 일치 ──────
  -- 100001/A (OPEN만 존재)
  if not exists (
    select 1 from public.candidate_outcome
    where ticker = '100001' and strategy = 'A' and entry_date = date '2099-06-01'
      and status = 'OPEN' and entry_price = 100
      and exit_date is null and exit_price is null and return_pct is null
      and cutoff_n = 30 and holding_days = 0
  ) then raise exception 'REBUILD[100001/A]: OPEN-only mismatch'; end if;

  -- 100002/B (SL terminal)
  if not exists (
    select 1 from public.candidate_outcome
    where ticker = '100002' and strategy = 'B' and entry_date = date '2099-06-01'
      and status = 'SL' and entry_price = 200
      and exit_date = date '2099-06-02' and exit_price = 194 and return_pct = -3.1
      and cutoff_n = 30 and holding_days = 1
  ) then raise exception 'REBUILD[100002/B]: SL terminal mismatch'; end if;

  -- 100003/C (TP terminal)
  if not exists (
    select 1 from public.candidate_outcome
    where ticker = '100003' and strategy = 'C' and entry_date = date '2099-06-01'
      and status = 'TP' and entry_price = 300
      and exit_date = date '2099-06-02' and exit_price = 309 and return_pct = 2.9
      and cutoff_n = 30 and holding_days = 1
  ) then raise exception 'REBUILD[100003/C]: TP terminal mismatch'; end if;

  -- 100004/A (두 번째 OPEN-only)
  if not exists (
    select 1 from public.candidate_outcome
    where ticker = '100004' and strategy = 'A' and entry_date = date '2099-06-01'
      and status = 'OPEN' and entry_price = 400
      and exit_date is null and exit_price is null and return_pct is null
      and cutoff_n = 30 and holding_days = 0
  ) then raise exception 'REBUILD[100004/A]: OPEN-only mismatch'; end if;

  -- 100005/B (SUSPENDED → OPEN 복귀, new_cutoff_n=15, exit 3필드 null)
  if not exists (
    select 1 from public.candidate_outcome
    where ticker = '100005' and strategy = 'B' and entry_date = date '2099-06-01'
      and status = 'OPEN' and entry_price = 500
      and exit_date is null and exit_price is null and return_pct is null
      and cutoff_n = 15 and holding_days = 0
  ) then raise exception 'REBUILD[100005/B]: SUSPENDED→OPEN recovery mismatch'; end if;

  -- 100006/C (TIMEOUT → CORRECTION DELISTED: exit_date/exit_price 교체, return_pct/ holding 보존)
  if not exists (
    select 1 from public.candidate_outcome
    where ticker = '100006' and strategy = 'C' and entry_date = date '2099-06-01'
      and status = 'DELISTED' and entry_price = 600
      and exit_date = date '2099-07-20' and exit_price = 610 and return_pct = 1.9
      and cutoff_n = 30 and holding_days = 30
  ) then raise exception 'REBUILD[100006/C]: DELISTED termination mismatch'; end if;

  -- 정확히 6행 재구축
  if (select count(*) from public.candidate_outcome) <> 6 then
    raise exception 'expected 6 rebuilt rows, got %', (select count(*) from public.candidate_outcome);
  end if;

  -- ── AC3: append-only 불변 — 재생 후 장부 변경·삭제·추가 없음 ────────────────
  if (select count(*) from public.outcome_events) <> v_event_count then
    raise exception 'outcome_events changed after rebuild (expected %, got %)',
      v_event_count, (select count(*) from public.outcome_events);
  end if;
  if (select count(*) from public.outcome_observations) <> v_obs_count then
    raise exception 'outcome_observations changed after rebuild (expected %, got %)',
      v_obs_count, (select count(*) from public.outcome_observations);
  end if;

  if not exists (select 1 from public.outcome_events where event_id = '10000000-0000-0000-0000-00000000000c')
     or not exists (select 1 from public.outcome_events where event_id = '10000000-0000-0000-0000-000000000001')
  then raise exception 'append-only outcome_events row missing after rebuild'; end if;

  -- ── idempotency: 같은 장부로 rebuild를 다시 호출해도 projection이 동일한가 ────
  perform public.rebuild_outcome_projection();
  if (select count(*) from public.candidate_outcome) <> 6 then
    raise exception 'idempotent rebuild: expected 6 rows, got %',
      (select count(*) from public.candidate_outcome);
  end if;
  if not exists (
    select 1 from public.candidate_outcome
    where ticker = '100006' and strategy = 'C' and entry_date = date '2099-06-01'
      and status = 'DELISTED' and exit_date = date '2099-07-20' and exit_price = 610
      and return_pct = 1.9 and cutoff_n = 30 and holding_days = 30
  ) then raise exception 'idempotent rebuild: DELISTED row drifted'; end if;

end $$;

select 'outcome_rebuild_contract' as fixture, 'pass' as result;
rollback;
