"""전략 부진 원인 분석 — 트레이드별 알파(초과수익)의 원천 파악

차트 출력 (results/analysis/):
1. scatter: 트레이드별 전략수익 vs 동일종목·동일구간 buy&hold (45도선 아래 = 열등)
2. 수익률 분포 비교 (전략 vs BH)
3. exit_reason 별 수익률 분포
4. 종목별 누적 기여 TOP (기여 = 트레이드 수익률 합)
5. 진입 시점 종목 상태(진입 전 60봉 수익률) vs 트레이드 알파
"""

from __future__ import annotations

import argparse
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import numpy as np
import pandas as pd

from ..compare import trade_vs_benchmark
from ..data.loader import load_all
from ..engine import TradeParams, run_backtest
from ..metrics import summarize
from ..signals import DoubleWaveParams, detect_entries

OUT = Path(__file__).parent.parent / "results" / "analysis"

plt.rcParams.update({
    "font.family": "IPAGothic",
    "axes.unicode_minus": False,
    "axes.titlesize": 11,
    "figure.dpi": 110,
})


def _entry_prior_return(data, trade) -> float:
    """진입 60봉 전 ~ 진입일 수익률 (%)"""
    df = data[trade.ticker]
    close = df["Close"]
    mask = df.index <= trade.entry_date
    seg = close[mask]
    if len(seg) < 61:
        return np.nan
    return (seg.iloc[-1] / seg.iloc[-61] - 1.0) * 100.0


def analyze(
    trades: list,
    data: dict,
    out_dir: Path = OUT,
) -> dict:
    out_dir.mkdir(parents=True, exist_ok=True)
    tvs = trade_vs_benchmark(trades, data)

    # ── 1) 산점도: 전략 vs 동일 BH ─────────────────────────────
    fig, ax = plt.subplots(figsize=(7, 7))
    ax.scatter(tvs["bh_pct"], tvs["strategy_pct"], s=14, alpha=0.6,
               c=np.where(tvs["alpha_pct"] > 0, "#2ca02c", "#d62728"))
    lim = max(tvs[["bh_pct", "strategy_pct"]].abs().max().max(), 5)
    ax.plot([-lim, lim], [-lim, lim], "k--", lw=1, label="전략=BH")
    ax.axhline(0, color="gray", lw=0.5)
    ax.axvline(0, color="gray", lw=0.5)
    n_alpha = int((tvs["alpha_pct"] > 0).sum())
    ax.set_title(f"트레이드별 전략 수익 vs 같은 종목·같은 기간 buy&hold\n"
                 f"알파>0: {n_alpha}/{len(tvs)} ({n_alpha/len(tvs)*100:.0f}%)")
    ax.set_xlabel("동일종목 buy&hold 수익률 (%)")
    ax.set_ylabel("전략 수익률 (%)")
    ax.legend()
    plt.tight_layout()
    fig.savefig(out_dir / "1_scatter_alpha.png")
    plt.close(fig)

    # ── 2) 수익률 분포 ─────────────────────────────────────────
    fig, ax = plt.subplots(figsize=(8, 4))
    bins = np.linspace(min(tvs[["strategy_pct", "bh_pct"]].min().min(), -15),
                       max(tvs[["strategy_pct", "bh_pct"]].max().max(), 15), 40)
    ax.hist(tvs["bh_pct"], bins=bins, alpha=0.55, label="buy&hold", color="#1f77b4")
    ax.hist(tvs["strategy_pct"], bins=bins, alpha=0.55, label="전략", color="#ff7f0e")
    ax.axvline(tvs["bh_pct"].mean(), color="#1f77b4", ls="--", label=f"BH 평균 {tvs['bh_pct'].mean():+.2f}%")
    ax.axvline(tvs["strategy_pct"].mean(), color="#ff7f0e", ls="--", label=f"전략 평균 {tvs['strategy_pct'].mean():+.2f}%")
    ax.legend()
    ax.set_title("트레이드 수익률 분포")
    ax.set_xlabel("수익률 (%)")
    plt.tight_layout()
    fig.savefig(out_dir / "2_hist_return.png")
    plt.close(fig)

    # ── 3) exit_reason 별 ──────────────────────────────────────
    info = pd.DataFrame([t.to_dict() for t in trades])
    reasons = ["tp", "sl", "end"]
    labels = {
        "tp": f"tp\n(익절 {int((info['exit_reason']=='tp').sum())})",
        "sl": f"sl\n(손절 {int((info['exit_reason']=='sl').sum())})",
        "end": f"end\n(강제 {int((info['exit_reason']=='end').sum())})",
    }
    fig, ax = plt.subplots(figsize=(8, 4))
    data_reason = [info.loc[info["exit_reason"] == r, "return_pct"] for r in reasons]
    ax.boxplot([d for d in data_reason if len(d)], showmeans=True)
    ax.set_xticklabels([labels[r] for r in reasons])
    ax.axhline(0, color="gray", lw=0.6)
    ax.set_title("청산 사유별 수익률 분포")
    ax.set_ylabel("수익률 (%)")
    plt.tight_layout()
    fig.savefig(out_dir / "3_exit_reason.png")
    plt.close(fig)

    # ── 4) 종목별 누적 기여 ────────────────────────────────────
    by_ticker = info.groupby("ticker").agg(
        n=("return_pct", "size"),
        contrib=("return_pct", "sum"),
        avg=("return_pct", "mean"),
    ).sort_values("contrib", ascending=False)
    fig, ax = plt.subplots(figsize=(10, 6))
    top = by_ticker.head(20)
    colors = np.where(top["contrib"] > 0, "#2ca02c", "#d62728")
    ax.bar(top.index, top["contrib"], color=colors)
    ax.set_xticklabels(top.index, rotation=90, fontsize=7)
    ax.set_title("종목별 트레이드 수익 기여 합 (상위 20)")
    ax.set_ylabel("누적 수익률 기여 (%)")
    plt.tight_layout()
    fig.savefig(out_dir / "4_ticker_contribution.png")
    plt.close(fig)

    # ── 5) 진입 전 종목 상태 vs 알파 ───────────────────────────
    tvs["prior60"] = tvs.apply(lambda r: _entry_prior_return(data, next(
        t for t in trades if t.ticker == r["ticker"] and t.entry_date == r["entry_date"]
    )), axis=1)
    fig, ax = plt.subplots(figsize=(7, 5))
    ok = tvs["prior60"].notna()
    ax.scatter(tvs.loc[ok, "prior60"], tvs.loc[ok, "alpha_pct"], s=14, alpha=0.6)
    ax.axhline(0, color="gray", lw=0.6)
    ax.set_title("진입 전 60봉 상승률(%) vs 트레이드 알파(%)")
    ax.set_xlabel("진입 전 60봉 수익률 (%)")
    ax.set_ylabel("알파 (%)")
    plt.tight_layout()
    fig.savefig(out_dir / "5_prior_return_vs_alpha.png")
    plt.close(fig)

    # 통계 요약
    corr = tvs[["prior60", "alpha_pct"]].dropna().corr().iloc[0, 1] if len(tvs) else np.nan
    summary = {
        "n_trades": len(tvs),
        "alpha_avg": round(float(tvs["alpha_pct"].mean()), 3),
        "alpha_pos": round(float((tvs["alpha_pct"] > 0).mean()), 3),
        "strategy_avg": round(float(tvs["strategy_pct"].mean()), 3),
        "bh_avg": round(float(tvs["bh_pct"].mean()), 3),
        "prior60_vs_alpha_corr": round(float(corr), 3),
        "exit_reason": info["exit_reason"].value_counts().to_dict(),
        "top_tickers_contrib": by_ticker.head(10).reset_index().to_dict("records"),
        "charts": [p.name for p in sorted(out_dir.glob("*.png"))],
    }
    (out_dir / "analysis_summary.json").write_text(
        __import__("json").dumps(summary, ensure_ascii=False, indent=2)
    )
    return summary


