"""Production Supabase ↔  로컬 migration 저장소 패리티 점검 (epic-3-retro-item-15 / epic-6-retro-item-23).

default-branch(배포) gate: 로컬 SQL fixture가 통과했는데 운영에 함수가 없는
불일치를 차단한다. 저장소에 선언된 public 함수 catalog와 migration 적용 목록을
production의 실측 state와 비교한다.

세 가지 실행 모드:

1. 오프라인(baseline 대비, 기본값, 없을 때는 커밋된 스냅샷 사용)
   - `python tools/check_production_parity.py`
   로컬 파서 결과 ↔ `tools/production_parity_baseline.json`(프로덕션 실측 스냅샷)을 비교한다.
   baseline이 주장하는 migration/함수가 로컬 migration에 없는 "역방향 drift"(커밋된
   migration/함수를 누가 지웠는지)를 ERROR로 차단한다. 로컬이 baseline보다 앞선 것은
   배포 대기 상태이므로 WARN으로만 알린다(PR CI 용도).

2. live gate(운영 실측 대비, 배포 gate)
   - `python tools/check_production_parity.py --gate`
   Supabase Management API 데이터베이스 쿼리로 live 프로덕션을 조회해 로컬과 비교한다.
   로컬 migration/함수가 live에 없는(미배포) 것은 ERROR — "fixture는 pass했는데 운영 함수
   부재"를 차단한다. live가 로컬보다 앞선(역방향) 것은 WARN. plus 커밋된 baseline이 live와
   다른지도 검증한다(baseline 갱신 누락 탐지). token은 SUPABASE_ACCESS_TOKEN 환경변수.

3. baseline 갱신
   - `python tools/check_production_parity.py --write-baseline` (live 조회 후 저장)

결과가 항상 동일한 기준으로 diff되도록, 비교는 모두 SQL 조회만 수행하고 어떤 변경도
가하지 않는다. 저장소 단위로 "어느 쪽이 맞는지"가 아니라 "drift 여부"를 보고한다.

pin(의도적으로 양쪽 기준이 어긋나는 항목):
- PROD_ONLY_MIGRATIONS: prod에는 있지만 로컬 파일이 없는 migration(다른 이름/스쿼시 적용).
- LOCAL_ONLY_MIGRATIONS: 로컬에는 있지만 prod schema_migrations에 없어도 정상인 것
  (epic1-fix로 squashed된 초기 13개 + pg_cron/pg_net 불가 + 다른 이름으로 적용된 3개).
- PROD_ONLY_FUNCTIONS: prod에만 존재하는 함수(rls_auto_enable: Supabase Dashboard 관리).
"""

from __future__ import annotations

import argparse
import json
import os
import re
import urllib.request
from datetime import date
from pathlib import Path

ROOT = Path(__file__).resolve().parents[1]
MIGRATION_DIR = ROOT / "infra" / "supabase" / "migrations"
DEFAULT_BASELINE = ROOT / "tools" / "production_parity_baseline.json"
PROJECT_REF = "qqhjeumlecaudsiqhhdu"
MANAGEMENT_API = f"https://api.supabase.com/v1/projects/{PROJECT_REF}/database/query"

