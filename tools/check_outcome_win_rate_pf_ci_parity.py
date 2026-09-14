"""95% 신뢰구간 계산 & 기대치 판정 fixture의 JSON ↔ SQL ↔ Python 기준값 drift 방지 gate (story 5-8).

`tests/sql/test_outcome_win_rate_pf_ci_gated.sql`은 fixture 행을 candidate_outcome에
직접 삽입하고 같은 데이터가 `tests/fixtures/outcome_win_rate_pf_ci_gated/input_cases.json`에도
병렬로 존재한다(top-level 키: `input_cases`, `expected_rows`). Python 기준값은 5-7과
동일한 표본 게이트(30건 임계값) 로직 위에 승률의 95% Wilson score 신뢰구간(z=1.959963985,
round 4자리)과 전략 A/B/C 고정 기대치(0.6871/0.6895/0.6600) 판정을 더해 전략별(A/B/C/D) +
rollup 전체(strategy=None) 5행을 계산하며, SQL의 `ci_expected` 임시 테이블과 동일해야
한다. 네 경로(JSON 입력행/SQL INSERT행/JSON expected_rows/SQL ci_expected)가 갈라지면
drift를 차단한다.

SQL을 완전히 파싱하지는 않는다. 대신 fixture가 지켜야 하는 형태(구간 marker, 튜플 문법,
`ci_expected` DDL 컬럼 순서)를 전제로 하고, 전제가 깨지면 조용히 통과하는 대신 ERROR로
실패한다(5-7 parity 도구와 동일한 방어 패턴).

실행: `python tools/check_outcome_win_rate_pf_ci_parity.py`
"""

from __future__ import annotations

import json
import math
import re
import sys
from pathlib import Path

# Windows 콘솔 기본 코드페이지(cp949)에서 한국어/기호 출력이 UnicodeEncodeError로 죽지 않게 한다.
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

ROOT = Path(__file__).resolve().parents[1]
SQL_PATH = ROOT / "tests" / "sql" / "test_outcome_win_rate_pf_ci_gated.sql"
FIXTURE_DIR = ROOT / "tests" / "fixtures" / "outcome_win_rate_pf_ci_gated"

SETUP_MARKER = "-- ── parity fixture setup"
CI_EXPECTED_TABLE = "ci_expected"

# parity 구간의 candidate_outcome INSERT 컬럼 목록
INSERT_COLUMNS = (
    "ticker", "strategy", "entry_date", "entry_price", "status",
    "exit_date", "exit_price", "return_pct",
    "cutoff_n", "holding_days", "tp_pct", "sl_pct",
)
NUMERIC_FIELDS = {"entry_price", "exit_price", "return_pct", "cutoff_n", "holding_days", "tp_pct", "sl_pct"}
SETTLED_STATUSES = ("TP", "SL", "TIMEOUT")
VALID_STATUSES = {"TP", "SL", "TIMEOUT", "OPEN", "SUSPENDED", "DELISTED"}
SAMPLE_GATE_MIN_REQUIRED = 30

# migration(202609101500_create_outcome_win_rate_pf_ci_gated.sql)과 동일한 z값
# (scipy.stats.norm.ppf(0.975)를 SQL 리터럴로 고정한 것) — 두 곳이 갈라지면 4dp 동등성이
# 깨지므로 반드시 같은 상수를 쓴다.
Z = 1.959963985

# migration의 `expected` VALUES와 동일한 전략별 고정 백테스트 기대치. D/E/F는 의도적으로
# 여기 없다 — 스펙에 정의되지 않은 전략에 임의의 값을 채우지 않는다는 계약을 코드로 강제.
EXPECTED_WIN_RATE_BY_STRATEGY = {
    "A": 0.6871,
    "B": 0.6895,
    "C": 0.6600,
}

CI_ROW_FIELDS = (
    "total_settled", "wins", "losses", "open_count", "suspended_count", "delisted_count",
    "gross_win", "gross_loss", "win_rate", "profit_factor",
    "sample_gate_min_required", "sample_gate_passed", "sample_gate_label",
    "ci_lower", "ci_upper", "expected_win_rate", "expected_in_ci",
)


