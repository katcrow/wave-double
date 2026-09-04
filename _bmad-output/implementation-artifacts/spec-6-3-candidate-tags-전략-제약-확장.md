---
title: 'candidate_tags 전략 제약 확장'
type: 'feature'
created: '2026-09-04'
status: 'done'
baseline_revision: '623d5db3a97478e237cf874330fc3fd41645276c'
review_loop_iteration: 0
followup_review_recommended: true
context:
  - 'C:/dev/wave-double/_bmad-output/implementation-artifacts/epic-6-context.md'
warnings: []
deferred:
  - summary: >-
      운영 대용량 테이블에서 ALTER TABLE lock 사전 점검
    evidence: |-
      현재 candidate_tags 운영 행 수는 0이며, 일반 migration 운영 lock 정책은 별도 운영 스토리로 다룬다.
    location: >-
      infra/supabase/migrations/202609051400_expand_candidate_tags_strategy_check.sql:5-31
    severity: low
---

<intent-contract>

## Intent

**Problem:** `candidate_tags.strategy`가 A/B/C만 허용해 전략 D/E 태그를 저장할 수 없다.

**Approach:** 기존 제약을 삭제·재생성하는 forward-only Supabase migration으로 허용 전략을 A/B/C/D/E로 확장하고, 기존 태그의 삽입·조회·다중 태그·무결성 계약을 SQL fixture로 회귀 검증한다.

## Boundaries & Constraints

**Always:** 기존 A/B/C 행과 `(candidate_id, strategy, attempt_run_id)` 유일성, 합성 FK, RLS, attempt-scoped 의미를 보존한다. migration은 UTC timestamp 순서와 `begin`/`commit` 원자성을 지키고 D와 E를 각각 삽입할 수 있음을 검증한다. 생성 read-model 타입과 기존 조회 RPC의 동적 `strategy` 의미는 불필요하게 변경하지 않는다.

**Never:** 기존 migration을 수정하거나 down migration을 추가하지 않는다. 전략 계산 API, 태깅 stage, outcome, UI, 신규 후보 원천을 이번 스토리에 구현하지 않는다. A/B/C의 기존 데이터나 쿼리 결과를 재작성하지 않는다.

## I/O & Edge-Case Matrix

| Scenario | Input / State | Expected Output / Behavior | Error Handling |
|----------|--------------|---------------------------|----------------|
| HAPPY_PATH | 기존 후보/attempt와 A/B/C/D/E 전략값 | 다섯 전략 태그가 저장되고 같은 후보의 다중 태그가 허용됨 | 오류 없음 |
| LEGACY_COMPATIBILITY | 기존 A/B/C 행 및 기존 전략 필터 조회 | 행·유일성·FK·RLS와 A/B/C 조회 의미가 유지됨 | 회귀 시 fixture가 실패 |
| INVALID_STRATEGY | 전략값 F 또는 중복 태그 | CHECK 위반 또는 unique 위반으로 거부됨 | SQL 예외를 fixture에서 명시적으로 포착 |

</intent-contract>

## Code Map

- `infra/supabase/migrations/202609021600_create_candidate_tags.sql:8-29` -- 원본 테이블 정의와 현재 `strategy in ('A','B','C')` CHECK, 유일성·합성 FK·RLS 계약. 수정하지 않고 후속 migration의 기준으로만 사용한다.
- `infra/supabase/migrations/README.md:5-22` -- UTC 12자리 timestamp, 정렬 적용, forward-only·원자적 migration 규약.
- `infra/supabase/migrations/202609032200_add_outcome_correction_mechanism.sql:7-13` -- 기존 migration 불변 및 `begin`/additive 변경 패턴 참고.
- `tests/sql/test_candidate_tags.sql:24-105` -- 정상 A/B/C/D/E 삽입, stage 결과, 다중 태그, 전략별 UNIQUE, FK/RLS와 잘못된 전략 거부를 검증한다.
- `tests/sql/test_candidate_tags_upgrade.sql:1-78` -- N-1 CHECK와 기존 A/B/C 행을 만든 뒤 실제 Story 6.3 migration을 적용해 행 보존·D/E 허용을 검증한다.
- `.github/workflows/test.yml:65-112` -- 정렬된 전체 migration 적용 후 `test_candidate_tags.sql`을 실행하는 clean Postgres 16 CI 게이트.
- `tools/check_migration_order.py:9-60` -- migration filename timestamp·정렬 계약 검사.
- `202609031000_create_sync_vanished_tags.sql:45-75`, `202609031100_add_vanished_strategies_to_get_today_candidate_cards.sql:38-64` -- 전략값을 동적으로 전달하는 기존 조회 경계. A/B/C 상수 변경은 필요하지 않다.
- `packages/read-model/src/database.types.ts:99-137` -- `candidate_tags.strategy`가 이미 일반 `string`인 생성 타입. migration 후 재생성·변경하지 않는다.

