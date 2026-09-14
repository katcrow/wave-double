---
title: 'Story 5.12: Metric comparison UI'
type: 'feature'
created: '2026-09-14'
status: 'done'
baseline_revision: '382fe8f1ee324984bdc016ff472f585ab0a719e8'
baseline_commit: '382fe8f1ee324984bdc016ff472f585ab0a719e8'
review_loop_iteration: 1
followup_review_recommended: true
context:
  - 'C:/dev/wave-double/AGENTS.md'
  - 'C:/dev/wave-double/_bmad-output/implementation-artifacts/epic-5-context.md'
warnings: []
deferred:
  - summary: >-
      운영 Supabase MCP rollback fixture 검증은 이 세션에서 callable Supabase MCP 또는 로컬 SQL 실행기가 없어 수행하지 못했다.
    evidence: |-
      tools/check_production_parity.py는 0 ERROR, 2 WARN으로 신규 migration/function이 운영 catalog에 아직 없음을 확인했다. 따라서 운영 적용 및 SQL fixture pass를 주장하지 않는다.
    location: >-
      infra/supabase/migrations/202609141000_create_get_outcome_metric_comparison.sql
    severity: medium
---

<intent-contract>

## Intent

**Problem:** `/tracking`에는 outcome 행만 있어 실전 승률·PF가 전략별 백테스트 기대치와 얼마나 다른지 한눈에 판단할 수 없다. 표본 부족이나 신뢰구간을 숨기면 V2 진행 판단이 왜곡된다.

**Approach:** Story 5.7~5.10의 versioned read model을 인증된 read-only RPC로 노출하고, `/tracking`에 전체/전략별 선택과 실전·기대치 비교, 표본 게이트·95% CI·보조 이탈 경고·TIMEOUT 컷오프 고지를 함께 표시한다.

## Boundaries & Constraints

**Always:** 성과 숫자·카운트·게이트·CI·판정은 `candidate_outcome_cutoff_bias_notice`에서 읽고 UI에서 재계산하지 않는다. 전체(rollup)와 현재 지원되는 A/B/C/D/E/F 전략을 같은 계약으로 다루며, 기대치가 정의되지 않은 전략은 기대치 없음으로 명시한다. 종결 건수와 OPEN 건수는 항상 병기하고, 표본 30건 미만이면 승률·PF·CI·대조 판정을 숨긴다. 브라우저에는 restricted view 직접 SELECT 권한을 주지 않고 authenticated RPC만 허용하며 함수의 `search_path`를 고정한다.

**Never:** UI에서 outcome을 다시 집계하거나 기대치·신뢰구간·임계값을 추정하지 않는다. 표본 부족을 0% 성과로 표시하지 않으며, CI 판정을 임계값 경고로 대체하지 않는다. D/E/F에 임의의 백테스트 기대치를 채우거나, 현재 Story 5.11의 outcome 표·필터·Data trust bar 동작을 회귀시키지 않는다.

## I/O & Edge-Case Matrix

| Scenario | Input / State | Expected Output / Behavior | Error Handling |
|---|---|---|---|
| HAPPY_PATH | RPC가 전체와 전략별 metric row를 반환 | 전략 선택에 따라 실전 승률·PF와 기대치를 동일 비교 영역에 표시하고 종결/진행중 수를 병기 | 없음 |
| BELOW_GATE | 선택 전략의 `total_settled < 30` | 성과 수치 대신 `표본 부족 (n/30)`을 가장 눈에 띄게 표시하고 CI/threshold 판정은 숨김 | row는 유지하되 오류로 취급하지 않음 |
| GATED | 게이트 통과 row | 95% CI, 기대치 안/밖, 보조 임계값 경고, TIMEOUT/컷오프 고지를 표시 | 기대치가 NULL이면 기대치 없음으로 표시 |
| RPC_ERROR_OR_SHAPE | RPC 실패 또는 허용하지 않은 row shape | outcome tracking은 유지하고 metric 영역만 접근 가능한 오류 상태로 표시 | 원인을 서버 로그에 기록 |

</intent-contract>

## Code Map

