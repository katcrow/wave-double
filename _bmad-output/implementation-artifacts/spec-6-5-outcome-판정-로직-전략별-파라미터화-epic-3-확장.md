---
title: 'Outcome 판정 로직 전략별 파라미터화'
type: 'feature'
created: '2026-09-04'
status: 'done'
baseline_revision: '391ece817fa40cc4b00aa6b8a507fef9bbf477bf'
baseline_commit: '391ece817fa40cc4b00aa6b8a507fef9bbf477bf'
review_loop_iteration: 1
followup_review_recommended: true
context:
  - 'C:/dev/wave-double/_bmad-output/implementation-artifacts/epic-6-context.md'
  - 'C:/dev/wave-double/_bmad-output/implementation-artifacts/spec-6-4-전략-계산-api-일반화.md'
warnings: []
deferred:
  - summary: >-
      기존 rebuild의 malformed payload 및 terminal trading_day 누락 시 상태 전이 의미를 더 엄격하게 검증하는 작업
    evidence: >-
      Story 6.5의 파라미터 스냅샷을 투영하는 경로는 검증했지만, 기존 Epic 3 state-machine 보강은 이번 범위 밖이다.
    location: 'infra/supabase/migrations/202609051600_parameterize_outcome_strategy_rules.sql:455-519'
    severity: medium
  - summary: >-
      N/N-1 운영 데이터에 대한 별도 런타임 호환 fixture 추가
    evidence: >-
      migration은 A/B/C 기존 cutoff_n을 덮어쓰지 않고 legacy payload fallback을 유지하지만,
      이미 적용된 운영 DB에서 pre-migration 행을 별도 생성하는 검증 fixture는 이번 실행에 포함하지 않았다.
    location: 'tests/sql/test_outcome_rebuild.sql:1-190'
    severity: medium
---

<intent-contract>

## Intent

**Problem:** Outcome 판정 SQL과 OPEN 발행이 TP 3%·SL 3%·최대보유 30일을 공통 전제로 사용해 전략 D/E의 서로 다른 청산조건을 잃는다.

**Approach:** 전략별 TP/SL/최대보유를 DB의 단일 파라미터 권위에서 조회하고 OPEN 행과 append-only OPEN 이벤트에 스냅샷한다. 최신 `publish_attempt`와 projection 재구축을 이 값에 맞춰 확장한다.

## Boundaries & Constraints

**Always:** A/B/C는 TP 3%·SL 3%·30일을 유지하고 기존 outcome 행·cutoff_n을 재계산하지 않는다. D는 3%/5%/20일, E는 2%/5%/30일이다. SL을 TP보다 우선하고 왕복 비용 0.1%를 차감한다. outcome_events/observations는 append-only이며 DB 변경은 forward-only, service_role 전용 경계를 유지한다. 재구축은 판정을 재실행하지 않고 이벤트 payload를 투영한다.

**Never:** 기존 migration 수정, 전 전략 공통 1.03/0.97 또는 cutoff 30 하드코딩, 태깅 stage·UI 변경, 과거 outcome 재판정·일괄 보정은 하지 않는다.

## I/O & Edge-Case Matrix

| Scenario | Input / State | Expected Output / Behavior | Error Handling |
|----------|--------------|---------------------------|----------------|
| HAPPY_PATH | A/B/C/D/E active tag로 close publish | candidate_outcome에 전략별 tp_pct/sl_pct/cutoff_n과 OPEN payload 스냅샷 저장 | 파라미터 누락/미정 전략은 원자적으로 실패 |
| STRATEGY_JUDGEMENT | 저장된 OHLC 관찰이 TP 또는 SL 경계 도달 | 해당 행의 entry_price와 tp_pct/sl_pct로 terminal 전이, SL 우선, 비용 반영 return_pct | 관찰 결측은 기존처럼 판정 보류 |
| REBUILD | OPEN 및 후속 이벤트 장부 존재 | 재구축 후 entry/청산 결과와 전략별 파라미터 보존 | OPEN payload가 구형이면 A/B/C 레거시 기본값만 허용 |

</intent-contract>

## Code Map

