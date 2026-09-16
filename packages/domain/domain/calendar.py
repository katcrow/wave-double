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
            TradingCalendarEntry(trading_day, True, time(8, 30), time(19, 30)),
        )
    return CalendarDecision(
        CalendarStatus.CLOSED,
        TradingCalendarEntry(trading_day, False),
    )


def unavailable_decision() -> CalendarDecision:
    return CalendarDecision(CalendarStatus.UNAVAILABLE)


def decide_from_weekday(trading_day: date) -> CalendarDecision:
    """토/일요일만 휴장으로 판정한다.

    LS 일봉 조회(``decide_from_daily_bar``)가 이른 시각 호출 시 당일 일봉이 아직
    반영되지 않아 개장일을 휴장으로 오판한 사례(2026-09-15)가 있어, 공휴일 캘린더가
    정비될 때까지 임시로 요일만으로 판정한다.
    """
    if trading_day.weekday() >= 5:
        return CalendarDecision(
            CalendarStatus.CLOSED,
            TradingCalendarEntry(trading_day, False),
        )
    return CalendarDecision(
        CalendarStatus.OPEN,
        TradingCalendarEntry(trading_day, True, time(8, 30), time(19, 30)),
    )


def floor_to_intraday_slot(
    moment: datetime, interval_minutes: int = 20, offset_minutes: int = 0
) -> datetime:
    """초/마이크로초를 버리고 분을 ``interval_minutes`` 단위(``offset_minutes``만큼
    어긋난, 예: interval=60/offset=30 -> 매시 30분)로 내림한 시각을 반환한다.

    스케줄러가 "지금이 몇 시 슬롯인가"를 판정하는 데만 쓰며, 세션 범위 나열은
    ``intraday_slots``의 몫으로 남긴다. ``offset_minutes > 0``일 때는 ``moment``가
    그날 자정 이후 최소 ``offset_minutes``분 지난 시각이어야 한다(장중 스케줄러
    호출만 상정하며, 자정 부근 롤오버는 다루지 않는다).
    """
    if interval_minutes <= 0:
        raise ValueError("interval_minutes must be positive")
    if not 0 <= offset_minutes < interval_minutes:
        raise ValueError("offset_minutes must be in [0, interval_minutes)")
    total_minutes = moment.hour * 60 + moment.minute
    floored_total = (
        (total_minutes - offset_minutes) // interval_minutes
    ) * interval_minutes + offset_minutes
    floored_hour, floored_minute = divmod(floored_total, 60)
    return moment.replace(hour=floored_hour, minute=floored_minute, second=0, microsecond=0)


def intraday_slots(
    entry: TradingCalendarEntry, interval_minutes: int = 20
) -> tuple[datetime, ...]:
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
