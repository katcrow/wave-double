"""Story 5.9 이탈 임계값 fixture의 JSON/SQL/Python 4중 parity gate."""

from __future__ import annotations

import json
import math
import re
import sys
from decimal import Decimal
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

ROOT = Path(__file__).resolve().parents[1]
SQL_PATH = ROOT / "tests" / "sql" / "test_outcome_win_rate_pf_threshold_gated.sql"
FIXTURE_DIR = ROOT / "tests" / "fixtures" / "outcome_win_rate_pf_threshold_gated"
SETUP_MARKER = "-- ── parity fixture setup"
INSERT_COLUMNS = ("ticker", "strategy", "entry_date", "entry_price", "status", "exit_date", "exit_price", "return_pct", "cutoff_n", "holding_days", "tp_pct", "sl_pct")
VALID_STATUSES = {"TP", "SL", "TIMEOUT", "OPEN", "SUSPENDED", "DELISTED"}
SETTLED_STATUSES = {"TP", "SL", "TIMEOUT"}
Z = 1.959963985
SAMPLE_GATE_MIN_REQUIRED = 30
WIN_RATE_THRESHOLD_PP = 0.10
PROFIT_FACTOR_THRESHOLD_RATIO = 0.25
EXPECTED_WIN_RATE_BY_STRATEGY = {"A": 0.6871, "B": 0.6895, "C": 0.6600}
EXPECTED_PROFIT_FACTOR_BY_STRATEGY = {"A": 2.0540, "B": 2.0770, "C": 1.8159}
ROW_FIELDS = (
    "total_settled", "wins", "losses", "open_count", "suspended_count", "delisted_count",
    "gross_win", "gross_loss", "win_rate", "profit_factor", "sample_gate_min_required",
    "sample_gate_passed", "sample_gate_label", "ci_lower", "ci_upper", "expected_win_rate",
    "expected_in_ci", "expected_profit_factor", "win_rate_threshold_pp",
    "profit_factor_threshold_ratio", "win_rate_threshold_breached",
    "profit_factor_threshold_breached", "threshold_warning",
)


def _setup_region(sql: str) -> str:
    if SETUP_MARKER not in sql:
        raise SystemExit("ERROR: parity fixture setup 마커를 찾지 못했다")
    region = sql.split(SETUP_MARKER, 1)[1]
    return region.split("-- ── sql-only boundary fixture", 1)[0]


def _extract_tuples(block: str) -> list[str]:
    result: list[str] = []
    depth = 0
    start = None
    quoted = False
    i = 0
    while i < len(block):
        ch = block[i]
        if ch == "'":
            if quoted and i + 1 < len(block) and block[i + 1] == "'":
                i += 2
                continue
            quoted = not quoted
        elif not quoted and ch == "(" and depth == 0:
            start, depth = i, 1
        elif not quoted and ch == "(" and depth:
            depth += 1
        elif not quoted and ch == ")" and depth:
            depth -= 1
            if depth == 0 and start is not None:
                result.append(block[start + 1 : i])
                start = None
        i += 1
    return result


def _split_cells(value: str) -> list[str]:
    cells, current, quoted, i = [], [], False, 0
    while i < len(value):
        ch = value[i]
        if ch == "'":
            if quoted and i + 1 < len(value) and value[i + 1] == "'":
                current.extend(("'", "'"))
                i += 2
                continue
            quoted = not quoted
        if ch == "," and not quoted:
            cells.append("".join(current).strip())
            current = []
        else:
            current.append(ch)
        i += 1
    cells.append("".join(current).strip())
    return cells


def _literal(raw: str):
    raw = raw.strip()
    if raw.upper() == "NULL":
        return None
    if raw.upper() in {"TRUE", "FALSE"}:
        return raw.upper() == "TRUE"
    if raw.startswith("'") and raw.endswith("'"):
        return raw[1:-1].replace("''", "'")
    try:
        number = float(raw)
        return int(number) if number.is_integer() and "." not in raw else number
    except ValueError:
        return raw


