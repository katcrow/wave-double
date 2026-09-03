-- Supabase SQL fixture for Story 2.8: get_today_disappeared_candidates(p_run_id).
-- 실행 전 202609031200_create_get_today_disappeared_candidates.sql까지의 모든 migration을 적용한다.
-- psql 또는 CI의 local Supabase DB에서 실행하며, 실패 시 DO 블록이 예외를 낸다.
--
-- 커버리지:
--  1) 직전 attempt에서 active였던 ticker가 현재 attempt candidates에 없고, 현재 attempt
--     candidates stage='success'면 reason='population_dropout'.
--  2) 위와 동일하되 현재 attempt candidates stage='partial'/'failed'면 reason='collection_failure'.
--  3) 같은 거래일 직전 attempt가 없으면 빈 배열을 반환한다.
--  4) 현재 attempt candidates에 여전히 존재하는 ticker(소멸 대상)는 결과에 포함되지 않는다.
begin;

-- 시나리오 1: population_dropout.
do $$
declare
  prev_key text := 'premarket:2099-08-01'; prev_started jsonb; prev_run uuid; prev_fence bigint; prev_lease uuid;
  cur_key text := 'intraday:2099-08-01:11:00'; cur_started jsonb; cur_run uuid; cur_fence bigint; cur_lease uuid;
  dropped_id uuid := gen_random_uuid();
  -- candidates.candidate_id는 전역 PK라 attempt마다 새로 생성되며 재사용할 수 없다(ticker로만 매칭).
  prev_stayed_id uuid := gen_random_uuid();
  cur_stayed_id uuid := gen_random_uuid();
  result jsonb;
begin
  prev_started := public.start_attempt(prev_key, date '2099-08-01', 'premarket', 'manual', 300);
  prev_run := (prev_started->>'run_id')::uuid; prev_fence := (prev_started->>'fence_token')::bigint; prev_lease := (prev_started->>'lease_token')::uuid;
  perform public.write_stage(prev_run, 'candidates', prev_fence, prev_lease, 'pending', 'running');
  perform public.write_candidates(prev_run, prev_fence, prev_lease,
    jsonb_build_array(
      jsonb_build_object('candidate_id', dropped_id, 'ticker', '000110', 'name', '이탈종목', 'trading_value', 100,
        'sources', jsonb_build_array(jsonb_build_object('source', 't1859', 'weight', 1))),
      jsonb_build_object('candidate_id', prev_stayed_id, 'ticker', '000120', 'name', '유지종목', 'trading_value', 100,
        'sources', jsonb_build_array(jsonb_build_object('source', 't1859', 'weight', 1)))
    ),
    jsonb_build_object('selection_input_hash', repeat('a', 64), 'original_count', 2, 'candidate_count', 2, 'excluded_count', 0, 'truncated_count', 0));
  perform public.write_stage(prev_run, 'candidates', prev_fence, prev_lease, 'running', 'success');
  perform public.write_stage(prev_run, 'tags', prev_fence, prev_lease, 'pending', 'running');
  insert into public.candidate_tags(candidate_id, attempt_run_id, strategy, signal_date)
    values (dropped_id, prev_run, 'A', date '2099-08-01');
  insert into public.candidate_tags(candidate_id, attempt_run_id, strategy, signal_date)
    values (dropped_id, prev_run, 'C', date '2099-08-01');
  insert into public.candidate_tags(candidate_id, attempt_run_id, strategy, signal_date)
    values (prev_stayed_id, prev_run, 'A', date '2099-08-01');
  perform public.write_stage(prev_run, 'tags', prev_fence, prev_lease, 'running', 'success', jsonb_build_object('tagged_count', 3));
  update public.runs set started_at = timestamptz '2099-08-01 09:00:00+00' where run_id = prev_run;

  -- 현재 attempt: dropped_id는 조건검색 결과에서 빠지고(모집단 이탈) 같은 ticker(000120)가
  -- cur_stayed_id로만 남는다. candidates stage는 완전 성공(success) -- population_dropout 판정.
  cur_started := public.start_attempt(cur_key, date '2099-08-01', 'intraday', 'manual', 300);
  cur_run := (cur_started->>'run_id')::uuid; cur_fence := (cur_started->>'fence_token')::bigint; cur_lease := (cur_started->>'lease_token')::uuid;
  perform public.write_stage(cur_run, 'candidates', cur_fence, cur_lease, 'pending', 'running');
  perform public.write_candidates(cur_run, cur_fence, cur_lease,
    jsonb_build_array(
      jsonb_build_object('candidate_id', cur_stayed_id, 'ticker', '000120', 'name', '유지종목', 'trading_value', 100,
        'sources', jsonb_build_array(jsonb_build_object('source', 't1859', 'weight', 1)))
    ),
    jsonb_build_object('selection_input_hash', repeat('b', 64), 'original_count', 1, 'candidate_count', 1, 'excluded_count', 0, 'truncated_count', 0));
  perform public.write_stage(cur_run, 'candidates', cur_fence, cur_lease, 'running', 'success');
  update public.runs set started_at = timestamptz '2099-08-01 11:00:00+00' where run_id = cur_run;

  result := public.get_today_disappeared_candidates(cur_run);

  if jsonb_array_length(result) <> 1 then
    raise exception 'expected exactly one disappeared candidate (dropped_id), got %', jsonb_array_length(result);
  end if;
  if result->0->>'ticker' <> '000110' then
    raise exception 'expected disappeared ticker=000110, got %', result->0->>'ticker';
  end if;
  if result->0->>'reason' <> 'population_dropout' then
    raise exception 'expected reason=population_dropout when candidates stage=success, got %', result->0->>'reason';
  end if;
  if result->0->'strategies' <> '["A", "C"]'::jsonb then
    raise exception 'expected strategies=[A,C] for the disappeared candidate, got %', result->0->'strategies';
  end if;

  -- 여전히 candidates에 존재하는 stayed_id는 소멸/이탈 후보가 아니므로 결과에 없어야 한다.
  if exists (select 1 from jsonb_array_elements(result) e where e->>'ticker' = '000120') then
    raise exception 'a ticker still present in current candidates must not be reported as disappeared';
  end if;
