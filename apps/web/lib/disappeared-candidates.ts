import type { DisappearedCandidateRow, DisappearedReason } from "./dashboard-types.ts";

/**
 * Story 2.8: get_today_disappeared_candidates() 원시 행을 렌더링용 뷰모델로 변환하는 순수 함수.
 * "모집단 이탈"과 "수집 실패"는 사용자에게 서로 다른 문구로 구분되어야 하므로(스펙 Always 절),
 * reason 코드를 사람이 읽을 문구로 매핑하는 단일 출처를 이 모듈이 제공한다.
 */
export const DISAPPEARED_REASON_LABEL: Record<DisappearedReason, string> = {
  population_dropout: "모집단 이탈",
  collection_failure: "수집 실패",
};

export interface DisappearedCandidateViewModel {
  ticker: string;
  /** 렌더링용 표시 이름. name이 null이면 ticker로 대체. */
  displayName: string;
  reason: DisappearedReason;
  /** DISAPPEARED_REASON_LABEL 매핑 결과. 알 수 없는 reason 값이 와도 원본 문자열로 폴백한다. */
  reasonLabel: string;
  /** 직전 attempt에서 active였던 정렬된 전략 배열(SQL이 이미 정렬해 반환, 재정렬하지 않음). */
  strategies: string[];
}

export function buildDisappearedCandidateViewModels(
  rows: DisappearedCandidateRow[]
): DisappearedCandidateViewModel[] {
  return rows.map((row) => ({
    ticker: row.ticker,
    displayName: row.name ?? row.ticker,
    reason: row.reason,
    reasonLabel: DISAPPEARED_REASON_LABEL[row.reason] ?? row.reason,
    strategies: row.strategies,
  }));
}
