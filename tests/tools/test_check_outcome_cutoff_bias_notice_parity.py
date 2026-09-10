"""Story 5.10 컷오프 편향 고지 parity 계약 테스트."""

from __future__ import annotations

import copy
import importlib.util
import json

import pytest

ROOT = __import__("pathlib").Path(__file__).resolve().parents[2]
spec = importlib.util.spec_from_file_location(
    "check_outcome_cutoff_bias_notice_parity",
    ROOT / "tools" / "check_outcome_cutoff_bias_notice_parity.py",
)
parity = importlib.util.module_from_spec(spec)
spec.loader.exec_module(parity)


@pytest.fixture
def repo_fixture() -> dict:
    return json.loads((parity.FIXTURE_DIR / "input_cases.json").read_text(encoding="utf-8"))


def test_repository_fixture_is_in_sync() -> None:
    assert parity.main() == 0


def test_zero_and_positive_timeout_counts_keep_notice_contract(repo_fixture: dict) -> None:
    rows = {row["strategy"]: row for row in parity.compute_reference_rows(repo_fixture["input_cases"])}
    assert rows["A"]["timeout_count"] == 1
    assert rows["B"]["timeout_count"] == 1
    assert rows["C"]["timeout_count"] == 0
    assert rows["A"]["cutoff_bias_label"] == "TIMEOUT 0% / PF차 ±0"
    assert rows["B"]["cutoff_bias_timeout_rate"] == 0.0037
    assert rows["B"]["cutoff_bias_profit_factor_delta"] == 0.0125
    assert rows["C"]["cutoff_bias_sample_size"] == 30


def test_29_and_30_boundaries_keep_gate_and_notice_independent(repo_fixture: dict) -> None:
    rows = parity.compute_reference_rows(repo_fixture["input_cases"])
    by_strategy = {row["strategy"]: row for row in rows}
    assert by_strategy["C"]["total_settled"] == 29
    assert by_strategy["C"]["sample_gate_passed"] is False
    assert by_strategy["C"]["win_rate"] is None
    assert by_strategy["C"]["timeout_count"] == 0
    assert by_strategy["C"]["cutoff_bias_timeout_rate"] == 0.0
    assert by_strategy["D"]["total_settled"] == 30
    assert by_strategy["D"]["sample_gate_passed"] is True


def test_abc_mapping_and_de_fg_rollup_null_contract(repo_fixture: dict) -> None:
    extra = []
    for source in repo_fixture["input_cases"]:
        if source["strategy"] == "D":
            for strategy in ("E", "F"):
                extra.append({**source, "ticker": f"{strategy}{source['ticker'][2:]}", "strategy": strategy})
    rows = parity.compute_reference_rows(repo_fixture["input_cases"] + extra)
    by_strategy = {row["strategy"]: row for row in rows}
    assert by_strategy["A"]["cutoff_bias_profit_factor_delta"] == 0.0
    assert by_strategy["B"]["cutoff_bias_label"] == "TIMEOUT 0.37% / PF차 +0.0125"
    assert by_strategy["C"]["cutoff_bias_label"] == "TIMEOUT 0% / PF차 ±0"
    for strategy in ("D", "E", "F", None):
        assert by_strategy[strategy]["cutoff_bias_sample_size"] is None
        assert by_strategy[strategy]["cutoff_bias_timeout_rate"] is None
        assert by_strategy[strategy]["cutoff_bias_profit_factor_delta"] is None
        assert by_strategy[strategy]["cutoff_bias_label"] is None


def test_existing_59_columns_are_preserved(repo_fixture: dict) -> None:
    rows = parity.compute_reference_rows(repo_fixture["input_cases"])
    for row in rows:
        assert set(parity.CORE_FIELDS).issubset(row)
    mutated = copy.deepcopy(rows)
    mutated[0]["expected_in_ci"] = not mutated[0]["expected_in_ci"]
    errors = parity.compare_result_rows(rows, mutated, "5-9", "mutated")
    assert any("expected_in_ci" in error for error in errors)


def test_notice_drift_is_reported(repo_fixture: dict) -> None:
    expected = copy.deepcopy(repo_fixture["expected_rows"])
    expected[0]["cutoff_bias_label"] = "잘못된 고지"
    errors = parity.compare_result_rows(
        parity.compute_reference_rows(repo_fixture["input_cases"]), expected, "Python", "JSON"
    )
    assert any("cutoff_bias_label" in error for error in errors)


def test_timeout_is_not_reclassified_or_removed_from_denominator() -> None:
    rows = [
        {"strategy": "A", "status": "TP", "return_pct": 2.0},
        {"strategy": "A", "status": "SL", "return_pct": -1.0},
        {"strategy": "A", "status": "TIMEOUT", "return_pct": 1.0},
        {"strategy": "A", "status": "OPEN", "return_pct": None},
        {"strategy": "A", "status": "SUSPENDED", "return_pct": None},
        {"strategy": "A", "status": "DELISTED", "return_pct": None},
    ]
    for index, row in enumerate(rows):
        row.update({"ticker": f"EDGE{index:03d}", "entry_date": f"2099-03-{index + 1:02d}"})
    result = next(row for row in parity.compute_reference_rows(rows) if row["strategy"] == "A")
    assert result["total_settled"] == 3
    assert result["wins"] == 2
    assert result["timeout_count"] == 1
    assert result["open_count"] == result["suspended_count"] == result["delisted_count"] == 1
