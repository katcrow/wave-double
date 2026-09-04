from __future__ import annotations

from dataclasses import dataclass, field
from enum import StrEnum

import numpy as np
import pandas as pd

from .indicator_opt.combine_strategies import build_signals
from .indicators import atr
from .indicator_opt.strategy_d import (
    STRATEGY_D_PARAMS,
    compute_strategy_d,
)
from .indicator_opt.strategy_e import (
    STRATEGY_E_PARAMS,
    compute_strategy_e,
)
from domain.ohlcv_cache import MIN_HISTORY_TRADING_DAYS, OhlcvCacheStatus

_OHLCV_COLS = ("Open", "High", "Low", "Close", "Volume")
_STRATEGY_KEYS = ("A", "B", "C", "D", "E")
_STRATEGY_PARAMS: dict[str, dict[str, int | float]] = {
    "A": {
        "atr_window": 14,
        "take_profit_pct": 3.0,
        "stop_loss_pct": 3.0,
        "max_holding_bars": 30,
    },
    "B": {
        "atr_window": 14,
        "take_profit_pct": 3.0,
        "stop_loss_pct": 3.0,
        "max_holding_bars": 30,
    },
    "C": {
        "atr_window": 14,
        "take_profit_pct": 3.0,
        "stop_loss_pct": 3.0,
        "max_holding_bars": 30,
    },
    "D": STRATEGY_D_PARAMS.as_dict(),
    "E": STRATEGY_E_PARAMS.as_dict(),
}

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
    params_meta: dict[str, dict[str, int | float]] = field(default_factory=dict)

    @property
    def strategy_params(self) -> dict[str, dict[str, int | float]]:
        """전략별 파라미터 메타데이터의 의미가 드러나는 별칭."""

        return self.params_meta


def _check_non_finite_ohlvc(frame: pd.DataFrame) -> bool:
    if not isinstance(frame, pd.DataFrame):
        return True
    if any(col not in frame.columns for col in _OHLCV_COLS):
        return True
    for col in _OHLCV_COLS:
        try:
            s = frame[col].to_numpy(dtype=float)
        except (TypeError, ValueError):
            return True
        if not np.isfinite(s).all():
            return True
    return False


def _invalid_frame_reason(frame: pd.DataFrame) -> str | None:
    if not isinstance(frame, pd.DataFrame):
        return "OHLCV 입력은 DataFrame이어야 합니다"
    if frame.columns.has_duplicates:
        return "OHLCV 컬럼명은 중복될 수 없습니다"
    missing = [col for col in _OHLCV_COLS if col not in frame.columns]
    if missing:
        return f"OHLCV 컬럼이 없습니다: {', '.join(missing)}"
    if not isinstance(frame.index, pd.DatetimeIndex):
        return "OHLCV 인덱스는 DatetimeIndex여야 합니다"
    if not frame.index.is_monotonic_increasing or not frame.index.is_unique:
        return "OHLCV 인덱스는 중복 없는 오름차순이어야 합니다"
    if any(not pd.api.types.is_numeric_dtype(frame[col]) for col in _OHLCV_COLS):
        return "OHLCV 컬럼은 숫자형이어야 합니다"
    if _check_non_finite_ohlvc(frame):
        return "Non-finite value detected in OHLVC columns"
    return None


def _valid_ohlcv_rows(frame: pd.DataFrame) -> pd.Series:
    """관계가 유효한 행만 표시해 invalid 봉을 서로 연결하지 않는다."""

    values = frame.loc[:, _OHLCV_COLS]
    prices = values.loc[:, ("Open", "High", "Low", "Close")]
    valid = (
        np.isfinite(values.to_numpy(dtype=float)).all(axis=1)
        & (prices > 0).all(axis=1).to_numpy()
        & (values["Volume"] >= 0).to_numpy()
        & (values["High"] >= values["Low"]).to_numpy()
        & (values["High"] >= values["Open"]).to_numpy()
        & (values["High"] >= values["Close"]).to_numpy()
        & (values["Low"] <= values["Open"]).to_numpy()
        & (values["Low"] <= values["Close"]).to_numpy()
    )
    return pd.Series(valid, index=frame.index, dtype=bool)


def _valid_segments(frame: pd.DataFrame) -> list[pd.DataFrame]:
    valid_rows = _valid_ohlcv_rows(frame)
    positions = np.flatnonzero(valid_rows.to_numpy(dtype=bool))
    if len(positions) == 0:
        return []
    split_points = np.flatnonzero(np.diff(positions) > 1) + 1
    groups = np.split(positions, split_points)
    return [frame.iloc[group[0] : group[-1] + 1] for group in groups]


