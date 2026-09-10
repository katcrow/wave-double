"""승률·PF fixture의 JSON ↔ SQL ↔ Python 기준값 drift 방지 gate (story 5-5).

`tests/sql/test_outcome_win_rate_pf.sql`은 fixture 행을 candidate_outcome에 직접 삽입하고
같은 데이터가 `tests/fixtures/outcome_win_rate_pf/input_cases.json`에도 병렬로 존재한다.
Python 기준값은 backtest metrics와 동일한 산식으로 JSON으로부터 계산하며, SQL assertion 값과
동일해야 한다. 세 경로가 갈라지면 drift를 차단한다.

SQL을 완전히 파싱하지는 않는다. 대신 fixture가 지켜야 하는 형태(구간 marker, 튜플 문법)를
전제로 하고, 전제가 깨지면 조용히 통과하는 대신 ERROR로 실패한다.

실행: `python tools/check_outcome_win_rate_pf_parity.py`
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

# Windows 콘솔 기본 코드페이지(cp949)에서 한국어/기호 출력이 UnicodeEncodeError로 죽지 않게 한다.
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

ROOT = Path(__file__).resolve().parents[1]
SQL_PATH = ROOT / "tests" / "sql" / "test_outcome_win_rate_pf.sql"
FIXTURE_DIR = ROOT / "tests" / "fixtures" / "outcome_win_rate_pf"

SETUP_MARKER = "-- ── parity fixture setup"
EXPECTED_MARKER = "insert into win_pf_expected values"

# parity 구간의 candidate_outcome INSERT 컬럼 목록
INSERT_COLUMNS = (
    "ticker", "strategy", "entry_date", "entry_price", "status",
    "exit_date", "exit_price", "return_pct",
    "cutoff_n", "holding_days", "tp_pct", "sl_pct",
)
NUMERIC_FIELDS = {"entry_price", "exit_price", "return_pct", "cutoff_n", "holding_days", "tp_pct", "sl_pct"}
SETTLED_STATUSES = ("TP", "SL", "TIMEOUT")
VALID_STATUSES = {"TP", "SL", "TIMEOUT", "OPEN", "SUSPENDED", "DELISTED"}


# ── 파싱 유틸리티 ─────────────────────────────────────────────

def _setup_region(sql: str) -> str:
    """parity fixture setup 마커 아래의 candidate_outcome INSERT만 잘라낸다."""
    if SETUP_MARKER not in sql:
        raise SystemExit(
            "ERROR: parity fixture setup 마커를 찾지 못했다 — "
            "fixture 구조가 바뀌었다. 마커를 추가하거나 이 도구를 업데이트하세요."
        )
    return sql.split(SETUP_MARKER, 1)[1]


def _extract_value_tuples(values_block: str) -> list[str]:
    """INSERT VALUES 블록에서 개별 튜플 문자열 ``(…)`` 를 추출한다."""
    tuples: list[str] = []
    depth = 0
    start: int | None = None
    for i, ch in enumerate(values_block):
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
    return tuples


def _raw_to_python(raw: str):
    """SQL 리터럴 문자열을 Python 값으로 변환한다."""
    raw = raw.strip()
    if raw.upper() == "NULL":
        return None
    if raw.startswith("'") and raw.endswith("'"):
        return raw[1:-1]
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
    """SQL 리터럴 따옴표 안의 쉼표를 보존하며 분리한다."""
    parts: list[str] = []
    current: list[str] = []
    in_quote = False
    for ch in s:
        if ch == "'":
            in_quote = not in_quote
            current.append(ch)
        elif ch == "," and not in_quote:
            parts.append("".join(current))
            current = []
        else:
            current.append(ch)
    if current:
        parts.append("".join(current))
    return parts


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


def parse_sql_expected(sql: str) -> dict:
    """win_pf_expected INSERT 튜플을 파싱한다."""
    for line in sql.splitlines():
        stripped = line.strip()
        if stripped.lower().startswith(EXPECTED_MARKER):
            m = re.search(r"values\s*\(([^)]+)\)", stripped)
            if not m:
                raise SystemExit("ERROR: win_pf_expected VALUES 튜플을 파싱할 수 없다")
            raw_values = _split_preserving_quotes(m.group(1))
            expected_fields = [
                "total_settled", "wins", "losses", "open_count",
                "suspended_count", "delisted_count",
                "gross_win", "gross_loss", "win_rate", "profit_factor",
            ]
            if len(raw_values) != len(expected_fields):
                raise SystemExit(
                    f"ERROR: win_pf_expected 컬럼 수 불일치: "
                    f"{len(raw_values)}개 값 vs {len(expected_fields)}개 필드"
                )
            result: dict = {}
            for field, raw in zip(expected_fields, raw_values):
                result[field] = _raw_to_python(raw)
            return result
    raise SystemExit("ERROR: win_pf_expected INSERT를 찾지 못했다")


# ── JSON 로더 ─────────────────────────────────────────────────

def load_json_input_cases() -> list[dict]:
    """input_cases.json을 로드하고 검증한다."""
    path = FIXTURE_DIR / "input_cases.json"
    if not path.exists():
        raise SystemExit(f"ERROR: fixture 파일 없음: {path}")
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, list) or not data:
        raise SystemExit(f"ERROR: {path}는 비어 있지 않은 JSON 배열이어야 한다")
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


def compare_json_sql_rows(
    json_rows: list[dict], sql_rows: list[dict]
) -> list[str]:
    """JSON 행과 SQL INSERT 행을 완전 일치로 비교한다."""
    errors: list[str] = []
    by_json = {_row_key(r): r for r in json_rows}
    by_sql = {_row_key(r): r for r in sql_rows}

    if len(by_json) != len(json_rows):
        errors.append("input_cases.json에 (ticker,strategy,entry_date) 중복이 있다")
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
                errors.append(
                    f"행 {key} {col} 불일치: JSON {j_val!r} vs SQL {s_val!r}"
                )
                continue
            if col in NUMERIC_FIELDS:
                if float(j_val) != float(s_val):
                    errors.append(
                        f"행 {key} {col} 불일치: JSON {j_val} vs SQL {s_val}"
                    )
            elif str(j_val) != str(s_val):
                errors.append(
                    f"행 {key} {col} 불일치: JSON {j_val!r} vs SQL {s_val!r}"
                )

    if len(json_rows) != len(sql_rows):
        errors.append(
            f"행 수 불일치: JSON {len(json_rows)} vs SQL {len(sql_rows)}"
        )
    return errors


# ── Python 기준값 계산 ────────────────────────────────────────

def compute_reference(rows: list[dict]) -> dict:
    """JSON 행으로부터 backtest metrics와 동일한 산식의 기준값을 계산한다."""
    settled = [r for r in rows if r["status"] in SETTLED_STATUSES]
    total_settled = len(settled)
    wins = sum(1 for r in settled if r["return_pct"] is not None and r["return_pct"] > 0)
    losses = sum(1 for r in settled if r["return_pct"] is not None and r["return_pct"] < 0)

    gross_win = sum(
        r["return_pct"] for r in settled
        if r["return_pct"] is not None and r["return_pct"] > 0
    )
    gross_loss = abs(sum(
        r["return_pct"] for r in settled
        if r["return_pct"] is not None and r["return_pct"] < 0
    ))

    win_rate = round(wins / total_settled, 4) if total_settled > 0 else None
    profit_factor = round(gross_win / gross_loss, 4) if gross_loss > 0 else None

    return {
        "total_settled": total_settled,
        "wins": wins,
        "losses": losses,
        "open_count": sum(1 for r in rows if r["status"] == "OPEN"),
        "suspended_count": sum(1 for r in rows if r["status"] == "SUSPENDED"),
        "delisted_count": sum(1 for r in rows if r["status"] == "DELISTED"),
        "gross_win": gross_win if wins > 0 else None,
        "gross_loss": gross_loss if losses > 0 else None,
        "win_rate": win_rate,
        "profit_factor": profit_factor,
    }


def canonical_4dp(value) -> str | None:
    """round 4 고정 소수 4자리 문자열(부동 정밀도 흔적 상쇄). 비교 기준은 소수 4자리 동등."""
    if value is None:
        return None
    try:
        return f"{round(float(value), 4):.4f}"
    except (TypeError, ValueError):
        return str(value)


def compare_reference_vs_expected(
    ref: dict, expected: dict
) -> list[str]:
    """Python 기준값과 SQL 기대 튜플을 성분 단위로 비교한다."""
    errors: list[str] = []
    int_fields = [
        "total_settled", "wins", "losses",
        "open_count", "suspended_count", "delisted_count",
    ]
    for field in int_fields:
        if int(ref[field]) != int(expected[field]):
            errors.append(
                f"{field} 불일치: Python {ref[field]} vs SQL expected {expected[field]}"
            )
    for field in ("gross_win", "gross_loss"):
        ref_val = ref[field]
        exp_val = expected[field]
        if ref_val is None or exp_val is None:
            if ref_val != exp_val:
                errors.append(
                    f"{field} 불일치: Python {ref_val} vs SQL expected {exp_val}"
                )
            continue
        if round(float(ref_val), 4) != round(float(exp_val), 4):
            errors.append(
                f"{field} 불일치: Python {round(float(ref_val),4)} "
                f"vs SQL expected {round(float(exp_val),4)}"
            )
    for field in ("win_rate", "profit_factor"):
        ref_canon = canonical_4dp(ref[field])
        exp_canon = canonical_4dp(expected[field])
        if ref_canon != exp_canon:
            errors.append(
                f"{field} 불일치: Python {ref_canon} vs SQL expected {exp_canon}"
            )
    return errors


# ── main ──────────────────────────────────────────────────────

def main() -> int:
    if not SQL_PATH.exists():
        print(f"ERROR: SQL fixture 없음: {SQL_PATH}")
        return 1

    sql = SQL_PATH.read_text(encoding="utf-8")
    json_rows = load_json_input_cases()
    sql_rows = parse_sql_insert_rows(sql)
    sql_expected = parse_sql_expected(sql)

    errors: list[str] = []

    # 0. status 값 사전 검증: 오타/미지원 상태가 조용히 빠지지 않게 한다.
    errors += validate_statuses(json_rows)

    # 1. JSON ↔ SQL INSERT 행 대조
    errors += compare_json_sql_rows(json_rows, sql_rows)

    # 2. JSON 기준값 계산 ↔ SQL assertion 대조
    ref = compute_reference(json_rows)
    errors += compare_reference_vs_expected(ref, sql_expected)

    for error in errors:
        print(f"ERROR: {error}")
    if errors:
        print(
            f"결과: {len(errors)} ERROR - 승률·PF fixture의 JSON/SQL/Python이 갈라졌다. "
            "세 쪽을 함께 고치세요."
        )
        return 1

    print(
        f"story 5-5 win_rate_pf fixture drift 없음 "
        f"(행 {len(json_rows)}건, total_settled={ref['total_settled']}, "
        f"win_rate={ref['win_rate']}, profit_factor={ref['profit_factor']})"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
