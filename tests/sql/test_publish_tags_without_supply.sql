-- 태깅 후보 발행은 supply_3day/market_supply 성공 여부와 분리된다.
-- 실행 전 전체 migration을 적용하며, fixture는 rollback으로 운영 상태를 남기지 않는다.
begin;

do $fixture$
declare
  started jsonb;
  attempt_id uuid;
  fence bigint;
  lease uuid;
  candidate_id uuid := gen_random_uuid();
  publish_result jsonb;
  cards jsonb;
begin
  started := public.start_attempt('intraday:2099-09-29:17:30', date '2099-09-29', 'intraday', 'manual', 300);
  attempt_id := (started->>'run_id')::uuid;
  fence := (started->>'fence_token')::bigint;
  lease := (started->>'lease_token')::uuid;

  perform public.write_stage(attempt_id, 'candidates', fence, lease, 'pending', 'running');
  perform public.write_candidates(
    attempt_id, fence, lease,
    jsonb_build_array(jsonb_build_object(
      'candidate_id', candidate_id, 'ticker', 'FIXTAG01', 'name', 'fixture tag', 'trading_value', 100,
      'sources', jsonb_build_array(jsonb_build_object('source', 't1859', 'weight', 1)))),
    jsonb_build_object('selection_input_hash', repeat('e', 64), 'original_count', 1,
      'candidate_count', 1, 'excluded_count', 0, 'truncated_count', 0));
  perform public.write_stage(attempt_id, 'candidates', fence, lease, 'running', 'success');

  perform public.write_stage(attempt_id, 'tags', fence, lease, 'pending', 'running');
  insert into public.candidate_tags(candidate_id, attempt_run_id, strategy, signal_date)
    values (candidate_id, attempt_id, 'A', date '2099-09-29');
  perform public.write_stage(attempt_id, 'tags', fence, lease, 'running', 'success');

  perform public.write_stage(attempt_id, 'supply_3day', fence, lease, 'pending', 'running');
  perform public.write_stage(attempt_id, 'supply_3day', fence, lease, 'running', 'partial',
    jsonb_build_object('result_code', 'PARTIAL_SUPPLY'), 1);
  perform public.write_stage(attempt_id, 'market_supply', fence, lease, 'pending', 'running');
  perform public.write_stage(attempt_id, 'market_supply', fence, lease, 'running', 'failed',
    jsonb_build_object('result_code', 'MARKET_SUPPLY_FAILED'), 1);

  publish_result := public.publish_attempt(attempt_id, fence, lease);
  if publish_result->>'status' <> 'published' then
    raise exception 'expected published result, got %', publish_result;
  end if;
  if (select status from public.runs where run_id = attempt_id) <> 'published' then
    raise exception 'run was not published';
  end if;
  if (select current_complete_run_id from public.logical_runs
      where logical_run_key = 'intraday:2099-09-29:17:30') <> attempt_id then
    raise exception 'current complete pointer was not advanced';
  end if;

  cards := public.get_today_candidate_cards(attempt_id);
  if jsonb_array_length(cards) <> 1 or cards->0->>'ticker' <> 'FIXTAG01' then
    raise exception 'tagged card was not exposed: %', cards;
  end if;

  -- close에서도 태깅 발행과 outcome 생성은 수급 완전성과 분리된다.
  started := public.start_attempt('close:2099-09-30', date '2099-09-30', 'close', 'manual', 300);
  attempt_id := (started->>'run_id')::uuid;
  fence := (started->>'fence_token')::bigint;
  lease := (started->>'lease_token')::uuid;
  candidate_id := gen_random_uuid();

  perform public.write_stage(attempt_id, 'candidates', fence, lease, 'pending', 'running');
  perform public.write_candidates(
    attempt_id, fence, lease,
    jsonb_build_array(jsonb_build_object(
      'candidate_id', candidate_id, 'ticker', 'FIXCLOSE1', 'name', 'fixture close', 'trading_value', 100,
      'sources', jsonb_build_array(jsonb_build_object('source', 't1859', 'weight', 1)))),
    jsonb_build_object('selection_input_hash', repeat('f', 64), 'original_count', 1,
      'candidate_count', 1, 'excluded_count', 0, 'truncated_count', 0));
  perform public.write_stage(attempt_id, 'candidates', fence, lease, 'running', 'success');
  perform public.write_stage(attempt_id, 'tags', fence, lease, 'pending', 'running');
  insert into public.candidate_tags(candidate_id, attempt_run_id, strategy, signal_date)
    values (candidate_id, attempt_id, 'A', date '2099-09-30');
  perform public.write_stage(attempt_id, 'tags', fence, lease, 'running', 'success');
  perform public.write_stage(attempt_id, 'supply_3day', fence, lease, 'pending', 'running');
  perform public.write_stage(attempt_id, 'supply_3day', fence, lease, 'running', 'partial',
    jsonb_build_object('result_code', 'PARTIAL_SUPPLY'), 1);
  perform public.write_stage(attempt_id, 'market_supply', fence, lease, 'pending', 'running');
  perform public.write_stage(attempt_id, 'market_supply', fence, lease, 'running', 'failed',
    jsonb_build_object('result_code', 'MARKET_SUPPLY_FAILED'), 1);
  insert into public.daily_ohlcv(ticker, trading_day, open, high, low, close, volume)
    values ('FIXCLOSE1', date '2099-09-30', 100, 101, 99, 100, 1000);

  publish_result := public.publish_attempt(attempt_id, fence, lease);
  if publish_result->>'status' <> 'published'
     or (select status from public.runs where run_id = attempt_id) <> 'published' then
    raise exception 'close attempt was not published: %', publish_result;
  end if;
  if (select stage_status->>'outcome_tracking' from public.runs where run_id = attempt_id) <> 'success' then
    raise exception 'close outcome_tracking did not complete';
  end if;
  if (select stage_status->>'supply_3day' from public.runs where run_id = attempt_id) <> 'partial'
     or (select stage_status->>'market_supply' from public.runs where run_id = attempt_id) <> 'failed'
     or (select stage_results->'supply_3day'->>'result_code' from public.runs where run_id = attempt_id) <> 'PARTIAL_SUPPLY'
     or (select stage_results->'market_supply'->>'result_code' from public.runs where run_id = attempt_id) <> 'MARKET_SUPPLY_FAILED' then
    raise exception 'reference stage status/result was not preserved after publish';
  end if;
  if (select count(*) from public.candidate_outcome
      where ticker = 'FIXCLOSE1' and strategy = 'A' and entry_date = date '2099-09-30') <> 1
     or (select count(*) from public.outcome_events
         where logical_run_key = 'close:2099-09-30'
           and ticker = 'FIXCLOSE1' and strategy = 'A' and command_type = 'OPEN') <> 1 then
    raise exception 'close outcome was not emitted for a published partial-supply attempt';
  end if;
  if jsonb_array_length(public.get_candidate_evidence(attempt_id)) <> 0 then
    raise exception 'failed supply should expose no evidence values';
  end if;
  if jsonb_array_length(public.get_candidate_supply_hints(attempt_id)) <> 0
     or jsonb_array_length(public.get_market_supply(attempt_id)) <> 0 then
    raise exception 'failed supply/market stages must not be exposed as normal values';
  end if;
end
$fixture$;

rollback;
