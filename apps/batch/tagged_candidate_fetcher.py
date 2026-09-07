"""Story 4.1: 태깅된(active) 후보만 조회하는 fetcher.

``candidate_tags``(``status='active'``)로 이번 attempt에 태깅된 ``candidate_id``
목록을 얻은 뒤, ``candidates`` 테이블에서 ``ticker``를 재조회한다. 전체 후보를
반환하는 ``CandidateFetcher``와 구분되는, supply stage 전용 조회다(story 4.1 AC1:
"태깅된" 후보만 대상).

실패를 흡수하지 않고 그대로 전파한다(``supply_stage``가 잡아 stage를 명시적으로
``failed``로 기록한다 -- ``candidate_fetcher.py``와 동일한 원칙, AD-5).
"""

from __future__ import annotations

from dataclasses import dataclass

import httpx


@dataclass(frozen=True)
class TaggedCandidateRow:
    """supply stage에 전달할 최소한의 태깅된 후보 행."""

    candidate_id: str
    ticker: str


class TaggedCandidateFetcher:
    """``candidate_tags``(active) → ``candidates`` 순서로 태깅된 후보를 조회한다."""

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

    def __enter__(self) -> "TaggedCandidateFetcher":
        return self

    def __exit__(self, *_: object) -> None:
        self.close()

    def fetch(self, run_id: str) -> list[TaggedCandidateRow]:
        """``run_id``(attempt)에서 ``status='active'``인 태그를 가진 후보 목록을 반환한다.

        실패 시 예외를 그대로 전파한다(흡수하지 않음).
        """
        tag_response = self._http.get(
            f"{self._base_url}/rest/v1/candidate_tags",
            headers=self._headers(),
            params={
                "attempt_run_id": f"eq.{run_id}",
                "status": "eq.active",
                "select": "candidate_id",
            },
            timeout=self._timeout,
        )
        tag_response.raise_for_status()
        tag_rows = tag_response.json()
        if not isinstance(tag_rows, list):
            raise RuntimeError("Supabase candidate_tags response malformed: expected a list")

        candidate_ids = sorted({str(row["candidate_id"]) for row in tag_rows})
        if not candidate_ids:
            return []

        response = self._http.get(
            f"{self._base_url}/rest/v1/candidates",
            headers=self._headers(),
            params={
                "candidate_id": f"in.({','.join(candidate_ids)})",
                "attempt_run_id": f"eq.{run_id}",
                "select": "candidate_id,ticker",
            },
            timeout=self._timeout,
        )
        response.raise_for_status()
        rows = response.json()
        if not isinstance(rows, list):
            raise RuntimeError("Supabase candidates response malformed: expected a list")
        return [TaggedCandidateRow(str(row["candidate_id"]), str(row["ticker"])) for row in rows]

    def _headers(self) -> dict[str, str]:
        return {
            "content-type": "application/json",
            "apikey": self._key,
            "authorization": f"Bearer {self._key}",
        }


__all__ = ["TaggedCandidateRow", "TaggedCandidateFetcher"]
