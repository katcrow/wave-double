---
title: 'Story 5.10: 컷오프 편향 고지'
type: 'feature'
created: '2026-09-10'
status: 'in-progress'
baseline_revision: 'b42a7ac657e87ff77fed29089f2a03cd8fa1c181'
baseline_commit: 'b42a7ac657e87ff77fed29089f2a03cd8fa1c181'
review_loop_iteration: 0
followup_review_recommended: false
context:
  - 'C:/dev/wave-double/AGENTS.md'
  - 'C:/dev/wave-double/_bmad-output/implementation-artifacts/epic-5-context.md'
warnings: [oversized]
deferred: []
---

<intent-contract>

## Intent

**Problem:** TIMEOUT은 실전 outcome의 정상 종결 분모에는 포함되지만 백테스트에는 없는 상태라서, 실전 승률·PF를 기대치와 비교할 때 컷오프 처리로 생기는 해석상 왜곡을 숨기면 V2 판단을 오독할 수 있다.

**Approach:** 5.9의 threshold-gated read model을 그대로 소비하는 신규 versioned view에서 전략별·전체 TIMEOUT 건수와 N=30 기준 백테스트 부재 고지 값을 반환한다. UI가 임의 계산하지 않도록 고지 대상 수치와 표시용 단위를 데이터 계약으로 고정하고, A/B/C 이외 전략 및 rollup에는 근거 없는 baseline을 노출하지 않는다.

## Boundaries & Constraints

**Always:** TP/SL/TIMEOUT만 종결 분모로 사용하고 OPEN/SUSPENDED/DELISTED는 별도 카운트 의미를 유지한다. `timeout_count`는 실제 `candidate_outcome`의 TIMEOUT 수이며 strategy rollup 전체 행도 제공한다. 고지의 기준 표본은 `cutoff_bias_sample_size=30`으로 고정하고, baseline의 A `TIMEOUT 0% / PF차 ±0`, B `TIMEOUT 0.37% / PF차 +0.0125`, C `TIMEOUT 0% / PF차 ±0`을 정확히 보존한다. 5.9의 표본 게이트·CI 1차 판정·threshold 보조 판정·동일 비용 모델을 변경하지 않으며, 기존 view는 수정하지 않는다. Browser 역할은 신규 view를 SELECT할 수 없어야 한다.

**Never:** TIMEOUT을 TP/SL로 재분류하거나 분모에서 제거하지 않는다. B의 PF 값을 승률 왜곡으로 바꾸거나 D/E/F·rollup에 임의 기대치를 채우지 않는다. UI에서 수치를 재계산하거나 청산/배치 판정 로직을 변경하지 않는다.

## I/O & Edge-Case Matrix

| Scenario | Input / State | Expected Output / Behavior | Error Handling |
|---|---|---|---|
| TIMEOUT_PRESENT | A/B/C 행에 TIMEOUT 포함 | 실제 `timeout_count`와 전략별 N=30 예상 TIMEOUT 비율/PF 차이 및 label 반환 | 없음 |
| NO_TIMEOUT | 종결 행에 TIMEOUT 없음 | `timeout_count=0`, 고지 기준과 metric 계약은 보존되어 UI가 0건을 명시 가능 | 없음 |
| BELOW_GATE | 종결 29건 이하 | 5.9의 게이트·CI·threshold 결과를 그대로 보존하고, TIMEOUT 고지는 성과 수치와 독립된 고정 baseline으로 유지 | 없음 |
| NO_EXPECTATION | D/E/F 또는 rollup, 게이트 통과 | TIMEOUT count는 반환하되 A/B/C 전용 고정 baseline은 NULL | 없음 |

</intent-contract>

## Code Map

- `infra/supabase/migrations/202609101602_finalize_outcome_win_rate_pf_threshold_comment.sql` -- Story 5.9의 최종 threshold-gated view 계약. 신규 view는 이 결과를 소비하고 기존 view는 읽기 전용으로 유지한다.
- `infra/supabase/migrations/202609101300_create_outcome_win_rate_pf_gated.sql` -- TP/SL/TIMEOUT 분모와 OPEN/SUSPENDED/DELISTED 분리 카운트의 원천 산식.
- `_bmad-output/specs/spec-wave-double/backtest-baseline.md:368-378` -- N별 A/B/C TIMEOUT 비율 및 PF 차이의 재현된 baseline. N=30 행을 고정 입력으로 사용한다.
- `infra/supabase/migrations/202609031300_create_outcome_schema.sql` -- `candidate_outcome.status` 허용값과 `cutoff_n`/`return_pct` 제약.
- `packages/read-model/src/database.types.ts:917-943` -- 5.9 view의 generated 타입 인접 위치에 신규 view 반환 컬럼을 추가할 지점.
- `tests/sql/test_outcome_win_rate_pf_threshold_gated.sql` -- rollback fixture, 전략별+rollup 결과와 browser ACL 검증의 재사용 패턴.
- `tests/fixtures/outcome_win_rate_pf_threshold_gated/input_cases.json` -- TIMEOUT 및 예외 상태를 포함한 기존 입력 fixture. 신규 fixture는 고지 계약을 독립적으로 검증한다.
- `tools/check_outcome_win_rate_pf_threshold_parity.py` 및 `tests/tools/test_check_outcome_win_rate_pf_threshold_parity.py` -- JSON/SQL/Python 기준값 parity 도구·계약 테스트 패턴.
- `tools/check_migration_order.py`, `tools/check_generated_types_drift.py`, `tools/check_production_parity.py`, `tools/epic-path-manifests/epic-5.txt` -- migration/type/운영 parity/Epic scope gate.
- `_bmad-output/planning-artifacts/epics.md:1562-1576`, `_bmad-output/planning-artifacts/prds/prd-wave-double-2026-08-31/prd.md:288-297` -- TIMEOUT 고지의 사용자 계약과 표본 게이트·비용 모델 동시 구현 요구.

