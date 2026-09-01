-- Story 1.3 hardening follow-up: Supabase roles can retain explicit grants beyond PUBLIC.
begin;

revoke execute on function public.start_attempt(text, date, text, text, integer) from public, anon, authenticated;
revoke execute on function public.write_stage(uuid, text, bigint, uuid, text, text, jsonb, integer) from public, anon, authenticated;
revoke execute on function public.heartbeat_attempt(uuid, bigint, uuid, integer) from public, anon, authenticated;
revoke execute on function public.reap_expired_attempts(timestamptz) from public, anon, authenticated;
revoke execute on function public.publish_attempt(uuid, bigint) from public, anon, authenticated;
revoke execute on function public.publish_attempt(uuid, bigint, uuid) from public, anon, authenticated;
revoke execute on function public.write_candidates(uuid, bigint, uuid, jsonb, jsonb) from public, anon, authenticated;

grant execute on function public.start_attempt(text, date, text, text, integer), public.write_stage(uuid, text, bigint, uuid, text, text, jsonb, integer), public.heartbeat_attempt(uuid, bigint, uuid, integer), public.reap_expired_attempts(timestamptz), public.publish_attempt(uuid, bigint, uuid), public.write_candidates(uuid, bigint, uuid, jsonb, jsonb) to service_role;

commit;
