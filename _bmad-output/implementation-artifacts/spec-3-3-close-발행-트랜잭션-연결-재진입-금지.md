---
title: 'Story 3.3: Close 발행 트랜잭션 연결 & 재진입 금지'
type: 'feature'
created: '2026-09-03'
status: 'done'
baseline_revision: 'b115f1cf25b545890d1af348eae0bd6f90547d32'
baseline_commit: 'b115f1cf25b545890d1af348eae0bd6f90547d32'
review_loop_iteration: 0
followup_review_recommended: true
context:
  - '_bmad-output/implementation-artifacts/epic-3-context.md'
warnings: []
deferred: []
---

<intent-contract>

## Intent

**Problem:** Story 3.2의 `emit_open_command` RPC는 아직 어디서도 호출되지 않아, close 배치가 발행되어도 실제 OPEN outcome이 전혀 생성되지 않는다. 또한 candidate/tag 발행과 outcome 생성이 분리되어 있으면 둘 사이에 불일치 상태(발행은 됐는데 outcome은 없음)가 남을 수 있다.
**Approach:** `publish_attempt`를 `batch_kind='close'`일 때만 확장한다 — 같은 serializable 트랜잭션 안에서 이번 attempt의 활성(`status='active'`) `candidate_tags`를 (ticker, strategy)별로 순회하며 각각 `emit_open_command(logical_run_key, ticker, strategy)`를 호출하고, `stage_status.outcome_tracking`을 `success`로 갱신한다. 하나라도 실패하면 함수 전체가 예외로 rollback된다(AD-20). premarket/intraday는 이 로직을 건너뛴다. `get_dashboard_snapshot()`은 close 완료 스냅샷에 `outcome_tracking` section을 추가한다.

## Boundaries & Constraints

**Always:** `publish_attempt`가 `logical_row.batch_kind='close'`일 때만 outcome 생성 루프를 실행한다. 루프는 `candidate_tags`를 `attempt_run_id=p_run_id and status='active'`로 필터링하고 `candidates`와 join해 `ticker`를 얻어, `(ticker, strategy)` 쌍마다 정확히 한 번 `public.emit_open_command(p_logical_run_key, ticker, strategy)`를 호출한다. 이 호출들과 `runs`/`logical_runs` publish 갱신은 모두 `publish_attempt`의 기존 단일 트랜잭션 안에서 일어난다 — 별도 트랜잭션이나 subtransaction을 새로 열지 않는다(하나라도 예외를 내면 함수 전체가 자동 rollback되도록). 루프 완료 후 `stage_status`의 `outcome_tracking` 키를 `success`로 설정한다(`jsonb_set`, 기존 `tags`/`candidates` 갱신 방식과 동일). `get_dashboard_snapshot()`은 `complete_logical.batch_kind='close'`이고 최근 완료 attempt인 경우에만 `sections.outcome_tracking`을 채우고 `missing_sections`/`available_partial_sections`에서 그에 맞게 반영한다.

**Never:** `emit_open_command`(Story 3.2)의 RPC 본문·유니크 인덱스·no-op/replay 로직을 수정하지 않는다 — `publish_attempt`에서 호출만 추가한다. `outcome_observations`나 TP/SL/TIMEOUT 판정(Story 3.4/3.6)을 구현하지 않는다. premarket/intraday의 `publish_attempt` 필수 stage 목록에 `outcome_tracking`을 추가하지 않는다(AD-15 — 이 batch_kind는 `canonical_success_run_id`가 항상 NULL이라 애초에 이 분기를 타지 않는다). `write_stage`를 통한 외부 `outcome_tracking` 갱신 경로를 새로 만들지 않는다 — 이 stage는 오직 `publish_attempt` 내부에서만 설정된다.

## I/O & Edge-Case Matrix

