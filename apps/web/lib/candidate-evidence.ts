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
  missingSlots: EvidenceSlot[];
  pendingSlotCount: number;
  pendingSlots: EvidenceSlot[];
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

function isUsableNumber(value: unknown): value is number {
  return typeof value === "number" && Number.isFinite(value);
}

function isEvidenceSource(value: unknown): value is CandidateEvidenceRpcRow["sources"][number] {
  return value === "t1859" || value === "t1852" || value === "t1856";
}

function isEvidenceSlot(value: unknown): value is EvidenceSlot {
  return value === "D0" || value === "D-1" || value === "D-2";
}

function isEvidenceStatus(value: unknown): value is EvidenceInvestorStatus {
  return value === "confirmed" || value === "pending" || value === "missing";
}

function isCandidateEvidenceRawRow(value: unknown): value is CandidateEvidenceRawRow {
  if (typeof value !== "object" || value === null) return false;
  const row = value as Record<string, unknown>;
  return (
    typeof row.trading_day === "string" &&
    isEvidenceSlot(row.slot) &&
    isUsableNumber(row.close) &&
    isUsableNumber(row.volume) &&
    isUsableNumber(row.change_pct) &&
    (row.foreign_net === null || isUsableNumber(row.foreign_net)) &&
    (row.institution_net === null || isUsableNumber(row.institution_net)) &&
    (row.individual_net === null || isUsableNumber(row.individual_net)) &&
    (row.program_net === null || isUsableNumber(row.program_net)) &&
    isEvidenceStatus(row.investor_net_status) &&
    typeof row.collected_at === "string"
  );
}

/** 서버 RPC 결과를 렌더 전에 검증해 malformed 응답이 SSR을 깨뜨리지 않게 한다. */
export function isCandidateEvidenceRpcRow(value: unknown): value is CandidateEvidenceRpcRow {
  if (typeof value !== "object" || value === null) return false;
  const row = value as Record<string, unknown>;
  return (
    typeof row.candidate_id === "string" &&
    Array.isArray(row.sources) &&
    row.sources.every(isEvidenceSource) &&
    Array.isArray(row.rows) &&
    row.rows.every(isCandidateEvidenceRawRow)
  );
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
  const usableRows = rows.filter((row) => SLOT_ORDER.has(row.slot));
  const latest = latestRowsBySlot(usableRows);
  const slots = EVIDENCE_SLOTS.map((slot) => {
    const row = latest.get(slot) ?? null;
    return {
      slot,
      row,
      status: normalizeInvestorStatus(row?.investor_net_status),
    };
  });

  const collectedAt = usableRows
    .map((row) => row.collected_at)
    .filter((value): value is string => validDate(value) !== null)
    .sort((a, b) => (validDate(b) ?? 0) - (validDate(a) ?? 0))[0] ?? null;

  return {
    candidateId: evidence?.candidate_id ?? "",
    sourceLabel: evidence?.sources?.length ? evidence.sources.join(" · ") : "기본",
    collectedAt,
    slots,
    missingSlotCount: slots.filter(({ row, status }) => row === null || status === "missing").length,
    missingSlots: slots
      .filter(({ row, status }) => row === null || status === "missing")
      .map(({ slot }) => slot),
    pendingSlotCount: slots.filter(({ status }) => status === "pending").length,
    pendingSlots: slots.filter(({ status }) => status === "pending").map(({ slot }) => slot),
    hasRows: usableRows.length > 0,
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

export function formatEvidenceSummary(
  missingSlots: EvidenceSlot[],
  pendingSlots: EvidenceSlot[]
): string {
  const parts: string[] = [];
  if (missingSlots.length > 0) {
    parts.push(`미수집 ${missingSlots.length}행(${missingSlots.join("/")})`);
  }
  if (pendingSlots.length > 0) {
    parts.push(`미확정 ${pendingSlots.length}행(${pendingSlots.join("/")})`);
  }
  return parts.length > 0 ? `부분결측 · ${parts.join(" · ")}` : "";
}

export function evidenceSlotLabel(slot: EvidenceSlot): string {
  return slot;
}