if __name__ == "__main__":
    ap = argparse.ArgumentParser()
    ap.add_argument("--L", type=int, default=5)
    ap.add_argument("--S", type=int, default=3)
    ap.add_argument("--W", type=int, default=5)
    ap.add_argument("--k", type=int, default=3)
    ap.add_argument("--eps", type=float, default=0.05)
    ap.add_argument("--tp-atr", type=float, default=4.0)
    ap.add_argument("--sl-atr", type=float, default=2.0)
    args = ap.parse_args()

    data = load_all()
    sig_p = DoubleWaveParams(long_window=args.L, short_window=args.S, w_period=args.W,
                             k=args.k, eps=args.eps, adjust_eps=args.eps)
    tr_p = TradeParams(tp_atr=args.tp_atr, sl_atr=args.sl_atr)
    trades = []
    for tk, df in data.items():
        sigs = detect_entries(df, sig_p, ticker=tk)
        trades.extend(run_backtest(df, sigs, tr_p, ticker=tk))

    from ..metrics import summarize
    print("[" + "-" * 50)
    print(f"전략 ({args.L},{args.S},{args.W},{args.k},{args.eps} / TP{args.tp_atr} SL{args.sl_atr})")
    perf = summarize(trades)
    print(f"트레이드 {perf.n_trades} | 승률 {perf.win_rate*100:.1f}% | 복리 {perf.cum_return:.1f}% | MDD {perf.max_drawdown:.1f}%")
    print("-" * 50 + "]")

    s = analyze(trades, data)
    print(f"\n분석 요약:")
    print(f"  알파 평균: {s['alpha_avg']:+.3f}% | 알파>0 비율: {s['alpha_pos']*100:.0f}%")
    print(f"  진입 전 60봉 상승률 vs 알파 상관: {s['prior60_vs_alpha_corr']:+.3f}")
    print(f"  청산: tp {s['exit_reason'].get('tp',0)} / sl {s['exit_reason'].get('sl',0)} / end {s['exit_reason'].get('end',0)}")
    print(f"  종목별 기여 TOP5:")
    for r in s["top_tickers_contrib"][:5]:
        print(f"    {r['ticker']}: n={r['n']}, 누적 {r['contrib']:+.1f}%, 평균 {r['avg']:+.2f}%")
    print(f"\n차트: {OUT}")