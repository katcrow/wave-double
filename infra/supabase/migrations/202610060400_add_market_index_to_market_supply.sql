-- 시장 전체 수급 패널에 지수 등락률과 상승/보합/하락 종목수(t1511 업종현재가)를 더한다.
-- 지수 조회는 보조 정보라 실패해도 수급 행은 저장되므로 새 컬럼은 모두 nullable이다.
-- 기존 행은 null로 남고, get_market_supply는 새 필드를 함께 반환한다.
begin;

alter table public.market_supply
  add column if not exists index_price numeric check (
    index_price is null or (
      index_price <> 'NaN'::numeric and index_price <> 'Infinity'::numeric and index_price <> '-Infinity'::numeric
    )
  ),
  add column if not exists index_change_rate numeric check (
    index_change_rate is null or (
      index_change_rate <> 'NaN'::numeric and index_change_rate <> 'Infinity'::numeric and index_change_rate <> '-Infinity'::numeric
    )
  ),
  add column if not exists advancing_count integer check (advancing_count is null or advancing_count >= 0),
  add column if not exists unchanged_count integer check (unchanged_count is null or unchanged_count >= 0),
  add column if not exists declining_count integer check (declining_count is null or declining_count >= 0);

comment on column public.market_supply.index_price is 't1511 pricejisu 현재 지수(KOSPI 001, KOSDAQ 301).';
comment on column public.market_supply.index_change_rate is 't1511 diffjisu 지수 등락률(%, 부호 포함).';
comment on column public.market_supply.advancing_count is 't1511 highjo + upjo 상승 종목수(상한 포함).';
comment on column public.market_supply.unchanged_count is 't1511 unchgjo 보합 종목수.';
comment on column public.market_supply.declining_count is 't1511 lowjo + downjo 하락 종목수(하한 포함).';

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
        'index_price', ms.index_price,
        'index_change_rate', ms.index_change_rate,
        'advancing_count', ms.advancing_count,
        'unchanged_count', ms.unchanged_count,
        'declining_count', ms.declining_count,
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
  'published complete snapshot의 current_complete_run_id와 market_supply stage가 성공한 attempt에서 해당 trading_day의 KOSPI/KOSDAQ 수급과 지수 등락(t1511, nullable)을 반환한다. market_supply 직접 조회 대신 사용한다.';

revoke execute on function public.get_market_supply(uuid) from public, anon, authenticated;
grant execute on function public.get_market_supply(uuid) to anon, authenticated, service_role;

commit;