end $$;

-- 시나리오 2: collection_failure (현재 attempt candidates stage가 partial/failed).
do $$
declare
  prev_key text := 'premarket:2099-08-02'; prev_started jsonb; prev_run uuid; prev_fence bigint; prev_lease uuid;
  cur_key text := 'intraday:2099-08-02:11:00'; cur_started jsonb; cur_run uuid; cur_fence bigint; cur_lease uuid;
  dropped_id uuid := gen_random_uuid();
  result jsonb;
begin
  prev_started := public.start_attempt(prev_key, date '2099-08-02', 'premarket', 'manual', 300);
  prev_run := (prev_started->>'run_id')::uuid; prev_fence := (prev_started->>'fence_token')::bigint; prev_lease := (prev_started->>'lease_token')::uuid;
  perform public.write_stage(prev_run, 'candidates', prev_fence, prev_lease, 'pending', 'running');
  perform public.write_candidates(prev_run, prev_fence, prev_lease,
    jsonb_build_array(jsonb_build_object('candidate_id', dropped_id, 'ticker', '000210', 'name', '수집실패종목', 'trading_value', 100,
      'sources', jsonb_build_array(jsonb_build_object('source', 't1859', 'weight', 1)))),
    jsonb_build_object('selection_input_hash', repeat('a', 64), 'original_count', 1, 'candidate_count', 1, 'excluded_count', 0, 'truncated_count', 0));
  perform public.write_stage(prev_run, 'candidates', prev_fence, prev_lease, 'running', 'success');
  perform public.write_stage(prev_run, 'tags', prev_fence, prev_lease, 'pending', 'running');
  insert into public.candidate_tags(candidate_id, attempt_run_id, strategy, signal_date)
    values (dropped_id, prev_run, 'B', date '2099-08-02');
  perform public.write_stage(prev_run, 'tags', prev_fence, prev_lease, 'running', 'success', jsonb_build_object('tagged_count', 1));
  update public.runs set started_at = timestamptz '2099-08-02 09:00:00+00' where run_id = prev_run;

  -- 현재 attempt: 후보 수집 자체가 불완전(partial) -- dropped_id 부재가 이탈인지 수집실패인지
  -- 알 수 없으므로 보수적으로 collection_failure로 분류한다.
  cur_started := public.start_attempt(cur_key, date '2099-08-02', 'intraday', 'manual', 300);
  cur_run := (cur_started->>'run_id')::uuid; cur_fence := (cur_started->>'fence_token')::bigint; cur_lease := (cur_started->>'lease_token')::uuid;
  perform public.write_stage(cur_run, 'candidates', cur_fence, cur_lease, 'pending', 'running');
  perform public.write_candidates(cur_run, cur_fence, cur_lease, '[]'::jsonb,
    jsonb_build_object('selection_input_hash', repeat('b', 64), 'original_count', 0, 'candidate_count', 0, 'excluded_count', 0, 'truncated_count', 0));
  perform public.write_stage(cur_run, 'candidates', cur_fence, cur_lease, 'running', 'partial', jsonb_build_object('result_code', 'PARTIAL_CANDIDATES'), 1);
  update public.runs set started_at = timestamptz '2099-08-02 11:00:00+00' where run_id = cur_run;

  result := public.get_today_disappeared_candidates(cur_run);

  if jsonb_array_length(result) <> 1 then
    raise exception 'expected exactly one disappeared candidate, got %', jsonb_array_length(result);
  end if;
  if result->0->>'reason' <> 'collection_failure' then
    raise exception 'expected reason=collection_failure when candidates stage=partial, got %', result->0->>'reason';
  end if;
end $$;

-- 시나리오 3: 같은 거래일 직전 attempt가 없으면 빈 배열.
do $$
declare
  key text := 'close:2099-08-03'; started jsonb; run_id uuid; fence bigint; lease uuid;
  result jsonb;
begin
  started := public.start_attempt(key, date '2099-08-03', 'close', 'manual', 300);
  run_id := (started->>'run_id')::uuid; fence := (started->>'fence_token')::bigint; lease := (started->>'lease_token')::uuid;
  perform public.write_stage(run_id, 'candidates', fence, lease, 'pending', 'running');
  perform public.write_candidates(run_id, fence, lease, '[]'::jsonb,
    jsonb_build_object('selection_input_hash', repeat('c', 64), 'original_count', 0, 'candidate_count', 0, 'excluded_count', 0, 'truncated_count', 0));
  perform public.write_stage(run_id, 'candidates', fence, lease, 'running', 'success');

  result := public.get_today_disappeared_candidates(run_id);
  if result <> '[]'::jsonb then
    raise exception 'expected empty array when there is no prior same-day attempt, got %', result;
  end if;
end $$;

rollback;
