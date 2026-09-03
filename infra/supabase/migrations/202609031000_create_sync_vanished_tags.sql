-- Story 2.8: 장중 시그널 소멸 감지.
-- tags stage(upsert_tags) 성공 직후 호출되는 RPC. 같은 거래일의 직전 attempt(started_at 기준
-- 바로 이전, stage_status->>'tags' in ('success','partial'))에서 active였던 (ticker, strategy)가
-- 현재 attempt에서 재태깅되지 않았는데 ticker가 여전히 현재 attempt candidates에 있으면,
-- 현재 attempt 소유 candidate_tags 행을 status='vanished'로 추가 삽입한다.
-- 과거 attempt 행은 절대 UPDATE하지 않는다(append-only, AD-19) -- 소멸은 항상 현재 attempt
-- 소유 신규 행으로 표현한다(candidate_id가 attempt마다 새로 생성되므로 재사용 불가).
-- "같은 거래일" 판정은 logical_run_key가 달라도(예: intraday 09:30 -> intraday 11:00) 동일
-- trading_day를 가진 모든 attempt를 대상으로 한다(다음 거래일 premarket/close는 대상 밖).
begin;

create or replace function public.sync_vanished_tags(p_run_id uuid)
returns jsonb
language plpgsql
security definer
set search_path = public
as $$
declare
  cur public.runs%rowtype;
  cur_trading_day date;
  prev_run public.runs%rowtype;
  vanished_count integer := 0;
begin
  select * into cur from runs where run_id = p_run_id;
  if not found then
    raise exception using message = 'RUN_NOT_FOUND';
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
    return jsonb_build_object('vanished_count', 0);
  end if;

  with prev_active as (
    select ct.strategy, ct.signal_date, ct.params_meta, c.ticker
    from candidate_tags ct
    join candidates c on c.candidate_id = ct.candidate_id and c.attempt_run_id = ct.attempt_run_id
    where ct.attempt_run_id = prev_run.run_id and ct.status = 'active'
  ),
  current_active as (
    select c.ticker, ct.strategy
    from candidate_tags ct
    join candidates c on c.candidate_id = ct.candidate_id and c.attempt_run_id = ct.attempt_run_id
    where ct.attempt_run_id = p_run_id and ct.status = 'active'
  ),
  current_candidates as (
    select candidate_id, ticker from candidates where attempt_run_id = p_run_id
  ),
  to_insert as (
    select cc.candidate_id, pa.strategy, pa.signal_date, pa.params_meta
    from prev_active pa
    join current_candidates cc on cc.ticker = pa.ticker
    where not exists (
      select 1 from current_active ca where ca.ticker = pa.ticker and ca.strategy = pa.strategy
    )
  ),
  inserted as (
    insert into candidate_tags (candidate_id, attempt_run_id, strategy, signal_date, status, params_meta)
    select candidate_id, p_run_id, strategy, signal_date, 'vanished', coalesce(params_meta, '{}'::jsonb)
    from to_insert
    on conflict (candidate_id, strategy, attempt_run_id) do nothing
    returning 1
  )
  select count(*) into vanished_count from inserted;

  return jsonb_build_object('vanished_count', vanished_count);
end $$;

comment on function public.sync_vanished_tags(uuid) is
  'Story 2.8: 같은 거래일 직전 attempt에서 active였던 (ticker, strategy)가 현재 attempt에서 재태깅되지 않았고 ticker가 여전히 현재 candidates에 있으면 현재 attempt 소유 vanished 태그를 삽입한다. 과거 attempt 행은 UPDATE하지 않는다(append-only). 직전 attempt가 없으면(당일 최초) no-op으로 vanished_count=0을 반환한다. on conflict do nothing으로 재실행해도 안전하다(idempotent).';

revoke execute on function public.sync_vanished_tags(uuid) from public, anon, authenticated;
grant execute on function public.sync_vanished_tags(uuid) to service_role;

commit;