- `infra/supabase/migrations/202609042200_enforce_delisted_termination.sql:12-250` -- 현재 최신 `publish_attempt`; close의 OPEN·관찰·SUSPENDED·TP/SL/TIMEOUT 순서와 변경해야 할 판정 리터럴.
- `infra/supabase/migrations/202609042200_enforce_delisted_termination.sql:259-381` -- 현재 최신 `emit_open_command`; 전략 허용 목록, OPEN event payload, projection INSERT 경계.
- `infra/supabase/migrations/202609031300_create_outcome_schema.sql:32-57` -- `candidate_outcome` 원본 컬럼·전략 CHECK·cutoff 기본값.
- `infra/supabase/migrations/202609051200_create_rebuild_outcome_projection.sql:22-145` -- OPEN payload를 읽는 rebuild projection; 파라미터 스냅샷을 재생해야 한다.
- `infra/supabase/migrations/202609032201_fix_outcome_correction_review_patch.sql:14-134` -- correction의 허용 수정 경로와 cutoff/version 불변 경계.
- `backtest/strategy_api.py:23-74` -- A~E 전략의 기준 TP/SL/max_holding 파라미터 원천.
- `tests/sql/test_outcome_schema.sql`, `tests/sql/test_outcome_open_command.sql` -- schema·OPEN RPC fixture; 새 컬럼과 A~E 저장을 검증할 표면.
- `tests/sql/test_run_lineage.sql:594-1108`, `tests/sql/test_outcome_rebuild.sql:1-190` -- close 판정·SL 우선·TIMEOUT·재구축 회귀 fixture.
- `infra/supabase/migrations/202609051700_harden_outcome_strategy_snapshot_contract.sql`, `202609051800_preserve_outcome_strategy_check_order.sql`, `202609051900_revoke_outcome_snapshot_trigger_execute.sql` -- 리뷰에서 확인된 스냅샷 무결성·제약 오류 순서·내부 트리거 권한 경계를 forward-only로 보완한다.
- `packages/read-model/src/database.types.ts:18-60,580-650` -- Supabase 생성 타입의 outcome 테이블/함수 계약.
- `infra/supabase/migrations/README.md` -- UTC timestamp 및 forward-only migration 규칙.

## Tasks & Acceptance

**Execution:**
- [x] `infra/supabase/migrations/202609051600_parameterize_outcome_strategy_rules.sql` -- 전략 파라미터 권위 테이블/권한을 추가하고 candidate_outcome 및 event 전략 계약을 A~E로 확장한다 -- 신규 전략을 안전하게 저장한다.
- [x] 같은 migration의 `emit_open_command`, `publish_attempt`, `rebuild_outcome_projection` -- 파라미터 조회·OPEN payload 스냅샷·행별 TP/SL/TIMEOUT 판정·재생을 최신 함수에 create or replace로 반영한다 -- 운영 경로와 재구축 경로를 일치시킨다.
- [x] `packages/read-model/src/database.types.ts` -- 실제 스키마/RPC와 일치하도록 생성 타입을 갱신한다 -- 웹/서비스 호출 계약을 고정한다.
- [x] `tests/sql/test_outcome_schema.sql`, `tests/sql/test_outcome_open_command.sql` -- 컬럼·A~E 제약·A/B/C 보존·D/E별 OPEN 파라미터와 권한을 검증한다 -- 저장 경계를 증명한다.
- [x] `tests/sql/test_run_lineage.sql`, `tests/sql/test_outcome_rebuild.sql` -- D/E TP·SL·TIMEOUT, SL 우선, 비용, 과거 행 불변, rebuild 스냅샷 보존을 명시적 PASS assertion으로 추가한다 -- 판정과 재생 회귀를 고정한다.
- [x] 리뷰 보완 migration과 fixture -- 직접 projection 불일치·SL 범위·terminal 자연키 OPEN 충돌·D/E active tag publish·내부 trigger EXECUTE 노출을 차단하고 검증한다 -- 운영 경계를 닫는다.

**Acceptance Criteria:**
- Given A/B/C/D/E active tag가 있는 close attempt, when `emit_open_command`가 실행되면, then 각 행에 A/B/C=3/3/30, D=3/5/20, E=2/5/30의 tp_pct/sl_pct/cutoff_n이 저장되고 OPEN payload에도 기록된다.
- Given OPEN outcome의 오늘 관찰, when TP/SL을 계산하면, then 행별 `entry_price*(1+tp_pct/100)` 및 `entry_price*(1-sl_pct/100)`을 사용하고 SL 우선·왕복 0.1% 비용을 적용한다.
- Given TP/SL 미도달 관찰이 누적된 경우, when 저장된 cutoff_n에 도달하면, then TIMEOUT은 행별 cutoff와 오늘 종가 실손익으로 확정된다.
- Given Epic 3의 기존 A/B/C 행과 장부, when migration과 rebuild를 실행하면, then 기존 tp/sl/cutoff 및 terminal 결과를 재판정·변경하지 않고 장부는 수정하지 않는다.
- Given migration이 적용된 운영 DB, when SQL fixture와 catalog/함수 정의를 검사하면, then A~E 제약·service_role 권한·명시적 PASS assertion이 모두 통과한다.

