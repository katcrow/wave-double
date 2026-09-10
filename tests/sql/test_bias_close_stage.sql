-- Story 5.4: 실제 운영 RPC 경계를 검증하며 모든 fixture는 rollback한다.
begin;
create temp table bias54_checks (scenario text, status text) on commit drop;
do $$
declare
  r uuid; other_run uuid; lease uuid; f bigint; started jsonb; pop jsonb; result jsonb;
  e uuid := gen_random_uuid(); e2 uuid := gen_random_uuid(); bad uuid := gen_random_uuid();
  c uuid := gen_random_uuid(); c2 uuid := gen_random_uuid(); other_c uuid := gen_random_uuid();
  rows jsonb; invalid_rows jsonb; before_status jsonb; before_finished timestamptz;
  rejected boolean; stage_name text; role_name text; fn text;
begin
  -- 실 start + stage-write + publish 경로. 후보가 없어 outcome 생성 부작용은 없다.
  started := public.start_attempt('close:2098-05-04','2098-05-04','close','manual',300);
  r := (started->>'run_id')::uuid; f := (started->>'fence_token')::bigint;
  lease := (started->>'lease_token')::uuid;
  foreach stage_name in array array['candidates','tags','supply_3day','market_supply'] loop
    perform public.write_stage(r,stage_name,f,lease,'pending','running');
    perform public.write_stage(r,stage_name,f,lease,'running','success',jsonb_build_object('fixture','story 5-4'));
  end loop;
  insert into public.market_supply(attempt_run_id,market,trading_day,foreign_net,institution_net,individual_net,program_net)
    values(r,'KOSPI','2098-05-04',1,2,-3,4),(r,'KOSDAQ','2098-05-04',1,2,-3,4);
  perform public.publish_attempt(r,f,lease);
  if (select status from public.runs where run_id=r) <> 'published' then raise exception 'publish failed'; end if;
  if (select stage_results->'tags'->>'fixture' from public.runs where run_id=r) <> 'story 5-4' then
    raise exception 'multi-stage result restoration failed'; end if;
  insert into bias54_checks values('real_publish_and_multistage_contract','pass');
  if public.get_bias_population(r,f,lease) <> '[]'::jsonb then raise exception 'empty population'; end if;
  insert into bias54_checks values('empty_population','pass');

  -- DB 관계로 active/vanished 및 attempt 경계를 검증한다.
  insert into public.candidates(candidate_id,attempt_run_id,ticker,trading_day,trading_value)
    values(c,r,'005930','2098-05-04',100),(c2,r,'000660','2098-05-04',90);
  insert into public.candidate_source_contrib(candidate_id,attempt_run_id,source,contribution_weight)
    values(c,r,'t1859',0.5),(c,r,'t1852',0.5),(c2,r,'t1856',1);
  insert into public.candidate_tags(candidate_id,attempt_run_id,strategy,signal_date,status)
    values(c,r,'A','2098-05-03','active'),(c,r,'F','2098-05-03','active'),
      (c,r,'B','2098-05-03','vanished'),(c2,r,'A','2098-05-03','vanished');
  started := public.start_attempt('premarket:2098-05-04','2098-05-04','premarket','manual',300);
  other_run := (started->>'run_id')::uuid;
  insert into public.candidates(candidate_id,attempt_run_id,ticker,trading_day,trading_value)
    values(other_c,other_run,'005930','2098-05-04',100);
  insert into public.candidate_source_contrib(candidate_id,attempt_run_id,source,contribution_weight)
    values(other_c,other_run,'t1856',1);
  insert into public.candidate_tags(candidate_id,attempt_run_id,strategy,signal_date,status)
    values(other_c,other_run,'C','2098-05-03','active');
  pop := public.get_bias_population(r,f,lease);
  if jsonb_array_length(pop) <> 1 or pop->0->>'ticker' <> '005930'
    or pop->0->'strategies' <> '["A","F"]'::jsonb
    or jsonb_array_length(pop->0->'sources') <> 2 then raise exception 'population lineage mismatch: %',pop; end if;
  -- Python adapter는 sources 요소의 'source'/'weight' 키에 의존하므로 키명을 고정한다.
  if (select count(*) from jsonb_array_elements(pop->0->'sources') sx
      where not (sx ? 'source') or not (sx ? 'weight')
         or jsonb_typeof(sx->'weight') <> 'number') <> 0 then
    raise exception 'population source keys drifted: %',pop->0->'sources'; end if;
  insert into bias54_checks values('canonical_active_tag_source_lineage','pass');

  select jsonb_agg(jsonb_build_object('source',s,'candidate_pop_signal_count',1,
    'backtest_universe_signal_count',2,'intersection_count',1,'diff_count',0,'missed_opportunity_count',1)
    order by s) into rows from unnest(array['t1859','t1852','t1856']) s;
  -- 발행 뒤 lease 만료 및 active pointer 해제에도 bias는 정상 동작한다.
  update public.runs set lease_expires_at=now()-interval '1 hour' where run_id=r;
  select stage_status,finished_at into before_status,before_finished from public.runs where run_id=r;
  perform public.write_stage(r,'bias',f,lease,'pending','running');
  result := public.append_bias_event(r,f,lease,e,'{"fixture":"story 5-4"}',rows,'success');
  if (select count(*) from public.bias_events where bias_event_id=e) <> 1
    or (select count(*) from public.bias_event_by_source where bias_event_id=e) <> 3
    or (select stage_status->>'bias' from public.runs where run_id=r) <> 'success' then
    raise exception 'atomic append did not complete'; end if;
  if (select stage_status-'bias' from public.runs where run_id=r) <> before_status
    or (select finished_at from public.runs where run_id=r) is distinct from before_finished then
    raise exception 'bias changed required stages or finished_at'; end if;
  insert into bias54_checks values('append_three_rows_and_expired_published_lease','pass');
  result := public.append_bias_event(r,f,lease,e,'{"fixture":"story 5-4"}',rows,'success');
  if result->>'replayed' <> 'true' or (select count(*) from public.bias_events where bias_event_id=e) <> 1 then
    raise exception 'replay duplicated'; end if;
  rejected := false;
  begin
    perform public.append_bias_event(r,f,lease,e,'{"different":true}',rows,'success');
  exception when others then
    if sqlerrm <> 'BIAS_EVENT_ID_CONFLICT' then raise; end if; rejected := true;
  end;
  if not rejected then raise exception 'changed payload accepted'; end if;
  perform public.append_bias_event(r,f,lease,e2,'{"recalculation":true}',rows,'partial');
  if (select count(*) from public.bias_events where bias_event_id in (e,e2)) <> 2
    or (select stage_status->>'bias' from public.runs where run_id=r) <> 'partial' then
    raise exception 'recalculation did not append'; end if;
  insert into bias54_checks values('idempotent_retry_conflict_and_recalculation','pass');

  -- 메타 insert 이후 source CHECK 실패도 전체 rollback되어야 한다.
  invalid_rows := jsonb_set(rows,'{1,intersection_count}','99');
  rejected := false;
  begin perform public.append_bias_event(r,f,lease,bad,'{}',invalid_rows,'success');
  exception when check_violation then rejected:=true; end;
  if not rejected or exists(select 1 from public.bias_events where bias_event_id=bad)
    or (select stage_status->>'bias' from public.runs where run_id=r) <> 'partial' then
    raise exception 'atomic rollback failed'; end if;
  foreach invalid_rows in array array[rows-0,jsonb_set(rows,'{0,source}','"unknown"'),jsonb_set(rows,'{0,source}',rows->1->'source')] loop
    rejected := false;
    begin perform public.append_bias_event(r,f,lease,bad,'{}',invalid_rows,'success');
    exception when others then
      if sqlerrm <> 'INVALID_BIAS_SOURCES' then raise; end if; rejected:=true;
    end;
    if not rejected then raise exception 'invalid sources accepted'; end if;
  end loop;
  insert into bias54_checks values('atomic_rollback_and_source_validation','pass');

  rejected := false;
  begin perform public.get_bias_population(r,f,null);
  exception when others then
    if sqlerrm <> 'BIAS_CANONICAL_CLOSE_REQUIRED' then raise; end if; rejected:=true;
  end;
  if not rejected then raise exception 'null token accepted'; end if;
  rejected := false;
  begin perform public.append_bias_event(r,f+1,lease,bad,'{}',rows,'success');
  exception when others then
    if sqlerrm <> 'BIAS_CANONICAL_CLOSE_REQUIRED' then raise; end if; rejected:=true;
  end;
  if not rejected then raise exception 'wrong fence accepted'; end if;
  rejected := false;
  begin perform public.write_stage(r,'tags',f,lease,'success','success');
  exception when others then
    if sqlerrm <> 'STALE_FENCE_OR_LEASE' then raise; end if; rejected:=true;
  end;
  if not rejected then raise exception 'published tag write accepted'; end if;
  rejected := false;
  begin perform public.write_stage(other_run,'bias',(started->>'fence_token')::bigint,
    (started->>'lease_token')::uuid,'pending','running');
  exception when others then
    if sqlerrm <> 'BIAS_CANONICAL_CLOSE_REQUIRED' then raise; end if; rejected:=true;
  end;
  if not rejected then raise exception 'nonclose bias accepted'; end if;
  update public.logical_runs set canonical_success_run_id=null where logical_run_key='close:2098-05-04';
  rejected := false;
  begin perform public.get_bias_population(r,f,lease);
  exception when others then
    if sqlerrm <> 'BIAS_CANONICAL_CLOSE_REQUIRED' then raise; end if; rejected:=true;
  end;
  if not rejected then raise exception 'noncanonical read accepted'; end if;
  update public.logical_runs set canonical_success_run_id=r where logical_run_key='close:2098-05-04';
  insert into bias54_checks values('fence_canonical_and_existing_stage_guards','pass');

  perform public.write_stage(r,'bias',f,lease,'partial','running');
  perform public.write_stage(r,'bias',f,lease,'running','failed','{"result_code":"BIAS_FAILED"}');
  if (select status from public.runs where run_id=r) <> 'published'
    or (select stage_status->>'outcome_tracking' from public.runs where run_id=r) <> 'success'
    or (select canonical_success_run_id from public.logical_runs where logical_run_key='close:2098-05-04') <> r then
    raise exception 'failure damaged publication'; end if;
  insert into bias54_checks values('bias_failure_preserves_publication','pass');

  foreach fn in array array['public.get_bias_population(uuid,bigint,uuid)',
    'public.append_bias_event(uuid,bigint,uuid,uuid,jsonb,jsonb,text)',
    'public.write_stage(uuid,text,bigint,uuid,text,text,jsonb,integer,boolean)'] loop
    foreach role_name in array array['anon','authenticated'] loop
      if has_function_privilege(role_name,fn,'EXECUTE') then raise exception 'public RPC grant: %',fn; end if;
    end loop;
    if not has_function_privilege('service_role',fn,'EXECUTE') then raise exception 'missing service grant'; end if;
  end loop;
  insert into bias54_checks values('rpc_acl','pass');
end $$;
select * from bias54_checks order by scenario;
rollback;
