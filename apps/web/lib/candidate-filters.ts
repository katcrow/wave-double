import type { CandidateCardViewModel, CandidateSignalStatus } from "./candidate-cards.ts";
import type {
  CandidateEvidenceRpcRow,
  CandidateSupplyHintRpcRow,
  EvidenceInvestorStatus,
  SupplyHintStatus,
} from "./dashboard-types.ts";
import { getStrategyLabel } from "./strategy-labels.ts";

export type CandidateMissingFilter = "include" | "exclude";

export interface CandidateFilterState {
  strategies: string[];
  hintStatuses: SupplyHintStatus[];
  signalStatuses: CandidateSignalStatus[];
  sources: string[];
  missingSupply: CandidateMissingFilter;
}

export interface CandidateFilterItem {
  candidate: CandidateCardViewModel;
  evidence?: CandidateEvidenceRpcRow;
  hintStatus: SupplyHintStatus;
  investorNetStatus: EvidenceInvestorStatus | null;
  sources: string[];
  /** 카드 결측 플래그와 D0 힌트 RPC 상태를 합친 필터용 결측 판정. */
  supplyMissing: boolean;
}

export const SIGNAL_STATUS_LABEL: Record<CandidateSignalStatus, string> = {
  active: "활성",
  vanished: "소멸",
  mixed: "혼합",
};

export const HINT_STATUS_LABEL: Record<SupplyHintStatus, string> = {
  good: "좋은 수급",
  not_met: "미충족",
  undetermined: "판정 불가 · 장 마감 후 확정",
};

export const MISSING_SUPPLY_LABEL: Record<CandidateMissingFilter, string> = {
  include: "수급 결측 포함",
  exclude: "수급 결측 제외",
};

/** 기본값: 소멸(vanished)·혼합(mixed) 시그널은 목록에서 숨기고 활성 시그널만 보여준다. */
const DEFAULT_SIGNAL_STATUSES: CandidateSignalStatus[] = ["active"];

export function getDefaultCandidateFilterState(): CandidateFilterState {
  return {
    strategies: [],
    hintStatuses: [],
    signalStatuses: [...DEFAULT_SIGNAL_STATUSES],
    sources: [],
    missingSupply: "include",
  };
}

function sameSignalStatuses(values: CandidateSignalStatus[]): boolean {
  if (values.length !== DEFAULT_SIGNAL_STATUSES.length) return false;
  return DEFAULT_SIGNAL_STATUSES.every((status) => values.includes(status));
}

function compareDateValue(left: string | null | undefined, right: string | null | undefined): number {
  if (left === right) return 0;
  if (!left) return -1;
  if (!right) return 1;
  const leftTime = new Date(left).getTime();
  const rightTime = new Date(right).getTime();
  if (Number.isFinite(leftTime) && Number.isFinite(rightTime) && leftTime !== rightTime) {
    return leftTime - rightTime;
  }
  return left.localeCompare(right);
}

function latestEvidenceRow(row: CandidateEvidenceRpcRow): CandidateEvidenceRpcRow["rows"][number] | null {
  return row.rows.reduce<CandidateEvidenceRpcRow["rows"][number] | null>((latest, current) => {
    if (!latest) return current;
    const dayComparison = current.trading_day.localeCompare(latest.trading_day);
    if (dayComparison !== 0) return dayComparison > 0 ? current : latest;
    return compareDateValue(current.collected_at, latest.collected_at) > 0 ? current : latest;
  }, null);
}

function compareEvidenceRows(left: CandidateEvidenceRpcRow, right: CandidateEvidenceRpcRow): number {
  const leftLatest = latestEvidenceRow(left);
  const rightLatest = latestEvidenceRow(right);
  const dayComparison = (leftLatest?.trading_day ?? "").localeCompare(rightLatest?.trading_day ?? "");
  if (dayComparison !== 0) return dayComparison;
  const collectedComparison = compareDateValue(leftLatest?.collected_at, rightLatest?.collected_at);
  if (collectedComparison !== 0) return collectedComparison;
  return JSON.stringify(left.sources).localeCompare(JSON.stringify(right.sources));
}