## Tasks & Acceptance

**Execution:**
- `infra/supabase/migrations/202609101700_create_outcome_cutoff_bias_notice.sql` -- 5.9 결과를 소비하는 신규 versioned view를 만들고 실제 TIMEOUT count, 기준 N, 예상 TIMEOUT 비율, PF 차이, 표시 label을 전략별+rollup으로 반환한다.
- `tests/fixtures/outcome_cutoff_bias_notice/input_cases.json` -- A/B/C TIMEOUT 포함·미포함, 29건 게이트 미통과, D/E/F·rollup 및 예외 상태를 고정한다.
- `tests/sql/test_outcome_cutoff_bias_notice.sql` -- rollback 범위에서 view 결과, TIMEOUT 분리, null 계약, cardinality, browser SELECT revoke를 단언한다.
- `tools/check_outcome_cutoff_bias_notice_parity.py` -- JSON↔SQL INSERT↔Python 기준값↔SQL expected의 필드·정밀도·전략 매핑 parity를 검사한다.
- `tests/tools/test_check_outcome_cutoff_bias_notice_parity.py` -- 0/양수 TIMEOUT, 29/30 경계, A/B/C 고지 매핑, D/E/F·rollup NULL, 기존 5.9 결과 보존을 검증한다.
- `packages/read-model/src/database.types.ts`, `tools/epic-path-manifests/epic-5.txt`, `.github/workflows/test.yml` -- 생성 타입·Epic scope·SQL/parity CI gate를 갱신한다.
- `tools/production_parity_baseline.json`, `_bmad-output/implementation-artifacts/sprint-status.yaml` -- 운영 migration 적용 후 baseline과 Story 5.10 상태를 갱신한다.

**Acceptance Criteria:**
- Given 종결 건 중 TIMEOUT이 포함된 전략 A/B/C 행, when 컷오프 고지 view를 조회하면, then 실제 TIMEOUT 건수와 N=30 기준 A `TIMEOUT 0% / PF차 ±0`, B `TIMEOUT 0.37% / PF차 +0.0125`, C `TIMEOUT 0% / PF차 ±0` 고지가 함께 반환된다.
- Given TIMEOUT이 없는 행, when 고지 view를 조회하면, then `timeout_count=0`이 반환되어 데이터 부재와 실제 0을 구분할 수 있다.
- Given 5.9의 threshold/CI 판정 행, when 신규 view를 조회하면, then 5.9의 게이트·CI·승률·PF·threshold 컬럼 값은 변경 없이 함께 반환되고 고지 컬럼은 부가 결과로만 존재한다.
- Given 종결 30건 미만인 A/B/C 행, when 신규 view를 조회하면, then 성과 지표는 5.9 규칙대로 게이트 처리되고 컷오프 고지의 고정 baseline·실제 TIMEOUT count는 독립적으로 보존된다.
- Given D/E/F 또는 rollup 행, when 신규 view를 조회하면, then TIMEOUT count는 실제 집계하되 A/B/C에만 정의된 고지 metric/value/label은 NULL이다.
- Given 동일 fixture와 migration, when offline parity·SQL fixture·migration order·generated type·production parity gate를 실행하면, then Python 기준값·SQL view·expected rows·권한 계약이 일치한다.

## Spec Change Log

## Review Triage Log

## Design Notes

- `cutoff_bias_timeout_rate`는 N=30 baseline의 예상 TIMEOUT 비율( A/C `0.0000`, B `0.0037`)이고, `cutoff_bias_profit_factor_delta`는 PF 차이(A/C `0.0000`, B `0.0125`)다. UI는 각각 퍼센트와 PF 단위로 포맷하므로 숫자와 표시 단위를 분리한다.
- A/B/C의 고정 baseline 고지는 표본 게이트와 독립적으로 채운다. rollup은 여러 전략을 섞은 참고 집계라 단일 전략의 baseline 고지를 적용하지 않는다. `timeout_count`는 게이트와 무관하게 실제 상태 수를 계속 노출한다.
- 고지 view는 전략 목록을 하드코딩해 행을 만들지 않고 5.9 view의 행을 기준으로 left join/집계한다. 따라서 신규 전략이 추가돼도 관측 행이 사라지지 않고, 기대치가 없는 전략의 고지만 NULL로 남는다.

## Verification

**Commands:**
- `python tools/check_outcome_cutoff_bias_notice_parity.py` -- expected: fixture 입력/결과와 Python 기준값, SQL expected가 완전히 일치.
- `pytest -q tests/tools/test_check_outcome_cutoff_bias_notice_parity.py` -- expected: 경계·NULL·매핑 drift 계약 전체 통과.
- `python tools/check_migration_order.py` 및 `python tools/check_generated_types_drift.py` -- expected: migration과 generated type gate 통과.
- `python tools/check_production_parity.py` -- expected: 신규 migration이 운영 baseline 대비 정방향 pending이고 역방향 drift 없음.
- 운영 Supabase MCP에서 migration 및 `tests/sql/test_outcome_cutoff_bias_notice.sql`을 하나의 rollback transaction으로 실행 -- expected: 명시적 SQL assertion pass, 신규 view catalog/type/ACL 확인, fixture 원복.
