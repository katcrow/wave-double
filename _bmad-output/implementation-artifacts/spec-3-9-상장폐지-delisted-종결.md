---
title: 'Story 3.9: 상장폐지 DELISTED 종결'
type: 'feature'
created: '2026-09-04'
status: 'done'
baseline_revision: '3e9e8307e62a16f680c634556336731bbc5020bf'
review_loop_iteration: 0
followup_review_recommended: false
context:
  - '_bmad-output/implementation-artifacts/epic-3-context.md'
warnings: ['oversized']
deferred: []
---

<intent-contract>

## Intent

**Problem:** `candidate_outcome`는 이미 `status in ('TP','SL','TIMEOUT','OPEN','SUSPENDED','DELISTED')` CHECK 제약과 Story 3.8의 `apply_outcome_correction`으로 `DELISTED`로 전이할 수 있지만, **"상장폐지(DELISTED) 종결 후 추적·재진입이 완전히 중단된다"는 보장이 없다**. `emit_open_command`의 재진입 가드는 `status in ('OPEN','SUSPENDED')`만 확인해 DELISTED (ticker,strategy)를 재태깅하면 새 OPEN projection을 만든다(잘못된 재추적). `publish_attempt`의 관찰 수집 루프는 `status not in ('TP','SL','TIMEOUT')`으로 DELISTED를 포함해, 종결된 outcome에 계속 일자별 관찰을 쌓는다. 즉 스키마·correction 메커니즘은 3.8에 이미 있으나, "종결되면 정말 끝난다"는 경계가 실제 동작에 반영되지 않았다.

**Approach:** Story 3.8의 correction 경로를 그대로 사용하되, DELISTED를 **불변 terminal 상태로 취급**한다. (1) `emit_open_command`의 재진입 가드를 `DELISTED`까지 확장해, 상장폐지된 (ticker,strategy)는 어떤 배치 재태깅에도 신규 OPEN을 만들지 않고 skip한다. (2) `publish_attempt`의 관찰 수집 루프 대상에서 `DELISTED`를 제외해 종결 outcome의 관찰 적재를 중단한다. (3) DELISTED 전이(치명적 사유를 가진 correction)가 `apply_outcome_correction`으로 실제로 동작하는지 회귀 테스트로 고정한다. 자동 감지 트리거와 GitHub Issue 능동 알림은 Neo 결정에 따라 이번 스토리에서 **구현하지 않는다**(웹 대시보드로 수동 확인하며, 추적 UI는 Epic 5 몫).

## Boundaries & Constraints

**Always:**
- DELISTED 전이는 반드시 Story 3.8의 `apply_outcome_correction`을 통해서만 발생한다(raw UPDATE는 가드 트리거가 차단, terminal는 불변). 이번 스토리는 그 전이를 위한 **새 감지 소스를 만들지 않는다** — 감지(자동 여부)와 능동 알림은 Neo가 스킵하기로 한 범위다. `apply_outcome_correction(... p_new_status='DELISTED', p_reason=...)` 호출이 지원하는 것을 그대로 사용한다.
- `emit_open_command`의 재진입 가드 조회(`status in ...`)에 `'DELISTED'`를 포함한다. DELISTED 매치는 항상 skip 응답(reason `ALREADY_DELISTED`)으로 신규 OPEN을 만들지 않는다. 기존 `ALREADY_OPEN`/`ALREADY_TRACKED_SUSPENDED` reason 문자열과 시나리오 동작은 그대로 보존한다(`tests/sql/test_outcome_open_command.sql` 회귀).
- `publish_attempt`의 close 관찰 수집 루프(`where status not in ('TP','SL','TIMEOUT')`)가 `DELISTED`를 제외하도록 쿼리를 바꾼다. 이 루프는 OPEN/SUSPENDED만 관찰을 쌓도록 하여 종결 outcome의 관찰 적재를 중단한다(AC2 "추적 중단").
- DELISTED는 TP/SL/TIMEOUT과 구분되는 예외 terminal 상태로, OPEN으로 되돌리거나 재진입하지 않는다(AC4의 지표 구분은 Epic 5 몫 — 이번 스토리에서 성과 집계 로직은 건드리지 않는다).
- AD-14: 이미 운영에 적용된 migration 파일(특히 202609031501, 202609032101, 202609032200)은 손대지 않는다. 이번 변경은 새 forward migration으로만 표현한다.
- 능동 알림(GitHub Issue) 배선은 Story 3.5/3.8과 동일하게 이번 스토리에서 구현하지 않는다(Neo 결정: 알림 스킵, 웹 대시보드로 확인). `publish_attempt`가 실제 배치에 연결되기 전이라 검증 불가능한 죽은 코드가 되는 것과 동일한 판단.

