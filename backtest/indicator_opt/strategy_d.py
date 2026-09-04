"""전략 D(돌파3%기법) 계산 및 재현 백테스트."""

from __future__ import annotations

import argparse
import hashlib
from dataclasses import asdict, dataclass
from numbers import Integral, Real
from pathlib import Path

import numpy as np
import pandas as pd

from ..data.loader import load_all
from ..engine import EXIT_MAX_HOLD, TradeParams, run_backtest
from ..indicators import rsi, sma
from ..metrics import summarize
from ._signals import SimpleSignal
from .run import RESULTS_DIR

_OHLCV_COLUMNS = ("Open", "High", "Low", "Close", "Volume")
_PRICE_COLUMNS = ("Open", "High", "Low", "Close")
_MAX_WINDOW = 100_000
BASELINE_START = pd.Timestamp("2020-08-03")
BASELINE_END = pd.Timestamp("2026-08-27")


@dataclass(frozen=True)
class StrategyDParams:
    """전략 D 후보 A의 진입·청산 파라미터."""

    breakout_window: int = 20
    volume_window: int = 3
    volume_ratio_max: float = 0.95
    long_sma_window: int = 240
    rsi_period: int = 10
    rsi_smooth: int = 6
    rsi_threshold: float = 42.0
    rsi_min: float = 30.0
    take_profit_pct: float = 3.0
    stop_loss_pct: float = 5.0
    max_holding_bars: int = 20
    cost_rate: float = 0.0005

    def as_dict(self) -> dict[str, int | float]:
        return asdict(self)


STRATEGY_D_PARAMS = StrategyDParams()
CANDIDATE_A = STRATEGY_D_PARAMS


def _validate_finite_real(name: str, value: object) -> float:
    if isinstance(value, bool) or not isinstance(value, Real):
        raise ValueError(f"{name}은 유한한 실수여야 합니다")
    value = float(value)
    if not np.isfinite(value):
        raise ValueError(f"{name}은 유한한 실수여야 합니다")
    return value


def _validate_positive_integer(name: str, value: object) -> int:
    if isinstance(value, bool) or not isinstance(value, Integral):
        raise ValueError(f"{name}은 정수여야 합니다")
    value = int(value)
    if not 1 <= value <= _MAX_WINDOW:
        raise ValueError(f"{name}은 1~{_MAX_WINDOW} 범위여야 합니다")
    return value


def _validate_params(params: StrategyDParams) -> None:
    if not isinstance(params, StrategyDParams):
        raise ValueError("params는 StrategyDParams여야 합니다")
    for name in (
        "breakout_window", "volume_window", "long_sma_window",
        "rsi_period", "rsi_smooth", "max_holding_bars",
    ):
        _validate_positive_integer(name, getattr(params, name))

    volume_ratio_max = _validate_finite_real(
        "volume_ratio_max", params.volume_ratio_max
    )
    if not 0.0 < volume_ratio_max <= 1.0:
        raise ValueError("volume_ratio_max은 (0, 1] 범위여야 합니다")

    rsi_threshold = _validate_finite_real("rsi_threshold", params.rsi_threshold)
    rsi_min = _validate_finite_real("rsi_min", params.rsi_min)
    if not 0.0 <= rsi_min <= rsi_threshold <= 100.0:
        raise ValueError(
            "rsi_min과 rsi_threshold는 0~100 범위이고 min<=threshold여야 합니다"
        )

    take_profit_pct = _validate_finite_real(
        "take_profit_pct", params.take_profit_pct
    )
    stop_loss_pct = _validate_finite_real("stop_loss_pct", params.stop_loss_pct)
    if not 0.0 < take_profit_pct <= 100.0:
        raise ValueError("take_profit_pct은 (0, 100] 범위여야 합니다")
    if not 0.0 < stop_loss_pct <= 100.0:
        raise ValueError("stop_loss_pct은 (0, 100] 범위여야 합니다")

    cost_rate = _validate_finite_real("cost_rate", params.cost_rate)
    if not 0.0 <= cost_rate < 1.0:
        raise ValueError("cost_rate은 [0, 1) 범위여야 합니다")


def validate_strategy_d_params(params: StrategyDParams) -> None:
    """전략 D 파라미터 계약을 외부 검증 코드에서도 사용할 수 있게 노출한다."""

    _validate_params(params)


