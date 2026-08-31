"""확정 전략 A ∪ B 결합 백테스팅 (TP 3% / SL 3%)

전략 A (OBV 필터 합집합): (RSI+CCI & OBV) ∪ (RSI+IBS & OBV) ∪ (RSI+ADX & OBV)
전략 B (스토캐스틱 쌍바닥+주봉): 일봉(14-3-3) %K 쌍바닥 + 주봉(20-3) K 우상향

결합 방식 두 가지를 모두 계산:
  OR = A ∪ B  (둘 중 하나라도 신호 → 진입, 빈도 증가)
  AND = A ∩ B (둘 다 동시 신호 → 진입, 빈도 급감)
"""

from __future__ import annotations

import argparse

import pandas as pd

from ..data.loader import load_all
from ..engine import TradeParams, run_backtest
from ..metrics import summarize
from ._signals import get_signal_fn
from .run import _to_signals, RESULTS_DIR
from .union import TOP3, VOLUME

# 전략 B 고정 파라미터 (스토캐스틱 최적값)
STOCH_DB = dict(k_period=14, d_period=3, threshold=20.0, wk_period=20, wd_period=3)

# 전략 C 고정 파라미터 (스토캐스틱 3바닥 다이버전스 최적값)
DIV3 = dict(k_period=5, d_period=3, div_window=20, min_gap=5)


def build_signals(df, tp_pct, sl_pct, ticker):
    """신호 A(OBV합집합), B(스토캐스틱), C(3바닥 다이버전스)를 각각 마스크로 반환"""
    obv_mask = pd.Series(False, index=df.index)
    for _, iname, p in VOLUME:
        try:
            obv_mask |= get_signal_fn(iname)(df, **p).fillna(False)
        except Exception:
            pass
    a = pd.Series(False, index=df.index)
    for lab, ina, pa, inb, pb in TOP3:
        try:
            ma = get_signal_fn(ina)(df, **pa)
            mb = get_signal_fn(inb)(df, **pb)
            a |= (ma.fillna(False) & mb.fillna(False)) & obv_mask
        except Exception:
            pass
    try:
        b = get_signal_fn("stoch_db_weekly_k")(df, **STOCH_DB).fillna(False)
    except Exception:
        b = pd.Series(False, index=df.index)
    try:
        c = get_signal_fn("div_stoch3")(df, **DIV3).fillna(False)
    except Exception:
        c = pd.Series(False, index=df.index)
    return a, b, c


def run_combined(tp_pct: float = 3.0, sl_pct: float = 3.0):
    data = load_all()
    months = sorted(set(pd.Timestamp(d).to_period("M") for df in data.values() for d in df.index))
    sigs = {m: {} for m in ("a", "b", "c", "or", "or3")}
    for ticker, df in data.items():
        a, b, c = build_signals(df, tp_pct, sl_pct, ticker)
        sigs["a"][ticker] = _to_signals(df, a, ticker, tp_pct, sl_pct)
        sigs["b"][ticker] = _to_signals(df, b, ticker, tp_pct, sl_pct)
        sigs["c"][ticker] = _to_signals(df, c, ticker, tp_pct, sl_pct)
        sigs["or"][ticker] = _to_signals(df, a | b, ticker, tp_pct, sl_pct)
        sigs["or3"][ticker] = _to_signals(df, a | b | c, ticker, tp_pct, sl_pct)

    def backtest(name):
        trades = []
        for ticker, df in data.items():
            trades.extend(run_backtest(df, sigs[name].get(ticker, []), TradeParams(), ticker=ticker))
        p = summarize(trades)
        monthly = p.n_trades / len(months) if months else 0.0
        return {
            "mode": name, "n_trades": p.n_trades, "n_win": p.n_win,
            "win_rate": p.win_rate, "profit_factor": p.profit_factor,
            "avg_return": p.avg_return, "total_return": p.total_return,
            "cum_return": p.cum_return, "max_drawdown": p.max_drawdown,
            "tickers_hit": p.tickers_hit, "avg_holding_bars": p.avg_holding_bars,
            "monthly_freq": round(monthly, 2),
        }

    results = {"a": backtest("a"), "b": backtest("b"), "c": backtest("c")}
    results["or"] = backtest("or")
    results["or3"] = backtest("or3")
    return results


def _fmt(r: dict) -> str:
    return (f"{r['mode']:>4} | 거래 {r['n_trades']:>5} (승 {r['n_win']}) | 승률 {r['win_rate']*100:5.1f}% | "
            f"PF {r['profit_factor']:.2f} | 평균 {r['avg_return']:+.3f}% | 낙폭 {r['max_drawdown']:.1f}% | "
            f"월 {r['monthly_freq']:.2f}회")


def main() -> None:
    ap = argparse.ArgumentParser(description="확정 전략 A∪B∪C 결합 백테스팅")
    ap.add_argument("--tp", type=float, default=3.0)
    ap.add_argument("--sl", type=float, default=3.0)
    args = ap.parse_args()

    res = run_combined(args.tp, args.sl)
    print(f"=== 확정 전략 A ∪ B ∪ C 결합 (TP{args.tp}%/SL{args.sl}%) ===")
    print(f"{'전략 A':<26}: {_fmt(res['a'])}")
    print(f"{'전략 B':<26}: {_fmt(res['b'])}")
    print(f"{'전략 C':<26}: {_fmt(res['c'])}")
    print(f"{'A ∪ B (OR)':<26}: {_fmt(res['or'])}")
    print(f"{'A ∪ B ∪ C (OR3)':<26}: {_fmt(res['or3'])}")

    out = pd.DataFrame(list(res.values()))
    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    fname = RESULTS_DIR / "combined_A_B_C.csv"
    out.to_csv(fname, index=False)
    print(f"\n저장: {fname}")


if __name__ == "__main__":
    main()
