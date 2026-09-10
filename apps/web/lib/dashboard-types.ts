export type RunStatus =
  | "running"
  | "ready_to_publish"
  | "published"
  | "partial"
  | "failed"
  | "skipped"
  | "superseded"
  | "cancelled";

export type BatchKind = "premarket" | "intraday" | "close";
export type RunTrigger = "schedule" | "manual";
export type Market = "KOSPI" | "KOSDAQ";
export type SupplyHintStatus = "good" | "not_met" | "undetermined";
export type OutcomeStatus = "TP" | "SL" | "TIMEOUT" | "OPEN" | "SUSPENDED" | "DELISTED";
export type OutcomeStrategy = "A" | "B" | "C" | "D" | "E" | "F";

/** Story 5.11 get_outcome_tracking_rows()가 브라우저에 반환하는 제한된 행. */
export interface OutcomeTrackingRpcRow {
  outcome_id: string;
  ticker: string;
  strategy: OutcomeStrategy;
  entry_date: string;
  status: OutcomeStatus;
  exit_date: string | null;
  return_pct: number | null;
}

export interface CandidatesSection {
  candidate_count: number;
  truncated_count: number;
  original_count: number | null;
  excluded_count: number | null;
}

export interface CompleteSnapshot {
  logical_run_key: string;
  run_id: string;
  trading_day: string;
  batch_kind: BatchKind;
  published_at: string;
  sections: {
    candidates: CandidatesSection;
  };
}

export interface LatestAttempt {
  run_id: string;
  logical_run_key: string;
  trading_day: string;
  batch_kind: BatchKind;
  status: RunStatus;
  trigger: RunTrigger;
  started_at: string;
  finished_at: string | null;
  stage_status: Record<string, string>;
  unprocessed_count: number;
  truncated_count: number;
  original_count: number | null;
  excluded_count: number | null;
}

/** infra/supabase/migrations/202609020000_create_dashboard_snapshot.sql의 get_dashboard_snapshot() 반환 shape. */
export interface DashboardSnapshot {
  no_snapshot: boolean;
  result_code: "OK" | "NO_SNAPSHOT";
  complete_snapshot: CompleteSnapshot | null;
  latest_attempt: LatestAttempt | null;
  latest_partial_run_id: string | null;
  available_partial_sections: string[];
  missing_sections: string[];
  unprocessed_items: number;
}

function isRecord(value: unknown): value is Record<string, unknown> {
  return typeof value === "object" && value !== null;
}

/** 외부 RPC JSON이 tracking route의 서버 컴포넌트 계약에 맞는지 최소 안전 검증한다. */
export function isDashboardSnapshot(value: unknown): value is DashboardSnapshot {
  if (!isRecord(value)) return false;
  if (typeof value.no_snapshot !== "boolean" || (value.result_code !== "OK" && value.result_code !== "NO_SNAPSHOT")) return false;
  if (value.no_snapshot !== (value.complete_snapshot === null)) return false;
  if (!Array.isArray(value.available_partial_sections) || !value.available_partial_sections.every((item) => typeof item === "string")) return false;
  if (!Array.isArray(value.missing_sections) || !value.missing_sections.every((item) => typeof item === "string")) return false;
  if (typeof value.unprocessed_items !== "number" || !Number.isFinite(value.unprocessed_items)) return false;

  if (value.complete_snapshot !== null) {
    const snapshot = value.complete_snapshot;
    if (!isRecord(snapshot) || typeof snapshot.run_id !== "string" || typeof snapshot.logical_run_key !== "string" ||
      typeof snapshot.trading_day !== "string" || typeof snapshot.batch_kind !== "string" || typeof snapshot.published_at !== "string") return false;
    if (!isRecord(snapshot.sections) || !isRecord(snapshot.sections.candidates) ||
      typeof snapshot.sections.candidates.candidate_count !== "number") return false;
  }

  if (value.latest_attempt !== null) {
    const attempt = value.latest_attempt;
    if (!isRecord(attempt) || typeof attempt.run_id !== "string" || typeof attempt.logical_run_key !== "string" ||
      typeof attempt.trading_day !== "string" || typeof attempt.batch_kind !== "string" || typeof attempt.status !== "string" ||
      typeof attempt.trigger !== "string" || typeof attempt.started_at !== "string" || !isRecord(attempt.stage_status)) return false;
  }
  return true;
}

