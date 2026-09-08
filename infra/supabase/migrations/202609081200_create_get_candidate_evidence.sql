-- Story 4.6: 후보 카드가 소비하는 attempt-scoped 3일 근거 read RPC.
-- 기존 카드 RPC와 테이블 계약은 유지하고, active 태그 후보의 provenance와
-- 슬롯별 최신 supply 행을 D0/D-1/D-2 순서로 한 번에 반환한다.
begin;

create or replace function public.get_candidate_evidence(p_run_id uuid)
returns jsonb
language sql
security definer
stable
set search_path = public
as $$
  with active_candidates as (
    select c.candidate_id, c.attempt_run_id, c.ticker
    from public.candidates c
    where c.attempt_run_id = p_run_id
      and exists (
        select 1
        from public.candidate_tags t
        where t.candidate_id = c.candidate_id
          and t.attempt_run_id = c.attempt_run_id
          and t.status = 'active'
      )
  ),
  candidate_sources as (
    select
      ac.candidate_id,
      coalesce(
        jsonb_agg(
          csc.source
          order by csc.contribution_weight desc, csc.source
        ) filter (where csc.source is not null),
        '[]'::jsonb
      ) as sources
    from active_candidates ac
    left join public.candidate_source_contrib csc
      on csc.candidate_id = ac.candidate_id
      and csc.attempt_run_id = ac.attempt_run_id
    group by ac.candidate_id
  )
  select coalesce(
    jsonb_agg(
      jsonb_build_object(
        'candidate_id', ac.candidate_id,
        'sources', cs.sources,
        'rows', coalesce(
          (
            select jsonb_agg(
              jsonb_build_object(
                'trading_day', evidence.trading_day,
                'slot', evidence.slot,
                'close', evidence.close,
                'volume', evidence.volume,
                'change_pct', evidence.change_pct,
                'foreign_net', evidence.foreign_net,
                'institution_net', evidence.institution_net,
                'individual_net', evidence.individual_net,
                'program_net', evidence.program_net,
                'investor_net_status', evidence.investor_net_status,
                'collected_at', evidence.collected_at
              )
              order by case evidence.slot when 'D0' then 0 when 'D-1' then 1 when 'D-2' then 2 else 3 end
            )
            from (
              select distinct on (s.slot)
                s.trading_day,
                s.slot,
                s.close,
                s.volume,
                s.change_pct,
                s.foreign_net,
                s.institution_net,
                s.individual_net,
                s.program_net,
                s.investor_net_status,
                s.collected_at
              from public.supply_3day s
              where s.candidate_id = ac.candidate_id
                and s.attempt_run_id = ac.attempt_run_id
                and s.slot in ('D0', 'D-1', 'D-2')
              order by s.slot, s.trading_day desc, s.collected_at desc
            ) evidence
          ),
          '[]'::jsonb
        )
      )
      order by ac.ticker
    ),
    '[]'::jsonb
  )
  from active_candidates ac
  inner join candidate_sources cs on cs.candidate_id = ac.candidate_id;
$$;

comment on function public.get_candidate_evidence(uuid) is
  'Story 4.6: p_run_id로 격리한 active 후보의 candidate_source_contrib provenance와 supply_3day 슬롯별 최신 행을 D0/D-1/D-2 순서로 반환한다. 원천이 없으면 sources=[]이며 UI가 기본으로 표시한다. 기존 카드 RPC와 테이블은 수정하지 않는다.';

revoke execute on function public.get_candidate_evidence(uuid) from public, anon, authenticated;
grant execute on function public.get_candidate_evidence(uuid) to anon, authenticated, service_role;

commit;
