-- Story 4.9: 최신 D0 수급 행의 좋은 수급 힌트와 attempt-scoped read RPC.
-- 힌트 임계값은 이 view의 CASE 한 곳에서만 관리한다. 원본 supply_3day는 변경하지 않는다.
begin;

create or replace view public.candidate_supply_hints as
with latest_d0 as (
  select distinct on (s.candidate_id, s.attempt_run_id)
    s.candidate_id,
    s.attempt_run_id,
    s.trading_day,
    s.slot,
    s.foreign_net,
    s.institution_net,
    s.individual_net,
    s.program_net,
    s.investor_net_status,
    s.collected_at
  from public.supply_3day s
  where s.slot = 'D0'
  order by s.candidate_id, s.attempt_run_id, s.trading_day desc, s.collected_at desc
)
select
  d.candidate_id,
  d.attempt_run_id,
  c.ticker,
  d.trading_day,
  d.slot,
  l.batch_kind,
  d.foreign_net,
  d.institution_net,
  d.individual_net,
  d.program_net,
  d.investor_net_status,
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
from latest_d0 d
join public.candidates c
  on c.candidate_id = d.candidate_id
 and c.attempt_run_id = d.attempt_run_id
join public.runs r
  on r.run_id = d.attempt_run_id
join public.logical_runs l
  on l.logical_run_key = r.logical_run_key;

comment on view public.candidate_supply_hints is
  'Story 4.9: attempt별 최신 D0 supply_3day 행을 계산한다. close confirmed 상태에서 외인·기관·프로그램이 모두 0 초과일 때만 good이며, 개인은 값의 상태 정합성에만 포함한다.';

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
    select c.candidate_id, c.attempt_run_id, c.ticker
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
  'Story 4.9: active tag 후보 중 요청한 published current complete attempt의 trading_day/D0 힌트만 반환한다. candidate_supply_hints view를 통해 판정한다.';

revoke select on table public.supply_3day, public.candidate_supply_hints from public, anon, authenticated;
revoke execute on function public.get_candidate_supply_hints(uuid) from public, anon, authenticated;
grant execute on function public.get_candidate_supply_hints(uuid) to anon, authenticated, service_role;

commit;
