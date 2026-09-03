-- Supabase SQL fixture for Story 1.3.
-- 실행 전 lineage/candidates migration과 202609012100 hardening migration을 적용한다.
-- psql 또는 CI의 local Supabase DB에서 실행하며, 실패 시 DO 블록이 예외를 낸다.
begin;

do $$
 declare key text := 'close:2099-01-02'; started jsonb; attempt_id uuid; fence bigint; lease uuid; caught boolean := false;
begin
  started := public.start_attempt(key, date '2099-01-02', 'close', 'manual', 300);
   attempt_id := (started->>'run_id')::uuid; fence := (started->>'fence_token')::bigint; lease := (started->>'lease_token')::uuid;
   if (select jsonb_object_keys(stage_status) from public.runs where runs.run_id = attempt_id order by 1 limit 1) is null then
    raise exception 'stage registry is empty';
  end if;
   if (select count(*) from jsonb_object_keys((select stage_status from public.runs where runs.run_id = attempt_id))) <> 5 then
    raise exception 'expected five initial stages';
  end if;
   perform public.write_stage(attempt_id, 'candidates', fence, lease, 'pending', 'running');
   perform public.write_stage(attempt_id, 'candidates', fence, lease, 'running', 'success');
   if (select status from public.runs where runs.run_id = attempt_id) <> 'ready_to_publish' then raise exception 'not ready'; end if;
   -- Story 2.5: publish_attempt는 tags stage success도 게이트로 요구한다.
   perform public.write_stage(attempt_id, 'tags', fence, lease, 'pending', 'running');
   perform public.write_stage(attempt_id, 'tags', fence, lease, 'running', 'success');
  perform public.publish_attempt(attempt_id, fence, lease);
   if (select canonical_success_run_id from public.logical_runs where logical_run_key = key) <> attempt_id then raise exception 'close canonical pointer missing'; end if;
   if (select status from public.runs where runs.run_id = attempt_id) <> 'published' then raise exception 'not published'; end if;
   -- Story 3.3: 활성 태그가 없는 close attempt도 outcome_tracking stage가 success로 종결되어야 한다(빈 루프).
   if (select stage_status->>'outcome_tracking' from public.runs where runs.run_id = attempt_id) <> 'success' then
     raise exception 'expected outcome_tracking=success for close publish with no active tags';
   end if;
  begin
     perform public.write_stage(attempt_id, 'candidates', fence, lease, 'success', 'success');
  exception when others then caught := true;
  end;
  if not caught then raise exception 'published attempt accepted stage rewrite'; end if;
end $$;

do $$
 declare key text := 'intraday:2099-01-02:14:30'; started jsonb; attempt_id uuid; fence bigint; lease uuid; caught boolean := false;
begin
  started := public.start_attempt(key, date '2099-01-02', 'intraday', 'schedule', 300);
   attempt_id := (started->>'run_id')::uuid; fence := (started->>'fence_token')::bigint; lease := (started->>'lease_token')::uuid;
   perform public.write_stage(attempt_id, 'candidates', fence, lease, 'pending', 'running');
   perform public.write_stage(attempt_id, 'candidates', fence, lease, 'running', 'partial', '{}'::jsonb, 1);
   if (select status from public.runs where runs.run_id = attempt_id) <> 'partial' then raise exception 'partial status missing'; end if;
   if (select latest_partial_run_id from public.logical_runs where logical_run_key = key) <> attempt_id then raise exception 'latest partial pointer missing'; end if;
  if exists (select 1 from public.logical_runs where logical_run_key = key and current_complete_run_id is not null) then raise exception 'partial changed complete pointer'; end if;
  caught := false;
  begin
     perform public.publish_attempt(attempt_id, fence, lease);
  exception when others then caught := true;
  end;
  if not caught then raise exception 'partial attempt was published'; end if;
end $$;

do $$
declare key text := 'close:2099-01-03'; first_run uuid; second_run uuid; first_fence bigint; first_lease uuid; started jsonb; caught boolean := false;
begin
  started := public.start_attempt(key, date '2099-01-03', 'close', 'schedule', 300);
  first_run := (started->>'run_id')::uuid; first_fence := (started->>'fence_token')::bigint; first_lease := (started->>'lease_token')::uuid;
  started := public.start_attempt(key, date '2099-01-03', 'close', 'manual', 300);
  second_run := (started->>'run_id')::uuid;
  if (select status from public.runs where run_id = first_run) <> 'superseded' then raise exception 'old attempt was not superseded'; end if;
  if (select active_attempt_run_id from public.logical_runs where logical_run_key = key) <> second_run then raise exception 'second attempt did not acquire active fence'; end if;
  begin
    perform public.write_stage(first_run, 'candidates', first_fence, first_lease, 'pending', 'running');
  exception when others then caught := true;
  end;
  if not caught then raise exception 'stale attempt was allowed to write'; end if;
end $$;

do $$
 declare key text := 'close:2099-01-04'; started jsonb; attempt_id uuid; fence bigint; lease uuid;
begin
  started := public.start_attempt(key, date '2099-01-04', 'close', 'manual', 300);
   attempt_id := (started->>'run_id')::uuid; fence := (started->>'fence_token')::bigint; lease := (started->>'lease_token')::uuid;
   perform public.write_stage(attempt_id, 'candidates', fence, lease, 'pending', 'running');
   perform public.write_stage(attempt_id, 'candidates', fence, lease, 'running', 'success');
   update public.runs set status = 'running', lease_expires_at = now() - interval '1 second' where public.runs.run_id = attempt_id;
  perform public.reap_expired_attempts(now());
   if (select status from public.runs where public.runs.run_id = attempt_id) <> 'ready_to_publish' then raise exception 'salvage did not become ready'; end if;
   if (select active_attempt_run_id from public.logical_runs where logical_run_key = key) <> attempt_id then raise exception 'salvage incorrectly cleared active attempt'; end if;
end $$;

do $$
 declare key text := 'close:2099-01-05'; started jsonb; attempt_id uuid; fence bigint; lease uuid; caught boolean := false;
begin
  started := public.start_attempt(key, date '2099-01-05', 'close', 'manual', 300);
   attempt_id := (started->>'run_id')::uuid; fence := (started->>'fence_token')::bigint; lease := (started->>'lease_token')::uuid;
  begin
     perform public.write_stage(attempt_id, 'candidates', fence + 1, lease, 'pending', 'running');
  exception when others then caught := true;
  end;
  if not caught then raise exception 'wrong fence was accepted'; end if;
   if (select stage_status->>'candidates' from public.runs where public.runs.run_id = attempt_id) <> 'pending' then raise exception 'stale write changed stage'; end if;
   update public.runs set lease_expires_at = now() - interval '1 second' where public.runs.run_id = attempt_id;
  caught := false;
  begin
     perform public.heartbeat_attempt(attempt_id, fence, lease, 300);
  exception when others then caught := true;
  end;
  if not caught then raise exception 'expired lease was accepted'; end if;
end $$;

do $$
declare caught boolean := false;
begin
  begin
    perform public.start_attempt('intraday:2099-01-06:14:15', date '2099-01-06', 'intraday', 'manual', 300);
  exception when others then caught := true;
  end;
  if not caught then raise exception 'non-half-hour slot was accepted'; end if;
end $$;

-- Story 3.3: close 발행이 활성 태그 다수를 outcome OPEN으로 연결한다(AD-20).
do $$
declare
  key text := 'close:2099-01-07'; started jsonb; attempt_id uuid; fence bigint; lease uuid;
  candidate_a uuid := gen_random_uuid();
  candidate_b uuid := gen_random_uuid();
  open_event_count integer;
  open_projection_count integer;
