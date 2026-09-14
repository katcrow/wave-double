-- Story 5.14 원천별 tracking RPC 계약 fixture. 모든 변경은 rollback으로 되돌린다.
begin;

insert into public.logical_runs(logical_run_key, trading_day, batch_kind)
values
  ('close:2099-10-01', date '2099-10-01', 'close'),
  ('close:2099-10-10', date '2099-10-10', 'close')
on conflict (logical_run_key) do nothing;

insert into public.runs(run_id, logical_run_key, attempt_no, fence_token, lease_expires_at, trigger, status)
values
  ('50000000-0000-0000-0000-000000000001', 'close:2099-10-01', 1, 1, now() + interval '1 hour', 'schedule', 'published')
on conflict (run_id) do nothing;

update public.logical_runs
set canonical_success_run_id = '50000000-0000-0000-0000-000000000001'
where logical_run_key = 'close:2099-10-01';

delete from public.candidate_outcome;

insert into public.candidates(candidate_id, attempt_run_id, ticker, trading_day, trading_value)
values
  ('50000000-0000-0000-0000-000000000011', '50000000-0000-0000-0000-000000000001', 'S14A', date '2099-10-01', 1000),
  ('50000000-0000-0000-0000-000000000012', '50000000-0000-0000-0000-000000000001', 'S14B', date '2099-10-01', 1000),
  ('50000000-0000-0000-0000-000000000013', '50000000-0000-0000-0000-000000000001', 'S14C', date '2099-10-01', 1000)
on conflict (candidate_id, attempt_run_id) do nothing;

insert into public.candidate_source_contrib(candidate_id, attempt_run_id, source, contribution_weight)
values
  ('50000000-0000-0000-0000-000000000011', '50000000-0000-0000-0000-000000000001', 't1859', 1),
  ('50000000-0000-0000-0000-000000000012', '50000000-0000-0000-0000-000000000001', 't1852', 1),
  ('50000000-0000-0000-0000-000000000013', '50000000-0000-0000-0000-000000000001', 't1856', 1)
on conflict (candidate_id, attempt_run_id, source) do nothing;

insert into public.candidate_outcome(
  ticker, strategy, entry_date, entry_price, status, exit_date, exit_price, return_pct,
  cutoff_n, holding_days, tp_pct, sl_pct
)
values
  ('S14A', 'A', date '2099-10-01', 100, 'TP', date '2099-10-03', 102, 2, 30, 2, 3, 3),
  ('S14B', 'A', date '2099-10-01', 100, 'SL', date '2099-10-03', 99, -1, 30, 2, 3, 3),
  ('S14C', 'B', date '2099-10-01', 100, 'TIMEOUT', date '2099-10-31', 101, 1, 30, 30, 3, 3),
  ('S14N', 'D', date '2099-10-01', 100, 'OPEN', null, null, null, 20, 0, 3, 5);

insert into public.bias_events(trading_day, logical_run_key, calculation_meta)
values (
  date '2099-10-10',
  'close:2099-10-10',
  '{"by_source":{"t1859":{"truncated_only_missed_count":2},"t1852":{"truncated_only_missed_count":1},"t1856":{"truncated_only_missed_count":0}}}'::jsonb
);

do $$
declare
  v_event uuid;
  v jsonb;
  v_full jsonb;
  v_source jsonb;
