-- Preserve the active-attempt lease guard when adding market_probability dispatch support.
begin;

create or replace function public.request_manual_dispatch(
  p_idempotency_key text, p_payload_hash text, p_requested_by text, p_logical_run_key text,
  p_trading_day date, p_batch_kind text
) returns jsonb language plpgsql security definer set search_path = public as $$
declare existing_request public.dispatch_request; existing_outbox public.dispatch_outbox;
  active_run uuid; active_row public.runs; new_request public.dispatch_request; new_outbox public.dispatch_outbox;
begin
  if p_idempotency_key is null or length(btrim(p_idempotency_key)) = 0
     or p_payload_hash is null or length(btrim(p_payload_hash)) = 0
     or p_requested_by is null or length(btrim(p_requested_by)) = 0 then
    raise exception using message = 'INVALID_DISPATCH_REQUEST';
  end if;
  if p_batch_kind not in ('premarket', 'intraday', 'close', 'market_probability') then
    raise exception using message = 'invalid batch kind';
  end if;
  if (p_batch_kind = 'intraday' and p_logical_run_key !~ '^intraday:[0-9]{4}-[0-9]{2}-[0-9]{2}:([01][0-9]|2[0-3]):(00|10|20|30|40)$')
     or (p_batch_kind = 'market_probability' and p_logical_run_key !~ '^market_probability:[0-9]{4}-[0-9]{2}-[0-9]{2}:(15:(00|20|40)|16:(00|20|40)|17:(00|20|40)|18:(00|20|40)|19:00)$')
     or (p_batch_kind in ('premarket', 'close') and p_logical_run_key !~ ('^' || p_batch_kind || ':[0-9]{4}-[0-9]{2}-[0-9]{2}$')) then
    raise exception using message = 'invalid logical run key';
  end if;
  if p_trading_day is null or split_part(p_logical_run_key, ':', 2)::date <> p_trading_day then
    raise exception using message = 'TRADING_DAY_MISMATCH';
  end if;
  select * into existing_request from dispatch_request where idempotency_key = p_idempotency_key for update;
  if found then
    if existing_request.payload_hash <> p_payload_hash then raise exception using message = 'IDEMPOTENCY_KEY_CONFLICT'; end if;
    select * into existing_outbox from dispatch_outbox where dispatch_request_id = existing_request.dispatch_request_id;
    return jsonb_build_object('status', coalesce(existing_outbox.status, 'queued'), 'dispatch_request_id', existing_request.dispatch_request_id, 'reason', 'replayed');
  end if;
  select active_attempt_run_id into active_run from logical_runs where logical_run_key = p_logical_run_key for update;
  if active_run is not null then
    select * into active_row from runs where run_id = active_run;
    if active_row.status = 'ready_to_publish'
       or (active_row.status = 'running' and active_row.lease_expires_at > now()) then
      return jsonb_build_object('status', 'conflict', 'reason', 'ACTIVE_ATTEMPT', 'run_id', active_row.run_id,
        'started_at', active_row.started_at, 'trigger', active_row.trigger);
    end if;
  end if;
  insert into dispatch_request(idempotency_key, payload_hash, requested_by, logical_run_key)
    values (p_idempotency_key, p_payload_hash, p_requested_by, p_logical_run_key) returning * into new_request;
  insert into dispatch_outbox(dispatch_request_id, status) values (new_request.dispatch_request_id, 'queued') returning * into new_outbox;
  return jsonb_build_object('status', new_outbox.status, 'dispatch_request_id', new_request.dispatch_request_id,
    'outbox_id', new_outbox.outbox_id, 'reason', 'created');
exception when unique_violation then
  select * into existing_request from dispatch_request where idempotency_key = p_idempotency_key;
  if existing_request.payload_hash <> p_payload_hash then raise exception using message = 'IDEMPOTENCY_KEY_CONFLICT'; end if;
  select * into existing_outbox from dispatch_outbox where dispatch_request_id = existing_request.dispatch_request_id;
  return jsonb_build_object('status', coalesce(existing_outbox.status, 'queued'), 'dispatch_request_id', existing_request.dispatch_request_id, 'reason', 'replayed');
end $$;
revoke execute on function public.request_manual_dispatch(text, text, text, text, date, text) from public, anon, authenticated;
grant execute on function public.request_manual_dispatch(text, text, text, text, date, text) to service_role, postgres;

commit;

