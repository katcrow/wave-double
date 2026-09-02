import { test, expect } from "@playwright/test";

// Story 1.10: `/`와 `/runs`는 이제 보호 라우트다(AD-7). 미인증 세션은 `/login`으로 리다이렉트된다.
// 인증된 세션에서의 렌더링 확인은 e2e/manual-trigger.spec.ts와 spec의 Verification "Manual
// checks"를 참고한다(실제 로그인 세션 발급은 CI에서 자동화할 수 없다).
//
// Story 2.7: 카드 그리드/빈 상태(태깅 후보 유무에 따른 분기)도 같은 이유로 인증된 세션이 필요해
// 여기서는 자동화하지 않는다 -- spec-2-7의 Verification "Manual checks"에서 실제 Supabase
// 프로젝트로 확인한다. 카드 뷰모델 계산 자체의 회귀 방지는 lib/candidate-cards.test.ts가 담당한다.

test("미인증 상태로 오늘의 후보에 접속하면 로그인으로 리다이렉트된다", async ({ page }) => {
  await page.goto("/");
  await expect(page).toHaveURL(/\/login$/);
  await expect(page.getByRole("heading", { name: "로그인" })).toBeVisible();
});

test("미인증 상태로 배치 이력에 접속하면 로그인으로 리다이렉트된다", async ({ page }) => {
  await page.goto("/runs");
  await expect(page).toHaveURL(/\/login$/);
});
