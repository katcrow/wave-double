"""전략 G(양음돌파패턴: 거래량돌파양봉+음봉풀백+고가돌파) 계산 및 재현 백테스트.

원 설계는 docs/양음돌파패턴.md — 1일 보유 + 2%/4% 분할익절 + 익절우선이었으나,
프로덕션 청산 규약(AD-5, SL_PRIORITY=True, 단일 TP%/SL%)에 맞춰
단일청산으로 근사했다: TP 5% / SL 5% / 최대보유 20일 (SL-우선).
기존 baseline 기록(필터 적용 전, 관측창 2020-08-03~2026-08-27): 시그널 131, 거래 125건
(73승/52패), 승률 58.4%, 평균 +0.740%, PF 1.35 (SL-우선).
"""

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
from ..metrics import summarize
from ._signals import SimpleSignal
from .run import RESULTS_DIR
from .strategy_custom_vol_breakout_pullback import _breakout_pullback_mask

_OHLCV_COLUMNS = ("Open", "High", "Low", "Close", "Volume")
_PRICE_COLUMNS = ("Open", "High", "Low", "Close")
_MAX_WINDOW = 100_000
_OVEREXTENSION_WINDOW = 5
_MAX_CLOSE_OVEREXTENSION_PCT = 5.0
_TRADE_COLUMNS = (
    "ticker", "entry_date", "exit_date", "entry_price", "exit_price",
    "return_pct", "holding_bars", "exit_reason",
)
BASELINE_START = pd.Timestamp("2020-08-03")
BASELINE_END = pd.Timestamp("2026-08-27")


@dataclass(frozen=True)
class StrategyGParams:
    """전략 G의 진입·청산 파라미터."""

    min_gain_pct: float = 7.0  # 돌파봉 최소 양봉 상승률 (%), (Close-Open)/Open
    vol_sma_window: int = 5  # 거래량 이평 기간 (돌파 판정 기준)
    max_pullback: int = 3  # 허용 풀백 음봉 최대 개수
    take_profit_pct: float = 5.0
    stop_loss_pct: float = 5.0
    max_holding_bars: int = 20
    cost_rate: float = 0.0005

    def as_dict(self) -> dict[str, int | float]:
        return asdict(self)


STRATEGY_G_PARAMS = StrategyGParams()


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


def _validate_params(params: StrategyGParams) -> None:
    if not isinstance(params, StrategyGParams):
        raise ValueError("params는 StrategyGParams여야 합니다")
    for name in ("vol_sma_window", "max_pullback", "max_holding_bars"):
        _validate_positive_integer(name, getattr(params, name))

    min_gain_pct = _validate_finite_real("min_gain_pct", params.min_gain_pct)
    if not 0.0 < min_gain_pct <= 100.0:
        raise ValueError("min_gain_pct은 (0, 100] 범위여야 합니다")

    take_profit_pct = _validate_finite_real("take_profit_pct", params.take_profit_pct)
    stop_loss_pct = _validate_finite_real("stop_loss_pct", params.stop_loss_pct)
    if not 0.0 < take_profit_pct <= 100.0:
        raise ValueError("take_profit_pct은 (0, 100] 범위여야 합니다")
    if not 0.0 < stop_loss_pct < 100.0:
        raise ValueError("stop_loss_pct은 (0, 100) 범위여야 합니다")

    cost_rate = _validate_finite_real("cost_rate", params.cost_rate)
    if not 0.0 <= cost_rate < 1.0:
        raise ValueError("cost_rate은 [0, 1) 범위여야 합니다")


def validate_strategy_g_params(params: StrategyGParams) -> None:
    """전략 G 파라미터 계약을 외부 검증 코드에서도 사용할 수 있게 노출한다."""

    _validate_params(params)


def _validate_frame_layout(frame: pd.DataFrame) -> None:
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


def _validate_frame(frame: pd.DataFrame) -> None:
    _validate_frame_layout(frame)
    numeric = frame.loc[:, _OHLCV_COLUMNS].apply(pd.to_numeric, errors="coerce")
    values = numeric.to_numpy(dtype=float)
    if not np.isfinite(values).all():
        raise ValueError("OHLCV에 유한하지 않은 값이 있습니다")
    prices = numeric.loc[:, _PRICE_COLUMNS]
    if (prices <= 0).any().any():
        raise ValueError("OHLC 가격은 양수여야 합니다")
    if (numeric["Volume"] < 0).any():
        raise ValueError("거래량은 음수일 수 없습니다")
    if (numeric["High"] < numeric["Low"]).any():
        raise ValueError("고가는 저가보다 작을 수 없습니다")
    if (
        (numeric["High"] < numeric["Open"])
        | (numeric["High"] < numeric["Close"])
        | (numeric["Low"] > numeric["Open"])
        | (numeric["Low"] > numeric["Close"])
    ).any():
        raise ValueError("OHLC 가격 관계가 유효하지 않습니다")


