-- Story 5.6: 전략 × 원천 분리 승률·PF view 검증.
-- candidate_outcome, candidate_source_contrib, candidates, logical_runs에 fixture 행을 삽입하고
-- candidate_outcome_win_rate_pf_by_strategy_source view 조회 결과를 src_expected와 대조한다.
-- 모든 변경은 rollback으로 되돌린다.
-- parity 도구는 parity fixture setup 마커 아래의 INSERT만 파싱한다.
begin;
-- ── parity fixture setup

-- logical_runs: close:2098-05-01 .. 04
insert into public.logical_runs(logical_run_key, trading_day, batch_kind) values
('close:2098-05-01', '2098-05-01', 'close'),
('close:2098-05-02', '2098-05-02', 'close'),
('close:2098-05-03', '2098-05-03', 'close'),
('close:2098-05-04', '2098-05-04', 'close');

-- runs: 4 published runs (one per close day)
insert into public.runs(run_id, logical_run_key, attempt_no, fence_token, lease_expires_at, trigger, status) values
('10000000-0000-0000-0000-000000000001', 'close:2098-05-01', 1, 1, now() + interval '1 hour', 'schedule', 'published'),
('10000000-0000-0000-0000-000000000002', 'close:2098-05-02', 1, 2, now() + interval '1 hour', 'schedule', 'published'),
('10000000-0000-0000-0000-000000000003', 'close:2098-05-03', 1, 3, now() + interval '1 hour', 'schedule', 'published'),
('10000000-0000-0000-0000-000000000004', 'close:2098-05-04', 1, 4, now() + interval '1 hour', 'schedule', 'published');

-- canonical runs: set canonical_success_run_id on each close logical_run
update public.logical_runs set canonical_success_run_id = '10000000-0000-0000-0000-000000000001' where logical_run_key = 'close:2098-05-01';
update public.logical_runs set canonical_success_run_id = '10000000-0000-0000-0000-000000000002' where logical_run_key = 'close:2098-05-02';
update public.logical_runs set canonical_success_run_id = '10000000-0000-0000-0000-000000000003' where logical_run_key = 'close:2098-05-03';
update public.logical_runs set canonical_success_run_id = '10000000-0000-0000-0000-000000000004' where logical_run_key = 'close:2098-05-04';

-- candidates: 8 rows (A0001..A0008), name/truncated use defaults
insert into public.candidates(candidate_id, attempt_run_id, ticker, trading_day, trading_value) values
('00000000-0000-0000-0000-000000000001', '10000000-0000-0000-0000-000000000001', 'A0001', '2098-05-01', 1000000000),
('00000000-0000-0000-0000-000000000002', '10000000-0000-0000-0000-000000000001', 'A0002', '2098-05-01', 2000000000),
('00000000-0000-0000-0000-000000000003', '10000000-0000-0000-0000-000000000002', 'A0003', '2098-05-02', 3000000000),
('00000000-0000-0000-0000-000000000004', '10000000-0000-0000-0000-000000000002', 'A0004', '2098-05-02', 1500000000),
('00000000-0000-0000-0000-000000000005', '10000000-0000-0000-0000-000000000003', 'A0005', '2098-05-03', 2500000000),
('00000000-0000-0000-0000-000000000006', '10000000-0000-0000-0000-000000000003', 'A0006', '2098-05-03', 4000000000),
('00000000-0000-0000-0000-000000000007', '10000000-0000-0000-0000-000000000004', 'A0007', '2098-05-04', 3500000000),
('00000000-0000-0000-0000-000000000008', '10000000-0000-0000-0000-000000000004', 'A0008', '2098-05-04', 4500000000);

