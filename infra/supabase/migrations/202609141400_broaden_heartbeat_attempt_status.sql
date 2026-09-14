-- 실전 장애 조사(2026-09-14): scheduled-batch가 매 close/intraday 배치마다
-- "lease heartbeat failed 3 times consecutively"로 죽고 있었다. 202609021900이
-- write_stage의 candidates 단계 성공 시 status를 즉시 'running' -> 'ready_to_publish'로
-- 전이시키도록 계약을 넓혔는데(item-11 heartbeat 도입보다 먼저 있던 계약), 그 뒤에
-- 추가된 heartbeat_attempt(epic-2-retro item-11)는 여전히 status = 'running'만
-- 허용하는 원본(202609011600) 정의를 그대로 쓰고 있었다. candidates 단계는 tags/supply
-- 루프보다 먼저 끝나 status가 곧바로 ready_to_publish로 바뀌므로, heartbeat를 실제로
-- 필요로 하는 구간(ticker history 갱신 + tags stage)에서는 매번 즉시 STALE_FENCE_OR_LEASE로
-- 거부됐다 -- heartbeat 기능이 도입 이후 한 번도 정상 동작한 적이 없었다.
-- write_stage가 이미 이 세 상태에서의 계속 진행을 허용하므로(202609021900:29)
-- heartbeat_attempt도 동일한 허용 목록으로 맞춘다.
begin;

create or replace function public.heartbeat_attempt(
  p_run_id uuid, p_fence_token bigint, p_lease_token uuid, p_lease_seconds integer default 300
) returns jsonb language plpgsql security definer set search_path = public as $$
declare r public.runs;
begin
  if p_lease_seconds <= 0 then raise exception using message = 'lease_seconds must be positive'; end if;
  update runs set lease_expires_at = now() + make_interval(secs => p_lease_seconds)
    where run_id = p_run_id and fence_token = p_fence_token and lease_token = p_lease_token
      and status in ('running', 'ready_to_publish', 'partial') and lease_expires_at > now() returning * into r;
  if not found then raise exception using message = 'STALE_FENCE_OR_LEASE'; end if;
  return jsonb_build_object('run_id', r.run_id, 'lease_expires_at', r.lease_expires_at);
end $$;

commit;
