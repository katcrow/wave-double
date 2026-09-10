-- Story 5.7: 표본 게이트(30건) 처리 view 검증. candidate_outcome에 fixture 행을 삽입하고
-- candidate_outcome_win_rate_pf_by_strategy_gated view 조회 결과를 gate_expected와 대조한다.
-- 전략 A는 종결 정확히 29건(게이트 실패), 전략 B는 종결 정확히 30건(게이트 통과)이며
-- strategy IS NULL 전체 rollup 행이 A+B 합계로 게이트 통과함을 함께 검증한다.
-- 모든 변경은 rollback으로 되돌린다.
-- parity 도구는 parity fixture setup 마커 아래의 candidate_outcome INSERT만 파싱한다.
begin;
-- ── parity fixture setup
insert into public.candidate_outcome(ticker, strategy, entry_date, entry_price, status, exit_date, exit_price, return_pct, cutoff_n, holding_days, tp_pct, sl_pct) values
('G0001', 'A', '2098-05-02', 1000, 'TP', '2098-06-02', 1020, 2.0, 30, 2, 3.0, 3.0),
('G0002', 'A', '2098-05-03', 1000, 'TP', '2098-06-03', 1020, 2.0, 30, 2, 3.0, 3.0),
('G0003', 'A', '2098-05-04', 1000, 'TP', '2098-06-04', 1020, 2.0, 30, 2, 3.0, 3.0),
('G0004', 'A', '2098-05-05', 1000, 'TP', '2098-06-05', 1020, 2.0, 30, 2, 3.0, 3.0),
('G0005', 'A', '2098-05-06', 1000, 'TP', '2098-06-06', 1020, 2.0, 30, 2, 3.0, 3.0),
('G0006', 'A', '2098-05-07', 1000, 'TP', '2098-06-07', 1020, 2.0, 30, 2, 3.0, 3.0),
('G0007', 'A', '2098-05-08', 1000, 'TP', '2098-06-08', 1020, 2.0, 30, 2, 3.0, 3.0),
('G0008', 'A', '2098-05-09', 1000, 'TP', '2098-06-09', 1020, 2.0, 30, 2, 3.0, 3.0),
('G0009', 'A', '2098-05-10', 1000, 'TP', '2098-06-10', 1020, 2.0, 30, 2, 3.0, 3.0),
('G0010', 'A', '2098-05-11', 1000, 'TP', '2098-06-11', 1020, 2.0, 30, 2, 3.0, 3.0),
('G0011', 'A', '2098-05-12', 1000, 'TP', '2098-06-12', 1020, 2.0, 30, 2, 3.0, 3.0),
('G0012', 'A', '2098-05-13', 1000, 'TP', '2098-06-13', 1020, 2.0, 30, 2, 3.0, 3.0),
('G0013', 'A', '2098-05-14', 1000, 'TP', '2098-06-14', 1020, 2.0, 30, 2, 3.0, 3.0),
('G0014', 'A', '2098-05-15', 1000, 'TP', '2098-06-15', 1020, 2.0, 30, 2, 3.0, 3.0),
('G0015', 'A', '2098-05-16', 1000, 'TP', '2098-06-16', 1020, 2.0, 30, 2, 3.0, 3.0),
('G0016', 'A', '2098-05-17', 1000, 'TP', '2098-06-17', 1020, 2.0, 30, 2, 3.0, 3.0),
('G0017', 'A', '2098-05-18', 1000, 'TP', '2098-06-18', 1020, 2.0, 30, 2, 3.0, 3.0),
('G0018', 'A', '2098-05-19', 1000, 'TP', '2098-06-19', 1020, 2.0, 30, 2, 3.0, 3.0),
('G0019', 'A', '2098-05-20', 1000, 'TP', '2098-06-20', 1020, 2.0, 30, 2, 3.0, 3.0),
('G0020', 'A', '2098-05-21', 1000, 'TP', '2098-06-21', 1020, 2.0, 30, 2, 3.0, 3.0),
('G0021', 'A', '2098-05-22', 1000, 'TP', '2098-06-22', 1020, 2.0, 30, 2, 3.0, 3.0),
('G0022', 'A', '2098-05-23', 1000, 'TP', '2098-06-23', 1020, 2.0, 30, 2, 3.0, 3.0),
('G0023', 'A', '2098-05-24', 1000, 'TP', '2098-06-24', 1020, 2.0, 30, 2, 3.0, 3.0),
('G0024', 'A', '2098-05-25', 1000, 'TP', '2098-06-25', 1020, 2.0, 30, 2, 3.0, 3.0),
('G0025', 'A', '2098-05-26', 1000, 'TP', '2098-06-26', 1020, 2.0, 30, 2, 3.0, 3.0),
('G0026', 'A', '2098-05-27', 1000, 'TP', '2098-06-27', 1020, 2.0, 30, 2, 3.0, 3.0),
('G0027', 'A', '2098-05-28', 1000, 'TP', '2098-06-28', 1020, 2.0, 30, 2, 3.0, 3.0),
('G0028', 'A', '2098-05-01', 1000, 'TP', '2098-06-01', 1020, 2.0, 30, 2, 3.0, 3.0),
('G0029', 'A', '2098-05-02', 1000, 'TP', '2098-06-02', 1020, 2.0, 30, 2, 3.0, 3.0),
('G0030', 'A', '2098-05-05', 1000, 'OPEN', null, null, null, 30, 0, 3.0, 3.0),
('G0031', 'A', '2098-05-06', 1000, 'OPEN', null, null, null, 30, 0, 3.0, 3.0),
('G0032', 'A', '2098-05-07', 2000, 'SUSPENDED', null, null, null, 30, 0, 3.0, 3.0),
('H0001', 'B', '2098-05-02', 2000, 'TP', '2098-06-02', 2060, 3.0, 30, 2, 3.0, 3.0),
('H0002', 'B', '2098-05-03', 2000, 'TP', '2098-06-03', 2060, 3.0, 30, 2, 3.0, 3.0),
('H0003', 'B', '2098-05-04', 2000, 'TP', '2098-06-04', 2060, 3.0, 30, 2, 3.0, 3.0),
('H0004', 'B', '2098-05-05', 2000, 'TP', '2098-06-05', 2060, 3.0, 30, 2, 3.0, 3.0),
('H0005', 'B', '2098-05-06', 2000, 'TP', '2098-06-06', 2060, 3.0, 30, 2, 3.0, 3.0),
('H0006', 'B', '2098-05-07', 2000, 'TP', '2098-06-07', 2060, 3.0, 30, 2, 3.0, 3.0),
('H0007', 'B', '2098-05-08', 2000, 'TP', '2098-06-08', 2060, 3.0, 30, 2, 3.0, 3.0),
('H0008', 'B', '2098-05-09', 2000, 'TP', '2098-06-09', 2060, 3.0, 30, 2, 3.0, 3.0),
('H0009', 'B', '2098-05-10', 2000, 'TP', '2098-06-10', 2060, 3.0, 30, 2, 3.0, 3.0),
('H0010', 'B', '2098-05-11', 2000, 'TP', '2098-06-11', 2060, 3.0, 30, 2, 3.0, 3.0),
('H0011', 'B', '2098-05-12', 2000, 'TP', '2098-06-12', 2060, 3.0, 30, 2, 3.0, 3.0),
('H0012', 'B', '2098-05-13', 2000, 'TP', '2098-06-13', 2060, 3.0, 30, 2, 3.0, 3.0),
('H0013', 'B', '2098-05-14', 2000, 'TP', '2098-06-14', 2060, 3.0, 30, 2, 3.0, 3.0),
('H0014', 'B', '2098-05-15', 2000, 'TP', '2098-06-15', 2060, 3.0, 30, 2, 3.0, 3.0),
('H0015', 'B', '2098-05-16', 2000, 'TP', '2098-06-16', 2060, 3.0, 30, 2, 3.0, 3.0),
('H0016', 'B', '2098-05-17', 2000, 'SL', '2098-06-17', 1980, -1.0, 30, 2, 3.0, 3.0),
('H0017', 'B', '2098-05-18', 2000, 'SL', '2098-06-18', 1980, -1.0, 30, 2, 3.0, 3.0),
('H0018', 'B', '2098-05-19', 2000, 'SL', '2098-06-19', 1980, -1.0, 30, 2, 3.0, 3.0),
('H0019', 'B', '2098-05-20', 2000, 'SL', '2098-06-20', 1980, -1.0, 30, 2, 3.0, 3.0),
('H0020', 'B', '2098-05-21', 2000, 'SL', '2098-06-21', 1980, -1.0, 30, 2, 3.0, 3.0),
('H0021', 'B', '2098-05-22', 2000, 'SL', '2098-06-22', 1980, -1.0, 30, 2, 3.0, 3.0),
('H0022', 'B', '2098-05-23', 2000, 'SL', '2098-06-23', 1980, -1.0, 30, 2, 3.0, 3.0),
('H0023', 'B', '2098-05-24', 2000, 'SL', '2098-06-24', 1980, -1.0, 30, 2, 3.0, 3.0),
('H0024', 'B', '2098-05-25', 2000, 'SL', '2098-06-25', 1980, -1.0, 30, 2, 3.0, 3.0),
('H0025', 'B', '2098-05-26', 2000, 'SL', '2098-06-26', 1980, -1.0, 30, 2, 3.0, 3.0),
('H0026', 'B', '2098-05-27', 2000, 'SL', '2098-06-27', 1980, -1.0, 30, 2, 3.0, 3.0),
('H0027', 'B', '2098-05-28', 2000, 'SL', '2098-06-28', 1980, -1.0, 30, 2, 3.0, 3.0),
('H0028', 'B', '2098-05-01', 2000, 'SL', '2098-06-01', 1980, -1.0, 30, 2, 3.0, 3.0),
('H0029', 'B', '2098-05-02', 2000, 'SL', '2098-06-02', 1980, -1.0, 30, 2, 3.0, 3.0),
('H0030', 'B', '2098-05-03', 2000, 'SL', '2098-06-03', 1980, -1.0, 30, 2, 3.0, 3.0),
('H0031', 'B', '2098-05-08', 3000, 'DELISTED', '2098-05-20', 2800, null, 30, 5, 3.0, 3.0);

