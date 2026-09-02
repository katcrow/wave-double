---
title: '호스팅 배포 파이프라인'
type: 'feature'
created: '2026-09-02'
status: 'done'
baseline_revision: 'b8b638ccee42137c8629b6cf2da936f4bba093bd'
review_loop_iteration: 0
followup_review_recommended: true
context:
  - '{project-root}/_bmad-output/planning-artifacts/architecture/architecture-wave-double-2026-08-31/ARCHITECTURE-SPINE.md'
warnings: [oversized]
deferred:
  - summary: >-
      `.env.local`/`.env.example`에 `INTERNAL_CRON_SECRET`(미사용)과 `CRON_CALLBACK_SECRET`(실사용)
      이라는 같은 용도의 서로 다른 이름이 공존해, 운영자가 실수로 `INTERNAL_CRON_SECRET`만 채우고
      실제 게이트인 `CRON_CALLBACK_SECRET`을 비워두면 outbox worker(`/api/dispatch/worker`)의
      cron 인증이 조용히 깨질 수 있다.
    evidence: |-
      story 1.10 spec의 deferred 항목에서 이미 같은 중복을 지적했고, 이번 review의
      verification-gap 레이어가 리포 전체를 확인해 `INTERNAL_CRON_SECRET`을 실제로 읽는 코드가
      전혀 없음을 재확인했다(문서/주석에서만 언급됨). 이번 스토리는 `.env.example`에 그 사실을
      정확히 반영하고 경고 주석을 달았을 뿐, 두 이름이 공존하는 근본 상태 자체는 story 1.10
      이전부터 있던 것이라 이번 변경이 새로 만든 결함은 아니다.
    location: >-
      .env.local, .env.example, apps/web/app/api/dispatch/worker/route.ts
    severity: medium
---

<intent-contract>

## Intent

**Problem:** 웹 앱이 아직 실제 인터넷에 배포되지 않아 Neo가 브라우저로 접속할 수 없다. 호스팅 제공자 결정(Vercel Hobby, 2026-09-01)은 이미 architecture에 기록됐지만, 실제 연결 절차·환경변수 체크리스트·배포 후 contract smoke test·사용량 한도 근접 감지 절차가 없다.
**Approach:** Vercel 프로젝트 연결은 이 세션에 계정 자격증명이 없어 실행 불가한 수동 1회 작업이므로, 그 절차를 문서화하고(`docs/deployment.md`), 환경변수 체크리스트(`.env.example`)와 배포 후 실행할 자동화된 contract smoke test(`e2e/production-smoke.spec.ts`)를 코드로 제공한다. 사용량 80% 근접 감지는 Vercel 공식 REST API에 사용량 조회 엔드포인트가 없어(2026-09 확인) 커스텀 폴링 대신 Vercel 대시보드 내장 Usage Alert 활성화 절차로 문서화한다.

## Boundaries & Constraints

**Always:** Vercel 프로젝트 생성·GitHub 연동·Root Directory(`apps/web`) 설정·Node 버전 확인·환경변수 등록은 Vercel 대시보드에서 Neo가 수행하는 수동 1회 작업으로 `docs/deployment.md`에 단계별로 문서화한다(이 세션은 Vercel 계정 자격증명이 없어 실제 연결/배포를 실행할 수 없다). 모든 secret은 Vercel Environment Variables에만 등록하고 코드·로그·커밋 이력에 평문으로 남기지 않는다(NFR1). `.env.example`은 `.env.local`의 모든 키 이름과 용도 주석만 담고 실제 값은 포함하지 않으며, `INTERNAL_CRON_SECRET`(미사용)과 `CRON_CALLBACK_SECRET`(실사용, outbox worker가 비교하는 값)이 같은 용도의 서로 다른 이름임을 주석으로 명확히 구분한다. `e2e/production-smoke.spec.ts`는 `SMOKE_BASE_URL` 환경변수가 가리키는 대상(로컬 `npm run dev` 또는 실제 배포 URL)에 대해 인증 없이 확인 가능한 계약만 검증한다: `/`·`/runs` 미인증 리다이렉트, `/login` 200 응답, `/api/dispatch/worker`의 시크릿 헤더 없는 호출 401 응답. Vercel 사용량 한도 80% 근접 감지는 Vercel 대시보드의 Usage Alert(이메일 알림) 기능을 활성화하는 절차로 `docs/deployment.md`에 문서화하고, 그 근거(공식 API 부재)를 Design Notes에 남긴다. "서비스 접속 불가"(Vercel 인프라 레벨 한도 초과/장애)는 브라우저가 앱의 stale 문구 대신 Vercel 자체 오류 화면을 보여준다는 사실 자체가 이미 대시보드의 "stale" 표시와 구분됨을 `docs/deployment.md`에 문서화·확인한다(신규 UI 상태 불필요).

