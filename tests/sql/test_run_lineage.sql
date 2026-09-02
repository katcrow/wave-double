-- Supabase SQL fixture for Story 1.3.
-- 실행 전 lineage/candidates migration과 202609012100 hardening migration을 적용한다.
-- psql 또는 CI의 local Supabase DB에서 실행하며, 실패 시 DO 블록이 예외를 낸다.
begin;

do $$
 declare key text := 'close:2099-01-02'; started jsonb; attempt_id uuid; fence bigint; lease uuid; caught boolean := false;
begin
  started := public.start_attempt(key, date '2099-01-02', 'close', 'manual', 300);
   attempt_id := (started->>'run_id')::uuid; fence := (started->>'fence_token')::bigint; lease := (started->>'lease_token')::uuid;
   if (select jsonb_object_keys(stage_status) from public.runs where runs.run_id = attempt_id order by 1 limit 1) is null then
    raise exception 'stage registry is empty';
  end if;
   if (select count(*) from jsonb_object_keys((select stage_status from public.runs where runs.run_id = attempt_id))) <> 5 then
    raise exception 'expected five initial stages';
  end if;
   perform public.write_stage(attempt_id, 'candidates', fence, lease, 'pending', 'running');
   perform public.write_stage(attempt_id, 'candidates', fence, lease, 'running', 'success');
   if (select status from public.runs where runs.run_id = attempt_id) <> 'ready_to_publish' then raise exception 'not ready'; end if;
   -- Story 2.5: publish_attempt는 tags stage success도 게이트로 요구한다.
   perform public.write_stage(attempt_id, 'tags', fence, lease, 'pending', 'running');
   perform public.write_stage(attempt_id, 'tags', fence, lease, 'running', 'success');
  perform public.publish_attempt(attempt_id, fence, lease);
   if (select canonical_success_run_id from public.logical_runs where logical_run_key = key) <> attempt_id then raise exception 'close canonical pointer missing'; end if;
   if (select status from public.runs where runs.run_id = attempt_id) <> 'published' then raise exception 'not published'; end if;
  begin
     perform public.write_stage(attempt_id, 'candidates', fence, lease, 'success', 'success');
  exception when others then caught := true;
  end;
  if not caught then raise exception 'published attempt accepted stage rewrite'; end if;
end $$;

do $$
 declare key text := 'intraday:2099-01-02:14:30'; started jsonb; attempt_id uuid; fence bigint; lease uuid; caught boolean := false;
begin
  started := public.start_attempt(key, date '2099-01-02', 'intraday', 'schedule', 300);
   attempt_id := (started->>'run_id')::uuid; fence := (started->>'fence_token')::bigint; lease := (started->>'lease_token')::uuid;
   perform public.write_stage(attempt_id, 'candidates', fence, lease, 'pending', 'running');
   perform public.write_stage(attempt_id, 'candidates', fence, lease, 'running', 'partial', '{}'::jsonb, 1);
   if (select status from public.runs where runs.run_id = attempt_id) <> 'partial' then raise exception 'partial status missing'; end if;
   if (select latest_partial_run_id from public.logical_runs where logical_run_key = key) <> attempt_id then raise exception 'latest partial pointer missing'; end if;
  if exists (select 1 from public.logical_runs where logical_run_key = key and current_complete_run_id is not null) then raise exception 'partial changed complete pointer'; end if;
  caught := false;
  begin
     perform public.publish_attempt(attempt_id, fence, lease);
  exception when others then caught := true;
  end;
  if not caught then raise exception 'partial attempt was published'; end if;
end $$;

do $$
declare key text := 'close:2099-01-03'; first_run uuid; second_run uuid; first_fence bigint; first_lease uuid; started jsonb; caught boolean := false;
begin
  started := public.start_attempt(key, date '2099-01-03', 'close', 'schedule', 300);
  first_run := (started->>'run_id')::uuid; first_fence := (started->>'fence_token')::bigint; first_lease := (started->>'lease_token')::uuid;
  started := public.start_attempt(key, date '2099-01-03', 'close', 'manual', 300);
  second_run := (started->>'run_id')::uuid;
  if (select status from public.runs where run_id = first_run) <> 'superseded' then raise exception 'old attempt was not superseded'; end if;
  if (select active_attempt_run_id from public.logical_runs where logical_run_key = key) <> second_run then raise exception 'second attempt did not acquire active fence'; end if;
  begin
    perform public.write_stage(first_run, 'candidates', first_fence, first_lease, 'pending', 'running');
  exception when others then caught := true;
  end;
  if not caught then raise exception 'stale attempt was allowed to write'; end if;
end $$;

do $$
 declare key text := 'close:2099-01-04'; started jsonb; attempt_id uuid; fence bigint; lease uuid;
begin
  started := public.start_attempt(key, date '2099-01-04', 'close', 'manual', 300);
   attempt_id := (started->>'run_id')::uuid; fence := (started->>'fence_token')::bigint; lease := (started->>'lease_token')::uuid;
   perform public.write_stage(attempt_id, 'candidates', fence, lease, 'pending', 'running');
   perform public.write_stage(attempt_id, 'candidates', fence, lease, 'running', 'success');
   update public.runs set status = 'running', lease_expires_at = now() - interval '1 second' where public.runs.run_id = attempt_id;
  perform public.reap_expired_attempts(now());
   if (select status from public.runs where public.runs.run_id = attempt_id) <> 'ready_to_publish' then raise exception 'salvage did not become ready'; end if;
   if (select active_attempt_run_id from public.logical_runs where logical_run_key = key) <> attempt_id then raise exception 'salvage incorrectly cleared active attempt'; end if;
end $$;

do $$
 declare key text := 'close:2099-01-05'; started jsonb; attempt_id uuid; fence bigint; lease uuid; caught boolean := false;
begin
  started := public.start_attempt(key, date '2099-01-05', 'close', 'manual', 300);
   attempt_id := (started->>'run_id')::uuid; fence := (started->>'fence_token')::bigint; lease := (started->>'lease_token')::uuid;
  begin
     perform public.write_stage(attempt_id, 'candidates', fence + 1, lease, 'pending', 'running');
  exception when others then caught := true;
  end;
  if not caught then raise exception 'wrong fence was accepted'; end if;
   if (select stage_status->>'candidates' from public.runs where public.runs.run_id = attempt_id) <> 'pending' then raise exception 'stale write changed stage'; end if;
   update public.runs set lease_expires_at = now() - interval '1 second' where public.runs.run_id = attempt_id;
  caught := false;
  begin
     perform public.heartbeat_attempt(attempt_id, fence, lease, 300);
  exception when others then caught := true;
  end;
  if not caught then raise exception 'expired lease was accepted'; end if;
end $$;

do $$
declare caught boolean := false;
begin
  begin
    perform public.start_attempt('intraday:2099-01-06:14:15', date '2099-01-06', 'intraday', 'manual', 300);
  exception when others then caught := true;
  end;
  if not caught then raise exception 'non-half-hour slot was accepted'; end if;
end $$;

rollback;
