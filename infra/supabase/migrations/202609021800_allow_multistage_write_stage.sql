-- Story 2.5 발견 수정: write_stage가 candidates 이후 stage(tags 등)의 진행을 막던 버그를 고친다.
--
-- 202609012110/202609012200의 write_stage 가드는 "r.status <> 'running'이면 같은 stage의
-- 멱등 종결 재기록만 허용"이라는 단일-stage(candidates-only) 가정을 하고 있었다. candidates가
-- success/partial로 끝나면 runs.status가 'ready_to_publish'/'partial'로 바뀌어 더는 'running'이
-- 아니게 되므로, 뒤이은 tags stage의 pending->running 전이가 무조건 STALE_FENCE_OR_LEASE로
-- 거부되었다 -- Epic 1은 stage가 하나뿐이라 드러나지 않았던 잠재 결함이다(Story 2.5가 첫 발견).
--
-- 수정: candidates 완료 후에도 attempt가 아직 열려 있는 상태('ready_to_publish'/'partial')라면
-- 다른 stage의 정상 전이(pending->running, running->terminal)를 허용한다. 'published'는 여전히
-- 완전 잠금이고, 기존 stage의 멱등 종결 재기록 허용 범위는 그대로 유지한다(예: candidates가
-- 'failed'인 채 같은 write_stage(failed->failed) 재시도는 계속 허용).
begin;

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
  if r.status = 'published' or r.fence_token <> p_fence_token or r.lease_token <> p_lease_token or r.lease_expires_at <= now()
     or (r.status not in ('running', 'ready_to_publish', 'partial') and not (r.stage_status->>p_stage = p_expected_status and p_expected_status = p_status and p_status in ('success','failed','partial'))) then
    raise exception using message = 'STALE_FENCE_OR_LEASE';
  end if;
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

commit;
