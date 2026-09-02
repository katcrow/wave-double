import type { DashboardSnapshot } from "./dashboard-types.ts";
import { formatKstDateTime, formatKstTime, isStaleSince } from "./format.ts";

const BATCH_KIND_LABEL: Record<string, string> = {
  close: "종가 확정",
  premarket: "장중 참고 · 최종 추천 미확정",
  intraday: "장중 참고 · 최종 추천 미확정",
};

const TRIGGER_LABEL: Record<string, string> = {
  schedule: "자동",
  manual: "수동",
};

export interface TrustBarState {
  statusLine: string;
  stale: boolean;
  candidateCount: number | undefined;
  /** epics.md AC: "KST 실행 시각·트리거 유형·신선도"의 트리거 유형. */
  triggerLabel: string | undefined;
  /**
   * 비차단 Toast/notice 문구(실패/부분성공/stale에서만 채워짐).
   * 폴백 원천 사용은 스펙 Never 절에 따라 판정 근거(원천 필드)가 없어 이 알림에 포함하지 않는다.
   */
  notice: string | null;
}

/**
 * Story 1.9 I/O 매트릭스 6개 상태(스냅샷 없음/정상 발행/실패/부분성공/휴장일 스킵/stale)를 판정한다.
 * Design Notes: freshness 기준 시각은 complete_snapshot.published_at, 없으면
 * latest_attempt.finished_at ?? started_at이며 60분 이상 경과 시 stale.
 */
export function deriveTrustBarState(snapshot: DashboardSnapshot): TrustBarState {
  const { latest_attempt: latestAttempt, complete_snapshot: completeSnapshot } = snapshot;

  const referenceTimestamp =
    completeSnapshot?.published_at ??
    latestAttempt?.finished_at ??
    latestAttempt?.started_at ??
    null;
  const stale = referenceTimestamp ? isStaleSince(referenceTimestamp) : false;

  let statusLine: string;

  if (latestAttempt?.status === "failed") {
    // Design Notes: complete_snapshot도 없으면(첫 배치부터 실패) 빈 상태 문구보다 우선한다.
    statusLine = completeSnapshot
      ? `배치 실패 · 마지막 성공 ${formatKstDateTime(completeSnapshot.published_at)}`
      : "배치 실패 · 이전 성공 없음";
  } else if (latestAttempt?.status === "skipped") {
    statusLine = "휴장일 · 배치 스킵";
  } else if (latestAttempt?.status === "partial") {
    statusLine = `부분성공 · 미처리 ${latestAttempt.unprocessed_count}건`;
  } else if (completeSnapshot) {
    const label = BATCH_KIND_LABEL[completeSnapshot.batch_kind] ?? "배치 확정";
    statusLine = `${label} · ${formatKstTime(completeSnapshot.published_at)} KST`;
  } else {
    statusLine = "상태 없음";
  }

  if (stale && referenceTimestamp) {
    statusLine += ` · 데이터가 60분 이상 오래됨 (${formatKstDateTime(referenceTimestamp)})`;
  }

  let notice: string | null = null;
  if (latestAttempt?.status === "failed" || latestAttempt?.status === "partial") {
    notice = statusLine;
  } else if (stale) {
    notice = `데이터가 60분 이상 오래됨 (${referenceTimestamp ? formatKstDateTime(referenceTimestamp) : "-"})`;
  }

  return {
    statusLine,
    stale,
    candidateCount: completeSnapshot?.sections.candidates.candidate_count,
    triggerLabel: latestAttempt ? TRIGGER_LABEL[latestAttempt.trigger] ?? latestAttempt.trigger : undefined,
    notice,
  };
}
