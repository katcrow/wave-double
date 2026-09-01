-- Story 1.5 review fix: PUBLIC 기본 EXECUTE 상속도 제거한다.
begin;

revoke execute on function public.write_candidates(uuid, bigint, uuid, jsonb, jsonb) from public;

commit;
