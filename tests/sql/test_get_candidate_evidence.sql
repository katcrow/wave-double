-- Supabase SQL fixture for Story 4.6 후보 근거 RPC.
-- 모든 fixture는 rollback되어 실제 데이터는 남기지 않는다.
begin;

do $$
declare
  first_started jsonb;
  second_started jsonb;
  first_run uuid;
  second_run uuid;
  first_candidate uuid := gen_random_uuid();
  second_candidate uuid := gen_random_uuid();
  other_candidate uuid := gen_random_uuid();
  fallback_candidate uuid := gen_random_uuid();
  no_previous_candidate uuid := gen_random_uuid();
  result jsonb;
  candidate_result jsonb;
  fence bigint;
  lease uuid;
begin
  first_started := public.start_attempt('close:2099-06-10', date '2099-06-10', 'close', 'manual', 300);
  first_run := (first_started->>'run_id')::uuid;
  second_started := public.start_attempt('close:2099-06-11', date '2099-06-11', 'close', 'manual', 300);
  second_run := (second_started->>'run_id')::uuid;

  insert into public.candidates(candidate_id, attempt_run_id, ticker, name, trading_day, trading_value)
  values
    (first_candidate, first_run, '000001', '근거후보', date '2099-06-10', 100),
    (second_candidate, second_run, '000001', '다른시도', date '2099-06-11', 100),
    (other_candidate, first_run, '000002', '비활성후보', date '2099-06-10', 100);

  insert into public.candidate_tags(candidate_id, attempt_run_id, strategy, signal_date, status)
  values
    (first_candidate, first_run, 'A', date '2099-06-10', 'active'),
    (second_candidate, second_run, 'A', date '2099-06-11', 'active'),
    (other_candidate, first_run, 'A', date '2099-06-10', 'vanished');

  insert into public.candidate_source_contrib(candidate_id, attempt_run_id, source, contribution_weight)
  values
    (first_candidate, first_run, 't1852', 0.4),
    (first_candidate, first_run, 't1856', 0.6),
    (second_candidate, second_run, 't1859', 1),
    (other_candidate, first_run, 't1859', 1);

  insert into public.supply_3day(
    candidate_id, attempt_run_id, trading_day, slot, close, volume, change_pct,
    foreign_net, institution_net, individual_net, program_net, investor_net_status, collected_at
  ) values
    (first_candidate, first_run, date '2099-06-08', 'D-2', 68000, 100, 1, null, null, null, null, 'missing', timestamptz '2099-06-10 01:00:00+00'),
    (first_candidate, first_run, date '2099-06-09', 'D-1', 69000, 110, 1.4, null, null, null, null, 'pending', timestamptz '2099-06-10 02:00:00+00'),
    (first_candidate, first_run, date '2099-06-10', 'D0', 70000, 120, 1.45, 0, 200, -200, 0, 'confirmed', timestamptz '2099-06-10 03:00:00+00'),
    -- 같은 attempt의 과거 D0는 최신 슬롯 1행 선택에서 제외되어야 한다.
    (first_candidate, first_run, date '2099-06-07', 'D0', 69900, 119, 1.3, 0, 0, 0, 0, 'confirmed', timestamptz '2099-06-09 03:00:00+00'),
    -- 다른 attempt의 같은 candidate_id를 가정한 오염 행은 candidates 합성 FK상 허용되지 않으므로,
    -- 실제 격리는 같은 ticker의 별도 candidate로 검증한다.
    (second_candidate, second_run, date '2099-06-11', 'D0', 80000, 300, 2, 10, 20, -30, null, 'confirmed', timestamptz '2099-06-11 03:00:00+00');

  -- t1702에는 sujung 파라미터가 없으므로 종가/등락률 read projection은
  -- t8410(sujung=Y)로 적재된 adjusted daily_ohlcv를 사용한다.
  insert into public.daily_ohlcv(ticker, trading_day, open, high, low, close, volume, adjusted)
  values
    ('000001', date '2099-06-07', 67000, 67500, 66500, 67000, 100, true),
    ('000001', date '2099-06-08', 68000, 68500, 67500, 68000, 100, true),
    ('000001', date '2099-06-09', 69000, 69500, 68500, 69000, 100, true),
    ('000001', date '2099-06-10', 71000, 71500, 70500, 71000, 100, true),
    ('000001', date '2099-06-11', 73000, 73500, 72500, 73000, 100, true);
  insert into public.supply_3day(
    candidate_id, attempt_run_id, trading_day, slot, close, volume, change_pct,
    foreign_net, institution_net, individual_net, program_net, investor_net_status, collected_at
  ) values
    (first_candidate, first_run, date '2099-06-11', 'D0', 72000, 121, 1.41, 1, 1, 1, 1, 'confirmed', timestamptz '2099-06-11 03:00:00+00');

  fence := (first_started->>'fence_token')::bigint;
  lease := (first_started->>'lease_token')::uuid;
  perform public.write_stage(first_run, 'candidates', fence, lease, 'pending', 'running');
  perform public.write_stage(first_run, 'candidates', fence, lease, 'running', 'success');
  perform public.write_stage(first_run, 'tags', fence, lease, 'pending', 'running');
  perform public.write_stage(first_run, 'tags', fence, lease, 'running', 'success');
  perform public.write_stage(first_run, 'supply_3day', fence, lease, 'pending', 'running');
  perform public.write_stage(first_run, 'supply_3day', fence, lease, 'running', 'success');
  perform public.write_stage(first_run, 'market_supply', fence, lease, 'pending', 'running');
  perform public.write_stage(first_run, 'market_supply', fence, lease, 'running', 'success');
  insert into public.market_supply(attempt_run_id, market, trading_day, foreign_net, institution_net, individual_net, program_net)
  values (first_run, 'KOSPI', date '2099-06-10', 1, 1, 1, 1), (first_run, 'KOSDAQ', date '2099-06-10', 1, 1, 1, 1);
  perform public.publish_attempt(first_run, fence, lease);

  fence := (second_started->>'fence_token')::bigint;
  lease := (second_started->>'lease_token')::uuid;
  perform public.write_stage(second_run, 'candidates', fence, lease, 'pending', 'running');
  perform public.write_stage(second_run, 'candidates', fence, lease, 'running', 'success');
  perform public.write_stage(second_run, 'tags', fence, lease, 'pending', 'running');
  perform public.write_stage(second_run, 'tags', fence, lease, 'running', 'success');
  perform public.write_stage(second_run, 'supply_3day', fence, lease, 'pending', 'running');
  perform public.write_stage(second_run, 'supply_3day', fence, lease, 'running', 'success');
  perform public.write_stage(second_run, 'market_supply', fence, lease, 'pending', 'running');
  perform public.write_stage(second_run, 'market_supply', fence, lease, 'running', 'success');
  insert into public.market_supply(attempt_run_id, market, trading_day, foreign_net, institution_net, individual_net, program_net)
  values (second_run, 'KOSPI', date '2099-06-11', 1, 1, 1, 1), (second_run, 'KOSDAQ', date '2099-06-11', 1, 1, 1, 1);
  perform public.publish_attempt(second_run, fence, lease);

  result := public.get_candidate_evidence(first_run);

  if jsonb_array_length(result) <> 1 then
    raise exception 'expected only active candidates in requested attempt, got %', result;
  end if;
  candidate_result := result->0;
  if candidate_result->>'candidate_id' <> first_candidate::text then
    raise exception 'unexpected candidate returned: %', candidate_result->>'candidate_id';
  end if;
  if candidate_result->'sources' <> '["t1856", "t1852"]'::jsonb then
    raise exception 'provenance order/values were not preserved: %', candidate_result->'sources';
  end if;
  if (candidate_result->'rows'->0->>'slot') <> 'D0'
     or (candidate_result->'rows'->1->>'slot') <> 'D-1'
     or (candidate_result->'rows'->2->>'slot') <> 'D-2' then
    raise exception 'expected D0/D-1/D-2 order with all three rows: %', candidate_result->'rows';
  end if;
  if (candidate_result->'rows'->0->>'close')::numeric <> 71000 then
    raise exception 'adjusted latest D0 row was not selected: %', candidate_result->'rows'->0;
  end if;
  if (candidate_result->'rows'->0->>'change_pct')::numeric <> 2.9 then
    raise exception 'adjusted D0 change_pct was not calculated: %', candidate_result->'rows'->0;
  end if;
  if candidate_result->'rows'->1->>'investor_net_status' <> 'pending'
     or (candidate_result->'rows'->1->>'foreign_net') is not null then
    raise exception 'pending status/null investor values were not preserved: %', candidate_result->'rows'->1;
  end if;
  if candidate_result->'rows'->2->>'investor_net_status' <> 'missing'
     or (candidate_result->'rows'->2->>'program_net') is not null then
    raise exception 'missing status/null investor values were not preserved: %', candidate_result->'rows'->2;
  end if;
  if jsonb_array_length(candidate_result->'rows') <> 3
     or exists (
       select 1 from jsonb_array_elements(candidate_result->'rows') e
       where e->>'trading_day' = '2099-06-11'
     ) then
    raise exception 'future D0 supply row leaked into evidence: %', candidate_result->'rows';
  end if;

  result := public.get_candidate_evidence(second_run);
  if jsonb_array_length(result) <> 1 or (result->0->>'candidate_id') <> second_candidate::text then
    raise exception 'attempt isolation failed: %', result;
  end if;

  -- publish 이후 추가된 provenance 없는 active 후보는 read RPC에서 source/rows가 비어도
  -- 정상적으로 반환되어, 후보 source fallback 계약을 계속 검사한다.
  insert into public.candidates(candidate_id, attempt_run_id, ticker, name, trading_day, trading_value)
  values (fallback_candidate, first_run, '000003', '원천없는후보', date '2099-06-10', 100);
  insert into public.candidate_tags(candidate_id, attempt_run_id, strategy, signal_date, status)
  values (fallback_candidate, first_run, 'B', date '2099-06-10', 'active');
  insert into public.candidates(candidate_id, attempt_run_id, ticker, name, trading_day, trading_value)
  values (no_previous_candidate, first_run, '000004', '이전봉없는후보', date '2099-06-10', 100);
  insert into public.candidate_tags(candidate_id, attempt_run_id, strategy, signal_date, status)
  values (no_previous_candidate, first_run, 'C', date '2099-06-10', 'active');
  insert into public.supply_3day(
    candidate_id, attempt_run_id, trading_day, slot, close, volume, change_pct,
    foreign_net, institution_net, individual_net, program_net, investor_net_status, collected_at
  ) values
    (no_previous_candidate, first_run, date '2099-06-10', 'D0', 99999, 100, 99, 1, 1, 1, 1, 'confirmed', timestamptz '2099-06-10 04:00:00+00');
  insert into public.daily_ohlcv(ticker, trading_day, open, high, low, close, volume, adjusted)
  values ('000004', date '2099-06-10', 1000, 1100, 900, 1050, 100, true);
  result := public.get_candidate_evidence(first_run);
  select e into candidate_result
  from jsonb_array_elements(result) e
  where e->>'candidate_id' = fallback_candidate::text;
  if candidate_result is null then
    raise exception 'fallback candidate was not returned: %', result;
  end if;
  if candidate_result->'sources' <> '[]'::jsonb or candidate_result->'rows' <> '[]'::jsonb then
    raise exception 'fallback candidate shape was not empty-source/empty-rows: %', candidate_result;
  end if;

  select e into candidate_result
  from jsonb_array_elements(result) e
  where e->>'candidate_id' = no_previous_candidate::text;
  if candidate_result is null or candidate_result->'rows' <> '[]'::jsonb then
    raise exception 'raw change_pct fallback leaked without an adjusted previous bar: %', candidate_result;
  end if;

  if not has_function_privilege('anon', 'public.get_candidate_evidence(uuid)'::regprocedure, 'EXECUTE')
     or not has_function_privilege('authenticated', 'public.get_candidate_evidence(uuid)'::regprocedure, 'EXECUTE')
     or not has_function_privilege('service_role', 'public.get_candidate_evidence(uuid)'::regprocedure, 'EXECUTE') then
    raise exception 'anon/authenticated/service_role execute grants are incomplete';
  end if;
  if exists (
    select 1
    from information_schema.routine_privileges
    where specific_schema = 'public'
      and routine_name = 'get_candidate_evidence'
      and grantee = 'PUBLIC'
      and privilege_type = 'EXECUTE'
  ) then
    raise exception 'PUBLIC must not retain execute on get_candidate_evidence';
  end if;
  if coalesce(array_position(
    (select proconfig from pg_proc where oid = 'public.get_candidate_evidence(uuid)'::regprocedure),
    'search_path=pg_catalog, public'
  ), 0) = 0 then
    raise exception 'SECURITY DEFINER search_path is not hardened';
  end if;
end $$;

select 'story_4_6_candidate_evidence: pass' as result;

rollback;
