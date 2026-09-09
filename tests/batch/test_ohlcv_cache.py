from datetime import date

import httpx
import pytest

from apps.batch.ls_client import LsResponse
from apps.batch.ohlcv_cache import (
    CachedTickerState,
    IncrementalUpdateResult,
    LsOhlcvCacheProvider,
    OhlcvCacheResult,
    SupabaseOhlcvCacheRepository,
    initialize_new_ticker_history,
    update_existing_ticker_history,
)
from domain.ohlcv_cache import MIN_HISTORY_TRADING_DAYS, AdjustmentFlag, OhlcvCacheStatus


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


# --- LsOhlcvCacheProvider.fetch_range ---------------------------------------


def _range_row(day: str, close: float = 105, pricechk: int = 0) -> dict:
    return {
        "date": day,
        "open": 100,
        "high": 110,
        "low": 90,
        "close": close,
        "jdiff_vol": 1000,
        "pricechk": pricechk,
    }


def test_fetch_range_requests_qrycnt_500_with_start_and_end():
    response = LsResponse(data={"t8410OutBlock1": [_range_row("20260902")]})
    client = FakeClient(response)
    provider = LsOhlcvCacheProvider(client)
    rows = provider.fetch_range("005930", date(2026, 9, 2), date(2026, 9, 2))
    assert client.calls[0][0] == "t8410"
    in_block = client.calls[0][1]["t8410InBlock"]
    assert in_block == {
        "shcode": "005930",
        "gubun": "2",
        "qrycnt": 500,
        "sdate": "20260902",
        "edate": "20260902",
        "cts_date": "",
        "comp_yn": "N",
        "sujung": "Y",
    }
    assert rows == [
        {
            "trading_day": date(2026, 9, 2),
            "open": 100,
            "high": 110,
            "low": 90,
            "close": 105,
            "volume": 1000,
            "pricechk": 0,
        }
    ]


def test_fetch_range_with_none_start_sends_empty_sdate():
    response = LsResponse(data={"t8410OutBlock1": [_range_row("20260902")]})
    client = FakeClient(response)
    provider = LsOhlcvCacheProvider(client)
    provider.fetch_range("005930", None, date(2026, 9, 2))
    assert client.calls[0][1]["t8410InBlock"]["sdate"] == ""


def test_fetch_range_raises_on_failed_response():
    provider = LsOhlcvCacheProvider(FakeClient(LsResponse(result_code="HTTP_ERROR")))
    with pytest.raises(RuntimeError):
        provider.fetch_range("005930", date(2026, 9, 1), date(2026, 9, 2))


def test_fetch_full_history_row_has_no_pricechk_key():
    response = LsResponse(data={"t8410OutBlock1": [_bar_row("20260901")]})
    provider = LsOhlcvCacheProvider(FakeClient(response))
    rows = provider.fetch_full_history("005930", date(2026, 9, 2))
    assert "pricechk" not in rows[0]


# --- SupabaseOhlcvCacheRepository.latest_state ------------------------------


def test_latest_state_takes_first_row_per_ticker_after_desc_sort():
    def handler(request):
        assert request.url.params["ticker"] == "in.(005930,000660)"
        assert request.url.params["select"] == "ticker,trading_day,close,adjustment_version"
        assert request.url.params["order"] == "trading_day.desc"
        return httpx.Response(
            200,
            json=[
                {"ticker": "005930", "trading_day": "2026-09-02", "close": 105, "adjustment_version": 2},
                {"ticker": "005930", "trading_day": "2026-09-01", "close": 100, "adjustment_version": 2},
                {"ticker": "000660", "trading_day": "2026-09-01", "close": 50, "adjustment_version": 1},
            ],
        )

    repo = make_repo(handler)
    states = repo.latest_state(["005930", "000660"])
    assert states == {
        "005930": CachedTickerState(date(2026, 9, 2), 105, 2),
        "000660": CachedTickerState(date(2026, 9, 1), 50, 1),
    }


def test_latest_state_empty_input_short_circuits():
    repo = make_repo(lambda request: httpx.Response(200, json=[]))
    assert repo.latest_state([]) == {}


