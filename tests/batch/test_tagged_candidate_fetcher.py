import httpx
import pytest

from apps.batch.tagged_candidate_fetcher import TaggedCandidateFetcher, TaggedCandidateRow


def make_fetcher(handler):
    transport = httpx.MockTransport(handler)
    return TaggedCandidateFetcher(
        "https://example.supabase.co", "service-role-key", http_client=httpx.Client(transport=transport)
    )


def test_fetch_queries_active_tags_then_candidates_with_expected_params():
    seen = []

    def handler(request):
        seen.append(request)
        if request.url.path == "/rest/v1/candidate_tags":
            assert request.url.params["attempt_run_id"] == "eq.run-1"
            assert request.url.params["status"] == "eq.active"
            assert request.url.params["select"] == "candidate_id"
            return httpx.Response(200, json=[{"candidate_id": "c1"}, {"candidate_id": "c2"}])
        assert request.url.path == "/rest/v1/candidates"
        assert request.url.params["candidate_id"] == "in.(c1,c2)"
        assert request.url.params["attempt_run_id"] == "eq.run-1"
        assert request.url.params["select"] == "candidate_id,ticker"
        return httpx.Response(
            200,
            json=[{"candidate_id": "c1", "ticker": "005930"}, {"candidate_id": "c2", "ticker": "000660"}],
        )

    fetcher = make_fetcher(handler)
    rows = fetcher.fetch("run-1")

    assert len(seen) == 2
    assert rows == [
        TaggedCandidateRow("c1", "005930"),
        TaggedCandidateRow("c2", "000660"),
    ]


def test_fetch_deduplicates_candidate_ids_across_multiple_active_tags():
    seen_candidates_params = {}

    def handler(request):
        if request.url.path == "/rest/v1/candidate_tags":
            # 같은 candidate_id가 A/B 두 전략으로 태깅되어 두 행으로 돌아온다.
            return httpx.Response(200, json=[{"candidate_id": "c1"}, {"candidate_id": "c1"}])
        seen_candidates_params.update(request.url.params)
        return httpx.Response(200, json=[{"candidate_id": "c1", "ticker": "005930"}])

    fetcher = make_fetcher(handler)
    rows = fetcher.fetch("run-1")

    assert seen_candidates_params["candidate_id"] == "in.(c1)"
    assert rows == [TaggedCandidateRow("c1", "005930")]


def test_fetch_returns_empty_list_without_second_call_when_no_active_tags():
    calls = []

    def handler(request):
        calls.append(request)
        return httpx.Response(200, json=[])

    fetcher = make_fetcher(handler)
    rows = fetcher.fetch("run-1")

    assert rows == []
    assert len(calls) == 1
    assert calls[0].url.path == "/rest/v1/candidate_tags"


def test_fetch_raises_on_malformed_candidate_tags_response():
    fetcher = make_fetcher(lambda request: httpx.Response(200, json={"unexpected": "shape"}))
    with pytest.raises(RuntimeError):
        fetcher.fetch("run-1")


def test_fetch_raises_on_malformed_candidates_response():
    def handler(request):
        if request.url.path == "/rest/v1/candidate_tags":
            return httpx.Response(200, json=[{"candidate_id": "c1"}])
        return httpx.Response(200, json={"unexpected": "shape"})

    fetcher = make_fetcher(handler)
    with pytest.raises(RuntimeError):
        fetcher.fetch("run-1")


def test_fetch_propagates_http_error_instead_of_swallowing():
    fetcher = make_fetcher(lambda request: httpx.Response(500, json={"message": "boom"}))
    with pytest.raises(httpx.HTTPStatusError):
        fetcher.fetch("run-1")


def test_fetch_propagates_transport_error():
    def handler(request):
        raise httpx.ConnectError("connection refused", request=request)

    fetcher = make_fetcher(handler)
    with pytest.raises(httpx.ConnectError):
        fetcher.fetch("run-1")
