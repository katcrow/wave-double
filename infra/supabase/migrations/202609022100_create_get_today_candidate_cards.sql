-- Story 2.7: 오늘의 후보 카드 UI가 소비할 RPC.
-- get_dashboard_snapshot()이 반환하는 complete_snapshot.run_id로 호출되며, 태그가 있는(active) 후보만
-- candidates INNER JOIN candidate_tags(status='active')로 골라 전략 태그 배열과 D0 수급 부분결측 여부를
-- 함께 반환한다. 기존 candidates/candidate_tags/supply_3day 테이블과 get_dashboard_snapshot()은
-- 수정하지 않는다(신규 RPC만 추가).
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
      array_agg(distinct t.strategy order by t.strategy) as strategies,
      -- D0 행이 없으면(Epic 4 수집 미구현) NULL -> coalesce로 false. D0 행이 있고 investor_net_status가
      -- pending/missing일 때만 true -- 부분결측은 데이터 일부가 존재할 때의 상태이지 전체 부재가 아니다.
      coalesce(s.investor_net_status in ('pending', 'missing'), false) as supply_partial_missing
    from public.candidates c
    inner join public.candidate_tags t
      on t.candidate_id = c.candidate_id
      and t.attempt_run_id = c.attempt_run_id
      and t.status = 'active'
    left join public.supply_3day s
      on s.candidate_id = c.candidate_id
      and s.attempt_run_id = c.attempt_run_id
      and s.slot = 'D0'
    where c.attempt_run_id = p_run_id
    group by c.candidate_id, c.ticker, c.name, s.investor_net_status
  ) card
$$;

comment on function public.get_today_candidate_cards(uuid) is
  'Story 2.7: 태그가 있는(candidate_tags.status=active) 후보를 카드 뷰모델 원시 행으로 반환한다. strategies는 정렬된 A/B/C 배열, supply_partial_missing은 D0 슬롯의 investor_net_status가 pending/missing일 때만 true(D0 행 자체가 없으면 false).';

revoke execute on function public.get_today_candidate_cards(uuid) from public;
grant execute on function public.get_today_candidate_cards(uuid) to anon, authenticated, service_role;

commit;
