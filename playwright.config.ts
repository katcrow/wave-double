import { defineConfig } from "@playwright/test";

const PORT = 3000;
const BASE_URL = `http://localhost:${PORT}`;

export default defineConfig({
  testDir: "./e2e",
  // Story 1.11: production-smoke.spec.ts는 SMOKE_BASE_URL 대상(webServer 없음)으로만 실행되는
  // 별도 스위트다(playwright.smoke.config.ts). 여기서 제외하지 않으면 로컬 dev 서버 대상
  // `npm run test:e2e`(및 CI의 "E2E test (web)" 스텝)에도 함께 실행돼 버린다.
  testIgnore: /production-smoke\.spec\.ts/,
  timeout: 60_000,
  fullyParallel: false,
  // epic-2-retro-item-12: candidate-surface-scenarios.spec.ts는 mock Supabase의 활성 시나리오를
  // 바꿔가며 렌더 결과를 검증한다. 그 상태는 mock 서버 프로세스 하나에 전역이므로, 파일이
  // 서로 다른 worker에서 동시에 돌면 다른 스펙이 남의 시나리오를 보게 된다
  // (`fullyParallel: false`는 파일 "안"의 순서만 보장하고 파일 "간" 병렬은 막지 않는다).
  workers: 1,
  retries: 1,
  reporter: "list",
  use: {
    baseURL: BASE_URL,
  },
  webServer: {
    command: `node e2e/start-test-web.mjs`,
    url: BASE_URL,
    reuseExistingServer: !process.env.CI,
    timeout: 120_000,
  },
});
