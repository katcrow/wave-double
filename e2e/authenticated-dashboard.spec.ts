import { test, expect } from "@playwright/test";

test.afterEach(async ({ request }) => {
  await request.post("http://127.0.0.1:54321/__e2e/scenario", { data: { scenario: "default" } });
});

test("잘못된 인증 정보는 로그인 페이지에 오류를 표시한다", async ({ page }) => {
  await page.goto("/login");
  await page.getByLabel("이메일").fill("neo@example.test");
  await page.getByLabel("비밀번호").fill("wrong-password");
  await page.getByRole("button", { name: "로그인" }).click();

  await expect(page).toHaveURL(/\/login$/);
  await expect(page.locator('p[role="alert"]')).toContainText("Invalid login credentials");
});

test("인증된 후보·근거·시장·필터 표면은 반응형 fixture에서 동작한다", async ({ page }) => {
  const documentNavigationRequests: string[] = [];
  page.on("request", (request) => {
    const url = new URL(request.url());
    if (request.method() === "GET" && url.pathname === "/" && request.isNavigationRequest()) {
      documentNavigationRequests.push(request.url());
    }
  });

  await page.goto("/login");
  await page.getByLabel("이메일").fill("neo@example.test");
  await page.getByLabel("비밀번호").fill("fixture-password");
  await page.getByRole("button", { name: "로그인" }).click();

  await expect(page).toHaveURL(/\/$/);
  await expect.poll(() => documentNavigationRequests.length).toBeGreaterThan(0);
  await expect(page.getByRole("heading", { name: "조정후보" })).toBeVisible();
  await expect(page.getByRole("heading", { name: "조정후보" })).toHaveCount(1);
  await expect(page.getByRole("heading", { name: "거래대금 상위 후보" })).toBeVisible();
  await expect(page.locator(".top-trading-candidates__item")).toHaveCount(3);
  const topCandidate = page.locator(".top-trading-candidates__item").nth(0);
  await expect(topCandidate).toContainText("조정후보");
  await expect(topCandidate.locator("dt").filter({ hasText: "거래대금" }).locator("..").locator("dd")).toHaveText("1억원");
  await expect(topCandidate.locator("dt").filter({ hasText: "당일 상승률" }).locator("..").locator("dd")).toHaveText("+2.90%");
  await expect(topCandidate.locator("dt").filter({ hasText: "주요 섹터" }).locator("..").locator("dd")).toHaveText("반도체");
  await expect(topCandidate.locator("dt").filter({ hasText: "프로그램 순매수금액" }).locator("..").locator("dd")).toHaveText("12억원");
  await expect(page.locator(".top-trading-candidates__item").nth(1)).toContainText("SK하이닉스");
  await expect(page.locator(".top-trading-candidates__item").nth(1)).toContainText("000660");
  await expect(page.locator(".top-trading-candidates__item").nth(2)).toContainText("NAVER");
  await expect(page.locator(".top-trading-candidates__item").nth(2)).toContainText("035420");

  await page.getByRole("button", { name: "근거 보기" }).click();
  const evidence = page.getByRole("region", { name: "후보 근거 패널" });
  await expect(evidence).toBeVisible();
  await expect(evidence).toContainText("종가·등락률 수정주가");
  await expect(evidence).toContainText("71,000");

  await page.getByRole("checkbox", { name: "좋은 수급" }).check();
  await expect(page.locator(".candidate-filter__result-count")).toContainText("필터 결과 1건");
  await expect(page.locator(".top-trading-candidates__item")).toHaveCount(3);
  await expect(page.locator(".top-trading-candidates__item").nth(1)).toContainText("SK하이닉스");

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

test("상단 요약 shape 오류는 기존 후보 카드 표면을 막지 않는다", async ({ page, request }) => {
  await request.post("http://127.0.0.1:54321/__e2e/scenario", { data: { scenario: "top-malformed" } });
  await page.goto("/login");
  await page.getByLabel("이메일").fill("neo@example.test");
  await page.getByLabel("비밀번호").fill("fixture-password");
  await page.getByRole("button", { name: "로그인" }).click();

  await expect(page).toHaveURL(/\/$/);
  await expect(page.getByRole("heading", { name: "거래대금 상위 후보" })).toHaveCount(0);
  await expect(page.getByRole("heading", { name: "조정후보" })).toBeVisible();
});

test("상단 요약 RPC transport 오류는 기존 후보 카드를 유지한다", async ({ page, request }) => {
  await request.post("http://127.0.0.1:54321/__e2e/scenario", { data: { scenario: "top-error" } });
  await page.goto("/login");
  await page.getByLabel("이메일").fill("neo@example.test");
  await page.getByLabel("비밀번호").fill("fixture-password");
  await page.getByRole("button", { name: "로그인" }).click();

  await expect(page).toHaveURL(/\/$/);
  await expect(page.getByRole("heading", { name: "거래대금 상위 후보" })).toHaveCount(0);
  await expect(page.getByRole("heading", { name: "조정후보" })).toBeVisible();
});

test("기존 카드 RPC 오류는 기존 오류 표면을 유지하고 상단 요약을 생략한다", async ({ page, request }) => {
  await request.post("http://127.0.0.1:54321/__e2e/scenario", { data: { scenario: "card-error" } });
  await page.goto("/login");
  await page.getByLabel("이메일").fill("neo@example.test");
  await page.getByLabel("비밀번호").fill("fixture-password");
  await page.getByRole("button", { name: "로그인" }).click();

  await expect(page).toHaveURL(/\/$/);
  await expect(page.getByRole("heading", { name: "거래대금 상위 후보" })).toHaveCount(0);
  await expect(page.locator(".notice-banner")).toContainText("오늘의 후보 카드를 불러오지 못했습니다");
});
