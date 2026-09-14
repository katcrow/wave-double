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
  await page.getByLabel("전략", { exact: true }).selectOption("D");
  await page.getByLabel("Ticker").fill("051910");
  await page.getByRole("button", { name: "필터 적용" }).click();

  await expect(page).toHaveURL(/\/tracking\?status=OPEN&strategy=D&ticker=051910/);
  await expect(page.locator(".outcome-tracking__table tbody tr")).toHaveCount(1);
  await expect(page.locator(".outcome-tracking__table tbody")).toContainText("051910");
  await expect(page.locator(".outcome-tracking__table tbody")).toContainText("전략 D");
  await expect(page.getByLabel("상태")).toHaveValue("OPEN");
  await expect(page.getByLabel("전략", { exact: true })).toHaveValue("D");
  await page.reload();
  await expect(page.getByLabel("전략", { exact: true })).toHaveValue("D");
  await expect(page.locator(".outcome-tracking__table tbody tr")).toHaveCount(1);
  await page.goBack();
  await expect(page).toHaveURL(/\/tracking$/);
  await page.getByRole("link", { name: "초기화", exact: true }).click();
  await expect(page).toHaveURL(/\/tracking$/);
});

test("tracking은 잘못된 query 필터를 전체 조회로 정규화한다", async ({ page }) => {
  await signIn(page);
  await page.goto("/tracking?status=UNKNOWN&strategy=G&ticker=%3Cscript%3E");
  await expect(page.getByLabel("상태")).toHaveValue("");
  await expect(page.getByLabel("전략", { exact: true })).toHaveValue("");
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

test("tracking metric은 전체 범위에서 실전/기대치, count, CI를 함께 표시한다", async ({ page }) => {
  await signIn(page);
  await page.goto("/tracking");

  await expect(page.getByRole("heading", { name: "Metric comparison" })).toBeVisible();
  await expect(page.getByLabel("성과 기준 전략")).toHaveValue("");
  await expect(page.getByText("비교 범위: 전체 전략")).toBeVisible();
  await expect(page.locator(".metric-comparison__counts")).toContainText("종결 179건");
  await expect(page.locator(".metric-comparison__counts")).toContainText("진행 중 1건");
  await expect(page.locator(".metric-comparison__metric-value").first()).toContainText("49.72%");
  await expect(page.getByText("기대치 없음 — 이 비교 범위에는 정의된 백테스트 기대치가 없습니다.")).toBeVisible();
  await expect(page.getByText("95% CI", { exact: true })).toBeVisible();
  await expect(page.getByText(/TIMEOUT 2건 · N=30 기준/)).toBeVisible();
});

test("tracking metric 전략 선택은 outcome 필터와 함께 URL에 보존되고 게이트/경고를 표시한다", async ({ page }) => {
  await signIn(page);
  await page.goto("/tracking?status=OPEN&strategy=D&ticker=051910");
  await expect(page.locator(".metric-comparison__filters input[type='hidden'][name='status']")).toHaveValue("OPEN");
  await expect(page.locator(".metric-comparison__filters input[type='hidden'][name='strategy']")).toHaveValue("D");
  await expect(page.locator(".metric-comparison__filters input[type='hidden'][name='ticker']")).toHaveValue("051910");
  await page.getByLabel("성과 기준 전략").selectOption("B");
  await page.getByRole("button", { name: "비교 범위 적용" }).click();

  await expect(page).toHaveURL(/\/tracking\?status=OPEN&strategy=D&ticker=051910&metric_strategy=B/);
  await expect(page.getByText("비교 범위: 전략 B")).toBeVisible();
  await expect(page.getByText("백테스트 기대 승률이 95% CI 밖에 있습니다.")).toBeVisible();
  await expect(page.getByText("승률 기대치 대비 ±10%p 초과")).toBeVisible();
  await expect(page.getByText("PF 기대치 대비 ±25% 초과")).toBeVisible();
  await expect(page.getByText(/TIMEOUT 1건 · N=30 예상 왜곡: TIMEOUT 0\.37%/)).toBeVisible();
  await expect(page.locator(".metric-comparison__bar-group[role='img']")).toHaveCount(2);
  await expect(page.locator(".metric-comparison__bar-group[role='img']").nth(1)).toHaveAttribute("aria-label", /PF 비교 그래픽/);
  await page.reload();
  await expect(page.getByLabel("성과 기준 전략")).toHaveValue("B");
});

test("metric은 기대치가 없는 전략을 명시하고 키보드로 범위를 바꿀 수 있다", async ({ page }) => {
  await signIn(page);
  for (const strategy of ["D", "F"]) {
    await page.goto(`/tracking?metric_strategy=${strategy}`);
    await expect(page.getByText("기대치 없음 — 이 비교 범위에는 정의된 백테스트 기대치가 없습니다.")).toBeVisible();
    await expect(page.getByText("95% CI 판정", { exact: true })).toHaveCount(0);
    await expect(page.getByText("95% CI", { exact: true })).toBeVisible();
  }
  await page.goto("/tracking");
  const selector = page.getByRole("combobox", { name: "성과 기준 전략" });
  await expect(selector).toHaveRole("combobox");
  await selector.focus();
  await page.keyboard.press("ArrowDown");
  await expect(selector).toHaveValue("A");
});

test("all-win PF NULL은 산출 불가 의미를 표시한다", async ({ page, request }) => {
  await signIn(page);
  await request.post("http://127.0.0.1:54321/__e2e/scenario", { data: { scenario: "tracking-metric-all-win" } });
  await page.goto("/tracking?metric_strategy=F");
  await expect(page.getByText("산출 불가(음의 손익 없음)")).toBeVisible();
});

test("tracking metric 표본 부족은 성과/CI/threshold를 숨긴다", async ({ page, request }) => {
  await signIn(page);
  await request.post("http://127.0.0.1:54321/__e2e/scenario", { data: { scenario: "tracking-metric-below-gate" } });
  await page.goto("/tracking?metric_strategy=C");

  await expect(page.getByText("표본 부족 (29/30)")).toBeVisible();
  await expect(page.locator(".metric-comparison__gate")).toBeVisible();
  await expect(page.locator(".metric-comparison__metric-value")).toHaveCount(0);
  await expect(page.getByText("95% CI 판정")).toHaveCount(0);
});

test("tracking metric RPC 실패와 shape 오류는 outcome tracking을 유지한다", async ({ page, request }) => {
  await signIn(page);
  await request.post("http://127.0.0.1:54321/__e2e/scenario", { data: { scenario: "tracking-metric-error" } });
  await page.goto("/tracking");
  await expect(page.locator(".metric-comparison__state[role='alert']")).toContainText("성과 비교 데이터를 불러오지 못했습니다");
  await expect(page.getByRole("heading", { name: "Outcome tracking" })).toBeVisible();
  await expect(page.locator(".outcome-tracking__table tbody tr")).toHaveCount(6);

  await request.post("http://127.0.0.1:54321/__e2e/scenario", { data: { scenario: "tracking-metric-malformed" } });
  await page.reload();
  await expect(page.locator(".metric-comparison__state[role='alert']")).toContainText("성과 비교 데이터를 불러오지 못했습니다");
  await expect(page.locator(".outcome-tracking__table tbody tr")).toHaveCount(6);
});

test("tracking metric은 375px 폭에서도 전략 선택과 metric 결과를 읽을 수 있다", async ({ page }) => {
  await signIn(page);
  await page.goto("/tracking?metric_strategy=A");
  await page.setViewportSize({ width: 375, height: 812 });
  await expect(page.getByLabel("성과 기준 전략")).toBeVisible();
  await expect(page.locator(".metric-comparison__metric")).toHaveCount(2);
  await expect(page.locator(".metric-comparison__metric-value").first()).toBeVisible();
  await expect(page.getByText("백테스트 기대 승률이 95% CI 안에 있습니다.")).toBeVisible();
});

test("tracking bias는 기존 query를 유지한 채 날짜를 바꾸고 실제 URL 상태를 복원한다", async ({ page }) => {
  await signIn(page);
  await page.goto("/tracking?status=OPEN&strategy=D&ticker=051910&metric_strategy=B&bias_date=2026-09-08");

  await expect(page.getByRole("heading", { name: "Bias diagnostic" })).toBeVisible();
  await expect(page.getByLabel("편향 진단 날짜")).toHaveValue("2026-09-08");
  await expect(page.getByText("기준일: 2026-09-08")).toBeVisible();
  await expect(page.locator(".bias-diagnostic__metric")).toHaveCount(4);
  await expect(page.locator(".bias-diagnostic__value").nth(0)).toHaveText("12");
  await expect(page.locator(".bias-diagnostic__value").nth(1)).toHaveText("18");
  await expect(page.locator(".bias-diagnostic__value").nth(2)).toHaveText("7");
  await expect(page.locator(".bias-diagnostic__value").nth(3)).toHaveText("14");
  await expect(page.getByText("성과 실패 원인을 뜻하지는 않습니다.")).toBeVisible();

  await page.getByLabel("편향 진단 날짜").fill("2026-09-10");
  await page.getByRole("button", { name: "날짜 적용" }).click();
  await expect(page).toHaveURL(/\/tracking\?status=OPEN&strategy=D&ticker=051910&metric_strategy=B&bias_date=2026-09-10/);
  await expect(page.getByLabel("편향 진단 날짜")).toHaveValue("2026-09-10");
  await expect(page.getByLabel("상태")).toHaveValue("OPEN");
  await expect(page.getByLabel("전략", { exact: true })).toHaveValue("D");
  await expect(page.getByLabel("Ticker")).toHaveValue("051910");
  await expect(page.getByLabel("성과 기준 전략")).toHaveValue("B");
  await page.reload();
  await expect(page.getByLabel("편향 진단 날짜")).toHaveValue("2026-09-10");
  await page.goBack();
  await expect(page).toHaveURL(/\/tracking\?status=OPEN&strategy=D&ticker=051910&metric_strategy=B&bias_date=2026-09-08/);
  await expect(page.getByLabel("편향 진단 날짜")).toHaveValue("2026-09-08");
});

test("tracking bias는 무쿼리일 때 KST 오늘을 기본값으로 쓰고 뒤로가기로 무쿼리 상태를 복원한다", async ({ page }) => {
  await signIn(page);
  await page.goto("/tracking");
  const parts = new Intl.DateTimeFormat("en-US", {
    timeZone: "Asia/Seoul",
    year: "numeric",
    month: "2-digit",
    day: "2-digit",
  }).formatToParts(new Date());
  const values = Object.fromEntries(parts.map(({ type, value }) => [type, value]));
  const kstToday = `${values.year}-${values.month}-${values.day}`;
  await expect(page).toHaveURL(/\/tracking$/);
  await expect(page.getByLabel("편향 진단 날짜")).toHaveValue(kstToday);

  await page.getByLabel("편향 진단 날짜").fill("2026-09-10");
  await page.getByRole("button", { name: "날짜 적용" }).click();
  await expect(page).toHaveURL(/\/tracking\?bias_date=2026-09-10/);
  await page.goBack();
  await expect(page).toHaveURL(/\/tracking$/);
  await expect(page.getByLabel("편향 진단 날짜")).toHaveValue(kstToday);
});

test("tracking bias는 미수집·RPC 오류·shape 오류를 분리하고 기존 결과를 유지한다", async ({ page, request }) => {
  await signIn(page);
  await request.post("http://127.0.0.1:54321/__e2e/scenario", { data: { scenario: "tracking-bias-empty" } });
  await page.goto("/tracking?bias_date=2026-09-11");
  await expect(page.locator(".bias-diagnostic__state")).toContainText("이 날짜의 편향 데이터가 없습니다");
  await expect(page.locator(".bias-diagnostic__value")).toHaveCount(0);
  await expect(page.locator(".outcome-tracking__table tbody tr")).toHaveCount(6);

  await request.post("http://127.0.0.1:54321/__e2e/scenario", { data: { scenario: "tracking-bias-error" } });
  await page.reload();
  await expect(page.locator(".bias-diagnostic__state[role='alert']")).toContainText("편향 진단 데이터를 불러오지 못했습니다");
  await expect(page.locator(".metric-comparison__metric-value").first()).toBeVisible();
  await expect(page.locator(".outcome-tracking__table tbody tr")).toHaveCount(6);

  await request.post("http://127.0.0.1:54321/__e2e/scenario", { data: { scenario: "tracking-bias-malformed" } });
  await page.reload();
  await expect(page.locator(".bias-diagnostic__state[role='alert']")).toContainText("편향 진단 데이터를 불러오지 못했습니다");
  await expect(page.locator(".outcome-tracking__table tbody tr")).toHaveCount(6);
});

test("tracking bias 네 수치는 좁은 화면에서도 읽을 수 있다", async ({ page }) => {
  await signIn(page);
  await page.goto("/tracking");
  await page.setViewportSize({ width: 375, height: 812 });
  await expect(page.getByLabel("편향 진단 날짜")).toBeVisible();
  await expect(page.locator(".bias-diagnostic__metric")).toHaveCount(4);
  await expect(page.locator(".bias-diagnostic__grid")).toHaveRole("list");
  await expect(page.locator(".bias-diagnostic__metric").first()).toHaveRole("listitem");
  await expect(page.locator(".bias-diagnostic__grid")).toBeVisible();
});
