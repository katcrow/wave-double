from __future__ import annotations

from dataclasses import dataclass
from enum import StrEnum

import numpy as np
import pandas as pd

from .indicator_opt.combine_strategies import build_signals
from .indicators import atr
from domain.ohlcv_cache import MIN_HISTORY_TRADING_DAYS, OhlcvCacheStatus

_OHLCV_COLS = ("Open", "High", "Low", "Close", "Volume")

# TP/SL SL-우선 규칙: 같은 봉에서 목표가·손절가가 동시에 도달되면
# 손절(SL)을 먼저 처리한다. backtest.engine._exit_price_on_bar 가 단일 원천.
SL_PRIORITY: bool = True


class StrategyErrorCode(StrEnum):
    SIGNAL_COMPUTE_ERROR = "SIGNAL_COMPUTE_ERROR"


@dataclass(frozen=True)
class StrategyError:
    code: StrategyErrorCode
    strategy: str | None
    message: str


@dataclass(frozen=True)
class StrategyResult:
    ticker: str
    status: OhlcvCacheStatus
    signals: dict[str, pd.Series]
    error: StrategyError | None


def _check_non_finite_ohlvc(frame: pd.DataFrame) -> bool:
    for col in _OHLCV_COLS:
        s = frame[col].to_numpy()
        if not np.all(np.isfinite(s)):
            return True
    return False


def _apply_atr_last_bar_filters(
    raw: dict[str, pd.Series], frame: pd.DataFrame
) -> dict[str, pd.Series]:
    atr_series = atr(frame["High"], frame["Low"], frame["Close"], window=14)
    last_idx = len(frame) - 1
    result: dict[str, pd.Series] = {}
    for key in ("A", "B", "C"):
        mask = raw[key].copy()
        mask.iloc[last_idx] = False
        atr_valid = atr_series.notna() & (atr_series > 0)
        mask = mask & atr_valid
        result[key] = mask
    return result


def compute_abc(frame: pd.DataFrame, *, ticker: str = "") -> StrategyResult:
    if len(frame) < MIN_HISTORY_TRADING_DAYS:
        return StrategyResult(
            ticker=ticker,
            status=OhlcvCacheStatus.INELIGIBLE_INSUFFICIENT_HISTORY,
            signals={},
            error=None,
        )

    if _check_non_finite_ohlvc(frame):
        return StrategyResult(
            ticker=ticker,
            status=OhlcvCacheStatus.ERROR,
            signals={},
            error=StrategyError(
                code=StrategyErrorCode.SIGNAL_COMPUTE_ERROR,
                strategy=None,
                message="Non-finite value detected in OHLVC columns",
            ),
        )

    try:
        raw_a, raw_b, raw_c = build_signals(frame, 3.0, 3.0, ticker, strict=True)
        raw = {"A": raw_a, "B": raw_b, "C": raw_c}
        signals = _apply_atr_last_bar_filters(raw, frame)
    except Exception as exc:
        return StrategyResult(
            ticker=ticker,
            status=OhlcvCacheStatus.ERROR,
            signals={},
            error=StrategyError(
                code=StrategyErrorCode.SIGNAL_COMPUTE_ERROR,
                strategy=None,
                message=str(exc),
            ),
        )

    return StrategyResult(
        ticker=ticker,
        status=OhlcvCacheStatus.READY,
        signals=signals,
        error=None,
    )
