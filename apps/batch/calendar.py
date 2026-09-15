"""일봉 조회와 거래 캘린더 캐시의 애플리케이션 경계."""

from collections.abc import Callable
from datetime import date
from typing import Protocol

from domain.calendar import (
    CalendarDecision,
    CalendarStatus,
    TradingCalendarEntry,
    decide_from_weekday,
)


class DailyBarProvider(Protocol):
    def has_daily_bar(self, trading_day: date) -> bool: ...


class CalendarRepository(Protocol):
    def upsert(self, decision: CalendarDecision) -> None: ...
    def get(self, trading_day: date) -> TradingCalendarEntry | None: ...
    def recent_open_days(self, cutoff: date, count: int) -> list[date]: ...


def resolve_for_schedule(
    trading_day: date,
    provider: DailyBarProvider,
    repository: CalendarRepository,
) -> CalendarDecision:
    """캐시를 먼저 조회하고, 캐시 미스일 때만 ``resolve_and_cache``(provider 1콜)를 호출한다."""
    try:
        cached = repository.get(trading_day)
    except Exception:
        cached = None
    if cached is not None:
        status = CalendarStatus.OPEN if cached.is_open else CalendarStatus.CLOSED
        return CalendarDecision(status, cached)
    return resolve_and_cache(trading_day, provider, repository)


def resolve_and_cache(
    trading_day: date,
    provider: DailyBarProvider,
    repository: CalendarRepository,
) -> CalendarDecision:
    """토/일요일만 휴장으로 판정하고 캘린더에 저장한다.

    임시 조치(2026-09-15): LS 일봉 조회(``provider``)가 이른 시각 호출 시 당일 일봉
    미반영을 휴장으로 오판해 실제 개장일을 스킵시킨 사고가 있어, 공휴일 캘린더가
    정비될 때까지 일봉 조회를 우회하고 요일만으로 판정한다. ``provider``는 향후
    복구를 위해 시그니처만 유지한다.
    """
    decision = decide_from_weekday(trading_day)
    if decision.entry is not None:
        repository.upsert(decision)
    return decision


def resolver_from_callable(
    lookup: Callable[[date], bool], repository: CalendarRepository
) -> Callable[[date], CalendarDecision]:
    """간단한 provider 함수용 adapter를 반환한다."""
    class _Provider:
        def has_daily_bar(self, trading_day: date) -> bool:
            return lookup(trading_day)

    return lambda trading_day: resolve_and_cache(trading_day, _Provider(), repository)
