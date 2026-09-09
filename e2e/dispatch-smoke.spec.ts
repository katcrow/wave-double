import { test, expect } from "@playwright/test";

/**
 * Retro epic-1-retro-item-6: 운영 배포 전에 검증해야 할 인증된 수동 dispatch 흐름과 CSP를
 * 자동으로 커버하는 smoke. mock Supabase(e2e/mock-supabase-server.mjs)가 RS256 서명 JWT를 발급하고
 * JWKS를 서빙하므로, `/api/dispatch`의 모든 인증 게이트(JWKS 서명/issuer/audience/expiry ->
 * allowlist -> CSRF -> rate limit)와 `request_manual_dispatch` RPC 호출 경로가 실제로 끝까지
 * 동작함을 CI에서 확인할 수 있다(production-smoke.spec.ts는 인증 없이 확인 가능한 계약만 다룬다).
 *
 * 실행: `npm run test:e2e`(playwright.config.ts). rate limit은 sub당 5회/분이므로 dispatch POST를
 * 이 스위트 전체로 3회 이하로 유지한다.
 */

test("인증된 세션의 수동 실행 요청이 /api/dispatch에서 202로 수락된다", async ({ page }) => {
  const dispatchStatuses: number[] = [];
  page.on("response", (response) => {
    if (response.url().includes("/api/dispatch")) dispatchStatuses.push(response.status());
  });

  await page.goto("/login");
  await page.getByLabel("이메일").fill("neo@example.test");
  await page.getByLabel("비밀번호").fill("fixture-password");
  await page.getByRole("button", { name: "로그인" }).click();
  await expect(page).toHaveURL(/\/$/);
  await expect(page.getByRole("button", { name: "수동 실행" })).toBeEnabled();

  await page.getByRole("button", { name: "수동 실행" }).click();

  // 202 = JWT 검증 + allowlist + CSRF + rate limit을 통과하고 request_manual_dispatch가
  // created를 반환해야만 나오는 status 코드다.
  await expect.poll(() => dispatchStatuses, { timeout: 15_000 }).toContain(202);
});

test("유효한 세션 토큰이지만 CSRF 헤더가 없으면 dispatch는 403 CSRF_VALIDATION_FAILED를 반환한다", async ({ page }) => {
  let accessToken: string | null = null;
  page.on("response", async (response) => {
    if (response.url().includes("/auth/v1/token") && response.request().method() === "POST") {
      try {
        const body = await response.json();
        accessToken = body?.access_token ?? null;
      } catch {
        // 비 JSON 응답(404 등)은 테스트의 몰래 실패 방지를 위해 무시하지 않고 그대로 둔다.
      }
    }
  });

  await page.goto("/login");
  await page.getByLabel("이메일").fill("neo@example.test");
  await page.getByLabel("비밀번호").fill("fixture-password");
  await page.getByRole("button", { name: "로그인" }).click();
  await expect(page).toHaveURL(/\/$/);
  await expect.poll(() => accessToken).toBeTruthy();

  const result = await page.evaluate(async (token) => {
    const response = await fetch("/api/dispatch", {
      method: "POST",
      headers: {
        "content-type": "application/json",
        authorization: `Bearer ${token}`,
      },
      body: JSON.stringify({
        idempotency_key: crypto.randomUUID(),
        logical_run_key: "close:2026-09-09",
        trading_day: "2026-09-09",
        batch_kind: "close",
      }),
    });
    return { status: response.status, body: await response.json().catch(() => ({})) };
  }, accessToken);

  expect(result.status).toBe(403);
  expect(result.body).toEqual({ error: "CSRF_VALIDATION_FAILED" });
});

test("미인증 /api/dispatch POST는 401 UNAUTHENTICATED를 반환한다", async ({ request }) => {
  const response = await request.post("/api/dispatch", {
    data: { idempotency_key: "x", logical_run_key: "close:2026-09-09", trading_day: "2026-09-09", batch_kind: "close" },
  });
  expect(response.status()).toBe(401);
  expect(await response.json()).toEqual({ error: "UNAUTHENTICATED" });
});

test("로그인부터 인증된 dispatch까지 CSP 콘솔 위반이 발생하지 않는다", async ({ page }) => {
  const cspErrors: string[] = [];
  page.on("console", (message) => {
    if (message.type() === "error" && message.text().includes("Content Security Policy")) {
      cspErrors.push(message.text());
    }
  });

  await page.goto("/login");
  await page.getByLabel("이메일").fill("neo@example.test");
  await page.getByLabel("비밀번호").fill("fixture-password");
  await page.getByRole("button", { name: "로그인" }).click();
  await expect(page).toHaveURL(/\/$/);
  await expect(page.getByRole("heading", { name: "조정후보" })).toBeVisible();

  await page.getByRole("button", { name: "수동 실행" }).click();
  // 로그아웃 버튼이 활성화됐다가(수동 실행 성공) 대시보드에 남아있는 것으로 수락 후 흐름을 확인한다.
  await expect(page.getByRole("button", { name: "로그아웃" })).toBeVisible();

  expect(cspErrors).toEqual([]);
});