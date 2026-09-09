-- Supabase SQL fixture for Story 4.9 좋은 수급 힌트 view/RPC.
-- psql가 실제 CSV를 temp table로 로드한다. Supabase MCP에서는 동등한 INSERT로 대체 실행한다.
begin;

create temporary table supply_hint_fixture (
  case_id text primary key,
  batch_kind text not null,
  slot text not null,
  investor_net_status text not null,
  foreign_net numeric,
  institution_net numeric,
  individual_net numeric,
  program_net numeric,
  expected text not null,
  candidate_id uuid
) on commit drop;

\copy supply_hint_fixture(case_id, batch_kind, slot, investor_net_status, foreign_net, institution_net, individual_net, program_net, expected) from 'tests/fixtures/supply_hint_cases.csv' with (format csv, header true)

do $$
declare
  started jsonb;
  published_run uuid;
  replacement_run uuid;
  intraday_run uuid;
  unpublished_run uuid;
  fence bigint;
  lease uuid;
  current_candidate_id uuid;
  missing_candidate uuid := gen_random_uuid();
  replacement_candidate uuid := gen_random_uuid();
  intraday_candidate uuid := gen_random_uuid();
  unpublished_candidate uuid := gen_random_uuid();
  inactive_candidate uuid := gen_random_uuid();
  fixture_case record;
  result jsonb;
  candidate_result jsonb;
  actual_status text;
  actual_trading_day date;
  actual_count bigint;
  candidate_count bigint;
  missing_investor_net_status text;
  missing_collected_at timestamptz;
