-- 2026-09-16: GitHub Actions 무료 플랜 사용량 절감을 위해 인트라데이 슬롯을 20분
-- 간격(하루 ~34회)에서 60분 간격(매시 30분, 하루 12회)으로 줄인다(Neo 확인).
-- 세션은 KST 08:30 시작, 19:30 마감(=close 배치)이다: intraday 08:30~18:30(11회),
-- close 19:30(1회). 이 migration은 202609151600_add_auto_schedule_dispatch_cron.sql의
-- enqueue_scheduled_dispatch()를 그대로 복사하고 슬롯 창/분 조건만 바꾼다. pg_cron
-- 잡(auto-schedule-dispatch-tick) 자체의 매분 tick 주기는 그대로 둔다 -- 비용을 만드는
-- 건 이 함수 안의 판정이지, 바깥 tick 주기가 아니다.
-- .github/workflows/scheduled-batch.yml의 on.schedule: cron도 같은 창으로 함께 바꿨다
-- (이중 안전망, 두 경로 모두 logical_run_key fence로 dedupe됨).
begin;

-- 0) logical_runs.logical_run_key_shape CHECK을 :00/:20/:40 -> :00/:20/:30/:40으로
-- 확장한다(과거 이력은 그대로, 신규 슬롯 :30을 허용).
do $$
begin
  if not exists (
    select 1
    from pg_constraint c
    join pg_class r on r.oid = c.conrelid
    join pg_namespace n on n.oid = r.relnamespace
    where n.nspname = 'public'
      and r.relname = 'logical_runs'
      and c.conname = 'logical_run_key_shape'
      and c.contype = 'c'
      and pg_get_constraintdef(c.oid) like '%(00|20|40)%'
      and pg_get_constraintdef(c.oid) not like '%30%'
  ) then
    raise exception 'logical_run_key_shape old constraint precondition failed';
  end if;
end $$;

alter table public.logical_runs
  drop constraint logical_run_key_shape;

alter table public.logical_runs
  add constraint logical_run_key_shape
  check (
    (batch_kind = 'intraday' and logical_run_key ~ '^intraday:[0-9]{4}-[0-9]{2}-[0-9]{2}:([01][0-9]|2[0-3]):(00|20|30|40)$')
    or (batch_kind = any (array['premarket', 'close']) and logical_run_key ~ ('^' || batch_kind || ':[0-9]{4}-[0-9]{2}-[0-9]{2}$'))
  );

comment on constraint logical_run_key_shape on public.logical_runs is
  '2026-09-16: intraday 슬롯 분(minute)에 :30(60분 간격, 신규 스케줄)을 추가로 허용한다. :00/:20/:40은 이전 20분 간격 스케줄의 과거 이력과의 호환을 위해 남긴다.';

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

  -- KST 08:30~18:30 60분 간격(매시 30분) intraday, KST 19:30 close.
  -- (scheduled-batch.yml의 on.schedule: cron 세 항목과 동일한 창.)
  if hh = 19 and mi = 30 then
    batch_kind := 'close';
    logical_key := 'close:' || trading_day::text;
  elsif hh between 8 and 18 and mi = 30 then
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

comment on function public.enqueue_scheduled_dispatch() is
  '2026-09-16: 60분 간격(매시 30분) 슬롯으로 축소(GitHub Actions 무료 플랜 사용량 절감, Neo 확인). intraday는 KST 08:30~18:30, close는 KST 19:30 하나뿐이다.';

-- request_manual_dispatch/start_attempt도 같은 정규식으로 logical_run_key 모양을 인라인
-- 검증한다(테이블 CHECK만으로는 두 함수가 예외를 던지기 전에 먼저 막지 못함). 각각의
-- 현재 운영 본문(사전 조회로 확인함)을 그대로 복사하고 정규식 한 줄만 :30까지 확장한다.
create or replace function public.request_manual_dispatch(
  p_idempotency_key text,
  p_payload_hash text,
  p_requested_by text,
  p_logical_run_key text,
  p_trading_day date,
  p_batch_kind text
) returns jsonb
language plpgsql
security definer
set search_path = public
as $$
declare
  existing_request public.dispatch_request;
  existing_outbox public.dispatch_outbox;
  active_run uuid;
  active_row public.runs;
  new_request public.dispatch_request;
  new_outbox public.dispatch_outbox;
