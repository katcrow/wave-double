"""전략×원천 분리 승률·PF fixture의 JSON ↔ SQL ↔ Python 기준값 drift 방지 gate (story 5-6).

tests/sql/test_outcome_win_rate_pf_by_strategy_source.sql은 fixture 행을
logical_runs/runs/candidates/candidate_source_contrib/candidate_outcome에 직접 삽입하고
candidate_outcome_win_rate_pf_by_strategy_source view 조회 결과를 src_expected와 대조한다.
같은 데이터가 tests/fixtures/outcome_win_rate_pf_by_strategy_source/input_cases.json에도 병렬로 존재한다.
Python 기준값은 backtest metrics와 동일한 산식으로 JSON으로부터 primary pick과 셀 계산을 수행하며,
SQL assertion 값과 동일해야 한다. 네 경로(JSON/SQL 행/SQL 셀/Python 기준값)가 갈라지면 drift를 차단한다.

실행: python tools/check_outcome_win_rate_pf_source_parity.py
"""

from __future__ import annotations

import json
import re
import sys
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

ROOT = Path(__file__).resolve().parents[1]
SQL_PATH = ROOT / "tests" / "sql" / "test_outcome_win_rate_pf_by_strategy_source.sql"
FIXTURE_DIR = ROOT / "tests" / "fixtures" / "outcome_win_rate_pf_by_strategy_source"

SETUP_MARKER = "-- ── parity fixture setup"

# source 우선순위: t1859 > t1852 > t1856 (index가 낮을수록 우선)
SOURCE_PRIORITY = {"t1859": 0, "t1852": 1, "t1856": 2}
VALID_SOURCES = {"t1859", "t1852", "t1856"}
SETTLED_STATUSES = ("TP", "SL", "TIMEOUT")
VALID_STATUSES = {"TP", "SL", "TIMEOUT", "OPEN", "SUSPENDED", "DELISTED"}

# candidate_outcome INSERT 컬럼 (parity 파서 대상)
OUTCOME_COLUMNS = (
    "ticker", "strategy", "entry_date", "entry_price", "status",
    "exit_date", "exit_price", "return_pct",
    "cutoff_n", "holding_days", "tp_pct", "sl_pct",
)
NUMERIC_OUTCOME_FIELDS = {"entry_price", "exit_price", "return_pct", "cutoff_n", "holding_days", "tp_pct", "sl_pct"}


# ── 파싱 유틸리티 ─────────────────────────────────────────────

def _setup_region(sql: str) -> str:
    if SETUP_MARKER not in sql:
        raise SystemExit(
            "ERROR: parity fixture setup 마커를 찾지 못했다 — "
            "fixture 구조가 바뀌었다. 마커를 추가하거나 이 도구를 업데이트하세요."
        )
    return sql.split(SETUP_MARKER, 1)[1]


def _extract_value_tuples(values_block: str) -> list[str]:
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
    raw = raw.strip()
    if raw.upper() == "NULL":
        return None
    if raw.startswith("'") and raw.endswith("'"):
        return raw[1:-1]
    if raw.endswith("::jsonb"):
        return json.loads(raw[: -len("::jsonb")].strip())
    if raw.upper() in ("TRUE", "FALSE"):
        return raw.upper() == "TRUE"
    try:
        f = float(raw)
        if f == int(f) and "." not in raw:
            return int(f)
        return f
    except ValueError:
        return raw


def _split_preserving_quotes(s: str) -> list[str]:
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


def canonical_4dp(value) -> str | None:
    if value is None:
        return None
    try:
        return f"{round(float(value), 4):.4f}"
    except (TypeError, ValueError):
        return str(value)


# ── SQL 파서 ──────────────────────────────────────────────────

