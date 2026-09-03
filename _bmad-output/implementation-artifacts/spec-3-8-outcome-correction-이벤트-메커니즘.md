---
title: '3.8 Outcome correction 이벤트 메커니즘'
type: 'feature'
created: '2026-09-04'
status: 'done'
review_loop_iteration: 0
followup_review_recommended: true
context: []
warnings: ['oversized']
deferred:
  - summary: >-
      apply_outcome_correction의 outcome_events insert에 on conflict가 없어, 같은
      (logical_run_key,ticker,strategy)에 CORRECTION을 두 번째로 남기면 raw
      unique_violation으로 거부된다.
    evidence: |-
      outcome_events_open_command_key_idx는 (logical_run_key,ticker,strategy,command_type)
      unique index이고 command_type='CORRECTION'도 같은 index에 걸린다(blind-hunter 발견,
      infra/supabase/migrations/202609031500_create_emit_open_command.sql:10-11과
      202609032200_add_outcome_correction_mechanism.sql의 insert 확인). 같은 날 같은
      outcome에 서로 다른 사유로 두 번 correction을 남기는 경우 스펙/AC 어디에도 명시되지
      않아, idempotent replay로 만들지 매번 새 이벤트로 append할지는 사람의 설계 결정이 필요하다.
    location: infra/supabase/migrations/202609032200_add_outcome_correction_mechanism.sql:595-618
    severity: medium
  - summary: >-
      apply_outcome_correction이 candidate_outcome의 기존 unique 제약(OPEN 1건 제한 등)을
      사전 검증하지 않아, 충돌 시 친절한 도메인 에러 대신 raw postgres 예외가 노출된다.
    evidence: |-
      candidate_outcome_one_open_per_ticker_strategy_idx는 status='OPEN'에만 걸린 partial
      unique index다(infra/supabase/migrations/202609031300_create_outcome_schema.sql:55-57).
      SUSPENDED->OPEN correction 시점에 같은 (ticker,strategy)로 이미 다른 OPEN 행이 있으면
      (예: 정지 중 재진입 발생) 이 correction은 unique_violation으로 실패한다(blind-hunter/
      edge-case-hunter 공통 지적). 데이터 무결성은 지켜지지만 에러 메시지가 OUTCOME_NOT_FOUND
      류의 다른 도메인 에러와 다르게 일관성이 없다.
    location: infra/supabase/migrations/202609032200_add_outcome_correction_mechanism.sql:585-593
    severity: medium
  - summary: >-
      p_new_status가 SUSPENDED로 향하는 correction은 exit_date/exit_price/return_pct를
      null로 되돌리지 않아, terminal에서 SUSPENDED로 되돌리면 종결값이 남을 수 있다.
    evidence: |-
      apply_outcome_correction의 분기는 p_new_status='OPEN'일 때만 exit 3필드를 null로
      되돌리고, 그 외(SUSPENDED 포함)는 명시된 값 또는 기존 값을 유지한다(blind-hunter 발견).
      epics Story 3.8 AC와 이 스펙의 I/O 매트릭스 모두 SUSPENDED->OPEN 복귀만 다루고
      TP/SL/TIMEOUT->SUSPENDED 되돌리기는 요구하지 않아 이번 스토리 범위 밖이지만, 향후
      이 경로가 실제로 쓰이면 잔존 종결값이 노출될 수 있다.
    location: infra/supabase/migrations/202609032200_add_outcome_correction_mechanism.sql:585-593
    severity: low
  - summary: >-
      apply_outcome_correction에 entry_date를 정정하는 파라미터가 없어, 진입일 자체가
      잘못 기록된 경우 정정할 방법이 없다.
    evidence: |-
      함수 시그니처는 p_new_entry_price는 받지만 entry_date는 받지 않는다(blind-hunter
      발견). entry_date는 (ticker,strategy,entry_date) unique 제약과 holding_days/cutoff_n
      계산의 기준이라 영향이 있지만, epics AC1의 "수치 수정" 요구는 손익/가격 수치를
      가리키는 것으로 읽히며 진입일 자체의 정정은 이번 스토리 스펙 어디에도 명시되지 않았다.
    location: infra/supabase/migrations/202609032200_add_outcome_correction_mechanism.sql:538-550
    severity: low
  - summary: >-
      apply_outcome_correction(outcome_id 잠금)과 emit_open_command(ticker/strategy
      조회)가 서로 다른 잠금 키를 써서, 같은 (ticker,strategy)에 대한 동시 실행이
      경합하면 unique index 위반으로만 한쪽이 실패하는 미검증 경로가 있다.
    evidence: |-
      emit_open_command는 status in ('OPEN','SUSPENDED')로 select ... for update하고
      apply_outcome_correction은 outcome_id로만 잠근다(blind-hunter 지적). 실제로는
      correction은 드문 수동 작업이고 emit_open_command는 하루 한 번의 단일 close
      배치에서만 호출되어 발생 확률은 낮으며, 실패해도 트랜잭션 롤백으로 데이터 손상은
      없다.
    location: infra/supabase/migrations/202609032200_add_outcome_correction_mechanism.sql:452-474
    severity: low
  - summary: >-
      publish_attempt의 SUSPENDED/TP/SL/TIMEOUT UPDATE가 실제로 candidate_outcome.version을
      증가시키는지 검증하는 명시적 테스트 assertion이 없다.
    evidence: |-
      guard_candidate_outcome_mutation 트리거는 플래그로 통과한 모든 UPDATE에 대해 무조건
      new.version := old.version + 1을 실행하므로 publish_attempt 경로도 구조적으로 동일하게
      적용된다(세션이 트리거 정의를 직접 확인). 다만 blind-hunter 지적대로 이를 직접 읽고
      비교하는 assertion은 3.5~3.7 회귀 시나리오에 아직 추가되지 않았다.
    location: tests/sql/test_run_lineage.sql
    severity: low
