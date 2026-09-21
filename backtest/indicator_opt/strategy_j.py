"""전략 J(VWAP 지지) 계산 및 재현 백테스트.

일봉만 사용하므로 VWAP은 직전 vwap_window봉(당일 포함)의 롤링 거래량가중평균가로
정의한다: VWAP = Σ(TypicalPrice_i * Volume_i) / Σ(Volume_i), TypicalPrice = (H+L+C)/3.
기간변수(vwap_window)는 고정값이 아니라 탐색 대상이다.

진입 조건 (전부 만족):
    1. 전일 종가가 전일 VWAP 위에서 마감 (지지 추세 확인)
    2. 당일 저가가 당일 VWAP의 ±vwap_band_pct% 범위 안으로 들어옴 (VWAP 지지 테스트)
    3. 당일 종가가 당일 VWAP 위에서 마감 (지지 확인 후 반등 마감)

청산 (익일 1봉 보유):
    - 익절: 진입 종가 대비 take_profit_pct%(기본 3.0) 수익
    - 손절: 진입일 VWAP 대비 stop_loss_pct%(기본 5.0) 아래
    - max_holding_bars=1 → 익일 TP/SL 미도달 시 익일 종가로 강제 청산
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
class StrategyJParams:
    """전략 J(VWAP 지지)의 진입·청산 파라미터."""

    vwap_window: int = 20        # 롤링 VWAP 관측 기간 (봉) — 탐색 대상
    vwap_band_pct: float = 2.0   # 당일 저가가 VWAP ±이 %안에 들어와야 지지로 인정
    take_profit_pct: float = 3.0  # 익절: 진입 종가 대비 %
    stop_loss_pct: float = 5.0    # 손절: 진입일 VWAP 대비 %
    max_holding_bars: int | None = 1  # 익일 1봉 보유 후 강제 청산 (TP/SL 미도달 시)
    tp_first: bool = True         # 같은 봉 TP·SL 동시 도달 시 익절 우선
    cost_rate: float = 0.0005     # 편도 수수료+슬리피지

    def as_dict(self) -> dict[str, object]:
        return asdict(self)


STRATEGY_J_PARAMS = StrategyJParams()
CANDIDATE_A = STRATEGY_J_PARAMS


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


def _validate_params(params: StrategyJParams) -> None:
    if not isinstance(params, StrategyJParams):
        raise ValueError("params는 StrategyJParams여야 합니다")
    _validate_positive_integer("vwap_window", params.vwap_window)

    vwap_band_pct = _validate_finite_real("vwap_band_pct", params.vwap_band_pct)
    if not 0.0 < vwap_band_pct <= 50.0:
        raise ValueError("vwap_band_pct는 (0, 50] 범위여야 합니다")

    take_profit_pct = _validate_finite_real("take_profit_pct", params.take_profit_pct)
    stop_loss_pct = _validate_finite_real("stop_loss_pct", params.stop_loss_pct)
    if not 0.0 < take_profit_pct <= 100.0:
        raise ValueError("take_profit_pct은 (0, 100] 범위여야 합니다")
    if not 0.0 < stop_loss_pct < 100.0:
        raise ValueError("stop_loss_pct은 (0, 100) 범위여야 합니다")

    if not isinstance(params.tp_first, bool):
        raise ValueError("tp_first는 bool이어야 합니다")

    if params.max_holding_bars is not None:
        _validate_positive_integer("max_holding_bars", params.max_holding_bars)

    cost_rate = _validate_finite_real("cost_rate", params.cost_rate)
    if not 0.0 <= cost_rate < 1.0:
        raise ValueError("cost_rate은 [0, 1) 범위여야 합니다")


def validate_strategy_j_params(params: StrategyJParams) -> None:
    """전략 J 파라미터 계약을 외부 검증 코드에서도 사용할 수 있게 노출한다."""

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


def rolling_vwap(frame: pd.DataFrame, window: int) -> pd.Series:
    """직전 window봉(당일 포함)의 롤링 거래량가중평균가(VWAP)."""

    typical_price = (frame["High"] + frame["Low"] + frame["Close"]) / 3.0
    pv = typical_price * frame["Volume"]
    pv_sum = pv.rolling(window, min_periods=window).sum()
    volume_sum = frame["Volume"].rolling(window, min_periods=window).sum()
    return pv_sum / volume_sum.replace(0.0, np.nan)


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


def compute_strategy_j(
    frame: pd.DataFrame,
    params: StrategyJParams = STRATEGY_J_PARAMS,
) -> pd.Series:
    """전략 J(VWAP 지지) 진입 조건을 동일 인덱스의 bool 마스크로 계산한다."""

    _validate_frame(frame)
    _validate_params(params)

    close = frame["Close"]
    low = frame["Low"]
    vwap = rolling_vwap(frame, params.vwap_window)
    band = params.vwap_band_pct / 100.0

    # 1) 전일 종가가 전일 VWAP 위에서 마감
    prev_above = (close.shift(1) > vwap.shift(1)).fillna(False)
    # 2) 당일 저가가 당일 VWAP ±band% 범위 안 (지지 테스트)
    low_near_vwap = (
        (low >= vwap * (1.0 - band)) & (low <= vwap * (1.0 + band))
    ).fillna(False)
    # 3) 당일 종가가 당일 VWAP 위에서 마감
    close_above = (close > vwap).fillna(False)

    mask = prev_above & low_near_vwap & close_above & vwap.notna()
    return mask.fillna(False).astype(bool)


def strategy_j_signals(
    frame: pd.DataFrame,
    ticker: str = "",
    params: StrategyJParams = STRATEGY_J_PARAMS,
) -> list[SimpleSignal]:
    """전략 J 마스크를 종가 진입용 신호로 변환한다.

    종가 진입, 익절은 진입 종가 대비 take_profit_pct%, 손절가는 진입일 VWAP
    대비 stop_loss_pct% 아래로 고정한다.
    """

    mask = compute_strategy_j(frame, params)
    vwap = rolling_vwap(frame, params.vwap_window)
    return [
        SimpleSignal(
            ticker=ticker,
            date=frame.index[position],
            price=float(frame["Close"].iloc[position]),
            take_profit_pct=params.take_profit_pct,
            stop_price=float(vwap.iloc[position]) * (1.0 - params.stop_loss_pct / 100.0),
        )
        for position in np.flatnonzero(mask.to_numpy())
    ]


def run_strategy_j_backtest(
    data: dict[str, pd.DataFrame] | None = None,
    params: StrategyJParams = STRATEGY_J_PARAMS,
    start: pd.Timestamp | str | None = BASELINE_START,
    end: pd.Timestamp | str | None = BASELINE_END,
) -> dict[str, object]:
    """고정 관측창의 parquet 유니버스에서 전략 J를 재현 실행한다."""

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
            signals = strategy_j_signals(segment, ticker=ticker, params=params)
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
        "strategy": "J",
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
        f"전략 J | 시그널 {result['n_signals']} | 거래 {result['n_trades']} "
        f"({result['n_win']}승/{result['n_loss']}패) | "
        f"승률 {result['win_rate'] * 100:.1f}% | PF {result['profit_factor']:.2f} | "
        f"평균 {result['avg_return']:+.3f}% | 최대보유 청산 {result['max_hold_exits']}건"
    )


def main() -> None:
    parser = argparse.ArgumentParser(description="전략 J(VWAP 지지) baseline 백테스트")
    parser.add_argument(
        "--output", type=Path,
        default=RESULTS_DIR / "strategy_j_baseline.csv",
        help="요약 CSV 출력 경로",
    )
    parser.add_argument("--start", default=BASELINE_START.date().isoformat())
    parser.add_argument("--end", default=BASELINE_END.date().isoformat())
    parser.add_argument("--vwap-window", type=int, default=STRATEGY_J_PARAMS.vwap_window)
    args = parser.parse_args()
    params = StrategyJParams(vwap_window=args.vwap_window)
    result = run_strategy_j_backtest(params=params, start=args.start, end=args.end)
    print("=== 전략 J(VWAP 지지) ===")
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
