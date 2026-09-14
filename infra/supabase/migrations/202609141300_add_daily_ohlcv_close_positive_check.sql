-- Deferred from story 3.5 code review (2026-09-03, low): daily_ohlcv.close가 0/음수를
-- 걸러내지 못해 전일 종가가 0이면 Story 3.5 갭 안전망(`v_prev_close <> 0` 가드)이 나눗셈
-- 예외 대신 감지를 조용히 건너뛴다. close에 양수 제약을 추가해 이 상태 자체가 저장되지
-- 않게 한다.
begin;

alter table public.daily_ohlcv
  add constraint daily_ohlcv_close_positive check (close > 0);

commit;
