---
title: 'Story 4.3: D0 당일 행 attempt별 누적 저장'
type: 'feature'
created: '2026-09-08'
status: 'done'
review_loop_iteration: 0
followup_review_recommended: false
baseline_revision: '004ab00e26ebb7dfba75fd3c2283ff8a68b669fc'
baseline_commit: '004ab00e26ebb7dfba75fd3c2283ff8a68b669fc'
context:
  - 'C:/dev/wave-double/_bmad-output/implementation-artifacts/epic-4-context.md'
warnings: []
deferred: []
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
- `tests/sql/test_supply_3day.sql:241-270` -- 기존 다른 attempt 누적 fixture. D-2 중심 검증을 동일 ticker의 D0 공존·기존 값 보존으로 보강한다.

## Tasks & Acceptance

**Execution:**
- [x] `tests/batch/test_supply_3day_repository.py` -- 서로 다른 attempt의 D0 행이 같은 요청/저장 경계에서 분리되고 동일 attempt 재시도만 멱등 갱신됨을 검증 -- conflict target 회귀 방지.
- [x] `tests/batch/test_supply_stage.py` -- 동일 ticker를 두 attempt로 처리해 각 D0 `SupplyRow`가 서로 다른 `attempt_run_id`로 누적됨을 검증 -- stage 전달 회귀 방지.
- [x] `tests/sql/test_supply_3day.sql` -- 운영 DB에서 동일 ticker·D0의 두 attempt 행 count=2와 첫 attempt 값 보존을 assert하고, D-2/D-1 및 close D0를 정리 대상과 구분하는 계약 주석/검증을 보강 -- 실제 제약 증명.

**Acceptance Criteria:**
- Given 장중 30분 배치가 같은 ticker에 대해 두 attempt로 실행되면, when D0을 저장하면, then 두 `attempt_run_id`의 D0 행이 모두 존재하고 첫 행의 값은 두 번째 저장으로 바뀌지 않는다.
- Given 동일 attempt가 네트워크 재시도로 다시 저장되면, when 같은 `(candidate_id, trading_day, attempt_run_id)`를 upsert하면, then 중복 행은 생기지 않고 최신 해당 attempt payload만 반영된다.
- Given 하루 D0 이력을 조회하면, when `trading_day`와 ticker 기준으로 attempt를 정렬하면, then 09:30·10:00·10:30에 해당하는 각 attempt 행을 재구성할 수 있다.
- Given 보존 정책을 적용할 때, when 정리 대상을 판정하면, then 장중 D0만 잠정 90일 정리 후보이고 D-2/D-1 및 종가 확정 D0는 별도 보존 기준으로 남는다는 계약이 문서와 fixture에 명시된다.

## Spec Change Log

## Review Triage Log

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
- `git diff --check` -- 공백 오류가 없다.

**Manual checks (if no CLI):**
- 운영 Supabase MCP에서 migration 목록·`supply_3day` 제약/RLS를 확인하고, rollback 가능한 fixture로 서로 다른 attempt의 동일 ticker/D0 count=2와 기존 값 보존을 명시적으로 확인한다.

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