create temp table gate_expected (
  strategy text, total_settled int, wins int, losses int,
  open_count int, suspended_count int, delisted_count int,
  gross_win numeric, gross_loss numeric,
  win_rate numeric, profit_factor numeric,
  sample_gate_min_required int, sample_gate_passed boolean, sample_gate_label text
);
insert into gate_expected values
('A', 29, 29, 0, 2, 1, 0, 58.0, null, null, null, 30, false, '표본 부족 (29/30)'),
('B', 30, 15, 15, 0, 0, 1, 45.0, 15.0, 0.5000, 3.0000, 30, true, null),
(null, 59, 44, 15, 2, 1, 1, 103.0, 15.0, 0.7458, 6.8667, 30, true, null);

do $$
declare
  e record;
  r record;
  msg text;
begin
  for e in select * from gate_expected loop
    select * into r
    from public.candidate_outcome_win_rate_pf_by_strategy_gated v
    where v.strategy is not distinct from e.strategy;

    if not found then
      raise exception 'story 5-7: strategy % 행이 view에 없다', e.strategy;
    end if;

    if r.total_settled <> e.total_settled then
      msg := format('strategy %s total_settled mismatch: view=%s expected=%s', e.strategy, r.total_settled, e.total_settled);
      raise exception '%', msg;
    end if;
    if r.wins <> e.wins then
      msg := format('strategy %s wins mismatch: view=%s expected=%s', e.strategy, r.wins, e.wins);
      raise exception '%', msg;
    end if;
    if r.losses <> e.losses then
      msg := format('strategy %s losses mismatch: view=%s expected=%s', e.strategy, r.losses, e.losses);
      raise exception '%', msg;
    end if;
    if r.open_count <> e.open_count then
      msg := format('strategy %s open_count mismatch: view=%s expected=%s', e.strategy, r.open_count, e.open_count);
      raise exception '%', msg;
    end if;
    if r.suspended_count <> e.suspended_count then
      msg := format('strategy %s suspended_count mismatch: view=%s expected=%s', e.strategy, r.suspended_count, e.suspended_count);
      raise exception '%', msg;
    end if;
    if r.delisted_count <> e.delisted_count then
      msg := format('strategy %s delisted_count mismatch: view=%s expected=%s', e.strategy, r.delisted_count, e.delisted_count);
      raise exception '%', msg;
    end if;
    if r.gross_win is distinct from e.gross_win then
      msg := format('strategy %s gross_win mismatch: view=%s expected=%s', e.strategy, r.gross_win, e.gross_win);
      raise exception '%', msg;
    end if;
    if r.gross_loss is distinct from e.gross_loss then
      msg := format('strategy %s gross_loss mismatch: view=%s expected=%s', e.strategy, r.gross_loss, e.gross_loss);
      raise exception '%', msg;
    end if;
    if r.win_rate is distinct from e.win_rate then
      msg := format('strategy %s win_rate mismatch: view=%s expected=%s', e.strategy, r.win_rate, e.win_rate);
      raise exception '%', msg;
    end if;
    if r.profit_factor is distinct from e.profit_factor then
      msg := format('strategy %s profit_factor mismatch: view=%s expected=%s', e.strategy, r.profit_factor, e.profit_factor);
      raise exception '%', msg;
    end if;
    if r.sample_gate_min_required <> e.sample_gate_min_required then
      msg := format('strategy %s sample_gate_min_required mismatch: view=%s expected=%s', e.strategy, r.sample_gate_min_required, e.sample_gate_min_required);
      raise exception '%', msg;
    end if;
    if r.sample_gate_passed <> e.sample_gate_passed then
      msg := format('strategy %s sample_gate_passed mismatch: view=%s expected=%s', e.strategy, r.sample_gate_passed, e.sample_gate_passed);
      raise exception '%', msg;
    end if;
    if r.sample_gate_label is distinct from e.sample_gate_label then
      msg := format('strategy %s sample_gate_label mismatch: view=%s expected=%s', e.strategy, r.sample_gate_label, e.sample_gate_label);
      raise exception '%', msg;
    end if;
  end loop;

  raise notice 'story 5-7 gated view assertion: all fields match (A/B/rollup)';
