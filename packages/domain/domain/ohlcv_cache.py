"""일봉 캐시 조회/적재 상태의 순수 계약.

외부 API·저장소를 알지 않는다. ``domain/calendar.py``·``domain/run_state.py``와
동일하게 I/O 없는 상태 어휘만 제공한다.
"""

from enum import StrEnum


class OhlcvCacheStatus(StrEnum):
    READY = "READY"
    INELIGIBLE_INSUFFICIENT_HISTORY = "INELIGIBLE_INSUFFICIENT_HISTORY"
    ERROR = "ERROR"


# 전략 B 주봉 %K(20-3) 요구를 충족하는 최소 보유 거래일 수.
MIN_HISTORY_TRADING_DAYS = 120


__all__ = ["OhlcvCacheStatus", "MIN_HISTORY_TRADING_DAYS"]