| Scenario | Input / State | Expected Output / Behavior | Error Handling |
|----------|--------------|---------------------------|----------------|
| close 발행, 활성 태그 다수 | `batch_kind='close'` attempt, `candidate_tags`에 status='active' 2건(서로 다른 ticker/strategy), 각 ticker의 해당 거래일 `daily_ohlcv` close 존재 | `publish_attempt` 성공, 각 (ticker,strategy)마다 `outcome_events` OPEN 1행 + `candidate_outcome` 1행 생성, `runs.stage_status.outcome_tracking='success'` | 없음 |
| close 발행, 활성 태그 없음 | `batch_kind='close'` attempt, `candidate_tags` 0건 | `publish_attempt` 성공(빈 루프), outcome 이벤트/행 생성 없이 `outcome_tracking='success'` | 없음 |
| emit_open_command 실패 | 활성 태그 있는 ticker의 해당 거래일 `daily_ohlcv` close 없음 | `publish_attempt` 전체가 예외로 rollback — `runs.status`는 `published`로 바뀌지 않고 `logical_runs.canonical_success_run_id`도 설정되지 않는다 | 예외 전파(`MISSING_DAILY_OHLCV_CLOSE`), candidate/tag 발행도 함께 rollback |
| premarket/intraday 발행 | `batch_kind` in ('premarket','intraday') | outcome 루프를 실행하지 않고 기존 발행 로직만 수행, `outcome_tracking`은 `pending`으로 남음 | 없음 |
| 대시보드 스냅샷 조회 | close 완료 attempt의 `outcome_tracking='success'` | `get_dashboard_snapshot().complete_snapshot.sections.outcome_tracking`에 생성된 OPEN 건수 반영, `missing_sections`에서 `outcome_tracking` 제외 | 없음 |

</intent-contract>

## Code Map

- `infra/supabase/migrations/202609021700_add_tags_to_publish_and_snapshot.sql` -- 현재 `publish_attempt(p_run_id, p_fence_token, p_lease_token)`와 `get_dashboard_snapshot()`의 권위 있는 최신 정의(create or replace 대상 baseline). 이 파일을 그대로 두고 신규 forward migration에서 `create or replace`한다(AD-14, Story 3.2의 `202609031501` 선례).
- `infra/supabase/migrations/202609011600_create_run_lineage.sql:33,42-51` -- `runs.stage_status`에 `outcome_tracking` 키가 이미 스캐폴딩되어 있고(`pending` 기본값, `run_stage_values` 체크가 이미 다섯 stage 모두 검증), `write_stage`(line 124)도 `outcome_tracking`을 유효 stage로 이미 허용한다 -- 스키마 변경 불필요, `publish_attempt` 로직만 확장.
- `infra/supabase/migrations/202609031500_create_emit_open_command.sql` + `202609031501_fix_emit_open_command_review_patch.sql` -- 호출 대상 `public.emit_open_command(p_logical_run_key text, p_ticker text, p_strategy text) returns jsonb`. 반환 `skipped`/`replayed` 키는 무시하고 예외 발생 여부만으로 성공/실패를 판단한다(예외는 자동 propagate).
- `infra/supabase/migrations/202609021600_create_candidate_tags.sql` -- `candidate_tags(candidate_id, attempt_run_id, strategy, status)`, `status='active'`가 이번 attempt에서 유효한 태그. `candidates(candidate_id, attempt_run_id)` 합성키 FK로 join해 `ticker`를 얻는다(`infra/supabase/migrations/202609011700_create_candidates.sql:6-15`).
- `tests/sql/test_run_lineage.sql:6-31` -- 기존 close 발행 시나리오(`close:2099-01-02`)가 `candidate_tags` 없이 `publish_attempt`를 호출한다 -- 빈 루프 케이스가 이 기존 fixture로 이미 회귀 검증됨(수정 불필요, 통과 유지 확인 대상).
- `tests/sql/test_dashboard_snapshot.sql` -- 기존 시나리오는 모두 `premarket`/`intraday`만 사용해 `outcome_tracking`을 건드리지 않는다(missing_sections 3종 그대로 유지 확인). close 성공 시나리오는 신규로 추가한다.
- `.github/workflows/test.yml:108` -- `sql-schema-tests` job fixture 목록에 신규 테스트 파일 추가.
- `packages/read-model/src/database.types.ts` -- 운영 project에 migration 적용 후 Supabase 생성 타입 갱신(`publish_attempt`/`get_dashboard_snapshot` 반환 shape는 시그니처 불변, 내부 jsonb만 변경이라 타입 자체는 영향 없을 수 있음 -- 그래도 갱신해 드리프트를 막는다).

## Tasks & Acceptance

