-- Independent KOSPI/KOSDAQ probability snapshots and the 15:00-19:00 schedule.
-- Results are keyed by trading_day; a delayed older slot cannot replace a newer success.
begin;

create table if not exists public.market_index_probability (
  trading_day date primary key,
  target_trading_day date not null,
  kospi_probability double precision not null check (kospi_probability between 0 and 1),
  kosdaq_probability double precision not null check (kosdaq_probability between 0 and 1),
  slot time without time zone not null,
  last_success_at timestamptz not null,
  feature_as_of timestamptz not null,
  model_version text not null,
  validation_status text not null default 'experimental' check (validation_status in ('experimental', 'validated')),
  input_quality jsonb not null default '{}'::jsonb,
  feature_snapshot jsonb not null default '{}'::jsonb,
  created_at timestamptz not null default now(),
  updated_at timestamptz not null default now(),
  check (target_trading_day > trading_day),
  check (slot >= time '15:00' and slot <= time '19:00' and extract(minute from slot)::integer in (0, 20, 40)
    and extract(second from slot) = 0 and (extract(hour from slot) < 19 or extract(minute from slot) = 0))
);

alter table public.market_index_probability enable row level security;
comment on table public.market_index_probability is
  'Latest successful same-day KOSPI/KOSDAQ next-joint-trading-day high-break probabilities. Failures do not write this table.';

create or replace function public.upsert_market_index_probability(p_payload jsonb)
returns jsonb language plpgsql security definer set search_path = public as $$
declare written public.market_index_probability; p_trading_day date; p_target_trading_day date;
  p_kospi_probability double precision; p_kosdaq_probability double precision; p_slot time without time zone;
  p_last_success_at timestamptz; p_feature_as_of timestamptz; p_model_version text;
  p_validation_status text; p_input_quality jsonb; p_feature_snapshot jsonb;
begin
  p_trading_day := (p_payload->>'trading_day')::date;
  p_target_trading_day := (p_payload->>'target_trading_day')::date;
  p_kospi_probability := (p_payload->>'kospi_probability')::double precision;
  p_kosdaq_probability := (p_payload->>'kosdaq_probability')::double precision;
  p_slot := (p_payload->>'slot')::time;
  p_last_success_at := (p_payload->>'last_success_at')::timestamptz;
  p_feature_as_of := (p_payload->>'feature_as_of')::timestamptz;
  p_model_version := p_payload->>'model_version';
  p_validation_status := p_payload->>'validation_status';
  p_input_quality := p_payload->'input_quality';
  p_feature_snapshot := p_payload->'feature_snapshot';
  if p_trading_day is null or p_target_trading_day is null or p_target_trading_day <= p_trading_day
     or p_kospi_probability is null or p_kospi_probability not between 0 and 1
     or p_kosdaq_probability is null or p_kosdaq_probability not between 0 and 1
     or p_slot is null or p_slot < time '15:00' or p_slot > time '19:00'
     or extract(minute from p_slot)::integer not in (0, 20, 40) or extract(second from p_slot) <> 0
     or (extract(hour from p_slot) = 19 and extract(minute from p_slot) <> 0)
     or p_last_success_at is null or p_feature_as_of is null
     or p_model_version is null or length(btrim(p_model_version)) = 0
     or p_validation_status not in ('experimental', 'validated') then
    raise exception using message = 'INVALID_MARKET_INDEX_PROBABILITY';
  end if;
  insert into public.market_index_probability(
    trading_day, target_trading_day, kospi_probability, kosdaq_probability, slot,
    last_success_at, feature_as_of, model_version, validation_status, input_quality, feature_snapshot
  ) values (
    p_trading_day, p_target_trading_day, p_kospi_probability, p_kosdaq_probability, p_slot,
    p_last_success_at, p_feature_as_of, p_model_version, p_validation_status,
    coalesce(p_input_quality, '{}'::jsonb), coalesce(p_feature_snapshot, '{}'::jsonb)
  )
  on conflict (trading_day) do update set
    target_trading_day = excluded.target_trading_day,
    kospi_probability = excluded.kospi_probability,
    kosdaq_probability = excluded.kosdaq_probability,
    slot = excluded.slot,
    last_success_at = excluded.last_success_at,
    feature_as_of = excluded.feature_as_of,
    model_version = excluded.model_version,
    validation_status = excluded.validation_status,
    input_quality = excluded.input_quality,
    feature_snapshot = excluded.feature_snapshot,
    updated_at = now()
  where excluded.slot > market_index_probability.slot
     or (excluded.slot = market_index_probability.slot and excluded.last_success_at > market_index_probability.last_success_at)
  returning * into written;
  if not found then
    return jsonb_build_object('stored', false, 'reason', 'STALE_OR_DUPLICATE_SLOT');
  end if;
  return jsonb_build_object('stored', true, 'trading_day', written.trading_day, 'slot', written.slot,
    'last_success_at', written.last_success_at);
