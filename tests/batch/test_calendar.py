from datetime import date, time

from apps.batch.calendar import resolve_and_cache, resolve_for_schedule
from domain.calendar import CalendarStatus, TradingCalendarEntry


class FakeProvider:
    def __init__(self, value=None, error=None):
        self.value = value
        self.error = error
        self.calls = 0

    def has_daily_bar(self, trading_day):
        self.calls += 1
        if self.error:
            raise self.error
        return self.value


class FakeRepository:
    def __init__(self, cached=None):
        self.saved = []
        self._cached = cached or {}

    def upsert(self, decision):
        self.saved.append(decision)
        if decision.entry is not None:
            self._cached[decision.entry.trading_day] = decision.entry

    def get(self, trading_day):
        return self._cached.get(trading_day)


def test_weekday_is_open_and_weekend_is_closed_regardless_of_provider():
    repo = FakeRepository()
    # 2026-09-01 is a Tuesday, 2026-10-03 is a Saturday.
    assert resolve_and_cache(date(2026, 9, 1), FakeProvider(False), repo).status is CalendarStatus.OPEN
    assert resolve_and_cache(date(2026, 10, 3), FakeProvider(True), repo).status is CalendarStatus.CLOSED
    assert len(repo.saved) == 2


def test_resolve_and_cache_never_calls_the_daily_bar_provider():
    repo = FakeRepository()
    provider = FakeProvider(error=TimeoutError("should not be called"))
    result = resolve_and_cache(date(2026, 9, 1), provider, repo)
    assert result.status is CalendarStatus.OPEN
    assert provider.calls == 0


def test_resolve_for_schedule_cache_hit_never_calls_provider():
    cached_open = TradingCalendarEntry(date(2026, 9, 1), True, time(9), time(15, 30))
    repo = FakeRepository(cached={date(2026, 9, 1): cached_open})
    provider = FakeProvider(True)
    result = resolve_for_schedule(date(2026, 9, 1), provider, repo)
    assert result.status is CalendarStatus.OPEN
    assert result.entry == cached_open
    assert provider.calls == 0
    assert repo.saved == []


def test_resolve_for_schedule_cache_hit_closed_never_calls_provider():
    cached_closed = TradingCalendarEntry(date(2026, 10, 3), False)
    repo = FakeRepository(cached={date(2026, 10, 3): cached_closed})
    provider = FakeProvider(True)
    result = resolve_for_schedule(date(2026, 10, 3), provider, repo)
    assert result.status is CalendarStatus.CLOSED
    assert provider.calls == 0


def test_resolve_for_schedule_cache_miss_decides_from_weekday_and_caches():
    repo = FakeRepository()
    provider = FakeProvider(True)
    result = resolve_for_schedule(date(2026, 9, 1), provider, repo)
    assert result.status is CalendarStatus.OPEN
    assert provider.calls == 0
    assert len(repo.saved) == 1
    # 두 번째 호출은 이제 캐시를 사용해야 한다.
    second = resolve_for_schedule(date(2026, 9, 1), provider, repo)
    assert second.status is CalendarStatus.OPEN


class RaisingGetRepository(FakeRepository):
    def get(self, trading_day):
        raise TimeoutError("supabase network error")


def test_resolve_for_schedule_cache_read_failure_falls_through_to_weekday_decision():
    repo = RaisingGetRepository()
    provider = FakeProvider(True)
    result = resolve_for_schedule(date(2026, 9, 1), provider, repo)
    assert result.status is CalendarStatus.OPEN
    assert len(repo.saved) == 1