def test_latest_state_rejects_non_alnum_ticker_before_calling_supabase():
    calls = []

    def handler(request):
        calls.append(request)
        return httpx.Response(200, json=[])

    repo = make_repo(handler)
    with pytest.raises(ValueError):
        repo.latest_state(["005930", "abc),(select"])
    assert calls == []


def test_upsert_rows_accepts_adjustment_version_and_pricechk():
    seen = []

    def handler(request):
        seen.append(request)
        return httpx.Response(201, json={})

    repo = make_repo(handler)
    repo.upsert_rows(
        "005930",
        [
            {
                "trading_day": date(2026, 9, 1),
                "open": 1,
                "high": 2,
                "low": 0.5,
                "close": 1.5,
                "volume": 10,
                "pricechk": 1,
            }
        ],
        adjustment_version=3,
    )
    import json

    body = json.loads(seen[0].content)
    assert body[0]["adjustment_version"] == 3
    assert body[0]["pricechk"] == 1


# --- update_existing_ticker_history: I/O & Edge-Case Matrix -----------------


class FakeStateRepository:
    def __init__(self, states, upsert_failures=None, latest_state_error=None):
        self.states = states
        self.upsert_failures = upsert_failures or set()
        self.latest_state_error = latest_state_error
        self.upserted = []
        self.latest_state_calls = []

    def latest_state(self, tickers):
        self.latest_state_calls.append(list(tickers))
        if self.latest_state_error is not None:
            raise self.latest_state_error
        return self.states

    def upsert_rows(self, ticker, rows, *, adjustment_version=1):
        if ticker in self.upsert_failures:
            raise RuntimeError("supabase upsert failed")
        self.upserted.append((ticker, rows, adjustment_version))


class FakeRangeProvider:
    def __init__(self, by_ticker):
        self.by_ticker = by_ticker
        self.calls = []

    def fetch_range(self, ticker, start, end):
        self.calls.append((ticker, start, end))
        outcome = self.by_ticker[(ticker, start)]
        if isinstance(outcome, Exception):
            raise outcome
        return outcome


def test_ticker_already_at_cutoff_skips_ls_call():
    states = {"005930": CachedTickerState(date(2026, 9, 2), 100.0, 1)}
    repository = FakeStateRepository(states)
    provider = FakeRangeProvider({})
    result = update_existing_ticker_history(["005930"], provider, repository, date(2026, 9, 2))
    assert result.results["005930"] == OhlcvCacheResult("005930", OhlcvCacheStatus.READY, 0)
    assert provider.calls == []
    assert repository.upserted == []


def test_ticker_with_new_trading_day_fetches_only_incremental_range():
    states = {
        "005930": CachedTickerState(date(2026, 9, 1), 100.0, 1),
        "000660": CachedTickerState(date(2026, 9, 2), 50.0, 1),
    }
    repository = FakeStateRepository(states)
    provider = FakeRangeProvider(
        {("005930", date(2026, 9, 2)): [{"trading_day": date(2026, 9, 2), "close": 101, "pricechk": 0}]}
    )
    result = update_existing_ticker_history(["005930", "000660"], provider, repository, date(2026, 9, 2))
    assert provider.calls == [("005930", date(2026, 9, 2), date(2026, 9, 2))]
    assert result.results["005930"] == OhlcvCacheResult("005930", OhlcvCacheStatus.READY, 1)
    assert result.results["000660"] == OhlcvCacheResult("000660", OhlcvCacheStatus.READY, 0)
    assert repository.upserted == [
        ("005930", [{"trading_day": date(2026, 9, 2), "close": 101, "pricechk": 0}], 1)
    ]
    assert result.adjustment_flags == []


