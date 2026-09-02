import { test, expect } from "@playwright/test";

/**
 * Story 1.11: 배포 후(또는 로컬 `next dev` 대상) 실행하는 contract smoke test.
 * `SMOKE_BASE_URL`이 가리키는 대상에 대해 인증 없이 확인 가능한 계약만 검증한다
 * (I/O & Edge-Case Matrix 4개 시나리오). 실행: `npm run test:smoke`
 * (예: `SMOKE_BASE_URL=http://localhost:3000 npm run test:smoke`).
 *
 * 인증이 필요한 화면(Story 1.9 `/`·`/runs` 실제 렌더링, Story 1.8 스냅샷 API 데이터)은
 * 사전 등록된 슈퍼유저 계정 자격증명 없이는 자동화할 수 없어 여기서 검증하지 않는다 --
 * spec의 Verification "Manual checks" 참고.
 */

test("미인증 상태로 오늘의 후보(/)에 접속하면 로그인으로 리다이렉트된다", async ({ page }) => {
  await page.goto("/");
  await expect(page).toHaveURL(/\/login$/);
});

test("미인증 상태로 배치 이력(/runs)에 접속하면 로그인으로 리다이렉트된다", async ({ page }) => {
  await page.goto("/runs");
  await expect(page).toHaveURL(/\/login$/);
});

test("/login은 200으로 응답하고 이메일/비밀번호 로그인 폼을 렌더링한다", async ({ page }) => {
  const cspErrors: string[] = [];
  page.on("console", (message) => {
    if (message.type() === "error" && message.text().includes("Content Security Policy")) {
      cspErrors.push(message.text());
    }
  });

  const response = await page.goto("/login");
  expect(response?.status()).toBe(200);
  await expect(page.getByRole("heading", { name: "로그인" })).toBeVisible();
  await expect(page.getByLabel("이메일")).toBeVisible();
  await expect(page.getByLabel("비밀번호")).toBeVisible();
  await expect(page.getByRole("button", { name: "로그인" })).toBeVisible();
  expect(cspErrors).toEqual([]);
});

test("시크릿 헤더 없이 /api/dispatch/worker를 호출하면 401을 반환한다(route가 살아있고 게이트가 걸림을 증명)", async ({
  request,
}) => {
  const response = await request.post("/api/dispatch/worker", { data: {} });
  expect(response.status()).toBe(401);
});
