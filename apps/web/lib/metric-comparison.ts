import type { OutcomeMetricComparisonRpcRow, OutcomeStrategy } from "./dashboard-types";
import type { SourceFilter } from "./source-filter";
import { getStrategyLabel } from "./strategy-labels.ts";
export type { OutcomeMetricComparisonRpcRow } from "./dashboard-types";

export const METRIC_STRATEGY_OPTIONS = ["A", "B", "C", "D", "E", "F"] as const;
export type MetricStrategy = OutcomeStrategy | "";

const METRIC_ROW_KEYS = [
  "ci_lower",
  "ci_upper",
  "cutoff_bias_label",
  "cutoff_bias_profit_factor_delta",
  "cutoff_bias_sample_size",
  "cutoff_bias_timeout_rate",
  "delisted_count",
  "expected_in_ci",
  "expected_profit_factor",
  "expected_win_rate",
  "gross_loss",
  "gross_win",
  "losses",
  "open_count",
  "profit_factor",
  "profit_factor_threshold_breached",
  "profit_factor_threshold_ratio",
  "sample_gate_label",
  "sample_gate_min_required",
  "sample_gate_passed",
  "strategy",
  "suspended_count",
  "threshold_warning",
  "timeout_count",
  "total_settled",
  "win_rate",
  "win_rate_threshold_breached",
  "win_rate_threshold_pp",
  "wins",
].join("|");

const NUMBER_FIELDS = [
  "ci_lower",
  "ci_upper",
  "cutoff_bias_profit_factor_delta",
  "cutoff_bias_sample_size",
  "cutoff_bias_timeout_rate",
  "expected_profit_factor",
  "expected_win_rate",
  "gross_loss",
  "gross_win",
  "losses",
  "open_count",
  "profit_factor",
  "profit_factor_threshold_ratio",
  "sample_gate_min_required",
  "suspended_count",
  "timeout_count",
  "total_settled",
  "win_rate",
  "win_rate_threshold_pp",
  "wins",
] as const;

type QueryInput = URLSearchParams | Readonly<Record<string, string | string[] | undefined | null>>;

function readQueryValue(input: QueryInput, key: string): string | null {
  if (input instanceof URLSearchParams) return input.get(key);
  const value = input[key];
  return Array.isArray(value) ? value[0] ?? null : value ?? null;
}

function isOneOf<const T extends readonly string[]>(value: string | null, options: T): value is T[number] {
  return value !== null && (options as readonly string[]).includes(value);
}

function isNullableFiniteNumber(value: unknown): value is number | null {
  return value === null || (typeof value === "number" && Number.isFinite(value));
}

function isNonNegativeInteger(value: unknown): value is number {
  return typeof value === "number" && Number.isInteger(value) && value >= 0;
}

function isNullableNonNegativeNumber(value: unknown): value is number | null {
  return value === null || (typeof value === "number" && Number.isFinite(value) && value >= 0);
}

function isNullableProbability(value: unknown): value is number | null {
  return isNullableFiniteNumber(value) && (value === null || (value >= 0 && value <= 1));
}

export function normalizeMetricStrategy(input: QueryInput): MetricStrategy {
  const value = readQueryValue(input, "metric_strategy")?.trim() ?? "";
  const strategy = value || null;
  return isOneOf(strategy, METRIC_STRATEGY_OPTIONS) ? strategy : "";
}

export function toMetricComparisonRpcParams(strategy: MetricStrategy, source: SourceFilter = "") {
  return source
    ? { p_strategy: strategy || null, p_source: source }
    : { p_strategy: strategy || null };
}

