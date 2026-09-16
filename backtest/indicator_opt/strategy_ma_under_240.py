"""240이평 아래 단기 이평선 상향돌파 전략의 기간별 백테스트.

신호일 종가가 SMA240 아래이고 SMA20>SMA60인 상태에서, 선택한 SMA(3~120)를
전일 이하에서 당일 초과로 상향 돌파하면 종가 진입한다. 청산은 +3%/-3% 고정
TP/SL이며 같은 봉 동시 도달은 익절 우선이다.
"""

from __future__ import annotations

import argparse
from dataclasses import asdict, dataclass
from pathlib import Path

import numpy as np
import pandas as pd

from ..data.loader import load_all
from ..engine import TradeParams, run_backtest
from ..indicators import sma
from ._signals import sig_stoch_double_bottom
from ..metrics import summarize
from ..results_dir import scratch_root
from ._signals import SimpleSignal

RESULTS_DIR = scratch_root() / "ma_under_240"
BASELINE_START = pd.Timestamp("2020-08-03")
BASELINE_END = pd.Timestamp("2026-09-15")


@dataclass(frozen=True)
class MaUnder240Params:
    ma_min: int = 3
    ma_max: int = 120
    reference_ma: int = 240
    trend_fast_ma: int = 20
    trend_slow_ma: int = 60
    take_profit_pct: float = 3.0
    stop_loss_pct: float = 3.0
    cost_rate: float = 0.0005
    tp_first: bool = True
    stoch_threshold: float = 30.0

    def as_dict(self) -> dict[str, object]:
        return asdict(self)


def _validate_params(params: MaUnder240Params) -> None:
    if not isinstance(params, MaUnder240Params):
        raise ValueError("params는 MaUnder240Params여야 합니다")
    if not (1 <= params.ma_min <= params.ma_max <= 100_000):
        raise ValueError("ma_min/ma_max는 1~100000 범위의 오름차순이어야 합니다")
    for name in ("reference_ma", "trend_fast_ma", "trend_slow_ma"):
        value = getattr(params, name)
        if isinstance(value, bool) or not isinstance(value, int) or value < 1:
            raise ValueError(f"{name}은 1 이상의 정수여야 합니다")
    if params.trend_fast_ma >= params.trend_slow_ma:
        raise ValueError("trend_fast_ma는 trend_slow_ma보다 작아야 합니다")
    for name in ("take_profit_pct", "stop_loss_pct"):
        value = getattr(params, name)
        if not np.isfinite(value) or value <= 0 or value >= 100:
            raise ValueError(f"{name}은 0과 100 사이의 유한한 값이어야 합니다")
    if not np.isfinite(params.cost_rate) or not 0 <= params.cost_rate < 1:
        raise ValueError("cost_rate은 [0, 1) 범위여야 합니다")
    if not isinstance(params.tp_first, bool):
        raise ValueError("tp_first는 bool이어야 합니다")
    if not np.isfinite(params.stoch_threshold) or not 0 < params.stoch_threshold <= 100:
        raise ValueError("stoch_threshold는 (0, 100] 범위여야 합니다")


def _valid_segments(frame: pd.DataFrame) -> list[pd.DataFrame]:
    required = ("Open", "High", "Low", "Close", "Volume")
    if not isinstance(frame.index, pd.DatetimeIndex) or not frame.index.is_monotonic_increasing:
        raise ValueError("OHLCV 인덱스는 오름차순 DatetimeIndex여야 합니다")
    values = frame.loc[:, required].to_numpy(dtype=float)
    prices = frame.loc[:, ("Open", "High", "Low", "Close")]
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
    positions = np.flatnonzero(valid)
    if len(positions) == 0:
        return []
    groups = np.split(positions, np.flatnonzero(np.diff(positions) > 1) + 1)
    return [frame.iloc[group[0] : group[-1] + 1] for group in groups]


