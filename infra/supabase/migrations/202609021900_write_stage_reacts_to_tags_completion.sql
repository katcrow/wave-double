-- Story 2.5 코드 리뷰 발견(high) 수정: write_stage의 runs.status/finished_at 갱신 로직이
-- p_stage='candidates' 전이에만 반응해, tags stage(후보 재조회 실패/전 종목
-- SIGNAL_COMPUTE_ERROR/upsert 실패)가 failed/partial로 종결돼도 runs.status가
-- candidates가 남긴 'ready_to_publish'/'partial'에 그대로 머물러 있었다 -- 죽은 파이프라인이
-- 영원히 "발행 가능"처럼 보이는 상태로 남는다.
--
-- 수정: p_stage='tags'가 terminal(success/failed/partial)로 종결될 때도 runs.status/
-- finished_at이 반응하도록 CASE 분기를 추가한다.
--   - tags success: 이미 candidates가 정한 상태(ready_to_publish 또는 partial)를 그대로
--     확정한다(격상/격하하지 않음).
--   - tags partial: 아직 failed가 아니면 partial로 낮춘다(부분 태깅 실패를 노출).
--   - tags failed: failed로 낮춘다(태깅이 전혀 저장되지 않았음을 노출).
-- finished_at도 candidates뿐 아니라 tags의 terminal 종결 시각까지 반영하도록 확장한다
-- (tags가 candidates 뒤에 이어서 실행되므로, 파이프라인 전체가 끝난 시각을 반영하는 편이
-- 더 정확하다).
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
  if r.status = 'partial' then update logical_runs set latest_partial_run_id = r.run_id where logical_run_key = r.logical_run_key; end if;
  return jsonb_build_object('run_id', r.run_id, 'stage', p_stage, 'status', r.status, 'stage_status', r.stage_status, 'stage_result', r.stage_results->p_stage, 'fallback_used', r.fallback_used);
end $$;

commit;
