import assert from "node:assert/strict";
import { test } from "node:test";
import {
  formatMetricPercent,
  formatMetricProfitFactor,
  getMetricComparisonRow,
  getMetricExpectedVerdict,
  getMetricSampleGateLabel,
  getMetricThresholdMessages,
  getMetricTimeoutNotice,
  isOutcomeMetricComparisonRpcResponse,
  normalizeMetricStrategy,
  toMetricComparisonRpcParams,
  type OutcomeMetricComparisonRpcRow,
} from "./metric-comparison.ts";

function row(overrides: Partial<OutcomeMetricComparisonRpcRow> = {}): OutcomeMetricComparisonRpcRow {
  return {
    strategy: "A",
    total_settled: 40,
    wins: 28,
    losses: 12,
    open_count: 2,
    suspended_count: 0,
    delisted_count: 0,
    gross_win: 56,
    gross_loss: 12,
    win_rate: 0.7,
    profit_factor: 4.6667,
    sample_gate_min_required: 30,
    sample_gate_passed: true,
    sample_gate_label: null,
    ci_lower: 0.54,
    ci_upper: 0.82,
    expected_win_rate: 0.6871,
    expected_in_ci: true,
    expected_profit_factor: 2.054,
    win_rate_threshold_pp: 0.1,
    profit_factor_threshold_ratio: 0.25,
    win_rate_threshold_breached: false,
    profit_factor_threshold_breached: true,
    threshold_warning: true,
    timeout_count: 1,
    cutoff_bias_sample_size: 30,
    cutoff_bias_timeout_rate: 0,
    cutoff_bias_profit_factor_delta: 0,
    cutoff_bias_label: "TIMEOUT 0% / PF차 ±0",
    ...overrides,
  };
}

test("metric RPC row shape는 정확한 key, nullable 수치, 전략 중복을 검증한다", () => {
  assert.equal(isOutcomeMetricComparisonRpcResponse([row(), row({
    strategy: null,
    expected_win_rate: null,
    expected_in_ci: null,
    expected_profit_factor: null,
    win_rate_threshold_pp: null,
    profit_factor_threshold_ratio: null,
    win_rate_threshold_breached: null,
    profit_factor_threshold_breached: null,
    threshold_warning: null,
  })]), true);
  assert.equal(isOutcomeMetricComparisonRpcResponse([row({ sample_gate_passed: false, sample_gate_label: "표본 부족 (29/30)", total_settled: 29, win_rate: null, profit_factor: null, ci_lower: null, ci_upper: null, expected_win_rate: null, expected_in_ci: null, expected_profit_factor: null, win_rate_threshold_pp: null, profit_factor_threshold_ratio: null, win_rate_threshold_breached: null, profit_factor_threshold_breached: null, threshold_warning: null })], "A"), true);
  assert.equal(isOutcomeMetricComparisonRpcResponse([row(), row()]), false);
  assert.equal(isOutcomeMetricComparisonRpcResponse([row()], ""), false);
  assert.equal(isOutcomeMetricComparisonRpcResponse([row({ strategy: "D" })], "D"), true);
  assert.equal(isOutcomeMetricComparisonRpcResponse([row({ strategy: "A" })], "D"), false);
  assert.equal(isOutcomeMetricComparisonRpcResponse([{ ...row(), strategy: "I" }]), false);
  assert.equal(isOutcomeMetricComparisonRpcResponse([{ ...row(), wins: -1 }]), false);
  assert.equal(isOutcomeMetricComparisonRpcResponse([{ ...row(), ci_lower: Number.NaN }]), false);
  assert.equal(isOutcomeMetricComparisonRpcResponse({ rows: [row()] }), false);
});

