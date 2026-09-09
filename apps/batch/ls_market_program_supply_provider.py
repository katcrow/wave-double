"""시장 전체 프로그램 순매수(t1631) adapter."""

from __future__ import annotations

from dataclasses import dataclass
from math import isclose, isfinite
from typing import Any, Protocol

from .ls_client import LsResponse
from .ls_market_supply_provider import MARKETS

TR_CODE = "t1631"
API_PATH = "/stock/program"
_MARKET_TO_GUBUN = {"KOSPI": "1", "KOSDAQ": "2"}


class MarketProgramSupplyClient(Protocol):
    def request(
        self, tr_code: str, params: dict[str, Any], *, path: str | None = None
    ) -> LsResponse: ...


@dataclass(frozen=True)
class MarketProgramSupplyBar:
    market: str
    program_net: float

    def __post_init__(self) -> None:
        if self.market not in MARKETS:
            raise ValueError(f"unsupported market: {self.market}")
        if isinstance(self.program_net, bool) or not isfinite(float(self.program_net)):
            raise ValueError("program_net must be a finite number")


MarketProgramSupply = MarketProgramSupplyBar


class LsMarketProgramSupplyProvider:
    """t1631 당일조회에서 시장별 전체 행의 순매수수량을 반환한다.

    문서 fixture의 세 행은 차익/비차익/전체 순서다. 전체 행을 임의 합산하지
    않고 마지막 행만 사용하며, 행 수가 달라지면 계약 위반으로 거부한다.
    """

    def __init__(self, client: MarketProgramSupplyClient) -> None:
        self._client = client

    def fetch(self, market: str) -> MarketProgramSupplyBar:
        if market not in _MARKET_TO_GUBUN:
            raise ValueError(f"unsupported market: {market}")
        response = self._client.request(
            TR_CODE,
            {
                "t1631InBlock": {
                    "gubun": _MARKET_TO_GUBUN[market],
                    "dgubun": "1",
                    "sdate": "",
                    "edate": "",
                    "exchgubun": "U",
                }
            },
            path=API_PATH,
        )
        if not response.ok:
            raise RuntimeError(f"LS t1631 lookup failed for {market}: {response.result_code}")
        return _parse_response(response.data, market)


def _parse_response(data: Any, market: str) -> MarketProgramSupplyBar:
    if not isinstance(data, dict):
        raise RuntimeError("LS t1631 response malformed: expected an object")
    rows = data.get("t1631OutBlock1")
    if not isinstance(rows, list) or len(rows) not in (3, 9):
        raise RuntimeError("LS t1631 response malformed: expected three or nine aggregate rows")
    if any(not isinstance(row, dict) for row in rows):
        raise RuntimeError("LS t1631 response malformed: aggregate row is not an object")
    try:
        volumes = [_finite_number(row["volume"], "volume") for row in rows]
        if len(volumes) == 3:
            total_indexes = [
                index for index, volume in enumerate(volumes)
                if isclose(volume, sum(other for other_index, other in enumerate(volumes) if other_index != index), abs_tol=1e-9)
            ]
            if len(total_indexes) != 1:
                raise ValueError("t1631 response did not identify exactly one total row")
            integrated_total = volumes[total_indexes[0]]
        else:
            # exchgubun=U currently returns three official aggregate groups.
            # Each group is [차익, 비차익, 전체], and the final group is the
            # integrated KRX+NXT result. Live values can differ by one unit
            # between component rows while the API is being updated, so the
            # documented aggregate position is the stable contract here.
            integrated_total = volumes[-1]
        # 공식 응답은 차익/비차익/전체 집계다. 전체 행을 식별해 value가 아니라
        # t1601과 단위를 맞춘 순매수수량(volume)을 사용하며 응답 순서에는 의존하지 않는다.
        return MarketProgramSupplyBar(market, integrated_total)
    except (KeyError, TypeError, ValueError, OverflowError) as exc:
        raise RuntimeError("LS t1631 response row malformed: missing/non-finite volume") from exc


def _finite_number(value: Any, field: str) -> float:
    if isinstance(value, bool) or value is None:
        raise ValueError(f"{field} must be a finite number")
    parsed = float(value)
    if not isfinite(parsed):
        raise ValueError(f"{field} must be a finite number")
    return parsed


__all__ = [
    "API_PATH",
    "LsMarketProgramSupplyProvider",
    "MarketProgramSupply",
    "MarketProgramSupplyBar",
    "TR_CODE",
]
