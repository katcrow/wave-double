-- Supabase SQL fixture for Story 2.8: sync_vanished_tags(p_run_id).
-- 실행 전 202609031000_create_sync_vanished_tags.sql까지의 모든 migration을 적용한다.
-- psql 또는 CI의 local Supabase DB에서 실행하며, 실패 시 DO 블록이 예외를 낸다.
--
-- 커버리지:
--  1) 직전 attempt에서 A,B로 active였던 ticker가 현재 attempt에서 A만 재태깅되면 B가 vanished로 삽입된다.
--  2) 현재 attempt에서 재태깅되지 않았고 ticker도 현재 candidates에 없으면 vanished가 삽입되지 않는다
--     (population dropout/collection failure는 get_today_disappeared_candidates의 몫).
--  3) 과거(직전) attempt의 candidate_tags 행은 UPDATE되지 않는다(append-only).
--  4) 같은 거래일 직전 attempt가 없으면(당일 최초) no-op, vanished_count=0.
--  5) 재실행해도 중복 삽입되지 않는다(idempotent, on conflict do nothing).
begin;

-- 시나리오 1,2,3: 부분 재태깅 + 모집단 이탈 혼재.
do $$
declare
  prev_key text := 'premarket:2099-07-01'; prev_started jsonb; prev_run uuid; prev_fence bigint; prev_lease uuid;
  cur_key text := 'intraday:2099-07-01:11:00'; cur_started jsonb; cur_run uuid; cur_fence bigint; cur_lease uuid;
  -- candidates.candidate_id는 전역 PK라 attempt마다 새로 생성되며 재사용할 수 없다(ticker로만 매칭).
  prev_stayed_id uuid := gen_random_uuid();  -- 직전 attempt 소유 '유지종목' 후보 행
  cur_stayed_id uuid := gen_random_uuid();   -- 현재 attempt 소유 '유지종목' 후보 행(같은 ticker, 다른 candidate_id)
  dropped_id uuid;                       -- 이전 attempt에서만 태깅, 이번 attempt candidates에 없음 -- vanished 대상 아님
  sync_result jsonb;
