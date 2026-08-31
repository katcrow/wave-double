"""수정주가 정합 검증 (읽기 전용).

백테스트 데이터(yfinance auto_adjust=True, 분할+배당 조정)와
LS t8410의 sujung=Y / sujung=N 를 동일 종목·기간으로 대조한다.

목적: PRD §10-2 / FR-3a의 [검증 필요] 해소.
  - LS sujung=Y 가 배당까지 조정하는가?
  - 백테스트 데이터셋과 실전 데이터셋이 같은 기준인가?
    다르면 FR-3의 골든 픽스처 회귀 대조가 통과할 수 없다.

실행: PYTHONIOENCODING=utf-8 uv run --with pandas --with pyarrow --python 3.12 \
        _bmad-output/.../analysis_sujung.py
"""
from __future__ import annotations

import json
import os
import time
import urllib.request
from pathlib import Path

import pandas as pd

BASE = "https://openapi.ls-sec.co.kr:8080"
ROOT = Path(__file__).resolve().parents[4]


def load_env():
    env = {}
    for line in (ROOT / ".env.local").read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if line.startswith("#") or "=" not in line:
            continue
        k, v = line.split("=", 1)
        env[k.strip()] = v.strip()
    return env


def post(path, headers, body):
    req = urllib.request.Request(
        BASE + path,
        data=json.dumps(body).encode(),
        headers={"content-type": "application/json; charset=utf-8", **headers},
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.loads(r.read().decode())


def get_token(env):
    data = (
        f"appkey={env['LS_OPEN_API_APP_KEY']}&appsecretkey={env['LS_OPEN_API_APP_SECRET']}"
        "&grant_type=client_credentials&scope=oob"
    ).encode()
    req = urllib.request.Request(
        BASE + "/oauth2/token",
        data=data,
        headers={"content-type": "application/x-www-form-urlencoded"},
        method="POST",
    )
    with urllib.request.urlopen(req, timeout=30) as r:
        return json.loads(r.read().decode())["access_token"]


def chart(tok, shcode, sujung, sdate, edate, cnt=500):
    d = post(
        "/stock/chart",
        {"authorization": f"Bearer {tok}", "tr_cd": "t8410", "tr_cont": "N", "tr_cont_key": ""},
        {
            "t8410InBlock": {
                "shcode": shcode, "gubun": "2", "qrycnt": cnt,
                "sdate": sdate, "edate": edate,
                "cts_date": "", "comp_yn": "N", "sujung": sujung,
            }
        },
    )
    rows = d.get("t8410OutBlock1") or []
    if not rows:
        return pd.DataFrame()
    df = pd.DataFrame(rows)
    df["date"] = pd.to_datetime(df["date"], format="%Y%m%d")
    return df.set_index("date")[["open", "high", "low", "close", "jdiff_vol"]].sort_index()


TICKERS = ["000070", "000100", "000150", "005930", "000660"]
SDATE, EDATE = "20240101", "20260827"


def main():
    env = load_env()
    tok = get_token(env)
    print("token ok\n")

    print("=" * 96)
    print("수정주가 기준 대조 — yfinance(auto_adjust=True) vs LS t8410 sujung=Y vs sujung=N")
    print(f"기간 {SDATE}~{EDATE}, 종가 기준")
    print("=" * 96)

    for t in TICKERS:
        pq = ROOT / "backtest" / "data" / "raw" / f"{t}_KS.parquet"
        if not pq.exists():
            print(f"\n[{t}] parquet 없음 — 건너뜀")
            continue
        yf = pd.read_parquet(pq)
        yf.index = pd.to_datetime(yf.index)
        yf = yf[(yf.index >= SDATE) & (yf.index <= EDATE)]["Close"]

        ly = chart(tok, t, "Y", SDATE, EDATE); time.sleep(1.1)
        ln = chart(tok, t, "N", SDATE, EDATE); time.sleep(1.1)
        if ly.empty or ln.empty:
            print(f"\n[{t}] LS 응답 없음 — 건너뜀")
            continue

        idx = yf.index.intersection(ly.index).intersection(ln.index)
        if len(idx) == 0:
            print(f"\n[{t}] 공통 거래일 없음")
            continue
        a, b, c = yf.loc[idx], ly.loc[idx, "close"], ln.loc[idx, "close"]

        dyn = (b - c).abs()                       # sujung Y vs N
        dyy = (a - b).abs() / b * 100             # yfinance vs sujung Y
        dyn2 = (a - c).abs() / c * 100            # yfinance vs sujung N

        print(f"\n[{t}]  공통 거래일 {len(idx)}건  ({idx.min().date()} ~ {idx.max().date()})")
        print(f"  LS sujung=Y vs N      : 불일치 {int((dyn > 0.5).sum()):4d}건 / 최대차 {dyn.max():>10,.0f}원")
        print(f"  yfinance vs sujung=Y  : 불일치 {int((dyy > 0.01).sum()):4d}건 / 최대 {dyy.max():6.2f}% / 평균 {dyy.mean():5.2f}%")
        print(f"  yfinance vs sujung=N  : 불일치 {int((dyn2 > 0.01).sum()):4d}건 / 최대 {dyn2.max():6.2f}% / 평균 {dyn2.mean():5.2f}%")
        print(f"  최근 종가  yf={a.iloc[-1]:,.0f}  sujungY={b.iloc[-1]:,.0f}  sujungN={c.iloc[-1]:,.0f}")
        print(f"  최초 종가  yf={a.iloc[0]:,.0f}  sujungY={b.iloc[0]:,.0f}  sujungN={c.iloc[0]:,.0f}")

        worst = dyy.nlargest(3)
        if worst.iloc[0] > 0.01:
            print("  yfinance vs sujung=Y 최대 괴리 3일:")
            for d, v in worst.items():
                print(f"    {d.date()}  yf={a[d]:>10,.0f}  sujungY={b[d]:>10,.0f}  차 {v:5.2f}%")


if __name__ == "__main__":
    main()
