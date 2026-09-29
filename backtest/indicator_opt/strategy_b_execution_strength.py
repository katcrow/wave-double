"""전략 B(체결강도 변곡점 B) — 단독 전략, 중복 매수 없음, 익절2%/손절2%, 전체 유니버스 백테스트."""

from __future__ import annotations

import argparse
from pathlib import Path

import numpy as np
import pandas as pd

from ..data.loader import load_all
from ..engine import TradeParams, run_backtest
from ..indicators import execution_strength
from ..metrics import summarize
from .run import RESULTS_DIR

BASELINE_START = pd.Timestamp("2020-08-03")
BASELINE_END = pd.Timestamp("2026-08-27")


# ── 신호: B (연속 하락 후 반등) ─────────────────────────────────────────────────


def _sig_b(df: pd.DataFrame, decline_window: int = 3) -> pd.Series:
    """체결강도 B 변곡: 연속 하락 후 반등."""
    es = execution_strength(df["Close"], df["High"], df["Low"], df["Volume"], vol_window=20)
    diff = es.diff()
    decline_mask = diff.fillna(0) < 0
    prev_all_down = decline_mask.rolling(decline_window, min_periods=decline_window).sum().shift(1) >= (decline_window - 1)
    current_up = (diff > 0) & diff.notna()
    prev_down_window = decline_mask.rolling(decline_window - 1, min_periods=decline_window - 1).sum().shift(1) >= (decline_window - 1)
    return (current_up & prev_down_window).fillna(False).astype(bool)


def _sig_c(df: pd.DataFrame, window: int = 5) -> pd.Series:
    """체결강도 C 변곡: rolling 최저점(지역 최저) 후 상승 시작."""
    es = execution_strength(
        df["Close"], df["High"], df["Low"], df["Volume"], vol_window=20
    )
    rolling_min_prev = es.rolling(window=window, min_periods=window).min().shift(1)
    local_min_prev = (es.shift(1) == rolling_min_prev) & rolling_min_prev.notna()
    current_rising = (es > es.shift(1)) & es.shift(1).notna()
    return (local_min_prev & current_rising).fillna(False).astype(bool)


# ── 전략 파라미터 ─────────────────────────────────────────────────────────────

class StrategyBParams:
    def __init__(self, decline_window: int = 3, vol_window: int = 20,
                 tp_pct: float = 2.0, sl_pct: float = 2.0,
                 max_hold: int = 30, cost_rate: float = 0.0005,
                 obv_filter: str = "none"):  # "rising", "none"
        self.decline_window = decline_window
        self.vol_window = vol_window
        self.tp_pct = tp_pct
        self.sl_pct = sl_pct
        self.max_hold = max_hold
        self.cost_rate = cost_rate
        self.obv_filter = obv_filter

    def as_dict(self):
        return {
            "decline_window": self.decline_window,
            "vol_window": self.vol_window,
            "tp_pct": self.tp_pct,
            "sl_pct": self.sl_pct,
            "max_hold": self.max_hold,
            "cost_rate": self.cost_rate,
            "obv_filter": self.obv_filter,
        }


DEFAULT_PARAMS = StrategyBParams()


def run_strategy_b_backtest(
    data: dict[str, pd.DataFrame] | None = None,
    params: StrategyBParams = DEFAULT_PARAMS,
    start: pd.Timestamp | str | None = BASELINE_START,
    end: pd.Timestamp | str | None = BASELINE_END,
) -> dict:
    data = load_all() if data is None else data
    start_ts = pd.Timestamp(start) if start is not None else None
    end_ts = pd.Timestamp(end) if end is not None else None

    # 엔진: TP/SL 2% 고정, 수익우선 (tp_first=True)
    from ._signals import SimpleSignal
    trade_params = TradeParams(
        cost_rate=params.cost_rate,
        max_holding_bars=params.max_hold,
        tp_first=True,  # 수익우선
    )

    all_trades = []
    signal_count = 0
    for ticker in sorted(data):
        df = data[ticker]
        if not isinstance(df.index, pd.DatetimeIndex):
            continue
        df = df.sort_index()
        if start_ts is not None:
            df = df[df.index >= start_ts]
        if end_ts is not None:
            df = df[df.index <= end_ts]
        if len(df) < 10:
            continue

        mask = _sig_b(df, decline_window=params.decline_window) & _sig_c(df, window=params.decline_window)
        # OBV 상승조건 필터
        if params.obv_filter == "rising":
            from ..indicators import obv
            obv_series = obv(df["Close"], df["Volume"])
            mask = mask & (obv_series > obv_series.shift(1))
        signals = [
            SimpleSignal(
                ticker=ticker,
                date=df.index[i],
                price=float(df["Close"].iloc[i]),
                take_profit_pct=params.tp_pct,
                stop_price=float(df["Close"].iloc[i]) * (1.0 - params.sl_pct / 100.0),
            )
            for i in np.flatnonzero(mask.to_numpy())
        ]
        if start_ts is not None:
            signals = [s for s in signals if s.date >= start_ts]
        if end_ts is not None:
            signals = [s for s in signals if s.date <= end_ts]

        signal_count += len(signals)
        trades = run_backtest(df, signals, trade_params=trade_params, ticker=ticker)
        all_trades.extend(trades)

    all_trades.sort(key=lambda t: (t.entry_date, t.ticker, t.exit_date))
    perf = summarize(all_trades)
    result = {
        "strategy": "B_execution_strength",
        "params": params.as_dict(),
        "start": str(start_ts.date()) if start_ts else None,
        "end": str(end_ts.date()) if end_ts else None,
        "n_signals": signal_count,
        "n_trades": len(all_trades),
        "win_rate": round(perf.win_rate, 4) if hasattr(perf, 'win_rate') else None,
        "profit_factor": round(perf.profit_factor, 4) if hasattr(perf, 'profit_factor') else None,
        "trades": [t.to_dict() for t in all_trades],
    }
    # 추가 성과 요약 포함
    try:
        d = perf.to_dict()
        result.update({k: v for k, v in d.items() if k not in result})
    except Exception:
        pass
    return result


def main():
    parser = argparse.ArgumentParser(description="전략 B(체결강도 변곡점) 단독 백테스트")
    parser.add_argument("--output", type=Path, default=RESULTS_DIR / "strategy_b_baseline.csv")
    parser.add_argument("--start", default=BASELINE_START.date().isoformat())
    parser.add_argument("--end", default=BASELINE_END.date().isoformat())
    args = parser.parse_args()
    result = run_strategy_b_backtest(start=args.start, end=args.end)
    print(f"전략 B | 시그널 {result['n_signals']} | 거래 {result['n_trades']} "
          f"승률 {result.get('win_rate', 'N/A')} PF {result.get('profit_factor', 'N/A')}")
    args.output.parent.mkdir(parents=True, exist_ok=True)
    import pandas as pd
    pd.DataFrame([{
        "strategy": result["strategy"],
        "start": result["start"],
        "end": result["end"],
        "n_signals": result["n_signals"],
        "n_trades": result["n_trades"],
        **result.get("params", {}),
        **{k: v for k, v in result.items() if k not in {
            "strategy", "start", "end", "n_signals", "n_trades", "params", "trades"
        }},
    }]).to_csv(args.output, index=False)
    print(f"저장: {args.output}")


if __name__ == "__main__":
    main()
