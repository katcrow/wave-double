-- Supabase SQL fixture for Story 1.3.
-- 실행 전 lineage/candidates migration과 202609012100 hardening migration을 적용한다.
-- psql 또는 CI의 local Supabase DB에서 실행하며, 실패 시 DO 블록이 예외를 낸다.
begin;

create function public.__fixture_seed_market_supply(p_run_id uuid)
returns void language sql as $$
  insert into public.market_supply(
    attempt_run_id, market, trading_day, foreign_net, institution_net, individual_net, program_net
  )
  select p_run_id, m.market, l.trading_day, 1, 2, 3, 4
  from public.runs r
  join public.logical_runs l on l.logical_run_key = r.logical_run_key
  cross join (values ('KOSPI'::text), ('KOSDAQ'::text)) m(market)
  where r.run_id = p_run_id
  on conflict (attempt_run_id, market, trading_day) do nothing;
$$;

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
   -- Story 4.1: publish_attempt는 supply_3day stage success도 게이트로 요구한다.
   perform public.write_stage(attempt_id, 'supply_3day', fence, lease, 'pending', 'running');
   perform public.write_stage(attempt_id, 'supply_3day', fence, lease, 'running', 'success');
   perform public.write_stage(attempt_id, 'market_supply', fence, lease, 'pending', 'running');
   perform public.write_stage(attempt_id, 'market_supply', fence, lease, 'running', 'success');
  perform public.__fixture_seed_market_supply(attempt_id);
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
 declare key text := 'intraday:2099-01-02:14:20'; started jsonb; attempt_id uuid; fence bigint; lease uuid; caught boolean := false;
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
     perform public.__fixture_seed_market_supply(attempt_id);
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

-- 실전 장애 회귀(2026-09-14, 202609141400): candidates 단계 성공으로 status가
-- 'ready_to_publish'로 전이된 뒤에도(tags stage가 아직 진행 중인 정상 구간)
-- heartbeat가 유효한 lease를 계속 연장할 수 있어야 한다. 이전 정의는 status = 'running'만
-- 허용해 이 구간에서 매번 STALE_FENCE_OR_LEASE로 거부됐다.
do $$
 declare key text := 'close:2099-01-06'; started jsonb; attempt_id uuid; fence bigint; lease uuid; extended timestamptz;
begin
  started := public.start_attempt(key, date '2099-01-06', 'close', 'manual', 300);
   attempt_id := (started->>'run_id')::uuid; fence := (started->>'fence_token')::bigint; lease := (started->>'lease_token')::uuid;
   perform public.write_stage(attempt_id, 'candidates', fence, lease, 'pending', 'running');
   perform public.write_stage(attempt_id, 'candidates', fence, lease, 'running', 'success');
   if (select status from public.runs where public.runs.run_id = attempt_id) <> 'ready_to_publish' then
    raise exception 'fixture precondition failed: expected ready_to_publish after candidates success';
  end if;
   perform public.heartbeat_attempt(attempt_id, fence, lease, 300);
   select lease_expires_at into extended from public.runs where public.runs.run_id = attempt_id;
   if extended <= now() + interval '299 seconds' then
    raise exception 'heartbeat during ready_to_publish did not extend the lease';
  end if;
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
  perform public.write_stage(attempt_id, 'supply_3day', fence, lease, 'pending', 'running');
  perform public.write_stage(attempt_id, 'supply_3day', fence, lease, 'running', 'success');
  perform public.write_stage(attempt_id, 'market_supply', fence, lease, 'pending', 'running');
  perform public.write_stage(attempt_id, 'market_supply', fence, lease, 'running', 'success');

  perform public.__fixture_seed_market_supply(attempt_id);
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

-- Story 6.5 review patch: active D/E tags must reach publish_attempt, not only
-- direct emit/judgement fixtures.
do $$
declare
  key text := 'close:2099-02-02'; started jsonb; attempt_id uuid; fence bigint; lease uuid;
  candidate_d uuid := gen_random_uuid(); candidate_e uuid := gen_random_uuid();
begin
  insert into public.daily_ohlcv(ticker, trading_day, open, high, low, close, volume)
  values ('ZZ6TAGD', date '2099-02-02', 100, 101, 99, 100, 1000),
         ('ZZ6TAGE', date '2099-02-02', 200, 201, 199, 200, 1000);
  started := public.start_attempt(key, date '2099-02-02', 'close', 'manual', 300);
  attempt_id := (started->>'run_id')::uuid; fence := (started->>'fence_token')::bigint; lease := (started->>'lease_token')::uuid;
  perform public.write_stage(attempt_id, 'candidates', fence, lease, 'pending', 'running');
  perform public.write_candidates(attempt_id, fence, lease,
    jsonb_build_array(
      jsonb_build_object('candidate_id', candidate_d, 'ticker', 'ZZ6TAGD', 'name', 'D tag integration', 'trading_value', 100,
        'sources', jsonb_build_array(jsonb_build_object('source', 't1859', 'weight', 1))),
      jsonb_build_object('candidate_id', candidate_e, 'ticker', 'ZZ6TAGE', 'name', 'E tag integration', 'trading_value', 100,
        'sources', jsonb_build_array(jsonb_build_object('source', 't1859', 'weight', 1)))),
    jsonb_build_object('selection_input_hash', repeat('d', 64), 'original_count', 2, 'candidate_count', 2, 'excluded_count', 0, 'truncated_count', 0));
  perform public.write_stage(attempt_id, 'candidates', fence, lease, 'running', 'success');
  perform public.write_stage(attempt_id, 'tags', fence, lease, 'pending', 'running');
  insert into public.candidate_tags(candidate_id, attempt_run_id, strategy, signal_date)
  values (candidate_d, attempt_id, 'D', date '2099-02-02'), (candidate_e, attempt_id, 'E', date '2099-02-02');
  perform public.write_stage(attempt_id, 'tags', fence, lease, 'running', 'success');
  perform public.write_stage(attempt_id, 'supply_3day', fence, lease, 'pending', 'running');
  perform public.write_stage(attempt_id, 'supply_3day', fence, lease, 'running', 'success');
  perform public.write_stage(attempt_id, 'market_supply', fence, lease, 'pending', 'running');
  perform public.write_stage(attempt_id, 'market_supply', fence, lease, 'running', 'success');
  perform public.__fixture_seed_market_supply(attempt_id);
  perform public.publish_attempt(attempt_id, fence, lease);

  if not exists (
    select 1 from public.candidate_outcome
    where ticker = 'ZZ6TAGD' and strategy = 'D' and tp_pct = 3 and sl_pct = 5 and cutoff_n = 20 and status = 'OPEN'
  ) then raise exception 'active D tag did not create strategy snapshot'; end if;
  if not exists (
    select 1 from public.candidate_outcome
    where ticker = 'ZZ6TAGE' and strategy = 'E' and tp_pct = 2 and sl_pct = 5 and cutoff_n = 30 and status = 'OPEN'
  ) then raise exception 'active E tag did not create strategy snapshot'; end if;
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
  perform public.write_stage(attempt_id, 'supply_3day', fence, lease, 'pending', 'running');
  perform public.write_stage(attempt_id, 'supply_3day', fence, lease, 'running', 'success');
  perform public.write_stage(attempt_id, 'market_supply', fence, lease, 'pending', 'running');
  perform public.write_stage(attempt_id, 'market_supply', fence, lease, 'running', 'success');

  perform public.__fixture_seed_market_supply(attempt_id);
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
  perform public.write_stage(attempt_id, 'supply_3day', fence, lease, 'pending', 'running');
  perform public.write_stage(attempt_id, 'supply_3day', fence, lease, 'running', 'success');
  perform public.write_stage(attempt_id, 'market_supply', fence, lease, 'pending', 'running');
  perform public.write_stage(attempt_id, 'market_supply', fence, lease, 'running', 'success');

  begin
    perform public.__fixture_seed_market_supply(attempt_id);
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
  perform public.write_stage(attempt_id, 'supply_3day', fence, lease, 'pending', 'running');
  perform public.write_stage(attempt_id, 'supply_3day', fence, lease, 'running', 'success');
  perform public.write_stage(attempt_id, 'market_supply', fence, lease, 'pending', 'running');
  perform public.write_stage(attempt_id, 'market_supply', fence, lease, 'running', 'success');

  begin
    perform public.__fixture_seed_market_supply(attempt_id);
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
  perform public.write_stage(attempt_id, 'supply_3day', fence, lease, 'pending', 'running');
  perform public.write_stage(attempt_id, 'supply_3day', fence, lease, 'running', 'success');
  perform public.write_stage(attempt_id, 'market_supply', fence, lease, 'pending', 'running');
  perform public.write_stage(attempt_id, 'market_supply', fence, lease, 'running', 'success');

  perform public.__fixture_seed_market_supply(attempt_id);
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
  perform public.write_stage(attempt_id, 'supply_3day', fence, lease, 'pending', 'running');
  perform public.write_stage(attempt_id, 'supply_3day', fence, lease, 'running', 'success');
  perform public.write_stage(attempt_id, 'market_supply', fence, lease, 'pending', 'running');
  perform public.write_stage(attempt_id, 'market_supply', fence, lease, 'running', 'success');

  perform public.__fixture_seed_market_supply(attempt_id);
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
  perform public.write_stage(attempt_id, 'supply_3day', fence, lease, 'pending', 'running');
  perform public.write_stage(attempt_id, 'supply_3day', fence, lease, 'running', 'success');
  perform public.write_stage(attempt_id, 'market_supply', fence, lease, 'pending', 'running');
  perform public.write_stage(attempt_id, 'market_supply', fence, lease, 'running', 'success');

  perform public.__fixture_seed_market_supply(attempt_id);
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

