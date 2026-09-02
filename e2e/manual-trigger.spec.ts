import { test, expect } from "@playwright/test";

/**
 * Story 1.10: 인증된 세션에서의 수동 실행 버튼 활성화 -> `/api/dispatch` 요청 흐름은 실제
 * Supabase Auth 슈퍼유저 계정(사전 등록, 비밀번호 로그인)이 있어야 검증할 수 있어 CI에서
 * 자동화할 수 없다(별도 테스트 계정을 만들지 않는 한). 그 케이스는 spec의 Verification
 * "Manual checks"로 옮겼다: 실제 Supabase 프로젝트에 migration을 적용한 뒤 브라우저로
 * 로그인해 버튼이 활성화되는지, `curl`로 `request_manual_dispatch`를 중복 호출해 replay/409
 * 응답을 확인한다.
 *
 * 여기서는 CI에서 자동 검증 가능한 범위 -- 로그인 폼 자체의 렌더링과 미인증 상태에서 워커
 * 라우트가 `/login`으로 리다이렉트되지 않는지(cron 전용 경로 제외 확인) -- 만 검증한다.
 */

test("로그인 폼이 렌더링되고 이메일/비밀번호 제출 UI를 제공한다", async ({ page }) => {
  await page.goto("/login");
  await expect(page.getByRole("heading", { name: "로그인" })).toBeVisible();
  await expect(page.getByLabel("이메일")).toBeVisible();
  await expect(page.getByLabel("비밀번호")).toBeVisible();
  await expect(page.getByRole("button", { name: "로그인" })).toBeVisible();
});

test("cron 전용 outbox worker 라우트는 인증 없이도 시크릿 검증 단계까지 도달한다(리다이렉트되지 않는다)", async ({ request }) => {
  const response = await request.post("/api/dispatch/worker", { data: {} });
  // proxy.ts의 세션 리다이렉트 대상에서 제외됐는지만 확인한다 -- 302가 아니라 401(시크릿 불일치)이어야 한다.
  expect(response.status()).toBe(401);
});
