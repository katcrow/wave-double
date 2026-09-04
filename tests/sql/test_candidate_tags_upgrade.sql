-- Supabase SQL fixture for Story 6.3 N/N-1 upgrade compatibility.
-- CI runs this after the full migration set. It temporarily recreates the N-1
-- CHECK, commits legacy rows, then applies the exact Story 6.3 migration file.
-- The database is disposable in CI; production verification uses an equivalent
-- transaction-scoped SQL assertion through Supabase MCP.

begin;

alter table public.candidate_tags
  drop constraint candidate_tags_strategy_check;
alter table public.candidate_tags
  add constraint candidate_tags_strategy_check
  check (strategy in ('A', 'B', 'C'));

do $$
declare
  started jsonb;
  run_id uuid;
  fence bigint;
  lease uuid;
  candidate_id uuid := gen_random_uuid();
begin
  started := public.start_attempt('close:2099-08-01', date '2099-08-01', 'close', 'manual', 300);
  run_id := (started->>'run_id')::uuid;
  fence := (started->>'fence_token')::bigint;
  lease := (started->>'lease_token')::uuid;
  perform public.write_stage(run_id, 'candidates', fence, lease, 'pending', 'running');
  perform public.write_candidates(
    run_id, fence, lease,
    jsonb_build_array(jsonb_build_object(
      'candidate_id', candidate_id, 'ticker', '000060', 'name', '업그레이드테스트', 'trading_value', 100,
      'sources', jsonb_build_array(jsonb_build_object('source', 't1859', 'weight', 1)))),
    jsonb_build_object('selection_input_hash', repeat('u', 64), 'original_count', 1, 'candidate_count', 1,
      'excluded_count', 0, 'truncated_count', 0));
  perform public.write_stage(run_id, 'candidates', fence, lease, 'running', 'success');
  insert into public.candidate_tags(candidate_id, attempt_run_id, strategy, signal_date)
    values
      (candidate_id, run_id, 'A', date '2099-08-01'),
      (candidate_id, run_id, 'B', date '2099-08-01'),
      (candidate_id, run_id, 'C', date '2099-08-01');
end $$;

commit;

\ir ../../infra/supabase/migrations/202609051400_expand_candidate_tags_strategy_check.sql

begin;

do $$
declare
  run_id uuid;
  candidate_id uuid;
begin
  select ct.attempt_run_id, ct.candidate_id
    into run_id, candidate_id
    from public.candidate_tags ct
   where ct.signal_date = date '2099-08-01'
   group by ct.attempt_run_id, ct.candidate_id;

  if (select count(*) from public.candidate_tags where attempt_run_id = run_id) <> 3 then
    raise exception 'legacy A/B/C candidate_tags rows were not preserved';
  end if;
  if (select count(*) from public.candidate_tags where attempt_run_id = run_id and status = 'active') <> 3 then
    raise exception 'legacy candidate_tags defaults were not preserved';
  end if;

  insert into public.candidate_tags(candidate_id, attempt_run_id, strategy, signal_date)
    values (candidate_id, run_id, 'D', date '2099-08-01'), (candidate_id, run_id, 'E', date '2099-08-01');
  if (select count(*) from public.candidate_tags where attempt_run_id = run_id) <> 5 then
    raise exception 'D/E tags were not accepted after upgrade';
  end if;
end $$;

select jsonb_build_object('status', 'PASS', 'fixture', 'test_candidate_tags_upgrade', 'legacy_rows_preserved', 3,
  'new_strategies_accepted', jsonb_build_array('D', 'E')) as verification;

rollback;
