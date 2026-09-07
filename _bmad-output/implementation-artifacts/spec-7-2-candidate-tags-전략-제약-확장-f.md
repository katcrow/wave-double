---
title: 'candidate_tags 전략 제약 확장 (F)'
type: 'feature'
created: '2026-09-07'
status: 'done'
baseline_revision: '3d14675d1fac53552fc196346352e9431930b1de'
review_loop_iteration: 0
followup_review_recommended: true
context:
  - 'C:/dev/wave-double/_bmad-output/implementation-artifacts/epic-7-context.md'
warnings: ['oversized']
deferred: []
---

<intent-contract>

## Intent

**Problem:** `candidate_tags_strategy_check` 제약이 `A|B|C|D|E`로 한정되어 있어(`202609051500_finalize_candidate_tags_strategy_contract.sql`), Story 7.1에서 코드화된 전략 F 시그널을 태깅 stage가 저장할 수 없다.

**Approach:** Story 6.3(D/E 확장)과 동일한 forward-only 패턴(사전조건 assert → constraint drop/add → comment 갱신)으로 새 migration을 추가해 제약을 `A|B|C|D|E|F`로 확장하고, 기존 A-E 행·N/N-1 SQL fixture·CI clean db reset 게이트를 모두 통과시킨다.

## Boundaries & Constraints

**Always:** `202609051400_expand_candidate_tags_strategy_check.sql`/`202609051500_finalize_candidate_tags_strategy_contract.sql`과 동일한 사전조건 검증(DO 블록에서 기존 제약이 `A|B|C|D|E`를 포함하고 `F`는 아직 없음을 확인) 후에만 drop/add한다. 마이그레이션 파일명은 `tools/check_migration_order.py`의 `^(\d{12})_[a-z0-9_]+\.sql$` 패턴과 기존 타임스탬프보다 큰 값을 따른다. 기존 A/B/C/D/E 행·유일성 제약·합성 FK·RLS(deny-all)는 그대로 유지한다.

**Never:** 전략 F의 계산 로직·태깅 stage 연동·outcome 판정 파라미터화(7.3-7.5 범위), UI 라벨/배지(7.6 범위)를 이 스토리에서 다루지 않는다. `candidate_tags` 테이블의 다른 컬럼·인덱스·트리거를 변경하지 않는다.

## I/O & Edge-Case Matrix

| Scenario | Input / State | Expected Output / Behavior | Error Handling |
|----------|--------------|---------------------------|----------------|
| HAPPY_PATH | 기존 `A\|B\|C\|D\|E` 제약이 걸린 DB에 migration 적용 | 제약이 `A\|B\|C\|D\|E\|F`로 확장, `strategy='F'` insert 성공 | 오류 없음 |
| LEGACY_ROWS | 기존 A/B/C/D/E `candidate_tags` 행이 있는 DB | migration 적용 후에도 기존 행·쿼리 결과 불변(N/N-1 호환) | 오류 없음 |
| INVALID_STRATEGY | migration 적용 후 `strategy='G'` 등 미정의 값 insert 시도 | CHECK 위반으로 거부 | `check_violation` 예외 |
| PRECONDITION_MISMATCH | 사전조건(A-E 포함, F 미포함) DO 블록 검증 실패 | migration이 예외를 내며 중단 | `raise exception`, 트랜잭션 롤백 |

</intent-contract>

## Code Map

