"""골든 픽스처 결정적 재생성 도구 (Story 2.4 개발 유틸).

``backtest/data/raw/*.parquet`` 원본에서 다음 3파일을 결정적으로 재생성한다.

- ``golden_day.json`` — 고정 거래일·universe
- ``ohlcv_raw.json.gz`` — universe 별 전체 일봉 원본(수정주가 ``sujung=Y``) gzip 압축
- ``golden_signals.json`` — 참조 시그널 집합(A/B/C)

판정 기준은 완전 일치가 아닌 통계적 유사도(**전략별 Jaccard ≥ 0.9**)이며, backtest
(yfinance 배당조정)와 운영(LS ``sujung``)의 조정-방식론 동등성이 별도 단발성
검증으로 확인된 후에만 유효하다(AD-5, "조용한 누락 금지"). 재생성 시 고정된
golden 파일 대비 새로 계산한 ``compute_abc`` 결과의 Jaccard가 전략별로 0.9 이상인지
sanity로 강제하고, 미달이면 ``SystemExit(1)``을 발생시킨다.

실행: ``uv run --with pandas --with numpy --with pyarrow \\
      python tests/fixtures/golden/generate_golden.py [--trading-day 2026-08-26] [--window-start 2026-01-01]``

``backtest``/``domain`` 패키지는 본 모듈 상단의 경로 부트스트랩으로 자동 로드된다.
"""
from __future__ import annotations

import argparse
import gzip
import json
import sys
from pathlib import Path

# 저장소 루트를 import 경로에 추가: backtest(루트)와 domain(packages/domain) 모두
# 스크립트 실행 환경(PYTHONPATH=packages/domain 등)에서 로드되도록 한다.
_REPO_ROOT = Path(__file__).resolve().parents[3]
for _p in (_REPO_ROOT, _REPO_ROOT / "packages" / "domain"):
    if str(_p) not in sys.path:
        sys.path.insert(0, str(_p))

import pandas as pd

from backtest.data.loader import DATA_DIR, list_tickers, load_ticker
from backtest.indicator_opt.combine_strategies import build_signals
from backtest.strategy_api import compute_abc
from domain.ohlcv_cache import MIN_HISTORY_TRADING_DAYS

GOLDEN_DIR = Path(__file__).resolve().parent

# 고정 파라미터 — 언더레이 raw 일봉 범위와 함께 골든 픽스처 스키마 계약을 이룬다.
TRADING_DAY = "2026-08-26"
WINDOW_START = "2026-01-01"
TP_PCT = 3.0
SL_PCT = 3.0
JACCARD_GATE = 0.9  # 통계적 유사도 기준(AD-5 조정-방식론 동등성 선행조건)
_GOLDEN_KEYS = ("A", "B", "C")


def _round_hist(hist: pd.DataFrame) -> pd.DataFrame:
    """골든 픽스처 인코딩(가격 4자리, 거래량 2자리 반올림)을 그대로 적용한 프레임."""
    out = hist.copy()
    for col in ("Open", "High", "Low", "Close"):
        out[col] = out[col].round(4)
    out["Volume"] = out["Volume"].round(2)
    return out


def _ref_signal(mask: pd.Series, frame: pd.DataFrame, start_ts: pd.Timestamp) -> bool:
    """창 [window_start, trading_day] 내 신호 1회 이상 여부 (screen_abc.screen() 규칙)."""
    return bool(mask.reindex(frame[frame.index >= start_ts].index).fillna(False).any())


def build_universe(trading_day: str, data_dir: Path = DATA_DIR) -> list[str]:
    """해당 거래일까지 일봉이 120행 이상인 종목을 universe로 산출(정렬)."""
    gday = pd.Timestamp(trading_day)
    universe = []
    for ticker in sorted(list_tickers(data_dir)):
        hist = load_ticker(ticker, data_dir)
        hist = hist[hist.index <= gday]
        if len(hist) >= MIN_HISTORY_TRADING_DAYS:
            universe.append(ticker)
    return universe


def compute_reference(
    universe: list[str], frame_fn, start_ts: pd.Timestamp
) -> dict[str, dict[str, bool]]:
    """build_signals(비엄격 기본 호출) 기반 참조 시그널. 매 전략 bool 매핑 반환."""
    ref: dict[str, dict[str, bool]] = {}
    for ticker in universe:
        frame = frame_fn(ticker)
        a, b, c = build_signals(frame, TP_PCT, SL_PCT, ticker)
        masks = {"A": a, "B": b, "C": c}
        ref[ticker] = {k: _ref_signal(m, frame, start_ts) for k, m in masks.items()}
    return ref


