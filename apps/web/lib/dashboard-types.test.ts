import assert from "node:assert/strict";
import { test } from "node:test";
import { isIntradaySnapshot } from "./dashboard-types.ts";
import type { CompleteSnapshot, DashboardSnapshot } from "./dashboard-types.ts";

function complete(overrides: Partial<CompleteSnapshot> = {}): CompleteSnapshot {
  return {
    logical_run_key: "2026-09-02:close",
    run_id: "11111111-1111-1111-1111-111111111111",
    trading_day: "2026-09-02",
    batch_kind: "close",
    published_at: new Date().toISOString(),
    sections: { candidates: { candidate_count: 12, truncated_count: 0, original_count: 12, excluded_count: 0 } },
    ...overrides,
  };
}

function snapshot(overrides: Partial<DashboardSnapshot> = {}): DashboardSnapshot {
  return {
    no_snapshot: true,
    result_code: "NO_SNAPSHOT",
    complete_snapshot: null,
    latest_attempt: null,
    latest_partial_run_id: null,
    available_partial_sections: [],
    missing_sections: ["candidates", "tags", "supply_3day", "market_supply", "outcome_tracking"],
    unprocessed_items: 0,
    ...overrides,
  };
}

// UJ-2: batch_kind='close'면 장중 라벨을 표시하지 않는다.
test("batch_kind='close': false", () => {
  const result = isIntradaySnapshot(snapshot({ complete_snapshot: complete({ batch_kind: "close" }) }));
  assert.equal(result, false);
});

// UJ-2: batch_kind='intraday'/'premarket'이면 장중 라벨을 표시한다.
test("batch_kind='intraday': true", () => {
  const result = isIntradaySnapshot(snapshot({ complete_snapshot: complete({ batch_kind: "intraday" }) }));
  assert.equal(result, true);
});

test("batch_kind='premarket': true", () => {
  const result = isIntradaySnapshot(snapshot({ complete_snapshot: complete({ batch_kind: "premarket" }) }));
  assert.equal(result, true);
});

// complete_snapshot이 없으면(스냅샷 없음/실패 등) 장중 라벨을 표시하지 않는다.
test("complete_snapshot=null: false", () => {
  const result = isIntradaySnapshot(snapshot({ complete_snapshot: null }));
  assert.equal(result, false);
});
