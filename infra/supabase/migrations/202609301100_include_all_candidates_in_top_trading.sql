-- 거래대금 상위 후보 참고 순위.
-- 기존 public RPC 시그니처는 유지하되 candidate_tags 상태와 무관하게
-- 동일 complete snapshot의 후보 모집단에서 거래대금 상위 3개를 반환한다.
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
      and r.logical_run_key = lr.logical_run_key
      and r.status = 'published'
    inner join public.candidates c
      on c.attempt_run_id = r.run_id
      and c.trading_day = lr.trading_day
    order by c.trading_value desc, c.ticker asc
    limit 3
  ) top_candidate
$$;

comment on function public.get_top_tagged_candidates(uuid) is
  'complete snapshot의 current_complete_run_id와 trading_day에 일치하는 published run의 후보를 거래대금 DESC, ticker ASC로 최대 3개 반환한다. candidate_tags 상태와 무관하다.';

revoke execute on function public.get_top_tagged_candidates(uuid) from public;
grant execute on function public.get_top_tagged_candidates(uuid) to anon, authenticated, service_role;

commit;
