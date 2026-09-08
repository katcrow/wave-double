-- Story 3.2 emit_open_command fixture. All writes are rolled back.
begin;

do $$
declare
  v_result jsonb;
  v_result2 jsonb;
  v_result3 jsonb;
  v_event_id uuid;
  v_outcome_id uuid;
  v_caught boolean;
  v_event_count integer;
  v_outcome_count integer;
  v_result4 jsonb;
  v_result5 jsonb;
  v_result8 jsonb;
  v_result9 jsonb;
  v_result10 jsonb;
  v_preexisting_outcome_id uuid;
begin
  insert into public.logical_runs(logical_run_key, trading_day, batch_kind)
  values
    ('close:2099-07-01', date '2099-07-01', 'close'),
    ('close:2099-07-02', date '2099-07-02', 'close'),
    ('intraday:2099-07-01:09:30', date '2099-07-01', 'intraday')
  on conflict (logical_run_key) do nothing;

  -- ZZTEST1/A has a close-day OHLCV row; ZZTEST2/B (missing daily_ohlcv scenario) does not.
  -- Fake, non-real tickers are used so this fixture is safe to run against a database that
  -- already holds real production outcome data (real KRX tickers are 6-digit codes).
  insert into public.daily_ohlcv(ticker, trading_day, open, high, low, close, volume)
  values
    ('ZZTEST1', date '2099-07-01', 100, 105, 99, 101, 1000),
    ('ZZTEST1', date '2099-07-02', 100, 105, 99, 102, 1000),
    ('ZZTEST3', date '2099-07-01', 200, 205, 199, 201, 1000),
    ('ZZTEST4', date '2099-07-01', 300, 305, 299, 301, 1000),
    ('ZZTEST7', date '2099-07-01', 400, 405, 399, 401, 1000),
    ('ZZTEST8', date '2099-07-01', 500, 505, 499, 501, 1000),
    ('ZZTEST9', date '2099-07-01', 600, 605, 599, 601, 1000)
  on conflict (ticker, trading_day) do nothing;

  -- Scenario: 최초 발행.
  v_result := public.emit_open_command('close:2099-07-01', 'ZZTEST1', 'A');
  if (v_result->>'replayed')::boolean is distinct from false
     or (v_result->>'skipped')::boolean is distinct from false
     or v_result->>'event_id' is null
     or v_result->>'outcome_id' is null
     or (v_result->>'entry_date')::date <> date '2099-07-01'
     or (v_result->>'entry_price')::numeric <> 101 then
    raise exception 'initial emit_open_command result mismatch: %', v_result;
  end if;
  v_event_id := (v_result->>'event_id')::uuid;
  v_outcome_id := (v_result->>'outcome_id')::uuid;

  select count(*) into v_event_count from public.outcome_events
    where logical_run_key = 'close:2099-07-01' and ticker = 'ZZTEST1' and strategy = 'A' and command_type = 'OPEN';
  if v_event_count <> 1 then raise exception 'expected exactly one OPEN event, got %', v_event_count; end if;

  if not exists (
    select 1 from public.candidate_outcome
    where outcome_id = v_outcome_id and ticker = 'ZZTEST1' and strategy = 'A'
      and entry_date = date '2099-07-01' and entry_price = 101 and status = 'OPEN'
  ) then raise exception 'candidate_outcome projection row missing or mismatched after initial emit'; end if;
  if not exists (
    select 1 from public.outcome_events
    where event_id = v_event_id and payload @> '{"tp_pct":3.0,"sl_pct":3.0,"cutoff_n":30}'::jsonb
  ) then raise exception 'A OPEN payload strategy parameters were not snapshotted'; end if;

  -- Story 6.5: D/E도 OPEN 시점의 전략별 청산 파라미터를 원장과 projection에 함께 고정한다.
  v_result8 := public.emit_open_command('close:2099-07-01', 'ZZTEST7', 'D');
  v_result9 := public.emit_open_command('close:2099-07-01', 'ZZTEST8', 'E');
  if (v_result8->>'skipped')::boolean is distinct from false
     or (v_result8->>'tp_pct')::numeric <> 3.0
     or (v_result8->>'sl_pct')::numeric <> 5.0
     or (v_result8->>'cutoff_n')::integer <> 20 then
    raise exception 'D OPEN strategy parameters mismatch: %', v_result8;
  end if;
  if (v_result9->>'skipped')::boolean is distinct from false
     or (v_result9->>'tp_pct')::numeric <> 2.0
     or (v_result9->>'sl_pct')::numeric <> 5.0
     or (v_result9->>'cutoff_n')::integer <> 30 then
    raise exception 'E OPEN strategy parameters mismatch: %', v_result9;
  end if;
  if not exists (
    select 1 from public.candidate_outcome
    where ticker = 'ZZTEST7' and strategy = 'D' and tp_pct = 3.0 and sl_pct = 5.0 and cutoff_n = 20
  ) or not exists (
    select 1 from public.candidate_outcome
    where ticker = 'ZZTEST8' and strategy = 'E' and tp_pct = 2.0 and sl_pct = 5.0 and cutoff_n = 30
  ) then raise exception 'D/E candidate_outcome parameters were not snapshotted'; end if;
  if not exists (
    select 1 from public.outcome_events
    where ticker = 'ZZTEST7' and strategy = 'D' and command_type = 'OPEN'
      and payload @> '{"tp_pct":3.0,"sl_pct":5.0,"cutoff_n":20}'::jsonb
  ) or not exists (
    select 1 from public.outcome_events
    where ticker = 'ZZTEST8' and strategy = 'E' and command_type = 'OPEN'
      and payload @> '{"tp_pct":2.0,"sl_pct":5.0,"cutoff_n":30}'::jsonb
  ) then raise exception 'D/E OPEN payload parameters were not snapshotted'; end if;

  -- Story 7.4: F도 OPEN 시점의 전략별 청산 파라미터(TP 3%/SL 4%/cutoff_n sentinel 999999
  -- = 무제한 보유)를 원장과 projection에 함께 고정한다.
  v_result10 := public.emit_open_command('close:2099-07-01', 'ZZTEST9', 'F');
  if (v_result10->>'skipped')::boolean is distinct from false
     or (v_result10->>'tp_pct')::numeric <> 3.0
     or (v_result10->>'sl_pct')::numeric <> 4.0
     or (v_result10->>'cutoff_n')::integer <> 999999 then
    raise exception 'F OPEN strategy parameters mismatch: %', v_result10;
  end if;
  if not exists (
    select 1 from public.candidate_outcome
    where ticker = 'ZZTEST9' and strategy = 'F' and tp_pct = 3.0 and sl_pct = 4.0 and cutoff_n = 999999
  ) then raise exception 'F candidate_outcome parameters were not snapshotted'; end if;
  if not exists (
    select 1 from public.outcome_events
    where ticker = 'ZZTEST9' and strategy = 'F' and command_type = 'OPEN'
      and payload @> '{"tp_pct":3.0,"sl_pct":4.0,"cutoff_n":999999}'::jsonb
  ) then raise exception 'F OPEN payload parameters were not snapshotted'; end if;

  -- Story 7.4: F도 동일-key replay 시 rule 행이 일시적으로 없어도 저장된 snapshot을 그대로 반환한다.
  delete from public.outcome_strategy_rules where strategy = 'F';
  v_result10 := public.emit_open_command('close:2099-07-01', 'ZZTEST9', 'F');
  if (v_result10->>'replayed')::boolean is distinct from true
     or (v_result10->>'outcome_id')::uuid is null
     or (v_result10->>'tp_pct')::numeric <> 3.0
     or (v_result10->>'sl_pct')::numeric <> 4.0
     or (v_result10->>'cutoff_n')::integer <> 999999 then
    raise exception 'F replay must return stored snapshot without rule lookup: %', v_result10;
  end if;
  insert into public.outcome_strategy_rules(strategy, tp_pct, sl_pct, cutoff_n)
  values ('F', 3.0, 4.0, 999999);

  -- 기존 동일-key replay는 rule row가 일시적으로 없어도 저장된 snapshot을 반환한다.
  delete from public.outcome_strategy_rules where strategy = 'D';
  v_result8 := public.emit_open_command('close:2099-07-01', 'ZZTEST7', 'D');
  if (v_result8->>'replayed')::boolean is distinct from true
     or (v_result8->>'outcome_id')::uuid is null
     or (v_result8->>'tp_pct')::numeric <> 3.0
     or (v_result8->>'sl_pct')::numeric <> 5.0
     or (v_result8->>'cutoff_n')::integer <> 20 then
    raise exception 'D replay must return stored snapshot without rule lookup: %', v_result8;
  end if;
  insert into public.outcome_strategy_rules(strategy, tp_pct, sl_pct, cutoff_n)
  values ('D', 3.0, 5.0, 20);

  -- Mutate daily_ohlcv after publication to prove entry_price is fixed at OPEN time,
  -- not recomputed on replay.
  update public.daily_ohlcv set close = 999 where ticker = 'ZZTEST1' and trading_day = date '2099-07-01';

  -- Scenario: 동일 key 재호출 -> replay, no new rows, unchanged entry_price.
  v_result2 := public.emit_open_command('close:2099-07-01', 'ZZTEST1', 'A');
  if (v_result2->>'replayed')::boolean is distinct from true
     or (v_result2->>'skipped')::boolean is distinct from false
     or (v_result2->>'event_id')::uuid <> v_event_id
     or (v_result2->>'outcome_id')::uuid <> v_outcome_id
     or (v_result2->>'entry_price')::numeric <> 101 then
    raise exception 'replayed emit_open_command result mismatch: %', v_result2;
  end if;

  select count(*) into v_event_count from public.outcome_events
    where logical_run_key = 'close:2099-07-01' and ticker = 'ZZTEST1' and strategy = 'A' and command_type = 'OPEN';
  if v_event_count <> 1 then raise exception 'replay must not create a new event, got count %', v_event_count; end if;

  select count(*) into v_outcome_count from public.candidate_outcome where outcome_id = v_outcome_id;
  if v_outcome_count <> 1 then raise exception 'replay must not create a new projection row'; end if;

  -- Scenario: 재진입 금지 -- different (next) trading day's close batch, same (ticker,strategy) still OPEN.
  v_result3 := public.emit_open_command('close:2099-07-02', 'ZZTEST1', 'A');
  if (v_result3->>'replayed')::boolean is distinct from false
     or (v_result3->>'skipped')::boolean is distinct from true
     or v_result3->>'reason' <> 'ALREADY_OPEN'
     or (v_result3->>'outcome_id')::uuid <> v_outcome_id then
    raise exception 'reentry guard result mismatch: %', v_result3;
  end if;

  select count(*) into v_event_count from public.outcome_events
    where ticker = 'ZZTEST1' and strategy = 'A' and command_type = 'OPEN';
  if v_event_count <> 1 then raise exception 'reentry attempt must not create a new event, got count %', v_event_count; end if;

  select count(*) into v_outcome_count from public.candidate_outcome where ticker = 'ZZTEST1' and strategy = 'A';
  if v_outcome_count <> 1 then raise exception 'reentry attempt must not create a new projection row'; end if;

  -- Scenario: 장중 배치 오호출.
  v_caught := false;
  begin
    perform public.emit_open_command('intraday:2099-07-01:09:30', 'ZZTEST1', 'A');
  exception when others then
    if sqlerrm = 'OPEN_COMMAND_REQUIRES_CLOSE_BATCH' then v_caught := true; else raise; end if;
  end;
  if not v_caught then raise exception 'intraday logical_run_key was accepted'; end if;

  -- Scenario: 종가 데이터 없음.
  v_caught := false;
  begin
    perform public.emit_open_command('close:2099-07-01', 'ZZTEST2', 'B');
  exception when others then
    if sqlerrm = 'MISSING_DAILY_OHLCV_CLOSE' then v_caught := true; else raise; end if;
  end;
  if not v_caught then raise exception 'missing daily_ohlcv close was accepted'; end if;

  -- Scenario: 미지원 전략. D/E/F는 Epic 6.5/7.4에서 지원되므로 진짜 미정의 코드('G')만
  -- 거부되어야 한다.
  v_caught := false;
  begin
    perform public.emit_open_command('close:2099-07-01', 'ZZTEST1', 'G');
  exception when others then
    if sqlerrm = 'INVALID_STRATEGY' then v_caught := true; else raise; end if;
  end;
  if not v_caught then raise exception 'unsupported strategy was accepted'; end if;

  -- Scenario: NULL 전략 (fix #1 -- `not in` with NULL is NULL, not TRUE, so the guard must
  -- explicitly check `is null` too, else this falls through to a NOT NULL constraint error).
  v_caught := false;
  begin
    perform public.emit_open_command('close:2099-07-01', 'ZZTEST1', null);
  exception when others then
    if sqlerrm = 'INVALID_STRATEGY' then v_caught := true; else raise; end if;
  end;
  if not v_caught then raise exception 'NULL strategy was accepted'; end if;

  -- Scenario: 동시 삽입 경쟁 (fix #2) -- simulate a losing concurrent call by pre-seeding a
  -- candidate_outcome OPEN row for (ticker,strategy) whose entry_date equals this call's
  -- trading_day. The pre-check does not fire (entry_date matches), so the function proceeds
  -- to insert a new outcome_events row (succeeds) and then a new candidate_outcome row, which
  -- collides with the pre-seeded OPEN row on the one-open-per-ticker-strategy unique index.
  -- The exception handler must catch that unique_violation and return the ALREADY_OPEN skip
  -- shape (with event_id, since the event insert did succeed) instead of raising.
  insert into public.candidate_outcome(ticker, strategy, entry_date, entry_price, status)
    values ('ZZTEST3', 'A', date '2099-07-01', 201, 'OPEN')
    returning outcome_id into v_preexisting_outcome_id;

  v_result4 := public.emit_open_command('close:2099-07-01', 'ZZTEST3', 'A');
  if (v_result4->>'replayed')::boolean is distinct from false
     or (v_result4->>'skipped')::boolean is distinct from true
     or v_result4->>'reason' <> 'ALREADY_OPEN'
     or v_result4->>'event_id' is null
     or (v_result4->>'outcome_id')::uuid <> v_preexisting_outcome_id
     or (v_result4->>'entry_price')::numeric <> 201 then
    raise exception 'concurrent-insert race result mismatch: %', v_result4;
  end if;

  select count(*) into v_event_count from public.outcome_events
    where logical_run_key = 'close:2099-07-01' and ticker = 'ZZTEST3' and strategy = 'A' and command_type = 'OPEN';
  if v_event_count <> 1 then
    raise exception 'concurrent-insert race must still record the submitted command event, got count %', v_event_count;
  end if;

  select count(*) into v_outcome_count from public.candidate_outcome where ticker = 'ZZTEST3' and strategy = 'A';
  if v_outcome_count <> 1 then
    raise exception 'concurrent-insert race must not create a duplicate OPEN projection row, got count %', v_outcome_count;
  end if;

  -- Scenario: projection drift on replay (fix #4) -- an outcome_events row exists for the
  -- command key, but its matching candidate_outcome projection row is missing. The replay
  -- branch must raise a clear error (OUTCOME_PROJECTION_MISSING) instead of silently
  -- returning nulls.
  v_result5 := public.emit_open_command('close:2099-07-01', 'ZZTEST4', 'C');
  if (v_result5->>'replayed')::boolean is distinct from false
     or (v_result5->>'skipped')::boolean is distinct from false
     or v_result5->>'outcome_id' is null then
    raise exception 'ZZTEST4 initial emit_open_command result mismatch: %', v_result5;
  end if;

  delete from public.candidate_outcome where outcome_id = (v_result5->>'outcome_id')::uuid;

  v_caught := false;
  begin
    perform public.emit_open_command('close:2099-07-01', 'ZZTEST4', 'C');
  exception when others then
    if sqlerrm = 'OUTCOME_PROJECTION_MISSING' then v_caught := true; else raise; end if;
  end;
  if not v_caught then raise exception 'projection drift on replay was not detected'; end if;

  -- Scenario (Story 3.8): SUSPENDED 재태깅 -- (ticker,strategy)가 SUSPENDED 상태일 때 다음
  -- close 배치가 같은 종목을 다시 태깅해도 신규 OPEN/candidate_outcome 중복 행이 생기지 않고
  -- ALREADY_TRACKED_SUSPENDED로 skip해야 한다(진입일과 무관하게 항상 skip).
  declare
    v_suspended_outcome_id uuid;
    v_result6 jsonb;
  begin
    -- emit_open_command checks daily_ohlcv for a close price before it reaches the reentry
    -- guard, so ZZTEST5 needs a close-day row on 2099-07-02 too, else it would fail earlier
    -- with MISSING_DAILY_OHLCV_CLOSE and never reach the ALREADY_TRACKED_SUSPENDED branch.
    insert into public.daily_ohlcv(ticker, trading_day, open, high, low, close, volume)
      values ('ZZTEST5', date '2099-07-02', 50, 55, 49, 51, 1000)
      on conflict (ticker, trading_day) do nothing;

    insert into public.outcome_events(ticker, strategy, command_type, logical_run_key, payload)
      values ('ZZTEST5', 'A', 'OPEN', 'close:2099-07-01', jsonb_build_object('entry_date', date '2099-07-01', 'entry_price', 50));
    insert into public.candidate_outcome(ticker, strategy, entry_date, entry_price, status)
      values ('ZZTEST5', 'A', date '2099-07-01', 50, 'SUSPENDED')
      returning outcome_id into v_suspended_outcome_id;

    v_result6 := public.emit_open_command('close:2099-07-02', 'ZZTEST5', 'A');
    if (v_result6->>'replayed')::boolean is distinct from false
       or (v_result6->>'skipped')::boolean is distinct from true
       or v_result6->>'reason' <> 'ALREADY_TRACKED_SUSPENDED'
       or (v_result6->>'outcome_id')::uuid <> v_suspended_outcome_id then
      raise exception 'SUSPENDED re-tagging skip result mismatch: %', v_result6;
    end if;

    select count(*) into v_event_count from public.outcome_events
      where ticker = 'ZZTEST5' and strategy = 'A' and command_type = 'OPEN';
    if v_event_count <> 1 then raise exception 'SUSPENDED re-tagging must not create a new OPEN event, got count %', v_event_count; end if;

    select count(*) into v_outcome_count from public.candidate_outcome where ticker = 'ZZTEST5' and strategy = 'A';
    if v_outcome_count <> 1 then raise exception 'SUSPENDED re-tagging must not create a duplicate candidate_outcome row, got count %', v_outcome_count; end if;

    if (select status from public.candidate_outcome where outcome_id = v_suspended_outcome_id) <> 'SUSPENDED' then
      raise exception 'SUSPENDED re-tagging must not change the projection status';
    end if;
  end;

  -- Scenario (Story 3.9): DELISTED 재태깅 -- (ticker,strategy)가 DELISTED 상태일 때 다음
  -- close 배치가 같은 종목을 다시 태깅해도 신규 OPEN/candidate_outcome 중복 행이 생기지 않고
  -- ALREADY_DELISTED로 skip해야 한다(진입일과 무관하게 항상 skip).
  declare
    v_delisted_outcome_id uuid;
    v_result7 jsonb;
  begin
    -- emit_open_command checks daily_ohlcv for a close price before it reaches the reentry
    -- guard, so ZZTEST6 needs a close-day row on 2099-07-02 too, else it would fail earlier
    -- with MISSING_DAILY_OHLCV_CLOSE and never reach the ALREADY_DELISTED branch.
    insert into public.daily_ohlcv(ticker, trading_day, open, high, low, close, volume)
      values ('ZZTEST6', date '2099-07-02', 60, 65, 59, 61, 1000)
      on conflict (ticker, trading_day) do nothing;

    insert into public.outcome_events(ticker, strategy, command_type, logical_run_key, payload)
      values ('ZZTEST6', 'A', 'OPEN', 'close:2099-07-01', jsonb_build_object('entry_date', date '2099-07-01', 'entry_price', 60));
    insert into public.candidate_outcome(ticker, strategy, entry_date, entry_price, status)
      values ('ZZTEST6', 'A', date '2099-07-01', 60, 'DELISTED')
      returning outcome_id into v_delisted_outcome_id;

    v_result7 := public.emit_open_command('close:2099-07-02', 'ZZTEST6', 'A');
    if (v_result7->>'replayed')::boolean is distinct from false
       or (v_result7->>'skipped')::boolean is distinct from true
       or v_result7->>'reason' <> 'ALREADY_DELISTED'
       or (v_result7->>'outcome_id')::uuid <> v_delisted_outcome_id then
      raise exception 'DELISTED re-tagging skip result mismatch: %', v_result7;
    end if;

    select count(*) into v_event_count from public.outcome_events
      where ticker = 'ZZTEST6' and strategy = 'A' and command_type = 'OPEN';
    if v_event_count <> 1 then raise exception 'DELISTED re-tagging must not create a new OPEN event, got count %', v_event_count; end if;

    select count(*) into v_outcome_count from public.candidate_outcome where ticker = 'ZZTEST6' and strategy = 'A';
    if v_outcome_count <> 1 then raise exception 'DELISTED re-tagging must not create a duplicate candidate_outcome row, got count %', v_outcome_count; end if;

    if (select status from public.candidate_outcome where outcome_id = v_delisted_outcome_id) <> 'DELISTED' then
      raise exception 'DELISTED re-tagging must not change the projection status';
    end if;
  end;

  -- Grant/revoke: only service_role may execute.
  if exists (
    select 1
    from information_schema.role_routine_grants
    where routine_schema = 'public' and routine_name = 'emit_open_command'
      and grantee in ('PUBLIC', 'anon', 'authenticated')
  ) then raise exception 'emit_open_command must not be executable by public/anon/authenticated'; end if;

  if not exists (
    select 1
    from information_schema.role_routine_grants
    where routine_schema = 'public' and routine_name = 'emit_open_command'
      and grantee = 'service_role' and privilege_type = 'EXECUTE'
  ) then raise exception 'emit_open_command must be executable by service_role'; end if;
end $$;

select 'outcome_open_command' as fixture, 'pass' as result;
rollback;
