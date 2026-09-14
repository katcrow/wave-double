import assert from "node:assert/strict";
import { test } from "node:test";
import {
  formatBiasCount,
  getKstToday,
  isIsoDate,
  isBiasDiagnosticRpcResponse,
  normalizeBiasDate,
  toBiasDiagnosticRpcParams,
  type BiasDiagnosticRpcRow,
} from "./bias-diagnostic.ts";

function row(overrides: Partial<BiasDiagnosticRpcRow> = {}): BiasDiagnosticRpcRow {
  return {
    trading_day: "2026-09-09",
    has_data: true,
    candidate_population_signal_count: 12,
    backtest_universe_signal_count: 18,
    intersection_count: 7,
    missed_opportunity_count: 14,
    ...overrides,
  };
}

test("bias RPC row guard는 네 count와 미수집 nullable shape를 구분한다", () => {
  assert.equal(isBiasDiagnosticRpcResponse(row(), "2026-09-09"), true);
  assert.equal(isBiasDiagnosticRpcResponse(row({ candidate_population_signal_count: null }), "2026-09-09"), false);
  assert.equal(isBiasDiagnosticRpcResponse(row({
    has_data: false,
    candidate_population_signal_count: null,
    backtest_universe_signal_count: null,
    intersection_count: null,
    missed_opportunity_count: null,
  }), "2026-09-09"), true);
  assert.equal(isBiasDiagnosticRpcResponse(row({ has_data: false }), "2026-09-09"), false);
  assert.equal(isBiasDiagnosticRpcResponse(row({ candidate_population_signal_count: 1.5 }), "2026-09-09"), false);
  assert.equal(isBiasDiagnosticRpcResponse(row({ missed_opportunity_count: -1 }), "2026-09-09"), false);
  assert.equal(isBiasDiagnosticRpcResponse(row({ trading_day: "2026-02-30" }), "2026-09-09"), false);
  assert.equal(isBiasDiagnosticRpcResponse({ ...row(), extra: 1 }, "2026-09-09"), false);
  assert.equal(isBiasDiagnosticRpcResponse(row(), "2026-09-10"), false);
  assert.equal(isBiasDiagnosticRpcResponse([row()]), false);
});

test("bias_date query는 유효한 날짜만 통과하고 잘못된 값은 KST 오늘로 정규화한다", () => {
  const now = new Date("2026-09-13T15:30:00.000Z");
  assert.equal(getKstToday(now), "2026-09-14");
  assert.equal(normalizeBiasDate({ bias_date: "2026-09-12" }, now), "2026-09-12");
  assert.equal(normalizeBiasDate({ bias_date: "2026-02-30" }, now), "2026-09-14");
  assert.equal(normalizeBiasDate({ bias_date: "<script>" }, now), "2026-09-14");
  assert.equal(normalizeBiasDate({ bias_date: ["2026-09-11", "2026-09-12"] }, now), "2026-09-11");
  assert.deepEqual(toBiasDiagnosticRpcParams("2026-09-12"), { p_trading_day: "2026-09-12" });
});

test("연도 0001-0099도 ISO 날짜의 윤년·월말을 정확히 검증한다", () => {
  assert.equal(isIsoDate("0001-01-01"), true);
  assert.equal(isIsoDate("0099-12-31"), true);
  assert.equal(isIsoDate("0099-02-28"), true);
  assert.equal(isIsoDate("0099-02-29"), false);
  assert.equal(isIsoDate("0004-02-29"), true);
});

test("bias count format은 숫자와 미수집 null을 명시적으로 표현한다", () => {
  assert.equal(formatBiasCount(12345), "12,345");
  assert.equal(formatBiasCount(0), "0");
  assert.equal(formatBiasCount(null), "-");
});
