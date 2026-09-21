"""전략 K(장단기 이평 이격 + 단기 변곡) 계산 및 백테스트.

진입 조건 (전부 만족):
    1. 장기이평선(SMA long_window)의 각도(angle_k, long_angle_bars봉 기준, 도)가
       (long_angle_min, long_angle_max) 범위 — "작은 각도로 우상향" 필터
    2. 단기이평선(SMA short_window)과 장기이평선의 이격도
       (short_ma - long_ma) / long_ma * 100 의 절댓값이 deviation_pct% 이하
    3. 단기이평선의 최소제곱 기울기(slope_window봉 rolling linreg)가
       전일 <= 0 → 당일 > 0 으로 전환되는 변곡 시점 (우상향 변곡)
    4. 당일 종가로 매수

청산 (ATR 기반, engine.run_backtest 기본 경로):
    - 익절: entry + tp_atr * ATR(진입봉)
    - 손절: entry - sl_atr * ATR(진입봉)
    - max_holding_bars 지정 시 해당 봉 종가로 강제 청산 (기본 None = TP/SL만)
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
from ..indicators import angle_k, sma
from ..metrics import summarize
from ._signals import SimpleSignal
from .run import RESULTS_DIR

_OHLCV_COLUMNS = ("Open", "High", "Low", "Close", "Volume")
_PRICE_COLUMNS = ("Open", "High", "Low", "Close")
_MAX_WINDOW = 100_000
_TRADE_COLUMNS = (
    "ticker", "entry_date", "exit_date", "entry_price", "exit_price",
    "return_pct", "holding_bars", "exit_reason",
)
BASELINE_START = pd.Timestamp("2020-08-03")
BASELINE_END = pd.Timestamp("2026-09-15")


@dataclass(frozen=True)
class StrategyKParams:
    """전략 K(장단기 이평 이격 + 단기 변곡)의 진입·청산 파라미터."""

    long_window: int = 60         # 장기이평 기간 (탐색 대상)
    short_window: int = 20        # 단기이평 기간 (탐색 대상)
    long_angle_bars: int = 5      # 장기이평 각도 계산 구간 (angle_k의 k)
    long_angle_min: float = 0.1   # 장기이평 각도 하한 (도) — 최소 우상향
    long_angle_max: float = 3.0   # 장기이평 각도 상한 (도) — "작은 각도"로 제한
    deviation_pct: float = 5.0    # |단기이평-장기이평|/장기이평 상한 (%)
    slope_window: int = 5         # 단기이평 최소제곱 기울기 계산 구간
    tp_atr: float = 3.0           # 익절 = entry + tp_atr * ATR
    sl_atr: float = 2.0           # 손절 = entry - sl_atr * ATR
    atr_window: int = 14
    max_holding_bars: int | None = None  # None이면 TP/SL에만 의존
    cost_rate: float = 0.0005     # 편도 수수료+슬리피지
    tp_first: bool = False        # 같은 봉 TP·SL 동시 도달 시 익절 우선 여부

    def as_dict(self) -> dict[str, int | float | bool | None]:
        return asdict(self)


STRATEGY_K_PARAMS = StrategyKParams()
CANDIDATE_A = STRATEGY_K_PARAMS


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


def _validate_params(params: StrategyKParams) -> None:
    if not isinstance(params, StrategyKParams):
        raise ValueError("params는 StrategyKParams여야 합니다")

    _validate_positive_integer("long_window", params.long_window)
    _validate_positive_integer("short_window", params.short_window)
    if params.short_window >= params.long_window:
        raise ValueError("short_window는 long_window보다 작아야 합니다")

    _validate_positive_integer("long_angle_bars", params.long_angle_bars)
    if params.long_angle_bars >= params.long_window:
        raise ValueError("long_angle_bars는 long_window보다 작아야 합니다")

    long_angle_min = _validate_finite_real("long_angle_min", params.long_angle_min)
    long_angle_max = _validate_finite_real("long_angle_max", params.long_angle_max)
    if not 0.0 <= long_angle_min < long_angle_max <= 90.0:
        raise ValueError(
            "long_angle_min/long_angle_max는 0 <= min < max <= 90 범위여야 합니다"
        )

    deviation_pct = _validate_finite_real("deviation_pct", params.deviation_pct)
    if not 0.0 < deviation_pct <= 100.0:
        raise ValueError("deviation_pct는 (0, 100] 범위여야 합니다")

    slope_window = _validate_positive_integer("slope_window", params.slope_window)
    if slope_window < 2:
        raise ValueError("slope_window는 2 이상이어야 합니다")

    tp_atr = _validate_finite_real("tp_atr", params.tp_atr)
    sl_atr = _validate_finite_real("sl_atr", params.sl_atr)
    if tp_atr <= 0.0:
        raise ValueError("tp_atr은 0보다 커야 합니다")
    if sl_atr <= 0.0:
        raise ValueError("sl_atr은 0보다 커야 합니다")

    _validate_positive_integer("atr_window", params.atr_window)

    if params.max_holding_bars is not None:
        _validate_positive_integer("max_holding_bars", params.max_holding_bars)

    cost_rate = _validate_finite_real("cost_rate", params.cost_rate)
    if not 0.0 <= cost_rate < 1.0:
        raise ValueError("cost_rate은 [0, 1) 범위여야 합니다")

    if not isinstance(params.tp_first, bool):
        raise ValueError("tp_first는 bool이어야 합니다")


def validate_strategy_k_params(params: StrategyKParams) -> None:
    """전략 K 파라미터 계약을 외부 검증 코드에서도 사용할 수 있게 노출한다."""

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
    valid = (
        np.isfinite(frame.loc[:, _OHLCV_COLUMNS].to_numpy(dtype=float)).all(axis=1)
        & (prices > 0).all(axis=1).to_numpy()
        & (frame["Volume"] >= 0).to_numpy()
        & (frame["High"] >= frame["Low"]).to_numpy()
        & (frame["High"] >= frame["Open"]).to_numpy()
        & (frame["High"] >= frame["Close"]).to_numpy()
        & (frame["Low"] <= frame["Open"]).to_numpy()
        & (frame["Low"] <= frame["Close"]).to_numpy()
    )
    return pd.Series(valid, index=frame.index, dtype=bool)


def _valid_segments(frame: pd.DataFrame, valid_rows: pd.Series) -> list[pd.DataFrame]:
    """유효 행만 이어지는 구간을 분리해 invalid 행을 봉 연결로 취급하지 않는다."""

    positions = np.flatnonzero(valid_rows.to_numpy(dtype=bool))
    if len(positions) == 0:
        return []
    split_points = np.flatnonzero(np.diff(positions) > 1) + 1
    groups = np.split(positions, split_points)
    return [frame.iloc[group[0] : group[-1] + 1] for group in groups]


def _rolling_linreg_slope(series: pd.Series, window: int) -> pd.Series:
    """window봉 종가(또는 이평)에 대한 최소제곱 선형회귀 기울기 (rolling, 벡터화).

    t=0..window-1에 대해 회귀한 기울기를 window의 마지막 봉에 배치한다.
    m = Σ(t-t̄)(y-ȳ) / Σ(t-t̄)²
    """

    values = series.to_numpy(dtype=float)
    n = len(values)
    out = np.full(n, np.nan)
    if n < window:
        return pd.Series(out, index=series.index)

    x = np.arange(window, dtype=float)
    xm = x.mean()
    denom = float(((x - xm) ** 2).sum())

    finite = np.isfinite(values)
    # NaN이 섞인 window는 sliding_window_view가 그대로 전파하므로 결과가 NaN이 된다.
    view = np.lib.stride_tricks.sliding_window_view(values, window)
    valid_view = np.lib.stride_tricks.sliding_window_view(finite, window).all(axis=1)
    mean_y = np.where(valid_view, view.mean(axis=1), np.nan)
    slope = ((x - xm)[None, :] * (view - mean_y[:, None])).sum(axis=1) / denom
    out[window - 1 :] = np.where(valid_view, slope, np.nan)
    return pd.Series(out, index=series.index)


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


def compute_strategy_k(
    frame: pd.DataFrame,
    params: StrategyKParams = STRATEGY_K_PARAMS,
) -> pd.Series:
    """전략 K(장단기 이격 + 단기 변곡) 진입 조건을 동일 인덱스의 bool 마스크로 계산한다."""

    _validate_frame(frame)
    _validate_params(params)

    close = frame["Close"]
    long_ma = sma(close, params.long_window)
    short_ma = sma(close, params.short_window)

    # 1) 장기이평 각도(도)가 (long_angle_min, long_angle_max) 범위 — 작은 각도 우상향
    long_angle = angle_k(long_ma, params.long_angle_bars)
    angle_ok = (
        (long_angle >= params.long_angle_min) & (long_angle <= params.long_angle_max)
    ).fillna(False)

    # 2) 단기-장기 이격도 |short-long|/long 이 deviation_pct% 이내
    with np.errstate(divide="ignore", invalid="ignore"):
        deviation = (short_ma - long_ma) / long_ma * 100.0
    deviation_ok = (deviation.abs() <= params.deviation_pct).fillna(False)

    # 3) 단기이평 최소제곱 기울기가 전일 <=0 → 당일 >0 으로 전환 (우상향 변곡)
    short_slope = _rolling_linreg_slope(short_ma, params.slope_window)
    slope_turn_up = (
        (short_slope.shift(1) <= 0.0) & (short_slope > 0.0)
    ).fillna(False)

    mask = angle_ok & deviation_ok & slope_turn_up
    return mask.fillna(False).astype(bool)


def strategy_k_signals(
    frame: pd.DataFrame,
    ticker: str = "",
    params: StrategyKParams = STRATEGY_K_PARAMS,
) -> list[SimpleSignal]:
    """전략 K 마스크를 종가 진입용 신호로 변환한다.

    stop_price/take_profit을 지정하지 않으므로 engine.run_backtest가 기본
    ATR 기반 TP/SL(entry ± tp_atr/sl_atr * ATR)로 청산을 계산한다.
    """

    mask = compute_strategy_k(frame, params)
    return [
        SimpleSignal(
            ticker=ticker,
            date=frame.index[position],
            price=float(frame["Close"].iloc[position]),
        )
        for position in np.flatnonzero(mask.to_numpy())
    ]


def run_strategy_k_backtest(
    data: dict[str, pd.DataFrame] | None = None,
    params: StrategyKParams = STRATEGY_K_PARAMS,
    start: pd.Timestamp | str | None = BASELINE_START,
    end: pd.Timestamp | str | None = BASELINE_END,
) -> dict[str, object]:
    """고정 관측창의 parquet 유니버스에서 전략 K를 재현 실행한다."""

    data = load_all() if data is None else data
    _validate_params(params)
    start_ts = _parse_bound("start", start)
    end_ts = _parse_bound("end", end)
    _validate_bound_pair_timezones(start_ts, end_ts)
    if start_ts is not None and end_ts is not None and start_ts > end_ts:
        raise ValueError("start는 end보다 늦을 수 없습니다")

    trade_params = TradeParams(
        tp_atr=params.tp_atr,
        sl_atr=params.sl_atr,
        atr_window=params.atr_window,
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
            signals = strategy_k_signals(segment, ticker=ticker, params=params)
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
        "strategy": "K",
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
        f"전략 K | 시그널 {result['n_signals']} | 거래 {result['n_trades']} "
        f"({result['n_win']}승/{result['n_loss']}패) | "
        f"승률 {result['win_rate'] * 100:.1f}% | PF {result['profit_factor']:.2f} | "
        f"평균 {result['avg_return']:+.3f}% | 복리 {result['cum_return']:+.1f}% | "
        f"최대보유 청산 {result['max_hold_exits']}건"
    )


def main() -> None:
    parser = argparse.ArgumentParser(description="전략 K(장단기 이평 이격 + 단기 변곡) baseline 백테스트")
    parser.add_argument(
        "--output", type=Path,
        default=RESULTS_DIR / "strategy_k_baseline.csv",
        help="요약 CSV 출력 경로",
    )
    parser.add_argument("--start", default=BASELINE_START.date().isoformat())
    parser.add_argument("--end", default=BASELINE_END.date().isoformat())
    parser.add_argument("--long-window", type=int, default=STRATEGY_K_PARAMS.long_window)
    parser.add_argument("--short-window", type=int, default=STRATEGY_K_PARAMS.short_window)
    parser.add_argument("--long-angle-min", type=float, default=STRATEGY_K_PARAMS.long_angle_min)
    parser.add_argument("--long-angle-max", type=float, default=STRATEGY_K_PARAMS.long_angle_max)
    parser.add_argument("--deviation-pct", type=float, default=STRATEGY_K_PARAMS.deviation_pct)
    parser.add_argument("--slope-window", type=int, default=STRATEGY_K_PARAMS.slope_window)
    parser.add_argument("--tp-atr", type=float, default=STRATEGY_K_PARAMS.tp_atr)
    parser.add_argument("--sl-atr", type=float, default=STRATEGY_K_PARAMS.sl_atr)
    args = parser.parse_args()

    params = StrategyKParams(
        long_window=args.long_window,
        short_window=args.short_window,
        long_angle_min=args.long_angle_min,
        long_angle_max=args.long_angle_max,
        deviation_pct=args.deviation_pct,
        slope_window=args.slope_window,
        tp_atr=args.tp_atr,
        sl_atr=args.sl_atr,
    )
    result = run_strategy_k_backtest(params=params, start=args.start, end=args.end)
    print("=== 전략 K(장단기 이평 이격 + 단기 변곡) ===")
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
