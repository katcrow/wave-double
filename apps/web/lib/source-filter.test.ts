import assert from "node:assert/strict";
import { test } from "node:test";
import {
  getSourceLabel,
  getSourceScopeDescription,
  normalizeSource,
  SOURCE_QUERY_KEY,
  SOURCE_OPTIONS,
} from "./source-filter.ts";
import { toBiasDiagnosticRpcParams } from "./bias-diagnostic.ts";
import { toMetricComparisonRpcParams } from "./metric-comparison.ts";

test("source query는 허용된 세 원천만 통과시키고 나머지는 전체로 정규화한다", () => {
  assert.deepEqual(SOURCE_OPTIONS, ["t1859", "t1852", "t1856"]);
  assert.equal(normalizeSource({ source: "t1852" }), "t1852");
  assert.equal(normalizeSource(new URLSearchParams("source=t1856")), "t1856");
  assert.equal(normalizeSource({ source: " t1859 " }), "t1859");
  assert.equal(normalizeSource({ source: "unknown" }), "");
  assert.equal(normalizeSource({ source: ["t1852", "t1859"] }), "t1852");
  assert.equal(normalizeSource({}), "");
});

test("source label과 read model RPC 인자는 전체/선택 범위를 구분한다", () => {
  assert.equal(SOURCE_QUERY_KEY, "source");
  assert.equal(getSourceLabel(""), "전체 원천 통합");
  assert.equal(getSourceLabel("t1852"), "t1852 폴백 원천");
  assert.match(getSourceScopeDescription(""), /혼합된 지표/);
  assert.match(getSourceScopeDescription("t1859"), /원천별 결과/);
  assert.doesNotMatch(getSourceScopeDescription("t1859"), /primary source/);
  assert.deepEqual(toMetricComparisonRpcParams("B", "t1852"), { p_strategy: "B", p_source: "t1852" });
  assert.deepEqual(toBiasDiagnosticRpcParams("2026-09-14", "t1856"), { p_trading_day: "2026-09-14", p_source: "t1856" });
  assert.deepEqual(toMetricComparisonRpcParams(""), { p_strategy: null });
  assert.deepEqual(toBiasDiagnosticRpcParams("2026-09-14"), { p_trading_day: "2026-09-14" });
});
