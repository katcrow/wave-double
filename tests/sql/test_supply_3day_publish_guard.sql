-- Supabase SQL fixture for Story 4.1.
-- 실행 전 202609080900_parameterize_outcome_strategy_rules_f.sql까지의 모든 migration을 적용한다.
-- psql 또는 CI의 local Supabase DB에서 실행하며, 실패 시 DO 블록이 예외를 낸다.
begin;

create temp table _supply_fixture_results (
  scenario text primary key,
  status text not null
) on commit drop;

do $$
begin
  if not exists (
    select 1 from pg_constraint c
    join pg_class t on t.oid = c.conrelid
    join pg_namespace n on n.oid = t.relnamespace
    where n.nspname = 'public' and t.relname = 'candidate_tags'
      and c.conname = 'candidate_tags_strategy_check'
      and pg_get_constraintdef(c.oid) like '%''F''%'
  ) then raise exception 'candidate_tags F constraint is missing'; end if;
  if not exists (select 1 from public.outcome_strategy_rules where strategy = 'F' and tp_pct = 3 and sl_pct = 4 and cutoff_n = 999999) then
    raise exception 'F outcome rule is missing or incorrect';
  end if;
  if not has_function_privilege('service_role', 'public.publish_attempt(uuid,bigint,uuid)', 'execute')
     or has_function_privilege('anon', 'public.publish_attempt(uuid,bigint,uuid)', 'execute')
     or has_function_privilege('authenticated', 'public.publish_attempt(uuid,bigint,uuid)', 'execute') then
    raise exception 'publish_attempt grants are incorrect';
  end if;
  if not has_function_privilege('service_role', 'public.emit_open_command(text,text,text)', 'execute')
     or has_function_privilege('anon', 'public.emit_open_command(text,text,text)', 'execute')
     or has_function_privilege('authenticated', 'public.emit_open_command(text,text,text)', 'execute') then
    raise exception 'emit_open_command grants are incorrect';
  end if;
end $$;
insert into _supply_fixture_results values ('schema_and_grants', 'pass');

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
insert into _supply_fixture_results values ('pending_supply_gate', 'pass');

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
insert into _supply_fixture_results values ('failed_supply_gate', 'pass');

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
insert into _supply_fixture_results values ('partial_supply_gate', 'pass');

-- 시나리오 4: supply_3day success로 완료된 attempt -- A/F multi-tag publish_attempt가 통과하고,
-- get_dashboard_snapshot()이 supply_3day를 missing_sections에서 제외하며 해당 section을 반영한다.
do $$
declare
  key text := 'close:2099-06-04'; started jsonb; attempt_id uuid; fence bigint; lease uuid;
  candidate_id uuid := gen_random_uuid();
  snapshot jsonb; duplicate_caught boolean := false;
begin
  started := public.start_attempt(key, date '2099-06-04', 'close', 'manual', 300);
  attempt_id := (started->>'run_id')::uuid; fence := (started->>'fence_token')::bigint; lease := (started->>'lease_token')::uuid;
  perform public.write_stage(attempt_id, 'candidates', fence, lease, 'pending', 'running');
  perform public.write_candidates(attempt_id, fence, lease,
    jsonb_build_array(jsonb_build_object(
      'candidate_id', candidate_id, 'ticker', 'STORY41F', 'name', 'fixture F', 'trading_value', 100,
      'sources', jsonb_build_array(jsonb_build_object('source', 't1859', 'weight', 1)))),
    jsonb_build_object('selection_input_hash', repeat('d', 64), 'original_count', 1, 'candidate_count', 1, 'excluded_count', 0, 'truncated_count', 0));
  perform public.write_stage(attempt_id, 'candidates', fence, lease, 'running', 'success');
  perform public.write_stage(attempt_id, 'tags', fence, lease, 'pending', 'running');
  perform public.write_stage(attempt_id, 'tags', fence, lease, 'running', 'success');
  perform public.write_stage(attempt_id, 'supply_3day', fence, lease, 'pending', 'running');
  perform public.write_stage(attempt_id, 'supply_3day', fence, lease, 'running', 'success', jsonb_build_object('row_count', 3));

  -- Story 7.2/7.4 경계: 동일 후보의 A/F multi-tag와 F rule snapshot을 publish한다.
  insert into public.candidate_tags(candidate_id, attempt_run_id, strategy, signal_date, params_meta)
  values (candidate_id, attempt_id, 'F', date '2099-06-04', jsonb_build_object('strategy_f_params', jsonb_build_object('take_profit_pct', 3, 'stop_loss_pct', 4, 'max_holding_bars', null)));
  insert into public.candidate_tags(candidate_id, attempt_run_id, strategy, signal_date)
  values (candidate_id, attempt_id, 'A', date '2099-06-04');
  begin
    insert into public.candidate_tags(candidate_id, attempt_run_id, strategy, signal_date)
    values (candidate_id, attempt_id, 'F', date '2099-06-04');
  exception when unique_violation then
    duplicate_caught := true;
  end;
  if not duplicate_caught then
    raise exception 'candidate_tags allowed a duplicate F tag for the same candidate and attempt';
  end if;
  insert into public.daily_ohlcv(ticker, trading_day, open, high, low, close, volume)
  values ('STORY41F', date '2099-06-04', 71000, 73000, 70000, 72000, 1200000);

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
  if (select count(*) from public.candidate_outcome where ticker = 'STORY41F' and strategy = 'F' and entry_date = date '2099-06-04') <> 1 then
    raise exception 'expected F candidate_outcome to be emitted from an A/F multi-tag';
  end if;
  if (select cutoff_n from public.candidate_outcome where ticker = 'STORY41F' and strategy = 'F' and entry_date = date '2099-06-04') <> 999999 then
    raise exception 'expected F outcome cutoff_n sentinel 999999';
  end if;
  if not exists (select 1 from public.candidate_outcome where ticker = 'STORY41F' and strategy = 'F' and entry_date = date '2099-06-04' and tp_pct = 3 and sl_pct = 4) then
    raise exception 'expected F outcome TP/SL snapshot 3/4';
  end if;
  if not exists (
    select 1 from public.outcome_events
    where logical_run_key = key and ticker = 'STORY41F' and strategy = 'F' and command_type = 'OPEN'
      and payload->>'tp_pct' = '3.0' and payload->>'sl_pct' = '4.0' and payload->>'cutoff_n' = '999999'
  ) then
    raise exception 'expected F OPEN event payload TP/SL/cutoff snapshot';
  end if;
  if (select count(*) from public.candidate_outcome where ticker = 'STORY41F' and strategy = 'A' and entry_date = date '2099-06-04') <> 1 then
    raise exception 'expected legacy A outcome to remain compatible with A/F multi-tag publish';
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

insert into _supply_fixture_results values ('f_only_publish_and_snapshot', 'pass');
do $$
begin
  if (select count(*) from _supply_fixture_results) <> 5 then
    raise exception 'expected exactly 5 fixture pass rows';
  end if;
  if exists (select 1 from _supply_fixture_results where status <> 'pass') then
    raise exception 'fixture returned a non-pass status';
  end if;
end $$;
select scenario, status from _supply_fixture_results order by scenario;

rollback;
