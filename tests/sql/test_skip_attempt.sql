-- Supabase SQL fixture for Story 1.7.
-- 실행 전 lineage/candidates migration, hardening migration들, 202609012300 skip_attempt migration을 적용한다.
-- psql 또는 CI의 local Supabase DB에서 실행하며, 실패 시 DO 블록이 예외를 낸다.
begin;

do $$
 declare key text := 'close:2099-02-01'; started jsonb; attempt_id uuid; fence bigint; lease uuid; before_stage_status jsonb;
begin
  started := public.start_attempt(key, date '2099-02-01', 'close', 'schedule', 300);
  attempt_id := (started->>'run_id')::uuid; fence := (started->>'fence_token')::bigint; lease := (started->>'lease_token')::uuid;
  before_stage_status := (select stage_status from public.runs where run_id = attempt_id);
  perform public.skip_attempt(attempt_id, fence, lease, 'holiday');
  if (select status from public.runs where run_id = attempt_id) <> 'skipped' then raise exception 'status was not set to skipped'; end if;
  if (select skip_reason from public.runs where run_id = attempt_id) <> 'holiday' then raise exception 'skip_reason was not recorded'; end if;
  if (select finished_at from public.runs where run_id = attempt_id) is null then raise exception 'finished_at was not set'; end if;
  if (select stage_status from public.runs where run_id = attempt_id) <> before_stage_status then raise exception 'stage_status was mutated by skip_attempt'; end if;
end $$;

do $$
declare key text := 'close:2099-02-02'; started jsonb; attempt_id uuid; fence bigint; lease uuid; caught boolean := false;
begin
  started := public.start_attempt(key, date '2099-02-02', 'close', 'schedule', 300);
  attempt_id := (started->>'run_id')::uuid; fence := (started->>'fence_token')::bigint; lease := (started->>'lease_token')::uuid;
  begin
    perform public.skip_attempt(attempt_id, fence + 1, lease, 'holiday');
  exception when others then caught := true;
  end;
  if not caught then raise exception 'wrong fence was accepted by skip_attempt'; end if;
  if (select status from public.runs where run_id = attempt_id) <> 'running' then raise exception 'stale fence write changed status'; end if;
end $$;

do $$
declare key text := 'close:2099-02-03'; started jsonb; attempt_id uuid; fence bigint; lease uuid; caught boolean := false;
begin
  started := public.start_attempt(key, date '2099-02-03', 'close', 'schedule', 300);
  attempt_id := (started->>'run_id')::uuid; fence := (started->>'fence_token')::bigint; lease := (started->>'lease_token')::uuid;
  begin
    perform public.skip_attempt(attempt_id, fence, lease, '');
  exception when others then caught := true;
  end;
  if not caught then raise exception 'empty skip_reason was accepted'; end if;
end $$;

do $$
declare key text := 'close:2099-02-04'; started jsonb; attempt_id uuid; fence bigint; lease uuid; caught boolean := false;
begin
  started := public.start_attempt(key, date '2099-02-04', 'close', 'schedule', 300);
  attempt_id := (started->>'run_id')::uuid; fence := (started->>'fence_token')::bigint; lease := (started->>'lease_token')::uuid;
  perform public.skip_attempt(attempt_id, fence, lease, 'holiday');
  begin
    perform public.skip_attempt(attempt_id, fence, lease, 'holiday');
  exception when others then caught := true;
  end;
  if not caught then raise exception 'skip_attempt was accepted on an already-terminal run'; end if;
end $$;

rollback;
