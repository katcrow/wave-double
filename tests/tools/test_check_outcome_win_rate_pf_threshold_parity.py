"""Story 5.9 이탈 임계값 parity 계약 테스트."""

from __future__ import annotations

import copy
import importlib.util
import json

import pytest

ROOT = __import__("pathlib").Path(__file__).resolve().parents[2]
spec = importlib.util.spec_from_file_location(
    "check_outcome_win_rate_pf_threshold_parity",
    ROOT / "tools" / "check_outcome_win_rate_pf_threshold_parity.py",
)
parity = importlib.util.module_from_spec(spec)
spec.loader.exec_module(parity)


@pytest.fixture
def repo_fixture() -> dict:
    return json.loads((parity.FIXTURE_DIR / "input_cases.json").read_text(encoding="utf-8"))


def test_repository_fixture_is_in_sync() -> None:
    assert parity.main() == 0


def test_fixture_covers_warning_and_null_paths(repo_fixture: dict) -> None:
    rows = parity.compute_reference_rows(repo_fixture["input_cases"])
    by_strategy = {row["strategy"]: row for row in rows}
    assert by_strategy["A"]["win_rate_threshold_breached"] is True
    assert by_strategy["A"]["profit_factor_threshold_breached"] is True
    assert by_strategy["A"]["threshold_warning"] is True
    assert by_strategy["B"]["threshold_warning"] is True
    assert by_strategy["C"]["sample_gate_passed"] is False
    assert all(by_strategy["C"][field] is None for field in (
        "expected_profit_factor", "win_rate_threshold_breached",
        "profit_factor_threshold_breached", "threshold_warning",
    ))
    assert all(by_strategy["D"][field] is None for field in (
        "expected_profit_factor", "win_rate_threshold_breached",
        "profit_factor_threshold_breached", "threshold_warning",
    ))
    assert by_strategy[None]["expected_profit_factor"] is None


def test_exact_threshold_boundaries_are_not_warnings() -> None:
    win_breached, pf_breached, warning = parity.compute_threshold_flags(
        0.7871, 2.5675, 0.6871, 2.0540
    )
    assert (win_breached, pf_breached, warning) == (False, False, False)


def test_thresholds_are_strictly_exceeded() -> None:
    assert parity.compute_threshold_flags(0.7872, 2.5676, 0.6871, 2.0540) == (True, True, True)


def test_expected_pf_mapping_drift_is_reported(repo_fixture: dict) -> None:
    mutated = copy.deepcopy(repo_fixture["expected_rows"])
    for row in mutated:
        if row["strategy"] == "A":
            row["expected_profit_factor"] = 2.0770
    errors = parity.compare_result_rows(
        parity.compute_reference_rows(repo_fixture["input_cases"]), mutated, "Python", "expected"
    )
    assert any("expected_profit_factor" in error for error in errors)


def test_ci_primary_judgement_is_preserved(repo_fixture: dict) -> None:
    rows = parity.compute_reference_rows(repo_fixture["input_cases"])
    a_row = next(row for row in rows if row["strategy"] == "A")
    assert a_row["expected_in_ci"] is False
    assert a_row["threshold_warning"] is True


def test_e_and_f_keep_no_expectation_when_gate_passes(repo_fixture: dict) -> None:
    source = [row for row in repo_fixture["input_cases"] if row["strategy"] == "D"]
    rows = [dict(row, strategy=strategy, ticker=f"{strategy}{row['ticker'][2:]}") for strategy in ("E", "F") for row in source]
    result = {row["strategy"]: row for row in parity.compute_reference_rows(rows)}
    for strategy in ("E", "F"):
        assert result[strategy]["sample_gate_passed"] is True
        assert result[strategy]["expected_profit_factor"] is None
        assert result[strategy]["win_rate_threshold_breached"] is None
        assert result[strategy]["profit_factor_threshold_breached"] is None
        assert result[strategy]["threshold_warning"] is None


def test_timeout_zero_return_and_exception_counts_are_preserved() -> None:
    rows = []
    for i in range(1, 11):
        rows.append({"strategy": "A", "status": "TP", "return_pct": 2.0})
    for i in range(11, 21):
        rows.append({"strategy": "A", "status": "SL", "return_pct": -1.0})
    rows.append({"strategy": "A", "status": "TIMEOUT", "return_pct": 1.0})
    for i in range(22, 31):
        rows.append({"strategy": "A", "status": "TP", "return_pct": 0.0})
    rows.extend(
        {"strategy": "A", "status": status, "return_pct": None}
        for status in ("OPEN", "SUSPENDED", "DELISTED")
    )
    for i, row in enumerate(rows):
        row.update({"ticker": f"EDGE{i:03d}", "entry_date": f"2099-03-{i + 1:02d}"})
    result = next(row for row in parity.compute_reference_rows(rows) if row["strategy"] == "A")
    assert result["total_settled"] == 30
    assert result["wins"] == 11
    assert result["losses"] == 10
    assert result["open_count"] == result["suspended_count"] == result["delisted_count"] == 1


def test_warning_is_true_when_only_one_metric_is_available() -> None:
    assert parity.compute_threshold_flags(0.5, None, 0.6871, 2.0540) == (True, None, True)
    assert parity.compute_threshold_flags(None, 1.0, 0.6871, 2.0540) == (None, True, True)


def test_missing_sql_expected_row_is_reported(repo_fixture: dict) -> None:
    sql = parity.SQL_PATH.read_text(encoding="utf-8")
    expected = parity.parse_sql_expected_rows(sql)[:-1]
    errors = parity.compare_result_rows(
        parity.compute_reference_rows(repo_fixture["input_cases"]), expected, "Python", "SQL"
    )
    assert any("strategy=None" in error for error in errors)
