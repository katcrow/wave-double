from uuid import uuid4

import pytest

from apps.batch.theme_enrichment import CandidateTheme, ThemeEnrichmentResult
from tools import backfill_candidate_themes as backfill


class FakeResponse:
    def __init__(self, payload, status_code=200):
        self._payload = payload
        self.status_code = status_code
        self.content = b"{}" if payload is not None else b""

    def json(self):
        return self._payload


class FakeSupabaseClient:
    def __init__(self, run_id, existing_candidate_id):
        self.run_id = run_id
        self.existing_candidate_id = existing_candidate_id
        self.posts = []

    def __enter__(self):
        return self

    def __exit__(self, *args):
        return False

    def request(self, method, url, **kwargs):
        if method == "GET" and url.endswith("/runs"):
            return FakeResponse([{"run_id": self.run_id, "logical_run_key": "close:2026-10-02"}])
        if method == "GET" and url.endswith("/logical_runs"):
            return FakeResponse([{"logical_run_key": "close:2026-10-02"}])
        if method == "GET" and url.endswith("/candidates"):
            return FakeResponse([
                {"candidate_id": self.existing_candidate_id, "ticker": "000001"},
                {"candidate_id": "candidate-new", "ticker": "000002"},
            ])
        if method == "GET" and url.endswith("/candidate_themes"):
            return FakeResponse([{"candidate_id": self.existing_candidate_id}])
        if method == "POST" and url.endswith("/candidate_themes"):
            self.posts.append(kwargs)
            return FakeResponse(None)
        raise AssertionError((method, url, kwargs))


def test_backfill_only_enriches_candidates_without_existing_theme_rows(monkeypatch, capsys):
    run_id = str(uuid4())
    supabase = FakeSupabaseClient(run_id, "candidate-existing")

    class FakeContext:
        def __init__(self, *args, **kwargs):
            pass

        def __enter__(self):
            return self

        def __exit__(self, *args):
            return False

    class FakeLsClient(FakeContext):
        pass

    monkeypatch.setenv("SUPABASE_URL", "https://example.supabase.co")
    monkeypatch.setenv("SUPABASE_SERVICE_ROLE_KEY", "service-role-test")
    monkeypatch.setenv("LS_APP_KEY", "ls-key-test")
    monkeypatch.setenv("LS_APP_SECRET", "ls-secret-test")
    monkeypatch.setattr(backfill.httpx, "Client", lambda **kwargs: supabase)
    monkeypatch.setattr(backfill, "LsOAuthTokenProvider", FakeContext)
    monkeypatch.setattr(backfill, "LsClient", FakeLsClient)

    def fake_enrich(tickers, client):
        assert tickers == ["000002"]
        return ThemeEnrichmentResult(
            themes_by_ticker={"000002": (CandidateTheme("T1", "테마1", 2.5),)},
            empty_tickers=(),
            failed_tickers=(),
            requested_count=1,
            success_count=1,
            empty_count=0,
            failed_count=0,
        )

    monkeypatch.setattr(backfill, "enrich_candidate_themes", fake_enrich)

    assert backfill.run(["--run-id", run_id]) == 0
    assert len(supabase.posts) == 1
    assert supabase.posts[0]["headers"]["Prefer"].startswith("resolution=ignore-duplicates")
    assert supabase.posts[0]["json"][0]["candidate_id"] == "candidate-new"
    assert "themes_success=1" in capsys.readouterr().out


def test_backfill_rejects_malformed_existing_theme_row(monkeypatch):
    class Client:
        def request(self, *args, **kwargs):
            return FakeResponse([{}])

    with pytest.raises(RuntimeError, match="theme REST response contained a malformed row"):
        backfill._load_existing_theme_candidate_ids(Client(), "https://example.supabase.co", "key", "run")


@pytest.mark.parametrize(
    ("runs", "pointers", "message"),
    [
        ([{"run_id": "run", "logical_run_key": "close:2026-10-02"}], [], "current complete published snapshot"),
        ([], [{"logical_run_key": "close:2026-10-02"}], "published run"),
    ],
)
def test_backfill_rejects_non_current_or_unpublished_run(runs, pointers, message):
    class Client:
        def request(self, method, url, **kwargs):
            if url.endswith("/runs"):
                return FakeResponse(runs)
            if url.endswith("/logical_runs"):
                return FakeResponse(pointers)
            raise AssertionError(url)

    with pytest.raises(RuntimeError, match=message):
        backfill._assert_current_complete_run(Client(), "https://example.supabase.co", "key", "run")
