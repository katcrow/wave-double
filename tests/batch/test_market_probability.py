from datetime import date, time, timedelta

import pytest

from apps.batch.ls_client import LsResponse
from apps.batch.ls_client import DEFAULT_PATH_BY_TR
from apps.batch.market_probability import (
    HALF_LIFE_SAMPLES,
    DailyIndexBar,
    LsIndexHistoryProvider,
    build_payload,
    empirical_probability,
    next_joint_trading_day,
)
from domain.calendar import KRX_HOLIDAYS


class FakeClient:
    def __init__(self, response: LsResponse) -> None:
        self.response = response
        self.calls = []

    def request(self, tr_code, params, *, path=None):
        self.calls.append((tr_code, params, path))
        return self.response


def _weekdays(count: int) -> list[date]:
    days: list[date] = []
    current = date(2024, 1, 2)
    while len(days) < count:
        if current.weekday() < 5 and current not in KRX_HOLIDAYS:
            days.append(current)
        current += timedelta(days=1)
    return days


def _flat_bars(count: int = 34, highs: dict[int, float] | None = None) -> list[DailyIndexBar]:
    days = _weekdays(count)
    return [
        DailyIndexBar(day, (highs or {}).get(index, 100.0), 100.0)
        for index, day in enumerate(days)
    ]


def _after(bars: list[DailyIndexBar]) -> date:
    return bars[-1].trading_day + timedelta(days=1)


def test_next_high_exactly_at_target_is_a_failure_and_above_is_a_success():
    # 표본 i의 라벨은 bars[i + 2]의 고가로 정해진다(종가 100, 목표 100.5).
    bars = _flat_bars(highs={2: 100.5, 3: 100.51})

    estimate = empirical_probability(bars, today_change_pct=0.0, today=_after(bars))

    assert len(estimate.history) == 32
    assert estimate.history[0]["target_hit"] == 0
    assert estimate.history[0]["next_high_return_pct"] == 0.5
    assert estimate.history[1]["next_high_return_pct"] > 0.5
    assert estimate.history[1]["target_hit"] == 1
    assert estimate.diagnostics["success_count"] == 1
    assert estimate.diagnostics["target_return_pct"] == 0.5
    assert estimate.diagnostics["half_life_samples"] == HALF_LIFE_SAMPLES


def test_recent_successes_weigh_more_than_unweighted_rate():
    count = 34
    # 마지막 10개 표본만 목표를 넘는다(표본 i의 라벨은 bars[i + 2]).
    bars = _flat_bars(count, highs={index: 101.0 for index in range(count - 10, count)})

    estimate = empirical_probability(bars, today_change_pct=0.0, today=_after(bars))

    samples = len(estimate.history)
    unweighted = (10 + 1) / (samples + 2)
    weights = [0.5 ** ((samples - 1 - index) / HALF_LIFE_SAMPLES) for index in range(samples)]
    expected = (sum(weights[-10:]) + 1) / (sum(weights) + 2)
    assert estimate.probability > unweighted
    assert estimate.probability == pytest.approx(expected)
    assert estimate.diagnostics["weight_sum"] == pytest.approx(sum(weights))
    assert estimate.diagnostics["success_weight"] == pytest.approx(sum(weights[-10:]))


def _alternating_bars(count: int = 120) -> list[DailyIndexBar]:
    """종가가 100→101→100(보합·상승·하락)을 반복하고, 상승일 다음날만 고가가 목표를 넘는 일봉."""
    days = _weekdays(count)
    closes = [101.0 if index % 3 == 1 else 100.0 for index in range(count)]
    bars = []
    for index, day in enumerate(days):
        rose_yesterday = index >= 2 and closes[index - 1] > closes[index - 2]
        high = closes[index - 1] * 1.01 if rose_yesterday else closes[index]
        bars.append(DailyIndexBar(day, max(high, closes[index]), closes[index]))
    return bars


def test_base_rate_uses_all_samples_with_the_same_weighting():
    bars = _alternating_bars()

    up = empirical_probability(bars, today_change_pct=5.0, today=_after(bars))
    down = empirical_probability(bars, today_change_pct=-5.0, today=_after(bars))

    assert up.diagnostics["condition"] == "up"
    assert down.diagnostics["condition"] == "down"
    assert up.base_rate == pytest.approx(down.base_rate)
    assert 0 < down.probability < up.base_rate < up.probability < 1
    assert up.diagnostics["base_rate"] == up.base_rate
    assert up.diagnostics["base_sample_count"] == len(up.history)


class FakeHistoryProvider:
    def __init__(self, bars: list[DailyIndexBar]) -> None:
        self.bars = bars

    def fetch(self, market: str, count: int = 500) -> list[DailyIndexBar]:
        return self.bars


def test_payload_carries_base_rates_and_v2_model_version():
    bars = _alternating_bars()
    trading_day = _after(bars)

    payload = build_payload(trading_day, trading_day + timedelta(days=1), time(15, 20),
                            {"KOSPI": 5.0, "KOSDAQ": -5.0}, FakeHistoryProvider(bars))

    assert payload["model_version"] == "historical_conditional_rate_v2"
    for prefix in ("kospi", "kosdaq"):
        assert 0 <= payload[f"{prefix}_base_rate"] <= 1
        assert 0 <= payload[f"{prefix}_probability"] <= 1
    assert payload["kospi_base_rate"] == pytest.approx(payload["kosdaq_base_rate"])
    diagnostics = payload["feature_snapshot"]["diagnostics"]["KOSPI"]
    for key in ("sample_count", "weight_sum", "success_weight", "base_rate", "target_return_pct", "half_life_samples"):
        assert key in diagnostics
    history = payload["feature_snapshot"]["history"]["KOSPI"][0]
    assert set(history) == {"trading_day", "close_change_pct", "next_high_return_pct", "target_hit"}


def test_next_joint_trading_day_skips_2025_chuseok_holidays():
    assert next_joint_trading_day(date(2025, 10, 2)) == date(2025, 10, 10)


def test_missing_daily_bar_excludes_samples_that_span_multiple_sessions():
    days = _weekdays(36)
    bars = [
        DailyIndexBar(day, 100.0, 100.0)
        for index, day in enumerate(days)
        if index != 18
    ]

    estimate = empirical_probability(
        bars, today_change_pct=0.0, today=days[-1] + timedelta(days=1)
    )

    assert len(estimate.history) == 31
    assert estimate.diagnostics["sample_count"] == 31


def test_history_provider_fails_closed_on_a_malformed_bar():
    client = FakeClient(LsResponse(data={
        "t8429OutBlock1": [{"date": "2024-01-02", "close": "100"}],
    }))

    with pytest.raises(RuntimeError, match="malformed bar"):
        LsIndexHistoryProvider(client).fetch("KOSPI")


def test_history_provider_routes_t8429_to_sector_chart_endpoint():
    client = FakeClient(LsResponse(data={
        "t8429OutBlock1": [{"date": "2024-01-02", "high": "101", "close": "100"}],
    }))

    bars = LsIndexHistoryProvider(client).fetch("KOSPI")

    assert len(bars) == 1
    assert client.calls[0][0] == "t8429"
    assert client.calls[0][1]["t8429InBlock"]["shcode"] == "001"
    assert client.calls[0][2] is None
    assert DEFAULT_PATH_BY_TR["t8429"] == "/indtp/chart"
