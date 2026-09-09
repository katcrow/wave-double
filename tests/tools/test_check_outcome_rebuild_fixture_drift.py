"""tools/check_outcome_rebuild_fixture_drift.py 계약 테스트(epic-3-retro-item-17).

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
    "check_outcome_rebuild_fixture_drift",
    ROOT / "tools" / "check_outcome_rebuild_fixture_drift.py",
)
drift = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(drift)


@pytest.fixture
def repo_fixtures() -> dict:
    return {
        "sql": drift.SQL_PATH.read_text(encoding="utf-8"),
        "events": json.loads((drift.FIXTURE_DIR / "events.json").read_text(encoding="utf-8")),
        "observations": json.loads(
            (drift.FIXTURE_DIR / "observations.json").read_text(encoding="utf-8")
        ),
        "projection": json.loads(
            (drift.FIXTURE_DIR / "expected_projection.json").read_text(encoding="utf-8")
        ),
    }


def test_repository_fixtures_are_in_sync() -> None:
    assert drift.main() == 0


def test_sql_parsing_finds_the_ac1_sample_ledger(repo_fixtures: dict) -> None:
    sql = repo_fixtures["sql"]

    assert len(drift.parse_sql_events(sql)) == len(repo_fixtures["events"])
    assert len(drift.parse_sql_observations(sql)) == len(repo_fixtures["observations"])
    assert len(drift.parse_sql_expected_projection(sql)) == len(repo_fixtures["projection"])


def test_ac1_setup_region_excludes_later_story_blocks(repo_fixtures: dict) -> None:
    """Story 6.5 legacy 케이스의 이벤트는 JSON fixture의 대상이 아니다."""
    region = drift.ac1_setup_region(repo_fixtures["sql"])

    assert "10000000-0000-0000-0000-000000000001" in region
    assert "10000000-0000-0000-0000-00000000000d" not in region


def test_event_missing_from_json_is_reported(repo_fixtures: dict) -> None:
    sql_events = drift.parse_sql_events(repo_fixtures["sql"])
    json_events = repo_fixtures["events"][:-1]

    errors = drift.compare_events(json_events, sql_events)

    assert any("events.json에 없다" in e for e in errors)


def test_event_missing_from_sql_is_reported(repo_fixtures: dict) -> None:
    sql_events = drift.parse_sql_events(repo_fixtures["sql"])[:-1]

    errors = drift.compare_events(repo_fixtures["events"], sql_events)

    assert any("SQL fixture에 없다" in e for e in errors)


def test_event_payload_drift_is_reported(repo_fixtures: dict) -> None:
    json_events = [dict(row) for row in repo_fixtures["events"]]
    json_events[0]["payload"] = dict(json_events[0]["payload"], entry_price=999)

    errors = drift.compare_events(json_events, drift.parse_sql_events(repo_fixtures["sql"]))

    assert any("payload 불일치" in e for e in errors)


def test_event_command_type_drift_is_reported(repo_fixtures: dict) -> None:
    json_events = [dict(row) for row in repo_fixtures["events"]]
    json_events[1]["command_type"] = "TP"

    errors = drift.compare_events(json_events, drift.parse_sql_events(repo_fixtures["sql"]))

    assert any("command_type 불일치" in e for e in errors)


def test_observation_value_drift_is_reported(repo_fixtures: dict) -> None:
    json_obs = [dict(row) for row in repo_fixtures["observations"]]
    json_obs[0]["close"] = 12345

    errors = drift.compare_observations(
        json_obs, drift.parse_sql_observations(repo_fixtures["sql"])
    )

    assert errors


def test_observation_row_count_drift_is_reported(repo_fixtures: dict) -> None:
    errors = drift.compare_observations(
        repo_fixtures["observations"][:-1], drift.parse_sql_observations(repo_fixtures["sql"])
    )

    assert any("개수 불일치" in e for e in errors)


def test_projection_field_drift_is_reported(repo_fixtures: dict) -> None:
    json_projection = [dict(row) for row in repo_fixtures["projection"]]
    json_projection[1]["return_pct"] = -9.9

    errors = drift.compare_projection(
        json_projection, drift.parse_sql_expected_projection(repo_fixtures["sql"])
    )

    assert any("return_pct 불일치" in e for e in errors)


def test_projection_status_drift_is_reported(repo_fixtures: dict) -> None:
    json_projection = [dict(row) for row in repo_fixtures["projection"]]
    json_projection[0]["status"] = "TP"

    errors = drift.compare_projection(
        json_projection, drift.parse_sql_expected_projection(repo_fixtures["sql"])
    )

    assert any("status 불일치" in e for e in errors)


def test_projection_nullability_drift_is_reported(repo_fixtures: dict) -> None:
    """SQL이 `exit_date is null`을 주장하는데 JSON에 값이 있으면 잡아야 한다."""
    json_projection = [dict(row) for row in repo_fixtures["projection"]]
    json_projection[0]["exit_date"] = "2099-06-02"

    errors = drift.compare_projection(
        json_projection, drift.parse_sql_expected_projection(repo_fixtures["sql"])
    )

    assert any("exit_date 불일치" in e for e in errors)


def test_projection_row_missing_from_sql_is_reported(repo_fixtures: dict) -> None:
    sql_rows = drift.parse_sql_expected_projection(repo_fixtures["sql"])[:-1]

    errors = drift.compare_projection(repo_fixtures["projection"], sql_rows)

    assert any("SQL AC1 assertion이 없다" in e for e in errors)


def test_row_count_assertion_must_match_projection_length(repo_fixtures: dict) -> None:
    assert drift.check_row_count_assertion(repo_fixtures["sql"], len(repo_fixtures["projection"])) == []
    assert drift.check_row_count_assertion(repo_fixtures["sql"], 99)


def test_missing_setup_marker_fails_loudly() -> None:
    """구조가 바뀌어 파싱이 불가능해지면 조용히 통과하지 않는다."""
    with pytest.raises(SystemExit):
        drift.ac1_setup_region("-- 아무 marker도 없는 SQL\nbegin;\ncommit;\n")


def test_missing_insert_section_fails_loudly() -> None:
    with pytest.raises(SystemExit):
        drift.insert_section("select 1;", "outcome_events")