begin
  -- 직전 attempt(premarket): prev_stayed_id(A,B active), dropped_id(A active).
  prev_started := public.start_attempt(prev_key, date '2099-07-01', 'premarket', 'manual', 300);
  prev_run := (prev_started->>'run_id')::uuid; prev_fence := (prev_started->>'fence_token')::bigint; prev_lease := (prev_started->>'lease_token')::uuid;
  dropped_id := gen_random_uuid();
  perform public.write_stage(prev_run, 'candidates', prev_fence, prev_lease, 'pending', 'running');
  perform public.write_candidates(prev_run, prev_fence, prev_lease,
    jsonb_build_array(
      jsonb_build_object('candidate_id', prev_stayed_id, 'ticker', '000010', 'name', '유지종목', 'trading_value', 100,
        'sources', jsonb_build_array(jsonb_build_object('source', 't1859', 'weight', 1))),
      jsonb_build_object('candidate_id', dropped_id, 'ticker', '000020', 'name', '이탈종목', 'trading_value', 100,
        'sources', jsonb_build_array(jsonb_build_object('source', 't1859', 'weight', 1)))
    ),
    jsonb_build_object('selection_input_hash', repeat('a', 64), 'original_count', 2, 'candidate_count', 2, 'excluded_count', 0, 'truncated_count', 0));
  perform public.write_stage(prev_run, 'candidates', prev_fence, prev_lease, 'running', 'success');
  perform public.write_stage(prev_run, 'tags', prev_fence, prev_lease, 'pending', 'running');
  insert into public.candidate_tags(candidate_id, attempt_run_id, strategy, signal_date, params_meta)
    values (prev_stayed_id, prev_run, 'A', date '2099-07-01', '{"batch_kind":"premarket"}'::jsonb);
  insert into public.candidate_tags(candidate_id, attempt_run_id, strategy, signal_date, params_meta)
    values (prev_stayed_id, prev_run, 'B', date '2099-07-01', '{"batch_kind":"premarket"}'::jsonb);
  insert into public.candidate_tags(candidate_id, attempt_run_id, strategy, signal_date, params_meta)
    values (dropped_id, prev_run, 'A', date '2099-07-01', '{"batch_kind":"premarket"}'::jsonb);
  perform public.write_stage(prev_run, 'tags', prev_fence, prev_lease, 'running', 'success', jsonb_build_object('tagged_count', 3));
  -- 트랜잭션 내내 now()가 고정되므로 started_at을 명시적으로 앞선 시각으로 고정한다.
  update public.runs set started_at = timestamptz '2099-07-01 09:00:00+00' where run_id = prev_run;

  -- 현재 attempt(intraday 11:00): 같은 ticker(000010)가 cur_stayed_id로 candidates에 남아 있고
  -- A만 재태깅. dropped_id(000020)는 candidates에서 아예 사라짐(모집단 이탈/수집실패 --
  -- sync_vanished_tags 대상 아님).
  cur_started := public.start_attempt(cur_key, date '2099-07-01', 'intraday', 'manual', 300);
  cur_run := (cur_started->>'run_id')::uuid; cur_fence := (cur_started->>'fence_token')::bigint; cur_lease := (cur_started->>'lease_token')::uuid;
  perform public.write_stage(cur_run, 'candidates', cur_fence, cur_lease, 'pending', 'running');
  perform public.write_candidates(cur_run, cur_fence, cur_lease,
    jsonb_build_array(
      jsonb_build_object('candidate_id', cur_stayed_id, 'ticker', '000010', 'name', '유지종목', 'trading_value', 100,
        'sources', jsonb_build_array(jsonb_build_object('source', 't1859', 'weight', 1)))
    ),
    jsonb_build_object('selection_input_hash', repeat('b', 64), 'original_count', 1, 'candidate_count', 1, 'excluded_count', 0, 'truncated_count', 0));
  perform public.write_stage(cur_run, 'candidates', cur_fence, cur_lease, 'running', 'success');
  perform public.write_stage(cur_run, 'tags', cur_fence, cur_lease, 'pending', 'running');
  insert into public.candidate_tags(candidate_id, attempt_run_id, strategy, signal_date, params_meta)
    values (cur_stayed_id, cur_run, 'A', date '2099-07-01', '{"batch_kind":"intraday"}'::jsonb);
  perform public.write_stage(cur_run, 'tags', cur_fence, cur_lease, 'running', 'success', jsonb_build_object('tagged_count', 1));
  update public.runs set started_at = timestamptz '2099-07-01 11:00:00+00' where run_id = cur_run;

  sync_result := public.sync_vanished_tags(cur_run);

  if (sync_result->>'vanished_count')::integer <> 1 then
    raise exception 'expected vanished_count=1 (cur_stayed_id strategy B), got %', sync_result->>'vanished_count';
  end if;

  if not exists (
    select 1 from public.candidate_tags
    where candidate_id = cur_stayed_id and attempt_run_id = cur_run and strategy = 'B' and status = 'vanished'
  ) then
    raise exception 'expected a vanished candidate_tags row for cur_stayed_id/B owned by the current attempt';
  end if;

  -- dropped_id는 현재 attempt candidates에 없으므로 vanished 삽입 대상이 아니다(현재 attempt에
  -- dropped_id 소유 candidates 행 자체가 없어 FK를 만족할 수 없다).
  if exists (
    select 1 from public.candidate_tags where attempt_run_id = cur_run and candidate_id = dropped_id
  ) then
    raise exception 'dropped_id must not gain any candidate_tags row under the current attempt';
  end if;

  -- 과거(직전) attempt의 행은 그대로 active로 남아 있어야 한다(append-only, UPDATE 금지).
  if (select count(*) from public.candidate_tags where attempt_run_id = prev_run and status = 'active') <> 3 then
    raise exception 'previous attempt candidate_tags rows must remain active and untouched';
  end if;

  -- 재실행해도 중복 삽입되지 않는다(idempotent).
  sync_result := public.sync_vanished_tags(cur_run);
  if (sync_result->>'vanished_count')::integer <> 0 then
    raise exception 'expected vanished_count=0 on idempotent re-run, got %', sync_result->>'vanished_count';
  end if;
  if (select count(*) from public.candidate_tags where attempt_run_id = cur_run and status = 'vanished') <> 1 then
    raise exception 'expected exactly one vanished row after re-running sync_vanished_tags twice';
  end if;
end $$;