baseline_revision: '48fb0e79449da1583678ef0e52f040eec873f284'
---

<intent-contract>

## Intent

**Problem:** `candidate_outcome`은 현재 raw UPDATE로 자유롭게 수정 가능해 terminal(TP/SL/TIMEOUT) 상태의 불변성이 코드 관행에만 의존하고 있고, SUSPENDED 복귀(Story 3.5가 예고)나 수치 정정을 남길 버전 관리된 경로가 없다. 또한 `emit_open_command`의 재진입 가드가 `status='OPEN'`만 확인해 SUSPENDED 상태에서 재태깅되면 중복 `candidate_outcome` 행이 생길 수 있다(2026-09-03 review, deferred-work.md 기존 항목).

**Approach:** `candidate_outcome`에 `version` 컬럼과 BEFORE UPDATE 가드 트리거를 추가해 세션 로컬 플래그가 켜진 경우에만 UPDATE를 허용하고 매 통과마다 버전을 증가시킨다. `publish_attempt`의 기존 SUSPENDED/TP/SL/TIMEOUT UPDATE는 이 플래그를 잠깐 켰다 끄는 방식으로 그대로 동작을 유지한다. `expected_version` 낙관적 동시성 검사를 하는 새 `apply_outcome_correction` RPC를 추가해 `outcome_events`에 `CORRECTION` 이벤트를 append하고 같은 플래그로 projection을 갱신한다. `emit_open_command`의 재진입 가드를 `SUSPENDED`까지 확장한다.

## Boundaries & Constraints

**Always:**
- `outcome_events`는 계속 append-only다 -- correction은 기존 이벤트를 수정하지 않고 `command_type='CORRECTION'`인 새 행을 추가한다.
- `candidate_outcome`의 모든 UPDATE는 `set_config('wave_double.outcome_mutation_allowed', 'on', true)`가 켜진 상태에서만 통과하며, 통과할 때마다 BEFORE UPDATE 트리거가 `version`을 정확히 1 증가시킨다. 이 플래그 없이 시도된 UPDATE(raw UPDATE, service_role 포함)는 예외로 거부된다.
- `apply_outcome_correction`은 대상 행을 잠근 뒤 `candidate_outcome.version = p_expected_version`을 확인하고, 일치할 때만 이벤트 삽입과 projection 갱신을 수행한다. 불일치 시 아무 것도 쓰지 않고 예외로 거부한다.
- SUSPENDED에서 `OPEN`으로 복귀하는 correction은 `exit_date`/`exit_price`/`return_pct`를 다시 null로 되돌리고 `entry_date`/`entry_price`는 보존한다. TP/SL/TIMEOUT/DELISTED로의 correction은 그 값들을 유지하거나 명시적으로 갱신한다.
- terminal 상태(TP/SL/TIMEOUT)의 수치 정정(entry_price/exit_price/return_pct/holding_days/cutoff_n)도 같은 correction 경로로 허용한다(epics AC1의 "수치 수정" 요구).
- `emit_open_command`의 재진입 가드는 기존 `status='OPEN'` 검사에 더해 같은 (ticker,strategy)에 `SUSPENDED` 행이 있으면 신규 OPEN을 만들지 않고 skip 응답을 반환한다. 기존 `ALREADY_OPEN` reason 문자열과 그 시나리오의 동작은 그대로 둔다(`tests/sql/test_outcome_open_command.sql` 회귀 보존).
- AD-14: 이미 운영에 적용된 마이그레이션 파일은 손대지 않는다. 이번 변경은 새 forward migration으로만 표현한다.

