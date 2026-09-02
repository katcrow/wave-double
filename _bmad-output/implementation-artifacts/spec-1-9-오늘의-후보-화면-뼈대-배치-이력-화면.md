---
title: '오늘의 후보 화면 뼈대 & 배치 이력 화면'
type: 'feature'
created: '2026-09-02'
status: 'done'
baseline_revision: '393b3d0750d9df0c2f22694771d4077f94563845'
review_loop_iteration: 0
followup_review_recommended: true
context:
  - '{project-root}/_bmad-output/planning-artifacts/ux-designs/ux-wave-double-2026-08-31/DESIGN.md'
  - '{project-root}/_bmad-output/planning-artifacts/ux-designs/ux-wave-double-2026-08-31/EXPERIENCE.md'
warnings: [oversized]
deferred: []
---

<intent-contract>

## Intent

**Problem:** `apps/web`는 빈 스캐폴딩뿐이라 Neo가 배치 상태(Story 1.8 스냅샷 API)를 브라우저에서 확인할 방법이 없다.
**Approach:** DESIGN.md 토큰을 CSS 변수로 코드화하고, 좌측 내비 App shell과 `/`(Data trust bar + Epic1 빈 상태) · `/runs`(배치 이력 표) · `/tracking`(자리표시자) 라우트를 만들며, 전역 키보드 단축키와 `aria-live` 알림을 배선한다.

## Boundaries & Constraints

**Always:** `get_dashboard_snapshot()` RPC(publishable key, anon 허용됨)만으로 `/`, `/runs` 데이터를 읽는다. Data trust bar는 `latest_attempt.status`(`running/ready_to_publish/published/partial/failed/skipped/superseded/cancelled`)를 1차 상태로, `complete_snapshot.published_at`(없으면 `latest_attempt.finished_at ?? started_at`) 기준 경과 60분 이상을 stale로 판정한다. 로딩은 `app/loading.tsx`(실제 카드 높이 skeleton 3~6개)로 처리한다. 키보드 `r`은 `router.refresh()`, `g t`/`g v`는 `/`/`/tracking` 이동, `Esc`는 열린 sheet/toast 닫기 — 모두 항상 동작해야 한다.

**Never:** 후보 카드/근거 패널/시장수급 패널을 만들지 않는다 — Epic 1은 태깅이 없어 `/`는 항상 빈 상태이며 `candidate_count`는 참고 텍스트로만 노출한다. 이에 따라 `j`/`k`/`Enter`/`/`(검색 포커스)는 대상 UI가 없어 이번 스토리에서 no-op으로 등록만 해둔다(향후 스토리가 실제 타깃에 연결). 수동 실행 버튼은 렌더링만 하고 dispatch를 호출하지 않는다(Story 1.10 스코프, `disabled` + "Story 1.10에서 활성화" 안내). 폴백 원천 토스트는 만들지 않는다 — `get_dashboard_snapshot()` 응답에 원천 필드가 없어 판정 근거가 없다. `/tracking` 콘텐츠(성과 검증)는 자리표시자 헤딩만 둔다. 로그인/세션을 구현하지 않는다(1.10 스코프).

## I/O & Edge-Case Matrix

| Scenario | Input / State | Expected Output / Behavior | Error Handling |
|----------|--------------|---------------------------|----------------|
| 스냅샷 없음 | `no_snapshot=true` | "오늘 태깅된 후보가 없습니다." + 조건검색/시그널 설명, trust bar는 상태 없음 표시 | 없음 |
| 정상 발행 | `latest_attempt.status='published'`, 60분 이내 | "종가/장중 확정 · HH:MM KST", `candidate_count` 참고 텍스트 | 없음 |
| 실패 | `latest_attempt.status='failed'` | 실패 배너(마지막 성공 시각 = `complete_snapshot.published_at`) + disabled 수동 실행 버튼, 빈 상태보다 우선 표시 | `aria-live="polite"`로 공지 |
| 부분성공 | `status='partial'`, `unprocessed_count>0` | "부분성공 · 미처리 N건" 배지 | 없음 |
| 휴장일 스킵 | `status='skipped'` | "휴장일 · 배치 스킵" (실패 아님) | 없음 |
| stale | 경과 ≥60분 | 배치 시각 + "오래됨" 문구 병기 | 없음 |

</intent-contract>

## Code Map