**Never:** 새 npm/pip 의존성을 추가하지 않는다(Playwright는 이미 devDependency). `/`·`/runs` UI에 새 상태·배너·컴포넌트를 추가하지 않는다(AC4는 문서화·확인 요건이지 신규 UI 요건이 아니다). Vercel 계정 생성, 실제 GitHub-Vercel 연동, 실제 배포 실행, 프로덕션 환경변수 입력은 이 세션에서 수행하지 않는다(자격증명 부재, Manual checks로 위임). 사용량 조회를 위한 커스텀 GitHub Actions 폴링 워크플로를 새로 만들지 않는다(대상 API가 존재하지 않는다).

## I/O & Edge-Case Matrix

| Scenario | Input / State | Expected Output / Behavior | Error Handling |
|----------|--------------|---------------------------|----------------|
| 미인증 `/` 접속 | 세션 쿠키 없음, `SMOKE_BASE_URL` 대상 | `/login`으로 리다이렉트 | 없음(정상 동작) |
| 미인증 `/runs` 접속 | 세션 쿠키 없음 | `/login`으로 리다이렉트 | 없음 |
| `/login` 접속 | 무관 | `200`, OTP 요청 폼 렌더 | 없음 |
| 시크릿 헤더 없이 `/api/dispatch/worker` 호출 | `x-cron-secret` 헤더 누락 | 라우트가 살아있고 게이트가 걸림을 증명 | `401` |

</intent-contract>

## Code Map

- `apps/web/proxy.ts:19-26` -- `PUBLIC_PATH_PATTERNS`. `/`·`/runs`는 여기 없으므로 미인증 시 `/login`으로 리다이렉트됨(smoke test가 검증하는 기존 동작).
- `apps/web/app/login/page.tsx` -- OTP 요청 폼(story 1.10 구현). smoke test가 200 응답과 폼 존재를 확인하는 대상.
- `apps/web/app/api/dispatch/worker/route.ts` -- `CRON_CALLBACK_SECRET` 헤더 검증(story 1.10). 헤더 없이 호출 시 401을 반환하는 기존 동작을 smoke test가 재확인한다(배포 후 이 route가 실제로 살아있고 게이트가 걸림을 증명).
- `.env.local`(미버전관리) -- 전체 키 목록(`SUPABASE_*`, `OPERATOR_ALLOWLIST`, `GITHUB_DISPATCH_TOKEN`, `CRON_CALLBACK_SECRET`, `INTERNAL_CRON_SECRET`, `GITHUB_REPO_OWNER/NAME`, `LS_OPEN_API_*`, `LS_CONDITION_SEARCH_USER_ID`) -- `.env.example`이 이름만 이식할 원본.
- `apps/web/next.config.ts`(`loadRootEnvFile`) -- 루트 `.env.local` 병합기. Vercel은 이 파일을 읽지 않고 대시보드 Environment Variables만 읽으므로, 이 목록이 Vercel에도 그대로 등록돼야 한다는 점을 문서에 명시한다.
- `playwright.config.ts` -- 기존 로컬 E2E config(webServer로 `next dev` 기동, `baseURL` 하드코딩). 신규 `playwright.smoke.config.ts`는 이 파일과 별개로 webServer 없이 `SMOKE_BASE_URL`을 baseURL로 쓴다(로컬 재사용 시 `http://localhost:3000` 지정 가능).
- `package.json`(root) `scripts.test:e2e` -- 옆에 `test:smoke` 스크립트를 추가하는 자리.
- `_bmad-output/implementation-artifacts/spec-1-10-인증-수동-트리거.md`(deferred, 2번째 항목) -- `.env.example` 부재 지적. 이번 스토리로 해소.
- `_bmad-output/planning-artifacts/architecture/architecture-wave-double-2026-08-31/ARCHITECTURE-SPINE.md:267-268` -- Vercel Hobby 결정과 근거, "남은 유일 사항"이 이 스토리의 contract smoke test임을 명시.