**Never:**
- GitHub Issue 생성/close API 호출을 SQL에서 하지 않는다 -- Story 3.5와 동일하게 알림 배선은 `publish_attempt`가 실제 오케스트레이터에 연결된 이후 별도 스토리로 미룬다. correction 이벤트의 `payload`(사유, 시각, 이전/이후 상태)는 그 미래 배선이 이슈를 상관시킬 수 있는 최소한의 근거만 남긴다.
- `outcome_events`/`outcome_observations`로부터의 replay/rebuild 검증(Story 3.10)을 구현하지 않는다.
- TP/SL/TIMEOUT 판정 임계값, cutoff_n 계산, SUSPENDED 최초 감지 로직(Story 3.5~3.7)을 변경하지 않는다 -- 이번 스토리는 그 결과를 되돌리는 경로만 추가한다.
- `candidate_outcome`에 RLS 정책을 새로 추가하지 않는다(기존 RLS 활성+정책 0개=default-deny 유지, 접근 통제는 계속 함수 단위 GRANT/REVOKE로만 한다).

## I/O & Edge-Case Matrix

| Scenario | Input / State | Expected Output / Behavior | Error Handling |
|----------|--------------|---------------------------|----------------|
| Raw UPDATE 시도 | 가드 플래그 미설정 상태에서 `update candidate_outcome set status=... where outcome_id=...` 직접 실행 | 트리거가 예외 발생, 행 변경 없음 | errcode 55000, 메시지에 correction 경로 안내 |
| SUSPENDED 정상 복귀 | SUSPENDED 행, `p_expected_version`이 현재 버전과 일치, `p_new_status='OPEN'` | `CORRECTION` 이벤트 append, status→OPEN, exit 3필드 null로 복귀, version+1 | 없음(정상) |
| stale expected_version | 다른 세션이 먼저 correction/판정을 적용해 버전이 이미 증가한 뒤 구버전 `p_expected_version`으로 재호출 | 이벤트/projection 모두 미변경 | `CORRECTION_VERSION_MISMATCH` 예외 |
| terminal 수치 정정 | TP로 이미 종결된 행에 `p_new_status='TP'`, 보정된 `p_new_return_pct` 전달 | `CORRECTION` 이벤트 append, `return_pct`만 갱신, status는 TP 유지, version+1 | 없음(정상) |
| 존재하지 않는 outcome_id | 임의 uuid | 이벤트/projection 미생성 | `OUTCOME_NOT_FOUND` 예외 |
| 잘못된 신규 상태값 | `p_new_status='INVALID'` | 이벤트/projection 미생성 | `INVALID_STATUS` 예외(스키마 CHECK 도달 전 조기 검증) |
| SUSPENDED 재태깅 | (ticker,strategy)가 SUSPENDED인 상태에서 다음 close 배치가 같은 종목을 다시 태깅 | `emit_open_command`가 신규 OPEN 미생성, skip 응답 반환, `candidate_outcome` 중복 행 없음 | 없음(skip은 정상 응답, reason='ALREADY_TRACKED_SUSPENDED') |

</intent-contract>

## Code Map

