-- Story 5.14 원천별 tracking RPC 계약 fixture. 모든 변경은 rollback으로 되돌린다.
begin;

-- Remove only a previous interrupted copy of this fixture before inserting the
-- deterministic identifiers. This remains safely scoped and is rolled back.
delete from public.candidate_source_contrib
where candidate_id in (
  '50000000-0000-0000-0000-000000000011',
  '50000000-0000-0000-0000-000000000012',
  '50000000-0000-0000-0000-000000000013'
);
delete from public.candidate_outcome
where ticker in ('S14A', 'S14B', 'S14C', 'S14N')
  and entry_date in (date '2099-10-01', date '2099-10-10');
delete from public.candidates
where candidate_id in (
  '50000000-0000-0000-0000-000000000011',
  '50000000-0000-0000-0000-000000000012',
  '50000000-0000-0000-0000-000000000013'
);
delete from public.bias_event_by_source
where bias_event_id in (
  select bias_event_id from public.bias_events where trading_day = date '2099-10-10'
);
delete from public.bias_events where trading_day = date '2099-10-10';
delete from public.runs where run_id = '50000000-0000-0000-0000-000000000001';
delete from public.logical_runs where logical_run_key in ('close:2099-10-01', 'close:2099-10-10');

insert into public.logical_runs(logical_run_key, trading_day, batch_kind)
values
  ('close:2099-10-01', date '2099-10-01', 'close'),
  ('close:2099-10-10', date '2099-10-10', 'close');

insert into public.runs(run_id, logical_run_key, attempt_no, fence_token, lease_expires_at, trigger, status)
values
  ('50000000-0000-0000-0000-000000000001', 'close:2099-10-01', 1, 1, now() + interval '1 hour', 'schedule', 'published');

update public.logical_runs
set canonical_success_run_id = '50000000-0000-0000-0000-000000000001'
where logical_run_key = 'close:2099-10-01';

insert into public.candidates(candidate_id, attempt_run_id, ticker, trading_day, trading_value)
values
  ('50000000-0000-0000-0000-000000000011', '50000000-0000-0000-0000-000000000001', 'S14A', date '2099-10-01', 1000),
  ('50000000-0000-0000-0000-000000000012', '50000000-0000-0000-0000-000000000001', 'S14B', date '2099-10-01', 1000),
  ('50000000-0000-0000-0000-000000000013', '50000000-0000-0000-0000-000000000001', 'S14C', date '2099-10-01', 1000);

insert into public.candidate_source_contrib(candidate_id, attempt_run_id, source, contribution_weight)
values
  ('50000000-0000-0000-0000-000000000011', '50000000-0000-0000-0000-000000000001', 't1859', 1),
  ('50000000-0000-0000-0000-000000000012', '50000000-0000-0000-0000-000000000001', 't1852', 1),
  ('50000000-0000-0000-0000-000000000013', '50000000-0000-0000-0000-000000000001', 't1856', 1);

