import type {
  CandidateEvidenceRawRow,
  EvidenceInvestorStatus,
} from "./dashboard-types.ts";
import {
  formatEvidenceNumber,
  formatEvidenceSignedNumber,
  formatEvidenceValue,
} from "./candidate-evidence.ts";
import { toneFromSign, type ValueTone } from "./value-tone.ts";

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

const SIGNED_METRIC_KEYS = [
  "change_pct",
  "foreign_net",
  "institution_net",
  "individual_net",
  "program_net",
] as const satisfies readonly EvidenceMetricKey[];

export function formatEvidenceMetricValue(
  row: CandidateEvidenceRawRow | null,
  status: EvidenceInvestorStatus | "missing",
  key: EvidenceMetricKey
): string {
  if (key === "close") return formatEvidenceNumber(row?.close);
  if (key === "volume") return formatEvidenceNumber(row?.volume);
  if (key === "change_pct") return row ? `${formatEvidenceSignedNumber(row.change_pct)}%` : "미수집";
  return formatEvidenceValue(row?.[key], status);
}

/** 등락률·투자자별 순매수처럼 부호가 있는 값에만 색상 톤을 부여한다. */
export function getEvidenceMetricTone(
  row: CandidateEvidenceRawRow | null,
  status: EvidenceInvestorStatus | "missing",
  key: EvidenceMetricKey
): ValueTone {
  if (status !== "confirmed" || !row) return "neutral";
  if (!(SIGNED_METRIC_KEYS as readonly string[]).includes(key)) return "neutral";
  return toneFromSign(row[key as (typeof SIGNED_METRIC_KEYS)[number]]);
}

export function formatEvidenceStatusLabel(status: EvidenceInvestorStatus | "missing"): string {
  return status === "confirmed" ? "확정" : status === "pending" ? "미확정" : "미수집";
}

export function getEvidenceTradingDay(row: CandidateEvidenceRawRow | null): string | null {
  const tradingDay = row?.trading_day.trim();
  return tradingDay || null;
}