def parse_sql_logical_runs(region: str) -> list[dict]:
    pattern = re.compile(
        r"insert\s+into\s+public\.logical_runs\s*\([^)]*\)\s*\n?\s*values\s*(?P<values>.*?);",
        re.DOTALL | re.IGNORECASE,
    )
    match = pattern.search(region)
    if not match:
        raise SystemExit("ERROR: parity 구간에서 logical_runs INSERT를 찾지 못했다")
    tuples = _extract_value_tuples(match.group("values"))
    rows: list[dict] = []
    for tuple_str in tuples:
        raw_values = _split_preserving_quotes(tuple_str)
        if len(raw_values) != 3:
            raise SystemExit(f"ERROR: logical_runs 튜플 컬럼 수 불일치: {len(raw_values)} ({tuple_str[:60]})")
        rows.append({
            "logical_run_key": _raw_to_python(raw_values[0]),
            "trading_day": _raw_to_python(raw_values[1]),
            "batch_kind": _raw_to_python(raw_values[2]),
        })
    return rows


def parse_sql_canonicals(region: str) -> list[dict]:
    pattern = re.compile(
        r"update\s+public\.logical_runs\s+set\s+canonical_success_run_id\s*=\s*'([^']+)'\s+"
        r"where\s+logical_run_key\s*=\s*'(close:[^']+)'",
        re.DOTALL | re.IGNORECASE,
    )
    results: list[dict] = []
    for m in pattern.finditer(region):
        run_id = m.group(1)
        key = m.group(2)
        trading_day = key.split(":", 1)[1]
        results.append({"trading_day": trading_day, "attempt_run_id": run_id})
    if not results:
        raise SystemExit("ERROR: parity 구간에서 canonical update를 찾지 못했다")
    return results


def parse_sql_candidates(region: str) -> list[dict]:
    columns = ("candidate_id", "attempt_run_id", "ticker", "trading_day", "trading_value")
    pattern = re.compile(
        r"insert\s+into\s+public\.candidates\s*\([^)]*\)\s*\n?\s*values\s*(?P<values>.*?);",
        re.DOTALL | re.IGNORECASE,
    )
    match = pattern.search(region)
    if not match:
        raise SystemExit("ERROR: parity 구간에서 candidates INSERT를 찾지 못했다")
    tuples = _extract_value_tuples(match.group("values"))
    if not tuples:
        raise SystemExit("ERROR: candidates INSERT에서 튜플을 찾지 못했다")
    rows: list[dict] = []
    for tuple_str in tuples:
        raw_values = _split_preserving_quotes(tuple_str)
        if len(raw_values) != 5:
            raise SystemExit(f"ERROR: candidates 튜플 컬럼 수 불일치: {len(raw_values)} ({tuple_str[:60]})")
        row = {}
        for col, raw in zip(columns, raw_values):
            row[col] = _raw_to_python(raw)
        rows.append(row)
    return rows


def parse_sql_contributors(region: str) -> list[dict]:
    columns = ("candidate_id", "attempt_run_id", "source", "contribution_weight")
    pattern = re.compile(
        r"insert\s+into\s+public\.candidate_source_contrib\s*\([^)]*\)\s*\n?\s*values\s*(?P<values>.*?);",
        re.DOTALL | re.IGNORECASE,
    )
    match = pattern.search(region)
    if not match:
        raise SystemExit("ERROR: parity 구간에서 candidate_source_contrib INSERT를 찾지 못했다")
    tuples = _extract_value_tuples(match.group("values"))
    if not tuples:
        raise SystemExit("ERROR: candidate_source_contrib INSERT에서 튜플을 찾지 못했다")
    rows: list[dict] = []
    for tuple_str in tuples:
        raw_values = _split_preserving_quotes(tuple_str)
        if len(raw_values) != 4:
            raise SystemExit(f"ERROR: contributor 튜플 컬럼 수 불일치: {len(raw_values)} ({tuple_str[:60]})")
        row = {}
        for col, raw in zip(columns, raw_values):
            row[col] = _raw_to_python(raw)
        rows.append(row)
    return rows


def parse_sql_outcomes(region: str) -> list[dict]:
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
        if len(raw_values) != len(OUTCOME_COLUMNS):
            raise SystemExit(
                f"ERROR: outcome 튜플 컬럼 수 불일치: {len(raw_values)}개 값 vs "
                f"{len(OUTCOME_COLUMNS)}개 컬럼 ({tuple_str[:60]})"
            )
        row = {}
        for col, raw in zip(OUTCOME_COLUMNS, raw_values):
            row[col] = _raw_to_python(raw)
        rows.append(row)
    return rows


