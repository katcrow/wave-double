---
title: 'Story 5.1: bias_events append-only 스키마'
type: 'feature'
created: '2026-09-09'
status: 'done'
review_loop_iteration: 0
followup_review_recommended: true
context:
  - 'C:/dev/wave-double/_bmad-output/implementation-artifacts/epic-5-context.md'
warnings: []
deferred:
  - summary: >-
      bias_events 회차가 source 분해 행 없이 단독으로 존재할 수 있다.
    evidence: |-
      Story 5.1 AC는 회차와 source 행을 한 트랜잭션에 함께 append하도록 요구하지 않고,
      스키마도 이를 강제하지 않는다. 강제하려면 deferred constraint trigger가 필요해
      이 스토리 범위에서 trivially fixable하지 않다. 실제 쓰기 경로(Story 5.4)가 1+N을
      함께 append하고, 조회 UI(Story 5.13)는 어차피 명시적 빈 상태를 요구한다.
    location: >-
      infra/supabase/migrations/202609091700_create_bias_events.sql:12-18
    severity: low
  - summary: >-
      epic-5 경로 manifest가 여러 에픽이 공유하는 파일을 포함한다.
    evidence: |-
      packages/read-model/src/database.types.ts와 tools/production_parity_baseline.json은
      모든 에픽이 건드리는 파일인데 epic-5.txt에 들어 있어, manifest 자체 헤더가 말하는
      "정확한 경로로만 범위를 게이트한다" 원칙이 이 두 경로에서는 약해진다. 이번 스토리가
      실제로 두 파일을 바꿨으므로 제거할 수는 없고, epic 범위 게이트 규약 자체의 후속 정리 대상이다.
    location: >-
      tools/epic-path-manifests/epic-5.txt:4-7
    severity: low
baseline_revision: '9e884c306c6600253524c7e1245adb957ec94ef4'
baseline_commit: '9e884c306c6600253524c7e1245adb957ec94ef4'
---

<intent-contract>

## Intent

**Problem:** 모집단 편향 관측치를 담을 저장소가 없어 Story 5.3/5.4의 계산 결과를 적재할 수 없고, 재계산이 과거 관측치를 덮어쓰면 "그 날 편향이 얼마였는가"를 사후에 복원할 수 없다.

**Approach:** 회차 메타(`bias_events`)와 source별 분해(`bias_event_by_source`) 두 테이블을 DB 경계에서 UPDATE/DELETE가 거부되는 append-only로 만들고, 동일 거래일의 최신 회차만 노출하는 canonical view 한 쌍을 둔다. source 권위는 `candidate_source_contrib`에만 두고 bias 쪽에는 독립 source 사본을 만들지 않는다(AD-12/AD-21).

## Boundaries & Constraints

**Always:** 두 테이블 모두 trigger로 UPDATE/DELETE를 거부하고, 재계산은 새 `bias_event_id`로만 append한다. `bias_events`는 `source` 컬럼을 갖지 않으며 source 분해는 `bias_event_by_source`의 행으로만 표현한다. source 도메인 값은 `candidate_source_contrib.source`와 동일한 집합(`t1859|t1852|t1856`)으로 고정하고, source별 view는 `candidate_source_contrib`를 join해 기여 사실을 확인한다. canonical view는 `trading_day`별로 `created_at` 최신(동시각이면 `bias_event_id` 큰 쪽) 회차 하나만 선택한다. `trading_day`는 연결된 `logical_run_key`의 거래일과 일치해야 한다. 모든 카운트는 음수 불가이며 `intersection_count`는 두 집합 크기를 초과할 수 없다. RLS를 켜고 원본 테이블·view의 브라우저 SELECT는 차단한다. forward-only migration만 추가한다.

**Never:** 기존 migration 파일을 수정하거나 `bias_events`/`bias_event_by_source`에 source 사본·집계 사본을 두지 않는다. 편향 계산 로직(Story 5.3), close 배치 배선과 stage 기록(Story 5.4), 조회 RPC·UI(Story 5.13/5.14)는 이 스토리에서 구현하지 않는다. 기여가 없는 source 행(전부 0)을 스키마가 거부하지 않는다 — 폴백 source의 null-safe 0 행은 유효한 관측치다.

