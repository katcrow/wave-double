import json
from datetime import date

import httpx

from apps.batch.supply_3day_repository import SupabaseSupply3DayRepository, SupplyRow


def make_repo(handler):
    transport = httpx.MockTransport(handler)
    return SupabaseSupply3DayRepository(
        "https://example.supabase.co", "service-role-key", http_client=httpx.Client(transport=transport)
    )


def _row(**overrides):
    fields = dict(
        candidate_id="c1",
        attempt_run_id="run-1",
        trading_day=date(2026, 9, 1),
        slot="D0",
        close=72000.0,
        volume=1200000.0,
        change_pct=1.41,
        foreign_net=800.0,
        institution_net=400.0,
        individual_net=-1200.0,
        program_net=None,
        investor_net_status="confirmed",
    )
    fields.update(overrides)
    return SupplyRow(**fields)


def test_upsert_rows_empty_list_short_circuits_without_http_call():
    calls = []

    def handler(request):
        calls.append(request)
        return httpx.Response(201, json={})

    repo = make_repo(handler)
    assert repo.upsert_rows([]) == 0
    assert calls == []


def test_upsert_rows_sends_merge_duplicates_with_conflict_target_and_serialized_payload():
    seen = []

    def handler(request):
        seen.append(request)
        return httpx.Response(201, json={})

    repo = make_repo(handler)
    row = _row()
    count = repo.upsert_rows([row])

    assert count == 1
    request = seen[0]
    assert request.url.path == "/rest/v1/supply_3day"
    assert request.headers["prefer"] == "resolution=merge-duplicates"
    assert request.url.params["on_conflict"] == "candidate_id,trading_day,attempt_run_id"
    body = json.loads(request.content)
    assert body[0]["candidate_id"] == "c1"
    assert body[0]["attempt_run_id"] == "run-1"
    assert body[0]["trading_day"] == "2026-09-01"
    assert body[0]["slot"] == "D0"
    assert body[0]["close"] == 72000.0
    assert body[0]["volume"] == 1200000.0
    assert body[0]["change_pct"] == 1.41
    assert body[0]["foreign_net"] == 800.0
    assert body[0]["institution_net"] == 400.0
    assert body[0]["individual_net"] == -1200.0
    assert body[0]["program_net"] is None
    assert body[0]["investor_net_status"] == "confirmed"
    assert "collected_at" in body[0]


def test_upsert_rows_serializes_multiple_rows_in_order():
    seen = []

    def handler(request):
        seen.append(request)
        return httpx.Response(201, json={})

    repo = make_repo(handler)
    rows = [
        _row(trading_day=date(2026, 8, 28), slot="D-2"),
        _row(trading_day=date(2026, 8, 31), slot="D-1"),
        _row(trading_day=date(2026, 9, 1), slot="D0"),
    ]
    count = repo.upsert_rows(rows)

    assert count == 3
    body = json.loads(seen[0].content)
    assert [row["slot"] for row in body] == ["D-2", "D-1", "D0"]


def test_upsert_rows_preserves_non_null_program_net():
    seen = []

    def handler(request):
        seen.append(request)
        return httpx.Response(201, json={})

    repo = make_repo(handler)
    assert repo.upsert_rows([_row(program_net=-1234.0)]) == 1

    body = json.loads(seen[0].content)
    assert body[0]["program_net"] == -1234.0


def test_upsert_rows_accumulates_d0_per_attempt_but_retries_are_idempotent():
    stored = {}
    requests = []

    def handler(request):
        requests.append(request)
        for row in json.loads(request.content):
            key = (row["candidate_id"], row["trading_day"], row["attempt_run_id"])
            stored[key] = row
        return httpx.Response(201, json={})

    repo = make_repo(handler)
    first_attempt = _row(candidate_id="c1", attempt_run_id="run-1", close=72000.0)
    second_attempt = _row(candidate_id="c2", attempt_run_id="run-2", close=72100.0)
    retry = _row(candidate_id="c1", attempt_run_id="run-1", close=72500.0)

    assert repo.upsert_rows([first_attempt, second_attempt]) == 2
    assert repo.upsert_rows([retry]) == 1

    assert len(stored) == 2
    assert stored[("c1", "2026-09-01", "run-1")]["close"] == 72500.0
    assert stored[("c2", "2026-09-01", "run-2")]["close"] == 72100.0
    assert all(
        request.url.params["on_conflict"] == "candidate_id,trading_day,attempt_run_id"
        for request in requests
    )


def test_upsert_rows_raises_on_http_error():
    def handler(request):
        return httpx.Response(500, json={"message": "boom"})

    repo = make_repo(handler)
    try:
        repo.upsert_rows([_row()])
    except httpx.HTTPStatusError:
        pass
    else:
        raise AssertionError("expected HTTPStatusError to propagate")
