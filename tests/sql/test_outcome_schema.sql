-- Story 3.1 schema contract fixture. All writes are rolled back.
begin;

do $$
declare
  v_outcome_id uuid := gen_random_uuid();
  v_event_id uuid;
  v_columns text[];
  v_column_types text[];
  v_caught boolean;
begin
  insert into public.logical_runs(logical_run_key, trading_day, batch_kind)
  values ('close:2099-06-01', date '2099-06-01', 'close')
  on conflict (logical_run_key) do nothing;

  -- Catalog shape, key, and lineage contracts.
  select array_agg(column_name::text order by ordinal_position)
    into v_columns
  from information_schema.columns
  where table_schema = 'public' and table_name = 'outcome_events';
  if v_columns <> array['event_id','ticker','strategy','command_type','logical_run_key','payload','created_at'] then
    raise exception 'outcome_events columns mismatch: %', v_columns;
  end if;
  select array_agg(data_type::text order by ordinal_position)
    into v_column_types
  from information_schema.columns
  where table_schema = 'public' and table_name = 'outcome_events';
  if v_column_types <> array['uuid','text','text','text','text','jsonb','timestamp with time zone'] then
    raise exception 'outcome_events column types mismatch: %', v_column_types;
  end if;

  select array_agg(column_name::text order by ordinal_position)
    into v_columns
  from information_schema.columns
  where table_schema = 'public' and table_name = 'outcome_observations';
  if v_columns <> array['outcome_id','evaluation_trading_day','high','low','close','result_code'] then
    raise exception 'outcome_observations columns mismatch: %', v_columns;
  end if;
  select array_agg(data_type::text order by ordinal_position)
    into v_column_types
  from information_schema.columns
  where table_schema = 'public' and table_name = 'outcome_observations';
  if v_column_types <> array['uuid','date','numeric','numeric','numeric','text'] then
    raise exception 'outcome_observations column types mismatch: %', v_column_types;
  end if;

  select array_agg(column_name::text order by ordinal_position)
    into v_columns
  from information_schema.columns
  where table_schema = 'public' and table_name = 'candidate_outcome';
  -- Story 3.8 added version; Story 6.5 appends the immutable exit-rule snapshot.
  if v_columns <> array['outcome_id','ticker','strategy','entry_date','entry_price','status','exit_date','exit_price','return_pct','cutoff_n','holding_days','version','tp_pct','sl_pct'] then
    raise exception 'candidate_outcome columns mismatch: %', v_columns;
  end if;
  select array_agg(data_type::text order by ordinal_position)
    into v_column_types
  from information_schema.columns
  where table_schema = 'public' and table_name = 'candidate_outcome';
  if v_column_types <> array['uuid','text','text','date','numeric','text','date','numeric','numeric','integer','integer','integer','numeric','numeric'] then
    raise exception 'candidate_outcome column types mismatch: %', v_column_types;
  end if;

  if (select count(*) from public.outcome_strategy_rules) <> 6 then
    raise exception 'outcome_strategy_rules must contain exactly A/B/C/D/E/F';
  end if;
  if exists (
    select 1 from public.outcome_strategy_rules
    where (strategy in ('A','B','C') and (tp_pct, sl_pct, cutoff_n) <> (3.0, 3.0, 30))
       or (strategy = 'D' and (tp_pct, sl_pct, cutoff_n) <> (3.0, 5.0, 20))
       or (strategy = 'E' and (tp_pct, sl_pct, cutoff_n) <> (2.0, 5.0, 30))
       or (strategy = 'F' and (tp_pct, sl_pct, cutoff_n) <> (3.0, 4.0, 999999))
  ) then raise exception 'outcome_strategy_rules values mismatch'; end if;

  -- sl_pct의 rule 범위는 candidate_outcome.exit_price가 양수가 되는 범위와 일치해야 한다.
  v_caught := false;
  begin
    update public.outcome_strategy_rules set sl_pct = 100 where strategy = 'D';
  exception when check_violation then v_caught := true;
  end;
  if not v_caught then raise exception 'outcome_strategy_rules accepted sl_pct >= 100'; end if;

  if (
    select array_agg(kcu.column_name::text order by kcu.ordinal_position)
    from information_schema.table_constraints tc
    join information_schema.key_column_usage kcu
      on kcu.constraint_name = tc.constraint_name and kcu.constraint_schema = tc.constraint_schema
    where tc.table_schema = 'public' and tc.table_name = 'outcome_events' and tc.constraint_type = 'PRIMARY KEY'
  ) <> array['event_id'] then
    raise exception 'outcome_events primary key mismatch';
  end if;

  if (
    select array_agg(kcu.column_name::text order by kcu.ordinal_position)
    from information_schema.table_constraints tc
    join information_schema.key_column_usage kcu
      on kcu.constraint_name = tc.constraint_name and kcu.constraint_schema = tc.constraint_schema
    where tc.table_schema = 'public' and tc.table_name = 'outcome_observations' and tc.constraint_type = 'PRIMARY KEY'
  ) <> array['outcome_id','evaluation_trading_day'] then
    raise exception 'outcome_observations primary key mismatch';
  end if;

  if (
    select array_agg(kcu.column_name::text order by kcu.ordinal_position)
    from information_schema.table_constraints tc
    join information_schema.key_column_usage kcu
      on kcu.constraint_name = tc.constraint_name and kcu.constraint_schema = tc.constraint_schema
    where tc.table_schema = 'public' and tc.table_name = 'candidate_outcome' and tc.constraint_type = 'PRIMARY KEY'
  ) <> array['outcome_id'] then
    raise exception 'candidate_outcome primary key mismatch';
  end if;

  if not exists (
    select 1
    from information_schema.table_constraints tc
    where tc.table_schema = 'public' and tc.table_name = 'candidate_outcome'
      and tc.constraint_type = 'UNIQUE'
      and (
        select array_agg(kcu.column_name::text order by kcu.ordinal_position)
        from information_schema.key_column_usage kcu
        where kcu.constraint_schema = tc.constraint_schema and kcu.constraint_name = tc.constraint_name
      ) = array['ticker','strategy','entry_date']
  ) then raise exception 'candidate_outcome (ticker,strategy,entry_date) unique constraint missing'; end if;

  if not exists (
    select 1
    from information_schema.table_constraints tc
    join information_schema.constraint_column_usage ccu
      on ccu.constraint_name = tc.constraint_name and ccu.constraint_schema = tc.constraint_schema
    where tc.table_schema = 'public' and tc.table_name = 'outcome_events'
      and tc.constraint_type = 'FOREIGN KEY'
      and ccu.table_schema = 'public' and ccu.table_name = 'logical_runs'
      and ccu.column_name = 'logical_run_key'
  ) then raise exception 'outcome_events.logical_run_key lineage FK missing'; end if;

  if not exists (
    select 1 from pg_indexes
    where schemaname = 'public' and tablename = 'candidate_outcome'
      and indexname = 'candidate_outcome_one_open_per_ticker_strategy_idx'
      and indexdef like '%UNIQUE%ticker, strategy%WHERE (status = ''OPEN''::text)%'
  ) then raise exception 'candidate_outcome OPEN partial unique index missing or malformed'; end if;

  if exists (
    select 1 from information_schema.columns
    where table_schema = 'public' and table_name = 'candidate_outcome'
      and column_name in ('source', 'source_jsonb')
  ) then raise exception 'candidate_outcome must not contain source/source_jsonb'; end if;

  if exists (
    select 1 from information_schema.table_constraints
    where table_schema = 'public' and table_name = 'outcome_observations'
      and constraint_type = 'FOREIGN KEY'
  ) then raise exception 'outcome_observations must not depend on rebuildable projection by FK'; end if;

  if (
    select count(*) from pg_trigger t
    join pg_class c on c.oid = t.tgrelid
    join pg_namespace n on n.oid = c.relnamespace
    where n.nspname = 'public' and c.relname in ('outcome_events','outcome_observations')
      and t.tgname in ('outcome_events_append_only','outcome_events_append_only_truncate',
                       'outcome_observations_append_only','outcome_observations_append_only_truncate')
      and not t.tgisinternal and t.tgenabled <> 'D'
  ) <> 4 then raise exception 'both ledgers must have active append-only UPDATE/DELETE and TRUNCATE triggers'; end if;

  -- RLS is deny-all for browser roles: enabled with no policies.
  if exists (
    select 1 from unnest(array['outcome_events','outcome_observations','candidate_outcome']) table_name
    where not coalesce((
      select c.relrowsecurity from pg_class c join pg_namespace n on n.oid = c.relnamespace
      where n.nspname = 'public' and c.relname = table_name
    ), false)
  ) then raise exception 'all outcome tables must have RLS enabled'; end if;

  if exists (
    select 1 from pg_policies
    where schemaname = 'public' and tablename in ('outcome_events','outcome_observations','candidate_outcome')
  ) then raise exception 'outcome tables must have zero RLS policies'; end if;

  -- Valid rows and defaults.
  insert into public.outcome_events(ticker, strategy, command_type, logical_run_key, payload)
  values ('005930', 'A', 'OPEN', 'close:2099-06-01', '{"outcome_id":"fixture"}'::jsonb)
  returning event_id into v_event_id;
  if v_event_id is null then raise exception 'outcome_events UUID default missing'; end if;

  insert into public.outcome_observations(outcome_id, evaluation_trading_day, high, low, close, result_code)
  values (v_outcome_id, date '2099-06-02', 103, 97, 101, 'NO_HIT');

  v_caught := false;
  begin
    insert into public.outcome_observations(outcome_id, evaluation_trading_day, high, low, close, result_code)
    values (v_outcome_id, date '2099-06-02', 103, 97, 101, 'NO_HIT');
  exception when unique_violation then v_caught := true;
  end;
  if not v_caught then raise exception 'duplicate observation identity was accepted'; end if;

  insert into public.candidate_outcome(outcome_id, ticker, strategy, entry_date, entry_price, status)
  values (v_outcome_id, '005930', 'A', date '2099-06-01', 100, 'OPEN');
  if not exists (
    select 1 from public.candidate_outcome
    where outcome_id = v_outcome_id and cutoff_n = 30 and holding_days = 0
      and tp_pct = 3.0 and sl_pct = 3.0
  ) then raise exception 'candidate_outcome defaults mismatch'; end if;

  -- Story 6.5 review patch: D/E direct projection writes cannot bypass the
  -- strategy-specific snapshot contract.
  v_caught := false;
  begin
    insert into public.candidate_outcome(ticker, strategy, entry_date, entry_price, status)
    values ('000006', 'D', date '2099-06-01', 1, 'OPEN');
  exception when others then
    if sqlerrm = 'OUTCOME_STRATEGY_SNAPSHOT_MISMATCH' then v_caught := true; else raise; end if;
  end;
  if not v_caught then raise exception 'D strategy snapshot mismatch was accepted'; end if;

  v_caught := false;
  begin
    perform set_config('wave_double.outcome_rule_override_allowed', 'on', true);
    insert into public.candidate_outcome(ticker, strategy, entry_date, entry_price, status, tp_pct, sl_pct, cutoff_n)
    values ('000006', 'D', date '2099-06-01', 1, 'OPEN', 3, 100, 20);
  exception when others then
    if sqlstate = '23514' then v_caught := true; else raise; end if;
  end;
  if not v_caught then raise exception 'SL percentage >= 100 was accepted'; end if;

  insert into public.candidate_outcome(ticker, strategy, entry_date, entry_price, status, tp_pct, sl_pct, cutoff_n)
  values ('000006', 'D', date '2099-06-02', 1, 'OPEN', 3, 5, 20);
  v_caught := false;
  begin
    perform set_config('wave_double.outcome_mutation_allowed', 'on', true);
    update public.candidate_outcome
    set tp_pct = 2
    where ticker = '000006' and strategy = 'D' and entry_date = date '2099-06-02';
  exception when others then
    if sqlerrm = 'OUTCOME_STRATEGY_SNAPSHOT_MISMATCH' then v_caught := true; else raise; end if;
  end;
  perform set_config('wave_double.outcome_mutation_allowed', 'off', true);
  if not v_caught then raise exception 'direct candidate_outcome snapshot UPDATE was accepted'; end if;

  -- Story 7.4 review patch: F direct projection writes cannot bypass the
  -- strategy-specific snapshot contract either (guard_outcome_strategy_snapshot's
  -- cutoff_n comparison was extended from D/E to D/E/F).
  v_caught := false;
  begin
    insert into public.candidate_outcome(ticker, strategy, entry_date, entry_price, status, tp_pct, sl_pct, cutoff_n)
    values ('000008', 'F', date '2099-06-01', 1, 'OPEN', 3, 4, 1);
  exception when others then
    if sqlerrm = 'OUTCOME_STRATEGY_SNAPSHOT_MISMATCH' then v_caught := true; else raise; end if;
  end;
  if not v_caught then raise exception 'F strategy snapshot cutoff_n mismatch was accepted'; end if;

  -- A natural-key collision with an already-terminal projection must reject the
  -- OPEN ledger insert instead of leaving an orphan OPEN event behind.
  insert into public.daily_ohlcv(ticker, trading_day, open, high, low, close, volume)
  values ('000007', date '2099-06-01', 1, 1.1, 0.9, 1, 1000)
  on conflict (ticker, trading_day) do nothing;
  insert into public.candidate_outcome(ticker, strategy, entry_date, entry_price, status, exit_date, exit_price, return_pct)
  values ('000007', 'B', date '2099-06-01', 1, 'TP', date '2099-06-02', 1.03, 2.9);
  v_caught := false;
  begin
    perform public.emit_open_command('close:2099-06-01', '000007', 'B');
  exception when others then
    if sqlerrm = 'OUTCOME_PROJECTION_CONFLICT' then v_caught := true; else raise; end if;
  end;
  if not v_caught then raise exception 'terminal natural-key OPEN conflict was accepted'; end if;
  if exists (
    select 1 from public.outcome_events
    where ticker = '000007' and strategy = 'B' and command_type = 'OPEN'
  ) then raise exception 'terminal natural-key conflict left an orphan OPEN event'; end if;

  -- Ledger UPDATE and DELETE are both rejected without changing rows.
  v_caught := false;
  begin
    update public.outcome_events set payload = '{"tampered":true}' where event_id = v_event_id;
  exception when sqlstate '55000' then v_caught := true;
  end;
  if not v_caught then raise exception 'outcome_events UPDATE was accepted'; end if;

  v_caught := false;
  begin
    delete from public.outcome_events where event_id = v_event_id;
  exception when sqlstate '55000' then v_caught := true;
  end;
  if not v_caught then raise exception 'outcome_events DELETE was accepted'; end if;

  v_caught := false;
  begin
    update public.outcome_observations set close = 102 where outcome_id = v_outcome_id;
  exception when sqlstate '55000' then v_caught := true;
  end;
  if not v_caught then raise exception 'outcome_observations UPDATE was accepted'; end if;

  v_caught := false;
  begin
    delete from public.outcome_observations where outcome_id = v_outcome_id;
  exception when sqlstate '55000' then v_caught := true;
  end;
  if not v_caught then raise exception 'outcome_observations DELETE was accepted'; end if;

  if not exists (select 1 from public.outcome_events where event_id = v_event_id)
     or not exists (select 1 from public.outcome_observations where outcome_id = v_outcome_id) then
    raise exception 'append-only rejection changed ledger rows';
  end if;

  -- Only one OPEN per ticker/strategy, while distinct terminal entry history remains valid.
  v_caught := false;
  begin
    insert into public.candidate_outcome(ticker, strategy, entry_date, entry_price, status)
    values ('005930', 'A', date '2099-06-03', 102, 'OPEN');
  exception when unique_violation then v_caught := true;
  end;
  if not v_caught then raise exception 'duplicate OPEN ticker/strategy was accepted'; end if;

  -- Story 3.8 review patch: candidate_outcome_guard_mutation now rejects any UPDATE that
  -- doesn't set the wave_double.outcome_mutation_allowed session flag first. This fixture
  -- setup UPDATE isn't testing that guard itself (see test_run_lineage.sql's 3.8 block for
  -- that), so it bypasses the guard the same way publish_attempt/apply_outcome_correction do.
  perform set_config('wave_double.outcome_mutation_allowed', 'on', true);
  update public.candidate_outcome set status = 'TP', exit_date = date '2099-06-03', exit_price = 103, return_pct = 2.9, holding_days = 2
  where outcome_id = v_outcome_id;
  perform set_config('wave_double.outcome_mutation_allowed', 'off', true);
  insert into public.candidate_outcome(ticker, strategy, entry_date, entry_price, status, exit_date, exit_price, return_pct, holding_days)
  values
    ('005930', 'A', date '2099-06-04', 104, 'SL', date '2099-06-05', 100.88, -3.1, 1),
    ('005930', 'A', date '2099-06-06', 101, 'TIMEOUT', date '2099-07-16', 102, 0.89, 30),
    ('000003', 'B', date '2099-06-01', 50, 'SUSPENDED', null, null, null, 3),
    ('000004', 'C', date '2099-06-01', 60, 'DELISTED', date '2099-06-10', null, null, 7);

  v_caught := false;
  begin
    insert into public.candidate_outcome(ticker, strategy, entry_date, entry_price, status)
    values ('005930', 'A', date '2099-06-04', 104, 'TP');
  exception when unique_violation then v_caught := true;
  end;
  if not v_caught then raise exception 'duplicate projection history identity was accepted'; end if;

  -- Invalid strategies, statuses, prices, ratios, ranges, and empty extensible codes.
  v_caught := false;
  begin
    insert into public.outcome_events(ticker, strategy, command_type, logical_run_key)
    values ('000001', 'G', 'OPEN', 'close:2099-06-01');
  exception when check_violation then v_caught := true;
  end;
  if not v_caught then raise exception 'invalid event strategy was accepted'; end if;

  v_caught := false;
  begin
    insert into public.outcome_events(ticker, strategy, command_type, logical_run_key)
    values ('000001', 'A', '   ', 'close:2099-06-01');
  exception when check_violation then v_caught := true;
  end;
  if not v_caught then raise exception 'blank command_type was accepted'; end if;

  v_caught := false;
  begin
    insert into public.outcome_observations(outcome_id, evaluation_trading_day, high, low, close, result_code)
    values (gen_random_uuid(), date '2099-06-03', 'NaN'::numeric, 1, 1, 'NO_HIT');
  exception when check_violation then v_caught := true;
  end;
  if not v_caught then raise exception 'NaN observation price was accepted'; end if;

  v_caught := false;
  begin
    insert into public.outcome_observations(outcome_id, evaluation_trading_day, high, low, close, result_code)
    values (gen_random_uuid(), date '2099-06-03', 1, 'Infinity'::numeric, 1, 'NO_HIT');
  exception when check_violation then v_caught := true;
  end;
  if not v_caught then raise exception 'infinite observation price was accepted'; end if;

  v_caught := false;
  begin
    insert into public.outcome_observations(outcome_id, evaluation_trading_day, high, low, close, result_code)
    values (gen_random_uuid(), date '2099-06-03', 1, 1, 1, '   ');
  exception when check_violation then v_caught := true;
  end;
  if not v_caught then raise exception 'blank result_code was accepted'; end if;

  v_caught := false;
  begin
    insert into public.outcome_observations(outcome_id, evaluation_trading_day, high, low, close, result_code)
    values (gen_random_uuid(), date '2099-06-03', 1, 1, 0, 'NO_HIT');
  exception when check_violation then v_caught := true;
  end;
  if not v_caught then raise exception 'non-positive observation price was accepted'; end if;

  v_caught := false;
  begin
    insert into public.candidate_outcome(ticker, strategy, entry_date, entry_price, status)
    values ('000002', 'B', date '2099-06-01', 1, 'UNKNOWN');
  exception when check_violation then v_caught := true;
  end;
  if not v_caught then raise exception 'invalid outcome status was accepted'; end if;

  v_caught := false;
  begin
    insert into public.candidate_outcome(ticker, strategy, entry_date, entry_price, status)
    values ('000002', 'G', date '2099-06-01', 1, 'OPEN');
  exception when check_violation then v_caught := true;
  end;
  if not v_caught then raise exception 'invalid projection strategy was accepted'; end if;

  v_caught := false;
  begin
    insert into public.candidate_outcome(ticker, strategy, entry_date, entry_price, status)
    values ('000002', 'B', date '2099-06-01', 'Infinity'::numeric, 'OPEN');
  exception when check_violation then v_caught := true;
  end;
  if not v_caught then raise exception 'infinite entry_price was accepted'; end if;

  v_caught := false;
  begin
    insert into public.candidate_outcome(ticker, strategy, entry_date, entry_price, status, exit_price)
    values ('000002', 'B', date '2099-06-01', 1, 'TP', -1);
  exception when check_violation then v_caught := true;
  end;
  if not v_caught then raise exception 'non-positive exit_price was accepted'; end if;

  v_caught := false;
  begin
    insert into public.candidate_outcome(ticker, strategy, entry_date, entry_price, status, return_pct)
    values ('000002', 'B', date '2099-06-01', 1, 'TP', 'NaN'::numeric);
  exception when check_violation then v_caught := true;
  end;
  if not v_caught then raise exception 'NaN return_pct was accepted'; end if;

  v_caught := false;
  begin
    insert into public.candidate_outcome(ticker, strategy, entry_date, entry_price, status, cutoff_n)
    values ('000002', 'B', date '2099-06-01', 1, 'OPEN', 0);
  exception when check_violation then v_caught := true;
  end;
  if not v_caught then raise exception 'non-positive cutoff_n was accepted'; end if;

  v_caught := false;
  begin
    insert into public.candidate_outcome(ticker, strategy, entry_date, entry_price, status, holding_days)
    values ('000002', 'B', date '2099-06-01', 1, 'OPEN', -1);
  exception when check_violation then v_caught := true;
  end;
  if not v_caught then raise exception 'negative holding_days was accepted'; end if;

  -- Review follow-up: OHLC ordering, exit-before-entry, FK enforcement, TRUNCATE, and role denial.
  v_caught := false;
  begin
    insert into public.outcome_observations(outcome_id, evaluation_trading_day, high, low, close, result_code)
    values (gen_random_uuid(), date '2099-06-03', 90, 100, 95, 'NO_HIT');
  exception when check_violation then v_caught := true;
  end;
  if not v_caught then raise exception 'observation with high < low was accepted'; end if;

  v_caught := false;
  begin
    insert into public.outcome_observations(outcome_id, evaluation_trading_day, high, low, close, result_code)
    values (gen_random_uuid(), date '2099-06-03', 100, 90, 110, 'NO_HIT');
  exception when check_violation then v_caught := true;
  end;
  if not v_caught then raise exception 'observation with close outside [low,high] was accepted'; end if;

  v_caught := false;
  begin
    insert into public.candidate_outcome(ticker, strategy, entry_date, entry_price, status, exit_date)
    values ('000005', 'A', date '2099-06-05', 1, 'TP', date '2099-06-04');
  exception when check_violation then v_caught := true;
  end;
  if not v_caught then raise exception 'exit_date before entry_date was accepted'; end if;

  v_caught := false;
  begin
    insert into public.outcome_events(ticker, strategy, command_type, logical_run_key)
    values ('000001', 'A', 'OPEN', 'close:nonexistent-run-key');
  exception when foreign_key_violation then v_caught := true;
  end;
  if not v_caught then raise exception 'outcome_events with unknown logical_run_key was accepted'; end if;

  v_caught := false;
  begin
    truncate public.outcome_events;
  exception when sqlstate '55000' then v_caught := true;
  end;
  if not v_caught then raise exception 'outcome_events TRUNCATE was accepted'; end if;

  v_caught := false;
  begin
    truncate public.outcome_observations;
  exception when sqlstate '55000' then v_caught := true;
  end;
  if not v_caught then raise exception 'outcome_observations TRUNCATE was accepted'; end if;

  if exists (
    select 1 from information_schema.role_routine_grants
    where routine_schema = 'public'
      and routine_name in ('emit_open_command', 'publish_attempt', 'rebuild_outcome_projection')
      and grantee in ('PUBLIC', 'anon', 'authenticated')
  ) then raise exception 'Story 6.5 outcome functions must not be executable by browser roles'; end if;
  if (
    select count(distinct routine_name) from information_schema.role_routine_grants
    where routine_schema = 'public'
      and routine_name in ('emit_open_command', 'publish_attempt', 'rebuild_outcome_projection')
      and grantee = 'service_role' and privilege_type = 'EXECUTE'
  ) <> 3 then raise exception 'Story 6.5 outcome functions must be executable by service_role'; end if;
  if exists (
    select 1 from information_schema.role_table_grants
    where table_schema = 'public' and table_name = 'outcome_strategy_rules'
      and grantee in ('PUBLIC', 'anon', 'authenticated')
  ) then raise exception 'outcome_strategy_rules must not be readable by browser roles'; end if;

  -- daily_ohlcv 하드닝 선례와 동일하게 RLS enable + 정책 0개 catalog 검사로 anon/authenticated
  -- 접근 차단을 확인한다. 로컬 CI의 vanilla Postgres에는 anon/authenticated 역할 자체가
  -- 없어 SET ROLE로 실제 거부를 재현할 수 없고, RLS가 있고 정책이 없으면 non-bypassrls
  -- 역할은 어떤 행도 보거나 쓸 수 없다는 것이 Postgres 엔진 자체가 보장하는 동작이다.
end $$;

select 'outcome_schema_contract' as fixture, 'pass' as result;
rollback;
