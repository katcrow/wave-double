import { test, expect } from "@playwright/test";

test("인증된 후보·근거·시장·필터 표면은 반응형 fixture에서 동작한다", async ({ page }) => {
  await page.goto("/login");
  await page.getByLabel("이메일").fill("neo@example.test");
  await page.getByLabel("비밀번호").fill("fixture-password");
  await page.getByRole("button", { name: "로그인" }).click();

  await expect(page).toHaveURL(/\/$/);
  await expect(page.getByRole("heading", { name: "조정후보" })).toBeVisible();

  await page.getByRole("button", { name: "근거 보기" }).click();
  const evidence = page.getByRole("region", { name: "후보 근거 패널" });
  await expect(evidence).toBeVisible();
  await expect(evidence).toContainText("종가·등락률 수정주가");
  await expect(evidence).toContainText("71,000");

  await page.getByRole("checkbox", { name: "좋은 수급" }).check();
  await expect(page.locator(".candidate-filter__result-count")).toContainText("필터 결과 1건");

  await page.getByRole("tab", { name: "KOSDAQ" }).click();
  await expect(page).toHaveURL(/market=KOSDAQ/);
  await expect(page.getByRole("tab", { name: "KOSDAQ" })).toHaveAttribute("aria-selected", "true");

  await page.setViewportSize({ width: 1280, height: 900 });
  await expect(page.locator(".candidate-evidence-table")).toBeVisible();
  await page.setViewportSize({ width: 375, height: 812 });
  await expect(page.locator(".candidate-evidence-card-list")).toBeVisible();
  await page.evaluate(() => { document.documentElement.style.zoom = "200%"; });
  await expect(page.locator(".candidate-evidence-card-list")).toBeVisible();
});
