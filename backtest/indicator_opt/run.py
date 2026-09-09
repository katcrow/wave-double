"""보조지표별 파라미터 최적화 실행기

각 보조지표의 파라미터를 그리드 탐색하여 "승률 최대화" 기준으로 최적 조합을
선택하고, 보조지표별 성과를 요약·저장한다.

파이프라인 (지표별):
    파라미터 조합 → 각 종목 OHLCV에 대해 시그널 생성 → 엔진 백테스트(ATR TP/SL)
    → 트레이드 집계(summarize) → 승률/수익률 등 지표 계산
"""

from __future__ import annotations

import argparse
from concurrent.futures import ProcessPoolExecutor, as_completed
from pathlib import Path

import numpy as np
import pandas as pd

from ..data.loader import load_all
from ..engine import TradeParams, run_backtest
from ..metrics import summarize
from ._signals import SimpleSignal, get_signal_fn, label, param_grid, param_names
from ..results_dir import results_root

RESULTS_DIR = results_root() / "indicator_opt"

_SHARED: dict = {}


def _init_worker(shared: dict) -> None:
    global _SHARED
    _SHARED = shared


def _to_signals(df, mask: pd.Series, ticker: str, tp_pct: float, sl_pct: float):
    """불 시그널 마스크 → EntrySignal 리스트.

    시그널 봉 종가 진입, 고정 익절(tp_pct%) / 고정 손절(sl_pct%) 지정.
    """
    idx = df.index[mask.fillna(False).to_numpy()]
    return [
        SimpleSignal(
            ticker=ticker,
            date=ts,
            price=float(df["Close"].loc[ts]),
            take_profit_pct=tp_pct,
            stop_price=float(df["Close"].loc[ts]) * (1.0 - sl_pct / 100.0),
        )
        for ts in idx
    ]


def _run_one(ind_name: str, params: dict, tp_pct: float, sl_pct: float) -> dict:
    fn = get_signal_fn(ind_name)
    sigs_map: dict[str, list] = {}
    for ticker, df in _SHARED["data"].items():
        try:
            mask = fn(df, **params)
        except Exception:
            continue
        sigs_map[ticker] = _to_signals(df, mask, ticker, tp_pct, sl_pct)

    trades = []
    for ticker, df in _SHARED["data"].items():
        trades.extend(
            run_backtest(df, sigs_map.get(ticker, []), TradeParams(), ticker=ticker)
        )
    perf = summarize(trades)
    return {
        "indicator": ind_name,
        "tp_pct": tp_pct,
        "sl_pct": sl_pct,
        **params,
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
        "exit_counts": perf.exit_counts,
    }


def optimize_indicator(
    ind_name: str,
    tp_pct: float = 3.0,
    sl_pct: float = 5.0,
    min_trades: int = 20,
    workers: int = 4,
) -> pd.DataFrame:
    """한 보조지표 전체 파라미터 그리드 탐색 → 결과 DataFrame (고정 TP/SL)"""
    grid = param_grid(ind_name)
    if not grid:
        return pd.DataFrame()

    tasks = [(ind_name, p, tp_pct, sl_pct) for p in grid]

    with ProcessPoolExecutor(
        max_workers=workers, initializer=_init_worker, initargs=(_SHARED,)
    ) as ex:
        futs = {ex.submit(_run_one, *t): t for t in tasks}
        rows = []
        for fut in as_completed(futs):
            rows.append(fut.result())

    df = pd.DataFrame(rows)
    df["label"] = label(ind_name)
    return df


def main() -> None:
    ap = argparse.ArgumentParser(description="보조지표 파라미터 최적화")
    ap.add_argument("--indicator", default="", help="특정 지표만 최적화 (빈 값 = 전체)")
    ap.add_argument("--min-trades", type=int, default=20, help="최소 트레이드 수 필터")
    ap.add_argument("--workers", type=int, default=6)
    ap.add_argument("--tp", type=float, default=3.0, help="고정 익절 percent")
    ap.add_argument("--sl", type=float, default=5.0, help="고정 손절 percent")
    args = ap.parse_args()

    tp_pct, sl_pct = args.tp, args.sl

    data = load_all()
    _SHARED["data"] = data
    print(f"종목 {len(data)}개, 고정 TP{tp_pct}%/SL{sl_pct}%, 워커 {args.workers}")

    RESULTS_DIR.mkdir(parents=True, exist_ok=True)

    from ._signals import _REGISTRY

    indicators = [args.indicator] if args.indicator else list(_REGISTRY.keys())
    summary_rows = []

    for ind in indicators:
        grid_rows = optimize_indicator(
            ind, tp_pct=tp_pct, sl_pct=sl_pct,
            min_trades=args.min_trades, workers=args.workers,
        )
        if grid_rows.empty:
            print(f"[{label(ind)}] 시그널 없음/그리드 없음")
            continue

        # 그리드별 전체 저장
        grid_csv = RESULTS_DIR / f"{ind}_grid.csv"
        grid_rows.to_csv(grid_csv, index=False)

        # 최적 파라미터 = 승률 최대 (최소 트레이드 확보 시)
        filt = grid_rows[grid_rows["n_trades"] >= args.min_trades].copy()
        if filt.empty:
            best = grid_rows.loc[grid_rows["n_trades"].idxmax()]
        else:
            # 승률 우선, 동률 시 ProfitFactor/트레이드 수 보정
            filt = filt.sort_values(
                ["win_rate", "profit_factor", "n_trades"], ascending=False
            )
            best = filt.iloc[0]

        names = param_names(ind)
        tp_sl_info = f"TP{tp_pct}%·SL{sl_pct}%"
        row = {
            "indicator": ind,
            "label": label(ind),
            "best_params": str({k: best.get(k) for k in names}),
            "tp_pct": tp_pct,
            "sl_pct": sl_pct,
            "n_combo": len(grid_rows),
            **{f"best_{c}": best.get(c) for c in
               ["n_trades", "win_rate", "avg_return", "cum_return",
                "profit_factor", "max_drawdown", "avg_holding_bars", "tickers_hit"]},
        }
        summary_rows.append(row)

        wr = best["win_rate"] * 100
        print(
            f"[{label(ind):<18}] 최적 {row['best_params']:<34} "
            f"({tp_sl_info:<10}) "
            f"승률 {wr:5.1f}% | 트레이드 {best['n_trades']:>3} | "
            f"PF {best['profit_factor']:5.2f} | 복리 {best['cum_return']:7.2f}% | "
            f"종목 {best['tickers_hit']}"
        )

    summary = pd.DataFrame(summary_rows)
    summary.to_csv(RESULTS_DIR / "summary_all.csv", index=False)
    print(f"\n저장: {RESULTS_DIR}")


if __name__ == "__main__":
    main()
