-- Story 5.12 metric comparison RPC 계약 fixture. 모든 변경은 rollback으로 되돌린다.
begin;

-- Canonical view aggregates the whole candidate_outcome table. Isolate the fixture
-- inside this transaction so production rows cannot change the expected strategy rows.
savepoint metric_fixture_isolation;
delete from public.candidate_outcome;

insert into public.candidate_outcome(
  ticker, strategy, entry_date, entry_price, status, exit_date, exit_price, return_pct,
  cutoff_n, holding_days, tp_pct, sl_pct
)
select
  'MCA' || strategy || lpad(gs::text, 3, '0'),
  strategy,
  date '2099-01-01' + gs,
  1000,
  case when gs <= 15 then 'TP' when gs = 30 then 'TIMEOUT' else 'SL' end,
  date '2099-02-01' + gs,
  case when gs <= 15 then 1020 when gs = 30 then 1005 else 980 end,
  case when gs <= 15 then 2 when gs = 30 then 0.5 else -1 end,
  30, 2, 3, 3
from unnest(array['A', 'B', 'D', 'E', 'F']::text[]) as strategies(strategy)
cross join generate_series(1, 30) as series(gs);

insert into public.candidate_outcome(
  ticker, strategy, entry_date, entry_price, status, exit_date, exit_price, return_pct,
  cutoff_n, holding_days, tp_pct, sl_pct
)
select
  'MCC' || lpad(gs::text, 3, '0'), 'C', date '2099-03-01' + gs, 1000,
  case when gs <= 14 then 'TP' else 'SL' end,
  date '2099-04-01' + gs,
  case when gs <= 14 then 1020 else 980 end,
  case when gs <= 14 then 2 else -1 end,
  30, 2, 3, 3
from generate_series(1, 29) as series(gs);

do $$
declare
  all_rows jsonb;
  canonical_rows jsonb;
  canonical_rollup jsonb;
  invalid_rows jsonb;
  canonical_strategy_row jsonb;
  metric_strategy text;
  metric_row jsonb;
  expected_win_rate_text text;
  expected_profit_factor_text text;
  row jsonb;