test("metric RPC row guard는 게이트·범위·기대치·threshold/cutoff 불변식을 검증한다", () => {
  const belowGate = row({
    strategy: "C",
    total_settled: 29,
    sample_gate_passed: false,
    sample_gate_label: "표본 부족 (29/30)",
    win_rate: null,
    profit_factor: null,
    ci_lower: null,
    ci_upper: null,
    expected_win_rate: null,
    expected_in_ci: null,
    expected_profit_factor: null,
    win_rate_threshold_pp: null,
    profit_factor_threshold_ratio: null,
    win_rate_threshold_breached: null,
    profit_factor_threshold_breached: null,
    threshold_warning: null,
  });
  assert.equal(isOutcomeMetricComparisonRpcResponse([belowGate], "C"), true);
  assert.equal(isOutcomeMetricComparisonRpcResponse([{ ...belowGate, total_settled: 30 }], "C"), false);
  assert.equal(isOutcomeMetricComparisonRpcResponse([{ ...belowGate, sample_gate_label: "  " }], "C"), false);
  assert.equal(isOutcomeMetricComparisonRpcResponse([{ ...row(), expected_profit_factor: null }]), false);
  assert.equal(isOutcomeMetricComparisonRpcResponse([{ ...row(), win_rate: 1.01 }]), false);
  assert.equal(isOutcomeMetricComparisonRpcResponse([{ ...row(), ci_lower: 0.8, ci_upper: 0.7 }]), false);
  assert.equal(isOutcomeMetricComparisonRpcResponse([{ ...row(), cutoff_bias_sample_size: 30.5 }]), false);
  assert.equal(isOutcomeMetricComparisonRpcResponse([{ ...row(), win_rate_threshold_breached: null }]), false);
  assert.equal(isOutcomeMetricComparisonRpcResponse([{ ...row(), threshold_warning: false }]), false);
  assert.equal(isOutcomeMetricComparisonRpcResponse([{ ...row(), threshold_warning: true, win_rate_threshold_breached: false, profit_factor_threshold_breached: false }]), false);
  assert.equal(isOutcomeMetricComparisonRpcResponse([row({ profit_factor: null, gross_loss: null, profit_factor_threshold_breached: null, win_rate_threshold_breached: true, threshold_warning: true })], "A"), true);
  assert.equal(isOutcomeMetricComparisonRpcResponse([row({ strategy: "A" })]), false);
});

test("metric 범위 query와 RPC 인자는 허용 전략만 유지한다", () => {
  assert.equal(normalizeMetricStrategy({ metric_strategy: " D " }), "D");
  assert.equal(normalizeMetricStrategy({ metric_strategy: "I" }), "");
  assert.equal(normalizeMetricStrategy(new URLSearchParams("metric_strategy=C")), "C");
  assert.deepEqual(toMetricComparisonRpcParams(""), { p_strategy: undefined });
  assert.deepEqual(toMetricComparisonRpcParams("F"), { p_strategy: "F" });
  assert.deepEqual(toMetricComparisonRpcParams("B", "t1852"), { p_strategy: "B", p_source: "t1852" });
  assert.equal(getMetricComparisonRow([row({ strategy: null }), row({ strategy: "D" })], "" )?.strategy, null);
  assert.equal(getMetricComparisonRow([row({ strategy: "D" })], "D")?.strategy, "D");
});

test("게이트, CI/threshold, TIMEOUT 고지는 canonical 값을 표시용 문장으로만 변환한다", () => {
  const gated = row();
  assert.equal(getMetricSampleGateLabel(gated), null);
  assert.equal(getMetricExpectedVerdict(gated), "백테스트 기대 승률이 95% CI 안에 있습니다.");
  assert.deepEqual(getMetricThresholdMessages(gated), ["PF 기대치 대비 ±25% 초과"]);
  assert.equal(getMetricTimeoutNotice(gated), "TIMEOUT 1건 · N=30 예상 왜곡: TIMEOUT 0% / PF차 ±0");

  const belowGate = row({ strategy: "C", total_settled: 29, sample_gate_passed: false, sample_gate_label: "표본 부족 (29/30)", win_rate: null, profit_factor: null, ci_lower: null, ci_upper: null, expected_win_rate: null, expected_in_ci: null, expected_profit_factor: null, win_rate_threshold_pp: null, profit_factor_threshold_ratio: null, win_rate_threshold_breached: null, profit_factor_threshold_breached: null, threshold_warning: null });
  assert.equal(getMetricSampleGateLabel(belowGate), "표본 부족 (29/30)");
  assert.equal(getMetricExpectedVerdict(belowGate), "표본 게이트 미통과로 판정하지 않습니다.");
  assert.deepEqual(getMetricThresholdMessages(belowGate), []);

  const noExpectation = row({ strategy: "F", expected_win_rate: null, expected_in_ci: null, expected_profit_factor: null, cutoff_bias_label: null });
  assert.equal(getMetricExpectedVerdict(noExpectation), "기대치 없음 — 비교 기준을 정의하지 않았습니다.");
  assert.equal(getMetricTimeoutNotice(noExpectation), "TIMEOUT 1건 · N=30 기준 백테스트 기대치가 없어 예상 왜곡을 정량화하지 않습니다.");
  assert.equal(formatMetricPercent(0.6871), "68.71%");
  assert.equal(formatMetricProfitFactor(2.054), "2.05");
});
