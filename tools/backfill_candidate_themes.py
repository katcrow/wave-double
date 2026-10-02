"""현재 발행 스냅샷의 후보별 LS t1532 테마를 candidate_themes에 채운다.

운영 배치가 새 후보를 저장하기 전의 기존 발행 스냅샷을 보완하기 위한 일회성/재실행
가능한 도구다. LS 조회 실패 후보의 기존 테마는 보존하고, 빈 응답 후보만 비운다.
"""

from __future__ import annotations

import argparse
import os
import sys
from pathlib import Path
from typing import Any

sys.path.insert(0, str(Path(__file__).resolve().parents[1]))

import httpx

from apps.batch.ls_auth import LsOAuthTokenProvider
from apps.batch.ls_client import LsClient, LsClientConfig
from apps.batch.theme_enrichment import enrich_candidate_themes


def _required(name: str, *fallbacks: str) -> str:
    for candidate in (name, *fallbacks):
        value = os.environ.get(candidate)
        if value:
            return value
    raise SystemExit(f"missing required environment variable: {name}")


def _headers(key: str) -> dict[str, str]:
    return {"apikey": key, "authorization": f"Bearer {key}"}


def _request_json(client: httpx.Client, method: str, url: str, *, key: str, headers: dict[str, str] | None = None, **kwargs: Any) -> Any:
    response = client.request(
        method,
        url,
        headers={**_headers(key), "content-type": "application/json", **(headers or {})},
        **kwargs,
    )
    if response.status_code >= 400:
        raise RuntimeError(f"Supabase REST returned HTTP {response.status_code}")
    if not response.content:
        return None
    return response.json()


def _snapshot_run_id(client: httpx.Client, base_url: str, key: str) -> str:
    snapshot = _request_json(client, "POST", f"{base_url}/rest/v1/rpc/get_dashboard_snapshot", key=key, json={})
    complete = snapshot.get("complete_snapshot") if isinstance(snapshot, dict) else None
    run_id = complete.get("run_id") if isinstance(complete, dict) else None
    if not isinstance(run_id, str) or not run_id:
        raise RuntimeError("published complete snapshot is unavailable")
    return run_id


def _assert_current_complete_run(client: httpx.Client, base_url: str, key: str, run_id: str) -> None:
    runs = _request_json(
        client,
        "GET",
        f"{base_url}/rest/v1/runs",
        key=key,
        params={"run_id": f"eq.{run_id}", "status": "eq.published", "select": "run_id,logical_run_key"},
    )
    if not isinstance(runs, list) or len(runs) != 1 or not isinstance(runs[0], dict):
        raise RuntimeError("run_id must identify a published run")
    logical_run_key = runs[0].get("logical_run_key")
    if not isinstance(logical_run_key, str):
        raise RuntimeError("published run lineage is unavailable")
    pointers = _request_json(
        client,
        "GET",
        f"{base_url}/rest/v1/logical_runs",
        key=key,
        params={
            "logical_run_key": f"eq.{logical_run_key}",
            "current_complete_run_id": f"eq.{run_id}",
            "select": "logical_run_key",
        },
    )
    if not isinstance(pointers, list) or len(pointers) != 1:
        raise RuntimeError("run_id must be the current complete published snapshot")


def _load_candidates(client: httpx.Client, base_url: str, key: str, run_id: str) -> list[dict[str, str]]:
    rows = _request_json(
        client,
        "GET",
        f"{base_url}/rest/v1/candidates",
        key=key,
        params={
            "attempt_run_id": f"eq.{run_id}",
            "select": "candidate_id,ticker",
            "order": "ticker.asc",
        },
    )
    if not isinstance(rows, list):
        raise RuntimeError("candidate REST response was not an array")
    candidates: list[dict[str, str]] = []
    for row in rows:
        if not isinstance(row, dict) or not isinstance(row.get("candidate_id"), str) or not isinstance(row.get("ticker"), str):
            raise RuntimeError("candidate REST response contained a malformed row")
        candidates.append({"candidate_id": row["candidate_id"], "ticker": row["ticker"]})
    return candidates


