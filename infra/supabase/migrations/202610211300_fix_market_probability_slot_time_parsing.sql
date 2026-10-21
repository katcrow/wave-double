-- Parse the HH and MM parts of market_probability logical keys as one SQL time.
-- logical_run_key is market_probability:<date>:<HH>:<MM>, so split_part(..., 3)
-- alone returns only the hour and is not a valid time literal.
begin;

create or replace function public.enforce_scheduled_batch_operating_window()
returns trigger language plpgsql security definer set search_path = pg_catalog, public as $$
declare payload jsonb := to_jsonb(new); logical_run_key text := payload->>'logical_run_key';
  batch_kind text := split_part(coalesce(logical_run_key, ''), ':', 1);
  trigger_name text := payload->>'trigger'; requested_by text := payload->>'requested_by';
  now_kst timestamp := clock_timestamp() at time zone 'Asia/Seoul';
  slot_date date; slot_time time; allowed boolean := false;
begin
  if tg_table_name = 'runs' and trigger_name <> 'schedule' then return new; end if;
  if tg_table_name = 'dispatch_request' and requested_by <> 'system:scheduler' then return new; end if;
  if batch_kind = 'intraday' then allowed := now_kst::time >= time '08:00' and now_kst::time < time '19:30';
  elsif batch_kind = 'close' then allowed := now_kst::time >= time '19:30' and now_kst::time < time '19:50';
  elsif batch_kind = 'market_probability' then
    if logical_run_key ~ '^market_probability:[0-9]{4}-[0-9]{2}-[0-9]{2}:(15:(00|20|40)|16:(00|20|40)|17:(00|20|40)|18:(00|20|40)|19:00)$' then
      slot_date := split_part(logical_run_key, ':', 2)::date;
      slot_time := (split_part(logical_run_key, ':', 3) || ':' || split_part(logical_run_key, ':', 4))::time;
      allowed := slot_date = now_kst::date
        and now_kst::time >= slot_time
        and now_kst::time < slot_time + interval '20 minutes';
    end if;
  end if;
  if not allowed then raise exception using message = 'SCHEDULE_OUTSIDE_OPERATING_WINDOW',
    detail = format('batch_kind=%s now_kst=%s logical_run_key=%s', batch_kind, now_kst, logical_run_key); end if;
  return new;
end $$;

commit;