-- 시나리오 4: 같은 거래일 직전 attempt가 없으면(당일 최초) no-op.
do $$
declare
  key text := 'close:2099-07-02'; started jsonb; run_id uuid; fence bigint; lease uuid;
  candidate_id uuid := gen_random_uuid();
  sync_result jsonb;
begin
  started := public.start_attempt(key, date '2099-07-02', 'close', 'manual', 300);
  run_id := (started->>'run_id')::uuid; fence := (started->>'fence_token')::bigint; lease := (started->>'lease_token')::uuid;
  perform public.write_stage(run_id, 'candidates', fence, lease, 'pending', 'running');
  perform public.write_candidates(run_id, fence, lease,
    jsonb_build_array(jsonb_build_object('candidate_id', candidate_id, 'ticker', '000030', 'name', '최초종목', 'trading_value', 100,
      'sources', jsonb_build_array(jsonb_build_object('source', 't1859', 'weight', 1)))),
    jsonb_build_object('selection_input_hash', repeat('c', 64), 'original_count', 1, 'candidate_count', 1, 'excluded_count', 0, 'truncated_count', 0));
  perform public.write_stage(run_id, 'candidates', fence, lease, 'running', 'success');
  perform public.write_stage(run_id, 'tags', fence, lease, 'pending', 'running');
  insert into public.candidate_tags(candidate_id, attempt_run_id, strategy, signal_date)
    values (candidate_id, run_id, 'A', date '2099-07-02');
  perform public.write_stage(run_id, 'tags', fence, lease, 'running', 'success', jsonb_build_object('tagged_count', 1));

  sync_result := public.sync_vanished_tags(run_id);
  if (sync_result->>'vanished_count')::integer <> 0 then
    raise exception 'expected vanished_count=0 when no prior same-day attempt exists, got %', sync_result->>'vanished_count';
  end if;
  if exists (select 1 from public.candidate_tags where attempt_run_id = run_id and status = 'vanished') then
    raise exception 'no vanished rows expected when there is no prior same-day attempt';
  end if;
end $$;

-- 시나리오 6: 같은 거래일 중간 attempt의 tags stage가 'failed'면 직전 attempt 탐색 시 건너뛴다.
-- attempt1(success, ticker X strategy A active) -> attempt2(failed, candidate_tags 없음)
-- -> attempt3(현재, X는 candidates에 남아 있으나 재태깅되지 않음). attempt3의 sync_vanished_tags는
-- attempt2가 아니라 attempt1을 비교 대상으로 찾아 X/A를 vanished로 삽입해야 한다.
do $$
declare
  a1_key text := 'close:2099-07-03'; a1_started jsonb; a1_run uuid; a1_fence bigint; a1_lease uuid;
  a2_key text := 'intraday:2099-07-03:10:00'; a2_started jsonb; a2_run uuid; a2_fence bigint; a2_lease uuid;
  a3_key text := 'intraday:2099-07-03:11:00'; a3_started jsonb; a3_run uuid; a3_fence bigint; a3_lease uuid;
  a1_candidate_id uuid := gen_random_uuid();
  a2_candidate_id uuid := gen_random_uuid();
  a3_candidate_id uuid := gen_random_uuid();
  sync_result jsonb;
