-- 예약 배치가 GitHub Actions 지연으로 장외에 실행되지 않도록 DB 경계에서도 차단한다.
-- 자동 스케줄은 KST 08:10~19:10 intraday와 19:40 close만 허용한다.
-- manual trigger는 기존 수동/복구 계약을 보존한다.
begin;

create or replace function public.enforce_scheduled_batch_operating_window()
returns trigger
language plpgsql
security definer
set search_path = pg_catalog, public
as $$
declare
  payload jsonb := to_jsonb(new);
  logical_run_key text := payload->>'logical_run_key';
  batch_kind text := split_part(coalesce(logical_run_key, ''), ':', 1);
  trigger_name text := payload->>'trigger';
  requested_by text := payload->>'requested_by';
  -- now()는 트랜잭션 시작 시각으로 고정되므로, 장시간 열린 트랜잭션에서도 실제
  -- INSERT 시각을 기준으로 guard가 판정되도록 clock_timestamp()를 사용한다.
  now_kst time := (clock_timestamp() at time zone 'Asia/Seoul')::time;
  allowed boolean := false;
begin
  if tg_table_name = 'runs' and trigger_name <> 'schedule' then
    return new;
  end if;
  if tg_table_name = 'dispatch_request' and requested_by <> 'system:scheduler' then
    return new;
  end if;

  if batch_kind = 'intraday' then
    allowed := now_kst >= time '08:00' and now_kst < time '20:00';
  elsif batch_kind = 'close' then
    allowed := now_kst >= time '19:30' and now_kst < time '20:00';
  end if;

  if not allowed then
    raise exception using
      message = 'SCHEDULE_OUTSIDE_OPERATING_WINDOW',
      detail = format('batch_kind=%s now_kst=%s logical_run_key=%s', batch_kind, now_kst, logical_run_key);
  end if;
  return new;
end;
$$;

drop trigger if exists runs_scheduled_operating_window_guard on public.runs;
create trigger runs_scheduled_operating_window_guard
before insert on public.runs
for each row execute function public.enforce_scheduled_batch_operating_window();

drop trigger if exists dispatch_request_scheduled_operating_window_guard on public.dispatch_request;
create trigger dispatch_request_scheduled_operating_window_guard
before insert on public.dispatch_request
for each row execute function public.enforce_scheduled_batch_operating_window();

comment on function public.enforce_scheduled_batch_operating_window() is
  '예약 배치의 실제 KST 실행 시각을 검증한다. intraday는 08:00~20:00, close는 19:30~20:00만 허용하며 manual은 우회한다.';

revoke execute on function public.enforce_scheduled_batch_operating_window() from public, anon, authenticated;
grant execute on function public.enforce_scheduled_batch_operating_window() to postgres, service_role;

-- Python CLI가 장외 자동 dispatch를 attempt 없이 terminal 처리할 수 있게 한다.
create or replace function public.reject_scheduled_dispatch(
  p_dispatch_request_id uuid,
  p_reason text
) returns jsonb
language plpgsql
security definer
set search_path = public
as $$
declare
  request_row public.dispatch_request;
  outbox_row public.dispatch_outbox;
begin
  if p_dispatch_request_id is null or p_reason is null or length(btrim(p_reason)) = 0 then
    raise exception using message = 'INVALID_SCHEDULED_DISPATCH_REJECTION';
  end if;
  select * into request_row
  from public.dispatch_request
  where dispatch_request_id = p_dispatch_request_id
  for share;
  if not found then raise exception using message = 'DISPATCH_REQUEST_NOT_FOUND'; end if;
  if request_row.requested_by <> 'system:scheduler' then
    raise exception using message = 'MANUAL_DISPATCH_REJECTION_FORBIDDEN';
  end if;
  select * into outbox_row
  from public.dispatch_outbox
  where dispatch_request_id = p_dispatch_request_id
  for update;
  if not found then raise exception using message = 'OUTBOX_NOT_FOUND'; end if;
  if outbox_row.status in ('completed', 'failed', 'dead_letter') then
    return jsonb_build_object('status', outbox_row.status, 'ignored', true, 'reason', p_reason);
  end if;
  if outbox_row.status not in ('queued', 'accepted') then
    raise exception using message = 'DISPATCH_ALREADY_STARTED';
  end if;
  update public.dispatch_outbox
  set status = 'failed', lease_token = null, lease_expires_at = null, updated_at = now()
  where outbox_id = outbox_row.outbox_id;
  return jsonb_build_object('status', 'failed', 'ignored', false, 'reason', p_reason);
end;
$$;

revoke execute on function public.reject_scheduled_dispatch(uuid, text) from public, anon, authenticated;
grant execute on function public.reject_scheduled_dispatch(uuid, text) to service_role;

commit;
