/**
 * Story 1.10 후속: outbox worker(`app/api/dispatch/worker/route.ts`)의 재시도/dead-letter 판단
 * 로직을 순수 함수로 추출한다. 이 스토리의 다른 모든 신규 로직(JWT/CSRF/rate-limit/allowlist/
 * idempotency)은 전부 `lib/*.ts`로 추출돼 단위 테스트를 갖췄지만, "무한 재시도 금지"라는 이 스토리의
 * 핵심 불변식을 구현하는 이 결정 로직만 route.ts에 인라인으로 남아 테스트가 없었다.
 */

export const MAX_DISPATCH_ATTEMPTS = 5;
/**
 * accepted(receipt 폴링) 단계는 queued(dispatch 재시도) 단계보다 훨씬 긴 예산을 준다 --
 * GitHub Actions의 정상적인 콜드스타트/큐잉 시간이 queued 단계의 재시도 상한과 같은 수준이면
 * 실제로는 살아있는 배치가 dead_letter로 오탐될 수 있기 때문이다(1분 tick당 최대 120초 lease 기준
 * 약 1시간 예산).
 */
export const MAX_RECEIPT_ATTEMPTS = 30;

export interface OutboxAttemptState {
  status: "queued" | "accepted" | "started";
  attempts: number;
}

export type OutboxDecision =
  | { action: "dead_letter"; reasonCode: "ATTEMPTS_EXHAUSTED" | "RECEIPT_TIMEOUT" }
  | { action: "dispatch" }
  | { action: "await_receipt" }
  | { action: "noop" };

/** claim 시점의 상태/attempts만으로 다음 행동을 결정한다(Boundaries: 무한 재시도 금지). */
export function decideOutboxAction(row: OutboxAttemptState): OutboxDecision {
  if (row.status === "queued") {
    if (row.attempts > MAX_DISPATCH_ATTEMPTS) {
      return { action: "dead_letter", reasonCode: "ATTEMPTS_EXHAUSTED" };
    }
    return { action: "dispatch" };
  }
  if (row.status === "accepted") {
    if (row.attempts > MAX_RECEIPT_ATTEMPTS) {
      return { action: "dead_letter", reasonCode: "RECEIPT_TIMEOUT" };
    }
    return { action: "await_receipt" };
  }
  return { action: "noop" };
}

/** queued 상태에서 GitHub dispatch 호출 자체가 실패했을 때, 이번에 dead_letter로 닫을지 결정한다. */
export function shouldDeadLetterAfterDispatchFailure(attempts: number): boolean {
  return attempts >= MAX_DISPATCH_ATTEMPTS;
}