# 로컬에는 있고 prod schema_migrations에는 없어도 정상인 migration. key가 reason.
LOCAL_ONLY_MIGRATIONS = {
    "202609011500_create_trading_calendar": "epic1-fix 스쿼시 적용 대상(초기 라인age/캘린더)",
    "202609011600_create_run_lineage": "epic1-fix 스쿼시 적용 대상",
    "202609011700_create_candidates": "epic1-fix 스쿼시 적용 대상",
    "202609011800_harden_candidate_rls": "epic1-fix 스쿼시 적용 대상",
    "202609011900_restrict_candidate_writer": "epic1-fix 스쿼시 적용 대상",
    "202609012000_restrict_candidate_writer_public": "epic1-fix 스쿼시 적용 대상",
    "202609012100_harden_run_and_candidate_contracts": "epic1-fix 스쿼시 적용 대상",
    "202609012110_revoke_run_rpc_browser_roles": "epic1-fix 스쿼시 적용 대상",
    "202609012200_add_candidate_fallback_support": "epic1-fix 스쿼시 적용 대상",
    "202609012300_add_skip_attempt": "prod는 add_skip_attempt_rpc라는 다른 이름으로 적용",
    "202609020000_create_dashboard_snapshot": "epic1-fix 스쿼시 적용 대상",
    "202609021000_create_dispatch_outbox": "epic1-fix 스쿼시 적용 대상",
    "202609021100_schedule_dispatch_worker_cron": "pg_cron/pg_net 미설치 — batch는 scheduled-batch.yml로 구동",
    "202609032200_add_outcome_correction_mechanism": "prod는 add_outcome_correction_mechanism이라는 다른 이름으로 적용",
    "202609032201_fix_outcome_correction_review_patch": "prod는 fix_outcome_correction_review_patch라는 다른 이름으로 적용",
    "202609042200_enforce_delisted_termination": "prod 적용 시 이름/스쿼시 경로가 다름(운영 반영 확인됨)",
    "202609100200_bias_close_stage": "prod는 20260910020000_bias_close_stage라는 다른 timestamp로 적용(운영 반영 확인됨)",
    "202609101100_create_outcome_win_rate_pf": "prod는 create_outcome_win_rate_pf라는 timestamp 접두사 없는 이름으로 적용(운영 반영 확인됨)",
    "202609101200_create_outcome_win_rate_pf_by_strategy_source": "prod는 create_outcome_win_rate_pf_by_strategy_source라는 timestamp 접두사 없는 이름으로 적용(운영 반영 확인됨)",
}

# prod에는 있고 로컬 파일이 없는 migration. 다른 이름/스쿼시로 적용된 것.
PROD_ONLY_MIGRATIONS = {
    "add_outcome_correction_mechanism": "로컬 202609032200_add_outcome_correction_mechanism의 운영명",
    "fix_outcome_correction_review_patch": "로컬 202609032201_fix_outcome_correction_review_patch의 운영명",
    "create_rebuild_outcome_projection": "로컬 202609051200_create_rebuild_outcome_projection의 운영 이전명",
    "add_skip_attempt_rpc": "로컬 202609012300_add_skip_attempt의 운영명",
    "epic4-091300-strict-adjusted-evidence-rate": "운영 수동 보정 migration(스토리 4.13 계약)",
    "epic1_fix_add_run_lineage_and_dashboard_snapshot": "초기 13개 migration을 스쿼시한 운영 migration",
    "20260910020000_bias_close_stage": "로컬 202609100200_bias_close_stage 적용 시 timestamp가 다르게 기록된 운영명(story 5-4)",
    "create_outcome_win_rate_pf": "로컬 202609101100_create_outcome_win_rate_pf 적용 시 timestamp 접두사 없이 기록된 운영명(story 5-5)",
    "create_outcome_win_rate_pf_by_strategy_source": "로컬 202609101200_create_outcome_win_rate_pf_by_strategy_source 적용 시 timestamp 접두사 없이 기록된 운영명(story 5-6)",
}

# prod에만 존재하고 로컬 migration이 선언하지 않아도 정상인 함수.
PROD_ONLY_FUNCTIONS = {
    "rls_auto_enable": "Supabase Dashboard가 RLS 토글 시 자동 생성하는 헬퍼",
}

# 검사할 role. PostgreSQL has_function_privilege('role', oid, 'EXECUTE')와 1:1.
ROLES = ("anon", "authenticated", "service_role")

# 시뮬레이션 대상 role 목록(statement에 등장 가능한 것 + public 키워드)
GRANT_ROLES = ROLES + ("public",)

