"""tools/check_outcome_win_rate_pf_ci_parity.py 계약 테스트 (story 5-8).

drift gate 자체가 "무엇을 놓치는가"가 중요하므로, 실제 저장소 fixture가 통과하는 것과
각 종류의 drift(z-value 오기, expected_win_rate 오매핑, D/E/F에 값이 채워지는 회귀,
expected_in_ci boolean 반전 등)를 심어 넣었을 때 실패하는 것을 함께 고정한다. 경계값
(29건 게이트 실패 vs 40건 CI 안/밖 vs 35건 기대치 없음)이 fixture에 고정돼 있는지도
검증한다.
"""

from __future__ import annotations

import copy
import importlib.util
import json
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
_spec = importlib.util.spec_from_file_location(
    "check_outcome_win_rate_pf_ci_parity",
    ROOT / "tools" / "check_outcome_win_rate_pf_ci_parity.py",
)
parity = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(parity)


@pytest.fixture
def repo_fixtures() -> dict:
    return {
        "sql": parity.SQL_PATH.read_text(encoding="utf-8"),
        "fixture": json.loads(
            (parity.FIXTURE_DIR / "input_cases.json").read_text(encoding="utf-8")
        ),
    }


def test_repository_fixtures_are_in_sync() -> None:
    assert parity.main() == 0


def test_setup_marker_exists(repo_fixtures: dict) -> None:
    assert parity.SETUP_MARKER in repo_fixtures["sql"]


def test_missing_setup_marker_fails_loudly() -> None:
    with pytest.raises(SystemExit, match="parity fixture setup 마커"):
        parity._setup_region("begin;\ninsert into public.candidate_outcome(a) values (1);\n")


def test_sql_parsing_finds_all_insert_rows(repo_fixtures: dict) -> None:
    sql = repo_fixtures["sql"]
    rows = parity.parse_sql_insert_rows(sql)
    assert len(rows) == len(repo_fixtures["fixture"]["input_cases"])


def test_ci_expected_has_five_rows(repo_fixtures: dict) -> None:
    """전략 A/B/C/D + rollup 전체 5행이 fixture에 있어야 한다."""
    rows = parity.parse_sql_ci_expected(repo_fixtures["sql"])
    assert len(rows) == 5
    strategies = {r["strategy"] for r in rows}
    assert strategies == {"A", "B", "C", "D", None}


def test_strategy_a_ci_contains_expected() -> None:
    """전략 A(종결 40건, 28승)는 게이트를 통과하고 기대치 0.6871이 CI 안쪽이어야 한다."""
    fixture = parity.load_json_fixture()
    ref_rows = parity.compute_reference_rows(fixture["input_cases"])
    a_row = next(r for r in ref_rows if r["strategy"] == "A")
    assert a_row["total_settled"] == 40
    assert a_row["sample_gate_passed"] is True
    assert a_row["ci_lower"] is not None and a_row["ci_upper"] is not None
    assert a_row["expected_win_rate"] == 0.6871
    assert a_row["expected_in_ci"] is True


def test_strategy_b_ci_excludes_expected() -> None:
    """전략 B(종결 40건, 38승)는 게이트를 통과하지만 기대치 0.6895가 CI 바깥쪽이어야 한다."""
    fixture = parity.load_json_fixture()
    ref_rows = parity.compute_reference_rows(fixture["input_cases"])
    b_row = next(r for r in ref_rows if r["strategy"] == "B")
    assert b_row["total_settled"] == 40
    assert b_row["sample_gate_passed"] is True
    assert b_row["expected_win_rate"] == 0.6895
    assert b_row["expected_in_ci"] is False


def test_strategy_c_below_gate_has_all_null_ci_fields() -> None:
    """전략 C는 종결 29건으로 게이트 실패 — ci_lower/ci_upper/expected_win_rate/expected_in_ci
    모두 NULL이어야 한다(전략 C가 A/B/C 기대치 세트에 속해도 게이트 미통과면 노출되지
    않는다는 AC를 고정)."""
    fixture = parity.load_json_fixture()
    ref_rows = parity.compute_reference_rows(fixture["input_cases"])
    c_row = next(r for r in ref_rows if r["strategy"] == "C")
    assert c_row["total_settled"] == 29
    assert c_row["sample_gate_passed"] is False
    assert c_row["ci_lower"] is None
    assert c_row["ci_upper"] is None
    assert c_row["expected_win_rate"] is None
    assert c_row["expected_in_ci"] is None


def test_strategy_d_gate_passed_no_expected() -> None:
    """전략 D는 게이트를 통과해 CI는 계산되지만 기대치가 정의돼 있지 않으므로
    expected_win_rate/expected_in_ci는 NULL이어야 한다."""
    fixture = parity.load_json_fixture()
    ref_rows = parity.compute_reference_rows(fixture["input_cases"])
    d_row = next(r for r in ref_rows if r["strategy"] == "D")
    assert d_row["total_settled"] == 35
    assert d_row["sample_gate_passed"] is True
    assert d_row["ci_lower"] is not None
    assert d_row["ci_upper"] is not None
    assert d_row["expected_win_rate"] is None
    assert d_row["expected_in_ci"] is None


def test_rollup_gate_passed_no_expected() -> None:
    """rollup 전체(strategy=None) 행은 게이트를 통과해도 기대치가 정의돼 있지 않다."""
    fixture = parity.load_json_fixture()
    ref_rows = parity.compute_reference_rows(fixture["input_cases"])
    total_row = next(r for r in ref_rows if r["strategy"] is None)
    assert total_row["sample_gate_passed"] is True
    assert total_row["ci_lower"] is not None
    assert total_row["expected_win_rate"] is None
    assert total_row["expected_in_ci"] is None


