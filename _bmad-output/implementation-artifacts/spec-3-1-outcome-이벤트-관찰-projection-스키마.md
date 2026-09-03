---
title: 'Story 3.1: Outcome 이벤트/관찰/projection 스키마'
type: 'feature'
created: '2026-09-03'
status: 'done'
baseline_revision: '001346e089d383058e8c9e95ba45e7408544c73c'
baseline_commit: '001346e089d383058e8c9e95ba45e7408544c73c'
review_loop_iteration: 0
followup_review_recommended: true
context:
  - '_bmad-output/implementation-artifacts/epic-3-context.md'
warnings: ['oversized']
deferred:
  - summary: >-
      운영 Supabase project에 `public.skip_attempt` RPC가 실제로는 적용되어 있지 않다.
    evidence: |-
      `mcp__supabase__list_migrations` 결과에 `202609012300_add_skip_attempt` migration이 없고,
      `pg_proc` 직접 조회(`select ... where proname = 'skip_attempt'`) 결과도 0건이었다.
      그러나 `apps/batch/run_state.py:229`는 `rpc("skip_attempt", ...)`로 이 함수를 호출한다.
    location: >-
      infra/supabase/migrations/202609012300_add_skip_attempt.sql, apps/batch/run_state.py:229
    severity: high
---

<intent-contract>

## Intent

**Problem:** 실전 outcome 생명주기를 보존할 append-only 이벤트·관찰 장부와, 장부로부터 재구축 가능한 현재 상태 projection이 아직 없다. 재시도나 후속 판정이 과거 결과를 덮어쓰지 못하도록 데이터베이스 경계에서 구조와 불변식을 먼저 확립해야 한다.

**Approach:** 운영 Supabase migration으로 세 테이블, 상태·값 제약, OPEN 중복 방지 인덱스, append-only trigger와 RLS를 정의한다. 자기완결 SQL fixture와 CI, 생성 타입 및 운영 프로젝트 실행 증거로 실제 계약을 검증한다.

## Boundaries & Constraints

**Always:** 이벤트와 관찰은 UPDATE/DELETE가 DB trigger에서 거부되는 장부여야 한다. projection만 후속 command 처리에서 갱신 가능하다. 금액·비율은 finite `numeric`, 시각은 `timestamptz`, 거래일은 `date`, 내부 ID는 UUID를 사용한다. 브라우저 역할은 세 테이블에 직접 접근할 수 없어야 한다. `logical_run_key`는 기존 실행 계보를 참조하고, 전략은 A/B/C, 상태는 TP/SL/TIMEOUT/OPEN/SUSPENDED/DELISTED만 허용한다.

**Never:** `candidate_outcome`에 `source` 또는 `source_jsonb`를 저장하지 않는다. 이벤트·관찰을 upsert나 cascade delete 가능한 가변 이력으로 만들지 않는다. 관찰을 rebuildable projection에 FK로 결박해 projection 재구축을 방해하지 않는다. Story 3.2 이후의 command 발행·projection 갱신 RPC나 실제 성과 판정 로직은 구현하지 않는다.

## I/O & Edge-Case Matrix

| Scenario | Input / State | Expected Output / Behavior | Error Handling |
|----------|--------------|---------------------------|----------------|
| 정상 스키마 | 유효한 이벤트, 관찰, projection 행 | 선언된 키·타입·기본값으로 저장되고 장부 행은 유지됨 | 오류 없음 |
| 장부 변조 | 기존 이벤트/관찰 UPDATE 또는 DELETE | 행이 변경·삭제되지 않음 | append-only trigger가 명시적 오류 반환 |
| 중복 OPEN | 같은 ticker/strategy에 OPEN 두 건 | 첫 행만 허용 | partial unique 위반 |
| 유효하지 않은 값 | 미지원 상태·전략, 비양수 가격, NaN/Infinity, 음수 holding_days | 저장되지 않음 | CHECK 제약 위반 |
| 허용된 이력 | 같은 ticker/strategy의 서로 다른 entry_date terminal 행 | 모두 저장됨 | 오류 없음 |
| 원천 분리 | 신규 projection 메타데이터 검사 | source 계열 컬럼이 없음 | fixture가 존재 시 실패 |