def _valid_ohlcv_rows(frame: pd.DataFrame) -> pd.Series:
    numeric = frame.loc[:, _OHLCV_COLUMNS].apply(pd.to_numeric, errors="coerce")
    prices = numeric.loc[:, _PRICE_COLUMNS]
    valid = (
        np.isfinite(numeric.to_numpy(dtype=float)).all(axis=1)
        & (prices > 0).all(axis=1).to_numpy()
        & (numeric["Volume"] >= 0).to_numpy()
        & (numeric["High"] >= numeric["Low"]).to_numpy()
        & (numeric["High"] >= numeric["Open"]).to_numpy()
        & (numeric["High"] >= numeric["Close"]).to_numpy()
        & (numeric["Low"] <= numeric["Open"]).to_numpy()
        & (numeric["Low"] <= numeric["Close"]).to_numpy()
    )
    return pd.Series(valid, index=frame.index, dtype=bool)


def _valid_segments(frame: pd.DataFrame, valid_rows: pd.Series) -> list[pd.DataFrame]:
    positions = np.flatnonzero(valid_rows.to_numpy(dtype=bool))
    if len(positions) == 0:
        return []
    split_points = np.flatnonzero(np.diff(positions) > 1) + 1
    groups = np.split(positions, split_points)
    return [frame.iloc[group[0] : group[-1] + 1] for group in groups]


def _parse_bound(name: str, value: pd.Timestamp | str | None) -> pd.Timestamp | None:
    if value is None:
        return None
    try:
        parsed = pd.Timestamp(value)
    except (TypeError, ValueError) as exc:
        raise ValueError(f"{name}은 유효한 timestamp여야 합니다") from exc
    if pd.isna(parsed):
        raise ValueError(f"{name}은 유효한 timestamp여야 합니다")
    return parsed


def _timezone_label(timezone: object) -> str | None:
    return None if timezone is None else str(timezone)


def _validate_bound_timezones(
    frame: pd.DataFrame, start: pd.Timestamp | None, end: pd.Timestamp | None
) -> None:
    index_timezone = _timezone_label(frame.index.tz)
    for name, bound in (("start", start), ("end", end)):
        if bound is None:
            continue
        bound_timezone = _timezone_label(bound.tz)
        if bound_timezone != index_timezone:
            raise ValueError(f"{name}과 OHLCV 인덱스의 timezone이 일치하지 않습니다")


def _validate_bound_pair_timezones(
    start: pd.Timestamp | None, end: pd.Timestamp | None
) -> None:
    if start is not None and end is not None:
        if _timezone_label(start.tz) != _timezone_label(end.tz):
            raise ValueError("start와 end의 timezone이 일치하지 않습니다")


def _in_bounds(
    value: pd.Timestamp, start: pd.Timestamp | None, end: pd.Timestamp | None
) -> bool:
    return (start is None or value >= start) and (end is None or value <= end)


def compute_strategy_g(
    frame: pd.DataFrame,
    params: StrategyGParams = STRATEGY_G_PARAMS,
) -> pd.Series:
    """양음돌파패턴과 5일 고점 대비 과열 필터를 적용한 진입 마스크."""

    _validate_frame(frame)
    _validate_params(params)

    if len(frame) < max(params.vol_sma_window, _OVEREXTENSION_WINDOW) + params.max_pullback + 2:
        return pd.Series(False, index=frame.index, dtype=bool)

    open_ = frame["Open"].to_numpy(dtype=float)
    high = frame["High"].to_numpy(dtype=float)
    close = frame["Close"].to_numpy(dtype=float)
    volume = frame["Volume"].to_numpy(dtype=float)
    vol_sma = (
        frame["Volume"]
        .rolling(params.vol_sma_window, min_periods=params.vol_sma_window)
        .mean()
        .shift(1)
        .to_numpy(dtype=float)
    )

    mask = _breakout_pullback_mask(
        open_, high, close, volume, vol_sma, params.min_gain_pct, params.max_pullback
    )
    recent_high = (
        frame["High"]
        .rolling(_OVEREXTENSION_WINDOW, min_periods=_OVEREXTENSION_WINDOW)
        .max()
        .shift(1)
        .to_numpy(dtype=float)
    )
    max_close = recent_high * (1.0 + _MAX_CLOSE_OVEREXTENSION_PCT / 100.0)
    # 십진 호가의 정확한 5% 경계가 이진 부동소수점 오차로 제외되지 않게 한다.
    boundary_tolerance = np.zeros_like(max_close)
    finite_limits = np.isfinite(max_close)
    boundary_tolerance[finite_limits] = np.spacing(max_close[finite_limits]) * 4.0
    mask &= np.isfinite(recent_high) & (close <= max_close + boundary_tolerance)
    return pd.Series(mask, index=frame.index, dtype=bool)


