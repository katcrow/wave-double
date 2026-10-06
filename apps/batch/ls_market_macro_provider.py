"""나스닥100 선물·원/달러 환율 시세(t3521 해외지수조회) adapter.

실측(2026-10-06) 기준 응답 계약:
- ``t3521``(kind F/R)은 장중에도 갱신되는 현재가를 준다. 같은 심볼을
  ``t3518`` 일봉으로 받으면 kind F의 가격이 1/100로 내려오므로(31351.50 →
  313.5025) 쓰지 않는다.
- ``diff``(등락률, %)와 ``change``(전일대비)는 부호를 포함해 내려오지만
  (``-0.05``/sign ``5``) 부호의 권위는 ``sign``(1·2 상승, 3 보합, 4·5 하락)에
  둔다.
- ``date``는 해당 시장 기준 일자다. CME 나스닥 선물은 미국 거래일
  (KST 낮에는 전날)로, 원/달러는 서울 거래일로 온다. 미존재 심볼은
  rsp 정상에 ``symbol``이 빈 문자열로 온다.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime
from math import isfinite
from typing import Any, Protocol

from .ls_client import LsResponse

TR_CODE = "t3521"
API_PATH = "/stock/investinfo"

# 화면 표시 순서. (심볼, t3521 kind)
MACRO_SYMBOLS: tuple[tuple[str, str], ...] = (
    ("CME@NQ", "F"),
    ("USDKRWSMBS", "R"),
)
_KIND_BY_SYMBOL = dict(MACRO_SYMBOLS)
_RISING_SIGNS = {"1", "2"}
_FALLING_SIGNS = {"4", "5"}


class MarketMacroClient(Protocol):
    def request(
        self, tr_code: str, params: dict[str, Any], *, path: str | None = None
    ) -> LsResponse: ...


@dataclass(frozen=True)
class MarketMacroQuote:
    symbol: str
    price: float
    change: float  # 전일대비, 부호 포함
    change_rate: float  # % 단위, 부호 포함
    quote_date: date | None

    def __post_init__(self) -> None:
        if self.symbol not in _KIND_BY_SYMBOL:
            raise ValueError(f"unsupported macro symbol: {self.symbol}")
        for field in ("price", "change", "change_rate"):
            value = getattr(self, field)
            if isinstance(value, bool) or not isfinite(float(value)):
                raise ValueError(f"{field} must be a finite number")
        if self.price <= 0:
            raise ValueError("price must be positive")


class LsMarketMacroProvider:
    def __init__(self, client: MarketMacroClient) -> None:
        self._client = client

    def fetch(self, symbol: str) -> MarketMacroQuote:
        kind = _KIND_BY_SYMBOL.get(symbol)
        if kind is None:
            raise ValueError(f"unsupported macro symbol: {symbol}")
        response = self._client.request(
            TR_CODE,
            {"t3521InBlock": {"kind": kind, "symbol": symbol}},
            path=API_PATH,
        )
        if not response.ok:
            raise RuntimeError(f"LS t3521 lookup failed for {symbol}: {response.result_code}")
        return _parse_response(response.data, symbol)


def _parse_response(data: Any, symbol: str) -> MarketMacroQuote:
    if not isinstance(data, dict):
        raise RuntimeError("LS t3521 response malformed: expected an object")
    block = data.get("t3521OutBlock")
    if not isinstance(block, dict):
        raise RuntimeError("LS t3521 response malformed: missing/non-object t3521OutBlock")
    if block.get("symbol") != symbol:
        raise RuntimeError(f"LS t3521 returned no quote for {symbol}")
    try:
        sign = str(block["sign"]).strip()
        return MarketMacroQuote(
            symbol=symbol,
            price=_finite_number(block["close"], "close"),
            change=_signed(_finite_number(block["change"], "change"), sign),
            change_rate=_signed(_finite_number(block["diff"], "diff"), sign),
            quote_date=_quote_date(block.get("date")),
        )
    except (KeyError, TypeError, ValueError, OverflowError) as exc:
        raise RuntimeError("LS t3521 response row malformed: t3521OutBlock") from exc


def _signed(value: float, sign: str) -> float:
    if sign in _RISING_SIGNS:
        return abs(value)
    if sign in _FALLING_SIGNS:
        return -abs(value)
    if sign == "3":
        return 0.0
    return value


def _quote_date(value: Any) -> date | None:
    text = str(value or "").strip()
    if not text:
        return None
    return datetime.strptime(text, "%Y%m%d").date()


def _finite_number(value: Any, field: str) -> float:
    if isinstance(value, bool) or value is None:
        raise ValueError(f"{field} must be a finite number")
    parsed = float(value)
    if not isfinite(parsed):
        raise ValueError(f"{field} must be a finite number")
    return parsed


__all__ = [
    "API_PATH",
    "LsMarketMacroProvider",
    "MACRO_SYMBOLS",
    "MarketMacroQuote",
    "TR_CODE",
]
