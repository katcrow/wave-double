import type { TopTradingCandidateRpcRow } from "./dashboard-types";

export const TOP_TRADING_CANDIDATE_LIMIT = 3;

export interface TopTradingCandidateViewModel {
  rank: number;
  candidateId: string;
  name: string | null;
  displayName: string;
  ticker: string;
  tradingValue: number;
  formattedTradingValue: string;
}

const NUMBER_FORMATTER = new Intl.NumberFormat("ko-KR", {
  maximumFractionDigits: 0,
});

function isSafeNonNegativeNumber(value: unknown): value is number {
  return (
    typeof value === "number" &&
    Number.isFinite(value) &&
    value >= 0 &&
    value <= Number.MAX_SAFE_INTEGER
  );
}

function isIsoDate(value: unknown): value is string {
  if (typeof value !== "string" || !/^\d{4}-\d{2}-\d{2}$/.test(value)) return false;
  const [year, month, day] = value.split("-").map(Number);
  const date = new Date(Date.UTC(year, month - 1, day));
  return date.getUTCFullYear() === year && date.getUTCMonth() === month - 1 && date.getUTCDate() === day;
}

/** 서버 RPC 경계에서 거래대금 숫자와 snapshot lineage를 최소 shape로 검증한다. */
export function isTopTradingCandidateRpcRow(value: unknown): value is TopTradingCandidateRpcRow {
  if (typeof value !== "object" || value === null) return false;
  const row = value as Record<string, unknown>;
  return (
    typeof row.candidate_id === "string" && row.candidate_id.length > 0 &&
    typeof row.attempt_run_id === "string" && row.attempt_run_id.length > 0 &&
    typeof row.ticker === "string" && row.ticker.length > 0 &&
    (row.name === null || typeof row.name === "string") &&
    isIsoDate(row.trading_day) &&
    isSafeNonNegativeNumber(row.trading_value)
  );
}

function compareRows(a: TopTradingCandidateRpcRow, b: TopTradingCandidateRpcRow): number {
  return b.trading_value - a.trading_value || a.ticker.localeCompare(b.ticker);
}

/**
 * 동일 complete snapshot의 행만 남기고, SQL 계약을 방어적으로 재확인해 화면 모델을 만든다.
 * rank와 표시 문자열은 이 함수에서만 정한다.
 */
export function buildTopTradingCandidateViewModels(
  rows: readonly TopTradingCandidateRpcRow[],
  expectedRunId: string,
  expectedTradingDay: string,
): TopTradingCandidateViewModel[] {
  return rows
    .filter((row) => row.attempt_run_id === expectedRunId && row.trading_day === expectedTradingDay)
    .sort(compareRows)
    .slice(0, TOP_TRADING_CANDIDATE_LIMIT)
    .map((row, index) => ({
      rank: index + 1,
      candidateId: row.candidate_id,
      name: row.name?.trim() || null,
      displayName: row.name?.trim() || row.ticker,
      ticker: row.ticker,
      tradingValue: row.trading_value,
      formattedTradingValue: NUMBER_FORMATTER.format(row.trading_value),
    }));
}

export function formatTradingValue(value: number): string {
  return isSafeNonNegativeNumber(value) ? NUMBER_FORMATTER.format(value) : "미확인";
}