def parse_sql_cells(region: str) -> list[dict]:
    """src_expected INSERT 튜플을 파싱한다.

    컬럼 순서는 `create temp table src_expected (...)` DDL에서 직접 읽어온다 --
    이 순서와 실제 view의 select 순서가 어긋나면 EXCEPT 비교가 위치 기준으로
    깨지는 사고가 이미 한 번 있었다(spec-5-6 Spec Change Log). 순서를 하드코딩된
    튜플로 별도 유지하면 DDL과 다시 갈라져도 아무도 모르게 통과하므로, DDL을
    유일한 출처로 삼는다.
    """
    ddl_pattern = re.compile(
        r"create\s+temp(?:orary)?\s+table\s+src_expected\s*\((?P<cols>.*?)\)\s*;",
        re.DOTALL | re.IGNORECASE,
    )
    ddl_match = ddl_pattern.search(region)
    if not ddl_match:
        raise SystemExit("ERROR: parity 구간에서 src_expected DDL(create temp table)을 찾지 못했다")
    cell_columns = tuple(
        line.strip().split()[0]
        for line in ddl_match.group("cols").split(",")
        if line.strip()
    )
    pattern = re.compile(
        r"insert\s+into\s+src_expected\s*values\s*(?P<values>.*?);",
        re.DOTALL | re.IGNORECASE,
    )
    match = pattern.search(region)
    if not match:
        raise SystemExit("ERROR: parity 구간에서 src_expected INSERT를 찾지 못했다")
    tuples = _extract_value_tuples(match.group("values"))
    if not tuples:
        raise SystemExit("ERROR: src_expected INSERT에서 튜플을 찾지 못했다")
    rows: list[dict] = []
    for tuple_str in tuples:
        raw_values = _split_preserving_quotes(tuple_str)
        if len(raw_values) != len(cell_columns):
            raise SystemExit(
                f"ERROR: src_expected 튜플 컬럼 수 불일치: "
                f"{len(raw_values)}개 값 vs {len(cell_columns)}개 필드"
            )
        row = {}
        for col, raw in zip(cell_columns, raw_values):
            row[col] = _raw_to_python(raw)
        rows.append(row)
    return rows


# ── JSON 로더 ─────────────────────────────────────────────────

def load_json_input_cases() -> dict:
    path = FIXTURE_DIR / "input_cases.json"
    if not path.exists():
        raise SystemExit(f"ERROR: fixture 파일 없음: {path}")
    data = json.loads(path.read_text(encoding="utf-8"))
    required_keys = ("outcomes", "logical_runs", "canonicals", "candidates", "contributors", "expected_cells", "expected_overall")
    for key in required_keys:
        if key not in data:
            raise SystemExit(f"ERROR: JSON에 '{key}' 키가 없다")
    required_overall_fields = (
        "total_settled", "wins", "losses", "open_count", "suspended_count",
        "delisted_count", "gross_win", "gross_loss", "win_rate", "profit_factor",
    )
    missing_overall = [f for f in required_overall_fields if f not in data["expected_overall"]]
    if missing_overall:
        raise SystemExit(f"ERROR: expected_overall에 필수 필드가 없다: {missing_overall}")
    return data


# ── 기준값 계산 ────────────────────────────────────────────────

def _pick_primary_source(
    ticker: str,
    entry_date: str,
    candidates: list[dict],
    contributors: list[dict],
    canonicals_by_day: dict[str, str],
    source_priority: dict[str, int] | None = None,
) -> str | None:
    """canonical + candidate + contrib에서 primary source를 도출한다."""
    priority = source_priority or SOURCE_PRIORITY
    attempt_run_id = canonicals_by_day.get(entry_date)
    if attempt_run_id is None:
        return None
    cand = None
    for c in candidates:
        if c["ticker"] == ticker and c["trading_day"] == entry_date and c["attempt_run_id"] == attempt_run_id:
            cand = c
            break
    if cand is None:
        return None
    relevant = [c for c in contributors if c["candidate_id"] == cand["candidate_id"] and c["attempt_run_id"] == cand["attempt_run_id"]]
    if not relevant:
        return None
    # 알 수 없는 source는 SQL view의 `case ... else 2 end`와 동일하게 최하위로 취급한다
    # (현재는 candidate_source_contrib의 CHECK 제약과 validate_contributors가 이 경로 도달을
    # 막지만, 우선순위 표현 자체를 SQL과 일치시켜 둔다).
    best = max(relevant, key=lambda c: (float(c["contribution_weight"]), -priority.get(c["source"], len(priority))))
    return best["source"]


