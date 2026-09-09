"""파라미터 그리드 탐색 — 백테스트 최적 파라미터 도출

효율 설계:
- 시그널 검출은 시그널 파라미터(L,S,W,k,eps,회복진폭,등락률상한)에만 의존
- TP/SL(ATR 배수)은 엔진에만 영향 ← 시그널 검출 결과만으로 재시뮬레이션
- 검출/시뮬레이션 모두 ProcessPool 병렬 + 공유 데이터는 initializer로 전달 (fork)
- 결과에 buy&hold 대비 알파(초과수익 avg, pos비율) 포함 → '수익률'이 아닌 '알파' 기준 최적화
"""

from __future__ import annotations

import argparse
import itertools
from concurrent.futures import ProcessPoolExecutor, as_completed
from dataclasses import dataclass, asdict
from pathlib import Path

import pandas as pd

from ..compare import trade_vs_benchmark
from ..data.loader import load_all
from ..engine import TradeParams, run_backtest
from ..metrics import summarize
from ..signals import DoubleWaveParams, detect_entries
from ..results_dir import results_root

RESULTS_DIR = results_root()

# 시그널 키 순서: L, S, W, k, eps, rise, max_rise
SIG_KEYS = ["L", "S", "W", "k", "eps", "pullback_rise_pct", "max_rise_pct"]
TRADE_KEYS = ["tp_atr", "sl_atr"]

_SHARED: dict = {}


def _init_worker(shared: dict) -> None:
    global _SHARED
    _SHARED = shared


def _params(sig: tuple) -> DoubleWaveParams:
    L, S, W, k, eps, rise, max_rise = sig
    return DoubleWaveParams(
        long_window=L,
        short_window=S,
        w_period=W,
        k=k,
        eps=eps,
        adjust_eps=eps,
        pullback_rise_pct=rise,
        max_rise_pct=max_rise,
    )


def _detect_worker(sig_key: tuple) -> tuple:
    params = _params(sig_key)
    out = {}
    for ticker, df in _SHARED.items():
        out[ticker] = detect_entries(df, params, ticker=ticker)
    return sig_key, out


def _sim_worker(sig_key: tuple, tp_atr: float, sl_atr: float) -> tuple:
    sigs_map = _SHARED["__signals__"][sig_key]
    trade_params = TradeParams(tp_atr=tp_atr, sl_atr=sl_atr)
    total = []
    for ticker in _SHARED["__ticker_order__"]:
        df = _SHARED[ticker]
        total.extend(
            run_backtest(df, sigs_map.get(ticker, []), trade_params, ticker=ticker)
        )
    perf = summarize(total).to_dict()
    if total:
        tvb = trade_vs_benchmark(total, _SHARED)
        perf["alpha_avg"] = round(float(tvb["alpha_pct"].mean()), 3) if len(tvb) else 0.0
        perf["alpha_pos"] = round(float((tvb["alpha_pct"] > 0).mean()), 3) if len(tvb) else 0.0
    else:
        perf["alpha_avg"] = 0.0
        perf["alpha_pos"] = 0.0
    return (sig_key, tp_atr, sl_atr), perf


def run_grid(
    sig_grid: list[tuple],
    trade_grid: list[tuple],
    data: dict | None = None,
    workers: int = 4,
) -> pd.DataFrame:
    """그리드 탐색 → 조합별 성능 요약 DataFrame"""
    tickers = list(data.keys())

    # 1) 시그널 검출 (병렬)
    signals_by_key: dict = {}
    with ProcessPoolExecutor(max_workers=workers, initializer=_init_worker,
                             initargs=(data,)) as ex:
        futs = [ex.submit(_detect_worker, s) for s in sig_grid]
        for fut in as_completed(futs):
            sig_key, out = fut.result()
            signals_by_key[sig_key] = out

    # 2) 시뮬레이션 (병렬)
    shared = {**data, "__signals__": signals_by_key, "__ticker_order__": tickers}
    results = {}
    with ProcessPoolExecutor(max_workers=workers, initializer=_init_worker,
                             initargs=(shared,)) as ex:
        futs = {}
        for sig_key in sig_grid:
            for tp_atr, sl_atr in trade_grid:
                futs[ex.submit(_sim_worker, sig_key, tp_atr, sl_atr)] = (sig_key, tp_atr, sl_atr)
        for fut in as_completed(futs):
            key, perf = fut.result()
            results[key] = perf

    rows = []
    for sig_key in sig_grid:
        for tp_atr, sl_atr in trade_grid:
            perf = results[(sig_key, tp_atr, sl_atr)]
            base = dict(zip(SIG_KEYS, sig_key))
            base.update({"tp_atr": tp_atr, "sl_atr": sl_atr})
            base.update(perf)
            rows.append(base)
    return pd.DataFrame(rows)


