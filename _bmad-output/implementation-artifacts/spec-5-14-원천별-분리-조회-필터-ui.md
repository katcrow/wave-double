---
title: 'Story 5.14: 원천별 분리 조회 필터 UI'
type: 'feature'
created: '2026-09-14'
status: 'done'
baseline_revision: '99dcadec3325705bcbbe2322c13afe1442e30795'
baseline_commit: '99dcadec3325705bcbbe2322c13afe1442e30795'
review_loop_iteration: 1
followup_review_recommended: false
context:
  - 'C:/dev/wave-double/AGENTS.md'
  - 'C:/dev/wave-double/_bmad-output/implementation-artifacts/epic-5-context.md'
warnings: []
deferred: []
---

<intent-contract>

## Intent

**Problem:** `/tracking`의 성과·편향 수치는 전체 원천을 합친 값만 보여 주므로 t1859 본원천과 t1852/t1856 폴백 원천의 왜곡 영향을 분리해 확인할 수 없다.

**Approach:** 기존 metric/bias read model의 계산 규칙을 보존하면서 인증된 source-aware RPC를 추가하고, `/tracking`의 하나의 원천 필터를 전략·날짜 필터와 함께 query string에 저장해 두 패널에 같은 범위를 적용한다.

## Boundaries & Constraints

**Always:** 선택 원천은 `t1859`, `t1852`, `t1856` 중 하나 또는 전체이며 전체는 모든 원천 통합으로 명시한다. metric의 표본 게이트·CI·기대치·threshold·TIMEOUT 고지와 bias의 전체 기회 누락 산식은 DB canonical 결과를 그대로 사용한다. 기존 1-인자 RPC와 기존 query/패널 동작은 호환성을 유지하고, source RPC는 `SECURITY DEFINER`, `search_path = pg_catalog, public`, authenticated/service_role만 EXECUTE로 제한한다. source가 없는 provenance 행은 전체 통합에는 포함하되 선택 옵션에는 임의의 원천으로 매핑하지 않는다.

**Never:** UI에서 성과·편향을 재집계하거나 source별 행의 `missed_opportunity_count`를 합산해 전체 누락을 만들지 않는다. restricted view/table에 browser SELECT를 허용하지 않는다. 원천 필터 적용을 outcome 행 필터나 별도 임의 source 추정으로 확장하지 않는다.

## I/O & Edge-Case Matrix

| Scenario | Input / State | Expected Output / Behavior | Error Handling |
|---|---|---|---|
| HAPPY_PATH | `source=t1852`와 전략/날짜 필터 | metric 승률·PF와 bias 네 수치가 t1852 기준으로 표시되고 원천 범위를 명시 | 없음 |
| ALL_SOURCES | source query 없음 또는 초기화 | 전체 통합 metric/bias가 표시되고 `전체 원천 통합` 및 혼합 지표 문구가 표시 | 없음 |
| QUERY_PRESERVATION | source 적용 후 전략 변경·bias 날짜 변경·새로고침·뒤로가기 | source와 다른 query가 유지되고 실제 URL 상태가 복원 | 잘못된 source는 전체로 정규화 |
| RPC_ERROR_OR_SHAPE | source-aware RPC 실패/shape 오류 | 해당 metric 또는 bias 영역만 오류, 다른 영역은 유지 | 서버 로그 기록 |
| ACL_AND_EMPTY_SOURCE | source별 데이터 없음 또는 browser 권한 검사 | 실제 0/빈 결과와 오류를 혼동하지 않으며 restricted 직접 SELECT는 거부 | authenticated RPC만 허용 |

</intent-contract>

## Code Map

- `apps/web/app/tracking/page.tsx:54-104` -- query 정규화 후 metric/bias RPC를 호출하고 두 패널에 source 범위를 전달하는 서버 경계.
- `apps/web/lib/metric-comparison.ts:5-173`, `apps/web/lib/bias-diagnostic.ts:5-80` -- 기존 전략/날짜 정규화·shape guard·RPC 인자·표시 규칙 재사용 지점.
- `apps/web/components/tracking/MetricComparisonPanel.tsx:73-165`, `apps/web/components/tracking/BiasDiagnosticPanel.tsx:43-98` -- source 선택 UI, query hidden field, 전체/선택 범위 문구를 추가할 기존 클라이언트 패널.
- `apps/web/lib/dashboard-types.ts:29-70`, `packages/read-model/src/database.types.ts:877-891,1058-1069` -- 기존 row shape를 유지하면서 새 RPC args를 동기화할 타입 경계.
- `infra/supabase/migrations/202609101200_create_outcome_win_rate_pf_by_strategy_source.sql:11-64` -- `candidate_source_contrib`의 primary source 귀속·동률 우선순위 권위; `202609141000`/`202609141100`은 기존 metric/bias RPC 호환 계약.
- `tests/fixtures/outcome_win_rate_pf_by_strategy_source/input_cases.json`, `tests/sql/test_outcome_win_rate_pf_by_strategy_source.sql`, `tests/sql/test_get_outcome_metric_comparison.sql`, `tests/sql/test_get_bias_diagnostic.sql` -- source parity·row shape·ACL·rollback fixture 패턴.
- `e2e/mock-supabase-server.mjs:217-296`, `e2e/tracking.spec.ts:124-282` -- mock RPC 분기와 인증 tracking의 query/오류/반응형 Playwright 표면.
- `e2e/start-test-web.mjs:1-42` -- Playwright가 Next.js를 기다리는 동안 mock Supabase readiness도 먼저 보장하는 테스트 harness.

