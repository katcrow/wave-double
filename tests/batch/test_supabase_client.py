import json
from datetime import date, time

import httpx

from apps.batch.supabase_client import SupabaseCalendarRepository, SupabaseRpcClient
from domain.calendar import CalendarDecision, CalendarStatus, TradingCalendarEntry


def make_rpc_client(handler):
    transport = httpx.MockTransport(handler)
    return SupabaseRpcClient("https://example.supabase.co", "service-role-key", http_client=httpx.Client(transport=transport))


def make_calendar_repo(handler):
    transport = httpx.MockTransport(handler)
    return SupabaseCalendarRepository("https://example.supabase.co", "service-role-key", http_client=httpx.Client(transport=transport))


def test_rpc_posts_to_expected_path_with_service_role_auth():
    seen = []

    def handler(request):
        seen.append(request)
        return httpx.Response(200, json={"run_id": "abc"})

    client = make_rpc_client(handler)
    result = client.rpc("start_attempt", {"p_trading_day": "2026-09-01"})
    assert result == {"data": {"run_id": "abc"}}
    assert seen[0].url == httpx.URL("https://example.supabase.co/rest/v1/rpc/start_attempt")
    assert seen[0].headers["apikey"] == "service-role-key"
    assert seen[0].headers["authorization"] == "Bearer service-role-key"
    assert json.loads(seen[0].content) == {"p_trading_day": "2026-09-01"}


def test_rpc_maps_4xx_and_5xx_to_error_shape():
    client = make_rpc_client(lambda request: httpx.Response(400, json={"message": "STALE_FENCE_OR_LEASE"}))
    result = client.rpc("write_stage", {})
    assert result["error"]["code"] == "STALE_FENCE_OR_LEASE"
    assert result["error"]["message"] == "STALE_FENCE_OR_LEASE"
    assert result["error"]["retryable"] is False

    retryable_client = make_rpc_client(lambda request: httpx.Response(503, json={"message": "unavailable"}))
    retryable_result = retryable_client.rpc("write_stage", {})
    assert retryable_result["error"]["retryable"] is True


def test_rpc_transport_failure_is_structured_not_raised():
    def raises(request):
        raise httpx.ConnectError("boom", request=request)

    client = make_rpc_client(raises)
    result = client.rpc("start_attempt", {})
    assert result["error"]["code"] == "SUPABASE_TRANSPORT_ERROR"
    assert result["error"]["retryable"] is True


def test_calendar_get_returns_none_when_no_row_found():
    repo = make_calendar_repo(lambda request: httpx.Response(200, json=[]))
    assert repo.get(date(2026, 9, 1)) is None


def test_calendar_get_parses_open_row():
    def handler(request):
        assert request.url.params["trading_day"] == "eq.2026-09-01"
        return httpx.Response(200, json=[{"trading_day": "2026-09-01", "is_open": True, "open_time": "09:00:00", "close_time": "15:30:00"}])

    repo = make_calendar_repo(handler)
    entry = repo.get(date(2026, 9, 1))
    assert entry == TradingCalendarEntry(date(2026, 9, 1), True, time(9), time(15, 30))


def test_calendar_get_parses_closed_row_without_session_times():
    def handler(request):
        return httpx.Response(200, json=[{"trading_day": "2026-10-03", "is_open": False, "open_time": None, "close_time": None}])

    repo = make_calendar_repo(handler)
    entry = repo.get(date(2026, 10, 3))
    assert entry == TradingCalendarEntry(date(2026, 10, 3), False)


def test_calendar_upsert_sends_merge_duplicates_prefer_header():
    seen = []

    def handler(request):
        seen.append(request)
        return httpx.Response(201, json={})

    repo = make_calendar_repo(handler)
    decision = CalendarDecision(CalendarStatus.OPEN, TradingCalendarEntry(date(2026, 9, 1), True, time(9), time(15, 30)))
    repo.upsert(decision)
    assert seen[0].url == httpx.URL("https://example.supabase.co/rest/v1/trading_calendar")
    assert seen[0].headers["prefer"] == "resolution=merge-duplicates"
    body = json.loads(seen[0].content)
    assert body == {"trading_day": "2026-09-01", "is_open": True, "open_time": "09:00:00", "close_time": "15:30:00"}


def test_calendar_upsert_rejects_decision_without_entry():
    repo = make_calendar_repo(lambda request: httpx.Response(200, json={}))
    unavailable = CalendarDecision(CalendarStatus.UNAVAILABLE)
    try:
        repo.upsert(unavailable)
    except ValueError:
        pass
    else:
        raise AssertionError("expected ValueError for entry-less decision")


def test_recent_open_days_sends_expected_query_params():
    def handler(request):
        assert request.url.path == "/rest/v1/trading_calendar"
        assert request.url.params["is_open"] == "eq.true"
        assert request.url.params["trading_day"] == "lte.2026-09-01"
        assert request.url.params["select"] == "trading_day"
        assert request.url.params["order"] == "trading_day.desc"
        assert request.url.params["limit"] == "3"
        return httpx.Response(
            200,
            json=[
                {"trading_day": "2026-09-01"},
                {"trading_day": "2026-08-31"},
                {"trading_day": "2026-08-28"},
            ],
        )

    repo = make_calendar_repo(handler)
    days = repo.recent_open_days(date(2026, 9, 1), 3)
    assert days == [date(2026, 9, 1), date(2026, 8, 31), date(2026, 8, 28)]


def test_recent_open_days_returns_fewer_than_count_when_calendar_is_short():
    repo = make_calendar_repo(lambda request: httpx.Response(200, json=[{"trading_day": "2026-09-01"}]))
    days = repo.recent_open_days(date(2026, 9, 1), 3)
    assert days == [date(2026, 9, 1)]


def test_recent_open_days_raises_on_non_list_response():
    repo = make_calendar_repo(lambda request: httpx.Response(200, json={"unexpected": "shape"}))
    try:
        repo.recent_open_days(date(2026, 9, 1), 3)
    except RuntimeError:
        pass
    else:
        raise AssertionError("expected RuntimeError for malformed (non-list) response")


def test_recent_open_days_raises_on_http_error():
    repo = make_calendar_repo(lambda request: httpx.Response(500, json={"message": "boom"}))
    try:
        repo.recent_open_days(date(2026, 9, 1), 3)
    except httpx.HTTPStatusError:
        pass
    else:
        raise AssertionError("expected HTTPStatusError to propagate")