# ── 파싱 유틸리티 ─────────────────────────────────────────────

def _setup_region(sql: str) -> str:
    """parity fixture setup 마커 아래의 SQL 구간만 잘라낸다."""
    if SETUP_MARKER not in sql:
        raise SystemExit(
            "ERROR: parity fixture setup 마커를 찾지 못했다 — "
            "fixture 구조가 바뀌었다. 마커를 추가하거나 이 도구를 업데이트하세요."
        )
    return sql.split(SETUP_MARKER, 1)[1]


def _extract_value_tuples(values_block: str) -> list[str]:
    """INSERT VALUES 블록에서 개별 튜플 문자열 ``(…)`` 를 추출한다.

    따옴표로 감싼 문자열 안의 괄호나 이스케이프된 따옴표(``''``)는 튜플
    경계로 오인하지 않는다.
    """
    tuples: list[str] = []
    depth = 0
    start: int | None = None
    in_quote = False
    i = 0
    n = len(values_block)
    while i < n:
        ch = values_block[i]
        if ch == "'":
            if in_quote and i + 1 < n and values_block[i + 1] == "'":
                i += 2
                continue
            in_quote = not in_quote
        elif not in_quote:
            if ch == "(" and depth == 0:
                start = i
                depth = 1
            elif ch == "(" and depth > 0:
                depth += 1
            elif ch == ")" and depth > 0:
                depth -= 1
                if depth == 0 and start is not None:
                    tuples.append(values_block[start + 1 : i])
                    start = None
        i += 1
    return tuples


def _raw_to_python(raw: str):
    """SQL 리터럴 문자열을 Python 값으로 변환한다."""
    raw = raw.strip()
    if raw.upper() == "NULL":
        return None
    if raw.upper() in ("TRUE", "FALSE"):
        return raw.upper() == "TRUE"
    if raw.startswith("'") and raw.endswith("'"):
        return raw[1:-1].replace("''", "'")
    if raw.endswith("::jsonb"):
        return json.loads(raw[: -len("::jsonb")].strip())
    try:
        f = float(raw)
        if f == int(f) and "." not in raw:
            return int(f)
        return f
    except ValueError:
        return raw


def _split_preserving_quotes(s: str) -> list[str]:
    """SQL 리터럴 따옴표 안의 쉼표를 보존하며 분리한다.

    이스케이프된 따옴표(``''``)는 문자열을 닫는 것으로 오인하지 않는다.
    """
    parts: list[str] = []
    current: list[str] = []
    in_quote = False
    i = 0
    n = len(s)
    while i < n:
        ch = s[i]
        if ch == "'":
            if in_quote and i + 1 < n and s[i + 1] == "'":
                current.append("''")
                i += 2
                continue
            in_quote = not in_quote
            current.append(ch)
        elif ch == "," and not in_quote:
            parts.append("".join(current))
            current = []
        else:
            current.append(ch)
        i += 1
    if current:
        parts.append("".join(current))
    return parts


def canonical_4dp(value) -> str | None:
    """round 4 고정 소수 4자리 문자열(부동 정밀도 흔적 상쇄). 비교 기준은 소수 4자리 동등."""
    if value is None:
        return None
    try:
        return f"{round(float(value), 4):.4f}"
    except (TypeError, ValueError):
        return str(value)


# ── SQL 파서 ──────────────────────────────────────────────────

