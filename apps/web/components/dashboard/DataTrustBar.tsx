"use client";

import { useCallback, useEffect, useRef, useState } from "react";
import { useRouter } from "next/navigation";
import type { BatchKind, DashboardSnapshot } from "@/lib/dashboard-types";
import { deriveTrustBarState, type DispatchUiState } from "@/lib/trust-bar";
import { CSRF_COOKIE_NAME, CSRF_HEADER_NAME } from "@/lib/csrf-constants";
import { getSupabaseAuthBrowserClient } from "@/lib/supabase-browser-auth";

/**
 * Story 1.9 I/O 매트릭스 6개 상태(스냅샷 없음/정상 발행/실패/부분성공/휴장일 스킵/stale)를 렌더링한다.
 * Story 1.10: 버튼 클릭 시 인증된 세션의 access_token + double-submit CSRF 토큰으로 `/api/dispatch`를
 * 호출한다. 상태 판정 로직은 `lib/trust-bar.ts`의 순수 함수로 분리해 단위 테스트한다.
 */

function readCookie(name: string): string | null {
  if (typeof document === "undefined") return null;
  const match = document.cookie.match(new RegExp(`(?:^|; )${name}=([^;]*)`));
  return match ? decodeURIComponent(match[1]) : null;
}

function todayKstDateString(): string {
  const parts = new Intl.DateTimeFormat("en-CA", {
    timeZone: "Asia/Seoul",
    year: "numeric",
    month: "2-digit",
    day: "2-digit",
  }).formatToParts(new Date());
  const lookup = Object.fromEntries(parts.map((part) => [part.type, part.value]));
  return `${lookup.year}-${lookup.month}-${lookup.day}`;
}

/**
 * Boundaries "Always": 재실행 대상 batch_kind/logical_run_key는 `latest_attempt`에서 도출한다
 * (하드코딩 금지). `latest_attempt`가 없을 때만 오늘 날짜의 `close`로 대체한다.
 */
function deriveManualDispatchTarget(
  snapshot: DashboardSnapshot
): { batchKind: BatchKind; logicalRunKey: string; tradingDay: string } {
  const attempt = snapshot.latest_attempt;
  if (attempt) {
    return {
      batchKind: attempt.batch_kind,
      logicalRunKey: attempt.logical_run_key,
      tradingDay: attempt.trading_day,
    };
  }
  const today = todayKstDateString();
  return { batchKind: "close", logicalRunKey: `close:${today}`, tradingDay: today };
}

const POST_DISPATCH_POLL_INTERVAL_MS = 10_000;
const POST_DISPATCH_POLL_MAX_TICKS = 12; // ~2분