CREATE_FUNCTION = re.compile(
    r"create\s+(?:or\s+replace\s+)?function\s+public\.([a-z0-9_]+)\s*\(",
    re.IGNORECASE,
)
ALTER_SEARCH_PATH = re.compile(
    r"alter\s+function\s+public\.([a-z0-9_]+)\s*\([^)]*\)\s*set\s+search_path\s*=\s*([a-z0-9_, ]+)[;]",
    re.IGNORECASE,
)
# roles 그룹은 역할 목록 "전체"를 감싼다. 반복부를 그룹 밖에 두면 `to anon, authenticated,
# service_role`에서 첫 역할만 잡혀 뒤쪽 grant가 사라진다(패리티 오탐 원인).
GRANT_REVOKE = re.compile(
    r"(?P<verb>grant|revoke)\s+execute\s+on\s+function\s+"
    r"(?P<funcs>.*?)"
    r"\s+(?P<dir>to|from)\s+"
    r"(?P<roles>(?:public|anon|authenticated|service_role)"
    r"(?:\s*,\s*(?:public|anon|authenticated|service_role))*)"
    r"\s*;",
    re.DOTALL | re.IGNORECASE,
)
SEARCH_PATH = re.compile(r"set\s+search_path\s*=\s*([a-z0-9_, ]+)", re.IGNORECASE)
FUNCTION_IN_LIST = re.compile(r"public\.([a-z0-9_]+)\s*\(", re.IGNORECASE)


def migration_stem(path: Path) -> str:
    return path.name[: -len(".sql")]


def _header_up_to_body(text: str, start: int) -> str:
    """create function 문법 헤더(as $$ 본문 시작)까지만 잘라낸다."""
    body_at = text.find("as $$", start)
    if body_at == -1:
        body_at = text.find("language", start) + 80
    return text[start:body_at]


def parse_search_path(path: Path) -> dict[str, str]:
    """migration 파일에서 함수별로 지정된 search_path를 수집.

    ALTER FUNCTION ... SET search_path가 create의 `set search_path`보다 우선한다.
    각 함수 헤더 = create 이후부터 `as $$` 직전까지만 스캔해 다른 함수 본문 오염을 막는다.
    """
    text = path.read_text(encoding="utf-8")
    final: dict[str, str] = {}
    for match in ALTER_SEARCH_PATH.finditer(text):
        final[match.group(1)] = _normalize_search_path(match.group(2))
    for match in CREATE_FUNCTION.finditer(text):
        name = match.group(1)
        sp = SEARCH_PATH.search(_header_up_to_body(text, match.start()))
        if sp and name not in final:
            final[name] = _normalize_search_path(sp.group(1))
    return final


def _normalize_search_path(value: str) -> str:
    return ", ".join(part.strip() for part in value.split(",") if part.strip())


def simulate_grants(files: list[Path]) -> dict[str, dict[str, bool]]:
    """migration 실행 일정(stem 정렬)대로 grant/revoke를 재현한다.

    PostgreSQL 의미를 그대로 모델링한다 — PUBLIC 유사역할 grant와 역할별 직접 grant는
    별개다. `revoke ... from public`은 PUBLIC grant만 내리고, 직접 grant를 가진 역할의
    권한은 그대로 남는다. 따라서 effective = 직접 grant OR PUBLIC grant.

    초기 상태(Supabase 기본값):
    - PUBLIC grant: 함수 생성 시 기본으로 부여됨 → True
    - service_role: Supabase가 public 스키마 함수에 기본 권한으로 직접 부여 → True
    - anon/authenticated: 직접 grant 없음(PUBLIC grant를 통해서만 실행 가능) → False

    이 구분이 없으면 `revoke ... from public, anon, authenticated`(= service_role은
    의도적으로 유지)를 service_role까지 내린 것으로 오판한다.
    """
    state: dict[str, dict] = {}

    def acl_for(name: str) -> dict:
        return state.setdefault(
            name,
            {"public": True, "direct": {"anon": False, "authenticated": False, "service_role": True}},
        )

    for path in files:
        text = path.read_text(encoding="utf-8")
        for match in GRANT_REVOKE.finditer(text):
            verb = match.group("verb").lower()
            func_names = FUNCTION_IN_LIST.findall(match.group("funcs"))
            roles = [
                r.strip().lower()
                for r in re.findall(r"(?:public|anon|authenticated|service_role)", match.group("roles"))
            ]
            for name in func_names:
                acl = acl_for(name)
                for role in roles:
                    if role == "public":
                        acl["public"] = verb == "grant"
                    else:
                        acl["direct"][role] = verb == "grant"

    return {
        name: {role: acl["direct"][role] or acl["public"] for role in ROLES}
        for name, acl in state.items()
    }


def collect_local() -> dict:
    """로컬 migration 저장소를 파싱해 expected catalog를 만든다."""
    return collect_local_from(files=sorted(MIGRATION_DIR.glob("*.sql")))


