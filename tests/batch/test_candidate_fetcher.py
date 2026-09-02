import httpx
import pytest

from apps.batch.candidate_fetcher import CandidateFetcher, CandidateRow


def make_fetcher(handler):
    transport = httpx.MockTransport(handler)
    return CandidateFetcher(
        "https://example.supabase.co", "service-role-key", http_client=httpx.Client(transport=transport)
    )


def test_fetch_filters_by_attempt_run_id_and_returns_rows():
    def handler(request):
        assert request.url.params["attempt_run_id"] == "eq.run-1"
        assert request.url.params["select"] == "candidate_id,ticker,name"
        assert request.url.params["order"] == "trading_value.desc,ticker.asc"
        return httpx.Response(
            200,
            json=[{"candidate_id": "c1", "ticker": "005930", "name": "Samsung"}],
        )

    fetcher = make_fetcher(handler)
    rows = fetcher.fetch("run-1")
    assert rows == [CandidateRow("c1", "005930", "Samsung")]


def test_fetch_propagates_http_error_instead_of_swallowing():
    fetcher = make_fetcher(lambda request: httpx.Response(500, json={"message": "boom"}))
    with pytest.raises(httpx.HTTPStatusError):
        fetcher.fetch("run-1")


def test_fetch_raises_on_malformed_non_list_response():
    fetcher = make_fetcher(lambda request: httpx.Response(200, json={"unexpected": "shape"}))
    with pytest.raises(RuntimeError):
        fetcher.fetch("run-1")


def test_fetch_propagates_transport_error():
    def handler(request):
        raise httpx.ConnectError("connection refused", request=request)

    fetcher = make_fetcher(handler)
    with pytest.raises(httpx.ConnectError):
        fetcher.fetch("run-1")
