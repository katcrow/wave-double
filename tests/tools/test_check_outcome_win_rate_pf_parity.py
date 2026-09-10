"""tools/check_outcome_win_rate_pf_parity.py 계약 테스트 (story 5-5).

drift gate 자체가 "무엇을 놓치는가"가 중요하므로, 실제 저장소 fixture가 통과하는 것과
각 종류의 drift를 심어 넣었을 때 실패하는 것을 함께 고정한다.
"""

from __future__ import annotations

import importlib.util
import json
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
_spec = importlib.util.spec_from_file_location(
    "check_outcome_win_rate_pf_parity",
    ROOT / "tools" / "check_outcome_win_rate_pf_parity.py",
)
parity = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(parity)


@pytest.fixture
def repo_fixtures() -> dict:
    return {
        "sql": parity.SQL_PATH.read_text(encoding="utf-8"),
        "json_rows": json.loads(
            (parity.FIXTURE_DIR / "input_cases.json").read_text(encoding="utf-8")
        ),
    }


def test_repository_fixtures_are_in_sync() -> None:
    assert parity.main() == 0


def test_sql_parsing_finds_all_insert_rows(repo_fixtures: dict) -> None:
    sql = repo_fixtures["sql"]
    rows = parity.parse_sql_insert_rows(sql)
    assert len(rows) == len(repo_fixtures["json_rows"])


def test_setup_marker_exists(repo_fixtures: dict) -> None:
    """parity fixture setup 마커가 존재해야 한다."""
    assert parity.SETUP_MARKER in repo_fixtures["sql"]


def test_missing_setup_marker_fails_loudly() -> None:
    """마커가 없으면 조용히 통과하지 않고 ERROR를 반환한다."""
    with pytest.raises(SystemExit, match="parity fixture setup 마커"):
        parity.parse_sql_insert_rows("begin;\ninsert into public.candidate_outcome(a) values (1);\n")


def test_json_row_missing_from_sql_is_reported(repo_fixtures: dict) -> None:
    sql_rows = parity.parse_sql_insert_rows(repo_fixtures["sql"])[:-1]

    errors = parity.compare_json_sql_rows(repo_fixtures["json_rows"], sql_rows)

    assert any("SQL fixture에 없다" in e for e in errors)


def test_sql_row_missing_from_json_is_reported(repo_fixtures: dict) -> None:
    sql_rows = parity.parse_sql_insert_rows(repo_fixtures["sql"])
    json_rows = repo_fixtures["json_rows"][:-1]

    errors = parity.compare_json_sql_rows(json_rows, sql_rows)

    assert any("input_cases.json에 없다" in e for e in errors)


def test_return_pct_null_drift_is_reported(repo_fixtures: dict) -> None:
    sql_rows = parity.parse_sql_insert_rows(repo_fixtures["sql"])
    json_rows = [dict(row) for row in repo_fixtures["json_rows"]]
    json_rows[6]["return_pct"] = 1.0

    errors = parity.compare_json_sql_rows(json_rows, sql_rows)

    assert any("return_pct" in e for e in errors)


def test_settled_row_return_pct_value_drift_is_reported(repo_fixtures: dict) -> None:
    """종결(settled) 행의 return_pct 값 변경도 gate가 잡아야 한다."""
    sql_rows = parity.parse_sql_insert_rows(repo_fixtures["sql"])
    json_rows = [dict(row) for row in repo_fixtures["json_rows"]]
    json_rows[0]["return_pct"] = 2.8  # A0001 TP의 손익률을 미세 조정

    errors = parity.compare_json_sql_rows(json_rows, sql_rows)

    assert any("return_pct" in e for e in errors)


def test_invalid_status_is_reported(repo_fixtures: dict) -> None:
    """지원되지 않는 status 값이 fixture에 섞이면 gate가 잡아야 한다."""
    json_rows = [dict(row) for row in repo_fixtures["json_rows"]]
    json_rows[0]["status"] = "TPP"  # 오타로 유효하지 않은 상태

    errors = parity.validate_statuses(json_rows)

    assert any("status" in e and "TPP" in e for e in errors)


def test_win_pf_expected_numeric_drift_is_reported(repo_fixtures: dict) -> None:
    sql_expected = parity.parse_sql_expected(repo_fixtures["sql"])
    ref = parity.compute_reference(repo_fixtures["json_rows"])

    sql_expected["win_rate"] = 0.9999

    errors = parity.compare_reference_vs_expected(ref, sql_expected)

    assert any("win_rate" in e for e in errors)


