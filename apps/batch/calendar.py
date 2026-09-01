"""일봉 조회와 거래 캘린더 캐시의 애플리케이션 경계."""

from collections.abc import Callable
from datetime import date
from typing import Protocol

from domain.calendar import CalendarDecision, decide_from_daily_bar, unavailable_decision


class DailyBarProvider(Protocol):
    def has_daily_bar(self, trading_day: date) -> bool: ...


class CalendarRepository(Protocol):
    def upsert(self, decision: CalendarDecision) -> None: ...


def resolve_and_cache(
    trading_day: date,
    provider: DailyBarProvider,
    repository: CalendarRepository,
) -> CalendarDecision:
    """일봉 결과를 판정하고, 확정된 open/closed만 캘린더에 저장한다."""
    try:
        has_bar = provider.has_daily_bar(trading_day)
        if not isinstance(has_bar, bool):
            raise ValueError("daily bar provider must return bool")
        decision = decide_from_daily_bar(trading_day, has_bar)
    except Exception:
        decision = unavailable_decision()
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
