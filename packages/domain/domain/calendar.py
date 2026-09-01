"""KRX 거래 세션의 순수 규칙.

외부 캘린더/API와 저장소를 알지 않으며, 배치 계층이 이 모듈의 값을 캐시한다.
"""

from dataclasses import dataclass
from datetime import date, datetime, time, timedelta
from enum import StrEnum


class CalendarStatus(StrEnum):
    OPEN = "OPEN"
    CLOSED = "CLOSED"
    UNAVAILABLE = "CALENDAR_UNAVAILABLE"


@dataclass(frozen=True)
class TradingCalendarEntry:
    trading_day: date
    is_open: bool
    open_time: time | None = None
    close_time: time | None = None


@dataclass(frozen=True)
class CalendarDecision:
    status: CalendarStatus
    entry: TradingCalendarEntry | None = None


def decide_from_daily_bar(trading_day: date, has_daily_bar: bool) -> CalendarDecision:
    """일봉 응답 존재 여부를 캘린더 결과로 변환한다."""
    if has_daily_bar:
        return CalendarDecision(
            CalendarStatus.OPEN,
            TradingCalendarEntry(trading_day, True, time(9), time(15, 30)),
        )
    return CalendarDecision(
        CalendarStatus.CLOSED,
        TradingCalendarEntry(trading_day, False),
    )


def unavailable_decision() -> CalendarDecision:
    return CalendarDecision(CalendarStatus.UNAVAILABLE)


def intraday_slots(entry: TradingCalendarEntry, interval_minutes: int = 30) -> tuple[datetime, ...]:
    """세션 시작부터 종료 전까지의 KST 장중 슬롯을 반환한다."""
    if interval_minutes <= 0:
        raise ValueError("interval_minutes must be positive")
    if not entry.is_open:
        return ()
    if entry.open_time is None or entry.close_time is None:
        raise ValueError("open sessions require open_time and close_time")
    start = datetime.combine(entry.trading_day, entry.open_time)
    end = datetime.combine(entry.trading_day, entry.close_time)
    if start >= end:
        raise ValueError("invalid session range")
    slots: list[datetime] = []
    while start < end:
        slots.append(start)
        start += timedelta(minutes=interval_minutes)
    return tuple(slots)