def _cell_key(strategy: str, source: str | None) -> tuple[str, str | None]:
    return (strategy, source)


def _outcome_row_key(row: dict) -> tuple:
    return (row["ticker"], row["strategy"], row["entry_date"])


def compute_reference_cells(
    json_data: dict,
    source_priority: dict[str, int] | None = None,
) -> list[dict]:
    """JSON fixture로부터 Python 기준 셀 계산."""
    outcomes = json_data["outcomes"]
    candidates = json_data["candidates"]
    contributors = json_data["contributors"]
    canonicals = json_data["canonicals"]

    # contributor → candidate_id 매핑 (SQL fixture의 ticker 매핑 재현)
    cand_by_ticker: dict[str, dict] = {}
    for c in candidates:
        cand_by_ticker[c["ticker"]] = c

    # contributors에 candidate_id가 없으면 (JSON에는 ticker만 있으므로) 생성.
    # ticker가 candidates에 없으면 fixture drift(오타 등)이므로 조용히 건너뛰지 않고 에러로 낸다.
    enriched_contributors = []
    orphaned_tickers = sorted({c["ticker"] for c in contributors if c["ticker"] not in cand_by_ticker})
    if orphaned_tickers:
        raise SystemExit(
            f"ERROR: contributors에 candidates가 없는 ticker가 있다: {orphaned_tickers}"
        )
    for c in contributors:
        cand = cand_by_ticker[c["ticker"]]
        enriched_contributors.append({
            "candidate_id": cand["candidate_id"],
            "attempt_run_id": cand["attempt_run_id"],
            "source": c["source"],
            "contribution_weight": c["contribution_weight"],
        })

    canonicals_by_day = {c["trading_day"]: c["attempt_run_id"] for c in canonicals}

    groups: dict[tuple, list[dict]] = {}
    for o in outcomes:
        source = _pick_primary_source(
            o["ticker"], o["entry_date"],
            candidates, enriched_contributors, canonicals_by_day,
            source_priority,
        )
        key = _cell_key(o["strategy"], source)
        groups.setdefault(key, []).append(o)

    cells: list[dict] = []
    for (strategy, source), rows in sorted(groups.items(), key=lambda kv: (kv[0][0], str(kv[0][1]))):
        settled = [r for r in rows if r["status"] in SETTLED_STATUSES]
        total_settled = len(settled)
        wins = sum(1 for r in settled if r["return_pct"] is not None and r["return_pct"] > 0)
        losses = sum(1 for r in settled if r["return_pct"] is not None and r["return_pct"] < 0)
        gross_win = sum(
            r["return_pct"] for r in settled if r["return_pct"] is not None and r["return_pct"] > 0
        )
        gross_loss = abs(sum(
            r["return_pct"] for r in settled if r["return_pct"] is not None and r["return_pct"] < 0
        ))
        win_rate = round(wins / total_settled, 4) if total_settled > 0 else None
        # SQL view와 동일: sum(filter)가 빈 집합이면 NULL이므로 gross_win/gross_loss 어느 쪽이
        # 없어도 (승이 0이거나 패가 0이면) profit_factor는 NULL이다.
        gw_eff = gross_win if wins > 0 else None
        gl_eff = gross_loss if losses > 0 else None
        profit_factor = round(gw_eff / gl_eff, 4) if (gw_eff is not None and gl_eff is not None) else None

        cells.append({
            "strategy": strategy,
            "source": source,
            "total_settled": total_settled,
            "wins": wins,
            "losses": losses,
            "open_count": sum(1 for r in rows if r["status"] == "OPEN"),
            "suspended_count": sum(1 for r in rows if r["status"] == "SUSPENDED"),
            "delisted_count": sum(1 for r in rows if r["status"] == "DELISTED"),
            "gross_win": gw_eff,
            "gross_loss": gl_eff,
            "win_rate": win_rate,
            "profit_factor": profit_factor,
        })
    return cells


