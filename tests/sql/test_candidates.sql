-- Story 1.5 SQL fixture. 후보 hardening migration까지 적용한다.
begin;
do $$
declare key text := 'close:2099-02-01'; started jsonb; run_id uuid; fence bigint; lease uuid; candidate uuid := gen_random_uuid();
begin
  started := public.start_attempt(key, date '2099-02-01', 'close', 'manual', 300);
  run_id := (started->>'run_id')::uuid; fence := (started->>'fence_token')::bigint; lease := (started->>'lease_token')::uuid;
  perform public.write_stage(run_id, 'candidates', fence, lease, 'pending', 'running');
  perform public.write_candidates(run_id, fence, lease, jsonb_build_array(jsonb_build_object('candidate_id', candidate, 'ticker', '005930', 'name', '삼성전자', 'trading_value', 100, 'sources', jsonb_build_array(jsonb_build_object('source', 't1859', 'weight', 1)))), jsonb_build_object('selection_input_hash', repeat('a', 64), 'original_count', 1, 'candidate_count', 1, 'excluded_count', 0, 'truncated_count', 0));
  if (select count(*) from public.candidate_source_contrib where attempt_run_id = run_id) <> 1 then raise exception 'contribution missing'; end if;
  if (select count(*) from public.candidates where attempt_run_id = run_id and truncated) <> 0 then raise exception 'truncated candidates must not be persisted'; end if;
  if (select sum(contribution_weight) from public.candidate_source_contrib where attempt_run_id = run_id) <> 1 then raise exception 'weight mismatch'; end if;
  if exists (select 1 from information_schema.columns where table_schema = 'public' and table_name = 'candidates' and column_name = 'source') then raise exception 'candidates.source must not exist'; end if;
  if not (select c.relrowsecurity from pg_class c join pg_namespace n on n.oid = c.relnamespace where n.nspname = 'public' and c.relname = 'candidates') then raise exception 'candidates RLS must be enabled'; end if;
  if not (select c.relrowsecurity from pg_class c join pg_namespace n on n.oid = c.relnamespace where n.nspname = 'public' and c.relname = 'candidate_source_contrib') then raise exception 'candidate_source_contrib RLS must be enabled'; end if;
  perform public.write_stage(run_id, 'candidates', fence, lease, 'running', 'success');
end $$;
rollback;
