"""LS sujung=Y ⇄ backtest raw fixture 조정-방식론 동등성 단발 검증 (AD-5 gate, retro item-10).

골든 픽스처 gate는 백테스트(yfinance 배당조정)와 운영(LS ``t8410 sujung``)의 조정
방식론이 신호 재현에 무시할 수 있는 수준으로 동등함을 **별도 단발성 검증**으로 확인한
뒤에만 유효하다(``tests/fixtures/golden/README.md`` AD-5). 이 도구가 그 단발성 검증이다.

절차:
  1. golden universe(98종목)의 ``ohlcv_raw.json.gz``(yfinance 배당조정 기준)을 로드한다.
  2. 동일 종목·동일 기간 ``[history_start, trading_day]``을 LS ``t8410 sujung=Y``로 실측 조회한다.
  3. 두 데이터 각각에 골든 gate와 동일한 ``_reference_signals``(전략 A/B/C/D/E/F)를 적용해
     창 ``[2026-01-01, trading_day]`` 신호 집합을 재계산한다.
  4. 전략별로 (a) LS vs fixture(동일 창·동일 웜업), (b) LS vs 저장 골든 참조 의
     Jaccard ≥ 0.9 를 gate로 강제한다. 미달 시 ``SystemExit(1)``.
  5. 종가 비율 괴리(평균 이탈 %, 최대, CV)를 종목별로 보고해 판정 근거를 남긴다.

실행:
  uv run --with pandas --with numpy --with pyarrow --with pytest \\
        tools/verify_adjustment_equivalence.py [--limit N] [--rate 1.0] [--history-start 2025-01-01]

``backtest``/``domain`` 패키지는 본 모듈 상단의 경로 부트스트랩으로 로드된다.
"""
from __future__ import annotations

import argparse
import gzip
import json
import sys
from pathlib import Path

import numpy as np
import pandas as pd

if sys.stdout and hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8")

_REPO_ROOT = Path(__file__).resolve().parents[1]
for _p in (_REPO_ROOT, _REPO_ROOT / "packages" / "domain"):
    if str(_p) not in sys.path:
        sys.path.insert(0, str(_p))

from backtest.tests.test_golden_fixture import JACCARD_GATE, _GOLDEN_KEYS, _reference_signals

GOLDEN_DIR = _REPO_ROOT / "tests" / "fixtures" / "golden"
OUT_DIR = _REPO_ROOT / "_bmad-output" / "implementation-artifacts"
TRADING_DAY = "2026-08-26"
WINDOW_START = "2026-01-01"
HISTORY_START = "2025-01-01"


def _load_env() -> dict[str, str]:
    env: dict[str, str] = {}
    env_file = _REPO_ROOT / ".env.local"
    for line in env_file.read_text(encoding="utf-8").splitlines():
        line = line.strip()
        if not line or line.startswith("#") or "=" not in line:
            continue
        k, v = line.split("=", 1)
        env[k.strip()] = v.strip()
    for key in ("LS_OPEN_API_APP_KEY", "LS_OPEN_API_APP_SECRET"):
        if not env.get(key):
            raise SystemExit(f"{key} 누락 — .env.local 확인")
    return env


def _load_ohlcv_raw() -> dict:
    with gzip.open(GOLDEN_DIR / "ohlcv_raw.json.gz", "rt", encoding="utf-8") as f:
        return json.load(f)


def _load_ls_cache(path: Path) -> dict | None:
    if not path.exists():
        return None
    with gzip.open(path, "rt", encoding="utf-8") as f:
        return json.load(f)


def _dump_ls_cache(path: Path, payload: dict) -> None:
    path.parent.mkdir(parents=True, exist_ok=True)
    data = json.dumps(payload, ensure_ascii=False).encode("utf-8")
    with gzip.open(path, "wb") as gz:
        gz.write(data)


def _load_golden_day() -> dict:
    with open(GOLDEN_DIR / "golden_day.json", encoding="utf-8") as f:
        return json.load(f)


def _load_golden_signals() -> dict:
    with open(GOLDEN_DIR / "golden_signals.json", encoding="utf-8") as f:
        return json.load(f)


