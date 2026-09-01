from datetime import date

import pytest

from apps.batch.ls_client import LsResponse
from apps.batch.ls_daily_bar import LsDailyBarProvider, REFERENCE_TICKER


class FakeClient:
    def __init__(self, response):
        self.response = response
        self.calls = []

    def request(self, tr_code, params):
        self.calls.append((tr_code, params))
        return self.response


def test_has_daily_bar_true_when_date_present_in_outblock1():
    response = LsResponse(data={"t8410OutBlock1": [{"date": "20260901", "close": 100}]})
    client = FakeClient(response)
    provider = LsDailyBarProvider(client)
    assert provider.has_daily_bar(date(2026, 9, 1)) is True
    assert client.calls[0][0] == "t8410"
    in_block = client.calls[0][1]["t8410InBlock"]
    assert in_block["shcode"] == REFERENCE_TICKER
    assert in_block["gubun"] == "2"
    assert in_block["sujung"] == "Y"
    assert in_block["sdate"] == "20260901"
    assert in_block["edate"] == "20260901"


def test_has_daily_bar_false_when_date_absent():
    response = LsResponse(data={"t8410OutBlock1": []})
    provider = LsDailyBarProvider(FakeClient(response))
    assert provider.has_daily_bar(date(2026, 10, 3)) is False


def test_has_daily_bar_raises_on_failed_response():
    response = LsResponse(result_code="HTTP_ERROR", message="unavailable")
    provider = LsDailyBarProvider(FakeClient(response))
    with pytest.raises(RuntimeError):
        provider.has_daily_bar(date(2026, 9, 1))


def test_has_daily_bar_raises_on_malformed_ok_response():
    # response.ok가 True인데도 t8410OutBlock1이 없거나 list가 아니면
    # 이를 "해당 없음"으로 취급해 실제 개장일을 휴장으로 캐시해서는 안 된다.
    response = LsResponse(data={"t8410OutBlock1": "not-a-list"})
    provider = LsDailyBarProvider(FakeClient(response))
    with pytest.raises(RuntimeError):
        provider.has_daily_bar(date(2026, 9, 1))
