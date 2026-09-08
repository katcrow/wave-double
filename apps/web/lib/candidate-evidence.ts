import type {
  CandidateEvidenceRawRow,
  CandidateEvidenceRpcRow,
  EvidenceInvestorStatus,
  EvidenceSlot,
} from "./dashboard-types";

export const EVIDENCE_SLOTS = ["D0", "D-1", "D-2"] as const satisfies readonly EvidenceSlot[];

export interface NormalizedEvidenceSlot {
  slot: EvidenceSlot;
  row: CandidateEvidenceRawRow | null;
  status: EvidenceInvestorStatus | "missing";
}

export interface CandidateEvidenceViewModel {
  candidateId: string;
  sourceLabel: string;
  collectedAt: string | null;
  slots: NormalizedEvidenceSlot[];
  missingSlotCount: number;
  pendingSlotCount: number;
  hasRows: boolean;
}

const NUMBER_FORMATTER = new Intl.NumberFormat("ko-KR", {
  maximumFractionDigits: 2,
});

const DATETIME_FORMATTER = new Intl.DateTimeFormat("ko-KR", {
  timeZone: "Asia/Seoul",
  year: "numeric",
  month: "2-digit",
  day: "2-digit",
  hour: "2-digit",
  minute: "2-digit",
  hour12: false,
});

const SLOT_ORDER = new Map<EvidenceSlot, number>(EVIDENCE_SLOTS.map((slot, index) => [slot, index]));

function validDate(iso: string | null | undefined): number | null {
  if (!iso) return null;
  const timestamp = new Date(iso).getTime();
  return Number.isFinite(timestamp) ? timestamp : null;
}

function isUsableNumber(value: number | null | undefined): value is number {
  return typeof value === "number" && Number.isFinite(value);
}

function normalizeInvestorStatus(value: string | undefined): EvidenceInvestorStatus | "missing" {
  return value === "confirmed" || value === "pending" || value === "missing" ? value : "missing";
}

function latestRowsBySlot(rows: CandidateEvidenceRawRow[]): Map<EvidenceSlot, CandidateEvidenceRawRow> {
  const latest = new Map<EvidenceSlot, CandidateEvidenceRawRow>();
  for (const row of rows) {
    if (!SLOT_ORDER.has(row.slot)) continue;
    const previous = latest.get(row.slot);
    if (!previous) {
      latest.set(row.slot, row);
      continue;
    }
    const rowDay = row.trading_day.localeCompare(previous.trading_day);
    const rowCollected = (validDate(row.collected_at) ?? Number.MIN_SAFE_INTEGER) -
      (validDate(previous.collected_at) ?? Number.MIN_SAFE_INTEGER);
    if (rowDay > 0 || (rowDay === 0 && rowCollected > 0)) latest.set(row.slot, row);
  }
  return latest;
}

/** RPC 응답을 항상 D0/D-1/D-2 세 슬롯으로 정규화한다. 없는 슬롯은 missing으로 유지한다. */
export function normalizeCandidateEvidence(
  evidence: CandidateEvidenceRpcRow | null | undefined
): CandidateEvidenceViewModel {
  const rows = evidence?.rows ?? [];
  const latest = latestRowsBySlot(rows);
  const slots = EVIDENCE_SLOTS.map((slot) => {
    const row = latest.get(slot) ?? null;
    return {
      slot,
      row,
      status: normalizeInvestorStatus(row?.investor_net_status),
    };
  });

  const collectedAt = rows
    .map((row) => row.collected_at)
    .filter((value): value is string => validDate(value) !== null)
    .sort((a, b) => (validDate(b) ?? 0) - (validDate(a) ?? 0))[0] ?? null;

  return {
    candidateId: evidence?.candidate_id ?? "",
    sourceLabel: evidence?.sources?.length ? evidence.sources.join(" · ") : "기본",
    collectedAt,
    slots,
    missingSlotCount: slots.filter(({ row, status }) => row === null || status === "missing").length,
    pendingSlotCount: slots.filter(({ status }) => status === "pending").length,
    hasRows: rows.length > 0,
  };
}

/** confirmed의 실제 0은 숫자 0으로 유지하고 미확정/미수집만 상태 문구로 치환한다. */
export function formatEvidenceValue(
  value: number | null | undefined,
  status: EvidenceInvestorStatus | "missing"
): string {
  if (status === "pending") return "미확정";
  if (status === "missing" || !isUsableNumber(value)) return "미수집";
  return NUMBER_FORMATTER.format(value);
}

export function formatEvidenceNumber(value: number | null | undefined): string {
  return isUsableNumber(value) ? NUMBER_FORMATTER.format(value) : "미수집";
}

export function formatEvidenceDateTime(iso: string | null): string {
  const timestamp = validDate(iso);
  return timestamp === null ? "시각 미상" : DATETIME_FORMATTER.format(new Date(timestamp));
}

export function evidenceSlotLabel(slot: EvidenceSlot): string {
  return slot;
}
