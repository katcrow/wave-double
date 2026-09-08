---
title: 'Story 4.3: D0 당일 행 attempt별 누적 저장'
type: 'feature'
created: '2026-09-08'
status: 'done'
review_loop_iteration: 0
followup_review_recommended: true
baseline_revision: '004ab00e26ebb7dfba75fd3c2283ff8a68b669fc'
baseline_commit: '004ab00e26ebb7dfba75fd3c2283ff8a68b669fc'
context:
  - 'C:/dev/wave-double/_bmad-output/implementation-artifacts/epic-4-context.md'
warnings: [oversized]
deferred:
  - summary: >-
      D0 장중 90일 cleanup 실행 배치와 실제 eligible-row 삭제 검증은 후속 운영 작업으로 남긴다.
    evidence: |-
      현재 supply_3day에는 보존 기준 주석과 attempt별 저장 계약만 있고 cleanup RPC/cron은 없다. 이번 스토리의 Never 규칙도 새 90일 삭제 배치를 제외한다.
    location: >-
      infra/supabase/migrations/202609022000_create_supply_3day.sql:43
    severity: medium
---

<intent-contract>

## Intent

**Problem:** 장중 배치가 반복될 때 D0 수급 행이 같은 종목의 이전 관측을 잃지 않고 attempt별로 남아야 한다. 현재 저장 경계는 해당 구조를 갖추고 있으나 D0 기준의 반복 배치 회귀와 보존 기준이 충분히 고정되어 있지 않다.

**Approach:** 기존 `UNIQUE (candidate_id, trading_day, attempt_run_id)` 및 `attempt_run_id` conflict target을 유지하고, 서로 다른 attempt의 동일 ticker/D0 행 공존과 같은 attempt 재실행의 멱등성을 Python·SQL fixture로 검증한다. D0 장중 이력, D-2/D-1, 종가 확정 D0의 정리 기준도 계약으로 문서화한다.

## Boundaries & Constraints

**Always:** 모든 supply 행은 해당 배치의 `attempt_run_id`를 가진다. 서로 다른 attempt의 동일 ticker와 D0 거래일 값은 모두 보존한다. 동일 attempt 재시도만 같은 자연키에서 멱등 갱신한다. `slot`, 합성 FK, RLS, 기존 supply stage/publish gate와 A~F 태그 소비 계약을 유지한다.

**Never:** `candidate_id` 또는 `trading_day`만 conflict 기준으로 사용하지 않는다. 기존 migration을 수정하거나 D0 이력을 ticker별 단일 행으로 압축하지 않는다. 이번 스토리에서 UI·시장 수급·새로운 90일 삭제 배치를 구현하지 않는다.

</intent-contract>

## Code Map

- `infra/supabase/migrations/202609022000_create_supply_3day.sql:9-43` -- `attempt_run_id` 포함 유일키, candidates 합성 FK, D0 누적·정리 대상 주석의 원본 저장 계약. 읽기 전용.
- `apps/batch/supply_3day_repository.py:16-97` -- `SupplyRow`의 attempt 귀속과 `on_conflict=candidate_id,trading_day,attempt_run_id` 멱등 upsert 경계.
- `apps/batch/supply_stage.py:149-205` -- tagged candidate에서 D-2/D-1/D0 행을 만들고 현재 attempt `run_id`를 모든 행에 주입하는 경로.
- `apps/batch/scheduler.py:189-221` -- intraday/close에 scheduler의 새 attempt run id를 supply stage로 전달하는 배선; premarket 제외 계약 유지.
- `tests/batch/test_supply_3day_repository.py:35-119` -- REST conflict target·payload·재시도 저장소 테스트.
- `tests/batch/test_supply_stage.py` -- stage가 생성하는 세 슬롯과 attempt 귀속을 검증하는 단위 테스트 경계.
- `tests/sql/test_supply_3day.sql:289-385` -- 동일 ticker의 세 intraday attempt가 D-2/D-1/D0를 모두 누적하고 정확한 시각·값을 보존하는 운영 fixture.

## Tasks & Acceptance