begin
  insert into public.daily_ohlcv(ticker, trading_day, open, high, low, close, volume)
    values
      ('ZZLIN1', date '2099-01-07', 100, 105, 99, 101, 1000),
      ('ZZLIN2', date '2099-01-07', 200, 205, 199, 201, 1000)
    on conflict (ticker, trading_day) do nothing;

  started := public.start_attempt(key, date '2099-01-07', 'close', 'manual', 300);
  attempt_id := (started->>'run_id')::uuid; fence := (started->>'fence_token')::bigint; lease := (started->>'lease_token')::uuid;
  perform public.write_stage(attempt_id, 'candidates', fence, lease, 'pending', 'running');
  perform public.write_candidates(attempt_id, fence, lease,
    jsonb_build_array(
      jsonb_build_object('candidate_id', candidate_a, 'ticker', 'ZZLIN1', 'name', 'Lineage Test 1', 'trading_value', 100,
        'sources', jsonb_build_array(jsonb_build_object('source', 't1859', 'weight', 1))),
      jsonb_build_object('candidate_id', candidate_b, 'ticker', 'ZZLIN2', 'name', 'Lineage Test 2', 'trading_value', 100,
        'sources', jsonb_build_array(jsonb_build_object('source', 't1859', 'weight', 1)))),
    jsonb_build_object('selection_input_hash', repeat('b', 64), 'original_count', 2, 'candidate_count', 2, 'excluded_count', 0, 'truncated_count', 0));
  perform public.write_stage(attempt_id, 'candidates', fence, lease, 'running', 'success');
  perform public.write_stage(attempt_id, 'tags', fence, lease, 'pending', 'running');
  insert into public.candidate_tags(candidate_id, attempt_run_id, strategy, signal_date)
    values (candidate_a, attempt_id, 'A', date '2099-01-07'), (candidate_b, attempt_id, 'B', date '2099-01-07');
  perform public.write_stage(attempt_id, 'tags', fence, lease, 'running', 'success', jsonb_build_object('tagged_count', 2));

  perform public.publish_attempt(attempt_id, fence, lease);

  if (select status from public.runs where run_id = attempt_id) <> 'published' then raise exception 'close attempt with active tags did not publish'; end if;
  if (select stage_status->>'outcome_tracking' from public.runs where run_id = attempt_id) <> 'success' then
    raise exception 'expected outcome_tracking=success for close publish with active tags';
  end if;

  select count(*) into open_event_count from public.outcome_events
    where logical_run_key = key and command_type = 'OPEN';
  if open_event_count <> 2 then raise exception 'expected 2 OPEN events for 2 active (ticker,strategy) tags, got %', open_event_count; end if;

  select count(*) into open_projection_count from public.candidate_outcome
    where (ticker, strategy) in (('ZZLIN1', 'A'), ('ZZLIN2', 'B')) and status = 'OPEN';
  if open_projection_count <> 2 then raise exception 'expected 2 OPEN candidate_outcome rows, got %', open_projection_count; end if;

  -- Story 3.4: 방금 신규 OPEN된 두 outcome도 같은 트랜잭션에서 진입일 관찰이 함께 기록되어야 한다.
  if not exists (
    select 1 from public.outcome_observations oo
      join public.candidate_outcome co on co.outcome_id = oo.outcome_id
      where co.ticker = 'ZZLIN1' and co.strategy = 'A' and oo.evaluation_trading_day = date '2099-01-07'
        and oo.high = 105 and oo.low = 99 and oo.close = 101 and oo.result_code = 'OK'
  ) then
    raise exception 'expected entry-day observation for ZZLIN1/A';
  end if;
  if not exists (
    select 1 from public.outcome_observations oo
      join public.candidate_outcome co on co.outcome_id = oo.outcome_id
      where co.ticker = 'ZZLIN2' and co.strategy = 'B' and oo.evaluation_trading_day = date '2099-01-07'
        and oo.high = 205 and oo.low = 199 and oo.close = 201 and oo.result_code = 'OK'
  ) then
    raise exception 'expected entry-day observation for ZZLIN2/B';
  end if;
end $$;

-- Story 3.4: 일자별 판정 관찰 수집 -- 기존 OPEN outcome의 다음 거래일 관찰 추가, terminal 제외,
-- 멱등 재시도, daily_ohlcv 결측 시 그 outcome만 건너뛰고 publish는 정상 커밋됨을 검증한다.
do $$
declare
  key text := 'close:2099-01-10'; started jsonb; attempt_id uuid; fence bigint; lease uuid;
  outcome_a uuid; outcome_b uuid; outcome_tp uuid; outcome_invalid uuid;
  obs_count integer;
  direct_result jsonb;
