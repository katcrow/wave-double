---
title: 'Story 3.2: Idempotent OPEN command 발행 로직'
type: 'feature'
created: '2026-09-03'
status: 'done'
baseline_revision: '3fab98010e8d6c148d17acff21b0699731e0386f'
baseline_commit: '3fab98010e8d6c148d17acff21b0699731e0386f'
review_loop_iteration: 0
followup_review_recommended: true
context:
  - '_bmad-output/implementation-artifacts/epic-3-context.md'
warnings: []
deferred: []
---

<intent-contract>

## Intent

**Problem:** 태깅된 후보마다 진입(OPEN) 이벤트를 정확히 한 번만 발행할 방법이 아직 없어, 재시도나 이후 스토리(3.3)의 close 발행 연결이 중복 진입을 만들 위험이 있다.

**Approach:** `outcome_events`에 idempotent command key 유니크 제약을 추가하고, `(logical_run_key, ticker, strategy)`를 받아 `logical_runs.batch_kind='close'`를 강제하며, 이미 OPEN이면 no-op, 이미 같은 key로 발행됐으면 기존 결과를 반환하고, 아니면 `daily_ohlcv`의 해당 거래일 종가로 이벤트와 `candidate_outcome` 행을 원자적으로 생성하는 SQL RPC `emit_open_command`를 도입한다. close 발행 트랜잭션 연결(Story 3.3)은 범위 밖이며, 이 RPC는 아직 어디서도 호출되지 않는다(장중 배치가 호출하지 않는다는 AC는 호출부 부재로 자연히 충족되고, `batch_kind` 가드로 방어선을 이중화한다).

## Boundaries & Constraints

**Always:** command 멱등 키는 `(logical_run_key, ticker, strategy, command_type)`이며 `outcome_events`에 유니크 제약으로 강제한다. entry_date=거래일, entry_price=`daily_ohlcv`의 해당 거래일 `close`(adjusted). 이벤트와 projection 삽입은 하나의 함수 호출 내에서 원자적이다. `logical_row.batch_kind <> 'close'`면 예외로 거부한다. 이미 `(ticker,strategy)` OPEN 행이 있으면 이벤트를 만들지 않고 no-op 응답을 반환한다(재진입 금지).

**Never:** `publish_attempt`나 `apps/batch/` 오케스트레이션에서 이 RPC를 호출하지 않는다(Story 3.3 범위). `outcome_observations`나 TP/SL/TIMEOUT 판정 로직을 구현하지 않는다. `candidate_outcome`에 `logical_run_key`나 source 컬럼을 추가하지 않는다. `supply_3day`를 진입가 출처로 쓰지 않는다.

## I/O & Edge-Case Matrix

| Scenario | Input / State | Expected Output / Behavior | Error Handling |
|----------|--------------|---------------------------|----------------|
| 최초 발행 | close 배치 logical_run_key, 신규 (ticker,strategy), `daily_ohlcv`에 해당 거래일 close 존재 | `outcome_events`에 OPEN 1행, `candidate_outcome`에 status=OPEN 1행 생성, entry_date/entry_price가 그 거래일 close로 고정 | 없음 |
| 동일 key 재호출 | 같은 (logical_run_key,ticker,strategy,'OPEN')로 재호출 | 새 이벤트/행을 만들지 않고 기존 event_id/outcome_id를 반환(`replayed: true`) | 없음 |
| 재진입 금지 | 이미 (ticker,strategy) status=OPEN 존재, 다른(다음) 거래일 logical_run_key로 재호출 | 이벤트도 projection 행도 만들지 않고 no-op 응답(`skipped: true, reason: ALREADY_OPEN`) | 없음(정상 흐름) |
| 장중 배치 오호출 | `batch_kind='intraday'`인 logical_run_key | 이벤트/행 생성 없이 거부 | 예외 `OPEN_COMMAND_REQUIRES_CLOSE_BATCH` |
| 종가 데이터 없음 | 해당 (ticker,trading_day)에 `daily_ohlcv` 행 없음 | 이벤트/행 생성 없이 거부 | 예외 `MISSING_DAILY_OHLCV_CLOSE` |
| 미지원 전략 | `strategy`가 A/B/C 아님 | 이벤트/행 생성 없이 거부 | 예외 `INVALID_STRATEGY` |

</intent-contract>

## Code Map

