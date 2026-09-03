import json
from datetime import date

import httpx

from apps.batch.candidate_tags_repository import CandidateTag, SupabaseCandidateTagsRepository


def make_repo(handler):
    transport = httpx.MockTransport(handler)
    return SupabaseCandidateTagsRepository(
        "https://example.supabase.co", "service-role-key", http_client=httpx.Client(transport=transport)
    )


def test_upsert_tags_empty_list_short_circuits_without_http_call():
    calls = []

    def handler(request):
        calls.append(request)
        return httpx.Response(201, json={})

    repo = make_repo(handler)
    assert repo.upsert_tags([]) == 0
    assert calls == []


def test_upsert_tags_sends_merge_duplicates_with_conflict_target():
    seen = []

    def handler(request):
        seen.append(request)
        return httpx.Response(201, json={})

    repo = make_repo(handler)
    tag = CandidateTag(
        candidate_id="c1", strategy="A", signal_date=date(2026, 9, 1),
        attempt_run_id="run-1", params_meta={"k": "v"},
    )
    count = repo.upsert_tags([tag])

    assert count == 1
    request = seen[0]
    assert request.headers["prefer"] == "resolution=merge-duplicates"
    assert request.url.params["on_conflict"] == "candidate_id,strategy,attempt_run_id"
    body = json.loads(request.content)
    assert body[0]["candidate_id"] == "c1"
    assert body[0]["strategy"] == "A"
    assert body[0]["signal_date"] == "2026-09-01"
    assert body[0]["attempt_run_id"] == "run-1"
    assert body[0]["status"] == "active"
    assert body[0]["params_meta"] == {"k": "v"}


def test_upsert_tags_defaults_params_meta_to_empty_dict():
    seen = []

    def handler(request):
        seen.append(request)
        return httpx.Response(201, json={})

    repo = make_repo(handler)
    tag = CandidateTag(candidate_id="c1", strategy="B", signal_date=date(2026, 9, 1), attempt_run_id="run-1")
    repo.upsert_tags([tag])
    body = json.loads(seen[0].content)
    assert body[0]["params_meta"] == {}


def test_sync_vanished_calls_rpc_endpoint_with_run_id_and_returns_count():
    seen = []

    def handler(request):
        seen.append(request)
        return httpx.Response(200, json={"vanished_count": 3})

    repo = make_repo(handler)
    result = repo.sync_vanished("run-1")

    assert result == {"vanished_count": 3}
    request = seen[0]
    assert request.url.path == "/rest/v1/rpc/sync_vanished_tags"
    body = json.loads(request.content)
    assert body == {"p_run_id": "run-1"}
    assert request.headers["apikey"] == "service-role-key"


def test_sync_vanished_raises_on_http_error():
    def handler(request):
        return httpx.Response(500, json={"message": "boom"})

    repo = make_repo(handler)
    try:
        repo.sync_vanished("run-1")
    except httpx.HTTPStatusError:
        pass
    else:
        raise AssertionError("expected HTTPStatusError to propagate")