-- candidate_source_contrib: 10 rows
insert into public.candidate_source_contrib(candidate_id, attempt_run_id, source, contribution_weight) values
('00000000-0000-0000-0000-000000000001', '10000000-0000-0000-0000-000000000001', 't1859', 1.0),
('00000000-0000-0000-0000-000000000002', '10000000-0000-0000-0000-000000000001', 't1852', 1.0),
('00000000-0000-0000-0000-000000000003', '10000000-0000-0000-0000-000000000002', 't1852', 0.7),
('00000000-0000-0000-0000-000000000003', '10000000-0000-0000-0000-000000000002', 't1859', 0.3),
('00000000-0000-0000-0000-000000000004', '10000000-0000-0000-0000-000000000002', 't1859', 0.5),
('00000000-0000-0000-0000-000000000004', '10000000-0000-0000-0000-000000000002', 't1852', 0.5),
('00000000-0000-0000-0000-000000000005', '10000000-0000-0000-0000-000000000003', 't1856', 1.0),
('00000000-0000-0000-0000-000000000006', '10000000-0000-0000-0000-000000000003', 't1859', 1.0),
('00000000-0000-0000-0000-000000000007', '10000000-0000-0000-0000-000000000004', 't1859', 1.0),
('00000000-0000-0000-0000-000000000008', '10000000-0000-0000-0000-000000000004', 't1852', 1.0);

-- candidate_outcome: 5-5 동일 9건
insert into public.candidate_outcome(ticker, strategy, entry_date, entry_price, status, exit_date, exit_price, return_pct, cutoff_n, holding_days, tp_pct, sl_pct) values
('A0001', 'A', '2098-05-01', 1000, 'TP', '2098-05-03', 1029, 2.9, 30, 2, 3.0, 3.0),
('A0002', 'B', '2098-05-01', 2000, 'SL', '2098-05-03', 1940, -3.0, 30, 2, 3.0, 3.0),
('A0003', 'C', '2098-05-02', 5000, 'TIMEOUT', '2098-06-01', 5075, 1.5, 30, 30, 3.0, 3.0),
('A0004', 'A', '2098-05-02', 1000, 'TIMEOUT', '2098-06-01', 980, -2.0, 30, 30, 3.0, 3.0),
('A0005', 'B', '2098-05-03', 3000, 'TP', '2098-05-05', 3060, 2.0, 30, 2, 3.0, 3.0),
('A0006', 'C', '2098-05-03', 4000, 'SL', '2098-05-05', 3840, -4.0, 30, 2, 3.0, 3.0),
('A0007', 'A', '2098-05-04', 1000, 'OPEN', null, null, null, 30, 0, 3.0, 3.0),
('A0008', 'B', '2098-05-04', 2000, 'SUSPENDED', null, null, null, 30, 0, 3.0, 3.0),
('A0009', 'C', '2098-05-05', 5000, 'DELISTED', '2098-05-10', 4800, null, 30, 5, 3.0, 3.0);

-- src_expected: 6 cells (컬럼 순서는 view select 순서와 동일해야 `select *` EXCEPT가 위치 기준으로 정확히 비교된다)
create temp table src_expected (
  strategy text, source text,
  total_settled integer, wins integer, losses integer,
  open_count integer, suspended_count integer, delisted_count integer,
  win_rate numeric, gross_win numeric, gross_loss numeric,
  profit_factor numeric
);
insert into src_expected values
('A', 't1859', 2, 1, 1, 1, 0, 0, 0.5000, 2.9, 2.0, 1.4500),
('B', 't1852', 1, 0, 1, 0, 1, 0, 0.0000, NULL, 3.0, NULL),
('B', 't1856', 1, 1, 0, 0, 0, 0, 1.0000, 2.0, NULL, NULL),
('C', 't1852', 1, 1, 0, 0, 0, 0, 1.0000, 1.5, NULL, NULL),
('C', 't1859', 1, 0, 1, 0, 0, 0, 0.0000, NULL, 4.0, NULL),
('C', NULL, 0, 0, 0, 0, 0, 1, NULL, NULL, NULL, NULL);

-- EXCEPT-diff 대조: NULL-safe (PostgreSQL EXCEPT treats NULLs as equal)
do $$
declare
  v_view_only integer;
  v_expected_only integer;
begin
  select count(*) into v_view_only from (
    select * from public.candidate_outcome_win_rate_pf_by_strategy_source
    except
    select * from src_expected
  ) d;
  select count(*) into v_expected_only from (
    select * from src_expected
    except
    select * from public.candidate_outcome_win_rate_pf_by_strategy_source
  ) d;
  if v_view_only > 0 or v_expected_only > 0 then
    raise exception 'story 5-6 src view EXCEPT diff: view-only=% expected-only=% rows', v_view_only, v_expected_only;
  end if;
  raise notice 'story 5-6 src view assertion: all cells match';
end $$;
rollback;