- `apps/web/app/tracking/page.tsx` -- 기존 snapshot/outcome RPC 조회 뒤 metric comparison RPC를 호출해 패널에 전달한다. Data trust bar와 outcome row는 그대로 유지한다.
- `apps/web/components/tracking/OutcomeTrackingPanel.tsx` -- 기존 `/tracking` UI의 형제 영역으로 metric 선택 UI와 결과 패널을 배치할 재사용 경계다.
- `apps/web/lib/outcome-tracking.ts`, `apps/web/lib/strategy-labels.ts` -- 전략 허용 목록·표시 라벨 및 URL 상태 정규화 규칙을 재사용한다.
- `apps/web/lib/dashboard-types.ts`, `packages/read-model/src/database.types.ts` -- metric RPC/view row의 nullable 필드와 함수 계약을 동기화한다.
- `infra/supabase/migrations/202609101700_create_outcome_cutoff_bias_notice.sql` -- 승률·PF·표본 게이트·CI·threshold·TIMEOUT 고지의 canonical 입력 view이며 수정하지 않고 신규 RPC가 소비한다.
- `e2e/mock-supabase-server.mjs`, `e2e/tracking.spec.ts` -- 인증 tracking fixture/RPC 분기와 Playwright 표면 검증을 확장한다.
- `apps/web/app/globals.css` -- 기존 dark console 카드/반응형 규칙에 metric comparison 영역 스타일을 추가한다.
- `tests/sql/`, `tools/epic-path-manifests/epic-5.txt`, `tools/production_parity_baseline.json` -- RPC row shape·ACL·migration/parity 범위를 고정한다.

## Tasks & Acceptance

**Execution:**
- `infra/supabase/migrations/202609141000_create_get_outcome_metric_comparison.sql` -- cutoff-bias view를 선택 전략 또는 전체로 제한해 JSONB 배열로 반환하는 SECURITY DEFINER read RPC와 authenticated execute grant를 추가한다.
- `packages/read-model/src/database.types.ts`, `apps/web/lib/dashboard-types.ts`, `apps/web/lib/metric-comparison.ts` -- RPC row 타입, 런타임 shape guard, 선택 범위·표시 포맷·판정 문구를 구현한다.
- `apps/web/app/tracking/page.tsx`, `apps/web/components/tracking/MetricComparisonPanel.tsx`, `apps/web/app/globals.css` -- 선택 가능한 전략 비교 UI와 표본 게이트/CI/threshold/TIMEOUT 고지를 outcome panel과 함께 렌더링한다.
- `e2e/mock-supabase-server.mjs`, `e2e/tracking.spec.ts`, `apps/web/lib/metric-comparison.test.ts` -- 전체/전략 선택, 표본 부족, 게이트 통과, 오류, 반응형·접근성 표면을 검증한다.
- `tests/sql/test_get_outcome_metric_comparison.sql`, `tools/epic-path-manifests/epic-5.txt`, `tools/production_parity_baseline.json` -- row shape·필터·권한·검색 경계와 운영 parity를 고정한다.
- `_bmad-output/implementation-artifacts/sprint-status.yaml` -- 구현·review·검증 완료를 근거와 함께 Story 5.12 및 Epic 5에 동기화한다.

**Acceptance Criteria:**
- Given `/tracking`에서 전체 또는 전략을 선택하면, when metric comparison을 렌더링할 때, then 선택 범위의 실전 승률·PF와 백테스트 기대치가 같은 비교 영역에 표시되고 종결/진행중 건수가 함께 표시된다.
- Given 선택 범위의 종결 건수가 30건 미만이면, when 화면을 렌더링할 때, then 승률·PF 대신 `표본 부족 (n/30)`이 성과 수치보다 크게 표시된다.
- Given 종결 건수가 30건 이상이면, when 화면을 렌더링할 때, then 95% CI와 기대치의 안/밖 판정 및 ±10%p/±25% 보조 임계값 경고가 함께 표시된다.
- Given TIMEOUT이 존재하면, when 선택 범위의 metric을 렌더링할 때, then TIMEOUT 건수와 Story 5.10의 N=30 예상 왜곡 고지가 표시된다.
- Given D/E/F 또는 전체처럼 백테스트 기대치가 정의되지 않은 범위를 선택하면, when 비교 영역을 렌더링할 때, then 기대치 없음이 명시되고 임의의 기대치나 판정은 표시되지 않는다.
- Given RPC가 실패하거나 shape가 맞지 않으면, when `/tracking`을 렌더링할 때, then 기존 outcome tracking은 유지되고 metric 영역에 접근 가능한 오류 상태가 표시된다.
- Given browser 역할로 metric 데이터를 조회하면, when 권한을 검사할 때, then authenticated RPC execute만 허용되고 anon execute 및 restricted view 직접 SELECT는 거부된다.

## Spec Change Log

## Review Triage Log

### 2026-09-14 — Review pass 1