end $$;

-- ── edge case 시나리오(parity 파서 대상 아님: 전체 테이블을 재구성하므로 main parity
--    INSERT와 분리된 do 블록으로만 처리한다. 전부 rollback으로 되돌린다.)

-- NO_SETTLED: 전략에 종결 0건, OPEN만 존재하면 게이트 실패(0/30)이고 카운트는 정상 노출된다.
do $$
declare
  r record;
begin
  delete from public.candidate_outcome;
  insert into public.candidate_outcome(ticker, strategy, entry_date, entry_price, status, exit_date, exit_price, return_pct, cutoff_n, holding_days, tp_pct, sl_pct) values
  ('N0001', 'C', '2098-05-01', 1000, 'OPEN', null, null, null, 30, 0, 3.0, 3.0),
  ('N0002', 'C', '2098-05-02', 1000, 'OPEN', null, null, null, 30, 0, 3.0, 3.0);
  select * into r from public.candidate_outcome_win_rate_pf_by_strategy_gated where strategy = 'C';
  if r.total_settled <> 0 then
    raise exception 'NO_SETTLED total_settled mismatch: view=% expected=0', r.total_settled;
  end if;
  if r.open_count <> 2 then
    raise exception 'NO_SETTLED open_count mismatch: view=% expected=2', r.open_count;
  end if;
  if r.sample_gate_passed <> false then
    raise exception 'NO_SETTLED sample_gate_passed should be false: view=%', r.sample_gate_passed;
  end if;
  if r.sample_gate_label is distinct from '표본 부족 (0/30)' then
    raise exception 'NO_SETTLED sample_gate_label mismatch: view=%', r.sample_gate_label;
  end if;
  if r.win_rate is not null then
    raise exception 'NO_SETTLED win_rate should be NULL: view=%', r.win_rate;
  end if;
  if r.profit_factor is not null then
    raise exception 'NO_SETTLED profit_factor should be NULL: view=%', r.profit_factor;
  end if;
  raise notice 'story 5-7 NO_SETTLED scenario: pass';