-- Story 3.7: TIMEOUT 컷오프 확정 & 추적 대상 유계화. 3.6의 TP/SL 판정 루프가 그대로 확장되어
-- traded_days_since_entry(outcome_observations count, evaluation_trading_day>entry_date and
-- result_code='OK')가 각 행의 cutoff_n 이상이면 오늘 종가 기준 실손익으로 TIMEOUT을 확정하는지,
-- 컷오프 미도달/TP·TIMEOUT 동시충족/SL·TIMEOUT 동시충족/거래정지 기간 제외/커스텀 cutoff_n/
-- 재시도 idempotency/TP 확정 시 holding_days 기록을 하나의 close 발행으로 검증한다.
do $$
declare
  key text := 'close:2099-01-14'; started jsonb; attempt_id uuid; fence bigint; lease uuid;
  outcome_cutoff_hit uuid; outcome_cutoff_not_reached uuid; outcome_tp_over_timeout uuid;
  outcome_sl_over_timeout uuid; outcome_suspension_gap uuid; outcome_custom_cutoff uuid;
  outcome_tp_holding uuid;
  event_count integer;
begin
  -- ZZLIN22/A: 컷오프 정확히 도달(29 기존 관측 + 오늘 = 30 = cutoff_n 기본값). TP/SL 미충족.
  insert into public.outcome_events(ticker, strategy, command_type, logical_run_key, payload)
    values ('ZZLIN22', 'A', 'OPEN', 'close:2099-01-11', jsonb_build_object('entry_date', date '2098-11-01', 'entry_price', 100));
  insert into public.candidate_outcome(ticker, strategy, entry_date, entry_price, status)
    values ('ZZLIN22', 'A', date '2098-11-01', 100, 'OPEN')
    returning outcome_id into outcome_cutoff_hit;
  insert into public.outcome_observations(outcome_id, evaluation_trading_day, high, low, close, result_code)
    select outcome_cutoff_hit, d::date, 101, 99, 100, 'OK'
    from generate_series(date '2098-11-02', date '2098-11-30', interval '1 day') as d;
  insert into public.daily_ohlcv(ticker, trading_day, open, high, low, close, volume)
    values ('ZZLIN22', date '2099-01-14', 100, 101, 98, 98.5, 1000)
    on conflict (ticker, trading_day) do nothing;

  -- ZZLIN23/A: 컷오프 미도달(28 기존 관측 + 오늘 = 29 < 30). TP/SL 미충족. OPEN 유지 기대.
  insert into public.outcome_events(ticker, strategy, command_type, logical_run_key, payload)
    values ('ZZLIN23', 'A', 'OPEN', 'close:2099-01-11', jsonb_build_object('entry_date', date '2098-11-01', 'entry_price', 100));
  insert into public.candidate_outcome(ticker, strategy, entry_date, entry_price, status)
    values ('ZZLIN23', 'A', date '2098-11-01', 100, 'OPEN')
    returning outcome_id into outcome_cutoff_not_reached;
  insert into public.outcome_observations(outcome_id, evaluation_trading_day, high, low, close, result_code)
    select outcome_cutoff_not_reached, d::date, 101, 99, 100, 'OK'
    from generate_series(date '2098-11-02', date '2098-11-29', interval '1 day') as d;
  insert into public.daily_ohlcv(ticker, trading_day, open, high, low, close, volume)
    values ('ZZLIN23', date '2099-01-14', 100, 101, 99, 100, 1000)
    on conflict (ticker, trading_day) do nothing;

  -- ZZLIN24/A: traded_days_since_entry>=30이고 오늘 고가 104(TP 충족)면 TP가 우선 확정(TIMEOUT 아님).
  insert into public.outcome_events(ticker, strategy, command_type, logical_run_key, payload)
    values ('ZZLIN24', 'A', 'OPEN', 'close:2099-01-11', jsonb_build_object('entry_date', date '2098-11-01', 'entry_price', 100));
  insert into public.candidate_outcome(ticker, strategy, entry_date, entry_price, status)
    values ('ZZLIN24', 'A', date '2098-11-01', 100, 'OPEN')
    returning outcome_id into outcome_tp_over_timeout;
  insert into public.outcome_observations(outcome_id, evaluation_trading_day, high, low, close, result_code)
    select outcome_tp_over_timeout, d::date, 101, 99, 100, 'OK'
    from generate_series(date '2098-11-02', date '2098-11-30', interval '1 day') as d;
  insert into public.daily_ohlcv(ticker, trading_day, open, high, low, close, volume)
    values ('ZZLIN24', date '2099-01-14', 100, 104, 99, 103.5, 1000)
    on conflict (ticker, trading_day) do nothing;

  -- ZZLIN25/A: traded_days_since_entry>=30이고 오늘 저가 96.5(SL 충족)면 SL이 우선 확정(TIMEOUT 아님).
  insert into public.outcome_events(ticker, strategy, command_type, logical_run_key, payload)
    values ('ZZLIN25', 'A', 'OPEN', 'close:2099-01-11', jsonb_build_object('entry_date', date '2098-11-01', 'entry_price', 100));
  insert into public.candidate_outcome(ticker, strategy, entry_date, entry_price, status)
    values ('ZZLIN25', 'A', date '2098-11-01', 100, 'OPEN')
    returning outcome_id into outcome_sl_over_timeout;
  insert into public.outcome_observations(outcome_id, evaluation_trading_day, high, low, close, result_code)
    select outcome_sl_over_timeout, d::date, 101, 99, 100, 'OK'
    from generate_series(date '2098-11-02', date '2098-11-30', interval '1 day') as d;
  insert into public.daily_ohlcv(ticker, trading_day, open, high, low, close, volume)
    values ('ZZLIN25', date '2099-01-14', 100, 100.5, 96.5, 97, 1000)
    on conflict (ticker, trading_day) do nothing;

  -- ZZLIN26/A: 진입 후 5거래일 관측 + 10일 거래정지(daily_ohlcv/관측 행 없음, 행 자체가 없어 카운트에서
  -- 자동 제외) + 24거래일 추가 관측 = 29 + 오늘 = 30 = cutoff_n. 그 시점에 TIMEOUT 확정.
  insert into public.outcome_events(ticker, strategy, command_type, logical_run_key, payload)
    values ('ZZLIN26', 'A', 'OPEN', 'close:2099-01-11', jsonb_build_object('entry_date', date '2098-10-01', 'entry_price', 100));
  insert into public.candidate_outcome(ticker, strategy, entry_date, entry_price, status)
    values ('ZZLIN26', 'A', date '2098-10-01', 100, 'OPEN')
    returning outcome_id into outcome_suspension_gap;
  insert into public.outcome_observations(outcome_id, evaluation_trading_day, high, low, close, result_code)
    select outcome_suspension_gap, d::date, 101, 99, 100, 'OK'
    from generate_series(date '2098-10-02', date '2098-10-06', interval '1 day') as d; -- 5 거래일
  -- 2098-10-07 ~ 2098-10-16(10일)은 거래정지로 유효 관측 행이 없다 -- 의도적으로 아무 행도 넣지 않는다.
  insert into public.outcome_observations(outcome_id, evaluation_trading_day, high, low, close, result_code)
    select outcome_suspension_gap, d::date, 101, 99, 100, 'OK'
    from generate_series(date '2098-10-17', date '2098-11-09', interval '1 day') as d; -- 24 거래일
  insert into public.daily_ohlcv(ticker, trading_day, open, high, low, close, volume)
    values ('ZZLIN26', date '2099-01-14', 100, 101, 99, 99.2, 1000)
    on conflict (ticker, trading_day) do nothing;

  -- ZZLIN27/A: cutoff_n=5(전역 기본값 30이 아닌 이 행에 저장된 값)으로 4개 기존 관측 + 오늘 = 5에서 TIMEOUT.
  insert into public.outcome_events(ticker, strategy, command_type, logical_run_key, payload)
    values ('ZZLIN27', 'A', 'OPEN', 'close:2099-01-05', jsonb_build_object('entry_date', date '2099-01-05', 'entry_price', 100));
  insert into public.candidate_outcome(ticker, strategy, entry_date, entry_price, status, cutoff_n)
    values ('ZZLIN27', 'A', date '2099-01-05', 100, 'OPEN', 5)
    returning outcome_id into outcome_custom_cutoff;
  insert into public.outcome_observations(outcome_id, evaluation_trading_day, high, low, close, result_code)
    select outcome_custom_cutoff, d::date, 101, 99, 100, 'OK'
    from generate_series(date '2099-01-06', date '2099-01-09', interval '1 day') as d; -- 4 거래일
  insert into public.daily_ohlcv(ticker, trading_day, open, high, low, close, volume)
    values ('ZZLIN27', date '2099-01-14', 100, 99, 97.5, 98, 1000)
    on conflict (ticker, trading_day) do nothing;

  -- ZZLIN28/A: 관측 10일차(9 기존 + 오늘)에 TP 조건 충족 -- status=TP와 함께 holding_days=10 기록.
  insert into public.outcome_events(ticker, strategy, command_type, logical_run_key, payload)
    values ('ZZLIN28', 'A', 'OPEN', 'close:2099-01-11', jsonb_build_object('entry_date', date '2098-12-20', 'entry_price', 100));
  insert into public.candidate_outcome(ticker, strategy, entry_date, entry_price, status)
    values ('ZZLIN28', 'A', date '2098-12-20', 100, 'OPEN')
    returning outcome_id into outcome_tp_holding;
  insert into public.outcome_observations(outcome_id, evaluation_trading_day, high, low, close, result_code)
    select outcome_tp_holding, d::date, 101, 99, 100, 'OK'
    from generate_series(date '2098-12-21', date '2098-12-29', interval '1 day') as d; -- 9 거래일
  insert into public.daily_ohlcv(ticker, trading_day, open, high, low, close, volume)
    values ('ZZLIN28', date '2099-01-14', 100, 104, 99, 103.5, 1000)
    on conflict (ticker, trading_day) do nothing;

  started := public.start_attempt(key, date '2099-01-14', 'close', 'manual', 300);
  attempt_id := (started->>'run_id')::uuid; fence := (started->>'fence_token')::bigint; lease := (started->>'lease_token')::uuid;
  perform public.write_stage(attempt_id, 'candidates', fence, lease, 'pending', 'running');
  perform public.write_stage(attempt_id, 'candidates', fence, lease, 'running', 'success');
  perform public.write_stage(attempt_id, 'tags', fence, lease, 'pending', 'running');
  perform public.write_stage(attempt_id, 'tags', fence, lease, 'running', 'success');
  perform public.write_stage(attempt_id, 'supply_3day', fence, lease, 'pending', 'running');
  perform public.write_stage(attempt_id, 'supply_3day', fence, lease, 'running', 'success');
  perform public.write_stage(attempt_id, 'market_supply', fence, lease, 'pending', 'running');
  perform public.write_stage(attempt_id, 'market_supply', fence, lease, 'running', 'success');

  perform public.__fixture_seed_market_supply(attempt_id);
  perform public.__fixture_seed_market_supply(attempt_id);
  perform public.publish_attempt(attempt_id, fence, lease);

  if (select status from public.runs where run_id = attempt_id) <> 'published' then
    raise exception 'close attempt with TIMEOUT-candidate outcomes did not publish';
  end if;

  -- 컷오프 정확히 도달: TIMEOUT 확정, exit_price=오늘 종가, return_pct=실측 비용반영, holding_days=30.
  if (select status from public.candidate_outcome where outcome_id = outcome_cutoff_hit) <> 'TIMEOUT' then
    raise exception 'expected ZZLIN22/A to transition to TIMEOUT at cutoff_n';
  end if;
  if (select exit_price from public.candidate_outcome where outcome_id = outcome_cutoff_hit) <> 98.5 then
    raise exception 'expected ZZLIN22/A exit_price to be today close 98.5';
  end if;
  if (select return_pct from public.candidate_outcome where outcome_id = outcome_cutoff_hit) <> -1.6 then
    raise exception 'expected ZZLIN22/A return_pct to be (98.5/100-1)*100-0.1 = -1.6, got %', (select return_pct from public.candidate_outcome where outcome_id = outcome_cutoff_hit);
  end if;
  if (select holding_days from public.candidate_outcome where outcome_id = outcome_cutoff_hit) <> 30 then
    raise exception 'expected ZZLIN22/A holding_days to be 30';
  end if;
  select count(*) into event_count from public.outcome_events
    where logical_run_key = key and ticker = 'ZZLIN22' and strategy = 'A' and command_type = 'TIMEOUT';
  if event_count <> 1 then raise exception 'expected exactly 1 TIMEOUT event for ZZLIN22/A, got %', event_count; end if;

  -- 컷오프 미도달: 판정 없음, OPEN 유지.
  if (select status from public.candidate_outcome where outcome_id = outcome_cutoff_not_reached) <> 'OPEN' then
    raise exception 'expected ZZLIN23/A to remain OPEN with traded_days_since_entry=29 < cutoff_n=30';
  end if;
  if (select holding_days from public.candidate_outcome where outcome_id = outcome_cutoff_not_reached) <> 0 then
    raise exception 'expected ZZLIN23/A holding_days to remain untouched (0) while still OPEN';
  end if;

  -- TP·TIMEOUT 동시 충족: TP가 우선 확정.
  if (select status from public.candidate_outcome where outcome_id = outcome_tp_over_timeout) <> 'TP' then
    raise exception 'expected ZZLIN24/A to resolve to TP even though cutoff_n is also reached';
  end if;
  if (select return_pct from public.candidate_outcome where outcome_id = outcome_tp_over_timeout) <> 2.9 then
    raise exception 'expected ZZLIN24/A return_pct to remain the fixed TP value 2.9, not a TIMEOUT actual';
  end if;
  if (select holding_days from public.candidate_outcome where outcome_id = outcome_tp_over_timeout) <> 30 then
    raise exception 'expected ZZLIN24/A holding_days to be recorded as 30 on TP transition too';
  end if;
  if exists (select 1 from public.outcome_events where logical_run_key = key and ticker = 'ZZLIN24' and strategy = 'A' and command_type = 'TIMEOUT') then
    raise exception 'ZZLIN24/A must not also receive a TIMEOUT event when TP wins the same-day tie';
  end if;

  -- SL·TIMEOUT 동시 충족: SL이 우선 확정.
  if (select status from public.candidate_outcome where outcome_id = outcome_sl_over_timeout) <> 'SL' then
    raise exception 'expected ZZLIN25/A to resolve to SL even though cutoff_n is also reached';
  end if;
  if (select holding_days from public.candidate_outcome where outcome_id = outcome_sl_over_timeout) <> 30 then
    raise exception 'expected ZZLIN25/A holding_days to be recorded as 30 on SL transition too';
  end if;
  if exists (select 1 from public.outcome_events where logical_run_key = key and ticker = 'ZZLIN25' and strategy = 'A' and command_type = 'TIMEOUT') then
    raise exception 'ZZLIN25/A must not also receive a TIMEOUT event when SL wins the same-day tie';
  end if;

  -- 거래정지 기간 존재: 그 기간은 traded_days_since_entry에서 제외되고, 5+24+오늘=30에서 TIMEOUT 확정.
  if (select status from public.candidate_outcome where outcome_id = outcome_suspension_gap) <> 'TIMEOUT' then
    raise exception 'expected ZZLIN26/A to transition to TIMEOUT once the 10-day suspension gap is excluded from the count';
  end if;
  if (select holding_days from public.candidate_outcome where outcome_id = outcome_suspension_gap) <> 30 then
    raise exception 'expected ZZLIN26/A holding_days to be 30 (suspension gap excluded)';
  end if;

  -- 커스텀 cutoff_n: 전역 기본값(30)이 아니라 이 행에 저장된 cutoff_n=5가 그대로 판정에 쓰인다.
  if (select status from public.candidate_outcome where outcome_id = outcome_custom_cutoff) <> 'TIMEOUT' then
    raise exception 'expected ZZLIN27/A to transition to TIMEOUT at its own stored cutoff_n=5, not the global default 30';
  end if;
  if (select holding_days from public.candidate_outcome where outcome_id = outcome_custom_cutoff) <> 5 then
    raise exception 'expected ZZLIN27/A holding_days to be 5';
  end if;
  if (select return_pct from public.candidate_outcome where outcome_id = outcome_custom_cutoff) <> -2.1 then
    raise exception 'expected ZZLIN27/A return_pct to be (98/100-1)*100-0.1 = -2.1, got %', (select return_pct from public.candidate_outcome where outcome_id = outcome_custom_cutoff);
  end if;

  -- TP 확정 시 holding_days: 관측 10일차(9 기존 + 오늘)에 TP 조건 충족.
  if (select status from public.candidate_outcome where outcome_id = outcome_tp_holding) <> 'TP' then
    raise exception 'expected ZZLIN28/A to transition to TP on its 10th traded day';
  end if;
  if (select holding_days from public.candidate_outcome where outcome_id = outcome_tp_holding) <> 10 then
    raise exception 'expected ZZLIN28/A holding_days to be 10, got %', (select holding_days from public.candidate_outcome where outcome_id = outcome_tp_holding);
  end if;

  -- 재시도(동일 attempt 재발행): 이미 (logical_run_key,ticker,strategy,'TIMEOUT') 이벤트가 있으므로
  -- 직접 재호출해도 새 이벤트/전이 없이 재확인만 되어야 한다.
  insert into public.outcome_events(ticker, strategy, command_type, logical_run_key, payload)
    values ('ZZLIN22', 'A', 'TIMEOUT', key, jsonb_build_object('retry', true))
    on conflict (logical_run_key, ticker, strategy, command_type) do nothing;
  select count(*) into event_count from public.outcome_events
    where logical_run_key = key and ticker = 'ZZLIN22' and strategy = 'A' and command_type = 'TIMEOUT';
  if event_count <> 1 then raise exception 'idempotent retry created a duplicate TIMEOUT event, got %', event_count; end if;

  -- 이미 TIMEOUT으로 확정된 outcome은 후속 배치의 추적 대상 산출에서 기존 status not in (''TP'',''SL'',''TIMEOUT'') 필터로 자동 제외된다.
  if exists (
    select 1 from public.candidate_outcome
    where outcome_id = outcome_cutoff_hit and status not in ('TP', 'SL', 'TIMEOUT')
  ) then
    raise exception 'expected ZZLIN22/A to be excluded from the open-tracking filter after TIMEOUT';
  end if;
