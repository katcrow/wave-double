"""tools/check_outcome_win_rate_pf_source_parity.py 계약 테스트 (story 5-6).

drift gate 자체가 "무엇을 놓치는가"가 중요하므로, 실제 저장소 fixture가 통과하는 것과
각 종류의 drift를 심어 넣었을 때 실패하는 것을 함께 고정한다.
"""

from __future__ import annotations

import copy
import importlib.util
import json
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
_spec = importlib.util.spec_from_file_location(
    "check_outcome_win_rate_pf_source_parity",
    ROOT / "tools" / "check_outcome_win_rate_pf_source_parity.py",
)
parity = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(parity)


@pytest.fixture
def repo_fixtures() -> dict:
    return {
        "sql": parity.SQL_PATH.read_text(encoding="utf-8"),
        "json_data": json.loads(
            (parity.FIXTURE_DIR / "input_cases.json").read_text(encoding="utf-8")
        ),
    }


def test_repository_fixtures_are_in_sync() -> None:
    assert parity.main() == 0


def test_setup_marker_exists(repo_fixtures: dict) -> None:
    assert parity.SETUP_MARKER in repo_fixtures["sql"]


def test_missing_setup_marker_fails_loudly() -> None:
    with pytest.raises(SystemExit, match="parity fixture setup 마커"):
        parity._setup_region("begin;\ninsert into public.logical_runs(a) values (1);\n")


def test_contributor_weight_drift_is_reported(repo_fixtures: dict) -> None:
    data = copy.deepcopy(repo_fixtures["json_data"])
    data["contributors"][2]["contribution_weight"] = 0.2
    python_cells = parity.compute_reference_cells(data)
    errors = parity.compare_sql_vs_sql(python_cells, data["expected_cells"], "Python", "expected")
    assert errors


def test_contributor_row_drift_is_reported(repo_fixtures: dict) -> None:
    data = copy.deepcopy(repo_fixtures["json_data"])
    data["contributors"] = [c for c in data["contributors"] if not (c["ticker"] == "A0005" and c["source"] == "t1856")]
    python_cells = parity.compute_reference_cells(data)
    errors = parity.compare_sql_vs_sql(python_cells, data["expected_cells"], "Python", "expected")
    assert errors


def test_primary_rule_change_drift_is_reported(repo_fixtures: dict) -> None:
    flipped_priority = {"t1859": 2, "t1852": 1, "t1856": 0}
    python_cells = parity.compute_reference_cells(repo_fixtures["json_data"], flipped_priority)
    errors = parity.compare_sql_vs_sql(python_cells, repo_fixtures["json_data"]["expected_cells"], "flipped", "expected")
    assert errors


def test_canonical_change_drift_is_reported(repo_fixtures: dict) -> None:
    data = copy.deepcopy(repo_fixtures["json_data"])
    data["canonicals"][0]["attempt_run_id"] = "10000000-0000-0000-0000-000000000099"
    python_cells = parity.compute_reference_cells(data)
    errors = parity.compare_sql_vs_sql(python_cells, data["expected_cells"], "Python", "expected")
    assert errors


def test_expected_cell_drift_is_reported(repo_fixtures: dict) -> None:
    data = copy.deepcopy(repo_fixtures["json_data"])
    data["expected_cells"][0]["gross_win"] = 9.99
    errors = parity.compare_json_vs_sql(data["expected_cells"], repo_fixtures["json_data"]["expected_cells"])
    assert errors


def test_outcome_row_drift_is_reported(repo_fixtures: dict) -> None:
    data = copy.deepcopy(repo_fixtures["json_data"])
    data["outcomes"][0]["return_pct"] = 1.0
    python_cells = parity.compute_reference_cells(data)
    errors = parity.compare_sql_vs_sql(python_cells, data["expected_cells"], "Python", "expected")
    assert errors


def test_compute_reference_cell_count() -> None:
    cells = parity.compute_reference_cells(parity.load_json_input_cases())
    assert len(cells) == 6


def test_null_source_cell_exists() -> None:
    cells = parity.compute_reference_cells(parity.load_json_input_cases())
    null_cells = [c for c in cells if c["source"] is None]
    assert len(null_cells) == 1
    assert null_cells[0]["strategy"] == "C"
    assert null_cells[0]["delisted_count"] == 1


def test_overall_sum_matches() -> None:
    data = parity.load_json_input_cases()
    cells = parity.compute_reference_cells(data)
    errors = parity.verify_overall(cells, data["expected_overall"])
    assert not errors


def test_canonical_invariants_pass() -> None:
    data = parity.load_json_input_cases()
    errors = parity.verify_candidate_canonical_invariants(data["candidates"], data["canonicals"])
    assert not errors