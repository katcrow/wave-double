from datetime import date

from apps.batch.calendar import resolve_and_cache
from domain.calendar import CalendarStatus


class FakeProvider:
    def __init__(self, value=None, error=None):
        self.value = value
        self.error = error

    def has_daily_bar(self, trading_day):
        if self.error:
            raise self.error
        return self.value


class FakeRepository:
    def __init__(self):
        self.saved = []

    def upsert(self, decision):
        self.saved.append(decision)


def test_open_and_closed_results_are_cached():
    repo = FakeRepository()
    assert resolve_and_cache(date(2026, 9, 1), FakeProvider(True), repo).status is CalendarStatus.OPEN
    assert resolve_and_cache(date(2026, 10, 3), FakeProvider(False), repo).status is CalendarStatus.CLOSED
    assert len(repo.saved) == 2


def test_lookup_failure_is_unavailable_and_not_cached_as_closed():
    repo = FakeRepository()
    result = resolve_and_cache(date(2026, 9, 1), FakeProvider(error=TimeoutError()), repo)
    assert result.status is CalendarStatus.UNAVAILABLE
    assert repo.saved == []


def test_malformed_lookup_result_is_unavailable():
    repo = FakeRepository()
    result = resolve_and_cache(date(2026, 9, 1), FakeProvider(value=None), repo)
    assert result.status is CalendarStatus.UNAVAILABLE
    assert repo.saved == []