</intent-contract>

## Code Map

- `_bmad-output/planning-artifacts/epics.md` -- Story 3.1의 외부 계약과 금지된 source 컬럼의 권위.
- `_bmad-output/implementation-artifacts/epic-3-context.md` -- Epic 3 상태 집합, 재구축·멱등성·보존 경계.
- `infra/supabase/migrations/202609011600_create_run_lineage.sql` -- `logical_runs.logical_run_key` 타입과 실행 계보 FK 기준.
- `infra/supabase/migrations/202609021500_create_daily_ohlcv.sql` -- UUID/date/timestamptz/numeric finite 검사와 deny-all RLS 관례.
- `infra/supabase/migrations/202609021600_create_candidate_tags.sql` -- A/B/C 전략 CHECK 및 복합 키·RLS 관례.
- `infra/supabase/migrations/202609031300_create_outcome_schema.sql` -- 신규 outcome 장부·projection 및 공용 append-only trigger 구현 위치.
- `infra/supabase/migrations/202609031400_harden_outcome_schema_invariants.sql` -- 리뷰 후속: OHLC 순서·exit_date 선후관계 CHECK와 TRUNCATE append-only guard 추가.
- `tests/sql/test_outcome_schema.sql` -- catalog와 실제 DML을 함께 검증할 rollback fixture.
- `.github/workflows/test.yml` -- disposable PostgreSQL migration/SQL fixture 실행 목록.
- `packages/read-model/src/database.types.ts` -- 운영 schema에서 다시 생성할 공유 DB 타입; 수기 추정 금지.

## Tasks & Acceptance

**Execution:**
- [x] `infra/supabase/migrations/202609031300_create_outcome_schema.sql` -- 세 테이블과 PK/UNIQUE/FK/CHECK/partial unique index, ledger UPDATE·DELETE 차단 trigger, RLS를 원자적으로 추가한다 -- 후속 스토리가 의존할 DB 불변식을 권위 경계에서 강제하기 위해서다.
- [x] `tests/sql/test_outcome_schema.sql` -- 정상 삽입, catalog shape, append-only 거부, 상태·전략·finite/양수/범위 제약, 중복 OPEN, source 컬럼 부재와 RLS 무정책 상태를 rollback fixture로 검증한다 -- 선언과 실제 동작의 차이를 잡기 위해서다.
- [x] `.github/workflows/test.yml` -- 신규 fixture를 migration 적용 후 실행 목록에 연결하고 SQL 단계 이름을 현재 범위에 맞춘다 -- CI에서 Story 3.1 계약 누락을 막기 위해서다.
- [x] `packages/read-model/src/database.types.ts` -- 운영 migration 적용 후 Supabase가 생성한 타입으로 갱신한다 -- 코드와 실제 운영 schema의 드리프트를 막기 위해서다.

**Acceptance Criteria:**
- Given migration을 적용한 DB, when `outcome_events` catalog를 검사하면, event_id PK와 ticker/strategy/command_type/logical_run_key/payload/created_at이 존재하고 logical_run_key가 실행 계보를 참조하며 UPDATE·DELETE가 거부된다.
- Given 이벤트 장부가 생성된 DB, when `outcome_observations`를 검사하고 행을 변조하려 하면, 복합 PK `(outcome_id,evaluation_trading_day)`와 high/low/close/result_code가 존재하며 UPDATE·DELETE가 거부된다.
- Given projection schema, when 정상 및 비정상 행을 삽입하면, 지정된 전체 컬럼과 `(ticker,strategy,entry_date)` UNIQUE, 6개 상태, finite·양수 가격과 비음수 holding_days 제약만 통과한다.
- Given 같은 ticker/strategy의 OPEN 행이 이미 존재할 때, when 두 번째 OPEN을 삽입하면, partial unique index가 거부하되 terminal 이력은 보존된다.
- Given 신규 세 테이블, when anon/authenticated 직접 접근 경계와 catalog를 검사하면, RLS가 활성화되고 허용 정책이 없으며 projection에 source/source_jsonb 컬럼이 없다.
- Given 저장소 migration과 fixture가 통과할 때, when 운영 프로젝트 `qqhjeumlecaudsiqhhdu`에 migration을 적용하고 같은 계약을 실행하면, 실제 schema·trigger·RLS 결과가 명시적 pass 행으로 확인되고 생성 TypeScript 타입이 그 schema와 일치한다.