- `infra/supabase/migrations/202609031300_create_outcome_schema.sql:32-57` -- `candidate_outcome` 원본 정의(현재 `version` 컬럼 없음, "deliberately mutable" 주석). 이번 스토리가 `version integer not null default 1`을 추가하고 그 "자유롭게 mutable" 전제를 가드 트리거로 좁힌다.
- `infra/supabase/migrations/202609031300_create_outcome_schema.sql:59-77` -- `reject_outcome_ledger_mutation()`/append-only 트리거 참고 패턴. `candidate_outcome`용 가드 트리거는 이 패턴(트리거 함수 + `before update`)을 재사용하되 전면 차단이 아니라 세션 플래그 기반 조건부 차단으로 변형한다.
- `infra/supabase/migrations/202609032101_fix_timeout_cutoff_review_patch.sql:11-243` -- `publish_attempt` 현재 권위 정의(최신 baseline). 122-125행(SUSPENDED UPDATE), 207-214행(TP/SL/TIMEOUT UPDATE) 두 지점을 `set_config` on/off로 감싸는 `create or replace`가 필요하다. 별도 판정 로직 변경은 없음.
- `infra/supabase/migrations/202609031501_fix_emit_open_command_review_patch.sql:53-66` -- `emit_open_command`의 현재 재진입 가드(`status='OPEN'`만 조회). SUSPENDED 조건을 추가하는 `create or replace` 대상.
- `infra/supabase/migrations/202609031500_create_emit_open_command.sql:10-11` -- `outcome_events_open_command_key_idx` unique index, `(logical_run_key,ticker,strategy,command_type)`. `command_type='CORRECTION'`도 동일 index 자동 적용(같은 실행에서 같은 key로 중복 correction 방지) -- 스키마 변경 불필요.
- `infra/supabase/migrations/202609011600_create_run_lineage.sql:5-19` -- `logical_runs` 스키마와 `logical_run_key` shape 제약(`premarket|intraday|close:YYYY-MM-DD[...]`). `apply_outcome_correction`은 FK 제약상 기존 `logical_runs` 행을 참조하는 `p_logical_run_key`를 요구한다 -- 운영자/자동화 호출자는 보정을 남기는 시점과 연결된 기존 key(전형적으로 최근 close run의 key)를 넘긴다.
- `_bmad-output/implementation-artifacts/deferred-work.md:18` -- 이번 스토리가 반드시 함께 다뤄야 한다고 명시적으로 남겨진 SUSPENDED 재진입 중복 생성 gap의 원출처.
- `_bmad-output/implementation-artifacts/spec-3-5-가격-조정-이상-감지-suspended-전이.md` -- GitHub Issue 알림 배선이 `publish_attempt` 프로덕션 미배선으로 인해 별도 스토리로 이연된 선례(이번 스토리도 동일 판단 유지).
- `tests/sql/test_outcome_open_command.sql` -- `emit_open_command` 전용 fixture(ZZTEST 티커 컨벤션). SUSPENDED 재진입 스킵 시나리오를 여기에 추가한다.
- `tests/sql/test_run_lineage.sql` -- `publish_attempt` 전 스토리 시나리오 누적 fixture(ZZLIN 티커 컨벤션). correction 이벤트(복귀/수치 정정/버전 불일치/raw UPDATE 차단) 시나리오를 3.7 시나리오 뒤에 추가한다.
- `packages/read-model/src/database.types.ts` -- Supabase 생성 타입. `version` 컬럼과 `apply_outcome_correction` 함수 시그니처가 추가되므로 이번엔 실제 diff가 발생할 것으로 예상하고 재생성 후 커밋한다(3.6/3.7의 "diff 없음 확인"과 다른 케이스).

## Tasks & Acceptance

**Execution:**
- `infra/supabase/migrations/202609032200_add_outcome_correction_mechanism.sql` -- (1) `alter table candidate_outcome add column version integer not null default 1;` (2) `guard_candidate_outcome_mutation()` 트리거 함수 + `before update on candidate_outcome` 트리거 생성(`wave_double.outcome_mutation_allowed`가 `'on'`이 아니면 예외, 통과 시 `new.version := old.version + 1`) (3) `publish_attempt`를 `create or replace`해 기존 두 UPDATE 지점을 `perform set_config(...,'on',true)` / `perform set_config(...,'off',true)`로 감싼다(판정 로직 자체는 무변경) (4) `emit_open_command`를 `create or replace`해 재진입 가드 조회를 `status in ('OPEN','SUSPENDED')`로 넓히고, SUSPENDED 매치는 항상 skip(reason `ALREADY_TRACKED_SUSPENDED`)하도록 분기 추가 (5) `apply_outcome_correction(p_logical_run_key text, p_outcome_id uuid, p_expected_version integer, p_reason text, p_new_status text, p_new_entry_price numeric default null, p_new_exit_date date default null, p_new_exit_price numeric default null, p_new_return_pct numeric default null, p_new_holding_days integer default null, p_new_cutoff_n integer default null) returns jsonb` 신규 생성(security definer, `for update` 잠금, 버전 검사, `outcome_events` insert, 가드 플래그로 감싼 `candidate_outcome` UPDATE, OPEN 미만 상태로 갈 때 exit 3필드 null 처리) (6) `revoke execute ... from public, anon, authenticated; grant execute ... to service_role;`.
- `tests/sql/test_outcome_open_command.sql` -- SUSPENDED 상태의 (ticker,strategy)를 준비한 뒤 `emit_open_command` 재호출이 신규 OPEN/candidate_outcome 행 없이 `ALREADY_TRACKED_SUSPENDED`로 skip됨을 검증하는 시나리오 추가.
- `tests/sql/test_run_lineage.sql` -- I/O 매트릭스 7개 시나리오(raw UPDATE 차단, SUSPENDED→OPEN 복귀, stale version 거부, terminal 수치 정정, 존재하지 않는 outcome_id, 잘못된 status, 위 emit_open_command 스킵과의 정합)를 커버하는 fixture를 3.7 시나리오 뒤에 추가.
- `packages/read-model/src/database.types.ts` -- 운영 project에 migration 적용 후 `generate_typescript_types` 재실행, `version` 컬럼과 `apply_outcome_correction` 함수 타입이 반영된 diff를 커밋.

