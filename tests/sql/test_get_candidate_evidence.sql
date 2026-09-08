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
  result jsonb;
  candidate_result jsonb;
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
    (first_candidate, first_run, 't1856', 0.6);

  insert into public.supply_3day(
    candidate_id, attempt_run_id, trading_day, slot, close, volume, change_pct,
    foreign_net, institution_net, individual_net, program_net, investor_net_status, collected_at
  ) values
    (first_candidate, first_run, date '2099-06-08', 'D-2', 68000, 100, 1, 0, 0, 0, 0, 'confirmed', timestamptz '2099-06-10 01:00:00+00'),
    (first_candidate, first_run, date '2099-06-09', 'D-1', 69000, 110, 1.4, null, null, null, null, 'pending', timestamptz '2099-06-10 02:00:00+00'),
    (first_candidate, first_run, date '2099-06-10', 'D0', 70000, 120, 1.45, 0, 200, -200, 0, 'confirmed', timestamptz '2099-06-10 03:00:00+00'),
    -- 같은 attempt의 과거 D0는 최신 슬롯 1행 선택에서 제외되어야 한다.
    (first_candidate, first_run, date '2099-06-07', 'D0', 69900, 119, 1.3, 0, 0, 0, 0, 'confirmed', timestamptz '2099-06-09 03:00:00+00'),
    -- 다른 attempt의 같은 candidate_id를 가정한 오염 행은 candidates 합성 FK상 허용되지 않으므로,
    -- 실제 격리는 같은 ticker의 별도 candidate로 검증한다.
    (second_candidate, second_run, date '2099-06-11', 'D0', 80000, 300, 2, 10, 20, -30, null, 'confirmed', timestamptz '2099-06-11 03:00:00+00');

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
  if (candidate_result->'rows'->0->>'close')::numeric <> 70000 then
    raise exception 'latest D0 row was not selected: %', candidate_result->'rows'->0;
  end if;
  if candidate_result->'rows'->1->>'investor_net_status' <> 'pending'
     or (candidate_result->'rows'->1->>'foreign_net') is not null then
    raise exception 'pending status/null investor values were not preserved: %', candidate_result->'rows'->1;
  end if;

  result := public.get_candidate_evidence(second_run);
  if jsonb_array_length(result) <> 1 or (result->0->>'candidate_id') <> second_candidate::text then
    raise exception 'attempt isolation failed: %', result;
  end if;

  -- provenance가 없는 active 후보는 반환되지만 source 배열은 빈 배열이어야 한다.
  insert into public.candidate_tags(candidate_id, attempt_run_id, strategy, signal_date, status)
  values (other_candidate, first_run, 'B', date '2099-06-10', 'active');
  result := public.get_candidate_evidence(first_run);
  select e into candidate_result
  from jsonb_array_elements(result) e
  where e->>'candidate_id' = other_candidate::text;
  if candidate_result->'sources' <> '[]'::jsonb or candidate_result->'rows' <> '[]'::jsonb then
    raise exception 'fallback candidate shape was not empty-source/empty-rows: %', candidate_result;
  end if;
end $$;

select 'story_4_6_candidate_evidence: pass' as result;

rollback;