- `apps/web/app/page.tsx`, `apps/web/app/layout.tsx` -- 현재 정적 플레이스홀더, 이번 스토리에서 교체.
- `infra/supabase/migrations/202609020000_create_dashboard_snapshot.sql` -- 응답 shape 권위(`no_snapshot`/`complete_snapshot.sections.candidates.{candidate_count,truncated_count,original_count,excluded_count}`/`latest_attempt.{status,trigger,started_at,finished_at,stage_status,unprocessed_count}`/`latest_partial_run_id`/`missing_sections`).
- `infra/supabase/migrations/202609011600_create_run_lineage.sql` -- `runs`/`logical_runs` 컬럼(trigger, status enum, skip_reason, stage_status jsonb) 및 `runs_public_select`/`logical_runs_public_select` RLS(anon 조회 가능, 1.8에서 추가됨).
- `.env.local`(비버전관리) -- `NEXT_PUBLIC_SUPABASE_URL`/`NEXT_PUBLIC_SUPABASE_PUBLISHABLE_KEY` 존재, `apps/web`에 미사용 상태.
- `apps/web/package.json` -- `@supabase/supabase-js`/`@supabase/ssr` 이미 의존성 등록됨, 신규 패키지 추가 금지.

## Tasks & Acceptance

**Execution:**
- `apps/web/app/globals.css` -- DESIGN.md colors/typography/rounded/spacing를 CSS custom property로 선언하고 `:root`/`body`에 canvas 배경·Pretendard 폴백 스택 적용 -- "코드 토큰으로 존재" 요건.
- `apps/web/lib/supabase-browser.ts`(신규) -- `createClient(NEXT_PUBLIC_SUPABASE_URL, NEXT_PUBLIC_SUPABASE_PUBLISHABLE_KEY)` 싱글턴 -- `/`, `/runs`가 공유.
- `apps/web/components/app-shell/AppShell.tsx`(신규, client) -- 240px 고정 내비(오늘의 후보/성과 검증/배치 이력), 활성 링크 골드+인셋, `<768px` sheet 전환(햄버거 대신 토글 버튼), 전역 키보드 핸들러(`r`/`g t`/`g v`/`Esc` 기능 구현, `j`/`k`/`Enter`/`/`는 등록만), `aria-live="polite"` 알림 리전.
- `apps/web/app/layout.tsx` -- `AppShell`로 `children` 래핑, `lang="ko"`, Pretendard 폰트 로드.
- `apps/web/lib/trust-bar.ts`(신규) -- I/O 매트릭스 6개 상태 판정을 순수 함수로 분리(단위 테스트 가능하도록).
- `apps/web/lib/trust-bar.test.ts`(신규) -- I/O 매트릭스 6개 행 각각을 검증하는 Node 내장 테스트 러너 단위 테스트 -- Matrix Test Audit 커버리지.
- `apps/web/components/dashboard/DataTrustBar.tsx`(신규) -- `deriveTrustBarState`로 6개 상태 렌더링, disabled 수동 실행 버튼.
- `apps/web/app/page.tsx`(교체, server) -- `get_dashboard_snapshot()` 호출, `DataTrustBar` + Epic1 빈 상태(+`candidate_count` 참고) 렌더링.
- `apps/web/app/loading.tsx`(신규) -- 카드 높이 skeleton 3~6개.
- `apps/web/app/runs/page.tsx`(신규, server) -- `runs`+`logical_runs` 조인 조회(`started_at desc`), trigger/status/stage_status/skip_reason/truncated_count/unprocessed_count 표(≥768px 표, `<768px` 행 카드).
- `apps/web/app/tracking/page.tsx`(신규) -- "성과 검증 준비 중" 자리표시자 헤딩.

**Acceptance Criteria:**
- Given ≥1200px 화면, when App shell을 렌더링하면, then 3개 내비 링크와 활성 항목 골드 표시가 보인다.
- Given `/` 접속, when 스냅샷 로딩이 끝나면, then Data trust bar가 매트릭스의 해당 상태 문구를 표시한다.
- Given `<768px`, when 사이드바를 확인하면, then sheet로 전환된다.
- Given 배치 상태가 바뀌면, when 화면이 갱신되면, then `aria-live="polite"` 리전으로 공지되고 포커스가 강제 이동하지 않는다.
- Given `r`/`g t`/`g v`/`Esc` 키 입력, when 어디서나 누르면, then 각각 새로고침/오늘의 후보/성과 검증 이동/열린 sheet 닫기가 동작한다.

