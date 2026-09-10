-- Story 5.11: 브라우저에 candidate_outcome 원본을 노출하지 않는 인증 read RPC.
-- 상태/전략/ticker 필터를 허용 목록으로 제한하고, 최신 진입일과 outcome_id 순으로
-- 안정 정렬한 뒤 최대 500건만 반환한다. outcome 테이블과 성과 restricted view는
-- browser 역할에서 직접 읽을 수 없게 유지한다.
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
  'Story 5.11: 인증된 read-only outcome tracking 행만 반환한다. candidate_outcome 직접 SELECT 및 성과 restricted view SELECT 대신 사용하며, 허용 상태(TP/SL/TIMEOUT/OPEN/SUSPENDED/DELISTED)·전략(A-F) 필터를 적용하고 entry_date desc, outcome_id desc로 최대 500건을 반환한다. 잘못된 상태·전략 필터는 전체 조회로 정규화한다.';

revoke select on table public.candidate_outcome from public, anon, authenticated;
revoke execute on function public.get_outcome_tracking_rows(text, text, text, integer) from public, anon;
grant execute on function public.get_outcome_tracking_rows(text, text, text, integer) to authenticated, service_role;

commit;