## Tasks & Acceptance

**Execution:**
- `infra/supabase/migrations/202609051400_expand_candidate_tags_strategy_check.sql` -- 기존 CHECK를 A/B/C/D/E 허용 제약으로 교체하고 설명을 갱신한다 -- 운영 스키마를 forward-only로 확장한다.
- `infra/supabase/migrations/202609051500_finalize_candidate_tags_strategy_contract.sql` -- 이미 적용된 환경의 constraint precondition과 RPC/table 설명을 동기화한다 -- migration 적용 이력과 운영 스키마의 관찰 가능 계약을 맞춘다.
- `tests/sql/test_candidate_tags.sql` -- D/E 삽입 성공, A/B/C 기존 조회·다중 태그·UNIQUE/FK/RLS 회귀, 잘못된 전략 거부를 명시적 SQL assertion으로 검증한다 -- clean reset CI에서 스키마 호환성을 증명한다.
- `tests/sql/test_candidate_tags_upgrade.sql`, `.github/workflows/test.yml` -- N/N-1 upgrade fixture를 전체 schema CI에 등록한다 -- 기존 A/B/C 행 보존을 clean reset만으로 놓치지 않게 한다.

**Acceptance Criteria:**
- Given N-1 CHECK와 기존 A/B/C 태그 행, when 새 migration 파일을 적용하면, then 기존 행·기본값·유일성·합성 FK·RLS가 보존되고 CHECK가 A/B/C/D/E를 허용한다.
- Given 유효한 후보와 attempt, when D와 E 태그를 각각 삽입하면, then 같은 후보에 기존 전략과 함께 다중 태그가 저장되고 기존 A/B/C 필터 조회도 이전 의미를 유지한다.
- Given 전략 F 또는 동일 `(candidate_id, strategy, attempt_run_id)`를 삽입하면, then CHECK 또는 UNIQUE 위반으로 거부된다.
- Given clean Postgres 16에서 전체 migration과 두 candidate_tags fixture를 실행하면, then migration 순서 검사와 schema CI 게이트가 통과한다.

## Review Triage Log

### 2026-09-04 — Review pass
- intent_gap: 0
- bad_spec: 0
- patch: 8: (high 0, medium 4, low 4)
- defer: 1: (high 0, medium 0, low 1)
- dismissed:
  - fixture의 constraint/index catalog 직접 검사 누락 — migration이 테이블을 재생성하지 않고 기존 UNIQUE/FK를 유지하며, upgrade fixture와 유효·중복 삽입이 결과 계약을 직접 검증한다.
  - 모든 잘못된 문자열 변형 테스트 누락 — 정확한 allowlist의 대표값 F와 NOT NULL 제약으로 경계가 검증되며 모든 invalid 문자열을 열거할 필요는 없다.
  - get_today_candidate_cards·sync_vanished_tags에 D/E 별도 케이스 부족 — 두 경로는 전략값을 동적으로 집계하고 현재 변경의 표면은 candidate_tags 스키마이며, 실제 태깅 연동은 후속 Story 6.6 범위다.
  - 실패 중간 단계의 rollback negative fixture 부족 — migration 자체가 begin/commit 원자 블록이고 실제 운영 적용이 성공했으며, 실패 주입은 이 단순 제약 교체의 관찰 가능한 계약을 추가하지 않는다.
  - frontmatter follow-up 플래그와 검증 증거 부족 — 검수 전 상태 지적이며 아래 최종 결과에 실제 증거와 계산된 플래그를 반영한다.
- addressed_findings:
  - `[medium]` `[patch]` five-tag fixture metadata — tags stage의 `tagged_count`를 5로 고치고 저장된 stage result를 assertion했다.
  - `[medium]` `[patch]` missing N/N-1 upgrade coverage — 실제 migration 파일을 호출하는 upgrade fixture와 CI 등록을 추가해 기존 A/B/C 행 보존을 검증했다.
  - `[medium]` `[patch]` migration constraint-name drift — 구 A/B/C 제약의 이름·정의를 사전 확인하고 불일치 시 fail-closed하도록 수정했다.
  - `[medium]` `[patch]` D/E uniqueness coverage — D 중복 삽입 거부를 fixture에 추가했다.
  - `[low]` `[patch]` stale fixture instructions — Story 6.3 및 전체 migration 기준으로 갱신했다.
  - `[low]` `[patch]` missing D/E default assertion — D/E 태그의 active 기본값을 검증했다.
  - `[low]` `[patch]` RLS deny-all evidence — candidate_tags에 정책이 생기지 않았음을 catalog assertion으로 검증했다.
  - `[low]` `[patch]` stale downstream RPC/table documentation — 새 forward migration에서 A/B/C/D/E 설명으로 동기화했다.