def strategy_ma_signals(
    frame: pd.DataFrame,
    ma_window: int,
    *,
    ticker: str = "",
    params: MaUnder240Params = MaUnder240Params(),
    stoch_db: pd.Series | None = None,
) -> list[SimpleSignal]:
    """선택한 단기 SMA의 상향 교차 신호를 계산한다."""

    if len(frame) <= 240:
        return []
    close = frame["Close"]
    selected = sma(close, ma_window)
    ma240 = sma(close, params.reference_ma)
    ma20 = sma(close, params.trend_fast_ma)
    ma60 = sma(close, params.trend_slow_ma)
    if stoch_db is None:
        stoch_db = sig_stoch_double_bottom(
            frame, k_period=5, d_period=3, threshold=params.stoch_threshold
        )
    stoch_db = stoch_db.reindex(frame.index).fillna(False).astype(bool)
    mask = (
        (close.shift(1) <= selected.shift(1))
        & (close > selected)
        & (close < ma240)
        & (ma20 > ma60)
        & stoch_db
    ).fillna(False).astype(bool)
    return [
        SimpleSignal(ticker=ticker, date=frame.index[i], price=float(close.iloc[i]),
                     take_profit_pct=params.take_profit_pct,
                     stop_price=float(close.iloc[i]) * (1.0 - params.stop_loss_pct / 100.0))
        for i in np.flatnonzero(mask.to_numpy())
    ]


def run_strategy_ma_backtest(
    data: dict[str, pd.DataFrame] | None = None,
    params: MaUnder240Params = MaUnder240Params(),
    *,
    start: pd.Timestamp | str | None = BASELINE_START,
    end: pd.Timestamp | str | None = BASELINE_END,
) -> dict[str, object]:
    """SMA 3~120 각각을 독립적으로 실행해 기간별 요약을 반환한다."""

    _validate_params(params)
    data = load_all() if data is None else data
    start_ts = pd.Timestamp(start) if start is not None else None
    end_ts = pd.Timestamp(end) if end is not None else None
    if start_ts is not None and end_ts is not None and start_ts > end_ts:
        raise ValueError("start는 end보다 늦을 수 없습니다")

    rows: list[dict[str, object]] = []
    trades_by_window: dict[int, list[dict[str, object]]] = {}
    for window in range(params.ma_min, params.ma_max + 1):
        all_trades = []
        signal_count = 0
        for ticker in sorted(data):
            for segment in _valid_segments(data[ticker]):
                stoch_db = sig_stoch_double_bottom(
                    segment, k_period=5, d_period=3, threshold=params.stoch_threshold
                )
                signals = strategy_ma_signals(
                    segment, window, ticker=ticker, params=params, stoch_db=stoch_db
                )
                signals = [s for s in signals if (start_ts is None or s.date >= start_ts) and (end_ts is None or s.date <= end_ts)]
                signal_count += len(signals)
                all_trades.extend(run_backtest(
                    segment, signals,
                    TradeParams(cost_rate=params.cost_rate, tp_first=params.tp_first),
                    ticker=ticker,
                ))
        all_trades.sort(key=lambda t: (t.entry_date, t.ticker, t.exit_date))
        performance = summarize(all_trades).to_dict()
        rows.append({"ma_window": window, "n_signals": signal_count, **performance})
        trades_by_window[window] = [dict(trade.to_dict(), ma_window=window) for trade in all_trades]
    return {"strategy": "MA_UNDER_240", "params": params.as_dict(), "summary": rows, "trades": trades_by_window}


def main() -> None:
    parser = argparse.ArgumentParser(description="240이평 아래 이평선 돌파 그리드 백테스트")
    parser.add_argument("--start", default=BASELINE_START.date().isoformat())
    parser.add_argument("--end", default=BASELINE_END.date().isoformat())
    args = parser.parse_args()
    result = run_strategy_ma_backtest(start=args.start, end=args.end)
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    pd.DataFrame(result["summary"]).to_csv(RESULTS_DIR / "summary.csv", index=False)
    trades = [trade for window in result["trades"].values() for trade in window]
    pd.DataFrame(trades).to_csv(RESULTS_DIR / "trades.csv", index=False)
    summary = pd.DataFrame(result["summary"])
    ranked = summary.sort_values(["profit_factor", "cum_return"], ascending=False).head(10)
    print("=== 240이평 아래 이평선 상향돌파 그리드 ===")
    print(ranked.to_string(index=False))
    print(f"\n요약 저장: {RESULTS_DIR / 'summary.csv'}")
    print(f"거래 저장: {RESULTS_DIR / 'trades.csv'}")


if __name__ == "__main__":
    main()
