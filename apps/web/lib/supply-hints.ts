import type {
  BatchKind,
  CandidateSupplyHintRpcRow,
  EvidenceInvestorStatus,
  SupplyHintStatus,
} from "./dashboard-types.ts";

const BATCH_KINDS = ["premarket", "intraday", "close"] as const satisfies readonly BatchKind[];
const INVESTOR_STATUSES = ["confirmed", "pending", "missing"] as const satisfies readonly EvidenceInvestorStatus[];
const HINT_STATUSES = ["good", "not_met", "undetermined"] as const satisfies readonly SupplyHintStatus[];

function isNonEmptyString(value: unknown): value is string {
  return typeof value === "string" && value.length > 0;
}

function isIsoDate(value: unknown): value is string {
  if (typeof value !== "string" || !/^\d{4}-\d{2}-\d{2}$/.test(value)) return false;
  const [year, month, day] = value.split("-").map(Number);
  const candidate = new Date(Date.UTC(year, month - 1, day));
  return candidate.getUTCFullYear() === year
    && candidate.getUTCMonth() === month - 1
    && candidate.getUTCDate() === day;
}

function isIsoDateTime(value: unknown): value is string {
  return typeof value === "string" && Number.isFinite(new Date(value).getTime());
}

function isFiniteNumberOrNull(value: unknown): value is number | null {
  return value === null || (typeof value === "number" && Number.isFinite(value));
}

function isLiteral<T extends string>(values: readonly T[], value: unknown): value is T {
  return typeof value === "string" && values.includes(value as T);
}

/** RPC 경계에서 supply hint 행의 shape와 literal 계약을 검증한다. */
export function isCandidateSupplyHintRpcRow(value: unknown): value is CandidateSupplyHintRpcRow {
  if (typeof value !== "object" || value === null) return false;
  const row = value as Record<string, unknown>;
  return (
    isNonEmptyString(row.candidate_id) &&
    isNonEmptyString(row.attempt_run_id) &&
    isNonEmptyString(row.ticker) &&
    isIsoDate(row.trading_day) &&
    row.slot === "D0" &&
    isLiteral(BATCH_KINDS, row.batch_kind) &&
    isFiniteNumberOrNull(row.foreign_net) &&
    isFiniteNumberOrNull(row.institution_net) &&
    isFiniteNumberOrNull(row.individual_net) &&
    isFiniteNumberOrNull(row.program_net) &&
    isLiteral(INVESTOR_STATUSES, row.investor_net_status) &&
    (row.collected_at === null || isIsoDateTime(row.collected_at)) &&
    isLiteral(HINT_STATUSES, row.hint_status)
  );
}
