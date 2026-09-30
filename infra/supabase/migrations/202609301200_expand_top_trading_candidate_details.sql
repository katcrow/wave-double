-- 거래대금 상위 후보 참고 영역이 후보별 핵심 지표를 함께 표시하도록 확장한다.
-- change_pct는 published snapshot의 D0 수정주가 기준, program_buy_value는
-- 후보별 프로그램 순매수 수량에 D0 종가를 곱한 억원 환산값이다.
begin;

alter table public.candidates
  add column if not exists major_sector_name text;

create or replace function public.get_top_tagged_candidates(p_run_id uuid)
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

comment on function public.get_top_tagged_candidates(uuid) is
  'published complete snapshot의 후보를 태그 상태와 무관하게 거래대금 상위 3개로 반환한다. trading_value는 원 단위, change_pct는 당일 수정주가 등락률, program_buy_value는 프로그램 순매수 수량과 D0 종가를 환산한 억원 단위이며 major_sector_name은 후보에 저장된 주요 섹터명이다.';

commit;
