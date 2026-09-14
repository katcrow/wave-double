---
title: 'Story 5.13: Bias diagnostic UI'
type: 'feature'
created: '2026-09-14'
status: 'done'
baseline_revision: '147024f928b4eac5421d749c4fc3c1bafc1460b3'
baseline_commit: '147024f928b4eac5421d749c4fc3c1bafc1460b3'
review_loop_iteration: 0
followup_review_recommended: true
context:
  - C:/dev/wave-double/_bmad-output/implementation-artifacts/epic-5-context.md
warnings: []
deferred:
  - summary: >-
      운영 migration history 등록과 production authenticated browser E2E는 별도 운영 확인이 필요하다.
    evidence: |-
      Management API catalog와 rollback SQL fixture는 PASS였지만 check_production_parity.py가 신규 migration/function 미등록 WARN 4건을 반환했고, 세션에 Supabase MCP와 production authenticated browser 세션이 노출되지 않았다.
    location: >-
      tools/check_production_parity.py; infra/supabase/migrations/202609141100_create_get_bias_diagnostic.sql
    severity: medium
---

<intent-contract>

## Intent

**Problem:** `/tracking`에서 실전 성과 이탈을 해석할 때 후보 모집단과 백테스트 유니버스 사이의 기회 차이를 확인할 수 없다.

**Approach:** 선택한 거래일의 최신 canonical bias event를 인증된 read-only RPC로 조회하고, 기존 `/tracking`에 네 가지 모집단 수치와 담백한 설명을 추가한다.

## Boundaries & Constraints

**Always:** 배치가 저장한 A~F 전략 시그널 합집합의 수치를 사용하고 UI에서 재계산하지 않는다. `candidate_population ∩ strategy_signal`, `backtest_universe ∩ strategy_signal`, 교집합, 기회 누락을 각각 표시한다. `bias_date` query를 새로 고침·뒤로가기에도 보존하고, 날짜가 없으면 KST 오늘을 조회한다. 데이터 없음은 숫자 0이 아닌 명시적 빈 상태로 표시한다. bias 테이블과 view의 브라우저 직접 SELECT는 계속 거부하고 authenticated RPC만 허용한다.

**Never:** source별 행의 `missed_opportunity_count`를 단순 합산해 전체 누락을 만들지 않는다. 편향을 성과의 실패 원인으로 단정하거나 과장된 그래픽을 추가하지 않는다. 기존 outcome/metric/Data trust 동작이나 5.14 source 필터 범위를 변경하지 않는다.

## I/O & Edge-Case Matrix

| Scenario | Input / State | Expected Output / Behavior | Error Handling |
|---|---|---|---|
| HAPPY_PATH | canonical event가 선택일에 존재 | 네 수치와 각 의미 설명을 표시 | 없음 |
| NO_DATA | 미래일 또는 미수집 과거일 | 숫자를 렌더링하지 않고 `이 날짜의 편향 데이터가 없습니다` 표시 | 정상 빈 상태 |
| RPC_ERROR_OR_SHAPE | RPC 실패 또는 계약 외 응답 | metric/outcome은 유지하고 bias 영역만 접근 가능한 오류 표시 | 서버 로그 기록 |

</intent-contract>

## Code Map

- `apps/web/app/tracking/page.tsx` -- 기존 snapshot/outcome/metric 조회 흐름에 `bias_date` 정규화와 bias RPC 호출을 추가한다.
- `apps/web/lib/dashboard-types.ts` -- `BiasDiagnosticRpcRow`의 전체 데이터·빈 데이터 shape를 공통 타입으로 둔다.
- `apps/web/lib/bias-diagnostic.ts` -- 날짜 query, RPC 파라미터, 응답 shape guard, 숫자 표시 포맷을 담당한다.
- `apps/web/components/tracking/BiasDiagnosticPanel.tsx` -- 날짜 선택, 네 수치, 설명, 빈 상태와 오류 상태를 렌더링하는 형제 패널이다.
- `apps/web/app/globals.css` -- 기존 dark console 카드·반응형 규칙을 재사용해 담백한 4수치 grid를 추가한다.
- `infra/supabase/migrations/202609141100_create_get_bias_diagnostic.sql` -- canonical bias event를 날짜로 제한하는 SECURITY DEFINER RPC와 authenticated/service_role 권한을 추가한다.
- `packages/read-model/src/database.types.ts` -- 신규 RPC 인자/JSON 반환 계약을 동기화한다.
- `e2e/mock-supabase-server.mjs`, `e2e/tracking.spec.ts`, `apps/web/lib/bias-diagnostic.test.ts` -- 정상·빈 날짜·오류/shape·query 보존·반응형 표면을 검증한다.
- `tests/sql/test_get_bias_diagnostic.sql`, `tools/epic-path-manifests/epic-5.txt` -- row shape·집합 산식·ACL·운영 migration 범위를 고정한다.

## Tasks & Acceptance

