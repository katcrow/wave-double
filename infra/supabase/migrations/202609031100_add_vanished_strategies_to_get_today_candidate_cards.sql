-- Story 2.8: get_today_candidate_cards()가 vanished 태그도 카드 유지에 반영하도록 확장.
-- 202609022200_fix_get_today_candidate_cards_d0_dedupe.sql의 최종본을 base로,
-- candidate_tags INNER JOIN 조건을 status in ('active','vanished')로 넓히고,
-- 전략 배열을 status별로 분리한 strategies(active)/vanished_strategies(vanished)로 반환한다.
-- D0 dedupe(LATERAL 최신 1행 선택) 로직은 그대로 유지한다.
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
        'strategies', to_jsonb(card.strategies),
        'vanished_strategies', to_jsonb(card.vanished_strategies),
        'supply_partial_missing', card.supply_partial_missing
      )
      order by card.ticker
    ),
    '[]'::jsonb
  )
  from (
    select
      c.candidate_id,
      c.ticker,
      c.name,
      coalesce(
        array_agg(distinct t.strategy order by t.strategy) filter (where t.status = 'active'),
        array[]::text[]
      ) as strategies,
      coalesce(
        array_agg(distinct t.strategy order by t.strategy) filter (where t.status = 'vanished'),
        array[]::text[]
      ) as vanished_strategies,
      -- D0 행이 없으면(Epic 4 수집 미구현) NULL -> coalesce로 false. D0 행이 있고 investor_net_status가
      -- pending/missing일 때만 true -- 부분결측은 데이터 일부가 존재할 때의 상태이지 전체 부재가 아니다.
      coalesce(d0.investor_net_status in ('pending', 'missing'), false) as supply_partial_missing
    from public.candidates c
    inner join public.candidate_tags t
      on t.candidate_id = c.candidate_id
      and t.attempt_run_id = c.attempt_run_id
      and t.status in ('active', 'vanished')
    -- supply_3day의 D0 슬롯은 attempt_run_id별로 누적되며 덮어쓰지 않는다(테이블 comment 참고) --
    -- 같은 (candidate_id, attempt_run_id)에 D0 행이 여러 개일 수 있으므로, 조인/집계 전에 후보당
    -- 정확히 한 행만(trading_day 기준 최신) LATERAL로 선택해 investor_net_status가 group by
    -- 키에 들어가 카드가 중복 노출되는 일을 막는다.
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
    group by c.candidate_id, c.ticker, c.name, d0.investor_net_status
  ) card
$$;

comment on function public.get_today_candidate_cards(uuid) is
  'Story 2.7/2.8: candidate_tags.status가 active 또는 vanished인 후보를 카드 뷰모델 원시 행으로 반환한다. strategies는 active 태그만 정렬된 A/B/C 배열, vanished_strategies는 vanished 태그만 정렬된 배열(둘 다 빈 배열 가능, 둘 다 비어있는 행은 존재하지 않음 -- INNER JOIN 조건). supply_partial_missing은 D0 슬롯의 investor_net_status가 pending/missing일 때만 true(D0 행 자체가 없으면 false). D0 슬롯이 후보당 여러 행 누적돼 있어도 trading_day 기준 최신 1행만 반영해 카드 중복을 방지한다(202609022200 patch 유지).';

commit;
