from datetime import date

import pytest

from apps.batch.ls_client import LsResponse
from apps.batch.ls_program_supply_provider import LsProgramSupplyProvider, ProgramSupplyBar, TR_CODE


class FakeClient:
    def __init__(self, response):
        self.response = response
        self.calls = []

    def request(self, tr_code, params):
        self.calls.append((tr_code, params))
        return self.response


def _row(**overrides):
    row = {"date": "20260901", "time": "090100", "svolume": 1234}
    row.update(overrides)
    return row


def test_fetch_sends_daily_quantity_t1637_request_and_filters_date_range():
    response = LsResponse(
        data={
            "t1637OutBlock1": [
                _row(date="20260901", svolume="30"),
                _row(date="20260831", svolume=-20),
                _row(date="20260828", svolume=10),
                _row(date="20260827", svolume=999),
            ]
        }
    )
    client = FakeClient(response)

    bars = LsProgramSupplyProvider(client).fetch("005930", date(2026, 8, 28), date(2026, 9, 1))

    assert client.calls == [
        (
            TR_CODE,
            {
                "t1637InBlock": {
                    "gubun1": "0",
                    "gubun2": "1",
                    "shcode": "005930",
                    "date": "",
                    "time": "",
                    "cts_idx": 0,
                    "exchgubun": "U",
                }
            },
        )
    ]
    assert bars == [
        ProgramSupplyBar(date(2026, 9, 1), 30.0),
        ProgramSupplyBar(date(2026, 8, 31), -20.0),
        ProgramSupplyBar(date(2026, 8, 28), 10.0),
    ]


def test_fetch_rejects_non_ok_and_malformed_responses():
    with pytest.raises(RuntimeError, match="lookup failed"):
        LsProgramSupplyProvider(FakeClient(LsResponse(result_code="HTTP_ERROR"))).fetch(
            "005930", date(2026, 8, 28), date(2026, 9, 1)
        )

    for data in (
        {},
        {"t1637OutBlock1": "not-a-list"},
        {"t1637OutBlock1": ["not-an-object"]},
        {"t1637OutBlock1": [_row(date="202609011")]},
        {"t1637OutBlock1": [_row(date="20260230")]},
        {"t1637OutBlock1": [_row(svolume=None)]},
        {"t1637OutBlock1": [_row(svolume="")]},
        {"t1637OutBlock1": [_row(svolume="not-a-number")]},
        {"t1637OutBlock1": [_row(svolume="nan")]},
        {"t1637OutBlock1": [_row(svolume="inf")]},
    ):
        with pytest.raises(RuntimeError):
            LsProgramSupplyProvider(FakeClient(LsResponse(data=data))).fetch(
                "005930", date(2026, 8, 28), date(2026, 9, 1)
            )


def test_fetch_rejects_reversed_date_range():
    with pytest.raises(ValueError, match="fromdt"):
        LsProgramSupplyProvider(FakeClient(LsResponse(data={"t1637OutBlock1": []}))).fetch(
            "005930", date(2026, 9, 1), date(2026, 8, 28)
        )
