-- 거래대금 상위 태깅 후보 참고 순위.
-- complete snapshot으로 지정된 published run의 active 태그만 읽고, 전략 종류와 무관하게
-- 거래대금 DESC / ticker ASC 순으로 최대 3개를 반환한다.
begin;

create or replace function public.get_top_tagged_candidates(p_run_id uuid)
returns jsonb
language sql
security definer
stable
set search_path = public
as $$
  select coalesce(
    jsonb_agg(
      jsonb_build_object(
        'candidate_id', top_candidate.candidate_id,
        'attempt_run_id', top_candidate.attempt_run_id,
        'ticker', top_candidate.ticker,
        'name', top_candidate.name,
        'trading_day', top_candidate.trading_day,
        'trading_value', top_candidate.trading_value
      )
      order by top_candidate.trading_value desc, top_candidate.ticker asc
    ),
    '[]'::jsonb
  )
  from (
    select c.candidate_id, c.attempt_run_id, c.ticker, c.name, c.trading_day, c.trading_value
    from public.logical_runs lr
    inner join public.runs r
      on r.run_id = lr.current_complete_run_id
      and r.run_id = p_run_id
      and r.status = 'published'
    inner join public.candidates c
      on c.attempt_run_id = r.run_id
      and c.trading_day = lr.trading_day
    where exists (
      select 1
      from public.candidate_tags t
      where t.candidate_id = c.candidate_id
        and t.attempt_run_id = c.attempt_run_id
        and t.status = 'active'
    )
    order by c.trading_value desc, c.ticker asc
    limit 3
  ) top_candidate
$$;

comment on function public.get_top_tagged_candidates(uuid) is
  'complete snapshot의 current_complete_run_id와 trading_day에 일치하는 run에서 active 태그 후보를 거래대금 DESC, ticker ASC로 최대 3개 반환한다. vanished-only 후보는 제외한다.';

revoke execute on function public.get_top_tagged_candidates(uuid) from public;
grant execute on function public.get_top_tagged_candidates(uuid) to anon, authenticated, service_role;

commit;