begin
  -- ZZLIN1(strategy A)/ZZLIN2(strategy B)는 2099-01-07 close에서 이미 OPEN되었다.
  -- 오늘(2099-01-10)은 ZZLIN1의 종가만 존재하고 ZZLIN2는 의도적으로 daily_ohlcv를 결측시킨다.
  insert into public.daily_ohlcv(ticker, trading_day, open, high, low, close, volume)
    values ('ZZLIN1', date '2099-01-10', 101, 110, 100, 108, 1000)
    on conflict (ticker, trading_day) do nothing;

  -- ZZLIN7(strategy C)는 daily_ohlcv 행이 존재하지만 high/low/close 순서가 무효(low > high)한 상태다.
  -- outcome_observations_high_low_close_order 제약을 건드리기 전에 record_outcome_observation이
  -- 예외 없이 걸러내는지, 그리고 그 걸러냄이 publish_attempt 전체를 rollback시키지 않는지 검증한다.
  insert into public.outcome_events(ticker, strategy, command_type, logical_run_key, payload)
    values ('ZZLIN7', 'C', 'OPEN', 'close:2099-01-07', jsonb_build_object('entry_date', date '2099-01-01', 'entry_price', 100));
  insert into public.candidate_outcome(ticker, strategy, entry_date, entry_price, status)
    values ('ZZLIN7', 'C', date '2099-01-01', 100, 'OPEN')
    returning outcome_id into outcome_invalid;
  insert into public.daily_ohlcv(ticker, trading_day, open, high, low, close, volume)
    values ('ZZLIN7', date '2099-01-10', 100, 95, 105, 100, 1000)
    on conflict (ticker, trading_day) do nothing;

  select outcome_id into outcome_a from public.candidate_outcome where ticker = 'ZZLIN1' and strategy = 'A';
  select outcome_id into outcome_b from public.candidate_outcome where ticker = 'ZZLIN2' and strategy = 'B';
  if outcome_a is null or outcome_b is null then raise exception 'expected prior OPEN outcomes from 2099-01-07 scenario'; end if;

  -- terminal 상태(TP) outcome은 관찰 대상 조회에서 제외되어야 한다.
  insert into public.outcome_events(ticker, strategy, command_type, logical_run_key, payload)
    values ('ZZLIN6', 'C', 'OPEN', 'close:2099-01-07', jsonb_build_object('entry_date', date '2099-01-01', 'entry_price', 100));
  insert into public.candidate_outcome(ticker, strategy, entry_date, entry_price, status, exit_date, exit_price, return_pct)
    values ('ZZLIN6', 'C', date '2099-01-01', 100, 'TP', date '2099-01-02', 103, 2.9)
    returning outcome_id into outcome_tp;

  started := public.start_attempt(key, date '2099-01-10', 'close', 'manual', 300);
  attempt_id := (started->>'run_id')::uuid; fence := (started->>'fence_token')::bigint; lease := (started->>'lease_token')::uuid;
  perform public.write_stage(attempt_id, 'candidates', fence, lease, 'pending', 'running');
  perform public.write_stage(attempt_id, 'candidates', fence, lease, 'running', 'success');
  perform public.write_stage(attempt_id, 'tags', fence, lease, 'pending', 'running');
  perform public.write_stage(attempt_id, 'tags', fence, lease, 'running', 'success');

  perform public.publish_attempt(attempt_id, fence, lease);

  if (select status from public.runs where run_id = attempt_id) <> 'published' then
    raise exception 'close attempt with tracked outcomes but no active tags did not publish';
  end if;
  if (select stage_status->>'outcome_tracking' from public.runs where run_id = attempt_id) <> 'success' then
    raise exception 'expected outcome_tracking=success for observation-only close publish';
  end if;

  -- ZZLIN1(outcome_a): daily_ohlcv 존재 -> 관찰 1행 신규 기록.
  select count(*) into obs_count from public.outcome_observations
    where outcome_id = outcome_a and evaluation_trading_day = date '2099-01-10';
  if obs_count <> 1 then raise exception 'expected 1 observation row for outcome_a on 2099-01-10, got %', obs_count; end if;
  if not exists (
    select 1 from public.outcome_observations
      where outcome_id = outcome_a and evaluation_trading_day = date '2099-01-10'
        and high = 110 and low = 100 and close = 108 and result_code = 'OK'
  ) then
    raise exception 'observation values did not match daily_ohlcv for outcome_a';
  end if;

  -- ZZLIN2(outcome_b): daily_ohlcv 결측 -> 관찰 없이 건너뛰지만 publish는 정상 커밋되어야 한다(이미 위에서 확인).
  if exists (select 1 from public.outcome_observations where outcome_id = outcome_b and evaluation_trading_day = date '2099-01-10') then
    raise exception 'observation should not exist for outcome_b due to missing daily_ohlcv';
  end if;

  -- Story 3.5: 오늘 daily_ohlcv가 없으면 SUSPENDED 감지 루프도 판정 근거가 없어 자연 제외되어야 한다
  -- (outcome_b는 이 attempt에서 daily_ohlcv가 없는 채로 status='OPEN'을 유지해야 하며, SUSPENDED로 잘못
  -- 전이되거나 예외가 발생하면 안 된다).
  if (select status from public.candidate_outcome where outcome_id = outcome_b) <> 'OPEN' then
    raise exception 'expected outcome_b to remain OPEN when today''s daily_ohlcv is missing (no basis for SUSPENDED detection)';
  end if;
  if exists (select 1 from public.outcome_events where ticker = 'ZZLIN2' and strategy = 'B' and command_type = 'SUSPENDED') then
    raise exception 'unexpected SUSPENDED event for ZZLIN2/B despite missing daily_ohlcv';
  end if;

  -- terminal(TP) outcome은 관찰 루프에서 제외된다.
  if exists (select 1 from public.outcome_observations where outcome_id = outcome_tp and evaluation_trading_day = date '2099-01-10') then
    raise exception 'terminal TP outcome should not receive a new observation';
  end if;

  -- 멱등 재시도: 동일 (outcome_id, evaluation_trading_day)에 대한 직접 RPC 재호출은 새 행을 만들지 않는다.
  direct_result := public.record_outcome_observation(outcome_a, 'ZZLIN1', date '2099-01-10');
  if (direct_result->>'replayed')::boolean is not true then raise exception 'expected replayed:true on idempotent retry'; end if;
  if (direct_result->>'recorded')::boolean is not true then raise exception 'expected recorded:true on idempotent retry'; end if;
  select count(*) into obs_count from public.outcome_observations
    where outcome_id = outcome_a and evaluation_trading_day = date '2099-01-10';
  if obs_count <> 1 then raise exception 'idempotent retry created a duplicate observation row, got %', obs_count; end if;

  -- daily_ohlcv 결측에 대한 직접 RPC 반환값도 확인한다(예외 없이 recorded:false를 반환).
  direct_result := public.record_outcome_observation(outcome_b, 'ZZLIN2', date '2099-01-10');
  if (direct_result->>'recorded')::boolean is not false then raise exception 'expected recorded:false for missing daily_ohlcv'; end if;
  if direct_result->>'reason' <> 'MISSING_DAILY_OHLCV' then raise exception 'expected reason MISSING_DAILY_OHLCV'; end if;

  -- ZZLIN7(outcome_invalid): daily_ohlcv는 존재하지만 high/low/close 순서가 무효 -> 예외 없이 건너뛰고
  -- publish_attempt는 위에서 이미 정상 커밋된 것으로 확인됨. 관찰 행도 생성되지 않아야 한다.
  if exists (select 1 from public.outcome_observations where outcome_id = outcome_invalid and evaluation_trading_day = date '2099-01-10') then
    raise exception 'observation should not exist for outcome_invalid due to invalid daily_ohlcv ordering';
  end if;

  -- 무효 daily_ohlcv 순서에 대한 직접 RPC 반환값도 확인한다(예외 없이 recorded:false, reason:INVALID_DAILY_OHLCV).
  direct_result := public.record_outcome_observation(outcome_invalid, 'ZZLIN7', date '2099-01-10');
  if (direct_result->>'recorded')::boolean is not false then raise exception 'expected recorded:false for invalid daily_ohlcv ordering'; end if;
  if direct_result->>'reason' <> 'INVALID_DAILY_OHLCV' then raise exception 'expected reason INVALID_DAILY_OHLCV'; end if;
end $$;

-- Story 3.3: emit_open_command 실패(종가 데이터 없음)는 publish_attempt 전체를 rollback한다(AD-20).
do $$
declare
  key text := 'close:2099-01-08'; started jsonb; attempt_id uuid; fence bigint; lease uuid;
  candidate_c uuid := gen_random_uuid();
  caught boolean := false;
begin
  -- 의도적으로 daily_ohlcv에 ZZLIN3의 2099-01-08 종가를 넣지 않는다.
  started := public.start_attempt(key, date '2099-01-08', 'close', 'manual', 300);
  attempt_id := (started->>'run_id')::uuid; fence := (started->>'fence_token')::bigint; lease := (started->>'lease_token')::uuid;
  perform public.write_stage(attempt_id, 'candidates', fence, lease, 'pending', 'running');
  perform public.write_candidates(attempt_id, fence, lease,
    jsonb_build_array(jsonb_build_object('candidate_id', candidate_c, 'ticker', 'ZZLIN3', 'name', 'Lineage Test 3', 'trading_value', 100,
      'sources', jsonb_build_array(jsonb_build_object('source', 't1859', 'weight', 1)))),
    jsonb_build_object('selection_input_hash', repeat('c', 64), 'original_count', 1, 'candidate_count', 1, 'excluded_count', 0, 'truncated_count', 0));
  perform public.write_stage(attempt_id, 'candidates', fence, lease, 'running', 'success');
  perform public.write_stage(attempt_id, 'tags', fence, lease, 'pending', 'running');
  insert into public.candidate_tags(candidate_id, attempt_run_id, strategy, signal_date)
    values (candidate_c, attempt_id, 'C', date '2099-01-08');
  perform public.write_stage(attempt_id, 'tags', fence, lease, 'running', 'success', jsonb_build_object('tagged_count', 1));

  begin
    perform public.publish_attempt(attempt_id, fence, lease);
  exception when others then
    if sqlerrm = 'MISSING_DAILY_OHLCV_CLOSE' then caught := true; else raise; end if;
  end;
  if not caught then raise exception 'publish_attempt did not propagate emit_open_command failure'; end if;

  if (select status from public.runs where run_id = attempt_id) = 'published' then
    raise exception 'candidate/tag publish was not rolled back after outcome generation failure';
  end if;
  if (select canonical_success_run_id from public.logical_runs where logical_run_key = key) is not null then
    raise exception 'canonical_success_run_id was set despite outcome generation failure';
  end if;
  if exists (select 1 from public.outcome_events where logical_run_key = key) then
    raise exception 'outcome_events row leaked despite rollback';
  end if;
  if exists (select 1 from public.candidate_outcome where ticker = 'ZZLIN3' and strategy = 'C') then
    raise exception 'candidate_outcome row leaked despite rollback';
  end if;
