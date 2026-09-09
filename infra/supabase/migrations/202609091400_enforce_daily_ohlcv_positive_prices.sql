-- epic-3-retro-item-17: daily_ohlcv 가격 양수 invariant.
--
-- 기존 check는 NaN/±Infinity만 막았다. 0이나 음수 가격은 유한하므로 그대로 통과하는데,
-- 이 캐시의 close는 outcome 판정의 분모다 -- `detect_price_adjustment_suspension`의
-- gap 비율, TP/SL 판정의 손익률(`(exit-entry)/entry`)이 모두 가격으로 나눈다. close=0이
-- 한 행이라도 들어오면 division-by-zero이거나(더 나쁘게) 조용히 왜곡된 손익률이 장부에
-- append-only로 확정된다. 상장 종목의 가격은 정의상 양수이므로 DB 계약으로 고정한다.
--
-- volume은 0이 정상(거래정지·무거래일)이므로 음수만 막는다.
-- 적용 시점의 운영 daily_ohlcv는 0행이고 위반 행도 0건이므로 backfill이 필요 없다.
begin;

alter table public.daily_ohlcv
  add constraint daily_ohlcv_positive_prices
  check (open > 0 and high > 0 and low > 0 and close > 0);

alter table public.daily_ohlcv
  add constraint daily_ohlcv_nonnegative_volume
  check (volume >= 0);

comment on constraint daily_ohlcv_positive_prices on public.daily_ohlcv is
  'epic-3-retro-item-17: close는 outcome 손익률/조정 gap 계산의 분모다. 0·음수 가격을 DB에서 차단한다.';
comment on constraint daily_ohlcv_nonnegative_volume on public.daily_ohlcv is
  'volume 0은 정상(거래정지·무거래일)이고 음수만 불가능하다.';

commit;