def _load_existing_theme_candidate_ids(client: httpx.Client, base_url: str, key: str, run_id: str) -> set[str]:
    rows = _request_json(
        client,
        "GET",
        f"{base_url}/rest/v1/candidate_themes",
        key=key,
        params={"attempt_run_id": f"eq.{run_id}", "select": "candidate_id"},
    )
    if not isinstance(rows, list):
        raise RuntimeError("theme REST response was not an array")
    candidate_ids: set[str] = set()
    for row in rows:
        if not isinstance(row, dict) or not isinstance(row.get("candidate_id"), str):
            raise RuntimeError("theme REST response contained a malformed row")
        candidate_ids.add(row["candidate_id"])
    return candidate_ids


def _insert_themes(client: httpx.Client, base_url: str, key: str, run_id: str, candidate_id: str, themes: list[dict[str, Any]]) -> None:
    if not themes:
        return
    payload = [
        {"candidate_id": candidate_id, "attempt_run_id": run_id, **theme}
        for theme in themes
    ]
    _request_json(
        client,
        "POST",
        f"{base_url}/rest/v1/candidate_themes",
        key=key,
        params={"on_conflict": "candidate_id,attempt_run_id,theme_code"},
        headers={"Prefer": "resolution=ignore-duplicates,return=minimal"},
        json=payload,
    )


def _parse_args(argv: list[str] | None = None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--run-id", help="대상 complete snapshot run_id. 생략하면 현재 발행 스냅샷을 사용한다.")
    return parser.parse_args(argv)


def run(argv: list[str] | None = None) -> int:
    args = _parse_args(argv)
    base_url = _required("SUPABASE_URL").rstrip("/")
    supabase_key = _required("SUPABASE_SERVICE_ROLE_KEY")
    ls_key = _required("LS_APP_KEY", "LS_OPEN_API_APP_KEY")
    ls_secret = _required("LS_APP_SECRET", "LS_OPEN_API_APP_SECRET")

    with httpx.Client(timeout=30.0) as supabase, LsOAuthTokenProvider(ls_key, ls_secret) as token_provider, LsClient(
        token_provider, config=LsClientConfig()
    ) as ls_client:
        run_id = args.run_id or _snapshot_run_id(supabase, base_url, supabase_key)
        _assert_current_complete_run(supabase, base_url, supabase_key, run_id)
        candidates = _load_candidates(supabase, base_url, supabase_key, run_id)
        existing_candidate_ids = _load_existing_theme_candidate_ids(supabase, base_url, supabase_key, run_id)
        pending_candidates = [candidate for candidate in candidates if candidate["candidate_id"] not in existing_candidate_ids]
        result = enrich_candidate_themes([candidate["ticker"] for candidate in pending_candidates], ls_client)

        candidate_by_ticker = {candidate["ticker"]: candidate for candidate in pending_candidates}
        insert_failed_count = 0
        for ticker, themes in result.themes_by_ticker.items():
            candidate = candidate_by_ticker[ticker]
            # 백필 중 새 run이 publish되면 더 이상 현재 카드의 원천이 아니므로 중단한다.
            _assert_current_complete_run(supabase, base_url, supabase_key, run_id)
            try:
                _insert_themes(supabase, base_url, supabase_key, run_id, candidate["candidate_id"], [theme.as_dict() for theme in themes])
            except Exception as exc:  # noqa: BLE001 - 한 후보의 REST write 실패는 다음 후보를 막지 않는다.
                insert_failed_count += 1
                print(f"ticker={ticker} theme_insert_failed={exc}")

        print(
            f"run_id={run_id} candidates={len(candidates)} pending={len(pending_candidates)} themes_success={result.success_count} "
            f"themes_empty={result.empty_count} themes_failed={result.failed_count + insert_failed_count}"
        )
    return 2 if result.failed_count or insert_failed_count else 0


if __name__ == "__main__":
    sys.exit(run())