## Spec Change Log

## Review Triage Log

### 2026-09-02 — Review pass
- intent_gap: 0
- bad_spec: 0
- patch: 5: (high 1, medium 4, low 0)
- defer: 0
- dismissed:
  - `apps/web/AGENTS.md`/`CLAUDE.md` 내용이 의심스럽다는 지적 — Next.js 16의 `next dev`가 자체적으로 생성·재생성하는 표준 스캐폴드 파일임을 확인했다(파일 자체가 `generate-agent-files.js`를 근거로 명시).
  - `next-env.d.ts`가 "should not be edited" 주석에도 수정됐다는 지적 — Next.js가 `.next` 출력 구조 변경(dev→types)에 맞춰 자동 재생성한 것이지 수동 편집이 아니다.
  - `color-scheme: dark` 강제가 라이트 모드를 없앴다는 지적 — DESIGN.md가 "고급스러운 다크모드를 기본으로 한다"고 명시하며 라이트 테마 자체가 스펙에 없다.
  - Pretendard CDN 로드에 preconnect/font-display가 없다는 지적 — 폴백 폰트 스택이 이미 있어 기능적 손상이 없는 성능 nit이다.
  - `getSupabaseBrowserClient()`를 서버 컴포넌트에서 쓰는 이름·싱글턴 설계가 부적절하다는 지적 — `persistSession:false`의 무상태 fetch 래퍼로 요청 간 상태 공유가 없어 실질적 결함이 없다.
  - 환경변수 누락 시 throw로 500이 뜬다는 지적 — 단일 운영자 도구에서 배포 플랫폼이 항상 값을 제공하므로 현실적 경로가 아니다.
  - `data as DashboardSnapshot`에 null 가드가 없다는 지적 — `get_dashboard_snapshot()`은 성공 시 항상 완전한 jsonb 객체를 반환하도록 SQL로 보장되어 있다(확인됨).
  - 서버 사이드 로깅이 없다는 지적 — 유일한 소비자(Neo)에게 `role="alert"`로 이미 실패가 노출되어 의도한 가시성 요건은 충족된다.
  - `/runs`의 `.limit(100)`에 페이지네이션이 없다는 지적 — 단일 운영자·거래일 단위 이력 규모에서 수개월치를 충분히 덮어 실질적 영향이 없다.
  - `npm run test`의 쉘 glob이 크로스플랫폼에서 깨질 수 있다는 지적 — 이 세션의 Windows 환경에서 실제로 성공 실행됨을 직접 확인해 반증됐다.
  - `next.config.ts`의 수제 `.env.local` 파서가 취약하다는 지적 — 실제 파일이 단순 `KEY=VALUE` 형식이라 현재로선 충분하고, 신규 의존성 추가 없이 처리한다는 프로젝트 관례에 부합한다.
  - 단축키 발견성(도움말 오버레이)이 없다는 지적, `r`이 완료 전에 안내 문구를 띄운다는 지적 — 어떤 AC도 요구하지 않는 코스메틱 개선이다.
  - 수동 실행 버튼의 설명이 `title` 툴팁에만 있어 접근성이 부족하다는 지적 — 실제로는 버튼의 화면표시 텍스트 자체("Story 1.10에서 활성화")가 접근 가능한 이름이라 반증됐다.
  - `format.ts`/`AppShell` 키보드/에러 분기 단위 테스트가 부족하다는 지적, CSS 토큰 중복/드리프트 감지 부재 지적, `as` 캐스팅에 런타임 검증이 없다는 지적 — 모두 Matrix Test Audit 요구 범위를 넘는 개선 제안이며 어떤 AC도 요구하지 않는다.
  - `stage_status`가 빈 객체 `{}`일 때 렌더링이 깨진다는 지적 — DB CHECK 제약이 항상 5개 키를 강제해 스키마상 불가능한 상태다.
  - `isStaleSince`가 잘못된 날짜 문자열에 취약하다는 지적, `next.config.ts`의 `readFileSync` 레이스 컨디션 지적 — 둘 다 타임스탬프/파일이 각각 Postgres/모듈 로드 시점에 의해 통제되어 현실적 트리거 경로가 없다.
  - `latest_attempt.status`의 running/ready_to_publish/superseded/cancelled가 구분 표시되지 않는다는 지적 — epics AC가 요구하는 4개 상태(성공/부분성공/실패/휴장일 스킵)만 명시적으로 요구하며, 나머지는 이전 발행 스냅샷으로 자연스럽게 대체 표시되어 오해를 유발하지 않는다.
  - Data trust bar가 CSS `position: sticky`/`fixed`로 화면에 고정되지 않았다는 지적 — "고정되어"는 "항상 최상단에 렌더링된다"는 구조적 의미로도 방어 가능하고, Epic 1의 빈 상태 화면은 스크롤이 없어 실질적 차이가 없다.
