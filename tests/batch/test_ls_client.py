from datetime import datetime, timezone
import json
from concurrent.futures import ThreadPoolExecutor
from math import inf, nan

import pytest

import httpx

from apps.batch.ls_client import ConfigurationError, LsClient, LsClientConfig


class FakeClock:
    def __init__(self, value=0.0):
        self.value = value

    def __call__(self):
        return self.value

    def sleep(self, seconds):
        self.value += seconds


def make_client(handler, *, config=None, clock=None):
    clock = clock or FakeClock()
    transport = httpx.MockTransport(handler)
    return LsClient(lambda: "token-value", config=config, http_client=httpx.Client(transport=transport), clock=clock, sleeper=clock.sleep)


def test_generic_request_uses_common_headers_and_payload():
    seen = []

    def handler(request):
        seen.append(request)
        return httpx.Response(200, json={"rsp": "ok"})

    result = make_client(handler).request("t-any", {"foo": "bar"})
    assert result.data == {"rsp": "ok"}
    assert seen[0].url == httpx.URL("https://openapi.ls-sec.co.kr:8080")
    assert seen[0].headers["authorization"] == "Bearer token-value"
    assert seen[0].headers["tr_cd"] == "t-any"
    assert seen[0].headers["tr_cont"] == "N"
    assert json.loads(seen[0].content) == {"foo": "bar"}


def test_caller_can_select_api_path_and_optional_mac_address():
    seen = []
    client = make_client(
        lambda request: (seen.append(request) or httpx.Response(200, json={})),
        config=LsClientConfig(endpoint="https://example.test:8080", mac_address="00:11:22:33:44:55"),
    )
    client.request("t1101", {}, path="/stock/market-data")
    assert seen[0].url == httpx.URL("https://example.test:8080/stock/market-data")
    assert seen[0].headers["mac_address"] == "00:11:22:33:44:55"


@pytest.mark.parametrize(
    ("tr_code", "path"),
    [
        ("t1859", "/stock/item-search"),
        ("t1702", "/stock/frgr-itt"),
        ("t8410", "/stock/chart"),
        ("t1637", "/stock/program"),
    ],
)
def test_known_tr_codes_use_their_official_api_path(tr_code, path):
    seen = []
    client = make_client(
        lambda request: (seen.append(request) or httpx.Response(200, json={}))
    )
    client.request(tr_code, {})
    assert seen[0].url == httpx.URL(f"https://openapi.ls-sec.co.kr:8080{path}")


def test_buckets_are_independent_per_tr():
    clock = FakeClock()
    result_codes = []
    client = make_client(lambda request: (result_codes.append(request.headers["tr_cd"]) or httpx.Response(200, json={})), clock=clock)
    client.request("a", {})
    client.request("b", {})
    assert result_codes == ["a", "b"]
    assert clock.value == 0.0


def test_same_tr_reservations_do_not_share_a_future_slot():
    clock = FakeClock()
    sent_at = []
    client = make_client(lambda request: (sent_at.append(clock.value) or httpx.Response(200, json={})), clock=clock)
    client.request("same", {})
    client.request("same", {})
    client.request("same", {})
    assert sent_at == [0.0, 1.0, 2.0]


def test_concurrent_same_tr_calls_are_refill_limited():
    clock = FakeClock()
    sent_at = []

    def handler(request):
        sent_at.append(clock.value)
        return httpx.Response(200, json={})

    client = make_client(handler, clock=clock)
    with ThreadPoolExecutor(max_workers=2) as pool:
        list(pool.map(lambda _: client.request("same", {}), range(2)))
    assert sorted(sent_at) == [0.0, 1.0]


@pytest.mark.parametrize("field", ["personal_requests_per_second", "default_backoff_seconds", "max_retry_after_seconds", "budget_seconds"])
@pytest.mark.parametrize("value", [nan, inf, -inf])
def test_config_rejects_non_finite_timing_values(field, value):
    with pytest.raises(ConfigurationError):
        LsClientConfig(**{field: value})


