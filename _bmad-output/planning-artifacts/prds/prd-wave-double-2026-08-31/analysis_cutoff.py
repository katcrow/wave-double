"""컷오프 N 결정용 분석 (읽기 전용).

backtest/engine.py:82-169 의 run_backtest 를 그대로 미러링하되,
max_hold(N거래일) 시간청산을 추가해 N별 승률/PF 변화를 측정한다.
원 코드는 수정하지 않는다.

실행: uv run _bmad-output/planning-artifacts/prds/prd-wave-double-2026-08-31/analysis_cutoff.py
"""
from __future__ import annotations

import sys
from collections import Counter
from pathlib import Path

import numpy as np
import pandas as pd

sys.path.insert(0, str(Path(__file__).resolve().parents[4]))

from backtest.data.loader import load_all
from backtest.engine import TradeParams, atr
from backtest.indicator_opt.combine_strategies import build_signals
from backtest.indicator_opt.run import _to_signals

COST = TradeParams().cost_rate * 200.0  # 왕복 0.1%


def simulate(df, signals, ticker, max_hold=None):
    """engine.run_backtest 미러 + max_hold 시간청산.

    max_hold=None 이면 원본과 동일해야 한다(검증용).
    """
    if not signals or len(df) < 2:
        return []
    high = df["High"].to_numpy()
    low = df["Low"].to_numpy()
    close = df["Close"].to_numpy()
    atr_arr = atr(df["High"], df["Low"], df["Close"], window=TradeParams().atr_window).to_numpy()
    pos = {ts: i for i, ts in enumerate(df.index)}

    out = []
    last_exit = -1
    for sig in signals:
        if sig.date not in pos:
            continue
        e = pos[sig.date]
        if e <= last_exit or e >= len(df) - 1:
            continue
        if not np.isfinite(atr_arr[e]) or atr_arr[e] <= 0:
            continue

        entry = sig.price
        tp = entry * (1.0 + sig.take_profit_pct / 100.0)
        sl = sig.stop_price

        # 원본과 동일: 판정은 e+1 부터, 봉 내 SL 우선
        stop_t = len(df) if max_hold is None else min(len(df), e + 1 + max_hold)
        px = None
        reason = ""
        exit_idx = e
        for t in range(e + 1, stop_t):
            if low[t] <= sl:
                px, reason, exit_idx = sl, "sl", t
                break
            if high[t] >= tp:
                px, reason, exit_idx = tp, "tp", t
                break

        if px is None:
            if max_hold is not None and stop_t < len(df):
                # N거래일 경과 → 그 봉 종가로 시간청산
                exit_idx = stop_t - 1
                px, reason = close[exit_idx], "timeout"
            else:
                exit_idx = len(df) - 1
                px, reason = close[-1], "end"

        net = (px / entry - 1.0) * 100.0 - COST
        out.append((round(net, 4), exit_idx - e, reason))
        last_exit = exit_idx
    return out


def stats(trades):
    r = np.array([t[0] for t in trades])
    n = len(r)
    wins, losses = r[r > 0], r[r < 0]
    pf = wins.sum() / abs(losses.sum()) if losses.sum() != 0 else float("inf")
    return {
        "n": n,
        "win_rate": (r > 0).sum() / n * 100 if n else 0.0,
        "pf": pf,
        "total": r.sum(),
        "reasons": Counter(t[2] for t in trades),
    }


def main():
    data = load_all()
    sigs = {k: {} for k in ("a", "b", "c")}
    for ticker, df in data.items():
        a, b, c = build_signals(df, 3.0, 3.0, ticker)
        sigs["a"][ticker] = _to_signals(df, a, ticker, 3.0, 3.0)
        sigs["b"][ticker] = _to_signals(df, b, ticker, 3.0, 3.0)
        sigs["c"][ticker] = _to_signals(df, c, ticker, 3.0, 3.0)

    print("=" * 78)
    print("STEP 1 — 미러 검증 (max_hold=None 이 원본 baseline 과 일치하는가)")
    print("=" * 78)
    base = {}
    for name in ("a", "b", "c"):
        tr = []
        for ticker, df in data.items():
            tr += simulate(df, sigs[name].get(ticker, []), ticker, None)
        base[name] = tr
        s = stats(tr)
        print(f"  {name.upper()}: n={s['n']:4d}  승률={s['win_rate']:5.2f}%  "
              f"PF={s['pf']:.6f}  total={s['total']:.1f}  {dict(s['reasons'])}")
    print("  기대(combined_A_B_C.csv): A n=147 승률=68.71 PF=2.053997 | "
          "B n=541 68.95 2.076997 | C n=50 66.00 1.815939")

    print()
    print("=" * 78)
    print("STEP 2 — 보유봉 분포 (원본, 시간청산 없음)")
    print("=" * 78)
    for name in ("a", "b", "c"):
        hb = np.array([t[1] for t in base[name]])
        print(f"\n  전략 {name.upper()}  (n={len(hb)}, 평균={hb.mean():.2f}봉, "
              f"중앙값={int(np.median(hb))}, 최대={hb.max()})")
        print("    누적 청산 비율:")
        for n in (1, 2, 3, 4, 5, 7, 10, 15, 20, 30, 60):
            pct = (hb <= n).sum() / len(hb) * 100
            print(f"      N={n:3d} 이내 청산 {pct:6.2f}%   → N={n} 컷오프 시 "
                  f"TIMEOUT {100 - pct:6.2f}% ({(hb > n).sum()}건)")

    print()
    print("=" * 78)
    print("STEP 3 — 컷오프 N별 실전 지표 재계산 (백테스트 기대치와의 대조 편향)")
    print("=" * 78)
    for name in ("a", "b", "c"):
        s0 = stats(base[name])
        print(f"\n  전략 {name.upper()} — 컷오프 없음(백테스트 기대치): "
              f"승률 {s0['win_rate']:.2f}%  PF {s0['pf']:.4f}")
        print(f"    {'N':>4} | {'승률':>7} | {'PF':>7} | {'승률차':>7} | {'PF차':>8} | TIMEOUT")
        print(f"    {'-'*4}-+-{'-'*7}-+-{'-'*7}-+-{'-'*7}-+-{'-'*8}-+--------")
        for N in (3, 5, 7, 10, 15, 20, 30, 60):
            tr = []
            for ticker, df in data.items():
                tr += simulate(df, sigs[name].get(ticker, []), ticker, N)
            s = stats(tr)
            to = s["reasons"].get("timeout", 0)
            print(f"    {N:>4} | {s['win_rate']:6.2f}% | {s['pf']:7.4f} | "
                  f"{s['win_rate']-s0['win_rate']:+6.2f}p | {s['pf']-s0['pf']:+8.4f} | "
                  f"{to:4d}건 ({to/s['n']*100:5.2f}%)")


if __name__ == "__main__":
    main()