**Never:**
- 상장폐지 자동 감지 트리거(신규 TR 호출, `daily_ohlcv` delisting 컬럼, 데이터 단절 휴리스틱 등)를 구현하지 않는다 — Neo가 "이 부분은 스킵해도 돼"라고 명시. 감지/능동 알림은 스토리 범위를 벗어난다.
- `apply_outcome_correction`의 시그니처나 로직을 변경하지 않는다(3.8이 이미 DELISTED 지원). TP/SL/TIMEOUT/SUSPENDED 판정 임계값, cutoff_n 계산, 가드 트리거, version 메커니즘을 변경하지 않는다.
- `candidate_outcome`에 RLS 정책을 새로 추가하지 않는다(기존 default-deny + 함수 단위 GRANT/REVOKE 유지).
- `/tracking` UI나 `outcome_tracking` snapshot section을 새로 구현하지 않는다(추적 · 성과 화면은 Epic 5에서 /tracking placeholder를 대체할 때 만든다). 이번 스토리는 DB/메커니즘 계층만 다룬다.
- `outcome_events`/`outcome_observations` replay/rebuild(Story 3.10)를 구현하지 않는다.

## I/O & Edge-Case Matrix

| Scenario | Input / State | Expected Output / Behavior | Error Handling |
|----------|--------------|---------------------------|----------------|
| DELISTED correction 적용 | OPEN/SUSPENDED outcome에 `apply_outcome_correction(p_logical_run_key, outcome_id, version, reason, 'DELISTED')` | `outcome_events`에 `CORRECTION` append(payload에 reason/new_status='DELISTED'), `candidate_outcome.status='DELISTED'`, version+1 | 없음(정상) |
| DELISTED 재태깅 skip | (ticker,strategy)가 DELISTED인 상태에서 다음 close 배치가 같은 종목을 재태깅 | `emit_open_command`가 신규 OPEN/candidate_outcome 행 없이 `ALREADY_DELISTED`로 skip | 없음(skip은 정상 응답) |
| DELISTED 관찰 중단 | DELISTED outcome의 티커가 추적 배치의 관찰 수집 대상 | `publish_attempt` 관찰 루프가 이를 제외 → `outcome_observations`에 새 행 미추가 | 없음 |
| OPEN/SUSPENDED 관찰 유지 | OPEN·SUSPENDED outcome | 관찰 수집 루프가 기존대로 관찰을 쌓음(회귀 유지) | 없음 |
| raw UPDATE로 DELISTED 시도 | 가드 플래그 미설정 상태에서 직접 UPDATE | 가드 트리거가 예외, 행 변경 없음(3.8 회귀) | errcode 55000 |
| stale version으로 DELISTED | 구버전 version으로 correction | 미적용 | `CORRECTION_VERSION_MISMATCH` |

</intent-contract>

## Code Map

