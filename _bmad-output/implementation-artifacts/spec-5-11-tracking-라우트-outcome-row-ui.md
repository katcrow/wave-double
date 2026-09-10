---
title: 'Story 5.11: /tracking 라우트 & Outcome row UI'
type: 'feature'
created: '2026-09-10'
status: 'done'
baseline_revision: '14f4555a6065e781cbb66bea50da0ea0e1f6f9af'
baseline_commit: '14f4555a6065e781cbb66bea50da0ea0e1f6f9af'
review_loop_iteration: 1
followup_review_recommended: true
context:
  - 'C:/dev/wave-double/AGENTS.md'
  - 'C:/dev/wave-double/_bmad-output/implementation-artifacts/epic-5-context.md'
warnings: [oversized]
deferred: []
---

<intent-contract>

## Intent

**Problem:** `/tracking`은 현재 자리표시자만 있어 추천 후보의 사후 결과와 진행 중 건을 확인할 수 없다. 상태를 색상만으로 보여주거나 OPEN을 성과 분모처럼 오해하면 실전 검증 화면의 신뢰성이 떨어진다.

**Approach:** 운영 `candidate_outcome`을 브라우저에 직접 노출하지 않는 인증된 read-only RPC와 웹 타입/검증 경계를 추가하고, `/tracking`에서 Data trust bar와 함께 필터 가능한 Outcome row 표/모바일 카드를 렌더링한다.

## Boundaries & Constraints

**Always:** 기존 `get_dashboard_snapshot()`의 `outcome_tracking` 계보를 사용해 Data trust bar를 표시한다. Outcome 상태 TP/SL/TIMEOUT/OPEN/SUSPENDED/DELISTED는 텍스트와 상세 설명을 함께 제공하고, OPEN은 별도 카운트로 표시한다. RPC는 정렬·필터를 서버에서 제한하고 인증된 역할에만 실행 권한을 주며 `SECURITY DEFINER` 함수의 `search_path`를 고정한다. 필터는 URL query string으로 보존되어 뒤로가기·새로고침에서 복원되고, 수치 성과 계산은 후속 Story 5.12가 담당한다.

**Never:** 브라우저 역할에 `candidate_outcome` 테이블이나 성과 restricted view의 SELECT 권한을 부여하지 않는다. UI에서 승률·PF·표본 게이트를 재계산하지 않는다. outcome을 수정하거나 상태를 재판정하지 않으며, 색상만으로 상태 의미를 전달하지 않는다.

## I/O & Edge-Case Matrix

| Scenario | Input / State | Expected Output / Behavior | Error Handling |
|---|---|---|---|
| HAPPY_PATH | 인증 사용자, outcome 행 존재 | 6개 상태의 텍스트 badge와 ticker/전략/진입일/상태/종결일/손익률 row를 최신 진입일 우선 표시 | 없음 |
| FILTERED | `status`, `strategy`, `ticker` query 값 | 선택된 필터가 폼에 반영되고 URL에 유지되며 RPC 결과도 해당 조건으로 제한 | 허용 목록 밖 값은 무시하고 전체 결과로 안전하게 처리 |
| OPEN_COUNT | OPEN 및 종결/예외 행 혼재 | `진행 중 n건`을 별도 노출하고 OPEN을 종결 건수에 포함하지 않음 | 없음 |
| EMPTY | 유효한 조회지만 결과 0건 | “추적 중인 outcome이 없습니다.”를 표시하고 필터 상태는 유지 | 없음 |
| RPC_ERROR | RPC 실패 또는 예상 shape 불일치 | 기존 페이지를 깨뜨리지 않고 `Outcome 데이터를 불러오지 못했습니다` alert 표시 | 서버 로그에 원인 기록 |

</intent-contract>

## Code Map

