-- Story 4.9 patch: candidate-day scoped D0 rows and explicit missing-row RPC output.
-- 202609091000 is already applied; all corrections are forward-only here.
begin;

create or replace view public.candidate_supply_hints as
with latest_d0 as (
  select distinct on (s.candidate_id, s.attempt_run_id)
    s.candidate_id,
    s.attempt_run_id,
    s.foreign_net,
    s.institution_net,
    s.individual_net,
    s.program_net,
    s.investor_net_status,
    s.collected_at
  from public.supply_3day s
  join public.candidates c
    on c.candidate_id = s.candidate_id
   and c.attempt_run_id = s.attempt_run_id
   and c.trading_day = s.trading_day
  where s.slot = 'D0'
  order by s.candidate_id, s.attempt_run_id, s.collected_at desc
)
select
  c.candidate_id,
  c.attempt_run_id,
  c.ticker,
  c.trading_day,
  'D0'::text as slot,
  l.batch_kind,
  d.foreign_net,
  d.institution_net,
  d.individual_net,
  d.program_net,
  coalesce(d.investor_net_status, 'missing') as investor_net_status,
  d.collected_at,
  case
    when l.batch_kind = 'close'
      and d.investor_net_status = 'confirmed'
      and d.foreign_net is not null
      and d.institution_net is not null
      and d.individual_net is not null
      and d.program_net is not null
      and d.foreign_net > 0
      and d.institution_net > 0
      and d.program_net > 0
      then 'good'
    when l.batch_kind = 'close'
      and d.investor_net_status = 'confirmed'
      and d.foreign_net is not null
      and d.institution_net is not null
      and d.individual_net is not null
      and d.program_net is not null
      then 'not_met'
    else 'undetermined'
  end as hint_status
from public.candidates c
join public.runs r
  on r.run_id = c.attempt_run_id
join public.logical_runs l
  on l.logical_run_key = r.logical_run_key
left join latest_d0 d
  on d.candidate_id = c.candidate_id
 and d.attempt_run_id = c.attempt_run_id;

comment on view public.candidate_supply_hints is
  'Story 4.9: candidate trading_day와 일치하는 attempt별 D0 supply_3day 행만 계산한다. 행이 없으면 missing/undetermined를 반환하며, close confirmed 상태에서 외인·기관·프로그램이 모두 0 초과일 때만 good이다.';

create or replace function public.get_candidate_supply_hints(p_run_id uuid)
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
      and r.stage_status->>'supply_3day' = 'success'
  ),
  active_candidates as (
    select c.candidate_id, c.attempt_run_id
    from public.candidates c
    join published_complete_attempt p
      on p.run_id = c.attempt_run_id
    where exists (
      select 1
      from public.candidate_tags t
      where t.candidate_id = c.candidate_id
        and t.attempt_run_id = c.attempt_run_id
        and t.status = 'active'
    )
  )
  select coalesce(
    jsonb_agg(
      jsonb_build_object(
        'candidate_id', h.candidate_id,
        'attempt_run_id', h.attempt_run_id,
        'ticker', h.ticker,
        'trading_day', h.trading_day,
        'slot', h.slot,
        'batch_kind', h.batch_kind,
        'foreign_net', h.foreign_net,
        'institution_net', h.institution_net,
        'individual_net', h.individual_net,
        'program_net', h.program_net,
        'investor_net_status', h.investor_net_status,
        'collected_at', h.collected_at,
        'hint_status', h.hint_status
      )
      order by h.ticker, h.candidate_id
    ),
    '[]'::jsonb
  )
  from active_candidates ac
  join public.candidate_supply_hints h
    on h.candidate_id = ac.candidate_id
   and h.attempt_run_id = ac.attempt_run_id
  join published_complete_attempt p
    on p.run_id = h.attempt_run_id
   and p.trading_day = h.trading_day
  where h.slot = 'D0';
$$;

comment on function public.get_candidate_supply_hints(uuid) is
  'Story 4.9: active tag 후보 중 요청한 published current complete attempt의 candidate trading_day/D0 힌트를 반환한다. D0가 없으면 missing/undetermined 행을 포함한다.';

revoke select on table public.supply_3day, public.candidate_supply_hints from public, anon, authenticated;
revoke execute on function public.get_candidate_supply_hints(uuid) from public, anon, authenticated;
grant execute on function public.get_candidate_supply_hints(uuid) to anon, authenticated, service_role;

commit;