## I/O & Edge-Case Matrix

| Scenario | Input / State | Expected Output / Behavior | Error Handling |
|---|---|---|---|
| HAPPY_PATH | 한 거래일에 회차 1건 + source 3행 insert | 두 테이블에 그대로 적재되고 canonical view가 그 회차를 반환 | 없음 |
| RECALC_APPEND | 같은 `trading_day`에 두 번째 회차 append | 기존 행은 그대로 남고 canonical view는 최신 회차만 반환 | 없음 |
| MUTATION_REJECTED | 적재된 회차/source 행에 UPDATE 또는 DELETE | 두 테이블 모두 거부 | `55000` append-only 예외 |
| EMPTY_SOURCE | 폴백 source 행의 모든 카운트가 0 | 유효 행으로 적재되고 canonical view에 0으로 노출 | 없음 |
| BAD_COUNTS | 음수 카운트 또는 집합 크기보다 큰 `intersection_count` | 적재 거부 | check 제약 위반 |
| DAY_MISMATCH | `logical_run_key`의 거래일과 다른 `trading_day` | 적재 거부 | `BIAS_EVENT_TRADING_DAY_MISMATCH` |
| BROWSER_READ | anon/authenticated가 테이블·view 직접 SELECT | 권한 없음 | ACL 차단 |

</intent-contract>

## Code Map

- `infra/supabase/migrations/202609031300_create_outcome_schema.sql:6-87` -- append-only 원장의 기준 구현. `public.reject_outcome_ledger_mutation()`(59-69행)은 테이블명을 메시지에 넣는 범용 guard이므로 bias 테이블 trigger에서 그대로 재사용한다. RLS enable + `comment on table` 배치 순서도 이 파일을 따른다.
- `infra/supabase/migrations/202609011700_create_candidates.sql:17-31` -- `candidate_source_contrib(candidate_id, attempt_run_id, source, contribution_weight)`와 `source in ('t1859','t1852','t1856')` check가 source 권위의 원본이다. bias 쪽 source 도메인은 이 리스트와 동일해야 하며 drift는 SQL fixture가 막는다.
- `infra/supabase/migrations/202609011600_create_run_lineage.sql` -- `logical_runs(logical_run_key, trading_day, batch_kind, canonical_success_run_id, ...)`와 `runs`의 구조. `logical_run_key` FK와 거래일 일치 검증, canonical close 판별에 사용한다.
- `infra/supabase/migrations/202609091000_create_candidate_supply_hints.sql:5-132` -- view 정의 → `comment on view` → `revoke select on table ... from public, anon, authenticated` 순서의 read-model/ACL 패턴. `distinct on` + `order by ... desc`로 최신 행을 고르는 관용구(9-20행)를 canonical view에 재사용한다.
- `infra/supabase/migrations/202609081000_create_market_supply.sql:5-31` -- 최신 스키마 migration의 헤더 주석·`begin/commit`·컬럼 comment 스타일 기준이다.
- `tests/sql/test_market_supply.sql:1-40` -- `create temp table _*_fixture_results ... on commit drop` + `do $$ ... end $$` + explicit pass row 방식의 rollback fixture 구조. bias fixture도 이 구조를 따른다.
- `tests/sql/test_outcome_schema.sql` -- append-only trigger가 UPDATE/DELETE를 거부하는지 검증하는 기존 assertion 패턴이다.
- `.github/workflows/test.yml:196-215` -- `tests/sql/test_*.sql`를 자동 수집하므로 fixture 파일을 두는 것만으로 CI 게이트에 들어온다. 워크플로우 수정은 필요 없다.
- `tools/check_generated_types_drift.py:14-50` -- migration의 `create table`/`create view` 이름이 `packages/read-model/src/database.types.ts`에 없으면 CI 실패. 신규 테이블 2개와 view 2개를 타입에 반영해야 한다.
- `tools/production_parity_baseline.json` -- `migrations` 배열과 `functions` 딕셔너리를 운영 실측과 대조하는 baseline. 운영 적용 후 갱신 대상이다.
- `tools/check_migration_order.py:9-25` -- 파일명은 `^(\d{12})_[a-z0-9_]+\.sql$`이고 timestamp 중복이 금지된다. `REQUIRED_ORDER`는 Epic 3 전용이므로 수정하지 않는다.
- `tools/epic-path-manifests/epic-4.txt` -- epic별 경로 manifest 규약(`--epic N`). Epic 5 작업 범위를 게이트하려면 `epic-5.txt`가 필요하다.

