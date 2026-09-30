-- get_top_tagged_candidates()의 published snapshot lineage, active/vanished 태그,
-- 거래대금 상위 3개와 ticker tie-break fixture.
begin;

do $$
declare
  key text := 'close:2099-09-30';
  started jsonb;
  run_id uuid;
  fence bigint;
  lease uuid;
  result jsonb;
  active_a uuid := gen_random_uuid();
  active_b uuid := gen_random_uuid();
  active_c uuid := gen_random_uuid();
  active_d uuid := gen_random_uuid();
  vanished_only uuid := gen_random_uuid();
begin
  started := public.start_attempt(key, date '2099-09-30', 'close', 'manual', 300);
  run_id := (started->>'run_id')::uuid;
  fence := (started->>'fence_token')::bigint;
  lease := (started->>'lease_token')::uuid;

  perform public.write_stage(run_id, 'candidates', fence, lease, 'pending', 'running');
  perform public.write_candidates(run_id, fence, lease,
    jsonb_build_array(
      jsonb_build_object('candidate_id', active_a, 'ticker', '000003', 'name', '상위1', 'trading_value', 300,
        'sources', jsonb_build_array(jsonb_build_object('source', 't1859', 'weight', 1))),
      jsonb_build_object('candidate_id', active_b, 'ticker', '000002', 'name', '동률2', 'trading_value', 200,
        'sources', jsonb_build_array(jsonb_build_object('source', 't1859', 'weight', 1))),
      jsonb_build_object('candidate_id', active_c, 'ticker', '000001', 'name', '동률1', 'trading_value', 200,
        'sources', jsonb_build_array(jsonb_build_object('source', 't1859', 'weight', 1))),
      jsonb_build_object('candidate_id', active_d, 'ticker', '000004', 'name', '상위외', 'trading_value', 100,
        'sources', jsonb_build_array(jsonb_build_object('source', 't1859', 'weight', 1))),
      jsonb_build_object('candidate_id', vanished_only, 'ticker', '999999', 'name', '소멸전용', 'trading_value', 999,
        'sources', jsonb_build_array(jsonb_build_object('source', 't1859', 'weight', 1)))
    ),
    jsonb_build_object('selection_input_hash', repeat('a', 64), 'original_count', 5,
      'candidate_count', 5, 'excluded_count', 0, 'truncated_count', 0));
  perform public.write_stage(run_id, 'candidates', fence, lease, 'running', 'success');

  perform public.write_stage(run_id, 'tags', fence, lease, 'pending', 'running');
  insert into public.candidate_tags(candidate_id, attempt_run_id, strategy, signal_date, status) values
    (active_a, run_id, 'A', date '2099-09-30', 'active'),
    (active_b, run_id, 'B', date '2099-09-30', 'active'),
    (active_b, run_id, 'C', date '2099-09-30', 'vanished'),
    (active_c, run_id, 'D', date '2099-09-30', 'active'),
    (active_d, run_id, 'E', date '2099-09-30', 'active'),
    (vanished_only, run_id, 'F', date '2099-09-30', 'vanished');
  perform public.write_stage(run_id, 'tags', fence, lease, 'running', 'success');
  perform public.publish_attempt(run_id, fence, lease);

  result := public.get_top_tagged_candidates(run_id);
  if jsonb_array_length(result) <> 3 then
    raise exception 'expected 3 top candidates, got %', jsonb_array_length(result);
  end if;
  if (result->0->>'ticker') <> '000003' or (result->1->>'ticker') <> '000001' or (result->2->>'ticker') <> '000002' then
    raise exception 'unexpected trading value/ticker order: %', result;
  end if;
  if exists (select 1 from jsonb_array_elements(result) e where (e->>'ticker') = '999999') then
    raise exception 'vanished-only candidate must be excluded';
  end if;
  if exists (select 1 from jsonb_array_elements(result) e where (e->>'attempt_run_id')::uuid <> run_id or (e->>'trading_day') <> '2099-09-30') then
    raise exception 'snapshot lineage is not preserved';
  end if;
end $$;

do $$
declare
  key text := 'close:2099-10-01';
  started jsonb;
  run_id uuid;
  fence bigint;
  lease uuid;
  candidate_id uuid := gen_random_uuid();
  result jsonb;
begin
  started := public.start_attempt(key, date '2099-10-01', 'close', 'manual', 300);
  run_id := (started->>'run_id')::uuid;
  fence := (started->>'fence_token')::bigint;
  lease := (started->>'lease_token')::uuid;
  perform public.write_stage(run_id, 'candidates', fence, lease, 'pending', 'running');
  perform public.write_candidates(run_id, fence, lease,
    jsonb_build_array(jsonb_build_object('candidate_id', candidate_id, 'ticker', '000010', 'name', '소멸만', 'trading_value', 500,
      'sources', jsonb_build_array(jsonb_build_object('source', 't1859', 'weight', 1)))),
    jsonb_build_object('selection_input_hash', repeat('b', 64), 'original_count', 1,
      'candidate_count', 1, 'excluded_count', 0, 'truncated_count', 0));
  perform public.write_stage(run_id, 'candidates', fence, lease, 'running', 'success');
  perform public.write_stage(run_id, 'tags', fence, lease, 'pending', 'running');
  insert into public.candidate_tags(candidate_id, attempt_run_id, strategy, signal_date, status)
    values (candidate_id, run_id, 'A', date '2099-10-01', 'vanished');
  perform public.write_stage(run_id, 'tags', fence, lease, 'running', 'success');
  perform public.publish_attempt(run_id, fence, lease);

  result := public.get_top_tagged_candidates(run_id);
  if result <> '[]'::jsonb then
    raise exception 'vanished-only snapshot must return an empty array, got %', result;
  end if;
end $$;

rollback;