def test_retry_after_delta_seconds_is_respected():
    clock = FakeClock()
    calls = 0

    def handler(request):
        nonlocal calls
        calls += 1
        return httpx.Response(429, headers={"Retry-After": "2"}) if calls == 1 else httpx.Response(200, json={"ok": True})

    result = make_client(handler, clock=clock).request("t", {})
    assert result.ok and calls == 2 and clock.value == 2


def test_retry_after_http_date_and_invalid_value_use_bounded_defaults():
    clock = FakeClock(datetime(2026, 9, 1, tzinfo=timezone.utc).timestamp())
    calls = 0

    def handler(request):
        nonlocal calls
        calls += 1
        if calls == 1:
            return httpx.Response(429, headers={"Retry-After": "Tue, 01 Sep 2026 00:00:03 GMT"})
        return httpx.Response(200, json={})

    result = make_client(handler, clock=clock).request("t", {})
    assert result.ok and clock.value == datetime(2026, 9, 1, tzinfo=timezone.utc).timestamp() + 3

    invalid_clock = FakeClock()
    client = make_client(lambda request: httpx.Response(429, headers={"Retry-After": "nonsense"}), clock=invalid_clock, config=LsClientConfig(max_retries=0))
    assert client.request("t", {}).result_code == "RATE_LIMIT_EXHAUSTED"


def test_invalid_retry_after_uses_default_and_exhausts_all_bounded_retries():
    clock = FakeClock()
    calls = 0

    def handler(request):
        nonlocal calls
        calls += 1
        return httpx.Response(429, headers={"Retry-After": "not-a-delay"})

    result = make_client(handler, clock=clock, config=LsClientConfig(max_retries=2, default_backoff_seconds=2)).request("t", {})
    assert result.result_code == "RATE_LIMIT_EXHAUSTED"
    assert calls == 3 and clock.value == 4


def test_clock_overshoot_after_sleeper_prevents_next_http_request():
    clock = FakeClock()
    calls = 0

    def handler(request):
        nonlocal calls
        calls += 1
        return httpx.Response(429, headers={"Retry-After": "1"})

    def oversleep(seconds):
        clock.value += seconds + 1

    client = LsClient(
        lambda: "token-value",
        config=LsClientConfig(budget_seconds=1.5),
        http_client=httpx.Client(transport=httpx.MockTransport(handler)),
        clock=clock,
        sleeper=oversleep,
    )
    result = client.request("t", {})
    assert result.result_code == "BUDGET_EXHAUSTED" and calls == 1


def test_retryable_5xx_is_retried_and_transport_failure_is_structured():
    clock = FakeClock()
    calls = 0

    def handler(request):
        nonlocal calls
        calls += 1
        return httpx.Response(503) if calls == 1 else httpx.Response(200, json={"ok": True})

    result = make_client(handler, clock=clock).request("t", {})
    assert result.ok and calls == 2 and clock.value == 1

    def raises(request):
        raise httpx.ConnectError("unavailable", request=request)

    result = make_client(raises, config=LsClientConfig(max_retries=1, budget_seconds=0.5), clock=FakeClock()).request("t", {})
    assert result.result_code == "BUDGET_EXHAUSTED" and result.retryable


def test_retry_and_budget_exhaustion_do_not_send_extra_request():
    clock = FakeClock()
    calls = 0

    def handler(request):
        nonlocal calls
        calls += 1
        return httpx.Response(429, headers={"Retry-After": "5"})

    result = make_client(handler, clock=clock, config=LsClientConfig(budget_seconds=3)).request("t", {})
    assert result.result_code == "BUDGET_EXHAUSTED" and calls == 1


def test_cross_tr_parallelization_is_rejected():
    try:
        LsClientConfig(allow_cross_tr_parallel=True)
    except ConfigurationError:
        pass
    else:
        raise AssertionError("configuration must reject cross-TR parallelism")