begin
  if pg_get_function_result('public.get_outcome_metric_comparison(text)'::regprocedure) <> 'jsonb' then
    raise exception 'metric comparison RPC must return jsonb';
  end if;

  all_rows := public.get_outcome_metric_comparison(null);
  select coalesce(jsonb_agg(to_jsonb(v) order by v.strategy is not null, v.strategy), '[]'::jsonb)
    into canonical_rows
    from public.candidate_outcome_cutoff_bias_notice v;
  if all_rows is distinct from canonical_rows then
    raise exception 'metric RPC must pass through canonical view values: % vs %', all_rows, canonical_rows;
  end if;
  if jsonb_array_length(all_rows) < 1 then
    raise exception 'full metric comparison must return the rollup row: %', all_rows;
  end if;
  if all_rows->0->>'strategy' is not null then
    raise exception 'metric rows must be ordered rollup first: %', all_rows;
  end if;
  if exists (
    select 1
    from jsonb_array_elements(all_rows) row
    where (select array_agg(key order by key) from jsonb_object_keys(row) key) <> array[
      'ci_lower','ci_upper','cutoff_bias_label','cutoff_bias_profit_factor_delta',
      'cutoff_bias_sample_size','cutoff_bias_timeout_rate','delisted_count','expected_in_ci',
      'expected_profit_factor','expected_win_rate','gross_loss','gross_win','losses','open_count',
      'profit_factor','profit_factor_threshold_breached','profit_factor_threshold_ratio',
      'sample_gate_label','sample_gate_min_required','sample_gate_passed','strategy',
      'suspended_count','threshold_warning','timeout_count','total_settled','win_rate',
      'win_rate_threshold_breached','win_rate_threshold_pp','wins'
    ]::text[]
    or jsonb_typeof(row->'strategy') not in ('string', 'null')
    or jsonb_typeof(row->'total_settled') <> 'number'
    or jsonb_typeof(row->'sample_gate_passed') <> 'boolean'
  ) then
    raise exception 'metric row shape/type mismatch: %', all_rows;
  end if;

  foreach metric_strategy in array array['A', 'B', 'C', 'D', 'E', 'F'] loop
    metric_row := public.get_outcome_metric_comparison(metric_strategy)->0;
    select to_jsonb(v) into canonical_strategy_row
      from public.candidate_outcome_cutoff_bias_notice v
      where v.strategy = metric_strategy;
    if jsonb_array_length(public.get_outcome_metric_comparison(metric_strategy)) <> 1
       or metric_row is distinct from canonical_strategy_row then
      raise exception '% filter must return exactly its canonical row: % vs %', metric_strategy, metric_row, canonical_strategy_row;
    end if;

    if metric_strategy in ('A', 'B', 'C') then
      expected_win_rate_text := case metric_strategy when 'A' then '0.6871' when 'B' then '0.6895' else '0.6600' end;
      expected_profit_factor_text := case metric_strategy when 'A' then '2.0540' when 'B' then '2.0770' else '1.8159' end;
      if (metric_row->>'sample_gate_passed')::boolean then
        if (metric_row->>'expected_win_rate')::numeric is distinct from expected_win_rate_text::numeric
           or (metric_row->>'expected_profit_factor')::numeric is distinct from expected_profit_factor_text::numeric
           or metric_row->'ci_lower' = 'null'::jsonb
           or metric_row->'ci_upper' = 'null'::jsonb
           or metric_row->>'win_rate_threshold_pp' is distinct from '0.10'
           or metric_row->>'profit_factor_threshold_ratio' is distinct from '0.25' then
          raise exception '% gated expectation/CI/threshold contract failed: %', metric_strategy, metric_row;
        end if;
      else
        if metric_row->'win_rate' <> 'null'::jsonb
           or metric_row->'profit_factor' <> 'null'::jsonb
           or metric_row->'ci_lower' <> 'null'::jsonb
           or metric_row->'ci_upper' <> 'null'::jsonb
           or metric_row->'expected_win_rate' <> 'null'::jsonb
           or metric_row->'expected_profit_factor' <> 'null'::jsonb
           or metric_row->'expected_in_ci' <> 'null'::jsonb
           or metric_row->'win_rate_threshold_pp' <> 'null'::jsonb
           or metric_row->'profit_factor_threshold_ratio' <> 'null'::jsonb
           or metric_row->'win_rate_threshold_breached' <> 'null'::jsonb
           or metric_row->'profit_factor_threshold_breached' <> 'null'::jsonb
           or metric_row->'threshold_warning' <> 'null'::jsonb then
          raise exception '% below-gate fields must be NULL: %', metric_strategy, metric_row;
        end if;
      end if;
      if metric_strategy = 'A' and ((metric_row->>'cutoff_bias_sample_size')::numeric is distinct from 30 or (metric_row->>'cutoff_bias_timeout_rate')::numeric is distinct from 0.0000 or (metric_row->>'cutoff_bias_profit_factor_delta')::numeric is distinct from 0.0000 or metric_row->>'cutoff_bias_label' is distinct from 'TIMEOUT 0% / PF차 ±0') then
        raise exception 'A cutoff baseline mismatch: %', metric_row;
      elsif metric_strategy = 'B' and ((metric_row->>'cutoff_bias_sample_size')::numeric is distinct from 30 or (metric_row->>'cutoff_bias_timeout_rate')::numeric is distinct from 0.0037 or (metric_row->>'cutoff_bias_profit_factor_delta')::numeric is distinct from 0.0125 or metric_row->>'cutoff_bias_label' is distinct from 'TIMEOUT 0.37% / PF차 +0.0125') then
        raise exception 'B cutoff baseline mismatch: %', metric_row;
      elsif metric_strategy = 'C' and ((metric_row->>'cutoff_bias_sample_size')::numeric is distinct from 30 or (metric_row->>'cutoff_bias_timeout_rate')::numeric is distinct from 0.0000 or (metric_row->>'cutoff_bias_profit_factor_delta')::numeric is distinct from 0.0000 or metric_row->>'cutoff_bias_label' is distinct from 'TIMEOUT 0% / PF차 ±0') then
        raise exception 'C cutoff baseline mismatch: %', metric_row;
      end if;
    else
      if metric_row->'expected_win_rate' <> 'null'::jsonb
         or metric_row->'expected_profit_factor' <> 'null'::jsonb
         or metric_row->'expected_in_ci' <> 'null'::jsonb
         or metric_row->'win_rate_threshold_pp' <> 'null'::jsonb
         or metric_row->'profit_factor_threshold_ratio' <> 'null'::jsonb
         or metric_row->'win_rate_threshold_breached' <> 'null'::jsonb
         or metric_row->'profit_factor_threshold_breached' <> 'null'::jsonb
         or metric_row->'threshold_warning' <> 'null'::jsonb
         or metric_row->'cutoff_bias_sample_size' <> 'null'::jsonb
         or metric_row->'cutoff_bias_timeout_rate' <> 'null'::jsonb
         or metric_row->'cutoff_bias_profit_factor_delta' <> 'null'::jsonb
         or metric_row->'cutoff_bias_label' <> 'null'::jsonb then
        raise exception '% must expose no expectation/threshold/cutoff baseline: %', metric_strategy, metric_row;
      end if;
    end if;
    if ((metric_row->>'sample_gate_passed')::boolean and (metric_row->'ci_lower' = 'null'::jsonb or metric_row->'ci_upper' = 'null'::jsonb))
       or (not (metric_row->>'sample_gate_passed')::boolean and (metric_row->'ci_lower' <> 'null'::jsonb or metric_row->'ci_upper' <> 'null'::jsonb)) then
      raise exception '% CI gate contract failed: %', metric_strategy, metric_row;
    end if;
    if jsonb_typeof(metric_row->'timeout_count') <> 'number'
       or (metric_row->>'timeout_count')::numeric < 0
       or (metric_row->>'timeout_count')::numeric <> trunc((metric_row->>'timeout_count')::numeric) then
      raise exception '% TIMEOUT count must be a non-negative integer: %', metric_strategy, metric_row;
    end if;
    if metric_strategy <> 'C' and (metric_row->>'timeout_count')::numeric < 1 then
      raise exception '% fixture TIMEOUT must survive existing-data contamination: %', metric_strategy, metric_row;
    end if;
  end loop;

  select to_jsonb(v) into canonical_rollup from public.candidate_outcome_cutoff_bias_notice v where v.strategy is null;
  if canonical_rollup is null or all_rows->0 is distinct from canonical_rollup then
    raise exception 'rollup metric row must match canonical view';
  end if;
  metric_row := all_rows->0;
  if metric_row->'expected_win_rate' <> 'null'::jsonb
     or metric_row->'expected_profit_factor' <> 'null'::jsonb
     or metric_row->'expected_in_ci' <> 'null'::jsonb
     or metric_row->'win_rate_threshold_pp' <> 'null'::jsonb
     or metric_row->'profit_factor_threshold_ratio' <> 'null'::jsonb
     or metric_row->'win_rate_threshold_breached' <> 'null'::jsonb
     or metric_row->'profit_factor_threshold_breached' <> 'null'::jsonb
     or metric_row->'threshold_warning' <> 'null'::jsonb
     or metric_row->'cutoff_bias_sample_size' <> 'null'::jsonb
     or metric_row->'cutoff_bias_timeout_rate' <> 'null'::jsonb
     or metric_row->'cutoff_bias_profit_factor_delta' <> 'null'::jsonb
     or metric_row->'cutoff_bias_label' <> 'null'::jsonb
     or (metric_row->>'timeout_count')::numeric < 5 then
    raise exception 'rollup expectation/threshold/cutoff/TIMEOUT contract failed: %', metric_row;
  end if;
  if ((metric_row->>'sample_gate_passed')::boolean and (metric_row->'ci_lower' = 'null'::jsonb or metric_row->'ci_upper' = 'null'::jsonb))
     or (not (metric_row->>'sample_gate_passed')::boolean and (metric_row->'ci_lower' <> 'null'::jsonb or metric_row->'ci_upper' <> 'null'::jsonb)) then
    raise exception 'rollup CI gate contract failed: %', metric_row;
  end if;
  invalid_rows := public.get_outcome_metric_comparison('INVALID');
  if invalid_rows is distinct from all_rows then
    raise exception 'invalid strategy must normalize to the full canonical result';
  end if;
  raise notice 'story 5-12 row shape/filter/gate assertions: pass';