end $$;

-- Story 3.7 review patch: traded_days_since_entry는 evaluation_trading_day가 오늘(logical_row.
-- trading_day)보다 나중인 outcome_observations 행을 카운트에서 제외해야 한다(edge-case-hunter
-- 리뷰 발견). ZZLIN29/A: cutoff_n=7. 5개 과거 관측 + 미래로 잘못 선기록된 관측 1개(카운트되면 안 됨)
-- + 오늘 = 패치 전이면 7(버그로 TIMEOUT), 패치 후면 6(<7, OPEN 유지)이어야 한다.
do $$
declare
  key text := 'close:2099-01-15'; started jsonb; attempt_id uuid; fence bigint; lease uuid;
  outcome_future_row uuid;
begin
  insert into public.outcome_events(ticker, strategy, command_type, logical_run_key, payload)
    values ('ZZLIN29', 'A', 'OPEN', 'close:2099-01-11', jsonb_build_object('entry_date', date '2099-01-05', 'entry_price', 100));
  insert into public.candidate_outcome(ticker, strategy, entry_date, entry_price, status, cutoff_n)
    values ('ZZLIN29', 'A', date '2099-01-05', 100, 'OPEN', 7)
    returning outcome_id into outcome_future_row;
  insert into public.outcome_observations(outcome_id, evaluation_trading_day, high, low, close, result_code)
    select outcome_future_row, d::date, 101, 99, 100, 'OK'
    from generate_series(date '2099-01-06', date '2099-01-10', interval '1 day') as d; -- 5 거래일
  -- 잘못 선기록된 미래(오늘 2099-01-15보다 나중) 관측 -- 카운트에서 제외되어야 한다.
  insert into public.outcome_observations(outcome_id, evaluation_trading_day, high, low, close, result_code)
    values (outcome_future_row, date '2099-01-16', 101, 99, 100, 'OK');
  insert into public.daily_ohlcv(ticker, trading_day, open, high, low, close, volume)
    values ('ZZLIN29', date '2099-01-15', 100, 101, 99, 100, 1000)
    on conflict (ticker, trading_day) do nothing;

  started := public.start_attempt(key, date '2099-01-15', 'close', 'manual', 300);
  attempt_id := (started->>'run_id')::uuid; fence := (started->>'fence_token')::bigint; lease := (started->>'lease_token')::uuid;
  perform public.write_stage(attempt_id, 'candidates', fence, lease, 'pending', 'running');
  perform public.write_stage(attempt_id, 'candidates', fence, lease, 'running', 'success');
  perform public.write_stage(attempt_id, 'tags', fence, lease, 'pending', 'running');
  perform public.write_stage(attempt_id, 'tags', fence, lease, 'running', 'success');
  perform public.write_stage(attempt_id, 'supply_3day', fence, lease, 'pending', 'running');
  perform public.write_stage(attempt_id, 'supply_3day', fence, lease, 'running', 'success');
  perform public.write_stage(attempt_id, 'market_supply', fence, lease, 'pending', 'running');
  perform public.write_stage(attempt_id, 'market_supply', fence, lease, 'running', 'success');

  perform public.__fixture_seed_market_supply(attempt_id);
  perform public.__fixture_seed_market_supply(attempt_id);
  perform public.publish_attempt(attempt_id, fence, lease);

  if (select status from public.candidate_outcome where outcome_id = outcome_future_row) <> 'OPEN' then
    raise exception 'expected ZZLIN29/A to remain OPEN (traded_days_since_entry=6 < cutoff_n=7 once the future-dated row is excluded), got %',
      (select status from public.candidate_outcome where outcome_id = outcome_future_row);
  end if;
