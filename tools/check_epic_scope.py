"""Verify that a revision range stays inside an Epic path manifest."""

from __future__ import annotations

import argparse
import json
import subprocess
from pathlib import Path


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
    parser = argparse.ArgumentParser()
    parser.add_argument("--range", required=True)
    parser.add_argument("--manifest", required=True, type=Path)
    parser.add_argument("--repo", default=".", type=Path)
    parser.add_argument(
        "--worktree",
        action="store_true",
        help="Compare one revision with the working tree and include untracked files.",
    )
    args = parser.parse_args()

    entries = load_manifest(args.manifest)
    paths = changed_paths(args.repo, args.range, worktree=args.worktree)
    out_of_scope = [path for path in paths if not is_allowed(path, entries)]
    print(json.dumps({
        "range": args.range,
        "manifest": str(args.manifest),
        "changed_paths": paths,
        "out_of_scope": out_of_scope,
        "ok": not out_of_scope,
    }, ensure_ascii=False))
    return 1 if out_of_scope else 0


if __name__ == "__main__":
    raise SystemExit(main())
