"""최근 3개월 기간 스크리닝 — 현재 매수 후보 종목 발굴

상위 3개 조합의 합집합 신호(및 개별 조합)로 최근 3개월 내 시그널이
발생한 종목을 스크리닝한다. 시그널 봉은 종가 진입(TP 3%/SL 3%) 가정.

- 스크리닝 창: 최근 N개월(기본 3) = 분석 최신일 대비 캘린더 N개월
- 후보 종목: 창 내 시그널 발생 1회 이상
- 각 종목별: 시그널 수, 최근 시그널일, 최신 종가, 진입 후 수익률(3%/5% 도달 여부)
"""

from __future__ import annotations

import argparse
from dataclasses import dataclass
from pathlib import Path

import pandas as pd

from ..data.loader import load_all
from . import _signals as S
from .union import TOP3, VOLUME

OUT_DIR = Path(__file__).parent.parent / "results" / "indicator_opt"


@dataclass
class TickerResult:
    ticker: str
    latest_date: pd.Timestamp
    union_count: int
    latest_signal: pd.Timestamp | None
    signals_recent: dict
    last_close: float
    fwd_3pct_reached: bool | None
    fwd_5pct_hit: bool | None


def screen(months: int = 3, tp_pct: float = 3.0, sl_pct: float = 5.0, label: str = "union") -> pd.DataFrame:
    data = load_all()
    cutoff = None

    rows = []
    for ticker, df in data.items():
        idx = df.index
        latest = idx[-1]
        cutoff = latest - pd.DateOffset(months=months)
        recent_slice = df[df.index >= cutoff]

        per_strat = {}
        union = pd.Series(False, index=idx)
        # OBV 필터 마스크 (합집합과 동일: window=3)
        obv_mask = pd.Series(False, index=idx)
        for _, iname, p in VOLUME:
            try:
                obv_mask |= S.get_signal_fn(iname)(df, **p).fillna(False)
            except Exception:
                pass
        for strat_name, ina, pa, inb, pb in TOP3:
            try:
                ma = S.get_signal_fn(ina)(df, **pa)
                mb = S.get_signal_fn(inb)(df, **pb)
                combo = (ma.fillna(False) & mb.fillna(False)) & obv_mask
            except Exception:
                combo = pd.Series(False, index=idx)
            union |= combo
            recent_combo = combo.reindex(recent_slice.index).fillna(False)
            per_strat[strat_name] = int(recent_combo.sum())

        recent_union = union.reindex(recent_slice.index).fillna(False)
        n_sig = int(recent_union.sum())

        if n_sig == 0:
            continue

        recent_idx = recent_slice.index
        sig_dates = recent_idx[recent_union.to_numpy()]
        last_sig = sig_dates[-1] if len(sig_dates) else None

        # 진입(최신 시그널) 후 수익률 상태 확인 (마지막 봉 종가 기준)
        last_close = float(df["Close"].iloc[-1])
        fwd3 = fwd5 = None
        if last_sig is not None and last_sig < latest:
            entry = float(df["Close"].loc[last_sig])
            fwd = (last_close / entry - 1.0) * 100.0
            fwd3 = fwd >= tp_pct
            fwd5 = fwd <= -sl_pct

        rows.append({
            "ticker": ticker,
            "latest_date": latest,
            "union_signals": n_sig,
            "latest_signal": last_sig,
            **per_strat,
            "last_close": round(last_close, 2),
            "fwd_ge_tp": fwd3,
            "fwd_le_sl": fwd5,
        })

    res = pd.DataFrame(rows)
    if not res.empty:
        res = res.sort_values(["union_signals", "latest_signal"], ascending=False)
    return res


def main() -> None:
    ap = argparse.ArgumentParser(description="최근 3개월 매수 후보 스크리닝")
    ap.add_argument("--months", type=int, default=3)
    ap.add_argument("--min-signals", type=int, default=1, help="창 내 최소 시그널 수")
    ap.add_argument("--tp", type=float, default=3.0)
    ap.add_argument("--sl", type=float, default=5.0)
    args = ap.parse_args()

    res = screen(months=args.months, tp_pct=args.tp, sl_pct=args.sl)
    if res.empty:
        print("최근 해당 기간 내 시그널 발생 종목 없음")
        return

    filt = res[res["union_signals"] >= args.min_signals].copy()

    print(f"=== 최근 {args.months}개월({filt['latest_date'].max().date()} 기준) 매수 후보 스크리닝 ===")
    print(f"(합집합+OBV3: (RSI+CCI|RSI+IBS|RSI+ADX) & OBV, 진입 TP{args.tp}%/SL{args.sl}%)\n")
    print(f"시그널 발생 종목: {len(filt)}개\n")

    show = filt.copy()
    show["latest_date"] = show["latest_date"].dt.date
    show["latest_signal"] = pd.to_datetime(show["latest_signal"]).dt.date
    print(show.to_string(index=False))

    # 현재 시점(각 종목 최신 거래일)에 시그널이 살아있는(당일 발생) 종목 = 즉시 대응 가능
    tsig = pd.to_datetime(filt["latest_signal"])
    tdate = filt["latest_date"]
    fresh = filt[tsig == tdate]
    print(f"\n[각 종목 최신 거래일 당일 시그널 발생(=즉시 매수 가능) 종목: {len(fresh)}개]")
    if not fresh.empty:
        print(fresh[["ticker", "union_signals", "latest_signal"]].to_string(index=False))

    OUT_DIR.mkdir(parents=True, exist_ok=True)
    fname = OUT_DIR / f"screen_{args.months}m.csv"
    filt.to_csv(fname, index=False)
    print(f"\n저장: {fname}")


if __name__ == "__main__":
    main()