## Tasks & Acceptance

**Execution:**
- `infra/supabase/migrations/202609091200_create_bias_events.sql` -- `bias_events`(source 컬럼 없음)와 `bias_event_by_source`를 생성하고, append-only trigger(기존 `reject_outcome_ledger_mutation` 재사용), 카운트/`calculation_meta` check, `logical_run_key` FK, 거래일 일치 검증 trigger, 조회 index, RLS, 테이블·컬럼 comment를 함께 둔다 -- Story 5.3/5.4의 적재 대상과 불변식을 DB 경계에 고정한다.
- 같은 migration -- `public.bias_events_canonical`(거래일별 최신 회차)과 `public.bias_event_by_source_canonical`(그 회차의 source별 행 + `candidate_source_contrib` join으로 확인한 기여 후보 수)을 만들고 원본 테이블·view의 브라우저 SELECT를 revoke한다 -- Story 5.6/5.13/5.14가 단일 row에서 source별 집계를 바로 읽게 하고 source 권위를 `candidate_source_contrib`로 유지한다.
- 운영 Supabase(`qqhjeumlecaudsiqhhdu`)에 위 migration을 적용한다 -- 운영이 로컬 선언과 어긋나는 drift를 만들지 않는다.
- `tests/sql/test_bias_events.sql` -- 스키마 계약, append-only 거부, 재계산 append 시 canonical 최신 선택과 과거 행 보존, 임의 `bias_event_id` 조회, 0 카운트 source 행 허용, 음수/초과 카운트 거부, 거래일 불일치 거부, source 도메인이 `candidate_source_contrib`와 동일함, 테이블·view ACL을 rollback fixture로 검증한다 -- I/O 매트릭스 전 케이스의 회귀망을 만든다.
- `packages/read-model/src/database.types.ts` -- 신규 테이블 2개와 view 2개의 Row/Insert/Update 타입을 운영 스키마에서 생성한 결과로 반영한다 -- offline drift lint와 운영 재생성 diff gate를 모두 통과시킨다.
- `tools/production_parity_baseline.json` -- 운영 적용 후 migration/함수 실측 스냅샷을 갱신한다 -- 배포 gate가 baseline 누락으로 실패하지 않게 한다.
- `tools/epic-path-manifests/epic-5.txt` -- Epic 5 산출물 경로 manifest를 추가한다 -- epic 범위 게이트와 회고 귀속을 가능하게 한다.

**Acceptance Criteria:**
- Given migration을 적용한 직후일 때, when 스키마를 확인하면, then `bias_events`에는 `source` 컬럼이 없고 `bias_event_by_source`는 `(bias_event_id, source)` PK로 한 회차의 source별 행을 갖는다.
- Given 같은 거래일에 두 번째 회차를 append했을 때, when canonical view를 조회하면, then 최신 회차 하나만 반환되고 첫 회차의 메타·source 행은 그대로 조회된다.
- Given 임의의 과거 `bias_event_id`를 지정했을 때, when 원본 테이블을 조회하면, then 그 회차의 메타와 source별 행이 모두 남아 있다.
- Given source별 view 정의를 검토할 때, when source 결정 경로를 확인하면, then `candidate_source_contrib` join만으로 기여 사실이 확인되고 bias 테이블에는 별도 source 사본이 없다.
- Given 브라우저 역할이 두 테이블과 두 view를 직접 조회할 때, when ACL을 확인하면, then SELECT가 모두 차단된다.
- Given 운영 Supabase에 migration을 적용한 뒤일 때, when 로컬 검증 도구(`check_migration_order`, `check_generated_types_drift`, `check_production_parity`)를 실행하면, then 모두 통과한다.