- `infra/supabase/migrations/202609031300_create_outcome_schema.sql` -- `outcome_events`/`candidate_outcome` 정의와 OPEN partial unique index(`candidate_outcome_one_open_per_ticker_strategy_idx`, line 55-57)의 권위.
- `infra/supabase/migrations/202609011600_create_run_lineage.sql:71-115` -- `start_attempt`의 idempotent "replay 기존 결과 반환" 패턴(신규 RPC가 따를 관례).
- `infra/supabase/migrations/202609031000_create_sync_vanished_tags.sql` -- `on conflict ... do nothing returning`, `security definer`/`set search_path`/revoke·grant 관례의 최신 예시.
- `infra/supabase/migrations/202609012300_add_skip_attempt.sql` -- revoke/grant(browser role 차단, service_role만 허용) 정확한 문구.
- `infra/supabase/migrations/202609021500_create_daily_ohlcv.sql:6-18` -- `daily_ohlcv(ticker, trading_day, close, ...)` PK `(ticker,trading_day)`, `close`가 곧 adjusted 종가.
- `infra/supabase/migrations/202609011600_create_run_lineage.sql:5-19` -- `logical_runs(logical_run_key, trading_day, batch_kind)`, batch_kind 체크 제약.
- `tests/sql/test_outcome_schema.sql` -- rollback fixture 관례(`begin`/`do $$ ... $$`/`rollback`, `2099-*` 미래 날짜, `v_caught` 예외 검증 패턴). 신규 fixture는 이 파일과 나란히 추가한다.
- `.github/workflows/test.yml:108` -- `sql-schema-tests` job의 fixture 실행 목록(신규 fixture 파일명을 이 목록에 추가). migration은 `infra/supabase/migrations/*.sql` 전체를 정렬 실행하므로 별도 등록이 필요 없다.
- `packages/read-model/src/database.types.ts` -- RPC 시그니처도 타입으로 추적됨(`publish_attempt` 등 기존 RPC 참고). 운영 적용 후 재생성 대상.

## Tasks & Acceptance

**Execution:**
- `infra/supabase/migrations/202609031500_create_emit_open_command.sql` -- `outcome_events(logical_run_key, ticker, strategy, command_type)` 유니크 인덱스 추가 + `public.emit_open_command(p_logical_run_key text, p_ticker text, p_strategy text) returns jsonb` 함수(위 로직) 생성, `security definer`/`set search_path=public`, `revoke ... from public, anon, authenticated` + `grant ... to service_role` -- Story 3.3이 트랜잭션 안에서 호출할 idempotent 진입점을 DB 경계에 확립하기 위해서다.
- `tests/sql/test_outcome_open_command.sql` -- I/O 매트릭스의 6개 시나리오를 rollback fixture로 검증(신규 발행 후 `outcome_events`/`candidate_outcome` 행 내용 확인, 동일 key 재호출 시 event_id/outcome_id 불변, 이미 OPEN인 상태에서 재호출 시 신규 행 없음, intraday key 거부, 종가 부재 거부, 잘못된 전략 거부) -- 선언한 계약과 실제 동작의 차이를 잡기 위해서다.
- `.github/workflows/test.yml:108` -- 목록에 `tests/sql/test_outcome_open_command.sql` 추가 -- CI에서 Story 3.2 계약 누락을 막기 위해서다.
- `packages/read-model/src/database.types.ts` -- 운영 project에 migration 적용 후 Supabase 생성 타입으로 갱신(`emit_open_command` RPC 타입 반영) -- 코드와 운영 schema 드리프트를 막기 위해서다.

**Acceptance Criteria:**
- Given close 배치의 canonical 후보 집합에서 (ticker,strategy) 조합, when `emit_open_command`를 호출하면, `(logical_run_key, ticker, strategy, command_type=OPEN)` key로 `outcome_events`에 append되고 같은 key로 재호출 시 새 이벤트를 만들지 않고 기존 이벤트를 반환한다.
- Given OPEN 이벤트가 발행되는 경우, when entry 필드를 기록하면, entry_date=해당 거래일, entry_price=그 거래일 `daily_ohlcv.close`(adjusted)로 고정되고 이후 재호출로 값이 바뀌지 않는다.
- Given 이미 해당 (ticker,strategy)에 OPEN 상태인 outcome이 존재하는 경우, when 다른 거래일 logical_run_key로 같은 종목을 다시 호출하면, 새 진입을 생성하지 않는다.
- Given 이 RPC가 구현되는 경우, when `apps/batch/`나 `publish_attempt`의 호출부를 확인하면, 어디서도 호출되지 않는다(장중 배치가 이 로직을 호출하지 않는다는 요건은 호출부 부재로 충족되며, `batch_kind` 가드가 방어선을 이중화한다).

## Spec Change Log

## Review Triage Log

