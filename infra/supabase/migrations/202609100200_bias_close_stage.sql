-- Story 5.4: 종가 발행 후 선택 편향 stage 및 원자적 append.
-- 운영에 되돌아간 구 write_stage를 2.5 multi-stage 계약으로 복원한다.
begin;

-- 5개 section은 유지하면서 선택 bias 키만 허용한다. 기존 5-key run도 유효하다.
alter table public.runs drop constraint run_stage_keys;
alter table public.runs add constraint run_stage_keys check (
  stage_status - 'bias' = jsonb_build_object(
    'candidates', stage_status->>'candidates', 'tags', stage_status->>'tags',
    'supply_3day', stage_status->>'supply_3day', 'market_supply', stage_status->>'market_supply',
    'outcome_tracking', stage_status->>'outcome_tracking')
);
alter table public.runs add constraint run_bias_stage_value check (
  not (stage_status ? 'bias') or (
    jsonb_typeof(stage_status->'bias') = 'string'
    and stage_status->>'bias' in ('pending','running','success','failed','partial')
  )
);

create or replace function public.write_stage(
  p_run_id uuid, p_stage text, p_fence_token bigint, p_lease_token uuid, p_expected_status text,
  p_status text, p_result jsonb default '{}'::jsonb, p_unprocessed_count integer default 0,
  p_fallback_used boolean default false
) returns jsonb language plpgsql security definer set search_path = pg_catalog as $$
declare r public.runs; current_status text;
begin
  if p_stage is null or p_stage not in ('candidates','tags','supply_3day','market_supply','outcome_tracking','bias') or p_status is null or p_status not in ('pending','running','success','failed','partial') or jsonb_typeof(p_result) is distinct from 'object' or p_expected_status is null or p_unprocessed_count is null or p_unprocessed_count < 0 or p_fallback_used is null then raise exception using message = 'invalid stage, status, or result'; end if;
  select * into r from public.runs where run_id = p_run_id for update;
  if not found then raise exception using message = 'RUN_NOT_FOUND'; end if;
  -- Story 5.4: 완료된 canonical close의 선택 작업만 별도 허용한다.
  -- active_attempt/lease 만료는 발행 후 의미가 없지만 token identity는 필수다.
  if p_stage = 'bias' then
    if r.status <> 'published' or r.fence_token is distinct from p_fence_token
       or r.lease_token is distinct from p_lease_token then
      raise exception using message = 'BIAS_CANONICAL_CLOSE_REQUIRED';
    end if;
    perform 1 from public.logical_runs l where l.logical_run_key = r.logical_run_key
      and l.batch_kind = 'close' and l.canonical_success_run_id = r.run_id for share;
    if not found then raise exception using message = 'BIAS_CANONICAL_CLOSE_REQUIRED'; end if;
    current_status := coalesce(r.stage_status->>'bias', 'pending');
    if current_status is distinct from p_expected_status then
      raise exception using message = 'EXPECTED_STATUS_MISMATCH';
    end if;
    if not ((p_expected_status in ('pending','success','partial','failed') and p_status = 'running')
      or (p_expected_status = 'running' and p_status in ('success','partial','failed'))
      or (p_expected_status = p_status and p_status in ('success','partial','failed'))) then
      raise exception using message = 'INVALID_STAGE_TRANSITION';
    end if;
    update public.runs set stage_status = jsonb_set(stage_status, array['bias'], to_jsonb(p_status)),
      stage_results = jsonb_set(stage_results, array['bias'], p_result)
      where run_id = p_run_id returning * into r;
    return jsonb_build_object('run_id', r.run_id, 'stage', p_stage, 'status', r.status,
      'stage_status', r.stage_status, 'stage_result', r.stage_results->p_stage,
      'fallback_used', r.fallback_used);
  end if;
  if r.status = 'published' or r.fence_token is distinct from p_fence_token or r.lease_token is distinct from p_lease_token or r.lease_expires_at <= now()
     or (r.status not in ('running', 'ready_to_publish', 'partial') and not (r.stage_status->>p_stage = p_expected_status and p_expected_status = p_status and p_status in ('success','failed','partial'))) then
    raise exception using message = 'STALE_FENCE_OR_LEASE';
  end if;
  current_status := r.stage_status->>p_stage;
  if current_status is distinct from p_expected_status then raise exception using message = 'EXPECTED_STATUS_MISMATCH'; end if;
  if not ((p_expected_status = 'pending' and p_status = 'running') or (p_expected_status = 'running' and p_status in ('success','failed','partial')) or (p_expected_status = p_status and p_status in ('success','failed','partial'))) then raise exception using message = 'INVALID_STAGE_TRANSITION'; end if;
  update public.runs set stage_status = jsonb_set(stage_status, array[p_stage], to_jsonb(p_status)),
      stage_results = jsonb_set(stage_results, array[p_stage], p_result),
      unprocessed_count = greatest(unprocessed_count, p_unprocessed_count),
      fallback_used = fallback_used or p_fallback_used,
      status = case
        when p_stage = 'candidates' and p_status = 'success' then 'ready_to_publish'
        when p_stage = 'candidates' and p_status = 'partial' then 'partial'
        when p_stage = 'candidates' and p_status = 'failed' then 'failed'
        when p_stage = 'tags' and p_status = 'failed' then 'failed'
        when p_stage = 'tags' and p_status = 'partial' and status <> 'failed' then 'partial'
        else status
      end,
      finished_at = case when p_status in ('success','failed','partial') and p_stage in ('candidates','tags') then now() else finished_at end
    where run_id = p_run_id returning * into r;
  if r.status = 'partial' then update public.logical_runs set latest_partial_run_id = r.run_id where logical_run_key = r.logical_run_key; end if;
  return jsonb_build_object('run_id', r.run_id, 'stage', p_stage, 'status', r.status, 'stage_status', r.stage_status, 'stage_result', r.stage_results->p_stage, 'fallback_used', r.fallback_used);
