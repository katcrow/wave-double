"""Generated read-model type drift lint (offline, no Supabase access needed).

Migration 파일의 create table 이름을 packages/read-model/src/database.types.ts에 있는
table 이름과 대조해, 새 migration이 테이블을 추가했는데 committed 타입이 재생성되지 않은
drift를 PR CI에서 차단한다. 프로덕션 접근 없이 실행할 수 있는 offline 계약으로,
online 재생성(npm run generate:read-model-types)과 함께 사용한다.
"""

from __future__ import annotations

import re
from pathlib import Path

TABLE_CREATE = re.compile(
    r"create\s+table\s+(?:if\s+not\s+exists\s+)?(?:public\.)?([a-z0-9_]+)",
    re.IGNORECASE,
)
VIEW_CREATE = re.compile(
    r"create\s+(?:or\s+replace\s+)?view\s+(?:public\.)?([a-z0-9_]+)",
    re.IGNORECASE,
)


def main() -> int:
    root = Path(__file__).resolve().parents[1]
    migration_dir = root / "infra" / "supabase" / "migrations"
    types_path = root / "packages" / "read-model" / "src" / "database.types.ts"

    if not types_path.exists():
        print(f"ERROR: committed read-model types not found: {types_path}")
        return 1

    types_text = types_path.read_text(encoding="utf-8")
    errors: list[str] = []

    db_objects: set[str] = set()
    for path in sorted(migration_dir.glob("*.sql")):
        text = path.read_text(encoding="utf-8")
        db_objects.update(TABLE_CREATE.findall(text))
        db_objects.update(VIEW_CREATE.findall(text))

    for name in sorted(db_objects):
        if not name.startswith("_") and name not in ("schema_migrations",):
            if re.search(rf"\b{name}\s*:", types_text) is None:
                errors.append(f"table/view '{name}' in migrations is missing from generated types")

    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        print("해결: 프로덕션 접근 가능 환경에서 `npm run generate:read-model-types` 실행 후 커밋")
        return 1

    print(f"generated read-model types cover {len(db_objects)} migration-declared table/view objects")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())