## Design Notes

`diff_count`와 `missed_opportunity_count`의 정확한 산식은 Story 5.3이 확정한다. 이 스토리는 방향을 못 박지 않고, 어떤 정의에서도 참인 약한 불변식만 DB에 남긴다 — 즉 `diff_count`는 해당 source 모집단 시그널 수를 넘지 못하고(모집단 전용 차집합), `missed_opportunity_count`는 `backtest_universe_signal_count - intersection_count` 이상이다(NFR-7 절단분이 더해지므로). 컬럼 comment에 이 경계와 "산식 확정은 5.3" 사실을 남긴다.

canonical view는 `distinct on (trading_day)` + `order by trading_day, created_at desc, bias_event_id desc`로 동시각 tie까지 결정론적으로 해소한다.

## Verification

**Commands:**
- `python tools/check_migration_order.py` -- expected: 파일명/순서 계약 통과
- `python tools/check_generated_types_drift.py` -- expected: 신규 테이블·view가 생성 타입에 존재
- `python tools/check_production_parity.py` -- expected: 역방향 drift 없음(로컬 선행은 WARN 허용)
- 운영 Supabase에서 `tests/sql/test_bias_events.sql`의 각 검증 블록 실행 -- expected: 모든 시나리오가 pass row로 기록되고 rollback으로 잔여 데이터 없음

## Spec Change Log

## Review Triage Log

### 2026-09-09 — Review pass
- intent_gap: 0
- bad_spec: 0
- patch: 6: (high 0, medium 3, low 3)
- defer: 2: (high 0, medium 0, low 2)
- dismissed:
  - 생성 타입의 `bias_event_by_source.Relationships`에 같은 FK가 3번 나오고 view를 가리켜 잘못됐다 — Supabase 생성기가 실제로 view 대상 항목을 함께 내보낸다(`candidate_source_contrib` → `candidate_supply_hints` 선례). 운영 생성기 출력과 커밋된 블록이 일치함을 재확인했으므로 오류가 아니다.
  - 타입의 `source`가 리터럴 union이 아니라 `string`이다 — 기존 `strategy: string`과 동일한 생성기 출력이고, 손으로 좁히면 default branch의 재생성 diff gate가 깨진다.
  - view에 `security_invoker = true`가 없다 — 저장소 전체에 이 옵션 선례가 없고, 주장된 결과(브라우저 우회)는 지금 없는 SELECT 권한을 누가 나중에 부여해야 성립한다. 현재 상태에서 그 경로가 없다.
  - `create table if not exists`가 형태가 다른 기존 테이블을 조용히 지나칠 수 있다 — 저장소에 두 선례가 모두 있고, 주장된 drift는 CI의 N/N-1 및 clean full-apply 스키마 diff gate가 이미 잡는다.
  - `missed_opportunity_count` 상한과 `trading_day` 범위 check가 없다 — 산식은 Story 5.3 소관임이 spec에 명시돼 있고, `current_date`는 CHECK에서 immutable하지 않아 제안된 형태 자체가 성립하지 않는다.
  - `bias_event_by_source(source)` 보조 index가 없다 — 이 테이블은 거래일당 source 3행 규모이고 5.14 조회도 거래일로 함께 좁히므로, 주장된 성능 결과에 이르는 경로가 없다.
  - spec이 migration 파일명을 `202609091200`으로 적어 실제 `202609091700`과 어긋난다 — 이 build가 구현 중인 spec을 고치는 수정이므로 워크플로우 규칙상 dismiss한다(파일명 충돌 경위는 migration 헤더와 아래 Auto Run Result에 기록했다).
  - Verification 절에 tsc/타입 재생성 명령이 없다 — 같은 이유로 spec 수정에 해당해 dismiss한다. 실제로는 이번 패스에서 `npx tsc --noEmit`과 운영 생성기 대조를 모두 수행했다.
  - sprint-status.yaml이 갱신되지 않았고 커밋이 없다 — 이 워크플로우의 Finalize 단계와 사용자가 지시한 스프린트 동기화가 담당하는 절차이며, 코드 결함이 아니다.