end $$;

-- Story 3.8: outcome correction 이벤트 메커니즘. raw UPDATE 차단, SUSPENDED->OPEN 정상 복귀
-- (exit 3필드 null 복귀, entry 보존, version+1), stale expected_version 거부, terminal 수치
-- 정정, 존재하지 않는 outcome_id, 잘못된 신규 상태값, outcome_events append-only 회귀를
-- close:2099-01-16을 감사 앵커로 검증한다.
do $$
declare
  key text := 'close:2099-01-16';
  outcome_raw_update uuid;
  outcome_suspended_return uuid;
  outcome_terminal uuid;
  v_version integer;
  caught boolean := false;
  correction_result jsonb;
  v_event_count integer;
begin
  insert into public.logical_runs(logical_run_key, trading_day, batch_kind)
    values (key, date '2099-01-16', 'close')
    on conflict (logical_run_key) do nothing;

  -- Scenario: raw UPDATE 차단 -- 가드 플래그 없이 직접 UPDATE를 시도하면 55000 예외로 거부되고
  -- 상태/version 모두 변경되지 않아야 한다.
  insert into public.outcome_events(ticker, strategy, command_type, logical_run_key, payload)
    values ('ZZCORR1', 'A', 'OPEN', key, jsonb_build_object('entry_date', date '2099-01-16', 'entry_price', 100));
  insert into public.candidate_outcome(ticker, strategy, entry_date, entry_price, status)
    values ('ZZCORR1', 'A', date '2099-01-16', 100, 'OPEN')
    returning outcome_id into outcome_raw_update;

  caught := false;
  begin
    update public.candidate_outcome set status = 'TIMEOUT' where outcome_id = outcome_raw_update;
  exception when others then
    if sqlstate = '55000' then caught := true; else raise; end if;
  end;
  if not caught then raise exception 'raw UPDATE on candidate_outcome was not rejected'; end if;
  if (select status from public.candidate_outcome where outcome_id = outcome_raw_update) <> 'OPEN' then
    raise exception 'raw UPDATE attempt mutated candidate_outcome despite rejection';
  end if;
  if (select version from public.candidate_outcome where outcome_id = outcome_raw_update) <> 1 then
    raise exception 'rejected raw UPDATE must not increment version';
  end if;

  -- Scenario: SUSPENDED -> OPEN 정상 복귀. exit_date/exit_price/return_pct는 null로 복귀,
  -- entry_date/entry_price는 보존, version은 정확히 1 증가해야 한다.
  insert into public.outcome_events(ticker, strategy, command_type, logical_run_key, payload)
    values ('ZZCORR2', 'B', 'OPEN', key, jsonb_build_object('entry_date', date '2099-01-10', 'entry_price', 200));
  insert into public.candidate_outcome(ticker, strategy, entry_date, entry_price, status, exit_date, exit_price, return_pct)
    values ('ZZCORR2', 'B', date '2099-01-10', 200, 'SUSPENDED', date '2099-01-15', 190, -5.0)
    returning outcome_id into outcome_suspended_return;

  select version into v_version from public.candidate_outcome where outcome_id = outcome_suspended_return;
  correction_result := public.apply_outcome_correction(key, outcome_suspended_return, v_version, 'price adjustment cleared, resume tracking', 'OPEN');

  if (correction_result->>'status') <> 'OPEN' then raise exception 'expected OPEN after SUSPENDED return correction, got %', correction_result; end if;
  if (select status from public.candidate_outcome where outcome_id = outcome_suspended_return) <> 'OPEN' then
    raise exception 'projection status was not updated to OPEN';
  end if;
  if exists (
    select 1 from public.candidate_outcome
    where outcome_id = outcome_suspended_return
      and (exit_date is not null or exit_price is not null or return_pct is not null)
  ) then
    raise exception 'expected exit_date/exit_price/return_pct to be reset to null on SUSPENDED->OPEN correction';
  end if;
  if (select entry_price from public.candidate_outcome where outcome_id = outcome_suspended_return) <> 200 then
    raise exception 'entry_price must be preserved on SUSPENDED->OPEN correction';
  end if;
  if (select version from public.candidate_outcome where outcome_id = outcome_suspended_return) <> v_version + 1 then
    raise exception 'expected version to increment by exactly 1 on correction';
  end if;
  if not exists (
    select 1 from public.outcome_events
    where logical_run_key = key and ticker = 'ZZCORR2' and strategy = 'B' and command_type = 'CORRECTION'
      and payload->>'reason' = 'price adjustment cleared, resume tracking'
  ) then
    raise exception 'expected CORRECTION event with reason to be recorded';
  end if;

  -- Scenario: stale expected_version -- 위 correction으로 이미 버전이 증가했으므로 옛 버전으로
  -- 재호출하면 이벤트/projection 모두 변경 없이 거부되어야 한다.
  caught := false;
  begin
    perform public.apply_outcome_correction(key, outcome_suspended_return, v_version, 'stale retry', 'OPEN');
  exception when others then
    if sqlerrm = 'CORRECTION_VERSION_MISMATCH' then caught := true; else raise; end if;
  end;
  if not caught then raise exception 'stale expected_version was accepted'; end if;
  select count(*) into v_event_count from public.outcome_events
    where logical_run_key = key and ticker = 'ZZCORR2' and strategy = 'B' and command_type = 'CORRECTION';
  if v_event_count <> 1 then raise exception 'stale expected_version must not append a new CORRECTION event, got %', v_event_count; end if;

  -- Scenario: terminal 수치 정정 -- TP로 이미 종결된 행의 return_pct만 보정하고 status/다른
  -- 값은 그대로 유지되어야 한다(epics AC1의 "수치 수정" 요구).
  insert into public.outcome_events(ticker, strategy, command_type, logical_run_key, payload)
    values ('ZZCORR3', 'C', 'OPEN', key, jsonb_build_object('entry_date', date '2099-01-10', 'entry_price', 100));
  insert into public.candidate_outcome(ticker, strategy, entry_date, entry_price, status, exit_date, exit_price, return_pct, holding_days)
    values ('ZZCORR3', 'C', date '2099-01-10', 100, 'TP', date '2099-01-11', 103, 2.9, 1)
    returning outcome_id into outcome_terminal;

  select version into v_version from public.candidate_outcome where outcome_id = outcome_terminal;
  correction_result := public.apply_outcome_correction(key, outcome_terminal, v_version, 'exit price data correction', 'TP', null, null, null, 2.85);

  if (select status from public.candidate_outcome where outcome_id = outcome_terminal) <> 'TP' then
    raise exception 'terminal numeric correction must keep status TP';
  end if;
  if (select return_pct from public.candidate_outcome where outcome_id = outcome_terminal) <> 2.85 then
    raise exception 'expected return_pct to be corrected to 2.85, got %', (select return_pct from public.candidate_outcome where outcome_id = outcome_terminal);
  end if;
  if (select exit_price from public.candidate_outcome where outcome_id = outcome_terminal) <> 103 then
    raise exception 'unspecified exit_price must be preserved on terminal numeric correction';
  end if;
  if (select entry_price from public.candidate_outcome where outcome_id = outcome_terminal) <> 100 then
    raise exception 'unspecified entry_price must be preserved on terminal numeric correction';
  end if;
  if (select version from public.candidate_outcome where outcome_id = outcome_terminal) <> v_version + 1 then
    raise exception 'expected version to increment by exactly 1 on terminal numeric correction';
  end if;

  -- Scenario: 존재하지 않는 outcome_id.
  caught := false;
  begin
    perform public.apply_outcome_correction(key, gen_random_uuid(), 1, 'no such outcome', 'OPEN');
  exception when others then
    if sqlerrm = 'OUTCOME_NOT_FOUND' then caught := true; else raise; end if;
  end;
  if not caught then raise exception 'nonexistent outcome_id was accepted'; end if;

  -- Scenario: 잘못된 신규 상태값 -- 스키마 CHECK 도달 전에 조기 검증되어야 한다.
  select version into v_version from public.candidate_outcome where outcome_id = outcome_terminal;
  caught := false;
  begin
    perform public.apply_outcome_correction(key, outcome_terminal, v_version, 'bad status', 'INVALID');
  exception when others then
    if sqlerrm = 'INVALID_STATUS' then caught := true; else raise; end if;
  end;
  if not caught then raise exception 'invalid new status was accepted'; end if;
  if (select version from public.candidate_outcome where outcome_id = outcome_terminal) <> v_version then
    raise exception 'rejected invalid-status correction must not increment version';
  end if;

  -- Scenario: outcome_events는 여전히 append-only다 -- CORRECTION 이벤트 자체도 UPDATE되면
  -- 안 된다(기존 3.1 append-only 트리거의 회귀 확인).
  caught := false;
  begin
    update public.outcome_events set payload = '{}'::jsonb
      where logical_run_key = key and ticker = 'ZZCORR2' and command_type = 'CORRECTION';
  exception when others then
    if sqlstate = '55000' then caught := true; else raise; end if;
  end;
  if not caught then raise exception 'CORRECTION outcome_events row was mutable'; end if;

  -- Scenario: NULL expected_version must not bypass the version check (review patch) -- a
  -- correction called with p_expected_version=null must be rejected the same way a stale
  -- version is, with no event/projection change.
  caught := false;
  begin
    perform public.apply_outcome_correction(key, outcome_suspended_return, null, 'null version probe', 'OPEN');
  exception when others then
    if sqlerrm = 'CORRECTION_VERSION_MISMATCH' then caught := true; else raise; end if;
  end;
  if not caught then raise exception 'NULL expected_version was accepted'; end if;
  select count(*) into v_event_count from public.outcome_events
    where logical_run_key = key and ticker = 'ZZCORR2' and strategy = 'B' and command_type = 'CORRECTION';
  if v_event_count <> 1 then raise exception 'NULL expected_version must not append a new CORRECTION event, got %', v_event_count; end if;

  -- Scenario: p_reason NULL/blank must be rejected (review patch, epics AC4).
  select version into v_version from public.candidate_outcome where outcome_id = outcome_terminal;
  caught := false;
  begin
    perform public.apply_outcome_correction(key, outcome_terminal, v_version, null, 'TP');
  exception when others then
    if sqlerrm = 'REASON_REQUIRED' then caught := true; else raise; end if;
  end;
  if not caught then raise exception 'NULL reason was accepted'; end if;

  caught := false;
  begin
    perform public.apply_outcome_correction(key, outcome_terminal, v_version, '   ', 'TP');
  exception when others then
    if sqlerrm = 'REASON_REQUIRED' then caught := true; else raise; end if;
  end;
  if not caught then raise exception 'blank reason was accepted'; end if;
  if (select version from public.candidate_outcome where outcome_id = outcome_terminal) <> v_version then
    raise exception 'rejected reason-less correction must not increment version';
  end if;

  -- Grant/revoke: only service_role may execute apply_outcome_correction (same pattern as
  -- emit_open_command in test_outcome_open_command.sql).
  if exists (
    select 1
    from information_schema.role_routine_grants
    where routine_schema = 'public' and routine_name = 'apply_outcome_correction'
      and grantee in ('PUBLIC', 'anon', 'authenticated')
  ) then raise exception 'apply_outcome_correction must not be executable by public/anon/authenticated'; end if;

  if not exists (
    select 1
    from information_schema.role_routine_grants
    where routine_schema = 'public' and routine_name = 'apply_outcome_correction'
      and grantee = 'service_role' and privilege_type = 'EXECUTE'
  ) then raise exception 'apply_outcome_correction must be executable by service_role'; end if;
