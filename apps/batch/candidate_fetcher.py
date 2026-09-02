"""DB에서 후보 목록을 조회하는 가벼운 fetcher.

tags_stage가 ``compute_abc``를 호출하기 위해 ``candidates`` 테이블에서
``attempt_run_id``로 ``candidate_id`` + ``ticker``를 재조회한다.

실패(HTTP 오류, malformed 응답)를 절대 흡수하지 않고 그대로 전파한다 -- 호출자인
``tags_stage``가 이를 잡아 stage를 명시적으로 ``failed``로 기록한다. 후보 조회
자체의 실패를 조용한 "빈 성공"(``except Exception: return []``)으로 만들지
않기 위함이다(AD-5, story 2.5 Never 규칙).
"""

from __future__ import annotations

from dataclasses import dataclass
from typing import Any

import httpx


@dataclass(frozen=True)
class CandidateRow:
    """tags_stage에 전달할 최소한의 후보 행."""

    candidate_id: str
    ticker: str
    name: str | None = None


class CandidateFetcher:
    """``candidates`` 테이블에서 ``attempt_run_id``별 후보 목록을 조회한다."""

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

    def __enter__(self) -> "CandidateFetcher":
        return self

    def __exit__(self, *_: object) -> None:
        self.close()

    def fetch(self, run_id: str) -> list[CandidateRow]:
        """``run_id``(attempt)에 해당하는 후보 목록을 반환한다.

        실패 시 예외를 그대로 전파한다(흡수하지 않음).
        """
        response = self._http.get(
            f"{self._base_url}/rest/v1/candidates",
            headers=self._headers(),
            params={
                "attempt_run_id": f"eq.{run_id}",
                "select": "candidate_id,ticker,name",
                "order": "trading_value.desc,ticker.asc",
            },
            timeout=self._timeout,
        )
        response.raise_for_status()
        rows = response.json()
        if not isinstance(rows, list):
            raise RuntimeError("Supabase candidates response malformed: expected a list")
        return [
            CandidateRow(str(row["candidate_id"]), str(row["ticker"]), row.get("name"))
            for row in rows
        ]

    def _headers(self) -> dict[str, str]:
        return {
            "content-type": "application/json",
            "apikey": self._key,
            "authorization": f"Bearer {self._key}",
        }


__all__ = ["CandidateRow", "CandidateFetcher"]