def _truncate_ohlcv(raw: dict, start: str) -> dict:
    """trading_day >= start 배열만 남긴다(가격 4자리·거래량 2자리 반올림 인코딩 유지)."""
    ohlcv = {}
    for ticker, rec in raw["ohlcv"].items():
        keep = [i for i, d in enumerate(rec["trading_day"]) if d >= start]
        if not keep:
            ohlcv[ticker] = {
                "trading_day": [], "open": [], "high": [], "low": [], "close": [], "volume": []
            }
            continue
        i0, i1 = keep[0], keep[-1] + 1
        ohlcv[ticker] = {
            "trading_day": rec["trading_day"][i0:i1],
            "open": rec["open"][i0:i1],
            "high": rec["high"][i0:i1],
            "low": rec["low"][i0:i1],
            "close": rec["close"][i0:i1],
            "volume": rec["volume"][i0:i1],
        }
    return {"sujung": "Y", "ohlcv": ohlcv}


def _ls_date(value: str) -> str:
    """'YYYY-MM-DD' → LS t8410 'YYYYMMDD' (하이픈 미포함)."""
    return value.replace("-", "")


def _fetch_ls_ohlcv(env: dict[str, str], universe: list[str], sdate: str, edate: str, rate: float) -> tuple[dict, dict[str, str]]:
    """전체 universe t8410 sujung=Y 단일 콜로 실측 조회. (ohlcv, 실패 사유) 반환."""
    from apps.batch.ls_client import LsClient, LsClientConfig
    from apps.batch.ls_auth import LsOAuthTokenProvider

    ohlcv: dict[str, dict[str, list]] = {}
    failures: dict[str, str] = {}
    config = LsClientConfig(personal_requests_per_second=max(rate, 0.01))
    with LsClient(
        LsOAuthTokenProvider(env["LS_OPEN_API_APP_KEY"], env["LS_OPEN_API_APP_SECRET"]),
        config=config,
    ) as client:
        for i, ticker in enumerate(universe, 1):
            shcode = ticker.split(".")[0]
            resp = client.request(
                "t8410",
                {"t8410InBlock": {
                    "shcode": shcode, "gubun": "2", "qrycnt": 500,
                    "sdate": _ls_date(sdate), "edate": _ls_date(edate), "cts_date": "", "comp_yn": "N", "sujung": "Y",
                }},
            )
            if not resp.ok:
                failures[ticker] = f"LS 응답 실패: {resp.result_code} {resp.message} status={resp.status_code}"
                print(f"  [{i}/{len(universe)}] {ticker} FAIL: {failures[ticker]}")
                continue
            data = resp.data or {}
            if data.get("rsp_cd", "00000") != "00000":
                failures[ticker] = f"LS rsp_cd={data.get('rsp_cd')} msg={data.get('rsp_msg')}"
                print(f"  [{i}/{len(universe)}] {ticker} FAIL: {failures[ticker]}")
                continue
            rows = data.get("t8410OutBlock1") or []
            if not rows:
                failures[ticker] = "LS 조회 결과 0행"
                print(f"  [{i}/{len(universe)}] {ticker} FAIL: 0행")
                continue
            days = [r["date"] for r in rows]
            if days != sorted(days):
                rows = list(reversed(rows))  # LS는 내림차순 반환 → 오름차순 정렬 보장
                days = [r["date"] for r in rows]
            date_day = sorted(set(days))
            if len(date_day) != len(days):
                failures[ticker] = f"중복 거래일({len(days)}-{len(date_day)})"
                print(f"  [{i}/{len(universe)}] {ticker} FAIL: {failures[ticker]}")
                continue
            iso = [f"{d[:4]}-{d[4:6]}-{d[6:]}" for d in days]
            ohlcv[ticker] = {
                "trading_day": iso,
                "open": [round(float(r["open"]), 4) for r in rows],
                "high": [round(float(r["high"]), 4) for r in rows],
                "low": [round(float(r["low"]), 4) for r in rows],
                "close": [round(float(r["close"]), 4) for r in rows],
                "volume": [round(float(r["jdiff_vol"]), 2) for r in rows],
            }
            if i % 10 == 0 or i == len(universe):
                print(f"  [{i}/{len(universe)}] {ticker} OK ({len(rows)}봉)")
    return {"sujung": "Y", "ohlcv": ohlcv}, failures


def _jaccard(a: set[str], b: set[str]) -> float:
    union = a | b
    return len(a & b) / len(union) if union else 1.0


