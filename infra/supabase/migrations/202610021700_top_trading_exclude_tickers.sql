-- 거래대금 상위 후보 RPC가 제외 ticker 배열을 받아 조회 단계에서 제외한 뒤 상위 3개를 반환한다.
-- 단일 시그니처로 재생성해 overload 모호성을 막고, 기본값 '{}'로 p_run_id만 넘기는 기존 호출을 유지한다.
begin;

drop function if exists public.get_top_tagged_candidates(uuid);

create or replace function public.get_top_tagged_candidates(
  p_run_id uuid,
  p_exclude_tickers text[] default '{}'
)
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
  )
  select coalesce(
    jsonb_agg(
      jsonb_build_object(
        'candidate_id', top_candidate.candidate_id,
        'attempt_run_id', top_candidate.attempt_run_id,
        'ticker', top_candidate.ticker,
        'name', top_candidate.name,
        'trading_day', top_candidate.trading_day,
        'trading_value', top_candidate.trading_value,
        'change_pct', top_candidate.change_pct,
        'major_sector_name', top_candidate.major_sector_name,
        'themes', top_candidate.themes,
        'program_buy_value', top_candidate.program_buy_value
      )
      order by top_candidate.trading_value desc, top_candidate.ticker asc
    ),
    '[]'::jsonb
  )
  from (
    select
      c.candidate_id,
      c.attempt_run_id,
      c.ticker,
      c.name,
      c.trading_day,
      c.trading_value,
      c.major_sector_name,
      coalesce(
        (
          select jsonb_agg(
            jsonb_build_object(
              'theme_code', ct.theme_code,
              'theme_name', ct.theme_name,
              'average_change_pct', ct.average_change_pct
            ) order by ct.average_change_pct desc, ct.theme_code asc
          )
          from public.candidate_themes ct
          where ct.candidate_id = c.candidate_id
            and ct.attempt_run_id = c.attempt_run_id
        ),
        '[]'::jsonb
      ) as themes,
      coalesce(
        round(((current_bar.close - previous_bar.close) / nullif(previous_bar.close, 0)) * 100, 2),
        d0.change_pct
      ) as change_pct,
      case
        when d0.program_net is null then null
        else round((d0.program_net * coalesce(current_bar.close, d0.close)) / 100000000.0, 2)
      end as program_buy_value
    from published_complete_attempt p
    join public.candidates c
      on c.attempt_run_id = p.run_id
      and c.trading_day = p.trading_day
      and not (c.ticker = any(array_remove(coalesce(p_exclude_tickers, '{}'), null)))
    left join lateral (
      select s.close, s.change_pct, s.program_net
      from public.supply_3day s
      where s.candidate_id = c.candidate_id
        and s.attempt_run_id = c.attempt_run_id
        and s.trading_day = c.trading_day
        and s.slot = 'D0'
        and s.investor_net_status = 'confirmed'
      order by s.collected_at desc
      limit 1
    ) d0 on true
    left join lateral (
      select d.close
      from public.daily_ohlcv d
      where d.ticker = c.ticker
        and d.trading_day = c.trading_day
        and d.adjusted is true
      limit 1
    ) current_bar on true
    left join lateral (
      select d.close
      from public.daily_ohlcv d
      where d.ticker = c.ticker
        and d.trading_day < c.trading_day
        and d.adjusted is true
      order by d.trading_day desc
      limit 1
    ) previous_bar on true
    order by c.trading_value desc, c.ticker asc
    limit 3
  ) top_candidate;
$$;

revoke execute on function public.get_top_tagged_candidates(uuid, text[]) from public;
grant execute on function public.get_top_tagged_candidates(uuid, text[]) to anon, authenticated, service_role;

comment on function public.get_top_tagged_candidates(uuid, text[]) is
  'published complete snapshot의 거래대금 상위 3개 후보와 attempt-scoped t1532 테마를 반환한다. p_exclude_tickers에 든 ticker는 상위 3개를 고르기 전에 제외한다(기본 빈 배열). 테마는 average_change_pct DESC, theme_code ASC로 정렬한다.';

commit;
