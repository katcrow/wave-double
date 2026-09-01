-- Stories 1.3-1.5 hardening: forward-only repair of lineage, result, and write guards.
begin;

alter table public.runs add column if not exists stage_results jsonb not null default '{}'::jsonb;

create or replace function public.start_attempt(
  p_logical_run_key text, p_trading_day date, p_batch_kind text, p_trigger text,
  p_lease_seconds integer default 300
) returns jsonb language plpgsql security definer set search_path = public as $$
declare logical_row public.logical_runs; new_run public.runs; next_attempt integer; next_fence bigint;
begin
  if p_lease_seconds <= 0 then raise exception using message = 'lease_seconds must be positive'; end if;
  if p_batch_kind not in ('premarket','intraday','close') or p_trigger not in ('schedule','manual') then raise exception using message = 'invalid batch kind or trigger'; end if;
  if (p_batch_kind = 'intraday' and p_logical_run_key !~ '^intraday:[0-9]{4}-[0-9]{2}-[0-9]{2}:([01][0-9]|2[0-3]):(00|30)$')
     or (p_batch_kind in ('premarket','close') and p_logical_run_key !~ ('^' || p_batch_kind || ':[0-9]{4}-[0-9]{2}-[0-9]{2}$')) then raise exception using message = 'invalid logical run key'; end if;
  if split_part(p_logical_run_key, ':', 2)::date <> p_trading_day then raise exception using message = 'LOGICAL_KEY_ARGUMENT_MISMATCH'; end if;
  insert into logical_runs(logical_run_key, trading_day, batch_kind) values (p_logical_run_key, p_trading_day, p_batch_kind) on conflict (logical_run_key) do nothing;
  select * into logical_row from logical_runs where logical_run_key = p_logical_run_key for update;
  if logical_row.trading_day <> p_trading_day or logical_row.batch_kind <> p_batch_kind then raise exception using message = 'LOGICAL_KEY_ARGUMENT_MISMATCH'; end if;
  if logical_row.canonical_success_run_id is not null then return jsonb_build_object('replayed', true, 'run_id', logical_row.canonical_success_run_id, 'logical_run_key', p_logical_run_key); end if;
  if logical_row.active_attempt_run_id is not null then update runs set status = 'superseded', finished_at = now() where run_id = logical_row.active_attempt_run_id and status in ('running', 'ready_to_publish'); end if;
  select coalesce(max(attempt_no), 0) + 1, coalesce(max(fence_token), 0) + 1 into next_attempt, next_fence from runs where logical_run_key = p_logical_run_key;
  insert into runs(logical_run_key, attempt_no, fence_token, lease_expires_at, trigger, status) values (p_logical_run_key, next_attempt, next_fence, now() + make_interval(secs => p_lease_seconds), p_trigger, 'running') returning * into new_run;
  update logical_runs set active_attempt_run_id = new_run.run_id where logical_run_key = p_logical_run_key;
  return jsonb_build_object('run_id', new_run.run_id, 'logical_run_key', new_run.logical_run_key, 'attempt_no', new_run.attempt_no, 'fence_token', new_run.fence_token, 'lease_token', new_run.lease_token, 'lease_expires_at', new_run.lease_expires_at);
end $$;

