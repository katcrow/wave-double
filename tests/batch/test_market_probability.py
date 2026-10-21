from datetime import date, timedelta

import pytest

from apps.batch.ls_client import LsResponse
from apps.batch.market_probability import (
    DailyIndexBar,
    LsIndexHistoryProvider,
    empirical_probability,
)


class FakeClient:
    def __init__(self, response: LsResponse) -> None:
        self.response = response

    def request(self, tr_code, params, *, path=None):
        return self.response


def _weekdays(count: int) -> list[date]:
    days: list[date] = []
    current = date(2024, 1, 2)
    while len(days) < count:
        if current.weekday() < 5:
            days.append(current)
        current += timedelta(days=1)
    return days


def _flat_bars(count: int = 34, breakout_at: int | None = None) -> list[DailyIndexBar]:
    days = _weekdays(count)
    return [
        DailyIndexBar(day, 101.0 if index == breakout_at else 100.0, 100.0)
        for index, day in enumerate(days)
    ]


def test_equal_next_high_is_a_failure_and_strictly_higher_is_a_success():
    bars = _flat_bars(breakout_at=3)

    probability, diagnostics, history = empirical_probability(
        bars, today_change_pct=0.0, today=bars[-1].trading_day + timedelta(days=1)
    )

    assert len(history) == 32
    assert history[0]["next_high_break"] == 0
    assert history[1]["next_high_break"] == 1
    assert diagnostics["success_count"] == 1
    assert probability == pytest.approx(2 / 34)


def test_missing_daily_bar_excludes_samples_that_span_multiple_sessions():
    days = _weekdays(36)
    bars = [
        DailyIndexBar(day, 100.0, 100.0)
        for index, day in enumerate(days)
        if index != 18
    ]

    _, diagnostics, history = empirical_probability(
        bars, today_change_pct=0.0, today=days[-1] + timedelta(days=1)
    )

    assert len(history) == 31
    assert diagnostics["sample_count"] == 31


def test_history_provider_fails_closed_on_a_malformed_bar():
    client = FakeClient(LsResponse(data={
        "t8429OutBlock1": [{"date": "2024-01-02", "close": "100"}],
    }))

    with pytest.raises(RuntimeError, match="malformed bar"):
        LsIndexHistoryProvider(client).fetch("KOSPI")
