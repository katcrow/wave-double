-- Story 4.8: 시장 수급 원본 테이블은 read RPC만 통해 노출한다.
-- 기존 202609081300 migration은 수정하지 않고 권한을 forward-only로 잠근다.
begin;

revoke select on table public.market_supply from public, anon, authenticated;

comment on table public.market_supply is
  'Story 4.5/4.8: 원본 테이블 직접 SELECT는 허용하지 않으며 published complete attempt 전용 read RPC로만 조회한다.';

commit;
