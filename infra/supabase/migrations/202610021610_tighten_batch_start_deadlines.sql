-- 2026-10-02: 예약 배치는 KST 20:00 이후 새로 진입하지 않는다(Neo 확인). 실행이 20:00 전에
-- 끝나도록 시작 마감을 앞당긴다: intraday는 19:30 미만,
-- close는 19:30 이상 19:50 미만만 허용한다(정상 슬롯 19:10 intraday, 19:40 close는 그대로 통과).
-- 이미 진행 중인 실행은 20:00을 넘겨도 마무리하며, 20:00 이후 새 진입만 막는다.
-- 202610021000_enforce_batch_operating_window.sql 본문을 그대로 두고 창 경계만 바꾼다.
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
    allowed := now_kst >= time '08:00' and now_kst < time '19:30';
  elsif batch_kind = 'close' then
    allowed := now_kst >= time '19:30' and now_kst < time '19:50';
  end if;

  if not allowed then
    raise exception using
      message = 'SCHEDULE_OUTSIDE_OPERATING_WINDOW',
      detail = format('batch_kind=%s now_kst=%s logical_run_key=%s', batch_kind, now_kst, logical_run_key);
  end if;
  return new;
end;
$$;

comment on function public.enforce_scheduled_batch_operating_window() is
  '예약 배치의 실제 KST 시작 시각을 검증한다. intraday는 08:00~19:30, close는 19:30~19:50만 허용하며 manual은 우회한다. 진행 중인 실행은 20:00 이후에도 마무리한다.';

commit;