## Spec Change Log

## Review Triage Log

### 2026-09-03 — Review pass
- intent_gap: 0
- bad_spec: 0
- patch: 6: (high 0high, medium 2medium, low 4low)
- defer: 1: (high 1high, medium 0medium, low 0low)
- dismissed:
  - `candidate_outcome` table comment의 `candidate_source_contrib` 참조가 존재하지 않는 테이블을 가리킨다는 지적 — 반증됨: `candidate_source_contrib`는 `202609011700_create_candidates.sql`에서 이미 생성되어 있고 재생성된 `database.types.ts`의 Tables 목록에도 존재한다.
  - `candidate_outcome`과 `candidate_source_contrib` 사이에 공유 컬럼이 없어 join이 불가능하다는 지적 — 반증됨: `candidate_outcome(ticker, entry_date)`와 `candidates(ticker, trading_day)`를 통해 `candidate_source_contrib`까지 join이 가능하다(FK로 강제되지는 않지만 실행 가능한 경로가 존재).
  - `outcome_events`/`outcome_observations`와 `candidate_outcome.outcome_id`의 상관관계가 스키마 수준에서 강제되지 않는다는 지적 — intent-contract의 Never 절이 Story 3.2 이후의 command 발행·projection 갱신 로직 구현을 명시적으로 범위 밖으로 규정하며, 이 상관관계는 바로 그 로직에서 확립된다.
  - `candidate_outcome`의 status와 exit_date/exit_price/return_pct 존재 여부 간 일관성이 CHECK로 강제되지 않는다는 지적 — Story 3.5(SUSPENDED 전이)·3.8(correction)·3.9(DELISTED 종결)이 아직 구현되지 않아 정확한 규칙(예: SUSPENDED/DELISTED의 exit 필드 처리)이 미확정이며, intent-contract Never 절이 해당 후속 스토리의 판정 로직 구현을 범위 밖으로 규정한다. 현재 fixture의 유효 행 집합(OPEN/SUSPENDED는 exit_date null, DELISTED는 exit_date만 존재)만으로는 정확한 CHECK 규칙을 확정할 근거가 부족하다.
  - `outcome_events(ticker, strategy)` 등 replay용 index가 없다는 지적 — 아직 이를 조회하는 코드 경로가 전혀 없다(replay/projection 갱신은 Story 3.2 이후 범위). 검증 가능한 실제 성능 문제가 없어 조기 최적화로 판단.
  - down/rollback migration과 service_role에 대한 명시적 grant가 없다는 지적 — 이 저장소의 다른 테이블 생성 migration(`202609021500_create_daily_ohlcv.sql`, `202609021600_create_candidate_tags.sql` 등)도 동일하게 down migration이나 명시적 grant를 두지 않는다(Supabase service_role은 기본적으로 RLS를 우회). 기존 컨벤션과 일치하므로 이 diff가 만든 결함이 아니다.
  - `deferred-work.md` 항목이 별도 tracked ticket과 연결되어 있지 않다는 지적 — 이 저장소는 외부 티켓 시스템을 쓰지 않고 `deferred-work.md` 자체가 지정된 추적 장치다(기존 Story 1.3 항목도 동일 형식).
  - `sprint-status.yaml`(in-progress)과 spec frontmatter(in-review)의 상태 불일치 지적 — 이 리뷰 패스가 끝나고 Finalize 단계에서 spec을 `done`으로, sprint-status를 그에 맞춰 동기화하므로 일시적 상태였을 뿐이다.
  - RLS가 `pg_policies`/`relrowsecurity` catalog 검사로만 확인되고 실제 `anon`/`authenticated` role로 접근을 시도해 거부를 재현하지 않는다는 지적 — `test_daily_ohlcv.sql`의 기존 선례와 동일한 검증 방식이다. 로컬 CI의 vanilla Postgres에는 `anon`/`authenticated` role 자체가 없어 `SET ROLE`로 재현할 수 없고, RLS가 활성화되고 정책이 0개이면 non-bypassrls role은 어떤 행도 보거나 쓸 수 없다는 것은 Postgres 엔진이 보장하는 결정적 동작이다.
