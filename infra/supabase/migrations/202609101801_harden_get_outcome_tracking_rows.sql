-- Story 5.11 review patch: 이미 적용된 202609101800 함수는 forward-only로 보강한다.
-- ticker 검색어의 ILIKE wildcard가 데이터 필터 의미를 바꾸지 않도록 SQL 경계에서도
-- backslash, percent, underscore를 escape한다. 적용 migration은 수정하지 않는다.
begin;

create or replace function public.get_outcome_tracking_rows(
  p_status text default null,
  p_strategy text default null,
  p_ticker text default null,
  p_limit integer default 500
)
returns jsonb
language sql
security definer
stable
set search_path = pg_catalog, public
as $$
  with normalized as (
    select
      case when p_status in ('TP', 'SL', 'TIMEOUT', 'OPEN', 'SUSPENDED', 'DELISTED') then p_status end as status,
      case when p_strategy in ('A', 'B', 'C', 'D', 'E', 'F') then p_strategy end as strategy,
      nullif(replace(replace(replace(btrim(p_ticker), E'\\', E'\\\\'), '%', E'\\%'), '_', E'\\_'), '') as ticker,
      least(greatest(coalesce(p_limit, 500), 1), 500) as row_limit
  )
  select coalesce(
    jsonb_agg(to_jsonb(rows) order by rows.entry_date desc, rows.outcome_id desc),
    '[]'::jsonb
  )
  from (
    select
      co.outcome_id,
      co.ticker,
      co.strategy,
      co.entry_date,
      co.status,
      co.exit_date,
      co.return_pct
    from public.candidate_outcome co
    cross join normalized n
    where (n.status is null or co.status = n.status)
      and (n.strategy is null or co.strategy = n.strategy)
      and (n.ticker is null or co.ticker ilike '%' || n.ticker || '%' escape E'\\')
    order by co.entry_date desc, co.outcome_id desc
    limit (select row_limit from normalized)
  ) rows;
$$;

comment on function public.get_outcome_tracking_rows(text, text, text, integer) is
  'Story 5.11 review patch: 인증된 read-only outcome tracking 행을 반환한다. ticker ILIKE wildcard를 SQL 경계에서 escape하고, 허용 상태·전략 필터와 최대 500건·안정 정렬을 유지한다.';

revoke select on table public.candidate_outcome from public, anon, authenticated;
revoke execute on function public.get_outcome_tracking_rows(text, text, text, integer) from public, anon;
grant execute on function public.get_outcome_tracking_rows(text, text, text, integer) to authenticated, service_role;

commit;