**Execution:**
- [x] `infra/supabase/migrations/202609141100_create_get_bias_diagnostic.sql` -- 최신 canonical event와 source 행 및 `calculation_meta` 절단 보정값으로 전체 집합 지표를 산출하는 날짜 RPC를 추가한다.
- [x] `packages/read-model/src/database.types.ts`, `apps/web/lib/dashboard-types.ts`, `apps/web/lib/bias-diagnostic.ts` -- nullable 빈 상태와 유한 non-negative 정수 계약, query/format helper를 구현한다.
- [x] `apps/web/app/tracking/page.tsx`, `apps/web/components/tracking/BiasDiagnosticPanel.tsx`, `apps/web/app/globals.css` -- metric/outcome과 독립된 bias panel 및 날짜 필터를 렌더링한다.
- [x] `e2e/mock-supabase-server.mjs`, `e2e/tracking.spec.ts`, `apps/web/lib/bias-diagnostic.test.ts` -- 네 수치, 빈 데이터, 오류, 접근성·좁은 화면을 검증한다.
- [x] `tests/sql/test_get_bias_diagnostic.sql`, `tools/epic-path-manifests/epic-5.txt` -- SQL shape·집합 누락 보정·권한·범위를 고정한다.
- [ ] `tools/production_parity_baseline.json` -- 운영 catalog에 신규 migration/RPC가 아직 없어 baseline을 선반영하지 않는다.
- [x] `_bmad-output/implementation-artifacts/sprint-status.yaml` -- Story 5.13 구현 상태를 `review`로 동기화한다.

**Acceptance Criteria:**
- Given `/tracking`에서 날짜를 선택하면, when Bias diagnostic을 렌더링할 때, then 네 모집단 수치와 각각의 짧은 설명이 표시된다.
- Given 차집합을 표시하면, when 화면을 확인할 때, then 담백한 수치/텍스트로 표현되고 성과 실패 원인으로 단정하지 않는다.
- Given 선택일의 bias event가 없으면, when 화면을 렌더링할 때, then 네 숫자 대신 명시적 미수집 빈 상태가 표시된다.
- Given RPC가 실패하거나 shape가 틀리면, when `/tracking`을 렌더링할 때, then bias 영역만 오류를 표시하고 metric/outcome을 유지한다.
- Given browser 역할이 bias 데이터를 조회하면, when 권한을 검사할 때, then authenticated RPC execute만 허용되고 anon execute 및 bias 원본/canonical view 직접 SELECT는 거부된다.

## Spec Change Log

- 2026-09-14 review patch: 전체 기회 누락 산식을 `max(universe) - sum(intersection) + truncated_only_missed_count`로 고정하고, canonical source 3행·정확한 `by_source` 메타·null 거래일을 무결성 오류로 격리했다. 기존 source별 missed 합산과 부분 event의 정상 표시를 방지한다.

## Review Triage Log

- 2026-09-14 — Review pass
  - intent_gap: 0
  - bad_spec: 0
  - patch: 6: (high 1, medium 1, low 4)
  - defer: 1: (medium 1)
  - dismissed:
    - canonical RPC 선택이 비결정적이라는 finding — `bias_events_canonical`이 거래일별 `distinct on`과 `created_at desc, bias_event_id desc`로 이미 1행을 결정하므로 RPC의 `limit 1`은 그 단일 행에만 적용된다.
    - source별 backtest 수를 max로 집계하면 undercount한다는 finding — Story 5.3 계약상 유니버스 수는 세 source 행에 반복되는 전역 값이므로 max가 전체 수이며 source별 합산이 아니다.
    - 정수 overflow finding — 배치 도메인의 후보 상한 150과 백테스트 유니버스 104 범위에서는 integer overflow 경로가 성립하지 않는다.
    - E2E 다음 테스트에 malformed scenario가 누출된다는 finding — 각 테스트의 `beforeEach`가 매번 default scenario로 reset한다.
    - RPC error branch가 미검증이라는 finding — mock의 404 응답은 Supabase client의 `error` 경로를 실제로 발생시키며 해당 E2E가 로그와 bias 오류 상태를 확인한다.
    - focus-visible 누락 finding — 전역 `:focus-visible` 규칙이 date input과 button에도 적용된다.
    - invalid bias_date를 URL에서 즉시 정규화하지 않는다는 finding — 명세가 요구하는 것은 RPC 입력 정규화와 유효값 guard이며, 사용자 입력 후에는 HTML date required와 서버 정규화로 안전하게 처리된다.
  - addressed_findings:
    - [high] [patch] 전역 유니버스 수를 source마다 중복 차감하던 누락 산식을 `max(universe) - sum(intersection) + truncation correction`으로 수정하고 SQL fixture를 8로 고정했다.
    - [medium] [patch] source 3행·정확한 by_source metadata·null 날짜를 fail-closed RPC 오류로 격리하고 malformed metadata fixture를 추가했다.
    - [low] [patch] JavaScript 연도 0001~0099 ISO 날짜 검증을 `setUTCFullYear` 기반으로 보완했다.
    - [low] [patch] populated row의 null count 거부와 날짜 기본값·기존 query 보존·history 복원을 단위/E2E로 보강했다.
    - [low] [patch] bias metric grid에 list/listitem 접근성 semantics와 Playwright 검증을 추가했다.
    - [low] [patch] review 상태와 manifest가 실제 변경 범위와 일치하도록 spec checklist 및 epic manifest를 정리했다.