**Execution:**
- `infra/supabase/migrations/202609031600_link_publish_attempt_to_outcome.sql` -- `publish_attempt`를 `create or replace`해 `batch_kind='close'`일 때 `candidate_tags`(status='active', attempt_run_id=p_run_id)를 `candidates`와 join해 (ticker,strategy)별로 `emit_open_command`를 호출하고 `stage_status`에 `outcome_tracking:'success'`를 `jsonb_set`으로 반영하는 로직을 기존 발행 절차 안에 추가; `get_dashboard_snapshot()`도 `create or replace`해 close 완료 attempt의 `outcome_tracking` section(예: OPEN 이벤트 생성 건수)과 `missing_sections`/`available_partial_sections` 갱신을 추가 -- Story 3.2의 idempotent 진입점을 실제 발행 흐름에 연결해 outcome이 생성되지 않는 gap을 없애기 위해서다.
- `tests/sql/test_run_lineage.sql` -- 기존 `close:2099-01-02` 시나리오(태그 없음) 실행 후 `stage_status->>'outcome_tracking'='success'`인지 확인하는 assertion을 추가하고, 활성 태그 1건 이상이 있는 새 close 시나리오를 추가해 `outcome_events`/`candidate_outcome` 생성과 `stage_status.outcome_tracking='success'`를 검증하며, `daily_ohlcv` close 부재로 `emit_open_command`가 실패할 때 `publish_attempt` 전체가 rollback(`runs.status<>'published'`, `canonical_success_run_id` 미설정)됨을 검증하는 시나리오도 추가 -- I/O 매트릭스의 4개 시나리오를 커버하기 위해서다.
- `tests/sql/test_dashboard_snapshot.sql` -- close batch_kind로 발행 + 활성 태그 1건 있는 신규 시나리오를 추가해 `complete_snapshot.sections.outcome_tracking`이 채워지고 `missing_sections`에서 `outcome_tracking`이 빠지는지 검증 -- I/O 매트릭스의 대시보드 시나리오를 커버하기 위해서다.
- `.github/workflows/test.yml:108` -- 목록에 변경 없음(기존 `test_run_lineage.sql`/`test_dashboard_snapshot.sql`을 그대로 사용하므로 신규 파일 추가 없음) -- 확인만 하고 별도 작업 불필요.
- `packages/read-model/src/database.types.ts` -- 운영 project에 migration 적용 후 Supabase 생성 타입으로 갱신 -- 코드와 운영 schema 드리프트를 막기 위해서다.

**Acceptance Criteria:**
- Given close batch_kind의 attempt가 활성 태그를 가진 상태에서, when `publish_attempt`를 호출하면, 같은 트랜잭션 안에서 각 활성 (ticker,strategy)에 대해 `emit_open_command`가 호출되고 `outcome` 관련 projection이 candidate/tag 발행과 함께 커밋된다(AD-20).
- Given close 배치의 필수 stage 목록에 `outcome_tracking`이 포함된 상태에서, when outcome 생성(emit_open_command 호출)이 실패하면, `publish_attempt` 전체 트랜잭션이 rollback되어 candidate/tag 발행도 함께 취소된다(불일치 상태가 남지 않음).
- Given premarket/intraday 배치가 발행되는 경우, when 필수 stage 목록을 확인하면, `outcome_tracking`은 이 batch_kind의 발행 로직에 영향을 주지 않는다(canonical_success_run_id가 애초에 NULL로 고정되므로 이 분기 자체를 타지 않음, AD-15).
- Given close 배치가 완료되어 `stage_status.outcome_tracking='success'`인 경우, when `get_dashboard_snapshot()`을 조회하면, `complete_snapshot.sections`에 `outcome_tracking`이 반영되고 `missing_sections`에서 제외된다.

## Review Triage Log

