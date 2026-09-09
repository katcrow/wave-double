import { test, expect, type APIRequestContext, type Page } from "@playwright/test";

/**
 * epic-2-retro-item-12 / epic-7-retro-item-29: 인증 세션에서 실제 렌더 결과를 검증한다.
 *
 * 두 회고 모두 같은 공백을 지적했다 -- 카드/소멸/모집단 이탈/수집 실패/장중 라벨과 전략 F
 * 배지는 순수 함수 단위 테스트로는 "화면에 그렇게 그려지는가"를 증명하지 못한다. 각 상태는
 * 같은 화면의 서로 다른 RPC 응답 조합이므로, mock Supabase의 시나리오 스위치
 * (`POST /__e2e/scenario`)로 응답을 바꿔가며 렌더 결과를 확인한다.
 */

const MOCK_BASE = "http://127.0.0.1:54321";

async function setScenario(request: APIRequestContext, scenario: string): Promise<void> {
  const response = await request.post(`${MOCK_BASE}/__e2e/scenario`, { data: { scenario } });
  expect(response.ok(), `시나리오 전환 실패: ${scenario}`).toBe(true);
  expect((await response.json()).scenario).toBe(scenario);
}

async function login(page: Page): Promise<void> {
  await page.goto("/login");
  await page.getByLabel("이메일").fill("neo@example.test");
  await page.getByLabel("비밀번호").fill("fixture-password");
  await page.getByRole("button", { name: "로그인" }).click();
  await expect(page).toHaveURL(/\/$/);
}

test.afterEach(async ({ request }) => {
  // 시나리오는 mock 서버 프로세스에 남으므로 다른 스펙으로 새지 않게 되돌린다.
  await setScenario(request, "default");
});

test("기본 시나리오: 활성 카드가 소멸/미수집 문구 없이 렌더된다", async ({ page, request }) => {
  await setScenario(request, "default");
  await login(page);

  const card = page.locator(".candidate-card").first();
  await expect(card).toContainText("조정후보");
  await expect(card).toContainText("시그널 활성");
  await expect(card.locator(".candidate-card__notice--vanished")).toHaveCount(0);
  await expect(card).not.toContainText("수급 일부 미수집");
  await expect(page.locator(".disappeared-candidates")).toHaveCount(0);
  await expect(page.locator(".intraday-label")).toHaveCount(0);
});

test("부분 소멸: 카드가 목록에 남고 소멸된 전략이 함께 표시된다", async ({ page, request }) => {
  await setScenario(request, "partial-vanish");
  await login(page);

  const card = page.locator(".candidate-card").first();
  await expect(card).toBeVisible();
  await expect(card).toContainText("시그널 혼합");
  await expect(card.locator(".candidate-card__notice--vanished")).toContainText("소멸: 전략 B");
  // 부분 소멸은 카드를 목록에서 빼지 않는다(스펙 Always).
  await expect(page.locator(".candidate-card")).toHaveCount(1);
});

test("완전 소멸: active 태그가 0건이어도 카드는 남고 시그널이 소멸이다", async ({ page, request }) => {
  await setScenario(request, "complete-vanish");
  await login(page);

  const card = page.locator(".candidate-card").first();
  await expect(card).toBeVisible();
  await expect(card).toContainText("시그널 소멸");
  await expect(page.locator(".candidate-card")).toHaveCount(1);
});

test("모집단 이탈: 카드 그리드와 별개 영역에 이탈 문구로 표시된다", async ({ page, request }) => {
  await setScenario(request, "population-dropout");
  await login(page);

  const notice = page.locator(".disappeared-candidates");
  await expect(notice).toBeVisible();
  await expect(notice).toContainText("이탈종목");
  await expect(notice).toContainText("000660");
  await expect(notice.locator(".disappeared-candidates__reason")).toContainText("모집단 이탈");
  await expect(notice).not.toContainText("수집 실패");
});

test("수집 실패: 이탈과 다른 문구로 구분되고 카드에는 미수집 단서가 붙는다", async ({ page, request }) => {
  await setScenario(request, "collection-failure");
  await login(page);

  const notice = page.locator(".disappeared-candidates");
  await expect(notice).toBeVisible();
  await expect(notice).toContainText("수집실패종목");
  await expect(notice.locator(".disappeared-candidates__reason")).toContainText("수집 실패");
  await expect(notice).not.toContainText("모집단 이탈");

  const card = page.locator(".candidate-card").first();
  await expect(card.locator(".candidate-card__notice")).toContainText("수급 일부 미수집");
  // 미수집 단서는 카드를 목록에서 제외하지 않는다.
  await expect(page.locator(".candidate-card")).toHaveCount(1);
});

test("장중 라벨: 장중 배치 스냅샷에는 최종 추천 미확정 라벨이 고정 표시된다", async ({ page, request }) => {
  await setScenario(request, "intraday");
  await login(page);

  const label = page.locator(".intraday-label");
  await expect(label).toBeVisible();
  await expect(label).toContainText("장중 참고");
  await expect(label).toContainText("최종 추천 미확정");
  await expect(label).toHaveAttribute("role", "status");
});

test("전략 F: 카드에 전략 F 배지가 렌더되고 F 라우트가 열린다", async ({ page, request }) => {
  await setScenario(request, "strategy-f");
  await login(page);

  const card = page.locator(".candidate-card").first();
  await expect(card).toContainText("F후보");
  await expect(card).toContainText("전략 F");

  await page.goto("/strategies/F");
  await expect(page.getByRole("heading", { name: "전략 F" })).toBeVisible();
});

test("전략 G: 정의되지 않은 전략 라우트는 not-found로 떨어진다", async ({ page }) => {
  // 인증 없이 /strategies/G로 바로 가면 미들웨어가 /login으로 돌려보내므로 not-found에
  // 도달하지도 못한다 -- 세션이 있어야 이 회귀를 볼 수 있다.
  await login(page);

  await page.goto("/strategies/G");

  // 렌더 결과로 판정한다. `notFound()`는 프로덕션 빌드에서 HTTP 404를 내지만 dev 서버는
  // not-found 페이지를 그리면서 상태 코드는 200으로 응답한다 -- 이 스위트는 dev 서버를
  // 대상으로 돌기 때문에 상태 코드로 판정하면 항상 실패한다(실제로 그렇게 실패했다).
  await expect(page.getByRole("heading", { name: "404" })).toBeVisible();
  await expect(page.getByRole("heading", { name: "전략 G" })).toHaveCount(0);
  await expect(page.locator("body")).not.toContainText("설명/성과 준비 중입니다");
});
