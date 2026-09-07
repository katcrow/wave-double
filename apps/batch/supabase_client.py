"""Supabase REST/RPC로 향하는 production adapter.

``ls_client.py``의 httpx 사용 패턴(명시적 http_client 주입, 구조화된 오류 반환)을
그대로 따른다. 이 모듈 밖으로는 httpx 예외를 노출하지 않는다.
"""

from __future__ import annotations

from datetime import date, time
from typing import Any

import httpx

from domain.calendar import CalendarDecision, TradingCalendarEntry


class SupabaseRpcClient:
    """``POST {url}/rest/v1/rpc/{fn}``으로 Supabase RPC를 호출하는 ``RpcClient``."""

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

    def __enter__(self) -> "SupabaseRpcClient":
        return self

    def __exit__(self, *_: object) -> None:
        self.close()

    def rpc(self, function: str, params: dict[str, Any]) -> dict[str, Any]:
        try:
            response = self._http.post(
                f"{self._base_url}/rest/v1/rpc/{function}",
                headers=self._headers(),
                json=params,
                timeout=self._timeout,
            )
        except httpx.HTTPError as exc:
            return {"error": {"code": "SUPABASE_TRANSPORT_ERROR", "message": str(exc), "retryable": True}}
        if response.status_code >= 400:
            return {"error": self._error_from_response(response)}
        try:
            data = response.json()
        except ValueError:
            return {"error": {"code": "INVALID_RESPONSE", "message": "Supabase RPC response was not valid JSON", "retryable": False}}
        return {"data": data}

    def _headers(self) -> dict[str, str]:
        return {
            "content-type": "application/json",
            "apikey": self._key,
            "authorization": f"Bearer {self._key}",
        }

    @staticmethod
    def _error_from_response(response: httpx.Response) -> dict[str, Any]:
        try:
            body = response.json()
        except ValueError:
            body = {}
        message = body.get("message") if isinstance(body, dict) else None
        if not message:
            message = f"Supabase RPC returned HTTP {response.status_code}"
        retryable = response.status_code == 429 or 500 <= response.status_code <= 599
        # Postgres 함수는 `raise exception using message = '<CODE>'`로 의미 있는 코드를 message에 싣는다.
        return {"code": message, "message": message, "retryable": retryable}


class SupabaseCalendarRepository:
    """``trading_calendar`` 테이블에 대한 ``GET``/``POST {url}/rest/v1/trading_calendar`` adapter."""

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

    def __enter__(self) -> "SupabaseCalendarRepository":
        return self

    def __exit__(self, *_: object) -> None:
        self.close()

    def get(self, trading_day: date) -> TradingCalendarEntry | None:
        response = self._http.get(
            f"{self._base_url}/rest/v1/trading_calendar",
            headers=self._headers(),
            params={
                "trading_day": f"eq.{trading_day.isoformat()}",
                "select": "trading_day,is_open,open_time,close_time",
                "limit": "1",
            },
            timeout=self._timeout,
        )
        response.raise_for_status()
        rows = response.json()
        if not isinstance(rows, list) or not rows:
            return None
        return self._entry_from_row(rows[0])

    def upsert(self, decision: CalendarDecision) -> None:
        entry = decision.entry
        if entry is None:
            raise ValueError("cannot upsert a calendar decision without an entry")
        row = {
            "trading_day": entry.trading_day.isoformat(),
            "is_open": entry.is_open,
            "open_time": entry.open_time.isoformat() if entry.open_time else None,
            "close_time": entry.close_time.isoformat() if entry.close_time else None,
        }
        response = self._http.post(
            f"{self._base_url}/rest/v1/trading_calendar",
            headers={**self._headers(), "Prefer": "resolution=merge-duplicates"},
            json=row,
            timeout=self._timeout,
        )
        response.raise_for_status()

    def recent_open_days(self, cutoff: date, count: int) -> list[date]:
        """Story 4.1: ``is_open=true and trading_day<=cutoff``인 최근 거래일 ``count``건을
        내림차순(최신일 먼저)으로 반환한다. supply stage가 D-2/D-1/D0 날짜를 확보하는 데 쓴다.
        """
        response = self._http.get(
            f"{self._base_url}/rest/v1/trading_calendar",
            headers=self._headers(),
            params={
                "is_open": "eq.true",
                "trading_day": f"lte.{cutoff.isoformat()}",
                "select": "trading_day",
                "order": "trading_day.desc",
                "limit": str(count),
            },
            timeout=self._timeout,
        )
        response.raise_for_status()
        rows = response.json()
        if not isinstance(rows, list):
            raise RuntimeError("Supabase trading_calendar response malformed: expected a list")
        return [date.fromisoformat(str(row["trading_day"])) for row in rows]

    def _headers(self) -> dict[str, str]:
        return {
            "content-type": "application/json",
            "apikey": self._key,
            "authorization": f"Bearer {self._key}",
        }

    @staticmethod
    def _entry_from_row(row: dict[str, Any]) -> TradingCalendarEntry:
        return TradingCalendarEntry(
            date.fromisoformat(row["trading_day"]),
            bool(row["is_open"]),
            time.fromisoformat(row["open_time"]) if row.get("open_time") else None,
            time.fromisoformat(row["close_time"]) if row.get("close_time") else None,
        )


__all__ = ["SupabaseCalendarRepository", "SupabaseRpcClient"]
