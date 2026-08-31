"""상위 3개 조합에 OBV(거래량) 필터를 AND로 추가한 뒤 OR 합집합

각 조합:
    1위 = (RSI & CCI) & OBV
    2위 = (RSI & IBS) & OBV
    3위 = (RSI & ADX) & OBV
전체 = 1위 ∪ 2위 ∪ 3위   (OR)

즉, 개별 조합 신호를 OBV 신호로 검증(AND)한 뒤 그 3개를 OR로 합친다.
각 조합의 최적 파라미터는 combine.py 결과, OBV는 window=10(3%/3% 최적화 결과) 사용.
"""

from __future__ import annotations

import argparse
from concurrent.futures import ProcessPoolExecutor, as_completed

import pandas as pd

from ..data.loader import load_all
from ..engine import TradeParams, run_backtest
from ..metrics import summarize
from . import _signals as S
from .run import RESULTS_DIR, _to_signals, _SHARED, _init_worker

# 상위 3개 조합 (combine 결과에서 채택한 최적 파라미터)
# 3위(RSI+ADX)는 OBV 필터 대비 빈도가 너무 적어(월 1.30회) threshold를 30→25로 완화해
# 목표 2회/월 도달 (147건, 월 2.01회, 승률 68.7%)
TOP3 = [
    ("RSI+CCI", "rsi", {"period": 21, "threshold": 25.0}, "cci", {"period": 10, "threshold": 150}),
    ("RSI+IBS", "rsi", {"period": 9, "threshold": 20.0}, "ibs", {"threshold": 0.3, "period": 1}),
    ("RSI+ADX", "rsi", {"period": 2, "threshold": 30.0}, "adx", {"length": 20, "threshold": 25.0}),
]

# OR 조건으로 추가되는 거래량 지표 (OBV) — 각 조합에 AND 필터로 적용
VOLUME = [("OBV", "obv", {"window": 3})]
OBV_WINDOW_DEFAULT = 3


def _run_union(tp_pct: float, sl_pct: float, obv_window: int = OBV_WINDOW_DEFAULT) -> dict:
    """합집합 시그널 성과 계산 (단일 프로세스 가정, _SHARED 전역 사용)"""
    data = _SHARED["data"]
    sigs_map = {}
    for ticker, df in data.items():
        union = pd.Series(False, index=df.index)
        # OBV 필터 마스크 (1회 계산 후 재사용)
        obv_mask = pd.Series(False, index=df.index)
        for label, iname, p in VOLUME:
            p = {**p, "window": obv_window}
            try:
                obv_mask |= S.get_signal_fn(iname)(df, **p).fillna(False)
            except Exception:
                pass
        for label, ina, pa, inb, pb in TOP3:
            try:
                ma = S.get_signal_fn(ina)(df, **pa)
                mb = S.get_signal_fn(inb)(df, **pb)
                combo = (ma.fillna(False) & mb.fillna(False)) & obv_mask
                union |= combo
            except Exception:
                pass
        sigs_map[ticker] = _to_signals(df, union, ticker, tp_pct, sl_pct)

    trades = []
    for ticker, df in data.items():
        trades.extend(
            run_backtest(df, sigs_map.get(ticker, []), TradeParams(), ticker=ticker)
        )
    perf = summarize(trades)
    months = sorted(set(pd.Timestamp(d).to_period("M") for df in data.values() for d in df.index))
    monthly = perf.n_trades / len(months) if months else 0.0
    return {
        "tp_pct": tp_pct, "sl_pct": sl_pct,
        "n_trades": perf.n_trades, "n_win": perf.n_win,
        "win_rate": perf.win_rate, "avg_return": perf.avg_return,
        "total_return": perf.total_return, "cum_return": perf.cum_return,
        "profit_factor": perf.profit_factor, "max_drawdown": perf.max_drawdown,
        "avg_holding_bars": perf.avg_holding_bars, "tickers_hit": perf.tickers_hit,
        "n_months": len(months), "monthly_freq": round(monthly, 2),
        "exit_counts": perf.exit_counts,
    }


def main() -> None:
    ap = argparse.ArgumentParser(description="상위 3개 조합 합집합 시그널")
    ap.add_argument("--tp", type=float, default=3.0)
    ap.add_argument("--sl", type=float, default=3.0)
    ap.add_argument("--obv-window", type=int, default=OBV_WINDOW_DEFAULT)
    args = ap.parse_args()

    data = load_all()
    _SHARED["data"] = data

    print(f"종목 {len(data)}개, 고정 TP{args.tp}/SL{args.sl}, OBV window={args.obv_window}")
    print("결합 신호(합집합): " + " ∪ ".join(f"({a} & OBV)" for a, *_ in TOP3))
    print()

    res = _run_union(args.tp, args.sl, obv_window=args.obv_window)

    # 개별 조합(교집합) 성과와 병행 출력
    print("--- 대조: 개별 조합 승률 (combine 결과) ---")
    try:
        cs = pd.read_csv(RESULTS_DIR / "combo_summary.csv")
        for a, *_ in TOP3:
            row = cs[cs["label"] == a]
            if not row.empty:
                r = row.iloc[0]
                print(f"  {a:>10}: 승률 {r['win_rate']*100:5.1f}% | 트레이드 {r['n_trades']:>3} "
                      f"| 월평균 {r['monthly_freq']:4.2f}회")
    except Exception as e:
        print(f"  (대조 로드 실패: {e})")

    print()
    print("=== (1위 & OBV) ∪ (2위 & OBV) ∪ (3위 & OBV) 결과 ===")
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

    # 저장
    pd.DataFrame([res]).to_csv(RESULTS_DIR / "union_top3_plus_obv.csv", index=False)
    print(f"\n저장: {RESULTS_DIR}/union_top3_plus_obv.csv")


if __name__ == "__main__":
    main()
