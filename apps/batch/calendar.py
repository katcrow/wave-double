"""일봉 조회와 거래 캘린더 캐시의 애플리케이션 경계."""

from collections.abc import Callable
from datetime import date
from typing import Protocol

from domain.calendar import (
    CalendarDecision,
    CalendarStatus,
    TradingCalendarEntry,
    decide_from_daily_bar,
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
    """토/일요일과 KRX 휴장일 목록(``domain.calendar.KRX_HOLIDAYS``)으로 판정하고
    캘린더에 저장한다.

    LS 일봉 조회(``provider``)가 이른 시각 호출 시 당일 일봉 미반영을 휴장으로
    오판해 실제 개장일을 스킵시킨 사고(2026-09-15)가 있어 일봉 조회는 우회한다.
    ``provider``는 향후 복구를 위해 시그니처만 유지한다.
    """
    decision = decide_from_weekday(trading_day)
    if decision.entry is not None:
        repository.upsert(decision)
    return decision


def confirm_close_session(
    decision: CalendarDecision,
    provider: DailyBarProvider,
    repository: CalendarRepository,
) -> CalendarDecision:
    """close 배치 시점에 개장 판정을 실제 일봉으로 재확인한다.

    정적 휴장일 목록에 없는 임시휴장일은 요일 판정으로 개장 처리되지만, close 배치
    (19:30 이후)에는 개장일이라면 기준 종목 당일 일봉이 반드시 존재한다. 일봉이 없으면
    휴장으로 캘린더를 정정하고 CLOSED를 반환한다. 이른 시각 조회 오판(2026-09-15)은
    장 시작 전 호출에서만 생기므로 close 시점에는 해당하지 않는다. 조회 자체가 실패하면
    판정을 바꾸지 않는다(휴장 오판으로 정상 개장일을 건너뛰지 않기 위함).
    """
    if decision.status is not CalendarStatus.OPEN or decision.entry is None:
        return decision
    trading_day = decision.entry.trading_day
    try:
        has_bar = provider.has_daily_bar(trading_day)
    except Exception:
        return decision
    if has_bar:
        return decision
    closed = decide_from_daily_bar(trading_day, False)
    try:
        repository.upsert(closed)
    except Exception:
        pass
    return closed


def resolver_from_callable(
    lookup: Callable[[date], bool], repository: CalendarRepository
) -> Callable[[date], CalendarDecision]:
    """간단한 provider 함수용 adapter를 반환한다."""
    class _Provider:
        def has_daily_bar(self, trading_day: date) -> bool:
            return lookup(trading_day)

    return lambda trading_day: resolve_and_cache(trading_day, _Provider(), repository)