### 2026-09-03 — Review pass
- intent_gap: 0
- bad_spec: 0
- patch: 3: (high 0high, medium 1medium, low 2low)
- defer: 0
- dismissed:
  - `database.types.ts`가 갱신되지 않았다는 지적(blind-hunter/intent-alignment 중복 제기) — 반증됨: `publish_attempt`/`get_dashboard_snapshot`의 Args/Returns 시그니처는 이 diff로 바뀌지 않았고(둘 다 `Returns: Json`으로 opaque), 실제 파일을 확인한 결과 드리프트가 없다.
  - `(ticker,strategy)` 쌍이 attempt 내에서 중복 호출될 수 있다는 지적 — 반증됨: `candidates`의 `unique(ticker, trading_day, attempt_run_id)`와 `candidate_tags`의 `unique(candidate_id, strategy, attempt_run_id)`가 결합해 한 attempt 안에서 (ticker,strategy) 쌍의 유일성을 이미 transitively 강제하며, `emit_open_command` 자체의 멱등성(Story 3.2)이 방어를 이중화한다.
  - `emit_open_command`의 jsonb 반환값(`skipped`/`replayed`)을 버린다는 지적(blind-hunter/edge-case-hunter 중복 제기) — 스펙의 Code Map에 명시된 의도된 설계다: 이 저장소의 모든 RPC가 실패를 예외로만 신호하는 컨벤션을 따르며, 현재 `publish_attempt`의 반환값에서 태그별 skip 상세를 소비하는 곳이 없다.
  - `outcome_tracking` stage가 다른 stage처럼 `running` 중간 상태를 거치지 않는다는 지적 — 의도된 설계: 이 stage는 `write_stage`를 통한 외부 장시간 배치 단계가 아니라 `publish_attempt` 자신의 트랜잭션 안에서 원자적으로 생성되므로 중단 가능한 중간 상태가 존재하지 않는다.
  - `runs` 테이블에 대한 두 번의 별도 UPDATE를 하나로 합칠 수 있다는 지적 — 이미 잠긴 단일 행에 대한 조기 최적화이며 실측 근거 없음(Story 3.2 리뷰에서 유사 지적을 기각한 선례와 일치).
  - N개의 순차 RPC 호출로 인한 lock 보유 시간/성능 우려 — 실제 성능 문제 근거가 없는 조기 최적화(Story 3.2 리뷰에서 동일 사유로 기각한 선례와 일치).
  - `publish_attempt`에 새 동작을 설명하는 `comment on function`이 없다는 지적 — 기존 컨벤션과 일치: 이전 어떤 migration도 `publish_attempt`에 함수 코멘트를 추가한 적이 없다.
  - `baseline_revision`/`baseline_commit` 프런트매터가 동일 값을 중복 보유한다는 지적 — Story 3.1/3.2와 동일한 스펙 템플릿 컨벤션.
  - intent-alignment 감사의 스프린트 동기화·git 커밋 미실행 관찰 — 코드 결함이 아니라 워크플로 후속 단계(이 Auto Run의 Finalize 단계에서 수행), Story 3.1/3.2와 동일 판단.
  - `has_outcome_tracking`이 배치 종류를 불문한 "가장 최근 완료된 단일 attempt"에만 연동된다는 지적 — Story 1.8/2.5부터 존재한 대시보드 설계이며 이 diff가 새로 만들거나 악화시키지 않았다. 오히려 이 diff가 추가한 `batch_kind='close'` 게이트는 기존에 게이트가 없던 candidates/tags section보다 더 보수적이다.
  - 시나리오 6/7의 `published_at` 강제 설정이 취약하다는 지적 — 기존 파일 컨벤션(시나리오 2~4의 `started_at` 강제 설정)과 동일한 패턴.
  - 태그 lifecycle 전이(해제/재태깅) 엣지 케이스가 테스트되지 않았다는 지적 — intent-contract Never 절 기준 범위 밖(태그 lifecycle은 Story 2.8 소관).
- addressed_findings:
  - `[medium]` `[patch]` 활성 태그가 2개 이상이고 그중 하나는 `emit_open_command`가 성공할 수 있는 상태(종가 존재)이며 다른 하나는 실패하는 상태(종가 없음)일 때, 단일 태그 실패 테스트만으로는 "부분 루프" 전체 unwind(AD-20)를 증명하지 못한다는 지적 — `tests/sql/test_run_lineage.sql`에 `close:2099-01-09` 시나리오를 추가해 먼저 처리되었을 수도 있는 태그의 `outcome_events`/`candidate_outcome` 행도 함께 rollback됨을 검증했다.
  - `[low]` `[patch]` close 발행 + 활성 태그 0건 케이스에서 `get_dashboard_snapshot()`의 `sections.outcome_tracking.open_count`가 명시적으로 0인지(null이나 키 누락이 아닌지) 검증하는 테스트가 없다는 지적 — `tests/sql/test_dashboard_snapshot.sql`에 시나리오 7(`close:2099-02-04`)을 추가해 `open_count` 키 존재·not-null·`=0`을 모두 검증했다.
  - `[low]` `[patch]` premarket 발행 후 `runs.stage_status->>'outcome_tracking'`이 `'pending'`으로 남는지 raw 컬럼으로 직접 검증하는 assertion이 없다는 지적(`missing_sections`를 통한 간접 확인만 존재) — 기존 `premarket:2099-02-01` 시나리오에 직접 assertion을 추가했다.

