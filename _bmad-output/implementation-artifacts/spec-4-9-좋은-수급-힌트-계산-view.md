---
title: 'Story 4.9: 좋은 수급 힌트 계산 view'
type: 'feature'
created: '2026-09-09'
status: 'in-review'
review_loop_iteration: 0
followup_review_recommended: true
context:
  - 'C:/dev/wave-double/_bmad-output/implementation-artifacts/epic-4-context.md'
warnings: []
deferred: []
baseline_revision: '6810878917cfbf6e2fa74d7d93e7add242b961ea'
baseline_commit: '6810878917cfbf6e2fa74d7d93e7add242b961ea'
---

<intent-contract>

## Intent

**Problem:** 수급 힌트를 UI나 Python이 각각 계산하면 `0`과 미확정 NULL을 혼동하거나 구현별 결과가 달라질 수 있다.

**Approach:** `supply_3day`의 최신 D0 행을 대상으로 `candidate_supply_hints` versioned SQL view와 attempt-scoped read RPC를 만들고, 순수 domain rule을 동일한 경계값으로 유지한다. 확정 종가 배치에서 외인·기관·프로그램이 모두 `> 0`일 때만 `good`으로 반환하고, 그 외 확정값은 `not_met`, 미확정/미수집 또는 장중은 `undetermined`로 반환한다.

## Boundaries & Constraints

**Always:** `investor_net_status='confirmed'`이며 batch kind가 `close`인 경우에만 세 값의 엄격한 양수 비교를 한다. NULL/pending/missing과 장중 배치는 판정 불가로 보존한다. 읽기 RPC는 활성 태그 후보와 요청 attempt/current complete pointer를 함께 격리하고, 임계값은 SQL view의 한 곳에 둔다. `individual_net`은 상태 정합성에는 포함되지만 힌트 기준에는 포함하지 않는다.

**Never:** `>= 0`을 순매수로 취급하거나 UI에서 힌트를 재계산하지 않는다. 원본 `supply_3day`의 값/상태를 수정하지 않고, 브라우저에 테이블 직접 SELECT 권한을 부여하지 않는다.

## I/O & Edge-Case Matrix

| Scenario | Input / State | Expected Output / Behavior | Error Handling |
|---|---|---|---|
| HAPPY_PATH | close + confirmed + 외인/기관/프로그램 모두 양수 | `good` | 없음 |
| NOT_MET | close + confirmed + 값 중 하나가 0 이하 | `not_met` | `good`으로 승격하지 않음 |
| UNKNOWN | pending/missing 또는 NULL 값 | `undetermined` | `not_met`으로 오판하지 않음 |
| INTRADAY | intraday 행이 confirmed이거나 값이 비어 있음 | `undetermined` | 장중 확정 힌트로 노출하지 않음 |

</intent-contract>

## Code Map

- `infra/supabase/migrations/202609022000_create_supply_3day.sql:8-53` -- `supply_3day` 컬럼, 상태/NULL 일관성, D0 attempt 누적 계약의 원본이다.
- `infra/supabase/migrations/202609081201_harden_get_candidate_evidence_attempt_scope.sql:6-103` -- published read RPC의 security-definer, 복합 attempt 경계, anon/authenticated execute grant 패턴을 재사용한다.
- `infra/supabase/migrations/202609070900_supply_3day_publish_guard.sql:215-347` -- `runs`의 stage/publish/current-complete 구조와 `batch_kind`를 확인하는 기존 계약이다.
- `packages/domain/domain/__init__.py` 및 `packages/domain/domain/*.py` -- 외부 I/O 없는 Python 도메인 규칙의 공개/테스트 패턴이다.
- `packages/read-model/src/database.types.ts:649-710` -- generated read-model의 `Views`/`Functions` 계약을 새 view와 RPC에 맞춰 갱신한다.
- `tests/fixtures/supply_hint_cases.csv` -- Python 단위 테스트와 SQL migration gate가 공유하는 양수/0/음수/NULL/장중 fixture다.
- `tests/sql/test_supply_hints.sql` -- view 계산, RPC attempt 격리, NULL/0 구분, ACL을 rollback fixture로 검증한다.
- `.github/workflows/test.yml` -- domain 테스트와 SQL fixture 실행 목록에 새 검증을 등록한다.

