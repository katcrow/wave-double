from datetime import date
from math import inf, nan

import pytest

from apps.batch.ls_client import LsResponse
from apps.batch.ls_market_supply_provider import (
    API_PATH,
    LsMarketSupplyProvider,
    MarketSupplyBar,
    TR_CODE,
)


class FakeClient:
    def __init__(self, response):
        self.response = response
        self.calls = []

    def request(self, tr_code, params, *, path=None):
        self.calls.append((tr_code, params, path))
        return self.response


def _block(foreign=10, institution=20, individual=-30):
    return {"svolume_17": foreign, "svolume_18": institution, "svolume_08": individual}


def test_fetch_uses_market_endpoint_and_no_ticker_parameter_and_maps_blocks():
    client = FakeClient(LsResponse(data={
        "t1601OutBlock1": _block(100, 200, -300),
        "t1601OutBlock2": _block(-10, -20, 30),
    }))

    values = LsMarketSupplyProvider(client).fetch()

    assert client.calls == [(
        TR_CODE,
        {"t1601InBlock": {
            "gubun1": "2", "gubun2": "2", "gubun3": "", "gubun4": "2", "exchgubun": "U",
        }},
        API_PATH,
    )]
    assert values == [
        MarketSupplyBar("KOSPI", 100.0, 200.0, -300.0),
        MarketSupplyBar("KOSDAQ", -10.0, -20.0, 30.0),
    ]
    assert "shcode" not in client.calls[0][1]["t1601InBlock"]


@pytest.mark.parametrize("field,value", [
    ("svolume_17", None), ("svolume_18", "bad"), ("svolume_08", nan), ("svolume_17", inf),
])
def test_fetch_rejects_missing_non_numeric_or_non_finite_market_values(field, value):
    block = _block()
    block[field] = value
    with pytest.raises(RuntimeError):
        LsMarketSupplyProvider(FakeClient(LsResponse(data={
            "t1601OutBlock1": block, "t1601OutBlock2": block.copy(),
        }))).fetch()


@pytest.mark.parametrize("data", [
    {},
    {"t1601OutBlock1": {}, "t1601OutBlock2": None},
    {"t1601OutBlock1": [], "t1601OutBlock2": []},
    {"t1601OutBlock1": "not-an-object", "t1601OutBlock2": "not-an-object"},
])
def test_fetch_rejects_malformed_blocks(data):
    with pytest.raises(RuntimeError):
        LsMarketSupplyProvider(FakeClient(LsResponse(data=data))).fetch()


def test_fetch_preserves_valid_market_when_the_other_block_is_malformed():
    values = LsMarketSupplyProvider(FakeClient(LsResponse(data={
        "t1601OutBlock1": {"svolume_17": "bad"},
        "t1601OutBlock2": _block(-10, -20, 30),
    }))).fetch()

    assert values == [MarketSupplyBar("KOSDAQ", -10.0, -20.0, 30.0)]


def test_fetch_rejects_non_ok_response():
    with pytest.raises(RuntimeError, match="lookup failed"):
        LsMarketSupplyProvider(FakeClient(LsResponse(result_code="HTTP_ERROR"))).fetch()
