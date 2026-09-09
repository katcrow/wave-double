"""tools/check_epic_scope.py 계약 테스트(epic-7-retro-item-30).

범위 게이트가 조용히 통과하면 Epic 산출물과 실험 산출물이 섞인 커밋을 막지 못한다.
manifest 해석, ignore 규칙, 누락 manifest의 명시적 실패를 고정한다.
"""

from __future__ import annotations

import importlib.util
from pathlib import Path

import pytest

ROOT = Path(__file__).resolve().parents[2]
_spec = importlib.util.spec_from_file_location(
    "check_epic_scope", ROOT / "tools" / "check_epic_scope.py"
)
scope = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(scope)


def test_exact_path_entry_matches_only_that_path() -> None:
    entries = ["apps/batch/scheduler.py"]

    assert scope.is_allowed("apps/batch/scheduler.py", entries)
    assert not scope.is_allowed("apps/batch/scheduler_extra.py", entries)
    assert not scope.is_allowed("apps/batch/tags_stage.py", entries)


def test_directory_entry_matches_everything_under_it() -> None:
    entries = ["apps/batch/"]

    assert scope.is_allowed("apps/batch/scheduler.py", entries)
    assert scope.is_allowed("apps/batch/nested/deep.py", entries)
    assert not scope.is_allowed("apps/web/page.tsx", entries)


def test_manifest_comments_and_blank_lines_are_ignored(tmp_path: Path) -> None:
    path = tmp_path / "epic-x.txt"
    path.write_text("# 주석\n\napps/batch/scheduler.py\n  apps/web/page.tsx  \n", encoding="utf-8")

    assert scope.load_manifest(path) == ["apps/batch/scheduler.py", "apps/web/page.tsx"]


def test_manifest_with_no_entries_is_an_error(tmp_path: Path) -> None:
    path = tmp_path / "epic-empty.txt"
    path.write_text("# 주석만 있다\n\n", encoding="utf-8")

    with pytest.raises(ValueError):
        scope.load_manifest(path)


def test_windows_separators_are_normalized(tmp_path: Path) -> None:
    path = tmp_path / "epic-win.txt"
    path.write_text("apps\\batch\\scheduler.py\n", encoding="utf-8")

    assert scope.load_manifest(path) == ["apps/batch/scheduler.py"]


def test_experiment_scratch_output_is_ignored_by_the_gate() -> None:
    """탐색적 백테스트 산출물이 범위 위반으로 잡히면 게이트가 쓸모를 잃는다."""
    assert scope.is_ignored("backtest/results/scratch/summary_x.csv")
    assert scope.is_ignored("test-results/whatever.png")
    assert scope.is_ignored("playwright-report/index.html")


def test_committed_baseline_results_are_not_ignored() -> None:
    """커밋된 baseline 증거는 여전히 범위 판정 대상이다(격리 대상이 아니다)."""
    assert not scope.is_ignored("backtest/results/grid_results.csv")
    assert not scope.is_ignored("backtest/results/indicator_opt/adx_grid.csv")


def test_missing_manifest_fails_loudly_instead_of_passing() -> None:
    with pytest.raises(SystemExit) as excinfo:
        scope.manifest_for_epic("does-not-exist-99")

    assert "manifest" in str(excinfo.value)


def test_epic_manifest_path_follows_the_convention() -> None:
    assert scope.manifest_for_epic("4") == scope.MANIFEST_DIR / "epic-4.txt"


def test_every_committed_manifest_loads() -> None:
    manifests = sorted(scope.MANIFEST_DIR.glob("epic-*.txt"))

    assert manifests, "manifest 디렉터리가 비어 있다"
    for path in manifests:
        assert scope.load_manifest(path), path