def _parse_values(sql: str, pattern: str, columns: tuple[str, ...]) -> list[dict]:
    match = re.search(pattern, _setup_region(sql), re.IGNORECASE | re.DOTALL)
    if not match:
        raise SystemExit("ERROR: parity fixture INSERT를 찾지 못했다")
    rows = []
    for tuple_text in _extract_tuples(match.group("values")):
        cells = _split_cells(tuple_text)
        if len(cells) != len(columns):
            raise SystemExit(f"ERROR: fixture 컬럼 수 불일치: {len(cells)} vs {len(columns)}")
        rows.append(dict(zip(columns, (_literal(cell) for cell in cells))))
    if not rows:
        raise SystemExit("ERROR: fixture INSERT가 비어 있다")
    return rows


def parse_sql_insert_rows(sql: str) -> list[dict]:
    region = _setup_region(sql)
    columns_match = re.search(
        r"insert\s+into\s+public\.candidate_outcome\s*\((?P<columns>[^)]*)\)\s*values",
        region,
        re.IGNORECASE,
    )
    if not columns_match:
        raise SystemExit("ERROR: candidate_outcome INSERT 컬럼 목록을 찾지 못했다")
    columns = tuple(column.strip() for column in columns_match.group("columns").split(","))
    if columns != INSERT_COLUMNS:
        raise SystemExit(f"ERROR: candidate_outcome INSERT 컬럼 순서가 계약과 다르다: {columns}")
    return _parse_values(
        sql,
        r"insert\s+into\s+public\.candidate_outcome\s*\([^)]*\)\s*values\s*(?P<values>.*?);",
        INSERT_COLUMNS,
    )


def parse_sql_expected_rows(sql: str) -> list[dict]:
    region = _setup_region(sql)
    ddl = re.search(r"create\s+temp\s+table\s+threshold_expected\s*\((?P<cols>.*?)\)\s*;", region, re.IGNORECASE | re.DOTALL)
    if not ddl:
        raise SystemExit("ERROR: threshold_expected DDL을 찾지 못했다")
    columns = tuple(line.strip().split()[0] for line in ddl.group("cols").split(",") if line.strip())
    expected_columns = ("strategy",) + ROW_FIELDS
    if columns != expected_columns:
        raise SystemExit(f"ERROR: threshold_expected 컬럼 순서가 view 계약과 다르다: {columns}")
    return _parse_values(sql, r"insert\s+into\s+threshold_expected\s+values\s*(?P<values>.*?);", columns)


def load_json_fixture() -> dict:
    path = FIXTURE_DIR / "input_cases.json"
    if not path.exists():
        raise SystemExit(f"ERROR: fixture 파일 없음: {path}")
    data = json.loads(path.read_text(encoding="utf-8"))
    if not isinstance(data.get("input_cases"), list) or not isinstance(data.get("expected_rows"), list):
        raise SystemExit("ERROR: input_cases/expected_rows 배열이 필요하다")
    return data


def validate_statuses(rows: list[dict]) -> list[str]:
    return [f"status 유효하지 않음: {row.get('status')!r}" for row in rows if row.get("status") not in VALID_STATUSES]


def _key(row: dict) -> tuple:
    return row.get("ticker"), row.get("strategy"), row.get("entry_date")