begin
  -- attempt1: tags stage success, ticker X(000040) strategy A active.
  a1_started := public.start_attempt(a1_key, date '2099-07-03', 'close', 'manual', 300);
  a1_run := (a1_started->>'run_id')::uuid; a1_fence := (a1_started->>'fence_token')::bigint; a1_lease := (a1_started->>'lease_token')::uuid;
  perform public.write_stage(a1_run, 'candidates', a1_fence, a1_lease, 'pending', 'running');
  perform public.write_candidates(a1_run, a1_fence, a1_lease,
    jsonb_build_array(jsonb_build_object('candidate_id', a1_candidate_id, 'ticker', '000040', 'name', 'X종목', 'trading_value', 100,
      'sources', jsonb_build_array(jsonb_build_object('source', 't1859', 'weight', 1)))),
    jsonb_build_object('selection_input_hash', repeat('d', 64), 'original_count', 1, 'candidate_count', 1, 'excluded_count', 0, 'truncated_count', 0));
  perform public.write_stage(a1_run, 'candidates', a1_fence, a1_lease, 'running', 'success');
  perform public.write_stage(a1_run, 'tags', a1_fence, a1_lease, 'pending', 'running');
  insert into public.candidate_tags(candidate_id, attempt_run_id, strategy, signal_date, params_meta)
    values (a1_candidate_id, a1_run, 'A', date '2099-07-03', '{"batch_kind":"close"}'::jsonb);
  perform public.write_stage(a1_run, 'tags', a1_fence, a1_lease, 'running', 'success', jsonb_build_object('tagged_count', 1));
  update public.runs set started_at = timestamptz '2099-07-03 09:00:00+00' where run_id = a1_run;

  -- attempt2: tags stage failed, candidate_tags 없음(태깅 자체가 실패했으므로).
  a2_started := public.start_attempt(a2_key, date '2099-07-03', 'intraday', 'manual', 300);
  a2_run := (a2_started->>'run_id')::uuid; a2_fence := (a2_started->>'fence_token')::bigint; a2_lease := (a2_started->>'lease_token')::uuid;
  perform public.write_stage(a2_run, 'candidates', a2_fence, a2_lease, 'pending', 'running');
  perform public.write_candidates(a2_run, a2_fence, a2_lease,
    jsonb_build_array(jsonb_build_object('candidate_id', a2_candidate_id, 'ticker', '000040', 'name', 'X종목', 'trading_value', 100,
      'sources', jsonb_build_array(jsonb_build_object('source', 't1859', 'weight', 1)))),
    jsonb_build_object('selection_input_hash', repeat('e', 64), 'original_count', 1, 'candidate_count', 1, 'excluded_count', 0, 'truncated_count', 0));
  perform public.write_stage(a2_run, 'candidates', a2_fence, a2_lease, 'running', 'success');
  perform public.write_stage(a2_run, 'tags', a2_fence, a2_lease, 'pending', 'running');
  perform public.write_stage(a2_run, 'tags', a2_fence, a2_lease, 'running', 'failed', jsonb_build_object('result_code', 'CANDIDATE_FETCH_FAILED'));
  update public.runs set started_at = timestamptz '2099-07-03 10:00:00+00' where run_id = a2_run;

  -- attempt3(현재): X는 candidates에 남아 있으나 재태깅되지 않음(strategy A 없음).
  a3_started := public.start_attempt(a3_key, date '2099-07-03', 'intraday', 'manual', 300);
  a3_run := (a3_started->>'run_id')::uuid; a3_fence := (a3_started->>'fence_token')::bigint; a3_lease := (a3_started->>'lease_token')::uuid;
  perform public.write_stage(a3_run, 'candidates', a3_fence, a3_lease, 'pending', 'running');
  perform public.write_candidates(a3_run, a3_fence, a3_lease,
    jsonb_build_array(jsonb_build_object('candidate_id', a3_candidate_id, 'ticker', '000040', 'name', 'X종목', 'trading_value', 100,
      'sources', jsonb_build_array(jsonb_build_object('source', 't1859', 'weight', 1)))),
    jsonb_build_object('selection_input_hash', repeat('f', 64), 'original_count', 1, 'candidate_count', 1, 'excluded_count', 0, 'truncated_count', 0));
  perform public.write_stage(a3_run, 'candidates', a3_fence, a3_lease, 'running', 'success');
  perform public.write_stage(a3_run, 'tags', a3_fence, a3_lease, 'pending', 'running');
  perform public.write_stage(a3_run, 'tags', a3_fence, a3_lease, 'running', 'success', jsonb_build_object('tagged_count', 0));
  update public.runs set started_at = timestamptz '2099-07-03 11:00:00+00' where run_id = a3_run;

  sync_result := public.sync_vanished_tags(a3_run);

  if (sync_result->>'vanished_count')::integer <> 1 then
    raise exception 'expected vanished_count=1 (X/A found via attempt1, skipping failed attempt2), got %', sync_result->>'vanished_count';
  end if;

  if not exists (
    select 1 from public.candidate_tags
    where candidate_id = a3_candidate_id and attempt_run_id = a3_run and strategy = 'A' and status = 'vanished'
  ) then
    raise exception 'expected a vanished candidate_tags row for a3_candidate_id/A (comparison must have used attempt1, not the failed attempt2)';
  end if;

  if exists (select 1 from public.candidate_tags where attempt_run_id = a2_run) then
    raise exception 'attempt2 (failed tags stage) must not gain any candidate_tags rows';
  end if;
end $$;

rollback;
