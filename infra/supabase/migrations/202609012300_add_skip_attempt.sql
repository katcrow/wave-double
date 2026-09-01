-- Story 1.7: 휴장일 스킵 종결을 위한 유일한 쓰기 경로.
-- 202609012200_add_candidate_fallback_support.sql 이후에 적용한다.
begin;

create or replace function public.skip_attempt(
  p_run_id uuid, p_fence_token bigint, p_lease_token uuid, p_skip_reason text
) returns jsonb language plpgsql security definer set search_path = public as $$
declare r public.runs;
begin
  if p_skip_reason is null or length(btrim(p_skip_reason)) = 0 then raise exception using message = 'INVALID_SKIP_REASON'; end if;
  select * into r from runs where run_id = p_run_id for update;
  if not found then raise exception using message = 'RUN_NOT_FOUND'; end if;
  if r.status <> 'running' or r.fence_token <> p_fence_token or r.lease_token <> p_lease_token or r.lease_expires_at <= now() then
    raise exception using message = 'STALE_FENCE_OR_LEASE';
  end if;
  update runs set status = 'skipped', skip_reason = p_skip_reason, finished_at = now()
    where run_id = p_run_id returning * into r;
  return jsonb_build_object('run_id', r.run_id, 'status', r.status, 'skip_reason', r.skip_reason);
end $$;

revoke execute on function public.skip_attempt(uuid, bigint, uuid, text) from public, anon, authenticated;
grant execute on function public.skip_attempt(uuid, bigint, uuid, text) to service_role;

commit;
