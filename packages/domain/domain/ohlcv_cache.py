"""일봉 캐시 조회/적재 상태의 순수 계약.

외부 API·저장소를 알지 않는다. ``domain/calendar.py``·``domain/run_state.py``와
동일하게 I/O 없는 상태 어휘만 제공한다.
"""

from dataclasses import dataclass
from datetime import date
from enum import StrEnum


class OhlcvCacheStatus(StrEnum):
    READY = "READY"
    INELIGIBLE_INSUFFICIENT_HISTORY = "INELIGIBLE_INSUFFICIENT_HISTORY"
    ERROR = "ERROR"


# 전략 B 주봉 %K(20-3) 요구를 충족하는 최소 보유 거래일 수.
MIN_HISTORY_TRADING_DAYS = 120


@dataclass(frozen=True)
class AdjustmentFlag:
    """증분 갱신 중 관측된 조정 신호(Story 2.2가 관측, Story 3.5가 소비하는 원시 입력).

    ``pricechk``가 관측되었거나(수정주가 반영), 전일 종가 대비 ``gap_pct``가
    ±30%를 초과한 거래일에 대해 발행된다. I/O 없는 순수 계약이며, 이 신호를
    소비해 SUSPENDED 전이를 판정하는 로직 자체는 Story 3.5의 범위다.
    """

    ticker: str
    trading_day: date
    pricechk: bool
    gap_pct: float


__all__ = ["OhlcvCacheStatus", "MIN_HISTORY_TRADING_DAYS", "AdjustmentFlag"]
