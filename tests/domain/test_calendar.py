from datetime import date, datetime, time

import pytest

from domain.calendar import (
    CalendarStatus,
    TradingCalendarEntry,
    decide_from_daily_bar,
    floor_to_half_hour,
    intraday_slots,
)


def test_daily_bar_means_open_and_caches_default_session():
    decision = decide_from_daily_bar(date(2026, 9, 1), True)
    assert decision.status is CalendarStatus.OPEN
    assert decision.entry == TradingCalendarEntry(date(2026, 9, 1), True, time(9), time(15, 30))


def test_missing_daily_bar_means_closed_without_session_times():
    decision = decide_from_daily_bar(date(2026, 10, 3), False)
    assert decision.status is CalendarStatus.CLOSED
    assert decision.entry and not decision.entry.is_open
    assert intraday_slots(decision.entry) == ()


def test_half_day_uses_stored_session_range():
    entry = TradingCalendarEntry(date(2026, 9, 1), True, time(9), time(12))
    slots = intraday_slots(entry)
    assert slots[0].time() == time(9)
    assert slots[-1].time() == time(11, 30)
    assert len(slots) == 6


def test_invalid_slot_interval_is_rejected():
    entry = TradingCalendarEntry(date(2026, 9, 1), True, time(9), time(15, 30))
    with pytest.raises(ValueError):
        intraday_slots(entry, 0)


def test_invalid_open_session_range_is_rejected():
    entry = TradingCalendarEntry(date(2026, 9, 1), True, time(15), time(9))
    with pytest.raises(ValueError, match="invalid session range"):
        intraday_slots(entry)


def test_floor_to_half_hour_snaps_down_to_the_boundary():
    assert floor_to_half_hour(datetime(2026, 9, 1, 9, 7, 33, 500)) == datetime(2026, 9, 1, 9, 0)
    assert floor_to_half_hour(datetime(2026, 9, 1, 9, 29, 59, 999999)) == datetime(2026, 9, 1, 9, 0)
    assert floor_to_half_hour(datetime(2026, 9, 1, 9, 30, 0)) == datetime(2026, 9, 1, 9, 30)
    assert floor_to_half_hour(datetime(2026, 9, 1, 9, 59, 59)) == datetime(2026, 9, 1, 9, 30)


def test_floor_to_half_hour_is_idempotent_at_exact_boundaries():
    assert floor_to_half_hour(datetime(2026, 9, 1, 0, 0)) == datetime(2026, 9, 1, 0, 0)
    assert floor_to_half_hour(datetime(2026, 9, 1, 23, 30)) == datetime(2026, 9, 1, 23, 30)