- `apps/web/app/tracking/page.tsx:1-8` -- 현재 자리표시자 라우트. snapshot 조회, DataTrustBar, Outcome row 컨테이너로 교체한다.
- `apps/web/app/page.tsx:21-39,149-155` -- `get_dashboard_snapshot()` 호출과 `DataTrustBar` 재사용 패턴.
- `apps/web/components/dashboard/DataTrustBar.tsx:55-180` -- snapshot 기반 trust bar 및 수동 실행 UX. `/tracking` 상단에서 동일 컴포넌트를 사용한다.
- `apps/web/lib/trust-bar.ts:40-96` -- 배치 상태·KST 시각·trigger·stale 문구의 단일 권위.
- `apps/web/lib/dashboard-types.ts:1-170` -- `DashboardSnapshot`/`RunRow` 타입 인접 위치에 Outcome row 계약을 추가한다.
- `apps/web/lib/supabase-browser.ts:5-25` -- 기존 publishable-key Supabase 클라이언트 및 RPC 호출 경계.
- `apps/web/components/dashboard/` -- 기존 접근 가능한 badge/table/mobile-card 스타일과 컴포넌트 배치 위치.
- `infra/supabase/migrations/202609031300_create_outcome_schema.sql:32-85` -- `candidate_outcome` 컬럼과 6개 상태, RLS 원천. 직접 SELECT 대신 신규 RPC의 내부 원천으로만 사용한다.
- `packages/read-model/src/database.types.ts:104-150,1058-1066` -- candidate_outcome 타입과 generated Functions에 신규 RPC 반환 계약을 추가할 위치.
- `e2e/mock-supabase-server.mjs:102-186` -- snapshot/RPC mock 응답 분기. tracking fixture를 추가한다.
- `e2e/authenticated-dashboard.spec.ts:3-31`, `e2e/home.spec.ts` -- 인증·반응형 Playwright 검증 패턴.
- `apps/web/app/globals.css:234-282,1273-1333` -- trust bar 및 반응형 table/card 스타일. Outcome 전용 스타일을 인접 위치에 추가한다.

## Tasks & Acceptance

**Execution:**
- [x] `infra/supabase/migrations/202609101800_create_get_outcome_tracking_rows.sql` -- 상태/전략/ticker 선택 필터, 최신순·limit 제한을 받는 SECURITY DEFINER read RPC와 authenticated execute grant를 추가한다.
- [x] `packages/read-model/src/database.types.ts`, `apps/web/lib/dashboard-types.ts` -- RPC 반환 row의 nullability와 6개 상태 타입을 동기화한다.
- [x] `apps/web/lib/outcome-tracking.ts` -- RPC shape 검증, 상태 label/상세 문장, query 필터 정규화와 표시 포맷을 순수 함수로 구현한다.
- [x] `apps/web/components/tracking/OutcomeTrackingPanel.tsx`, `apps/web/app/globals.css` -- URL 필터 폼, 별도 카운트, 접근 가능한 badge, desktop table/mobile card와 empty/error 상태를 구현한다.
- [x] `apps/web/app/tracking/page.tsx` -- snapshot과 outcome RPC를 조회해 DataTrustBar와 panel에 전달하고 동적 렌더링을 고정한다.
- [x] `apps/web/lib/outcome-tracking.test.ts`, `e2e/mock-supabase-server.mjs`, `e2e/tracking.spec.ts` -- 상태/필터/shape 계약과 인증·렌더링·반응형·URL 보존을 검증한다.
- [x] `tests/sql/test_get_outcome_tracking_rows.sql`, `tools/epic-path-manifests/epic-5.txt`, `tools/production_parity_baseline.json` -- rollback fixture, row shape/ACL, migration order/production parity 범위를 고정한다.
- [x] `_bmad-output/implementation-artifacts/sprint-status.yaml` -- 구현·리뷰·검증 완료 후 Story 5.11과 Epic 5 상태를 동기화한다.

**Acceptance Criteria:**
- Given 인증 사용자가 `/tracking`에 접속하면, when 페이지가 렌더링될 때, then 메인과 별도 라우트로 존재하고 상단에 `outcome_tracking` 계보를 반영한 Data trust bar와 outcome 목록이 표시된다.
- Given outcome 상태가 TP/SL/TIMEOUT/OPEN/SUSPENDED/DELISTED 중 하나이면, when row를 표시할 때, then 상태 텍스트 badge와 상태 의미를 설명하는 문장이 함께 제공된다.
- Given OPEN과 다른 상태의 outcome이 함께 있으면, when 목록 상단 요약을 표시할 때, then OPEN은 `진행 중 n건`으로 별도 집계되고 종결 건수에 섞이지 않는다.
- Given 상태·전략·ticker 필터를 변경하면, when 폼을 제출하거나 초기화할 때, then URL query와 결과가 함께 갱신되고 뒤로가기·새로고침 후에도 같은 필터가 복원된다.
- Given 결과가 없거나 RPC가 실패하면, when `/tracking`이 렌더링될 때, then 빈 결과와 오류가 서로 다른 문구로 표시되고 오류는 alert로 접근 가능하다.
- Given 데스크톱 또는 375px 폭 화면이면, when Outcome row를 렌더링할 때, then 데스크톱은 헤더가 있는 표, 좁은 화면은 읽기 가능한 카드로 전환되며 모든 상태는 색상 없이 텍스트로 식별 가능하다.
- Given browser 역할이 신규 RPC를 호출하거나 직접 테이블을 조회하면, when 권한 계약을 검사할 때, then RPC execute만 authenticated에 허용되고 candidate_outcome 직접 SELECT 및 anon execute는 거부된다.

## Spec Change Log

## Review Triage Log

### 2026-09-10 — 자동 리뷰 및 보완