def collect_local_from(*, files: list[Path]) -> dict:
    """주어진 migration 파일 목록(stem 정렬)을 파싱해 expected catalog를 만든다."""
    files = sorted(files, key=lambda f: f.name)
    migrations = [migration_stem(f) for f in files]

    functions: dict[str, dict] = {}
    grants = simulate_grants(files)
    for path in files:
        text = path.read_text(encoding="utf-8")
        for match in CREATE_FUNCTION.finditer(text):
            name = match.group(1)
            # 헤더는 `as $$` 직전까지만 본다. 고정 폭(2000자) 윈도우는 다음 함수 본문까지
            # 삼켜서 SECURITY DEFINER가 아닌 함수를 definer로 오판한다.
            header = _header_up_to_body(text, match.start())
            secdef = bool(re.search(r"security\s+definer", header, re.IGNORECASE))
            functions.setdefault(name, {"security_definer": secdef})

    for name, acl in grants.items():
        functions.setdefault(name, {"security_definer": True})
        functions[name]["grants"] = acl

    # parse_search_path는 파일 단위로 마지막 지정을 수집 → 함수별 최종 search_path 맵 구성
    search_path_by_name: dict[str, str] = {}
    for path in files:
        for name, value in parse_search_path(path).items():
            search_path_by_name[name] = value

    exact: dict[str, dict] = {}
    for name, info in functions.items():
        exact[name] = {
            "security_definer": bool(info["security_definer"]),
            "search_path": search_path_by_name.get(name),
            "grants": {r: bool(info.get("grants", {}).get(r, True)) for r in ROLES},
        }
    return {"migrations": migrations, "functions": exact}


# api.supabase.com은 Cloudflare 뒤에 있고 기본 User-Agent(urllib/python-requests 등)를
# 차단한다 -- 토큰이 유효해도 `error code: 1010`과 함께 403이 돌아온다. 인증 실패로 오인해
# secret을 다시 발급하게 만드는 함정이라 UA를 명시한다(실제로 이 gate가 그렇게 죽었다).
USER_AGENT = "wave-double-parity-gate/1.0"


def management_query(token: str, sql: str) -> list[dict]:
    """Supabase Management API PostgreSQL 엔드포인트로 읽기 전용 조회."""
    request = urllib.request.Request(
        MANAGEMENT_API,
        data=json.dumps({"query": sql}).encode("utf-8"),
        headers={
            "Authorization": f"Bearer {token}",
            "Content-Type": "application/json",
            "User-Agent": USER_AGENT,
        },
        method="POST",
    )
    with urllib.request.urlopen(request) as response:
        return json.loads(response.read().decode("utf-8"))


def parse_live_search_path(proconfig: str) -> str | None:
    """pg_proc.proconfig 텍스트에서 search_path 값을 뽑아낸다.

    proconfig는 배열 리터럴이고, 값에 쉼표가 있으면 원소 전체가 따옴표로 감싸진다:

        {search_path=public}                  -> "public"
        {"search_path=pg_catalog, public"}    -> "pg_catalog, public"
        {search_path=public,statement_timeout=5s} -> "public"

    이전 구현은 먼저 쉼표로 쪼갠 뒤 `search_path=`로 시작하는 원소를 찾았다. 따옴표로 감싼
    형태에서는 첫 조각이 `"search_path=pg_catalog`가 되어 접두사 검사에 실패하고 값이 통째로
    None이 됐다 -- 즉 `pg_catalog, public`으로 통일한 함수(epic-4-retro-item-33)마다 매 실행
    영구 WARN이 떠서 진짜 drift를 가렸다.
    """
    match = re.search(r'search_path=([^"}]*)', proconfig or "")
    if not match:
        return None
    parts: list[str] = []
    for token in match.group(1).split(","):
        token = token.strip()
        if not token:
            continue
        if "=" in token:
            # 다음 설정(`statement_timeout=...`)의 시작 -- search_path 값은 여기서 끝난다.
            break
        parts.append(token)
    return ", ".join(parts) or None