def parse_sql_insert_rows(sql: str) -> list[dict]:
    """parity 구간의 candidate_outcome INSERT 튜플을 파싱한다."""
    region = _setup_region(sql)
    pattern = re.compile(
        r"insert\s+into\s+public\.candidate_outcome\s*\([^)]*\)\s*\n?\s*values\s*(?P<values>.*?);",
        re.DOTALL | re.IGNORECASE,
    )
    match = pattern.search(region)
    if not match:
        raise SystemExit("ERROR: parity 구간에서 candidate_outcome INSERT를 찾지 못했다")
    tuples = _extract_value_tuples(match.group("values"))
    if not tuples:
        raise SystemExit("ERROR: candidate_outcome INSERT에서 튜플을 찾지 못했다")
    rows: list[dict] = []
    for tuple_str in tuples:
        raw_values = _split_preserving_quotes(tuple_str)
        if len(raw_values) != len(INSERT_COLUMNS):
            raise SystemExit(
                f"ERROR: 튜플 컬럼 수 불일치: {len(raw_values)}개 값 vs "
                f"{len(INSERT_COLUMNS)}개 컬럼 ({tuple_str[:60]}…)"
            )
        row = {}
        for col, raw in zip(INSERT_COLUMNS, raw_values):
            row[col] = _raw_to_python(raw)
        rows.append(row)
    return rows


def parse_sql_ci_expected(sql: str) -> list[dict]:
    """ci_expected 임시 테이블의 DDL 컬럼 순서와 INSERT 튜플을 파싱한다.

    컬럼 순서는 `create temp table ci_expected (...)` DDL에서 직접 읽어온다 — 이 순서와
    실제 view의 select 순서가 어긋나면 위치 기준 비교가 조용히 깨질 수 있으므로, DDL을
    유일한 출처로 삼는다(5-6/5-7 parity 도구와 동일한 방어).
    """
    region = _setup_region(sql)
    ddl_pattern = re.compile(
        rf"create\s+temp(?:orary)?\s+table\s+{CI_EXPECTED_TABLE}\s*\((?P<cols>.*?)\)\s*;",
        re.DOTALL | re.IGNORECASE,
    )
    ddl_match = ddl_pattern.search(region)
    if not ddl_match:
        raise SystemExit(f"ERROR: parity 구간에서 {CI_EXPECTED_TABLE} DDL(create temp table)을 찾지 못했다")
    columns = tuple(
        line.strip().split()[0]
        for line in ddl_match.group("cols").split(",")
        if line.strip()
    )

    insert_pattern = re.compile(
        rf"insert\s+into\s+{CI_EXPECTED_TABLE}\s*values\s*(?P<values>.*?);",
        re.DOTALL | re.IGNORECASE,
    )
    match = insert_pattern.search(region)
    if not match:
        raise SystemExit(f"ERROR: parity 구간에서 {CI_EXPECTED_TABLE} INSERT를 찾지 못했다")
    tuples = _extract_value_tuples(match.group("values"))
    if not tuples:
        raise SystemExit(f"ERROR: {CI_EXPECTED_TABLE} INSERT에서 튜플을 찾지 못했다")

    rows: list[dict] = []
    for tuple_str in tuples:
        raw_values = _split_preserving_quotes(tuple_str)
        if len(raw_values) != len(columns):
            raise SystemExit(
                f"ERROR: {CI_EXPECTED_TABLE} 튜플 컬럼 수 불일치: "
                f"{len(raw_values)}개 값 vs {len(columns)}개 필드"
            )
        row = {}
        for col, raw in zip(columns, raw_values):
            row[col] = _raw_to_python(raw)
        rows.append(row)
    return rows


# ── JSON 로더 ─────────────────────────────────────────────────

def load_json_fixture() -> dict:
    """input_cases.json을 로드하고 검증한다."""
    path = FIXTURE_DIR / "input_cases.json"
    if not path.exists():
        raise SystemExit(f"ERROR: fixture 파일 없음: {path}")
    data = json.loads(path.read_text(encoding="utf-8"))
    for key in ("input_cases", "expected_rows"):
        if key not in data:
            raise SystemExit(f"ERROR: {path}에 '{key}' 키가 없다")
    if not isinstance(data["input_cases"], list) or not data["input_cases"]:
        raise SystemExit(f"ERROR: {path}의 input_cases는 비어 있지 않은 배열이어야 한다")
    if not isinstance(data["expected_rows"], list) or not data["expected_rows"]:
        raise SystemExit(f"ERROR: {path}의 expected_rows는 비어 있지 않은 배열이어야 한다")
    return data


