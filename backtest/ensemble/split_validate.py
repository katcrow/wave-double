"""기간 분할 안정성 검증 — 그리드 상위 조합을 전반/후반 구간에서 재검증

과적합 스크리닝:
1. 그리드(전체 기간)에서 상위 성능 조합을 뽑는다.
2. 데이터를 기간 반분(전반/후반)해서 각 구간에서 독립적으로 재계산.
3. '양쪽 구간 모두에서 알파가 유지되는 조합' = 안정적 신호.
   (전체 기간 최적값이 어떤 한 쪽 구간에서만 발현됐다면 과적합으로 판정)

주의: 시그널 검출은 정보 누출 방지를 위해 전체 기간 df에서 수행하되,
매수(엔트리)는 해당 구간 날짜에 걸친 시그널만 사용한다.
"""

from __future__ import annotations

import argparse
import sys
from collections import defaultdict
from pathlib import Path

import pandas as pd

from ..compare import trade_vs_benchmark
from ..data.loader import load_all
from ..engine import TradeParams, run_backtest
from ..metrics import summarize
from ..signals import detect_entries
from .grid_search import RESULTS_DIR, SIG_KEYS, TRADE_KEYS, _params


def row_to_params(row: pd.Series) -> tuple:
    """그리드 CSV 행 → (SignalParams, TradeParams)"""
    sig = tuple(row[k] for k in SIG_KEYS)
    return _params(sig), TradeParams(tp_atr=row["tp_atr"], sl_atr=row["sl_atr"])


def split_half(
    data: dict[str, pd.DataFrame],
) -> tuple[pd.Timestamp, dict, dict]:
    """거래일 수 기준 반분 → (분할일, 전반, 후반)"""
    dates = next(iter(data.values())).index
    mid = dates[len(dates) // 2]
    h1 = {t: df[df.index < mid] for t, df in data.items()}
    h2 = {t: df[df.index >= mid] for t, df in data.items()}
    return mid, h1, h2


def evaluate_half(
    half_data: dict[str, pd.DataFrame],
    sigs_map: dict,  # ticker -> 시그널 리스트 (전체 기간)
    trade_params: TradeParams,
) -> dict:
    """구간 df 기준으로 시뮬레이션 + buy&hold 알파"""
    trades: list = []
    for ticker, df in half_data.items():
        valid = [s for s in sigs_map.get(ticker, []) if s.date in df.index]
        trades.extend(run_backtest(df, valid, trade_params, ticker=ticker))

    perf = summarize(trades).to_dict()
    tvb = trade_vs_benchmark(trades, half_data)
    return {
        "n": perf["n_trades"],
        "win_rate": perf["win_rate"],
        "cum_return": perf["cum_return"],
        "max_drawdown": perf["max_drawdown"],
        "alpha_avg": float(tvb["alpha_pct"].mean()) if len(tvb) else float("nan"),
        "alpha_pos": float((tvb["alpha_pct"] > 0).mean()) if len(tvb) else float("nan"),
    }


def validate_rows(rows: list[pd.Series], data, halves) -> pd.DataFrame:
    """조회 행들에 대해 전/후반 성능 계산 → 요약 DataFrame"""
    _, h1, h2 = halves
    out = []
    for row in rows:
        sig_params, trade_params = row_to_params(row)
        sigs_map = {
            ticker: detect_entries(df, sig_params, ticker=ticker)
            for ticker, df in data.items()
        }
        e1, e2 = evaluate_half(h1, sigs_map, trade_params), evaluate_half(h2, sigs_map, trade_params)

        stable = (
            (e1["n"] >= 10)
            and (e2["n"] >= 10)
            and (e1["alpha_avg"] > 0)
            and (e2["alpha_avg"] > 0)
        )
        base = {k: row[k] for k in SIG_KEYS + TRADE_KEYS}
        base.update(
            {
                "full_n": row["n_trades"],
                "full_alpha": row["alpha_avg"],
                # 전반
                "h1_n": e1["n"], "h1_win": e1["win_rate"],
                "h1_cum": e1["cum_return"], "h1_alpha": e1["alpha_avg"],
                "h1_alpha_pos": e1["alpha_pos"],
                # 후반
                "h2_n": e2["n"], "h2_win": e2["win_rate"],
                "h2_cum": e2["cum_return"], "h2_alpha": e2["alpha_avg"],
                "h2_alpha_pos": e2["alpha_pos"],
                "stable": stable,
            }
        )
        out.append(base)
    return pd.DataFrame(out)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--csv", default="grid_quick_v3.csv", help="그리드 결과 CSV")
    ap.add_argument("--metric", default="alpha_avg", help="상위 선택 기준 (alpha_avg|cum_return)")
    ap.add_argument("--n", type=int, default=15, help="검증할 상위 조합 수")
    ap.add_argument("--min-trades", type=int, default=8, help="구간별 최소 트레이드 수")
    args = ap.parse_args()

    grid = pd.read_csv(RESULTS_DIR / args.csv)
    filt = grid[grid["n_trades"] >= 20]
    if filt.empty:
        print("n_trades>=20 조합이 없습니다."); sys.exit(1)

    top = (
        filt.sort_values(args.metric, ascending=False)
        .drop_duplicates(subset=SIG_KEYS)
        .head(args.n)
    )

    data = load_all()
    mid, h1, h2 = split_half(data)
    print(f"종목 {len(data)}개 | 분할일: {mid.date()} "
          f"(전반 {len(next(iter(h1.values())))}봉 / 후반 {len(next(iter(h2.values())))}봉)")

    result = validate_rows([r for _, r in top.iterrows()], data, (mid, h1, h2))

    show_cols = ["L", "S", "W", "k", "eps", "pullback_rise_pct", "max_rise_pct",
                 "tp_atr", "sl_atr", "h1_n", "h1_alpha", "h1_alpha_pos",
                 "h2_n", "h2_alpha", "h2_alpha_pos", "stable"]
    print(result[show_cols].to_string(index=False))

    out_path = RESULTS_DIR / f"split_validation_{Path(args.csv).stem}.csv"
    result.to_csv(out_path, index=False)
    print(f"\n저장: {out_path}")

    n_stable = int(result["stable"].sum())
    print(f"안정 조합 (전후반 모두 알파>0, 트레이드≥10): {n_stable} / {len(result)}")


if __name__ == "__main__":
    main()