"""attempt 계보에 귀속된 ``market_supply`` 저장소 adapter."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime, timezone
from math import isfinite
from typing import Any, Protocol

import httpx

from .ls_market_macro_provider import MACRO_SYMBOLS
from .ls_market_supply_provider import MARKETS

_MACRO_SYMBOL_SET = frozenset(symbol for symbol, _ in MACRO_SYMBOLS)


@dataclass(frozen=True)
class MarketSupplyRow:
    attempt_run_id: str
    market: str
    trading_day: date
    foreign_net: float
    institution_net: float
    individual_net: float
    program_net: float
    # t1511 지수 등락률/종목수. 조회 실패 시 수급 행은 유지하고 None으로 저장한다.
    index_price: float | None = None
    index_change_rate: float | None = None
    advancing_count: int | None = None
    unchanged_count: int | None = None
    declining_count: int | None = None

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
        for field in ("index_price", "index_change_rate"):
            value = getattr(self, field)
            if value is not None and (
                isinstance(value, bool) or not isinstance(value, (int, float)) or not isfinite(float(value))
            ):
                raise ValueError(f"{field} must be a finite number")
        for field in ("advancing_count", "unchanged_count", "declining_count"):
            value = getattr(self, field)
            if value is not None and (isinstance(value, bool) or not isinstance(value, int) or value < 0):
                raise ValueError(f"{field} must be a non-negative integer")

    def as_db_row(self) -> dict[str, Any]:
        return {
            "attempt_run_id": self.attempt_run_id,
            "market": self.market,
            "trading_day": self.trading_day.isoformat(),
            "foreign_net": self.foreign_net,
            "institution_net": self.institution_net,
            "individual_net": self.individual_net,
            "program_net": self.program_net,
            "index_price": self.index_price,
            "index_change_rate": self.index_change_rate,
            "advancing_count": self.advancing_count,
            "unchanged_count": self.unchanged_count,
            "declining_count": self.declining_count,
            "collected_at": datetime.now(timezone.utc).isoformat(),
        }


@dataclass(frozen=True)
class MarketMacroRow:
    """t3521 매크로 시세(나스닥 선물·원/달러). 시장별이 아니라 attempt당 심볼별 1행이다."""

    attempt_run_id: str
    trading_day: date
    symbol: str
    price: float
    change: float
    change_rate: float
    quote_date: date | None

    def __post_init__(self) -> None:
        if not self.attempt_run_id:
            raise ValueError("attempt_run_id must be non-empty")
        if self.symbol not in _MACRO_SYMBOL_SET:
            raise ValueError(f"unsupported macro symbol: {self.symbol}")
        if type(self.trading_day) is not date:
            raise TypeError("trading_day must be a date")
        if self.quote_date is not None and type(self.quote_date) is not date:
            raise TypeError("quote_date must be a date or None")
        for field in ("price", "change", "change_rate"):
            value = getattr(self, field)
            if isinstance(value, bool) or not isinstance(value, (int, float)) or not isfinite(float(value)):
                raise ValueError(f"{field} must be a finite number")

    def as_db_row(self) -> dict[str, Any]:
        return {
            "attempt_run_id": self.attempt_run_id,
            "trading_day": self.trading_day.isoformat(),
            "symbol": self.symbol,
            "price": self.price,
            "change": self.change,
            "change_rate": self.change_rate,
            "quote_date": self.quote_date.isoformat() if self.quote_date else None,
            "collected_at": datetime.now(timezone.utc).isoformat(),
        }


class MarketSupplyRepositoryProtocol(Protocol):
    def upsert_rows(self, rows: list[MarketSupplyRow]) -> int: ...


class MarketMacroRepositoryProtocol(Protocol):
    def upsert_macro_rows(self, rows: list[MarketMacroRow]) -> int: ...


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

    def upsert_macro_rows(self, rows: list[MarketMacroRow]) -> int:
        if not rows:
            return 0
        payload = [row.as_db_row() for row in rows]
        response = self._http.post(
            f"{self._base_url}/rest/v1/market_macro",
            headers={**self._headers(), "Prefer": "resolution=merge-duplicates"},
            params={"on_conflict": "attempt_run_id,trading_day,symbol"},
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
    "MarketMacroRepositoryProtocol",
    "MarketMacroRow",
    "MarketSupplyRepositoryProtocol",
    "MarketSupplyRow",
    "SupabaseMarketSupplyRepository",
]