def compare_input_rows(json_rows: list[dict], sql_rows: list[dict]) -> list[str]:
    errors = []
    json_by_key, sql_by_key = {_key(r): r for r in json_rows}, {_key(r): r for r in sql_rows}
    if len(json_by_key) != len(json_rows):
        errors.append("JSON input_cases에 중복 키가 있다")
    if len(sql_by_key) != len(sql_rows):
        errors.append("SQL INSERT에 중복 키가 있다")
    for key in sorted(set(json_by_key) ^ set(sql_by_key), key=str):
        errors.append(f"입력 행 누락 또는 추가: {key}")
    for key in sorted(set(json_by_key) & set(sql_by_key), key=str):
        for field in INSERT_COLUMNS:
            if field not in json_by_key[key] or field not in sql_by_key[key]:
                errors.append(f"{key} {field} 컬럼이 누락됐다")
                continue
            left, right = json_by_key[key].get(field), sql_by_key[key].get(field)
            if left is None or right is None:
                if left != right:
                    errors.append(f"{key} {field} 불일치: {left!r} vs {right!r}")
            elif field in {"entry_price", "exit_price", "return_pct", "cutoff_n", "holding_days", "tp_pct", "sl_pct"}:
                if Decimal(str(left)) != Decimal(str(right)):
                    errors.append(f"{key} {field} 불일치")
            elif str(left) != str(right):
                errors.append(f"{key} {field} 불일치: {left!r} vs {right!r}")
    if len(json_rows) != len(sql_rows):
        errors.append(f"입력 행 수 불일치: {len(json_rows)} vs {len(sql_rows)}")
    return errors


def _canonical(value) -> str | None:
    return None if value is None else f"{round(float(value), 4):.4f}"


def compare_result_rows(left: list[dict], right: list[dict], left_name: str, right_name: str) -> list[str]:
    errors = []
    a, b = {r.get("strategy"): r for r in left}, {r.get("strategy"): r for r in right}
    for name, rows in ((left_name, left), (right_name, right)):
        if len(rows) != len({r.get("strategy") for r in rows}):
            errors.append(f"{name}에 strategy 중복 행이 있다")
        expected_keys = {"strategy", *ROW_FIELDS}
        for row in rows:
            if set(row) != expected_keys:
                errors.append(f"{name} strategy={row.get('strategy')!r} 컬럼 집합이 계약과 다르다")
    for strategy in sorted(set(a) ^ set(b), key=str):
        errors.append(f"{left_name}/{right_name} strategy={strategy!r} 행 불일치")
    int_fields = {"total_settled", "wins", "losses", "open_count", "suspended_count", "delisted_count", "sample_gate_min_required"}
    bool_fields = {"sample_gate_passed", "expected_in_ci", "win_rate_threshold_breached", "profit_factor_threshold_breached", "threshold_warning"}
    text_fields = {"sample_gate_label"}
    for strategy in sorted(set(a) & set(b), key=str):
        for field in ROW_FIELDS:
            av, bv = a[strategy].get(field), b[strategy].get(field)
            if field in int_fields:
                same = av == bv
            elif field in bool_fields:
                same = av == bv
            elif field in text_fields:
                same = av == bv
            elif field in {"gross_win", "gross_loss"}:
                same = av is None and bv is None or av is not None and bv is not None and Decimal(str(av)) == Decimal(str(bv))
            else:
                same = _canonical(av) == _canonical(bv)
            if not same:
                errors.append(f"strategy={strategy!r} {field} 불일치: {left_name}={av!r} vs {right_name}={bv!r}")
    return errors


def _wilson_ci(win_rate: float, total_settled: int) -> tuple[float, float]:
    z2 = Z * Z
    denom = 1 + z2 / total_settled
    center = (win_rate + z2 / (2 * total_settled)) / denom
    spread = math.sqrt((win_rate * (1 - win_rate) + z2 / (4 * total_settled)) / total_settled)
    return round(center - (Z / denom) * spread, 4), round(center + (Z / denom) * spread, 4)


def compute_threshold_flags(win_rate, profit_factor, expected_win_rate, expected_profit_factor):
    """SQL numeric과 같은 엄격한 초과(>) 경계 비교를 수행한다."""
    if win_rate is None or expected_win_rate is None:
        win_breached = None
    else:
        win_breached = abs(Decimal(str(win_rate)) - Decimal(str(expected_win_rate))) > Decimal("0.10")
    if profit_factor is None or expected_profit_factor in (None, 0):
        pf_breached = None
    else:
        pf_breached = (
            abs(Decimal(str(profit_factor)) - Decimal(str(expected_profit_factor)))
            / Decimal(str(expected_profit_factor))
            > Decimal("0.25")
        )
    warning = (bool(win_breached) or bool(pf_breached)) if win_breached is not None or pf_breached is not None else None
    return win_breached, pf_breached, warning


