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
 * infra/supabase/migrations/202609022100_create_get_today_candidate_cards.sql의
 * get_today_candidate_cards(p_run_id) 반환 배열 원소 shape.
 */
export interface TodayCandidateCardRow {
  candidate_id: string;
  ticker: string;
  name: string | null;
  strategies: string[];
  supply_partial_missing: boolean;
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
