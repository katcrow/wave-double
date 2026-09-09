"""백테스트 산출물 경로 해석 (epic-7-retro-item-30).

전략 실험 산출물이 `backtest/results/`에 바로 떨어지면, 탐색적 실행 한 번이 곧 dirty
worktree가 된다. Epic 7에서 그 산출물이 커밋 범위에 섞여 들어와 story-scoped
diff-check가 신뢰를 잃었다.

격리 규약:
- **커밋된 baseline 증거**는 지금 위치(`backtest/results/...`)에 그대로 둔다. 수용 증거이므로
  옮기거나 지우지 않는다.
- **탐색적 실행**은 산출물을 트리 밖(또는 gitignore된 `backtest/results/scratch/`)으로 보낸다.
  `WAVE_BACKTEST_RESULTS_DIR`로 루트를 바꾸면 모든 러너가 그 아래에 쓴다.

    # 트리를 더럽히지 않는 탐색적 실행
    WAVE_BACKTEST_RESULTS_DIR=backtest/results/scratch uv run python -m backtest.run ...
    # 또는 저장소 밖으로
    WAVE_BACKTEST_RESULTS_DIR=/tmp/wave-exp uv run python -m backtest.indicator_opt.run ...

기본값은 바뀌지 않으므로 기존 러너/문서/커밋된 baseline 경로는 그대로 동작한다.
"""

from __future__ import annotations

import os
from pathlib import Path

ENV_VAR = "WAVE_BACKTEST_RESULTS_DIR"
DEFAULT_ROOT = Path(__file__).resolve().parent / "results"
SCRATCH_DIRNAME = "scratch"


def results_root(env: dict[str, str] | None = None) -> Path:
    """산출물 루트. ``WAVE_BACKTEST_RESULTS_DIR``가 있으면 그 경로, 없으면 backtest/results."""
    source = os.environ if env is None else env
    override = (source.get(ENV_VAR) or "").strip()
    if not override:
        return DEFAULT_ROOT
    return Path(override).expanduser()


def scratch_root(env: dict[str, str] | None = None) -> Path:
    """gitignore된 탐색용 하위 경로. 오버라이드가 없을 때의 권장 목적지."""
    return results_root(env) / SCRATCH_DIRNAME