- addressed_findings:
  - `[medium]` `[patch]` `bias_event_by_source_canonical`의 기여 집계가 거래일로 그 날의 canonical close run을 찾아, 재실행이 canonical attempt를 바꾸면 과거 회차의 기여 수치가 소급 변했다. 회차 자신의 `logical_run_key`가 가리키는 canonical attempt에 연결하고 lateral로 행 단위 범위를 좁혀 append-only 보존을 회복했다(전체 테이블 재집계도 함께 해소).
  - `[medium]` `[patch]` 같은 view가 "canonical close 미발행"과 "해당 source 기여 0"을 모두 0으로 노출해 에픽의 미수집/실제 0 구분 원칙을 깼다. 미발행은 NULL, 기여 없음은 0으로 나누고 컬럼 comment에 3상태 의미를 명시했다.
  - `[medium]` `[patch]` `contributing_candidate_count`가 0이 아닌 값으로 한 번도 검증되지 않아 join을 무력화해도 fixture가 전부 통과했다. `runs`/`candidates`/`candidate_source_contrib`와 canonical attempt를 세우고 t1859=2, t1856=0, canonical 해제 시 NULL을 검증하는 `contribution_authority` 블록을 추가했다.
  - `[medium]` `[patch]` 편향 계산이 종가 배치 전용이라는 계약이 강제되지 않아 premarket/intraday 계보로도 회차가 적재됐다. 거래일 검증 trigger에 `batch_kind = 'close'` 검사를 추가하고 두 계보의 거부 케이스를 fixture에 넣었다.
  - `[low]` `[patch]` trigger 예외에 SQLSTATE가 없어 fixture가 `when others` + `sqlerrm` 문자열 비교로 잡고 무관한 오류까지 삼켰다. 두 거부에 `55000`을 명시하고 fixture가 해당 sqlstate만 잡도록 바꿨다.
  - `[low]` `[patch]` `diff_count`의 하한(`>= candidate_pop_signal_count - intersection_count`)이 없어 문서화된 정의에서 불가능한 값이 통과했다. 대칭 하한 check를 추가하고, 위반 거부·FK 위반·내용 있는 `calculation_meta` 허용·선언한 두 index 존재 케이스를 fixture에 추가했다.

## Auto Run Result

Status: done

### 구현 요약

모집단 편향 관측치를 담는 append-only 스키마를 만들었다. 회차 메타(`bias_events`)와 source별 분해(`bias_event_by_source`)를 분리해 카운트는 전부 source 행에만 두고, 두 테이블 모두 DB 경계에서 UPDATE/DELETE/TRUNCATE를 거부한다. 재계산은 새 `bias_event_id`로만 append되고 거래일별 canonical view가 최신 회차를 결정론적으로 고른다. source 권위는 `candidate_source_contrib`에만 남기고(AD-21) bias 쪽에는 사본을 두지 않는다. 계산 로직(5.3), close 배치 배선(5.4), 조회 RPC·UI(5.13/5.14)는 범위 밖이다.

### 변경 파일

- `infra/supabase/migrations/202609091700_create_bias_events.sql` — 두 append-only 테이블, 카운트 불변식, 종가 배치·거래일 일치 강제 trigger, 두 canonical view, RLS와 ACL. 운영에 적용했다.
- `tests/sql/test_bias_events.sql` — 6개 시나리오 rollback fixture(카탈로그 계약, source 도메인 drift, append/canonical, append-only 거부, 카운트·계보 불변식, 기여 권위, 브라우저 읽기 차단). `tests/sql/test_*.sql` 자동 수집으로 CI에 들어간다.
- `packages/read-model/src/database.types.ts` — 신규 테이블 2개·view 2개의 생성 타입.
- `tools/production_parity_baseline.json` — migration과 `enforce_bias_event_trading_day` 실측 스냅샷.
- `tools/epic-path-manifests/epic-5.txt` — Epic 5 경로 manifest(신규).
- `_bmad-output/implementation-artifacts/epic-5-context.md` — Epic 5 계획 컨텍스트(신규).

