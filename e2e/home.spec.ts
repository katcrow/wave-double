import { test, expect } from "@playwright/test";

test("web 스캐폴드 홈 라우트가 렌더링된다", async ({ page }) => {
  await page.goto("/");
  await expect(page.getByRole("heading", { name: "wave-double" })).toBeVisible();
  await expect(page.getByText("매수후보 추천 대시보드")).toBeVisible();
});