def fetch_live_production(token: str) -> dict:
    migrations_rows = management_query(
        token,
        "select name from supabase_migrations.schema_migrations order by name;",
    )
    func_rows = management_query(
        token,
        """
        select p.proname,
               p.prosecdef,
               coalesce(p.proconfig::text, '') as proconfig,
               pg_catalog.has_function_privilege('anon', p.oid, 'EXECUTE') as anon_exec,
               pg_catalog.has_function_privilege('authenticated', p.oid, 'EXECUTE') as auth_exec,
               pg_catalog.has_function_privilege('service_role', p.oid, 'EXECUTE') as sr_exec
        from pg_proc p
        join pg_namespace n on n.oid = p.pronamespace
        where n.nspname = 'public' and p.prokind = 'f'
        order by p.proname;
        """,
    )

    functions: dict[str, dict] = {}
    for row in func_rows:
        search_path = parse_live_search_path(row["proconfig"])
        functions[row["proname"]] = {
            "security_definer": bool(row["prosecdef"]),
            "search_path": search_path,
            "grants": {
                "anon": bool(row["anon_exec"]),
                "authenticated": bool(row["auth_exec"]),
                "service_role": bool(row["sr_exec"]),
            },
        }
    return {"migrations": [r["name"] for r in migrations_rows], "functions": functions}


def severity_for(mode: str, direction: str) -> str:
    """모드별 drift 방향의 심각도.

    - local_ahead: 로컬이 원격/기준보다 앞선 것(로컬 migration/함수가 아직 적용 안 됨).
      default-branch 배포 gate(--gate)에서는 미반영이므로 ERROR — item-15가 차단하려는
      "fixture pass했는데 운영에 함수 부재"의 핵심. offline(PR CI, 커밋 baseline 대비)에서는
      migration을 추가한 개발 속성 변화이므로 WARN만.
    - remote_ahead: 원격/기준이 로컬보다 앞선 것(baseline에 있는데 로컬 migration이 없음).
      오프라인에서는 커밋 baseline이 주장하는데 로컬이 갖지 못해 배포 가능 set에서 빠지는
      회귀 위험이므로 ERROR, live gate에서는 운영 실측이 진실이므로 WARN으로 알린다.
    """
    if direction == "local_ahead":
        return "ERROR" if mode == "gate" else "WARN"
    return "ERROR" if mode == "offline" else "WARN"


def compare(mode: str, local: dict, remote: dict) -> list[dict]:
    findings: list[dict] = []

    local_migrations = set(local["migrations"])
    remote_migrations = set(remote["migrations"])

    for name in sorted(local_migrations - remote_migrations):
        if name in LOCAL_ONLY_MIGRATIONS:
            continue
        findings.append(
            {
                "severity": severity_for(mode, "local_ahead"),
                "family": "migration",
                "name": name,
                "direction": "local_ahead",
                "message": f"로컬 migration '{name}'이 운영 catalog에 없음(미배포 또는 미기록)",
            }
        )
    for name in sorted(remote_migrations - local_migrations):
        if name in PROD_ONLY_MIGRATIONS:
            continue
        findings.append(
            {
                "severity": severity_for(mode, "remote_ahead"),
                "family": "migration",
                "name": name,
                "direction": "remote_ahead",
                "message": f"운영 catalog에 '{name}'이 있지만 로컬 migration에는 없음(역방향 drift)",
            }
        )

    local_funcs = set(local["functions"])
    remote_funcs = set(remote["functions"])

    for name in sorted(local_funcs - remote_funcs):
        findings.append(
            {
                "severity": severity_for(mode, "local_ahead"),
                "family": "function",
                "name": name,
                "direction": "local_ahead",
                "message": f"함수 '{name}'이 로컬 migration에 선언됐지만 운영 catalog에 없음(미배포)",
            }
        )
    for name in sorted(remote_funcs - local_funcs):
        if name in PROD_ONLY_FUNCTIONS:
            continue
        findings.append(
            {
                "severity": severity_for(mode, "remote_ahead"),
                "family": "function",
                "name": name,
                "direction": "remote_ahead",
                "message": f"운영 catalog에 '{name}'이 있지만 로컬 migration이 선언하지 않음(역방향 drift)",
            }
        )

    for name in sorted(local_funcs & remote_funcs):
        local_info = local["functions"][name]
        remote_info = remote["functions"][name]

        if local_info["security_definer"] != remote_info["security_definer"]:
            findings.append(
                {
                    "severity": "ERROR",
                    "family": "secdef",
                    "name": name,
                    "direction": "related",
                    "message": (
                        f"함수 '{name}' security definer 불일치: 로컬 {local_info['security_definer']} vs "
                        f"운영 {remote_info['security_definer']}"
                    ),
                }
            )
        if local_info["search_path"] != remote_info["search_path"]:
            findings.append(
                {
                    "severity": "WARN",
                    "family": "search_path",
                    "name": name,
                    "direction": "related",
                    "message": (
                        f"함수 '{name}' search_path 불일치: 로컬 {local_info['search_path']} vs "
                        f"운영 {remote_info['search_path']}"
                    ),
                }
            )
        for role in ROLES:
            expected = local_info["grants"].get(role, True)
            actual = remote_info["grants"].get(role)
            if actual is None or expected == actual:
                continue
            findings.append(
                {
                    "severity": "WARN",
                    "family": "grant",
                    "name": name,
                    "direction": "related",
                    "message": (
                        f"함수 '{name}' {role} EXECUTE 불일치: 로컬 시뮬레이션 {expected} vs "
                        f"운영 {actual}(운영 관리 grant일 수 있음, drift 보고)"
                    ),
                }
            )

    return findings