- `intent_gap`: 0
- `bad_spec`: 0
- `patch`: 6 (high 0, medium 4, low 2)
- `defer`: 1 (high 0, medium 1, low 0)
- `dismissed`:
  - 운영 parity baseline에 미적용 migration/function을 미리 기록하라는 finding은 반영하지 않았다. baseline은 운영 catalog의 마지막 확인 상태이므로 선기록하면 의도한 drift 경고를 숨긴다.
  - review 중간 상태에서 sprint-status가 `in-progress`이고 spec이 `in-review`인 점은 finalize 전에 필요한 절차 상태이므로 결함으로 보지 않았다.
  - review 시점에 commit이 없다는 finding은 review가 commit 전에 실행되는 workflow 순서 때문이므로 결함으로 보지 않았다.
- `addressed_findings`:
  - RPC 응답 guard에 표본 게이트, 수치 범위, CI 순서, 기대치/threshold 불변식, 전체/선택 cardinality 검증을 추가했다.
  - SQL fixture를 transaction 내부의 격리된 `candidate_outcome` 데이터로 실행하고 canonical row passthrough, A/B/C 기대치·cutoff 값, D/E/F 기대치 없음, ACL을 assert하도록 보강했다.
  - PF 비교 막대의 동적 기준, all-win PF의 산출 불가 문구, bar 접근성 이름, query state 보존을 보강했다.
  - 선택 전략 URL, B TIMEOUT/cutoff, D/F 기대치 없음, below-gate, malformed/error, 반응형·키보드 E2E를 추가했다.
  - generated `Database`를 browser/server Supabase client와 RPC args에 연결하고 기존 Json cast를 타입 안전하게 정리했다.
- `followup_review_recommended`: true. 계산: `3*medium + low = 3*4 + 2 = 14`.

## Auto Run Result

- 구현 완료: `get_outcome_metric_comparison` 인증 RPC, metric comparison panel, A-F/전체 선택, 표본 게이트·CI·threshold·TIMEOUT 고지, runtime guard 및 SQL/단위/E2E fixture.
- 리뷰: 4개 lens(blind, edge-case, verification-gap, intent) 결과를 triage하고 위 finding을 보완했다.
- 검증 통과: `npm run typecheck`, `npm test` (127 passed), `npm run build`, `npx playwright test e2e/tracking.spec.ts` (13 passed), migration order (80 files), generated type drift, `git diff --check`.
- 운영 parity: `0 ERROR, 2 WARN`. WARN은 신규 migration/function이 아직 운영 catalog에 없다는 정직한 미적용 상태다.
- 미수행: callable Supabase MCP/local SQL runner가 없어 운영 프로젝트에 migration을 적용하거나 rollback SQL fixture를 실행하지 못했다. Playwright suite는 mock Supabase 기반이며 production authenticated browser E2E는 별도 증거가 아니다.
- 잔여 위험: 운영 migration 적용 후 `tests/sql/test_get_outcome_metric_comparison.sql`을 `qqhjeumlecaudsiqhhdu` 프로젝트에서 rollback transaction으로 실행해 RPC 반환·ACL·restricted view 직접 SELECT 거부를 확인해야 한다.

## Design Notes

- RPC는 `{ strategy: null | 'A'...'F' }` 입력을 받고 전체 조회 시 rollup과 전략별 행을 모두 반환한다. UI는 선택 범위의 단일 row를 사용하되, 기대치가 없는 rollup/D/E/F는 `비교 기준 없음`으로 구분한다.
- 성과 수치는 게이트 통과 때만 표시한다. `open_count`는 `진행 중 n건`, `total_settled`는 `종결 n건`으로 별도 표시하여 OPEN이 분모에 섞이지 않음을 드러낸다.
- 비교 그래픽은 CSS 막대/수치 표면으로 제한하고, CI와 기대치의 관계는 텍스트로도 제공해 색상에 의존하지 않는다.

## Verification

**Commands:**
- `npm run typecheck` -- expected: TypeScript 오류 없음.
- `npm test` -- expected: metric/outcome 순수 함수 테스트 전체 통과.
- `npx playwright test e2e/tracking.spec.ts` -- expected: 인증 tracking의 metric 전체/전략 선택, 표본 부족, 오류, 반응형 및 접근성 검증 통과.
- `python tools/check_migration_order.py` 및 `python tools/check_generated_types_drift.py` -- expected: migration/read-model type gate 통과.
- `python tools/check_production_parity.py` -- expected: 운영 프로젝트 `qqhjeumlecaudsiqhhdu` 대비 신규 migration이 정방향으로 기록됨.
- 운영 Supabase MCP에서 신규 migration과 SQL fixture를 rollback transaction으로 실행 -- expected: row shape, 전체/전략 filter, gate/CI/timeout 전달, authenticated execute 및 anon/direct SELECT 거부 통과.