# ── 비교 ──────────────────────────────────────────────────────

def validate_statuses(rows: list[dict]) -> list[str]:
    errors: list[str] = []
    for row in rows:
        status = row.get("status")
        if status not in VALID_STATUSES:
            errors.append(
                f"행 {_outcome_row_key(row)} status 불일치: {status!r}는 유효한 상태가 아니다 "
                f"(허용: {sorted(VALID_STATUSES)})"
            )
    return errors


def validate_contributors(rows: list[dict]) -> list[str]:
    errors: list[str] = []
    for r in rows:
        src = r.get("source")
        if src is not None and src not in VALID_SOURCES:
            errors.append(f"contributor 불일치: source={src!r}는 유효하지 않다 (허용: {sorted(VALID_SOURCES)})")
        w = r.get("contribution_weight")
        if w is not None and float(w) <= 0:
            errors.append(f"contributor 불일치: weight={w}는 양수가 아니다")
    return errors


def _cell_value_equal(a, b) -> bool:
    if a is None and b is None:
        return True
    if a is None or b is None:
        return False
    if isinstance(a, (int, float)) and isinstance(b, (int, float)):
        return round(float(a), 4) == round(float(b), 4)
    return str(a) == str(b)


def compare_sql_vs_sql(
    a_cells: list[dict], b_cells: list[dict], a_label: str, b_label: str,
) -> list[str]:
    """두 셀 리스트를 전략×source 키로 비교한다."""
    errors: list[str] = []
    by_a = {(c["strategy"], c["source"]): c for c in a_cells}
    by_b = {(c["strategy"], c["source"]): c for c in b_cells}

    keys_a = set(by_a.keys())
    keys_b = set(by_b.keys())

    for key in sorted(keys_a - keys_b, key=str):
        errors.append(f"{a_label}의 {key} 셀이 {b_label}에 없다")
    for key in sorted(keys_b - keys_a, key=str):
        errors.append(f"{b_label}의 {key} 셀이 {a_label}에 없다")

    count_fields = ["total_settled", "wins", "losses", "open_count", "suspended_count", "delisted_count"]
    rate_fields = ["win_rate", "profit_factor"]
    gross_fields = ["gross_win", "gross_loss"]

    for key in sorted(keys_a & keys_b, key=str):
        a_row = by_a[key]
        b_row = by_b[key]
        for f in count_fields:
            av, bv = int(a_row[f]), int(b_row[f])
            if av != bv:
                errors.append(f"셀 {key} {f} 불일치: {a_label}={av} vs {b_label}={bv}")
        for f in gross_fields:
            av, bv = a_row[f], b_row[f]
            if not _cell_value_equal(av, bv):
                errors.append(f"셀 {key} {f} 불일치: {a_label}={av} vs {b_label}={bv}")
        for f in rate_fields:
            ac, bc = canonical_4dp(a_row[f]), canonical_4dp(b_row[f])
            if ac != bc:
                errors.append(f"셀 {key} {f} 불일치: {a_label}={ac} vs {b_label}={bc}")

    return errors


def compare_json_vs_sql(
    json_cells: list[dict], sql_cells: list[dict],
) -> list[str]:
    return compare_sql_vs_sql(json_cells, sql_cells, "JSON expected_cells", "SQL src_expected")


def compare_rows(
    json_rows: list[dict], sql_rows: list[dict],
    key_fn, columns: list[str],
    label: str,
) -> list[str]:
    errors: list[str] = []
    by_json = {key_fn(r): r for r in json_rows}
    by_sql = {key_fn(r): r for r in sql_rows}

    for key in sorted(set(by_json) - set(by_sql), key=str):
        errors.append(f"JSON {label}의 {key}가 SQL에 없다")
    for key in sorted(set(by_sql) - set(by_json), key=str):
        errors.append(f"SQL {label}의 {key}가 JSON에 없다")

    for key in sorted(set(by_json) & set(by_sql), key=str):
        j_row, s_row = by_json[key], by_sql[key]
        for col in columns:
            j_val = j_row.get(col)
            s_val = s_row.get(col)
            if j_val is None and s_val is None:
                continue
            if j_val is None or s_val is None:
                errors.append(f"행 {key} {col} 불일치: JSON {j_val!r} vs SQL {s_val!r}")
                continue
            if col in NUMERIC_OUTCOME_FIELDS:
                if float(j_val) != float(s_val):
                    errors.append(f"행 {key} {col} 불일치: JSON {j_val} vs SQL {s_val}")
            elif str(j_val) != str(s_val):
                errors.append(f"행 {key} {col} 불일치: JSON {j_val!r} vs SQL {s_val!r}")

    return errors


