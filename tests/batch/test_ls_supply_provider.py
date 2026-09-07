from datetime import date

import pytest

from apps.batch.ls_client import LsResponse
from apps.batch.ls_supply_provider import LsSupplyProvider, SupplyBar, TR_CODE


class FakeClient:
    def __init__(self, response):
        self.response = response
        self.calls = []

    def request(self, tr_code, params):
        self.calls.append((tr_code, params))
        return self.response


def _row(**overrides):
    row = {
        "date": "20260901",
        "close": 72000,
        "sign": "2",
        "change": 500,
        "diff": "0.70",
        "volume": 1200000,
        "tjj0008": -1200,
        "tjj0016": 800,
        "tjj0018": 400,
    }
    row.update(overrides)
    return row


def test_fetch_sends_correct_t1702_in_block_params():
    response = LsResponse(data={"t1702OutBlock1": [_row()]})
    client = FakeClient(response)
    provider = LsSupplyProvider(client)

    provider.fetch("005930", date(2026, 8, 28), date(2026, 9, 1))

    assert client.calls[0][0] == TR_CODE
    in_block = client.calls[0][1]["t1702InBlock"]
    assert in_block == {
        "shcode": "005930",
        "fromdt": "20260828",
        "todt": "20260901",
        "volvalgb": "1",
        "msmdgb": "0",
        "gubun": "0",
        "exchgubun": "U",
    }


def test_fetch_parses_rows_into_supply_bar_with_diff_carried_through_unchanged():
    response = LsResponse(data={"t1702OutBlock1": [_row()]})
    provider = LsSupplyProvider(FakeClient(response))

    bars = provider.fetch("005930", date(2026, 8, 28), date(2026, 9, 1))

    assert bars == [
        SupplyBar(
            trading_day=date(2026, 9, 1),
            close=72000.0,
            change_pct=0.70,  # diff는 재계산 없이 그대로 change_pct로 전달된다.
            volume=1200000.0,
            individual_net=-1200.0,
            foreign_net=800.0,
            institution_net=400.0,
        )
    ]


def test_fetch_parses_multiple_rows_independent_of_order():
    response = LsResponse(
        data={
            "t1702OutBlock1": [
                _row(date="20260901", close=72000, diff="1.41"),
                _row(date="20260828", close=70000, diff="1.00"),
            ]
        }
    )
    provider = LsSupplyProvider(FakeClient(response))

    bars = provider.fetch("005930", date(2026, 8, 28), date(2026, 9, 1))

    assert {bar.trading_day for bar in bars} == {date(2026, 9, 1), date(2026, 8, 28)}


def test_fetch_raises_on_non_ok_response():
    response = LsResponse(result_code="HTTP_ERROR", message="unavailable")
    provider = LsSupplyProvider(FakeClient(response))
    with pytest.raises(RuntimeError):
        provider.fetch("005930", date(2026, 8, 28), date(2026, 9, 1))


def test_fetch_raises_on_missing_out_block():
    response = LsResponse(data={"rsp_cd": "00000"})
    provider = LsSupplyProvider(FakeClient(response))
    with pytest.raises(RuntimeError):
        provider.fetch("005930", date(2026, 8, 28), date(2026, 9, 1))


def test_fetch_raises_on_non_list_out_block():
    response = LsResponse(data={"t1702OutBlock1": "not-a-list"})
    provider = LsSupplyProvider(FakeClient(response))
    with pytest.raises(RuntimeError):
        provider.fetch("005930", date(2026, 8, 28), date(2026, 9, 1))


def test_fetch_raises_on_row_missing_required_field():
    response = LsResponse(data={"t1702OutBlock1": [{"date": "20260901", "close": 72000}]})
    provider = LsSupplyProvider(FakeClient(response))
    with pytest.raises(RuntimeError):
        provider.fetch("005930", date(2026, 8, 28), date(2026, 9, 1))


def test_fetch_raises_on_malformed_date_length_instead_of_silently_misparsing():
    """리뷰 patch: 8자를 초과/미달하는 date 문자열은 슬라이싱 전에 검증되어 명시적으로
    거부되어야 한다(조용한 오파싱 금지)."""
    response = LsResponse(data={"t1702OutBlock1": [_row(date="202609011")]})  # 9 digits
    provider = LsSupplyProvider(FakeClient(response))
    with pytest.raises(RuntimeError):
        provider.fetch("005930", date(2026, 8, 28), date(2026, 9, 1))

    short_response = LsResponse(data={"t1702OutBlock1": [_row(date="2026901")]})  # 7 digits
    short_provider = LsSupplyProvider(FakeClient(short_response))
    with pytest.raises(RuntimeError):
        short_provider.fetch("005930", date(2026, 8, 28), date(2026, 9, 1))