function compareHintRows(left: CandidateSupplyHintRpcRow, right: CandidateSupplyHintRpcRow): number {
  const dayComparison = left.trading_day.localeCompare(right.trading_day);
  if (dayComparison !== 0) return dayComparison;
  const collectedComparison = compareDateValue(left.collected_at, right.collected_at);
  if (collectedComparison !== 0) return collectedComparison;
  return JSON.stringify(left).localeCompare(JSON.stringify(right));
}

function selectNewestByCandidate<T extends { candidate_id: string }>(
  rows: T[],
  compare: (left: T, right: T) => number,
): Map<string, T> {
  const selected = new Map<string, T>();
  for (const row of rows) {
    const previous = selected.get(row.candidate_id);
    if (!previous || compare(row, previous) > 0) selected.set(row.candidate_id, row);
  }
  return selected;
}

/** 서버가 전달한 배열을 필터링 가능한 직렬화 모델로 조합한다. */
export function buildCandidateFilterItems(
  candidates: CandidateCardViewModel[],
  evidenceRows: CandidateEvidenceRpcRow[],
  hintRows: CandidateSupplyHintRpcRow[],
  hintFetchFailed: boolean,
): CandidateFilterItem[] {
  const evidenceByCandidate = selectNewestByCandidate(evidenceRows, compareEvidenceRows);
  const hintByCandidate = selectNewestByCandidate(hintRows, compareHintRows);

  return candidates.map((candidate) => {
    const evidence = evidenceByCandidate.get(candidate.candidateId);
    const hint = hintByCandidate.get(candidate.candidateId);
    const investorNetStatus = hintFetchFailed ? null : hint?.investor_net_status ?? null;
    return {
      candidate,
      evidence,
      hintStatus: hintFetchFailed ? "undetermined" : hint?.hint_status ?? "undetermined",
      investorNetStatus,
      sources: evidence?.sources ?? [],
      supplyMissing:
        candidate.supplyPartialMissing ||
        (!hintFetchFailed &&
          (hint === undefined || investorNetStatus === "pending" || investorNetStatus === "missing")),
    };
  });
}

function matchesAny<T>(selected: T[], values: T[]): boolean {
  return selected.length === 0 || selected.some((value) => values.includes(value));
}

/** 전략/힌트/시그널/원천은 그룹 내부 OR, 그룹 간 AND로 적용한다. */
export function filterCandidateItems(
  items: CandidateFilterItem[],
  filters: CandidateFilterState,
): CandidateFilterItem[] {
  return items.filter((item) => {
    const allStrategies = [...item.candidate.strategies, ...item.candidate.vanishedStrategies];
    return (
      matchesAny(filters.strategies, allStrategies) &&
      matchesAny(filters.hintStatuses, [item.hintStatus]) &&
      matchesAny(filters.signalStatuses, [item.candidate.signalStatus]) &&
      matchesAny(filters.sources, item.sources) &&
      (filters.missingSupply === "include" || !item.supplyMissing)
    );
  });
}

export function hasActiveCandidateFilters(filters: CandidateFilterState): boolean {
  return (
    filters.strategies.length > 0 ||
    filters.hintStatuses.length > 0 ||
    !sameSignalStatuses(filters.signalStatuses) ||
    filters.sources.length > 0 ||
    filters.missingSupply === "exclude"
  );
}

/** 0건 상태에 표시할 현재 필터의 짧은 요약. */
export function summarizeCandidateFilters(filters: CandidateFilterState): string[] {
  const summary: string[] = [];
  if (filters.strategies.length > 0) {
    summary.push(`전략: ${filters.strategies.map((strategy) => getStrategyLabel(strategy) ?? `전략 ${strategy}`).join(", ")}`);
  }
  if (filters.hintStatuses.length > 0) {
    summary.push(`수급 힌트: ${filters.hintStatuses.map((status) => HINT_STATUS_LABEL[status]).join(", ")}`);
  }
  if (!sameSignalStatuses(filters.signalStatuses)) {
    summary.push(`시그널 상태: ${filters.signalStatuses.map((status) => SIGNAL_STATUS_LABEL[status]).join(", ") || "전체"}`);
  }
  if (filters.sources.length > 0) {
    summary.push(`원천: ${filters.sources.join(", ")}`);
  }
  if (filters.missingSupply === "exclude") summary.push(MISSING_SUPPLY_LABEL.exclude);
  return summary;
}