def test_win_pf_expected_rounding_equal_is_ok(repo_fixtures: dict) -> None:
    """round 4 결과가 같은 값(0.5 vs 0.5000)은 drift로 잡지 않는다."""
    sql_expected = parity.parse_sql_expected(repo_fixtures["sql"])
    ref = parity.compute_reference(repo_fixtures["json_rows"])

    sql_expected["win_rate"] = 0.5  # view가 4dp로 출력하므로 의미상 동일

    errors = parity.compare_reference_vs_expected(ref, sql_expected)

    assert not any("win_rate" in e for e in errors)


def test_gross_win_drift_is_reported(repo_fixtures: dict) -> None:
    sql_expected = parity.parse_sql_expected(repo_fixtures["sql"])
    ref = parity.compute_reference(repo_fixtures["json_rows"])

    sql_expected["gross_win"] = 6.5

    errors = parity.compare_reference_vs_expected(ref, sql_expected)

    assert any("gross_win" in e for e in errors)


def test_gross_loss_drift_is_reported(repo_fixtures: dict) -> None:
    sql_expected = parity.parse_sql_expected(repo_fixtures["sql"])
    ref = parity.compute_reference(repo_fixtures["json_rows"])

    sql_expected["gross_loss"] = 8.5

    errors = parity.compare_reference_vs_expected(ref, sql_expected)

    assert any("gross_loss" in e for e in errors)


def test_compute_reference_matches_expected(repo_fixtures: dict) -> None:
    ref = parity.compute_reference(repo_fixtures["json_rows"])
    ep = parity.parse_sql_expected(repo_fixtures["sql"])

    assert ref["total_settled"] == int(ep["total_settled"])
    assert ref["wins"] == int(ep["wins"])
    assert ref["losses"] == int(ep["losses"])
    assert ref["open_count"] == int(ep["open_count"])
    assert ref["suspended_count"] == int(ep["suspended_count"])
    assert ref["delisted_count"] == int(ep["delisted_count"])
    assert round(float(ref["gross_win"]), 4) == round(float(ep["gross_win"]), 4)
    assert round(float(ref["gross_loss"]), 4) == round(float(ep["gross_loss"]), 4)
    assert round(float(ref["win_rate"]), 4) == round(float(ep["win_rate"]), 4)
    assert round(float(ref["profit_factor"]), 4) == round(float(ep["profit_factor"]), 4)


def test_compute_reference_all_win_gross_loss_none() -> None:
    """ALL_WIN(손실 없음)에서는 SQL view와 동일하게 gross_loss가 None이어야 한다."""
    rows = [
        {"ticker": "B001", "strategy": "A", "entry_date": "2098-06-01",
         "status": "TP", "return_pct": 2.0},
        {"ticker": "B002", "strategy": "B", "entry_date": "2098-06-02",
         "status": "TP", "return_pct": 1.0},
    ]
    for r in rows:
        r.setdefault("exit_date", None); r.setdefault("exit_price", None)
        r.setdefault("cutoff_n", 30); r.setdefault("holding_days", 2)
        r.setdefault("entry_price", 1000); r.setdefault("tp_pct", 3.0)
        r.setdefault("sl_pct", 3.0)

    ref = parity.compute_reference(rows)

    assert ref["gross_loss"] is None
    assert ref["profit_factor"] is None
    assert ref["win_rate"] == round(2 / 2, 4)


def test_compute_reference_empty_settled_none() -> None:
    """settled 분모가 0이면 율 지표가 전부 None이고 카운트는 0이어야 한다."""
    rows: list[dict] = []

    ref = parity.compute_reference(rows)

    assert ref["total_settled"] == 0
    assert ref["win_rate"] is None
    assert ref["profit_factor"] is None


def test_profit_factor_drift_is_reported(repo_fixtures: dict) -> None:
    ref = parity.compute_reference(repo_fixtures["json_rows"])
    ep = parity.parse_sql_expected(repo_fixtures["sql"])

    ep["profit_factor"] = 9.9999

    errors = parity.compare_reference_vs_expected(ref, ep)

    assert any("profit_factor" in e for e in errors)
