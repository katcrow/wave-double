"""시장 지수 등락률과 상승/보합/하락 종목수(t1511 업종현재가) adapter.

KOSPI는 업종코드 ``001``(종합), KOSDAQ은 ``301``로 조회한다.

실측(2026-10-06) 기준 응답 계약:
- ``diffjisu``(지수등락율)는 부호가 포함된 % 값이다(예: ``-0.85``). 반면
  ``change``(전일대비)는 절댓값이라 부호는 ``sign``에만 있다. 등락률은
  ``diffjisu``를 그대로 쓴다.
- ``highjo``(상승)/``lowjo``(하락)는 상한/하한 종목을 포함하지 않는다.
  t1514 ``totjo``(종목수)가 ``high + unchg + low + up + down``과 일치함을
  확인했으므로, 화면의 상승/하락 종목수는 상한/하한을 더해 만든다.
"""

from __future__ import annotations

from dataclasses import dataclass
from math import isfinite
from typing import Any, Protocol

from .ls_client import LsResponse
from .ls_market_supply_provider import MARKETS

TR_CODE = "t1511"
API_PATH = "/indtp/market-data"
_MARKET_TO_UPCODE = {"KOSPI": "001", "KOSDAQ": "301"}


class MarketIndexClient(Protocol):
    def request(
        self, tr_code: str, params: dict[str, Any], *, path: str | None = None
    ) -> LsResponse: ...


@dataclass(frozen=True)
class MarketIndexBar:
    market: str
    index_price: float
    index_change_rate: float  # % 단위, 부호 포함
    advancing_count: int  # 상한 포함
    unchanged_count: int
    declining_count: int  # 하한 포함

    def __post_init__(self) -> None:
        if self.market not in MARKETS:
            raise ValueError(f"unsupported market: {self.market}")
        for field in ("index_price", "index_change_rate"):
            value = getattr(self, field)
            if isinstance(value, bool) or not isfinite(float(value)):
                raise ValueError(f"{field} must be a finite number")
        for field in ("advancing_count", "unchanged_count", "declining_count"):
            value = getattr(self, field)
            if isinstance(value, bool) or not isinstance(value, int) or value < 0:
                raise ValueError(f"{field} must be a non-negative integer")


class LsMarketIndexProvider:
    def __init__(self, client: MarketIndexClient) -> None:
        self._client = client

    def fetch(self, market: str) -> MarketIndexBar:
        if market not in _MARKET_TO_UPCODE:
            raise ValueError(f"unsupported market: {market}")
        response = self._client.request(
            TR_CODE,
            {"t1511InBlock": {"upcode": _MARKET_TO_UPCODE[market]}},
            path=API_PATH,
        )
        if not response.ok:
            raise RuntimeError(f"LS t1511 lookup failed for {market}: {response.result_code}")
        return _parse_response(response.data, market)


def _parse_response(data: Any, market: str) -> MarketIndexBar:
    if not isinstance(data, dict):
        raise RuntimeError("LS t1511 response malformed: expected an object")
    block = data.get("t1511OutBlock")
    if not isinstance(block, dict):
        raise RuntimeError("LS t1511 response malformed: missing/non-object t1511OutBlock")
    try:
        return MarketIndexBar(
            market=market,
            index_price=_finite_number(block["pricejisu"], "pricejisu"),
            index_change_rate=_finite_number(block["diffjisu"], "diffjisu"),
            advancing_count=_count(block["highjo"], "highjo") + _count(block["upjo"], "upjo"),
            unchanged_count=_count(block["unchgjo"], "unchgjo"),
            declining_count=_count(block["lowjo"], "lowjo") + _count(block["downjo"], "downjo"),
        )
    except (KeyError, TypeError, ValueError, OverflowError) as exc:
        raise RuntimeError("LS t1511 response row malformed: t1511OutBlock") from exc


def _finite_number(value: Any, field: str) -> float:
    if isinstance(value, bool) or value is None:
        raise ValueError(f"{field} must be a finite number")
    parsed = float(value)
    if not isfinite(parsed):
        raise ValueError(f"{field} must be a finite number")
    return parsed


def _count(value: Any, field: str) -> int:
    parsed = _finite_number(value, field)
    if parsed < 0 or not parsed.is_integer():
        raise ValueError(f"{field} must be a non-negative integer")
    return int(parsed)


__all__ = [
    "API_PATH",
    "LsMarketIndexProvider",
    "MarketIndexBar",
    "TR_CODE",
]