## Design Notes

`emit_open_command`는 이미 자체적으로 (logical_run_key,ticker,strategy,command_type) 유니크 키로 멱등이고 이미 다른 거래일에 OPEN인 (ticker,strategy)는 no-op으로 방어하므로(Story 3.2), `publish_attempt`에서는 매 활성 태그마다 그냥 호출하기만 하면 된다 -- 재진입 금지는 Story 3.2가 이미 구현했고, 이 스토리는 그 호출부를 트랜잭션에 연결하는 것뿐이다. 루프는 명시적 `for ... in select` cursor loop로 작성하고(이 저장소에 다른 RPC의 명시적 루프 선례는 없지만, plpgsql 표준 패턴이며 각 반복이 예외를 내면 자동으로 전체 함수를 rollback시킨다), `candidate_tags.strategy`는 이미 `('A','B','C')` 체크 제약이 있어 `emit_open_command`의 `INVALID_STRATEGY` 가드에 걸릴 일이 없다.

## Verification

**Commands:**
- `psql -v ON_ERROR_STOP=1 "$DATABASE_URL" -f tests/sql/test_run_lineage.sql` -- expected: 모든 assertion 통과 후 rollback.
- `psql -v ON_ERROR_STOP=1 "$DATABASE_URL" -f tests/sql/test_dashboard_snapshot.sql` -- expected: 모든 assertion 통과 후 rollback.
- `npm run typecheck` -- expected: 갱신된 DB 타입을 소비하는 TypeScript 전체 통과.
- `uv run --with pandas --with numpy --with pyarrow --with pytest pytest` -- expected: 기존 batch/domain 회귀망 통과(baseline에 존재하는 무관한 실패 제외, `tests/batch/test_scheduler.py`의 7건은 Story 3.1/3.2에서도 동일하게 확인된 baseline 실패).
- `git diff --check` -- expected: 공백 오류 없음.

**Manual checks (if no CLI):**
- Supabase MCP로 운영 project에 migration 적용, `publish_attempt`/`get_dashboard_snapshot` 함수 정의 갱신 및 fixture pass 행을 확인한다.
- UI 변경이 없는 DB 전용 스토리이므로 Playwright E2E는 적용 대상이 아니다(Story 3.1/3.2와 동일 판단 -- `get_dashboard_snapshot()`을 소비하는 UI는 아직 존재하지 않는다).

## Auto Run Result

**구현 요약:** 운영 Supabase project(`qqhjeumlecaudsiqhhdu`)에서 `publish_attempt`/`get_dashboard_snapshot`을 `create or replace`했다. `publish_attempt`는 `batch_kind='close'`일 때만, 기존 단일 트랜잭션 안에서 이번 attempt의 활성(`status='active'`) `candidate_tags`를 `candidates`와 join해 (ticker,strategy)별로 `emit_open_command`(Story 3.2)를 호출하고, 완료 후 `stage_status.outcome_tracking`을 `success`로 갱신한다. 호출 중 하나라도 예외를 내면(`MISSING_DAILY_OHLCV_CLOSE` 등) 함수 전체가 rollback되어 candidate/tag 발행도 함께 취소된다(AD-20). premarket/intraday는 이 로직을 건너뛰어 `outcome_tracking`이 `pending`으로 남는다(AD-15). `get_dashboard_snapshot()`은 close 완료 attempt의 `outcome_tracking='success'`일 때만 `sections.outcome_tracking.open_count`(해당 logical_run_key의 OPEN 이벤트 건수)를 채우고 `missing_sections`/`available_partial_sections`에 반영한다.

