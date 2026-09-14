-- Story 5.12: cutoff-bias canonical view를 인증된 metric comparison RPC로 노출한다.
-- 브라우저는 restricted view를 직접 읽지 않고, 이 함수가 반환하는 고정 JSON row만 소비한다.
begin;

create or replace function public.get_outcome_metric_comparison(
  p_strategy text default null
)
returns jsonb
language sql
security definer
stable
set search_path = pg_catalog, public
as $$
  with normalized as (
    select case
      when p_strategy in ('A', 'B', 'C', 'D', 'E', 'F') then p_strategy
      else null
    end as strategy_filter
  )
  select coalesce(
    jsonb_agg(to_jsonb(rows) order by rows.strategy is not null, rows.strategy),
    '[]'::jsonb
  )
  from (
    select v.*
    from public.candidate_outcome_cutoff_bias_notice v
    cross join normalized n
    where n.strategy_filter is null or v.strategy = n.strategy_filter
  ) rows;
$$;

comment on function public.get_outcome_metric_comparison(text) is
  'Story 5.12: candidate_outcome_cutoff_bias_notice의 전체 rollup 및 A-F 전략별 metric row를 인증 사용자에게만 반환한다. p_strategy가 A-F이면 해당 전략만 반환하고, NULL 또는 허용되지 않은 값이면 전체를 반환한다. 브라우저는 restricted view를 직접 SELECT하지 않는다.';

revoke select on table public.candidate_outcome_cutoff_bias_notice from public, anon, authenticated;
revoke execute on function public.get_outcome_metric_comparison(text) from public, anon;
grant execute on function public.get_outcome_metric_comparison(text) to authenticated, service_role;

commit;