begin
  if p_idempotency_key is null or length(btrim(p_idempotency_key)) = 0
     or p_payload_hash is null or length(btrim(p_payload_hash)) = 0
     or p_requested_by is null or length(btrim(p_requested_by)) = 0 then
    raise exception using message = 'INVALID_DISPATCH_REQUEST';
  end if;
  if p_batch_kind not in ('premarket', 'intraday', 'close') then
    raise exception using message = 'invalid batch kind';
  end if;
  if (p_batch_kind = 'intraday' and p_logical_run_key !~ '^intraday:[0-9]{4}-[0-9]{2}-[0-9]{2}:([01][0-9]|2[0-3]):(00|20|30|40)$')
     or (p_batch_kind in ('premarket', 'close') and p_logical_run_key !~ ('^' || p_batch_kind || ':[0-9]{4}-[0-9]{2}-[0-9]{2}$')) then
    raise exception using message = 'invalid logical run key';
  end if;
  if p_trading_day is null or split_part(p_logical_run_key, ':', 2)::date <> p_trading_day then
    raise exception using message = 'TRADING_DAY_MISMATCH';
  end if;

  select * into existing_request from dispatch_request where idempotency_key = p_idempotency_key for update;
  if found then
    if existing_request.payload_hash <> p_payload_hash then
      raise exception using message = 'IDEMPOTENCY_KEY_CONFLICT';
    end if;
    select * into existing_outbox from dispatch_outbox where dispatch_request_id = existing_request.dispatch_request_id;
    return jsonb_build_object(
      'status', coalesce(existing_outbox.status, 'queued'),
      'dispatch_request_id', existing_request.dispatch_request_id,
      'reason', 'replayed'
    );
  end if;

  select active_attempt_run_id into active_run from logical_runs where logical_run_key = p_logical_run_key for update;
  if active_run is not null then
    select * into active_row from runs where run_id = active_run;
    if active_row.status = 'ready_to_publish'
       or (active_row.status = 'running' and active_row.lease_expires_at > now()) then
      return jsonb_build_object(
        'status', 'conflict',
        'reason', 'ACTIVE_ATTEMPT',
        'run_id', active_row.run_id,
        'started_at', active_row.started_at,
        'trigger', active_row.trigger
      );
    end if;
  end if;

  insert into dispatch_request(idempotency_key, payload_hash, requested_by, logical_run_key)
    values (p_idempotency_key, p_payload_hash, p_requested_by, p_logical_run_key)
    returning * into new_request;
  insert into dispatch_outbox(dispatch_request_id, status)
    values (new_request.dispatch_request_id, 'queued')
    returning * into new_outbox;
  return jsonb_build_object(
    'status', new_outbox.status,
    'dispatch_request_id', new_request.dispatch_request_id,
    'outbox_id', new_outbox.outbox_id,
    'reason', 'created'
  );
exception when unique_violation then
  select * into existing_request from dispatch_request where idempotency_key = p_idempotency_key;
  if existing_request.payload_hash <> p_payload_hash then
    raise exception using message = 'IDEMPOTENCY_KEY_CONFLICT';
  end if;
  select * into existing_outbox from dispatch_outbox where dispatch_request_id = existing_request.dispatch_request_id;
  return jsonb_build_object(
    'status', coalesce(existing_outbox.status, 'queued'),
    'dispatch_request_id', existing_request.dispatch_request_id,
    'reason', 'replayed'
  );
end
$$;

create or replace function public.start_attempt(
  p_logical_run_key text,
  p_trading_day date,
  p_batch_kind text,
  p_trigger text,
  p_lease_seconds integer default 300
) returns jsonb
language plpgsql
security definer
set search_path = public
as $$
declare
  logical_row public.logical_runs;
  new_run public.runs;
  next_attempt integer;
  next_fence bigint;
begin
  if p_lease_seconds <= 0 then raise exception using message = 'lease_seconds must be positive'; end if;
  if p_batch_kind not in ('premarket','intraday','close') or p_trigger not in ('schedule','manual') then
    raise exception using message = 'invalid batch kind or trigger';
  end if;
  if (p_batch_kind = 'intraday' and p_logical_run_key !~ '^intraday:[0-9]{4}-[0-9]{2}-[0-9]{2}:([01][0-9]|2[0-3]):(00|20|30|40)$')
     or (p_batch_kind in ('premarket','close') and p_logical_run_key !~ ('^' || p_batch_kind || ':[0-9]{4}-[0-9]{2}-[0-9]{2}$')) then
    raise exception using message = 'invalid logical run key';
  end if;
  if split_part(p_logical_run_key, ':', 2)::date <> p_trading_day then
    raise exception using message = 'LOGICAL_KEY_ARGUMENT_MISMATCH';
  end if;
  insert into logical_runs(logical_run_key, trading_day, batch_kind)
    values (p_logical_run_key, p_trading_day, p_batch_kind)
    on conflict (logical_run_key) do nothing;
  select * into logical_row from logical_runs where logical_run_key = p_logical_run_key for update;
  if logical_row.trading_day <> p_trading_day or logical_row.batch_kind <> p_batch_kind then
    raise exception using message = 'LOGICAL_KEY_ARGUMENT_MISMATCH';
  end if;
  if logical_row.canonical_success_run_id is not null then
    return jsonb_build_object('replayed', true, 'run_id', logical_row.canonical_success_run_id, 'logical_run_key', p_logical_run_key);
  end if;
  if logical_row.active_attempt_run_id is not null then
    update runs set status = 'superseded', finished_at = now()
      where run_id = logical_row.active_attempt_run_id and status in ('running', 'ready_to_publish');
  end if;
  select coalesce(max(attempt_no), 0) + 1, coalesce(max(fence_token), 0) + 1
    into next_attempt, next_fence from runs where logical_run_key = p_logical_run_key;
  insert into runs(logical_run_key, attempt_no, fence_token, lease_expires_at, trigger, status)
    values (p_logical_run_key, next_attempt, next_fence, now() + make_interval(secs => p_lease_seconds), p_trigger, 'running')
    returning * into new_run;
  update logical_runs set active_attempt_run_id = new_run.run_id where logical_run_key = p_logical_run_key;
  return jsonb_build_object('run_id', new_run.run_id, 'logical_run_key', new_run.logical_run_key, 'attempt_no', new_run.attempt_no, 'fence_token', new_run.fence_token, 'lease_token', new_run.lease_token, 'lease_expires_at', new_run.lease_expires_at);
end
$$;

commit;
