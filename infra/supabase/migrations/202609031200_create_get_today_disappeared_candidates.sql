-- Story 2.8: 후보 모집단 자체에서 빠진 종목을 "모집단 이탈" / "수집 실패"로 구분해 반환한다.
-- sync_vanished_tags()가 처리하는 "소멸"(ticker는 여전히 candidates에 존재)과 달리, 이 RPC는
-- ticker가 현재 attempt candidates에 아예 없는 경우만 다룬다. 티커별 수집 실패 상세는 저장되지
-- 않으므로(Epic 1은 집계치만 저장), 현재 attempt의 runs.stage_status->>'candidates'로 보수적으로
-- 판정한다: 'success'면 조건검색 결과 변화(population_dropout), 그 외(partial/failed)면
-- 후보 수집 자체가 불완전했으므로 collection_failure로 분류한다(AD-5 "조용한 누락 금지" --
-- 애매하면 실패 쪽으로 표시).
begin;

create or replace function public.get_today_disappeared_candidates(p_run_id uuid)
returns jsonb
language plpgsql
security definer
stable
set search_path = public
as $$
declare
  cur public.runs%rowtype;
  cur_trading_day date;
  prev_run public.runs%rowtype;
  reason text;
  result jsonb;
begin
  select * into cur from runs where run_id = p_run_id;
  if not found then
    return '[]'::jsonb;
  end if;

  select trading_day into cur_trading_day from logical_runs where logical_run_key = cur.logical_run_key;

  select r.* into prev_run
  from runs r
  join logical_runs lr on lr.logical_run_key = r.logical_run_key
  where lr.trading_day = cur_trading_day
    and r.run_id <> p_run_id
    and (r.started_at, r.run_id) < (cur.started_at, cur.run_id)
    and r.stage_status->>'tags' in ('success', 'partial')
  order by r.started_at desc, r.run_id desc
  limit 1;

  if not found then
    return '[]'::jsonb;
  end if;

  reason := case when cur.stage_status->>'candidates' = 'success' then 'population_dropout' else 'collection_failure' end;

  select coalesce(
    jsonb_agg(
      jsonb_build_object(
        'ticker', d.ticker,
        'name', d.name,
        'reason', reason,
        'strategies', to_jsonb(d.strategies)
      )
      order by d.ticker
    ),
    '[]'::jsonb
  )
  into result
  from (
    select c.ticker, c.name, array_agg(distinct ct.strategy order by ct.strategy) as strategies
    from candidate_tags ct
    join candidates c on c.candidate_id = ct.candidate_id and c.attempt_run_id = ct.attempt_run_id
    where ct.attempt_run_id = prev_run.run_id
      and ct.status = 'active'
      and not exists (
        select 1 from candidates cc where cc.attempt_run_id = p_run_id and cc.ticker = c.ticker
      )
    group by c.ticker, c.name
  ) d;

  return result;
end $$;

comment on function public.get_today_disappeared_candidates(uuid) is
  'Story 2.8: 같은 거래일 직전 attempt에서 active 태그가 있었으나 현재 attempt candidates에 ticker 자체가 없는 종목을 반환한다. reason은 현재 attempt candidates stage가 success면 population_dropout, 아니면(partial/failed) collection_failure. 직전 attempt가 없으면 빈 배열을 반환한다.';

revoke execute on function public.get_today_disappeared_candidates(uuid) from public;
grant execute on function public.get_today_disappeared_candidates(uuid) to anon, authenticated, service_role;

commit;
