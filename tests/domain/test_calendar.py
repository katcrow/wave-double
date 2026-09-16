from datetime import date, datetime, time

import pytest

from domain.calendar import (
    CalendarStatus,
    TradingCalendarEntry,
    decide_from_daily_bar,
    decide_from_weekday,
    floor_to_intraday_slot,
    intraday_slots,
)


def test_daily_bar_means_open_and_caches_default_session():
    decision = decide_from_daily_bar(date(2026, 9, 1), True)
    assert decision.status is CalendarStatus.OPEN
    assert decision.entry == TradingCalendarEntry(
        date(2026, 9, 1), True, time(8, 30), time(19, 30)
    )


def test_missing_daily_bar_means_closed_without_session_times():
    decision = decide_from_daily_bar(date(2026, 10, 3), False)
    assert decision.status is CalendarStatus.CLOSED
    assert decision.entry and not decision.entry.is_open
    assert intraday_slots(decision.entry) == ()


def test_decide_from_weekday_marks_weekdays_open():
    # 2026-09-14 is a Monday, 2026-09-18 is a Friday.
    for weekday in (date(2026, 9, 14), date(2026, 9, 15), date(2026, 9, 18)):
        decision = decide_from_weekday(weekday)
        assert decision.status is CalendarStatus.OPEN
        assert decision.entry == TradingCalendarEntry(
            weekday, True, time(8, 30), time(19, 30)
        )


def test_decide_from_weekday_marks_weekend_closed():
    # 2026-09-19 is a Saturday, 2026-09-20 is a Sunday.
    for weekend_day in (date(2026, 9, 19), date(2026, 9, 20)):
        decision = decide_from_weekday(weekend_day)
        assert decision.status is CalendarStatus.CLOSED
        assert decision.entry and not decision.entry.is_open


def test_half_day_uses_stored_session_range():
    entry = TradingCalendarEntry(date(2026, 9, 1), True, time(9), time(12))
    slots = intraday_slots(entry)
    assert slots[0].time() == time(9)
    assert slots[-1].time() == time(11, 40)
    assert len(slots) == 9


def test_invalid_slot_interval_is_rejected():
    entry = TradingCalendarEntry(date(2026, 9, 1), True, time(8), time(20))
    with pytest.raises(ValueError):
        intraday_slots(entry, 0)


def test_invalid_open_session_range_is_rejected():
    entry = TradingCalendarEntry(date(2026, 9, 1), True, time(15), time(9))
    with pytest.raises(ValueError, match="invalid session range"):
        intraday_slots(entry)


def test_floor_to_intraday_slot_snaps_down_to_the_boundary():
    assert floor_to_intraday_slot(datetime(2026, 9, 1, 9, 7, 33, 500)) == datetime(2026, 9, 1, 9, 0)
    assert floor_to_intraday_slot(datetime(2026, 9, 1, 9, 19, 59, 999999)) == datetime(2026, 9, 1, 9, 0)
    assert floor_to_intraday_slot(datetime(2026, 9, 1, 9, 20, 0)) == datetime(2026, 9, 1, 9, 20)
    assert floor_to_intraday_slot(datetime(2026, 9, 1, 9, 39, 59)) == datetime(2026, 9, 1, 9, 20)
    assert floor_to_intraday_slot(datetime(2026, 9, 1, 9, 40, 0)) == datetime(2026, 9, 1, 9, 40)
    assert floor_to_intraday_slot(datetime(2026, 9, 1, 9, 59, 59)) == datetime(2026, 9, 1, 9, 40)


def test_floor_to_intraday_slot_is_idempotent_at_exact_boundaries():
    assert floor_to_intraday_slot(datetime(2026, 9, 1, 0, 0)) == datetime(2026, 9, 1, 0, 0)
    assert floor_to_intraday_slot(datetime(2026, 9, 1, 23, 40)) == datetime(2026, 9, 1, 23, 40)


def test_floor_to_intraday_slot_supports_a_custom_interval():
    assert floor_to_intraday_slot(datetime(2026, 9, 1, 9, 29), interval_minutes=30) == datetime(2026, 9, 1, 9, 0)
    with pytest.raises(ValueError):
        floor_to_intraday_slot(datetime(2026, 9, 1, 9, 0), interval_minutes=0)


def test_floor_to_intraday_slot_supports_an_offset():
    """08:30 시작 60분 간격(매시 30분) 스케줄(Neo 확인, 2026-09-16)을 지원한다."""
    assert floor_to_intraday_slot(
        datetime(2026, 9, 1, 9, 29), interval_minutes=60, offset_minutes=30
    ) == datetime(2026, 9, 1, 8, 30)
    assert floor_to_intraday_slot(
        datetime(2026, 9, 1, 9, 30), interval_minutes=60, offset_minutes=30
    ) == datetime(2026, 9, 1, 9, 30)
    assert floor_to_intraday_slot(
        datetime(2026, 9, 1, 10, 29, 59), interval_minutes=60, offset_minutes=30
    ) == datetime(2026, 9, 1, 9, 30)
    with pytest.raises(ValueError):
        floor_to_intraday_slot(datetime(2026, 9, 1, 9, 0), interval_minutes=60, offset_minutes=60)
    with pytest.raises(ValueError):
        floor_to_intraday_slot(datetime(2026, 9, 1, 9, 0), interval_minutes=60, offset_minutes=-1)
