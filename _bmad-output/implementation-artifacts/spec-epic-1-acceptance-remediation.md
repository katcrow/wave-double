---
title: 'Epic 1 운영 수용 기준 보정'
type: 'bugfix'
created: '09-02-2026'
status: 'in-progress'
review_loop_iteration: 0
baseline_commit: 'b15ee2bc711fd2f99768db42534d81efe6558c91'
context:
  - '{project-root}/AGENTS.md'
  - '{project-root}/_bmad-output/implementation-artifacts/epic-1-retro-09-02-2026.md'
---

<frozen-after-approval reason="human-owned intent — do not modify unless human renegotiates">

## Intent

**Problem:** Epic 1의 12개 스토리는 완료됐지만, 루트 TypeScript CI가 실패하고 운영 Supabase에는 dashboard/dispatch 관련 migration이 적용되지 않았다. 따라서 수동 실행·배치 이력·RLS 보호가 실제 운영에서 성립하지 않으며 회고 판정이 rejected다.

**Approach:** 로컬 검증 계약(TypeScript, CSP, migration/read-model CI)을 바로잡고, 기존의 forward-only migration을 운영 프로젝트에 순서대로 적용한다. 적용 후에는 운영 DB의 RLS·RPC·snapshot/outbox 계약과 브라우저 렌더링을 실제로 검증해 Epic 1 수용 근거를 갱신한다.

## Boundaries & Constraints

**Always:** 루트 `npm run typecheck`와 앱 typecheck가 모두 통과해야 한다. `logical_runs`·`runs`는 Story 1.8의 공개 SELECT 정책이 적용된 RLS 상태여야 하고, 후보/dispatch 원장은 직접 공개하지 않는다. migration은 현재 운영 프로젝트 `qqhjeumlecaudsiqhhdu`에 forward-only로 적용하며, 적용 전후 Supabase MCP로 실제 상태를 검증한다. CSP 변경 뒤 Playwright MCP에서 Pretendard stylesheet 오류가 없어야 한다.

**Never:** 기존 `backtest/` 전략 커널을 변경하지 않는다. migration 이력 수정·삭제, 운영 DB의 reset, secret 값의 출력/저장은 금지한다. RLS를 정책 없이 활성화하거나 browser role에 service RPC 권한을 주지 않는다.

## I/O & Edge-Case Matrix

| Scenario | Input / State | Expected Output / Behavior | Error Handling |
|----------|---------------|----------------------------|----------------|
| CI typecheck | workspace root | alias와 `.ts` import를 해석해 exit 0 | 오류가 있으면 CI가 실패한다 |
| 운영 migration | latest remote = `202609012110` | `12200`~`21100`이 순서대로 적용되고 dashboard/dispatch 객체가 생긴다 | 적용 실패 시 중단하고 실제 remote state를 기록한다 |
| 운영 RLS | migration `020000` 적용 후 | `logical_runs`·`runs`는 RLS enabled, anon/authenticated SELECT만 허용 | candidate/dispatch 테이블에는 직접 policy를 추가하지 않는다 |
| 브라우저 UI | `/login` 로드 | CSP console error 없이 Pretendard stylesheet가 허용된다 | 외부 font origin만 style/font-src에 최소 허용한다 |
| migration CI | clean Postgres | 모든 SQL fixture가 schema 순서대로 실행된다 | pg_cron/pg_net 전용 migration은 service DB에서만 검증하고 CI에는 명시적으로 제외한다 |

</frozen-after-approval>

## Code Map