**Acceptance Criteria:**
- Given terminal(TP/SL/TIMEOUT) 또는 그 외 상태의 `candidate_outcome` 행이 있는 경우, when 가드 플래그 없이 raw UPDATE를 시도하면, then 트리거가 예외를 던져 거부되고 `apply_outcome_correction`만 유효한 수정 경로로 남는다.
- Given `apply_outcome_correction`을 호출하는 경우, when `p_expected_version`을 지정하면, then 현재 저장된 `version`과 일치할 때만 적용되고 불일치 시 이벤트/projection 변경 없이 거부된다.
- Given SUSPENDED 상태의 outcome이 있는 경우, when 정상 복귀 correction을 적용하면, then projection이 OPEN으로 갱신되고(exit 3필드 null 복귀) `outcome_events` 원본 이력은 삭제되지 않는다.
- Given correction 이력을 감사하는 경우, when `outcome_events`를 `command_type='CORRECTION'`으로 조회하면, then 모든 correction이 사유(`payload->>'reason'`)와 함께 시간순으로 남아있다.
- Given SUSPENDED 상태인 (ticker,strategy)가 있는 경우, when 다음 close 배치가 같은 종목을 재태깅하면, then `emit_open_command`가 신규 OPEN을 만들지 않아 `candidate_outcome`에 중복 행이 생기지 않는다.

## Design Notes

`version` 증가를 가드 트리거 자체에 두어(호출자가 명시적으로 증가시키지 않음) `publish_attempt`의 기존 SUSPENDED/TP/SL/TIMEOUT UPDATE도 자동으로 버전을 쌓게 했다 -- 그래야 correction의 `expected_version` 검사가 "correction끼리"뿐 아니라 "운영자가 SUSPENDED를 확인하는 사이 배치가 먼저 TIMEOUT을 확정해버린" 경우도 정확히 감지한다. `set_config(...,true)`(트랜잭션 스코프)를 UPDATE 직후 바로 `'off'`로 되돌리는 이유는 같은 트랜잭션 안에서 플래그가 계속 켜진 채로 남아 다른 무관한 UPDATE까지 우연히 통과하는 것을 막기 위함이다(같은 함수 내 다음 루프 반복에서 다시 켜고 끄는 반복 비용은 무시할 수준).

`apply_outcome_correction`이 `p_logical_run_key`를 필수로 받는 이유는 `outcome_events.logical_run_key`가 `logical_runs` FK이자 NOT NULL이라서다 -- correction은 배치 attempt가 아니지만, 감사 추적을 위해 어느 운영 시점(전형적으로 correction을 남긴 날의 close run)과 연결됐는지 남긴다. 새 `logical_runs` 행을 이 함수가 직접 만들지는 않는다(기존 값 재사용, FK 위반 시 그대로 예외).

## Verification

**Commands:**
- `psql -v ON_ERROR_STOP=1 "$DATABASE_URL" -f tests/sql/test_outcome_open_command.sql` -- expected: 모든 assertion 통과 후 rollback.
- `psql -v ON_ERROR_STOP=1 "$DATABASE_URL" -f tests/sql/test_run_lineage.sql` -- expected: 모든 assertion 통과 후 rollback.
- `npm run typecheck` -- expected: 갱신된 DB 타입을 소비하는 TypeScript 전체 통과.
- `uv run --with pandas --with numpy --with pyarrow --with pytest pytest` -- expected: 기존 batch/domain 회귀망 통과.
- `git diff --check` -- expected: 공백 오류 없음.

**Manual checks (if no CLI):**
- Supabase MCP로 운영 project(`qqhjeumlecaudsiqhhdu`)에 migration 적용, `candidate_outcome.version` 컬럼 존재와 `publish_attempt`/`emit_open_command`/`apply_outcome_correction` 함수 정의 갱신을 확인한다.
- UI 변경이 없는 DB 전용 스토리이므로 Playwright E2E는 적용 대상이 아니다(Story 3.1~3.7과 동일 판단).

## Spec Change Log

## Review Triage Log