## Tasks & Acceptance

**Execution:**
- `.env.example`(신규, repo root) -- `.env.local`의 모든 키를 이름+한 줄 용도 주석으로 옮기되 값은 비워둔다(`KEY=`) -- `INTERNAL_CRON_SECRET`과 `CRON_CALLBACK_SECRET`이 같은 값을 가리키는 서로 다른 이름임을 주석으로 명시 -- Vercel 환경변수 등록 체크리스트 겸 1.10 deferred 항목 해소.
- `docs/deployment.md`(신규) -- ① Vercel Hobby 프로젝트 생성/GitHub 저장소 연동 절차, ② Root Directory=`apps/web`·Node 버전(24.x, 현재 Vercel 기본값) 확인 절차, ③ `.env.example` 기준 환경변수 전체 등록 절차, ④ main 병합 시 Vercel GitHub 통합이 자동 배포함(신규 워크플로 불필요, 근거 포함)을 확인하는 절차, ⑤ `npm run test:smoke -- --config=playwright.smoke.config.ts` 배포 후 실행 절차와 기대 결과, ⑥ 인증 필요 화면(Story 1.9 `/`·`/runs`, Story 1.8 스냅샷 API) 수동 확인 절차, ⑦ Vercel 대시보드 Usage Alert 활성화 절차와 "API 미제공" 근거, ⑧ "서비스 접속 불가" vs "stale" 구분 근거.
- `playwright.smoke.config.ts`(신규, repo root) -- `SMOKE_BASE_URL`(필수, 미설정 시 명확한 에러로 즉시 실패)을 `baseURL`로 쓰고 `webServer`를 정의하지 않는 config.
- `e2e/production-smoke.spec.ts`(신규) -- I/O 매트릭스 4개 시나리오를 검증한다.
- `package.json`(root) -- `scripts`에 `"test:smoke": "playwright test --config=playwright.smoke.config.ts"` 추가.

**Acceptance Criteria:**
- Given ARCHITECTURE-SPINE.md의 Vercel Hobby 결정(2026-09-01)이 이미 존재하면, when 이 스토리를 완료하면, then 남은 구현 항목(배포 절차 문서·환경변수 체크리스트·contract smoke test·사용량 알림 절차)이 모두 코드/문서로 준비된다.
- Given `docs/deployment.md`의 절차대로 Vercel 프로젝트를 연결하면(Manual, 자격증명 필요), when main에 머지하면, then Vercel GitHub 통합이 자동 배포를 트리거한다(코드 변경 없이 문서화된 플랫폼 동작).
- Given `SMOKE_BASE_URL=http://localhost:3000`으로 로컬 `next dev`를 띄운 상태에서 `npm run test:smoke`를 실행하면, when 스크립트가 완료되면, then I/O 매트릭스 4개 시나리오가 모두 통과한다(실제 배포 URL 없이도 로직을 검증할 수 있어야 한다).
- Given 인증된 세션으로 실제 배포 URL의 `/`·`/runs`에 접속하면(Manual check, OTP 자동화 불가), when 화면을 확인하면, then Story 1.9 화면과 Story 1.8 스냅샷 API 데이터가 정상 표시된다.
- Given `.env.example`을 열람하면, when `.env.local`과 대조하면, then 두 파일의 키 이름 집합이 정확히 일치한다(값은 `.env.example`에 없다).

## Spec Change Log

## Review Triage Log

