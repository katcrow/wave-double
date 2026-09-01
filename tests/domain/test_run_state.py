from datetime import date, time

import pytest

from domain.run_state import (
    BatchKind,
    LogicalRunKey,
    StageStatus,
    can_publish,
    initial_stage_status,
    validate_stage_transition,
)


def test_logical_key_uses_final_for_close_and_half_hour_slot_for_intraday():
    assert LogicalRunKey(date(2026, 9, 1), BatchKind.CLOSE).value == "close:2026-09-01"
    assert LogicalRunKey(date(2026, 9, 1), BatchKind.INTRADAY, time(14, 30)).value == "intraday:2026-09-01:14:30"
    assert LogicalRunKey.parse("premarket:2026-09-01").batch_kind is BatchKind.PREMARKET


def test_invalid_logical_key_slot_is_rejected():
    with pytest.raises(ValueError):
        LogicalRunKey(date(2026, 9, 1), BatchKind.INTRADAY, time(14, 15))
    with pytest.raises(ValueError):
        LogicalRunKey.parse("intraday:2026-09-01:14:15")
    with pytest.raises(ValueError):
        LogicalRunKey.parse("close:2026-09-01:14:30")


def test_initial_stage_registry_has_exactly_five_pending_stages():
    assert set(initial_stage_status()) == {
        "candidates", "tags", "supply_3day", "market_supply", "outcome_tracking"
    }
    assert all(value is StageStatus.PENDING for value in initial_stage_status().values())


def test_stage_transitions_are_forward_only_and_terminal_writes_are_idempotent():
    assert validate_stage_transition("pending", "running") is StageStatus.RUNNING
    assert validate_stage_transition("running", "success") is StageStatus.SUCCESS
    assert validate_stage_transition("success", "success") is StageStatus.SUCCESS
    with pytest.raises(ValueError):
        validate_stage_transition("success", "running")


def test_only_successful_candidates_can_publish_in_epic_one():
    assert can_publish({"candidates": "success"})
    assert not can_publish({"candidates": "partial"})


def test_stage_registry_uses_run_id_and_stage_callable_contract():
    from uuid import uuid4

    from domain.stage_registry import StageRegistry

    run_id = uuid4()
    calls = []

    def verifier(received_run_id, received_stage):
        calls.append((received_run_id, received_stage))
        return True

    registry = StageRegistry({"tags": verifier})
    assert registry.verify(run_id, "tags") is True
    assert calls == [(run_id, "tags")]


def test_default_candidates_verifier_receives_uuid_and_stage_name():
    from uuid import uuid4

    from domain.stage_registry import default_registry

    assert default_registry.verify(uuid4(), "candidates") is True
    with pytest.raises(KeyError, match="tags"):
        default_registry.verify(uuid4(), "tags")