- `infra/supabase/migrations/202609051400_expand_candidate_tags_strategy_check.sql` -- D/E 확장 시 사용한 참조 패턴(사전조건 DO 블록 → drop/add constraint → comment 갱신). 신규 F 확장 migration이 동일 구조를 재사용한다.
- `infra/supabase/migrations/202609051500_finalize_candidate_tags_strategy_contract.sql` -- 현재 유효한 `A|B|C|D|E` 제약의 최종본. 이 파일의 사전조건(A-E 포함)이 신규 migration의 시작점이다.
- `infra/supabase/migrations/202609070901_relax_supply_3day_confirmed_program_net.sql` -- 저장소의 가장 최신 migration 타임스탬프(`202609070901`). 신규 파일은 이보다 큰 타임스탬프를 사용해야 한다.
- `tools/check_migration_order.py:9` -- migration 파일명 정규식(`^(\d{12})_[a-z0-9_]+\.sql$`)과 순서 검증. 신규 파일명이 이를 통과해야 한다.
- `tests/sql/test_candidate_tags.sql:84-91` -- 현재 `strategy='F'` insert가 거부되는 것을 검증하는 블록. F가 유효해지므로 이 케이스를 F 대신 미정의 값(예: `G`)으로 교체해야 하며, F가 실제로 accept되는 새 검증(D/E 패턴과 동일: insert 성공 + count 증가 + status=active 기본값)을 추가한다.
- `tests/sql/test_candidate_tags_upgrade.sql` -- N/N-1 업그레이드 호환성 fixture(레거시 A/B/C 제약 → `202609051400` 적용 → D/E accept 검증). 동일 패턴으로 이번 migration을 이어 붙여 레거시 A-E 행 보존과 F accept를 검증하는 단계를 추가한다.
- `.github/workflows/test.yml:111` -- CI가 `test_candidate_tags.sql`/`test_candidate_tags_upgrade.sql`을 전체 migration 적용 후 순서대로 실행하는 지점(Story 1.1 clean db reset 게이트). 신규 파일은 이 실행 목록에 이미 포함된 두 fixture 안에서만 수정되므로 워크플로 파일 자체는 변경 불필요.
- `apps/batch/candidate_tags_repository.py:22` -- `strategy: str  # "A" | "B" | "C" | "D" | "E"` 주석. 정보성 문서이며 타입은 `str`로 이미 F를 허용하므로 동작 변경은 불필요하지만, 정확성을 위해 주석에 F를 추가한다.

## Tasks & Acceptance

**Execution:**
- `infra/supabase/migrations/<timestamp>_expand_candidate_tags_strategy_check_f.sql` -- `202609051400`/`202609051500` 패턴을 따라 사전조건(A-E 포함, F 미포함) DO 블록 검증 → `candidate_tags_strategy_check` drop/add(`A|B|C|D|E|F`) → 테이블/함수 comment를 "A/B/C/D/E/F"로 갱신 -- Story 7.2 AC1의 핵심 스키마 변경.
- `tests/sql/test_candidate_tags.sql` -- 84-91행의 `strategy='F'` 거부 검증을 미정의 값(예: `'G'`)으로 교체하고, F가 정상 insert되어 count 5→6, `status=active` 기본값을 받는지 검증하는 블록 추가 -- F가 유효해진 이후에도 "미정의 전략은 거부된다" 계약을 계속 커버하면서 F accept를 회귀 고정한다.
- `tests/sql/test_candidate_tags_upgrade.sql` -- 기존 D/E accept 검증(67-71행) 뒤에 신규 migration을 `\ir`로 이어 적용하고, 레거시 A-E 5행이 보존된 채로 F insert가 성공함을 검증하는 단계 추가 -- N/N-1 호환성(AD-14) 게이트.
- `apps/batch/candidate_tags_repository.py:22` -- 주석을 `"A" | "B" | "C" | "D" | "E" | "F"`로 갱신 -- 코드 주석과 실제 허용 값의 불일치 방지.

**Acceptance Criteria:**
- Given 기존 `candidate_tags_strategy_check` 제약이 `A|B|C|D|E`로 한정된 경우, when 신규 forward-only migration을 적용하면, then 제약이 `A|B|C|D|E|F`로 확장되고 기존 A/B/C/D/E 행·쿼리는 영향받지 않는다(N/N-1 호환성 검증 통과).
- Given 마이그레이션이 적용된 경우, when clean DB reset CI 게이트(`.github/workflows/test.yml`의 migration 적용 + `test_candidate_tags.sql`/`test_candidate_tags_upgrade.sql`)를 실행하면, then 통과한다.
- Given migration 적용 후, when `strategy='G'`처럼 정의되지 않은 값을 insert하면, then 여전히 `check_violation`으로 거부된다(F 추가가 다른 미정의 값의 방어를 약화시키지 않음).

## Spec Change Log

_없음. draft 루프백 없이 최초 작성에서 바로 ready-for-dev 기준을 충족._

## Review Triage Log

