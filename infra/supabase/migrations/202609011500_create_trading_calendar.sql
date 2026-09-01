-- KRX 거래일과 세션 시간의 단일 저장 계약 (AD-4, NFR-8)
create table if not exists public.trading_calendar (
  trading_day date primary key,
  is_open boolean not null,
  open_time time without time zone,
  close_time time without time zone,
  constraint trading_calendar_session_required
    check ((is_open = false and open_time is null and close_time is null)
      or (is_open = true and open_time is not null and close_time is not null)),
  constraint trading_calendar_session_order
    check (open_time is null or close_time is null or open_time < close_time)
);

comment on table public.trading_calendar is
  'KRX 거래일 캐시. 시간은 Asia/Seoul 현지 세션 시간이며, 판정 원천은 일봉 응답 존재 여부다.';
comment on column public.trading_calendar.trading_day is
  'Asia/Seoul 기준 거래일';
comment on column public.trading_calendar.open_time is
  '현지 장 시작 시각(반차 지원)';
comment on column public.trading_calendar.close_time is
  '현지 장 종료 시각(반차 지원)';