**Execution:**
- [x] `tests/batch/test_supply_3day_repository.py` -- 서로 다른 attempt의 D0 행이 같은 요청/저장 경계에서 분리되고 동일 attempt 재시도만 멱등 갱신됨을 검증 -- conflict target 회귀 방지.
- [x] `tests/batch/test_supply_stage.py` -- 동일 ticker를 두 attempt로 처리해 각 D0 `SupplyRow`가 서로 다른 `attempt_run_id`로 누적됨을 검증 -- stage 전달 회귀 방지.
- [x] `tests/sql/test_supply_3day.sql` -- 운영 DB에서 동일 ticker·D-2/D-1/D0의 세 intraday attempt 행 count=3과 첫 attempt 값 보존을 assert하고, 정리 기준 계약 주석/검증을 보강 -- 실제 제약 증명.

**Acceptance Criteria:**
- Given 장중 30분 배치가 같은 ticker에 대해 두 attempt로 실행되면, when D0을 저장하면, then 두 `attempt_run_id`의 D0 행이 모두 존재하고 첫 행의 값은 두 번째 저장으로 바뀌지 않는다.
- Given 동일 attempt가 네트워크 재시도로 다시 저장되면, when 같은 `(candidate_id, trading_day, attempt_run_id)`를 upsert하면, then 중복 행은 생기지 않고 최신 해당 attempt payload만 반영된다.
- Given 하루 D0 이력을 조회하면, when `trading_day`와 ticker 기준으로 attempt를 정렬하면, then 09:30·10:00·10:30에 해당하는 각 attempt 행을 재구성할 수 있다.
- Given 보존 정책을 적용할 때, when 정리 대상을 판정하면, then 장중 D0만 잠정 90일 정리 후보이고 D-2/D-1 및 종가 확정 D0는 별도 보존 기준으로 남는다는 계약이 문서와 fixture에 명시된다.

## Spec Change Log

## Review Triage Log

### 2026-09-08 — Review pass
- intent_gap: 0
- bad_spec: 0
- patch: 6: (high 0, medium 3, low 3)
- defer: 1: (high 0, medium 1, low 0)
- dismissed:
  - `SupplyRow.as_db_row()`가 재시도 때 `collected_at`을 갱신한다는 지적 — collected_at은 최신 payload의 실제 수집 시각이며, 동일 attempt 재저장은 최신 payload를 반영하는 멱등 upsert라는 명세와 일치한다.
  - repository 단위 테스트의 in-memory handler가 PostgREST conflict 동작을 흉내 낸다는 지적 — 해당 테스트의 책임은 HTTP payload/conflict target이고, 실제 UNIQUE 제약은 운영 Supabase fixture에서 별도로 확인했다.
  - stage 테스트의 FakeSupplyRepo가 실제 repository upsert를 실행하지 않는다는 지적 — stage 행 조립과 repository conflict 동작은 서로 다른 경계이며 둘 다 각각의 테스트와 운영 SQL fixture로 검증했다.
  - 동일 attempt를 stage 전체에서 재실행하는 테스트가 없다는 지적 — 동일 자연키 멱등성은 repository/SQL fixture에서 직접 검증하며 stage는 attempt 귀속을 검증하는 표면이다.
  - scheduler의 09:30/10:00 logical key 전용 테스트가 없다는 지적 — scheduler의 기존 key 생성·supply 배선 테스트가 존재하고, 이번 변경은 scheduler 코드를 바꾸지 않았으며 SQL fixture가 정확한 intraday key를 사용한다.
  - repository 테스트에 ticker 필드가 없다는 지적 — ticker 기준 동일 종목 공존은 stage 테스트와 운영 SQL fixture에서 검증한다.
  - 모든 investor 필드와 status를 모든 후속 attempt에 반복 assert하지 않는다는 지적 — 첫 attempt의 전체 payload 보존과 각 후속 attempt의 D0 존재·식별·시간을 assert하며 AC의 보존 조건을 충족한다.
  - missing→confirmed 이외 상태 전환 재시도가 없다는 지적 — 명세는 최신 해당 attempt payload의 멱등 반영을 요구할 뿐 특정 상태 전환을 제한하지 않는다.
  - attempt 정렬의 안정적 키가 없다는 지적 — 각 행의 attempt_run_id가 identity이고 collected_at은 관측 순서를 제공하며 fixture가 09:30/10:00/10:30을 명시적으로 assert한다.
  - SQL fixture에 별도 실행 명령이 없다는 지적 — 수정된 fixture 파일 자체를 운영 Supabase MCP execute_sql로 실행해 pass row를 확인했다.
  - 운영 검증 결과가 diff에 없다는 지적 — 실행 결과와 schema/advisor 확인을 아래 Auto Run Result에 기록했다.
  - 의도 정합성 리뷰의 커밋·done 미확인 지적 — 리뷰 시점에는 아직 최종화 전이었고, 이 pass의 후속 finalization에서 처리한다.
