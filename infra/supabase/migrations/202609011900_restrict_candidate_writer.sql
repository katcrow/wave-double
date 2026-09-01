-- Story 1.5 review fix: 후보 writer는 server-side batch만 호출한다.
begin;

revoke execute on function public.write_candidates(uuid, bigint, uuid, jsonb, jsonb) from anon, authenticated;

commit;
