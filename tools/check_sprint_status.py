"""sprint-status.yaml 계약 검증.

이 파일은 action item 원장이고 bmad 스킬(sprint-planning/retrospective/build sync)이 파싱한다.
그런데 손으로 편집하는 파일이라 조용히 깨지기 쉽다 -- 실제로 `ref` 값 끝에 잔여 쉼표가
남아 커밋된 상태로 **유효하지 않은 YAML**이었고(2026-09-09 발견), 그 사이 어떤 게이트도
알려주지 않았다. 흔한 파괴 패턴이 전부 인용 실수다: 큰따옴표 스칼라 안의 큰따옴표,
값 끝의 잔여 쉼표, 잘못된 이어쓰기 들여쓰기.

검사 항목:
1. YAML로 파싱된다.
2. 최상위 필수 키가 있다.
3. 모든 action item에 id/epic/action/owner/status가 있고 status가 허용 값이다.
4. done/in-progress 항목에는 근거(ref)가 있다 -- 근거 없는 done은 추적 가치가 없다.
5. id가 중복되지 않는다.

실행: `uv run --with pyyaml python tools/check_sprint_status.py`
"""

from __future__ import annotations

import sys
from pathlib import Path

if hasattr(sys.stdout, "reconfigure"):
    sys.stdout.reconfigure(encoding="utf-8", errors="replace")

ROOT = Path(__file__).resolve().parents[1]
STATUS_PATH = ROOT / "_bmad-output" / "implementation-artifacts" / "sprint-status.yaml"

REQUIRED_TOP_LEVEL = ("project", "development_status", "action_items")
ITEM_REQUIRED = ("id", "epic", "action", "owner", "status")
ALLOWED_STATUS = ("open", "in-progress", "done")
NEEDS_EVIDENCE = ("done", "in-progress")


def load(path: Path) -> dict:
    import yaml

    try:
        return yaml.safe_load(path.read_text(encoding="utf-8"))
    except yaml.YAMLError as error:
        raise SystemExit(
            f"ERROR: {path.name}이 유효한 YAML이 아니다.\n{error}\n\n"
            "흔한 원인: 큰따옴표 스칼라 안의 큰따옴표, 값 끝의 잔여 쉼표, 이어쓰기 줄의 들여쓰기."
        )


def check(data: dict) -> list[str]:
    errors: list[str] = []

    if not isinstance(data, dict):
        return ["최상위 구조가 매핑이 아니다"]

    for key in REQUIRED_TOP_LEVEL:
        if key not in data:
            errors.append(f"최상위 키 '{key}'가 없다")

    items = data.get("action_items")
    if items is None:
        return errors
    if not isinstance(items, list):
        return errors + ["action_items가 리스트가 아니다"]

    seen: dict[str, int] = {}
    for index, item in enumerate(items):
        where = f"action_items[{index}]"
        if not isinstance(item, dict):
            errors.append(f"{where}가 매핑이 아니다")
            continue

        for key in ITEM_REQUIRED:
            if key not in item or item[key] in (None, ""):
                errors.append(f"{where}에 '{key}'가 없다")

        item_id = item.get("id")
        if isinstance(item_id, str):
            if item_id in seen:
                errors.append(f"{where}의 id가 action_items[{seen[item_id]}]와 중복된다: {item_id}")
            else:
                seen[item_id] = index

        status = item.get("status")
        if status not in ALLOWED_STATUS:
            errors.append(f"{where} status가 허용 값이 아니다: {status!r} (허용: {ALLOWED_STATUS})")
        elif status in NEEDS_EVIDENCE:
            ref = item.get("ref")
            if not isinstance(ref, str) or not ref.strip():
                errors.append(f"{where}({item_id})가 {status}인데 근거(ref)가 없다")

    return errors


def main() -> int:
    if not STATUS_PATH.exists():
        print(f"ERROR: sprint status 파일 없음: {STATUS_PATH}")
        return 1

    data = load(STATUS_PATH)
    errors = check(data)
    for error in errors:
        print(f"ERROR: {error}")
    if errors:
        print(f"결과: {len(errors)} ERROR")
        return 1

    items = data["action_items"]
    counts = {status: sum(1 for i in items if i["status"] == status) for status in ALLOWED_STATUS}
    print(
        f"sprint-status 계약 통과 (action item {len(items)}건: "
        + ", ".join(f"{status} {count}" for status, count in counts.items())
        + ")"
    )
    return 0


if __name__ == "__main__":
    sys.exit(main())