- addressed_findings:
  - `[medium] [patch] 반복 저장 SQL fixture가 close/다른 trading_day를 사용하던 문제를 동일 거래일의 09:30/10:00/10:30 intraday attempt로 수정했다.`
  - `[medium] [patch] cross-attempt D-2/D-1 검증이 제거되어도 통과하던 공백을 세 슬롯 count=3 assertion으로 보강했다.`
  - `[medium] [patch] 원본 D0 scalar SELECT의 NULL 비교 취약성을 not exists와 전체 payload assertion으로 교체했다.`
  - `[low] [patch] 누적 행이 임의의 세 attempt로 채워지는 것을 막도록 기대한 세 attempt의 exact existence를 assert했다.`
  - `[low] [patch] rollback 이후에도 pass row가 출력될 수 있던 fixture 순서를 pass select 후 rollback으로 변경했다.`
  - `[low] [patch] Code Map line anchor·fixture task count·프로젝트 필수 full-suite 의존성 기록을 현재 산출물과 일치시켰다.`

### 2026-09-08 — 직접 리뷰 보완

- intent_gap: 0
- bad_spec: 0
- patch: 1
- defer: 0
- dismissed: 0
- addressed_findings:
  - 보존 정책이 migration 주석과 spec에는 있었지만 SQL fixture에 직접 명시되지 않아, D-2/D-1·종가 확정 D0·장중 D0의 구분 주석을 추가했다.

## Design Notes

`candidate_id`는 candidates의 전역 키라서 재실행 attempt마다 새 값이 발급된다. 따라서 “같은 종목”의 누적은 candidates의 ticker와 supply 행의 서로 다른 attempt/candidate 조합으로 검증한다. 동일 attempt의 재저장은 append가 아니라 idempotent upsert로 허용하며, 이것이 재시도 중복을 막는 경계다. 이번 스토리는 삭제 작업을 추가하지 않고, 향후 cleanup이 batch kind와 D0 확정 여부를 판별할 수 있도록 기존 주석·fixture 계약을 보존한다.

## Verification

**Commands:**
- `uv run --with pytest pytest tests/batch/test_supply_3day_repository.py tests/batch/test_supply_stage.py -q` -- 신규 attempt/D0 회귀와 기존 stage 저장 테스트가 모두 통과한다.
- `uv run --with pytest pytest tests/ -q` -- 전체 Python 회귀가 통과한다.
- `uv run --with pandas --with numpy --with pyarrow --with pytest pytest` -- 프로젝트 규정 의존성을 포함한 전체 backtest/Python 회귀가 통과한다.
- `git diff --check` -- 공백 오류가 없다.

**Manual checks (if no CLI):**
- 운영 Supabase MCP에서 migration 목록·`supply_3day` 제약/RLS를 확인하고, rollback 가능한 fixture로 서로 다른 attempt의 동일 ticker/D0 count=3과 기존 값 보존을 명시적으로 확인한다.

## Auto Run Result

