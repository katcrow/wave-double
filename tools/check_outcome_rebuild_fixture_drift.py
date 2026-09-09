"""outcome rebuild fixture의 JSON ↔ SQL drift 방지 gate (epic-3-retro-item-17).

`tests/sql/test_outcome_rebuild.sql`은 샘플 장부를 SQL에 인라인으로 적어 넣고,
같은 데이터가 `tests/fixtures/outcome_rebuild/*.json`에도 병렬로 존재한다. JSON 쪽은
어떤 코드도 읽지 않기 때문에(SQL 주석이 "동일 데이터"라고만 주장한다) 한쪽만 고쳐도
아무도 알아채지 못하는 구조였다 — 진실의 원천이 둘이면 조용히 갈라진다.

이 gate는 세 파일을 SQL fixture에서 실제로 파싱한 값과 대조해 그 drift를 차단한다.

- events.json        ↔ `insert into public.outcome_events ... values (...)` 튜플
- observations.json  ↔ `insert into public.outcome_observations ... values (...)` 튜플
- expected_projection.json ↔ AC1 구간의 `candidate_outcome` 기대 assertion

SQL을 완전히 파싱하지는 않는다. 대신 fixture가 지켜야 하는 형태(구간 marker, 튜플 문법)를
전제로 하고, 전제가 깨지면 조용히 통과하는 대신 ERROR로 실패한다.

실행: `python tools/check_outcome_rebuild_fixture_drift.py`
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
SQL_PATH = ROOT / "tests" / "sql" / "test_outcome_rebuild.sql"
FIXTURE_DIR = ROOT / "tests" / "fixtures" / "outcome_rebuild"

# 구간 marker. JSON fixture 3종은 AC1 샘플 장부 하나만 기술한다 -- Story 6.5 legacy 케이스나
# idempotency 재확인처럼 AC1 구간 밖에서 따로 삽입/검증하는 행은 JSON의 대상이 아니다.
SETUP_BEGIN = "-- ── fixture setup"
AC1_BEGIN = "-- ── AC1:"
AC1_END = "-- 정확히"

EVENT_TUPLE = re.compile(
    r"\(\s*'(?P<event_id>[0-9a-f-]{36})'\s*,\s*"
    r"'(?P<ticker>[^']*)'\s*,\s*"
    r"'(?P<strategy>[^']*)'\s*,\s*"
    r"'(?P<command_type>[^']*)'\s*,\s*"
    r"'(?P<logical_run_key>[^']*)'\s*,\s*"
    r"'(?P<payload>\{.*?\})'::jsonb\s*\)",
    re.DOTALL,
)
OBSERVATION_TUPLE = re.compile(
    r"\(\s*'(?P<outcome_id>[0-9a-f-]{36})'\s*,\s*"
    r"date\s*'(?P<evaluation_trading_day>[0-9-]{10})'\s*,\s*"
    r"(?P<high>-?[0-9.]+)\s*,\s*"
    r"(?P<low>-?[0-9.]+)\s*,\s*"
    r"(?P<close>-?[0-9.]+)\s*,\s*"
    r"'(?P<result_code>[A-Z_]+)'\s*\)"
)
ASSERTION_BLOCK = re.compile(
    r"select\s+1\s+from\s+public\.candidate_outcome\s*\n(?P<body>.*?)\)\s*then",
    re.DOTALL | re.IGNORECASE,
)
NUMERIC_FIELDS = ("entry_price", "exit_price", "return_pct", "cutoff_n", "holding_days")
PROJECTION_FIELDS = (
    "ticker",
    "strategy",
    "entry_date",
    "entry_price",
    "status",
    "exit_date",
    "exit_price",
    "return_pct",
    "cutoff_n",
    "holding_days",
)


def load_json(name: str) -> list[dict]:
    path = FIXTURE_DIR / name
    if not path.exists():
        raise SystemExit(f"ERROR: fixture 파일 없음: {path}")
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data, list) or not data:
        raise SystemExit(f"ERROR: {path}는 비어 있지 않은 JSON 배열이어야 한다")
    return data


def ac1_setup_region(sql: str) -> str:
    """AC1 샘플 장부를 삽입하는 구간만 잘라낸다(JSON fixture가 기술하는 범위)."""
    if SETUP_BEGIN not in sql:
        raise SystemExit(f"ERROR: setup 구간 marker('{SETUP_BEGIN}')를 찾지 못했다 - fixture 구조가 바뀌었다")
    region = sql.split(SETUP_BEGIN, 1)[1]
    if AC1_BEGIN not in region:
        raise SystemExit(f"ERROR: AC1 구간 marker('{AC1_BEGIN}')를 찾지 못했다 - fixture 구조가 바뀌었다")
    return region.split(AC1_BEGIN, 1)[0]


def insert_section(sql: str, table: str) -> str:
    """`insert into public.<table> ... values ...;` 구절을 모두 이어붙인다."""
    pattern = re.compile(
        rf"insert\s+into\s+public\.{table}\s*\([^)]*\)\s*\n?\s*values(?P<values>.*?);",
        re.DOTALL | re.IGNORECASE,
    )
    chunks = [m.group("values") for m in pattern.finditer(sql)]
    if not chunks:
        raise SystemExit(f"ERROR: {SQL_PATH.name}에서 public.{table} insert 구절을 찾지 못했다")
    return "\n".join(chunks)


def number(raw: str) -> float:
    return float(raw)


def parse_sql_events(sql: str) -> list[dict]:
    section = insert_section(ac1_setup_region(sql), "outcome_events")
    rows = []
    for match in EVENT_TUPLE.finditer(section):
        row = match.groupdict()
        # SQL 인라인 payload는 공백 없는 압축 표기다. 의미 비교를 위해 JSON으로 정규화한다.
        row["payload"] = json.loads(row["payload"])
        rows.append(row)
    return rows


def parse_sql_observations(sql: str) -> list[dict]:
    section = insert_section(ac1_setup_region(sql), "outcome_observations")
    rows = []
    for match in OBSERVATION_TUPLE.finditer(section):
        row = match.groupdict()
        for field in ("high", "low", "close"):
            row[field] = number(row[field])
        rows.append(row)
    return rows


def parse_sql_expected_projection(sql: str) -> list[dict]:
    if AC1_BEGIN not in sql:
        raise SystemExit(f"ERROR: AC1 구간 marker('{AC1_BEGIN}')를 찾지 못했다 - fixture 구조가 바뀌었다")
    region = sql.split(AC1_BEGIN, 1)[1]
    if AC1_END not in region:
        raise SystemExit(f"ERROR: AC1 종료 marker('{AC1_END}')를 찾지 못했다 - fixture 구조가 바뀌었다")
    region = region.split(AC1_END, 1)[0]

    rows = []
    for block in ASSERTION_BLOCK.finditer(region):
        body = block.group("body")
        row: dict = {}
        for field in PROJECTION_FIELDS:
            if re.search(rf"\b{field}\s+is\s+null\b", body, re.IGNORECASE):
                row[field] = None
                continue
            text_match = re.search(rf"\b{field}\s*=\s*(?:date\s*)?'([^']*)'", body)
            if text_match:
                row[field] = text_match.group(1)
                continue
            num_match = re.search(rf"\b{field}\s*=\s*(-?[0-9.]+)", body)
            if num_match:
                row[field] = number(num_match.group(1))
        rows.append(row)
    return rows


def normalize_json_projection(row: dict) -> dict:
    out = {}
    for field in PROJECTION_FIELDS:
        value = row.get(field)
        out[field] = number(value) if field in NUMERIC_FIELDS and value is not None else value
    return out


def key_of(row: dict) -> tuple:
    return (row.get("ticker"), row.get("strategy"), row.get("entry_date"))


def compare_events(json_rows: list[dict], sql_rows: list[dict]) -> list[str]:
    errors: list[str] = []
    by_json = {r["event_id"]: r for r in json_rows}
    by_sql = {r["event_id"]: r for r in sql_rows}

    if len(by_json) != len(json_rows):
        errors.append("events.json에 중복 event_id가 있다")
    if len(by_sql) != len(sql_rows):
        errors.append("SQL fixture에 중복 event_id가 있다")

    for event_id in sorted(set(by_json) - set(by_sql)):
        errors.append(f"events.json의 event_id {event_id}가 SQL fixture에 없다")
    for event_id in sorted(set(by_sql) - set(by_json)):
        errors.append(f"SQL fixture의 event_id {event_id}가 events.json에 없다")

    for event_id in sorted(set(by_json) & set(by_sql)):
        for field in ("ticker", "strategy", "command_type", "logical_run_key", "payload"):
            left, right = by_json[event_id].get(field), by_sql[event_id].get(field)
            if left != right:
                errors.append(f"event {event_id} {field} 불일치: JSON {left!r} vs SQL {right!r}")
    return errors


def compare_observations(json_rows: list[dict], sql_rows: list[dict]) -> list[str]:
    errors: list[str] = []

    def norm(row: dict) -> tuple:
        return (
            row["outcome_id"],
            row["evaluation_trading_day"],
            number(row["high"]),
            number(row["low"]),
            number(row["close"]),
            row["result_code"],
        )

    left = sorted(norm(r) for r in json_rows)
    right = sorted(norm(r) for r in sql_rows)
    for row in sorted(set(left) - set(right)):
        errors.append(f"observations.json의 관찰 행이 SQL fixture에 없다: {row}")
    for row in sorted(set(right) - set(left)):
        errors.append(f"SQL fixture의 관찰 행이 observations.json에 없다: {row}")
    if len(left) != len(right):
        errors.append(f"관찰 행 개수 불일치: JSON {len(left)} vs SQL {len(right)}")
    return errors


def compare_projection(json_rows: list[dict], sql_rows: list[dict]) -> list[str]:
    errors: list[str] = []
    by_json = {key_of(r): normalize_json_projection(r) for r in json_rows}
    by_sql = {key_of(r): r for r in sql_rows}

    if len(by_json) != len(json_rows):
        errors.append("expected_projection.json에 (ticker,strategy,entry_date) 중복이 있다")
    if len(by_sql) != len(sql_rows):
        errors.append("SQL AC1 assertion에 (ticker,strategy,entry_date) 중복이 있다")

    for key in sorted(set(by_json) - set(by_sql), key=str):
        errors.append(f"expected_projection.json의 {key}에 대응하는 SQL AC1 assertion이 없다")
    for key in sorted(set(by_sql) - set(by_json), key=str):
        errors.append(f"SQL AC1 assertion의 {key}가 expected_projection.json에 없다")

    for key in sorted(set(by_json) & set(by_sql), key=str):
        expected, actual = by_json[key], by_sql[key]
        for field in PROJECTION_FIELDS:
            if field not in actual:
                # SQL assertion이 이 필드를 아예 검증하지 않는 것은 허용한다(예: 100004의 tp_pct).
                continue
            if expected[field] != actual[field]:
                errors.append(
                    f"projection {key} {field} 불일치: JSON {expected[field]!r} vs SQL {actual[field]!r}"
                )
    return errors


def check_row_count_assertion(sql: str, expected_rows: int) -> list[str]:
    """fixture가 주장하는 재구축 행 수가 expected_projection 길이와 같은지 확인한다."""
    counts = {int(m) for m in re.findall(r"expected (\d+) rebuilt rows", sql)}
    counts |= {int(m) for m in re.findall(r"idempotent rebuild: expected (\d+) rows", sql)}
    if not counts:
        return ["SQL fixture에서 재구축 행 수 assertion을 찾지 못했다"]
    wrong = sorted(c for c in counts if c != expected_rows)
    return [
        f"재구축 행 수 assertion {c}가 expected_projection.json 행 수 {expected_rows}와 다르다"
        for c in wrong
    ]


def main() -> int:
    if not SQL_PATH.exists():
        print(f"ERROR: SQL fixture 없음: {SQL_PATH}")
        return 1
    sql = SQL_PATH.read_text(encoding="utf-8")

    events = load_json("events.json")
    observations = load_json("observations.json")
    projection = load_json("expected_projection.json")

    errors: list[str] = []
    errors += compare_events(events, parse_sql_events(sql))
    errors += compare_observations(observations, parse_sql_observations(sql))
    errors += compare_projection(projection, parse_sql_expected_projection(sql))
    errors += check_row_count_assertion(sql, len(projection))

    for error in errors:
        print(f"ERROR: {error}")
    if errors:
        print(
            f"결과: {len(errors)} ERROR - outcome rebuild fixture의 JSON과 SQL이 갈라졌다. "
            "두 쪽을 함께 고치세요."
        )
        return 1

    print(
        "outcome rebuild fixture drift 없음 "
        f"(이벤트 {len(events)}건, 관찰 {len(observations)}건, projection {len(projection)}행)"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
