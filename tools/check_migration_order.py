"""저장소 migration의 timestamp 순서와 Epic 3 선행 계약을 검증한다."""

from __future__ import annotations

import re
from pathlib import Path


MIGRATION_NAME = re.compile(r"^(\d{12})_[a-z0-9_]+\.sql$")
REQUIRED_ORDER = (
    "202609021500_create_daily_ohlcv.sql",
    "202609031300_create_outcome_schema.sql",
    "202609031400_harden_outcome_schema_invariants.sql",
    "202609031500_create_emit_open_command.sql",
    "202609031600_link_publish_attempt_to_outcome.sql",
    "202609031700_record_close_batch_observations.sql",
    "202609031800_detect_price_adjustment_suspension.sql",
    "202609032000_judge_tp_sl_outcomes.sql",
    "202609032100_confirm_timeout_cutoff.sql",
    "202609032200_add_outcome_correction_mechanism.sql",
    "202609042200_enforce_delisted_termination.sql",
    "202609051200_create_rebuild_outcome_projection.sql",
    "202609051300_harden_price_adjustment_search_path.sql",
)


def main() -> int:
    root = Path(__file__).resolve().parents[1]
    migration_dir = root / "infra" / "supabase" / "migrations"
    files = sorted(migration_dir.glob("*.sql"))
    errors: list[str] = []
    timestamps: dict[str, Path] = {}

    for path in files:
        match = MIGRATION_NAME.match(path.name)
        if not match:
            errors.append(f"invalid migration filename: {path.name}")
            continue
        timestamp = match.group(1)
        previous = timestamps.get(timestamp)
        if previous:
            errors.append(f"duplicate migration timestamp: {previous.name}, {path.name}")
        timestamps[timestamp] = path

    positions = {path.name: index for index, path in enumerate(files)}
    missing = [name for name in REQUIRED_ORDER if name not in positions]
    if missing:
        errors.append(f"missing required migration(s): {', '.join(missing)}")
    else:
        order = [positions[name] for name in REQUIRED_ORDER]
        if order != sorted(order):
            errors.append("Epic 3 prerequisite migrations are not lexicographically ordered")

    if errors:
        for error in errors:
            print(f"ERROR: {error}")
        return 1

    print(f"migration order contract passed ({len(files)} files)")
    return 0


if __name__ == "__main__":
    raise SystemExit(main())
