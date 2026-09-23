import assert from "node:assert/strict";
import { test } from "node:test";
import {
  formatOutcomeDate,
  formatOutcomeReturnPct,
  getOutcomeStatusMeta,
  getOutcomeSummary,
  isOutcomeTrackingRpcResponse,
  normalizeOutcomeFilters,
  toOutcomeTrackingRpcParams,
  type OutcomeTrackingRpcRow,
} from "./outcome-tracking.ts";

function row(overrides: Partial<OutcomeTrackingRpcRow> = {}): OutcomeTrackingRpcRow {
  return {
    outcome_id: "11111111-1111-1111-1111-111111111111",
    name: "삼성전자",
    ticker: "005930",
    strategy: "A",
    entry_date: "2026-09-09",
    status: "TP",
    exit_date: "2026-09-12",
    return_pct: 2.9,
    ...overrides,
  };
}

test("RPC row shape는 6개 상태, 전략, nullable 필드와 유한 손익률을 검증한다", () => {
  assert.equal(isOutcomeTrackingRpcResponse([row()]), true);
  assert.equal(isOutcomeTrackingRpcResponse([row({ status: "DELISTED", exit_date: null, return_pct: null })]), true);
  assert.equal(isOutcomeTrackingRpcResponse([row({ name: null })]), true);
  assert.equal(isOutcomeTrackingRpcResponse([{ ...row(), name: "" }]), false);
  assert.equal(isOutcomeTrackingRpcResponse([{ ...row(), status: "UNKNOWN" }]), false);
  assert.equal(isOutcomeTrackingRpcResponse([{ ...row(), strategy: "I" }]), false);
  assert.equal(isOutcomeTrackingRpcResponse([{ ...row(), entry_date: "not-a-date" }]), false);
  assert.equal(isOutcomeTrackingRpcResponse([{ ...row(), exit_date: "2026-02-30" }]), false);
  assert.equal(isOutcomeTrackingRpcResponse([{ ...row(), return_pct: Number.NaN }]), false);
  assert.equal(isOutcomeTrackingRpcResponse({ rows: [row()] }), false);
});

test("허용되지 않은 query 필터는 전체 조회로 안전하게 정규화한다", () => {
  assert.deepEqual(
    normalizeOutcomeFilters({ status: "OPEN", strategy: "F", ticker: " 005930 " }),
    { status: "OPEN", strategy: "F", ticker: "005930" },
  );
  assert.deepEqual(
    normalizeOutcomeFilters({ status: "INVALID", strategy: "I", ticker: "<script>" }),
    { status: "", strategy: "", ticker: "" },
  );
  assert.deepEqual(
    toOutcomeTrackingRpcParams({ status: "", strategy: "", ticker: "" }),
    { p_status: undefined, p_strategy: undefined, p_ticker: undefined, p_limit: 500 },
  );
});

test("상태 설명, 날짜/손익률 표시, OPEN 별도 집계를 보존한다", () => {
  assert.equal(getOutcomeStatusMeta("TIMEOUT").description, "정해진 보유 기간이 지나 종결되었습니다.");
  assert.equal(formatOutcomeDate("2026-09-09"), "2026.09.09");
  assert.equal(formatOutcomeDate(null), "-");
  assert.equal(formatOutcomeReturnPct(2.9, "TP"), "+2.90%");
  assert.equal(formatOutcomeReturnPct(-3, "SL"), "-3.00%");
  assert.equal(formatOutcomeReturnPct(null, "OPEN"), "미확정");
  assert.equal(formatOutcomeReturnPct(null, "DELISTED"), "미확정");
  assert.equal(formatOutcomeReturnPct(null, "TP"), "-");

  const summary = getOutcomeSummary([
    row({ status: "TP" }),
    row({ status: "SL" }),
    row({ status: "TIMEOUT" }),
    row({ status: "OPEN" }),
    row({ status: "SUSPENDED" }),
    row({ status: "DELISTED" }),
  ]);
  assert.deepEqual(summary, { settledCount: 3, openCount: 1, suspendedCount: 1, delistedCount: 1 });
});
