"""daily_ohlcv → pandas DataFrame 로더.

tags_stage가 ``compute_abc``를 호출하기 위해 Supabase ``daily_ohlcv`` 테이블에서
종목별 일봉 데이터를 읽어 ``strategy_api.compute_abc``가 기대하는 DataFrame 포맷으로
변환한다.

look-ahead 방지: 조회는 항상 ``trading_day<=cutoff``로 제한한다(cutoff는 태깅
대상 거래일). 필터 없이 전체 이력을 읽으면 미래 거래일 데이터가 신호 계산에
유입될 수 있다(story 2.5 Always 규칙).
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from typing import Any, Protocol

import httpx
import pandas as pd

from domain.ohlcv_cache import MIN_HISTORY_TRADING_DAYS, OhlcvCacheStatus

_OHLCV_COLS = ("Open", "High", "Low", "Close", "Volume")
_DB_TO_DF_RENAME = {
    "open": "Open",
    "high": "High",
    "low": "Low",
    "close": "Close",
    "volume": "Volume",
}


class OhlcvDbClient(Protocol):
    """daily_ohlcv 테이블에서 종목별 일봉을 조회하는 프로토콜."""

    def load_ohlcv(self, ticker: str, cutoff: date) -> pd.DataFrame | OhlcvCacheStatus: ...


@dataclass(frozen=True)
class LoadResult:
    """종목별 OHLCV 로딩 결과."""

    ticker: str
    status: OhlcvCacheStatus
    frame: pd.DataFrame | None = None
    trading_days: int = 0


class SupabaseOhlcvCacheLoader:
    """PostgREST를 통해 ``daily_ohlcv``에서 종목별 일봉을 읽어 DataFrame으로 반환한다.

    ``strategy_api.compute_abc``는 ``(Open, High, Low, Close, Volume)`` 컬럼과
    ``MIN_HISTORY_TRADING_DAYS`` 행 이상의 DataFrame을 기대한다. ``trading_day ASC``로
    정렬해 가장 최신 행이 마지막 인덱스에 오도록 하며, ``trading_day``는 DataFrame의
    ``DatetimeIndex``로 보존한다(태깅된 시그널의 거래일 역추적에 사용, 골든 픽스처와
    동일한 인덱싱 관례).
    """

    _DB_COLS = "trading_day,open,high,low,close,volume"

    def __init__(
        self,
        base_url: str,
        service_role_key: str,
        *,
        http_client: httpx.Client | None = None,
        timeout: float = 30.0,
    ) -> None:
        if not base_url or not service_role_key:
            raise ValueError("base_url and service_role_key must be non-empty")
        self._base_url = base_url.rstrip("/")
        self._key = service_role_key
        self._http = http_client or httpx.Client()
        self._timeout = timeout

    def close(self) -> None:
        self._http.close()

    def __enter__(self) -> "SupabaseOhlcvCacheLoader":
        return self

    def __exit__(self, *_: object) -> None:
        self.close()

    def load_ohlcv(self, ticker: str, cutoff: date) -> pd.DataFrame | OhlcvCacheStatus:
        """종목의 캐시된 일봉을 ``trading_day<=cutoff`` 범위로 DataFrame 로드한다.

        이력이 없으면 ``INELIGIBLE_INSUFFICIENT_HISTORY``를 반환한다.
        API 호출 실패는 ``ERROR``로 반환한다(재시도 가능한 stage error).
        """
        if not ticker or not ticker.isalnum():
            return OhlcvCacheStatus.ERROR
        try:
            response = self._http.get(
                f"{self._base_url}/rest/v1/daily_ohlcv",
                headers=self._headers(),
                params={
                    "ticker": f"eq.{ticker}",
                    "trading_day": f"lte.{cutoff.isoformat()}",
                    "select": self._DB_COLS,
                    "order": "trading_day.asc",
                },
                timeout=self._timeout,
            )
            response.raise_for_status()
            rows = response.json()

            if not isinstance(rows, list) or len(rows) == 0:
                return OhlcvCacheStatus.INELIGIBLE_INSUFFICIENT_HISTORY

            df = pd.DataFrame(rows)
            df["trading_day"] = pd.to_datetime(df["trading_day"])
            df = df.set_index("trading_day").rename(columns=_DB_TO_DF_RENAME)
            df = df[[_OHLCV_COLS[0], _OHLCV_COLS[1], _OHLCV_COLS[2], _OHLCV_COLS[3], _OHLCV_COLS[4]]]

            for col in _OHLCV_COLS:
                df[col] = pd.to_numeric(df[col], errors="coerce")
        except Exception:
            return OhlcvCacheStatus.ERROR

        return df

    def load_batch(self, tickers: list[str], cutoff: date) -> dict[str, LoadResult]:
        """여러 종목의 OHLCV를 순차 로드한다.

        한 종목의 실패가 나머지 종목 처리를 막지 않는다(부분 성공 허용).
        """
        results: dict[str, LoadResult] = {}
        for ticker in dict.fromkeys(tickers):  # dedupe preserving order
            frame_or_status = self.load_ohlcv(ticker, cutoff)
            if isinstance(frame_or_status, pd.DataFrame):
                if len(frame_or_status) < MIN_HISTORY_TRADING_DAYS:
                    results[ticker] = LoadResult(
                        ticker, OhlcvCacheStatus.INELIGIBLE_INSUFFICIENT_HISTORY, None, len(frame_or_status)
                    )
                else:
                    results[ticker] = LoadResult(ticker, OhlcvCacheStatus.READY, frame_or_status, len(frame_or_status))
            else:
                results[ticker] = LoadResult(ticker, frame_or_status)
        return results

    def _headers(self) -> dict[str, str]:
        return {
            "content-type": "application/json",
            "apikey": self._key,
            "authorization": f"Bearer {self._key}",
        }


__all__ = ["OhlcvDbClient", "LoadResult", "SupabaseOhlcvCacheLoader"]