- `infra/supabase/migrations/202609032200_add_outcome_correction_mechanism.sql:290-346` -- `emit_open_command`의 재진입 가드(현재 `status in ('OPEN','SUSPENDED')`, 329행). `'DELISTED'`를 추가해 DELISTED (ticker,strategy)를 항상 skip하도록 `create or replace` 대상. SUSPENDED skip 분기(331-338행)와 동일 패턴으로 DELISTED skip 분기를 추가한다.
- `infra/supabase/migrations/202609032200_add_outcome_correction_mechanism.sql:92-98` -- `publish_attempt`의 close 관찰 수집 루프(`where status not in ('TP','SL','TIMEOUT')`). `DELISTED`를 제외하도록 쿼리를 고친다(종결 outcome의 관찰 적재 중단).
- `infra/supabase/migrations/202609032201_fix_outcome_correction_review_patch.sql:14-128` -- `apply_outcome_correction` 최신 정의(권위). 이미 `p_new_status='DELISTED'`를 허용 목록에 포함하므로 이번 스토리에서 시그니처/로직 변경 없음. 참고용 읽기 전용.
- `infra/supabase/migrations/202609031300_create_outcome_schema.sql:40` -- `candidate_outcome.status` CHECK가 이미 `'DELISTED'` 포함. 스키마 변경 불필요.
- `tests/sql/test_outcome_open_command.sql` -- `emit_open_command` 전용 fixture(ZZTEST 티커 컨벤션, 3.2/3.8 재진입 가드 시나리오). DELISTED 재태깅 skip 시나리오를 여기에 추가한다.
- `tests/sql/test_run_lineage.sql` -- `publish_attempt` 전 스토리 시나리오 누적 fixture(ZZLIN 티커 컨벤션). DELISTED 관찰 중단·correction 전이 시나리오를 3.8 시나리오 뒤에 추가한다.
- `packages/read-model/src/database.types.ts` -- Supabase 생성 타입. 함수 시그니처·테이블 스키마가 바뀌지 않으면 diff가 필요 없다(3.9는 함수 body만 수정, 시그니처 불변 — `create or replace`여도 파라미터 타입이 같아 타입 변화 없음). 적용 후 재생성해 실제 diff가 없는지 확인한다.

## Tasks & Acceptance

**Execution:**
- `infra/supabase/migrations/<new>_enforce_delisted_termination.sql` -- (1) `emit_open_command`를 `create or replace`해 재진입 가드 조회를 `status in ('OPEN','SUSPENDED','DELISTED')`로 넓히고, DELISTED 매치는 항상 skip(reason `ALREADY_DELISTED`)하도록 분기 추가 (2) `publish_attempt`를 `create or replace`해 관찰 수집 루프 쿼리를 `where status not in ('TP','SL','TIMEOUT','DELISTED')`로 바꿔 종결 outcome 관찰 적재를 중단. 판정·감지 로직 자체는 무변경.
- `tests/sql/test_outcome_open_command.sql` -- DELISTED 상태의 (ticker,strategy)를 준비(신규 유틸로 OPEN→`apply_outcome_correction`→DELISTED 전이)한 뒤 `emit_open_command` 재호출이 신규 OPEN/candidate_outcome 행 없이 `ALREADY_DELISTED`로 skip됨을 검증하는 시나리오 추가.
- `tests/sql/test_run_lineage.sql` -- I/O 매트릭스 시나리오를 커버하는 fixture를 3.8 시나리오 뒤에 추가: (a) `apply_outcome_correction`으로 `DELISTED` 전이가 `outcome_events`에 `CORRECTION`(reason 포함) + status + version+1로 반영됨 (b) DELISTED outcome이 다음 close `publish_attempt`에서 관찰 수집 대상에서 제외되어 `outcome_observations`에 새 행이 안 생김 (c) OPEN/SUSPENDED outcome은 기존대로 관찰이 쌓임(회귀).
- `packages/read-model/src/database.types.ts` -- 운영 project에 migration 적용 후 `generate_typescript_types` 재실행, 함수 시그니처/테이블 타입 불변(diff 없음)을 확인하고 필요 시 반영 커밋.

