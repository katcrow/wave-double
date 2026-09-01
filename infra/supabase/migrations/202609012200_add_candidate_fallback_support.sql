-- Story 1.6: t1859 실패 시 t1856 폴백 경로와 다중 source 병합 계약을 반영한다.
-- 202609012110_revoke_run_rpc_browser_roles.sql 이후에 적용한다.
begin;

-- write_stage: fallback_used 기록 파라미터 추가. 이전 8-param 시그니처를 명시적으로 제거해
-- positional 호출(예: 6개 필수 인자만 넘기는 기존 호출부)이 두 오버로드 사이에서 모호해지는 것을 막는다.
drop function if exists public.write_stage(uuid, text, bigint, uuid, text, text, jsonb, integer);

create or replace function public.write_stage(
  p_run_id uuid, p_stage text, p_fence_token bigint, p_lease_token uuid, p_expected_status text,
  p_status text, p_result jsonb default '{}'::jsonb, p_unprocessed_count integer default 0,
  p_fallback_used boolean default false
) returns jsonb language plpgsql security definer set search_path = public as $$
declare r public.runs; current_status text;
begin
  if p_stage not in ('candidates','tags','supply_3day','market_supply','outcome_tracking') or p_status not in ('pending','running','success','failed','partial') or jsonb_typeof(p_result) <> 'object' then raise exception using message = 'invalid stage, status, or result'; end if;
  select * into r from runs where run_id = p_run_id for update;
  if not found then raise exception using message = 'RUN_NOT_FOUND'; end if;
  if r.status = 'published' or r.fence_token <> p_fence_token or r.lease_token <> p_lease_token or r.lease_expires_at <= now() or (r.status <> 'running' and not (r.stage_status->>p_stage = p_expected_status and p_expected_status = p_status and p_status in ('success','failed','partial'))) then raise exception using message = 'STALE_FENCE_OR_LEASE'; end if;
  current_status := r.stage_status->>p_stage;
  if current_status <> p_expected_status then raise exception using message = 'EXPECTED_STATUS_MISMATCH'; end if;
  if not ((p_expected_status = 'pending' and p_status = 'running') or (p_expected_status = 'running' and p_status in ('success','failed','partial')) or (p_expected_status = p_status and p_status in ('success','failed','partial'))) then raise exception using message = 'INVALID_STAGE_TRANSITION'; end if;
  update runs set stage_status = jsonb_set(stage_status, array[p_stage], to_jsonb(p_status)),
      stage_results = jsonb_set(stage_results, array[p_stage], p_result),
      unprocessed_count = greatest(unprocessed_count, p_unprocessed_count),
      fallback_used = fallback_used or p_fallback_used,
      status = case when p_stage = 'candidates' and p_status = 'success' then 'ready_to_publish' when p_stage = 'candidates' and p_status = 'partial' then 'partial' when p_stage = 'candidates' and p_status = 'failed' then 'failed' else status end,
      finished_at = case when p_status in ('success','failed','partial') and p_stage = 'candidates' then now() else finished_at end
    where run_id = p_run_id returning * into r;
  if r.status = 'partial' then update logical_runs set latest_partial_run_id = r.run_id where logical_run_key = r.logical_run_key; end if;
  return jsonb_build_object('run_id', r.run_id, 'stage', p_stage, 'status', r.status, 'stage_status', r.stage_status, 'stage_result', r.stage_results->p_stage, 'fallback_used', r.fallback_used);
end $$;

revoke execute on function public.write_stage(uuid, text, bigint, uuid, text, text, jsonb, integer, boolean) from public, anon, authenticated;
grant execute on function public.write_stage(uuid, text, bigint, uuid, text, text, jsonb, integer, boolean) to service_role;

-- write_candidates: source 하드코딩을 제거하고 candidate 항목별 sources[] 배열(weight 합계=1)을 소비한다.
-- 시그니처는 바뀌지 않으므로(같은 p_candidates jsonb) 기존 revoke/grant는 그대로 유효하다.
create or replace function public.write_candidates(p_run_id uuid, p_fence_token bigint, p_lease_token uuid, p_candidates jsonb, p_metadata jsonb)
returns jsonb language plpgsql security definer set search_path = public as $$
declare
  r public.runs;
  item jsonb;
  source_item jsonb;
  candidate_count integer := 0;
  candidate_day date;
  weight_sum numeric;
  source_code text;
  source_weight numeric;