- deferred:
  - 운영 대용량 테이블에서 ALTER TABLE lock 사전 점검 — 현재 candidate_tags 운영 행 수는 0이며, 일반 migration 운영 lock 정책은 별도 운영 스토리로 다룬다.

## Design Notes

원본 제약은 이름을 명시하지 않았으므로 PostgreSQL의 기본 이름 `candidate_tags_strategy_check`를 대상으로 한다. migration은 기존 제약의 이름·A/B/C 정의를 사전 확인한 뒤 불일치 시 즉시 실패하고, 일치할 때만 동일 이름의 A/B/C/D/E CHECK로 교체한다. 기존 테이블을 재생성하지 않아 데이터와 인덱스·RLS를 보존한다.

## Verification

**Commands:**
- `python tools/check_migration_order.py` -- expected: migration filename/order contract passes.
- `docker compose` 또는 CI와 동일한 Postgres 16 clean schema에 전체 migration 적용 -- expected: 새 migration 포함 전체 적용 성공.
- `psql ... -v ON_ERROR_STOP=1 -f tests/sql/test_candidate_tags.sql` -- expected: A/B/C/D/E·stage 결과·제약 fixture passes.
- `psql ... -v ON_ERROR_STOP=1 -f tests/sql/test_candidate_tags_upgrade.sql` -- expected: N/N-1 upgrade fixture returns an explicit PASS row.
- `Supabase MCP apply_migration + execute_sql` -- expected: 운영 프로젝트의 migration 기록, A/B/C/D/E constraint, candidate_tags fixture가 모두 explicit PASS를 반환한다.
- `git diff --check` -- expected: whitespace errors 없음.

## Auto Run Result

Summary: `candidate_tags.strategy`의 허용 전략을 A/B/C에서 A/B/C/D/E로 forward-only 확장하고, 기존 A/B/C 데이터·다중 태그·UNIQUE/FK/RLS 계약과 N/N-1 upgrade 경로를 SQL fixture로 검증했다. 운영 Supabase에도 두 migration을 적용해 실제 constraint와 fixture를 확인했다.

Files changed:
- `infra/supabase/migrations/202609051400_expand_candidate_tags_strategy_check.sql` — 구 CHECK를 fail-closed 사전조건과 함께 A/B/C/D/E로 교체.
- `infra/supabase/migrations/202609051500_finalize_candidate_tags_strategy_contract.sql` — 적용 환경의 constraint와 table/RPC 설명 동기화.
- `tests/sql/test_candidate_tags.sql` — 다섯 전략·stage count·D uniqueness·RLS deny-all 회귀 추가.
- `tests/sql/test_candidate_tags_upgrade.sql` — 실제 Story 6.3 migration을 호출하는 N/N-1 보존 fixture 추가.
- `.github/workflows/test.yml` — upgrade fixture를 schema CI에 등록.
- `_bmad-output/implementation-artifacts/spec-6-3-candidate-tags-전략-제약-확장.md` — 구현 계획·검수·실행 결과 기록.

Review findings breakdown: patch 8건(중간 4, 낮음 4)을 수정했고, 운영 대용량 테이블 lock 사전 점검 1건(낮음)은 별도 운영 범위로 이월했다. 나머지 5건은 기존 동적 조회 계약, 직접 결과 검증, 대표 invalid 경계, 명시적 transaction block, 최종 메타데이터 반영으로 각 사유를 위 triage log에 기록하고 기각했다.

Follow-up review recommendation: true (patched high 0, medium 4, low 4; score 16 = 3×4 + 4).

Verification: `python tools/check_migration_order.py` passed (41 files); `git diff --check` passed; Docker/psql 미설치로 로컬 clean Postgres 실행은 불가했다. 운영 Supabase `apply_migration` returned success for `202609051400_expand_candidate_tags_strategy_check` and `202609051500_finalize_candidate_tags_strategy_contract`; constraint catalog query returned explicit PASS with `A/B/C/D/E`; `test_candidate_tags` returned explicit PASS with five strategies and `tagged_count=5`; `test_candidate_tags_upgrade` returned explicit PASS with `legacy_rows_preserved=3` and D/E accepted. Security advisor의 candidate_tags RLS-without-policy INFO는 기존 deny-all 설계로 유지했다.

Residual risks: 로컬 Docker/psql 부재로 CI와 동일한 clean Postgres job 자체는 이 실행에서 재현하지 못했고, 대용량 운영 테이블의 ALTER TABLE lock 사전 점검은 이월했다. 전략 D/E를 실제 계산·태깅 stage에 연결하는 작업은 후속 Stories 6.4/6.6 범위다.