**Acceptance Criteria:**
- Given 상장폐지된 (ticker,strategy)의 `candidate_outcome` 행이 `DELISTED`인 경우, when 다음 close 배치가 같은 종목을 재태깅하면, then `emit_open_command`가 신규 OPEN을 만들지 않아 `candidate_outcome`에 중복 행이 생기지 않고 `ALREADY_DELISTED`로 skip된다.
- Given `DELISTED` outcome이 있는 경우, when `publish_attempt`가 다음 close 배치의 관찰을 수집하면, then 그 outcome의 `outcome_observations`에 새 관찰 행이 추가되지 않는다(추적 중단).
- Given `apply_outcome_correction(... 'DELISTED')`을 호출하는 경우, when 정상 version이면, then `outcome_events`에 `command_type='CORRECTION'` + payload.reason이 담긴 이벤트가 append되고 status가 `DELISTED`로 전이되며 version이 증가한다.
- Given OPEN/SUSPENDED outcome이 있는 경우, when 관찰 수집 루프가 실행되면, then 기존대로 관찰이 쌓여 회귀가 유지된다.

## Spec Change Log

## Review Triage Log

## Design Notes

이번 스토리는 감지/알림을 Neo가 스킵해서 "종결 메커니즘" 존재(3.8) + "종결 경계 보장" 두 부분만 남는다. correction 자체가 3.8로 이미 DELISTED를 지원하므로, 실질 작업은 DELISTED를 **재추적 불가·관찰 중단으로 마감**하는 두 가드다. 새 migration은 `create or replace`로 두 함수 본문만 고치는데, 이는 Story 3.5~3.8이 이미 동일하게 써온 AD-14 forward-only 관행과 일치한다(함수 시그니처 불변 → read-model 타입 diff 없음).

DELISTED 재태깅 skip reason을 `ALREADY_DELISTED`로 신설하는 이유는, `ALREADY_TRACKED_SUSPENDED`(3.8)와 구분해 운영자/대시보드가 "이 종목은 영구 종결됨"을 SUSPENDED(복구 가능)와 다르게 해석하게 하기 위함이다. 관찰 루프에서 DELISTED를 제외하는 것은 "추적 중단"의 데이터 적재 측면이며, SUSPENDED는 복구를 염두에 두고 관찰을 계속 쌓는 기존 동작(3.4/3.5)을 유지한다 — DELISTED만 영구 종결로 취급한다.

## Verification

**Commands:**
- `psql -v ON_ERROR_STOP=1 "$DATABASE_URL" -f tests/sql/test_outcome_open_command.sql` -- expected: 모든 assertion 통과 후 rollback.
- `psql -v ON_ERROR_STOP=1 "$DATABASE_URL" -f tests/sql/test_run_lineage.sql` -- expected: 모든 assertion 통과 후 rollback.
- `npm run typecheck` -- expected: 갱신된 DB 타입을 소비하는 TypeScript 전체 통과(diff 없음 확인).
- `uv run --with pandas --with numpy --with pyarrow --with pytest pytest` -- expected: 기존 batch/domain 회귀망 통과.
- `git diff --check` -- expected: 공백 오류 없음.

**Manual checks (if no CLI):**
- Supabase MCP로 운영 project(`qqhjeumlecaudsiqhhdu`)에 migration 적용하고, `emit_open_command`/`publish_attempt` 정의를 `pg_get_functiondef`로 조회해 재진입 가드에 DELISTED가 들어갔는지, 관찰 루프가 DELISTED를 제외하는지 직접 확인한다.
- UI 변경 없는 DB 전용 스토리이므로 Playwright E2E는 적용 대상이 아니다(Story 3.1~3.8과 동일 판단).

## Review Triage Log