- `tsconfig.json` -- root `typecheck`가 사용하는 설정; `apps/web/tsconfig.json`의 alias/extension 설정과 정합해야 한다.
- `apps/web/next.config.ts` -- 전역 CSP header; layout의 jsDelivr Pretendard stylesheet와 허용 origin을 맞춘다.
- `apps/web/app/layout.tsx` -- Pretendard CDN stylesheet를 선언하는 UI 진입점.
- `infra/supabase/migrations/202609012200_add_candidate_fallback_support.sql` ~ `202609021100_schedule_dispatch_worker_cron.sql` -- 아직 remote에 없는 forward-only Epic 1 운영 계약.
- `infra/supabase/migrations/202609020000_create_dashboard_snapshot.sql` -- `logical_runs`/`runs` RLS policy와 read-only snapshot RPC의 권위.
- `infra/supabase/migrations/202609021000_create_dispatch_outbox.sql` -- service-role-only dispatch RPC와 RLS deny-all outbox 원장.
- `.github/workflows/test.yml` -- root typecheck, build, Playwright 및 현재 dispatch SQL fixture CI.
- `tests/sql/*.sql` -- run lineage, candidate, fallback, skip, dashboard snapshot, dispatch outbox의 실제 DB fixture.
- `packages/read-model/src/index.ts` -- 현재 빈 read-model package; generated database type export 경계를 마련할 위치.
- `e2e/*.spec.ts`, `playwright.config.ts` -- 보호 경로와 browser smoke의 기존 자동 검증 범위.

## Tasks & Acceptance

**Execution:**

- [ ] `tsconfig.json`, `package.json` -- root typecheck가 web alias와 TS extension import 규칙을 일관되게 검사하도록 보정하고 CI failure를 재현·해소한다.
- [ ] `apps/web/next.config.ts`, `apps/web/app/layout.tsx`, `e2e/production-smoke.spec.ts` -- CSP와 Pretendard 제공 origin을 최소 권한으로 일치시키고 browser console regression을 검증한다.
- [ ] `packages/read-model/src/database.types.ts`, `packages/read-model/src/index.ts`, generation verification script -- 운영 schema에서 생성한 DB 타입을 export하고 재생성 diff가 CI에서 검출되게 한다.
- [ ] `.github/workflows/test.yml`, `tests/sql/*.sql` -- clean Postgres migration/fixture matrix를 모든 Epic 1 SQL contract로 확장하고 pg_cron/pg_net의 별도 운영 검증 경계를 명시한다.
- [ ] `infra/supabase/migrations/*`, 운영 Supabase -- 누락된 기존 migration을 번호 순서대로 적용하고 RLS, RPC grant, snapshot/outbox fixture를 실제 DB에서 확인한다.
- [ ] `_bmad-output/implementation-artifacts/epic-1-retro-09-02-2026.md`, `sprint-status.yaml` -- 검증 증거와 action item 상태를 결과에 맞게 갱신한다.

**Acceptance Criteria:**

- Given the repository root, when `npm run typecheck` runs, then it exits successfully and checks the same web source surface as the app configuration.
- Given the production project, when all pending Epic 1 migrations are applied, then dashboard snapshot and manual dispatch/outbox database objects exist and the remote migration history reaches `202609021100`.
- Given remote `logical_runs` and `runs`, when the security advisor and grants are inspected, then RLS is enabled and browser roles cannot execute service-only run/dispatch RPCs.
- Given the login page, when it is opened through Playwright MCP, then no CSP error blocks the Pretendard stylesheet.
- Given a clean CI database, when Epic 1 SQL fixtures run, then lineage, candidates/fallback, skip, dashboard, and outbox contracts pass.

## Spec Change Log

## Review Triage Log

## Design Notes

`202609020000_create_dashboard_snapshot.sql` already contains the intended `logical_runs`/`runs` RLS and public read policy. The retrospective security finding is a deployment drift issue, not a reason to create a second competing RLS migration. The remote apply order must preserve the existing filenames and then use MCP inspection/fixtures as the production proof.

## Verification

**Commands:**

- `npm run typecheck && npm run test && npm run build -w apps/web` -- expected: all exit 0.
- `uv run --with pandas --with numpy --with pyarrow --with pytest pytest backtest tests/domain tests/batch -q` -- expected: all pass.
- CI-equivalent SQL fixture command -- expected: every supported Epic 1 fixture passes on clean Postgres.
- Supabase MCP migration/table/grant/advisor queries and fixtures -- expected: remote schema/RLS/RPC contract matches the migration files.

**Manual checks:**

- Playwright MCP로 `/login`을 열어 CSP console 오류가 없고 stylesheet가 차단되지 않는지 확인한다.
