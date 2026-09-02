import { test, expect } from "@playwright/test";

test("오늘의 후보 홈 라우트가 렌더링된다", async ({ page }) => {
  await page.goto("/");
  await expect(page.getByRole("heading", { name: "오늘의 후보" })).toBeVisible();
  await expect(page.getByText("오늘 태깅된 후보가 없습니다.")).toBeVisible();
  await expect(page.getByRole("status").first()).toBeVisible();
});

test("배치 이력 라우트가 렌더링된다", async ({ page }) => {
  await page.goto("/runs");
  await expect(page.getByRole("heading", { name: "배치 이력" })).toBeVisible();
});