def _validate_frame(frame: pd.DataFrame) -> None:
    if not isinstance(frame, pd.DataFrame):
        raise ValueError("OHLCV 입력은 DataFrame이어야 합니다")
    if frame.columns.has_duplicates:
        raise ValueError("OHLCV 컬럼명은 중복될 수 없습니다")
    missing = [column for column in _OHLCV_COLUMNS if column not in frame.columns]
    if missing:
        raise ValueError(f"OHLCV 컬럼이 없습니다: {', '.join(missing)}")
    if not isinstance(frame.index, pd.DatetimeIndex):
        raise ValueError("OHLCV 인덱스는 DatetimeIndex여야 합니다")
    if not frame.index.is_monotonic_increasing or not frame.index.is_unique:
        raise ValueError("OHLCV 인덱스는 중복 없는 오름차순이어야 합니다")
    values = frame.loc[:, _OHLCV_COLUMNS].to_numpy(dtype=float)
    if not np.isfinite(values).all():
        raise ValueError("OHLCV에 유한하지 않은 값이 있습니다")
    prices = frame.loc[:, _PRICE_COLUMNS]
    if (prices <= 0).any().any():
        raise ValueError("OHLC 가격은 양수여야 합니다")
    if (frame["Volume"] < 0).any():
        raise ValueError("거래량은 음수일 수 없습니다")
    if (frame["High"] < frame["Low"]).any():
        raise ValueError("고가는 저가보다 작을 수 없습니다")
    if (
        (frame["High"] < frame["Open"])
        | (frame["High"] < frame["Close"])
        | (frame["Low"] > frame["Open"])
        | (frame["Low"] > frame["Close"])
    ).any():
        raise ValueError("OHLC 가격 관계가 유효하지 않습니다")


def _valid_ohlcv_rows(frame: pd.DataFrame) -> pd.Series:
    """baseline 입력에서 계산에 사용할 수 있는 행을 표시한다."""

    prices = frame.loc[:, _PRICE_COLUMNS]
    return (
        np.isfinite(frame.loc[:, _OHLCV_COLUMNS].to_numpy(dtype=float)).all(axis=1)
        & (prices > 0).all(axis=1).to_numpy()
        & (frame["Volume"] >= 0).to_numpy()
        & (frame["High"] >= frame["Low"]).to_numpy()
        & (frame["High"] >= frame["Open"]).to_numpy()
        & (frame["High"] >= frame["Close"]).to_numpy()
        & (frame["Low"] <= frame["Open"]).to_numpy()
        & (frame["Low"] <= frame["Close"]).to_numpy()
    )


def compute_strategy_d(
    frame: pd.DataFrame,
    params: StrategyDParams = STRATEGY_D_PARAMS,
) -> pd.Series:
    """후보 A의 전략 D 진입 조건을 동일 인덱스의 bool 마스크로 계산한다."""

    _validate_frame(frame)
    _validate_params(params)
    high = frame["High"]
    close = frame["Close"]
    volume = frame["Volume"]

    # 현재 봉 이전 N개 봉의 신고가를 돌파해야 한다.
    prior_high = high.shift(1).rolling(
        params.breakout_window, min_periods=params.breakout_window
    ).max()
    breakout = high > prior_high

    # 현재 봉을 포함한 W봉 최대 거래량이 0이거나 현재 거래량이 0이면 탈락한다.
    volume_max = volume.rolling(
        params.volume_window, min_periods=params.volume_window
    ).max()
    safe_volume_max = volume_max.where(volume_max > 0)
    accumulation = (volume > 0) & (
        (volume / safe_volume_max) < params.volume_ratio_max
    )

    below_long_sma = close < sma(close, params.long_sma_window)
    wilder_rsi = rsi(close, window=params.rsi_period)
    smooth_rsi = wilder_rsi.rolling(
        params.rsi_smooth, min_periods=params.rsi_smooth
    ).mean()
    rsi_breakout = (
        (smooth_rsi.shift(1) < params.rsi_threshold)
        & (smooth_rsi >= params.rsi_threshold)
        & (smooth_rsi >= params.rsi_min)
    )

    return (breakout & accumulation & below_long_sma & rsi_breakout).fillna(False).astype(bool)


def strategy_d_signals(
    frame: pd.DataFrame,
    ticker: str = "",
    params: StrategyDParams = STRATEGY_D_PARAMS,
) -> list[SimpleSignal]:
    """전략 D 마스크를 종가 진입용 고정 TP/SL 신호로 변환한다."""

    mask = compute_strategy_d(frame, params)
    return [
        SimpleSignal(
            ticker=ticker,
            date=frame.index[position],
            price=float(frame["Close"].iloc[position]),
            take_profit_pct=params.take_profit_pct,
            stop_price=float(frame["Close"].iloc[position])
            * (1.0 - params.stop_loss_pct / 100.0),
        )
        for position in np.flatnonzero(mask.to_numpy())
    ]