def test_corporate_action_detected_rebuilds_full_history_and_bumps_version():
    states = {
        "005930": CachedTickerState(date(2026, 9, 1), 100.0, 1),
        "000660": CachedTickerState(date(2026, 9, 1), 50.0, 1),
    }
    repository = FakeStateRepository(states)
    rebuilt = [
        {"trading_day": date(2026, 8, 1), "close": 50, "pricechk": 0},
        {"trading_day": date(2026, 9, 2), "close": 52, "pricechk": 1},
    ]
    provider = FakeRangeProvider(
        {
            ("005930", date(2026, 9, 2)): [{"trading_day": date(2026, 9, 2), "close": 52, "pricechk": 1}],
            ("005930", None): rebuilt,
            ("000660", date(2026, 9, 2)): [{"trading_day": date(2026, 9, 2), "close": 51, "pricechk": 0}],
        }
    )
    result = update_existing_ticker_history(["005930", "000660"], provider, repository, date(2026, 9, 2))
    assert result.results["005930"] == OhlcvCacheResult("005930", OhlcvCacheStatus.READY, len(rebuilt))
    assert result.results["000660"] == OhlcvCacheResult("000660", OhlcvCacheStatus.READY, 1)
    assert repository.upserted == [
        ("005930", rebuilt, 2),
        ("000660", [{"trading_day": date(2026, 9, 2), "close": 51, "pricechk": 0}], 1),
    ]


def test_partial_success_one_ticker_fails_others_continue():
    states = {
        "005930": CachedTickerState(date(2026, 9, 1), 100.0, 1),
        "000660": CachedTickerState(date(2026, 9, 1), 50.0, 1),
        "035420": CachedTickerState(date(2026, 9, 1), 200.0, 1),
    }
    repository = FakeStateRepository(states, upsert_failures={"035420"})
    provider = FakeRangeProvider(
        {
            ("005930", date(2026, 9, 2)): RuntimeError("LS failed"),
            ("000660", date(2026, 9, 2)): [{"trading_day": date(2026, 9, 2), "close": 51, "pricechk": 0}],
            ("035420", date(2026, 9, 2)): [{"trading_day": date(2026, 9, 2), "close": 201, "pricechk": 0}],
        }
    )
    result = update_existing_ticker_history(
        ["005930", "000660", "035420"], provider, repository, date(2026, 9, 2)
    )
    assert result.results["005930"].status == OhlcvCacheStatus.ERROR
    assert result.results["000660"].status == OhlcvCacheStatus.READY
    assert result.results["035420"].status == OhlcvCacheStatus.ERROR


def test_latest_state_total_failure_yields_error_for_all_candidates_without_ls_calls():
    repository = FakeStateRepository({}, latest_state_error=RuntimeError("supabase down"))
    provider = FakeRangeProvider({})
    result = update_existing_ticker_history(["005930", "000660"], provider, repository, date(2026, 9, 2))
    assert result.results["005930"].status == OhlcvCacheStatus.ERROR
    assert result.results["000660"].status == OhlcvCacheStatus.ERROR
    assert result.adjustment_flags == []
    assert provider.calls == []


def test_ticker_absent_from_latest_state_is_excluded_from_results():
    states = {"005930": CachedTickerState(date(2026, 9, 1), 100.0, 1)}
    repository = FakeStateRepository(states)
    provider = FakeRangeProvider(
        {("005930", date(2026, 9, 2)): [{"trading_day": date(2026, 9, 2), "close": 101, "pricechk": 0}]}
    )
    result = update_existing_ticker_history(["005930", "000660"], provider, repository, date(2026, 9, 2))
    assert "000660" not in result.results


def test_gap_over_30_percent_without_pricechk_flags_but_does_not_rebuild():
    states = {"005930": CachedTickerState(date(2026, 9, 1), 100.0, 1)}
    repository = FakeStateRepository(states)
    provider = FakeRangeProvider(
        {("005930", date(2026, 9, 2)): [{"trading_day": date(2026, 9, 2), "close": 135, "pricechk": 0}]}
    )
    result = update_existing_ticker_history(["005930"], provider, repository, date(2026, 9, 2))
    assert result.results["005930"] == OhlcvCacheResult("005930", OhlcvCacheStatus.READY, 1)
    assert result.adjustment_flags == [AdjustmentFlag("005930", date(2026, 9, 2), False, 0.35)]
    assert repository.upserted == [
        ("005930", [{"trading_day": date(2026, 9, 2), "close": 135, "pricechk": 0}], 1)
    ]