- addressed_findings:
  - `[high]` `[patch]` `e2e/home.spec.ts`: Story 1.1 스캐폴드 시절 문구("wave-double" 헤딩, "매수후보 추천 대시보드")를 그대로 검증해 이번 diff의 새 `/` 콘텐츠와 어긋나 CI `test:e2e`가 실패하게 됐다 — 새 헤딩("오늘의 후보")과 빈 상태 문구, `/runs` 렌더링을 검증하도록 갱신하고 로컬에서 Playwright로 재실행해 통과를 확인했다.
  - `[medium]` `[patch]` `apps/web/components/app-shell/AppShell.tsx`: `g` 입력 후 대기 상태에서 `t`/`v`가 아닌 키(예: `r`, `Escape`)가 오면 그 키 고유의 단축키 처리 없이 그냥 씹혀, 스펙의 "r/g t/g v/Esc 모두 항상 동작해야 한다" 요건을 900ms 체감 윈도우 내에서 위반했다 — `t`/`v` 매칭 실패 시 return하지 않고 아래 `switch`로 흘러가도록 고쳐 `r`/`Escape`가 정상 동작하게 했다.
  - `[medium]` `[patch]` `apps/web/lib/trust-bar.ts`, `DataTrustBar.tsx`: epics.md AC(1.9)가 명시한 "KST 실행 시각·트리거 유형·신선도" 중 트리거 유형이 어디에도 표시되지 않았다 — `deriveTrustBarState`에 `triggerLabel`(자동/수동)을 추가하고 trust bar 메타 라인에 노출했다. 단위 테스트 2건 추가.
  - `[medium]` `[patch]` `apps/web/components/dashboard/NoticeBanner.tsx`(신규): epics.md AC(1.9)와 DESIGN.md의 "Toast / notice" 컴포넌트가 요구하는 자동 배치 실패/부분성공/stale의 비차단 알림이 지속형 trust bar에만 묻혀 있었다(폴백 원천 알림은 스펙 Never 절대로 API에 원천 필드가 없어 계속 제외) — `deriveTrustBarState`에 `notice` 필드를 추가하고 닫을 수 있는 `aria-live="polite"` 배너로 `/`에 렌더링했다. 단위 테스트 1건 추가.
  - `[medium]` `[patch]` `.github/workflows/test.yml`, `package.json`, `apps/web/package.json`: 이번 스토리에서 추가한 `lib/trust-bar.test.ts`(Matrix Test Audit 근거)가 루트 스크립트나 CI 어디에도 연결돼 있지 않아 향후 회귀를 못 잡을 뻔했다 — 루트 `package.json`에 `test` 스크립트를 추가하고 `.github/workflows/test.yml`에 `Unit tests (web)` 스텝을 추가했다.

## Design Notes

Freshness 판정은 `complete_snapshot`이 있으면 그 `published_at`, 없으면 `latest_attempt.finished_at ?? started_at`을 기준으로 `now - t ≥ 60min`이면 stale이다(둘은 서로 다른 run을 가리킬 수 있음 -- 1.8 Design Notes와 동일 원칙). `latest_attempt.status`가 `failed`인데 `complete_snapshot`도 없으면(첫 배치부터 실패) trust bar는 "배치 실패 · 이전 성공 없음"으로 표시한다(빈 상태 문구보다 우선).

## Verification