## Tasks & Acceptance

**Execution:**
- [x] `infra/supabase/migrations/202609141200_create_source_filtered_tracking_read_models.sql` -- 기존 계약을 수정하지 않고 source-aware metric/bias view 또는 2-인자 RPC를 추가해 source 선택 결과가 5.7~5.10/5.13 산식을 그대로 보존하게 한다. source 도메인·NULL provenance·권한·search_path를 고정한다.
- [x] `apps/web/lib/source-filter.ts`, `apps/web/lib/metric-comparison.ts`, `apps/web/lib/bias-diagnostic.ts`, `apps/web/lib/dashboard-types.ts`, `packages/read-model/src/database.types.ts` -- source 옵션/라벨/정규화와 새 RPC args 및 동일 row shape guard를 구현한다.
- [x] `apps/web/app/tracking/page.tsx`, `apps/web/components/tracking/MetricComparisonPanel.tsx`, `apps/web/components/tracking/BiasDiagnosticPanel.tsx`, `apps/web/app/globals.css` -- 하나의 source query를 두 read model에 전달하고 선택/초기화, 혼합 표기, 키보드 접근성과 반응형 UI를 구현한다.
- [x] `e2e/mock-supabase-server.mjs`, `e2e/tracking.spec.ts`, `apps/web/lib/source-filter.test.ts`, 관련 metric/bias 테스트 -- 세 source, 전체 초기화, query history 보존, source별 값, 오류/shape와 접근성을 검증한다.
- [x] `tests/sql/test_get_source_filtered_tracking.sql`, `tools/epic-path-manifests/epic-5.txt` -- source별·전체 parity, NULL bucket, 빈 source, row shape, authenticated execute/anon 및 restricted 직접 SELECT 거부를 rollback transaction으로 고정한다.
- [x] `_bmad-output/implementation-artifacts/sprint-status.yaml` -- Story 5.14를 구현·검토·검증 증거와 함께 동기화한다.

**Acceptance Criteria:**
- Given `/tracking`에서 `t1859`/`t1852`/`t1856`을 선택하면, when metric과 bias를 조회할 때, then 선택 원천 기준의 승률·PF·편향 지표가 표시되고 원천 범위가 명시된다.
- Given 원천 필터를 초기화하면, when 페이지가 갱신될 때, then 전체 통합 metric/bias로 돌아가며 `전체 원천 통합` 및 혼합 지표임이 구분된다.
- Given 전략·날짜 필터를 변경하거나 새로고침·뒤로가기를 수행하면, when URL과 화면을 확인할 때, then source를 포함한 기존 query 상태가 보존·복원된다.
- Given source-aware RPC가 실패하거나 shape가 틀리면, when `/tracking`을 렌더링할 때, then 해당 영역만 접근 가능한 오류를 표시하고 나머지 outcome/metric/bias 영역은 유지한다.
- Given browser 역할의 권한을 검사하면, when source별 read model을 조회할 때, then authenticated RPC execute만 허용되고 anon execute 및 restricted 원본/view 직접 SELECT는 거부된다.

## Spec Change Log

- 2026-09-14 — 구현·리뷰·운영 rollback fixture 검증을 완료하고 Story 5.14를 done으로 확정했다.

## Review Triage Log

- 2026-09-14 — 4개 독립 리뷰 레이어의 통합 triage
  - intent_gap: 0
  - bad_spec: 0
  - patch: 5
  - defer: 0
  - source/full parity, NULL provenance, bias fail-closed 검증, ACL/search_path, query preservation을 코드·rollback fixture·운영 catalog 계약으로 확인했다.
  - patch 처리: 세 원천 mock/row-shape 및 bias 경로, source query history, NULL provenance 격리 fixture, metric/bias ACL·catalog 개별 검증, mock readiness 실패 cleanup을 보강했다.
  - dismiss: 중복 SQL 로직은 현재 결과 오류가 아닌 유지보수 위험으로 확인했고, threshold 지적은 5.9 final 계약과 기존 canonical fixture의 게이트 통과 기대치/게이트 외 NULL 규칙을 재확인해 수정하지 않았다. `reuseExistingServer` 환경 재사용 시 mock이 별도 기동되지 않는 현상은 clean-port 실행에서 최종 E2E가 통과했으며 Story 기능 결함이 아니므로 범위 밖으로 분류했다.