**변경 파일:**
- `infra/supabase/migrations/202609031600_link_publish_attempt_to_outcome.sql` -- `publish_attempt`에 close 전용 outcome 생성 루프 추가, `get_dashboard_snapshot()`에 `outcome_tracking` section 추가(신규 forward migration, AD-14).
- `tests/sql/test_run_lineage.sql` -- 태그 없는 close 발행의 `outcome_tracking=success` 확인, 활성 태그 2건의 OPEN 이벤트/projection 생성 검증, 종가 부재로 인한 전체 rollback 검증, 그리고 리뷰 후속으로 부분 루프(하나는 성공 가능, 하나는 실패) 전체 unwind 검증 시나리오를 추가.
- `tests/sql/test_dashboard_snapshot.sql` -- close 발행 + 활성 태그 1건의 `outcome_tracking` section 반영 검증(시나리오 6), 리뷰 후속으로 활성 태그 0건의 `open_count=0` 명시적 검증(시나리오 7)과 premarket 발행 후 `outcome_tracking='pending'` raw 컬럼 검증을 추가.
- `packages/read-model/src/database.types.ts` -- 확인만 수행, 변경 없음(Args/Returns 시그니처 불변, Json opaque).
- `.github/workflows/test.yml` -- 확인만 수행, 변경 없음(기존 fixture 파일을 그대로 사용, 신규 파일 추가 없음).

**리뷰 findings 분류:** patch 3건(적용 완료 -- 부분 루프 rollback 테스트[medium], 대시보드 open_count=0 테스트[low], premarket outcome_tracking=pending 직접 검증[low]), defer 0건, dismissed 12건(review triage log 참조 -- database.types.ts 드리프트·(ticker,strategy) 중복 호출·emit_open_command 반환값 무시는 모두 반증되거나 명시된 설계였고, 나머지는 조기 최적화·기존 컨벤션과 일치·워크플로 후속 단계·범위 밖 등으로 기각).

**후속 리뷰 권고:** `true` (patch medium 1건 + low 2건 → 3×1 + 1×2 = 5 ≥ 5).

**검증 수행:**
- Supabase MCP `execute_sql`로 운영 project에서 `tests/sql/test_run_lineage.sql`(리뷰 후속 시나리오 포함, 9개 시나리오)과 `tests/sql/test_dashboard_snapshot.sql`(리뷰 후속 시나리오 포함, 7개 시나리오) 전체를 두 차례(패치 전/후) 직접 실행 -- 모두 통과, `rollback`으로 잔여 행 없음을 확인.
- `npm run typecheck` -- 통과(패치 전/후 각 1회).
- `uv run --with pandas --with numpy --with pyarrow --with pytest pytest` -- 234 passed, 7 failed(모두 `tests/batch/test_scheduler.py`, baseline(b115f1c)에서도 동일하게 실패하는 기존 회귀로 이 스토리와 무관, Story 3.1/3.2에서도 동일하게 확인된 사항).
- `git diff --check` -- 공백 오류 없음(CRLF 관련 무해한 경고만 존재).
- Matrix Test Audit: I/O 매트릭스의 5개 행 모두 실행되어 통과한 테스트로 커버됨을 확인(부분 루프 실패, 대시보드 0건 케이스, premarket raw 컬럼 확인은 리뷰 패치로 보강).
- UI 변경이 없는 DB 전용 스토리라 Playwright E2E는 적용 대상이 아니며 실행하지 않았다(spec 자체 판단과 Story 3.1/3.2 선례 일치).

**잔여 위험:**
- `publish_attempt`의 outcome 생성 루프는 순차적으로 N개의 RPC를 같은 트랜잭션 안에서 호출하므로, 한 close 배치의 활성 태그 수가 매우 커지면 advisory lock 보유 시간이 길어질 수 있다(현재 규모에서는 근거 없는 우려로 기각했으나, 후보 수 상한이 크게 바뀌면 재검토 필요).
- `emit_open_command`의 `skipped`/`replayed` 반환 정보는 `publish_attempt`에서 소비되지 않는다 -- 향후 태그별 발행 결과(신규 OPEN vs 이미 OPEN)를 운영자에게 노출해야 하는 요구가 생기면 이 정보를 집계해 반환값에 포함하는 후속 작업이 필요하다.
- Story 3.1에서 기록된 `skip_attempt` RPC 운영 미적용 건은 이 스토리와 무관하게 여전히 미해결이다(`deferred-work.md` 참조).