- addressed_findings:
  - `[medium]` `[patch]` `outcome_observations`에 high/low/close 상호 순서를 강제하는 CHECK가 없어 물리적으로 불가능한 OHLC 값(예: low > high)이 저장될 수 있었다 — `high >= low and close between low and high` CHECK를 추가하고 fixture에 위반 케이스 2건을 추가했다. 운영 project에 적용 및 fixture 통과 확인.
  - `[medium]` `[patch]` append-only trigger가 UPDATE/DELETE만 막고 TRUNCATE는 막지 못해 장부 append-only 보장이 우회될 수 있었다 — 두 장부 테이블에 statement-level `BEFORE TRUNCATE` trigger를 추가하고 fixture에 TRUNCATE 거부 검증을 추가했다. 운영 project에 적용 및 fixture 통과 확인.
  - `[low]` `[patch]` `candidate_outcome.exit_date`가 `entry_date`보다 이른 값도 허용됐다 — `exit_date is null or exit_date >= entry_date` CHECK를 추가하고 fixture에 위반 케이스를 추가했다. 운영 project에 적용 및 fixture 통과 확인.
  - `[low]` `[patch]` fixture가 `outcome_events.logical_run_key` FK를 catalog 존재 여부로만 확인하고 실제 위반 삽입으로 검증하지 않았다 — 존재하지 않는 `logical_run_key`로 삽입해 FK 위반을 확인하는 케이스를 fixture에 추가했다.
  - `[low]` `[patch]` `.github/workflows/test.yml`의 `sql-schema-tests` job 상단 설명 주석이 Story 1.10 dispatch_outbox 범위만 서술해 이번에 넓어진 범위(스토리마다 자신의 schema fixture를 계속 추가하는 구조, 현재 Story 3.1 outcome 포함)를 반영하지 못했다 — 주석을 갱신했다.
  - `[low]` `[patch]` `candidate_outcome.cutoff_n` 기본값 30이 왜 그 값인지 설명이 없어 후속 독자가 근거를 확인하거나 안전하게 바꿀 방법이 없었다 — `Story 3.7` TIMEOUT 컷오프 정책을 설명하는 column comment를 추가했다.

## Design Notes

관찰의 `outcome_id`는 이벤트가 소유하는 안정 식별자이며 rebuildable `candidate_outcome` 행의 생존에 의존하지 않는다. 따라서 관찰→projection FK는 두지 않고, 후속 replay가 projection을 비운 뒤 같은 outcome_id로 복원할 수 있게 한다. `command_type`과 `result_code`는 후속 correction·예외 이벤트 확장을 막는 조기 enum 대신 비어 있지 않은 text로 제한한다.

## Verification

**Commands:**
- `psql -v ON_ERROR_STOP=1 "$DATABASE_URL" -f tests/sql/test_outcome_schema.sql` -- expected: 모든 assertion 통과 후 rollback.
- `npm run typecheck` -- expected: 운영 생성 DB 타입을 소비하는 TypeScript 전체 통과.
- `uv run --with pandas --with numpy --with pyarrow --with pytest pytest` -- expected: 기존 backtest·batch·domain 회귀망 전체 통과.
- `git diff --check` -- expected: 공백 오류 없음.

**Manual checks (if no CLI):**
- Supabase MCP로 운영 project migration 이력, 신규 table/constraint/index/trigger/RLS와 fixture pass 행을 확인한다.
- UI 변경이 없는 DB 전용 스토리이므로 Playwright E2E는 적용 대상이 아니다.

## Auto Run Result

**구현 요약:** 운영 Supabase project(`qqhjeumlecaudsiqhhdu`)에 `outcome_events`(append-only 이벤트 장부), `outcome_observations`(append-only 관찰 장부), `candidate_outcome`(재구축 가능한 현재 상태 projection) 세 테이블을 도입했다. PK/UNIQUE/FK/CHECK, OPEN 중복 방지 partial unique index, UPDATE/DELETE/TRUNCATE를 모두 거부하는 append-only trigger, 세 테이블 모두 RLS 활성화(정책 0개, deny-all)를 원자적 migration으로 적용했다. 자기완결 rollback fixture로 계약을 실제 DML까지 검증하고 CI에 연결했으며, 운영 schema로부터 TypeScript 타입을 재생성했다.

