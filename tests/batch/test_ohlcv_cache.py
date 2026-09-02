from datetime import date

import httpx
import pytest

from apps.batch.ls_client import LsResponse
from apps.batch.ohlcv_cache import (
    LsOhlcvCacheProvider,
    OhlcvCacheResult,
    SupabaseOhlcvCacheRepository,
    initialize_new_ticker_history,
)
from domain.ohlcv_cache import MIN_HISTORY_TRADING_DAYS, OhlcvCacheStatus


class FakeClient:
    def __init__(self, response):
        self.response = response
        self.calls = []

    def request(self, tr_code, params):
        self.calls.append((tr_code, params))
        return self.response


def _bar_row(day: str) -> dict:
    return {
        "date": day,
        "open": 100,
        "high": 110,
        "low": 90,
        "close": 105,
        "jdiff_vol": 1000,
    }


def make_repo(handler):
    transport = httpx.MockTransport(handler)
    return SupabaseOhlcvCacheRepository(
        "https://example.supabase.co", "service-role-key", http_client=httpx.Client(transport=transport)
    )


# --- LsOhlcvCacheProvider ---------------------------------------------------


def test_fetch_full_history_requests_qrycnt_120_single_call():
    response = LsResponse(data={"t8410OutBlock1": [_bar_row("20260901")]})
    client = FakeClient(response)
    provider = LsOhlcvCacheProvider(client)
    rows = provider.fetch_full_history("005930", date(2026, 9, 2))
    assert client.calls[0][0] == "t8410"
    in_block = client.calls[0][1]["t8410InBlock"]
    assert in_block == {
        "shcode": "005930",
        "gubun": "2",
        "qrycnt": 120,
        "sdate": "",
        "edate": "20260902",
        "cts_date": "",
        "comp_yn": "N",
        "sujung": "Y",
    }
    assert rows == [
        {"trading_day": date(2026, 9, 1), "open": 100, "high": 110, "low": 90, "close": 105, "volume": 1000}
    ]


def test_fetch_full_history_raises_on_failed_response():
    provider = LsOhlcvCacheProvider(FakeClient(LsResponse(result_code="HTTP_ERROR")))
    with pytest.raises(RuntimeError):
        provider.fetch_full_history("005930", date(2026, 9, 2))


def test_fetch_full_history_error_message_includes_result_code_and_message():
    provider = LsOhlcvCacheProvider(
        FakeClient(LsResponse(result_code="HTTP_ERROR", message="upstream unavailable"))
    )
    with pytest.raises(RuntimeError, match="HTTP_ERROR"):
        provider.fetch_full_history("005930", date(2026, 9, 2))
    with pytest.raises(RuntimeError, match="upstream unavailable"):
        provider.fetch_full_history("005930", date(2026, 9, 2))


def test_fetch_full_history_raises_on_malformed_response():
    provider = LsOhlcvCacheProvider(FakeClient(LsResponse(data={"t8410OutBlock1": "not-a-list"})))
    with pytest.raises(RuntimeError):
        provider.fetch_full_history("005930", date(2026, 9, 2))


def test_fetch_full_history_raises_runtime_error_on_missing_date_field():
    row = _bar_row("20260901")
    del row["date"]
    provider = LsOhlcvCacheProvider(FakeClient(LsResponse(data={"t8410OutBlock1": [row]})))
    with pytest.raises(RuntimeError):
        provider.fetch_full_history("005930", date(2026, 9, 2))


def test_fetch_full_history_raises_runtime_error_on_malformed_date_field():
    row = _bar_row("2026-09-01")  # not the expected YYYYMMDD shape
    provider = LsOhlcvCacheProvider(FakeClient(LsResponse(data={"t8410OutBlock1": [row]})))
    with pytest.raises(RuntimeError):
        provider.fetch_full_history("005930", date(2026, 9, 2))


# --- SupabaseOhlcvCacheRepository ------------------------------------------


def test_existing_tickers_queries_in_filter():
    def handler(request):
        assert request.url.params["ticker"] == "in.(005930,000660)"
        assert request.url.params["select"] == "ticker"
        return httpx.Response(200, json=[{"ticker": "005930"}])

    repo = make_repo(handler)
    assert repo.existing_tickers(["005930", "000660"]) == {"005930"}


def test_existing_tickers_empty_input_short_circuits():
    repo = make_repo(lambda request: httpx.Response(200, json=[]))
    assert repo.existing_tickers([]) == set()


def test_existing_tickers_rejects_non_alnum_ticker_before_calling_supabase():
    calls = []

    def handler(request):
        calls.append(request)
        return httpx.Response(200, json=[])

    repo = make_repo(handler)
    with pytest.raises(ValueError):
        repo.existing_tickers(["005930", "abc),(select"])
    assert calls == []


def test_upsert_rows_sends_merge_duplicates_with_conflict_target():
    seen = []

    def handler(request):
        seen.append(request)
        return httpx.Response(201, json={})

    repo = make_repo(handler)
    repo.upsert_rows(
        "005930",
        [{"trading_day": date(2026, 9, 1), "open": 1, "high": 2, "low": 0.5, "close": 1.5, "volume": 10}],
    )
    request = seen[0]
    assert request.headers["prefer"] == "resolution=merge-duplicates"
    assert request.url.params["on_conflict"] == "ticker,trading_day"
    import json

    body = json.loads(request.content)
    assert body == [
        {
            "ticker": "005930",
            "trading_day": "2026-09-01",
            "open": 1,
            "high": 2,
            "low": 0.5,
            "close": 1.5,
            "volume": 10,
            "adjusted": True,
            "adjustment_version": 1,
            "pricechk": None,
        }
    ]


