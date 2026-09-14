import type { BiasDiagnosticRpcRow } from "./dashboard-types";

export type { BiasDiagnosticRpcRow } from "./dashboard-types";

export const BIAS_DATE_QUERY_KEY = "bias_date";

type QueryInput = URLSearchParams | Readonly<Record<string, string | string[] | undefined | null>>;

const BIAS_ROW_KEYS = [
  "backtest_universe_signal_count",
  "candidate_population_signal_count",
  "has_data",
  "intersection_count",
  "missed_opportunity_count",
  "trading_day",
];

const BIAS_COUNT_FIELDS = [
  "candidate_population_signal_count",
  "backtest_universe_signal_count",
  "intersection_count",
  "missed_opportunity_count",
] as const;

function readQueryValue(input: QueryInput, key: string): string | null {
  if (input instanceof URLSearchParams) return input.get(key);
  const value = input[key];
  return Array.isArray(value) ? value[0] ?? null : value ?? null;
}

export function isIsoDate(value: unknown): value is string {
  if (typeof value !== "string" || !/^\d{4}-\d{2}-\d{2}$/.test(value)) return false;
  const [year, month, day] = value.split("-").map(Number);
  const date = new Date(Date.UTC(year, month - 1, day));
  return date.getUTCFullYear() === year && date.getUTCMonth() === month - 1 && date.getUTCDate() === day;
}

export function getKstToday(now = new Date()): string {
  const parts = new Intl.DateTimeFormat("en-US", {
    timeZone: "Asia/Seoul",
    year: "numeric",
    month: "2-digit",
    day: "2-digit",
  }).formatToParts(now);
  const values = Object.fromEntries(parts.map(({ type, value }) => [type, value]));
  return `${values.year}-${values.month}-${values.day}`;
}

export function normalizeBiasDate(input: QueryInput, now = new Date()): string {
  const value = readQueryValue(input, BIAS_DATE_QUERY_KEY)?.trim() ?? "";
  return isIsoDate(value) ? value : getKstToday(now);
}

export function toBiasDiagnosticRpcParams(tradingDay: string) {
  return { p_trading_day: tradingDay };
}

function isNonNegativeInteger(value: unknown): value is number {
  return typeof value === "number" && Number.isInteger(value) && value >= 0;
}

export function isBiasDiagnosticRpcRow(value: unknown, expectedDate?: string): value is BiasDiagnosticRpcRow {
  if (!value || typeof value !== "object") return false;
  const row = value as Record<string, unknown>;
  if (Object.keys(row).sort().join("|") !== BIAS_ROW_KEYS.join("|")) return false;
  if (!isIsoDate(row.trading_day) || (expectedDate !== undefined && row.trading_day !== expectedDate)) return false;
  if (typeof row.has_data !== "boolean") return false;
  if (!BIAS_COUNT_FIELDS.every((field) => row[field] === null || isNonNegativeInteger(row[field]))) return false;
  return row.has_data
    ? BIAS_COUNT_FIELDS.every((field) => isNonNegativeInteger(row[field]))
    : BIAS_COUNT_FIELDS.every((field) => row[field] === null);
}

export function isBiasDiagnosticRpcResponse(value: unknown, expectedDate?: string): value is BiasDiagnosticRpcRow {
  return isBiasDiagnosticRpcRow(value, expectedDate);
}

export function formatBiasCount(value: number | null): string {
  return value === null ? "-" : value.toLocaleString("ko-KR");
}
