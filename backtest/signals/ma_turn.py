"""20이동평균선 변곡 매수 시그널

전략 흐름 (리셋 버전):
1. MA 각도가 우하향(⇦ eps)에서 우상향(> eps)으로 변곡되는 봉에서 매수
   - 각도는 k=angle_window(기본 10) 봉 간 일평균 수익률 기준 = 평탄화
2. 거래량 전일 대비 volume_mult 배 이상
3. 익절: 최근 high_lookback 봉 내 직전 고점 (없으면 take_profit_pct 고정)
4. 손절: 진입 전 stop_lookback 봉 내 최저 저가 (단, -max_stop_pct보다 깊으면 -max_stop_pct로 캡)
"""

from __future__ import annotations

from dataclasses import dataclass, field

import numpy as np
import pandas as pd

from ..indicators import angle_k, sma

from .double_wave import EntrySignal


@dataclass
class MaTurnParams:
    ma_window: int = 20  # 변곡 판단 이동평균 주기
    angle_window: int = 10  # 각도 측정 구간 (평탄화 10일)
    eps: float = 0.0  # 변곡 판단 임계 (각도 <= eps → > eps 전환 시 매수)
    stop_lookback: int = 3  # 손절가: 진입 전 n봉 내 최저 저가
    max_stop_pct: float = 10.0  # 손절 하한 캡: 이전 저점이 -n%보다 깊으면 -n%로 고정
    volume_mult: float = 1.0  # 거래량 배수: 직전 거래량 대비 n배 이상일 때만 매수
    take_profit_pct: float = 4.0  # 폴백 고정 익절 (%)
    high_lookback: int = 10  # 직전 고점 탐색 봉수 (익절가 = 이 구간 최고가)
    max_prev_drop_pct: float | None = None  # 변곡봉 전일대비 하락 한도: 이보다 깊이 하락하면 제외 (None이면 무제한)
    zc_ref_count: int = 0  # 미사용 (설계 여지)

    def as_dict(self) -> dict:
        return {
            "ma_window": self.ma_window,
            "angle_window": self.angle_window,
            "eps": self.eps,
            "stop_lookback": self.stop_lookback,
            "max_stop_pct": self.max_stop_pct,
            "volume_mult": self.volume_mult,
            "take_profit_pct": self.take_profit_pct,
            "high_lookback": self.high_lookback,
            "max_prev_drop_pct": self.max_prev_drop_pct,
        }


def detect_ma_turn(
    df: pd.DataFrame,
    params: MaTurnParams | None = None,
    ticker: str = "",
) -> list[EntrySignal]:
    """MA20 변곡 봉마다 매수 시그널 생성 (벡터화).

    각 변곡 봉에 대해 독립 시그널. 종목당 동시 보유는 엔진에서 관리.
    """
    params = params or MaTurnParams()
    need = params.ma_window + params.angle_window + 2
    if len(df) < need:
        return []

    close = df["Close"]
    high = df["High"]
    low = df["Low"]
    volume = df["Volume"]

    ma = sma(close, params.ma_window)
    ang = angle_k(ma, params.angle_window)

    ang_arr = ang.to_numpy()
    # 변곡: 전봉 ≤ eps, 당봉 > eps (유효 각도 필요)
    cond = np.full(len(df), False)
    prev = np.concatenate([[np.nan], ang_arr[:-1]])
    valid = ~np.isnan(ang_arr) & ~np.isnan(prev)
    cond[valid] = (prev[valid] <= params.eps) & (ang_arr[valid] > params.eps)
    # 거래량 전일 대비 volume_mult 배 이상
    vol_arr = volume.to_numpy().astype(float)
    prev_vol = np.concatenate([[np.nan], vol_arr[:-1]])
    cond &= vol_arr > prev_vol * params.volume_mult
    # 변곡봉 전일 대비 하락 한도: max_prev_drop_pct보다 깊이 하락하면 제외
    if params.max_prev_drop_pct is not None:
        close_arr_full = close.to_numpy()
        prev_close = np.concatenate([[np.nan], close_arr_full[:-1]])
        ret = (close_arr_full / prev_close - 1.0) * 100.0
        cond &= ret >= params.max_prev_drop_pct
    # 진입 후 최소 1봉은 판단 가능해야 함
    cond &= np.arange(len(df)) < len(df) - 1

    idx = df.index
    entry_prices = close.to_numpy()
    high_arr = high.to_numpy()
    signals: list[EntrySignal] = []
    for t in np.flatnonzero(cond):
        # 손절가: 진입 전 stop_lookback 봉 내 최저 저가, 단 -max_stop_pct 하한 캡
        lo = int(max(0, t - params.stop_lookback))
        stop_from_low = float(low.iloc[lo:t].min())
        entry_price = float(entry_prices[t])
        stop_cap = entry_price * (1.0 - params.max_stop_pct / 100.0)
        if stop_from_low > entry_price:
            # 역전(직전 저점이 진입가 위): 이미 깨진 지지선은 손절 근거가 될 수 없음
            # → 진입가 -max_stop_pct%로 책정 (역전을 그대로 두면 갭다운시 체결 불가·가상수익 발생)
            stop_price = round(entry_price * (1.0 - params.max_stop_pct / 100.0), 6)
        else:
            stop_price = round(max(stop_from_low, stop_cap), 6)
        # 익절가: 최근 high_lookback 봉 내 최고 고가가 진입가보다 높으면 그 고가,
        # 없으면(신고가 부근 진입) 고정 4% 익절
        hlo = int(max(0, t - params.high_lookback))
        prev_high = float(high_arr[hlo:t].max())
        if prev_high > entry_price:
            take_profit_price = round(prev_high, 6)
            take_profit_pct = None
        else:
            take_profit_price = None
            take_profit_pct = params.take_profit_pct
        signals.append(
            EntrySignal(
                ticker=ticker,
                date=idx[t],
                gc_date=idx[t],
                a_gc=0.0,
                price=entry_price,
                short_ma=float(ma.iloc[t]),
                long_ma=0.0,
                pullback_min=0.0,
                take_profit_pct=take_profit_pct,
                take_profit_price=take_profit_price,
                stop_price=stop_price,
            )
        )
    return signals