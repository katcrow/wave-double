"""골든 픽스처 회귀 테스트 (Story 6.4).

운영 태깅(`compute_abc`)이 backtest 기준 구현이 검증한 전략 A/B/C/D/E를 통계적으로
재현하는지 ``tests/fixtures/golden/``의 고정 픽스처로 대조하는 gate다. 판정 기준은
완전 일치가 아닌 **전략별 Jaccard ≥ 0.9** (통계적 유사도)이며, backtest(yfinance
배당조정)와 운영(LS ``sujung``)의 조정-방식론 동등성이 별도 단발성 검증으로
확인된 후에만 이 gate가 유효하다(AD-5, "조용한 누락 금지"). 빈 픽스처·키 불완비·
non-READY 종목은 명시적 실패로 처리한다.
"""
from __future__ import annotations

import gzip
import json
from pathlib import Path

import numpy as np
import pandas as pd
import pytest

from backtest.indicator_opt.combine_strategies import build_signals
from backtest.indicator_opt.strategy_d import compute_strategy_d
from backtest.indicator_opt.strategy_e import compute_strategy_e
from backtest.indicators import atr
from backtest.strategy_api import compute_abc

REPO_ROOT = Path(__file__).resolve().parents[2]
GOLDEN_DIR = REPO_ROOT / "tests" / "fixtures" / "golden"

_GOLDEN_KEYS = ("A", "B", "C", "D", "E")
JACCARD_GATE = 0.9
TP_PCT = 3.0
SL_PCT = 3.0


def _load_golden_day() -> dict:
    with open(GOLDEN_DIR / "golden_day.json", encoding="utf-8") as f:
        return json.load(f)


def _load_golden_signals() -> dict:
    with open(GOLDEN_DIR / "golden_signals.json", encoding="utf-8") as f:
        return json.load(f)


def _load_ohlcv_raw() -> dict:
    with gzip.open(GOLDEN_DIR / "ohlcv_raw.json.gz", "rt", encoding="utf-8") as f:
        return json.load(f)


def _frame_from_ohlcv(ticker: str, ohlcv: dict) -> pd.DataFrame:
    """ohlcv_raw 컬럼형 배열에서 일봉 프레임(index=DatetimeIndex, OHLCV) 재구성."""
    rec = ohlcv["ohlcv"][ticker]
    df = pd.DataFrame(
        {
            "Open": rec["open"],
            "High": rec["high"],
            "Low": rec["low"],
            "Close": rec["close"],
            "Volume": rec["volume"],
        },
        index=pd.to_datetime(rec["trading_day"]),
    )
    df.index.name = "date"
    return df


def _windowed(mask: pd.Series, frame: pd.DataFrame, start_ts: pd.Timestamp) -> bool:
    return bool(mask.reindex(frame[frame.index >= start_ts].index).fillna(False).any())


def _valid_segments(frame: pd.DataFrame) -> list[pd.DataFrame]:
    """참조 계산에서도 invalid 봉을 인접한 정상 봉과 연결하지 않는다."""
    values = frame.loc[:, ("Open", "High", "Low", "Close", "Volume")]
    prices = values.loc[:, ("Open", "High", "Low", "Close")]
    valid = (
        np.isfinite(values.to_numpy(dtype=float)).all(axis=1)
        & (prices > 0).all(axis=1).to_numpy()
        & (values["Volume"] >= 0).to_numpy()
        & (values["High"] >= values["Low"]).to_numpy()
        & (values["High"] >= values["Open"]).to_numpy()
        & (values["High"] >= values["Close"]).to_numpy()
        & (values["Low"] <= values["Open"]).to_numpy()
        & (values["Low"] <= values["Close"]).to_numpy()
    )
    positions = np.flatnonzero(valid)
    if len(positions) == 0:
        return []
    split_points = np.flatnonzero(np.diff(positions) > 1) + 1
    return [
        frame.iloc[group[0] : group[-1] + 1]
        for group in np.split(positions, split_points)
    ]


