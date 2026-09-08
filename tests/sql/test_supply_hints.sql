-- Supabase SQL fixture for Story 4.9 좋은 수급 힌트 view/RPC.
-- CSV fixture(tests/fixtures/supply_hint_cases.csv)와 같은 경계값을 사용하며 rollback한다.
begin;

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
  replacement_candidate uuid := gen_random_uuid();
  intraday_candidate uuid := gen_random_uuid();
  unpublished_candidate uuid := gen_random_uuid();
  inactive_candidate uuid := gen_random_uuid();
  fixture_case record;
  result jsonb;
  candidate_result jsonb;
  actual_status text;
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

  create temporary table supply_hint_fixture (
    case_id text primary key,
    batch_kind text not null,
    investor_net_status text not null,
    foreign_net numeric,
    institution_net numeric,
    individual_net numeric,
    program_net numeric,
    expected text not null,
    candidate_id uuid
  ) on commit drop;

  insert into supply_hint_fixture(case_id, batch_kind, investor_net_status, foreign_net, institution_net, individual_net, program_net, expected)
  values
    ('HAPPY_PATH', 'close', 'confirmed', 101, 202, -303, 404, 'good'),
    ('NOT_MET_ZERO', 'close', 'confirmed', 101, 202, -303, 0, 'not_met'),
    ('NOT_MET_NEGATIVE', 'close', 'confirmed', 101, -202, -303, 404, 'not_met'),
    ('UNKNOWN_PENDING', 'close', 'pending', null, null, null, null, 'undetermined'),
    ('UNKNOWN_MISSING', 'close', 'missing', null, null, null, null, 'undetermined'),
    ('UNKNOWN_NULL', 'close', 'confirmed', 101, 202, -303, null, 'undetermined'),
    ('INTRADAY', 'intraday', 'confirmed', 101, 202, -303, 404, 'undetermined');

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

  for fixture_case in select * from supply_hint_fixture where batch_kind = 'close' order by case_id loop
    current_candidate_id := gen_random_uuid();
    update supply_hint_fixture f set candidate_id = current_candidate_id where f.case_id = fixture_case.case_id;
    insert into public.candidates(candidate_id, attempt_run_id, ticker, name, trading_day, trading_value)
    values (current_candidate_id, published_run, 'T' || right(fixture_case.case_id, 5), fixture_case.case_id, date '2099-08-01', 100);
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

  -- 같은 attempt의 오래된 D0는 최신 거래일 행으로 대체되어야 한다.
  select f.candidate_id into current_candidate_id from supply_hint_fixture f where f.case_id = 'HAPPY_PATH';
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

  for fixture_case in select * from supply_hint_fixture where batch_kind = 'close' order by case_id loop
    select h.hint_status into actual_status
    from public.candidate_supply_hints h
    where h.candidate_id = fixture_case.candidate_id and h.attempt_run_id = published_run;
    if actual_status <> fixture_case.expected then
      raise exception 'view mismatch for %: expected %, got %', fixture_case.case_id, fixture_case.expected, actual_status;
    end if;
  end loop;
  if (select h.trading_day from public.candidate_supply_hints h
      where h.candidate_id = (select candidate_id from supply_hint_fixture where case_id = 'HAPPY_PATH')
        and h.attempt_run_id = published_run) <> date '2099-08-01' then
    raise exception 'view did not select the latest D0 trading_day';
  end if;

  result := public.get_candidate_supply_hints(published_run);
  if jsonb_array_length(result) <> 6 then
    raise exception 'expected six active close fixture hints, got %', result;
  end if;
  for fixture_case in select * from supply_hint_fixture where batch_kind = 'close' loop
    select e into candidate_result
    from jsonb_array_elements(result) e
    where e->>'candidate_id' = fixture_case.candidate_id::text;
    if candidate_result is null or candidate_result->>'hint_status' <> fixture_case.expected then
      raise exception 'RPC mismatch for %: expected %, got %', fixture_case.case_id, fixture_case.expected, candidate_result;
    end if;
  end loop;
  if exists (
    select 1 from jsonb_array_elements(result) e
    where e->>'candidate_id' = inactive_candidate::text
  ) then
    raise exception 'inactive candidate leaked from supply hint RPC';
  end if;

  -- anon 역할도 security-definer RPC를 사용할 수 있지만 view/table SELECT는 없다.
  set local role anon;
  result := public.get_candidate_supply_hints(published_run);
  if jsonb_array_length(result) <> 6 then
    raise exception 'anon could not execute supply hint RPC: %', result;
  end if;
  set local role postgres;

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
  if actual_status <> 'undetermined' or jsonb_array_length(public.get_candidate_supply_hints(intraday_run)) <> 1 then
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