### 2026-09-03 — Review pass
- intent_gap: 0
- bad_spec: 0
- patch: 5: (high 0high, medium 3medium, low 2low)
- defer: 0
- dismissed:
  - `(ticker,strategy)`당 OPEN 1건만 허용하는 규칙을 DB가 강제하지 않는다는 지적 — 반증됨: `candidate_outcome_one_open_per_ticker_strategy_idx`(Story 3.1, `202609031300_create_outcome_schema.sql:55-57`) partial unique index가 이미 이 규칙을 강제한다.
  - 같은 거래일에 서로 다른 `logical_run_key`로 두 번 호출되면 재진입 가드를 우회해 unique_violation이 발생한다는 지적(blind-hunter/edge-case-hunter 중복 제기) — 반증됨: `batch_kind='close'`의 `logical_run_key`는 `close:<trading_day>` 형식으로 고정되고 `apps/batch/scheduler.py`의 `_build_logical_run_key`가 결정적으로 생성하므로, 같은 trading_day에 서로 다른 close `logical_run_key`가 존재할 수 없다(verification-gap 리뷰어가 코드로 직접 확인).
  - 예외에 SQLSTATE/errcode가 없어 프로그래밍적 구분이 어렵다는 지적 — 이 저장소의 모든 기존 RPC(`start_attempt`, `write_stage`, `skip_attempt`, `sync_vanished_tags`)가 동일하게 `raise exception using message=...`만 쓴다. 기존 컨벤션과 일치하므로 이 diff가 만든 결함이 아니다.
  - 유니크 인덱스를 트랜잭션 내에서 `concurrently` 없이 생성한다는 지적 — 이 저장소의 모든 index 생성 migration(Story 3.1의 OPEN partial unique index 포함)이 동일한 패턴이다. 기존 컨벤션과 일치.
  - `candidate_outcome`에 `(ticker,strategy,status)`/`(ticker,strategy,entry_date)` 조회용 index가 없다는 지적 — 실제 성능 문제 근거가 없는 조기 최적화로 판단(Story 3.1 리뷰에서 동일 사유로 유사 지적을 기각한 선례와 일치).
  - `ticker`/`strategy`가 실제 canonical 후보인지 검증하지 않는다는 지적 — intent-contract Never 절이 후보 검증·command 발행 오케스트레이션을 Story 3.3 범위로 명시한다. 이 RPC는 3.3이 태깅된 후보에 대해서만 호출할 idempotent 원시 연산이다.
  - 동시성/경합 호출이나 유니크 인덱스 자체를 직접 검증하는 fixture가 없다는 지적 — replay 시나리오(`v_event_count <> 1` 검증)가 이 인덱스에 의존하므로 인덱스 부재·오작동 시 해당 assertion이 이미 실패한다. 간접적으로 이미 검증됨.
  - `emit_open_command`가 아직 어디서도 호출되지 않음을 검증하는 assertion이 없다는 지적 — 코드 결함이 아니라 프로세스 확인 사항이며, `apps/batch/`와 `publish_attempt`에 대한 grep으로 이미 직접 확인했다(verification-gap 리뷰어도 동일하게 확인).
  - `p_ticker`/`p_logical_run_key`에 명시적 NULL 가드가 없어 오류 메시지가 불친절하다는 지적 — 이 저장소의 다른 RPC(`start_attempt`, `skip_attempt` 등)도 text 인자에 별도 NULL 가드를 두지 않고 하위 FK/제약 오류에 위임한다. 기존 컨벤션과 일치.
  - 전략 목록 `('A','B','C')`을 하드코딩해 별도 source of truth를 복제한다는 지적 — 이 schema의 다른 모든 테이블(`candidate_tags`, `candidate_outcome`, `outcome_events` 자신)도 동일하게 하드코딩하며, 이 저장소에 별도 전략 enum/lookup 테이블이 없다.
  - intent-alignment 감사의 "e2e 테스트"·스프린트 동기화·커밋 미실행 관찰 — 코드 결함이 아니라 워크플로 후속 단계(이 Auto Run의 Finalize 단계에서 수행)이며, DB 전용 스토리라 Playwright E2E는 spec 자체 판단으로도 적용 대상이 아니다(Story 3.1과 동일 판단).