end $$;

create or replace function public.get_bias_population(
  p_run_id uuid, p_fence_token bigint, p_lease_token uuid
) returns jsonb language plpgsql security definer set search_path = pg_catalog as $$
declare r public.runs; population jsonb;
begin
  select * into r from public.runs where run_id = p_run_id;
  if not found or r.status <> 'published' or r.fence_token is distinct from p_fence_token
    or r.lease_token is distinct from p_lease_token or not exists (
      select 1 from public.logical_runs l where l.logical_run_key = r.logical_run_key
        and l.batch_kind = 'close' and l.canonical_success_run_id = r.run_id
    ) then raise exception using message = 'BIAS_CANONICAL_CLOSE_REQUIRED'; end if;
  select coalesce(jsonb_agg(jsonb_build_object('ticker', c.ticker,
    'strategies', t.strategies, 'sources', s.sources) order by c.ticker), '[]'::jsonb)
    into population
  from public.candidates c
  cross join lateral (
    select jsonb_agg(distinct ct.strategy order by ct.strategy) as strategies
    from public.candidate_tags ct where ct.candidate_id = c.candidate_id
      and ct.attempt_run_id = c.attempt_run_id and ct.status = 'active'
  ) t
  cross join lateral (
    select coalesce(jsonb_agg(jsonb_build_object('source', sc.source,
      'weight', sc.contribution_weight) order by sc.source), '[]'::jsonb) as sources
    from public.candidate_source_contrib sc where sc.candidate_id = c.candidate_id
      and sc.attempt_run_id = c.attempt_run_id
  ) s
  where c.attempt_run_id = r.run_id and t.strategies is not null;
  return population;
end $$;

create or replace function public.append_bias_event(
  p_run_id uuid, p_fence_token bigint, p_lease_token uuid, p_event_id uuid,
  p_calculation_meta jsonb, p_rows jsonb, p_status text
) returns jsonb language plpgsql security definer set search_path = pg_catalog as $$
declare
  r public.runs; l public.logical_runs; previous public.bias_events;
  normalized_rows jsonb; stored_rows jsonb; meta jsonb; current_status text;