export function isOutcomeMetricComparisonRpcRow(value: unknown): value is OutcomeMetricComparisonRpcRow {
  if (!value || typeof value !== "object") return false;
  const row = value as Record<string, unknown>;
  if (Object.keys(row).sort().join("|") !== METRIC_ROW_KEYS) return false;
  if (!(row.strategy === null || isOneOf(typeof row.strategy === "string" ? row.strategy : null, METRIC_STRATEGY_OPTIONS))) return false;
  const sampleGatePassed = row.sample_gate_passed;
  const expectedInCi = row.expected_in_ci;
  const winRateThresholdBreached = row.win_rate_threshold_breached;
  const profitFactorThresholdBreached = row.profit_factor_threshold_breached;
  const thresholdWarning = row.threshold_warning;
  const sampleGateLabel = row.sample_gate_label;
  const expectedWinRate = row.expected_win_rate;
  const expectedProfitFactor = row.expected_profit_factor;
  const ciLower = row.ci_lower;
  const ciUpper = row.ci_upper;
  const totalSettled = row.total_settled;
  const sampleGateMinRequired = row.sample_gate_min_required;
  if (typeof sampleGatePassed !== "boolean") return false;
  if (expectedInCi !== null && typeof expectedInCi !== "boolean") return false;
  if (winRateThresholdBreached !== null && typeof winRateThresholdBreached !== "boolean") return false;
  if (profitFactorThresholdBreached !== null && typeof profitFactorThresholdBreached !== "boolean") return false;
  if (thresholdWarning !== null && typeof thresholdWarning !== "boolean") return false;
  if (sampleGateLabel !== null && typeof sampleGateLabel !== "string") return false;
  if (row.cutoff_bias_label !== null && typeof row.cutoff_bias_label !== "string") return false;
  if (!NUMBER_FIELDS.every((field) => isNullableFiniteNumber(row[field]))) return false;
  if (!["losses", "open_count", "sample_gate_min_required", "suspended_count", "timeout_count", "total_settled", "wins"].every((field) => isNonNegativeInteger(row[field]))) return false;
  if (!["cutoff_bias_sample_size"].every((field) => row[field] === null || isNonNegativeInteger(row[field]))) return false;
  if (!["gross_win", "gross_loss", "profit_factor", "expected_profit_factor", "profit_factor_threshold_ratio", "win_rate_threshold_pp"].every((field) => isNullableNonNegativeNumber(row[field]))) return false;
  if (!["win_rate", "ci_lower", "ci_upper", "expected_win_rate", "cutoff_bias_timeout_rate"].every((field) => isNullableProbability(row[field]))) return false;
  if (!isNonNegativeInteger(totalSettled) || !isNonNegativeInteger(sampleGateMinRequired)) return false;
  if (!isNullableProbability(ciLower) || !isNullableProbability(ciUpper) || !isNullableProbability(expectedWinRate)) return false;
  if (ciLower !== null && ciUpper !== null && ciLower > ciUpper) return false;
  if (sampleGatePassed !== (totalSettled >= sampleGateMinRequired)) return false;
  if (sampleGatePassed && sampleGateLabel !== null) return false;
  if (!sampleGatePassed) {
    if (!sampleGateLabel?.trim()) return false;
    if (["win_rate", "profit_factor", "ci_lower", "ci_upper", "expected_win_rate", "expected_in_ci", "expected_profit_factor", "win_rate_threshold_pp", "profit_factor_threshold_ratio", "win_rate_threshold_breached", "profit_factor_threshold_breached", "threshold_warning"].some((field) => row[field] !== null)) return false;
  }
  if ((expectedWinRate === null) !== (expectedProfitFactor === null)) return false;
  if (expectedWinRate === null && expectedInCi !== null) return false;
  if (expectedWinRate !== null && expectedInCi === null) return false;
  const thresholdFlagsAreNull = winRateThresholdBreached === null && profitFactorThresholdBreached === null;
  if ((thresholdWarning === null) !== thresholdFlagsAreNull) return false;
  if (thresholdWarning === true && winRateThresholdBreached !== true && profitFactorThresholdBreached !== true) return false;
  if (thresholdWarning === false && (winRateThresholdBreached === true || profitFactorThresholdBreached === true)) return false;
  if (expectedWinRate === null && (
    !thresholdFlagsAreNull ||
    thresholdWarning !== null ||
    row.win_rate_threshold_pp !== null ||
    row.profit_factor_threshold_ratio !== null
  )) return false;
  if (expectedWinRate !== null) {
    if (winRateThresholdBreached === null && row.win_rate !== null) return false;
    if (profitFactorThresholdBreached === null && row.profit_factor !== null) return false;
  }
  return true;
}

export function isOutcomeMetricComparisonRpcResponse(value: unknown, selectedStrategy: MetricStrategy = ""): value is OutcomeMetricComparisonRpcRow[] {
  if (!Array.isArray(value) || value.length > METRIC_STRATEGY_OPTIONS.length + 1) return false;
  if (!value.every(isOutcomeMetricComparisonRpcRow)) return false;
  const keys = value.map((row) => row.strategy ?? "__rollup__");
  if (new Set(keys).size !== keys.length) return false;
  if (selectedStrategy) return value.length === 0 || (value.length === 1 && value[0].strategy === selectedStrategy);
  return value.length === 0 || keys.includes("__rollup__");
}

export function getMetricComparisonRow(
  rows: readonly OutcomeMetricComparisonRpcRow[],
  strategy: MetricStrategy,
): OutcomeMetricComparisonRpcRow | null {
  return rows.find((row) => row.strategy === (strategy || null)) ?? null;
}

export function getMetricStrategyLabel(strategy: MetricStrategy): string {
  return strategy ? getStrategyLabel(strategy) ?? `전략 ${strategy}` : "전체 전략";
}

export function formatMetricPercent(value: number | null): string {
  return value === null ? "-" : `${(value * 100).toFixed(2)}%`;
}

export function formatMetricProfitFactor(value: number | null): string {
  return value === null ? "-" : value.toFixed(2);
}

export function formatMetricCount(value: number): string {
  return `${value.toLocaleString("ko-KR")}건`;
}

export function getMetricSampleGateLabel(row: OutcomeMetricComparisonRpcRow): string | null {
  if (row.sample_gate_passed) return null;
  return row.sample_gate_label ?? `표본 부족 (${row.total_settled}/${row.sample_gate_min_required ?? 30})`;
}

export function getMetricExpectedVerdict(row: OutcomeMetricComparisonRpcRow): string {
  if (!row.sample_gate_passed) return "표본 게이트 미통과로 판정하지 않습니다.";
  if (row.expected_win_rate === null) return "기대치 없음 — 비교 기준을 정의하지 않았습니다.";
  if (row.expected_in_ci === true) return "백테스트 기대 승률이 95% CI 안에 있습니다.";
  if (row.expected_in_ci === false) return "백테스트 기대 승률이 95% CI 밖에 있습니다.";
  return "기대치 판정을 확인할 수 없습니다.";
}

export function getMetricTimeoutNotice(row: OutcomeMetricComparisonRpcRow): string | null {
  if (row.timeout_count <= 0) return null;
  if (row.cutoff_bias_label) return `TIMEOUT ${row.timeout_count}건 · N=30 예상 왜곡: ${row.cutoff_bias_label}`;
  return `TIMEOUT ${row.timeout_count}건 · N=30 기준 백테스트 기대치가 없어 예상 왜곡을 정량화하지 않습니다.`;
}

export function getMetricThresholdMessages(row: OutcomeMetricComparisonRpcRow): string[] {
  if (!row.sample_gate_passed || row.threshold_warning !== true) return [];
  const messages: string[] = [];
  if (row.win_rate_threshold_breached === true) messages.push("승률 기대치 대비 ±10%p 초과");
  if (row.profit_factor_threshold_breached === true) messages.push("PF 기대치 대비 ±25% 초과");
  return messages;
}