def test_upsert_failure_after_incremental_fetch_yields_error_for_that_ticker_only():
    states = {
        "005930": CachedTickerState(date(2026, 9, 1), 100.0, 1),
        "000660": CachedTickerState(date(2026, 9, 1), 50.0, 1),
    }
    repository = FakeStateRepository(states, upsert_failures={"005930"})
    provider = FakeRangeProvider(
        {
            ("005930", date(2026, 9, 2)): [{"trading_day": date(2026, 9, 2), "close": 101, "pricechk": 0}],
            ("000660", date(2026, 9, 2)): [{"trading_day": date(2026, 9, 2), "close": 51, "pricechk": 0}],
        }
    )
    result = update_existing_ticker_history(["005930", "000660"], provider, repository, date(2026, 9, 2))
    assert result.results["005930"].status == OhlcvCacheStatus.ERROR
    assert result.results["000660"].status == OhlcvCacheStatus.READY


def test_malformed_new_row_yields_error_for_that_ticker_only_and_continues():
    """close=None on a new row breaks the gap_pct arithmetic; must not abort the batch
    (documented partial-success guarantee: "한 종목의 실패가 나머지 종목 처리를 막지 않는다")."""
    states = {
        "005930": CachedTickerState(date(2026, 9, 1), 100.0, 1),
        "000660": CachedTickerState(date(2026, 9, 1), 50.0, 1),
    }
    repository = FakeStateRepository(states)
    provider = FakeRangeProvider(
        {
            ("005930", date(2026, 9, 2)): [{"trading_day": date(2026, 9, 2), "close": None, "pricechk": 0}],
            ("000660", date(2026, 9, 2)): [{"trading_day": date(2026, 9, 2), "close": 51, "pricechk": 0}],
        }
    )
    result = update_existing_ticker_history(["005930", "000660"], provider, repository, date(2026, 9, 2))
    assert result.results["005930"].status == OhlcvCacheStatus.ERROR
    assert result.results["000660"].status == OhlcvCacheStatus.READY
    assert repository.upserted == [
        ("000660", [{"trading_day": date(2026, 9, 2), "close": 51, "pricechk": 0}], 1)
    ]


def test_corporate_action_rebuild_fetch_failure_excludes_ticker_flags_and_others_unaffected():
    """pricechk fires (flag recorded in-loop) but the rebuild fetch_range(ticker, None, cutoff)
    raises: the ticker must be ERROR and its provisional flag must NOT leak into the returned
    adjustment_flags (nothing for that trading day was actually persisted)."""
    states = {
        "005930": CachedTickerState(date(2026, 9, 1), 100.0, 1),
        "000660": CachedTickerState(date(2026, 9, 1), 50.0, 1),
    }
    repository = FakeStateRepository(states)
    provider = FakeRangeProvider(
        {
            ("005930", date(2026, 9, 2)): [{"trading_day": date(2026, 9, 2), "close": 52, "pricechk": 1}],
            ("005930", None): RuntimeError("rebuild fetch failed"),
            ("000660", date(2026, 9, 2)): [{"trading_day": date(2026, 9, 2), "close": 51, "pricechk": 0}],
        }
    )
    result = update_existing_ticker_history(["005930", "000660"], provider, repository, date(2026, 9, 2))
    assert result.results["005930"].status == OhlcvCacheStatus.ERROR
    assert result.results["000660"].status == OhlcvCacheStatus.READY
    assert all(flag.ticker != "005930" for flag in result.adjustment_flags)
    assert repository.upserted == [
        ("000660", [{"trading_day": date(2026, 9, 2), "close": 51, "pricechk": 0}], 1)
    ]


