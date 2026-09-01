"""캘린더 판정용 기준 종목 일봉 조회 adapter (t8410)."""

from __future__ import annotations

from datetime import date
from typing import Any, Protocol

from .ls_client import LsResponse

TR_CODE = "t8410"
# 삼성전자(005930): 캘린더 판정 목적일 뿐 후보 모집단과 무관. 유동성이 가장 높아
# 상장폐지·거래정지로 인한 오판 위험이 최소인 종목을 선택했다.
REFERENCE_TICKER = "005930"


class DailyBarClient(Protocol):
    def request(self, tr_code: str, params: dict[str, Any]) -> LsResponse: ...


class LsDailyBarProvider:
    """``t8410``(일주월년 차트) 조회로 특정 거래일의 개장 여부를 판정한다."""

    def __init__(self, client: DailyBarClient, *, ticker: str = REFERENCE_TICKER) -> None:
        self._client = client
        self._ticker = ticker

    def has_daily_bar(self, trading_day: date) -> bool:
        target = trading_day.strftime("%Y%m%d")
        response = self._client.request(
            TR_CODE,
            {
                "t8410InBlock": {
                    "shcode": self._ticker,
                    "gubun": "2",
                    "qrycnt": 1,
                    "sdate": target,
                    "edate": target,
                    "cts_date": "",
                    "comp_yn": "N",
                    "sujung": "Y",
                }
            },
        )
        if not response.ok:
            raise RuntimeError(f"LS daily bar lookup failed: {response.result_code}")
        return any(str(row.get("date")) == target for row in _rows(response.data))


def _rows(data: Any) -> list[dict[str, Any]]:
    if isinstance(data, dict):
        rows = data.get("t8410OutBlock1")
        if isinstance(rows, list):
            return rows
    raise RuntimeError("LS daily bar response malformed: missing/non-list t8410OutBlock1")


__all__ = ["LsDailyBarProvider", "REFERENCE_TICKER"]
