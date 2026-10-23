"""실시간 지수 등락률과 과거 일봉 결과로 계산하는 실험용 기준 확률."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime, time, timedelta, timezone
from decimal import Decimal
from math import isfinite
from typing import Any, Protocol

from .ls_client import LsResponse

INDEX_CODES = {"KOSPI": "001", "KOSDAQ": "301"}


class IndexChartClient(Protocol):
    def request(self, tr_code: str, params: dict[str, Any], *, path: str | None = None) -> LsResponse: ...


@dataclass(frozen=True)
class DailyIndexBar:
    trading_day: date
    high: float
    close: float


class LsIndexHistoryProvider:
    def __init__(self, client: IndexChartClient) -> None:
        self._client = client

    def fetch(self, market: str, count: int = 500) -> list[DailyIndexBar]:
        code = INDEX_CODES[market]
        response = self._client.request("t8429", {"t8429InBlock": {
            "shcode": code, "gubun": "2", "qrycnt": min(max(count, 2), 500),
            "sdate": " ", "edate": "99999999", "cts_date": " ", "comp_yn": "N",
        }})
        if not response.ok:
            raise RuntimeError(f"LS t8429 lookup failed for {market}: {response.result_code}")
        rows = response.data.get("t8429OutBlock1") if isinstance(response.data, dict) else None
        if not isinstance(rows, list):
            raise RuntimeError(f"LS t8429 response malformed for {market}")
        bars = []
        for row in rows:
            try:
                bars.append(DailyIndexBar(date.fromisoformat(str(row["date"])), _number(row["high"]), _number(row["close"])))
            except (KeyError, TypeError, ValueError):
                raise RuntimeError(f"LS t8429 response contains malformed bar for {market}")
        return sorted(bars, key=lambda bar: bar.trading_day)


def _number(value: Any) -> float:
    parsed = float(value)
    if not isfinite(parsed):
        raise ValueError("non-finite index price")
    return parsed


TARGET_RETURN_PCT = 0.5
HALF_LIFE_SAMPLES = 120
MODEL_VERSION = "historical_conditional_rate_v2"


@dataclass(frozen=True)
class ProbabilityEstimate:
    probability: float
    base_rate: float
    diagnostics: dict[str, Any]
    history: list[dict[str, Any]]


def _weighted_laplace(samples: list[tuple[float, int]]) -> tuple[float, float, float]:
    """(가중치, 라벨) 표본에서 ``(Σw·y + 1) / (Σw + 2)``와 가중합을 돌려준다."""
    weight_sum = sum(weight for weight, _ in samples)
    success_weight = sum(weight * label for weight, label in samples)
    return (success_weight + 1) / (weight_sum + 2), weight_sum, success_weight


def empirical_probability(bars: list[DailyIndexBar], today_change_pct: float, today: date) -> ProbabilityEstimate:
    """과거의 같은 방향/비슷한 일간 변동 구간에서 익일 고가가 목표(+0.5%)를 넘은 비율.

    label(d)는 high(next day) > close(d) × (1 + TARGET_RETURN_PCT/100). 오늘 데이터는
    학습 표본에서 제외한다. 표본마다 가장 최근 표본으로부터의 순번 age에 대해
    ``0.5 ** (age / HALF_LIFE_SAMPLES)`` 가중치를 주고 Laplace 보정한다. 같은 가중·보정을
    전체 표본에 적용한 값을 기본 성공률(base rate)로 함께 돌려준다.
    유효한 전체 표본이 30개 미만이면 계산을 중단한다. 조건 구간 표본이 (가중 전) 20개
    미만이면 전체 과거 빈도로 폴백한다.
    """
    ordered = [bar for bar in bars if bar.trading_day < today]
    # 경계(고가 = 종가×1.005)가 부동소수 오차로 성공 처리되지 않도록 십진수로 비교한다.
    target_multiplier = 1 + Decimal(str(TARGET_RETURN_PCT)) / 100
    samples: list[tuple[date, float, float, int]] = []
    for previous, current, following in zip(ordered, ordered[1:], ordered[2:]):
        # Do not let a missing daily bar turn a multi-session move into a one-day
        # feature or label. This keeps both return and target aligned to joint sessions.
        if next_joint_trading_day(previous.trading_day) != current.trading_day:
            continue
        if next_joint_trading_day(current.trading_day) != following.trading_day:
            continue
        if previous.close <= 0 or current.close <= 0:
            continue
        change = (current.close / previous.close - 1) * 100
        # 수익률과 라벨을 같은 십진수 값에서 구해 경계에서 두 history 필드가 어긋나지 않게 한다.
        next_high, close = Decimal(str(following.high)), Decimal(str(current.close))
        next_high_return = (next_high / close - 1) * 100
        samples.append((current.trading_day, change, float(next_high_return),
                        int(next_high > close * target_multiplier)))
    if len(samples) < 30:
        raise RuntimeError("INSUFFICIENT_HISTORY")
    newest_index = len(samples) - 1
    weights = [0.5 ** ((newest_index - index) / HALF_LIFE_SAMPLES) for index in range(len(samples))]
    # 절대 등락률의 20% 분위수를 공통 경계로 사용해 방향별 대칭 구간을 만든다.
    magnitudes = sorted(abs(rate) for _, rate, _, _ in samples)
    threshold = magnitudes[min(len(magnitudes) - 1, int(len(magnitudes) * .2))]

    def classify(rate: float) -> str:
        return "down" if rate < -threshold else "up" if rate > threshold else "flat"

    band = classify(today_change_pct)
    selected = [(weights[index], label) for index, (_, rate, _, label) in enumerate(samples) if classify(rate) == band]
    if len(selected) < 20:
        selected = [(weights[index], label) for index, (_, _, _, label) in enumerate(samples)]
        band = "base_rate_fallback"
    probability, weight_sum, success_weight = _weighted_laplace(selected)
    base_rate, base_weight_sum, base_success_weight = _weighted_laplace(
        [(weights[index], label) for index, (_, _, _, label) in enumerate(samples)])
    history_snapshot = [{"trading_day": sample_day.isoformat(), "close_change_pct": rate,
                         "next_high_return_pct": next_high_return, "target_hit": label}
                        for sample_day, rate, next_high_return, label in samples]
    diagnostics = {
        "sample_count": len(selected), "success_count": sum(label for _, label in selected),
        "weight_sum": weight_sum, "success_weight": success_weight,
        "base_rate": base_rate, "base_sample_count": len(samples),
        "base_weight_sum": base_weight_sum, "base_success_weight": base_success_weight,
        "condition": band, "smoothing": "weighted_laplace_1_1",
        "target_return_pct": TARGET_RETURN_PCT, "half_life_samples": HALF_LIFE_SAMPLES,
    }
    return ProbabilityEstimate(probability, base_rate, diagnostics, history_snapshot)


def build_payload(trading_day: date, target_day: date, slot: time, index_changes: dict[str, float], history_provider: LsIndexHistoryProvider) -> dict[str, Any]:
    probabilities = {}
    diagnostics = {}
    histories = {}
    for market, prefix in (("KOSPI", "kospi"), ("KOSDAQ", "kosdaq")):
        estimate = empirical_probability(history_provider.fetch(market), index_changes[market], trading_day)
        probabilities[f"{prefix}_probability"] = estimate.probability
        probabilities[f"{prefix}_base_rate"] = estimate.base_rate
        diagnostics[market] = estimate.diagnostics
        histories[market] = estimate.history
    now = datetime.now(timezone.utc).isoformat()
    return {
        "trading_day": trading_day.isoformat(), "target_trading_day": target_day.isoformat(),
        "slot": slot.strftime("%H:%M:%S"), **probabilities, "last_success_at": now, "feature_as_of": now,
        "model_version": MODEL_VERSION, "validation_status": "experimental",
        "input_quality": {"history": "sufficient", "intraday_quote_timestamp": "collection_time_only",
                          "feature_alignment": "intraday_quote_vs_daily_close_proxy_unvalidated"},
        "feature_snapshot": {"index_change_pct": index_changes, "diagnostics": diagnostics, "history": histories},
    }


class ProbabilityRepository(Protocol):
    def save(self, payload: dict[str, Any]) -> None: ...


class SupabaseProbabilityRepository:
    def __init__(self, rpc_client: Any) -> None:
        self._rpc = rpc_client

    def save(self, payload: dict[str, Any]) -> None:
        result = self._rpc.rpc("upsert_market_index_probability", {"p_payload": payload})
        if result.get("error"):
            raise RuntimeError(f"PROBABILITY_SAVE_FAILED: {result['error'].get('code', 'unknown')}")


def next_joint_trading_day(day: date) -> date:
    from domain.calendar import KRX_HOLIDAYS
    candidate = day + timedelta(days=1)
    while candidate.weekday() >= 5 or candidate in KRX_HOLIDAYS:
        candidate += timedelta(days=1)
    return candidate

