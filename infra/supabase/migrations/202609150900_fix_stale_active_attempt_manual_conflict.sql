-- 2026-09-15: request_manual_dispatch()가 active_attempt_run_id의 NULL 여부만으로
-- ACTIVE_ATTEMPT conflict를 판정해, skip_attempt/write_stage(failed)로 종결된 run도
-- active_attempt_run_id를 지우지 않는다는 사실과 겹쳐 영구히 수동 재실행을 막았다
-- (오늘 아침 휴장 오판으로 skip된 close:2026-09-15가 이후 정상 개장으로 확인된 뒤에도
-- "이미 실행 중" 오류로 수동 실행이 거부됨).
--
-- start_attempt()는 이미 "진짜 점유 중"인 상태를 running/ready_to_publish로만 취급해
-- 그 외 상태의 active_attempt_run_id는 superseded 처리 없이 그냥 덮어쓴다(즉 차단하지
-- 않는다). request_manual_dispatch()도 같은 정의를 따르도록 맞춘다: running은 lease가
-- 아직 살아있을 때만, ready_to_publish는 항상 conflict로 본다. skipped/failed/
-- superseded/cancelled/published처럼 이미 종결된 run은 더 이상 차단하지 않는다.
--
-- skip_attempt/write_stage 자체가 active_attempt_run_id를 정리하도록 고치는 편이 더
-- 근본적이지만, 이 마이그레이션은 즉시 발생한 장애(수동 실행 완전 차단)를 좁게 고치는
-- 데 집중한다.
begin;

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
  -- start_attempt()와 동일하게 "진짜 점유 중"만 차단한다: ready_to_publish는 항상,
  -- running은 lease가 아직 살아있을 때만. 그 외(skipped/failed/superseded/cancelled/
  -- published)로 종결된 active_attempt_run_id는 정리되지 않은 잔재이므로 차단하지 않는다.
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
