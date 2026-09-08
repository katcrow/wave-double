-- Story 4.8: published complete snapshot에 귀속된 시장 전체 수급 read RPC.
-- market_supply를 브라우저에 직접 노출하지 않고, p_run_id의 현재 complete attempt와
-- 해당 trading_day의 KOSPI/KOSDAQ 행만 반환한다.
begin;

create or replace function public.get_market_supply(p_run_id uuid)
returns jsonb
language sql
security definer
stable
set search_path = pg_catalog, public
as $$
  with published_complete_attempt as (
    select r.run_id, l.trading_day
    from public.runs r
    join public.logical_runs l on l.logical_run_key = r.logical_run_key
    where r.run_id = p_run_id
      and r.status = 'published'
      and l.current_complete_run_id = r.run_id
      and r.stage_status->>'market_supply' = 'success'
  )
  select coalesce(
    jsonb_agg(
      jsonb_build_object(
        'market', ms.market,
        'trading_day', ms.trading_day,
        'foreign_net', ms.foreign_net,
        'institution_net', ms.institution_net,
        'individual_net', ms.individual_net,
        'program_net', ms.program_net,
        'collected_at', ms.collected_at
      )
      order by case ms.market when 'KOSPI' then 0 when 'KOSDAQ' then 1 else 2 end
    ),
    '[]'::jsonb
  )
  from public.market_supply ms
  join published_complete_attempt p
    on p.run_id = ms.attempt_run_id
   and p.trading_day = ms.trading_day
  where ms.market in ('KOSPI', 'KOSDAQ');
$$;

comment on function public.get_market_supply(uuid) is
  'Story 4.8: published complete snapshot의 current_complete_run_id와 market_supply stage가 성공한 attempt에서 해당 trading_day의 KOSPI/KOSDAQ 수급만 반환한다. market_supply 직접 조회 대신 사용한다.';

revoke execute on function public.get_market_supply(uuid) from public, anon, authenticated;
grant execute on function public.get_market_supply(uuid) to anon, authenticated, service_role;

commit;
