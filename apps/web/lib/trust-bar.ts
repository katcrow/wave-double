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
   * 비차단 Toast/notice 문구(실패/부분성공/stale/수동 실행 거부·실패에서만 채워짐).
   * 폴백 원천 사용은 스펙 Never 절에 따라 판정 근거(원천 필드)가 없어 이 알림에 포함하지 않는다.
   */
  notice: string | null;
}

/** Story 1.10: DataTrustBar가 클라이언트에서 진행 중인 수동 실행 요청의 로컬 상태. */
export interface DispatchUiState {
  phase: "idle" | "pending" | "conflict" | "error";
  message?: string;
}

/**
 * close 배치만 publish_attempt를 호출해 complete_snapshot을 갱신한다(scheduler.py, Story 3.5) --
 * intraday/premarket은 태그·outcome tracking만 갱신하고 스냅샷을 다시 발행하지 않는다. 그 결과
 * "마지막 배치"를 complete_snapshot.published_at만으로 판단하면, close보다 최근에 끝난
 * intraday 성공을 무시하고 하루 종일 그날 아침 close 시각만 보여주게 된다(2026-09-14, 20분
 * 간격 intraday 전환 후 발견). latest_attempt가 종결(published/ready_to_publish)됐고
 * complete_snapshot보다 최근이면 그쪽을 "마지막 배치"로 우선한다.
 */
function mostRecentSuccessfulBatch(
  snapshot: DashboardSnapshot
): { timestamp: string; batchKind: string } | null {
  const { latest_attempt: latestAttempt, complete_snapshot: completeSnapshot } = snapshot;
  const attemptTimestamp =
    latestAttempt &&
    (latestAttempt.status === "published" || latestAttempt.status === "ready_to_publish") &&
    latestAttempt.finished_at
      ? latestAttempt.finished_at
      : null;
  const snapshotTimestamp = completeSnapshot?.published_at ?? null;

  if (attemptTimestamp && (!snapshotTimestamp || new Date(attemptTimestamp) > new Date(snapshotTimestamp))) {
    return { timestamp: attemptTimestamp, batchKind: latestAttempt!.batch_kind };
  }
  if (snapshotTimestamp) {
    return { timestamp: snapshotTimestamp, batchKind: completeSnapshot!.batch_kind };
  }
  return null;
}

/**
 * Story 1.9 I/O 매트릭스 6개 상태(스냅샷 없음/정상 발행/실패/부분성공/휴장일 스킵/stale)를 판정한다.
 * Design Notes: freshness 기준 시각은 마지막 성공 배치(close 발행 또는 intraday/premarket 종결
 * 중 더 최근인 쪽, mostRecentSuccessfulBatch), 없으면 latest_attempt.finished_at ?? started_at이며
 * 60분 이상 경과 시 stale.
 * Story 1.10: `dispatch` 인자가 idle이 아니면 수동 실행 진행/거부 문구가 배치 상태 문구를 덮는다.
 */
export function deriveTrustBarState(snapshot: DashboardSnapshot, dispatch?: DispatchUiState, focusStage?: string): TrustBarState {
  const { latest_attempt: latestAttempt, complete_snapshot: completeSnapshot } = snapshot;
  const recentSuccess = mostRecentSuccessfulBatch(snapshot);

  const referenceTimestamp =
    recentSuccess?.timestamp ??
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
  } else if (recentSuccess) {
    const label = BATCH_KIND_LABEL[recentSuccess.batchKind] ?? "배치 확정";
    statusLine = `${label} · ${formatKstTime(recentSuccess.timestamp)} KST`;
  } else {
    statusLine = "상태 없음";
  }

  if (stale && referenceTimestamp) {
    statusLine += ` · 데이터가 60분 이상 오래됨 (${formatKstDateTime(referenceTimestamp)})`;
  }

  const focusedStageStatus = focusStage ? latestAttempt?.stage_status?.[focusStage] : undefined;
  if (focusedStageStatus === "failed") {
    statusLine = `성과 검증 단계 실패 · ${completeSnapshot ? `마지막 성공 ${formatKstDateTime(completeSnapshot.published_at)}` : "이전 성공 없음"}`;
  } else if (focusedStageStatus === "partial") {
    statusLine = `성과 검증 단계 부분성공 · 미처리 ${latestAttempt?.unprocessed_count ?? 0}건`;
  }

  let notice: string | null = null;
  if (latestAttempt?.status === "failed" || latestAttempt?.status === "partial") {
    notice = statusLine;
  } else if (stale) {
    notice = `데이터가 60분 이상 오래됨 (${referenceTimestamp ? formatKstDateTime(referenceTimestamp) : "-"})`;
  }
  if (focusedStageStatus === "failed" || focusedStageStatus === "partial") notice = statusLine;

  // Story 1.10: 수동 실행 진행/거부/실패는 배치 상태 문구보다 우선해 사용자에게 즉시 보인다.
  if (dispatch?.phase === "pending") {
    statusLine = "수동 실행 요청 처리 중...";
  } else if (dispatch?.phase === "conflict") {
    statusLine = `수동 실행 거부됨 · ${dispatch.message ?? "이미 실행 중인 배치가 있습니다."}`;
    notice = statusLine;
  } else if (dispatch?.phase === "error") {
    statusLine = `수동 실행 실패 · ${dispatch.message ?? "잠시 후 다시 시도해 주세요."}`;
    notice = statusLine;
  }

  return {
    statusLine,
    stale,
    candidateCount: completeSnapshot?.sections.candidates.candidate_count,
    triggerLabel: latestAttempt ? TRIGGER_LABEL[latestAttempt.trigger] ?? latestAttempt.trigger : undefined,
    notice,
  };
}