export default function DataTrustBar({ snapshot }: { snapshot: DashboardSnapshot }) {
  const [dispatchState, setDispatchState] = useState<DispatchUiState>({ phase: "idle" });
  const idempotencyKeyRef = useRef<string | null>(null);
  const router = useRouter();
  const pollTimerRef = useRef<ReturnType<typeof setInterval> | null>(null);

  const { statusLine, candidateCount, triggerLabel } = deriveTrustBarState(snapshot, dispatchState);

  useEffect(() => {
    return () => {
      if (pollTimerRef.current) clearInterval(pollTimerRef.current);
    };
  }, []);

  /**
   * Story 1.10 후속: dispatch가 202로 수락된 뒤 UI는 outbox의 비동기 결과(실제 배치 시작/실패/
   * dead_letter)를 알 방법이 전혀 없었다. outbox 상태를 직접 노출하는 새 RPC 없이도, 대시보드
   * 스냅샷(latest_attempt/trigger)을 잠시 주기적으로 재조회하면 배치가 실제로 시작되는 순간은
   * 곧바로 반영된다 -- 완전한 신호는 아니지만(dead_letter까지는 드러내지 못한다), 페이지를 수동
   * 새로고침해야만 알 수 있던 것보다는 낫다.
   */
  const startPostDispatchPolling = useCallback(() => {
    if (pollTimerRef.current) clearInterval(pollTimerRef.current);
    let ticks = 0;
    pollTimerRef.current = setInterval(() => {
      ticks += 1;
      router.refresh();
      if (ticks >= POST_DISPATCH_POLL_MAX_TICKS && pollTimerRef.current) {
        clearInterval(pollTimerRef.current);
        pollTimerRef.current = null;
      }
    }, POST_DISPATCH_POLL_INTERVAL_MS);
  }, [router]);

  const handleSignOut = useCallback(async () => {
    // Story 1.10 후속: 세션 침해 의심 등으로 강제 로그아웃이 필요할 때 앱 안에서 할 방법이
    // 없었다 -- 단일 운영자 세션이 이 앱의 유일한 보안 경계이므로 in-product 로그아웃을 둔다.
    await fetch("/api/auth/signout", { method: "POST" });
    window.location.href = "/login";
  }, []);

  const handleManualTrigger = useCallback(async () => {
    setDispatchState({ phase: "pending" });
    try {
      const supabase = getSupabaseAuthBrowserClient();
      const {
        data: { session },
      } = await supabase.auth.getSession();
      if (!session) {
        setDispatchState({ phase: "error", message: "로그인이 필요합니다." });
        return;
      }

      const target = deriveManualDispatchTarget(snapshot);
      if (!idempotencyKeyRef.current) {
        idempotencyKeyRef.current = crypto.randomUUID();
      }
      const csrfToken = readCookie(CSRF_COOKIE_NAME);

      const response = await fetch("/api/dispatch", {
        method: "POST",
        headers: {
          "content-type": "application/json",
          authorization: `Bearer ${session.access_token}`,
          ...(csrfToken ? { [CSRF_HEADER_NAME]: csrfToken } : {}),
        },
        body: JSON.stringify({
          idempotency_key: idempotencyKeyRef.current,
          logical_run_key: target.logicalRunKey,
          trading_day: target.tradingDay,
          batch_kind: target.batchKind,
        }),
      });

      if (response.status === 202) {
        idempotencyKeyRef.current = null;
        setDispatchState({ phase: "idle" });
        startPostDispatchPolling();
        return;
      }

      const body: { error?: string } = await response.json().catch(() => ({}));
      idempotencyKeyRef.current = null;

      if (response.status === 409) {
        setDispatchState({
          phase: "conflict",
          message: body.error === "ACTIVE_ATTEMPT" ? "이미 실행 중인 배치가 있습니다." : "동일 요청이 이미 처리 중입니다.",
        });
        return;
      }

      setDispatchState({ phase: "error", message: body.error ?? "수동 실행 요청이 실패했습니다." });
    } catch {
      idempotencyKeyRef.current = null;
      setDispatchState({ phase: "error", message: "네트워크 오류로 수동 실행 요청이 실패했습니다." });
    }
  }, [snapshot, startPostDispatchPolling]);

  return (
    <div className="data-trust-bar" role="status" aria-live="polite">
      <div className="data-trust-bar__status">
        <span className="data-trust-bar__label">데이터 신뢰도</span>
        <span className="data-trust-bar__value">{statusLine}</span>
        <span className="data-trust-bar__meta">
          {triggerLabel ? `트리거 · ${triggerLabel}` : "트리거 정보 없음"}
          {typeof candidateCount === "number" && ` · 참고 · 오늘 태깅 후보 ${candidateCount}건`}
        </span>
      </div>
      <button
        type="button"
        className="data-trust-bar__manual-run"
        onClick={handleManualTrigger}
        disabled={dispatchState.phase === "pending"}
      >
        {dispatchState.phase === "pending" ? "수동 실행 요청 중..." : "수동 실행"}
      </button>
      <button type="button" className="data-trust-bar__sign-out" onClick={handleSignOut}>
        로그아웃
      </button>
    </div>
  );
}
