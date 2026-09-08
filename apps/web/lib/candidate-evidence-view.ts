import type {
  CandidateEvidenceRawRow,
  EvidenceInvestorStatus,
} from "./dashboard-types.ts";
import {
  formatEvidenceNumber,
  formatEvidenceValue,
} from "./candidate-evidence.ts";

export const EVIDENCE_METRICS = [
  { key: "close", label: "종가", unit: "원" },
  { key: "volume", label: "거래량", unit: "주" },
  { key: "change_pct", label: "등락률", unit: "%" },
  { key: "foreign_net", label: "외인", unit: "주" },
  { key: "institution_net", label: "기관", unit: "주" },
  { key: "individual_net", label: "개인", unit: "주" },
  { key: "program_net", label: "프로그램", unit: "주" },
] as const;

export type EvidenceMetricKey = (typeof EVIDENCE_METRICS)[number]["key"];

export function formatEvidenceMetricValue(
  row: CandidateEvidenceRawRow | null,
  status: EvidenceInvestorStatus | "missing",
  key: EvidenceMetricKey
): string {
  if (key === "close") return formatEvidenceNumber(row?.close);
  if (key === "volume") return formatEvidenceNumber(row?.volume);
  if (key === "change_pct") return row ? `${formatEvidenceNumber(row.change_pct)}%` : "미수집";
  return formatEvidenceValue(row?.[key], status);
}

export function formatEvidenceStatusLabel(status: EvidenceInvestorStatus | "missing"): string {
  return status === "confirmed" ? "확정" : status === "pending" ? "미확정" : "미수집";
}

export function getEvidenceTradingDay(row: CandidateEvidenceRawRow | null): string | null {
  const tradingDay = row?.trading_day.trim();
  return tradingDay || null;
}
