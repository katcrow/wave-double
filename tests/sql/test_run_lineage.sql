-- Supabase SQL fixture for Story 1.3.
-- 실행 전 202609011600_create_run_lineage.sql을 적용한다.
-- psql 또는 CI의 local Supabase DB에서 실행하며, 실패 시 DO 블록이 예외를 낸다.
begin;

do $$
declare key text := 'close:2099-01-02'; started jsonb; run_id uuid; fence bigint; lease uuid;
begin
  started := public.start_attempt(key, date '2099-01-02', 'close', 'manual', 300);
  run_id := (started->>'run_id')::uuid; fence := (started->>'fence_token')::bigint; lease := (started->>'lease_token')::uuid;
  if (select jsonb_object_keys(stage_status) from public.runs where runs.run_id = run_id order by 1 limit 1) is null then
    raise exception 'stage registry is empty';
  end if;
  if (select count(*) from jsonb_object_keys((select stage_status from public.runs where runs.run_id = run_id))) <> 5 then
    raise exception 'expected five initial stages';
  end if;
  perform public.write_stage(run_id, 'candidates', fence, lease, 'pending', 'running');
  perform public.write_stage(run_id, 'candidates', fence, lease, 'running', 'success');
  if (select status from public.runs where runs.run_id = run_id) <> 'ready_to_publish' then raise exception 'not ready'; end if;
  perform public.publish_attempt(run_id, fence);
  if (select canonical_success_run_id from public.logical_runs where logical_run_key = key) <> run_id then raise exception 'close canonical pointer missing'; end if;
  if (select status from public.runs where runs.run_id = run_id) <> 'published' then raise exception 'not published'; end if;
end $$;

do $$
declare key text := 'intraday:2099-01-02:14:30'; started jsonb; run_id uuid; fence bigint; lease uuid;
begin
  started := public.start_attempt(key, date '2099-01-02', 'intraday', 'schedule', 300);
  run_id := (started->>'run_id')::uuid; fence := (started->>'fence_token')::bigint; lease := (started->>'lease_token')::uuid;
  perform public.write_stage(run_id, 'candidates', fence, lease, 'pending', 'running');
  perform public.write_stage(run_id, 'candidates', fence, lease, 'running', 'partial', '{}'::jsonb, 1);
  if (select status from public.runs where runs.run_id = run_id) <> 'partial' then raise exception 'partial status missing'; end if;
  if (select latest_partial_run_id from public.logical_runs where logical_run_key = key) <> run_id then raise exception 'latest partial pointer missing'; end if;
  if exists (select 1 from public.logical_runs where logical_run_key = key and current_complete_run_id is not null) then raise exception 'partial changed complete pointer'; end if;
end $$;

rollback;