# --- initialize_new_ticker_history: I/O & Edge-Case Matrix ------------------


class FakeProvider:
    def __init__(self, by_ticker):
        self.by_ticker = by_ticker
        self.calls = []

    def fetch_full_history(self, ticker, cutoff):
        self.calls.append(ticker)
        outcome = self.by_ticker[ticker]
        if isinstance(outcome, Exception):
            raise outcome
        return outcome


class FakeRepository:
    def __init__(self, existing, upsert_failures=None):
        self.existing = existing
        self.upsert_failures = upsert_failures or set()
        self.upserted = {}
        self.existing_tickers_calls = []

    def existing_tickers(self, tickers):
        self.existing_tickers_calls.append(list(tickers))
        return self.existing

    def upsert_rows(self, ticker, rows):
        if ticker in self.upsert_failures:
            raise RuntimeError("supabase upsert failed")
        self.upserted[ticker] = rows


def _rows(n: int) -> list[dict]:
    return [
        {"trading_day": date(2026, 1, 1), "open": 1, "high": 1, "low": 1, "close": 1, "volume": 1}
        for _ in range(n)
    ]


def test_new_ticker_with_sufficient_history_is_ready_and_upserted():
    provider = FakeProvider({"005930": _rows(MIN_HISTORY_TRADING_DAYS)})
    repository = FakeRepository(existing=set())
    results = initialize_new_ticker_history(["005930"], provider, repository, date(2026, 9, 2))
    assert results["005930"] == OhlcvCacheResult("005930", OhlcvCacheStatus.READY, MIN_HISTORY_TRADING_DAYS)
    assert repository.upserted["005930"] == _rows(MIN_HISTORY_TRADING_DAYS)


def test_new_ticker_with_insufficient_history_is_ineligible_and_not_saved():
    provider = FakeProvider({"005930": _rows(MIN_HISTORY_TRADING_DAYS - 1)})
    repository = FakeRepository(existing=set())
    results = initialize_new_ticker_history(["005930"], provider, repository, date(2026, 9, 2))
    assert results["005930"].status == OhlcvCacheStatus.INELIGIBLE_INSUFFICIENT_HISTORY
    assert results["005930"].trading_days == MIN_HISTORY_TRADING_DAYS - 1
    assert repository.upserted == {}


def test_already_cached_ticker_is_skipped_without_ls_call():
    provider = FakeProvider({})
    repository = FakeRepository(existing={"005930"})
    results = initialize_new_ticker_history(["005930"], provider, repository, date(2026, 9, 2))
    assert results == {}
    assert provider.calls == []


def test_ls_failure_yields_error_status_without_saving():
    provider = FakeProvider({"005930": RuntimeError("LS daily bar history fetch failed: HTTP_ERROR")})
    repository = FakeRepository(existing=set())
    results = initialize_new_ticker_history(["005930"], provider, repository, date(2026, 9, 2))
    assert results["005930"].status == OhlcvCacheStatus.ERROR
    assert repository.upserted == {}


def test_supabase_upsert_failure_yields_error_status_for_that_ticker_only():
    provider = FakeProvider(
        {"005930": _rows(MIN_HISTORY_TRADING_DAYS), "000660": _rows(MIN_HISTORY_TRADING_DAYS)}
    )
    repository = FakeRepository(existing=set(), upsert_failures={"005930"})
    results = initialize_new_ticker_history(["005930", "000660"], provider, repository, date(2026, 9, 2))
    assert results["005930"].status == OhlcvCacheStatus.ERROR
    assert results["000660"].status == OhlcvCacheStatus.READY
    assert "005930" not in repository.upserted
    assert "000660" in repository.upserted


def test_existing_tickers_failure_yields_error_for_every_candidate_without_ls_calls():
    class FailingRepository(FakeRepository):
        def existing_tickers(self, tickers):
            self.existing_tickers_calls.append(list(tickers))
            raise RuntimeError("supabase existing_tickers failed")

    provider = FakeProvider({})
    repository = FailingRepository(existing=set())
    results = initialize_new_ticker_history(
        ["005930", "000660"], provider, repository, date(2026, 9, 2)
    )
    assert results["005930"].status == OhlcvCacheStatus.ERROR
    assert results["000660"].status == OhlcvCacheStatus.ERROR
    assert provider.calls == []


def test_duplicate_candidates_are_deduplicated_preserving_order():
    provider = FakeProvider({"005930": _rows(MIN_HISTORY_TRADING_DAYS)})
    repository = FakeRepository(existing=set())
    results = initialize_new_ticker_history(
        ["005930", "005930"], provider, repository, date(2026, 9, 2)
    )
    assert provider.calls == ["005930"]
    assert results.keys() == {"005930"}
    assert repository.existing_tickers_calls == [["005930"]]


def test_multiple_new_tickers_are_processed_sequentially_and_partial_success_allowed():
    provider = FakeProvider(
        {
            "005930": _rows(MIN_HISTORY_TRADING_DAYS),
            "000660": RuntimeError("boom"),
            "035420": _rows(10),
        }
    )
    repository = FakeRepository(existing={"999999"})
    results = initialize_new_ticker_history(
        ["005930", "000660", "035420", "999999"], provider, repository, date(2026, 9, 2)
    )
    assert provider.calls == ["005930", "000660", "035420"]
    assert results["005930"].status == OhlcvCacheStatus.READY
    assert results["000660"].status == OhlcvCacheStatus.ERROR
    assert results["035420"].status == OhlcvCacheStatus.INELIGIBLE_INSUFFICIENT_HISTORY
    assert "999999" not in results