end $$;

-- Story 3.9: DELISTED correction 전이. apply_outcome_correction으로 OPEN outcome을
-- 'DELISTED'로 전이하면 outcome_events에 CORRECTION(reason 포함)이 append되고 status가
-- DELISTED로 바뀌며 version이 정확히 1 증가한다(3.8 메커니즘의 DELISTED 회귀).
do $$
declare
  key text := 'close:2099-01-17';
  outcome_delist uuid;
  v_version integer;
  correction_result jsonb;
begin
  insert into public.logical_runs(logical_run_key, trading_day, batch_kind)
    values (key, date '2099-01-17', 'close')
    on conflict (logical_run_key) do nothing;

  insert into public.outcome_events(ticker, strategy, command_type, logical_run_key, payload)
    values ('ZZDEL1', 'B', 'OPEN', key, jsonb_build_object('entry_date', date '2099-01-10', 'entry_price', 200));
  insert into public.candidate_outcome(ticker, strategy, entry_date, entry_price, status)
    values ('ZZDEL1', 'B', date '2099-01-10', 200, 'OPEN')
    returning outcome_id into outcome_delist;

  select version into v_version from public.candidate_outcome where outcome_id = outcome_delist;
  correction_result := public.apply_outcome_correction(key, outcome_delist, v_version, 'delisted from KRX', 'DELISTED');

  if (correction_result->>'status') <> 'DELISTED' then raise exception 'expected DELISTED after correction, got %', correction_result; end if;
  if (select status from public.candidate_outcome where outcome_id = outcome_delist) <> 'DELISTED' then
    raise exception 'projection status was not updated to DELISTED';
  end if;
  if (select version from public.candidate_outcome where outcome_id = outcome_delist) <> v_version + 1 then
    raise exception 'expected version to increment by exactly 1 on DELISTED correction';
  end if;
  if not exists (
    select 1 from public.outcome_events
    where logical_run_key = key and ticker = 'ZZDEL1' and strategy = 'B' and command_type = 'CORRECTION'
      and payload->>'reason' = 'delisted from KRX'
  ) then
    raise exception 'expected CORRECTION event with reason to be recorded';
  end if;
