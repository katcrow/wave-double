"""Story 4.1: 종목별 가격·수급(t1702) adapter.

``ls_daily_bar.py``의 단일 TR adapter 패턴(``client.request(TR_CODE, {...})`` →
``response.ok`` 체크 → malformed 응답은 ``RuntimeError``)을 그대로 따른다.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date
import math
from typing import Any, Protocol

from .ls_client import LsResponse

TR_CODE = "t1702"


class SupplyClient(Protocol):
    def request(self, tr_code: str, params: dict[str, Any]) -> LsResponse: ...


@dataclass(frozen=True)
class SupplyBar:
    """``t1702OutBlock1``의 단일 거래일 행.

    ``change_pct``는 LS가 이미 전일 종가 대비로 계산해 내려준 ``diff``를 그대로
    옮긴 값이다(재계산 금지, story 4.1 Always 규칙).
    """

    trading_day: date
    close: float
    change_pct: float
    volume: float
    individual_net: float
    foreign_net: float
    institution_net: float

    def __post_init__(self) -> None:
        for name in (
            "close", "change_pct", "volume", "individual_net", "foreign_net", "institution_net",
        ):
            value = getattr(self, name)
            if isinstance(value, bool) or not math.isfinite(value):
                raise ValueError(f"t1702 {name} must be finite")


class LsSupplyProvider:
    """``t1702``(외인기관종목별동향) 조회로 종목의 일별 가격·수급을 반환한다.

    후보당 1콜: ``volvalgb="1"``(수량), ``msmdgb="0"``(순매수), ``gubun="0"``(일간),
    ``exchgubun="U"``(통합)로 고정한다(design notes). 응답 순서에 의존하지 않고
    각 행의 ``date``로 매핑할 수 있도록 파싱만 담당하며, 날짜 slot 매핑은
    ``supply_stage``의 책임이다.
    """

    def __init__(self, client: SupplyClient) -> None:
        self._client = client

    def fetch(self, ticker: str, fromdt: date, todt: date) -> list[SupplyBar]:
        response = self._client.request(
            TR_CODE,
            {
                "t1702InBlock": {
                    "shcode": ticker,
                    "fromdt": fromdt.strftime("%Y%m%d"),
                    "todt": todt.strftime("%Y%m%d"),
                    "volvalgb": "1",
                    "msmdgb": "0",
                    "gubun": "0",
                    "exchgubun": "U",
                }
            },
        )
        if not response.ok:
            raise RuntimeError(f"LS t1702 lookup failed: {response.result_code}")
        return [_parse_row(row) for row in _rows(response.data)]


def _rows(data: Any) -> list[dict[str, Any]]:
    if isinstance(data, dict):
        rows = data.get("t1702OutBlock1")
        if isinstance(rows, list):
            return rows
    raise RuntimeError("LS t1702 response malformed: missing/non-list t1702OutBlock1")


def _parse_row(row: dict[str, Any]) -> SupplyBar:
    try:
        raw_date = str(row["date"])
        if len(raw_date) != 8:
            raise ValueError(f"expected an 8-digit YYYYMMDD date, got {raw_date!r}")
        return SupplyBar(
            trading_day=date(int(raw_date[0:4]), int(raw_date[4:6]), int(raw_date[6:8])),
            close=float(row["close"]),
            change_pct=float(row["diff"]),
            volume=float(row["volume"]),
            individual_net=float(row["tjj0008"]),
            foreign_net=float(row["tjj0016"]),
            institution_net=float(row["tjj0018"]),
        )
    except (KeyError, TypeError, ValueError, IndexError) as exc:
        raise RuntimeError(f"LS t1702 response row malformed: {row}") from exc


__all__ = ["LsSupplyProvider", "SupplyBar", "TR_CODE"]
