"""tools/check_sprint_status.py 계약 테스트.

sprint-status.yaml은 손으로 편집하는 action item 원장인데, 커밋된 상태로 유효하지 않은
YAML이었던 전례가 있다(잔여 쉼표). 이 게이트가 그 재발을 막는지 고정한다.
"""

from __future__ import annotations

import importlib.util
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
_spec = importlib.util.spec_from_file_location(
    "check_sprint_status", ROOT / "tools" / "check_sprint_status.py"
)
sprint = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(sprint)


def item(**overrides) -> dict:
    base = {
        "id": "epic-1-retro-item-1-thing",
        "epic": 1,
        "action": "무언가를 한다.",
        "owner": "개발",
        "status": "open",
    }
    base.update(overrides)
    return base


def data(items: list[dict]) -> dict:
    return {"project": "wave-double", "development_status": {}, "action_items": items}


def test_committed_sprint_status_passes() -> None:
    assert sprint.main() == 0


def test_valid_document_has_no_errors() -> None:
    assert sprint.check(data([item(status="done", ref="evidence.md"), item(id="other")])) == []


def test_trailing_comma_makes_the_file_invalid_yaml(tmp_path: Path) -> None:
    """실제로 커밋돼 있던 파괴 패턴: 큰따옴표 값 끝의 잔여 쉼표."""
    path = tmp_path / "sprint-status.yaml"
    path.write_text(
        'project: x\naction_items:\n  - id: "a"\n    ref: "evidence.md",\n  - id: "b"\n',
        encoding="utf-8",
    )

    with pytest.raises(SystemExit) as excinfo:
        sprint.load(path)

    assert "YAML" in str(excinfo.value)


def test_double_quote_inside_a_quoted_scalar_is_invalid_yaml(tmp_path: Path) -> None:
    path = tmp_path / "sprint-status.yaml"
    path.write_text(
        'project: x\naction_items:\n  - id: "a"\n    ref: "WORKFLOW_REF("main") 결함"\n',
        encoding="utf-8",
    )

    with pytest.raises(SystemExit):
        sprint.load(path)


def test_missing_top_level_key_is_reported() -> None:
    errors = sprint.check({"action_items": []})

    assert any("'project'" in e for e in errors)
    assert any("'development_status'" in e for e in errors)


def test_unknown_status_is_reported() -> None:
    errors = sprint.check(data([item(status="wontfix")]))

    assert any("status가 허용 값이 아니다" in e for e in errors)


def test_done_item_without_evidence_is_reported() -> None:
    """근거 없는 done은 추적 가치가 없다."""
    errors = sprint.check(data([item(status="done")]))

    assert any("근거(ref)가 없다" in e for e in errors)


def test_in_progress_item_without_evidence_is_reported() -> None:
    errors = sprint.check(data([item(status="in-progress", ref="   ")]))

    assert any("근거(ref)가 없다" in e for e in errors)


def test_open_item_does_not_need_evidence() -> None:
    assert sprint.check(data([item(status="open")])) == []


def test_missing_required_field_is_reported() -> None:
    broken = item()
    del broken["owner"]

    errors = sprint.check(data([broken]))

    assert any("'owner'가 없다" in e for e in errors)


def test_duplicate_id_is_reported() -> None:
    errors = sprint.check(data([item(), item()]))

    assert any("중복된다" in e for e in errors)


def test_action_items_must_be_a_list() -> None:
    errors = sprint.check({"project": "x", "development_status": {}, "action_items": "nope"})

    assert any("리스트가 아니다" in e for e in errors)
