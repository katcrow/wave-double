-- Supabase SQL fixture for Story 4.1.
-- 실행 전 202609070900_supply_3day_publish_guard.sql까지의 모든 migration을 적용한다.
-- psql 또는 CI의 local Supabase DB에서 실행하며, 실패 시 DO 블록이 예외를 낸다.
begin;

-- 시나리오 1: supply_3day가 아직 pending인 채 publish_attempt 호출 -- SUPPLY_3DAY_STAGE_NOT_COMPLETE 예외.
do $$
declare
  key text := 'close:2099-06-01'; started jsonb; attempt_id uuid; fence bigint; lease uuid;
  candidate_id uuid := gen_random_uuid();
  caught boolean := false;
begin
  started := public.start_attempt(key, date '2099-06-01', 'close', 'manual', 300);
  attempt_id := (started->>'run_id')::uuid; fence := (started->>'fence_token')::bigint; lease := (started->>'lease_token')::uuid;
  perform public.write_stage(attempt_id, 'candidates', fence, lease, 'pending', 'running');
  perform public.write_candidates(attempt_id, fence, lease,
    jsonb_build_array(jsonb_build_object(
      'candidate_id', candidate_id, 'ticker', '005930', 'name', '삼성전자', 'trading_value', 100,
      'sources', jsonb_build_array(jsonb_build_object('source', 't1859', 'weight', 1)))),
    jsonb_build_object('selection_input_hash', repeat('a', 64), 'original_count', 1, 'candidate_count', 1, 'excluded_count', 0, 'truncated_count', 0));
  perform public.write_stage(attempt_id, 'candidates', fence, lease, 'running', 'success');
  perform public.write_stage(attempt_id, 'tags', fence, lease, 'pending', 'running');
  perform public.write_stage(attempt_id, 'tags', fence, lease, 'running', 'success');
  -- 의도적으로 supply_3day stage를 실행하지 않는다(여전히 'pending').

  begin
    perform public.publish_attempt(attempt_id, fence, lease);
  exception when others then
    if sqlerrm = 'SUPPLY_3DAY_STAGE_NOT_COMPLETE' then caught := true; else raise; end if;
  end;
  if not caught then raise exception 'publish_attempt did not enforce SUPPLY_3DAY_STAGE_NOT_COMPLETE for a pending supply_3day stage'; end if;
  if (select status from public.runs where run_id = attempt_id) = 'published' then
    raise exception 'attempt was published despite missing supply_3day stage';
  end if;
end $$;

-- 시나리오 2: supply_3day가 failed로 종결된 채 publish_attempt 호출 -- 동일하게 막혀야 한다.
do $$
declare
  key text := 'close:2099-06-02'; started jsonb; attempt_id uuid; fence bigint; lease uuid;
  candidate_id uuid := gen_random_uuid();
  caught boolean := false;
begin
  started := public.start_attempt(key, date '2099-06-02', 'close', 'manual', 300);
  attempt_id := (started->>'run_id')::uuid; fence := (started->>'fence_token')::bigint; lease := (started->>'lease_token')::uuid;
  perform public.write_stage(attempt_id, 'candidates', fence, lease, 'pending', 'running');
  perform public.write_candidates(attempt_id, fence, lease,
    jsonb_build_array(jsonb_build_object(
      'candidate_id', candidate_id, 'ticker', '005930', 'name', '삼성전자', 'trading_value', 100,
      'sources', jsonb_build_array(jsonb_build_object('source', 't1859', 'weight', 1)))),
    jsonb_build_object('selection_input_hash', repeat('b', 64), 'original_count', 1, 'candidate_count', 1, 'excluded_count', 0, 'truncated_count', 0));
  perform public.write_stage(attempt_id, 'candidates', fence, lease, 'running', 'success');
  perform public.write_stage(attempt_id, 'tags', fence, lease, 'pending', 'running');
  perform public.write_stage(attempt_id, 'tags', fence, lease, 'running', 'success');
  perform public.write_stage(attempt_id, 'supply_3day', fence, lease, 'pending', 'running');
  perform public.write_stage(attempt_id, 'supply_3day', fence, lease, 'running', 'failed');

  begin
    perform public.publish_attempt(attempt_id, fence, lease);
  exception when others then
    if sqlerrm = 'SUPPLY_3DAY_STAGE_NOT_COMPLETE' then caught := true; else raise; end if;
  end;
  if not caught then raise exception 'publish_attempt did not enforce SUPPLY_3DAY_STAGE_NOT_COMPLETE for a failed supply_3day stage'; end if;
end $$;

-- 시나리오 3: supply_3day가 partial로 종결된 채 publish_attempt 호출 -- 동일하게 막혀야 한다.
do $$
declare
  key text := 'close:2099-06-03'; started jsonb; attempt_id uuid; fence bigint; lease uuid;
  candidate_id uuid := gen_random_uuid();
  caught boolean := false;