end $$;

create or replace function public.get_latest_market_index_probability()
returns table (
  trading_day date, target_trading_day date, kospi_probability double precision,
  kosdaq_probability double precision, last_success_at timestamptz, feature_as_of timestamptz,
  model_version text, validation_status text
)
language sql stable security definer set search_path = public as $$
  select p.trading_day, p.target_trading_day, p.kospi_probability, p.kosdaq_probability,
    p.last_success_at, p.feature_as_of, p.model_version, p.validation_status
  from public.market_index_probability p order by p.trading_day desc limit 1
$$;

-- Probability jobs persist their own result row and intentionally do not create candidate runs.
-- Close their accepted outbox request directly after the successful probability upsert.
create or replace function public.complete_market_probability_dispatch(p_dispatch_request_id uuid)
returns jsonb language plpgsql security definer set search_path = public as $$
declare updated public.dispatch_outbox;
begin
  if p_dispatch_request_id is null then raise exception using message = 'INVALID_DISPATCH_REQUEST'; end if;
  update public.dispatch_outbox o set status = 'completed', updated_at = now()
    from public.dispatch_request r
    where o.dispatch_request_id = p_dispatch_request_id
      and r.dispatch_request_id = o.dispatch_request_id
      and split_part(r.logical_run_key, ':', 1) = 'market_probability'
      and o.status in ('queued', 'accepted', 'started')
    returning o.* into updated;
  if not found then raise exception using message = 'MARKET_PROBABILITY_DISPATCH_NOT_COMPLETABLE'; end if;
  return jsonb_build_object('dispatch_request_id', updated.dispatch_request_id, 'status', updated.status);
end $$;

-- A short probability job can finish before the dispatch worker records GitHub's 204 as accepted.
create or replace function public.advance_dispatch_outbox(
  p_outbox_id uuid, p_status text, p_lease_token uuid,
  p_run_id uuid default null, p_github_run_id bigint default null
) returns jsonb language plpgsql security definer set search_path = public as $$
declare o public.dispatch_outbox;
begin
  if p_status not in ('queued', 'accepted', 'started', 'completed', 'failed', 'dead_letter') then
    raise exception using message = 'invalid outbox status';
  end if;
  select * into o from public.dispatch_outbox where outbox_id = p_outbox_id for update;
  if not found then raise exception using message = 'OUTBOX_NOT_FOUND'; end if;
  if o.lease_token is distinct from p_lease_token then raise exception using message = 'STALE_LEASE'; end if;
  if o.status = 'completed' and p_status = 'accepted' then
    return jsonb_build_object('outbox_id', o.outbox_id, 'status', o.status, 'run_id', o.run_id,
      'github_run_id', o.github_run_id, 'attempts', o.attempts, 'ignored', true);
  end if;
  if o.status in ('completed', 'failed', 'dead_letter') then raise exception using message = 'OUTBOX_ALREADY_TERMINAL'; end if;
  if not ((o.status = 'queued' and p_status in ('accepted', 'dead_letter')) or
          (o.status = 'accepted' and p_status = 'dead_letter')) then
    raise exception using message = 'INVALID_OUTBOX_TRANSITION';
  end if;
  update public.dispatch_outbox set status = p_status,
    run_id = coalesce(p_run_id, run_id), github_run_id = coalesce(p_github_run_id, github_run_id), updated_at = now()
    where outbox_id = p_outbox_id returning * into o;
  return jsonb_build_object('outbox_id', o.outbox_id, 'status', o.status, 'run_id', o.run_id,
    'github_run_id', o.github_run_id, 'attempts', o.attempts);
end $$;

