-- Story 1.5 review fix: 후보 원천 테이블은 브라우저에서 직접 노출하지 않는다.
-- 읽기는 후속 approved view/RPC가 소유하고, 현재는 security-definer stage RPC만 기록한다.
begin;

alter table public.candidates enable row level security;
alter table public.candidate_source_contrib enable row level security;

commit;