### 2026-09-02 — Review pass
- intent_gap: 0
- bad_spec: 0
- patch: 3: (medium 2, low 1)
- defer: 1: (medium 1)
- dismissed:
  - "smoke test가 배포 파이프라인 트리거(auto-deploy 확인) 자체를 자동화하지 않고 수동 절차에 의존한다" — 이 세션에는 Vercel 계정 자격증명이 없어 실제 연결/배포를 실행할 수 없다는 사실적 제약이며, spec의 Boundaries·Never 절이 이미 이 분리를 명시적으로 설계했다(Manual checks로 위임).
  - "smoke test가 `/api/dispatch`(operator-triggered dispatch route)의 JWT 게이트를 검증하지 않는다" — epics.md의 story 1.11 AC는 `/`·`/runs` 페이지 로딩과 스냅샷 API 확인만 요구하며, `/api/dispatch`의 JWT/CSRF/rate-limit 검증은 이미 story 1.10에서 단위 테스트로 커버된다. 이번 스토리 intent가 요구하지 않는 범위다.
  - "배포 후 smoke test를 웹훅 등으로 자동 트리거하는 장치가 없다" — 신규 GitHub Actions 폴링/트리거 워크플로를 만들지 않는다는 spec Never 절과 자격증명 부재 제약에 따른 의도된 설계다.
  - "실패한 프로덕션 배포에 대한 롤백 절차가 문서화되어 있지 않다" — epics.md AC/NFR 어디에도 롤백 절차 문서화 요건이 없고, Vercel 대시보드 자체가 이전 배포로의 즉시 롤백을 기본 제공한다.
  - "Hobby 플랜 한도 수치·Node 버전 기본값이 출처 인용 없이 서술돼 있어 시간이 지나면 stale해질 수 있다" — 문서 자체가 이 수치를 참고용 근사치로 명시하고 있고, 코드의 어떤 로직도 이 정확한 숫자에 의존하지 않는다(검증 가능한 동작 결과가 없다).
  - "`playwright.smoke.config.ts`의 `retries: 1`이 비멱등 호출의 중복 실행 위험을 안고 있다" — 현재 4개 테스트는 전부 부작용 없는 GET이거나 인증 실패로 즉시 거부되는 POST(`/api/dispatch/worker`, 시크릿 헤더 없이 401)뿐이라 실제 상태 변경이 없다. 검증 가능한 현재 결함이 아니다.
  - "smoke test 실패 시 trace/screenshot 등 진단 아티팩트가 없다" — spec Verification 어디에도 진단 아티팩트 요건이 없고, 실패 시 재현은 `SMOKE_BASE_URL`을 대상으로 로컬에서 동일 커맨드를 재실행해 확인할 수 있다.
  - "`e2e/production-smoke.spec.ts`가 `/login` 화면의 한국어 문구를 하드코딩해 화면 문구 변경 시 조용히 깨질 수 있다" — 기존 `e2e/home.spec.ts`·`e2e/manual-trigger.spec.ts`도 동일한 방식(문구 직접 assert)을 이미 쓰고 있어 이번 변경이 새로 도입한 패턴이 아니다.
  - "frontmatter `warnings: [oversized]`가 무엇을 줄였는지 설명하지 않는다" — 이 필드는 spec-template의 크기 경고 플래그일 뿐 트리밍을 약속하지 않으며, story 1.10 spec도 동일하게 사용한 기존 관례다.
  - "Vercel 대시보드 UI에 절차가 의존해 단일 운영자(Neo)의 bus-factor 위험이 있다" — 이 프로젝트는 ARCHITECTURE-SPINE.md 전체가 1인 개인 운영을 전제로 설계돼 있어(NFR-1) 팀 인수인계 문서화는 intent 범위 밖이다.
  - "AC2(main 병합 시 자동 배포)가 사람이 Vercel을 수동 연결하기 전까지는 검증 불가능하다" — spec의 Intent/Boundaries가 이미 이 제약(자격증명 부재)을 명시하고 Manual checks로 분리했으며, 스코프 배제의 근거가 spec 서술이 아니라 실제 자격증명 부재라는 사실이다.
