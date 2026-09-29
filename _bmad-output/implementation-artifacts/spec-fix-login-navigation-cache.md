---
title: '로그인 직후 대시보드 데이터 표시'
type: 'bugfix'
created: '2026-09-29'
status: 'done'
baseline_commit: 'd880a86723723c411c869e8ee1c8e361637098c7'
review_loop_iteration: 0
context: []
---

<frozen-after-approval reason="human-owned intent — do not modify unless human renegotiates">

## Intent

**Problem:** 운영 환경에서 로그인 성공 후 `/`로 이동하면 대시보드 데이터가 즉시 표시되지 않고, 브라우저 새로고침 뒤에야 표시된다. 로그인 화면에 보호 라우트 링크가 존재하고 운영 환경의 Next.js Link prefetch가 인증 전 응답을 캐시할 수 있어, 클라이언트 전환 결과가 stale RSC 상태를 사용할 가능성이 있다.

**Approach:** 로그인 성공 후 보호 라우트를 클라이언트 라우터 캐시에 의존하지 않는 전체 문서 이동으로 연다. 로그인 화면에서는 보호 라우트 prefetch를 비활성화해 인증 전 `/` 응답이 로그인 전환에 재사용되지 않도록 한다.

## Boundaries & Constraints

**Always:** Supabase `signInWithPassword` 성공 여부와 기존 오류 표시를 유지한다. 인증 쿠키가 저장된 뒤 서버의 `proxy`가 인증 상태를 확인하는 `/` 요청이 발생해야 한다. 기존 대시보드, 로그아웃, 내비게이션 동작과 unrelated worktree 변경은 보존한다.

**Never:** Supabase 인증 방식, proxy 인증 게이트, 대시보드 RPC, 공개 회원가입 정책을 변경하지 않는다. 비밀값을 코드·로그·테스트에 추가하지 않는다.

## I/O & Edge-Case Matrix

| Scenario | Input / State | Expected Output / Behavior | Error Handling |
|----------|--------------|---------------------------|----------------|
| HAPPY_PATH | 유효한 운영자 이메일/비밀번호 | 로그인 성공 후 `/`가 전체 문서 요청으로 열리고 후보 데이터가 첫 화면에 표시됨 | N/A |
| AUTH_ERROR | 잘못된 이메일/비밀번호 | 현재 페이지에 오류 메시지가 표시되고 `/`로 이동하지 않음 | 기존 Supabase 오류 메시지 유지 |
| PREFETCHED_ROUTE | 로그인 전 `/` 링크가 prefetch된 상태 | 로그인 성공 후 stale prefetch 결과를 사용하지 않고 인증된 서버 렌더링 수행 | 새로고침 없이 데이터 표시 |

</frozen-after-approval>

## Code Map

- `apps/web/app/login/page.tsx:19-38` -- `signInWithPassword` 성공 후 현재 `router.push('/')`와 `router.refresh()`를 수행하는 로그인 제출 흐름. 성공 후 전체 문서 이동으로 교체할 대상.
- `apps/web/components/app-shell/AppShell.tsx:120-145` -- 로그인 화면에도 공통으로 렌더되는 주요 내비게이션. `/` 보호 링크의 prefetch 정책을 pathname에 맞게 조정할 대상.
- `apps/web/proxy.ts:20-82` -- `/` 요청에서 Supabase 쿠키 세션을 확인하는 보호 게이트. 인증 후 첫 서버 요청이 이 게이트를 통과해야 한다.
- `apps/web/app/page.tsx:21-150` -- 서버에서 snapshot 및 후보 RPC를 호출하는 대시보드. 로그인 성공 직후 서버 렌더링 데이터가 표시되는지 검증 기준이다.
- `e2e/authenticated-dashboard.spec.ts:3-31` -- mock Supabase 로그인 후 `/` 후보 표면을 검증하는 기존 Playwright 계약. 회귀 검증에 재사용한다.

## Tasks & Acceptance

**Execution:**
- [x] `apps/web/app/login/page.tsx` -- 로그인 성공 후 `window.location.replace('/')` 기반 전체 이동을 수행하도록 수정 -- stale App Router 상태를 제거하고 인증 쿠키를 포함한 서버 요청을 보장한다.
- [x] `apps/web/components/app-shell/AppShell.tsx` -- 로그인 pathname에서 보호 링크 prefetch를 비활성화하도록 수정 -- 인증 전 보호 라우트 응답의 prefetch 재사용을 차단한다.
- [x] `e2e/authenticated-dashboard.spec.ts` 또는 관련 E2E -- 로그인 직후 후보 데이터 표시 회귀를 검증 -- 수정된 사용자 흐름을 자동화한다.