## Tasks & Acceptance

**Execution:**
- [x] `packages/domain/domain/supply_hint.py`, `packages/domain/domain/__init__.py` -- `good/not_met/undetermined` 순수 판정 규칙과 공개 export를 구현한다 -- SQL과 비교할 기준값을 고정한다.
- [x] `tests/fixtures/supply_hint_cases.csv`, `tests/domain/test_supply_hint.py` -- 동일 fixture의 경계값과 장중 상태를 검증한다 -- Python 기준값을 회귀망으로 만든다.
- [x] `infra/supabase/migrations/202609091000_create_candidate_supply_hints.sql` -- D0 view와 `get_candidate_supply_hints(uuid)` security-definer RPC를 추가하고 published/current complete 및 active tag 경계를 적용한다 -- UI가 승인된 read model만 소비하게 한다.
- [x] `tests/sql/test_supply_hints.sql` -- view/RPC 결과가 공유 fixture와 일치하고 0, NULL, pending/missing, intraday, 비공개 attempt가 격리되는지 explicit pass row로 검증한다.
- [x] `packages/read-model/src/database.types.ts`, `apps/web/lib/dashboard-types.ts` -- view/RPC 반환 shape와 3상태 계약을 추가한다 -- 다음 스토리의 UI 소비 경계를 고정한다.
- [x] `.github/workflows/test.yml` -- Python domain test와 SQL fixture를 CI에 등록한다 -- migration 계약의 자동 회귀를 보장한다.

**Acceptance Criteria:**
- Given close 배치의 confirmed D0 행일 때, when versioned view/RPC를 호출하면, then 외인·기관·프로그램이 모두 `> 0`인 경우에만 `good`을 반환한다.
- Given confirmed D0에서 세 값 중 하나라도 0 이하일 때, when 판정하면, then `not_met`을 반환한다.
- Given pending/missing 또는 순매수 NULL일 때, when 판정하면, then `undetermined`를 반환해 `not_met`과 구분한다.
- Given intraday attempt일 때, when confirmed 값이 있더라도, then 힌트는 `undetermined`로 유지된다.
- Given 동일한 CSV fixture를 Python과 SQL에 적용할 때, when migration gate를 실행하면, then 모든 case의 판정 결과가 동등하고 RPC는 published current complete attempt의 active 후보만 반환한다.
- Given 브라우저 역할이 view/table을 직접 조회하려 할 때, when ACL을 확인하면, then 원본 테이블과 view SELECT는 차단되고 승인된 RPC만 anon/authenticated/service_role에 실행 권한이 있다.

## Spec Change Log

## Review Triage Log

### 2026-09-09 — 자체 review
- 독립 reviewer/subagent 레이어는 현재 실행 환경에 도구가 없어 실행하지 못했다.
- 자체 검토에서 임계값(`> 0`), NULL/상태 구분, close/intraday 분기, 최신 D0 선택, active tag, published/current-complete attempt, 원본 table/view ACL을 diff와 운영 fixture로 재확인했다.
- 운영 fixture 작성 중 발견한 provenance·market publish 선행계약 누락과 close/intraday attempt 혼합을 fixture에 보완했으며, 제품 코드의 triage 대상 결함은 남지 않았다.

### 2026-09-09 — 독립 리뷰 patch 보완
- 운영 적용 migration `202609091000`과 intent-contract는 보존하고 `202609091001_harden_candidate_supply_hints.sql`을 forward-only로 추가했다.
- candidate trading_day와 일치하는 D0만 view가 선택하고, D0가 없는 active 후보는 `missing`/`undetermined` nullable payload로 RPC에 포함되도록 보완했다.
- Python/SQL 공유 fixture에 slot 및 foreign_net 0/음수 경계를 추가하고 SQL fixture와 CSV drift 검사를 고정했다.
- RPC 전체 payload, authenticated role 조건부 호출, dashboard nullable 타입과 웹 runtime validator/literal narrowing 테스트를 추가했다.

