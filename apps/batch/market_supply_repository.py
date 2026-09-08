"""attempt 계보에 귀속된 ``market_supply`` 저장소 adapter."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime, timezone
from math import isfinite
from typing import Any, Protocol

import httpx

from .ls_market_supply_provider import MARKETS


@dataclass(frozen=True)
class MarketSupplyRow:
    attempt_run_id: str
    market: str
    trading_day: date
    foreign_net: float
    institution_net: float
    individual_net: float
    program_net: float

    def __post_init__(self) -> None:
        if not self.attempt_run_id:
            raise ValueError("attempt_run_id must be non-empty")
        if self.market not in MARKETS:
            raise ValueError(f"unsupported market: {self.market}")
        if type(self.trading_day) is not date:
            raise TypeError("trading_day must be a date")
        for field in ("foreign_net", "institution_net", "individual_net", "program_net"):
            value = getattr(self, field)
            if isinstance(value, bool) or not isinstance(value, (int, float)) or not isfinite(float(value)):
                raise ValueError(f"{field} must be a finite number")

    def as_db_row(self) -> dict[str, Any]:
        return {
            "attempt_run_id": self.attempt_run_id,
            "market": self.market,
            "trading_day": self.trading_day.isoformat(),
            "foreign_net": self.foreign_net,
            "institution_net": self.institution_net,
            "individual_net": self.individual_net,
            "program_net": self.program_net,
            "collected_at": datetime.now(timezone.utc).isoformat(),
        }


class MarketSupplyRepositoryProtocol(Protocol):
    def upsert_rows(self, rows: list[MarketSupplyRow]) -> int: ...


class SupabaseMarketSupplyRepository:
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

    def __enter__(self) -> "SupabaseMarketSupplyRepository":
        return self

    def __exit__(self, *_: object) -> None:
        self.close()

    def upsert_rows(self, rows: list[MarketSupplyRow]) -> int:
        if not rows:
            return 0
        payload = [row.as_db_row() for row in rows]
        response = self._http.post(
            f"{self._base_url}/rest/v1/market_supply",
            headers={**self._headers(), "Prefer": "resolution=merge-duplicates"},
            params={"on_conflict": "attempt_run_id,market,trading_day"},
            json=payload,
            timeout=self._timeout,
        )
        response.raise_for_status()
        return len(payload)

    def _headers(self) -> dict[str, str]:
        return {
            "content-type": "application/json",
            "apikey": self._key,
            "authorization": f"Bearer {self._key}",
        }


__all__ = [
    "MarketSupplyRepositoryProtocol",
    "MarketSupplyRow",
    "SupabaseMarketSupplyRepository",
]
