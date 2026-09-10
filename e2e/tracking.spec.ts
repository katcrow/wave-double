import { test, expect, type Page } from "@playwright/test";

async function signIn(page: Page) {
  await page.goto("/login");
  await page.getByLabel("이메일").fill("neo@example.test");
  await page.getByLabel("비밀번호").fill("fixture-password");
  await page.getByRole("button", { name: "로그인" }).click();
  await expect(page).toHaveURL(/\/$/);
}

test.beforeEach(async ({ request }) => {
  await request.post("http://127.0.0.1:54321/__e2e/scenario", { data: { scenario: "default" } });
});

test("미인증 상태로 tracking에 접속하면 로그인으로 리다이렉트된다", async ({ page }) => {
  await page.goto("/tracking");
  await expect(page).toHaveURL(/\/login$/);
});

test("인증된 tracking 라우트는 trust bar와 6개 상태를 표시한다", async ({ page }) => {
  await signIn(page);
  await page.goto("/tracking");

  await expect(page.getByRole("heading", { name: "성과 검증" })).toBeVisible();
  await expect(page.getByText("데이터 신뢰도")).toBeVisible();
  await expect(page.getByRole("heading", { name: "Outcome tracking" })).toBeVisible();
  for (const status of ["TP", "SL", "TIMEOUT", "OPEN", "SUSPENDED", "DELISTED"]) {
    await expect(page.locator(`.outcome-tracking__status--${status.toLowerCase()}`).first()).toBeVisible();
  }
  await expect(page.locator(".outcome-tracking__summary")).toContainText("진행 중 1건");
  await expect(page.getByText("아직 종결되지 않은 진행 중 outcome입니다.").first()).toBeVisible();
  for (const [status, description] of [
    ["TP", "목표 수익률에 도달해 종결되었습니다."],
    ["SL", "손절 기준에 도달해 종결되었습니다."],
    ["TIMEOUT", "정해진 보유 기간이 지나 종결되었습니다."],
    ["SUSPENDED", "가격 조정 이상으로 판정을 보류했습니다."],
    ["DELISTED", "상장폐지로 추적을 종료했습니다."],
  ] as const) {
    await expect(page.locator(`.outcome-tracking__status--${status.toLowerCase()}`).first()).toHaveText(status);
    await expect(page.getByText(description).first()).toBeVisible();
  }
  const firstRow = page.locator(".outcome-tracking__table tbody tr").first();
  await expect(firstRow).toContainText("005930");
  await expect(firstRow).toContainText("전략 A");
  await expect(firstRow).toContainText("2026.09.09");
  await expect(firstRow).toContainText("2026.09.12");
  await expect(firstRow).toContainText("+2.90%");
});

test("tracking 필터는 query string과 결과를 보존한다", async ({ page }) => {
  await signIn(page);
  await page.goto("/tracking");

  await page.getByLabel("상태").selectOption("OPEN");
  await page.getByLabel("전략").selectOption("D");
  await page.getByLabel("Ticker").fill("051910");
  await page.getByRole("button", { name: "필터 적용" }).click();

  await expect(page).toHaveURL(/\/tracking\?status=OPEN&strategy=D&ticker=051910/);
  await expect(page.locator(".outcome-tracking__table tbody tr")).toHaveCount(1);
  await expect(page.locator(".outcome-tracking__table tbody")).toContainText("051910");
  await expect(page.locator(".outcome-tracking__table tbody")).toContainText("전략 D");
  await expect(page.getByLabel("상태")).toHaveValue("OPEN");
  await expect(page.getByLabel("전략")).toHaveValue("D");
  await page.reload();
  await expect(page.getByLabel("전략")).toHaveValue("D");
  await expect(page.locator(".outcome-tracking__table tbody tr")).toHaveCount(1);
  await page.goBack();
  await expect(page).toHaveURL(/\/tracking$/);
  await page.getByRole("link", { name: "초기화" }).click();
  await expect(page).toHaveURL(/\/tracking$/);
});

test("tracking은 잘못된 query 필터를 전체 조회로 정규화한다", async ({ page }) => {
  await signIn(page);
  await page.goto("/tracking?status=UNKNOWN&strategy=G&ticker=%3Cscript%3E");
  await expect(page.getByLabel("상태")).toHaveValue("");
  await expect(page.getByLabel("전략")).toHaveValue("");
  await expect(page.getByLabel("Ticker")).toHaveValue("");
  await expect(page.locator(".outcome-tracking__table tbody tr")).toHaveCount(6);
});

test("tracking은 빈 결과와 RPC 오류를 구분한다", async ({ page, request }) => {
  await signIn(page);
  await request.post("http://127.0.0.1:54321/__e2e/scenario", { data: { scenario: "tracking-empty" } });
  await page.goto("/tracking");
  await expect(page.locator(".outcome-tracking__state")).toContainText("추적 중인 outcome이 없습니다.");

  await request.post("http://127.0.0.1:54321/__e2e/scenario", { data: { scenario: "tracking-error" } });
  await page.reload();
  await expect(page.locator(".outcome-tracking__state[role='alert']")).toContainText("Outcome 데이터를 불러오지 못했습니다");

  await request.post("http://127.0.0.1:54321/__e2e/scenario", { data: { scenario: "tracking-malformed" } });
  await page.reload();
  await expect(page.locator(".outcome-tracking__state[role='alert']")).toContainText("Outcome 데이터를 불러오지 못했습니다");
});

test("tracking은 좁은 화면에서 table을 읽기 가능한 카드로 전환한다", async ({ page }) => {
  await signIn(page);
  await page.goto("/tracking");
  await page.setViewportSize({ width: 1280, height: 900 });
  await expect(page.locator(".outcome-tracking__table")).toBeVisible();
  await page.setViewportSize({ width: 375, height: 812 });
  await expect(page.locator(".outcome-tracking__table")).toBeHidden();
  await expect(page.locator(".outcome-tracking__cards")).toBeVisible();
  await expect(page.locator(".outcome-tracking__card")).toHaveCount(6);
});
