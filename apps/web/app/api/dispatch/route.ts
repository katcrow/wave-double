import { NextResponse, type NextRequest } from "next/server";
import type { BatchKind } from "@/lib/dashboard-types";
import { CSRF_COOKIE_NAME, CSRF_HEADER_NAME } from "@/lib/csrf-constants";
import { hashDispatchPayload, isValidLogicalRunKey, validateCsrf } from "@/lib/dispatch";
import { isAllowedOperator } from "@/lib/auth-allowlist";
import { verifyJwt, JwtVerificationError } from "@/lib/jwt-verify";
import { RateLimiter } from "@/lib/rate-limit";
import { getSupabaseServiceClient } from "@/lib/supabase-service";

/**
 * Story 1.10 (AD-7/AD-18): 인증된 수동 실행 POST.
 * JWKS 서명/issuer/audience/expiry/sub 검증 -> allowlist -> CSRF -> rate limit을 모두 통과해야
 * `request_manual_dispatch` RPC(단일 트랜잭션)로 dispatch_request+dispatch_outbox를 생성한다.
 */
export const dynamic = "force-dynamic";

const BATCH_KINDS: readonly BatchKind[] = ["premarket", "intraday", "close"];
// 단일 운영자 전제(Never: 새 의존성 금지) 하의 in-memory rate limit. 분당 최대 5회.
const rateLimiter = new RateLimiter(5, 60_000);

interface DispatchRequestBody {
  idempotency_key?: unknown;
  logical_run_key?: unknown;
  trading_day?: unknown;
  batch_kind?: unknown;
}

function isNonEmptyString(value: unknown): value is string {
  return typeof value === "string" && value.trim().length > 0;
}

export async function POST(request: NextRequest) {
  const jwksUrl = process.env.SUPABASE_JWKS_URL;
  const issuer = process.env.SUPABASE_JWT_ISSUER;
  if (!jwksUrl || !issuer) {
    return NextResponse.json({ error: "SERVER_MISCONFIGURED" }, { status: 500 });
  }

  const authHeader = request.headers.get("authorization");
  const token = authHeader?.startsWith("Bearer ") ? authHeader.slice("Bearer ".length) : null;
  if (!token) {
    return NextResponse.json({ error: "UNAUTHENTICATED" }, { status: 401 });
  }

  let claims: Awaited<ReturnType<typeof verifyJwt>>;
  try {
    claims = await verifyJwt(token, { jwksUrl, issuer, audience: "authenticated" });
  } catch (error) {
    if (error instanceof JwtVerificationError) {
      // JWKS_FETCH_FAILED는 세션이 유효하지 않다는 뜻이 아니라 인증 인프라 자체가 응답하지 않는다는
      // 뜻이다 -- 401(재로그인 유도)로 뭉뚱그리면 운영자가 잘못된 진단(세션 만료)을 하게 된다.
      const status = error.code === "JWKS_FETCH_FAILED" ? 503 : 401;
      return NextResponse.json({ error: error.code }, { status });
    }
    return NextResponse.json({ error: "UNAUTHENTICATED" }, { status: 401 });
  }

  const subjectEmail = typeof claims.email === "string" ? claims.email : null;
  if (!isAllowedOperator(subjectEmail)) {
    return NextResponse.json({ error: "FORBIDDEN_NOT_ALLOWLISTED" }, { status: 403 });
  }

  const cookieValue = request.cookies.get(CSRF_COOKIE_NAME)?.value ?? null;
  const headerValue = request.headers.get(CSRF_HEADER_NAME);
  if (!validateCsrf(cookieValue, headerValue)) {
    return NextResponse.json({ error: "CSRF_VALIDATION_FAILED" }, { status: 403 });
  }

  let body: DispatchRequestBody;
  try {
    body = (await request.json()) as DispatchRequestBody;
  } catch {
    return NextResponse.json({ error: "INVALID_BODY" }, { status: 400 });
  }

  const { idempotency_key: idempotencyKey, logical_run_key: logicalRunKey, trading_day: tradingDay, batch_kind: batchKind } = body;

  if (
    !isNonEmptyString(idempotencyKey) ||
    !isNonEmptyString(logicalRunKey) ||
    !isNonEmptyString(tradingDay) ||
    !isNonEmptyString(batchKind) ||
    !BATCH_KINDS.includes(batchKind as BatchKind) ||
    !isValidLogicalRunKey(batchKind, logicalRunKey)
  ) {
    return NextResponse.json({ error: "INVALID_DISPATCH_REQUEST" }, { status: 400 });
  }

  // rate limit은 요청이 형식적으로 유효하다고 판정된 뒤에만 소비한다 -- 그렇지 않으면 CSRF 재발급
  // 지연이나 클라이언트 버그로 인한 잘못된 요청들이 정상 요청의 슬롯까지 잠식해, 정작 장애 대응
  // 중인 단일 운영자가 스스로를 잠그게 된다.
  const rateLimitResult = rateLimiter.check(claims.sub);
  if (!rateLimitResult.allowed) {
    return NextResponse.json(
      { error: "RATE_LIMITED" },
      { status: 429, headers: { "Retry-After": String(Math.ceil(rateLimitResult.retryAfterMs / 1000)) } }
    );
  }

  // 클라이언트가 보낸 hash는 절대 신뢰하지 않는다 -- 서버가 canonical 필드에서 직접 계산한다.
  const payloadHash = hashDispatchPayload({
    logical_run_key: logicalRunKey,
    trading_day: tradingDay,
    batch_kind: batchKind,
  });

  let data: { status?: string; dispatch_request_id?: string; outbox_id?: string; reason?: string; run_id?: string; started_at?: string; trigger?: string } | null;
  let error: { message: string } | null;
  try {
    const supabase = getSupabaseServiceClient();
    ({ data, error } = await supabase.rpc("request_manual_dispatch", {
      p_idempotency_key: idempotencyKey,
      p_payload_hash: payloadHash,
      p_requested_by: subjectEmail,
      p_logical_run_key: logicalRunKey,
      p_trading_day: tradingDay,
      p_batch_kind: batchKind,
    }));
  } catch (thrown) {
    // 서비스 클라이언트 생성(환경변수 누락) 또는 rpc() 자체의 네트워크 예외 -- route의 JSON 에러
    // 계약을 지켜 Next.js 기본 HTML 500 페이지 대신 구조화된 응답을 낸다.
    console.error(`request_manual_dispatch threw: ${thrown instanceof Error ? thrown.message : "unknown error"}`);
    return NextResponse.json({ error: "DISPATCH_REQUEST_FAILED" }, { status: 500 });
  }

  if (error) {
    if (error.message === "IDEMPOTENCY_KEY_CONFLICT") {
      return NextResponse.json({ error: "IDEMPOTENCY_KEY_CONFLICT" }, { status: 409 });
    }
    if (error.message === "TRADING_DAY_MISMATCH") {
      return NextResponse.json({ error: "TRADING_DAY_MISMATCH" }, { status: 400 });
    }
    return NextResponse.json({ error: "DISPATCH_REQUEST_FAILED" }, { status: 500 });
  }

  if (data?.status === "conflict") {
    return NextResponse.json(
      {
        error: data.reason ?? "ACTIVE_ATTEMPT",
        run_id: data.run_id,
        started_at: data.started_at,
        trigger: data.trigger,
      },
      { status: 409 }
    );
  }

  return NextResponse.json(
    { dispatch_request_id: data?.dispatch_request_id, status: data?.status, reason: data?.reason },
    { status: 202 }
  );
}