begin
  if jsonb_typeof(p_candidates) <> 'array' or jsonb_typeof(p_metadata) <> 'object' then raise exception using message = 'INVALID_CANDIDATE_PAYLOAD'; end if;
  select * into r from runs where run_id = p_run_id for update;
  if not found then raise exception using message = 'RUN_NOT_FOUND'; end if;
  if r.status <> 'running' or r.fence_token <> p_fence_token or r.lease_token <> p_lease_token or r.lease_expires_at <= now() then raise exception using message = 'STALE_FENCE_OR_LEASE'; end if;
  if coalesce((p_metadata->>'candidate_count')::integer, -1) <> jsonb_array_length(p_candidates) or coalesce((p_metadata->>'candidate_count')::integer, -1) > 150 or coalesce((p_metadata->>'original_count')::integer, -1) < coalesce((p_metadata->>'candidate_count')::integer, 0) + coalesce((p_metadata->>'excluded_count')::integer, 0) + coalesce((p_metadata->>'truncated_count')::integer, 0) then raise exception using message = 'INVALID_CANDIDATE_METADATA'; end if;
  select trading_day into candidate_day from logical_runs where logical_run_key = r.logical_run_key;
  for item in select value from jsonb_array_elements(p_candidates) loop
    if (item->>'candidate_id') is null or (item->>'ticker') is null or length(btrim(item->>'ticker')) = 0 or (item->>'trading_value') is null or (item->>'trading_value')::numeric in ('NaN'::numeric, 'Infinity'::numeric, '-Infinity'::numeric) or coalesce((item->>'truncated')::boolean, false) or jsonb_typeof(item->'sources') <> 'array' or jsonb_array_length(item->'sources') < 1 then raise exception using message = 'INVALID_CANDIDATE_PAYLOAD'; end if;
    -- 동일 source가 sources 배열에 중복되면 ON CONFLICT 업서트가 행을 덮어써 저장된 weight 합계가 검증한 값과 달라지므로 거부한다.
    if (select count(distinct s->>'source') from jsonb_array_elements(item->'sources') s) <> jsonb_array_length(item->'sources') then raise exception using message = 'INVALID_CANDIDATE_PAYLOAD'; end if;
    insert into candidates(candidate_id, attempt_run_id, ticker, name, trading_day, trading_value, truncated) values ((item->>'candidate_id')::uuid, p_run_id, btrim(item->>'ticker'), nullif(btrim(item->>'name'), ''), candidate_day, (item->>'trading_value')::numeric, false) on conflict (candidate_id, attempt_run_id) do nothing;

    weight_sum := 0;
    for source_item in select value from jsonb_array_elements(item->'sources') loop
      source_code := source_item->>'source';
      if source_code is null or source_code not in ('t1859', 't1852', 't1856') then raise exception using message = 'INVALID_CANDIDATE_PAYLOAD'; end if;
      source_weight := nullif(source_item->>'weight', '')::numeric;
      if source_weight is null or source_weight <= 0 or source_weight > 1 then raise exception using message = 'INVALID_CANDIDATE_PAYLOAD'; end if;
      weight_sum := weight_sum + source_weight;
      insert into candidate_source_contrib(candidate_id, attempt_run_id, source, contribution_weight) values ((item->>'candidate_id')::uuid, p_run_id, source_code, source_weight) on conflict (candidate_id, attempt_run_id, source) do update set contribution_weight = excluded.contribution_weight;
    end loop;
    if abs(weight_sum - 1) > 0.0001 then raise exception using message = 'INVALID_CANDIDATE_SOURCE_WEIGHTS'; end if;
    candidate_count := candidate_count + 1;
  end loop;
  update runs set selection_input_hash = p_metadata->>'selection_input_hash', original_count = (p_metadata->>'original_count')::integer, excluded_count = (p_metadata->>'excluded_count')::integer, truncated_count = (p_metadata->>'truncated_count')::integer where run_id = p_run_id;
  return jsonb_build_object('run_id', p_run_id, 'candidate_count', candidate_count);
exception when invalid_text_representation or numeric_value_out_of_range then raise exception using message = 'INVALID_CANDIDATE_PAYLOAD';
end $$;

commit;
