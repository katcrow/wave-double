"""전략 F(가속·이평선 쌍바닥) 계산 및 재현 백테스트.

진입 조건 (모두 AND):
1. 로그가격 30봉 최소제곱 선형회귀 기울기가 5봉 전 대비
   min_slope_delta(0.004)만큼 가속 (가속 ≥ 0 의미: 상승각도 가파라짐)
2. 이평선(MA16)이 쌍바닥(국소 저점 2개, 높은 저점) 후 넥라인 상향 돌파
청산: TP 3% / SL 4%, 같은 봉 TP·SL 동시 도달 시 TP(이익) 우선.
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
from ..indicators import sma
from ..metrics import summarize
from ._signals import SimpleSignal, _double_bottom_signal, sig_angle_accel_ls
from .run import RESULTS_DIR

_OHLCV_COLUMNS = ("Open", "High", "Low", "Close", "Volume")
_PRICE_COLUMNS = ("Open", "High", "Low", "Close")
_MAX_WINDOW = 100_000
_TRADE_COLUMNS = (
    "ticker", "entry_date", "exit_date", "entry_price", "exit_price",
    "return_pct", "holding_bars", "exit_reason",
)
BASELINE_START = pd.Timestamp("2020-08-03")
BASELINE_END = pd.Timestamp("2026-08-27")


@dataclass(frozen=True)
class StrategyFParams:
    """전략 F의 진입·청산 파라미터."""

    slope_window: int = 30          # 로그가격 최소제곱 회귀 기간
    accel_window: int = 5           # 가속 비교 이전 봉수
    min_slope_delta: float = 0.004  # 최소 가속량 (일별 로그수익률 스케일)
    ma_db_window: int = 16          # 쌍바닥 판정 이평선 기간
    take_profit_pct: float = 3.0
    stop_loss_pct: float = 4.0
    tp_first: bool = True           # 같은 봉 TP·SL 동시 도달 시 익절 우선
    max_holding_bars: int | None = None
    cost_rate: float = 0.0005

    def as_dict(self) -> dict[str, object]:
        return asdict(self)


STRATEGY_F_PARAMS = StrategyFParams()


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


def _validate_params(params: StrategyFParams) -> None:
    if not isinstance(params, StrategyFParams):
        raise ValueError("params는 StrategyFParams여야 합니다")
    for name in (
        "slope_window", "accel_window", "ma_db_window",
    ):
        _validate_positive_integer(name, getattr(params, name))
    if params.slope_window <= params.accel_window:
        raise ValueError("slope_window는 accel_window보다 커야 합니다")

    min_slope_delta = _validate_finite_real("min_slope_delta", params.min_slope_delta)
    if not 0.0 < min_slope_delta:
        raise ValueError("min_slope_delta는 양수여야 합니다")

    take_profit_pct = _validate_finite_real(
        "take_profit_pct", params.take_profit_pct
    )
    stop_loss_pct = _validate_finite_real("stop_loss_pct", params.stop_loss_pct)
    if not 0.0 < take_profit_pct <= 100.0:
        raise ValueError("take_profit_pct은 (0, 100] 범위여야 합니다")
    if not 0.0 < stop_loss_pct < 100.0:
        raise ValueError("stop_loss_pct은 (0, 100) 범위여야 합니다")

    cost_rate = _validate_finite_real("cost_rate", params.cost_rate)
    if not 0.0 <= cost_rate < 1.0:
        raise ValueError("cost_rate은 [0, 1) 범위여야 합니다")

    tp_first = params.tp_first
    if not isinstance(tp_first, bool):
        raise ValueError("tp_first는 bool이어야 합니다")

    max_holding = params.max_holding_bars
    if max_holding is not None:
        if isinstance(max_holding, bool) or not isinstance(max_holding, Integral):
            raise ValueError("max_holding_bars은 정수여야 합니다")
        max_holding = int(max_holding)
        if not 1 <= max_holding <= _MAX_WINDOW:
            raise ValueError(f"max_holding_bars은 1~{_MAX_WINDOW} 범위여야 합니다")


def validate_strategy_f_params(params: StrategyFParams) -> None:
    """전략 F 파라미터 계약을 외부 검증 코드에서도 사용할 수 있게 노출한다."""

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
    """baseline 입력에서 계산에 사용할 수 있는 행을 표시한다."""

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


def _valid_segments(
    frame: pd.DataFrame, valid_rows: pd.Series
) -> list[pd.DataFrame]:
    """유효 행만 이어지는 구간을 분리해 invalid 행을 봉 연결로 취급하지 않는다."""

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
    frame: pd.DataFrame,
    start: pd.Timestamp | None,
    end: pd.Timestamp | None,
) -> None:
    index_timezone = _timezone_label(frame.index.tz)
    for name, bound in (("start", start), ("end", end)):
        if bound is None:
            continue
        bound_timezone = _timezone_label(bound.tz)
        if bound_timezone != index_timezone:
            raise ValueError(
                f"{name}과 OHLCV 인덱스의 timezone이 일치하지 않습니다"
            )


def _validate_bound_pair_timezones(
    start: pd.Timestamp | None,
    end: pd.Timestamp | None,
) -> None:
    if start is not None and end is not None:
        if _timezone_label(start.tz) != _timezone_label(end.tz):
            raise ValueError("start와 end의 timezone이 일치하지 않습니다")


def _in_bounds(
    value: pd.Timestamp,
    start: pd.Timestamp | None,
    end: pd.Timestamp | None,
) -> bool:
    return (
        (start is None or value >= start)
        and (end is None or value <= end)
    )


def compute_strategy_f(
    frame: pd.DataFrame,
    params: StrategyFParams = STRATEGY_F_PARAMS,
) -> pd.Series:
    """기울기 가속 + 이평선 쌍바닥 두 조건의 전략 F 진입 마스크를 계산한다."""

    _validate_frame(frame)
    _validate_params(params)
    close = frame["Close"].astype(float)

    accel = sig_angle_accel_ls(
        frame,
        window=params.slope_window,
        accel_window=params.accel_window,
        min_slope_delta=params.min_slope_delta,
    )

    ma_arr = sma(close, params.ma_db_window).to_numpy(dtype=float)
    valid_from_mask = ~np.isnan(ma_arr)
    first_valid = int(np.argmax(valid_from_mask)) if valid_from_mask.any() else len(ma_arr)
    db_valid = _double_bottom_signal(ma_arr[first_valid:], float("inf"))
    ma_db_sig = np.concatenate([np.zeros(first_valid, dtype=bool), db_valid])
    ma_db_series = pd.Series(ma_db_sig, index=frame.index)

    return (accel.fillna(False) & ma_db_series).astype(bool)


def strategy_f_signals(
    frame: pd.DataFrame,
    ticker: str = "",
    params: StrategyFParams = STRATEGY_F_PARAMS,
) -> list[SimpleSignal]:
    """전략 F 마스크를 종가 진입용 고정 TP/SL 신호로 변환한다."""

    mask = compute_strategy_f(frame, params)
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


def run_strategy_f_backtest(
    data: dict[str, pd.DataFrame] | None = None,
    params: StrategyFParams = STRATEGY_F_PARAMS,
    start: pd.Timestamp | str | None = BASELINE_START,
    end: pd.Timestamp | str | None = BASELINE_END,
) -> dict[str, object]:
    """고정 관측창의 parquet 유니버스에서 전략 F를 재현 실행한다."""

    data = load_all() if data is None else data
    _validate_params(params)
    start_ts = _parse_bound("start", start)
    end_ts = _parse_bound("end", end)
    _validate_bound_pair_timezones(start_ts, end_ts)
    if start_ts is not None and end_ts is not None and start_ts > end_ts:
        raise ValueError("start는 end보다 늦을 수 없습니다")

    trade_params = TradeParams(
        cost_rate=params.cost_rate,
        max_holding_bars=params.max_holding_bars,
        tp_first=params.tp_first,
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
            signals = strategy_f_signals(segment, ticker=ticker, params=params)
            observed_signals = [
                signal
                for signal in signals
                if _in_bounds(signal.date, start_ts, end_ts)
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

    all_trades.sort(
        key=lambda trade: (trade.entry_date, trade.ticker, trade.exit_date)
    )

    performance = summarize(all_trades)
    result = {
        "strategy": "F",
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
    row = {
        key: value for key, value in result.items() if key not in {"params", "trades"}
    }
    row.update({f"param_{key}": value for key, value in params.items()})
    return row


def _format_result(result: dict[str, object]) -> str:
    return (
        f"전략 F | 시그널 {result['n_signals']} | 거래 {result['n_trades']} "
        f"({result['n_win']}승/{result['n_loss']}패) | "
        f"승률 {result['win_rate'] * 100:.1f}% | PF {result['profit_factor']:.2f} | "
        f"평균 {result['avg_return']:+.3f}% | 최대보유 청산 {result['max_hold_exits']}건"
    )


def main() -> None:
    parser = argparse.ArgumentParser(
        description="전략 F(가속·이평선 쌍바닥) baseline 백테스트"
    )
    parser.add_argument(
        "--output", type=Path,
        default=RESULTS_DIR / "strategy_f_baseline.csv",
        help="요약 CSV 출력 경로",
    )
    parser.add_argument("--start", default=BASELINE_START.date().isoformat())
    parser.add_argument("--end", default=BASELINE_END.date().isoformat())
    args = parser.parse_args()
    result = run_strategy_f_backtest(start=args.start, end=args.end)
    print("=== 전략 F(가속·이평선 쌍바닥) ===")
    print(f"관측창: {result['data_window_start']} ~ {result['data_window_end']}")
    print(f"파라미터: {result['params']}")
    print(_format_result(result))
    args.output.parent.mkdir(parents=True, exist_ok=True)
    pd.DataFrame([_baseline_row(result)]).to_csv(args.output, index=False)
    trades_output = args.output.with_name(f"{args.output.stem}_trades.csv")
    pd.DataFrame(result["trades"], columns=_TRADE_COLUMNS).to_csv(
        trades_output, index=False
    )
    print(f"저장: {args.output}")
    print(f"거래 상세 저장: {trades_output}")


if __name__ == "__main__":
    main()
