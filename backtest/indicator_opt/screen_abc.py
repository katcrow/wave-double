"""2026년 스크리닝 — 확정 전략 A / B / C 신호 발굴

확정 전략 3종(A: OBV필터 합집합, B: 스토캐스틱 쌍바닥+주봉K, C: 스토캐스틱 3바닥 다이버전스)의
2026년 시그널을 종목별로 스크리닝한다. 시그널 봉 종가 진입(TP 3%/SL 3%) 가정.

- 창: 기본 2026-01-01 ~ 분석 최신일(각 종목 최신 거래일)
- 후보: 창 내 A·B·C 중 하나라도 시그널 1회 이상
- 각 종목: 전략별 신호 수, 총 신호 수, 최근 시그널일, 신호원, 최신 종가
"""

from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd

from ..data.loader import load_all
from .combine_strategies import build_signals

OUT_DIR = Path(__file__).parent.parent / "results" / "indicator_opt"

LABELS = {"a": "A(OBV합집합)", "b": "B(스토캐스틱쌍바닥)", "c": "C(3바닥다이버전스)"}


def screen(start: str = "2026-01-01", tp_pct: float = 3.0, sl_pct: float = 3.0) -> pd.DataFrame:
    data = load_all()
    start_ts = pd.Timestamp(start)
    rows = []

    for ticker, df in data.items():
        idx = df.index
        latest = idx[-1]
        if latest < start_ts:
            continue
        win = df[df.index >= start_ts]

        a, b, c = build_signals(df, tp_pct, sl_pct, ticker)
        masks = {"a": a.fillna(False), "b": b.fillna(False), "c": c.fillna(False)}

        n = {k: int(v.reindex(win.index).fillna(False).sum()) for k, v in masks.items()}
        if sum(n.values()) == 0:
            continue

        total_mask = masks["a"] | masks["b"] | masks["c"]
        sig_dates = idx[total_mask.to_numpy()]
        last_sig = sig_dates[-1] if len(sig_dates) else None

        # 마지막 신호의 출처 전략(들)
        src = []
        for k, v in masks.items():
            if v.loc[last_sig] if last_sig is not None else False:
                src.append(LABELS[k])

        last_close = float(df["Close"].iloc[-1])
        fwd3 = fwd5 = None
        if last_sig is not None and last_sig < latest:
            entry = float(df["Close"].loc[last_sig])
            fwd = (last_close / entry - 1.0) * 100.0
            fwd3 = fwd >= tp_pct
            fwd5 = fwd <= -sl_pct

        rows.append({
            "ticker": ticker,
            "A": n["a"], "B": n["b"], "C": n["c"], "total": sum(n.values()),
            "latest_signal": last_sig,
            "source": "/".join(src) if src else "",
            "last_close": round(last_close, 2),
            "fwd_ge_tp": fwd3,
            "fwd_le_sl": fwd5,
        })

    res = pd.DataFrame(rows)
    if not res.empty:
        res = res.sort_values(["total", "latest_signal"], ascending=False)
    return res


def main() -> None:
    ap = argparse.ArgumentParser(description="2026년 확정 전략 A/B/C 스크리닝")
    ap.add_argument("--start", default="2026-01-01", help="검색 시작일(기본 2026-01-01)")
    ap.add_argument("--tp", type=float, default=3.0)
    ap.add_argument("--sl", type=float, default=3.0)
    args = ap.parse_args()

    res = screen(start=args.start, tp_pct=args.tp, sl_pct=args.sl)
    if res.empty:
        print("2026년 내 시그널 발생 종목 없음")
        return

    print(f"=== 2026년({args.start} 이후) 확정 전략 A/B/C 스크리닝 (TP{args.tp}%/SL{args.sl}%) ===")
    print(f"시그널 발생 종목: {len(res)}개 (2026년 총 신호 {int(res['total'].sum())}건)\n")

    tt = res[["ticker", "A", "B", "C", "total", "latest_signal", "source", "last_close", "fwd_ge_tp", "fwd_le_sl"]].copy()
    tt["latest_signal"] = pd.to_datetime(tt["latest_signal"]).dt.date
    print(tt.to_string(index=False))
    print()

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    fname = OUT_DIR / "screen_abc_2026.csv"
    res.to_csv(fname, index=False)
    print(f"\n저장: {fname}")


if __name__ == "__main__":
    main()