create or replace function public.write_stage(
  p_run_id uuid, p_stage text, p_fence_token bigint, p_lease_token uuid, p_expected_status text,
  p_status text, p_result jsonb default '{}'::jsonb, p_unprocessed_count integer default 0
) returns jsonb language plpgsql security definer set search_path = public as $$
declare r public.runs; current_status text;
begin
  if p_stage not in ('candidates','tags','supply_3day','market_supply','outcome_tracking') or p_status not in ('pending','running','success','failed','partial') or jsonb_typeof(p_result) <> 'object' then raise exception using message = 'invalid stage, status, or result'; end if;
  select * into r from runs where run_id = p_run_id for update;
  if not found then raise exception using message = 'RUN_NOT_FOUND'; end if;
  if r.status = 'published' or r.fence_token <> p_fence_token or r.lease_token <> p_lease_token or r.lease_expires_at <= now() or (r.status <> 'running' and not (r.stage_status->>p_stage = p_expected_status and p_expected_status = p_status and p_status in ('success','failed','partial'))) then raise exception using message = 'STALE_FENCE_OR_LEASE'; end if;
  current_status := r.stage_status->>p_stage;
  if current_status <> p_expected_status then raise exception using message = 'EXPECTED_STATUS_MISMATCH'; end if;
  if not ((p_expected_status = 'pending' and p_status = 'running') or (p_expected_status = 'running' and p_status in ('success','failed','partial')) or (p_expected_status = p_status and p_status in ('success','failed','partial'))) then raise exception using message = 'INVALID_STAGE_TRANSITION'; end if;
  update runs set stage_status = jsonb_set(stage_status, array[p_stage], to_jsonb(p_status)), stage_results = jsonb_set(stage_results, array[p_stage], p_result), unprocessed_count = greatest(unprocessed_count, p_unprocessed_count), status = case when p_stage = 'candidates' and p_status = 'success' then 'ready_to_publish' when p_stage = 'candidates' and p_status = 'partial' then 'partial' when p_stage = 'candidates' and p_status = 'failed' then 'failed' else status end, finished_at = case when p_status in ('success','failed','partial') and p_stage = 'candidates' then now() else finished_at end where run_id = p_run_id returning * into r;
  if r.status = 'partial' then update logical_runs set latest_partial_run_id = r.run_id where logical_run_key = r.logical_run_key; end if;
  return jsonb_build_object('run_id', r.run_id, 'stage', p_stage, 'status', r.status, 'stage_status', r.stage_status, 'stage_result', r.stage_results->p_stage);
end $$;

create or replace function public.write_candidates(p_run_id uuid, p_fence_token bigint, p_lease_token uuid, p_candidates jsonb, p_metadata jsonb)
returns jsonb language plpgsql security definer set search_path = public as $$
declare r public.runs; item jsonb; candidate_count integer := 0; candidate_day date;
begin
  if jsonb_typeof(p_candidates) <> 'array' or jsonb_typeof(p_metadata) <> 'object' then raise exception using message = 'INVALID_CANDIDATE_PAYLOAD'; end if;
  select * into r from runs where run_id = p_run_id for update;
  if not found then raise exception using message = 'RUN_NOT_FOUND'; end if;
  if r.status <> 'running' or r.fence_token <> p_fence_token or r.lease_token <> p_lease_token or r.lease_expires_at <= now() then raise exception using message = 'STALE_FENCE_OR_LEASE'; end if;
  if coalesce((p_metadata->>'candidate_count')::integer, -1) <> jsonb_array_length(p_candidates) or coalesce((p_metadata->>'candidate_count')::integer, -1) > 150 or coalesce((p_metadata->>'original_count')::integer, -1) < coalesce((p_metadata->>'candidate_count')::integer, 0) + coalesce((p_metadata->>'excluded_count')::integer, 0) + coalesce((p_metadata->>'truncated_count')::integer, 0) then raise exception using message = 'INVALID_CANDIDATE_METADATA'; end if;
  select trading_day into candidate_day from logical_runs where logical_run_key = r.logical_run_key;
  for item in select value from jsonb_array_elements(p_candidates) loop
    if (item->>'candidate_id') is null or (item->>'ticker') is null or length(btrim(item->>'ticker')) = 0 or (item->>'trading_value') is null or (item->>'trading_value')::numeric in ('NaN'::numeric, 'Infinity'::numeric, '-Infinity'::numeric) or coalesce((item->>'truncated')::boolean, false) then raise exception using message = 'INVALID_CANDIDATE_PAYLOAD'; end if;
    insert into candidates(candidate_id, attempt_run_id, ticker, name, trading_day, trading_value, truncated) values ((item->>'candidate_id')::uuid, p_run_id, btrim(item->>'ticker'), nullif(btrim(item->>'name'), ''), candidate_day, (item->>'trading_value')::numeric, false) on conflict (candidate_id, attempt_run_id) do nothing;
    insert into candidate_source_contrib(candidate_id, attempt_run_id, source, contribution_weight) values ((item->>'candidate_id')::uuid, p_run_id, 't1859', 1.0) on conflict (candidate_id, attempt_run_id, source) do update set contribution_weight = excluded.contribution_weight;
    candidate_count := candidate_count + 1;
  end loop;
  update runs set selection_input_hash = p_metadata->>'selection_input_hash', original_count = (p_metadata->>'original_count')::integer, excluded_count = (p_metadata->>'excluded_count')::integer, truncated_count = (p_metadata->>'truncated_count')::integer where run_id = p_run_id;
  return jsonb_build_object('run_id', p_run_id, 'candidate_count', candidate_count);