def load_baseline(path: Path) -> dict:
    if not path.exists():
        raise SystemExit(f"baseline 파일 없음: {path} — `--write-baseline`으로 먼저 생성하세요.")
    data = json.loads(path.read_text(encoding="utf-8"))
    return {
        "migrations": data["migrations"],
        "functions": data["functions"],
    }


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    mode = parser.add_mutually_exclusive_group()
    mode.add_argument("--gate", action="store_true", help="live 프로덕션 조회로 배포 gate 실행")
    mode.add_argument(
        "--write-baseline",
        metavar="PATH",
        nargs="?",
        const=str(DEFAULT_BASELINE),
        help="live 조회 결과를 baseline JSON으로 저장(경로 생략 시 기본값)",
    )
    parser.add_argument("--baseline", default=str(DEFAULT_BASELINE))

    args = parser.parse_args()

    local = collect_local()

    if args.write_baseline or args.gate:
        token = os.environ.get("SUPABASE_ACCESS_TOKEN")
        if not token:
            print("ERROR: live 조회에는 SUPABASE_ACCESS_TOKEN 환경변수 필요")
            return 1
        live = fetch_live_production(token)

        if args.write_baseline:
            out_path = Path(args.write_baseline)
            payload = {
                "project_ref": PROJECT_REF,
                "captured_at": date.today().isoformat(),
                "migrations": live["migrations"],
                "functions": live["functions"],
            }
            out_path.parent.mkdir(parents=True, exist_ok=True)
            out_path.write_text(
                json.dumps(payload, ensure_ascii=False, indent=2) + "\n",
                encoding="utf-8",
            )
            print(f"baseline 기록 완료({len(live['migrations'])} migration, {len(live['functions'])} 함수): {out_path}")
            return 0

        findings = compare("gate", local, live)
        baseline = load_baseline(Path(args.baseline))
        baseline_findings = compare("offline", local, baseline)
        print(f"live 프로덕션({PROJECT_REF}) 대비 패리티 gate (baseline: {args.baseline})")
        changed_against_baseline = [
            f for f in baseline_findings if f["direction"] in ("remote_ahead", "related") and f["severity"] == "ERROR"
        ]
        if changed_against_baseline:
            print("사전 기록 baseline 대비 역방향 drift:")
            for finding in changed_against_baseline:
                print(f"  {finding['severity']}: {finding['message']}")
    else:
        baseline = load_baseline(Path(args.baseline))
        findings = compare("offline", local, baseline)
        print(f"커밋된 baseline({args.baseline}) 대비 오프라인 패리티 점검")

    errors = [f for f in findings if f["severity"] == "ERROR"]
    warns = [f for f in findings if f["severity"] == "WARN"]

    for finding in findings:
        print(f"{finding['severity']}: {finding['family']:<12} {finding['name']:<42} {finding['message']}")

    print(f"결과: {len(errors)} ERROR, {len(warns)} WARN")
    return 1 if errors else 0


if __name__ == "__main__":
    raise SystemExit(main())