def _merge_segment_mask(
    target: pd.Series, segment: pd.DataFrame, mask: pd.Series
) -> None:
    if not isinstance(mask, pd.Series):
        raise TypeError("전략 계산 결과는 pandas Series여야 합니다")
    if not mask.index.equals(segment.index):
        raise ValueError("전략 계산 결과의 인덱스가 입력 구간과 일치하지 않습니다")
    if not pd.api.types.is_bool_dtype(mask.dtype):
        raise TypeError("전략 계산 결과는 bool Series여야 합니다")
    target.loc[segment.index] = mask.to_numpy(dtype=bool)


def _segmented_atr(frame: pd.DataFrame, segments: list[pd.DataFrame]) -> pd.Series:
    atr_series = pd.Series(np.nan, index=frame.index, dtype=float)
    for segment in segments:
        segment_atr = atr(
            segment["High"], segment["Low"], segment["Close"], window=14
        )
        atr_series.loc[segment.index] = segment_atr.reindex(segment.index).to_numpy()
    return atr_series


def _apply_atr_last_bar_filters(
    raw: dict[str, pd.Series], frame: pd.DataFrame,
    segments: list[pd.DataFrame],
    keys: tuple[str, ...],
) -> dict[str, pd.Series]:
    # invalid 행을 가로질러 ATR을 계산하지 않도록 유효 구간별로 계산한다.
    atr_series = _segmented_atr(frame, segments)
    terminal_indices = {segment.index[-1] for segment in segments if not segment.empty}
    result: dict[str, pd.Series] = {}
    for key in keys:
        mask = raw[key].reindex(frame.index).fillna(False).astype(bool).copy()
        mask.loc[list(terminal_indices)] = False
        atr_valid = atr_series.notna() & (atr_series > 0)
        result[key] = (mask & atr_valid).astype(bool)
    return result


def _error_result(
    ticker: str, strategy: str | None, exc: Exception
) -> StrategyResult:
    return StrategyResult(
        ticker=ticker,
        status=OhlcvCacheStatus.ERROR,
        signals={},
        error=StrategyError(
            code=StrategyErrorCode.SIGNAL_COMPUTE_ERROR,
            strategy=strategy,
            message=str(exc),
        ),
    )


def compute_abc(frame: pd.DataFrame, *, ticker: str = "") -> StrategyResult:
    if not isinstance(frame, pd.DataFrame):
        return _error_result(
            ticker, None, ValueError("OHLCV 입력은 DataFrame이어야 합니다")
        )
    invalid_reason = _invalid_frame_reason(frame)
    if invalid_reason is not None:
        return _error_result(
            ticker, None, ValueError(invalid_reason)
        )

    if len(frame) < MIN_HISTORY_TRADING_DAYS:
        return StrategyResult(
            ticker=ticker,
            status=OhlcvCacheStatus.INELIGIBLE_INSUFFICIENT_HISTORY,
            signals={},
            error=None,
        )

    segments = _valid_segments(frame)
    if not segments:
        return _error_result(
            ticker, None, ValueError("유효한 OHLCV 구간이 없습니다")
        )
    try:
        raw_a, raw_b, raw_c = build_signals(
            frame, 3.0, 3.0, ticker, strict=True
        )
        raw = {}
        for key, mask in zip(("A", "B", "C"), (raw_a, raw_b, raw_c)):
            validated = pd.Series(False, index=frame.index, dtype=bool)
            _merge_segment_mask(validated, frame, mask)
            raw[key] = validated
    except Exception as exc:
        return _error_result(ticker, None, exc)
    try:
        signals = _apply_atr_last_bar_filters(
            raw, frame, [frame], ("A", "B", "C")
        )
    except Exception as exc:
        return _error_result(ticker, None, exc)
    for key, calculator, params in (
        ("D", compute_strategy_d, STRATEGY_D_PARAMS),
        ("E", compute_strategy_e, STRATEGY_E_PARAMS),
    ):
        mask = pd.Series(False, index=frame.index, dtype=bool)
        try:
            for segment in segments:
                _merge_segment_mask(mask, segment, calculator(segment, params))
        except Exception as exc:
            return StrategyResult(
                ticker=ticker,
                status=OhlcvCacheStatus.ERROR,
                signals={},
                error=StrategyError(
                    code=StrategyErrorCode.SIGNAL_COMPUTE_ERROR,
                    strategy=key,
                    message=str(exc),
                ),
            )
        signals[key] = mask

    try:
        signals.update(
            _apply_atr_last_bar_filters(
                signals, frame, segments, ("D", "E")
            )
        )
        valid_rows = _valid_ohlcv_rows(frame)
        for key in _STRATEGY_KEYS:
            signals[key] = (signals[key] & valid_rows).astype(bool)
    except Exception as exc:
        return _error_result(ticker, None, exc)

    return StrategyResult(
        ticker=ticker,
        status=OhlcvCacheStatus.READY,
        signals=signals,
        error=None,
        params_meta={key: dict(value) for key, value in _STRATEGY_PARAMS.items()},
    )