end $$;

-- Story 3.9: DELISTED 관찰 중단. DELISTED outcome은 다음 close publish_attempt의 관찰 수집
-- 루프(status not in ('TP','SL','TIMEOUT','DELISTED'))에서 제외되어 outcome_observations에
-- 새 행이 생기지 않아야 한다. 통제용 OPEN(ZZDEL2/C)은 같은 날 daily_ohlcv가 있으면 기존대로
-- 관찰을 받아 루프가 여전히 동작함을 증명한다(DELISTED만 제외).
do $$
declare
  key text := 'close:2099-01-18'; started jsonb; attempt_id uuid; fence bigint; lease uuid;
  outcome_delisted uuid; control_open uuid;
begin
  -- ZZDEL1/B는 위 Story 3.9 correction 시나리오에서 이미 DELISTED다.
  select outcome_id into outcome_delisted from public.candidate_outcome where ticker = 'ZZDEL1' and strategy = 'B';
  if outcome_delisted is null then raise exception 'expected ZZDEL1/B DELISTED outcome from prior scenario'; end if;
  if (select status from public.candidate_outcome where outcome_id = outcome_delisted) <> 'DELISTED' then
    raise exception 'expected ZZDEL1/B to be DELISTED before observation-collection exclusion check';
  end if;

  -- 통제용 OPEN outcome: ZZDEL2(strategy C)는 이전 거래일에 OPEN 상태로 진입해 두고, 오늘
  -- daily_ohlcv를 두면 관찰 수집 루프가 기존대로 관찰을 받아야 한다.
  insert into public.outcome_events(ticker, strategy, command_type, logical_run_key, payload)
    values ('ZZDEL2', 'C', 'OPEN', 'close:2099-01-10', jsonb_build_object('entry_date', date '2099-01-10', 'entry_price', 100));
  insert into public.candidate_outcome(ticker, strategy, entry_date, entry_price, status)
    values ('ZZDEL2', 'C', date '2099-01-10', 100, 'OPEN')
    returning outcome_id into control_open;

  -- DELISTED(ZZDEL1)와 통제 OPEN(ZZDEL2) 둘 다 오늘 daily_ohlcv가 있으면 관찰이 가능한 상태다
  -- -- DELISTED만 제외되어야 하므로, ZZDEL2는 관찰을 받고 ZZDEL1은 받지 않아야 한다.
  insert into public.daily_ohlcv(ticker, trading_day, open, high, low, close, volume)
    values
      ('ZZDEL1', date '2099-01-18', 100, 105, 99, 101, 1000),
      ('ZZDEL2', date '2099-01-18', 100, 101, 99, 100, 1000)
    on conflict (ticker, trading_day) do nothing;

  started := public.start_attempt(key, date '2099-01-18', 'close', 'manual', 300);
  attempt_id := (started->>'run_id')::uuid; fence := (started->>'fence_token')::bigint; lease := (started->>'lease_token')::uuid;
  perform public.write_stage(attempt_id, 'candidates', fence, lease, 'pending', 'running');
  perform public.write_stage(attempt_id, 'candidates', fence, lease, 'running', 'success');
  perform public.write_stage(attempt_id, 'tags', fence, lease, 'pending', 'running');
  perform public.write_stage(attempt_id, 'tags', fence, lease, 'running', 'success');
  perform public.write_stage(attempt_id, 'supply_3day', fence, lease, 'pending', 'running');
  perform public.write_stage(attempt_id, 'supply_3day', fence, lease, 'running', 'success');
  perform public.write_stage(attempt_id, 'market_supply', fence, lease, 'pending', 'running');
  perform public.write_stage(attempt_id, 'market_supply', fence, lease, 'running', 'success');

  perform public.__fixture_seed_market_supply(attempt_id);
  perform public.__fixture_seed_market_supply(attempt_id);
  perform public.publish_attempt(attempt_id, fence, lease);

  if (select status from public.runs where run_id = attempt_id) <> 'published' then
    raise exception 'close attempt with a DELISTED outcome but no active tags did not publish';
  end if;

  -- DELISTED outcome(ZZDEL1/B): 같은 날 daily_ohlcv가 있어도 관찰 수집 루프에서 제외된다.
  if exists (select 1 from public.outcome_observations where outcome_id = outcome_delisted and evaluation_trading_day = date '2099-01-18') then
    raise exception 'DELISTED outcome must not receive a new observation from the collection loop';
  end if;

  -- 통제 OPEN outcome(ZZDEL2/C): 기존대로 관찰을 받아 루프가 여전히 동작함을 확인한다.
  if not exists (
    select 1 from public.outcome_observations
    where outcome_id = control_open and evaluation_trading_day = date '2099-01-18'
      and high = 101 and low = 99 and close = 100 and result_code = 'OK'
  ) then
    raise exception 'expected control OPEN outcome ZZDEL2/C to receive a new observation on 2099-01-18';
  end if;
