-- Let the minute cron recover the intended 20-minute probability slot after a
-- transient enqueue failure, while keeping one stable logical/idempotency key.
begin;

create or replace function public.enqueue_scheduled_dispatch() returns jsonb
language plpgsql security definer set search_path = public as $$
declare now_kst timestamp := now() at time zone 'Asia/Seoul'; dow int := extract(isodow from now_kst);
  hh int := extract(hour from now_kst); mi int := extract(minute from now_kst); trading_day date := now_kst::date;
  slot_minute int; logical_key text; batch_kind text; idem_key text; payload_hash text;
begin
  if dow > 5 then return jsonb_build_object('status', 'skipped', 'reason', 'WEEKEND'); end if;
  if hh = 19 and mi = 40 then
    batch_kind := 'close'; logical_key := 'close:' || trading_day::text;
  elsif hh between 8 and 19 and mi = 10 then
    batch_kind := 'intraday'; logical_key := format('intraday:%s:%s:%s', trading_day::text, lpad(hh::text, 2, '0'), lpad(mi::text, 2, '0'));
  elsif (hh between 15 and 18) or (hh = 19 and mi < 20) then
    batch_kind := 'market_probability';
    slot_minute := (mi / 20) * 20;
    logical_key := format('market_probability:%s:%s:%s', trading_day::text,
      lpad(hh::text, 2, '0'), lpad(slot_minute::text, 2, '0'));
  else return jsonb_build_object('status', 'skipped', 'reason', 'OUTSIDE_WINDOW');
  end if;
  idem_key := 'auto-schedule:' || logical_key; payload_hash := md5(idem_key);
  return request_manual_dispatch(idem_key, payload_hash, 'system:scheduler', logical_key, trading_day, batch_kind);
end $$;

comment on function public.enqueue_scheduled_dispatch() is
  'Enqueues each market probability slot throughout its 20-minute window using a stable idempotency key.';

commit;
