-- 메인 태깅 후보 카드에 거래대금(원)을 함께 반환해 카드에 표시한다. 정렬 규칙은 그대로다.
begin;

create or replace function public.get_today_candidate_cards(p_run_id uuid)
returns jsonb
language sql
security definer
stable
set search_path = public
as $$
  select coalesce(
    jsonb_agg(
      jsonb_build_object(
        'candidate_id', card.candidate_id,
        'ticker', card.ticker,
        'name', card.name,
        'trading_value', card.trading_value,
        'strategies', to_jsonb(card.strategies),
        'vanished_strategies', to_jsonb(card.vanished_strategies),
        'supply_partial_missing', card.supply_partial_missing,
        'themes', card.themes
      )
      order by
        card.active_strategy_count desc,
        card.trading_value desc,
        card.ticker asc
    ),
    '[]'::jsonb
  )
  from (
    select
      c.candidate_id,
      c.attempt_run_id,
      c.ticker,
      c.name,
      c.trading_value,
      count(distinct t.strategy) filter (where t.status = 'active') as active_strategy_count,
      coalesce(
        array_agg(distinct t.strategy order by t.strategy) filter (where t.status = 'active'),
        array[]::text[]
      ) as strategies,
      coalesce(
        array_agg(distinct t.strategy order by t.strategy) filter (where t.status = 'vanished'),
        array[]::text[]
      ) as vanished_strategies,
      coalesce(d0.investor_net_status in ('pending', 'missing'), false) as supply_partial_missing,
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
      ) as themes
    from public.candidates c
    inner join public.candidate_tags t
      on t.candidate_id = c.candidate_id
      and t.attempt_run_id = c.attempt_run_id
      and t.status in ('active', 'vanished')
    left join lateral (
      select s.investor_net_status
      from public.supply_3day s
      where s.candidate_id = c.candidate_id
        and s.attempt_run_id = c.attempt_run_id
        and s.slot = 'D0'
      order by s.trading_day desc
      limit 1
    ) d0 on true
    where c.attempt_run_id = p_run_id
    group by c.candidate_id, c.attempt_run_id, c.ticker, c.name, c.trading_value, d0.investor_net_status
  ) card
$$;

revoke execute on function public.get_today_candidate_cards(uuid) from public;
grant execute on function public.get_today_candidate_cards(uuid) to anon, authenticated, service_role;

comment on function public.get_today_candidate_cards(uuid) is
  '현재 attempt의 태깅 후보 카드(거래대금 trading_value 포함)를 active 전략 수 DESC, 거래대금 DESC, ticker ASC로 반환한다. vanished 전략은 현재 전략 수에 포함하지 않으며 테마는 average_change_pct DESC, theme_code ASC로 정렬한다.';

commit;