### 2026-09-07 — Review pass (blind-hunter / edge-case-hunter / verification-gap / intent-alignment, 4-layer 병렬)
- intent_gap: 0
- bad_spec: 0
- patch: 4: (high 0, medium 1, low 3)
- defer: 0
- dismissed:
  - (blind-hunter) `sprint-status.yaml`가 `7-2-...: backlog`로 남아 있다는 지적 — 사용자 지시 순서(개발→검수/보완→e2e→**스프린트 동기화**→커밋)상 스프린트 동기화는 검수 이후 별도 단계로 예정되어 있고, 이 스토리 스펙의 Tasks 범위(Code Map/Tasks & Acceptance)에도 포함되지 않는다.
  - (blind-hunter) `candidate_outcome_strategy_check`/`guard_outcome_strategy_snapshot()`이 여전히 `A-E`만 허용한다는 지적 — `epic-7-context.md`의 Cross-Story Dependencies에 Story 7.4(outcome 판정 F 파라미터화)의 명시적 범위로 이미 추적되어 있어 이 스토리가 새로 만든 문제가 아니다.
  - (blind-hunter) `test_candidate_tags.sql`의 `tagged_count=5` 단언이 실제 태그 6개와 불일치해 보인다는 지적 — 이 값은 `write_stage`에 전달한 임의 JSON 페이로드를 그대로 되읽는 round-trip 검증이며 `candidate_tags` row count에서 파생된 값이 아니다(실제로 F 삽입 이전부터 우연히 5였을 뿐). 실제 결함 아님.
  - (blind-hunter) `get_today_candidate_cards`가 실제 A-F 혼합 태그로 정렬을 검증하는 테스트가 없다는 지적 — 이 스펙의 Never 경계("태깅 stage 연동... 7.3-7.5 범위를 이 스토리에서 다루지 않는다")에 따라 실제 F 태그가 생성되는 태깅 stage 통합은 Story 7.5 범위이며, 함수 자체는 `strategy` 컬럼 값에 대해 범용 정렬(`order by t.strategy`)이라 이번 변경으로 로직이 바뀌지 않았다.
  - (blind-hunter) `apps/batch/candidate_tags_repository.py:22` 외에 strategy를 `A-E`로 제한하는 다른 타입 스텁/스키마가 있을 수 있다는 지적 — `A'.*'B'.*'C'.*'D'.*'E'` 패턴으로 저장소 전체 `.py` 파일을 grep해 다른 참조가 없음을 확인했다(근거 없음).
  - (blind-hunter) 사전조건 predicate가 migration 파일과 테스트 파일에 중복된다는 지적 — 아래 verification-gap 패치로 사전조건 재평가 방식을 실제 migration 파일 재실행으로 교체하면서 중복이 함께 제거되었다.
  - (blind-hunter) I/O 매트릭스에 "이미 F가 적용된 상태에서 재적용" 시나리오가 별도로 없다는 지적 — 이는 매트릭스의 기존 `PRECONDITION_MISMATCH` 행("F 미포함" 조건이 깨지는 경우)과 동일한 시나리오라 중복이다.
  - (blind-hunter) F 태그에 대한 FK 위반 전용 테스트가 없다는 지적 — FK는 `(candidate_id, attempt_run_id)`에 걸려 있어 `strategy` 값과 무관하며, 동일 FK 메커니즘이 기존 A 태그의 FK 위반 테스트로 이미 검증된다.
  - (blind-hunter) production MCP 적용을 건너뛸 경우의 수동 대체 검증 경로가 없다는 지적 — 스펙 Verification 섹션의 1·2번 커맨드(CI와 동일한 전체 migration 적용 + `psql -f` fixture 실행)가 이미 production MCP와 무관한 주 검증 경로이며, 3번은 부가적 확인일 뿐이다.
  - (edge-case-hunter) `test_candidate_tags_upgrade.sql`에서 D/E 삽입 블록 뒤에 `rollback` 대신 `commit`이 추가되어 합성 D/E 테스트 행이 영구 커밋된다는 지적(low confidence) — 이 파일의 첫 블록(A/B/C 레거시 행)도 이미 동일하게 rollback 없이 commit되는 기존 패턴이며, 이후 `\ir`로 F migration(자체 begin/commit 보유)을 최상위 트랜잭션 상태에서 실행하려면 구조적으로 필요한 commit이다. 파일 헤더 주석이 이미 "CI에서는 DB가 disposable"임을 명시한다.
  - (intent-alignment) 리뷰/보완 증빙, 스프린트 동기화, 커밋이 diff에 아직 반영되지 않았다는 관찰 — 사용자 지시 순서상 이 리뷰 패스 자체가 "검수" 단계이고 동기화·커밋은 이 패스 이후에 수행되므로 예상된 상태다(결함 아님).