def _close_ratio_stats(fixture: dict, ls: dict, sdate: str) -> dict[str, dict]:
    stats: dict[str, dict] = {}
    for ticker, rec in ls["ohlcv"].items():
        f_rec = fixture["ohlcv"].get(ticker)
        if not f_rec:
            continue
        f_map = dict(zip(f_rec["trading_day"], f_rec["close"], strict=False))
        ratios = []
        for day, close in zip(rec["trading_day"], rec["close"], strict=False):
            if day in f_map and f_map[day] > 0 and close > 0 and day >= sdate:
                ratios.append(close / f_map[day])
        if not ratios:
            continue
        r = np.asarray(ratios)
        devs = np.abs(r - 1.0) * 100.0
        stats[ticker] = {
            "n": int(len(r)),
            "mean_dev_pct": float(devs.mean()),
            "max_dev_pct": float(devs.max()),
            "p90_dev_pct": float(float(np.percentile(devs, 90))),
            "cv": float(r.std(ddof=1) / r.mean()) if len(r) > 1 else 0.0,
        }
    return stats


def _fmt_pct(v: float) -> str:
    return f"{v:.2f}%"


def main() -> None:
    ap = argparse.ArgumentParser(description="LS sujung=Y vs golden raw fixture 조정 동등성 gate")
    ap.add_argument("--trading-day", default=TRADING_DAY)
    ap.add_argument("--window-start", default=WINDOW_START)
    ap.add_argument("--history-start", default=HISTORY_START, help="LS 조회 시작일(웜업 포함)")
    ap.add_argument("--rate", type=float, default=1.0, help="LS t8410 초당 요청 수(게이트 기본 1.0)")
    ap.add_argument("--limit", type=int, default=None, help="smoke용 종목 수 제한")
    ap.add_argument("--no-write", action="store_true", help="evidence 파일 기록 생략")
    ap.add_argument("--no-cache", action="store_true", help="LS 조회 결과 캐시 사용 안 함")
    args = ap.parse_args()

    start_ts = pd.Timestamp(args.window_start)
    env = _load_env()
    golden_day = _load_golden_day()
    golden_signals = _load_golden_signals()
    stored = golden_signals["strategy_signals"]
    if golden_day["trading_day"] != args.trading_day:
        raise SystemExit(f"golden_day trading_day {golden_day['trading_day']} != {args.trading_day}")

    universe = golden_day["universe"]
    if args.limit:
        universe = universe[: args.limit]

    print(f"golden universe {len(universe)}종목, 기간 {args.history_start}~{args.trading_day}")
    print(f"LS t8410 sujung=Y 실측 조회 시작...")
    ls_cache = OUT_DIR / f"ls-ohlcv-cache-{args.history_start}-{args.trading_day}.json.gz"
    if not args.no_cache and ls_cache.exists():
        print(f"LS 캐시 사용: {ls_cache}")
        ls_raw = _load_ls_cache(ls_cache)
        failures = {}
    else:
        ls_raw, failures = _fetch_ls_ohlcv(env, universe, args.history_start, args.trading_day, args.rate)
        if not args.no_cache:
            _dump_ls_cache(ls_cache, ls_raw)
            print(f"LS 캐시 저장: {ls_cache}")
    fail_tickers = sorted(failures.keys())
    if fail_tickers:
        print("\n[실패] LS 조회 실패 종목(조용한 누락 금지, AD-5):")
        for t in fail_tickers:
            print(f"  {t}: {failures[t]}")

    # 동일 기간·동일 웜업으로 apples-to-apples 비교
    fixture_trunc = _truncate_ohlcv(_load_ohlcv_raw(), args.history_start)
    fixture_universe = [t for t in universe if t in fixture_trunc["ohlcv"]]

    ref_fixture = _reference_signals(fixture_universe, fixture_trunc, start_ts)
    ls_universe = [t for t in universe if t in ls_raw["ohlcv"]]
    ref_ls = _reference_signals(ls_universe, ls_raw, start_ts)

    ratio_stats = _close_ratio_stats(fixture_trunc, ls_raw, args.history_start)

    print("\n=== 조정-방식론 동등성 (전략별 Jaccard) ===")
    print(f"gate 기준: Jaccard ≥ {JACCARD_GATE:.1f}")
    print(f"{'전략':<4} {'LS vs fixture':>14} {'LS vs golden':>14} {'ref(fix)':>9} {'ref(ls)':>9} {'golden':>7}")

    rows: list[dict] = []
    disagreements: dict[str, dict] = {}
    gate_ok = True
    for k in _GOLDEN_KEYS:
        j_ls_fix = _jaccard(ref_ls[k], ref_fixture[k])
        j_ls_go = _jaccard(ref_ls[k], set(stored[k]))
        ok = j_ls_fix >= JACCARD_GATE and j_ls_go >= JACCARD_GATE
        gate_ok = gate_ok and ok
        only_ls = sorted(ref_ls[k] - ref_fixture[k])
        only_fix = sorted(ref_fixture[k] - ref_ls[k])
        disagreements[k] = {
            "만 LS(신호 존재)": only_ls,
            "만 fixture(신호 존재)": only_fix,
        }
        print(
            f"{k:<4} {j_ls_fix:>12.4f} {j_ls_go:>14.4f} "
            f"{len(ref_fixture[k]):>9d} {len(ref_ls[k]):>9d} {len(stored[k]):>7d}"
        )
        rows.append({
            "strategy": k,
            "jaccard_ls_vs_fixture": round(j_ls_fix, 4),
            "jaccard_ls_vs_golden": round(j_ls_go, 4),
            "ref_fixture_size": len(ref_fixture[k]),
            "ref_ls_size": len(ref_ls[k]),
            "stored_golden_size": len(stored[k]),
            "pass": ok,
            "only_ls": only_ls,
            "only_fixture": only_fix,
        })

    print("\n=== 전략별 불일치 종목 (LS vs fixture) ===")
    for k in _GOLDEN_KEYS:
        only_ls = disagreements[k]["만 LS(신호 존재)"]
        only_fix = disagreements[k]["만 fixture(신호 존재)"]
        if not only_ls and not only_fix:
            print(f"{k}: 일치")
            continue
        print(f"{k}: LS만 {len(only_ls)}개 {only_ls} / fixture만 {len(only_fix)}개 {only_fix}")

    print("\n=== 종가 괴리 (LS sujung=Y / yfinance) 종목별 요약 ===")
    devs = [s["mean_dev_pct"] for s in ratio_stats.values()]
    maxes = [s["max_dev_pct"] for s in ratio_stats.values()]
    if devs:
        print(f"종목 수(공통 날짜 있음): {len(devs)}")
        print(f"일평균 |괴리|%:  평균 {np.mean(devs):.2f}  중앙 {np.median(devs):.2f}  최대 {np.max(maxes):.2f}")
        worst = sorted(((s["max_dev_pct"], t) for t, s in ratio_stats.items()), reverse=True)[:5]
        print("최대 괴리 상위 5종목:")
        for v, t in worst:
            print(f"  {t}: max {v:.2f}% (n={ratio_stats[t]['n']}, cv={ratio_stats[t]['cv']:.4f})")
    else:
        print("공통 날짜 없음")

    if fail_tickers:
        gate_ok = False
        print(f"\n[결과] FAIL — LS 조회 실패 {len(fail_tickers)}종목")
    elif gate_ok:
        print(f"\n[결과] PASS — 모든 전략 Jaccard ≥ {JACCARD_GATE}")
    else:
        print(f"\n[결과] FAIL — 전략별 Jaccard 미달")

    if not args.no_write:
        OUT_DIR.mkdir(parents=True, exist_ok=True)
        day = args.trading_day
        payload = {
            "title": "조정-방식론 동등성 단발 검증 (AD-5, retro item-10)",
            "trading_day": day,
            "window_start": args.window_start,
            "history_start": args.history_start,
            "universe_count": len(universe),
            "ls_call_limit": args.limit,
            "rate_per_sec": args.rate,
            "jaccard_gate": JACCARD_GATE,
            "fail_tickers": fail_tickers,
            "failures": failures,
            "per_strategy": rows,
            "close_ratio_stats": ratio_stats,
            "disagreements": disagreements,
            "gate_pass": gate_ok,
        }
        ev_path = OUT_DIR / f"adjustment-equivalence-{day}.json"
        ev_path.write_text(json.dumps(payload, ensure_ascii=False, indent=2), encoding="utf-8")
        print(f"\nevidence: {ev_path}")
    sys.exit(0 if gate_ok else 1)


if __name__ == "__main__":
    main()