## Design Notes

- RPC는 `{ p_trading_day: date }`를 받고 항상 `trading_day`, `has_data`, 네 nullable count key를 반환한다. 데이터가 없으면 `has_data=false`와 count `null`을 반환해 0과 미수집을 구분한다.
- 전체 기회 누락은 전역 `max(backtest_universe_signal_count) - sum(intersection_count) + calculation_meta.by_source`의 `truncated_only_missed_count` 합으로 계산한다. source 행의 universe 수가 반복되므로 source별 차이를 합산하지 않으며, 정확히 3개 source와 3개 truncated metadata가 모두 유효할 때만 정상 데이터를 반환한다.
- 기본 날짜는 애플리케이션 서버의 KST 달력 날짜로 만들고, 날짜 입력은 연도 0001-0099를 포함한 실제 달력 기준 `YYYY-MM-DD` 유효값만 통과시킨다.

## Verification

**Commands:**
- `npm run typecheck` -- expected: TypeScript 오류 없음.
- `npm test` -- expected: bias/outcome/metric 순수 함수 테스트 전체 통과.
- `npx playwright test e2e/tracking.spec.ts` -- expected: bias 정상·빈 데이터·오류·query 보존·반응형 검증 통과.
- `python tools/check_migration_order.py` 및 `python tools/check_generated_types_drift.py` -- expected: migration/type gate 통과.
- `python tools/check_production_parity.py` -- expected: 신규 migration이 운영 프로젝트 `qqhjeumlecaudsiqhhdu` 기준으로 정방향 확인된다.
- 운영 Supabase MCP에서 migration과 SQL fixture를 rollback transaction으로 실행 -- expected: row shape·집합 산식·authenticated RPC·anon/direct SELECT 거부 통과.

## Auto Run Result

- 구현: 날짜 기반 `get_bias_diagnostic` 인증 RPC, A~F 합집합 네 지표, 명시적 no-data/error 상태, `/tracking` Bias diagnostic 패널과 query 보존을 추가했다.
- 변경 파일: `apps/web/app/tracking/page.tsx` 라우트 RPC 호출, `apps/web/components/tracking/BiasDiagnosticPanel.tsx` UI, `apps/web/lib/bias-diagnostic.ts` 계약/날짜 guard, `apps/web/lib/dashboard-types.ts` 타입, `apps/web/app/globals.css` 반응형 스타일, `infra/supabase/migrations/202609141100_create_get_bias_diagnostic.sql` RPC, `packages/read-model/src/database.types.ts` generated RPC 타입, `e2e/mock-supabase-server.mjs`와 `e2e/tracking.spec.ts` E2E, `apps/web/lib/bias-diagnostic.test.ts` 단위 테스트, `tests/sql/test_get_bias_diagnostic.sql` SQL fixture, `tools/epic-path-manifests/epic-5.txt` scope manifest, 이 spec 및 sprint status.
- 리뷰: patch 6건(High 1, Medium 1, Low 4)을 보완했고, Medium defer 1건(운영 migration history 및 production authenticated browser E2E)을 남겼다. dismissed finding은 위 Review Triage Log에 사유와 함께 기록했다.
- 후속 리뷰 권고: `true` — 이번 pass patch 점수 규칙상 High finding이 있어 재검토 권고다.
- 검증: `npm run typecheck` 통과, `npm test` 131개 통과, `npm run build` 통과, `npx playwright test e2e/tracking.spec.ts` 17개 통과, migration order 81 files 통과, generated type drift 통과, Epic 5 scope `out_of_scope=[]`, `git diff --check` 통과.
- 운영 검증: 설정된 ref `qqhjeumlecaudsiqhhdu`의 catalog에서 함수가 `SECURITY DEFINER`, `search_path=pg_catalog, public`, authenticated/service_role execute, anon/direct bias 원본·canonical view SELECT 거부임을 확인했다. 동일 `tests/sql/test_get_bias_diagnostic.sql`을 Management API rollback transaction으로 실행해 `PASS`를 확인했다. Supabase MCP는 이 세션에 노출되지 않아 공식 Management API fallback을 사용했다.
- 운영 잔여 위험: `python tools/check_production_parity.py`는 0 ERROR, 4 WARN을 반환했으며 신규 migration/function의 migration history 등록과 production authenticated browser E2E는 별도 운영 확인이 필요하다. 기존 사용자 변경 `tests/sql/test_get_outcome_metric_comparison.sql`은 보존했고 커밋하지 않았다.
