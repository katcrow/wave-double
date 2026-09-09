"""파동중첩 전략 백테스트 실행기

- 유니버스(전체 종목) 로드 → 진입 시그널 검출 → 트레이드 시뮬레이션 → 성과 리포트
- 결과는 results/에 parquet + 요약 저장
"""

from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd

from .data.loader import load_all
from .engine import TradeParams, Trade, run_backtest
from .metrics import summarize
from .signals import DoubleWaveParams, detect_entries
from .results_dir import results_root

RESULTS_DIR = results_root()


def parse_args() -> argparse.Namespace:
    ap = argparse.ArgumentParser(description="파동중첩 백테스트")
    ap.add_argument("--L", type=int, default=7, help="장기선 기간")
    ap.add_argument("--S", type=int, default=3, help="단기선 기간")
    ap.add_argument("--W", type=int, default=7, help="골든크로스 근접도")
    ap.add_argument("--k", type=int, default=5, help="각도 측정 구간")
    ap.add_argument("--eps", type=float, default=0.0, help="양판별 임계 (도)")
    ap.add_argument("--tp-atr", type=float, default=3.0, help="목표가 ATR 배수")
    ap.add_argument("--sl-atr", type=float, default=2.0, help="손절가 ATR 배수")
    ap.add_argument("--ticker", type=str, default="", help="특정 종목만 (예: 005930.KS)")
    ap.add_argument("--json", action="store_true", help="요약을 JSON으로만 출력")
    return ap.parse_args()


def main() -> None:
    args = parse_args()

    sig_params = DoubleWaveParams(
        long_window=args.L,
        short_window=args.S,
        w_period=args.W,
        k=args.k,
        eps=args.eps,
    )
    trade_params = TradeParams(tp_atr=args.tp_atr, sl_atr=args.sl_atr)

    tickers = [args.ticker] if args.ticker else None
    data = load_all(tickers)

    all_trades: list[Trade] = []
    all_signals = 0
    print(f"종목 수: {len(data)}")
    print(f"시그널 파라미터: {sig_params.as_dict()}")
    print(f"청산 파라미터: {trade_params.as_dict()}")
    print("-" * 60)

    for ticker, df in data.items():
        signals = detect_entries(df, sig_params, ticker=ticker)
        all_signals += len(signals)
        trades = run_backtest(df, signals, trade_params, ticker=ticker)
        all_trades.extend(trades)
        if trades:
            stat = summarize(trades)
            print(
                f"{ticker}: 시그널 {len(signals):>2} | 트레이드 {stat.n_trades:>2} | "
                f"승률 {stat.win_rate*100:5.1f}% | 누적 {stat.cum_return:7.2f}% "
                f"| 평균 {stat.avg_return:6.2f}%"
            )
        else:
            print(f"{ticker}: 시그널 {len(signals):>2} | 트레이드   0")

    print("-" * 60)
    perf = summarize(all_trades)
    print(f"총 시그널: {all_signals} | 총 트레이드: {perf.n_trades}")

    if args.json:
        import json

        print(json.dumps({"signals": all_signals, **perf.to_dict()}, ensure_ascii=False, indent=2))
    else:
        print(f"  승률:        {perf.win_rate*100:.1f}%  ({perf.n_win}승/{perf.n_trades})")
        print(f"  평균 수익률: {perf.avg_return:.2f}%")
        print(f"  복리 누적:   {perf.cum_return:.2f}%")
        print(f"  단리 누적:   {perf.total_return:.2f}%")
        print(f"  ProfitFactor:{perf.profit_factor:.2f}")
        print(f"  평균 보유:   {perf.avg_holding_bars:.1f}봉")
        print(f"  최대낙폭:    {perf.max_drawdown:.2f}%")
        print(f"  MVP/최악:    {perf.best_return:.2f}% / {perf.worst_return:.2f}%")
        print(f"  청산 사유:   {perf.exit_counts}")
        print(f"  종목 커버:   {perf.tickers_hit}개")

    # 결과 저장
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    trades_df = pd.DataFrame([t.to_dict() for t in all_trades])
    if not trades_df.empty:
        trades_df.to_parquet(RESULTS_DIR / "trades.parquet")
        trades_df.to_csv(RESULTS_DIR / "trades.csv", index=False)
    tag = f"L{args.L}_S{args.S}_W{args.W}_k{args.k}_eps{args.eps}_tp{args.tp_atr}_sl{args.sl_atr}"
    pd.DataFrame([perf.to_dict()]).to_csv(RESULTS_DIR / f"summary_{tag}.csv", index=False)
    print(f"\n결과 저장: {RESULTS_DIR}")


if __name__ == "__main__":
    main()