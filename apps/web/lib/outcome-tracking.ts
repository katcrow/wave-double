import { getStrategyLabel } from "./strategy-labels.ts";
import type { OutcomeStatus, OutcomeStrategy, OutcomeTrackingRpcRow } from "./dashboard-types";
import { toneFromSign, type ValueTone } from "./value-tone.ts";
export type { OutcomeStatus, OutcomeStrategy, OutcomeTrackingRpcRow } from "./dashboard-types";

export const OUTCOME_STATUS_OPTIONS = [
  "TP",
  "SL",
  "TIMEOUT",
  "OPEN",
  "SUSPENDED",
  "DELISTED",
] as const;

export const OUTCOME_STRATEGY_OPTIONS = ["A", "B", "C", "D", "E", "F", "G", "H"] as const;

export interface OutcomeTrackingFilters {
  status: OutcomeStatus | "";
  strategy: OutcomeStrategy | "";
  ticker: string;
}

export interface OutcomeStatusMeta {
  label: OutcomeStatus;
  description: string;
}

const OUTCOME_STATUS_META: Record<OutcomeStatus, OutcomeStatusMeta> = {
  TP: { label: "TP", description: "목표 수익률에 도달해 종결되었습니다." },
  SL: { label: "SL", description: "손절 기준에 도달해 종결되었습니다." },
  TIMEOUT: { label: "TIMEOUT", description: "정해진 보유 기간이 지나 종결되었습니다." },
  OPEN: { label: "OPEN", description: "아직 종결되지 않은 진행 중 outcome입니다." },
  SUSPENDED: { label: "SUSPENDED", description: "가격 조정 이상으로 판정을 보류했습니다." },
  DELISTED: { label: "DELISTED", description: "상장폐지로 추적을 종료했습니다." },
};

type QueryInput = URLSearchParams | Readonly<Record<string, string | string[] | undefined | null>>;

function readQueryValue(input: QueryInput, key: string): string | null {
  if (input instanceof URLSearchParams) return input.get(key);
  const value = input[key];
  return Array.isArray(value) ? value[0] ?? null : value ?? null;
}

function isOneOf<const T extends readonly string[]>(value: string | null, options: T): value is T[number] {
  return value !== null && (options as readonly string[]).includes(value);
}

function isIsoDate(value: unknown): value is string {
  if (typeof value !== "string" || !/^\d{4}-\d{2}-\d{2}$/.test(value)) return false;
  const [year, month, day] = value.split("-").map(Number);
  const date = new Date(Date.UTC(year, month - 1, day));
  return date.getUTCFullYear() === year && date.getUTCMonth() === month - 1 && date.getUTCDate() === day;
}

function normalizeTicker(value: string | null): string {
  const trimmed = value?.trim() ?? "";
  // 화면에 그대로 되돌려 표시할 수 있는 검색어만 허용한다. 제어문자/마크업/URL
  // 구분자는 RPC에 전달하지 않고, 잘못된 값은 전체 조회로 안전하게 정규화한다.
  if (!trimmed || trimmed.length > 40 || !/^[\p{L}\p{N} ._-]+$/u.test(trimmed)) return "";
  return trimmed;
}

export function normalizeOutcomeFilters(input: QueryInput): OutcomeTrackingFilters {
  const rawStatus = readQueryValue(input, "status");
  const rawStrategy = readQueryValue(input, "strategy");
  return {
    status: isOneOf(rawStatus, OUTCOME_STATUS_OPTIONS) ? rawStatus : "",
    strategy: isOneOf(rawStrategy, OUTCOME_STRATEGY_OPTIONS) ? rawStrategy : "",
    ticker: normalizeTicker(readQueryValue(input, "ticker")),
  };
}

export function toOutcomeTrackingRpcParams(filters: OutcomeTrackingFilters) {
  return {
    p_status: filters.status || undefined,
    p_strategy: filters.strategy || undefined,
    p_ticker: filters.ticker || undefined,
    p_limit: 500,
  };
}

const OUTCOME_ROW_KEYS = ["entry_date", "exit_date", "outcome_id", "return_pct", "status", "strategy", "ticker"];

export function isOutcomeTrackingRpcRow(value: unknown): value is OutcomeTrackingRpcRow {
  if (!value || typeof value !== "object") return false;
  const row = value as Record<string, unknown>;
  return (
    Object.keys(row).sort().join("|") === OUTCOME_ROW_KEYS.join("|") &&
    typeof row.outcome_id === "string" && row.outcome_id.length > 0 &&
    typeof row.ticker === "string" && row.ticker.length > 0 &&
    isOneOf(typeof row.strategy === "string" ? row.strategy : null, OUTCOME_STRATEGY_OPTIONS) &&
    isIsoDate(row.entry_date) &&
    isOneOf(typeof row.status === "string" ? row.status : null, OUTCOME_STATUS_OPTIONS) &&
    (row.exit_date === null || isIsoDate(row.exit_date)) &&
    (row.return_pct === null || (typeof row.return_pct === "number" && Number.isFinite(row.return_pct)))
  );
}

export function isOutcomeTrackingRpcResponse(value: unknown): value is OutcomeTrackingRpcRow[] {
  return Array.isArray(value) && value.length <= 500 && value.every(isOutcomeTrackingRpcRow);
}

export function getOutcomeStatusMeta(status: OutcomeStatus): OutcomeStatusMeta {
  return OUTCOME_STATUS_META[status];
}

export function getOutcomeStrategyLabel(strategy: OutcomeStrategy): string {
  return getStrategyLabel(strategy) ?? `전략 ${strategy}`;
}

export function formatOutcomeDate(value: string | null): string {
  if (!value) return "-";
  const match = /^(\d{4})-(\d{2})-(\d{2})/.exec(value);
  return match ? `${match[1]}.${match[2]}.${match[3]}` : value;
}

export function formatOutcomeReturnPct(value: number | null, status: OutcomeStatus): string {
  if (value === null) return status === "OPEN" || status === "SUSPENDED" || status === "DELISTED" ? "미확정" : "-";
  const sign = value > 0 ? "+" : "";
  return `${sign}${value.toFixed(2)}%`;
}

export function getOutcomeReturnTone(value: number | null): ValueTone {
  return toneFromSign(value);
}

export function getOutcomeSummary(rows: readonly OutcomeTrackingRpcRow[]) {
  return {
    settledCount: rows.filter((row) => row.status === "TP" || row.status === "SL" || row.status === "TIMEOUT").length,
    openCount: rows.filter((row) => row.status === "OPEN").length,
    suspendedCount: rows.filter((row) => row.status === "SUSPENDED").length,
    delistedCount: rows.filter((row) => row.status === "DELISTED").length,
  };
}
