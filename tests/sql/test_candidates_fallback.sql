-- Story 1.6 SQL fixture. 202609012200_add_candidate_fallback_support.sql까지 적용한다.
begin;

-- FALLBACK_SUCCESS + MULTI_SOURCE_MERGE: t1859/t1856 두 source가 같은 종목에 기여하면
-- weight 합계는 1, fallback_used는 true로 기록된다.
do $$
#variable_conflict use_variable
declare key text := 'close:2099-03-01'; started jsonb; run_id uuid; fence bigint; lease uuid; candidate uuid := gen_random_uuid();
begin
  started := public.start_attempt(key, date '2099-03-01', 'close', 'manual', 300);
  run_id := (started->>'run_id')::uuid; fence := (started->>'fence_token')::bigint; lease := (started->>'lease_token')::uuid;
  perform public.write_stage(run_id, 'candidates', fence, lease, 'pending', 'running');
  perform public.write_candidates(
    run_id, fence, lease,
    jsonb_build_array(jsonb_build_object(
      'candidate_id', candidate, 'ticker', '005930', 'name', '삼성전자', 'trading_value', 200,
      'sources', jsonb_build_array(
        jsonb_build_object('source', 't1859', 'weight', 0.5),
        jsonb_build_object('source', 't1856', 'weight', 0.5)
      )
    )),
    jsonb_build_object('selection_input_hash', repeat('a', 64), 'original_count', 1, 'candidate_count', 1, 'excluded_count', 0, 'truncated_count', 0)
  );
  if (select count(*) from public.candidate_source_contrib where attempt_run_id = run_id) <> 2 then raise exception 'expected two source contribution rows'; end if;
  if (select sum(contribution_weight) from public.candidate_source_contrib where attempt_run_id = run_id) <> 1 then raise exception 'weight sum must equal 1'; end if;
  if (select count(*) from public.candidate_source_contrib where attempt_run_id = run_id and source = 't1859' and contribution_weight = 0.5) <> 1 then raise exception 't1859 contribution missing'; end if;
  if (select count(*) from public.candidate_source_contrib where attempt_run_id = run_id and source = 't1856' and contribution_weight = 0.5) <> 1 then raise exception 't1856 contribution missing'; end if;

  perform public.write_stage(run_id, 'candidates', fence, lease, 'running', 'success', p_fallback_used => true);
  if not (select r.fallback_used from public.runs r where r.run_id = run_id) then raise exception 'fallback_used must be true after successful fallback'; end if;
end $$;

-- BOTH_FAIL: t1859/t1856 모두 실패하면 stage는 failed, unprocessed_count>0, fallback_used는 false로 유지된다.
do $$
#variable_conflict use_variable
declare key text := 'close:2099-03-02'; started jsonb; run_id uuid; fence bigint; lease uuid;
begin
  started := public.start_attempt(key, date '2099-03-02', 'close', 'manual', 300);
  run_id := (started->>'run_id')::uuid; fence := (started->>'fence_token')::bigint; lease := (started->>'lease_token')::uuid;
  perform public.write_stage(run_id, 'candidates', fence, lease, 'pending', 'running');
  perform public.write_stage(
    run_id, 'candidates', fence, lease, 'running', 'failed',
    p_result => jsonb_build_object('result_code', 'CANDIDATE_SOURCES_EXHAUSTED', 't1859_result_code', 'HTTP_ERROR', 't1856_result_code', 'HTTP_ERROR'),
    p_unprocessed_count => 1,
    p_fallback_used => false
  );
  if (select r.status from public.runs r where r.run_id = run_id) <> 'failed' then raise exception 'stage must end failed when both sources fail'; end if;
  if (select r.unprocessed_count from public.runs r where r.run_id = run_id) <= 0 then raise exception 'unprocessed_count must be recorded as > 0'; end if;
  if (select r.fallback_used from public.runs r where r.run_id = run_id) then raise exception 'fallback_used must stay false when fallback itself failed'; end if;
end $$;

-- INVALID_CANDIDATE_SOURCE_WEIGHTS: sources weight 합계가 1이 아니면 거부된다.
do $$
declare key text := 'close:2099-03-03'; started jsonb; run_id uuid; fence bigint; lease uuid; candidate uuid := gen_random_uuid(); rejected boolean := false;
begin
  started := public.start_attempt(key, date '2099-03-03', 'close', 'manual', 300);
  run_id := (started->>'run_id')::uuid; fence := (started->>'fence_token')::bigint; lease := (started->>'lease_token')::uuid;
  perform public.write_stage(run_id, 'candidates', fence, lease, 'pending', 'running');
  begin
    perform public.write_candidates(
      run_id, fence, lease,
      jsonb_build_array(jsonb_build_object(
        'candidate_id', candidate, 'ticker', '005930', 'name', '삼성전자', 'trading_value', 100,
        'sources', jsonb_build_array(jsonb_build_object('source', 't1859', 'weight', 0.4))
      )),
      jsonb_build_object('selection_input_hash', repeat('b', 64), 'original_count', 1, 'candidate_count', 1, 'excluded_count', 0, 'truncated_count', 0)
    );
  exception when others then
    rejected := true;
  end;
  if not rejected then raise exception 'write_candidates must reject sources weight sums that are not 1'; end if;
end $$;

rollback;