end $$;

-- Story 3.3 review patch: 2개 이상의 활성 태그 중 하나는 emit_open_command가 성공할 수 있는 상태(종가 존재)이고
-- 다른 하나는 실패하는 상태(종가 없음)일 때, 먼저 처리되어 성공했을 수도 있는 태그의 outcome 행도
-- 함께 rollback되는지 검증한다 -- 단일 태그 실패만으로는 이 "부분 루프" unwind를 증명하지 못하기 때문이다(AD-20).
do $$
declare
  key text := 'close:2099-01-09'; started jsonb; attempt_id uuid; fence bigint; lease uuid;
  candidate_d uuid := gen_random_uuid();
  candidate_e uuid := gen_random_uuid();
  caught boolean := false;
begin
  -- ZZLIN4는 종가가 존재해 emit_open_command가 성공할 수 있는 태그, ZZLIN5는 의도적으로 종가를 넣지 않아
  -- emit_open_command가 실패하는 태그다. 루프의 실제 순회 순서와 무관하게, 예외 발생 후에는
  -- ZZLIN4 태그가 먼저 처리되어 성공했더라도 그 outcome 행이 남아있으면 안 된다.
  insert into public.daily_ohlcv(ticker, trading_day, open, high, low, close, volume)
    values ('ZZLIN4', date '2099-01-09', 100, 105, 99, 101, 1000)
    on conflict (ticker, trading_day) do nothing;

  started := public.start_attempt(key, date '2099-01-09', 'close', 'manual', 300);
  attempt_id := (started->>'run_id')::uuid; fence := (started->>'fence_token')::bigint; lease := (started->>'lease_token')::uuid;
  perform public.write_stage(attempt_id, 'candidates', fence, lease, 'pending', 'running');
  perform public.write_candidates(attempt_id, fence, lease,
    jsonb_build_array(
      jsonb_build_object('candidate_id', candidate_d, 'ticker', 'ZZLIN4', 'name', 'Lineage Test 4', 'trading_value', 100,
        'sources', jsonb_build_array(jsonb_build_object('source', 't1859', 'weight', 1))),
      jsonb_build_object('candidate_id', candidate_e, 'ticker', 'ZZLIN5', 'name', 'Lineage Test 5', 'trading_value', 100,
        'sources', jsonb_build_array(jsonb_build_object('source', 't1859', 'weight', 1)))),
    jsonb_build_object('selection_input_hash', repeat('e', 64), 'original_count', 2, 'candidate_count', 2, 'excluded_count', 0, 'truncated_count', 0));
  perform public.write_stage(attempt_id, 'candidates', fence, lease, 'running', 'success');
  perform public.write_stage(attempt_id, 'tags', fence, lease, 'pending', 'running');
  insert into public.candidate_tags(candidate_id, attempt_run_id, strategy, signal_date)
    values (candidate_d, attempt_id, 'A', date '2099-01-09'), (candidate_e, attempt_id, 'B', date '2099-01-09');
  perform public.write_stage(attempt_id, 'tags', fence, lease, 'running', 'success', jsonb_build_object('tagged_count', 2));

  begin
    perform public.publish_attempt(attempt_id, fence, lease);
  exception when others then
    if sqlerrm = 'MISSING_DAILY_OHLCV_CLOSE' then caught := true; else raise; end if;
  end;
  if not caught then raise exception 'publish_attempt did not propagate emit_open_command failure for the second active tag'; end if;

  if (select status from public.runs where run_id = attempt_id) = 'published' then
    raise exception 'partial-loop failure did not roll back candidate/tag publish';
  end if;
  if (select canonical_success_run_id from public.logical_runs where logical_run_key = key) is not null then
    raise exception 'canonical_success_run_id was set despite partial-loop outcome generation failure';
  end if;
  if exists (select 1 from public.outcome_events where logical_run_key = key) then
    raise exception 'outcome_events row leaked for any tag despite partial-loop rollback';
  end if;
  if exists (select 1 from public.outcome_events where logical_run_key = key and ticker = 'ZZLIN4') then
    raise exception 'the first (would-have-succeeded) tag''s outcome_events row leaked despite rollback';
  end if;
  if exists (select 1 from public.candidate_outcome where (ticker, strategy) in (('ZZLIN4', 'A'), ('ZZLIN5', 'B'))) then
    raise exception 'candidate_outcome rows leaked for the partial loop despite rollback';
  end if;
end $$;

-- Story 3.5: 가격 조정 이상 감지 & SUSPENDED 전이. pricechk 갭 무관 전이, 갭 안전망(35%), 임계값 이하(12%)
-- 정상 유지, 이미 SUSPENDED인 outcome의 제외, 동일 attempt 재발행 idempotency, 전일 daily_ohlcv 없음
-- (갭 계산 스킵) 케이스를 하나의 close 발행으로 검증한다.
do $$
declare
  key text := 'close:2099-01-11'; started jsonb; attempt_id uuid; fence bigint; lease uuid;
  outcome_pricechk uuid; outcome_gap uuid; outcome_normal uuid; outcome_already_suspended uuid; outcome_no_prev uuid;
  suspended_event_count integer;
  transitions jsonb;
  publish_result jsonb;