insert into public.candidate_outcome(
  ticker, strategy, entry_date, entry_price, status, exit_date, exit_price, return_pct,
  cutoff_n, holding_days, tp_pct, sl_pct
)
values
  ('S14A', 'A', date '2099-10-01', 100, 'TP', date '2099-10-03', 102, 2, 30, 2, 3, 3),
  ('S14B', 'A', date '2099-10-01', 100, 'SL', date '2099-10-03', 99, -1, 30, 2, 3, 3),
  ('S14C', 'B', date '2099-10-01', 100, 'TIMEOUT', date '2099-10-31', 101, 1, 30, 30, 3, 3),
  ('S14N', 'D', date '2099-10-01', 100, 'TIMEOUT', date '2099-10-31', 101, 1, 20, 20, 3, 5);

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
  v_source_name text;
  v_metric_row jsonb;
  v_bias_row jsonb;
  v_expected_keys text[] := array[
    'ci_lower','ci_upper','cutoff_bias_label','cutoff_bias_profit_factor_delta',
    'cutoff_bias_sample_size','cutoff_bias_timeout_rate','delisted_count','expected_in_ci',
    'expected_profit_factor','expected_win_rate','gross_loss','gross_win','losses','open_count',
    'profit_factor','profit_factor_threshold_breached','profit_factor_threshold_ratio',
    'sample_gate_label','sample_gate_min_required','sample_gate_passed','strategy',
    'suspended_count','threshold_warning','timeout_count','total_settled','win_rate',
    'win_rate_threshold_breached','win_rate_threshold_pp','wins'
  ];
  v_expected_bias_keys text[] := array[
    'backtest_universe_signal_count','candidate_population_signal_count','has_data',
    'intersection_count','missed_opportunity_count','trading_day'
  ];
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
  if (select array_agg(key order by key) from jsonb_object_keys(v_full) key) <> v_expected_bias_keys then
    raise exception 'full bias row shape mismatch: %', v_full;
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
  foreach v_source_name in array array['t1859', 't1852', 't1856'] loop
    v := public.get_bias_diagnostic(date '2099-10-10', v_source_name);
    if (select array_agg(key order by key) from jsonb_object_keys(v) key) <> v_expected_bias_keys then
      raise exception 'bias % row shape mismatch: %', v_source_name, v;
    end if;
  end loop;
  v := public.get_bias_diagnostic(date '2099-10-10', 't1859');
  if (v->>'candidate_population_signal_count')::integer <> 5
    or (v->>'intersection_count')::integer <> 3
    or (v->>'missed_opportunity_count')::integer <> 8 then
    raise exception 't1859 source bias row mismatch: %', v;
  end if;
  v := public.get_bias_diagnostic(date '2099-10-10', 't1856');
  if (v->>'candidate_population_signal_count')::integer <> 1
    or (v->>'intersection_count')::integer <> 0
    or (v->>'missed_opportunity_count')::integer <> 9 then
    raise exception 't1856 source bias row mismatch: %', v;
  end if;

  v_full := public.get_outcome_metric_comparison(null, null);
  if jsonb_array_length(v_full) <> 4
    or (v_full->0->>'total_settled')::integer <> 4
    or (v_full->0->>'wins')::integer <> 3
    or (v_full->0->>'open_count')::integer <> 0 then
    raise exception 'metric full scope mismatch: %', v_full;
  end if;
  for v_metric_row in select value from jsonb_array_elements(v_full) loop
    if (select array_agg(key order by key) from jsonb_object_keys(v_metric_row) key) <> v_expected_keys then
      raise exception 'metric full row shape mismatch: %', v_metric_row;
    end if;
    if (v_metric_row->>'sample_gate_passed')::boolean
       and (v_metric_row->'win_rate_threshold_pp' is distinct from '0.1'::jsonb
         or v_metric_row->'profit_factor_threshold_ratio' is distinct from '0.25'::jsonb) then
      raise exception 'gated metric threshold constants mismatch: %', v_metric_row;
    end if;
    if not (v_metric_row->>'sample_gate_passed')::boolean
       and (v_metric_row->'win_rate_threshold_pp' is distinct from 'null'::jsonb
         or v_metric_row->'profit_factor_threshold_ratio' is distinct from 'null'::jsonb) then
      raise exception 'below-gate metric threshold constants must be NULL: %', v_metric_row;
    end if;
  end loop;
  foreach v_source_name in array array['t1859', 't1852', 't1856'] loop
    v_source := public.get_outcome_metric_comparison(null, v_source_name);
    if jsonb_array_length(v_source) <> 2 then
      raise exception 'metric % row shape mismatch: %', v_source_name, v_source;
    end if;
    if (v_source->0->>'open_count')::integer <> 0 then
      raise exception 'metric % must exclude NULL-provenance outcome rows: %', v_source_name, v_source;
    end if;
    for v_metric_row in select value from jsonb_array_elements(v_source) loop
      if (select array_agg(key order by key) from jsonb_object_keys(v_metric_row) key) <> v_expected_keys then
        raise exception 'metric % row shape mismatch: %', v_source_name, v_metric_row;
      end if;
      if (v_metric_row->>'sample_gate_passed')::boolean
         and (v_metric_row->'win_rate_threshold_pp' is distinct from '0.1'::jsonb
           or v_metric_row->'profit_factor_threshold_ratio' is distinct from '0.25'::jsonb) then
        raise exception 'metric % gated threshold constants mismatch: %', v_source_name, v_metric_row;
      end if;
      if not (v_metric_row->>'sample_gate_passed')::boolean
         and (v_metric_row->'win_rate_threshold_pp' is distinct from 'null'::jsonb
           or v_metric_row->'profit_factor_threshold_ratio' is distinct from 'null'::jsonb) then
        raise exception 'metric % below-gate threshold constants must be NULL: %', v_source_name, v_metric_row;
      end if;
    end loop;
  end loop;
  v_source := public.get_outcome_metric_comparison(null, 't1852');
  if (v_source->0->>'total_settled')::integer <> 1
    or (v_source->0->>'wins')::integer <> 0
    or (v_source->0->>'open_count')::integer <> 0
    or v_source->0->>'strategy' is not null
    or (v_source->1->>'strategy') is distinct from 'A' then
    raise exception 'metric source scope mismatch: full=% source=%', v_full, v_source;
  end if;
  if (v_full->0->>'total_settled')::integer = (v_source->0->>'total_settled')::integer then
    raise exception 'full metric must include NULL-provenance and all primary source partitions';
  end if;
  if public.get_outcome_metric_comparison(null, 'invalid') is distinct from v_full then
    raise exception 'invalid source must normalize to full metric result';
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
  if has_function_privilege('anon', 'public.get_outcome_metric_comparison(text,text)'::regprocedure, 'EXECUTE') then
    raise exception 'anon must not execute source metric RPC';
  end if;
  if not has_function_privilege('authenticated', 'public.get_outcome_metric_comparison(text,text)'::regprocedure, 'EXECUTE') then
    raise exception 'authenticated must execute source metric RPC';
  end if;
  if has_function_privilege('anon', 'public.get_bias_diagnostic(date,text)'::regprocedure, 'EXECUTE') then
    raise exception 'anon must not execute source bias RPC';
  end if;
  if not has_function_privilege('authenticated', 'public.get_bias_diagnostic(date,text)'::regprocedure, 'EXECUTE') then
    raise exception 'authenticated must execute source bias RPC';
  end if;
  if not exists (
    select 1 from pg_proc p
    join pg_namespace n on n.oid = p.pronamespace
    where n.nspname = 'public'
      and p.proname = 'get_outcome_metric_comparison'
      and p.pronargs = 2
      and p.prosecdef
      and p.proconfig @> array['search_path=pg_catalog, public']::text[]
  ) then
    raise exception 'source metric RPC catalog contract failed';
  end if;
  if not exists (
    select 1 from pg_proc p
    join pg_namespace n on n.oid = p.pronamespace
    where n.nspname = 'public'
      and p.proname = 'get_bias_diagnostic'
      and p.pronargs = 2
      and p.prosecdef
      and p.proconfig @> array['search_path=pg_catalog, public']::text[]
  ) then
    raise exception 'source bias RPC must be SECURITY DEFINER with fixed search_path';
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
  v := public.get_outcome_metric_comparison(null, 't1856');
  if jsonb_array_length(v) <> 2 then
    raise exception 'authenticated source metric RPC failed: %', v;
  end if;
end $$;
reset role;

set local role anon;
do $$
declare
  v_caught boolean := false;
  v_name text;
begin
  foreach v_name in array array['candidate_outcome_win_rate_pf_threshold_gated', 'candidate_outcome_win_rate_pf_by_strategy_source', 'bias_event_by_source'] loop
    v_caught := false;
    begin
      execute format('select 1 from public.%I limit 1', v_name);
    exception when others then
      v_caught := true;
    end;
    if not v_caught then raise exception 'anon direct SELECT should be denied: %', v_name; end if;
  end loop;
  begin
    perform public.get_bias_diagnostic(date '2099-10-10', 't1856');
  exception when others then
    v_caught := true;
  end;
  if not v_caught then raise exception 'anon source RPC call should be denied'; end if;
  v_caught := false;
  begin
    perform public.get_outcome_metric_comparison(null, 't1856');
  exception when others then
    v_caught := true;
  end;
  if not v_caught then raise exception 'anon source metric RPC call should be denied'; end if;
end $$;
reset role;

select 'PASS'::text as story_5_14_verification;
rollback;