### 2026-09-04 — Review pass
- intent_gap: 0
- bad_spec: 0
- patch: 4: (high 2high, medium 1medium, low 1low)
- defer: 6: (high 0high, medium 2medium, low 4low)
- dismissed:
  - `set_config` on/off 켰다 끄는 패턴이 `publish_attempt` 2곳과 `apply_outcome_correction` 1곳에 중복돼 유지보수 리스크라는 지적(blind-hunter) -- 현재 동작에 어떤 구체적 결함도 없고 "미래에 실수할 수 있다"는 가설적 리스크일 뿐이라 이번 diff의 검증 가능한 결함이 아니다.
  - `publish_attempt`/`emit_open_command` 전체 함수 본문을 `create or replace`로 복붙해 의도치 않은 드리프트가 섞여도 리뷰어가 놓치기 쉽다는 지적(blind-hunter) -- 이 세션이 직접 202609032101/202609031501과 라인 단위로 대조해 의도한 변경(가드 플래그 wrap, SUSPENDED 재진입 분기) 외 드리프트가 없음을 확인했고, 이 전체 본문 재정의 방식 자체는 Story 3.5~3.7이 이미 동일하게 써온 이 저장소의 기존 관행(AD-14)이라 이번 스토리가 새로 만든 리스크가 아니다.
  - 가드 메커니즘이 `wave_double.outcome_mutation_allowed` 세션 플래그에만 의존해 `service_role`을 쥔 코드가 그 플래그를 직접 켜고 raw UPDATE를 할 수 있다는 지적(blind-hunter) -- 이는 이 저장소 전체가 함수 단위 GRANT/REVOKE + RLS default-deny로 접근을 통제하는 기존 보안 모델과 동일한 수준이며(코드 리뷰 규율에 의존하는 것도 기존 모든 SECURITY DEFINER 함수와 동일), 이번 스토리가 새로 도입한 구조적 약점이 아니다.
  - 상태 변경 없는 correction 호출(현재 status와 동일한 `p_new_status`, 필드 변경 없음)도 version 증가와 이벤트 append가 일어난다는 지적(edge-case-hunter/blind-hunter 공통 취지) -- epics AC4가 "모든 correction이 사유와 함께 시간순으로 남아있다"고 요구하고 어떤 correction도 감사 대상에서 제외하지 않으므로, 운영자가 명시적으로 호출한 확인성 correction을 기록하는 것은 결함이 아니라 의도된 감사 설계와 일치한다.
- addressed_findings:
  - `[high]` `[patch]` `apply_outcome_correction`의 `if target.version <> p_expected_version`이 `p_expected_version`이 NULL이면 SQL 3치 논리로 NULL이 되어 IF가 건너뛰어지고 버전 불일치 검사 자체가 우회됨을 직접 실행으로 확인(edge-case-hunter 발견, 세션이 프로덕션에서 재현: NULL을 넘긴 correction이 예외 없이 성공) -- `p_expected_version is null or target.version <> p_expected_version`으로 조건을 고쳐 NULL을 명시적으로 거부하도록 patch 예정.
  - `[high]` `[patch]` 새 `candidate_outcome_guard_mutation` 트리거가 `tests/sql/test_outcome_schema.sql:223-224`의 기존 raw UPDATE(예외 처리 블록 없음)를 거부해, 이 파일을 실행하는 `.github/workflows/test.yml`의 `sql-schema-tests` job이 그대로 깨짐을 확인(verification-gap 발견, 세션이 CI 워크플로 파일에서 해당 job의 fixture 목록과 `ON_ERROR_STOP=1` 사용을 직접 확인) -- 해당 UPDATE를 `publish_attempt`와 동일한 `set_config(...,'on',true)`/`set_config(...,'off',true)` 패턴으로 감싸도록 patch 예정.
  - `[medium]` `[patch]` `apply_outcome_correction`이 `p_reason`의 null/빈 문자열을 검증하지 않아, epics AC4("모든 correction이 사유와 함께... 남아있다")가 요구하는 감사 근거가 비어있는 채로 correction이 성립할 수 있음(blind-hunter/edge-case-hunter 공통 지적, 코드 확인으로 검증) -- `p_reason is null or length(btrim(p_reason))=0`이면 `REASON_REQUIRED`로 조기 거부하도록 patch 예정.
  - `[low]` `[patch]` 새 `apply_outcome_correction`이 `tests/sql/test_outcome_open_command.sql`이 `emit_open_command`에 대해 이미 갖춘 "only service_role may execute" grant/revoke 회귀 테스트와 동급의 테스트 없이 배포됨(blind-hunter 지적, 코드/스키마 확인으로 검증 -- 실제 GRANT/REVOKE 자체는 세션이 프로덕션에서 이미 올바름을 확인했으나 회귀 테스트가 없음) -- `tests/sql/test_run_lineage.sql`의 3.8 시나리오 블록에 동일 패턴의 grant/revoke 검증을 추가하도록 patch 예정.