def verify_overall(cells: list[dict], overall: dict) -> list[str]:
    errors: list[str] = []
    int_fields = ["total_settled", "wins", "losses", "open_count", "suspended_count", "delisted_count"]
    for f in int_fields:
        cell_sum = sum(int(c[f]) for c in cells)
        if cell_sum != int(overall[f]):
            errors.append(f"overall {f} 불일치: 셀 합={cell_sum} vs expected={overall[f]}")

    gw_cells = sum(float(c["gross_win"]) for c in cells if c["gross_win"] is not None)
    gl_cells = sum(float(c["gross_loss"]) for c in cells if c["gross_loss"] is not None)
    gw_exp = overall.get("gross_win")
    gl_exp = overall.get("gross_loss")

    if gw_exp is not None and round(float(gw_cells), 4) != round(float(gw_exp), 4):
        errors.append(f"overall gross_win 불일치: 셀 합={round(float(gw_cells),4)} vs expected={gw_exp}")
    if gl_exp is not None and round(float(gl_cells), 4) != round(float(gl_exp), 4):
        errors.append(f"overall gross_loss 불일치: 셀 합={round(float(gl_cells),4)} vs expected={gl_exp}")

    wins_total = sum(int(c["wins"]) for c in cells)
    settled_total = sum(int(c["total_settled"]) for c in cells)
    wr = round(wins_total / settled_total, 4) if settled_total > 0 else None
    wr_exp = overall.get("win_rate")
    if canonical_4dp(wr) != canonical_4dp(wr_exp):
        errors.append(f"overall win_rate 불일치: 재계산={canonical_4dp(wr)} vs expected={canonical_4dp(wr_exp)}")

    if gw_cells > 0 and gl_cells > 0:
        pf = round(gw_cells / gl_cells, 4)
    else:
        pf = None
    pf_exp = overall.get("profit_factor")
    if canonical_4dp(pf) != canonical_4dp(pf_exp):
        errors.append(f"overall profit_factor 불일치: 재계산={canonical_4dp(pf)} vs expected={canonical_4dp(pf_exp)}")

    return errors


def verify_candidate_canonical_invariants(
    candidates: list[dict], canonicals: list[dict],
) -> list[str]:
    """각 후보의 attempt_run_id가 해당 거래일의 canonical run과 일치하는지 검증한다."""
    errors: list[str] = []
    canonicals_by_day = {c["trading_day"]: c["attempt_run_id"] for c in canonicals}
    for c in candidates:
        expected_run = canonicals_by_day.get(c["trading_day"])
        if expected_run is None:
            errors.append(f"candidate {c['ticker']}({c['trading_day']})의 거래일에 canonical run이 없다")
        elif c["attempt_run_id"] != expected_run:
            errors.append(
                f"candidate {c['ticker']}({c['trading_day']})의 attempt_run_id={c['attempt_run_id']} "
                f"!= canonical={expected_run}"
            )
    return errors


# ── main ──────────────────────────────────────────────────────

