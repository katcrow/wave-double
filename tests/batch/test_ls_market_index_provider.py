import pytest

from apps.batch.ls_client import LsResponse
from apps.batch.ls_market_index_provider import (
    API_PATH,
    LsMarketIndexProvider,
    MarketIndexBar,
    TR_CODE,
)


class FakeClient:
    def __init__(self, response):
        self.response = response
        self.calls = []

    def request(self, tr_code, params, *, path=None):
        self.calls.append((tr_code, params, path))
        return self.response


def _block(**overrides):
    # 2026-10-06 KOSDAQ 실측 응답에서 필요한 필드만 발췌했다.
    block = {
        "pricejisu": "914.70", "sign": "2", "change": "21.41", "diffjisu": "2.40",
        "highjo": 950, "upjo": 4, "unchgjo": 145, "lowjo": 726, "downjo": 0,
    }
    block.update(overrides)
    return LsResponse(data={"t1511OutBlock": block})


@pytest.mark.parametrize("market,upcode", [("KOSPI", "001"), ("KOSDAQ", "301")])
def test_fetch_uses_market_upcode(market, upcode):
    client = FakeClient(_block())

    LsMarketIndexProvider(client).fetch(market)

    assert client.calls == [(TR_CODE, {"t1511InBlock": {"upcode": upcode}}, API_PATH)]


def test_fetch_adds_limit_counts_to_advancing_and_declining():
    result = LsMarketIndexProvider(FakeClient(_block(downjo=2))).fetch("KOSDAQ")

    assert result == MarketIndexBar("KOSDAQ", 914.70, 2.40, 954, 145, 728)


def test_fetch_keeps_signed_change_rate_even_though_change_is_absolute():
    result = LsMarketIndexProvider(FakeClient(_block(sign="5", change="59.84", diffjisu="-0.85"))).fetch("KOSPI")

    assert result.index_change_rate == -0.85


def test_fetch_raises_on_failed_response():
    with pytest.raises(RuntimeError, match="t1511 lookup failed"):
        LsMarketIndexProvider(FakeClient(LsResponse(result_code="HTTP_500"))).fetch("KOSPI")


@pytest.mark.parametrize("data", [
    None,
    {},
    {"t1511OutBlock": []},
    {"t1511OutBlock": {"pricejisu": "914.70"}},
])
def test_fetch_rejects_malformed_response(data):
    with pytest.raises(RuntimeError, match="malformed"):
        LsMarketIndexProvider(FakeClient(LsResponse(data=data))).fetch("KOSPI")


@pytest.mark.parametrize("overrides", [
    {"diffjisu": "NaN"},
    {"highjo": -1},
    {"lowjo": 1.5},
    {"unchgjo": None},
])
def test_fetch_rejects_invalid_values(overrides):
    with pytest.raises(RuntimeError, match="malformed"):
        LsMarketIndexProvider(FakeClient(_block(**overrides))).fetch("KOSPI")


def test_fetch_rejects_unknown_market():
    with pytest.raises(ValueError):
        LsMarketIndexProvider(FakeClient(_block())).fetch("NASDAQ")
