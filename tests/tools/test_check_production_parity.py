"""tools/check_production_parity.py 계약 테스트(epic-3-retro-item-15).

이 도구는 default-branch 배포 gate로 쓰이므로 파서 오탐이 곧 "gate 무력화"다.
초기 구현에 세 가지 파싱 결함이 있었고(역할 목록 절단, SECURITY DEFINER 헤더 윈도우
유출, `revoke ... from public`의 의미 오해) 각각을 회귀 테스트로 고정한다.
"""

from __future__ import annotations

import importlib.util
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
_spec = importlib.util.spec_from_file_location(
    "check_production_parity", ROOT / "tools" / "check_production_parity.py"
)
parity = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(parity)


def write(tmp_path: Path, name: str, body: str) -> Path:
    path = tmp_path / name
    path.write_text(body, encoding="utf-8")
    return path


def test_grant_statement_keeps_every_role_in_the_list(tmp_path: Path) -> None:
    """`to anon, authenticated, service_role`에서 첫 역할만 잡히면 안 된다."""
    path = write(
        tmp_path,
        "202601010000_grant.sql",
        """
        create or replace function public.read_thing(id uuid) returns void
        language sql security definer set search_path = pg_catalog, public
        as $$ select 1 $$;
        revoke execute on function public.read_thing(uuid) from public, anon, authenticated;
        grant execute on function public.read_thing(uuid) to anon, authenticated, service_role;
        """,
    )

    grants = parity.simulate_grants([path])

    assert grants["read_thing"] == {"anon": True, "authenticated": True, "service_role": True}


def test_revoke_from_public_does_not_strip_direct_service_role_grant(tmp_path: Path) -> None:
    """`revoke from public, anon, authenticated`는 service_role 직접 grant를 남긴다."""
    path = write(
        tmp_path,
        "202601010000_trigger.sql",
        """
        create or replace function public.guard_thing() returns trigger
        language plpgsql security definer set search_path = public
        as $$ begin return new; end $$;
        revoke execute on function public.guard_thing() from public, anon, authenticated;
        """,
    )

    grants = parity.simulate_grants([path])

    assert grants["guard_thing"] == {"anon": False, "authenticated": False, "service_role": True}


def test_revoke_names_service_role_explicitly_to_strip_it(tmp_path: Path) -> None:
    path = write(
        tmp_path,
        "202601010000_revoke_all.sql",
        """
        create or replace function public.internal_thing() returns void
        language sql as $$ select 1 $$;
        revoke execute on function public.internal_thing() from public, anon, authenticated, service_role;
        """,
    )

    grants = parity.simulate_grants([path])

    assert grants["internal_thing"] == {"anon": False, "authenticated": False, "service_role": False}


def test_security_definer_does_not_bleed_into_the_next_function(tmp_path: Path) -> None:
    """앞 함수 본문이 섞여 non-definer 함수가 definer로 오판되면 안 된다."""
    body = "select 1 " * 400  # 고정 폭 윈도우를 넘기기 위한 긴 본문
    path = write(
        tmp_path,
        "202601010000_two_functions.sql",
        f"""
        create or replace function public.plain_thing() returns numeric
        language sql immutable
        as $$ select 0.30::numeric $$;

        create or replace function public.definer_thing() returns void
        language sql security definer set search_path = public
        as $$ {body} $$;
        """,
    )

    local = parity.collect_local_from(files=[path])

    assert local["functions"]["plain_thing"]["security_definer"] is False
    assert local["functions"]["definer_thing"]["security_definer"] is True


def test_alter_function_search_path_wins_over_create(tmp_path: Path) -> None:
    path = write(
        tmp_path,
        "202601010000_alter_search_path.sql",
        """
        create or replace function public.read_thing(id uuid) returns void
        language sql security definer set search_path = public
        as $$ select 1 $$;
        alter function public.read_thing(uuid) set search_path = pg_catalog, public;
        """,
    )

    local = parity.collect_local_from(files=[path])

    assert local["functions"]["read_thing"]["search_path"] == "pg_catalog, public"


def test_later_migration_search_path_overrides_earlier(tmp_path: Path) -> None:
    first = write(
        tmp_path,
        "202601010000_create.sql",
        """
        create or replace function public.read_thing(id uuid) returns void
        language sql security definer set search_path = public
        as $$ select 1 $$;
        """,
    )
    second = write(
        tmp_path,
        "202601020000_harden.sql",
        """
        create or replace function public.read_thing(id uuid) returns void
        language sql security definer set search_path = pg_catalog, public
        as $$ select 1 $$;
        """,
    )

    local = parity.collect_local_from(files=[second, first])

    assert local["functions"]["read_thing"]["search_path"] == "pg_catalog, public"
    assert local["migrations"] == ["202601010000_create", "202601020000_harden"]