def main() -> int:
    if not SQL_PATH.exists():
        print(f"ERROR: SQL fixture 없음: {SQL_PATH}")
        return 1

    sql = SQL_PATH.read_text(encoding="utf-8")
    region = _setup_region(sql)
    json_data = load_json_input_cases()

    # SQL 파싱
    sql_logical_runs = parse_sql_logical_runs(region)
    sql_canonicals = parse_sql_canonicals(region)
    sql_candidates = parse_sql_candidates(region)
    sql_contributors = parse_sql_contributors(region)
    sql_outcomes = parse_sql_outcomes(region)
    sql_cells = parse_sql_cells(region)

    errors: list[str] = []

    # 0. status 검증
    errors += validate_statuses(json_data["outcomes"])

    # 1. contributor source/weight 검증
    errors += validate_contributors(json_data["contributors"])

    # 2. logical_runs 비교
    errors += compare_rows(
        json_data["logical_runs"], sql_logical_runs,
        key_fn=lambda r: (r["logical_run_key"],),
        columns=["logical_run_key", "trading_day", "batch_kind"],
        label="logical_runs",
    )

    # 3. canonicals 비교
    errors += compare_rows(
        json_data["canonicals"], sql_canonicals,
        key_fn=lambda r: (r["trading_day"],),
        columns=["trading_day", "attempt_run_id"],
        label="canonicals",
    )

    # 4. candidates 비교
    errors += compare_rows(
        json_data["candidates"], sql_candidates,
        key_fn=lambda r: (r["candidate_id"],),
        columns=["candidate_id", "ticker", "trading_day", "attempt_run_id", "trading_value"],
        label="candidates",
    )

    # 5. candidates ↔ canonicals 불변식 검증
    errors += verify_candidate_canonical_invariants(json_data["candidates"], json_data["canonicals"])

    # 6. contributors 비교 (ticker→candidate_id 매핑 후)
    sql_ticker_by_candidate_id = {c["candidate_id"]: c["ticker"] for c in sql_candidates}
    sql_contrib_enriched = []
    for c in sql_contributors:
        sql_contrib_enriched.append({
            "ticker": sql_ticker_by_candidate_id.get(c["candidate_id"]),
            "source": c["source"],
            "contribution_weight": c["contribution_weight"],
        })

    def _contrib_key(r: dict) -> tuple:
        return (r["ticker"], r["source"])

    errors += compare_rows(
        json_data["contributors"], sql_contrib_enriched,
        key_fn=_contrib_key,
        columns=["ticker", "source", "contribution_weight"],
        label="contributors",
    )

    # 7. outcomes 비교
    errors += compare_rows(
        json_data["outcomes"], sql_outcomes,
        key_fn=_outcome_row_key,
        columns=list(OUTCOME_COLUMNS),
        label="outcomes",
    )

    # 8. JSON expected_cells ↔ SQL src_expected 비교
    errors += compare_json_vs_sql(json_data["expected_cells"], sql_cells)

    # 9. Python 기준 셀 계산
    python_cells = compute_reference_cells(json_data)

    # 10. Python 기준 ↔ JSON expected_cells 비교
    errors += compare_sql_vs_sql(python_cells, json_data["expected_cells"], "Python 기준값", "JSON expected_cells")

    # 11. Python 기준 ↔ SQL src_expected 비교
    errors += compare_sql_vs_sql(python_cells, sql_cells, "Python 기준값", "SQL src_expected")

    # 12. outcome당 정확히 1셀 귀속 검증
    total_outcomes = len(json_data["outcomes"])
    total_cell_rows = sum(int(c["total_settled"]) + int(c["open_count"]) + int(c["suspended_count"]) + int(c["delisted_count"]) for c in python_cells)
    if total_outcomes != total_cell_rows:
        errors.append(f"outcome 총수 불일치: outcomes={total_outcomes} vs 셀 행 합={total_cell_rows}")

    # 13. 셀 합 = expected_overall 교차 검증
    errors += verify_overall(python_cells, json_data["expected_overall"])

    for error in errors:
        print(f"ERROR: {error}")
    if errors:
        print(
            f"결과: {len(errors)} ERROR - 승률·PF by_strategy_source fixture의 "
            "JSON/SQL/Python이 갈라졌다. 셋을 함께 고치세요."
        )
        return 1

    overall = json_data["expected_overall"]
    print(
        f"story 5-6 win_rate_pf_by_strategy_source fixture drift 없음 "
        f"(outcome {len(json_data['outcomes'])}건, cell {len(sql_cells)}행, "
        f"total_settled={overall['total_settled']}, "
        f"win_rate={overall['win_rate']}, profit_factor={overall['profit_factor']})"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())