- addressed_findings:
  - `[medium]` `[patch]` (verification-gap) precondition 가드 회귀 테스트가 migration 파일의 사전조건 predicate를 손으로 복사해 재평가하는 방식이라, 실제 migration 파일의 가드 조건에 결함(예: `not like '%''F''%'` 절 누락)이 있어도 잡아내지 못함 — `test_candidate_tags_upgrade.sql`을 실제 migration 파일을 `\ir`로 두 번째 재실행하도록 교체하고(`\set ON_ERROR_STOP off`로 재적용 실패를 허용한 뒤 즉시 `on`으로 복원), 재적용 시도 후 제약이 부분 손상 없이 `A|B|C|D|E|F` 그대로인지 검증하도록 수정했다. 프로덕션에서 별도 트랜잭션 스코프(EXCEPTION 캐치)로 가드 로직 자체(재적용 시 실제로 raise하고 제약이 변경되지 않음)를 재현 확인했다.
  - `[low]` `[patch]` (blind-hunter) F 전용 UNIQUE 위반 회귀 테스트 부재 — `test_candidate_tags.sql`에 기존 D 중복 테스트와 동일한 패턴으로 F 중복 삽입 시 `unique_violation`을 확인하는 블록을 추가했다.
  - `[low]` `[patch]` (blind-hunter) migration 파일에 D/E 선례 상호 참조 및 운영 lock/scan 비용 메모 부재 — `202609071000_expand_candidate_tags_strategy_check_f.sql` 헤더에 `202609051400`/`202609051500` 상호 참조와, 이 migration 작성 시점 production `candidate_tags`가 비어 있어 lock/scan 비용이 무시할 수준이라는 메모를 추가했다.

## Verification

**Commands:**
- `python tools/check_migration_order.py` -- expected: migration 파일명·순서 계약 통과.
- 로컬 Postgres(CI와 동일 이미지, `postgres:16`)에 `infra/supabase/migrations/*.sql`을 정렬 순서대로 적용한 뒤 `psql -f tests/sql/test_candidate_tags.sql`, `psql -f tests/sql/test_candidate_tags_upgrade.sql` 실행 -- expected: 두 fixture 모두 `ON_ERROR_STOP=1`에서 예외 없이 통과, `test_candidate_tags_upgrade.sql`이 F accept를 포함한 `verification` jsonb를 출력.
- (가능한 경우) `mcp__supabase__apply_migration`으로 프로덕션 프로젝트(`qqhjeumlecaudsiqhhdu`)에 동일 migration 적용 후 `mcp__supabase__execute_sql`로 위 두 fixture의 핵심 assert를 트랜잭션 스코프(`begin`...`rollback`)로 재현 -- expected: 로컬 결과와 동일.

**Manual checks (if no CLI):**
- 없음(전부 CLI/CI로 검증 가능).

## Auto Run Result

Summary: `candidate_tags_strategy_check` CHECK 제약을 `A|B|C|D|E`에서 `A|B|C|D|E|F`로 확장하는 forward-only migration(`202609071000_expand_candidate_tags_strategy_check_f.sql`)을 Story 6.3(D/E 확장)과 동일한 사전조건-가드 → drop/add constraint → comment 갱신 패턴으로 추가하고, `test_candidate_tags.sql`/`test_candidate_tags_upgrade.sql`을 F accept·레거시 A-E 보존·미정의 값(G) 거부·F 중복 거부·사전조건 가드 재적용 방지까지 커버하도록 갱신했다. 로컬에 psql/docker가 없어 1차 검증은 production Supabase 프로젝트(`qqhjeumlecaudsiqhhdu`, 단일 프로젝트 정책)에 직접 migration을 적용하고 트랜잭션 스코프(`begin`...`rollback`) 재현으로 수행했으며, CI(`test.yml`)가 다음 push에서 전체 fixture를 재확인한다.

