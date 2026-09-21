from math import inf, nan

import pytest

from apps.batch.ls_client import LsResponse
from apps.batch.ls_market_program_supply_provider import (
    LsMarketProgramSupplyProvider,
    MarketProgramSupplyBar,
    TR_CODE,
)


class FakeClient:
    def __init__(self, response):
        self.response = response
        self.calls = []

    def request(self, tr_code, params, *, path=None):
        self.calls.append((tr_code, params, path))
        return self.response


def _response(total=99):
    return LsResponse(data={"t1631OutBlock1": [
        {"value": 40}, {"value": 59}, {"value": total},
    ]})


@pytest.mark.parametrize("market,gubun", [("KOSPI", "1"), ("KOSDAQ", "2")])
def test_fetch_uses_market_gubun_and_selects_documented_total_row(market, gubun):
    client = FakeClient(_response())

    result = LsMarketProgramSupplyProvider(client).fetch(market)

    assert result == MarketProgramSupplyBar(market, 0.99)
    assert client.calls == [(
        TR_CODE,
        {"t1631InBlock": {
            "gubun": gubun, "dgubun": "1", "sdate": "", "edate": "", "exchgubun": "U",
        }},
        "/stock/program",
    )]


def test_fetch_identifies_total_row_without_relying_on_response_order():
    client = FakeClient(LsResponse(data={"t1631OutBlock1": [
        {"value": 99}, {"value": 40}, {"value": 59},
    ]}))

    assert LsMarketProgramSupplyProvider(client).fetch("KOSPI") == MarketProgramSupplyBar("KOSPI", 0.99)


def test_fetch_selects_integrated_total_from_current_nine_row_response():
    rows = [
        {"value": 10}, {"value": -55}, {"value": -45},
        {"value": -914}, {"value": 8}, {"value": -906},
        {"value": -635}, {"value": -316}, {"value": -951},
    ]
    assert LsMarketProgramSupplyProvider(FakeClient(LsResponse(data={"t1631OutBlock1": rows}))).fetch("KOSPI") == MarketProgramSupplyBar("KOSPI", -9.51)


@pytest.mark.parametrize("rows", [[], [{"value": 1}], [{"value": 1}, {"value": 2}], [{"value": 1}, "bad", {"value": 3}]])
def test_fetch_rejects_ambiguous_or_malformed_aggregate_rows(rows):
    with pytest.raises(RuntimeError):
        LsMarketProgramSupplyProvider(FakeClient(LsResponse(data={"t1631OutBlock1": rows}))).fetch("KOSPI")


@pytest.mark.parametrize("value", [None, "bad", nan, inf])
def test_fetch_rejects_non_finite_total_volume(value):
    with pytest.raises(RuntimeError):
        LsMarketProgramSupplyProvider(FakeClient(LsResponse(data={
            "t1631OutBlock1": [{"value": 1}, {"value": 2}, {"value": value}],
        }))).fetch("KOSPI")


@pytest.mark.parametrize("index", [0, 1])
def test_fetch_rejects_non_finite_component_volume(index):
    rows = [{"value": 40}, {"value": 59}, {"value": 99}]
    rows[index]["value"] = inf
    with pytest.raises(RuntimeError):
        LsMarketProgramSupplyProvider(FakeClient(LsResponse(data={"t1631OutBlock1": rows}))).fetch("KOSPI")


def test_fetch_rejects_unknown_market_and_non_ok_response():
    with pytest.raises(ValueError):
        LsMarketProgramSupplyProvider(FakeClient(_response())).fetch("KOSPI100")
    with pytest.raises(RuntimeError, match="lookup failed"):
        LsMarketProgramSupplyProvider(FakeClient(LsResponse(result_code="HTTP_ERROR"))).fetch("KOSDAQ")