### 2026-09-09 — 후속 patch 보완
- `compute_supply_hint`의 slot 기본값을 제거해 모든 호출자가 명시적인 D0/D-1/D-2를 전달하도록 고쳤다.
- SQL fixture의 중복 case `VALUES`/comment block을 제거하고 psql `\copy`로 공유 CSV를 직접 소비하도록 바꿨다. MCP 검증은 동일 CSV 기반 equivalent INSERT로 실행한다.
- view/RPC fixture의 단건 조회에 `FOUND`/count 및 `IS DISTINCT FROM` 방어를 추가하고, date JSON string과 missing row 전체 payload를 검증한다.

## Design Notes

`good`/`not_met`/`undetermined`는 저장·전송용 안정적 코드이며 한국어 라벨은 Story 4.10 UI가 매핑한다. SQL view가 `batch_kind='close'`까지 확인하므로 upstream 상태가 잘못 확정된 장중 행도 좋은 수급으로 노출되지 않는다. RPC는 후보의 `trading_day`와 D0를 묶어 같은 attempt의 과거 행이나 다른 attempt의 후보가 섞이지 않게 한다.

## Verification

**Commands:**
- `uv run --with pytest pytest tests/domain/test_supply_hint.py -q` -- expected: 공유 fixture 전건 통과.
- `npm run typecheck` -- expected: read-model/web 타입 오류 없음.
- `python tools/check_migration_order.py` -- expected: migration filename/order contract 통과.
- `psql ... -f tests/sql/test_supply_hints.sql` -- expected: `story_4_9_supply_hints: pass`.
- `git diff --check` -- expected: whitespace 오류 없음.

**실행 결과:**
- `uv run --with pytest pytest tests/domain/test_supply_hint.py -q` — 3 passed.
- `npm test` — 98 passed; `npm run typecheck` 및 `npm run build` 통과.
- `python tools/check_migration_order.py` — 58 files 통과.
- 운영 Supabase MCP `apply_migration` — 성공; `execute_sql` rollback fixture — `story_4_9_supply_hints: pass`.
- 운영 catalog/grant 확인 — anon/authenticated의 원본 table/view SELECT는 false, RPC EXECUTE는 anon/authenticated/service_role true, PUBLIC EXECUTE는 false.
- 로컬 `psql`/Supabase CLI는 설치되어 있지 않아 SQL fixture는 운영 Supabase MCP로 검증했다.

## Suggested Review Order

**SQL 판정 및 공개 경계**

- 최신 D0와 세 투자자 임계값을 한 view에서 계산한다.
  [`202609091001_harden_candidate_supply_hints.sql:5`](../../infra/supabase/migrations/202609091001_harden_candidate_supply_hints.sql#L5)

- published current complete attempt와 active tag 후보만 RPC로 제한한다.
  [`202609091001_harden_candidate_supply_hints.sql:76`](../../infra/supabase/migrations/202609091001_harden_candidate_supply_hints.sql#L76)

- 원본 table/view 직접 SELECT를 차단하고 RPC 실행 권한만 부여한다.
  [`202609091001_harden_candidate_supply_hints.sql:132`](../../infra/supabase/migrations/202609091001_harden_candidate_supply_hints.sql#L132)

**Python 기준 규칙**

- SQL과 동일한 close·confirmed·엄격한 양수 판정을 순수 함수로 고정한다.
  [`supply_hint.py:33`](../../packages/domain/domain/supply_hint.py#L33)

**회귀·소비 계약**

- 공유 fixture로 0, 음수, NULL, 상태, 장중 경계를 모두 회귀 검증한다.
  [`test_supply_hint.py:15`](../../tests/domain/test_supply_hint.py#L15)

- 운영 rollback fixture에서 attempt 격리와 ACL까지 explicit pass로 확인한다.
  [`test_supply_hints.sql:1`](../../tests/sql/test_supply_hints.sql#L1)

- 다음 UI 스토리가 사용할 view/RPC 반환 shape와 3상태를 확인한다.
  [`dashboard-types.ts:74`](../../apps/web/lib/dashboard-types.ts#L74)

- RPC row의 nullable missing payload와 literal narrowing을 웹 경계에서 검증한다.
  [`supply-hints.ts:38`](../../apps/web/lib/supply-hints.ts#L38)

- domain 및 SQL fixture가 CI에서 실행되도록 등록한다.
  [`test.yml:34`](../../.github/workflows/test.yml#L34)
