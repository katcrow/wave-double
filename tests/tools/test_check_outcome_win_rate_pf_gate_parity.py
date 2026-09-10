"""tools/check_outcome_win_rate_pf_gate_parity.py 계약 테스트 (story 5-7).

drift gate 자체가 "무엇을 놓치는가"가 중요하므로, 실제 저장소 fixture가 통과하는 것과
각 종류의 drift(게이트 라벨 오기, boolean 반전, win_rate 미NULL화 등)를 심어 넣었을 때
실패하는 것을 함께 고정한다. 경계값(29 vs 30)이 fixture에 고정돼 있는지도 검증한다.
"""

from __future__ import annotations

import copy
import importlib.util
import json
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
_spec = importlib.util.spec_from_file_location(
    "check_outcome_win_rate_pf_gate_parity",
    ROOT / "tools" / "check_outcome_win_rate_pf_gate_parity.py",
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


def test_gate_expected_has_three_rows(repo_fixtures: dict) -> None:
    """전략 A(29건, 실패) + 전략 B(30건, 통과) + rollup 전체 3행이 fixture에 있어야 한다."""
    rows = parity.parse_sql_gate_expected(repo_fixtures["sql"])
    assert len(rows) == 3
    strategies = {r["strategy"] for r in rows}
    assert strategies == {"A", "B", None}


def test_boundary_below_gate_strategy_a() -> None:
    """전략 A는 종결 정확히 29건으로 게이트 실패해야 한다(경계값 boundary)."""
    fixture = parity.load_json_fixture()
    ref_rows = parity.compute_reference_rows(fixture["input_cases"])
    a_row = next(r for r in ref_rows if r["strategy"] == "A")
    assert a_row["total_settled"] == 29
    assert a_row["sample_gate_passed"] is False
    assert a_row["win_rate"] is None
    assert a_row["profit_factor"] is None
    assert a_row["sample_gate_label"] == "표본 부족 (29/30)"


def test_boundary_at_gate_strategy_b() -> None:
    """전략 B는 종결 정확히 30건으로 게이트를 통과해야 한다(경계값 boundary)."""
    fixture = parity.load_json_fixture()
    ref_rows = parity.compute_reference_rows(fixture["input_cases"])
    b_row = next(r for r in ref_rows if r["strategy"] == "B")
    assert b_row["total_settled"] == 30
    assert b_row["sample_gate_passed"] is True
    assert b_row["win_rate"] is not None
    assert b_row["profit_factor"] is not None
    assert b_row["sample_gate_label"] is None


def test_rollup_total_passes_gate_with_combined_settled() -> None:
    """전략 A(29)+B(30) 혼재 시 rollup 전체(59건)는 게이트를 통과해야 한다."""
    fixture = parity.load_json_fixture()
    ref_rows = parity.compute_reference_rows(fixture["input_cases"])
    total_row = next(r for r in ref_rows if r["strategy"] is None)
    assert total_row["total_settled"] == 59
    assert total_row["sample_gate_passed"] is True
    assert total_row["sample_gate_label"] is None


def test_always_counts_present_even_when_gate_fails() -> None:
    """게이트 실패 행(전략 A)도 open_count/suspended_count 등은 숨기지 않고 채워진다."""
    fixture = parity.load_json_fixture()
    ref_rows = parity.compute_reference_rows(fixture["input_cases"])
    a_row = next(r for r in ref_rows if r["strategy"] == "A")
    assert a_row["open_count"] == 2
    assert a_row["suspended_count"] == 1
    assert a_row["total_settled"] == 29


def test_rollup_matches_sum_of_strategies() -> None:
    fixture = parity.load_json_fixture()
    ref_rows = parity.compute_reference_rows(fixture["input_cases"])
    errors = parity.verify_rollup_matches_sum(ref_rows)
    assert not errors


def test_rollup_mismatch_is_reported() -> None:
    rows = [
        {"strategy": "A", "total_settled": 29, "wins": 29, "losses": 0, "open_count": 0,
         "suspended_count": 0, "delisted_count": 0},
        {"strategy": None, "total_settled": 999, "wins": 29, "losses": 0, "open_count": 0,
         "suspended_count": 0, "delisted_count": 0},
    ]
    errors = parity.verify_rollup_matches_sum(rows)
    assert any("total_settled" in e for e in errors)


def test_missing_rollup_row_is_reported() -> None:
    rows = [
        {"strategy": "A", "total_settled": 29, "wins": 29, "losses": 0, "open_count": 0,
         "suspended_count": 0, "delisted_count": 0},
    ]
    errors = parity.verify_rollup_matches_sum(rows)
    assert any("rollup 전체" in e for e in errors)


def test_gate_label_typo_drift_is_reported(repo_fixtures: dict) -> None:
    fixture = copy.deepcopy(repo_fixtures["fixture"])
    for row in fixture["expected_rows"]:
        if row["strategy"] == "A":
            row["sample_gate_label"] = "표본 부족 (28/30)"  # 오기
    ref_rows = parity.compute_reference_rows(fixture["input_cases"])
    errors = parity.compare_gate_rows(ref_rows, fixture["expected_rows"], "Python", "expected")
    assert any("sample_gate_label" in e for e in errors)


def test_gate_passed_boolean_flip_drift_is_reported(repo_fixtures: dict) -> None:
    fixture = copy.deepcopy(repo_fixtures["fixture"])
    for row in fixture["expected_rows"]:
        if row["strategy"] == "B":
            row["sample_gate_passed"] = False  # 반전
    ref_rows = parity.compute_reference_rows(fixture["input_cases"])
    errors = parity.compare_gate_rows(ref_rows, fixture["expected_rows"], "Python", "expected")
    assert any("sample_gate_passed" in e for e in errors)


def test_win_rate_not_nulled_on_gate_fail_drift_is_reported(repo_fixtures: dict) -> None:
    """게이트 실패 행인데 win_rate가 NULL이 아니게(미NULL화) drift가 발생하면 잡아야 한다."""
    fixture = copy.deepcopy(repo_fixtures["fixture"])
    for row in fixture["expected_rows"]:
        if row["strategy"] == "A":
            row["win_rate"] = 1.0000  # 게이트 실패인데 값이 채워짐
    ref_rows = parity.compute_reference_rows(fixture["input_cases"])
    errors = parity.compare_gate_rows(ref_rows, fixture["expected_rows"], "Python", "expected")
    assert any("win_rate" in e for e in errors)


def test_profit_factor_drift_is_reported(repo_fixtures: dict) -> None:
    fixture = copy.deepcopy(repo_fixtures["fixture"])
    for row in fixture["expected_rows"]:
        if row["strategy"] == "B":
            row["profit_factor"] = 9.9999
    ref_rows = parity.compute_reference_rows(fixture["input_cases"])
    errors = parity.compare_gate_rows(ref_rows, fixture["expected_rows"], "Python", "expected")
    assert any("profit_factor" in e for e in errors)


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


def test_all_loss_gate_passed_group_has_null_profit_factor() -> None:
    """전략 전체가 손실(승리 0건)이고 게이트를 통과하면 gross_win이 NULL이므로 profit_factor도
    NULL이어야 한다 — SQL의 sum(...) filter(...)가 승리 없을 때 NULL을 반환하고 NULL/x가
    NULL이 되는 것과 동일해야 한다. wins==0인데 gross_loss>0만 보고 profit_factor를
    0.0으로 계산하는 회귀를 고정한다(review: verification-gap)."""
    rows = [
        {"strategy": "Z", "status": "SL", "return_pct": -1.0}
        for _ in range(30)
    ]
    ref_rows = parity.compute_reference_rows(rows)
    z_row = next(r for r in ref_rows if r["strategy"] == "Z")
    assert z_row["total_settled"] == 30
    assert z_row["sample_gate_passed"] is True
    assert z_row["wins"] == 0
    assert z_row["gross_win"] is None
    assert z_row["profit_factor"] is None


def test_zero_settled_group_has_null_gate_fields() -> None:
    """종결 거래가 0건(전부 OPEN)인 전략은 게이트를 통과할 수 없고 win_rate/profit_factor는
    NULL이어야 한다 — SQL fixture의 NO_SETTLED 시나리오(`tests/sql/test_outcome_win_rate_pf_gated.sql`)를
    Python 기준값 계산에도 동일하게 고정한다."""
    rows = [
        {"strategy": "NOSETTLE", "status": "OPEN", "return_pct": None}
        for _ in range(3)
    ]
    ref_rows = parity.compute_reference_rows(rows)
    row = next(r for r in ref_rows if r["strategy"] == "NOSETTLE")
    assert row["total_settled"] == 0
    assert row["sample_gate_passed"] is False
    assert row["win_rate"] is None
    assert row["profit_factor"] is None
    assert row["sample_gate_label"] == "표본 부족 (0/30)"


def test_rounding_equal_values_are_not_drift(repo_fixtures: dict) -> None:
    """round 4 결과가 같은 값(0.5 vs 0.5000)은 drift로 잡지 않는다."""
    fixture = copy.deepcopy(repo_fixtures["fixture"])
    ref_rows = parity.compute_reference_rows(fixture["input_cases"])
    for row in fixture["expected_rows"]:
        if row["strategy"] == "B":
            row["win_rate"] = 0.5  # 의미상 0.5000과 동일
    errors = parity.compare_gate_rows(ref_rows, fixture["expected_rows"], "Python", "expected")
    assert not any("win_rate" in e for e in errors)