- Summary: 기존 attempt-scoped supply 저장 계약을 유지하면서 동일 ticker의 반복 intraday D0 이력과 전체 3슬롯 누적을 회귀 테스트·운영 SQL fixture로 고정했다. 동일 attempt 재시도는 중복 없이 최신 payload를 반영한다.
- Files changed:
  - `tests/batch/test_supply_3day_repository.py` -- 서로 다른 attempt D0 공존과 동일 attempt 멱등 upsert 테스트.
  - `tests/batch/test_supply_stage.py` -- 동일 ticker 두 attempt의 D0 행과 attempt 귀속 테스트.
  - `tests/sql/test_supply_3day.sql` -- 동일 거래일 3개 intraday attempt, D-2/D-1/D0 누적, 전체 값 보존, 제약/RLS fixture.
  - `_bmad-output/implementation-artifacts/sprint-status.yaml` -- Story 4.3 진행 상태 동기화.
  - `_bmad-output/implementation-artifacts/spec-4-3-d0-당일-행-attempt별-누적-저장.md` -- 구현·리뷰·검증 결과.
- Review findings breakdown: patch 6건(중간 3, 낮음 3) 적용, cleanup 배치 1건(중간) deferred, 나머지는 각 사유와 함께 dismissed 기록.
- Follow-up review recommendation: true (patched: high 0, medium 3, low 3; score 12).
- Verification:
  - `uv run --with pytest pytest tests/batch/test_supply_3day_repository.py tests/batch/test_supply_stage.py -q`: 22 passed.
  - `uv run --with pytest pytest tests/ -q`: 261 passed.
  - `uv run --with pandas --with numpy --with pyarrow --with pytest pytest -q`: 413 passed in 60.65s.
  - `python -m compileall -q apps/batch tests/batch`: pass.
  - `git diff --check`: pass.
  - 운영 Supabase MCP `list_migrations`에서 supply migration 적용 이력, `list_tables`에서 `supply_3day` attempt_run_id/UNIQUE 대상·RLS 활성 상태를 확인했다. `get_advisors(security)`의 기존 trading_calendar RLS 경고와 deny-all 테이블 정보도 확인했으며 이번 story 범위 밖이라 수정하지 않았다.
  - 수정된 `tests/sql/test_supply_3day.sql` 전체를 운영 Supabase MCP `execute_sql`로 실행해 `story_4_3_d0_attempt_accumulation: pass`를 확인했다. transaction은 rollback으로 정리됐다.
  - UI 변경이 없는 batch/DB fixture 스토리이므로 Playwright E2E는 실행하지 않았다.
- Residual risks: D0 90일 cleanup 실행 배치와 close D0 보존 판정 로직은 deferred이며, 후속 운영 story에서 구현·fixture 검증이 필요하다.

## Suggested Review Order

**저장 계약과 멱등성**

- attempt를 포함한 유일키와 D0 보존 정책의 원본 계약입니다.
  [`202609022000_create_supply_3day.sql:23`](../../infra/supabase/migrations/202609022000_create_supply_3day.sql#L23)

- REST upsert conflict target이 attempt별 자연키를 그대로 사용합니다.
  [`supply_3day_repository.py:84`](../../apps/batch/supply_3day_repository.py#L84)

**배치 attempt 전파**

- stage가 모든 공급 행에 현재 run의 attempt ID를 주입합니다.
  [`supply_stage.py:149`](../../apps/batch/supply_stage.py#L149)

- close/intraday만 supply stage로 연결해 premarket 계약을 보존합니다.
  [`scheduler.py:209`](../../apps/batch/scheduler.py#L209)

**회귀 및 운영 증명**

- 저장소 mock이 서로 다른 attempt 누적과 동일 attempt 최신값 갱신을 검증합니다.
  [`test_supply_3day_repository.py:113`](../../tests/batch/test_supply_3day_repository.py#L113)

- stage가 동일 ticker의 두 D0 행과 각 attempt 값을 보존하는지 검증합니다.
  [`test_supply_stage.py:243`](../../tests/batch/test_supply_stage.py#L243)

- 운영 DB에서 멱등성·D0 시계열·보존 계약을 rollback fixture로 검증합니다.
  [`test_supply_3day.sql:289`](../../tests/sql/test_supply_3day.sql#L289)
