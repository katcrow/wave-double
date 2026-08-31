"""벤치마크 비교 실행기 — 지정 파라미터의 전략 결과를 buy&hold와 비교"""

from __future__ import annotations

import argparse
import json

from ..compare import benchmark_report
from ..data.loader import load_all
from ..engine import TradeParams, run_backtest
from ..signals import DoubleWaveParams, detect_entries


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--L", type=int, default=5)
    ap.add_argument("--S", type=int, default=3)
    ap.add_argument("--W", type=int, default=5)
    ap.add_argument("--k", type=int, default=3)
    ap.add_argument("--eps", type=float, default=0.05)
    ap.add_argument("--tp-atr", type=float, default=4.0)
    ap.add_argument("--sl-atr", type=float, default=2.0)
    args = ap.parse_args()

    sig_params = DoubleWaveParams(
        long_window=args.L, short_window=args.S, w_period=args.W,
        k=args.k, eps=args.eps, adjust_eps=args.eps,
    )
    trade_params = TradeParams(tp_atr=args.tp_atr, sl_atr=args.sl_atr)

    data = load_all()
    trades = []
    for ticker, df in data.items():
        sigs = detect_entries(df, sig_params, ticker=ticker)
        trades.extend(run_backtest(df, sigs, trade_params, ticker=ticker))

    from ..metrics import summarize

    perf = summarize(trades)
    rep = benchmark_report(trades, data)

    print(f"전략 ({args.L},{args.S},{args.W},{args.k},{args.eps} / TP{args.tp_atr} SL{args.sl_atr})")
    print("-" * 60)
    print(f"전략 트레이드: {perf.n_trades} | 승률 {perf.win_rate*100:.1f}% | "
          f"복리누적 {perf.cum_return:.1f}% | PF {perf.profit_factor:.2f} | MDD {perf.max_drawdown:.1f}%")
    print()
    print("[벤치마크] 기간 전체 buy & hold")
    bm = rep["benchmark"]
    print(f"  유니버스 동일비중 지수:  {bm['equal_weight_index_return_pct']:+.1f}%")
    print(f"  종목별 평균 buy&hold:    {bm['bh_mean_ticker_pct']:+.1f}% (중앙 {bm['bh_median_ticker_pct']:+.1f})")
    print(f"  종목별 분포:             {bm['bh_min_ticker_pct']:+.1f} ~ {bm['bh_max_ticker_pct']:+.1f}%")
    print()
    tvs = rep["trade_vs_bh"]
    if tvs:
        print("[트레이드별 동일종목·동일보유기간 비교]")
        print(f"  트레이드 수:            {tvs['n_trades']}")
        print(f"  전략 평균:              {tvs['strategy_avg_pct']:+.2f}%")
        print(f"  buy&hold 평균:          {tvs['bh_avg_pct']:+.2f}%")
        print(f"  알파(초과수익) 평균:    {tvs['alpha_avg_pct']:+.2f}%")
        print(f"  알파>0 비율:            {tvs['alpha_win_rate']*100:.1f}%")

    from pathlib import Path
    out = Path(__file__).parent.parent / "results" / "benchmark_report.json"
    out.write_text(json.dumps(rep, ensure_ascii=False, indent=2))
    print(f"\n저장: {out}")


if __name__ == "__main__":
    main()