begin
  -- ZZLIN8(strategy A): pricechk가 0이 아니고 갭은 10%뿐이지만 그래도 무조건 SUSPENDED로 전이되어야 한다.
  insert into public.daily_ohlcv(ticker, trading_day, open, high, low, close, volume)
    values ('ZZLIN8', date '2099-01-10', 100, 105, 99, 100, 1000)
    on conflict (ticker, trading_day) do nothing;
  insert into public.daily_ohlcv(ticker, trading_day, open, high, low, close, volume, pricechk)
    values ('ZZLIN8', date '2099-01-11', 108, 115, 105, 110, 1000, 1)
    on conflict (ticker, trading_day) do nothing;
  insert into public.outcome_events(ticker, strategy, command_type, logical_run_key, payload)
    values ('ZZLIN8', 'A', 'OPEN', 'close:2099-01-07', jsonb_build_object('entry_date', date '2099-01-07', 'entry_price', 100));
  insert into public.candidate_outcome(ticker, strategy, entry_date, entry_price, status)
    values ('ZZLIN8', 'A', date '2099-01-07', 100, 'OPEN')
    returning outcome_id into outcome_pricechk;

  -- ZZLIN9(strategy B): pricechk는 null이지만 전일 대비 종가 갭이 35%(안전망 임계값 30% 초과)라 SUSPENDED로 전이되어야 한다.
  insert into public.daily_ohlcv(ticker, trading_day, open, high, low, close, volume)
    values ('ZZLIN9', date '2099-01-10', 100, 105, 99, 100, 1000)
    on conflict (ticker, trading_day) do nothing;
  insert into public.daily_ohlcv(ticker, trading_day, open, high, low, close, volume)
    values ('ZZLIN9', date '2099-01-11', 130, 138, 128, 135, 1000)
    on conflict (ticker, trading_day) do nothing;
  insert into public.outcome_events(ticker, strategy, command_type, logical_run_key, payload)
    values ('ZZLIN9', 'B', 'OPEN', 'close:2099-01-07', jsonb_build_object('entry_date', date '2099-01-07', 'entry_price', 100));
  insert into public.candidate_outcome(ticker, strategy, entry_date, entry_price, status)
    values ('ZZLIN9', 'B', date '2099-01-07', 100, 'OPEN')
    returning outcome_id into outcome_gap;

  -- ZZLIN10(strategy C): pricechk는 null이고 갭은 10%(임계값 이하)라 전이 없이 OPEN으로 유지되어야 한다.
  -- entry_price(110)는 Story 3.6의 TP/SL 판정(고가 111/저가 108 모두 ±3% 이내)도 우연히 충족하지
  -- 않도록 오늘 daily_ohlcv 범위 안쪽으로 골랐다 -- 이 시나리오는 SUSPENDED 감지만 검증한다.
  insert into public.daily_ohlcv(ticker, trading_day, open, high, low, close, volume)
    values ('ZZLIN10', date '2099-01-10', 100, 105, 99, 100, 1000)
    on conflict (ticker, trading_day) do nothing;
  insert into public.daily_ohlcv(ticker, trading_day, open, high, low, close, volume)
    values ('ZZLIN10', date '2099-01-11', 109, 111, 108, 110, 1000)
    on conflict (ticker, trading_day) do nothing;
  insert into public.outcome_events(ticker, strategy, command_type, logical_run_key, payload)
    values ('ZZLIN10', 'C', 'OPEN', 'close:2099-01-07', jsonb_build_object('entry_date', date '2099-01-07', 'entry_price', 110));
  insert into public.candidate_outcome(ticker, strategy, entry_date, entry_price, status)
    values ('ZZLIN10', 'C', date '2099-01-07', 110, 'OPEN')
    returning outcome_id into outcome_normal;

  -- ZZLIN11(strategy A): 이미 SUSPENDED 상태 -- 감지 대상에서 제외되어 재전이/중복 이벤트가 없어야 한다.
  insert into public.daily_ohlcv(ticker, trading_day, open, high, low, close, volume, pricechk)
    values ('ZZLIN11', date '2099-01-11', 200, 250, 190, 240, 1000, 1)
    on conflict (ticker, trading_day) do nothing;
  insert into public.outcome_events(ticker, strategy, command_type, logical_run_key, payload)
    values ('ZZLIN11', 'A', 'OPEN', 'close:2099-01-07', jsonb_build_object('entry_date', date '2099-01-07', 'entry_price', 100));
  insert into public.candidate_outcome(ticker, strategy, entry_date, entry_price, status)
    values ('ZZLIN11', 'A', date '2099-01-07', 100, 'SUSPENDED')
    returning outcome_id into outcome_already_suspended;

  -- ZZLIN12(strategy B): 신규 진입 첫날이라 전일 daily_ohlcv가 없다. pricechk는 null이므로 갭 계산을
  -- 시도하지만 전일 행이 없어 계산을 건너뛰고 오탐 없이 OPEN으로 유지되어야 한다.
  insert into public.daily_ohlcv(ticker, trading_day, open, high, low, close, volume)
    values ('ZZLIN12', date '2099-01-11', 50, 55, 48, 52, 1000)
    on conflict (ticker, trading_day) do nothing;
  insert into public.outcome_events(ticker, strategy, command_type, logical_run_key, payload)
    values ('ZZLIN12', 'B', 'OPEN', 'close:2099-01-07', jsonb_build_object('entry_date', date '2099-01-11', 'entry_price', 52));
  insert into public.candidate_outcome(ticker, strategy, entry_date, entry_price, status)
    values ('ZZLIN12', 'B', date '2099-01-11', 52, 'OPEN')
    returning outcome_id into outcome_no_prev;

  started := public.start_attempt(key, date '2099-01-11', 'close', 'manual', 300);
  attempt_id := (started->>'run_id')::uuid; fence := (started->>'fence_token')::bigint; lease := (started->>'lease_token')::uuid;
  perform public.write_stage(attempt_id, 'candidates', fence, lease, 'pending', 'running');
  perform public.write_stage(attempt_id, 'candidates', fence, lease, 'running', 'success');
  perform public.write_stage(attempt_id, 'tags', fence, lease, 'pending', 'running');
  perform public.write_stage(attempt_id, 'tags', fence, lease, 'running', 'success');

  publish_result := public.publish_attempt(attempt_id, fence, lease);

  if (select status from public.runs where run_id = attempt_id) <> 'published' then
    raise exception 'close attempt with SUSPENDED-candidate outcomes did not publish';
  end if;

  -- pricechk 관측(갭 무관): SUSPENDED 전이 + outcome_events 1행.
  if (select status from public.candidate_outcome where outcome_id = outcome_pricechk) <> 'SUSPENDED' then
    raise exception 'expected ZZLIN8/A to transition to SUSPENDED via pricechk';
  end if;
  select count(*) into suspended_event_count from public.outcome_events
    where logical_run_key = key and ticker = 'ZZLIN8' and strategy = 'A' and command_type = 'SUSPENDED';
  if suspended_event_count <> 1 then raise exception 'expected exactly 1 SUSPENDED event for ZZLIN8/A, got %', suspended_event_count; end if;

  -- 갭 안전망(35% > 30%): SUSPENDED 전이.
  if (select status from public.candidate_outcome where outcome_id = outcome_gap) <> 'SUSPENDED' then
    raise exception 'expected ZZLIN9/B to transition to SUSPENDED via gap safety net';
  end if;
  select count(*) into suspended_event_count from public.outcome_events
    where logical_run_key = key and ticker = 'ZZLIN9' and strategy = 'B' and command_type = 'SUSPENDED';
  if suspended_event_count <> 1 then raise exception 'expected exactly 1 SUSPENDED event for ZZLIN9/B, got %', suspended_event_count; end if;

  -- 임계값 이하(12%): 전이 없음, OPEN 유지.
  if (select status from public.candidate_outcome where outcome_id = outcome_normal) <> 'OPEN' then
    raise exception 'expected ZZLIN10/C to remain OPEN under the 30%% gap threshold';
  end if;
  if exists (select 1 from public.outcome_events where logical_run_key = key and ticker = 'ZZLIN10' and command_type = 'SUSPENDED') then
    raise exception 'unexpected SUSPENDED event for ZZLIN10/C under threshold';
  end if;

  -- 이미 SUSPENDED: 감지 대상 제외, 중복 이벤트 없음, 상태 그대로.
  if (select status from public.candidate_outcome where outcome_id = outcome_already_suspended) <> 'SUSPENDED' then
    raise exception 'expected ZZLIN11/A to remain SUSPENDED';
  end if;
  if exists (select 1 from public.outcome_events where logical_run_key = key and ticker = 'ZZLIN11' and command_type = 'SUSPENDED') then
    raise exception 'already-SUSPENDED outcome should not receive a new SUSPENDED event from this attempt';
  end if;

  -- 전일 daily_ohlcv 없음: 갭 계산 스킵, 오탐 없이 OPEN 유지.
  if (select status from public.candidate_outcome where outcome_id = outcome_no_prev) <> 'OPEN' then
    raise exception 'expected ZZLIN12/B to remain OPEN when no prior trading day daily_ohlcv exists';
  end if;

  -- publish_attempt 반환 jsonb의 suspended_transitions에 이번 attempt 신규 전이 2건만 노출되어야 한다.
  transitions := publish_result->'suspended_transitions';
  if jsonb_array_length(transitions) <> 2 then
    raise exception 'expected 2 suspended_transitions entries, got %', jsonb_array_length(transitions);
  end if;
  if not exists (
    select 1 from jsonb_array_elements(transitions) e
      where e->>'ticker' = 'ZZLIN8' and e->>'strategy' = 'A' and (e->>'via_pricechk')::boolean is true
  ) then
    raise exception 'expected suspended_transitions to expose ZZLIN8/A via pricechk';
  end if;
  if not exists (
    select 1 from jsonb_array_elements(transitions) e
      where e->>'ticker' = 'ZZLIN9' and e->>'strategy' = 'B' and (e->>'via_pricechk')::boolean is false
  ) then
    raise exception 'expected suspended_transitions to expose ZZLIN9/B via gap safety net';
  end if;

  -- 재시도(동일 attempt 재발행): 같은 (logical_run_key,ticker,strategy,'SUSPENDED') 이벤트가 이미 있으므로
  -- 직접 재호출해도 새 이벤트를 만들지 않고 publish_attempt 자체는 정상 커밋된 상태를 유지해야 한다.
  insert into public.outcome_events(ticker, strategy, command_type, logical_run_key, payload)
    values ('ZZLIN8', 'A', 'SUSPENDED', key, jsonb_build_object('retry', true))
    on conflict (logical_run_key, ticker, strategy, command_type) do nothing;
  select count(*) into suspended_event_count from public.outcome_events
    where logical_run_key = key and ticker = 'ZZLIN8' and strategy = 'A' and command_type = 'SUSPENDED';
  if suspended_event_count <> 1 then raise exception 'idempotent retry created a duplicate SUSPENDED event, got %', suspended_event_count; end if;
