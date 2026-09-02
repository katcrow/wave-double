import { defineConfig } from "@playwright/test";

/**
 * Story 1.11: 배포된(또는 로컬 `next dev`) 대상에 대한 contract smoke test config.
 * `playwright.config.ts`와 달리 webServer를 정의하지 않는다 -- 이 config는 이미 떠 있는
 * 대상(SMOKE_BASE_URL)을 검증하는 용도이지, 로컬에서 서버를 새로 띄우는 용도가 아니다.
 *
 * SMOKE_BASE_URL이 없으면 즉시 명확한 에러로 실패한다(예: 실수로 하드코딩된 URL을 치는 것을
 * 방지) -- `docs/deployment.md`의 절차대로 로컬(`http://localhost:3000`) 또는 실제 배포 URL을
 * 명시적으로 지정해야 한다.
 */
const SMOKE_BASE_URL = process.env.SMOKE_BASE_URL;
if (!SMOKE_BASE_URL) {
  throw new Error(
    "SMOKE_BASE_URL 환경변수가 설정되지 않았습니다. 예: SMOKE_BASE_URL=http://localhost:3000 npm run test:smoke"
  );
}
try {
  new URL(SMOKE_BASE_URL);
} catch {
  throw new Error(`SMOKE_BASE_URL이 올바른 URL이 아닙니다: ${SMOKE_BASE_URL}`);
}

export default defineConfig({
  testDir: "./e2e",
  testMatch: /production-smoke\.spec\.ts/,
  timeout: 60_000,
  fullyParallel: false,
  retries: 1,
  reporter: "list",
  use: {
    baseURL: SMOKE_BASE_URL,
  },
});