## Review Triage Log

### 2026-09-04 — 독립 리뷰 4종

- intent_gap: 0
- bad_spec: 0
- patch: 4 (high 1, medium 3, low 0)
  - projection snapshot 불일치: `candidate_outcome` 직접 INSERT/UPDATE를 전략 권위값과 검증하도록 trigger를 추가했다. A/B/C의 기존 사용자 지정 cutoff_n은 보존하고 D/E는 전체 스냅샷을 고정했다.
  - SL 100% 이상 입력: 전략 규칙과 outcome snapshot 모두 `sl_pct < 100` 제약을 추가했다.
  - terminal natural-key와 새 OPEN 이벤트 충돌: 이미 terminal인 projection에 대응하는 OPEN event를 append하지 않도록 trigger와 fixture assertion을 추가했다.
  - D/E active tag 통합 검증 및 A payload 검증: `candidate_tags`에서 실제 `publish_attempt`로 이어지는 D/E fixture와 A OPEN payload assertion을 추가했다.
- defer: 2 (high 0, medium 2, low 0)
  - 기존 rebuild malformed payload 및 terminal trading_day/state-machine 의미 보강은 Epic 3 기존 동작 영역이다.
  - N/N-1 pre-migration 운영 행을 별도 생성하는 런타임 호환 fixture는 migration의 보존 코드와 현재 fixture 범위를 넘어선다.
- dismissed:
  - 전략 규칙 테이블의 별도 audit/history는 이번 스토리의 고정 seed·service-only 권위 계약에 포함되지 않는다.
  - UI, backtest 권위 동기화, 비정상 관찰 판정, correction state-machine의 확장은 이번 SQL parameterization 범위 밖이며 새 변경의 회귀가 아니다.
- final review result: 수정 후 운영 fixture·catalog 권한·advisory를 재검증했고, Story 6.5 범위 내 미해결 finding은 없다.

## Design Notes

전략 파라미터 테이블은 A~E의 현재 값을 seed하고 수정 권한을 제한한다. 새 컬럼은 기존 직접 fixture와 N/N-1 호환을 위해 A/B/C legacy 값을 backfill하되 기존 cutoff_n은 덮어쓰지 않는다. 신규 OPEN은 조회한 값을 event payload와 projection에 함께 저장하며, rebuild는 payload를 우선하고 payload가 없는 구형 A/B/C OPEN만 legacy 3/3/30으로 복구한다. `publish_attempt`는 최신 delisted/correction/rebuild 이후 정의를 기준으로 전체 함수를 재생성해 이전 단계 로직을 잃지 않게 한다.

## Verification

**Commands:**
- `python tools/check_migration_order.py` -- expected: timestamp 순서와 migration 정적 계약 통과.
- `uv run --with pandas --with numpy --with pyarrow --with pytest pytest backtest -q` -- expected: 기존 전략 회귀 통과.
- `git diff --check` -- expected: 공백 오류 없음.

**Manual checks (Supabase MCP):**
- 운영 프로젝트 `qqhjeumlecaudsiqhhdu`에 migration을 적용하고 catalog, `pg_get_functiondef`, 명시적 PASS fixture 결과를 확인한다. 실제 DB 적용 전에는 완료로 판정하지 않는다.

실행 결과:

- 운영 Supabase에 `202609051600`, `202609051700`, `202609051800`, `202609051900` migration 적용 성공.
- `test_outcome_schema.sql`, `test_outcome_open_command.sql`, `test_outcome_rebuild.sql`, `test_run_lineage.sql` 운영 fixture 모두 명시적 `pass`.
- 운영 catalog assertion: 전략값·snapshot 컬럼·A~E/SL 제약·snapshot trigger·service_role 전용 함수 권한 모두 `pass`.
- 운영 security advisor 재검사: 이번 변경으로 추가된 trigger 함수 공개 EXECUTE 경고를 제거했고, 남은 advisory는 기존 프로젝트 baseline이다.
- `uv run --with pandas --with numpy --with pyarrow --with pytest pytest backtest -q` — 131 passed.
- `npm run typecheck` — 통과.
- `python tools/check_migration_order.py` — 45 files 통과.
- `git diff --check` — 통과.
- Playwright MCP: UI 변경이 없는 SQL/backend 스토리이므로 실행하지 않았다.