- addressed_findings:
  - `[medium]` `[patch]` `playwright.config.ts`: `testDir: "./e2e"`에 제한이 없어 신규 `e2e/production-smoke.spec.ts`가 로컬 dev 대상 `npm run test:e2e`(및 CI "E2E test (web)" 스텝)에도 함께 실행되고 있었다(blind-hunter/edge-case-hunter/verification-gap 3개 레이어가 교차 확인) — 오늘은 assertion이 우연히 로컬에서도 참이라 통과했지만, smoke test에 프로덕션 전용 가정이 추가되면 이 일반 CI 게이트가 조용히 깨질 수 있었다. `testIgnore: /production-smoke\.spec\.ts/`를 추가해 두 스위트를 분리했다. `npm run test:e2e`(4/4, 기존 스펙만 실행) / `npm run test:smoke`(4/4) 재검증 통과.
  - `[low]` `[patch]` `playwright.smoke.config.ts`: `SMOKE_BASE_URL`이 설정만 확인되고 형식은 검증되지 않아, 오타 등 유효하지 않은 URL을 넣으면 Playwright의 저수준 에러로 원인 파악이 어려웠다(edge-case-hunter). `new URL(SMOKE_BASE_URL)`을 try/catch로 감싸 기존과 같은 스타일의 명확한 에러로 실패하도록 고쳤다.
  - `[medium]` `[patch]` `docs/deployment.md`(③): Preview 환경변수 등록 안내에 Vercel의 Git Fork Protection(기본 활성화, fork PR 빌드가 Preview secret에 접근하지 못하게 막는 안전장치) 관련 경고가 없어, 이 리포가 public임을 고려하면(AD-11과 동일 위험군) 향후 누군가 이 보호를 실수로 끌 경우의 위험을 문서가 미리 경고하지 못했다(blind-hunter가 지적한 Preview secret scoping 우려를 구체화·검증한 결과 — Vercel 공식 문서로 기본 보호가 이미 존재함을 확인해 "신규 취약점"이 아니라 "문서 보강" 항목으로 재분류). "Git Fork Protection을 끄지 말 것" 경고 문단을 추가했다.

## Design Notes