end $$;

do $$
declare
  view_name text;
begin
  if has_function_privilege('anon', 'public.get_outcome_metric_comparison(text)'::regprocedure, 'EXECUTE') then
    raise exception 'anon must not execute metric comparison RPC';
  end if;
  if not has_function_privilege('authenticated', 'public.get_outcome_metric_comparison(text)'::regprocedure, 'EXECUTE') then
    raise exception 'authenticated must execute metric comparison RPC';
  end if;
  if not exists (
    select 1 from pg_proc p
    join pg_namespace n on n.oid = p.pronamespace
    where n.nspname = 'public' and p.proname = 'get_outcome_metric_comparison'
      and p.prosecdef and p.proconfig @> array['search_path=pg_catalog, public']::text[]
  ) then
    raise exception 'metric comparison RPC must be SECURITY DEFINER with fixed search_path';
  end if;
  foreach view_name in array array[
    'candidate_outcome_win_rate_pf',
    'candidate_outcome_win_rate_pf_by_strategy_gated',
    'candidate_outcome_win_rate_pf_ci_gated',
    'candidate_outcome_win_rate_pf_threshold_gated',
    'candidate_outcome_cutoff_bias_notice'
  ] loop
    if has_table_privilege('authenticated', 'public.' || view_name, 'SELECT') then
      raise exception 'authenticated must not directly SELECT restricted view %', view_name;
    end if;
  end loop;
end $$;

set local role authenticated;
do $$
declare v jsonb;
begin
  v := public.get_outcome_metric_comparison('D');
  if jsonb_array_length(v) <> 1 or v->0->>'strategy' <> 'D' then
    raise exception 'authenticated RPC execution failed: %', v;
  end if;
end $$;
reset role;

set local role anon;
do $$
declare caught boolean := false;
begin
  begin
    perform public.get_outcome_metric_comparison(null);
  exception when others then caught := true;
  end;
  if not caught then raise exception 'anon direct RPC call should be denied'; end if;
end $$;
reset role;

do $$ begin raise notice 'story 5-12 ACL assertions: pass'; end $$;
select 'PASS'::text as story_5_12_verification;
rollback;