- addressed_findings:
  - `[medium]` `[patch]` `p_strategy`가 NULL이면 `p_strategy not in ('A','B','C')`가 NULL로 평가되어 `INVALID_STRATEGY` 가드를 우회하고 이후 NOT NULL 제약 위반이라는 불친절한 오류로 이어졌다 — 가드를 `p_strategy is null or p_strategy not in (...)`로 수정.
  - `[medium]` `[patch]` 최초 OPEN 삽입 시 `for update` 잠금이 "행이 있을 때만" 걸려 두 개의 서로 다른 거래일 close 배치가 같은 티커에 동시에 최초 진입을 시도하면 partial unique index 위반이 처리되지 않은 예외로 전파될 수 있었다 — `candidate_outcome` insert를 예외 블록으로 감싸 `unique_violation`을 잡아 기존 OPEN 행을 재조회한 뒤 `ALREADY_OPEN` 응답으로 정상 반환하도록 수정.
  - `[low]` `[patch]` `ALREADY_OPEN` no-op 응답에만 `replayed` 키가 빠져 있어 세 응답 스키마가 일관되지 않았다 — `replayed: false`를 추가했다.
  - `[low]` `[patch]` replay 분기에서 `existing_event`/`candidate_outcome` 재조회가 못 찾은 경우를 확인하지 않아 원장 드리프트 시 `event_id`/`entry_price`가 null인 응답을 조용히 반환할 수 있었다 — 각 조회에 `if not found then raise exception` 가드를 추가했다.
  - `[medium]` `[patch]` 위 4개 항목을 패치하며 구현 subagent가 이미 운영에 적용된 `202609031500_create_emit_open_command.sql`을 새 forward migration이 아니라 파일 자체를 수정하는 방식으로 고쳐, `infra/supabase/migrations/README.md`의 AD-14(forward-only 진화) 규약을 위반하고 저장소 migration 목록과 운영 `list_migrations` 이력(`202609031501_fix_emit_open_command_review_patch`가 파일 없이 존재)이 어긋났다 — `202609031500`을 원래 내용으로 되돌리고, 패치된 함수 본문만 담은 신규 forward migration `infra/supabase/migrations/202609031501_fix_emit_open_command_review_patch.sql`을 추가해 저장소와 운영 이력을 다시 일치시켰다(운영 함수 정의를 `pg_proc.prosrc`로 직접 대조해 확인).

## Design Notes

`candidate_outcome`에는 `logical_run_key`나 이벤트 참조 컬럼이 없으므로, 재호출 시 기존 projection 행은 `(ticker, strategy, entry_date=trading_day)`로 찾는다 — `trading_day`는 `logical_run_key`에서 결정적으로 유도되므로 안전하다. "이미 OPEN이면 no-op"과 "동일 key 재호출이면 replay"는 서로 다른 시나리오다: 전자는 사전 조회로 이벤트 자체를 만들지 않고, 후자는 `on conflict do nothing`으로 삽입을 시도한 뒤 실패하면 기존 행을 재조회해 반환한다(`start_attempt` 패턴과 동일).

## Verification

**Commands:**
- `psql -v ON_ERROR_STOP=1 "$DATABASE_URL" -f tests/sql/test_outcome_open_command.sql` -- expected: 모든 assertion 통과 후 rollback.
- `npm run typecheck` -- expected: 갱신된 DB 타입을 소비하는 TypeScript 전체 통과.
- `uv run --with pandas --with numpy --with pyarrow --with pytest pytest` -- expected: 기존 batch/domain 회귀망 통과(baseline에 존재하는 무관한 실패 제외).
- `git diff --check` -- expected: 공백 오류 없음.

**Manual checks (if no CLI):**
- Supabase MCP로 운영 project에 migration 적용, `emit_open_command` 함수 존재·grant 상태, fixture pass 행을 확인한다.
- UI 변경이 없는 DB 전용 스토리이므로 Playwright E2E는 적용 대상이 아니다.

## Auto Run Result

**구현 요약:** 운영 Supabase project(`qqhjeumlecaudsiqhhdu`)에 `public.emit_open_command(p_logical_run_key, p_ticker, p_strategy)` RPC를 도입했다. `outcome_events`에 `(logical_run_key, ticker, strategy, command_type)` 유니크 인덱스를 추가해 command 멱등 키를 DB 경계에서 강제하고, 동일 key 재호출은 새 이벤트를 만들지 않고 기존 `event_id`/`outcome_id`/`entry_price`를 replay하며, 이미 다른 거래일에 `(ticker,strategy)` OPEN이 있으면 이벤트·projection 모두 만들지 않는 `ALREADY_OPEN` no-op을 반환한다. entry_date/entry_price는 `daily_ohlcv`의 해당 거래일 종가로 고정되고, `batch_kind<>'close'`와 종가 부재는 각각 명확한 오류로 거부한다. 이 RPC는 Story 3.3 이전까지 `apps/batch/`나 `publish_attempt` 어디에서도 호출되지 않는다(grep으로 확인).

