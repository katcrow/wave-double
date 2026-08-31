"""벤치마크 비교 — buy & hold 대비 전략 우위 측정

1. 유니버스 동일비중 buy&hold 지수 (전체 기간)
2. 종목별 buy&hold 총수익률 분포
3. 트레이드별 벤치마크: 같은 종목을 같은 보유기간 동안 buy&hold 했을 때와 비교
   → 시그널 타이밍(매수 시점 선택)의 순수 우위를 측정
"""

from __future__ import annotations

import numpy as np
import pandas as pd


def buy_hold_total_return(data: dict[str, pd.DataFrame]) -> pd.DataFrame:
    """종목별 buy&hold 총수익률 (%)"""
    rows = []
    for ticker, df in data.items():
        close = df["Close"]
        ret = (close.iloc[-1] / close.iloc[0] - 1.0) * 100.0
        rows.append({"ticker": ticker, "bh_return_pct": round(ret, 2)})
    out = pd.DataFrame(rows)
    return out


def equal_weight_index(data: dict[str, pd.DataFrame]) -> pd.Series:
    """유니버스 동일비중 지수 (일별 평균 수익률 누적, 시작=1.0)"""
    rets = []
    for ticker, df in data.items():
        close = df["Close"]
        s = close.pct_change().rename(ticker)
        rets.append(s)
    matrix = pd.concat(rets, axis=1)
    daily = matrix.mean(axis=1).fillna(0.0)
    index = (1.0 + daily).cumprod()
    index.iloc[0] = 1.0
    return index


def trade_vs_benchmark(
    trades: list, data: dict[str, pd.DataFrame]
) -> pd.DataFrame:
    """각 트레이드와 같은 종목 동일 보유기간 buy&hold 수익률 비교.

    반환 컬럼: ticker, entry_date, exit_date, strategy_pct, bh_pct, alpha_pct
    """
    rows = []
    for tr in trades:
        df = data.get(tr.ticker)
        if df is None:
            continue
        close = df["Close"]
        mask = (df.index >= tr.entry_date) & (df.index <= tr.exit_date)
        seg = close[mask]
        if len(seg) < 2:
            continue
        bh = (seg.iloc[-1] / seg.iloc[0] - 1.0) * 100.0
        rows.append(
            {
                "ticker": tr.ticker,
                "entry_date": tr.entry_date,
                "exit_date": tr.exit_date,
                "strategy_pct": tr.return_pct,
                "bh_pct": round(float(bh), 4),
                "alpha_pct": round(tr.return_pct - float(bh), 4),
            }
        )
    return pd.DataFrame(rows)


def benchmark_report(
    trades: list,
    data: dict[str, pd.DataFrame],
    strategy_label: str = "전략",
) -> dict:
    """전체 벤치마크 리포트 요약 dict"""
    bh = buy_hold_total_return(data)
    ew = equal_weight_index(data)
    tvs = trade_vs_benchmark(trades, data)

    return {
        "benchmark": {
            "period": f"{ew.index[0].date()} ~ {ew.index[-1].date()}",
            "equal_weight_index_return_pct": round(float((ew.iloc[-1] - 1.0) * 100.0), 2),
            "bh_mean_ticker_pct": round(float(bh["bh_return_pct"].mean()), 2),
            "bh_median_ticker_pct": round(float(bh["bh_return_pct"].median()), 2),
            "bh_min_ticker_pct": round(float(bh["bh_return_pct"].min()), 2),
            "bh_max_ticker_pct": round(float(bh["bh_return_pct"].max()), 2),
        },
        "trade_vs_bh": None if tvs.empty else {
            "n_trades": len(tvs),
            "strategy_avg_pct": round(float(tvs["strategy_pct"].mean()), 2),
            "bh_avg_pct": round(float(tvs["bh_pct"].mean()), 2),
            "alpha_avg_pct": round(float(tvs["alpha_pct"].mean()), 2),
            "alpha_win_rate": round(float((tvs["alpha_pct"] > 0).mean()), 2),
        },
    }