**변경 파일:**
- `infra/supabase/migrations/202609031300_create_outcome_schema.sql` -- 신규 outcome 장부·projection 테이블, 제약, index, append-only trigger(UPDATE/DELETE), RLS 최초 도입.
- `infra/supabase/migrations/202609031400_harden_outcome_schema_invariants.sql` -- 리뷰 후속: OHLC 순서 CHECK, exit_date 선후관계 CHECK, `cutoff_n` 설명 comment, TRUNCATE append-only guard 추가.
- `tests/sql/test_outcome_schema.sql` -- catalog·DML·append-only·제약·RLS를 검증하는 rollback fixture(리뷰 후속 케이스 포함).
- `.github/workflows/test.yml` -- `sql-schema-tests` job에 신규 fixture 연결, 상단 설명 주석을 넓어진 범위에 맞게 갱신.
- `packages/read-model/src/database.types.ts` -- 운영 project에서 재생성한 공유 DB 타입(신규 outcome 세 테이블 반영).
- `_bmad-output/implementation-artifacts/deferred-work.md` -- 리뷰 중 발견한 기존 pytest 회귀 7건, `skip_attempt` RPC 운영 미적용 건을 각각 기록.

**리뷰 findings 분류:** patch 6건(적용 완료, 아래 addressed_findings 참조), defer 1건(`skip_attempt` RPC 운영 미적용, high — `deferred-work.md` 기록), dismissed 9건(위 Review Triage Log 참조 — 반증 2건, intent-contract Never 절 기준 범위 밖 2건, 근거 부족 1건, 기존 컨벤션과 일치 2건, 이 저장소 특성상 해당 없음 1건, 워크플로 자체 Finalize에서 해소되는 일시적 상태 1건).

**후속 리뷰 권고:** `true` (patch medium 2건 + low 4건 → 3×2 + 1×4 = 10 ≥ 5).

**검증 수행:**
- `psql`(MCP `execute_sql`을 통해 운영 project에서 직접 실행) -- `tests/sql/test_outcome_schema.sql` fixture, 리뷰 후속 케이스 포함 전체 assertion 통과(`outcome_schema_contract / pass`) 후 rollback.
- `npm run typecheck` -- 통과.
- `uv run --with pandas --with numpy --with pyarrow --with pytest pytest` -- 234 passed, 7 failed. 실패 7건은 모두 `tests/batch/test_scheduler.py`이며 baseline(001346e)에서도 동일하게 실패함을 확인해 이 스토리와 무관한 기존 회귀로 판정, `deferred-work.md`에 기록.
- `git diff --check` -- 공백 오류 없음.
- Supabase MCP -- `apply_migration`으로 두 migration을 운영 project에 순서대로 적용, `list_migrations`/`get_advisors`(security)로 확인. 신규 RLS-no-policy INFO 3건은 기존 테이블과 동일한 의도된 deny-all 패턴이며 새로운 WARN/ERROR 없음.
- UI 변경이 없는 DB 전용 스토리라 Playwright E2E는 적용 대상이 아니며 실행하지 않았다(spec 자체 판단과 일치).

**잔여 위험:**
- `candidate_outcome`의 status↔exit 필드 일관성(예: SUSPENDED/DELISTED가 exit_date를 언제 갖는지)은 아직 CHECK로 강제되지 않는다. Story 3.5/3.8/3.9가 정확한 규칙을 확정하기 전까지는 애플리케이션 계층의 정확성에 의존한다.
- `outcome_events`/`outcome_observations`와 `candidate_outcome.outcome_id`의 상관관계는 스키마가 아니라 Story 3.2 이후 command 처리 로직이 보장해야 한다.
- `skip_attempt` RPC의 운영 미적용은 이 스토리와 무관하지만 실제 배치 실행에 영향을 줄 수 있는 활성 결함이며 별도 조치가 필요하다(`deferred-work.md` 참조).