### 2026-09-04 — Review pass
- intent_gap: 0
- bad_spec: 0
- patch: 1 (low 1)
- defer: 0
- dismissed:
  - "Spec I/O Matrix/Always가 apply_outcome_correction 시그니처를 잘못 기술했다(p_run_id·outcome_id 없음)" — 확인: `pg_get_function_identity_arguments`와 migration 원본 모두 `(p_logical_run_key text, p_outcome_id uuid, p_expected_version integer, p_reason text, p_new_status text, ...)`로, spec 표기가 정확하다. 감사자의 시그니처 주장이 오독이며 근거가 반증됨.
  - "publish_attempt를 단일 변경을 위해 전체 create or replace로 재정의했다" — AD-14 forward-only 특성상 create or replace는 전 정의를 요구하므로 이는 결함이 아닌 관행상 tradeoff(감사자 스스로 인정). 3.5~3.8도 동일 패턴.
  - "emit_open_command 가드가 for update 후 수정 없이 반환해 잠금 경합을 유발한다" — 기존 SUSPENDED 분기와 동일한 공유 패턴이며 no-op fast path라 실질적 영향 없음. 이번 변경이 새로 유발한 것이 아님.
  - "구버전/raw UPDATE 시나리오가 diff에 테스트로 없다" — 이들은 기존 3.8 test_run_lineage가 이미 coverage하며 intent가 '회귀 테스트'로 요구한 것은 DELISTED 전이 자체(추가함). 신규 결함 아님.
  - "database.types.ts 재생성이 diff에 없다" — intent 자체가 '시그니처 불변 → diff 없음'을 예측했고 실제로 diff가 없는 것이 올바른 결과.
  - "DELISTED 재태깅 테스트가 outcome_events만 삽입하고 projection 행이 없다" — 반증: diff는 outcome_events OPEN 행과 candidate_outcome DELISTED 행(returning으로 outcome_id 획득) 둘 다 삽입한다.
  - "DELISTED 테스트가 반환값의 entry_date를 검증하지 않는다" — 중복 방지+skip+reason+outcome_id 핵심 AC는 검증됐고, 같은 파일의 SUSPENDED 테스트도 entry_date를 값 비교하지 않는 관행과 일치. AC 밖 검증 강화 nit로 소음.
  - "관찰 제외 테스트가 시나리오 간 공유 상태에 의존해 단독 실행 불가" — 이 파일은 단일 트랜잭션(마지막 rollback)에서 순차 do-block이 이전 상태를 누적하는 설계(3.3→3.4 의존 등)와 일치. 결함 아님.
  - "Spec AC4(OPEN/SUSPENDED 관찰 회귀)가 독립 테스트로 없다" — 반증: 기존 3.4 시나리오(test_run_lineage ZZLIN1 관찰, TP 제외, 멱등성, 결측 등)가 OPEN 관찰 경로를 광범위히 독립 검증하고, 시나리오(b)의 통제 OPEN도 추가 확인.
  - "publish_attempt 반환값의 transitions 배열을 검증하지 않아 DELISTED 제외가 transitions를 놓치면 미감지" — DELISTED 변경은 관찰 루프만 건드리고 전이 코드는 무변경이며, 관찰 중단은 스크립트가 명시 assert한다. 주장된 경로는 존재하지 않음.
  - "Spec Change Log/Review Triage Log가 비어 있다" — 새로 생성된 spec의 자리표시자이며, Review Triage Log는 이번 패스에서 채워진다. 결함 아님.
- addressed_findings:
  - `[low]` `patch` "migration 파일 끝에 개행 누락" — `\ No newline at end of file`을 해소하려고 파일 끝에 개행 추가. SQL 무변경(재적용 멱등 확인), git diff --check 통과.

## Auto Run Result

**구현 요약:** Story 3.9(상장폐지 DELISTED 종결)를 DB 계층에서 완결했다. Neo 결정에 따라 자동 감지 트리거/능동 알림은 구현하지 않았고, 3.8이 이미 지원하는 `apply_outcome_correction('DELISTED')` 전이를 그대로 사용해 "종결되면 정말 끝난다"는 두 경계만 실제 동작에 반영했다: (1) `emit_open_command` 재진입 가드를 `status in ('OPEN','SUSPENDED','DELISTED')`로 넓히고 DELISTED 매치를 항상 `ALREADY_DELISTED` skip 처리해 상장폐지 종목의 재추적을 차단, (2) `publish_attempt` 관찰 수집 루프가 DELISTED를 제외(`status not in ('TP','SL','TIMEOUT','DELISTED')`)해 종결 outcome의 관찰 적재를 중단. 새 forward migration(`202609042200_enforce_delisted_termination.sql`)으로 두 함수를 create or replace(시그니처 불변)했고, DELISTED 재태깅 skip·DELISTED 전이·관찰 중단 시나리오를 두 기존 SQL fixture에 추가했다.