revoke all on public.market_index_probability from public, anon, authenticated;
revoke execute on function public.upsert_market_index_probability(jsonb) from public, anon, authenticated;
revoke execute on function public.get_latest_market_index_probability() from public, anon;
grant execute on function public.upsert_market_index_probability(jsonb) to service_role;
grant execute on function public.get_latest_market_index_probability() to anon, authenticated, service_role;
revoke execute on function public.complete_market_probability_dispatch(uuid) from public, anon, authenticated;
grant execute on function public.complete_market_probability_dispatch(uuid) to service_role;

-- Extend the existing run/outbox vocabulary while retaining every candidate kind.
alter table public.logical_runs drop constraint logical_run_key_shape;
alter table public.logical_runs add constraint logical_run_key_shape check (
  (batch_kind = 'intraday' and logical_run_key ~ '^intraday:[0-9]{4}-[0-9]{2}-[0-9]{2}:([01][0-9]|2[0-3]):(00|10|20|30|40)$')
  or (batch_kind = 'market_probability' and logical_run_key ~ '^market_probability:[0-9]{4}-[0-9]{2}-[0-9]{2}:(15:(00|20|40)|16:(00|20|40)|17:(00|20|40)|18:(00|20|40)|19:00)$')
  or (batch_kind in ('premarket', 'close') and logical_run_key ~ ('^' || batch_kind || ':[0-9]{4}-[0-9]{2}-[0-9]{2}$'))
);
alter table public.logical_runs drop constraint logical_runs_batch_kind_check;
alter table public.logical_runs add constraint logical_runs_batch_kind_check check (batch_kind in ('premarket', 'intraday', 'close', 'market_probability'));

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
    return jsonb_build_object('status', 'conflict', 'reason', 'ACTIVE_ATTEMPT', 'run_id', active_row.run_id,
      'started_at', active_row.started_at, 'trigger', active_row.trigger);
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

create or replace function public.start_attempt(
  p_logical_run_key text, p_trading_day date, p_batch_kind text, p_trigger text, p_lease_seconds integer default 300
) returns jsonb language plpgsql security definer set search_path = public as $$
declare logical_row public.logical_runs; new_run public.runs; next_attempt integer; next_fence bigint;
begin
  if p_lease_seconds <= 0 then raise exception using message = 'lease_seconds must be positive'; end if;
  if p_batch_kind not in ('premarket','intraday','close','market_probability') or p_trigger not in ('schedule','manual') then
    raise exception using message = 'invalid batch kind or trigger';
  end if;
  if (p_batch_kind = 'intraday' and p_logical_run_key !~ '^intraday:[0-9]{4}-[0-9]{2}-[0-9]{2}:([01][0-9]|2[0-3]):(00|10|20|30|40)$')
     or (p_batch_kind = 'market_probability' and p_logical_run_key !~ '^market_probability:[0-9]{4}-[0-9]{2}-[0-9]{2}:(15:(00|20|40)|16:(00|20|40)|17:(00|20|40)|18:(00|20|40)|19:00)$')
     or (p_batch_kind in ('premarket','close') and p_logical_run_key !~ ('^' || p_batch_kind || ':[0-9]{4}-[0-9]{2}-[0-9]{2}$')) then
    raise exception using message = 'invalid logical run key';
  end if;
  if split_part(p_logical_run_key, ':', 2)::date <> p_trading_day then raise exception using message = 'LOGICAL_KEY_ARGUMENT_MISMATCH'; end if;
  insert into logical_runs(logical_run_key, trading_day, batch_kind) values (p_logical_run_key, p_trading_day, p_batch_kind) on conflict (logical_run_key) do nothing;
  select * into logical_row from logical_runs where logical_run_key = p_logical_run_key for update;
  if logical_row.trading_day <> p_trading_day or logical_row.batch_kind <> p_batch_kind then raise exception using message = 'LOGICAL_KEY_ARGUMENT_MISMATCH'; end if;
  if logical_row.canonical_success_run_id is not null then return jsonb_build_object('replayed', true, 'run_id', logical_row.canonical_success_run_id, 'logical_run_key', p_logical_run_key); end if;
  if logical_row.active_attempt_run_id is not null then update runs set status = 'superseded', finished_at = now() where run_id = logical_row.active_attempt_run_id and status in ('running', 'ready_to_publish'); end if;
  select coalesce(max(attempt_no), 0) + 1, coalesce(max(fence_token), 0) + 1 into next_attempt, next_fence from runs where logical_run_key = p_logical_run_key;
  insert into runs(logical_run_key, attempt_no, fence_token, lease_expires_at, trigger, status)
    values (p_logical_run_key, next_attempt, next_fence, now() + make_interval(secs => p_lease_seconds), p_trigger, 'running') returning * into new_run;
  update logical_runs set active_attempt_run_id = new_run.run_id where logical_run_key = p_logical_run_key;
  return jsonb_build_object('run_id', new_run.run_id, 'logical_run_key', new_run.logical_run_key, 'attempt_no', new_run.attempt_no,
    'fence_token', new_run.fence_token, 'lease_token', new_run.lease_token, 'lease_expires_at', new_run.lease_expires_at);