def build_arg_grid(quick: bool, wide: bool = False) -> tuple[list, list, dict]:
    if quick:
        sig = dict(
            L=[5, 7, 10],
            S=[2, 3],
            W=[5, 7],
            k=[3, 5],
            eps=[0.0, 0.05],
            pullback_rise_pct=[0.0, 0.5],
            max_rise_pct=[5.0, 10.0],
        )
        trade = [(4.0, 1.0), (5.0, 1.0), (5.0, 1.5), (6.0, 1.5), (4.0, 2.0)]
    elif wide:
        # 중간 규모: quick 대비 ε=0.1, W에 3·10, rise에 1.0, max_rise에 3 추가
        sig = dict(
            L=[5, 7, 10],
            S=[2, 3],
            W=[3, 5, 7, 10],
            k=[3, 5],
            eps=[0.0, 0.05, 0.1],
            pullback_rise_pct=[0.0, 0.5, 1.0],
            max_rise_pct=[3.0, 5.0, 10.0],
        )
        trade = [(4.0, 1.0), (5.0, 1.5), (6.0, 1.0), (6.0, 1.5),
                 (8.0, 1.5), (4.0, 2.0)]
    else:
        sig = dict(
            L=[3, 5, 7, 10, 15],
            S=[2, 3, 5],
            W=[3, 5, 7, 10],
            k=[3, 5, 7],
            eps=[0.0, 0.05, 0.1],
            pullback_rise_pct=[0.0, 0.5, 1.0],
            max_rise_pct=[3.0, 5.0, 10.0],
        )
        trade = [(3.0, 1.0), (4.0, 1.0), (5.0, 1.0), (6.0, 1.0),
                 (4.0, 1.5), (5.0, 1.5), (6.0, 1.5), (8.0, 1.5),
                 (4.0, 2.0), (5.0, 2.0)]
    sig_grid = list(itertools.product(*[sig[k] for k in SIG_KEYS]))
    return sig_grid, trade, sig


def _format_top(df: pd.DataFrame) -> str:
    cols = ["L", "S", "W", "k", "eps", "pullback_rise_pct", "max_rise_pct",
            "tp_atr", "sl_atr", "n_trades", "win_rate", "cum_return",
            "profit_factor", "max_drawdown", "alpha_avg", "alpha_pos"]
    return df[cols].to_string(index=False)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--workers", type=int, default=4)
    ap.add_argument("--out", default="grid_results.csv")
    ap.add_argument("--quick", action="store_true", help="빠른 서브그리드")
    ap.add_argument("--wide", action="store_true", help="중간 규모 확장 그리드 (quick~full)")
    args = ap.parse_args()

    sig_grid, trade_grid, sig = build_arg_grid(args.quick, args.wide)
    print(f"시그널 조합: {len(sig_grid)} | TP/SL 조합: {len(trade_grid)} | "
          f"전체: {len(sig_grid)*len(trade_grid)}")
    print(f"그리드: {sig}")

    data = load_all()
    print(f"종목 {len(data)}개 로드, 탐색 시작 (워커 {args.workers})...")
    result = run_grid(sig_grid, trade_grid, data=data, workers=args.workers)

    filt = result[result["n_trades"] >= 20].copy()
    filt = filt.sort_values(["alpha_avg", "profit_factor"], ascending=False).reset_index(drop=True)

    out_path = RESULTS_DIR / args.out
    filt.to_csv(out_path, index=False)
    print(f"\n저장: {out_path} (n_trades>=20, 총 {len(filt)} 조합)")
    print("\n=== TOP 15 (알파 평균 기준) ===")
    print(_format_top(filt.head(15)))
    print("\n=== TOP 15 (복리 누적 기준) ===")
    print(_format_top(result[result["n_trades"] >= 20]
                      .sort_values("cum_return", ascending=False).head(15)))


if __name__ == "__main__":
    main()