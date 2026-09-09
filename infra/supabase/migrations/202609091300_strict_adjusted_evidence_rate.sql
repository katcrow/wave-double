-- Epic 4 acceptance remediation: never fall back to raw t1702 change_pct.
begin;

create or replace function public.get_candidate_evidence(p_run_id uuid)
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
    select c.candidate_id, c.attempt_run_id, c.ticker, c.trading_day
    from public.candidates c
    join published_complete_attempt p on p.run_id = c.attempt_run_id
     and p.trading_day = c.trading_day
    where exists (
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
        jsonb_agg(csc.source order by csc.contribution_weight desc, csc.source)
          filter (where csc.source is not null),
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
                adjusted_bar.close,
                s.volume,
                round(((adjusted_bar.close - previous_bar.close) / nullif(previous_bar.close, 0)) * 100, 2) as change_pct,
                s.foreign_net,
                s.institution_net,
                s.individual_net,
                s.program_net,
                s.investor_net_status,
                s.collected_at
              from public.supply_3day s
              join public.daily_ohlcv adjusted_bar
                on adjusted_bar.ticker = ac.ticker
               and adjusted_bar.trading_day = s.trading_day
               and adjusted_bar.adjusted is true
              join lateral (
                select d.close
                from public.daily_ohlcv d
                where d.ticker = ac.ticker
                  and d.trading_day < s.trading_day
                  and d.adjusted is true
                order by d.trading_day desc
                limit 1
              ) previous_bar on true
              where s.candidate_id = ac.candidate_id
                and s.attempt_run_id = ac.attempt_run_id
                and s.slot in ('D0', 'D-1', 'D-2')
                and s.trading_day <= ac.trading_day
                and (s.slot <> 'D0' or s.trading_day = ac.trading_day)
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
  'Epic 4 remediation: published current complete supply-success attempt만 읽으며, 후보 trading_day 범위와 adjusted OHLCV 종가·등락률만 제공한다.';

revoke execute on function public.get_candidate_evidence(uuid) from public, anon, authenticated;
grant execute on function public.get_candidate_evidence(uuid) to anon, authenticated, service_role;

commit;
