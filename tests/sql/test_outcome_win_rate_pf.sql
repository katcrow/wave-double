-- Story 5.5: 전체 기준 승률·PF 산식 view 검증. candidate_outcome에 fixture 행을 삽입하고
-- view 조회 결과를 기대 튜플과 대조한다. 모든 변경은 rollback으로 되돌린다.
-- parity 도구는 parity fixture setup 마커 아래의 candidate_outcome INSERT만 파싱한다.
begin;
-- ── parity fixture setup
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

create temp table win_pf_expected (
  total_settled int, wins int, losses int,
  open_count int, suspended_count int, delisted_count int,
  gross_win numeric, gross_loss numeric,
  win_rate numeric, profit_factor numeric
);
insert into win_pf_expected values (6, 3, 3, 1, 1, 1, 6.4, 9.0, 0.5000, 0.7111);

do $$
declare
  r record;
  e win_pf_expected;
  msg text;
begin
  select * into r from public.candidate_outcome_win_rate_pf;
  select * into e from win_pf_expected;

  if r.total_settled <> e.total_settled then
    msg := format('total_settled mismatch: view=%s expected=%s', r.total_settled, e.total_settled);
    raise exception '%', msg;
  end if;
  if r.wins <> e.wins then
    msg := format('wins mismatch: view=%s expected=%s', r.wins, e.wins);
    raise exception '%', msg;
  end if;
  if r.losses <> e.losses then
    msg := format('losses mismatch: view=%s expected=%s', r.losses, e.losses);
    raise exception '%', msg;
  end if;
  if r.open_count <> e.open_count then
    msg := format('open_count mismatch: view=%s expected=%s', r.open_count, e.open_count);
    raise exception '%', msg;
  end if;
  if r.suspended_count <> e.suspended_count then
    msg := format('suspended_count mismatch: view=%s expected=%s', r.suspended_count, e.suspended_count);
    raise exception '%', msg;
  end if;
  if r.delisted_count <> e.delisted_count then
    msg := format('delisted_count mismatch: view=%s expected=%s', r.delisted_count, e.delisted_count);
    raise exception '%', msg;
  end if;
  if r.win_rate is distinct from e.win_rate then
    msg := format('win_rate mismatch: view=%s expected=%s', r.win_rate, e.win_rate);
    raise exception '%', msg;
  end if;
  if r.gross_win is distinct from e.gross_win then
    msg := format('gross_win mismatch: view=%s expected=%s', r.gross_win, e.gross_win);
    raise exception '%', msg;
  end if;
  if r.gross_loss is distinct from e.gross_loss then
    msg := format('gross_loss mismatch: view=%s expected=%s', r.gross_loss, e.gross_loss);
    raise exception '%', msg;
  end if;
  if r.profit_factor is distinct from e.profit_factor then
    msg := format('profit_factor mismatch: view=%s expected=%s', r.profit_factor, e.profit_factor);
    raise exception '%', msg;
  end if;

  raise notice 'story 5-5 view assertion: all fields match';
end $$;

-- ── edge case 시나리오(parity 파서 대상 아님: 각 시나리오가 전체 테이블을 재구성하므로
--    main parity INSERT와 분리된 do 블록으로만 처리한다. 전부 rollback으로 되돌린다.)

-- ZERO_RETURN: return_pct = 0인 종결 건은 분모에 포함되고 승/패 어느 쪽에도 세지 않는다.
do $$
declare
  r record;