begin
  if has_table_privilege('anon', 'public.supply_3day', 'select')
     or has_table_privilege('authenticated', 'public.supply_3day', 'select')
     or has_table_privilege('anon', 'public.candidate_supply_hints', 'select')
     or has_table_privilege('authenticated', 'public.candidate_supply_hints', 'select') then
    raise exception 'supply_3day and candidate_supply_hints direct SELECT must remain revoked';
  end if;
  if not has_function_privilege('anon', 'public.get_candidate_supply_hints(uuid)'::regprocedure, 'EXECUTE')
     or not has_function_privilege('authenticated', 'public.get_candidate_supply_hints(uuid)'::regprocedure, 'EXECUTE')
     or not has_function_privilege('service_role', 'public.get_candidate_supply_hints(uuid)'::regprocedure, 'EXECUTE') then
    raise exception 'get_candidate_supply_hints execute grants are incomplete';
  end if;
  if exists (
    select 1
    from information_schema.routine_privileges
    where specific_schema = 'public'
      and routine_name = 'get_candidate_supply_hints'
      and grantee = 'PUBLIC'
      and privilege_type = 'EXECUTE'
  ) then
    raise exception 'PUBLIC must not retain execute on get_candidate_supply_hints';
  end if;

  started := public.start_attempt('close:2099-08-01', date '2099-08-01', 'close', 'manual', 300);
  published_run := (started->>'run_id')::uuid;
  fence := (started->>'fence_token')::bigint;
  lease := (started->>'lease_token')::uuid;
  perform public.write_stage(published_run, 'candidates', fence, lease, 'pending', 'running');
  perform public.write_stage(published_run, 'candidates', fence, lease, 'running', 'success');
  perform public.write_stage(published_run, 'tags', fence, lease, 'pending', 'running');
  perform public.write_stage(published_run, 'tags', fence, lease, 'running', 'success');
  perform public.write_stage(published_run, 'supply_3day', fence, lease, 'pending', 'running');
  perform public.write_stage(published_run, 'supply_3day', fence, lease, 'running', 'success');
  perform public.write_stage(published_run, 'market_supply', fence, lease, 'pending', 'running');
  perform public.write_stage(published_run, 'market_supply', fence, lease, 'running', 'success');

  for fixture_case in select * from supply_hint_fixture where batch_kind = 'close' and slot = 'D0' order by case_id loop
    current_candidate_id := gen_random_uuid();
    update supply_hint_fixture f set candidate_id = current_candidate_id where f.case_id = fixture_case.case_id;
    insert into public.candidates(candidate_id, attempt_run_id, ticker, name, trading_day, trading_value)
    values (current_candidate_id, published_run, 'T' || fixture_case.case_id, fixture_case.case_id, date '2099-08-01', 100);
    insert into public.candidate_source_contrib(candidate_id, attempt_run_id, source, contribution_weight)
    values (current_candidate_id, published_run, 't1859', 1);
    insert into public.candidate_tags(candidate_id, attempt_run_id, strategy, signal_date, status)
    values (current_candidate_id, published_run, 'A', date '2099-08-01', 'active');
    insert into public.supply_3day(
      candidate_id, attempt_run_id, trading_day, slot, close, volume, change_pct,
      foreign_net, institution_net, individual_net, program_net, investor_net_status, collected_at
    ) values (
      current_candidate_id, published_run, date '2099-08-01', 'D0', 70000, 100, 1.0,
      fixture_case.foreign_net, fixture_case.institution_net, fixture_case.individual_net,
      fixture_case.program_net, fixture_case.investor_net_status, timestamptz '2099-08-01 03:00:00+00'
  );
  end loop;

  -- D0가 없고 오래된/미래 D0만 있는 후보도 active RPC에서 missing으로 보존되어야 한다.
  insert into public.candidates(candidate_id, attempt_run_id, ticker, name, trading_day, trading_value)
  values (missing_candidate, published_run, 'MISS0', 'D0 없음', date '2099-08-01', 100);
  insert into public.candidate_source_contrib(candidate_id, attempt_run_id, source, contribution_weight)
  values (missing_candidate, published_run, 't1859', 1);
  insert into public.candidate_tags(candidate_id, attempt_run_id, strategy, signal_date, status)
  values (missing_candidate, published_run, 'A', date '2099-08-01', 'active');
  insert into public.supply_3day(
    candidate_id, attempt_run_id, trading_day, slot, close, volume, change_pct,
    foreign_net, institution_net, individual_net, program_net, investor_net_status
  ) values
    (missing_candidate, published_run, date '2099-07-31', 'D0', 70000, 100, 1, 99, 99, 99, 99, 'confirmed'),
    (missing_candidate, published_run, date '2099-08-02', 'D0', 70000, 100, 1, 99, 99, 99, 99, 'confirmed');

  -- 같은 attempt의 오래된 D0는 최신 거래일 행으로 대체되어야 한다.
  select f.candidate_id into current_candidate_id from supply_hint_fixture f where f.case_id = 'HAPPY_PATH';
  if not found then
    raise exception 'HAPPY_PATH fixture row was not loaded from CSV';
  end if;
  insert into public.supply_3day(
    candidate_id, attempt_run_id, trading_day, slot, close, volume, change_pct,
    foreign_net, institution_net, individual_net, program_net, investor_net_status, collected_at
  ) values (
    current_candidate_id, published_run, date '2099-07-31', 'D0', 60000, 100, 1.0,
    0, 0, 0, 0, 'confirmed', timestamptz '2099-07-31 03:00:00+00'
  );

  -- active tag가 없는 후보는 view에는 있어도 RPC에는 나오지 않는다.
  insert into public.candidates(candidate_id, attempt_run_id, ticker, name, trading_day, trading_value)
  values (inactive_candidate, published_run, 'INACT', '비활성', date '2099-08-01', 100);
  insert into public.candidate_tags(candidate_id, attempt_run_id, strategy, signal_date, status)
  values (inactive_candidate, published_run, 'A', date '2099-08-01', 'vanished');
  insert into public.candidate_source_contrib(candidate_id, attempt_run_id, source, contribution_weight)
  values (inactive_candidate, published_run, 't1859', 1);
  insert into public.supply_3day(
    candidate_id, attempt_run_id, trading_day, slot, close, volume, change_pct,
    foreign_net, institution_net, individual_net, program_net, investor_net_status
  ) values (inactive_candidate, published_run, date '2099-08-01', 'D0', 70000, 100, 1, 1, 1, 1, 1, 'confirmed');

  insert into public.daily_ohlcv(ticker, trading_day, open, high, low, close, volume)
  select c.ticker, date '2099-08-01', 69000, 71000, 68000, 70000, 1000
  from public.candidates c
  where c.attempt_run_id = published_run;
  insert into public.market_supply(
    attempt_run_id, market, trading_day, foreign_net, institution_net, individual_net, program_net
  ) values
    (published_run, 'KOSPI', date '2099-08-01', 1, 1, 1, 1),
    (published_run, 'KOSDAQ', date '2099-08-01', 1, 1, 1, 1);

  perform public.publish_attempt(published_run, fence, lease);

  for fixture_case in select * from supply_hint_fixture where batch_kind = 'close' and slot = 'D0' order by case_id loop
    select h.hint_status into actual_status
    from public.candidate_supply_hints h
    where h.candidate_id = fixture_case.candidate_id and h.attempt_run_id = published_run;
    if not found or actual_status is distinct from fixture_case.expected then
      raise exception 'view mismatch for %: expected %, got %', fixture_case.case_id, fixture_case.expected, actual_status;
    end if;
  end loop;
  select count(*), max(h.trading_day) into actual_count, actual_trading_day
  from public.candidate_supply_hints h
  where h.candidate_id = (select candidate_id from supply_hint_fixture where case_id = 'HAPPY_PATH')
    and h.attempt_run_id = published_run;
  if actual_count <> 1 or actual_trading_day is distinct from date '2099-08-01' then
    raise exception 'view did not select the latest D0 trading_day';
  end if;
  select h.hint_status into actual_status
  from public.candidate_supply_hints h
  where h.candidate_id = missing_candidate and h.attempt_run_id = published_run;
  if not found then
    raise exception 'missing D0 candidate has no view row';
  end if;
  select count(*) into actual_count
  from public.candidate_supply_hints h
  where h.candidate_id = missing_candidate and h.attempt_run_id = published_run;
  if actual_count <> 1 or actual_status is distinct from 'undetermined' then
    raise exception 'missing D0 candidate did not produce one undetermined view row';
  end if;
  select count(*) into actual_count
  from public.candidate_supply_hints h
  where h.candidate_id = missing_candidate and h.attempt_run_id = published_run;
  if actual_count <> 1 then
    raise exception 'missing D0 candidate view row count changed during payload check';
  end if;
  select h.investor_net_status, h.collected_at into missing_investor_net_status, missing_collected_at
  from public.candidate_supply_hints h
  where h.candidate_id = missing_candidate and h.attempt_run_id = published_run;
  if not found or missing_investor_net_status is distinct from 'missing' or missing_collected_at is not null then
    raise exception 'missing D0 candidate payload was not missing/null: %, %', missing_investor_net_status, missing_collected_at;
  end if;

  result := public.get_candidate_supply_hints(published_run);
  if jsonb_array_length(result) <> 9 then
    raise exception 'expected eight shared plus one missing active close hint, got %', result;
  end if;
  for fixture_case in select * from supply_hint_fixture where batch_kind = 'close' and slot = 'D0' order by case_id loop
    select count(*) into candidate_count
    from jsonb_array_elements(result) e
    where e->>'candidate_id' = fixture_case.candidate_id::text;
    if candidate_count <> 1 then
      raise exception 'RPC returned % rows for %, expected exactly one', candidate_count, fixture_case.case_id;
    end if;
    select e into candidate_result
    from jsonb_array_elements(result) e
    where e->>'candidate_id' = fixture_case.candidate_id::text;
    if not found
       or candidate_result is null
       or candidate_result->'candidate_id' <> to_jsonb(fixture_case.candidate_id::text)
       or candidate_result->'attempt_run_id' <> to_jsonb(published_run::text)
       or candidate_result->'ticker' <> to_jsonb(('T' || fixture_case.case_id)::text)
       or candidate_result->'trading_day' <> to_jsonb('2099-08-01'::text)
       or candidate_result->'slot' <> to_jsonb('D0'::text)
       or candidate_result->'batch_kind' <> to_jsonb('close'::text)
       or candidate_result->'foreign_net' <> coalesce(to_jsonb(fixture_case.foreign_net), 'null'::jsonb)
       or candidate_result->'institution_net' <> coalesce(to_jsonb(fixture_case.institution_net), 'null'::jsonb)
       or candidate_result->'individual_net' <> coalesce(to_jsonb(fixture_case.individual_net), 'null'::jsonb)
       or candidate_result->'program_net' <> coalesce(to_jsonb(fixture_case.program_net), 'null'::jsonb)
       or candidate_result->'investor_net_status' <> to_jsonb(fixture_case.investor_net_status)
       or candidate_result->'collected_at' <> to_jsonb(timestamptz '2099-08-01 03:00:00+00')
       or candidate_result->'hint_status' <> to_jsonb(fixture_case.expected) then
      raise exception 'RPC mismatch for %: expected %, got %', fixture_case.case_id, fixture_case.expected, candidate_result;
    end if;
  end loop;
  if to_jsonb(date '2099-08-01') <> to_jsonb('2099-08-01'::text) then
    raise exception 'date JSON representation is not the expected JSON string';
  end if;
  select count(*) into candidate_count
  from jsonb_array_elements(result) e
  where e->>'candidate_id' = missing_candidate::text;
  if candidate_count <> 1 then
    raise exception 'RPC returned % missing-row candidates, expected exactly one', candidate_count;
  end if;
  select e into candidate_result
  from jsonb_array_elements(result) e
  where e->>'candidate_id' = missing_candidate::text;
  if not found
     or candidate_result is null
     or candidate_result->'candidate_id' <> to_jsonb(missing_candidate::text)
     or candidate_result->'attempt_run_id' <> to_jsonb(published_run::text)
     or candidate_result->'ticker' <> to_jsonb('MISS0'::text)
     or candidate_result->'trading_day' <> to_jsonb('2099-08-01'::text)
     or candidate_result->'slot' <> to_jsonb('D0'::text)
     or candidate_result->'batch_kind' <> to_jsonb('close'::text)
     or candidate_result->'foreign_net' <> 'null'::jsonb
     or candidate_result->'institution_net' <> 'null'::jsonb
     or candidate_result->'individual_net' <> 'null'::jsonb
     or candidate_result->'program_net' <> 'null'::jsonb
     or candidate_result->'investor_net_status' <> to_jsonb('missing'::text)
     or candidate_result->'collected_at' <> 'null'::jsonb
     or candidate_result->'hint_status' <> to_jsonb('undetermined'::text) then
    raise exception 'RPC missing-row payload mismatch: %', candidate_result;
  end if;
  if exists (
    select 1 from jsonb_array_elements(result) e
    where e->>'candidate_id' = inactive_candidate::text
  ) then
    raise exception 'inactive candidate leaked from supply hint RPC';
  end if;

  -- anon 역할도 security-definer RPC를 사용할 수 있지만 view/table SELECT는 없다.
  set local role anon;
  result := public.get_candidate_supply_hints(published_run);
  if jsonb_array_length(result) <> 9 then
    raise exception 'anon could not execute supply hint RPC: %', result;
  end if;
  set local role postgres;

  if exists (select 1 from pg_roles where rolname = 'authenticated') then
    set local role authenticated;
    result := public.get_candidate_supply_hints(published_run);
    if jsonb_array_length(result) <> 9 then
      raise exception 'authenticated could not execute supply hint RPC: %', result;
    end if;
    set local role postgres;
  end if;

  -- 장중 attempt는 close 행과 분리되어야 하며, confirmed 값이 있어도 undetermined다.
  started := public.start_attempt('intraday:2099-08-01:10:00', date '2099-08-01', 'intraday', 'manual', 300);
  intraday_run := (started->>'run_id')::uuid;
  fence := (started->>'fence_token')::bigint;
  lease := (started->>'lease_token')::uuid;
  perform public.write_stage(intraday_run, 'candidates', fence, lease, 'pending', 'running');
  perform public.write_stage(intraday_run, 'candidates', fence, lease, 'running', 'success');
  perform public.write_stage(intraday_run, 'tags', fence, lease, 'pending', 'running');
  perform public.write_stage(intraday_run, 'tags', fence, lease, 'running', 'success');
  perform public.write_stage(intraday_run, 'supply_3day', fence, lease, 'pending', 'running');
  perform public.write_stage(intraday_run, 'supply_3day', fence, lease, 'running', 'success');
  perform public.write_stage(intraday_run, 'market_supply', fence, lease, 'pending', 'running');
  perform public.write_stage(intraday_run, 'market_supply', fence, lease, 'running', 'success');
  insert into public.candidates(candidate_id, attempt_run_id, ticker, name, trading_day, trading_value)
  values (intraday_candidate, intraday_run, 'INTRA', '장중', date '2099-08-01', 100);
  insert into public.candidate_source_contrib(candidate_id, attempt_run_id, source, contribution_weight)
  values (intraday_candidate, intraday_run, 't1859', 1);
  insert into public.candidate_tags(candidate_id, attempt_run_id, strategy, signal_date, status)
  values (intraday_candidate, intraday_run, 'A', date '2099-08-01', 'active');
  insert into public.supply_3day(
    candidate_id, attempt_run_id, trading_day, slot, close, volume, change_pct,
    foreign_net, institution_net, individual_net, program_net, investor_net_status
  ) values (intraday_candidate, intraday_run, date '2099-08-01', 'D0', 70000, 100, 1, 9, 9, 9, 9, 'confirmed');
  insert into public.market_supply(
    attempt_run_id, market, trading_day, foreign_net, institution_net, individual_net, program_net
  ) values
    (intraday_run, 'KOSPI', date '2099-08-01', 1, 1, 1, 1),
    (intraday_run, 'KOSDAQ', date '2099-08-01', 1, 1, 1, 1);
  perform public.publish_attempt(intraday_run, fence, lease);
  select h.hint_status into actual_status
  from public.candidate_supply_hints h
  where h.candidate_id = intraday_candidate and h.attempt_run_id = intraday_run;
  if not found then
    raise exception 'intraday candidate has no view row';
  end if;
  select count(*) into actual_count
  from public.candidate_supply_hints h
  where h.candidate_id = intraday_candidate and h.attempt_run_id = intraday_run;
  if actual_count <> 1 or actual_status is distinct from 'undetermined' or jsonb_array_length(public.get_candidate_supply_hints(intraday_run)) <> 1 then
    raise exception 'intraday confirmed values must remain undetermined';
  end if;

  -- 동일 intraday logical run의 새 published attempt가 current pointer가 되면 이전 attempt는 격리된다.
  started := public.start_attempt('intraday:2099-08-01:10:00', date '2099-08-01', 'intraday', 'manual', 300);
  replacement_run := (started->>'run_id')::uuid;
  fence := (started->>'fence_token')::bigint;
  lease := (started->>'lease_token')::uuid;
  perform public.write_stage(replacement_run, 'candidates', fence, lease, 'pending', 'running');
  perform public.write_stage(replacement_run, 'candidates', fence, lease, 'running', 'success');
  perform public.write_stage(replacement_run, 'tags', fence, lease, 'pending', 'running');
  perform public.write_stage(replacement_run, 'tags', fence, lease, 'running', 'success');
  perform public.write_stage(replacement_run, 'supply_3day', fence, lease, 'pending', 'running');
  perform public.write_stage(replacement_run, 'supply_3day', fence, lease, 'running', 'success');
  perform public.write_stage(replacement_run, 'market_supply', fence, lease, 'pending', 'running');
  perform public.write_stage(replacement_run, 'market_supply', fence, lease, 'running', 'success');
  insert into public.candidates(candidate_id, attempt_run_id, ticker, name, trading_day, trading_value)
  values (replacement_candidate, replacement_run, 'REPL', '교체', date '2099-08-01', 100);
  insert into public.candidate_source_contrib(candidate_id, attempt_run_id, source, contribution_weight)
  values (replacement_candidate, replacement_run, 't1859', 1);
  insert into public.candidate_tags(candidate_id, attempt_run_id, strategy, signal_date, status)
  values (replacement_candidate, replacement_run, 'A', date '2099-08-01', 'active');
  insert into public.supply_3day(
    candidate_id, attempt_run_id, trading_day, slot, close, volume, change_pct,
    foreign_net, institution_net, individual_net, program_net, investor_net_status
  ) values (replacement_candidate, replacement_run, date '2099-08-01', 'D0', 70000, 100, 1, 9, 9, 9, 9, 'confirmed');
  insert into public.market_supply(
    attempt_run_id, market, trading_day, foreign_net, institution_net, individual_net, program_net
  ) values
    (replacement_run, 'KOSPI', date '2099-08-01', 1, 1, 1, 1),
    (replacement_run, 'KOSDAQ', date '2099-08-01', 1, 1, 1, 1);
  perform public.publish_attempt(replacement_run, fence, lease);
  if public.get_candidate_supply_hints(intraday_run) <> '[]'::jsonb
     or jsonb_array_length(public.get_candidate_supply_hints(replacement_run)) <> 1 then
    raise exception 'previous current-complete attempt was not isolated';
  end if;

  started := public.start_attempt('close:2099-08-02', date '2099-08-02', 'close', 'manual', 300);
  unpublished_run := (started->>'run_id')::uuid;
  insert into public.candidates(candidate_id, attempt_run_id, ticker, name, trading_day, trading_value)
  values (unpublished_candidate, unpublished_run, 'UNPUB', '미발행', date '2099-08-02', 100);
  insert into public.candidate_tags(candidate_id, attempt_run_id, strategy, signal_date, status)
  values (unpublished_candidate, unpublished_run, 'A', date '2099-08-02', 'active');
  insert into public.supply_3day(
    candidate_id, attempt_run_id, trading_day, slot, close, volume, change_pct,
    foreign_net, institution_net, individual_net, program_net, investor_net_status
  ) values (unpublished_candidate, unpublished_run, date '2099-08-02', 'D0', 70000, 100, 1, 9, 9, 9, 9, 'confirmed');
  if public.get_candidate_supply_hints(unpublished_run) <> '[]'::jsonb then
    raise exception 'unpublished attempt was exposed';
  end if;
end $$;

select 'story_4_9_supply_hints: pass' as result;

rollback;