def compute_reference_rows(rows: list[dict]) -> list[dict]:
    groups = [(strategy, [r for r in rows if r["strategy"] == strategy]) for strategy in sorted({r["strategy"] for r in rows})]
    groups.append((None, rows))
    result = []
    for strategy, group in groups:
        settled = [r for r in group if r["status"] in SETTLED_STATUSES]
        total = len(settled)
        wins = sum(r["return_pct"] > 0 for r in settled if r["return_pct"] is not None)
        losses = sum(r["return_pct"] < 0 for r in settled if r["return_pct"] is not None)
        gross_win = sum(r["return_pct"] for r in settled if r["return_pct"] is not None and r["return_pct"] > 0)
        gross_loss = abs(sum(r["return_pct"] for r in settled if r["return_pct"] is not None and r["return_pct"] < 0))
        passed = total >= SAMPLE_GATE_MIN_REQUIRED
        win_rate = round(wins / total, 4) if passed else None
        profit_factor = round(gross_win / gross_loss, 4) if passed and wins > 0 and losses > 0 else None
        lower, upper = _wilson_ci(win_rate, total) if passed and win_rate is not None else (None, None)
        expected_win = EXPECTED_WIN_RATE_BY_STRATEGY.get(strategy) if passed else None
        expected_pf = EXPECTED_PROFIT_FACTOR_BY_STRATEGY.get(strategy) if passed else None
        expected_in_ci = expected_win is not None and lower <= expected_win <= upper if expected_win is not None else None
        win_breached, pf_breached, warning = compute_threshold_flags(win_rate, profit_factor, expected_win, expected_pf)
        result.append({
            "strategy": strategy, "total_settled": total, "wins": wins, "losses": losses,
            "open_count": sum(r["status"] == "OPEN" for r in group),
            "suspended_count": sum(r["status"] == "SUSPENDED" for r in group),
            "delisted_count": sum(r["status"] == "DELISTED" for r in group),
            "gross_win": gross_win if wins else None, "gross_loss": gross_loss if losses else None,
            "win_rate": win_rate, "profit_factor": profit_factor,
            "sample_gate_min_required": SAMPLE_GATE_MIN_REQUIRED, "sample_gate_passed": passed,
            "sample_gate_label": None if passed else f"표본 부족 ({total}/30)",
            "ci_lower": lower, "ci_upper": upper, "expected_win_rate": expected_win,
            "expected_in_ci": expected_in_ci, "expected_profit_factor": expected_pf,
            "win_rate_threshold_pp": WIN_RATE_THRESHOLD_PP if passed else None,
            "profit_factor_threshold_ratio": PROFIT_FACTOR_THRESHOLD_RATIO if passed else None,
            "win_rate_threshold_breached": win_breached, "profit_factor_threshold_breached": pf_breached,
            "threshold_warning": warning,
        })
    return result


def main() -> int:
    if not SQL_PATH.exists():
        print(f"ERROR: SQL fixture 없음: {SQL_PATH}")
        return 1
    fixture = load_json_fixture()
    sql = SQL_PATH.read_text(encoding="utf-8")
    errors = validate_statuses(fixture["input_cases"])
    errors += compare_input_rows(fixture["input_cases"], parse_sql_insert_rows(sql))
    reference = compute_reference_rows(fixture["input_cases"])
    expected = fixture["expected_rows"]
    sql_expected = parse_sql_expected_rows(sql)
    errors += compare_result_rows(reference, expected, "Python", "JSON")
    errors += compare_result_rows(reference, sql_expected, "Python", "SQL")
    errors += compare_result_rows(expected, sql_expected, "JSON", "SQL")
    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        return 1
    total = next(row for row in reference if row["strategy"] is None)
    print(f"story 5-9 threshold fixture drift 없음 (입력 {len(fixture['input_cases'])}건, 전체 종결 {total['total_settled']}건)")
    return 0


if __name__ == "__main__":
    sys.exit(main())
