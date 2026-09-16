"""시장 전체 투자자 수급(t1601) adapter.

t1601은 종목코드를 받지 않고 한 응답에서 시장별 block을 반환한다. 따라서
이 adapter는 시장별 호출을 흉내 내지 않고 한 번의 요청을 KOSPI/KOSDAQ
스냅샷으로 변환하며, stage가 외부 TR 형식을 알지 않도록 경계를 격리한다.

``gubun1``(주식금액수량구분1)을 "2"(금액)로 고정해 svolume_* 필드를 원(KRW)
단위 순매수 금액으로 받은 뒤 억원으로 환산한다. 대시보드 "시장 전체 수급"
패널이 뉴스에서 흔히 쓰는 금액(억원) 기준과 맞도록 하기 위함이며, 종목별
수급(t1702 등, 수량 기준 유지)과는 단위가 다르다.
"""

from __future__ import annotations

from dataclasses import dataclass
from math import isfinite
from typing import Any, Protocol

from .ls_client import LsResponse

TR_CODE = "t1601"
API_PATH = "/stock/investor"
MARKETS = ("KOSPI", "KOSDAQ")
_BLOCK_TO_MARKET = {"t1601OutBlock1": "KOSPI", "t1601OutBlock2": "KOSDAQ"}
_WON_PER_EOK = 100_000_000


class MarketSupplyClient(Protocol):
    def request(
        self, tr_code: str, params: dict[str, Any], *, path: str | None = None
    ) -> LsResponse: ...


@dataclass(frozen=True)
class MarketSupplyBar:
    """t1601의 한 시장 투자자별 순매수 스냅샷."""

    market: str
    foreign_net: float  # 억원 단위 순매수 금액
    institution_net: float
    individual_net: float

    def __post_init__(self) -> None:
        if self.market not in MARKETS:
            raise ValueError(f"unsupported market: {self.market}")
        for field in ("foreign_net", "institution_net", "individual_net"):
            value = getattr(self, field)
            if isinstance(value, bool) or not isfinite(float(value)):
                raise ValueError(f"{field} must be a finite number")


# 명시적인 이름을 선호하는 호출자도 기존 provider naming과 함께 사용할 수 있게 한다.
MarketInvestorSupply = MarketSupplyBar


class LsMarketSupplyProvider:
    """t1601 시장 전체 투자자 순매수를 파싱한다.

    ``shcode``/종목코드 파라미터는 의도적으로 존재하지 않는다. 금액 기준으로
    고정해 t1601의 ``svolume_17/18/08``(원 단위)을 억원으로 환산한 뒤
    외인/기관/개인에 매핑한다.
    """

    def __init__(self, client: MarketSupplyClient) -> None:
        self._client = client

    def fetch(self) -> list[MarketSupplyBar]:
        response = self._client.request(
            TR_CODE,
            {
                "t1601InBlock": {
                    "gubun1": "2",
                    "gubun2": "2",
                    "gubun3": "",
                    "gubun4": "2",
                    "exchgubun": "U",
                }
            },
            path=API_PATH,
        )
        if not response.ok:
            raise RuntimeError(f"LS t1601 lookup failed: {response.result_code}")
        bars: list[MarketSupplyBar] = []
        errors: list[str] = []
        for block, market in _BLOCK_TO_MARKET.items():
            try:
                bars.append(_parse_block(response.data, block, market))
            except RuntimeError as exc:
                errors.append(f"{market}: {exc}")
        if not bars:
            raise RuntimeError("LS t1601 response contained no valid market blocks: " + "; ".join(errors))
        return bars


def _parse_block(data: Any, block_name: str, market: str) -> MarketSupplyBar:
    if not isinstance(data, dict):
        raise RuntimeError("LS t1601 response malformed: expected an object")
    block = data.get(block_name)
    if not isinstance(block, dict):
        raise RuntimeError(f"LS t1601 response malformed: missing/non-object {block_name}")
    try:
        return MarketSupplyBar(
            market=market,
            foreign_net=_finite_number(block["svolume_17"], "svolume_17") / _WON_PER_EOK,
            institution_net=_finite_number(block["svolume_18"], "svolume_18") / _WON_PER_EOK,
            individual_net=_finite_number(block["svolume_08"], "svolume_08") / _WON_PER_EOK,
        )
    except (KeyError, TypeError, ValueError, OverflowError) as exc:
        raise RuntimeError(f"LS t1601 response row malformed: {block_name}") from exc


def _finite_number(value: Any, field: str) -> float:
    if isinstance(value, bool) or value is None:
        raise ValueError(f"{field} must be a finite number")
    parsed = float(value)
    if not isfinite(parsed):
        raise ValueError(f"{field} must be a finite number")
    return parsed


__all__ = [
    "API_PATH",
    "MARKETS",
    "LsMarketSupplyProvider",
    "MarketInvestorSupply",
    "MarketSupplyBar",
    "TR_CODE",
]