def compute_new(
    universe: list[str], frame_fn, start_ts: pd.Timestamp
) -> tuple[dict[str, dict[str, bool]], dict[str, str]]:
    """compute_abc 기반 신규 시그널. (시그널 매핑, 종목별 status) 반환."""
    new: dict[str, dict[str, bool]] = {}
    statuses: dict[str, str] = {}
    for ticker in universe:
        frame = frame_fn(ticker)
        result = compute_abc(frame, ticker=ticker)
        statuses[ticker] = result.status
        if result.status != "READY" or not result.signals:
            new[ticker] = {k: False for k in _GOLDEN_KEYS}
            continue
        win = frame[frame.index >= start_ts].index
        new[ticker] = {
            k: bool(result.signals[k].reindex(win).fillna(False).any())
            for k in _GOLDEN_KEYS
        }
    return new, statuses


def jaccard(ref_set: set[str], new_set: set[str]) -> float:
    union = ref_set | new_set
    if not union:
        return 1.0
    return len(ref_set & new_set) / len(union)


def _rounded_frame(ticker: str, gday: pd.Timestamp, data_dir: Path = DATA_DIR) -> pd.DataFrame:
    hist = load_ticker(ticker, data_dir)
    return _round_hist(hist[hist.index <= gday])


def generate(trading_day: str = TRADING_DAY, window_start: str = WINDOW_START, data_dir: Path = DATA_DIR) -> None:
    gday = pd.Timestamp(trading_day)
    start_ts = pd.Timestamp(window_start)

    universe = build_universe(trading_day, data_dir)
    if not universe:
        raise SystemExit(f"universe 비어 있음: {trading_day}")
    frame_fn = lambda t: _rounded_frame(t, gday, data_dir)

    ref = compute_reference(universe, frame_fn, start_ts)
    golden_signals = {
        "trading_day": trading_day,
        "strategy_signals": {
            k: sorted(t for t in universe if ref[t][k]) for k in _GOLDEN_KEYS
        },
    }

    _assert_parity(universe, frame_fn, ref, start_ts, gday)

    ohlcv = {}
    for ticker in universe:
        frame = frame_fn(ticker)
        ohlcv[ticker] = {
            "trading_day": [d.strftime("%Y-%m-%d") for d in frame.index.date],
            "open": [float(v) for v in frame["Open"].to_list()],
            "high": [float(v) for v in frame["High"].to_list()],
            "low": [float(v) for v in frame["Low"].to_list()],
            "close": [float(v) for v in frame["Close"].to_list()],
            "volume": [float(v) for v in frame["Volume"].to_list()],
        }

    golden_day = {
        "trading_day": trading_day,
        "batch_kind": "close",
        "universe": universe,
    }

    (GOLDEN_DIR / "golden_day.json").write_text(
        json.dumps(golden_day, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    payload = json.dumps({"sujung": "Y", "ohlcv": ohlcv}, ensure_ascii=False).encode("utf-8")
    with open(GOLDEN_DIR / "ohlcv_raw.json.gz", "wb") as raw:
        with gzip.GzipFile(filename="", mode="wb", fileobj=raw, mtime=0) as gz:
            gz.write(payload)
    (GOLDEN_DIR / "golden_signals.json").write_text(
        json.dumps(golden_signals, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )

    print(f"golden 픽스처 재생성 완료: universe {len(universe)}종목, 거래일 {trading_day}")
    for k in _GOLDEN_KEYS:
        print(f"  참조 시그널 {k}: {len(golden_signals['strategy_signals'][k])}종목")


def _assert_parity(universe, frame_fn, ref, start_ts, gday) -> None:
    """재생성 sanity: 참조 대비 compute_abc Jaccard가 전략별 0.9 이상이어야 한다."""
    new, statuses = compute_new(universe, frame_fn, start_ts)
    non_ready = [t for t, s in statuses.items() if s != "READY"]
    if non_ready:
        raise SystemExit(f"non-READY 종목 존재: {sorted(non_ready)}")
    for k in _GOLDEN_KEYS:
        ref_set = {t for t in universe if ref[t][k]}
        new_set = {t for t in universe if new[t][k]}
        j = jaccard(ref_set, new_set)
        if j < JACCARD_GATE:
            raise SystemExit(
                f"전략 {k} Jaccard {j:.3f} < {JACCARD_GATE} 미달. "
                f"ref-new={sorted(ref_set - new_set)} new-ref={sorted(new_set - ref_set)}"
            )
        print(f"  sanity Jaccard {k}: {j:.4f}")


def main() -> None:
    ap = argparse.ArgumentParser(description="골든 픽스처 결정적 재생성")
    ap.add_argument("--trading-day", default=TRADING_DAY, help=f"거래일(기본 {TRADING_DAY})")
    ap.add_argument("--window-start", default=WINDOW_START, help=f"참조 시그널 창 시작(기본 {WINDOW_START})")
    args = ap.parse_args()
    generate(trading_day=args.trading_day, window_start=args.window_start)


if __name__ == "__main__":
    main()