begin
  started := public.start_attempt(key, date '2099-06-03', 'close', 'manual', 300);
  attempt_id := (started->>'run_id')::uuid; fence := (started->>'fence_token')::bigint; lease := (started->>'lease_token')::uuid;
  perform public.write_stage(attempt_id, 'candidates', fence, lease, 'pending', 'running');
  perform public.write_candidates(attempt_id, fence, lease,
    jsonb_build_array(jsonb_build_object(
      'candidate_id', candidate_id, 'ticker', '005930', 'name', '삼성전자', 'trading_value', 100,
      'sources', jsonb_build_array(jsonb_build_object('source', 't1859', 'weight', 1)))),
    jsonb_build_object('selection_input_hash', repeat('c', 64), 'original_count', 1, 'candidate_count', 1, 'excluded_count', 0, 'truncated_count', 0));
  perform public.write_stage(attempt_id, 'candidates', fence, lease, 'running', 'success');
  perform public.write_stage(attempt_id, 'tags', fence, lease, 'pending', 'running');
  perform public.write_stage(attempt_id, 'tags', fence, lease, 'running', 'success');
  perform public.write_stage(attempt_id, 'supply_3day', fence, lease, 'pending', 'running');
  perform public.write_stage(attempt_id, 'supply_3day', fence, lease, 'running', 'partial', '{}'::jsonb, 1);

  begin
    perform public.publish_attempt(attempt_id, fence, lease);
  exception when others then
    if sqlerrm = 'SUPPLY_3DAY_STAGE_NOT_COMPLETE' then caught := true; else raise; end if;
  end;
  if not caught then raise exception 'publish_attempt did not enforce SUPPLY_3DAY_STAGE_NOT_COMPLETE for a partial supply_3day stage'; end if;
end $$;

-- 시나리오 4: supply_3day success로 완료된 attempt -- publish_attempt가 통과하고,
-- get_dashboard_snapshot()이 supply_3day를 missing_sections에서 제외하며 해당 section을 반영한다.
do $$
declare
  key text := 'close:2099-06-04'; started jsonb; attempt_id uuid; fence bigint; lease uuid;
  candidate_id uuid := gen_random_uuid();
  snapshot jsonb;
begin
  started := public.start_attempt(key, date '2099-06-04', 'close', 'manual', 300);
  attempt_id := (started->>'run_id')::uuid; fence := (started->>'fence_token')::bigint; lease := (started->>'lease_token')::uuid;
  perform public.write_stage(attempt_id, 'candidates', fence, lease, 'pending', 'running');
  perform public.write_candidates(attempt_id, fence, lease,
    jsonb_build_array(jsonb_build_object(
      'candidate_id', candidate_id, 'ticker', '005930', 'name', '삼성전자', 'trading_value', 100,
      'sources', jsonb_build_array(jsonb_build_object('source', 't1859', 'weight', 1)))),
    jsonb_build_object('selection_input_hash', repeat('d', 64), 'original_count', 1, 'candidate_count', 1, 'excluded_count', 0, 'truncated_count', 0));
  perform public.write_stage(attempt_id, 'candidates', fence, lease, 'running', 'success');
  perform public.write_stage(attempt_id, 'tags', fence, lease, 'pending', 'running');
  perform public.write_stage(attempt_id, 'tags', fence, lease, 'running', 'success');
  perform public.write_stage(attempt_id, 'supply_3day', fence, lease, 'pending', 'running');
  perform public.write_stage(attempt_id, 'supply_3day', fence, lease, 'running', 'success', jsonb_build_object('row_count', 3));

  insert into public.supply_3day(
    candidate_id, attempt_run_id, trading_day, slot, close, volume, change_pct,
    foreign_net, institution_net, individual_net, program_net, investor_net_status
  ) values
    (candidate_id, attempt_id, date '2099-06-02', 'D-2', 70000, 1000000, 1.0, 100, 200, -300, null, 'confirmed'),
    (candidate_id, attempt_id, date '2099-06-03', 'D-1', 71000, 1100000, 1.4, 110, 210, -320, null, 'confirmed'),
    (candidate_id, attempt_id, date '2099-06-04', 'D0', 72000, 1200000, 1.4, 120, 220, -340, null, 'confirmed');

  perform public.publish_attempt(attempt_id, fence, lease);
  if (select status from public.runs where run_id = attempt_id) <> 'published' then
    raise exception 'expected publish_attempt to succeed once supply_3day stage is success';
  end if;

  update public.logical_runs set published_at = timestamptz '2099-06-04 00:00:00+00' where logical_run_key = key;

  snapshot := public.get_dashboard_snapshot();
  if snapshot->'complete_snapshot'->>'run_id' <> attempt_id::text then
    raise exception 'complete_snapshot did not point at the published run';
  end if;
  if not (snapshot->'complete_snapshot'->'sections' ? 'supply_3day') then
    raise exception 'expected sections.supply_3day to be present, got %', snapshot->'complete_snapshot'->'sections';
  end if;
  if (snapshot->'complete_snapshot'->'sections'->'supply_3day'->>'row_count')::integer <> 3 then
    raise exception 'expected supply_3day.row_count=3, got %', snapshot->'complete_snapshot'->'sections'->'supply_3day';
  end if;
  if not (snapshot->'available_partial_sections' @> '["supply_3day"]'::jsonb) then
    raise exception 'expected available_partial_sections to include supply_3day, got %', snapshot->'available_partial_sections';
  end if;
  if snapshot->'missing_sections' @> '["supply_3day"]'::jsonb then
    raise exception 'expected missing_sections to exclude supply_3day, got %', snapshot->'missing_sections';
  end if;
  if not (snapshot->'missing_sections' @> '["market_supply"]'::jsonb) then
    raise exception 'expected missing_sections to still include market_supply (out of story scope), got %', snapshot->'missing_sections';
  end if;
end $$;

rollback;