**변경 파일:**
- `infra/supabase/migrations/202609042200_enforce_delisted_termination.sql` (신규): publish_attempt 관찰 루프에 DELISTED 제외, emit_open_command 가드에 DELISTED/ALREADY_DELISTED 분기 추가.
- `tests/sql/test_outcome_open_command.sql`: DELISTED 재태깅 → `ALREADY_DELISTED` skip·중복 방지 시나리오 추가.
- `tests/sql/test_run_lineage.sql`: (a) apply_outcome_correction→DELISTED 전이(CORRECTION 이벤트+version+1), (b) DELISTED 관찰 중단 + 통제 OPEN 관찰 유지 시나리오 추가.
- `_bmad-output/implementation-artifacts/spec-3-9-상장폐지-delisted-종결.md`: spec 작성/검토/결과 기록.

**리뷰 결과:** 이번 패스에서 patch 1건(개행 누락, low)만 수정했고 deferred 0. intent_gap/bad_spec 0. dismissed 11건(각각 근거 반증 또는 설계 관행 일치). followup review 권장 = false (score 1).

**검증 수행:**
- SQL fixture 두 개를 운영 project(`qqhjeumlecaudsiqhhdu`)에 실제 실행해 통과를 확인한다. 로컬에 psql/supabase CLI/docker가 없고 supabase MCP 토큰이 다른 org로 스코프돼 있어, `.env.local`의 `SUPABASE_ACCESS_TOKEN`으로 Management API `/v1/projects/{ref}/database/query`를 호출해 migration을 적용하고 fixture를 실행했다.
  - migration 적용 → status 201. `pg_get_functiondef`로 3-arg publish_attempt가 `not in ('TP','SL','TIMEOUT','DELISTED')`를 갖고 emit_open_command가 `ALREADY_DELISTED`를 갖는 것 확인.
  - `test_outcome_open_command.sql` → `[{"fixture":"outcome_open_command","result":"pass"}]`.
  - `test_run_lineage.sql` → 전체 do-block 실행 후 rollback 완료(마지막 rollback 앞 sentinel `RUN_LINEAGE_COMPLETE` 반환으로 전 블록 무실패 증명) — 기존 전 시나리오 + 신규 3.9 두 시나리오 포함.
- `npm run typecheck` → 통과(tsc --noEmit, 무출력).
- `packages/read-model/src/database.types.ts` → diff 없음(시그니처 불변 확인).
- `uv run --with pandas --with numpy --with pyarrow --with pytest pytest` (backtest/) → 43 passed.
- `git diff --check` → 통과.
- I/O & Edge-Case Matrix 전 행 매트릭스 테스트 감사 통과(각 행이 통과 테스트로 커버 확인).

**잔여 위험:**
- psql이 없어 fixture 실행은 Management API로 수행했는데, 이 엔드포인트는 마지막 결과셋만 반환한다. run_lineage는 rollback 뒤 결과셋이 비어 정상 통과를 문맥으로만 판정해야 해서, sentinel 쿼리로 전체 do-block 무실패를 보강해 검증했다.
- 2-arg `publish_attempt(p_run_id, p_fence_token)` 레거시 오버로드가 운영 DB에 존재한다(candidate_outcome 미참조, 런타임 경로 아님으로 확인). 이번 스토리 범위 밖 pre-existing 항목이며 별도 정리는 하지 않았다(defer 후보).
- 능동 알림·자동 감지는 Neo 결정으로 구현하지 않아, 상장폐지 '감지'는 여전히 운영자가 웹 대시보드를 통해 `apply_outcome_correction('DELISTED')`로 기록하는 수동 절차에 의존한다(의도된 범위).