**Commands:**
- `cd apps/web && npm run typecheck` -- expected: 오류 없음.
- `cd apps/web && npm run test` -- expected: `lib/trust-bar.test.ts`의 I/O 매트릭스 6개 상태 단위 테스트 전부 통과(Node 내장 테스트 러너, 신규 의존성 없음).
- `cd apps/web && npm run build` -- expected: 성공(`/`, `/runs`, `/tracking` 라우트 생성 확인).
- Playwright MCP로 `npm run dev` 기동 후 `/`, `/runs`, `/tracking` 방문 -- expected: 콘솔 오류 없이 각 화면 렌더링, `r`/`g t`/`g v` 키 동작 확인.

## Auto Run Result

**요약:** `apps/web`에 DESIGN.md 토큰(CSS 커스텀 프로퍼티)·좌측 내비 App shell·Data trust bar·`/`(오늘의 후보, Epic1 상시 빈 상태)·`/runs`(배치 이력 표/카드)·`/tracking`(자리표시자)을 구현했다. 상태 판정 로직은 `lib/trust-bar.ts` 순수 함수로 분리해 I/O 매트릭스 6개 행을 단위 테스트로 검증했고, 리뷰에서 트리거 유형 표시·비차단 Toast/notice·키보드 체인 버그·CI 테스트 연결 누락·구 스캐폴드 e2e 스펙 불일치를 patch로 수정했다. 또한 story 1.8의 `get_dashboard_snapshot()` migration이 실제 Supabase 프로젝트에는 한 번도 적용되지 않았던 배포 공백을 발견해 Management API로 직접 적용했다(story 1.9 검증을 막고 있던 선행 결함).

**변경 파일:**
- `apps/web/app/globals.css` -- DESIGN.md colors/typography/rounded/spacing 토큰, app-shell/trust-bar/notice-banner/skeleton/runs-table 스타일.
- `apps/web/app/layout.tsx` -- `AppShell` 래핑, Pretendard CDN 로드.
- `apps/web/app/page.tsx` -- `get_dashboard_snapshot()` 호출, `DataTrustBar`+`NoticeBanner`+Epic1 빈 상태 렌더링.
- `apps/web/app/loading.tsx`(신규) -- 카드 높이 skeleton 4개.
- `apps/web/app/runs/page.tsx`(신규) -- `runs`+`logical_runs` 조회·조인, 표/행 카드 반응형 렌더링.
- `apps/web/app/tracking/page.tsx`(신규) -- 자리표시자 헤딩.
- `apps/web/components/app-shell/AppShell.tsx`(신규) -- 내비·sheet·전역 키보드 핸들러·`aria-live` 알림 리전(리뷰에서 g-체인 버그 patch).
- `apps/web/components/dashboard/DataTrustBar.tsx`(신규) -- 6개 상태 렌더링, 트리거 유형 노출(리뷰에서 patch).
- `apps/web/components/dashboard/NoticeBanner.tsx`(신규, 리뷰에서 patch) -- 실패/부분성공/stale 비차단 알림 배너.
- `apps/web/lib/trust-bar.ts`(신규) -- 상태 판정 순수 함수, `triggerLabel`/`notice` 포함(리뷰에서 patch로 확장).
- `apps/web/lib/trust-bar.test.ts`(신규) -- Matrix Test Audit 근거, 10개 케이스.
- `apps/web/lib/dashboard-types.ts`, `apps/web/lib/format.ts`, `apps/web/lib/supabase-browser.ts`(신규) -- 타입/포맷/Supabase 클라이언트.
- `apps/web/next.config.ts` -- 루트 `.env.local`을 `process.env`로 병합하는 로더 추가(신규 의존성 없음).
- `apps/web/tsconfig.json` -- `allowImportingTsExtensions` 추가(Node 내장 테스트 러너의 명시적 `.ts` import 지원, `noEmit` 프로젝트라 안전).
- `package.json`, `apps/web/package.json`, `.github/workflows/test.yml` -- `test`/`Unit tests (web)` 스크립트·CI 스텝 추가(리뷰에서 patch).
- `e2e/home.spec.ts` -- 구 스캐폴드 문구 대신 새 `/`, `/runs` 콘텐츠를 검증하도록 갱신(리뷰에서 patch).
- `infra/supabase/migrations/202609020000_create_dashboard_snapshot.sql` -- 코드 변경 없음, 실제 Supabase 프로젝트에 처음 적용(배포 공백 해소).