begin
  delete from public.candidate_outcome;
  insert into public.candidate_outcome(ticker, strategy, entry_date, entry_price, status, exit_date, exit_price, return_pct, cutoff_n, holding_days, tp_pct, sl_pct) values
  ('A1001', 'A', '2098-06-01', 1000, 'TP', '2098-06-03', 1020, 2.0, 30, 2, 3.0, 3.0),
  ('A1002', 'B', '2098-06-01', 2000, 'SL', '2098-06-03', 1960, -2.0, 30, 2, 3.0, 3.0),
  ('A1003', 'C', '2098-06-02', 3000, 'TIMEOUT', '2098-07-02', 3000, 0.0, 30, 30, 3.0, 3.0);
  select * into r from public.candidate_outcome_win_rate_pf;
  if r.total_settled <> 3 then
    raise exception 'ZERO_RETURN total_settled mismatch: view=% expected=3', r.total_settled;
  end if;
  if r.wins <> 1 then
    raise exception 'ZERO_RETURN wins mismatch: view=% expected=1', r.wins;
  end if;
  if r.losses <> 1 then
    raise exception 'ZERO_RETURN losses mismatch: view=% expected=1', r.losses;
  end if;
  if r.win_rate <> 0.3333 then
    raise exception 'ZERO_RETURN win_rate mismatch: view=% expected=0.3333', r.win_rate;
  end if;
  if r.profit_factor is distinct from 1.0000 then
    raise exception 'ZERO_RETURN profit_factor mismatch: view=% expected=1.0000', r.profit_factor;
  end if;
  raise notice 'story 5-5 ZERO_RETURN scenario: pass';
end $$;

-- ALL_WIN: 손실 없이 승만 있으면 gross_loss가 없어 profit_factor는 NULL이어야 한다.
do $$
declare
  r record;
begin
  delete from public.candidate_outcome;
  insert into public.candidate_outcome(ticker, strategy, entry_date, entry_price, status, exit_date, exit_price, return_pct, cutoff_n, holding_days, tp_pct, sl_pct) values
  ('A2001', 'A', '2098-06-01', 1000, 'TP', '2098-06-03', 1020, 2.0, 30, 2, 3.0, 3.0),
  ('A2002', 'B', '2098-06-01', 2000, 'TP', '2098-06-03', 2020, 1.0, 30, 2, 3.0, 3.0);
  select * into r from public.candidate_outcome_win_rate_pf;
  if r.total_settled <> 2 then
    raise exception 'ALL_WIN total_settled mismatch: view=% expected=2', r.total_settled;
  end if;
  if r.wins <> 2 then
    raise exception 'ALL_WIN wins mismatch: view=% expected=2', r.wins;
  end if;
  if r.losses <> 0 then
    raise exception 'ALL_WIN losses mismatch: view=% expected=0', r.losses;
  end if;
  if r.win_rate <> 1.0000 then
    raise exception 'ALL_WIN win_rate mismatch: view=% expected=1.0000', r.win_rate;
  end if;
  if r.gross_loss is not null then
    raise exception 'ALL_WIN gross_loss should be NULL: view=%', r.gross_loss;
  end if;
  if r.profit_factor is not null then
    raise exception 'ALL_WIN profit_factor should be NULL: view=%', r.profit_factor;
  end if;
  raise notice 'story 5-5 ALL_WIN scenario: pass';
end $$;

-- EMPTY: settled 분모가 0이면 카운트는 0, win_rate/profit_factor는 NULL이어야 한다.
do $$
declare
  r record;
begin
  delete from public.candidate_outcome;
  select * into r from public.candidate_outcome_win_rate_pf;
  if r.total_settled <> 0 then
    raise exception 'EMPTY total_settled mismatch: view=% expected=0', r.total_settled;
  end if;
  if r.wins <> 0 then
    raise exception 'EMPTY wins mismatch: view=% expected=0', r.wins;
  end if;
  if r.losses <> 0 then
    raise exception 'EMPTY losses mismatch: view=% expected=0', r.losses;
  end if;
  if r.open_count <> 0 or r.suspended_count <> 0 or r.delisted_count <> 0 then
    raise exception 'EMPTY 상태별 카운트 mismatch: %', row_to_json(r);
  end if;
  if r.win_rate is not null then
    raise exception 'EMPTY win_rate should be NULL: view=%', r.win_rate;
  end if;
  if r.profit_factor is not null then
    raise exception 'EMPTY profit_factor should be NULL: view=%', r.profit_factor;
  end if;
  raise notice 'story 5-5 EMPTY scenario: pass';
end $$;
rollback;