# ── 비교 ──────────────────────────────────────────────────────

def _row_key(row: dict) -> tuple:
    return (row["ticker"], row["strategy"], row["entry_date"])


def validate_statuses(rows: list[dict]) -> list[str]:
    """모든 행의 status가 유효한 상태 집합 안에 있는지 검사한다."""
    errors: list[str] = []
    for row in rows:
        status = row.get("status")
        if status not in VALID_STATUSES:
            errors.append(
                f"행 {_row_key(row)} status 불일치: {status!r}는 유효한 상태가 아니다 "
                f"(허용: {sorted(VALID_STATUSES)})"
            )
    return errors


def compare_json_sql_rows(json_rows: list[dict], sql_rows: list[dict]) -> list[str]:
    """JSON input_cases와 SQL candidate_outcome INSERT 행을 완전 일치로 비교한다."""
    errors: list[str] = []
    by_json = {_row_key(r): r for r in json_rows}
    by_sql = {_row_key(r): r for r in sql_rows}

    if len(by_json) != len(json_rows):
        errors.append("input_cases.json의 input_cases에 (ticker,strategy,entry_date) 중복이 있다")
    if len(by_sql) != len(sql_rows):
        errors.append("SQL fixture에 (ticker,strategy,entry_date) 중복이 있다")

    for key in sorted(set(by_json) - set(by_sql), key=str):
        errors.append(f"input_cases.json의 {key}가 SQL fixture에 없다")
    for key in sorted(set(by_sql) - set(by_json), key=str):
        errors.append(f"SQL fixture의 {key}가 input_cases.json에 없다")

    for key in sorted(set(by_json) & set(by_sql), key=str):
        j_row, s_row = by_json[key], by_sql[key]
        for col in INSERT_COLUMNS:
            j_val = j_row.get(col)
            s_val = s_row.get(col)
            if j_val is None and s_val is None:
                continue
            if j_val is None or s_val is None:
                errors.append(f"행 {key} {col} 불일치: JSON {j_val!r} vs SQL {s_val!r}")
                continue
            if col in NUMERIC_FIELDS:
                if float(j_val) != float(s_val):
                    errors.append(f"행 {key} {col} 불일치: JSON {j_val} vs SQL {s_val}")
            elif str(j_val) != str(s_val):
                errors.append(f"행 {key} {col} 불일치: JSON {j_val!r} vs SQL {s_val!r}")

    if len(json_rows) != len(sql_rows):
        errors.append(f"행 수 불일치: JSON {len(json_rows)} vs SQL {len(sql_rows)}")
    return errors


def _ci_row_key(row: dict) -> str | None:
    return row.get("strategy")