def strategy_g_signals(
    frame: pd.DataFrame,
    ticker: str = "",
    params: StrategyGParams = STRATEGY_G_PARAMS,
) -> list[SimpleSignal]:
    """전략 G 마스크를 종가 진입용 고정 TP/SL 신호로 변환한다."""

    mask = compute_strategy_g(frame, params)
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


def run_strategy_g_backtest(
    data: dict[str, pd.DataFrame] | None = None,
    params: StrategyGParams = STRATEGY_G_PARAMS,
    start: pd.Timestamp | str | None = BASELINE_START,
    end: pd.Timestamp | str | None = BASELINE_END,
) -> dict[str, object]:
    """고정 관측창의 parquet 유니버스에서 전략 G를 재현 실행한다."""

    data = load_all() if data is None else data
    _validate_params(params)
    start_ts = _parse_bound("start", start)
    end_ts = _parse_bound("end", end)
    _validate_bound_pair_timezones(start_ts, end_ts)
    if start_ts is not None and end_ts is not None and start_ts > end_ts:
        raise ValueError("start는 end보다 늦을 수 없습니다")

    trade_params = TradeParams(
        cost_rate=params.cost_rate, max_holding_bars=params.max_holding_bars
    )
    all_trades = []
    signal_count = 0
    digest = hashlib.sha256()
    n_tickers = 0
    invalid_ohlcv_rows = 0
    months = set()
    for ticker in sorted(data):
        frame = data[ticker]
        _validate_frame_layout(frame)
        _validate_bound_timezones(frame, start_ts, end_ts)
        valid_rows = _valid_ohlcv_rows(frame)
        invalid_ohlcv_rows += int((~valid_rows).sum())
        ticker_bytes = ticker.encode("utf-8")
        digest.update(len(ticker_bytes).to_bytes(4, "big"))
        digest.update(ticker_bytes)
        digest.update(pd.util.hash_pandas_object(frame, index=True).to_numpy().tobytes())

        observed_rows = valid_rows.copy()
        if start_ts is not None:
            observed_rows &= frame.index >= start_ts
        if end_ts is not None:
            observed_rows &= frame.index <= end_ts
        if observed_rows.any():
            n_tickers += 1
            months.update(frame.index[observed_rows].to_period("M"))

        for segment in _valid_segments(frame, valid_rows):
            signals = strategy_g_signals(segment, ticker=ticker, params=params)
            observed_signals = [
                signal for signal in signals if _in_bounds(signal.date, start_ts, end_ts)
            ]
            signal_count += len(observed_signals)
            segment_trades = run_backtest(
                segment, observed_signals, trade_params, ticker=ticker
            )
            all_trades.extend(
                trade
                for trade in segment_trades
                if _in_bounds(trade.entry_date, start_ts, end_ts)
            )

    all_trades.sort(key=lambda trade: (trade.entry_date, trade.ticker, trade.exit_date))

    performance = summarize(all_trades)
    result = {
        "strategy": "G",
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
    params = result["params"]
    if not isinstance(params, dict):
        raise ValueError("baseline 결과의 params가 dict가 아닙니다")
    row = {key: value for key, value in result.items() if key not in {"params", "trades"}}
    row.update({f"param_{key}": value for key, value in params.items()})
    return row


def _format_result(result: dict[str, object]) -> str:
    return (
        f"전략 G | 시그널 {result['n_signals']} | 거래 {result['n_trades']} "
        f"({result['n_win']}승/{result['n_loss']}패) | "
        f"승률 {result['win_rate'] * 100:.1f}% | PF {result['profit_factor']:.2f} | "
        f"평균 {result['avg_return']:+.3f}% | 최대보유 청산 {result['max_hold_exits']}건"
    )


def main() -> None:
    parser = argparse.ArgumentParser(description="전략 G(양음돌파패턴) baseline 백테스트")
    parser.add_argument(
        "--output", type=Path,
        default=RESULTS_DIR / "strategy_g_baseline.csv",
        help="요약 CSV 출력 경로",
    )
    parser.add_argument("--start", default=BASELINE_START.date().isoformat())
    parser.add_argument("--end", default=BASELINE_END.date().isoformat())
    args = parser.parse_args()
    result = run_strategy_g_backtest(start=args.start, end=args.end)
    print("=== 전략 G(양음돌파패턴) ===")
    print(f"관측창: {result['data_window_start']} ~ {result['data_window_end']}")
    print(f"파라미터: {result['params']}")
    print(_format_result(result))
    args.output.parent.mkdir(parents=True, exist_ok=True)
    pd.DataFrame([_baseline_row(result)]).to_csv(args.output, index=False)
    trades_output = args.output.with_name(f"{args.output.stem}_trades.csv")
    pd.DataFrame(result["trades"], columns=_TRADE_COLUMNS).to_csv(trades_output, index=False)
    print(f"저장: {args.output}")
    print(f"거래 상세 저장: {trades_output}")


if __name__ == "__main__":
    main()
