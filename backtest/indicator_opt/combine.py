"""상위 지표 2개 조합 최적화

선정된 지표(RSI, CCI, IBS, Hull MA, ADX)를 2개씩 조합(신호 AND)하여
파라미터 그리드를 탐색 → 승률·수익률 최적 조합을 찾는다.

조합 규칙:
- 두 지표의 불 시그널 마스크를 AND 합성 (양쪽 모두 발동한 봉만 진입)
- 고정 TP/SL (기본 3%/3%)
- 월 평균 매매빈도 = 총 트레이드 / 월수(캘린더 월) 산출
"""

from __future__ import annotations

import argparse
import itertools
from concurrent.futures import ProcessPoolExecutor, as_completed
from pathlib import Path

import pandas as pd

from ..data.loader import load_all
from ..engine import TradeParams, run_backtest
from ..metrics import summarize
from ._signals import _REGISTRY, get_signal_fn, SimpleSignal
from .run import RESULTS_DIR, _to_signals

TOP5 = ["rsi", "cci", "ibs", "hma_turn", "adx"]

_SHARED: dict = {}


def _init_worker(shared: dict) -> None:
    global _SHARED
    _SHARED = shared


def _run_pair(name_a: str, pa: dict, name_b: str, pb: dict,
              tp_pct: float, sl_pct: float) -> dict:
    fna = get_signal_fn(name_a)
    fnb = get_signal_fn(name_b)
    sigs_map: dict[str, list] = {}
    total_idx = []
    for ticker, df in _SHARED["data"].items():
        try:
            ma = fna(df, **pa)
            mb = fnb(df, **pb)
            combined = ma.fillna(False) & mb.fillna(False)
        except Exception:
            continue
        sigs_map[ticker] = _to_signals(df, combined, ticker, tp_pct, sl_pct)
        total_idx.append(df.index)

    trades = []
    for ticker, df in _SHARED["data"].items():
        trades.extend(
            run_backtest(df, sigs_map.get(ticker, []), TradeParams(), ticker=ticker)
        )
    perf = summarize(trades)

    # 월 평균 매매빈도: 캘린더 월 수 기준
    all_dates = sorted(set(pd.Timestamp(d).to_period("M") for idx_list in total_idx
                           for d in idx_list))
    n_months = len(all_dates)
    monthly_freq = perf.n_trades / n_months if n_months else 0.0

    return {
        "ind_A": name_a,
        "params_A": str(pa),
        "ind_B": name_b,
        "params_B": str(pb),
        "tp_pct": tp_pct,
        "sl_pct": sl_pct,
        "n_trades": perf.n_trades,
        "n_win": perf.n_win,
        "win_rate": perf.win_rate,
        "avg_return": perf.avg_return,
        "total_return": perf.total_return,
        "cum_return": perf.cum_return,
        "profit_factor": perf.profit_factor,
        "max_drawdown": perf.max_drawdown,
        "avg_holding_bars": perf.avg_holding_bars,
        "tickers_hit": perf.tickers_hit,
        "n_months": n_months,
        "monthly_freq": round(monthly_freq, 2),
    }


def _pair_label(a: str, b: str) -> str:
    return f"{_REGISTRY[a]['label']}+{_REGISTRY[b]['label']}"


def main() -> None:
    ap = argparse.ArgumentParser(description="상위 지표 2개 조합 최적화")
    ap.add_argument("--indicators", default=",".join(TOP5),
                    help="조합 대상 지표 (쉼표 구분)")
    ap.add_argument("--min-trades", type=int, default=30)
    ap.add_argument("--workers", type=int, default=8)
    ap.add_argument("--tp", type=float, default=3.0)
    ap.add_argument("--sl", type=float, default=3.0)
    args = ap.parse_args()

    indicators = [x.strip() for x in args.indicators.split(",") if x.strip()]

    data = load_all()
    _SHARED["data"] = data
    print(f"종목 {len(data)}개, 고정 TP{args.tp}/SL{args.sl}, 워커 {args.workers}")
    print(f"조합 대상: {[ _REGISTRY[i]['label'] for i in indicators ]}")

    pairs = list(itertools.combinations(indicators, 2))
    print(f"쌍 조합: {len(pairs)}개\n")

    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    summary_rows = []

    for a, b in pairs:
        ga = _REGISTRY[a]["grid"]
        gb = _REGISTRY[b]["grid"]
        tasks = [(a, pa, b, pb, args.tp, args.sl) for pa in ga for pb in gb]

        with ProcessPoolExecutor(max_workers=args.workers,
                                 initializer=_init_worker,
                                 initargs=(_SHARED,)) as ex:
            futs = {ex.submit(_run_pair, *t): t for t in tasks}
            rows = [fut.result() for fut in as_completed(futs)]

        grid_df = pd.DataFrame(rows)
        grid_df.to_csv(RESULTS_DIR / f"combo_{a}_{b}.csv", index=False)

        filt = grid_df[grid_df["n_trades"] >= args.min_trades].copy()
        if filt.empty:
            best = grid_df.loc[grid_df["n_trades"].idxmax()]
        else:
            best = filt.sort_values(
                ["win_rate", "profit_factor", "n_trades"], ascending=False
            ).iloc[0]

        row = {
            "pair": f"{a}+{b}",
            "label": _pair_label(a, b),
            "params_A": best["params_A"],
            "params_B": best["params_B"],
            "n_combo": len(grid_df),
            "n_trades": best["n_trades"],
            "win_rate": best["win_rate"],
            "avg_return": best["avg_return"],
            "cum_return": best["cum_return"],
            "profit_factor": best["profit_factor"],
            "max_drawdown": best["max_drawdown"],
            "tickers_hit": best["tickers_hit"],
            "monthly_freq": best["monthly_freq"],
        }
        summary_rows.append(row)

        print(
            f"[{_pair_label(a, b):<24}] {row['params_A']:<34} × {row['params_B']:<34} "
            f"승률 {best['win_rate']*100:5.1f}% | 트레이드 {best['n_trades']:>3} "
            f"| PF {best['profit_factor']:5.2f} | 월평균 {best['monthly_freq']:5.2f}회 "
            f"| 평균 {best['avg_return']:6.3f}%"
        )

    summary = pd.DataFrame(summary_rows)
    summary.to_csv(RESULTS_DIR / "combo_summary.csv", index=False)
    print(f"\n저장: {RESULTS_DIR}/combo_summary.csv")


if __name__ == "__main__":
    main()