def run_strategy_d_backtest(
    data: dict[str, pd.DataFrame] | None = None,
    params: StrategyDParams = STRATEGY_D_PARAMS,
    start: pd.Timestamp | str | None = BASELINE_START,
    end: pd.Timestamp | str | None = BASELINE_END,
) -> dict[str, object]:
    """고정 관측창의 parquet 유니버스에서 전략 D를 재현 실행한다."""

    data = load_all() if data is None else data
    _validate_params(params)
    start_ts = pd.Timestamp(start) if start is not None else None
    end_ts = pd.Timestamp(end) if end is not None else None
    if start_ts is not None and end_ts is not None and start_ts > end_ts:
        raise ValueError("start는 end보다 늦을 수 없습니다")

    trade_params = TradeParams(
        cost_rate=params.cost_rate,
        max_holding_bars=params.max_holding_bars,
    )
    all_trades = []
    signal_count = 0
    digest = hashlib.sha256()
    n_tickers = 0
    invalid_ohlcv_rows = 0
    months = set()
    for ticker, frame in data.items():
        window = frame
        if start_ts is not None:
            window = window[window.index >= start_ts]
        if end_ts is not None:
            window = window[window.index <= end_ts]
        if window.empty:
            continue
        valid_rows = _valid_ohlcv_rows(window)
        invalid_ohlcv_rows += int((~valid_rows).sum())
        window = window.loc[valid_rows]
        if window.empty:
            continue
        n_tickers += 1
        months.update(window.index.to_period("M"))
        digest.update(ticker.encode("utf-8"))
        digest.update(pd.util.hash_pandas_object(window, index=True).to_numpy().tobytes())
        signals = strategy_d_signals(window, ticker=ticker, params=params)
        signal_count += len(signals)
        all_trades.extend(run_backtest(window, signals, trade_params, ticker=ticker))

    performance = summarize(all_trades)
    result = {
        "strategy": "D",
        "params": params.as_dict(),
        "data_window_start": str(start_ts.date()) if start_ts is not None else None,
        "data_window_end": str(end_ts.date()) if end_ts is not None else None,
        "n_tickers": n_tickers,
        "invalid_ohlcv_rows": invalid_ohlcv_rows,
        "data_fingerprint": digest.hexdigest(),
        "n_signals": signal_count,
        "monthly_frequency": round(len(all_trades) / len(months), 4) if months else 0.0,
        "trades": [trade.to_dict() for trade in all_trades],
        **performance.to_dict(),
    }
    result["max_hold_exits"] = sum(
        1 for trade in all_trades if trade.exit_reason == EXIT_MAX_HOLD
    )
    return result


def _baseline_row(result: dict[str, object]) -> dict[str, object]:
    """결과 CSV에 성과와 전략 파라미터를 함께 평탄화한다."""

    params = result["params"]
    if not isinstance(params, dict):
        raise ValueError("baseline 결과의 params가 dict가 아닙니다")
    row = {key: value for key, value in result.items() if key not in {"params", "trades"}}
    row.update({f"param_{key}": value for key, value in params.items()})
    return row


def _format_result(result: dict[str, object]) -> str:
    return (
        f"전략 D | 시그널 {result['n_signals']} | 거래 {result['n_trades']} "
        f"({result['n_win']}승/{result['n_loss']}패) | "
        f"승률 {result['win_rate'] * 100:.1f}% | PF {result['profit_factor']:.2f} | "
        f"평균 {result['avg_return']:+.3f}% | 최대보유 청산 {result['max_hold_exits']}건"
    )


def main() -> None:
    parser = argparse.ArgumentParser(description="전략 D(돌파3%기법) baseline 백테스트")
    parser.add_argument(
        "--output", type=Path,
        default=RESULTS_DIR / "strategy_d_baseline.csv",
        help="요약 CSV 출력 경로",
    )
    parser.add_argument("--start", default=BASELINE_START.date().isoformat())
    parser.add_argument("--end", default=BASELINE_END.date().isoformat())
    args = parser.parse_args()
    result = run_strategy_d_backtest(start=args.start, end=args.end)
    print("=== 전략 D(돌파3%기법) 후보 A ===")
    print(f"관측창: {result['data_window_start']} ~ {result['data_window_end']}")
    print(f"파라미터: {result['params']}")
    print(_format_result(result))
    args.output.parent.mkdir(parents=True, exist_ok=True)
    pd.DataFrame([_baseline_row(result)]).to_csv(args.output, index=False)
    trades_output = args.output.with_name(f"{args.output.stem}_trades.csv")
    pd.DataFrame(result["trades"]).to_csv(trades_output, index=False)
    print(f"저장: {args.output}")
    print(f"거래 상세 저장: {trades_output}")


if __name__ == "__main__":
    main()
