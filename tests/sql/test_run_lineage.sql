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

rollback;