/** infra/supabase/migrations/202609081300_create_get_market_supply.sql 반환 행. */
export interface MarketSupplyRpcRow {
  market: Market;
  trading_day: string;
  foreign_net: number;
  institution_net: number;
  individual_net: number;
  program_net: number;
  collected_at: string;
}

/** candidate_supply_hints view 및 get_candidate_supply_hints(p_run_id) 반환 행. */
export interface CandidateSupplyHintRpcRow {
  candidate_id: string;
  attempt_run_id: string;
  ticker: string;
  trading_day: string;
  slot: "D0";
  batch_kind: BatchKind;
  foreign_net: number | null;
  institution_net: number | null;
  individual_net: number | null;
  program_net: number | null;
  investor_net_status: EvidenceInvestorStatus;
  collected_at: string | null;
  hint_status: SupplyHintStatus;
}

/** infra/supabase/migrations/202609011600_create_run_lineage.sql의 runs 테이블 컬럼. */
export interface RunRow {
  run_id: string;
  logical_run_key: string;
  attempt_no: number;
  fence_token: number;
  lease_token: string;
  lease_expires_at: string;
  started_at: string;
  finished_at: string | null;
  trigger: RunTrigger;
  status: RunStatus;
  skip_reason: string | null;
  stage_status: Record<string, string>;
  unprocessed_count: number;
  truncated_count: number;
  fallback_used: boolean;
  selection_input_hash: string | null;
  original_count: number | null;
  excluded_count: number | null;
}

/**
 * infra/supabase/migrations/202609031100_add_vanished_strategies_to_get_today_candidate_cards.sql의
 * get_today_candidate_cards(p_run_id) 반환 배열 원소 shape.
 */
export interface TodayCandidateCardRow {
  candidate_id: string;
  ticker: string;
  name: string | null;
  strategies: string[];
  /** Story 2.8: 이전 attempt에서 active였으나 현재 attempt에서 재태깅되지 않은 전략(status=vanished). */
  vanished_strategies: string[];
  supply_partial_missing: boolean;
}

export type EvidenceSource = "t1859" | "t1852" | "t1856";
export type EvidenceSlot = "D0" | "D-1" | "D-2";
export type EvidenceInvestorStatus = "confirmed" | "pending" | "missing";

/**
 * infra/supabase/migrations/202609081200_create_get_candidate_evidence.sql의
 * get_candidate_evidence(p_run_id) 반환 배열 원소 안의 supply 행 shape.
 */
export interface CandidateEvidenceRawRow {
  trading_day: string;
  slot: EvidenceSlot;
  close: number;
  volume: number;
  change_pct: number;
  foreign_net: number | null;
  institution_net: number | null;
  individual_net: number | null;
  program_net: number | null;
  investor_net_status: EvidenceInvestorStatus;
  collected_at: string;
}

/** get_candidate_evidence() 반환 배열 원소. candidate_id와 attempt는 RPC p_run_id로 함께 격리된다. */
export interface CandidateEvidenceRpcRow {
  candidate_id: string;
  sources: EvidenceSource[];
  rows: CandidateEvidenceRawRow[];
}

export type DisappearedReason = "population_dropout" | "collection_failure";

/**
 * infra/supabase/migrations/202609031200_create_get_today_disappeared_candidates.sql의
 * get_today_disappeared_candidates(p_run_id) 반환 배열 원소 shape.
 */
export interface DisappearedCandidateRow {
  ticker: string;
  name: string | null;
  reason: DisappearedReason;
  strategies: string[];
}

/**
 * UJ-2: 장중 배치(batch_kind !== 'close')로 만들어진 complete_snapshot인지 판정한다.
 * complete_snapshot이 없으면(스냅샷 없음/실패 등) 장중 라벨을 표시하지 않는다.
 */
export function isIntradaySnapshot(snapshot: DashboardSnapshot): boolean {
  return snapshot.complete_snapshot != null && snapshot.complete_snapshot.batch_kind !== "close";
}

/** infra/supabase/migrations/202609011600_create_run_lineage.sql의 logical_runs 테이블 컬럼. */
export interface LogicalRunRow {
  logical_run_key: string;
  trading_day: string;
  batch_kind: BatchKind;
  active_attempt_run_id: string | null;
  canonical_success_run_id: string | null;
  current_complete_run_id: string | null;
  latest_partial_run_id: string | null;
  published_at: string | null;
}