end $$;

-- Story 3.5 review patch(verification-gap/edge-case-hunter): 같은 attempt 안에서 emit_open_command(3.2)가
-- 방금 새로 OPEN시킨 outcome도, 오늘 daily_ohlcv에 pricechk가 관측되면 SUSPENDED 감지 루프가 곧바로
-- 전이시켜야 한다 -- tag_row/emit_open_command 루프와 susp_row 루프가 실제로 결합되는 유일한 실경로이며
-- 지금까지의 3.5 시나리오는 모두 candidate_outcome을 직접 insert해 이 경로를 우회했다.
do $$
declare
  key text := 'close:2099-01-12'; started jsonb; attempt_id uuid; fence bigint; lease uuid;
  candidate_f uuid := gen_random_uuid();
  outcome_same_day uuid;
  open_event_count integer;
  suspended_event_count integer;
begin
  insert into public.daily_ohlcv(ticker, trading_day, open, high, low, close, volume)
    values ('ZZLIN13', date '2099-01-11', 100, 105, 99, 100, 1000)
    on conflict (ticker, trading_day) do nothing;
  insert into public.daily_ohlcv(ticker, trading_day, open, high, low, close, volume, pricechk)
    values ('ZZLIN13', date '2099-01-12', 100, 105, 99, 101, 1000, 1)
    on conflict (ticker, trading_day) do nothing;

  started := public.start_attempt(key, date '2099-01-12', 'close', 'manual', 300);
  attempt_id := (started->>'run_id')::uuid; fence := (started->>'fence_token')::bigint; lease := (started->>'lease_token')::uuid;
  perform public.write_stage(attempt_id, 'candidates', fence, lease, 'pending', 'running');
  perform public.write_candidates(attempt_id, fence, lease,
    jsonb_build_array(jsonb_build_object('candidate_id', candidate_f, 'ticker', 'ZZLIN13', 'name', 'Lineage Test 13', 'trading_value', 100,
      'sources', jsonb_build_array(jsonb_build_object('source', 't1859', 'weight', 1)))),
    jsonb_build_object('selection_input_hash', repeat('f', 64), 'original_count', 1, 'candidate_count', 1, 'excluded_count', 0, 'truncated_count', 0));
  perform public.write_stage(attempt_id, 'candidates', fence, lease, 'running', 'success');
  perform public.write_stage(attempt_id, 'tags', fence, lease, 'pending', 'running');
  insert into public.candidate_tags(candidate_id, attempt_run_id, strategy, signal_date)
    values (candidate_f, attempt_id, 'C', date '2099-01-12');
  perform public.write_stage(attempt_id, 'tags', fence, lease, 'running', 'success', jsonb_build_object('tagged_count', 1));

  perform public.publish_attempt(attempt_id, fence, lease);

  if (select status from public.runs where run_id = attempt_id) <> 'published' then
    raise exception 'close attempt with same-day pricechk on a freshly-opened tag did not publish';
  end if;

  select outcome_id into outcome_same_day from public.candidate_outcome where ticker = 'ZZLIN13' and strategy = 'C';
  if outcome_same_day is null then raise exception 'expected emit_open_command to open ZZLIN13/C'; end if;

  if (select status from public.candidate_outcome where outcome_id = outcome_same_day) <> 'SUSPENDED' then
    raise exception 'expected same-day-opened ZZLIN13/C to be immediately transitioned to SUSPENDED by the pricechk observed on its own entry day';
  end if;

  select count(*) into open_event_count from public.outcome_events
    where logical_run_key = key and ticker = 'ZZLIN13' and strategy = 'C' and command_type = 'OPEN';
  if open_event_count <> 1 then raise exception 'expected 1 OPEN event for ZZLIN13/C, got %', open_event_count; end if;

  select count(*) into suspended_event_count from public.outcome_events
    where logical_run_key = key and ticker = 'ZZLIN13' and strategy = 'C' and command_type = 'SUSPENDED';
  if suspended_event_count <> 1 then raise exception 'expected 1 SUSPENDED event for ZZLIN13/C, got %', suspended_event_count; end if;
end $$;

-- Story 3.6: TP/SL 판정 & 비용 반영 손익률. SUSPENDED 감지 루프 뒤에 재조회한 status='OPEN' and
-- entry_date<오늘인 candidate_outcome만 대상으로, 오늘자 outcome_observations(record_outcome_observation이
-- 이번 attempt에서 방금 기록)의 고가/저가로 TP/SL/동시충족(SL우선)/진입당일/임계값미달/이미SUSPENDED/
-- 관찰없음/terminal재판정제외/재시도idempotency를 하나의 close 발행으로 검증한다.
do $$
declare
  key text := 'close:2099-01-13'; started jsonb; attempt_id uuid; fence bigint; lease uuid;
  outcome_tp uuid; outcome_sl uuid; outcome_both uuid; outcome_entry_day uuid; outcome_below uuid;
  outcome_suspended uuid; outcome_no_obs uuid; outcome_terminal uuid;
  event_count integer;
  publish_result jsonb;
  transitions jsonb;
