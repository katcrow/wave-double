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


# KRX 휴장일(주말 제외). 연간 휴장일 공시가 나오면 갱신한다 -- 목록에 없는 평일은
# 개장일로 판정되므로, 다음 해 목록은 연말 전에 반드시 추가할 것.
KRX_HOLIDAYS: frozenset[date] = frozenset({
    # 2026
    date(2026, 1, 1),    # 신정
    date(2026, 2, 16),   # 설날 연휴
    date(2026, 2, 17),   # 설날
    date(2026, 2, 18),   # 설날 연휴
    date(2026, 3, 2),    # 삼일절 대체공휴일
    date(2026, 5, 1),    # 근로자의날
    date(2026, 5, 5),    # 어린이날
    date(2026, 5, 25),   # 부처님오신날 대체공휴일
    date(2026, 6, 3),    # 전국동시지방선거
    date(2026, 8, 17),   # 광복절 대체공휴일
    date(2026, 9, 24),   # 추석 연휴
    date(2026, 9, 25),   # 추석
    date(2026, 10, 5),   # 개천절 대체공휴일
    date(2026, 10, 9),   # 한글날
    date(2026, 12, 25),  # 성탄절
    date(2026, 12, 31),  # 연말 휴장
    # 2027
    date(2027, 1, 1),    # 신정
    date(2027, 2, 8),    # 설날 연휴
    date(2027, 2, 9),    # 설날 대체공휴일
    date(2027, 3, 1),    # 삼일절
    date(2027, 5, 5),    # 어린이날
    date(2027, 5, 13),   # 부처님오신날
    date(2027, 8, 16),   # 광복절 대체공휴일
    date(2027, 9, 14),   # 추석 연휴
    date(2027, 9, 15),   # 추석
    date(2027, 9, 16),   # 추석 연휴
    date(2027, 10, 4),   # 개천절 대체공휴일
    date(2027, 10, 11),  # 한글날 대체공휴일
    date(2027, 12, 27),  # 성탄절 대체공휴일
    date(2027, 12, 31),  # 연말 휴장
})


def decide_from_weekday(trading_day: date) -> CalendarDecision:
    """토/일요일과 ``KRX_HOLIDAYS``를 휴장으로 판정한다.

    LS 일봉 조회(``decide_from_daily_bar``)가 이른 시각 호출 시 당일 일봉이 아직
    반영되지 않아 개장일을 휴장으로 오판한 사례(2026-09-15)가 있어, 일봉 조회 대신
    요일과 정적 휴장일 목록으로 판정한다.
    """
    if trading_day.weekday() >= 5 or trading_day in KRX_HOLIDAYS:
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
