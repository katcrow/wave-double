"""Epic 범위 안에 변경이 머무는지 검증한다(epic-7-retro-item-30에서 표준화).

Epic이 서로 겹쳐 진행되는(interleaved) 이 저장소에서는 "이 Epic이 무엇을 건드렸는가"를
커밋 그래프만으로 복원할 수 없다. 그래서 Epic마다 경로 manifest를 두고 그 범위를 게이트한다.

표준 사용법(item-30):

    # Epic 번호로 manifest를 규약대로 찾는다(tools/epic-path-manifests/epic-<N>.txt)
    python tools/check_epic_scope.py --epic 4 --range <base>..HEAD

    # 작업 트리(미커밋 + untracked)까지 포함해 clean-tree까지 함께 확인한다
    python tools/check_epic_scope.py --epic 4 --range <base> --worktree --clean-tree

`--clean-tree`는 manifest 밖의 변경이 하나라도 있으면 실패한다 -- Epic 산출물과 탐색적
실험 산출물이 섞인 커밋을 막는 것이 목적이다. 실험 산출물 격리 규약은
`backtest/results_dir.py`를 참고한다(그 scratch 경로는 아래 IGNORED_PREFIXES로 제외된다).
"""

from __future__ import annotations

import argparse
import json
import subprocess
import sys
from pathlib import Path

# 이 저장소의 경로에는 한국어 파일명이 있다. Windows 콘솔 기본 코드페이지(cp949)로
# 출력하면 JSON 자체가 깨져서 호출부가 파싱에 실패한다.
if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")


def changed_paths(repo: Path, revision_range: str, *, worktree: bool = False) -> list[str]:
    if worktree:
        result = subprocess.run(
            ["git", "-c", "core.quotePath=false", "-C", str(repo), "diff", "--name-only", "--no-renames", revision_range, "--"],
            check=True,
            capture_output=True,
            text=True,
            encoding="utf-8",
        )
        untracked = subprocess.run(
            ["git", "-c", "core.quotePath=false", "-C", str(repo), "ls-files", "--others", "--exclude-standard"],
            check=True,
            capture_output=True,
            text=True,
            encoding="utf-8",
        )
        return sorted({
            line.strip().replace("\\", "/")
            for output in (result.stdout, untracked.stdout)
            for line in output.splitlines()
            if line.strip()
        })
    left, separator, right = revision_range.partition("..")
    if separator != ".." or not left or not right or right.startswith("."):
        raise ValueError("range must look like REV..REV")
    result = subprocess.run(
        ["git", "-c", "core.quotePath=false", "-C", str(repo), "diff", "--name-only", "--no-renames", revision_range, "--"],
        check=True,
        capture_output=True,
        text=True,
        encoding="utf-8",
    )
    return sorted({line.strip().replace("\\", "/") for line in result.stdout.splitlines() if line.strip()})


# 어느 Epic에도 귀속되지 않는 경로. 실험/생성 산출물이라 범위 판정에서 제외한다.
# (gitignore로 이미 대부분 걸러지지만, --worktree는 ls-files --others로 훑으므로
#  gitignore가 늦게 추가된 경로가 남아 있을 수 있다.)
IGNORED_PREFIXES = (
    "backtest/results/scratch/",
    "test-results/",
    "playwright-report/",
    ".playwright-mcp/",
    "node_modules/",
)

MANIFEST_DIR = Path(__file__).resolve().parent / "epic-path-manifests"


def manifest_for_epic(epic: str) -> Path:
    """Epic 번호 -> manifest 경로(규약). 없으면 만들라고 명시적으로 실패한다."""
    path = MANIFEST_DIR / f"epic-{epic}.txt"
    if not path.exists():
        raise SystemExit(
            f"Epic {epic}의 경로 manifest가 없다: {path} — "
            "Epic 산출물 경로를 한 줄에 하나씩 적어 만든 뒤 다시 실행하세요."
        )
    return path


def is_ignored(path: str) -> bool:
    return any(path.startswith(prefix) for prefix in IGNORED_PREFIXES)


def load_manifest(path: Path) -> list[str]:
    entries = []
    for line in path.read_text(encoding="utf-8").splitlines():
        value = line.strip().replace("\\", "/")
        if not value or value.startswith("#"):
            continue
        entries.append(value)
    if not entries:
        raise ValueError("manifest has no path entries")
    return entries


def is_allowed(path: str, entries: list[str]) -> bool:
    return any(path == entry or (entry.endswith("/") and path.startswith(entry)) for entry in entries)


def main() -> int:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--range", required=True)
    target = parser.add_mutually_exclusive_group(required=True)
    target.add_argument("--manifest", type=Path, help="manifest 파일 경로를 직접 지정")
    target.add_argument("--epic", help="Epic 번호. tools/epic-path-manifests/epic-<N>.txt를 쓴다")
    parser.add_argument("--repo", default=".", type=Path)
    parser.add_argument(
        "--worktree",
        action="store_true",
        help="Compare one revision with the working tree and include untracked files.",
    )
    parser.add_argument(
        "--clean-tree",
        action="store_true",
        help="manifest 밖 변경이 하나라도 있으면 실패한다(Epic 산출물과 실험 산출물의 혼입 차단).",
    )
    args = parser.parse_args()

    manifest_path = args.manifest if args.manifest else manifest_for_epic(args.epic)
    entries = load_manifest(manifest_path)
    paths = changed_paths(args.repo, args.range, worktree=args.worktree)
    ignored = [path for path in paths if is_ignored(path)]
    considered = [path for path in paths if not is_ignored(path)]
    out_of_scope = [path for path in considered if not is_allowed(path, entries)]
    print(json.dumps({
        "range": args.range,
        "manifest": str(manifest_path),
        "epic": args.epic,
        "changed_paths": paths,
        "ignored_paths": ignored,
        "out_of_scope": out_of_scope,
        "clean_tree": args.clean_tree,
        "ok": not out_of_scope,
    }, ensure_ascii=False))
    if out_of_scope:
        if args.clean_tree:
            print(
                "clean-tree 게이트 실패: 위 out_of_scope 경로를 Epic manifest에 추가하거나, "
                "실험 산출물이면 WAVE_BACKTEST_RESULTS_DIR로 트리 밖에 쓰도록 바꾸세요."
            )
        return 1
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
