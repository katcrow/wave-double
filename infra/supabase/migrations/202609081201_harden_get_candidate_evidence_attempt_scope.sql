-- Story 4.6 review patch: provenance 집계/조인도 candidate_id와 attempt_run_id를 함께
-- 묶어 동일 candidate_id가 여러 attempt에 재사용되는 경우의 교차 attempt 오염을 차단한다.
-- 202609081200 migration은 이미 적용된 원본으로 보존한다(forward-only).
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
      ac.attempt_run_id,
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
    group by ac.candidate_id, ac.attempt_run_id
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
  inner join candidate_sources cs
    on cs.candidate_id = ac.candidate_id
    and cs.attempt_run_id = ac.attempt_run_id;
$$;

comment on function public.get_candidate_evidence(uuid) is
  'Story 4.6 review patch: p_run_id와 candidate_id/attempt_run_id 복합 경계로 provenance와 supply 행을 격리한다.';

revoke execute on function public.get_candidate_evidence(uuid) from public, anon, authenticated;
grant execute on function public.get_candidate_evidence(uuid) to anon, authenticated, service_role;

commit;