**Acceptance Criteria:**
- Given 유효한 운영자 인증 정보, when 로그인 버튼을 제출하면, then 브라우저 새로고침 없이 `/`의 후보 데이터와 대시보드 UI가 표시된다.
- Given 잘못된 인증 정보, when 로그인 버튼을 제출하면, then 로그인 페이지에 오류가 표시되고 보호 라우트로 이동하지 않는다.
- Given 로그인 페이지에서 `/` 링크가 prefetch된 상태, when 로그인에 성공하면, then prefetch된 인증 전 결과가 재사용되지 않는다.
- Given 기존 unrelated worktree 변경, when 수정과 검증을 완료하면, then 해당 변경은 그대로 남는다.

## Spec Change Log

## Review Triage Log

- Applied patch: 로그인 성공의 전체 문서 이동을 직접 확인하도록 인증 E2E에 navigation-request assertion을 추가했다. 기존 URL/UI assertion만으로는 stale RSC 회귀를 잡지 못한다는 finding을 해결했다.
- Applied patch: `/login`뿐 아니라 `/login/` 하위 경로에서도 보호 링크 prefetch를 비활성화했다. proxy의 public-path 범위와 UI 정책을 일치시켰다.
- Applied patch: mock Supabase가 `refresh_token` grant를 유효 세션으로 처리하도록 보완했다. 전체 문서 이동 뒤 자동 세션 갱신이 비밀번호 오류로 오인되지 않게 했다.
- Applied patch: dispatch smoke의 토큰 interception 패턴이 query string을 포함하도록 수정하고 오류 주석을 실제 동작에 맞췄다.
- Dismissed: 체결강도·전략 B·backtest baseline 관련 findings는 이번 로그인 변경의 소비 경로가 아니며 기존 unrelated worktree 변경에 속한다. 해당 코드에는 수정하지 않았다.
- Dismissed: 기존 `review-prompt-*.md` 파일 관련 finding은 이번 작업에서 생성·수정한 파일이 아닌 기존 unrelated worktree 산출물이다. 삭제하거나 포함하지 않았다.
- Dismissed: 후보 partial-vanish, 전략 G, tracking query 관련 전체 E2E 실패는 이번 로그인 변경의 직접 consequence가 아니며 인증 핵심 E2E와 분리된 기존 시나리오 불일치다.

## Verification

**Commands:**
- `npm run typecheck` -- expected: TypeScript 검사 성공
- `npm test` -- expected: 웹 단위 테스트 전체 성공
- `npm run test:e2e -- e2e/authenticated-dashboard.spec.ts` -- expected: 로그인 직후 후보 표면 테스트 성공
- `npm run test:e2e -- e2e/authenticated-dashboard.spec.ts e2e/dispatch-smoke.spec.ts` -- expected: 로그인·전체 문서 이동·dispatch 인증 회귀 테스트 6개 성공
- `npm run build` -- expected: production build 성공

## Suggested Review Order

**인증 후 이동**

- 로그인 성공 뒤 브라우저 라우터 캐시를 거치지 않고 보호 서버 렌더링을 시작한다.
  [`page.tsx:32`](../../apps/web/app/login/page.tsx#L32)

- 로그인 페이지에서 인증 전 보호 라우트 prefetch를 차단한다.
  [`AppShell.tsx:24`](../../apps/web/components/app-shell/AppShell.tsx#L24)

- 하위 로그인 경로도 동일한 prefetch 정책을 적용한다.
  [`AppShell.tsx:136`](../../apps/web/components/app-shell/AppShell.tsx#L136)

**회귀 검증**

- 잘못된 인증 정보가 로그인 페이지에 남는지 확인한다.
  [`authenticated-dashboard.spec.ts:3`](../../e2e/authenticated-dashboard.spec.ts#L3)

- 성공 로그인 후 실제 document navigation과 후보 렌더링을 확인한다.
  [`authenticated-dashboard.spec.ts:14`](../../e2e/authenticated-dashboard.spec.ts#L14)

- 전체 이동과 호환되는 refresh-token mock 및 dispatch 토큰 캡처를 확인한다.
  [`mock-supabase-server.mjs:395`](../../e2e/mock-supabase-server.mjs#L395)

- query string을 포함한 토큰 interception으로 CSRF 회귀를 검증한다.
  [`dispatch-smoke.spec.ts:36`](../../e2e/dispatch-smoke.spec.ts#L36)
