-- Story 6.5 review patch (AD-14 forward-only).
-- 내부 트리거 함수는 RPC 표면이 아니므로 브라우저 역할의 EXECUTE를 허용하지 않는다.
begin;

revoke execute on function public.guard_outcome_strategy_snapshot() from public, anon, authenticated;
revoke execute on function public.reject_outcome_open_projection_conflict() from public, anon, authenticated;

commit;
