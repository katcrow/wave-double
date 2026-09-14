-- 거래소 정규 매매시간 변경(08:00~20:00, 20분 슬롯) 반영. premarket 슬롯은 더 이상
-- 스케줄되지 않지만(.github/workflows/scheduled-batch.yml), batch_kind 값 자체와 CHECK는
-- 하위호환을 위해 남겨둔다. intraday 슬롯 분(minute) 검증만 08:00~19:40 30분 간격에서
-- 20분 간격(00|20|40)으로 바꾼다. 이 정규식은 logical_runs.logical_run_key_shape CHECK와
-- start_attempt()/request_manual_dispatch() 두 RPC 세 곳에 중복돼 있다(AD-14 review 부채,
-- 2026-09-14 조사). apps/web/lib/dispatch.ts의 동일 정규식도 별도로 맞춘다.
begin;

alter table public.logical_runs drop constraint logical_run_key_shape;
alter table public.logical_runs add constraint logical_run_key_shape check (
  (batch_kind = 'intraday' and logical_run_key ~ '^intraday:[0-9]{4}-[0-9]{2}-[0-9]{2}:([01][0-9]|2[0-3]):(00|20|40)$')
  or (batch_kind in ('premarket', 'close') and logical_run_key ~ ('^' || batch_kind || ':[0-9]{4}-[0-9]{2}-[0-9]{2}$'))
);

create or replace function public.start_attempt(
  p_logical_run_key text,
  p_trading_day date,
  p_batch_kind text,
  p_trigger text,
  p_lease_seconds integer default 300
) returns jsonb language plpgsql security definer set search_path = public as $$
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
  if (p_batch_kind = 'intraday' and p_logical_run_key !~ '^intraday:[0-9]{4}-[0-9]{2}-[0-9]{2}:([01][0-9]|2[0-3]):(00|20|40)$')
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

create or replace function public.request_manual_dispatch(
  p_idempotency_key text,
  p_payload_hash text,
  p_requested_by text,
  p_logical_run_key text,
  p_trading_day date,
  p_batch_kind text
) returns jsonb language plpgsql security definer set search_path = public as $$
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
  if (p_batch_kind = 'intraday' and p_logical_run_key !~ '^intraday:[0-9]{4}-[0-9]{2}-[0-9]{2}:([01][0-9]|2[0-3]):(00|20|40)$')
     or (p_batch_kind in ('premarket', 'close') and p_logical_run_key !~ ('^' || p_batch_kind || ':[0-9]{4}-[0-9]{2}-[0-9]{2}$')) then
    raise exception using message = 'invalid logical run key';
  end if;
  -- Boundaries "Always": p_trading_day가 p_logical_run_key에 내포된 날짜와 일치해야 한다.
  -- p_trading_day가 NULL이면 <>는 NULL로 평가돼 if 조건이 조용히 통과되므로 NULL을 명시적으로 거부한다.
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

  -- 활성 attempt 가드: 1.3 fence 모델의 active_attempt_run_id를 읽기전용으로만 확인한다.
  -- start_attempt의 supersede 분기는 호출하지 않는다(Design Notes).
  select active_attempt_run_id into active_run from logical_runs where logical_run_key = p_logical_run_key for update;
  if active_run is not null then
    select * into active_row from runs where run_id = active_run;
    return jsonb_build_object(
      'status', 'conflict',
      'reason', 'ACTIVE_ATTEMPT',
      'run_id', active_row.run_id,
      'started_at', active_row.started_at,
      'trigger', active_row.trigger
    );
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
  -- 동시 요청이 같은 idempotency_key로 먼저 커밋됐다. 재조회해 idempotent 응답으로 수렴한다.
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

commit;