def compare_ci_rows(a_rows: list[dict], b_rows: list[dict], a_label: str, b_label: str) -> list[str]:
    """두 CI 게이트 행 리스트(전략별 + rollup 전체)를 strategy 키로 비교한다."""
    errors: list[str] = []
    by_a = {_ci_row_key(r): r for r in a_rows}
    by_b = {_ci_row_key(r): r for r in b_rows}

    for key in sorted((set(by_a) - set(by_b)), key=str):
        errors.append(f"{a_label}의 strategy={key!r} 행이 {b_label}에 없다")
    for key in sorted((set(by_b) - set(by_a)), key=str):
        errors.append(f"{b_label}의 strategy={key!r} 행이 {a_label}에 없다")

    int_fields = ["total_settled", "wins", "losses", "open_count", "suspended_count", "delisted_count", "sample_gate_min_required"]
    gross_fields = ["gross_win", "gross_loss"]
    rate_fields = ["win_rate", "profit_factor", "ci_lower", "ci_upper", "expected_win_rate"]
    bool_fields = ["sample_gate_passed", "expected_in_ci"]

    for key in sorted((set(by_a) & set(by_b)), key=str):
        a_row, b_row = by_a[key], by_b[key]
        for f in int_fields:
            av, bv = a_row.get(f), b_row.get(f)
            if av is None or bv is None:
                if av != bv:
                    errors.append(f"strategy={key!r} {f} 불일치: {a_label}={av!r} vs {b_label}={bv!r}")
                continue
            av, bv = int(av), int(bv)
            if av != bv:
                errors.append(f"strategy={key!r} {f} 불일치: {a_label}={av} vs {b_label}={bv}")
        for f in gross_fields:
            av, bv = a_row.get(f), b_row.get(f)
            if av is None or bv is None:
                if av != bv:
                    errors.append(f"strategy={key!r} {f} 불일치: {a_label}={av} vs {b_label}={bv}")
                continue
            if round(float(av), 4) != round(float(bv), 4):
                errors.append(f"strategy={key!r} {f} 불일치: {a_label}={round(float(av),4)} vs {b_label}={round(float(bv),4)}")
        for f in rate_fields:
            ac, bc = canonical_4dp(a_row.get(f)), canonical_4dp(b_row.get(f))
            if ac != bc:
                errors.append(f"strategy={key!r} {f} 불일치: {a_label}={ac} vs {b_label}={bc}")
        for f in bool_fields:
            av, bv = a_row.get(f), b_row.get(f)
            if av is None or bv is None:
                if av != bv:
                    errors.append(f"strategy={key!r} {f} 불일치: {a_label}={av!r} vs {b_label}={bv!r}")
                continue
            if bool(av) != bool(bv):
                errors.append(f"strategy={key!r} {f} 불일치: {a_label}={bool(av)} vs {b_label}={bool(bv)}")

        a_label_val, b_label_val = a_row.get("sample_gate_label"), b_row.get("sample_gate_label")
        if a_label_val != b_label_val:
            errors.append(
                f"strategy={key!r} sample_gate_label 불일치: {a_label}={a_label_val!r} vs {b_label}={b_label_val!r}"
            )

    return errors


# ── Python 기준값 계산 ────────────────────────────────────────

def _wilson_ci(win_rate: float, total_settled: int) -> tuple[float, float]:
    """migration과 동일한 Wilson score interval 계산(z=1.959963985, round 4자리).

    입력 win_rate는 이미 4dp로 반올림된 값이어야 한다 — view가 base(5-7)의 win_rate
    컬럼(이미 round(...,4))을 그대로 Wilson 공식에 대입하기 때문에, Python 기준값도
    반올림 전 원시 비율이 아니라 반올림된 win_rate로 계산해야 SQL과 4dp까지 일치한다.
    """
    z2 = Z * Z
    denom = 1 + z2 / total_settled
    center = (win_rate + z2 / (2 * total_settled)) / denom
    spread = math.sqrt((win_rate * (1 - win_rate) + z2 / (4 * total_settled)) / total_settled)
    half_width = (Z / denom) * spread
    return round(center - half_width, 4), round(center + half_width, 4)


