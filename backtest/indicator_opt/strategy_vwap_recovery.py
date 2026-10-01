"""VWAP 상향 회복 전략의 신호와 유니버스 백테스트.

이 전략은 운영 A~I 태깅 계약과 분리된 재현용 백테스트 전용 모듈이다.
진입은 당일 포함 30봉 rolling VWAP 상향 회복, 양봉, VWAP 재시험,
직전 15봉 거래량 평균 대비 거래량 확인을 모두 만족하는 봉의 종가에 한다.
청산은 다음 봉부터 3% 익절, 4% 손절을 평가하고, 둘 다 닿으면 익절을
우선한다. 둘 다 닿지 않은 봉의 종가가 진입가보다 높을 때만 그 종가로
청산한다.
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
from ..engine import EXIT_SL, EXIT_TP, Trade
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
BASELINE_END = pd.Timestamp("2026-08-27")
EXIT_CLOSE_PROFIT = "close_profit"


@dataclass(frozen=True)
class StrategyVwapRecoveryParams:
    """VWAP 상향 회복 전략의 고정 기본 파라미터."""

    vwap_window: int = 30
    volume_window: int = 15
    volume_multiplier: float = 1.2
    retest_band_pct: float = 0.5
    take_profit_pct: float = 3.0
    stop_loss_pct: float = 4.0
    cost_rate: float = 0.001  # 왕복 비용 0.1% (비율)

    def as_dict(self) -> dict[str, object]:
        return asdict(self)


STRATEGY_VWAP_RECOVERY_PARAMS = StrategyVwapRecoveryParams()
# 이름이 긴 모듈 API를 사용하는 호출자와 짧은 별칭을 사용하는 테스트를 모두 지원한다.
VWAP_RECOVERY_PARAMS = STRATEGY_VWAP_RECOVERY_PARAMS
VwapRecoveryParams = StrategyVwapRecoveryParams
StrategyVWAPRecoveryParams = StrategyVwapRecoveryParams


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


def _validate_params(params: StrategyVwapRecoveryParams) -> None:
    if not isinstance(params, StrategyVwapRecoveryParams):
        raise ValueError("params는 StrategyVwapRecoveryParams여야 합니다")
    _validate_positive_integer("vwap_window", params.vwap_window)
    _validate_positive_integer("volume_window", params.volume_window)

    volume_multiplier = _validate_finite_real(
        "volume_multiplier", params.volume_multiplier
    )
    if volume_multiplier <= 0.0:
        raise ValueError("volume_multiplier는 양수여야 합니다")

    retest_band_pct = _validate_finite_real(
        "retest_band_pct", params.retest_band_pct
    )
    if not 0.0 < retest_band_pct <= 50.0:
        raise ValueError("retest_band_pct는 (0, 50] 범위여야 합니다")

    take_profit_pct = _validate_finite_real(
        "take_profit_pct", params.take_profit_pct
    )
    stop_loss_pct = _validate_finite_real(
        "stop_loss_pct", params.stop_loss_pct
    )
    if not 0.0 < take_profit_pct <= 100.0:
        raise ValueError("take_profit_pct은 (0, 100] 범위여야 합니다")
    if not 0.0 < stop_loss_pct < 100.0:
        raise ValueError("stop_loss_pct은 (0, 100) 범위여야 합니다")

    cost_rate = _validate_finite_real("cost_rate", params.cost_rate)
    if not 0.0 <= cost_rate < 1.0:
        raise ValueError("cost_rate은 [0, 1) 범위여야 합니다")


def validate_strategy_vwap_recovery_params(
    params: StrategyVwapRecoveryParams = STRATEGY_VWAP_RECOVERY_PARAMS,
) -> None:
    """전략 파라미터 계약을 외부 검증 코드에서도 사용할 수 있게 노출한다."""

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


def _valid_ohlcv_rows(frame: pd.DataFrame) -> pd.Series:
    """계산에 사용할 수 있는 OHLCV 행을 표시한다."""

    values = frame.loc[:, _OHLCV_COLUMNS].to_numpy(dtype=float)
    prices = frame.loc[:, _PRICE_COLUMNS]
    valid = (
        np.isfinite(values).all(axis=1)
        & (prices > 0).all(axis=1).to_numpy()
        & (frame["Volume"] >= 0).to_numpy()
        & (frame["High"] >= frame["Low"]).to_numpy()
        & (frame["High"] >= frame["Open"]).to_numpy()
        & (frame["High"] >= frame["Close"]).to_numpy()
        & (frame["Low"] <= frame["Open"]).to_numpy()
        & (frame["Low"] <= frame["Close"]).to_numpy()
    )
    return pd.Series(valid, index=frame.index, dtype=bool)


def _valid_segments(
    frame: pd.DataFrame, valid_rows: pd.Series
) -> list[pd.DataFrame]:
    """invalid 행을 봉 연결로 취급하지 않고 유효 구간을 나눈다."""

    positions = np.flatnonzero(valid_rows.to_numpy(dtype=bool))
    if len(positions) == 0:
        return []
    split_points = np.flatnonzero(np.diff(positions) > 1) + 1
    groups = np.split(positions, split_points)
    return [frame.iloc[group[0] : group[-1] + 1] for group in groups]


def rolling_vwap(frame: pd.DataFrame, window: int = 30) -> pd.Series:
    """당일 포함 rolling Typical Price 거래량가중 VWAP을 계산한다."""

    typical_price = (frame["High"] + frame["Low"] + frame["Close"]) / 3.0
    pv_sum = (typical_price * frame["Volume"]).rolling(
        window, min_periods=window
    ).sum()
    volume_sum = frame["Volume"].rolling(window, min_periods=window).sum()
    return pv_sum / volume_sum.replace(0.0, np.nan)


def _compute_on_valid_segment(
    frame: pd.DataFrame, params: StrategyVwapRecoveryParams
) -> pd.Series:
    vwap = rolling_vwap(frame, params.vwap_window)
    prior_volume_mean = frame["Volume"].shift(1).rolling(
        params.volume_window, min_periods=params.volume_window
    ).mean()
    band = params.retest_band_pct / 100.0

    recovery = (
        frame["Close"].shift(1) <= vwap.shift(1)
    ) & (frame["Close"] > vwap)
    bullish = frame["Close"] > frame["Open"]
    retest = (
        (frame["Low"] >= vwap * (1.0 - band))
        & (frame["Low"] <= vwap * (1.0 + band))
    )
    volume_confirmed = (
        (prior_volume_mean > 0.0)
        & (frame["Volume"] >= prior_volume_mean * params.volume_multiplier)
    )
    return (
        recovery & bullish & retest & volume_confirmed
        & vwap.notna() & prior_volume_mean.notna()
    ).fillna(False).astype(bool)


def compute_vwap_recovery(
    frame: pd.DataFrame,
    params: StrategyVwapRecoveryParams = STRATEGY_VWAP_RECOVERY_PARAMS,
) -> pd.Series:
    """네 가지 진입 조건의 동일 인덱스 bool 마스크를 계산한다."""

    _validate_frame_layout(frame)
    _validate_params(params)
    valid_rows = _valid_ohlcv_rows(frame)
    mask = pd.Series(False, index=frame.index, dtype=bool)
    for segment in _valid_segments(frame, valid_rows):
        segment_mask = _compute_on_valid_segment(segment, params)
        mask.loc[segment.index] = segment_mask
    return mask


compute_strategy_vwap_recovery = compute_vwap_recovery


def vwap_recovery_signals(
    frame: pd.DataFrame,
    ticker: str = "",
    params: StrategyVwapRecoveryParams = STRATEGY_VWAP_RECOVERY_PARAMS,
) -> list[SimpleSignal]:
    """신호 봉 종가 진입용 SimpleSignal 목록을 만든다."""

    mask = compute_vwap_recovery(frame, params)
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


strategy_vwap_recovery_signals = vwap_recovery_signals


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
        if _timezone_label(bound.tz) != index_timezone:
            raise ValueError(f"{name}과 OHLCV 인덱스의 timezone이 일치하지 않습니다")


def _validate_bound_pair_timezones(
    start: pd.Timestamp | None, end: pd.Timestamp | None
) -> None:
    if start is not None and end is not None:
        if _timezone_label(start.tz) != _timezone_label(end.tz):
            raise ValueError("start와 end의 timezone이 일치하지 않습니다")


def _in_bounds(
    value: pd.Timestamp,
    start: pd.Timestamp | None,
    end: pd.Timestamp | None,
) -> bool:
    return (start is None or value >= start) and (end is None or value <= end)


def run_vwap_recovery(
    frame: pd.DataFrame,
    signals: list[SimpleSignal],
    params: StrategyVwapRecoveryParams = STRATEGY_VWAP_RECOVERY_PARAMS,
    ticker: str = "",
) -> list[Trade]:
    """한 종목의 VWAP recovery 거래를 실행한다.

    신호 봉은 청산 평가에서 제외한다. 끝까지 TP/SL 또는 수익 종가가
    발생하지 않은 포지션은 완료 거래가 아니므로 결과에 넣지 않는다.
    """

    _validate_frame_layout(frame)
    _validate_params(params)
    if not signals or len(frame) < 2:
        return []
    if not _valid_ohlcv_rows(frame).all():
        raise ValueError("run_vwap_recovery에는 유효한 OHLCV 구간만 전달해야 합니다")

    date_to_pos = {timestamp: position for position, timestamp in enumerate(frame.index)}
    high = frame["High"].to_numpy(dtype=float)
    low = frame["Low"].to_numpy(dtype=float)
    close = frame["Close"].to_numpy(dtype=float)
    trades: list[Trade] = []
    last_exit_idx = -1

    for signal in sorted(signals, key=lambda item: item.date):
        if signal.ticker and ticker and signal.ticker != ticker:
            continue
        if signal.date not in date_to_pos:
            continue
        entry_idx = date_to_pos[signal.date]
        if entry_idx <= last_exit_idx or entry_idx >= len(frame) - 1:
            continue

        try:
            entry_price = float(signal.price)
        except (TypeError, ValueError):
            continue
        if not np.isfinite(entry_price) or entry_price <= 0.0:
            continue
        take_profit = entry_price * (1.0 + params.take_profit_pct / 100.0)
        stop_loss = entry_price * (1.0 - params.stop_loss_pct / 100.0)
        exit_price: float | None = None
        exit_reason = ""
        exit_idx = entry_idx

        for evaluation_idx in range(entry_idx + 1, len(frame)):
            hit_tp = high[evaluation_idx] >= take_profit
            hit_sl = low[evaluation_idx] <= stop_loss
            if hit_tp:
                # 전략 계약은 같은 봉 TP/SL 동시 도달도 TP-first다.
                exit_price, exit_reason = take_profit, EXIT_TP
            elif hit_sl:
                exit_price, exit_reason = stop_loss, EXIT_SL
            elif close[evaluation_idx] > entry_price:
                exit_price, exit_reason = close[evaluation_idx], EXIT_CLOSE_PROFIT
            if exit_reason:
                exit_idx = evaluation_idx
                break

        if exit_price is None:
            # 데이터 끝까지 보유한 미완료 포지션도 이후 신호를 막아
            # 종목별 동시 보유 금지 계약을 유지한다.
            last_exit_idx = len(frame) - 1
            continue

        gross_return = (exit_price / entry_price - 1.0) * 100.0
        net_return = gross_return - params.cost_rate * 100.0
        trades.append(
            Trade(
                ticker=signal.ticker or ticker,
                entry_date=signal.date,
                exit_date=frame.index[exit_idx],
                entry_price=entry_price,
                exit_price=float(exit_price),
                return_pct=round(net_return, 4),
                holding_bars=exit_idx - entry_idx,
                exit_reason=exit_reason,
            )
        )
        last_exit_idx = exit_idx

    return trades


run_strategy_vwap_recovery = run_vwap_recovery


def run_vwap_recovery_backtest(
    data: dict[str, pd.DataFrame] | None = None,
    params: StrategyVwapRecoveryParams = STRATEGY_VWAP_RECOVERY_PARAMS,
    start: pd.Timestamp | str | None = BASELINE_START,
    end: pd.Timestamp | str | None = BASELINE_END,
) -> dict[str, object]:
    """일봉 parquet 유니버스를 대상으로 고정 관측창 백테스트를 실행한다."""

    data = load_all() if data is None else data
    _validate_params(params)
    start_ts = _parse_bound("start", start)
    end_ts = _parse_bound("end", end)
    _validate_bound_pair_timezones(start_ts, end_ts)
    if start_ts is not None and end_ts is not None and start_ts > end_ts:
        raise ValueError("start는 end보다 늦을 수 없습니다")

    all_trades: list[Trade] = []
    signal_count = 0
    digest = hashlib.sha256()
    n_tickers = 0
    invalid_ohlcv_rows = 0
    months: set[pd.Period] = set()

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
            signals = vwap_recovery_signals(segment, ticker=ticker, params=params)
            observed_signals = [
                signal for signal in signals
                if _in_bounds(signal.date, start_ts, end_ts)
            ]
            signal_count += len(observed_signals)
            all_trades.extend(
                trade
                for trade in run_vwap_recovery(
                    segment, observed_signals, params=params, ticker=ticker
                )
                if _in_bounds(trade.entry_date, start_ts, end_ts)
            )

    all_trades.sort(key=lambda trade: (trade.entry_date, trade.ticker, trade.exit_date))
    performance = summarize(all_trades)
    return {
        "strategy": "VWAP_RECOVERY",
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


run_strategy_vwap_recovery_backtest = run_vwap_recovery_backtest


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
        f"VWAP 상향 회복 | 시그널 {result['n_signals']} | 거래 {result['n_trades']} "
        f"({result['n_win']}승/{result['n_loss']}패) | "
        f"승률 {result['win_rate'] * 100:.1f}% | PF {result['profit_factor']:.2f} | "
        f"평균 {result['avg_return']:+.3f}%"
    )


def main() -> None:
    parser = argparse.ArgumentParser(description="VWAP 상향 회복 백테스트")
    parser.add_argument(
        "--output", type=Path,
        default=RESULTS_DIR / "strategy_vwap_recovery_baseline.csv",
        help="요약 CSV 출력 경로",
    )
    parser.add_argument("--start", default=BASELINE_START.date().isoformat())
    parser.add_argument("--end", default=BASELINE_END.date().isoformat())
    args = parser.parse_args()
    result = run_vwap_recovery_backtest(start=args.start, end=args.end)
    print("=== VWAP 상향 회복 ===")
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
