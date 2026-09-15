"""탐색용: 피벗 1차저항선(R1) 2일 연속 돌파 전략.

진입 조건 (Neo 요청, 2026-09-15):
1. 어제(t-1) 종가가 어제자 피벗 1차저항선(R1, t-2 데이터로 계산) 위에서 돌파 마감
2. 오늘(t) 종가도 **같은 R1**(어제자, 새로 계산한 오늘자 R1이 아님) 위에서 마감
   → 어제 뚫은 저항선을 오늘 지지선으로 삼아 유지하는지 확인 (저항→지지 전환 확인)
→ 오늘 종가에 매수

피벗 포인트(표준 공식, t-2 OHLC 기준 — 어제자 R1):
  Pivot = (High(t-2) + Low(t-2) + Close(t-2)) / 3
  R1    = 2 * Pivot - Low(t-2)

청산은 수익우선 분할청산(양음돌파패턴과 동일 엔진 재사용):
  다음 거래일 하루만 보유, +2% 절반매도 / +4% 나머지 절반매도 / 손절 -5% / 미도달 시 종가청산.
  익절 우선(같은 날 고가가 목표가에 닿았으면 저가의 손절 접촉 여부와 무관하게 익절 적용).

탐색적 실행이므로 결과는 backtest/results/scratch/ 아래에 저장한다 (results_dir 격리 규약).
"""

from __future__ import annotations

import argparse
from dataclasses import asdict, dataclass

import numpy as np
import pandas as pd

from ..data.loader import load_all
from ..metrics import summarize
from ..results_dir import scratch_root
from ._signals import SimpleSignal
from .strategy_custom_vol_breakout_pullback import (
    DEFAULT_PARTIAL_EXIT_PARAMS,
    PartialExitParams,
    run_partial_exit_backtest,
)

RESULTS_DIR = scratch_root()


@dataclass
class PivotR1BreakoutParams:
    def as_dict(self) -> dict:
        return asdict(self)


DEFAULT_PARAMS = PivotR1BreakoutParams()


def pivot_r1(df: pd.DataFrame) -> pd.Series:
    """전일 H/L/C 기준 표준 피벗 1차저항선(R1)."""
    prior_high = df["High"].shift(1)
    prior_low = df["Low"].shift(1)
    prior_close = df["Close"].shift(1)
    pivot = (prior_high + prior_low + prior_close) / 3.0
    return 2.0 * pivot - prior_low


def detect_signals(
    df: pd.DataFrame,
    ticker: str = "",
    params: PivotR1BreakoutParams = DEFAULT_PARAMS,
) -> list[SimpleSignal]:
    if len(df) < 3:
        return []

    # 어제(t-1)에 유효했던 R1(= t-2 데이터로 계산) 하나를 기준으로 이틀 모두 비교.
    # 오늘(t)은 새로 계산한 R1(t)이 아니라 "어제의 저항선"을 오늘 지지하는지 본다.
    r1_prev = pivot_r1(df).shift(1)
    close = df["Close"]
    cond = (close.shift(1) > r1_prev) & (close > r1_prev)
    cond = cond.fillna(False)

    close = df["Close"].to_numpy(dtype=float)
    return [
        SimpleSignal(ticker=ticker, date=df.index[i], price=float(close[i]))
        for i in np.flatnonzero(cond.to_numpy())
    ]


def run_strategy(
    data: dict[str, pd.DataFrame] | None = None,
    entry_params: PivotR1BreakoutParams = DEFAULT_PARAMS,
    exit_params: PartialExitParams = DEFAULT_PARTIAL_EXIT_PARAMS,
) -> dict[str, object]:
    data = load_all() if data is None else data
    all_trades = []
    signal_count = 0
    for ticker in sorted(data):
        frame = data[ticker]
        signals = detect_signals(frame, ticker=ticker, params=entry_params)
        signal_count += len(signals)
        all_trades.extend(
            run_partial_exit_backtest(frame, signals, exit_params, ticker=ticker)
        )

    all_trades.sort(key=lambda t: (t.entry_date, t.ticker, t.exit_date))
    perf = summarize(all_trades)
    return {
        "entry_params": entry_params.as_dict(),
        "exit_params": exit_params.as_dict(),
        "n_tickers": len(data),
        "n_signals": signal_count,
        "trades": all_trades,
        **perf.to_dict(),
    }


def _format_result(result: dict[str, object]) -> str:
    return (
        f"시그널 {result['n_signals']} | 거래 {result['n_trades']} "
        f"({result['n_win']}승/{result['n_loss']}패) | "
        f"승률 {result['win_rate'] * 100:.1f}% | PF {result['profit_factor']:.2f} | "
        f"평균 {result['avg_return']:+.3f}% | 단리누적 {result['total_return']:.2f}% | "
        f"MDD {result['max_drawdown']:.2f}% | 청산사유 {result['exit_counts']}"
    )


def parse_args() -> argparse.Namespace:
    ap = argparse.ArgumentParser(description="피벗 R1 2일연속돌파 전략 백테스트 (탐색용)")
    ap.add_argument("--tp1-pct", type=float, default=DEFAULT_PARTIAL_EXIT_PARAMS.tp1_pct)
    ap.add_argument("--tp2-pct", type=float, default=DEFAULT_PARTIAL_EXIT_PARAMS.tp2_pct)
    ap.add_argument(
        "--stop-loss-pct", type=float, default=DEFAULT_PARTIAL_EXIT_PARAMS.stop_loss_pct
    )
    return ap.parse_args()


def main() -> None:
    args = parse_args()
    exit_params = PartialExitParams(
        tp1_pct=args.tp1_pct, tp2_pct=args.tp2_pct, stop_loss_pct=args.stop_loss_pct
    )
    print(f"청산 파라미터: {exit_params.as_dict()}")
    result = run_strategy(exit_params=exit_params)
    print(_format_result(result))

    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    trades_df = pd.DataFrame([t.to_dict() for t in result["trades"]])
    if not trades_df.empty:
        trades_df.to_csv(RESULTS_DIR / "pivot_r1_breakout_trades.csv", index=False)
    summary_row = {k: v for k, v in result.items() if k != "trades"}
    pd.DataFrame([summary_row]).to_csv(
        RESULTS_DIR / "pivot_r1_breakout_summary.csv", index=False
    )
    print(f"\n결과 저장: {RESULTS_DIR}")


if __name__ == "__main__":
    main()
