-- Story 5.13: 거래일별 최신 canonical bias event를 인증된 read-only RPC로 노출한다.
-- 브라우저는 bias 원장/뷰를 직접 읽지 않고 이 고정 JSON 계약만 소비한다.
begin;

create or replace function public.get_bias_diagnostic(
  p_trading_day date
)
returns jsonb
language plpgsql
security definer
stable
set search_path = pg_catalog, public
as $$
declare
  v_event_id uuid;
  v_event_trading_day date;
  v_calculation_meta jsonb;
  v_expected_sources text[] := array['t1859', 't1852', 't1856'];
  v_source_count bigint;
  v_distinct_source_count bigint;
  v_candidate_population_signal_count bigint;
  v_backtest_universe_signal_count bigint;
  v_intersection_count bigint;
  v_truncated_only_missed_count bigint;
begin
  if p_trading_day is null then
    raise exception using errcode = '22004', message = 'BIAS_TRADING_DAY_REQUIRED';
  end if;

  select e.bias_event_id, e.trading_day, e.calculation_meta
    into v_event_id, v_event_trading_day, v_calculation_meta
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

  select count(*), count(distinct s.source),
      sum(s.candidate_pop_signal_count),
      max(s.backtest_universe_signal_count),
      sum(s.intersection_count)
    into v_source_count, v_distinct_source_count,
      v_candidate_population_signal_count,
      v_backtest_universe_signal_count,
      v_intersection_count
  from public.bias_event_by_source s
  where s.bias_event_id = v_event_id;

  if v_source_count <> 3 or v_distinct_source_count <> 3
    or exists (
      select 1 from public.bias_event_by_source s
      where s.bias_event_id = v_event_id and s.source <> all (v_expected_sources)
    )
    or exists (
      select 1 from unnest(v_expected_sources) expected(source)
      where not exists (
        select 1 from public.bias_event_by_source s
        where s.bias_event_id = v_event_id and s.source = expected.source
      )
    ) then
    raise exception using errcode = 'P0001', message = 'BIAS_EVENT_INTEGRITY_ERROR';
  end if;

  if jsonb_typeof(v_calculation_meta -> 'by_source') is distinct from 'object'
    or (select count(*) from jsonb_object_keys(v_calculation_meta -> 'by_source')) <> 3
    or exists (
      select 1 from jsonb_object_keys(v_calculation_meta -> 'by_source') key
      where key <> all (v_expected_sources)
    )
    or exists (
      select 1 from unnest(v_expected_sources) expected(source)
      where not (v_calculation_meta -> 'by_source' ? expected.source)
    )
    or exists (
      select 1
      from jsonb_each(v_calculation_meta -> 'by_source') item
      where jsonb_typeof(item.value) is distinct from 'object'
        or case
          when jsonb_typeof(item.value -> 'truncated_only_missed_count') = 'number'
            and item.value ->> 'truncated_only_missed_count' ~ '^(0|[1-9][0-9]*)$'
          then (item.value ->> 'truncated_only_missed_count')::numeric between 0 and 2147483647
          else false
        end is not true
    ) then
    raise exception using errcode = 'P0001', message = 'BIAS_EVENT_INTEGRITY_ERROR';
  end if;

  select sum((item.value ->> 'truncated_only_missed_count')::bigint)
    into v_truncated_only_missed_count
  from jsonb_each(v_calculation_meta -> 'by_source') item;

  if v_backtest_universe_signal_count - v_intersection_count + v_truncated_only_missed_count < 0 then
    raise exception using errcode = 'P0001', message = 'BIAS_EVENT_INTEGRITY_ERROR';
  end if;

  return jsonb_build_object(
    'trading_day', v_event_trading_day,
    'has_data', true,
    'candidate_population_signal_count', v_candidate_population_signal_count,
    'backtest_universe_signal_count', v_backtest_universe_signal_count,
    'intersection_count', v_intersection_count,
    'missed_opportunity_count',
      v_backtest_universe_signal_count - v_intersection_count + v_truncated_only_missed_count
  );
end;
$$;

comment on function public.get_bias_diagnostic(date) is
  'Story 5.13: 선택 거래일의 최신 canonical bias event에서 A-F 시그널 합집합 모집단 4개 지표를 반환한다. 전체 기회 누락은 전역 max(backtest_universe_signal_count) - sum(intersection_count) + calculation_meta.by_source의 절단 보정분으로 산출하며, source 3행 또는 메타 경계가 깨지면 BIAS_EVENT_INTEGRITY_ERROR로 격리하고 데이터가 없으면 count를 null로 반환한다.';

revoke execute on function public.get_bias_diagnostic(date) from public, anon;
grant execute on function public.get_bias_diagnostic(date) to authenticated, service_role;

revoke select on table
  public.bias_events,
  public.bias_event_by_source,
  public.bias_events_canonical,
  public.bias_event_by_source_canonical
from public, anon, authenticated;

commit;
