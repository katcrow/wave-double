-- 시장 전체 수급 패널에 매크로 시세(나스닥100 선물 CME@NQ, 원/달러 USDKRWSMBS; t3521)를 더한다.
-- 시장(KOSPI/KOSDAQ)별 값이 아니라 attempt당 심볼별 1행이라 market_supply와 분리한다.
-- 보조 정보라 조회 실패 심볼은 행이 없을 뿐 market_supply stage 상태와 발행 guard에는 관여하지 않는다.
-- runs FK는 on delete cascade라 purge_old_attempt_data가 run을 지우면 함께 정리된다.
begin;

create table if not exists public.market_macro (
  attempt_run_id uuid not null references public.runs(run_id) on delete cascade,
  trading_day date not null,
  symbol text not null check (symbol in ('CME@NQ', 'USDKRWSMBS')),
  price numeric not null check (
    price > 0 and price <> 'NaN'::numeric and price <> 'Infinity'::numeric
  ),
  change numeric not null check (
    change <> 'NaN'::numeric and change <> 'Infinity'::numeric and change <> '-Infinity'::numeric
  ),
  change_rate numeric not null check (
    change_rate <> 'NaN'::numeric and change_rate <> 'Infinity'::numeric and change_rate <> '-Infinity'::numeric
  ),
  quote_date date,
  collected_at timestamptz not null default now(),
  unique (attempt_run_id, trading_day, symbol)
);

comment on table public.market_macro is
  't3521 매크로 시세 스냅샷(attempt당 심볼별 1행). 원본 직접 SELECT는 허용하지 않으며 get_market_macro로만 조회한다.';
comment on column public.market_macro.price is 't3521 close 현재가.';
comment on column public.market_macro.change is 't3521 change 전일대비(부호는 sign 기준).';
comment on column public.market_macro.change_rate is 't3521 diff 등락률(%, 부호는 sign 기준).';
comment on column public.market_macro.quote_date is 't3521 date 시세 기준일(나스닥 선물은 미국 거래일).';

alter table public.market_macro enable row level security;
revoke all on table public.market_macro from public, anon, authenticated;

create or replace function public.get_market_macro(p_run_id uuid)
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
        'symbol', mm.symbol,
        'price', mm.price,
        'change', mm.change,
        'change_rate', mm.change_rate,
        'quote_date', mm.quote_date,
        'collected_at', mm.collected_at
      )
      order by case mm.symbol when 'CME@NQ' then 0 when 'USDKRWSMBS' then 1 else 2 end
    ),
    '[]'::jsonb
  )
  from public.market_macro mm
  join published_complete_attempt p
    on p.run_id = mm.attempt_run_id
   and p.trading_day = mm.trading_day;
$$;

comment on function public.get_market_macro(uuid) is
  'published complete snapshot의 current_complete_run_id이고 market_supply stage가 성공한 attempt의 매크로 시세(t3521)를 반환한다.';

revoke execute on function public.get_market_macro(uuid) from public, anon, authenticated;
grant execute on function public.get_market_macro(uuid) to anon, authenticated, service_role;

commit;