### 2026-09-04 — Patch pass (confirmed patches applied)
- 4개 confirmed patch 모두 적용 완료:
  - `[high]` NULL `p_expected_version` 우회: `infra/supabase/migrations/202609032201_fix_outcome_correction_review_patch.sql`(신규 forward migration, AD-14 준수)에서 `apply_outcome_correction`을 `create or replace`해 `p_expected_version is null or target.version <> p_expected_version`으로 조건을 고침. 프로덕션(`qqhjeumlecaudsiqhhdu`)에 적용 후 NULL 전달 시 `CORRECTION_VERSION_MISMATCH` 예외가 발생하고 projection이 변경되지 않음을 직접 재현해 확인.
  - `[high]` `tests/sql/test_outcome_schema.sql:223-224`의 raw UPDATE가 새 가드 트리거에 걸려 CI가 깨지는 문제: 해당 UPDATE 전후를 `set_config('wave_double.outcome_mutation_allowed','on'/'off',true)`로 감쌈(`publish_attempt`와 동일 패턴). 부수적으로 `candidate_outcome` 컬럼/타입 배열 검사(51-59행)도 3.8이 추가한 `version` 컬럼을 반영하도록 갱신(리뷰 목록엔 없었지만 이 파일 전체 통과에 필요해 함께 수정).
  - `[medium]` `p_reason` 미검증: 같은 202609032201 migration에서 `p_new_status` 조기 검증 직후 `p_reason is null or length(btrim(p_reason))=0`이면 `REASON_REQUIRED`로 거부하도록 추가.
  - `[low]` grant/revoke 회귀 테스트 부재: `tests/sql/test_run_lineage.sql`의 3.8 시나리오 블록 끝에 `emit_open_command`와 동일 패턴으로 `apply_outcome_correction`의 `information_schema.role_routine_grants` 검증(public/anon/authenticated 실행 불가, service_role만 가능)을 추가. 같은 블록에 NULL expected_version 및 NULL/공백 reason 거부 시나리오도 추가.
- 검증: `test_outcome_schema.sql`, `test_run_lineage.sql`, `test_outcome_open_command.sql` 전체를 `begin;...rollback;`으로 감싸 프로덕션에서 실행해 모두 pass 확인. `npm run typecheck`, `uv run pytest`(241 passed) 재확인. NULL expected_version 우회가 실제로 막혔음을 별도 반복 재현으로 확인. 프로덕션에 `ZZ*` 테스트 잔여 행 없음 확인.

## Auto Run Result

**구현 요약:** `candidate_outcome`에 `version` 컬럼과 세션 플래그(`wave_double.outcome_mutation_allowed`) 기반 BEFORE UPDATE 가드 트리거를 추가해, terminal 포함 모든 상태의 raw UPDATE를 차단하고 통과하는 UPDATE마다 버전을 1 증가시켰다. `publish_attempt`의 기존 SUSPENDED/TP/SL/TIMEOUT UPDATE 두 지점은 이 플래그를 트랜잭션 스코프로 켰다 끄는 방식으로 그대로 동작을 유지했다(판정 로직 자체는 무변경). `expected_version` 낙관적 동시성 검사를 하는 신규 `apply_outcome_correction(...)` RPC를 추가해 `outcome_events`에 `command_type='CORRECTION'` 이벤트를 append하고 같은 가드 플래그로 projection을 갱신한다 -- SUSPENDED→OPEN 복귀는 exit 3필드를 null로 되돌리고, 그 외 상태로의 correction은 명시된 값만 갱신해 terminal 수치 정정도 지원한다. `emit_open_command`의 재진입 가드를 `SUSPENDED`까지 확장해, 2026-09-03 리뷰에서 지적된 SUSPENDED 재태깅 시 `candidate_outcome` 중복 행 생성 gap을 닫았다. 리뷰에서 확정된 4개 patch(NULL `expected_version` 우회, 기존 CI 테스트 파괴, `p_reason` 미검증, grant/revoke 테스트 부재)를 같은 세션에서 반영했다.