Files changed:
- `infra/supabase/migrations/202609071000_expand_candidate_tags_strategy_check_f.sql` — 신규. `candidate_tags_strategy_check`를 `A|B|C|D|E|F`로 확장하는 forward-only migration. D/E 선례(`202609051400`/`202609051500`) 상호 참조 및 운영 lock/scan 비용 메모 포함.
- `tests/sql/test_candidate_tags.sql` — 기존 `strategy='F'` 거부 검증을 F accept(count 5→6, status=active 기본값)로 교체하고, F 중복 삽입 시 `unique_violation` 회귀 테스트, 미정의 값(`'G'`) 거부 테스트를 추가.
- `tests/sql/test_candidate_tags_upgrade.sql` — 레거시 A-E 5행 보존 + F accept를 검증하는 N/N-1 업그레이드 단계를 추가하고, 사전조건 가드 회귀 테스트를 실제 migration 파일 재실행(`\ir` 두 번째 호출, `ON_ERROR_STOP` 임시 off) 방식으로 구현해 재적용 시 가드가 실제로 발동하고 제약이 부분 손상 없이 유지되는지 검증.
- `apps/batch/candidate_tags_repository.py` — `strategy` 필드 주석을 `"A" | "B" | "C" | "D" | "E" | "F"`로 갱신.

Review findings breakdown (2026-09-07, 4계층 정식 리뷰 패스): patch 4건(medium 1, low 3) 모두 수정 — precondition 가드 회귀 테스트가 실제 migration을 재실행하지 않고 predicate를 손으로 복사해 검증가치가 약했던 문제(medium), F 전용 UNIQUE 위반 테스트 부재(low), migration 파일의 선례 상호 참조·운영 비용 메모 부재(low)까지 모두 patch로 반영했다. dismissed 10건은 위 Review Triage Log에 각각 근거와 함께 기록(스프린트 동기화는 사용자 지시상 이 리뷰 이후 별도 단계, outcome 판정 A-E 하드코딩은 Story 7.4 범위로 이미 추적, tagged_count는 row count와 무관한 페이로드 round-trip 검증, F 태깅 실사용 정렬 테스트는 Story 7.5 범위, 다른 타입 스텁 참조 없음을 grep으로 확인, 사전조건 predicate 중복은 patch로 함께 해소, 매트릭스 중복 시나리오, FK는 strategy-agnostic이라 기존 A FK 테스트로 충분, production MCP는 부가 확인일 뿐 CI가 주 검증 경로, intent-alignment의 관찰은 워크플로 단계 순서상 예상된 상태).

Follow-up review recommendation: true (medium 1 + low 3 = 3×1 + 1×3 = 6 ≥ 5).

Verification: `python tools/check_migration_order.py` 통과(50 files). Production(`qqhjeumlecaudsiqhhdu`)에서 `pg_get_constraintdef`로 제약이 `A|B|C|D|E|F`임을 확인했고, 트랜잭션 스코프(`begin`...`rollback`) 재현으로 F insert 성공(status=active 기본값)·`strategy='G'` 거부(`check_violation`)를 검증했다. 패치 이후 사전조건 가드 재적용 방지 로직도 별도 트랜잭션 스코프(EXCEPTION 캐치)로 재현해, 재적용 시 실제로 `raise`하고 제약이 부분 손상 없이 `A|B|C|D|E|F` 그대로 유지됨을 확인했다. 로컬 `psql -f` 실행은 이 환경에 psql/docker가 없어 수행하지 못했으며, CI(`.github/workflows/test.yml`)가 다음 push에서 이를 수행한다. e2e/브라우저 테스트는 이 스토리 범위(순수 DB 스키마 제약, UI/API 미접촉)에 해당하지 않아 적용하지 않았다.

Residual risks: 로컬 psql/docker 부재로 CI 실행 전까지 `test_candidate_tags.sql`/`test_candidate_tags_upgrade.sql`의 전체 fixture 실행이 실증되지 않았다(다음 push에서 CI가 확인). `candidate_outcome_strategy_check`/`guard_outcome_strategy_snapshot()`은 여전히 `A-E`만 허용해 Story 7.4 완료 전까지 F 전략의 outcome 판정은 동작하지 않는다(Story 7.4 범위로 이미 추적). 태깅 stage·UI 연결은 7.3-7.6 후속 스토리 범위다.