@pytest.mark.parametrize(
    ("mode", "direction", "expected"),
    [
        ("gate", "local_ahead", "ERROR"),
        ("gate", "remote_ahead", "WARN"),
        ("offline", "local_ahead", "WARN"),
        ("offline", "remote_ahead", "ERROR"),
    ],
)
def test_severity_matrix(mode: str, direction: str, expected: str) -> None:
    assert parity.severity_for(mode, direction) == expected


def catalog(functions: dict, migrations: list[str] | None = None) -> dict:
    return {"migrations": migrations or [], "functions": functions}


def test_gate_blocks_function_declared_locally_but_missing_in_production() -> None:
    """item-15의 핵심: 로컬 fixture는 pass인데 운영에 함수가 없는 상태를 차단한다."""
    local = catalog(
        {
            "get_thing": {
                "security_definer": True,
                "search_path": "public",
                "grants": {"anon": True, "authenticated": True, "service_role": True},
            }
        }
    )

    findings = parity.compare("gate", local, catalog({}))

    assert [(f["severity"], f["family"], f["name"]) for f in findings] == [
        ("ERROR", "function", "get_thing")
    ]


def test_gate_blocks_migration_not_applied_to_production() -> None:
    findings = parity.compare("gate", catalog({}, ["202609100000_new_thing"]), catalog({}))

    assert [(f["severity"], f["family"]) for f in findings] == [("ERROR", "migration")]


def test_offline_mode_only_warns_about_undeployed_local_migration() -> None:
    """PR CI에서는 새 migration 추가가 정상 개발 상태이므로 WARN에 그친다."""
    findings = parity.compare("offline", catalog({}, ["202609100000_new_thing"]), catalog({}))

    assert [(f["severity"], f["family"]) for f in findings] == [("WARN", "migration")]


def test_offline_mode_blocks_reverse_drift() -> None:
    """baseline이 주장하는 migration이 로컬에 없으면(삭제) 오프라인 gate가 차단한다."""
    findings = parity.compare("offline", catalog({}), catalog({}, ["202609100000_thing"]))

    assert [(f["severity"], f["direction"]) for f in findings] == [("ERROR", "remote_ahead")]


def test_pinned_local_only_migration_is_not_reported() -> None:
    pinned = next(iter(parity.LOCAL_ONLY_MIGRATIONS))

    assert parity.compare("gate", catalog({}, [pinned]), catalog({})) == []


def test_pinned_prod_only_migration_is_not_reported() -> None:
    pinned = next(iter(parity.PROD_ONLY_MIGRATIONS))

    assert parity.compare("gate", catalog({}), catalog({}, [pinned])) == []


def test_pinned_prod_only_function_is_not_reported() -> None:
    pinned = next(iter(parity.PROD_ONLY_FUNCTIONS))
    remote = catalog({pinned: {"security_definer": True, "search_path": None, "grants": {}}})

    assert parity.compare("gate", catalog({}), remote) == []


def test_security_definer_mismatch_is_always_error() -> None:
    shared = {
        "search_path": "public",
        "grants": {"anon": False, "authenticated": False, "service_role": True},
    }
    local = catalog({"thing": {"security_definer": True, **shared}})
    remote = catalog({"thing": {"security_definer": False, **shared}})

    findings = parity.compare("gate", local, remote)

    assert [(f["severity"], f["family"]) for f in findings] == [("ERROR", "secdef")]


def test_search_path_and_grant_drift_are_reported_as_warnings() -> None:
    local = catalog(
        {
            "thing": {
                "security_definer": True,
                "search_path": "pg_catalog, public",
                "grants": {"anon": False, "authenticated": True, "service_role": True},
            }
        }
    )
    remote = catalog(
        {
            "thing": {
                "security_definer": True,
                "search_path": "public",
                "grants": {"anon": False, "authenticated": False, "service_role": True},
            }
        }
    )

    findings = parity.compare("gate", local, remote)

    assert {(f["severity"], f["family"]) for f in findings} == {
        ("WARN", "search_path"),
        ("WARN", "grant"),
    }