begin
  if p_event_id is null or jsonb_typeof(p_calculation_meta) is distinct from 'object'
     or jsonb_typeof(p_rows) is distinct from 'array'
     or p_status is null or p_status not in ('success','partial') then
    raise exception using message = 'INVALID_BIAS_PAYLOAD';
  end if;
  if jsonb_array_length(p_rows) <> 3 or exists (
    select 1 from jsonb_array_elements(p_rows) x where jsonb_typeof(x) <> 'object'
  ) then raise exception using message = 'INVALID_BIAS_SOURCES'; end if;
  select jsonb_agg(to_jsonb(x) order by x.source) into normalized_rows
  from jsonb_to_recordset(p_rows) as x(source text, candidate_pop_signal_count integer,
    backtest_universe_signal_count integer, intersection_count integer,
    diff_count integer, missed_opportunity_count integer);
  if (select count(distinct x->>'source') from jsonb_array_elements(normalized_rows) x
      where x->>'source' in ('t1859','t1852','t1856')) <> 3 then
    raise exception using message = 'INVALID_BIAS_SOURCES';
  end if;
  select * into r from public.runs where run_id = p_run_id for update;
  if not found or r.status <> 'published' or r.fence_token is distinct from p_fence_token
     or r.lease_token is distinct from p_lease_token then
    raise exception using message = 'BIAS_CANONICAL_CLOSE_REQUIRED';
  end if;
  select * into l from public.logical_runs where logical_run_key = r.logical_run_key for share;
  if l.batch_kind <> 'close' or l.canonical_success_run_id is distinct from r.run_id then
    raise exception using message = 'BIAS_CANONICAL_CLOSE_REQUIRED';
  end if;
  meta := p_calculation_meta || jsonb_build_object('attempt_run_id', r.run_id, 'completion_status', p_status);
  -- 같은 ID의 동시 재전송도 serialize한다. 다른 run에서 같은 ID를 쓰는 충돌도 보호한다.
  perform pg_advisory_xact_lock(hashtextextended('bias:' || p_event_id::text, 0));
  select * into previous from public.bias_events where bias_event_id = p_event_id;
  if found then
    select jsonb_agg(jsonb_build_object('source', s.source,
      'candidate_pop_signal_count', s.candidate_pop_signal_count,
      'backtest_universe_signal_count', s.backtest_universe_signal_count,
      'intersection_count', s.intersection_count, 'diff_count', s.diff_count,
      'missed_opportunity_count', s.missed_opportunity_count) order by s.source)
      into stored_rows from public.bias_event_by_source s where s.bias_event_id = p_event_id;
    if previous.logical_run_key is distinct from r.logical_run_key
      or previous.trading_day is distinct from l.trading_day
      or previous.calculation_meta is distinct from meta
      or stored_rows is distinct from normalized_rows then
      raise exception using message = 'BIAS_EVENT_ID_CONFLICT';
    end if;
    return jsonb_build_object('bias_event_id', p_event_id, 'status', p_status, 'replayed', true);
  end if;
  current_status := coalesce(r.stage_status->>'bias', 'pending');
  if current_status <> 'running' then
    perform public.write_stage(p_run_id, 'bias', p_fence_token, p_lease_token,
      current_status, 'running');
  end if;
  insert into public.bias_events(bias_event_id, trading_day, logical_run_key, calculation_meta)
    values (p_event_id, l.trading_day, r.logical_run_key, meta);
  insert into public.bias_event_by_source(bias_event_id, source, candidate_pop_signal_count,
    backtest_universe_signal_count, intersection_count, diff_count, missed_opportunity_count)
    select p_event_id, x.source, x.candidate_pop_signal_count, x.backtest_universe_signal_count,
      x.intersection_count, x.diff_count, x.missed_opportunity_count
    from jsonb_to_recordset(normalized_rows) as x(source text, candidate_pop_signal_count integer,
      backtest_universe_signal_count integer, intersection_count integer,
      diff_count integer, missed_opportunity_count integer);
  perform public.write_stage(p_run_id, 'bias', p_fence_token, p_lease_token, 'running', p_status,
    jsonb_build_object('bias_event_id', p_event_id, 'result_code',
      case when p_status = 'success' then 'BIAS_OK' else 'BIAS_PARTIAL' end));
  return jsonb_build_object('bias_event_id', p_event_id, 'status', p_status, 'replayed', false);
end $$;

revoke execute on function public.write_stage(uuid,text,bigint,uuid,text,text,jsonb,integer,boolean)
  from public, anon, authenticated;
revoke execute on function public.get_bias_population(uuid,bigint,uuid) from public, anon, authenticated;
revoke execute on function public.append_bias_event(uuid,bigint,uuid,uuid,jsonb,jsonb,text)
  from public, anon, authenticated;
grant execute on function public.write_stage(uuid,text,bigint,uuid,text,text,jsonb,integer,boolean) to service_role;
grant execute on function public.get_bias_population(uuid,bigint,uuid) to service_role;
grant execute on function public.append_bias_event(uuid,bigint,uuid,uuid,jsonb,jsonb,text) to service_role;

comment on function public.append_bias_event(uuid,bigint,uuid,uuid,jsonb,jsonb,text) is
  'Story 5.4: canonical published close의 편향 메타+source 3행+stage-write 완료를 원자 append. 같은 event ID/payload는 재전송이며 다른 payload는 거부한다.';
comment on function public.get_bias_population(uuid,bigint,uuid) is
  'Story 5.4: canonical published close의 active 태그와 동일 candidate/attempt 기여만 읽는다.';

commit;

