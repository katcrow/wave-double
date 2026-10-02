"""수급 수집 대상 후보를 조회하는 fetcher.

``candidate_tags``(``status='active'``)로 이번 attempt에 태깅된 ``candidate_id``
목록을 얻고 거래대금 상위 3개 후보와 대형주(``EXCLUDED_TOP_TICKERS``) 제외 후 상위
3개 후보를 추가해 ``candidates``에서 ticker를 조회한다. active 후보 수급 수집은 유지하면서
거래대금 상위 참고 영역('전체'/'제외' 두 모드)에 필요한 프로그램 수급도 태그 상태와
무관하게 수집한다.

실패를 흡수하지 않고 그대로 전파한다(``supply_stage``가 잡아 stage를 명시적으로
``failed``로 기록한다 -- ``candidate_fetcher.py``와 동일한 원칙, AD-5).
"""

from __future__ import annotations

from dataclasses import dataclass

import httpx

# 거래대금 상위 참고 영역의 기본 '제외' 모드에서 빼는 대형주(삼성전자, SK하이닉스).
# web의 apps/web/lib/top-trading-candidates.ts TOP_TRADING_EXCLUDED_TICKERS와 같은 값을 유지한다.
EXCLUDED_TOP_TICKERS: tuple[str, ...] = ("005930", "000660")
TOP_CANDIDATE_LIMIT = 3


@dataclass(frozen=True)
class TaggedCandidateRow:
    """supply stage에 전달할 최소한의 수급 대상 후보 행."""

    candidate_id: str
    ticker: str


class TaggedCandidateFetcher:
    """active 태그 후보, 거래대금 상위 3개, 대형주 제외 후 상위 3개 후보의 합집합을 조회한다."""

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
        """active 태그 후보, 거래대금 상위 3개, 대형주 제외 후 상위 3개 후보를 중복 없이 반환한다.

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

        active_candidate_ids = {str(row["candidate_id"]) for row in tag_rows}

        response = self._http.get(
            f"{self._base_url}/rest/v1/candidates",
            headers=self._headers(),
            params={
                "attempt_run_id": f"eq.{run_id}",
                "select": "candidate_id,ticker,trading_value",
                "order": "trading_value.desc,ticker.asc",
            },
            timeout=self._timeout,
        )
        response.raise_for_status()
        rows = response.json()
        if not isinstance(rows, list):
            raise RuntimeError("Supabase candidates response malformed: expected a list")
        if any(
            not isinstance(row, dict)
            or not row.get("candidate_id")
            or not row.get("ticker")
            for row in rows
        ):
            raise RuntimeError("Supabase candidates response malformed: invalid candidate row")
        top_candidate_ids = {str(row["candidate_id"]) for row in rows[:TOP_CANDIDATE_LIMIT]}
        excluded_top_candidate_ids = {
            str(row["candidate_id"])
            for row in [r for r in rows if str(r["ticker"]) not in EXCLUDED_TOP_TICKERS][:TOP_CANDIDATE_LIMIT]
        }
        selected_ids = active_candidate_ids | top_candidate_ids | excluded_top_candidate_ids
        return [
            TaggedCandidateRow(str(row["candidate_id"]), str(row["ticker"]))
            for row in rows
            if isinstance(row, dict) and str(row.get("candidate_id")) in selected_ids
        ]

    def _headers(self) -> dict[str, str]:
        return {
            "content-type": "application/json",
            "apikey": self._key,
            "authorization": f"Bearer {self._key}",
        }


__all__ = ["EXCLUDED_TOP_TICKERS", "TaggedCandidateRow", "TaggedCandidateFetcher"]