def compute_reference_rows(rows: list[dict]) -> list[dict]:
    """JSON input_cases로부터 전략별(A/B/...) + rollup 전체(strategy=None) CI/기대치 기준값을 계산한다."""
    strategies = sorted({r["strategy"] for r in rows})
    groups: list[tuple[str | None, list[dict]]] = [(s, [r for r in rows if r["strategy"] == s]) for s in strategies]
    groups.append((None, rows))

    result: list[dict] = []
    for strategy, group_rows in groups:
        settled = [r for r in group_rows if r["status"] in SETTLED_STATUSES]
        total_settled = len(settled)
        wins = sum(1 for r in settled if r["return_pct"] is not None and r["return_pct"] > 0)
        losses = sum(1 for r in settled if r["return_pct"] is not None and r["return_pct"] < 0)

        gross_win = sum(r["return_pct"] for r in settled if r["return_pct"] is not None and r["return_pct"] > 0)
        gross_loss = abs(sum(r["return_pct"] for r in settled if r["return_pct"] is not None and r["return_pct"] < 0))

        gate_passed = total_settled >= SAMPLE_GATE_MIN_REQUIRED
        win_rate = round(wins / total_settled, 4) if gate_passed and total_settled > 0 else None
        # SQL의 sum(...) filter(...)는 승리(혹은 패배) 거래가 하나도 없으면 NULL을 반환하고
        # NULL/x는 NULL이 된다(5-7 parity 도구와 동일한 방어).
        profit_factor = (
            round(gross_win / gross_loss, 4)
            if gate_passed and wins > 0 and gross_loss > 0
            else None
        )
        label = None if gate_passed else f"표본 부족 ({total_settled}/30)"

        ci_lower = ci_upper = None
        if gate_passed and win_rate is not None:
            ci_lower, ci_upper = _wilson_ci(win_rate, total_settled)

        expected_win_rate = None
        expected_in_ci = None
        if gate_passed and strategy in EXPECTED_WIN_RATE_BY_STRATEGY:
            expected_win_rate = EXPECTED_WIN_RATE_BY_STRATEGY[strategy]
            expected_in_ci = ci_lower <= expected_win_rate <= ci_upper

        result.append({
            "strategy": strategy,
            "total_settled": total_settled,
            "wins": wins,
            "losses": losses,
            "open_count": sum(1 for r in group_rows if r["status"] == "OPEN"),
            "suspended_count": sum(1 for r in group_rows if r["status"] == "SUSPENDED"),
            "delisted_count": sum(1 for r in group_rows if r["status"] == "DELISTED"),
            "gross_win": gross_win if wins > 0 else None,
            "gross_loss": gross_loss if losses > 0 else None,
            "win_rate": win_rate,
            "profit_factor": profit_factor,
            "sample_gate_min_required": SAMPLE_GATE_MIN_REQUIRED,
            "sample_gate_passed": gate_passed,
            "sample_gate_label": label,
            "ci_lower": ci_lower,
            "ci_upper": ci_upper,
            "expected_win_rate": expected_win_rate,
            "expected_in_ci": expected_in_ci,
        })
    return result


# ── main ──────────────────────────────────────────────────────

def main() -> int:
    if not SQL_PATH.exists():
        print(f"ERROR: SQL fixture 없음: {SQL_PATH}")
        return 1

    sql = SQL_PATH.read_text(encoding="utf-8")
    fixture = load_json_fixture()
    json_rows = fixture["input_cases"]
    json_expected = fixture["expected_rows"]

    sql_rows = parse_sql_insert_rows(sql)
    sql_expected = parse_sql_ci_expected(sql)

    errors: list[str] = []

    # 0. status 값 사전 검증
    errors += validate_statuses(json_rows)

    # 1. JSON input_cases ↔ SQL INSERT 행 대조
    errors += compare_json_sql_rows(json_rows, sql_rows)

    # 2. Python 기준값 계산(전략별 + rollup 전체)
    ref_rows = compute_reference_rows(json_rows)

    # 3. Python 기준값 ↔ JSON expected_rows 대조
    errors += compare_ci_rows(ref_rows, json_expected, "Python 기준값", "JSON expected_rows")

    # 4. Python 기준값 ↔ SQL ci_expected 대조
    errors += compare_ci_rows(ref_rows, sql_expected, "Python 기준값", "SQL ci_expected")

    # 5. JSON expected_rows ↔ SQL ci_expected 대조(직접 비교로 위 두 대조의 이행성 확인)
    errors += compare_ci_rows(json_expected, sql_expected, "JSON expected_rows", "SQL ci_expected")

    for error in errors:
        print(f"ERROR: {error}")
    if errors:
        print(
            f"결과: {len(errors)} ERROR - CI/기대치 판정 fixture의 JSON/SQL/Python이 갈라졌다. "
            "세 쪽을 함께 고치세요."
        )
        return 1

    total_row = next(r for r in ref_rows if r["strategy"] is None)
    print(
        f"story 5-8 win_rate_pf ci gated fixture drift 없음 "
        f"(행 {len(json_rows)}건, 전략 {len(ref_rows) - 1}개, "
        f"전체 total_settled={total_row['total_settled']}, "
        f"ci=[{total_row['ci_lower']}, {total_row['ci_upper']}])"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