begin
  -- ZZLIN14/A: TP 확정. entry=100, 오늘 고가 103(>=103), 저가 100(>97).
  insert into public.daily_ohlcv(ticker, trading_day, open, high, low, close, volume)
    values ('ZZLIN14', date '2099-01-12', 100, 102, 98, 100, 1000)
    on conflict (ticker, trading_day) do nothing;
  insert into public.daily_ohlcv(ticker, trading_day, open, high, low, close, volume)
    values ('ZZLIN14', date '2099-01-13', 101, 103, 100, 101, 1000)
    on conflict (ticker, trading_day) do nothing;
  insert into public.outcome_events(ticker, strategy, command_type, logical_run_key, payload)
    values ('ZZLIN14', 'A', 'OPEN', 'close:2099-01-11', jsonb_build_object('entry_date', date '2099-01-11', 'entry_price', 100));
  insert into public.candidate_outcome(ticker, strategy, entry_date, entry_price, status)
    values ('ZZLIN14', 'A', date '2099-01-11', 100, 'OPEN')
    returning outcome_id into outcome_tp;

  -- ZZLIN15/B: SL 확정. entry=100, 오늘 저가 97(<=97).
  insert into public.daily_ohlcv(ticker, trading_day, open, high, low, close, volume)
    values ('ZZLIN15', date '2099-01-12', 100, 102, 98, 100, 1000)
    on conflict (ticker, trading_day) do nothing;
  insert into public.daily_ohlcv(ticker, trading_day, open, high, low, close, volume)
    values ('ZZLIN15', date '2099-01-13', 99, 99, 97, 98, 1000)
    on conflict (ticker, trading_day) do nothing;
  insert into public.outcome_events(ticker, strategy, command_type, logical_run_key, payload)
    values ('ZZLIN15', 'B', 'OPEN', 'close:2099-01-11', jsonb_build_object('entry_date', date '2099-01-11', 'entry_price', 100));
  insert into public.candidate_outcome(ticker, strategy, entry_date, entry_price, status)
    values ('ZZLIN15', 'B', date '2099-01-11', 100, 'OPEN')
    returning outcome_id into outcome_sl;

  -- ZZLIN16/C: 동일일 TP·SL 동시 충족 -- SL이 우선 확정되어야 한다. entry=100, 고가 105(TP충족), 저가 95(SL충족).
  insert into public.daily_ohlcv(ticker, trading_day, open, high, low, close, volume)
    values ('ZZLIN16', date '2099-01-12', 100, 102, 98, 100, 1000)
    on conflict (ticker, trading_day) do nothing;
  insert into public.daily_ohlcv(ticker, trading_day, open, high, low, close, volume)
    values ('ZZLIN16', date '2099-01-13', 100, 105, 95, 100, 1000)
    on conflict (ticker, trading_day) do nothing;
  insert into public.outcome_events(ticker, strategy, command_type, logical_run_key, payload)
    values ('ZZLIN16', 'C', 'OPEN', 'close:2099-01-11', jsonb_build_object('entry_date', date '2099-01-11', 'entry_price', 100));
  insert into public.candidate_outcome(ticker, strategy, entry_date, entry_price, status)
    values ('ZZLIN16', 'C', date '2099-01-11', 100, 'OPEN')
    returning outcome_id into outcome_both;

  -- ZZLIN17/A: 진입 당일(entry_date=오늘) -- 임계값을 충족해도 판정하지 않고 OPEN 유지되어야 한다.
  insert into public.daily_ohlcv(ticker, trading_day, open, high, low, close, volume)
    values ('ZZLIN17', date '2099-01-12', 100, 102, 98, 100, 1000)
    on conflict (ticker, trading_day) do nothing;
  insert into public.daily_ohlcv(ticker, trading_day, open, high, low, close, volume)
    values ('ZZLIN17', date '2099-01-13', 100, 110, 100, 100, 1000)
    on conflict (ticker, trading_day) do nothing;
  insert into public.outcome_events(ticker, strategy, command_type, logical_run_key, payload)
    values ('ZZLIN17', 'A', 'OPEN', 'close:2099-01-11', jsonb_build_object('entry_date', date '2099-01-13', 'entry_price', 100));
  insert into public.candidate_outcome(ticker, strategy, entry_date, entry_price, status)
    values ('ZZLIN17', 'A', date '2099-01-13', 100, 'OPEN')
    returning outcome_id into outcome_entry_day;

  -- ZZLIN18/B: 임계값 미달 -- 고가 102(<103), 저가 98(>97). 판정 없음, OPEN 유지.
  insert into public.daily_ohlcv(ticker, trading_day, open, high, low, close, volume)
    values ('ZZLIN18', date '2099-01-12', 100, 102, 98, 100, 1000)
    on conflict (ticker, trading_day) do nothing;
  insert into public.daily_ohlcv(ticker, trading_day, open, high, low, close, volume)
    values ('ZZLIN18', date '2099-01-13', 100, 102, 98, 100, 1000)
    on conflict (ticker, trading_day) do nothing;
  insert into public.outcome_events(ticker, strategy, command_type, logical_run_key, payload)
    values ('ZZLIN18', 'B', 'OPEN', 'close:2099-01-11', jsonb_build_object('entry_date', date '2099-01-11', 'entry_price', 100));
  insert into public.candidate_outcome(ticker, strategy, entry_date, entry_price, status)
    values ('ZZLIN18', 'B', date '2099-01-11', 100, 'OPEN')
    returning outcome_id into outcome_below;

  -- ZZLIN19/C: 이미 SUSPENDED -- 오늘 고가/저가가 SL/TP 임계값을 모두 충족해도 판정 대상에서 제외되어야 한다.
  insert into public.daily_ohlcv(ticker, trading_day, open, high, low, close, volume)
    values ('ZZLIN19', date '2099-01-13', 100, 130, 70, 100, 1000)
    on conflict (ticker, trading_day) do nothing;
  insert into public.outcome_events(ticker, strategy, command_type, logical_run_key, payload)
    values ('ZZLIN19', 'C', 'OPEN', 'close:2099-01-11', jsonb_build_object('entry_date', date '2099-01-11', 'entry_price', 100));
  insert into public.candidate_outcome(ticker, strategy, entry_date, entry_price, status)
    values ('ZZLIN19', 'C', date '2099-01-11', 100, 'SUSPENDED')
    returning outcome_id into outcome_suspended;

  -- ZZLIN20/A: 오늘 daily_ohlcv가 없어 3.4가 관찰을 기록하지 않음 -- 판정을 건너뛰고 OPEN 유지되어야 한다.
  insert into public.outcome_events(ticker, strategy, command_type, logical_run_key, payload)
    values ('ZZLIN20', 'A', 'OPEN', 'close:2099-01-11', jsonb_build_object('entry_date', date '2099-01-11', 'entry_price', 100));
  insert into public.candidate_outcome(ticker, strategy, entry_date, entry_price, status)
    values ('ZZLIN20', 'A', date '2099-01-11', 100, 'OPEN')
    returning outcome_id into outcome_no_obs;

  -- ZZLIN21/B: 이미 TP로 terminal -- status='OPEN' 쿼리에서 애초에 제외되어 재판정하지 않아야 한다.
  insert into public.outcome_events(ticker, strategy, command_type, logical_run_key, payload)
    values ('ZZLIN21', 'B', 'OPEN', 'close:2099-01-05', jsonb_build_object('entry_date', date '2099-01-05', 'entry_price', 100));
  insert into public.outcome_events(ticker, strategy, command_type, logical_run_key, payload)
    values ('ZZLIN21', 'B', 'TP', 'close:2099-01-05', jsonb_build_object('trading_day', date '2099-01-06', 'exit_price', 103, 'return_pct', 2.9));
  insert into public.candidate_outcome(ticker, strategy, entry_date, entry_price, status, exit_date, exit_price, return_pct)
    values ('ZZLIN21', 'B', date '2099-01-05', 100, 'TP', date '2099-01-06', 103, 2.9)
    returning outcome_id into outcome_terminal;

  started := public.start_attempt(key, date '2099-01-13', 'close', 'manual', 300);
  attempt_id := (started->>'run_id')::uuid; fence := (started->>'fence_token')::bigint; lease := (started->>'lease_token')::uuid;
  perform public.write_stage(attempt_id, 'candidates', fence, lease, 'pending', 'running');
  perform public.write_stage(attempt_id, 'candidates', fence, lease, 'running', 'success');
  perform public.write_stage(attempt_id, 'tags', fence, lease, 'pending', 'running');
  perform public.write_stage(attempt_id, 'tags', fence, lease, 'running', 'success');

  publish_result := public.publish_attempt(attempt_id, fence, lease);

  if (select status from public.runs where run_id = attempt_id) <> 'published' then
    raise exception 'close attempt with TP/SL-candidate outcomes did not publish';
  end if;

  -- TP 확정.
  if (select status from public.candidate_outcome where outcome_id = outcome_tp) <> 'TP' then
    raise exception 'expected ZZLIN14/A to transition to TP';
  end if;
  if (select exit_price from public.candidate_outcome where outcome_id = outcome_tp) <> 103 then
    raise exception 'expected ZZLIN14/A exit_price to be entry*1.03 = 103';
  end if;
  if (select return_pct from public.candidate_outcome where outcome_id = outcome_tp) <> 2.9 then
    raise exception 'expected ZZLIN14/A return_pct to be fixed +2.9';
  end if;
  select count(*) into event_count from public.outcome_events
    where logical_run_key = key and ticker = 'ZZLIN14' and strategy = 'A' and command_type = 'TP';
  if event_count <> 1 then raise exception 'expected exactly 1 TP event for ZZLIN14/A, got %', event_count; end if;

  -- SL 확정.
  if (select status from public.candidate_outcome where outcome_id = outcome_sl) <> 'SL' then
    raise exception 'expected ZZLIN15/B to transition to SL';
  end if;
  if (select exit_price from public.candidate_outcome where outcome_id = outcome_sl) <> 97 then
    raise exception 'expected ZZLIN15/B exit_price to be entry*0.97 = 97';
  end if;
  if (select return_pct from public.candidate_outcome where outcome_id = outcome_sl) <> -3.1 then
    raise exception 'expected ZZLIN15/B return_pct to be fixed -3.1';
  end if;
  select count(*) into event_count from public.outcome_events
    where logical_run_key = key and ticker = 'ZZLIN15' and strategy = 'B' and command_type = 'SL';
  if event_count <> 1 then raise exception 'expected exactly 1 SL event for ZZLIN15/B, got %', event_count; end if;

  -- 동일일 TP·SL 동시 충족: SL 우선.
  if (select status from public.candidate_outcome where outcome_id = outcome_both) <> 'SL' then
    raise exception 'expected ZZLIN16/C to resolve to SL when both TP and SL thresholds are met on the same day';
  end if;
  if exists (select 1 from public.outcome_events where logical_run_key = key and ticker = 'ZZLIN16' and strategy = 'C' and command_type = 'TP') then
    raise exception 'ZZLIN16/C must not also receive a TP event when SL wins the same-day tie';
  end if;

  -- 진입 당일: 판정 없음, OPEN 유지.
  if (select status from public.candidate_outcome where outcome_id = outcome_entry_day) <> 'OPEN' then
    raise exception 'expected ZZLIN17/A to remain OPEN when entry_date equals trading_day';
  end if;

  -- 임계값 미달: 판정 없음, OPEN 유지.
  if (select status from public.candidate_outcome where outcome_id = outcome_below) <> 'OPEN' then
    raise exception 'expected ZZLIN18/B to remain OPEN under both TP and SL thresholds';
  end if;

  -- 이미 SUSPENDED: 판정 대상에서 제외, 상태 그대로.
  if (select status from public.candidate_outcome where outcome_id = outcome_suspended) <> 'SUSPENDED' then
    raise exception 'expected ZZLIN19/C to remain SUSPENDED and not be judged for TP/SL';
  end if;
  if exists (select 1 from public.outcome_events where logical_run_key = key and ticker = 'ZZLIN19' and command_type in ('TP', 'SL')) then
    raise exception 'ZZLIN19/C must not receive a TP/SL event while SUSPENDED';
  end if;

  -- 오늘 관찰 없음: 판정 건너뜀, OPEN 유지.
  if (select status from public.candidate_outcome where outcome_id = outcome_no_obs) <> 'OPEN' then
    raise exception 'expected ZZLIN20/A to remain OPEN when no outcome_observations row exists for today';
  end if;

  -- terminal 재판정 시도: status='OPEN' 쿼리에서 애초에 제외되어 변하지 않는다.
  if (select status from public.candidate_outcome where outcome_id = outcome_terminal) <> 'TP' then
    raise exception 'expected ZZLIN21/B to remain TP (already-terminal outcomes are not re-judged)';
  end if;
  select count(*) into event_count from public.outcome_events
    where logical_run_key = key and ticker = 'ZZLIN21' and strategy = 'B' and command_type in ('TP', 'SL');
  if event_count <> 0 then raise exception 'ZZLIN21/B must not receive any new TP/SL event from this attempt, got %', event_count; end if;

  -- publish_attempt 반환 jsonb의 tp_sl_transitions에 이번 attempt 신규 전이 3건(TP,SL,SL)만 노출되어야 한다.
  transitions := publish_result->'tp_sl_transitions';
  if jsonb_array_length(transitions) <> 3 then
    raise exception 'expected 3 tp_sl_transitions entries, got %', jsonb_array_length(transitions);
  end if;
  if not exists (
    select 1 from jsonb_array_elements(transitions) e
      where e->>'ticker' = 'ZZLIN14' and e->>'strategy' = 'A' and e->>'status' = 'TP'
        and (e->>'exit_price')::numeric = 103 and (e->>'return_pct')::numeric = 2.9
  ) then
    raise exception 'expected tp_sl_transitions to expose ZZLIN14/A as TP with exit_price 103 and return_pct 2.9';
  end if;
  if not exists (
    select 1 from jsonb_array_elements(transitions) e
      where e->>'ticker' = 'ZZLIN15' and e->>'strategy' = 'B' and e->>'status' = 'SL'
        and (e->>'exit_price')::numeric = 97 and (e->>'return_pct')::numeric = -3.1
  ) then
    raise exception 'expected tp_sl_transitions to expose ZZLIN15/B as SL with exit_price 97 and return_pct -3.1';
  end if;
  if not exists (
    select 1 from jsonb_array_elements(transitions) e
      where e->>'ticker' = 'ZZLIN16' and e->>'strategy' = 'C' and e->>'status' = 'SL'
  ) then
    raise exception 'expected tp_sl_transitions to expose ZZLIN16/C as SL (same-day tie)';
  end if;

  -- 재시도(동일 attempt 재발행): 같은 (logical_run_key,ticker,strategy,'TP') 이벤트가 이미 있으므로
  -- 직접 재호출해도 새 이벤트를 만들지 않아야 한다.
  insert into public.outcome_events(ticker, strategy, command_type, logical_run_key, payload)
    values ('ZZLIN14', 'A', 'TP', key, jsonb_build_object('retry', true))
    on conflict (logical_run_key, ticker, strategy, command_type) do nothing;
  select count(*) into event_count from public.outcome_events
    where logical_run_key = key and ticker = 'ZZLIN14' and strategy = 'A' and command_type = 'TP';
  if event_count <> 1 then raise exception 'idempotent retry created a duplicate TP event, got %', event_count; end if;
end $$;

rollback;