Vercel REST API에는 프로젝트별 사용량(대역폭/함수 호출/빌드 시간) 조회 엔드포인트가 없다(2026-09 확인: 공식 `vercel.com/docs/rest-api`에 해당 엔드포인트 없음, `github.com/vercel/vercel` discussion #11120/#8310에서 커뮤니티가 동일하게 확인). 따라서 story 1.10의 dead-letter 알림(AD-10, GitHub Issue)과 같은 커스텀 폴링+알림 패턴을 사용량 감지에 재사용할 수 없다 -- 대신 Vercel이 기본 제공하는 대시보드 Usage Alert(플랜 한도 근접 시 이메일)를 활성화하는 것으로 AC4를 만족시킨다. 이 결정은 Vercel이 향후 사용량 API를 공개하면 재검토한다.

Vercel의 GitHub 통합은 push-to-deploy를 기본 제공하므로(Root Directory만 정확히 설정하면 됨) 별도 `.github/workflows/deploy.yml`이 필요 없다. 기존 `.github/workflows/{test,scheduled-batch}.yml`과 무관한 별개 배포 경로다.

## Verification

**Commands:**
- `npm run typecheck` -- expected: 오류 없음(신규 config/spec 파일이 기존 tsconfig 범위에 영향 없음을 확인).
- `SMOKE_BASE_URL=http://localhost:3000 npm run dev -w apps/web &` 후 `npm run test:smoke` -- expected: 4개 시나리오 전부 통과(로컬 대상으로 로직 검증).
- `diff <(grep -oE '^[A-Z_]+=' .env.local | sort) <(grep -oE '^[A-Z_]+=' .env.example | sort)` -- expected: 출력 없음(키 집합 완전 일치).

**Manual checks (if no CLI):**
- Vercel 대시보드에서 프로젝트 생성 → GitHub 저장소 연동 → Root Directory `apps/web` 설정 → `.env.example` 기준 환경변수 전부 등록 → main 병합 후 자동 배포 확인.
- 실제 배포 URL에 대해 `SMOKE_BASE_URL=<production-url> npm run test:smoke` 실행 후 통과 확인.
- 실제 배포 URL에 이메일 OTP로 로그인해 `/`·`/runs`가 Story 1.9 화면대로 렌더되고 Story 1.8 스냅샷 API 데이터를 반영하는지 육안 확인.
- Vercel 대시보드 Settings → Usage Alerts를 활성화해 이메일 수신 대상이 설정돼 있는지 확인.

## Auto Run Result

**요약:** Vercel Hobby 배포에 필요한, 이 세션에서 실행 가능한 부분(자격증명 불필요한 부분)을 모두 구현했다: `.env.example`(환경변수 체크리스트, 1.10 deferred 항목 해소), `docs/deployment.md`(8단계 배포 절차 — 프로젝트 연결·환경변수 등록·자동배포 확인·smoke test·인증화면 수동확인·Usage Alert·stale 구분 근거), `playwright.smoke.config.ts` + `e2e/production-smoke.spec.ts`(배포 대상에 대한 인증 불필요 계약 4종 검증), `package.json`의 `test:smoke` 스크립트. Vercel 계정 자격증명이 없어 실제 프로젝트 생성·GitHub 연동·환경변수 등록·배포 실행·Usage Alert 활성화·인증 화면 확인은 spec Verification의 Manual checks로 위임했다(spec Boundaries에 이미 명시된 제약).

**변경 파일:**
- `.env.example`(신규) — `.env.local`의 모든 키 이름+용도 주석(값 제외), `INTERNAL_CRON_SECRET`/`CRON_CALLBACK_SECRET` 중복 설명 포함.
- `docs/deployment.md`(신규) — Vercel Hobby 배포 8단계 가이드.
- `playwright.smoke.config.ts`(신규) — `SMOKE_BASE_URL` 필수·URL 형식 검증, webServer 없음.
- `e2e/production-smoke.spec.ts`(신규) — 미인증 `/`·`/runs` 리다이렉트, `/login` 200+폼, `/api/dispatch/worker` 401 4개 시나리오.
- `playwright.config.ts` — `testIgnore`로 `production-smoke.spec.ts`를 일반 `test:e2e`에서 제외(리뷰 patch).
- `package.json`(root) — `test:smoke` 스크립트 추가.
- `apps/web/next-env.d.ts` — `next dev` 실행 중 자동 재생성(비의도적, 무해).

**리뷰 결과 (2026-09-02 pass):**
- blind-hunter/edge-case-hunter/verification-gap/intent-alignment 4개 레이어 병렬 실행. patch 3건(medium 2, low 1) 확정 및 전부 수정·재검증 완료: ① `playwright.config.ts`에 `production-smoke.spec.ts` 제외 처리(일반 `test:e2e`에 새 spec이 의도치 않게 함께 실행되던 문제), ② `playwright.smoke.config.ts`의 `SMOKE_BASE_URL` 형식 검증 추가, ③ `docs/deployment.md`에 Vercel Git Fork Protection 유지 경고 추가. defer 1건(medium) — `INTERNAL_CRON_SECRET`/`CRON_CALLBACK_SECRET` 이름 중복은 story 1.10 이전부터의 기존 상태라 frontmatter `deferred`에 기록. dismissed 11건 — 전부 spec의 명시적 Boundaries/Never, epics.md AC 범위, 기존 리포 관례, 또는 검증 가능한 결과 부재를 근거로 기각(세부 근거는 Review Triage Log 참고).
- intent-alignment 레이어가 지적한 "sprint 동기화·git commit 미완료"는 diff 자체의 결함이 아니라 이 워크플로 실행 순서상 아직 도달하지 않은 후속 단계(스프린트 동기화·커밋)였으므로 리뷰 finding으로 분류하지 않았다 — 이 Finalize 단계에서 커밋을 수행하고, 워크플로 종료 후 스프린트 동기화를 별도로 수행한다.

**검증 수행:**
- `npm run typecheck` — 기존 베이스라인 오류(40줄, path-alias 미해결, 이 변경과 무관)와 동일, 신규 오류 없음(변경 전/후 `git stash` 비교로 확인).
- `SMOKE_BASE_URL=http://localhost:3000 npm run test:smoke`(로컬 `next dev` 대상) — 4/4 통과(패치 적용 전/후 모두 재검증).
- `npm run test:e2e` — 4/4 통과, `production-smoke.spec.ts`는 정상적으로 제외됨(패치 적용 후 재검증).
- `diff <(...) .env.local <(...) .env.example` — 키 집합 완전 일치 확인.

**잔여 위험:**
- Vercel 프로젝트 생성·GitHub 연동·Root Directory/환경변수 등록·실제 배포·`SMOKE_BASE_URL=<production-url>`로의 smoke test 실행·인증 화면 육안 확인·Usage Alert 활성화가 전부 미수행 상태다(이 세션에 Vercel 계정 자격증명이 없어 실행 불가) — `docs/deployment.md`의 절차대로 Neo가 직접 수행해야 story 1.11의 실사용 목표(브라우저로 실제 접속 가능)가 완성된다.
- `INTERNAL_CRON_SECRET`/`CRON_CALLBACK_SECRET` 이름 중복은 여전히 남아있다(frontmatter `deferred` 기록, story 1.10부터의 기존 상태).
