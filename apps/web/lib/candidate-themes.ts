import type { CandidateThemeRpcRow } from "./dashboard-types.ts";

export const MAX_VISIBLE_THEMES = 3;

export interface CandidateThemeViewModel {
  themeCode: string;
  themeName: string;
  averageChangePct: number;
  formattedAverageChangePct: string;
}

function isFiniteNumber(value: unknown): value is number {
  return typeof value === "number" && Number.isFinite(value);
}

export function isCandidateThemeRpcRow(value: unknown): value is CandidateThemeRpcRow {
  if (typeof value !== "object" || value === null) return false;
  const row = value as Record<string, unknown>;
  return (
    typeof row.theme_code === "string" && row.theme_code.trim().length > 0 &&
    typeof row.theme_name === "string" && row.theme_name.trim().length > 0 &&
    isFiniteNumber(row.average_change_pct)
  );
}

export function isCandidateThemeRpcRows(value: unknown): value is CandidateThemeRpcRow[] {
  return Array.isArray(value) && value.every(isCandidateThemeRpcRow);
}

export function formatThemeChangePct(value: number): string {
  const sign = value > 0 ? "+" : "";
  return `${sign}${value.toFixed(2)}%`;
}

export function buildCandidateThemeViewModels(
  rows: readonly CandidateThemeRpcRow[],
): CandidateThemeViewModel[] {
  return [...rows]
    .filter(isCandidateThemeRpcRow)
    .sort((a, b) => b.average_change_pct - a.average_change_pct || a.theme_code.localeCompare(b.theme_code))
    .map((row) => ({
      themeCode: row.theme_code,
      themeName: row.theme_name.trim(),
      averageChangePct: row.average_change_pct,
      formattedAverageChangePct: formatThemeChangePct(row.average_change_pct),
    }));
}
