-- Story 5.13: 거래일별 최신 canonical bias event를 인증된 read-only RPC로 노출한다.
-- 브라우저는 bias 원장/뷰를 직접 읽지 않고 이 고정 JSON 계약만 소비한다.
begin;

create or replace function public.get_bias_diagnostic(
  p_trading_day date
)
returns jsonb
language sql
security definer
stable
set search_path = pg_catalog, public
as $$
  with canonical as (
    select e.bias_event_id, e.trading_day, e.calculation_meta
    from public.bias_events_canonical e
    where e.trading_day = p_trading_day
    limit 1
  ),
  source_totals as (
    select
      coalesce(sum(s.candidate_pop_signal_count), 0)::integer as candidate_population_signal_count,
      coalesce(max(s.backtest_universe_signal_count), 0)::integer as backtest_universe_signal_count,
      coalesce(sum(s.intersection_count), 0)::integer as intersection_count,
      coalesce(sum(greatest(s.backtest_universe_signal_count - s.intersection_count, 0)), 0)::integer
        as universe_only_missed_count
    from public.bias_event_by_source_canonical s
    join canonical c on c.bias_event_id = s.bias_event_id
  ),
  truncated_totals as (
    select coalesce(sum(
      case
        when jsonb_typeof(item.value -> 'truncated_only_missed_count') = 'number'
          and item.value ->> 'truncated_only_missed_count' ~ '^[0-9]+$'
          and (item.value ->> 'truncated_only_missed_count')::numeric between 0 and 2147483647
        then (item.value ->> 'truncated_only_missed_count')::integer
        else 0
      end
    ), 0)::integer as truncated_only_missed_count
    from canonical c
    left join lateral jsonb_each(
      case when jsonb_typeof(c.calculation_meta -> 'by_source') = 'object'
        then c.calculation_meta -> 'by_source' else '{}'::jsonb end
    ) item on true
  )
  select coalesce(
    (
      select jsonb_build_object(
        'trading_day', c.trading_day,
        'has_data', true,
        'candidate_population_signal_count', t.candidate_population_signal_count,
        'backtest_universe_signal_count', t.backtest_universe_signal_count,
        'intersection_count', t.intersection_count,
        'missed_opportunity_count', t.universe_only_missed_count + x.truncated_only_missed_count
      )
      from canonical c
      cross join source_totals t
      cross join truncated_totals x
    ),
    jsonb_build_object(
      'trading_day', p_trading_day,
      'has_data', false,
      'candidate_population_signal_count', null,
      'backtest_universe_signal_count', null,
      'intersection_count', null,
      'missed_opportunity_count', null
    )
  );
$$;

comment on function public.get_bias_diagnostic(date) is
  'Story 5.13: 선택 거래일의 최신 canonical bias event에서 A-F 시그널 합집합 모집단 4개 지표를 반환한다. source별 missed를 합산하지 않고 유니버스 전용분과 calculation_meta.by_source의 절단 보정분으로 전체 기회 누락을 산출하며, 데이터가 없으면 count를 null로 반환한다.';

revoke execute on function public.get_bias_diagnostic(date) from public, anon;
grant execute on function public.get_bias_diagnostic(date) to authenticated, service_role;

revoke select on table
  public.bias_events,
  public.bias_event_by_source,
  public.bias_events_canonical,
  public.bias_event_by_source_canonical
from public, anon, authenticated;

commit;