**변경 파일:**
- `infra/supabase/migrations/202609031500_create_emit_open_command.sql` -- `outcome_events` 멱등 키 유니크 인덱스와 `emit_open_command` 함수 최초 도입(리뷰 패치 전 원본 상태로 보존).
- `infra/supabase/migrations/202609031501_fix_emit_open_command_review_patch.sql` -- 리뷰 후속(AD-14 forward-only): `emit_open_command`를 `create or replace`로 갱신 — NULL 전략 가드 우회 수정, 최초 OPEN 삽입 동시 경합 시 `unique_violation`을 잡아 `ALREADY_OPEN`으로 정상 응답, 사전 조회 `ALREADY_OPEN` 응답에 `replayed:false` 추가, replay 분기 재조회에 `not found` 가드(`OUTCOME_EVENT_MISSING`/`OUTCOME_PROJECTION_MISSING`) 추가.
- `tests/sql/test_outcome_open_command.sql` -- I/O 매트릭스 6개 시나리오와 리뷰 후속 4개 시나리오(NULL 전략, 동시 삽입 경합, replay 응답 스키마, replay 시 projection drift)를 검증하는 rollback fixture.
- `.github/workflows/test.yml` -- `sql-schema-tests` job에 신규 fixture 연결.
- `packages/read-model/src/database.types.ts` -- 운영 project에서 재생성한 공유 DB 타입(`emit_open_command` RPC 시그니처 반영).

**리뷰 findings 분류:** patch 5건(적용 완료, 아래 addressed_findings 참조 — review triage log의 4건은 4개 리뷰 레이어가 제기했고, 5번째(migration forward-only 위반)는 그 4건을 패치하는 과정에서 직접 발견해 같은 패스에서 수정), defer 0건, dismissed 11건(review triage log 참조 — blind-hunter/edge-case-hunter의 두 핵심 지적은 verification-gap 리뷰어가 코드로 직접 반증, 나머지는 기존 컨벤션과 일치하거나 intent-contract Never 절 기준 범위 밖이거나 이미 간접 검증됨).

**후속 리뷰 권고:** `true` (patch medium 3건 + low 2건 → 3×3 + 1×2 = 11 ≥ 5).

**검증 수행:**
- Supabase MCP `execute_sql`로 운영 project에서 `tests/sql/test_outcome_open_command.sql` fixture 전체(리뷰 후속 시나리오 포함, `begin;...rollback;`)를 두 차례(패치 전/후) 직접 실행 — 모두 `outcome_open_command / pass`, rollback 후 `ZZTEST*` 잔여 행 0건 확인.
- `pg_proc.prosrc` 직접 조회로 운영에 적용된 `emit_open_command` 함수 본문이 저장소의 `202609031500`+`202609031501` 두 migration을 순서대로 적용한 결과와 정확히 일치함을 확인.
- `npm run typecheck` -- 통과.
- `uv run --with pandas --with numpy --with pyarrow --with pytest pytest` -- 234 passed, 7 failed(모두 `tests/batch/test_scheduler.py`, baseline(3fab980)에서도 동일하게 실패하는 기존 회귀로 이 스토리와 무관, Story 3.1에서도 동일하게 확인된 사항).
- `git diff --check` -- 공백 오류 없음.
- `emit_open_command`에 대한 grep으로 `apps/batch/`·`publish_attempt` 어디에도 호출부가 없음을 확인(Story 3.3 범위임을 재확인).
- UI 변경이 없는 DB 전용 스토리라 Playwright E2E는 적용 대상이 아니며 실행하지 않았다(spec 자체 판단과 일치).

**잔여 위험:**
- Story 3.3이 `publish_attempt` 트랜잭션 안에서 이 RPC를 호출하도록 연결하기 전까지는 실제 OPEN outcome이 전혀 생성되지 않는다(의도된 범위).
- `emit_open_command`의 재진입 가드는 `candidate_outcome` 조회 시점의 `for update` 잠금에 의존하며, `publish_attempt`가 이미 `logical_run_key`별 advisory xact lock을 잡으므로 같은 거래일 내 경합은 없으나, 서로 다른 거래일의 close 배치가 이론적으로 동시에 실행되는 경우의 완전한 직렬성은 이 함수 자체가 보장하지 않는다(unique_violation을 우아하게 처리하지만, 그 경합이 실제로 발생할 수 있는 운영 시나리오인지는 Story 3.3의 오케스트레이션 설계에서 재확인이 필요하다).
- Story 3.1에서 이미 기록된 `skip_attempt` RPC 운영 미적용 건은 이 스토리와 무관하게 여전히 미해결이다(`deferred-work.md` 참조).