def _reference_signals(universe: list[str], ohlcv: dict, start_ts: pd.Timestamp) -> dict[str, set[str]]:
    """유효 구간별 전용 계산기 기반 참조 시그널 집합을 재계산한다."""
    ref: dict[str, set[str]] = {k: set() for k in _GOLDEN_KEYS}
    for ticker in universe:
        frame = _frame_from_ohlcv(ticker, ohlcv)
        a, b, c = build_signals(frame, TP_PCT, SL_PCT, ticker, strict=True)
        masks = {
            "A": a.reindex(frame.index).fillna(False).astype(bool),
            "B": b.reindex(frame.index).fillna(False).astype(bool),
            "C": c.reindex(frame.index).fillna(False).astype(bool),
            "D": pd.Series(False, index=frame.index, dtype=bool),
            "E": pd.Series(False, index=frame.index, dtype=bool),
        }
        for segment in _valid_segments(frame):
            segment_masks = {
                "D": compute_strategy_d(segment),
                "E": compute_strategy_e(segment),
            }
            for k, mask in segment_masks.items():
                masks[k].loc[segment.index] = (
                    mask.reindex(segment.index).fillna(False).astype(bool).to_numpy()
                )
        atr_series = atr(frame["High"], frame["Low"], frame["Close"], window=14)
        for k in ("A", "B", "C"):
            masks[k].iloc[-1] = False
            masks[k] = (masks[k] & atr_series.notna() & (atr_series > 0)).astype(bool)
        segmented_atr = pd.Series(float("nan"), index=frame.index, dtype=float)
        for segment in _valid_segments(frame):
            segmented_atr.loc[segment.index] = atr(
                segment["High"], segment["Low"], segment["Close"], window=14
            ).reindex(segment.index).to_numpy()
        for k in ("D", "E"):
            masks[k].loc[[segment.index[-1] for segment in _valid_segments(frame)]] = False
            masks[k] = (masks[k] & segmented_atr.notna() & (segmented_atr > 0)).astype(bool)
        values = frame.loc[:, ("Open", "High", "Low", "Close", "Volume")]
        prices = values.loc[:, ("Open", "High", "Low", "Close")]
        valid_rows = pd.Series(
            np.isfinite(values.to_numpy(dtype=float)).all(axis=1)
            & (prices > 0).all(axis=1).to_numpy()
            & (values["Volume"] >= 0).to_numpy()
            & (values["High"] >= values["Low"]).to_numpy()
            & (values["High"] >= values["Open"]).to_numpy()
            & (values["High"] >= values["Close"]).to_numpy()
            & (values["Low"] <= values["Open"]).to_numpy()
            & (values["Low"] <= values["Close"]).to_numpy(),
            index=frame.index,
            dtype=bool,
        )
        for k in _GOLDEN_KEYS:
            masks[k] = (masks[k] & valid_rows).astype(bool)
        for k, m in masks.items():
            if _windowed(m, frame, start_ts):
                ref[k].add(ticker)
    return ref


def _new_signals(
    universe: list[str], ohlcv: dict, start_ts: pd.Timestamp
) -> tuple[dict[str, set[str]], dict[str, str]]:
    """compute_abc 기반 신규 시그널 집합과 종목별 status."""
    new: dict[str, set[str]] = {k: set() for k in _GOLDEN_KEYS}
    statuses: dict[str, str] = {}
    for ticker in universe:
        frame = _frame_from_ohlcv(ticker, ohlcv)
        result = compute_abc(frame, ticker=ticker)
        statuses[ticker] = result.status
        if result.status != "READY" or not result.signals:
            continue
        for k in _GOLDEN_KEYS:
            if _windowed(result.signals[k], frame, start_ts):
                new[k].add(ticker)
    return new, statuses


@pytest.fixture(scope="module")
def golden_day() -> dict:
    return _load_golden_day()


@pytest.fixture(scope="module")
def golden_signals() -> dict:
    return _load_golden_signals()


@pytest.fixture(scope="module")
def ohlcv_raw() -> dict:
    return _load_ohlcv_raw()


class TestFixturesPresent:
    """① 픽스처 존재·비공백·strategy_signals 키 완비+비공백 (빈 픽스처 명시적 실패, AD-5)."""

    def test_fixture_files_exist(self) -> None:
        for name in ("golden_day.json", "ohlcv_raw.json.gz", "golden_signals.json"):
            assert (GOLDEN_DIR / name).exists(), f"픽스처 누락: {name}"

    def test_golden_day_non_empty(self, golden_day: dict) -> None:
        assert golden_day["trading_day"] == "2026-08-26"
        assert golden_day["batch_kind"] == "close"
        assert isinstance(golden_day["universe"], list) and len(golden_day["universe"]) > 0

    def test_ohlcv_raw_non_empty(self, ohlcv_raw: dict) -> None:
        assert ohlcv_raw["sujung"] == "Y"
        assert isinstance(ohlcv_raw["ohlcv"], dict) and len(ohlcv_raw["ohlcv"]) > 0

    def test_signals_keys_complete_and_non_empty(self, golden_signals: dict) -> None:
        assert golden_signals["trading_day"] == "2026-08-26"
        signals = golden_signals["strategy_signals"]
        assert set(signals.keys()) == set(_GOLDEN_KEYS)
        for k in _GOLDEN_KEYS:
            values = signals[k]
            assert isinstance(values, list) and values, f"전략 {k} 시그널 비어 있음"
            assert values == sorted(set(values)), f"전략 {k} 시그널이 정렬되지 않았거나 중복됨"


