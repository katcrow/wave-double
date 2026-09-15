"""candidate_tags 테이블에 대한 저장소 adapter.

PostgREST REST 직접 접근으로 candidate_tags 행을 upsert한다.
attempt-scoped 테이블(candidates/candidate_source_contrib)과 동일한 패턴을 따른다.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date, datetime, timezone
from typing import Any, Protocol
from uuid import uuid4

import httpx


@dataclass(frozen=True)
class CandidateTag:
    """candidate_tags 테이블에 저장할 단일 태그 행."""

    candidate_id: str
    strategy: str  # "A" | "B" | "C" | "D" | "E" | "F" | "G" | "H"
    signal_date: date
    attempt_run_id: str
    params_meta: dict[str, Any] | None = None

    def as_db_row(self) -> dict[str, Any]:
        return {
            "tag_id": str(uuid4()),
            "candidate_id": self.candidate_id,
            "strategy": self.strategy,
            "signal_date": self.signal_date.isoformat(),
            "attempt_run_id": self.attempt_run_id,
            "tagged_at": datetime.now(timezone.utc).isoformat(),
            "status": "active",
            "params_meta": self.params_meta or {},
        }


class TagsRepositoryProtocol(Protocol):
    """``candidate_tags`` 저장소 의존성 프로토콜(``run_tags_stage``/``run_scheduled_batch``가 사용)."""

    def upsert_tags(self, tags: list[CandidateTag]) -> int: ...

    def sync_vanished(self, run_id: str) -> dict[str, Any]: ...


class SupabaseCandidateTagsRepository:
    """candidate_tags 테이블에 대한 PostgREST upsert adapter."""

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

    def __enter__(self) -> "SupabaseCandidateTagsRepository":
        return self

    def __exit__(self, *_: object) -> None:
        self.close()

    def upsert_tags(self, tags: list[CandidateTag]) -> int:
        """태그 목록을 idempotent upsert한다. 저장된 행 수를 반환한다."""
        if not tags:
            return 0
        payload = [tag.as_db_row() for tag in tags]
        response = self._http.post(
            f"{self._base_url}/rest/v1/candidate_tags",
            headers={**self._headers(), "Prefer": "resolution=merge-duplicates"},
            params={"on_conflict": "candidate_id,strategy,attempt_run_id"},
            json=payload,
            timeout=self._timeout,
        )
        response.raise_for_status()
        return len(payload)

    def sync_vanished(self, run_id: str) -> dict[str, Any]:
        """Story 2.8: ``sync_vanished_tags(p_run_id)`` RPC를 호출해 소멸 태그를 동기화한다.

        upsert_tags 성공 직후 호출되어야 한다(같은 attempt의 active 태그가 이미 저장된 상태를
        전제로 소멸 판정을 하기 때문). 반환값은 ``{"vanished_count": int}`` 형태의 RPC 응답이다.
        """
        response = self._http.post(
            f"{self._base_url}/rest/v1/rpc/sync_vanished_tags",
            headers=self._headers(),
            json={"p_run_id": run_id},
            timeout=self._timeout,
        )
        response.raise_for_status()
        data = response.json()
        return data if isinstance(data, dict) else {}

    def _headers(self) -> dict[str, str]:
        return {
            "content-type": "application/json",
            "apikey": self._key,
            "authorization": f"Bearer {self._key}",
        }


__all__ = ["CandidateTag", "TagsRepositoryProtocol", "SupabaseCandidateTagsRepository"]
