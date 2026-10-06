from datetime import date

import pytest

from apps.batch.ls_client import LsResponse
from apps.batch.ls_market_macro_provider import (
    API_PATH,
    LsMarketMacroProvider,
    MarketMacroQuote,
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
    # 2026-10-06 CME@NQ 실측 응답.
    block = {
        "symbol": "CME@NQ", "hname": "E-Mini 나스닥100 선물", "close": "31351.50",
        "sign": "2", "change": "33.75", "diff": "0.11", "date": "20261005",
    }
    block.update(overrides)
    return LsResponse(data={"t3521OutBlock": block})


@pytest.mark.parametrize("symbol,kind", [("CME@NQ", "F"), ("USDKRWSMBS", "R")])
def test_fetch_uses_symbol_kind(symbol, kind):
    client = FakeClient(_block(symbol=symbol))

    LsMarketMacroProvider(client).fetch(symbol)

    assert client.calls == [(TR_CODE, {"t3521InBlock": {"kind": kind, "symbol": symbol}}, API_PATH)]


def test_parses_price_change_rate_and_quote_date():
    quote = LsMarketMacroProvider(FakeClient(_block())).fetch("CME@NQ")

    assert quote == MarketMacroQuote("CME@NQ", 31351.5, 33.75, 0.11, date(2026, 10, 5))


@pytest.mark.parametrize(
    "sign,change,diff,expected",
    [
        ("5", "-0.05", "-0.03", (-0.05, -0.03)),
        ("5", "0.05", "0.03", (-0.05, -0.03)),
        ("4", "0.05", "0.03", (-0.05, -0.03)),
        ("1", "-0.05", "-0.03", (0.05, 0.03)),
        ("3", "0.00", "0.00", (0.0, 0.0)),
    ],
)
def test_sign_code_is_authoritative(sign, change, diff, expected):
    quote = LsMarketMacroProvider(
        FakeClient(_block(symbol="USDKRWSMBS", close="1343.40", sign=sign, change=change, diff=diff))
    ).fetch("USDKRWSMBS")

    assert (quote.change, quote.change_rate) == expected


def test_blank_date_is_none():
    quote = LsMarketMacroProvider(FakeClient(_block(date=""))).fetch("CME@NQ")

    assert quote.quote_date is None


def test_unknown_symbol_response_is_an_error():
    # 미존재 심볼은 정상 rsp에 빈 symbol/close 0으로 온다.
    client = FakeClient(_block(symbol="", hname="", close="0", sign="", change="0", diff="0", date=""))

    with pytest.raises(RuntimeError, match="no quote"):
        LsMarketMacroProvider(client).fetch("CME@NQ")


@pytest.mark.parametrize("overrides", [{"close": "0"}, {"close": "nan"}, {"diff": None}, {"date": "2026-10-05"}])
def test_malformed_row_is_rejected(overrides):
    with pytest.raises(RuntimeError):
        LsMarketMacroProvider(FakeClient(_block(**overrides))).fetch("CME@NQ")


def test_failed_response_and_unsupported_symbol():
    with pytest.raises(RuntimeError, match="t3521 lookup failed"):
        LsMarketMacroProvider(FakeClient(LsResponse(data=None, result_code="HTTP_500"))).fetch("CME@NQ")
    with pytest.raises(ValueError):
        LsMarketMacroProvider(FakeClient(_block())).fetch("NYM@CL")