end $$;

-- Story 6.5: 전략별 TP/SL/TIMEOUT 판정. 같은 publish_attempt에서 D(3/5/20)와
-- E(2/5/30)를 함께 처리해 행별 스냅샷, SL 우선, 비용 0.1%, cutoff_n을 명시적으로 검증한다.
do $$
declare
  key text := 'close:2099-02-01';
  started jsonb;
  attempt_id uuid;
  fence bigint;
  lease uuid;
  outcome_d_tp uuid;
  outcome_e_sl uuid;
  outcome_d_timeout uuid;
  outcome_e_timeout uuid;
  seed_started jsonb;
  seed_attempt_id uuid;
  seed_fence bigint;
  seed_lease uuid;
  seed_d_candidate uuid := gen_random_uuid();
  seed_e_candidate uuid := gen_random_uuid();
begin
  insert into public.logical_runs(logical_run_key, trading_day, batch_kind)
  values
    (key, date '2099-02-01', 'close'),
    ('close:2099-01-31', date '2099-01-31', 'close'),
    ('close:2099-01-30', date '2099-01-30', 'close')
  on conflict (logical_run_key) do nothing;

  insert into public.outcome_events(ticker, strategy, command_type, logical_run_key, payload)
  values
    ('ZZ6DTO', 'D', 'OPEN', 'close:2099-01-30', '{"entry_date":"2098-01-01","entry_price":100,"tp_pct":3,"sl_pct":5,"cutoff_n":20}'::jsonb),
    ('ZZ6ETO', 'E', 'OPEN', 'close:2099-01-30', '{"entry_date":"2098-02-01","entry_price":100,"tp_pct":2,"sl_pct":5,"cutoff_n":30}'::jsonb);

  insert into public.candidate_outcome(ticker, strategy, entry_date, entry_price, status, tp_pct, sl_pct, cutoff_n)
  values
    ('ZZ6DTO', 'D', date '2098-01-01', 100, 'OPEN', 3, 5, 20),
    ('ZZ6ETO', 'E', date '2098-02-01', 100, 'OPEN', 2, 5, 30);
  select outcome_id into outcome_d_timeout from public.candidate_outcome where ticker = 'ZZ6DTO' and strategy = 'D';
  select outcome_id into outcome_e_timeout from public.candidate_outcome where ticker = 'ZZ6ETO' and strategy = 'E';

  insert into public.outcome_observations(outcome_id, evaluation_trading_day, high, low, close, result_code)
    select outcome_d_timeout, d::date, 101, 99, 100, 'OK'
    from generate_series(date '2098-01-02', date '2098-01-20', interval '1 day') d;
  insert into public.outcome_observations(outcome_id, evaluation_trading_day, high, low, close, result_code)
    select outcome_e_timeout, d::date, 101, 99, 100, 'OK'
    from generate_series(date '2098-02-02', date '2098-03-02', interval '1 day') d;
  insert into public.daily_ohlcv(ticker, trading_day, open, high, low, close, volume)
  values
    ('ZZ6DTP', date '2099-01-31', 100, 101, 99, 100, 1000),
    ('ZZ6ESL', date '2099-01-31', 100, 101, 99, 100, 1000),
    ('ZZ6DTP', date '2099-02-01', 100, 104, 99, 103, 1000),
    ('ZZ6ESL', date '2099-02-01', 100, 110, 94, 98, 1000),
    ('ZZ6DTO', date '2099-02-01', 100, 101, 97, 98, 1000),
    ('ZZ6ETO', date '2099-02-01', 100, 101, 97, 98, 1000)
  on conflict (ticker, trading_day) do nothing;

  -- 실제 active candidate_tags -> publish_attempt -> emit_open_command 경로로
  -- D/E OPEN snapshot을 생성한다. 이후 다음 close publish에서 판정을 수행한다.
  seed_started := public.start_attempt('close:2099-01-31', date '2099-01-31', 'close', 'manual', 300);
  seed_attempt_id := (seed_started->>'run_id')::uuid;
  seed_fence := (seed_started->>'fence_token')::bigint;
  seed_lease := (seed_started->>'lease_token')::uuid;
  perform public.write_stage(seed_attempt_id, 'candidates', seed_fence, seed_lease, 'pending', 'running');
  perform public.write_candidates(seed_attempt_id, seed_fence, seed_lease,
    jsonb_build_array(
      jsonb_build_object('candidate_id', seed_d_candidate, 'ticker', 'ZZ6DTP', 'name', 'Story 6.5 D TP', 'trading_value', 100,
        'sources', jsonb_build_array(jsonb_build_object('source', 't1859', 'weight', 1))),
      jsonb_build_object('candidate_id', seed_e_candidate, 'ticker', 'ZZ6ESL', 'name', 'Story 6.5 E SL', 'trading_value', 100,
        'sources', jsonb_build_array(jsonb_build_object('source', 't1859', 'weight', 1)))
    ),
    jsonb_build_object('selection_input_hash', repeat('6', 64), 'original_count', 2, 'candidate_count', 2, 'excluded_count', 0, 'truncated_count', 0));
  perform public.write_stage(seed_attempt_id, 'candidates', seed_fence, seed_lease, 'running', 'success');
  perform public.write_stage(seed_attempt_id, 'tags', seed_fence, seed_lease, 'pending', 'running');
  insert into public.candidate_tags(candidate_id, attempt_run_id, strategy, signal_date)
  values
    (seed_d_candidate, seed_attempt_id, 'D', date '2099-01-31'),
    (seed_e_candidate, seed_attempt_id, 'E', date '2099-01-31');
  perform public.write_stage(seed_attempt_id, 'tags', seed_fence, seed_lease, 'running', 'success', jsonb_build_object('tagged_count', 2));
  perform public.write_stage(seed_attempt_id, 'supply_3day', seed_fence, seed_lease, 'pending', 'running');
  perform public.write_stage(seed_attempt_id, 'supply_3day', seed_fence, seed_lease, 'running', 'success');
  perform public.write_stage(seed_attempt_id, 'market_supply', seed_fence, seed_lease, 'pending', 'running');
  perform public.write_stage(seed_attempt_id, 'market_supply', seed_fence, seed_lease, 'running', 'success');
  perform public.__fixture_seed_market_supply(seed_attempt_id);
  perform public.__fixture_seed_market_supply(seed_attempt_id);
  perform public.publish_attempt(seed_attempt_id, seed_fence, seed_lease);

  select outcome_id into outcome_d_tp from public.candidate_outcome where ticker = 'ZZ6DTP' and strategy = 'D';
  select outcome_id into outcome_e_sl from public.candidate_outcome where ticker = 'ZZ6ESL' and strategy = 'E';
  if outcome_d_tp is null or outcome_e_sl is null then
    raise exception 'active D/E candidate_tags did not create OPEN outcome projections';
  end if;
  if not exists (
    select 1 from public.outcome_events
    where ticker = 'ZZ6DTP' and strategy = 'D' and command_type = 'OPEN'
      and payload @> '{"tp_pct":3,"sl_pct":5,"cutoff_n":20}'::jsonb
  ) or not exists (
    select 1 from public.outcome_events
    where ticker = 'ZZ6ESL' and strategy = 'E' and command_type = 'OPEN'
      and payload @> '{"tp_pct":2,"sl_pct":5,"cutoff_n":30}'::jsonb
  ) then raise exception 'active D/E candidate_tags OPEN payload snapshot missing'; end if;

  started := public.start_attempt(key, date '2099-02-01', 'close', 'manual', 300);
  attempt_id := (started->>'run_id')::uuid;
  fence := (started->>'fence_token')::bigint;
  lease := (started->>'lease_token')::uuid;
  perform public.write_stage(attempt_id, 'candidates', fence, lease, 'pending', 'running');
  perform public.write_stage(attempt_id, 'candidates', fence, lease, 'running', 'success');
  perform public.write_stage(attempt_id, 'tags', fence, lease, 'pending', 'running');
  perform public.write_stage(attempt_id, 'tags', fence, lease, 'running', 'success');
  perform public.write_stage(attempt_id, 'supply_3day', fence, lease, 'pending', 'running');
  perform public.write_stage(attempt_id, 'supply_3day', fence, lease, 'running', 'success');
  perform public.write_stage(attempt_id, 'market_supply', fence, lease, 'pending', 'running');
  perform public.write_stage(attempt_id, 'market_supply', fence, lease, 'running', 'success');
  perform public.__fixture_seed_market_supply(attempt_id);
  perform public.publish_attempt(attempt_id, fence, lease);

  if (select status from public.candidate_outcome where outcome_id = outcome_d_tp) <> 'TP'
     or (select exit_price from public.candidate_outcome where outcome_id = outcome_d_tp) <> 103
     or (select return_pct from public.candidate_outcome where outcome_id = outcome_d_tp) <> 2.9 then
    raise exception 'D TP rule mismatch';
  end if;
  if (select status from public.candidate_outcome where outcome_id = outcome_e_sl) <> 'SL'
     or (select exit_price from public.candidate_outcome where outcome_id = outcome_e_sl) <> 95
     or (select return_pct from public.candidate_outcome where outcome_id = outcome_e_sl) <> -5.1 then
    raise exception 'E SL rule/cost mismatch';
  end if;
  if (select status from public.candidate_outcome where outcome_id = outcome_d_timeout) <> 'TIMEOUT'
     or (select holding_days from public.candidate_outcome where outcome_id = outcome_d_timeout) <> 20
     or (select return_pct from public.candidate_outcome where outcome_id = outcome_d_timeout) <> -2.1 then
    raise exception 'D TIMEOUT cutoff/cost mismatch';
  end if;
  if (select status from public.candidate_outcome where outcome_id = outcome_e_timeout) <> 'TIMEOUT'
     or (select holding_days from public.candidate_outcome where outcome_id = outcome_e_timeout) <> 30
     or (select return_pct from public.candidate_outcome where outcome_id = outcome_e_timeout) <> -2.1 then
    raise exception 'E TIMEOUT cutoff/cost mismatch';
  end if;
end $$;

rollback;

-- rollback fixture는 마지막 결과셋이 비어도 실행 실패가 없었다는 사실을 명시적으로 남긴다.
select 'run_lineage_contract' as fixture, 'pass' as result;