- 리뷰 입력: blind hunter 21건, edge-case hunter 4건, verification-gap hunter 6건, intent-alignment 확인 1건(중복 포함).
- 중복된 원인을 합쳐 `intent_gap: 0`, `bad_spec: 0`, `patch: 10`, `defer: 0`으로 분류했다. `patch`는 모두 적용 후 재검증했다. medium 8건 이상이므로 follow-up review 권고 점수는 24점 이상이다.
- 적용한 보완: snapshot/RPC shape 검증 및 generic error 경계, `outcome_tracking` focus trust-bar 표시, ticker ILIKE wildcard escape forward migration, RPC JSON allowlist, 500건 상한 안내, generated type와 웹 타입 경계 정리, SQL fixture의 tie/shape/limit/security/ACL assertion 강화, tracking E2E의 인증·필터·뒤로가기/새로고침·오류·반응형 보강, epic manifest 및 sprint timestamp 정리.
- dismiss: generated `Functions`의 JSON 반환 타입을 수동 row 타입으로 덮어쓰자는 의견은 generated file 재생성 시 손실되므로 웹 경계의 명시적 타입/런타임 guard로 처리했다. mock 서버가 모든 RPC 호출의 역할을 재검사해야 한다는 의견은 route 인증 E2E와 운영 Supabase ACL fixture가 각각의 계약을 검증하므로 현재 표면에 추가하지 않았다. 기존 restricted performance view ACL 누락 의견은 SQL fixture에서 다섯 view를 함께 검사하도록 반영했다. 정확히 500건일 때의 truncation ambiguity는 상한 안내 문구로 해소했다.
- 완료된 주요 finding은 리뷰 로그에 요약했으며, 미검증 상태로 남긴 finding은 없다.

## Design Notes

- Outcome row는 최신 `entry_date` 우선, 동일 날짜는 `outcome_id` 안정 정렬로 반환한다. 결과가 많아지는 운영 상황에서 RPC가 무제한 데이터를 브라우저로 전송하지 않도록 500건 상한을 둔다.
- 필터는 허용 상태/전략 집합에만 매핑한다. 잘못된 URL 값은 오류를 만들지 않고 제거된 전체 조회로 정규화하며, ticker는 trim 후 영숫자·한글 등 표시 가능한 검색 문자열로만 제한한다.
- `return_pct`가 NULL인 OPEN/SUSPENDED/DELISTED는 `미확정`으로 표시하고, 종결 row의 NULL도 `-`로 구분한다. UI는 성과 지표를 산출하지 않는다.

## Verification

**Commands:**
- `npm run typecheck` -- expected: 웹·read-model TypeScript 오류 없음.
- `npm run test` -- expected: 기존 웹 순수 함수 테스트와 outcome tracking 계약 테스트 통과.
- `npx playwright test e2e/tracking.spec.ts` -- expected: 인증 tracking 렌더, 6개 상태, 필터 URL 보존, 오류/빈 상태, 반응형 표면 통과.
- `python tools/check_migration_order.py` 및 `python tools/check_generated_types_drift.py` -- expected: migration/type gate 통과.
- `python tools/check_production_parity.py` -- expected: 신규 migration이 운영 baseline 대비 정방향으로 확인됨.
- 운영 Supabase MCP에서 migration과 `tests/sql/test_get_outcome_tracking_rows.sql`을 rollback transaction으로 실행 -- expected: row shape, 6개 상태, filter/limit, authenticated execute와 browser 직접 SELECT 차단 assertion 통과.

## Auto Run Result

- 결과: PASS. `/tracking` 인증 라우트, outcome read RPC, 상태 설명/OPEN 별도 집계, URL 필터 및 반응형 표면을 구현했다.
- 변경 범위: tracking page/panel과 순수 타입·검증·trust-bar 보완, CSS, Supabase RPC 및 forward hardening migration, SQL rollback fixture, mock/E2E, read-model parity/manifest, sprint status, 본 spec.
- 실행 증거: `npm run typecheck` 통과, `npm run test` 123 passed, `npx playwright test` 23 passed, `npm run build` 통과, migration order/generated drift/production parity 모두 통과(0 ERROR, 0 WARN), 운영 Supabase MCP fixture `PASS`.
- 운영 SQL fixture는 transaction rollback으로 실행했으며 실제 운영 프로젝트 `qqhjeumlecaudsiqhhdu`의 authenticated RPC execute, anon execute 거부, browser direct SELECT 거부, row shape/상태/filter/limit을 확인했다.
- residual risk: 실제 운영 인증 계정으로 브라우저를 연결한 live UI E2E는 별도 자격 증명이 없어 수행하지 않았다. route-level mock E2E와 운영 SQL/ACL 검증으로 대체했으며, 보호 데이터가 브라우저에 직접 노출되지 않는 계약은 확인했다.