def test_corporate_action_rebuild_upsert_failure_excludes_ticker_flags_and_others_unaffected():
    """pricechk fires, rebuild fetch succeeds, but the rebuild upsert_rows raises: the ticker
    must be ERROR and its provisional flag must NOT leak into adjustment_flags."""
    states = {
        "005930": CachedTickerState(date(2026, 9, 1), 100.0, 1),
        "000660": CachedTickerState(date(2026, 9, 1), 50.0, 1),
    }
    repository = FakeStateRepository(states, upsert_failures={"005930"})
    rebuilt = [{"trading_day": date(2026, 9, 2), "close": 52, "pricechk": 1}]
    provider = FakeRangeProvider(
        {
            ("005930", date(2026, 9, 2)): [{"trading_day": date(2026, 9, 2), "close": 52, "pricechk": 1}],
            ("005930", None): rebuilt,
            ("000660", date(2026, 9, 2)): [{"trading_day": date(2026, 9, 2), "close": 51, "pricechk": 0}],
        }
    )
    result = update_existing_ticker_history(["005930", "000660"], provider, repository, date(2026, 9, 2))
    assert result.results["005930"].status == OhlcvCacheStatus.ERROR
    assert result.results["000660"].status == OhlcvCacheStatus.READY
    assert all(flag.ticker != "005930" for flag in result.adjustment_flags)
    assert repository.upserted == [
        ("000660", [{"trading_day": date(2026, 9, 2), "close": 51, "pricechk": 0}], 1)
    ]


def test_corporate_action_success_includes_pricechk_flag_in_adjustment_flags():
    states = {"005930": CachedTickerState(date(2026, 9, 1), 100.0, 1)}
    repository = FakeStateRepository(states)
    rebuilt = [
        {"trading_day": date(2026, 8, 1), "close": 50, "pricechk": 0},
        {"trading_day": date(2026, 9, 2), "close": 52, "pricechk": 1},
    ]
    provider = FakeRangeProvider(
        {
            ("005930", date(2026, 9, 2)): [{"trading_day": date(2026, 9, 2), "close": 52, "pricechk": 1}],
            ("005930", None): rebuilt,
        }
    )
    result = update_existing_ticker_history(["005930"], provider, repository, date(2026, 9, 2))
    assert result.results["005930"].status == OhlcvCacheStatus.READY
    assert AdjustmentFlag("005930", date(2026, 9, 2), True, -0.48) in result.adjustment_flags


# --- epic-2-retro item-11: refresh 루프 heartbeat -----------------------------


class RecordingHeartbeat:
    def __init__(self):
        self.beats = 0

    def beat(self):
        self.beats += 1


def test_new_ticker_history_beats_per_new_ticker_when_heartbeat_given():
    provider = FakeProvider(
        {"005930": _rows(MIN_HISTORY_TRADING_DAYS), "000660": _rows(MIN_HISTORY_TRADING_DAYS)}
    )
    repository = FakeRepository(existing=set())
    hb = RecordingHeartbeat()
    initialize_new_ticker_history(["005930", "000660"], provider, repository, date(2026, 9, 2), heartbeat=hb)
    assert hb.beats == 2


def test_new_ticker_history_skips_heartbeat_for_already_cached_tickers():
    provider = FakeProvider({})
    repository = FakeRepository(existing={"005930"})
    hb = RecordingHeartbeat()
    initialize_new_ticker_history(["005930"], provider, repository, date(2026, 9, 2), heartbeat=hb)
    assert hb.beats == 0


def test_update_existing_history_beats_per_known_ticker_when_heartbeat_given():
    states = {
        "005930": CachedTickerState(date(2026, 8, 31), 100.0, 1),
        "000660": CachedTickerState(date(2026, 8, 31), 50.0, 1),
    }
    repository = FakeStateRepository(states)
    provider = FakeRangeProvider(
        {
            ("005930", date(2026, 9, 1)): [{"trading_day": date(2026, 9, 1), "close": 101, "pricechk": 0}],
            ("000660", date(2026, 9, 1)): [{"trading_day": date(2026, 9, 1), "close": 51, "pricechk": 0}],
        }
    )
    hb = RecordingHeartbeat()
    update_existing_ticker_history(["005930", "000660"], provider, repository, date(2026, 9, 2), heartbeat=hb)
    assert hb.beats == 2