begin
  select bias_event_id into v_event
  from public.bias_events
  where trading_day = date '2099-10-10';

  insert into public.bias_event_by_source(
    bias_event_id, source, candidate_pop_signal_count, backtest_universe_signal_count,
    intersection_count, diff_count, missed_opportunity_count
  ) values
    (v_event, 't1859', 5, 9, 3, 2, 8),
    (v_event, 't1852', 2, 9, 1, 1, 8),
    (v_event, 't1856', 1, 9, 0, 1, 9);

  v_full := public.get_bias_diagnostic(date '2099-10-10', null);
  if v_full->>'has_data' <> 'true'
    or (v_full->>'candidate_population_signal_count')::integer <> 8
    or (v_full->>'backtest_universe_signal_count')::integer <> 9
    or (v_full->>'intersection_count')::integer <> 4
    or (v_full->>'missed_opportunity_count')::integer <> 8 then
    raise exception 'full bias must retain 5.13 aggregate: %', v_full;
  end if;

  v := public.get_bias_diagnostic(date '2099-10-10', 't1852');
  if v->>'has_data' <> 'true'
    or (v->>'candidate_population_signal_count')::integer <> 2
    or (v->>'backtest_universe_signal_count')::integer <> 9
    or (v->>'intersection_count')::integer <> 1
    or (v->>'missed_opportunity_count')::integer <> 8 then
    raise exception 'source bias row mismatch: %', v;
  end if;
  if public.get_bias_diagnostic(date '2099-10-10', 'invalid') is distinct from v_full then
    raise exception 'invalid source must normalize to full bias result';
  end if;
  if v->'missed_opportunity_count' = '25'::jsonb then
    raise exception 'source bias must not sum source missed rows';
  end if;

  v_full := public.get_outcome_metric_comparison(null, null);
  v_source := public.get_outcome_metric_comparison(null, 't1852');
  if jsonb_array_length(v_full) <> 4 or jsonb_array_length(v_source) <> 2 then
    raise exception 'metric full/source row count mismatch: full=% source=%', v_full, v_source;
  end if;
  if (v_full->0->>'total_settled')::integer <> 3
    or (v_full->0->>'open_count')::integer <> 1
    or (v_source->0->>'total_settled')::integer <> 1
    or (v_source->0->>'wins')::integer <> 0
    or v_source->0->>'strategy' is not null then
    raise exception 'metric source scope mismatch: full=% source=%', v_full, v_source;
  end if;
  if public.get_outcome_metric_comparison(null, 'invalid') is distinct from v_full then
    raise exception 'invalid source must normalize to full metric result';
  end if;
  if (v_full->0->>'total_settled')::integer = (v_source->0->>'total_settled')::integer then
    raise exception 'full metric must include all primary source partitions';
  end if;
  raise notice 'story 5-14 source/full parity, source attribution, and no-double-count assertions: pass';
end $$;

do $$
declare
  v_name text;
begin
  foreach v_name in array array['candidate_outcome_cutoff_bias_notice', 'candidate_outcome_win_rate_pf_by_strategy_source', 'bias_events', 'bias_event_by_source', 'bias_events_canonical', 'bias_event_by_source_canonical'] loop
    if has_table_privilege('anon', 'public.' || v_name, 'SELECT')
      or has_table_privilege('authenticated', 'public.' || v_name, 'SELECT') then
      raise exception 'restricted object must deny browser SELECT: %', v_name;
    end if;
  end loop;
  foreach v_name in array array['public.get_outcome_metric_comparison(text,text)', 'public.get_bias_diagnostic(date,text)'] loop
    if has_function_privilege('anon', v_name::regprocedure, 'EXECUTE') then
      raise exception 'anon must not execute source RPC: %', v_name;
    end if;
    if not has_function_privilege('authenticated', v_name::regprocedure, 'EXECUTE') then
      raise exception 'authenticated must execute source RPC: %', v_name;
    end if;
  end loop;
  if not exists (
    select 1 from pg_proc p
    join pg_namespace n on n.oid = p.pronamespace
    where n.nspname = 'public'
      and p.proname in ('get_outcome_metric_comparison', 'get_bias_diagnostic')
      and p.pronargs = 2
      and p.prosecdef
      and p.proconfig @> array['search_path=pg_catalog, public']::text[]
  ) then
    raise exception 'source RPCs must be SECURITY DEFINER with fixed search_path';
  end if;
end $$;

set local role authenticated;
do $$
declare
  v jsonb;
begin
  v := public.get_bias_diagnostic(date '2099-10-10', 't1856');
  if (v->>'candidate_population_signal_count')::integer <> 1 then
    raise exception 'authenticated source bias RPC failed: %', v;
  end if;
end $$;
reset role;

set local role anon;
do $$
declare
  v_caught boolean := false;
begin
  begin
    perform public.get_bias_diagnostic(date '2099-10-10', 't1856');
  exception when others then
    v_caught := true;
  end;
  if not v_caught then raise exception 'anon source RPC call should be denied'; end if;
end $$;
reset role;

select 'PASS'::text as story_5_14_verification;
rollback;