class TestMembershipConsistency:
    """② universe·신호 집합이 ohlcv_raw에 모두 존재."""

    def test_universe_within_ohlcv(self, golden_day: dict, ohlcv_raw: dict) -> None:
        ohlcv_keys = set(ohlcv_raw["ohlcv"].keys())
        universe = golden_day["universe"]
        missing = [t for t in universe if t not in ohlcv_keys]
        assert not missing, f"universe 내 ohlcv_raw 미존재 종목: {missing}"

    def test_ohlcv_matches_universe_exactly(self, golden_day: dict, ohlcv_raw: dict) -> None:
        universe = set(golden_day["universe"])
        ohlcv_keys = set(ohlcv_raw["ohlcv"].keys())
        extras = sorted(ohlcv_keys - universe)
        missing = sorted(universe - ohlcv_keys)
        assert not extras, f"universe에 없는 ohlcv_raw 종목(여분): {extras}"
        assert not missing, f"ohlcv_raw에 없는 universe 종목(누락): {missing}"

    def test_ohlcv_record_arrays_equal_length(self, golden_day: dict, ohlcv_raw: dict) -> None:
        fields = ("trading_day", "open", "high", "low", "close", "volume")
        for ticker in golden_day["universe"]:
            rec = ohlcv_raw["ohlcv"][ticker]
            lengths = {f: len(rec[f]) for f in fields}
            expected = lengths["trading_day"]
            bad = [f for f, n in lengths.items() if n != expected]
            assert not bad, f"{ticker} ohlcv 배열 길이 불일치: {bad} ({lengths})"

    def test_ohlcv_trading_days_ascending_to_golden(self, golden_day: dict, ohlcv_raw: dict) -> None:
        golden = golden_day["trading_day"]
        for ticker in golden_day["universe"]:
            days = ohlcv_raw["ohlcv"][ticker]["trading_day"]
            assert days == sorted(days), f"{ticker} trading_day 오름차순 아님"
            assert len(set(days)) == len(days), f"{ticker} trading_day 중복 존재"
            assert days[-1] == golden, f"{ticker} 마지막 거래일 {days[-1]} != golden {golden}"

    def test_signal_tickers_within_universe(self, golden_day: dict, golden_signals: dict) -> None:
        universe = set(golden_day["universe"])
        for k in _GOLDEN_KEYS:
            outside = [t for t in golden_signals["strategy_signals"][k] if t not in universe]
            assert not outside, f"universe 밖 신호 종목({k}): {outside}"


class TestReferenceReproducibility:
    """③ ohlcv_raw로 참조 재계산 시 저장된 golden_signals와 정확히 일치 (수동 편집·오염 탐지)."""

    def test_recomputed_reference_matches(self, golden_day: dict, golden_signals: dict, ohlcv_raw: dict) -> None:
        # 참조 시그널 창 시작은 screen_abc.screen() 기본 창과 동일한 고정 2026-01-01을 쓴다.
        start_ts = pd.Timestamp("2026-01-01")
        ref = _reference_signals(golden_day["universe"], ohlcv_raw, start_ts)
        stored = golden_signals["strategy_signals"]
        for k in _GOLDEN_KEYS:
            assert ref[k] == set(stored[k]), (
                f"전략 {k} 참조 재계산 불일치: "
                f"ref-new={sorted(set(stored[k]) - ref[k])} new-ref={sorted(ref[k] - set(stored[k]))}"
            )


class TestJaccardGate:
    """④ compute_abc 결과와 참조의 전략별 Jaccard ≥ 0.9 (미달 시 불일치 목록 출력)."""

    def test_jaccard_ge_gate(self, golden_day: dict, golden_signals: dict, ohlcv_raw: dict) -> None:
        start_ts = pd.Timestamp("2026-01-01")
        ref = _reference_signals(golden_day["universe"], ohlcv_raw, start_ts)
        new, _ = _new_signals(golden_day["universe"], ohlcv_raw, start_ts)

        for k in _GOLDEN_KEYS:
            ref_set = ref[k]
            new_set = new[k]
            union = ref_set | new_set
            jaccard = len(ref_set & new_set) / len(union) if union else 1.0
            print(f"전략 {k} Jaccard: {jaccard:.4f}")
            assert jaccard >= JACCARD_GATE, (
                f"전략 {k} Jaccard {jaccard:.3f} < {JACCARD_GATE}. "
                f"ref-new={sorted(ref_set - new_set)} new-ref={sorted(new_set - ref_set)}"
            )


class TestAllReady:
    """⑤ 모든 universe 종목이 compute_abc에서 READY (non-READY는 명시적 실패·보고)."""

    def test_all_universe_ready(self, golden_day: dict, ohlcv_raw: dict) -> None:
        start_ts = pd.Timestamp("2026-01-01")
        _, statuses = _new_signals(golden_day["universe"], ohlcv_raw, start_ts)
        non_ready = [t for t, s in statuses.items() if s != "READY"]
        assert not non_ready, f"non-READY 종목 존재(조용한 누락 금지, AD-5): {non_ready}"
