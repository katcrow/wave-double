"""신규 편입 종목의 일봉 이력 초기 적재.

이미 ``daily_ohlcv``에 이력이 있는 티커는 이번 스토리 범위 밖(Story 2.2 증분 갱신)이므로
LS를 호출하지 않는다. ``ls_daily_bar.py``의 단일 콜 요청 구성 스타일과
``supabase_client.py``의 service-role REST 직접 upsert 패턴을 그대로 재사용한다.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from typing import Any, Protocol

import httpx

from domain.ohlcv_cache import MIN_HISTORY_TRADING_DAYS, OhlcvCacheStatus

from .ls_client import LsResponse

TR_CODE = "t8410"
QRYCNT = 120


class OhlcvClient(Protocol):
    def request(self, tr_code: str, params: dict[str, Any]) -> LsResponse: ...


@dataclass(frozen=True)
class OhlcvCacheResult:
    ticker: str
    status: OhlcvCacheStatus
    trading_days: int
    message: str = ""


class LsOhlcvCacheProvider:
    """``t8410``(qrycnt=120) 단일 콜로 한 종목의 전체 이력을 조회한다."""

    def __init__(self, client: OhlcvClient) -> None:
        self._client = client

    def fetch_full_history(self, ticker: str, cutoff: date) -> list[dict[str, Any]]:
        response = self._client.request(
            TR_CODE,
            {
                "t8410InBlock": {
                    "shcode": ticker,
                    "gubun": "2",
                    "qrycnt": QRYCNT,
                    "sdate": "",
                    "edate": cutoff.strftime("%Y%m%d"),
                    "cts_date": "",
                    "comp_yn": "N",
                    "sujung": "Y",
                }
            },
        )
        if not response.ok:
            raise RuntimeError(
                f"LS daily bar history fetch failed: {response.result_code} {response.message}".rstrip()
            )
        return [_normalize_row(row) for row in _rows(response.data)]


def _rows(data: Any) -> list[dict[str, Any]]:
    if isinstance(data, dict):
        rows = data.get("t8410OutBlock1")
        if isinstance(rows, list):
            return rows
    raise RuntimeError("LS daily bar response malformed: missing/non-list t8410OutBlock1")


def _normalize_row(row: dict[str, Any]) -> dict[str, Any]:
    try:
        raw_date = str(row["date"])
        trading_day = date.fromisoformat(f"{raw_date[:4]}-{raw_date[4:6]}-{raw_date[6:8]}")
    except (KeyError, TypeError, ValueError) as exc:
        raise RuntimeError(f"LS daily bar response malformed: invalid date in row {row!r}") from exc
    return {
        "trading_day": trading_day,
        "open": row.get("open"),
        "high": row.get("high"),
        "low": row.get("low"),
        "close": row.get("close"),
        "volume": row.get("jdiff_vol"),
    }


class SupabaseOhlcvCacheRepository:
    """``daily_ohlcv`` 테이블에 대한 ``GET``/``POST {url}/rest/v1/daily_ohlcv`` adapter.

    ``SupabaseCalendarRepository``와 동일하게 attempt-scoped가 아닌 테이블에 대한
    service-role REST 직접 접근만 쓴다.
    """

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

    def __enter__(self) -> "SupabaseOhlcvCacheRepository":
        return self

    def __exit__(self, *_: object) -> None:
        self.close()

    def existing_tickers(self, tickers: list[str]) -> set[str]:
        if not tickers:
            return set()
        for ticker in tickers:
            if not ticker.isalnum():
                raise ValueError(f"invalid ticker for PostgREST in.() filter: {ticker!r}")
        response = self._http.get(
            f"{self._base_url}/rest/v1/daily_ohlcv",
            headers=self._headers(),
            params={
                "ticker": f"in.({','.join(tickers)})",
                "select": "ticker",
            },
            timeout=self._timeout,
        )
        response.raise_for_status()
        rows = response.json()
        if not isinstance(rows, list):
            raise RuntimeError("Supabase daily_ohlcv response malformed: expected a list")
        return {row["ticker"] for row in rows}

    def upsert_rows(self, ticker: str, rows: list[dict[str, Any]]) -> None:
        payload = [
            {
                "ticker": ticker,
                "trading_day": row["trading_day"].isoformat() if hasattr(row["trading_day"], "isoformat") else row["trading_day"],
                "open": row["open"],
                "high": row["high"],
                "low": row["low"],
                "close": row["close"],
                "volume": row["volume"],
                "adjusted": True,
                "adjustment_version": 1,
                "pricechk": None,
            }
            for row in rows
        ]
        response = self._http.post(
            f"{self._base_url}/rest/v1/daily_ohlcv",
            headers={**self._headers(), "Prefer": "resolution=merge-duplicates"},
            params={"on_conflict": "ticker,trading_day"},
            json=payload,
            timeout=self._timeout,
        )
        response.raise_for_status()

    def _headers(self) -> dict[str, str]:
        return {
            "content-type": "application/json",
            "apikey": self._key,
            "authorization": f"Bearer {self._key}",
        }


def initialize_new_ticker_history(
    candidates: list[str],
    provider: LsOhlcvCacheProvider,
    repository: SupabaseOhlcvCacheRepository,
    cutoff: date,
) -> dict[str, OhlcvCacheResult]:
    """이미 이력이 있는 티커는 건너뛰고, 신규 편입 종목만 전체 이력을 적재한다.

    한 종목의 실패가 나머지 종목 처리를 막지 않는다(부분 성공 허용). 신규 티커 호출은
    순차 실행이며, ``LsClient``의 TR별 token bucket이 이미 1건/초를 강제하므로
    별도의 처리량 제한 로직을 추가하지 않는다(NFR-3).
    """
    deduped_candidates = list(dict.fromkeys(candidates))

    try:
        existing = repository.existing_tickers(deduped_candidates)
    except Exception as exc:
        return {
            ticker: OhlcvCacheResult(ticker, OhlcvCacheStatus.ERROR, 0, str(exc))
            for ticker in deduped_candidates
        }

    new_tickers = [ticker for ticker in deduped_candidates if ticker not in existing]

    results: dict[str, OhlcvCacheResult] = {}
    for ticker in new_tickers:
        try:
            rows = provider.fetch_full_history(ticker, cutoff)
        except Exception as exc:
            results[ticker] = OhlcvCacheResult(ticker, OhlcvCacheStatus.ERROR, 0, str(exc))
            continue

        if len(rows) < MIN_HISTORY_TRADING_DAYS:
            results[ticker] = OhlcvCacheResult(
                ticker, OhlcvCacheStatus.INELIGIBLE_INSUFFICIENT_HISTORY, len(rows)
            )
            continue

        try:
            repository.upsert_rows(ticker, rows)
        except Exception as exc:
            results[ticker] = OhlcvCacheResult(ticker, OhlcvCacheStatus.ERROR, len(rows), str(exc))
            continue

        results[ticker] = OhlcvCacheResult(ticker, OhlcvCacheStatus.READY, len(rows))

    return results


__all__ = [
    "LsOhlcvCacheProvider",
    "SupabaseOhlcvCacheRepository",
    "OhlcvCacheResult",
    "initialize_new_ticker_history",
]
