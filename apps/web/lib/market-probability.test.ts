import assert from "node:assert/strict";
import { test } from "node:test";
import { deriveMarketProbabilityChipState } from "./market-probability.ts";
import type { MarketIndexProbabilityRpcRow } from "./dashboard-types.ts";

const TODAY = "2026-10-21";

function row(overrides: Partial<MarketIndexProbabilityRpcRow> = {}): MarketIndexProbabilityRpcRow {
  return {
    trading_day: TODAY,
    target_trading_day: "2026-10-22",
    kospi_probability: 0.6234,
    kosdaq_probability: 0.4,
    last_success_at: "2026-10-21T06:20:00Z",
    feature_as_of: "2026-10-21T06:15:00Z",
    model_version: "v1",
    validation_status: "experimental",
    ...overrides,
  };
}

test("정상: 오늘 행이면 ready, stale 아님, 소수 1자리 퍼센트", () => {
  const state = deriveMarketProbabilityChipState(row(), false, TODAY);
  assert.equal(state.status, "ready");
  if (state.status !== "ready") return;
  assert.equal(state.stale, false);
  assert.equal(state.kospiPercent, "62.3%");
  assert.equal(state.kosdaqPercent, "40.0%");
});

test("직전값: trading_day가 오늘과 다르면 stale", () => {
  const state = deriveMarketProbabilityChipState(row({ trading_day: "2026-10-20" }), false, TODAY);
  assert.equal(state.status, "ready");
  if (state.status !== "ready") return;
  assert.equal(state.stale, true);
});

test("값 없음: row null이고 실패 아니면 empty", () => {
  assert.deepEqual(deriveMarketProbabilityChipState(null, false, TODAY), { status: "empty" });
});

test("조회 실패: fetchFailed면 row가 있어도 failed", () => {
  assert.deepEqual(deriveMarketProbabilityChipState(null, true, TODAY), { status: "failed" });
  assert.deepEqual(deriveMarketProbabilityChipState(row(), true, TODAY), { status: "failed" });
});
