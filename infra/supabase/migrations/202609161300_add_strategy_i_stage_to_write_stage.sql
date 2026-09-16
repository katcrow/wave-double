-- 전략 I(음봉수급쌍끌이)가 runs.stage_status에 strategy_i 키로 기록되도록 write_stage RPC와
-- runs 테이블 CHECK 제약을 확장한다.
--
-- 기존 선례(202609100200_bias_close_stage.sql)를 따르되, 전략 I는 배치 발행(publish) 전
-- active 단계에서 실행되므로 canonical close required 보호가 필요 없다.
-- 전략 I는 선택 stage이므로 기존 배치 성공 조건(publish_gate)에 영향이 없다.
begin;

-- 1) run_stage_keys: -'bias'에서 -'bias'-'strategy_i'로 확장한다.
--    기존 run이 strategy_i 키 없이 생성되어도 stage_status - 'bias' - 'strategy_i'는
--    여전히 5-키 기본값과 동일하므로 backward-compatible하다.
do $$
begin
  if not exists (
    select 1
    from pg_constraint c
    join pg_class r on r.oid = c.conrelid
    join pg_namespace n on n.oid = r.relnamespace
    where n.nspname = 'public'
      and r.relname = 'runs'
      and c.conname = 'run_stage_keys'
      and c.contype = 'c'
      and pg_get_constraintdef(c.oid) like '%''bias''%'
      and pg_get_constraintdef(c.oid) not like '%''strategy_i''%'
  ) then
    raise exception 'run_stage_keys old constraint precondition failed';
  end if;
end $$;

alter table public.runs
  drop constraint run_stage_keys;

alter table public.runs
  add constraint run_stage_keys check (
    (stage_status - 'bias' - 'strategy_i') = jsonb_build_object(
      'candidates', (stage_status ->> 'candidates'),
      'tags',       (stage_status ->> 'tags'),
      'supply_3day',(stage_status ->> 'supply_3day'),
      'market_supply',(stage_status ->> 'market_supply'),
      'outcome_tracking',(stage_status ->> 'outcome_tracking'))
  );

-- 2) run_strategy_i_stage_value: strategy_i 키가 존재하면 그 값이 유효한 stage_status여야 한다.
do $$
begin
  if exists (
    select 1
    from pg_constraint c
    join pg_class r on r.oid = c.conrelid
    join pg_namespace n on n.oid = r.relnamespace
    where n.nspname = 'public'
      and r.relname = 'runs'
      and c.conname = 'run_strategy_i_stage_value'
      and c.contype = 'c'
  ) then
    raise exception 'run_strategy_i_stage_value constraint already exists';
  end if;
end $$;

alter table public.runs
  add constraint run_strategy_i_stage_value check (
    not (stage_status ? 'strategy_i') or (
      jsonb_typeof(stage_status -> 'strategy_i') = 'string'
      and stage_status ->> 'strategy_i' in ('pending','running','success','failed','partial')
    )
  );

-- 3) write_stage: 'strategy_i'를 허용 스테이지 목록에 추가하고, 전용 분기를 삽입한다.
--    strategy_i는 발행 전 active 단계에서 실행되므로(coalesce로 null→'pending'을 처리),
--    bias와 달리 published/canonical close 조건이 없다.
create or replace function public.write_stage(
  p_run_id uuid, p_stage text, p_fence_token bigint, p_lease_token uuid,
  p_expected_status text, p_status text,
  p_result jsonb default '{}'::jsonb,
  p_unprocessed_count integer default 0,
  p_fallback_used boolean default false
) returns jsonb language plpgsql security definer set search_path = pg_catalog as $$
declare r public.runs; current_status text;
begin
  if p_stage is null or p_stage not in (
       'candidates','tags','supply_3day','market_supply','outcome_tracking','bias','strategy_i')
     or p_status is null
     or p_status not in ('pending','running','success','failed','partial')
     or jsonb_typeof(p_result) is distinct from 'object'
     or p_expected_status is null
     or p_unprocessed_count is null or p_unprocessed_count < 0
     or p_fallback_used is null
  then
    raise exception using message = 'invalid stage, status, or result';
  end if;

  select * into r from public.runs where run_id = p_run_id for update;
  if not found then raise exception using message = 'RUN_NOT_FOUND'; end if;

  -- Story 5.4: 완료된 canonical close의 선택 작업만 별도 허용한다.
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

  -- 전략 I(음봉수급쌍끌이): 발행 전 active 단계에서만 실행(16:00~20:00 KST 윈도우).
  -- 키가 없으면 coalesce로 'pending'으로 처리해 PENDING→RUNNING 전이를 허용한다.
  -- bias와 달리 canonical close 조건이 없다.
  if p_stage = 'strategy_i' then
    if r.fence_token is distinct from p_fence_token
       or r.lease_token is distinct from p_lease_token
       or r.lease_expires_at <= now() then
      raise exception using message = 'STALE_FENCE_OR_LEASE';
    end if;
    current_status := coalesce(r.stage_status->>'strategy_i', 'pending');
    if current_status is distinct from p_expected_status then
      raise exception using message = 'EXPECTED_STATUS_MISMATCH';
    end if;
    if not ((p_expected_status = 'pending' and p_status = 'running')
      or (p_expected_status = 'running' and p_status in ('success','partial','failed'))
      or (p_expected_status = p_status and p_status in ('success','partial','failed'))) then
      raise exception using message = 'INVALID_STAGE_TRANSITION';
    end if;
    update public.runs
      set stage_status = jsonb_set(stage_status, array['strategy_i'], to_jsonb(p_status)),
          stage_results = jsonb_set(stage_results, array['strategy_i'], p_result)
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

revoke execute on function public.write_stage(uuid, text, bigint, uuid, text, text, jsonb, integer, boolean) from public, anon, authenticated;
grant execute on function public.write_stage(uuid, text, bigint, uuid, text, text, jsonb, integer, boolean) to service_role;

commit;