exception when invalid_text_representation or numeric_value_out_of_range then raise exception using message = 'INVALID_CANDIDATE_PAYLOAD';
end $$;

create or replace function public.publish_attempt(p_run_id uuid, p_fence_token bigint, p_lease_token uuid) returns jsonb language plpgsql security definer set search_path = public as $$
declare r public.runs; logical_row public.logical_runs;
begin
  select * into r from runs where run_id = p_run_id; if not found then raise exception using message = 'RUN_NOT_FOUND'; end if;
  perform pg_advisory_xact_lock(hashtextextended(r.logical_run_key, 0));
  select * into r from runs where run_id = p_run_id for update; select * into logical_row from logical_runs where logical_run_key = r.logical_run_key for update;
  if logical_row.active_attempt_run_id is distinct from p_run_id or r.fence_token <> p_fence_token or r.lease_token <> p_lease_token or r.lease_expires_at <= now() then raise exception using message = 'STALE_FENCE_OR_LEASE'; end if;
  if r.status <> 'ready_to_publish' or r.stage_status->>'candidates' <> 'success' then raise exception using message = 'PUBLISH_GUARD_FAILED'; end if;
  if exists (select 1 from candidates c where c.attempt_run_id = p_run_id and not exists (select 1 from candidate_source_contrib s where s.candidate_id = c.candidate_id and s.attempt_run_id = c.attempt_run_id)) or exists (select 1 from (select candidate_id, attempt_run_id, sum(contribution_weight) as total from candidate_source_contrib where attempt_run_id = p_run_id group by candidate_id, attempt_run_id) s where s.total <> 1) then raise exception using message = 'PUBLISH_PROVENANCE_GUARD_FAILED'; end if;
  if logical_row.canonical_success_run_id is not null then raise exception using message = 'CANONICAL_ALREADY_PUBLISHED'; end if;
  update runs set status = 'published', finished_at = now() where run_id = p_run_id;
  update logical_runs set active_attempt_run_id = null, current_complete_run_id = p_run_id, canonical_success_run_id = case when batch_kind = 'close' then p_run_id else null end, published_at = now() where logical_run_key = r.logical_run_key;
  return jsonb_build_object('run_id', p_run_id, 'status', 'published', 'canonical_success_run_id', case when logical_row.batch_kind = 'close' then p_run_id else null end);
end $$;

revoke execute on function public.start_attempt(text, date, text, text, integer) from public;
revoke execute on function public.write_stage(uuid, text, bigint, uuid, text, text, jsonb, integer) from public;
revoke execute on function public.heartbeat_attempt(uuid, bigint, uuid, integer) from public;
revoke execute on function public.reap_expired_attempts(timestamptz) from public;
revoke execute on function public.publish_attempt(uuid, bigint) from public;
revoke execute on function public.publish_attempt(uuid, bigint, uuid) from public;
revoke execute on function public.write_candidates(uuid, bigint, uuid, jsonb, jsonb) from public;
grant execute on function public.start_attempt(text, date, text, text, integer), public.write_stage(uuid, text, bigint, uuid, text, text, jsonb, integer), public.heartbeat_attempt(uuid, bigint, uuid, integer), public.reap_expired_attempts(timestamptz), public.publish_attempt(uuid, bigint, uuid), public.write_candidates(uuid, bigint, uuid, jsonb, jsonb) to service_role;

commit;