**migration 파일명 주의:** spec이 제안한 `202609091200`은 `202609091200_reapply_candidate_evidence_read_boundary.sql`이 이미 쓰고 있고 `check_migration_order.py`가 timestamp 중복을 금지하므로 `202609091700`으로 두었다. migration 헤더에 경위를 남겼다.

### 리뷰 결과

4개 독립 레이어(blind-hunter, edge-case-hunter, verification-gap, intent-alignment)를 병렬 실행했다. intent_gap 0, bad_spec 0, patch 6건 적용(medium 3, low 3), defer 2건(low 2), dismissed 9건. 각 항목의 판정 근거는 위 Review Triage Log에 있다.

적용한 patch 중 셋은 실질적 결함이었다. (1) 기여 집계가 거래일 기준이어서 재실행이 canonical attempt를 바꾸면 과거 회차 수치가 소급 변했다 — append-only 보존 목적과 정면으로 충돌했다. (2) "canonical close 미발행"과 "기여 0"이 모두 0으로 보였다. (3) `contributing_candidate_count`가 0이 아닌 값으로 한 번도 검증되지 않아 join을 무력화해도 fixture가 전부 통과했다.

구현 단계에서는 별도로 에픽 AC와의 편차 4건(카운트가 `bias_events`에 있었음, 컬럼명 `candidate_population_signal_count`, by_source의 `calculation_meta`, trigger 함수의 브라우저 EXECUTE)을 먼저 교정했다.

**후속 리뷰 권고: true** — 이번 패스에서 patch로 처리한 항목이 medium 3건, low 3건이며 점수는 3×3 + 1×3 = 12로 기준(5) 이상이다. high는 없다.

### 검증

- 운영 Supabase(`qqhjeumlecaudsiqhhdu`)에 migration을 적용하고, fixture 6개 블록을 운영에서 실행해 전부 pass를 확인했다. 검증 트랜잭션은 의도적 예외로 중단시켜 `bias_events`/`bias_event_by_source`/`candidates`/`candidate_source_contrib`/2099년 `runs`·`logical_runs` 잔여 행이 모두 0임을 재조회로 확인했다.
- `contribution_authority` 블록에서 t1859 기여 2건, t1856 기여 0, canonical attempt 해제 시 NULL을 각각 확인했다.
- I/O 매트릭스 7개 행(HAPPY_PATH, RECALC_APPEND, MUTATION_REJECTED, EMPTY_SOURCE, BAD_COUNTS, DAY_MISMATCH, BROWSER_READ)이 모두 fixture로 커버되고 운영 실행에서 통과했다.
- `python tools/check_migration_order.py` — 67개 파일 통과.
- `python tools/check_generated_types_drift.py` — 21개 table/view 커버.
- `python tools/check_production_parity.py` — 0 ERROR, 0 WARN.
- `npx tsc --noEmit` — exit 0.
- `python tools/check_epic_scope.py --epic 5 --worktree` — 범위 밖 경로 없음.
- 운영 생성기 출력과 커밋된 read-model 타입의 bias 블록 4개가 일치함을 대조했다.

### 잔여 리스크

- 로컬에 Postgres가 없어 CI의 fresh Postgres 순차 적용과 N/N-1 스키마 parity gate는 이 실행에서 돌리지 못했다. migration은 단일 forward-only 파일이고 운영에서 통째로 적용됐지만, 두 gate의 실제 판정은 PR CI에서 확인된다.
- `npm run generate:read-model-types`가 이 계정 권한으로 실행되지 않아 타입은 Supabase MCP 생성기 출력과 대조해 반영했다. default branch의 온라인 재생성 diff gate가 최종 권위다.
- e2e 테스트는 수행하지 않았다. 이 스토리에는 브라우저에서 소비하는 표면이 없고(조회 RPC 자체가 5.13/5.14 범위) 브라우저 역할에는 SELECT 권한이 없어, 현재 단계에서 e2e가 관측할 대상이 존재하지 않는다.
- deferred 2건(회차 단독 존재 허용, epic manifest의 공유 경로)은 frontmatter에 기록했다.
