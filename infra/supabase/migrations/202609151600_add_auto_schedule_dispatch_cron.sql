-- 2026-09-15: .github/workflows/scheduled-batch.yml의 on.schedule: cron이 20분 간격처럼
-- 촘촘한 스케줄을 안정적으로 발화시키지 못한다(GitHub Actions가 고빈도 schedule tick의
-- 상당수를 조용히 드롭한다 -- 9/2~9/14 실행 이력 조사 결과 설계상 기대치 ~34회/일 대비
-- 실제 발화는 5~6회/일에 그침). 이미 검증된 Story 1.10 outbox 경로(pg_cron이 매분
-- Vercel worker를 깨우고, worker가 GitHub workflow_dispatch를 호출하는 구조 -- 지금까지는
-- 사람이 수동 실행을 요청할 때만 채워졌다)를 재사용해, 매분 pg_cron이 현재 KST 슬롯
-- 시각을 스스로 판단해 request_manual_dispatch()로 outbox에 자동으로 채워 넣는다.
-- 기존 on.schedule: cron은 이중 안전망으로 그대로 둔다 -- 두 경로 모두 logical_run_key
-- fence(1.3, AD-3)로 안전하게 dedupe된다.
begin;

-- request_manual_dispatch는 service_role에게만 EXECUTE가 부여돼 있다(Story 1.10).
-- 아래 enqueue_scheduled_dispatch가 security definer로 이 함수를 호출하려면 함수
-- owner(이 migration을 적용하는 postgres 역할)에게도 EXECUTE가 필요하다(postgres는
-- superuser가 아니다 -- rolsuper=false, rolbypassrls=true만 있다).
grant execute on function public.request_manual_dispatch(text, text, text, text, date, text) to postgres;

create or replace function public.enqueue_scheduled_dispatch() returns jsonb
language plpgsql security definer set search_path = public as $$
declare
  now_kst timestamp := now() at time zone 'Asia/Seoul';
  dow int := extract(isodow from now_kst); -- 1=월 .. 7=일
  hh int := extract(hour from now_kst);
  mi int := extract(minute from now_kst);
  trading_day date := now_kst::date;
  logical_key text;
  batch_kind text;
  idem_key text;
  payload_hash text;
begin
  if dow > 5 then
    return jsonb_build_object('status', 'skipped', 'reason', 'WEEKEND');
  end if;

  -- KST 08:00~19:40 20분 간격 intraday, KST 20:00 close.
  -- (scheduled-batch.yml의 on.schedule: cron 세 항목과 동일한 창.)
  if hh = 20 and mi = 0 then
    batch_kind := 'close';
    logical_key := 'close:' || trading_day::text;
  elsif hh between 8 and 19 and mi in (0, 20, 40) then
    batch_kind := 'intraday';
    logical_key := format('intraday:%s:%s:%s', trading_day::text, lpad(hh::text, 2, '0'), lpad(mi::text, 2, '0'));
  else
    return jsonb_build_object('status', 'skipped', 'reason', 'OUTSIDE_WINDOW');
  end if;

  -- idempotency_key를 슬롯에서 결정적으로 만들어, 이 함수가 같은 분(minute)에 두 번
  -- 불려도(재시도 등) request_manual_dispatch의 unique(idempotency_key)가 중복 삽입을
  -- 막는다. payload는 idem_key 자체에서만 유도되므로 매번 동일하다.
  idem_key := 'auto-schedule:' || logical_key;
  payload_hash := md5(idem_key);

  return request_manual_dispatch(
    idem_key,
    payload_hash,
    'system:scheduler',
    logical_key,
    trading_day,
    batch_kind
  );
end $$;

revoke execute on function public.enqueue_scheduled_dispatch() from public, anon, authenticated;
grant execute on function public.enqueue_scheduled_dispatch() to postgres, service_role;

-- claim_dispatch_outbox가 dr.requested_by도 함께 내려주게 한다: outbox worker가
-- 'system:scheduler'가 요청한 행과 사람이 요청한 행을 구분해 GitHub workflow_dispatch
-- 호출 시 올바른 trigger(schedule|manual)를 넘길 수 있게 하기 위함(runs.trigger가
-- 대시보드 트러스트바에 노출되므로, 자동 실행을 "manual"로 잘못 표시하면 안 된다).
create or replace function public.claim_dispatch_outbox(
  p_worker_lease_seconds integer default 120,
  p_limit integer default 20
) returns jsonb language plpgsql security definer set search_path = public as $$
declare result jsonb;
begin
  if p_worker_lease_seconds <= 0 or p_limit <= 0 then
    raise exception using message = 'invalid claim parameters';
  end if;

  with candidates as (
    select o.outbox_id
    from dispatch_outbox o
    where (o.status = 'queued' and (o.lease_expires_at is null or o.lease_expires_at <= now()))
       or (o.status = 'accepted' and o.lease_expires_at <= now())
    order by o.updated_at
    limit p_limit
    for update of o skip locked
  ), updated as (
    update dispatch_outbox o
      set lease_token = gen_random_uuid(),
          lease_expires_at = now() + make_interval(secs => p_worker_lease_seconds),
          attempts = o.attempts + 1,
          updated_at = now()
      from candidates
      where o.outbox_id = candidates.outbox_id
      returning o.outbox_id, o.dispatch_request_id, o.status, o.lease_token, o.run_id, o.github_run_id, o.attempts
  )
  select coalesce(jsonb_agg(jsonb_build_object(
      'outbox_id', updated.outbox_id,
      'dispatch_request_id', updated.dispatch_request_id,
      'status', updated.status,
      'lease_token', updated.lease_token,
      'run_id', updated.run_id,
      'github_run_id', updated.github_run_id,
      'attempts', updated.attempts,
      'logical_run_key', dr.logical_run_key,
      'idempotency_key', dr.idempotency_key,
      'requested_by', dr.requested_by
    )), '[]'::jsonb)
    into result
    from updated join dispatch_request dr on dr.dispatch_request_id = updated.dispatch_request_id;

  return result;
end $$;

do $$
begin
  if exists (select 1 from cron.job where jobname = 'auto-schedule-dispatch-tick') then
    perform cron.unschedule('auto-schedule-dispatch-tick');
  end if;
end $$;

select cron.schedule(
  'auto-schedule-dispatch-tick',
  '* * * * *',
  $$select public.enqueue_scheduled_dispatch();$$
);

commit;