def test_matching_catalogs_produce_no_findings() -> None:
    info = {
        "security_definer": True,
        "search_path": "public",
        "grants": {"anon": False, "authenticated": False, "service_role": True},
    }
    left = catalog({"thing": dict(info)}, ["202609100000_thing"])
    right = catalog({"thing": dict(info)}, ["202609100000_thing"])

    assert parity.compare("gate", left, right) == []


def test_committed_baseline_matches_the_repository_catalog() -> None:
    """커밋된 baseline이 로컬 migration 저장소와 역방향으로 어긋나면 차단한다."""
    local = parity.collect_local()
    baseline = parity.load_baseline(parity.DEFAULT_BASELINE)

    errors = [f for f in parity.compare("offline", local, baseline) if f["severity"] == "ERROR"]

    assert errors == [], errors


def test_committed_baseline_records_the_production_project() -> None:
    import json

    data = json.loads(parity.DEFAULT_BASELINE.read_text(encoding="utf-8"))

    assert data["project_ref"] == parity.PROJECT_REF
    assert data["migrations"] == sorted(data["migrations"])

# ── live 조회 경로 회귀 ────────────────────────────────────────────────────────
# 이 두 결함은 오프라인 테스트로는 드러나지 않았고, 실제로 운영 토큰으로 --gate를 돌려보고
# 나서야 발견됐다(403 그리고 영구 WARN 6건).


@pytest.mark.parametrize(
    ("proconfig", "expected"),
    [
        ("{search_path=public}", "public"),
        # 값에 쉼표가 있으면 원소 전체가 따옴표로 감싸진다 -- 이 형태가 파싱되지 않아
        # pg_catalog, public으로 통일한 함수마다 매 실행 WARN이 떴다.
        ('{"search_path=pg_catalog, public"}', "pg_catalog, public"),
        ("{search_path=pg_catalog}", "pg_catalog"),
        # search_path 뒤에 다른 설정이 붙어도 그 값까지 삼키지 않는다.
        ("{search_path=public,statement_timeout=5s}", "public"),
        ('{"search_path=pg_catalog, public",statement_timeout=5s}', "pg_catalog, public"),
        ("{}", None),
        ("", None),
        ("{statement_timeout=5s}", None),
    ],
)
def test_live_proconfig_search_path_parsing(proconfig: str, expected: str | None) -> None:
    assert parity.parse_live_search_path(proconfig) == expected


def test_live_search_path_matches_the_local_normalized_form() -> None:
    """live 파싱 결과와 로컬 파싱 결과가 같은 표기여야 비교가 성립한다."""
    assert parity.parse_live_search_path('{"search_path=pg_catalog,  public"}') == parity._normalize_search_path(
        "pg_catalog,  public"
    )


def test_management_api_request_sends_an_explicit_user_agent() -> None:
    """api.supabase.com은 Cloudflare 뒤에 있고 기본 UA를 error code 1010으로 차단한다.

    UA가 없으면 토큰이 유효해도 403이 돌아와, 배포 gate가 매번 "인증 실패"처럼 죽는다.
    """
    captured: dict = {}

    class FakeResponse:
        def read(self) -> bytes:
            return b"[]"

        def __enter__(self):
            return self

        def __exit__(self, *args) -> None:
            return None

    def fake_urlopen(request):
        captured["headers"] = dict(request.headers)
        return FakeResponse()

    original = parity.urllib.request.urlopen
    parity.urllib.request.urlopen = fake_urlopen
    try:
        parity.management_query("token-abc", "select 1;")
    finally:
        parity.urllib.request.urlopen = original

    # urllib은 헤더 이름을 Title-Case로 정규화한다.
    headers = {key.lower(): value for key, value in captured["headers"].items()}
    assert headers["user-agent"] == parity.USER_AGENT
    assert headers["authorization"] == "Bearer token-abc"
    assert headers["content-type"] == "application/json"


def test_committed_baseline_records_multi_element_search_paths() -> None:
    """baseline이 live에서 생성됐다면 pg_catalog, public 표기가 살아 있어야 한다."""
    import json

    data = json.loads(parity.DEFAULT_BASELINE.read_text(encoding="utf-8"))
    multi = [
        name
        for name, info in data["functions"].items()
        if info.get("search_path") == "pg_catalog, public"
    ]

    assert multi, "다중 원소 search_path가 baseline에 하나도 없다 -- live 파싱이 깨졌을 수 있다"
