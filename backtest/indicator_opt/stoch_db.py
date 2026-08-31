"""스토캐스틱 %K 쌍바닥(Double Bottom) 전략 백테스팅 (TP 3% / SL 3%)

엔트리: slow 스토캐스틱 5-3-3 %K가 쌍바닥을 이루고 넥라인을 상향 돌파
청산: 고정 익절 +3% / 고정 손절 -3%, 시그널 봉 종가 진입
"""

from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd

from ..data.loader import load_all
from ..engine import TradeParams, run_backtest
from ..metrics import summarize
from ._signals import get_signal_fn
from .run import _to_signals, RESULTS_DIR

DEFAULT = {"k_period": 5, "d_period": 3, "threshold": 30.0}


def run_stoch_db(tp_pct: float = 3.0, sl_pct: float = 3.0, weekly: bool = False, **params) -> dict:
    data = load_all()
    sigs_map = {}
    sig_name = "stoch_db_weekly_k" if weekly else "stoch_double_bottom"
    fn = get_signal_fn(sig_name)
    for ticker, df in data.items():
        try:
            mask = fn(df, **params)
        except Exception:
            continue
        sigs_map[ticker] = _to_signals(df, mask, ticker, tp_pct, sl_pct)

    trades = []
    for ticker, df in data.items():
        trades.extend(
            run_backtest(df, sigs_map.get(ticker, []), TradeParams(), ticker=ticker)
        )
    perf = summarize(trades)
    months = sorted(set(pd.Timestamp(d).to_period("M") for df in data.values() for d in df.index))
    monthly = perf.n_trades / len(months) if months else 0.0
    return {
        **{k: params.get(k, v) for k, v in DEFAULT.items()},
        "tp_pct": tp_pct, "sl_pct": sl_pct, "weekly_filter": weekly,
        "n_trades": perf.n_trades, "n_win": perf.n_win,
        "win_rate": perf.win_rate, "profit_factor": perf.profit_factor,
        "avg_return": perf.avg_return,
        "total_return": perf.total_return, "cum_return": perf.cum_return,
        "max_drawdown": perf.max_drawdown, "tickers_hit": perf.tickers_hit,
        "avg_holding_bars": perf.avg_holding_bars, "n_months": len(months),
        "monthly_freq": round(monthly, 2), "exit_counts": perf.exit_counts,
    }


def main() -> None:
    ap = argparse.ArgumentParser(description="스토캐스틱 %K 쌍바닥 전략 백테스팅 (TP3/SL3)")
    ap.add_argument("--tp", type=float, default=3.0)
    ap.add_argument("--sl", type=float, default=3.0)
    ap.add_argument("--k-period", type=int, default=DEFAULT["k_period"])
    ap.add_argument("--d-period", type=int, default=DEFAULT["d_period"])
    ap.add_argument("--threshold", type=float, default=DEFAULT["threshold"])
    ap.add_argument("--weekly", action="store_true",
                    help="주봉(10-6-6) K 우상향 필터 추가")
    ap.add_argument("--wk-period", type=int, default=10)
    ap.add_argument("--wd-period", type=int, default=6)
    args = ap.parse_args()

    params = dict(k_period=args.k_period, d_period=args.d_period, threshold=args.threshold)
    if args.weekly:
        params["wk_period"] = args.wk_period
        params["wd_period"] = args.wd_period
    res = run_stoch_db(args.tp, args.sl, weekly=args.weekly, **params)

    suffix = " + 주봉 K 우상향" if args.weekly else ""
    print(f"=== 스토캐스틱 %K({args.k_period}-{args.d_period}-3) 쌍바닥{suffix} 전략 (TP{args.tp}%/SL{args.sl}%) ===")
    print(f"트레이드:     {res['n_trades']} (승 {res['n_win']}/{res['n_trades']})")
    print(f"승률:         {res['win_rate']*100:.1f}%")
    print(f"ProfitFactor: {res['profit_factor']:.2f}")
    print(f"평균 수익률:  {res['avg_return']:.3f}%")
    print(f"단리 누적:    {res['total_return']:.2f}%")
    print(f"복리 누적:    {res['cum_return']:.2f}%")
    print(f"최대낙폭:     {res['max_drawdown']:.2f}%")
    print(f"종목 커버:    {res['tickers_hit']}개")
    print(f"보유 평균:    {res['avg_holding_bars']:.1f}봉")
    print(f"분석 기간:    {res['n_months']}개월")
    print(f"월평균 빈도:  {res['monthly_freq']}회/월")
    print(f"청산 사유:    {res['exit_counts']}")

    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    fname = RESULTS_DIR / ("stoch_db_weekly_k_533_1066.csv" if args.weekly
                           else "stoch_double_bottom_533.csv")
    pd.DataFrame([res]).to_csv(fname, index=False)
    print(f"\n저장: {fname}")


if __name__ == "__main__":
    main()
