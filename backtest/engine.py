"""백테스트 엔진 — 진입 시그널 → ATR 기반 목표/손절 보유 → 청산

- 진입: 타점 봉 종가 (signal.price)
- 목표가: entry + tp_atr * ATR(진입 봉)
- 손절가: entry - sl_atr * ATR(진입 봉)
- 같은 봉에 목표·손절 모두 닿으면 손절 우선 (보수적)
- 종목당 동시 1포지션, 이전 청산 이후의 시그널만 진입
- 데이터 끝까지 청산되지 않으면 마지막 종가로 강제 청산 (reason="end")
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pandas as pd

from .indicators import atr
from .signals import EntrySignal

EXIT_TP = "tp"
EXIT_SL = "sl"
EXIT_END = "end"


@dataclass
class TradeParams:
    tp_atr: float = 3.0  # 목표가 = entry + n * ATR
    sl_atr: float = 2.0  # 손절가 = entry - m * ATR
    atr_window: int = 14
    cost_rate: float = 0.0005  # 편도 수수료+슬리피지

    def as_dict(self) -> dict:
        return {
            "tp_atr": self.tp_atr,
            "sl_atr": self.sl_atr,
            "atr_window": self.atr_window,
            "cost_rate": self.cost_rate,
        }


@dataclass
class Trade:
    ticker: str
    entry_date: pd.Timestamp
    exit_date: pd.Timestamp
    entry_price: float
    exit_price: float
    return_pct: float  # 비용 차감 후 실제 수익률 (%)
    holding_bars: int
    exit_reason: str  # tp / sl / end

    def to_dict(self) -> dict:
        return {
            "ticker": self.ticker,
            "entry_date": str(self.entry_date.date()),
            "exit_date": str(self.exit_date.date()),
            "entry_price": round(self.entry_price, 4),
            "exit_price": round(self.exit_price, 4),
            "return_pct": round(self.return_pct, 4),
            "holding_bars": self.holding_bars,
            "exit_reason": self.exit_reason,
        }


def _exit_price_on_bar(
    open_: float,
    high: float,
    low: float,
    close: float,
    tp: float,
    sl: float,
) -> tuple[float, str]:
    """봉 안에서 목표/손절 도달 판단. 손절 우선 (보수적)."""
    if low <= sl:
        return sl, EXIT_SL
    if high >= tp:
        return tp, EXIT_TP
    return close, ""  # 미도달


def run_backtest(
    df: pd.DataFrame,
    signals: list[EntrySignal],
    trade_params: TradeParams | None = None,
    ticker: str = "",
) -> list[Trade]:
    """한 종목의 백테스트 실행. df: index=DatetimeIndex, 컬럼 OHLCV."""
    trade_params = trade_params or TradeParams()
    if not signals or len(df) < 2:
        return []

    open_arr = df["Open"].to_numpy()
    high_arr = df["High"].to_numpy()
    low_arr = df["Low"].to_numpy()
    close_arr = df["Close"].to_numpy()
    atr_arr = atr(
        df["High"], df["Low"], df["Close"], window=trade_params.atr_window
    ).to_numpy()

    date_to_pos = {ts: i for i, ts in enumerate(df.index)}
    trades: list[Trade] = []
    last_exit_idx = -1  # 직전 청산 봉 위치 (이 봉 이후만 새 진입 가능)

    for sig in signals:
        if sig.ticker and ticker and sig.ticker != ticker:
            continue
        if sig.date not in date_to_pos:
            continue

        e = date_to_pos[sig.date]
        if e <= last_exit_idx:
            continue  # 아직 보유 중이거나 같은 봉에서 청산된 직후
        if e >= len(df) - 1:
            continue  # 진입 후 판단할 봉이 없음
        if not np.isfinite(atr_arr[e]) or atr_arr[e] <= 0:
            continue

        entry_price = sig.price
        # 고정 익절/손절 (시그널 지정) 또는 ATR 기반
        if sig.stop_price is not None and (
            sig.take_profit_pct is not None or sig.take_profit_price is not None
        ):
            if sig.take_profit_price is not None:
                tp = sig.take_profit_price
            else:
                tp = entry_price * (1.0 + sig.take_profit_pct / 100.0)
            sl = sig.stop_price
        else:
            tp = entry_price + trade_params.tp_atr * atr_arr[e]
            sl = entry_price - trade_params.sl_atr * atr_arr[e]

        exit_price: float | None = None
        exit_reason = ""
        exit_idx = e

        for t in range(e + 1, len(df)):
            px, reason = _exit_price_on_bar(
                open_arr[t], high_arr[t], low_arr[t], close_arr[t], tp, sl
            )
            if reason:
                exit_price, exit_reason = px, reason
                exit_idx = t
                break

        if exit_price is None:
            # 데이터 끝까지 미청산 → 마지막 종가 강제 청산
            exit_price = close_arr[-1]
            exit_reason = EXIT_END
            exit_idx = len(df) - 1

        gross = (exit_price / entry_price - 1.0) * 100.0
        net = gross - trade_params.cost_rate * 200.0  # 매수+매도 편도비용

        trades.append(
            Trade(
                ticker=sig.ticker or ticker,
                entry_date=sig.date,
                exit_date=df.index[exit_idx],
                entry_price=entry_price,
                exit_price=float(exit_price),
                return_pct=round(net, 4),
                holding_bars=exit_idx - e,
                exit_reason=exit_reason,
            )
        )
        last_exit_idx = exit_idx

    return trades