import { createHash, randomUUID, timingSafeEqual } from "node:crypto";

/**
 * Story 1.10 (AD-18): dispatch route가 신뢰하는 canonical payload hash와 CSRF 비교 순수 함수.
 * server-only(`node:crypto`) 모듈이므로 클라이언트 컴포넌트에서 import하지 않는다
 * (브라우저 측 idempotency key 생성은 `crypto.randomUUID()`를 직접 쓴다).
 */

export interface DispatchPayload {
  logical_run_key: string;
  trading_day: string;
  batch_kind: string;
}

/** 서버가 직접 계산하는 canonical payload hash. 클라이언트가 보낸 hash는 절대 신뢰하지 않는다. */
export function hashDispatchPayload(payload: DispatchPayload): string {
  const canonical = JSON.stringify({
    batch_kind: payload.batch_kind,
    logical_run_key: payload.logical_run_key,
    trading_day: payload.trading_day,
  });
  return createHash("sha256").update(canonical, "utf8").digest("hex");
}

export function generateCsrfToken(): string {
  return randomUUID();
}

/**
 * SameSite=Strict double-submit CSRF 검증: 쿠키 값과 헤더 값이 모두 있어야 하고, 길이가 같아야
 * `timingSafeEqual`을 호출할 수 있다(길이가 다르면 던지므로 먼저 길이를 비교한다).
 */
export function validateCsrf(
  cookieValue: string | null | undefined,
  headerValue: string | null | undefined
): boolean {
  if (!cookieValue || !headerValue) return false;
  const cookieBuffer = Buffer.from(cookieValue, "utf8");
  const headerBuffer = Buffer.from(headerValue, "utf8");
  if (cookieBuffer.length !== headerBuffer.length) return false;
  return timingSafeEqual(cookieBuffer, headerBuffer);
}

const LOGICAL_RUN_KEY_PATTERNS: Record<string, RegExp> = {
  intraday: /^intraday:\d{4}-\d{2}-\d{2}:([01]\d|2[0-3]):(00|30)$/,
  premarket: /^premarket:\d{4}-\d{2}-\d{2}$/,
  close: /^close:\d{4}-\d{2}-\d{2}$/,
};

/** SQL의 `start_attempt`/`request_manual_dispatch`와 같은 shape 검증(RPC 이전 조기 거부용). */
export function isValidLogicalRunKey(batchKind: string, logicalRunKey: string): boolean {
  const pattern = LOGICAL_RUN_KEY_PATTERNS[batchKind];
  return pattern ? pattern.test(logicalRunKey) : false;
}

export function timingSafeEqualStrings(a: string | null | undefined, b: string | null | undefined): boolean {
  if (!a || !b) return false;
  const bufferA = Buffer.from(a, "utf8");
  const bufferB = Buffer.from(b, "utf8");
  if (bufferA.length !== bufferB.length) return false;
  return timingSafeEqual(bufferA, bufferB);
}