end $$;

create or replace function public.enforce_scheduled_batch_operating_window()
returns trigger language plpgsql security definer set search_path = pg_catalog, public as $$
declare payload jsonb := to_jsonb(new); logical_run_key text := payload->>'logical_run_key';
  batch_kind text := split_part(coalesce(logical_run_key, ''), ':', 1);
  trigger_name text := payload->>'trigger'; requested_by text := payload->>'requested_by';
  now_kst time := (clock_timestamp() at time zone 'Asia/Seoul')::time; allowed boolean := false;
begin
  if tg_table_name = 'runs' and trigger_name <> 'schedule' then return new; end if;
  if tg_table_name = 'dispatch_request' and requested_by <> 'system:scheduler' then return new; end if;
  if batch_kind = 'intraday' then allowed := now_kst >= time '08:00' and now_kst < time '19:30';
  elsif batch_kind = 'close' then allowed := now_kst >= time '19:30' and now_kst < time '19:50';
  elsif batch_kind = 'market_probability' then allowed := now_kst >= time '15:00' and now_kst < time '19:20';
  end if;
  if not allowed then raise exception using message = 'SCHEDULE_OUTSIDE_OPERATING_WINDOW',
    detail = format('batch_kind=%s now_kst=%s logical_run_key=%s', batch_kind, now_kst, logical_run_key); end if;
  return new;
end $$;

create or replace function public.enqueue_scheduled_dispatch() returns jsonb
language plpgsql security definer set search_path = public as $$
declare now_kst timestamp := now() at time zone 'Asia/Seoul'; dow int := extract(isodow from now_kst);
  hh int := extract(hour from now_kst); mi int := extract(minute from now_kst); trading_day date := now_kst::date;
  logical_key text; batch_kind text; idem_key text; payload_hash text;
begin
  if dow > 5 then return jsonb_build_object('status', 'skipped', 'reason', 'WEEKEND'); end if;
  if hh between 15 and 19 and mi in (0, 20, 40) and not (hh = 19 and mi > 0) then
    batch_kind := 'market_probability';
    logical_key := format('market_probability:%s:%s:%s', trading_day::text, lpad(hh::text, 2, '0'), lpad(mi::text, 2, '0'));
  elsif hh = 19 and mi = 0 then
    batch_kind := 'market_probability';
    logical_key := format('market_probability:%s:19:00', trading_day::text);
  elsif hh = 19 and mi = 40 then
    batch_kind := 'close'; logical_key := 'close:' || trading_day::text;
  elsif hh between 8 and 19 and mi = 10 then
    batch_kind := 'intraday'; logical_key := format('intraday:%s:%s:%s', trading_day::text, lpad(hh::text, 2, '0'), lpad(mi::text, 2, '0'));
  else return jsonb_build_object('status', 'skipped', 'reason', 'OUTSIDE_WINDOW');
  end if;
  idem_key := 'auto-schedule:' || logical_key; payload_hash := md5(idem_key);
  return request_manual_dispatch(idem_key, payload_hash, 'system:scheduler', logical_key, trading_day, batch_kind);
end $$;

comment on function public.enqueue_scheduled_dispatch() is
  'Enqueues existing candidate slots unchanged and market_probability at KST 15:00-19:00 every 20 minutes.';
revoke execute on function public.upsert_market_index_probability(jsonb) from public, anon, authenticated;
grant execute on function public.upsert_market_index_probability(jsonb) to service_role;
grant execute on function public.request_manual_dispatch(text, text, text, text, date, text) to service_role, postgres;
grant execute on function public.start_attempt(text, date, text, text, integer) to service_role;
revoke execute on function public.enqueue_scheduled_dispatch() from public, anon, authenticated;
grant execute on function public.enqueue_scheduled_dispatch() to postgres, service_role;

commit;
