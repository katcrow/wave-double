-- Story 5.14: 원천별 tracking read model 조회.
-- 기존 1-인자 RPC는 호환성을 위해 그대로 두고, 2-인자 overload만 추가한다.
-- source는 candidate_source_contrib의 primary source 귀속 결과만 사용하며,
-- 브라우저는 restricted view/table을 직접 SELECT하지 않는다.
begin;

create or replace function public.get_outcome_metric_comparison(
  p_strategy text,
  p_source text
)
returns jsonb
language sql
security definer
stable
set search_path = pg_catalog, public
as $$
  with normalized as (
    select
      case
        when p_strategy in ('A', 'B', 'C', 'D', 'E', 'F') then p_strategy
        else null
      end as strategy_filter,
      case
        when p_source in ('t1859', 't1852', 't1856') then p_source
        else null
      end as source_filter
  ),
  resolved as (
    select co.strategy, co.status, co.return_pct, src.source
    from public.candidate_outcome co
    left join lateral (
      select lr.canonical_success_run_id, lr.trading_day
      from public.logical_runs lr
      where lr.batch_kind = 'close'
        and lr.trading_day = co.entry_date
        and lr.canonical_success_run_id is not null
    ) run on true
    left join lateral (
      select cl.candidate_id, cl.attempt_run_id
      from public.candidates cl
      where cl.trading_day = run.trading_day
        and cl.ticker = co.ticker
        and cl.attempt_run_id = run.canonical_success_run_id
    ) cand on true
    left join lateral (
      select cs.source
      from public.candidate_source_contrib cs
      where cs.candidate_id = cand.candidate_id
        and cs.attempt_run_id = cand.attempt_run_id
      order by cs.contribution_weight desc,
        case cs.source when 't1859' then 0 when 't1852' then 1 else 2 end
      limit 1
    ) src on true
  ),
  scoped as (
    select r.*
    from resolved r
    cross join normalized n
    where n.source_filter is null or r.source = n.source_filter
  ),
  base as (
    select
      strategy,
      count(*) filter (where status in ('TP', 'SL', 'TIMEOUT')) as total_settled,
      count(*) filter (where status in ('TP', 'SL', 'TIMEOUT') and return_pct > 0) as wins,
      count(*) filter (where status in ('TP', 'SL', 'TIMEOUT') and return_pct < 0) as losses,
      count(*) filter (where status = 'OPEN') as open_count,
      count(*) filter (where status = 'SUSPENDED') as suspended_count,
      count(*) filter (where status = 'DELISTED') as delisted_count,
      sum(return_pct) filter (where status in ('TP', 'SL', 'TIMEOUT') and return_pct > 0) as gross_win,
      abs(sum(return_pct) filter (where status in ('TP', 'SL', 'TIMEOUT') and return_pct < 0)) as gross_loss
    from scoped
    group by rollup(strategy)
  ),
  expected as (
    select * from (values
      ('A', 0.6871::numeric, 2.0540::numeric),
      ('B', 0.6895::numeric, 2.0770::numeric),
      ('C', 0.6600::numeric, 1.8159::numeric)
    ) as e(strategy, expected_win_rate, expected_profit_factor)
  ),
  ci as (
    select
      b.*,
      case when b.total_settled >= 30 then round(b.wins::numeric / nullif(b.total_settled, 0), 4) end as win_rate,
      case when b.total_settled >= 30 then round(b.gross_win / nullif(b.gross_loss, 0), 4) end as profit_factor,
      30 as sample_gate_min_required,
      (b.total_settled >= 30) as sample_gate_passed,
      case when b.total_settled < 30 then '표본 부족 (' || b.total_settled || '/30)' end as sample_gate_label,
      case when b.total_settled >= 30 then
        1.959963985 / (1 + (1.959963985 ^ 2) / b.total_settled)
      end as z_denom_factor,
      case when b.total_settled >= 30 then
        (round(b.wins::numeric / nullif(b.total_settled, 0), 4) + (1.959963985 ^ 2) / (2 * b.total_settled))
          / (1 + (1.959963985 ^ 2) / b.total_settled)
      end as center,
      case when b.total_settled >= 30 then
        sqrt(
          ((round(b.wins::numeric / nullif(b.total_settled, 0), 4)
            * (1 - round(b.wins::numeric / nullif(b.total_settled, 0), 4)))
            + (1.959963985 ^ 2) / (4 * b.total_settled))
          / b.total_settled
        )
      end as spread,
      e.expected_win_rate,
      e.expected_profit_factor
    from base b
    left join expected e on e.strategy = b.strategy
  ),
  threshold_values as (
    select
      c.*,
      case when c.sample_gate_passed then round(c.center - c.z_denom_factor * c.spread, 4) end as ci_lower,
      case when c.sample_gate_passed then round(c.center + c.z_denom_factor * c.spread, 4) end as ci_upper
    from ci c
  ),
  timeout_counts as (
    select strategy, count(*) filter (where status = 'TIMEOUT')::integer as timeout_count
    from scoped
    group by rollup(strategy)
  ),
  output_rows as (
    select
      t.strategy,
      t.total_settled,
      t.wins,
      t.losses,
      t.open_count,
      t.suspended_count,
      t.delisted_count,
      t.gross_win,
      t.gross_loss,
      t.win_rate,
      t.profit_factor,
      t.sample_gate_min_required,
      t.sample_gate_passed,
      t.sample_gate_label,
      case when t.sample_gate_passed then t.ci_lower end as ci_lower,
      case when t.sample_gate_passed then t.ci_upper end as ci_upper,
      case when t.sample_gate_passed then t.expected_win_rate end as expected_win_rate,
      case when t.sample_gate_passed and t.expected_win_rate is not null then
        t.expected_win_rate between t.ci_lower and t.ci_upper
      end as expected_in_ci,
      case when t.sample_gate_passed then t.expected_profit_factor end as expected_profit_factor,
      case when t.sample_gate_passed and t.expected_win_rate is not null then 0.10::numeric end as win_rate_threshold_pp,
      case when t.sample_gate_passed and t.expected_profit_factor is not null then 0.25::numeric end as profit_factor_threshold_ratio,
      case when t.sample_gate_passed and t.expected_win_rate is not null and t.win_rate is not null
        then abs(t.win_rate - t.expected_win_rate) > 0.10
      end as win_rate_threshold_breached,
      case when t.sample_gate_passed and t.expected_profit_factor is not null and t.profit_factor is not null
        then abs(t.profit_factor - t.expected_profit_factor) / t.expected_profit_factor > 0.25
      end as profit_factor_threshold_breached,
      coalesce(tc.timeout_count, 0)::integer as timeout_count,
      case when t.strategy in ('A', 'B', 'C') then 30 end as cutoff_bias_sample_size,
      case t.strategy when 'B' then 0.0037::numeric when 'A' then 0.0000::numeric when 'C' then 0.0000::numeric end as cutoff_bias_timeout_rate,
      case t.strategy when 'B' then 0.0125::numeric when 'A' then 0.0000::numeric when 'C' then 0.0000::numeric end as cutoff_bias_profit_factor_delta,
      case t.strategy when 'B' then 'TIMEOUT 0.37% / PF차 +0.0125' when 'A' then 'TIMEOUT 0% / PF차 ±0' when 'C' then 'TIMEOUT 0% / PF차 ±0' end as cutoff_bias_label
    from threshold_values t
    left join timeout_counts tc on tc.strategy is not distinct from t.strategy
  ),
  final_rows as (
    select
      o.*,
      case when o.win_rate_threshold_breached or o.profit_factor_threshold_breached then true
        when o.win_rate_threshold_breached is null and o.profit_factor_threshold_breached is null then null
        else false
      end as threshold_warning
    from output_rows o
    cross join normalized n
    where n.strategy_filter is null or o.strategy = n.strategy_filter
  )
  select coalesce(
    jsonb_agg(to_jsonb(rows) order by rows.strategy is not null, rows.strategy),
    '[]'::jsonb
  )
  from final_rows rows;
