"""backtest/results_dir.py 계약 테스트(epic-7-retro-item-30).

전략 실험 산출물 격리는 "기본값을 바꾸지 않는다"가 핵심이다 -- 커밋된 baseline 경로가
움직이면 수용 증거가 끊긴다. 기본값 불변과 오버라이드 동작을 함께 고정한다.
"""

from __future__ import annotations

import importlib.util
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
_spec = importlib.util.spec_from_file_location(
    "backtest_results_dir", ROOT / "backtest" / "results_dir.py"
)
results_dir = importlib.util.module_from_spec(_spec)
_spec.loader.exec_module(results_dir)


def test_default_root_is_the_committed_results_directory() -> None:
    assert results_dir.results_root(env={}) == ROOT / "backtest" / "results"


def test_blank_override_falls_back_to_the_default() -> None:
    assert results_dir.results_root(env={results_dir.ENV_VAR: "   "}) == results_dir.DEFAULT_ROOT
    assert results_dir.results_root(env={results_dir.ENV_VAR: ""}) == results_dir.DEFAULT_ROOT


def test_override_redirects_the_root() -> None:
    root = results_dir.results_root(env={results_dir.ENV_VAR: "/tmp/wave-exp"})

    assert root == Path("/tmp/wave-exp")


def test_override_is_trimmed() -> None:
    assert results_dir.results_root(env={results_dir.ENV_VAR: "  /tmp/wave-exp  "}) == Path("/tmp/wave-exp")


def test_scratch_root_sits_under_the_resolved_root() -> None:
    assert results_dir.scratch_root(env={}) == results_dir.DEFAULT_ROOT / "scratch"
    assert results_dir.scratch_root(env={results_dir.ENV_VAR: "/tmp/x"}) == Path("/tmp/x/scratch")


def test_default_scratch_path_is_gitignored() -> None:
    """scratch가 gitignore에 없으면 격리 규약이 트리를 더럽히는 것을 못 막는다."""
    ignore = (ROOT / ".gitignore").read_text(encoding="utf-8")

    assert "backtest/results/scratch/" in ignore


def test_runners_resolve_their_results_dir_through_the_shared_resolver() -> None:
    """러너가 경로를 각자 하드코딩하면 오버라이드가 일부만 듣는다."""
    runners = [
        ROOT / "backtest" / "run.py",
        ROOT / "backtest" / "ensemble" / "grid_search.py",
        ROOT / "backtest" / "indicator_opt" / "run.py",
        ROOT / "backtest" / "indicator_opt" / "strategy_ma_derivative.py",
    ]

    for path in runners:
        text = path.read_text(encoding="utf-8")
        assert "results_root()" in text, path
        assert 'parent / "results"' not in text, path
        assert 'parent.parent / "results"' not in text, path