**변경 파일:**
- `infra/supabase/migrations/202609032200_add_outcome_correction_mechanism.sql` -- 신규. `version` 컬럼, 가드 트리거, `publish_attempt`/`emit_open_command` 패치, `apply_outcome_correction` 최초 정의.
- `infra/supabase/migrations/202609032201_fix_outcome_correction_review_patch.sql` -- 신규(AD-14 forward-only patch). `apply_outcome_correction`을 `create or replace`해 NULL `expected_version` 우회 차단과 `p_reason` 필수화를 추가.
- `tests/sql/test_outcome_open_command.sql` -- SUSPENDED 재태깅 skip(`ALREADY_TRACKED_SUSPENDED`) 시나리오 추가.
- `tests/sql/test_run_lineage.sql` -- correction 이벤트 I/O 매트릭스 7개 시나리오 + NULL version/NULL·공백 reason 거부 + `apply_outcome_correction` grant/revoke 회귀 시나리오 추가.
- `tests/sql/test_outcome_schema.sql` -- 기존 raw UPDATE를 가드 플래그로 감싸 신규 트리거와 호환시키고, `candidate_outcome` 컬럼/타입 배열 검사에 `version`을 반영.
- `packages/read-model/src/database.types.ts` -- `version` 컬럼과 `apply_outcome_correction` 함수 타입 반영, 실제 diff 발생.
- `_bmad-output/implementation-artifacts/sprint-status.yaml` -- `3-8-outcome-correction-이벤트-메커니즘`을 `done`으로 갱신.

**리뷰 결과 분류:**
- patch 4건 모두 적용 완료(위 Review Triage Log 참조): `[high]` NULL expected_version 우회, `[high]` test_outcome_schema.sql CI 파괴, `[medium]` p_reason 미검증, `[low]` grant/revoke 테스트 부재.
- defer 6건 (frontmatter `deferred` 참조): (medium) 같은 날 같은 outcome에 두 번째 correction 시 raw unique_violation, (medium) correction이 candidate_outcome의 기존 unique 제약과 충돌 시 raw unique_violation, (low) SUSPENDED로 향하는 correction이 exit 필드를 null로 되돌리지 않음, (low) entry_date 정정 파라미터 부재, (low) apply_outcome_correction과 emit_open_command 간 잠금 키 불일치로 인한 미검증 경합, (low) publish_attempt 전이가 version을 증가시킴을 직접 검증하는 assertion 부재.
- dismissed 4건(사유는 Review Triage Log 참조): set_config on/off 중복(가설적 리스크), 전체 함수 본문 copy-paste(기존 AD-14 관행과 동일, 드리프트 없음 직접 확인), 가드가 service_role 코드 규율에 의존(기존 보안 모델과 동일 수준), no-op correction의 version 증가·이벤트 append(의도된 감사 설계와 일치).

**Follow-up review recommendation:** `true`. 이번 patch pass에 `[high]` 심각도 항목이 2건 포함되어(NULL expected_version 우회, CI 파괴) 규칙상 고심각도 patch가 하나라도 있으면 무조건 true. (점수 계산상으로도 3×1(medium)+1×1(low)=4이지만, high 존재만으로 이미 true.)

**검증 수행:** `test_outcome_schema.sql`/`test_run_lineage.sql`(전체, story 1.3~3.8)/`test_outcome_open_command.sql`을 `begin;...rollback;`으로 감싸 운영 project(`qqhjeumlecaudsiqhhdu`)에서 실행해 모두 pass. `npm run typecheck` pass. `uv run pytest` 241 passed. `git diff --check` 공백 오류 없음. 이 세션이 독립적으로 프로덕션에서 NULL expected_version 거부, NULL/공백 reason 거부, grant 목록(service_role만 EXECUTE)을 직접 재현해 재확인했고, migration 목록(`add_outcome_correction_mechanism`, `fix_outcome_correction_review_patch`)과 `apply_outcome_correction`/트리거 정의를 `pg_get_functiondef`/`pg_trigger`로 직접 조회해 배포 상태를 확인했다. I/O 매트릭스 7개 시나리오 전부 테스트로 커버되고 실행되어 통과함을 확인(Matrix Test Audit 충족).

**잔존 리스크:** defer 처리된 6건은 이번 스토리 범위(SUSPENDED↔OPEN 복귀, terminal 수치 정정) 밖의 부가 시나리오(동일 outcome 재정정, 상태 충돌, SUSPENDED 대상 correction의 exit 필드 처리, entry_date 정정, 드문 동시성 경합)로 데이터 손상 없이 안전하게 실패(트랜잭션 롤백)하지만 사용성이 제한적이다. GitHub Issue 생성/close 자동화는 Story 3.5와 동일하게 `publish_attempt`의 실제 오케스트레이터 미배선으로 인해 이번 스토리 범위 밖으로 남아있다(별도 스토리 필요).