$$;

comment on function public.get_outcome_metric_comparison(text, text) is
  'Story 5.14: 5.10 canonical metric 산식을 보존한 원천별 metric comparison RPC. p_source가 t1859/t1852/t1856이면 candidate_source_contrib의 primary source 귀속 행만 사용하고, NULL 또는 허용되지 않은 값이면 전체 원천을 통합한다. 기존 1-인자 overload와 row shape를 유지한다.';

create or replace function public.get_bias_diagnostic(
  p_trading_day date,
  p_source text
)
returns jsonb
language plpgsql
security definer
stable
set search_path = pg_catalog, public
as $$
declare
  v_event_id uuid;
  v_source text;
  v_row record;
begin
  if p_trading_day is null then
    raise exception using errcode = '22004', message = 'BIAS_TRADING_DAY_REQUIRED';
  end if;

  v_source := case when p_source in ('t1859', 't1852', 't1856') then p_source end;
  if v_source is null then
    return public.get_bias_diagnostic(p_trading_day);
  end if;

  select e.bias_event_id
    into v_event_id
  from public.bias_events_canonical e
  where e.trading_day = p_trading_day;

  if not found then
    return jsonb_build_object(
      'trading_day', p_trading_day,
      'has_data', false,
      'candidate_population_signal_count', null,
      'backtest_universe_signal_count', null,
      'intersection_count', null,
      'missed_opportunity_count', null
    );
  end if;

  -- 전체 RPC의 fail-closed 검증을 먼저 통과시켜 부분 event/잘못된 meta를
  -- source 선택으로 우회하지 못하게 한다.
  perform public.get_bias_diagnostic(p_trading_day);

  select
    s.candidate_pop_signal_count,
    s.backtest_universe_signal_count,
    s.intersection_count,
    s.missed_opportunity_count
    into v_row
  from public.bias_event_by_source s
  where s.bias_event_id = v_event_id
    and s.source = v_source;

  if not found then
    raise exception using errcode = 'P0001', message = 'BIAS_EVENT_INTEGRITY_ERROR';
  end if;

  return jsonb_build_object(
    'trading_day', p_trading_day,
    'has_data', true,
    'candidate_population_signal_count', v_row.candidate_pop_signal_count,
    'backtest_universe_signal_count', v_row.backtest_universe_signal_count,
    'intersection_count', v_row.intersection_count,
    'missed_opportunity_count', v_row.missed_opportunity_count
  );
end;
$$;

comment on function public.get_bias_diagnostic(date, text) is
  'Story 5.14: 5.13 전체 bias RPC의 검증 경계를 보존하면서 유효한 p_source의 canonical source 행을 반환한다. NULL 또는 허용되지 않은 source는 전체 원천 통합으로 정규화하며, source별 missed_opportunity_count를 전체 산식에 합산하지 않는다.';

revoke execute on function public.get_outcome_metric_comparison(text, text) from public, anon;
grant execute on function public.get_outcome_metric_comparison(text, text) to authenticated, service_role;
revoke execute on function public.get_bias_diagnostic(date, text) from public, anon;
grant execute on function public.get_bias_diagnostic(date, text) to authenticated, service_role;

revoke select on table
  public.candidate_outcome_win_rate_pf_by_strategy_source
from public, anon, authenticated;

commit;
