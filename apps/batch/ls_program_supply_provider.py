"""Story 4.2: 종목별 프로그램 순매수(t1637) adapter."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from math import isfinite
from typing import Any, Protocol

from .ls_client import LsResponse

TR_CODE = "t1637"


class ProgramSupplyClient(Protocol):
    def request(self, tr_code: str, params: dict[str, Any]) -> LsResponse: ...


@dataclass(frozen=True)
class ProgramSupplyBar:
    """``t1637OutBlock1``의 일자별 프로그램 순매수 행."""

    trading_day: date
    program_net: float


class LsProgramSupplyProvider:
    """``t1637`` 일자별 수량 조회로 종목의 프로그램 순매수를 반환한다.

    t1637은 날짜 범위를 직접 받지 않고 일자 cursor를 사용하므로 최초 응답을
    한 번만 조회한 뒤 ``fromdt``/``todt`` 범위의 행만 반환한다. 날짜와 순매수
    수량은 엄격하게 파싱하며, 응답 순서나 ``time``에는 의존하지 않는다.
    """

    def __init__(self, client: ProgramSupplyClient) -> None:
        self._client = client

    def fetch(self, ticker: str, fromdt: date, todt: date) -> list[ProgramSupplyBar]:
        if fromdt > todt:
            raise ValueError("fromdt must not be later than todt")

        response = self._client.request(
            TR_CODE,
            {
                "t1637InBlock": {
                    "gubun1": "0",
                    "gubun2": "1",
                    "shcode": ticker,
                    "date": "",
                    "time": "",
                    "cts_idx": 0,
                    "exchgubun": "U",
                }
            },
        )
        if not response.ok:
            raise RuntimeError(f"LS t1637 lookup failed: {response.result_code}")

        bars = [_parse_row(row) for row in _rows(response.data)]
        return [bar for bar in bars if fromdt <= bar.trading_day <= todt]


def _rows(data: Any) -> list[dict[str, Any]]:
    if not isinstance(data, dict):
        raise RuntimeError("LS t1637 response malformed: expected an object")
    rows = data.get("t1637OutBlock1")
    if not isinstance(rows, list):
        raise RuntimeError("LS t1637 response malformed: missing/non-list t1637OutBlock1")
    if any(not isinstance(row, dict) for row in rows):
        raise RuntimeError("LS t1637 response malformed: t1637OutBlock1 contains non-object row")
    return rows


def _parse_row(row: dict[str, Any]) -> ProgramSupplyBar:
    try:
        raw_date = row["date"]
        if not isinstance(raw_date, str) or len(raw_date) != 8 or not raw_date.isdigit():
            raise ValueError(f"expected an 8-digit YYYYMMDD date, got {raw_date!r}")
        trading_day = date(int(raw_date[0:4]), int(raw_date[4:6]), int(raw_date[6:8]))
        return ProgramSupplyBar(
            trading_day=trading_day,
            program_net=_finite_number(row["svolume"], "svolume"),
        )
    except (KeyError, TypeError, ValueError, IndexError, OverflowError) as exc:
        raise RuntimeError(f"LS t1637 response row malformed: {row}") from exc


def _finite_number(value: Any, field: str) -> float:
    if isinstance(value, bool) or value is None:
        raise ValueError(f"{field} must be a finite number")
    parsed = float(value)
    if not isfinite(parsed):
        raise ValueError(f"{field} must be a finite number")
    return parsed


__all__ = ["LsProgramSupplyProvider", "ProgramSupplyBar", "TR_CODE"]