end $$;

-- EMPTY: candidate_outcome이 완전히 비어 있어도 group by rollup(strategy)의 ()
-- grouping set은 일반 집계처럼 단일 grand-total 행을 만든다(전략별 그룹은 0개이지만
-- 전체 rollup 행 자체는 "GROUP BY 없는 집계"와 동일하게 항상 1행 존재). 그 행은
-- strategy=NULL, 모든 카운트 0, 게이트 실패(0/30)여야 한다.
do $$
declare
  cnt int;
  r record;
begin
  delete from public.candidate_outcome;
  select count(*) into cnt from public.candidate_outcome_win_rate_pf_by_strategy_gated;
  if cnt <> 1 then
    raise exception 'EMPTY view row count mismatch: view=% expected=1(grand-total)', cnt;
  end if;
  select * into r from public.candidate_outcome_win_rate_pf_by_strategy_gated;
  if r.strategy is not null then
    raise exception 'EMPTY strategy should be NULL: view=%', r.strategy;
  end if;
  if r.total_settled <> 0 or r.open_count <> 0 or r.suspended_count <> 0 or r.delisted_count <> 0 then
    raise exception 'EMPTY 상태별 카운트 mismatch: %', row_to_json(r);
  end if;
  if r.sample_gate_passed <> false then
    raise exception 'EMPTY sample_gate_passed should be false: view=%', r.sample_gate_passed;
  end if;
  if r.sample_gate_label is distinct from '표본 부족 (0/30)' then
    raise exception 'EMPTY sample_gate_label mismatch: view=%', r.sample_gate_label;
  end if;
  if r.win_rate is not null or r.profit_factor is not null then
    raise exception 'EMPTY win_rate/profit_factor should be NULL: %', row_to_json(r);
  end if;
  raise notice 'story 5-7 EMPTY scenario: pass';
end $$;
rollback;