def test_wilson_ci_matches_known_value() -> None:
    """z=1.959963985 기준 Wilson CI가 알려진 값과 4dp까지 일치해야 한다(n=40, win_rate=0.7)."""
    lo, hi = parity._wilson_ci(0.7, 40)
    assert lo == 0.5457
    assert hi == 0.8193


def test_z_value_drift_is_caught() -> None:
    """z값이 잘못되면(예: 90% 신뢰수준 z=1.645) CI가 달라져 fixture와 어긋나야 한다."""
    original_z = parity.Z
    try:
        parity.Z = 1.645
        lo, hi = parity._wilson_ci(0.7, 40)
        assert (lo, hi) != (0.5457, 0.8193)
    finally:
        parity.Z = original_z


def test_expected_win_rate_mismapping_is_reported(repo_fixtures: dict) -> None:
    fixture = copy.deepcopy(repo_fixtures["fixture"])
    for row in fixture["expected_rows"]:
        if row["strategy"] == "A":
            row["expected_win_rate"] = 0.6895  # B의 값으로 오매핑
    ref_rows = parity.compute_reference_rows(fixture["input_cases"])
    errors = parity.compare_ci_rows(ref_rows, fixture["expected_rows"], "Python", "expected")
    assert any("expected_win_rate" in e for e in errors)


def test_expected_in_ci_boolean_flip_is_reported(repo_fixtures: dict) -> None:
    fixture = copy.deepcopy(repo_fixtures["fixture"])
    for row in fixture["expected_rows"]:
        if row["strategy"] == "A":
            row["expected_in_ci"] = False  # 반전
    ref_rows = parity.compute_reference_rows(fixture["input_cases"])
    errors = parity.compare_ci_rows(ref_rows, fixture["expected_rows"], "Python", "expected")
    assert any("expected_in_ci" in e for e in errors)


def test_d_strategy_expected_regression_is_reported(repo_fixtures: dict) -> None:
    """D/E/F에 임의의 기대치가 채워지는 회귀를 잡아야 한다."""
    fixture = copy.deepcopy(repo_fixtures["fixture"])
    for row in fixture["expected_rows"]:
        if row["strategy"] == "D":
            row["expected_win_rate"] = 0.6000  # 스펙에 없는 값이 채워지는 회귀
            row["expected_in_ci"] = True
    ref_rows = parity.compute_reference_rows(fixture["input_cases"])
    errors = parity.compare_ci_rows(ref_rows, fixture["expected_rows"], "Python", "expected")
    assert any("expected_win_rate" in e for e in errors)
    assert any("expected_in_ci" in e for e in errors)


def test_ci_lower_drift_is_reported(repo_fixtures: dict) -> None:
    fixture = copy.deepcopy(repo_fixtures["fixture"])
    for row in fixture["expected_rows"]:
        if row["strategy"] == "A":
            row["ci_lower"] = 0.1234
    ref_rows = parity.compute_reference_rows(fixture["input_cases"])
    errors = parity.compare_ci_rows(ref_rows, fixture["expected_rows"], "Python", "expected")
    assert any("ci_lower" in e for e in errors)


def test_gate_passed_boolean_flip_drift_is_reported(repo_fixtures: dict) -> None:
    fixture = copy.deepcopy(repo_fixtures["fixture"])
    for row in fixture["expected_rows"]:
        if row["strategy"] == "B":
            row["sample_gate_passed"] = False  # 반전
    ref_rows = parity.compute_reference_rows(fixture["input_cases"])
    errors = parity.compare_ci_rows(ref_rows, fixture["expected_rows"], "Python", "expected")
    assert any("sample_gate_passed" in e for e in errors)


def test_invalid_status_is_reported(repo_fixtures: dict) -> None:
    json_rows = [dict(row) for row in repo_fixtures["fixture"]["input_cases"]]
    json_rows[0]["status"] = "TPP"  # 오타로 유효하지 않은 상태

    errors = parity.validate_statuses(json_rows)

    assert any("status" in e and "TPP" in e for e in errors)


def test_sql_row_missing_from_json_is_reported(repo_fixtures: dict) -> None:
    sql_rows = parity.parse_sql_insert_rows(repo_fixtures["sql"])
    json_rows = repo_fixtures["fixture"]["input_cases"][:-1]

    errors = parity.compare_json_sql_rows(json_rows, sql_rows)

    assert any("input_cases.json에 없다" in e for e in errors)


def test_json_row_missing_from_sql_is_reported(repo_fixtures: dict) -> None:
    sql_rows = parity.parse_sql_insert_rows(repo_fixtures["sql"])[:-1]

    errors = parity.compare_json_sql_rows(repo_fixtures["fixture"]["input_cases"], sql_rows)

    assert any("SQL fixture에 없다" in e for e in errors)


def test_rounding_equal_values_are_not_drift(repo_fixtures: dict) -> None:
    """round 4 결과가 같은 값(0.7 vs 0.7000)은 drift로 잡지 않는다."""
    fixture = copy.deepcopy(repo_fixtures["fixture"])
    ref_rows = parity.compute_reference_rows(fixture["input_cases"])
    for row in fixture["expected_rows"]:
        if row["strategy"] == "A":
            row["win_rate"] = 0.7  # 의미상 0.7000과 동일
    errors = parity.compare_ci_rows(ref_rows, fixture["expected_rows"], "Python", "expected")
    assert not any("win_rate" in e for e in errors)