## Design Notes

- 기존 1-인자 RPC는 유지하고 새 2-인자 overload를 사용해 배포 순서와 기존 호출자를 보호한다. source 인자가 유효하지 않으면 전체로 정규화한다.
- metric source 행은 primary source 귀속을 한 번만 적용해 셀 합이 전체와 이중 계상되지 않게 한다. 전체 bias 누락은 기존 전역 산식, 단일 source bias는 해당 canonical source 행을 사용한다.
- source query key는 `source` 하나로 통일한다. source가 없을 때도 URL을 정리하지 않아 새로고침·뒤로가기에서 전체 통합 상태가 안정적으로 복원된다.

## Verification

**Commands:**
- `npm run typecheck` -- expected: TypeScript 오류 없음.
- `npm test` -- expected: source/metric/bias/query 계약 테스트 전체 통과.
- `npx playwright test e2e/tracking.spec.ts` -- expected: source 선택·초기화·history·오류·반응형/접근성 통과.
- `python tools/check_migration_order.py` 및 `python tools/check_generated_types_drift.py` -- expected: migration/type gate 통과.
- `python tools/check_production_parity.py` -- expected: 운영 프로젝트 `qqhjeumlecaudsiqhhdu` 대비 신규 migration/function drift가 정직하게 보고됨.
- 운영 Supabase에서 신규 migration과 `tests/sql/test_get_source_filtered_tracking.sql`을 rollback transaction으로 실행 -- expected: source별/전체 row shape·산식·ACL·직접 SELECT 거부 PASS.

**Observed Results (2026-09-14):**

- `npm run typecheck`: PASS.
- `npm test`: PASS, 133 passed.
- `npx playwright test e2e/tracking.spec.ts --reporter=dot`: PASS, 20 passed.
- 운영 프로젝트 ref `qqhjeumlecaudsiqhhdu`에서 `tests/sql/test_get_source_filtered_tracking.sql`: `{"story_5_14_verification":"PASS"}`.
- 운영 catalog: 두 source-aware overload 모두 존재, `SECURITY DEFINER`, `search_path=pg_catalog, public`, authenticated EXECUTE 허용, anon EXECUTE 및 restricted view SELECT 거부.
- `check_production_parity.py`의 직접 gate 호출은 Management API 403으로 재현되어 완료 증거로 사용하지 않았고, 같은 프로젝트에 대한 직접 catalog/query와 rollback fixture 결과로 대체 확인했다.

## Suggested Review Order

**서버 경계와 canonical read model**

- tracking query를 정규화하고 같은 source 범위를 두 RPC에 전달합니다. [`page.tsx:56`](../../apps/web/app/tracking/page.tsx#L56)
- 기존 1-인자 호환성과 source-aware overload의 산식·권한 경계를 확인합니다. [`202609141200...sql:9`](../../infra/supabase/migrations/202609141200_create_source_filtered_tracking_read_models.sql#L9)

**source 계약과 UI query 상태**

- 허용 원천·라벨·전체 통합 의미를 확인합니다. [`source-filter.ts:1`](../../apps/web/lib/source-filter.ts#L1)
- metric/bias 패널의 선택·초기화·query preservation을 확인합니다. [`MetricComparisonPanel.tsx:81`](../../apps/web/components/tracking/MetricComparisonPanel.tsx#L81), [`BiasDiagnosticPanel.tsx:50`](../../apps/web/components/tracking/BiasDiagnosticPanel.tsx#L50)
- RPC 인자와 generated type이 기존 row shape를 유지하는지 확인합니다. [`metric-comparison.ts:98`](../../apps/web/lib/metric-comparison.ts#L98), [`bias-diagnostic.ts:56`](../../apps/web/lib/bias-diagnostic.ts#L56), [`database.types.ts:1062`](../../packages/read-model/src/database.types.ts#L1062)

**검증 증거**

- source별·전체 parity, NULL provenance, ACL 및 rollback을 확인합니다. [`test_get_source_filtered_tracking.sql:1`](../../tests/sql/test_get_source_filtered_tracking.sql#L1)
- 선택·초기화·history·zero-value UI 시나리오를 확인합니다. [`tracking.spec.ts:285`](../../e2e/tracking.spec.ts#L285), [`source-filter.test.ts:12`](../../apps/web/lib/source-filter.test.ts#L12)