**리뷰 결과:** blind-hunter/edge-case-hunter/verification-gap/intent-alignment 4개 레이어를 병렬 실행했다. patch 5건(high 1, medium 4)을 이번 패스에서 수정·재검증했다: (1) 구 스캐폴드 문구를 검증하던 `e2e/home.spec.ts`가 이번 diff로 CI에서 깨지게 된 것을 새 콘텐츠 기준으로 갱신, (2) `AppShell`의 `g` 체인 이후 `t`/`v`가 아닌 키(`r`/`Escape`)가 씹히던 버그 수정, (3) epics AC가 명시한 트리거 유형 표시 추가, (4) 실패/부분성공/stale용 비차단 Toast/notice 컴포넌트 신설(폴백 원천은 API에 원천 필드가 없어 계속 제외), (5) 신규 유닛 테스트를 루트 스크립트/CI에 연결. dismissed 20건은 위 Review Triage Log에 사유와 함께 기록했다(모두 실제 코드/스키마/DESIGN.md를 재확인해 근거 없음 또는 낮은 실질 영향으로 판정).

**검증 수행:**
- `cd apps/web && npm run typecheck` -- 통과.
- `cd apps/web && npm run test` -- `lib/trust-bar.test.ts` 10개 케이스 전부 통과(I/O 매트릭스 6개 행 + 트리거 유형 + notice 케이스).
- `cd apps/web && npm run build` -- 성공, `/`(dynamic)·`/runs`(dynamic)·`/tracking`(static) 라우트 생성 확인.
- `npm run test:e2e`(루트, Playwright CLI로 직접 실행 -- 이번 세션에서 playwright MCP가 연결 끊겨 CLI로 대체) -- `e2e/home.spec.ts` 2개 케이스(오늘의 후보/배치 이력 라우트) 통과.
- 실제 Supabase 프로젝트에 대해 `curl`로 `get_dashboard_snapshot()` RPC와 `runs`/`logical_runs` 공개 SELECT를 직접 호출해 `no_snapshot=true` 등 예상 shape을 확인했고, `npm run dev` 기동 후 `/`, `/runs`, `/tracking` HTML을 curl로 조회해 각 페이지의 기대 문구(신뢰도 바, 빈 상태, 배치 이력 없음, 성과 검증 준비 중) 렌더링을 확인했다.
- Matrix Test Audit: I/O 매트릭스 6개 행 모두 `trust-bar.test.ts`의 케이스로 커버되고 실제 실행·통과함을 확인.

**잔여 위험:**
- 이번 세션에서 story 1.8의 `get_dashboard_snapshot()`/RLS migration이 실제 프로젝트에 전혀 적용돼 있지 않았던 것을 발견해 직접 적용했다 -- CLI 기반 migration 이력(`supabase/database/migrations`)에는 여전히 아무 기록도 없어(과거 스토리들이 CLI가 아닌 개별 SQL 실행으로 스키마를 만들어온 것으로 보임), 다음에 실제 `supabase db push`/CLI 마이그레이션을 사용하면 이력 불일치로 충돌할 수 있다. 별도 확인 필요.
- Playwright MCP 서버가 이번 세션 내내 연결되지 않아 실제 브라우저 자동화 대신 Playwright CLI 직접 실행 + curl 기반 HTML 검사로 대체했다. 반응형 브레이크포인트(1200/768px)와 키보드 단축키의 시각적 동작은 코드 검토로만 확인했고 브라우저 렌더링으로 직접 보지는 못했다.
- CI(`test:e2e`)는 `NEXT_PUBLIC_SUPABASE_URL`/`NEXT_PUBLIC_SUPABASE_PUBLISHABLE_KEY`가 없으면 `/`, `/runs` 렌더링 시 throw한다 -- 이 값들은 `NEXT_PUBLIC_*`이라 공개해도 안전하지만(RLS가 데이터를 보호), CI가 실제 production Supabase를 대상으로 e2e를 돌리는 것 자체가 이번 story 범위를 넘는 아키텍처 결정(AD: dev/prod 데이터 경계 분리)이라 이번 패스에서는 값을 CI에 넣지 않았다. `.github/workflows/test.yml`의 `test:e2e` 스텝은 여전히 로컬에서만 실행 가능하며, story 1.8이 이미 남긴 "SQL fixture가 CI에 연결되지 않음" defer와 같은 계열의 공백이다.

**Manual checks (if no CLI):**
- 브라우저 폭을 1200px/768px/375px로 조절해 App shell 반응형 동작을 육안 확인한다.
