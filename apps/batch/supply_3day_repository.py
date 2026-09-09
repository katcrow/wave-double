"""``supply_3day`` 테이블에 대한 저장소 adapter.

PostgREST REST 직접 접근으로 supply_3day 행을 upsert한다.
``candidate_tags_repository.py``와 동일한 패턴을 따른다.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime, timezone
import math
from typing import Any, Protocol

import httpx


@dataclass(frozen=True)
class SupplyRow:
    """``supply_3day`` 테이블에 저장할 단일 행."""

    candidate_id: str
    attempt_run_id: str
    trading_day: date
    slot: str  # "D-2" | "D-1" | "D0"
    close: float
    volume: float
    change_pct: float
    foreign_net: float | None
    institution_net: float | None
    individual_net: float | None
    program_net: float | None
    investor_net_status: str  # "confirmed" | "pending" | "missing"

    def __post_init__(self) -> None:
        if self.slot not in {"D-2", "D-1", "D0"}:
            raise ValueError(f"invalid supply slot: {self.slot}")
        if self.investor_net_status not in {"confirmed", "pending", "missing"}:
            raise ValueError(f"invalid investor_net_status: {self.investor_net_status}")
        for name in ("close", "volume", "change_pct"):
            value = getattr(self, name)
            if isinstance(value, bool) or not math.isfinite(value):
                raise ValueError(f"supply {name} must be finite")
        nets = (self.foreign_net, self.institution_net, self.individual_net, self.program_net)
        if any(value is not None and (isinstance(value, bool) or not math.isfinite(value)) for value in nets):
            raise ValueError("supply investor values must be finite or null")
        if self.investor_net_status != "confirmed" and any(value is not None for value in nets):
            raise ValueError("pending/missing supply rows must keep investor values null")

    def as_db_row(self) -> dict[str, Any]:
        return {
            "candidate_id": self.candidate_id,
            "attempt_run_id": self.attempt_run_id,
            "trading_day": self.trading_day.isoformat(),
            "slot": self.slot,
            "close": self.close,
            "volume": self.volume,
            "change_pct": self.change_pct,
            "foreign_net": self.foreign_net,
            "institution_net": self.institution_net,
            "individual_net": self.individual_net,
            "program_net": self.program_net,
            "investor_net_status": self.investor_net_status,
            "collected_at": datetime.now(timezone.utc).isoformat(),
        }


class Supply3DayRepositoryProtocol(Protocol):
    """``supply_3day`` 저장소 의존성 프로토콜(``run_supply_stage``/``run_scheduled_batch``가 사용)."""

    def upsert_rows(self, rows: list[SupplyRow]) -> int: ...


class SupabaseSupply3DayRepository:
    """supply_3day 테이블에 대한 PostgREST upsert adapter."""

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

    def __enter__(self) -> "SupabaseSupply3DayRepository":
        return self

    def __exit__(self, *_: object) -> None:
        self.close()

    def upsert_rows(self, rows: list[SupplyRow]) -> int:
        """행 목록을 idempotent upsert한다. 저장된 행 수를 반환한다."""
        if not rows:
            return 0
        payload = [row.as_db_row() for row in rows]
        response = self._http.post(
            f"{self._base_url}/rest/v1/supply_3day",
            headers={**self._headers(), "Prefer": "resolution=merge-duplicates"},
            params={"on_conflict": "candidate_id,trading_day,attempt_run_id"},
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


__all__ = ["SupplyRow", "Supply3DayRepositoryProtocol", "SupabaseSupply3DayRepository"]
