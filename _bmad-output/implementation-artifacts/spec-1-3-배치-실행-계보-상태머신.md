---
title: '배치 실행 계보 상태머신'
type: 'feature'
created: '2026-09-01'
status: 'done'
review_loop_iteration: 0
baseline_revision: '2f2ab869c07b81106b8de6c2e1ef512cf772a270'
baseline_commit: '2f2ab869c07b81106b8de6c2e1ef512cf772a270'
followup_review_recommended: false
context:
  - _bmad-output/implementation-artifacts/epic-1-context.md
  - _bmad-output/specs/spec-wave-double/data-model.md
  - _bmad-output/planning-artifacts/architecture/architecture-wave-double-2026-08-31/ARCHITECTURE-SPINE.md
warnings: []
deferred: []
---

<intent-contract>

## Intent

**Problem:** 배치 실행의 재시도·중첩·stale worker를 판별하고 안전하게 발행할 영속 계보 계약이 없다.

**Approach:** `logical_runs`와 attempt 단위 `runs`, lease/fence 검증 RPC, 5개 stage 상태 레지스트리를 도입한다. 모든 상태 변경과 publication pointer 갱신은 DB transaction/RPC의 권위 아래 둔다.

## Boundaries & Constraints

**Always:** logical key는 close/premarket은 거래일 단위, intraday는 KST 30분 슬롯 단위다. stage 키는 `candidates`, `tags`, `supply_3day`, `market_supply`, `outcome_tracking`로 고정한다. stage는 `pending → running → success|failed|partial`만 전이하며 partial/failed는 완전 발행을 막는다. published 결과와 모든 non-canonical attempt 이력은 보존한다. close만 canonical pointer를 가진다.

**Never:** domain에서 Supabase/SQL/HTTP를 import하지 않는다. stage 결과를 다른 attempt에 쓰거나 stale fence로 덮어쓰지 않는다. reaper의 `ready_to_publish`를 최종 발행으로 간주하지 않는다. Epic 2 이후 stage 구현이나 웹 UI를 구현하지 않는다.

## I/O & Edge-Case Matrix

| Scenario | Input / State | Expected Output / Behavior | Error Handling |
|----------|---------------|----------------------------|----------------|
| START | logical key, trigger | 새 UUID/attempt/fence/lease 발급 | active 실행 충돌은 거부 또는 supersede 규칙 적용 |
| STAGE_WRITE | run, stage, fence/lease, expected status | 소유 attempt의 idempotent 전이 | fence·lease·expected status 불일치 거부 |
| REAP | 만료된 running attempt | 성공 stage 존재 시 salvage ready, 없으면 failed | 다른 active attempt가 있으면 무조건 failed |
| PUBLISH | ready attempt와 fence | candidates success 검증 후 pointer/status 원자 갱신 | partial/failed·권한 불일치면 rollback |

</intent-contract>

## Code Map

- `infra/supabase/migrations/202609011600_create_run_lineage.sql` -- logical/runs 스키마, 제약, 인덱스와 start/stage/heartbeat/reaper/publish RPC의 단일 forward-only 계약.
- `packages/domain/domain/run_state.py` -- 순수 enum/value object, logical key와 stage/status 전이 규칙.
- `packages/domain/domain/stage_registry.py` -- `StageVerifier`와 candidates 기본 verifier 및 후속 stage 확장 registry.
- `apps/batch/run_state.py` -- RPC payload/결과를 batch 포트로 감싸는 Protocol 기반 adapter.
- `tests/domain/test_run_state.py` -- 키 생성, 5개 초기 stage, 허용·금지 전이 단위 테스트.
- `tests/batch/test_run_state.py` -- RPC 인자, fence/lease 오류, 재호출 멱등성 테스트.
- `tests/sql/test_run_lineage.sql` -- migration 계약, publish guard와 동시 start/fence 시나리오를 검증하는 SQL fixture.

## Tasks & Acceptance

**Execution:**
- [x] `infra/supabase/migrations/202609011600_create_run_lineage.sql` -- 스키마와 RPC를 원자적 transaction/제약으로 구현 -- lease/fence와 publication 권위를 DB에 고정한다.
- [x] `packages/domain/domain/run_state.py`, `packages/domain/domain/stage_registry.py` -- 외부 의존성 없는 상태·키·verifier 계약 구현 -- 모든 caller의 stage taxonomy를 통일한다.
- [x] `apps/batch/run_state.py` -- Supabase RPC 호출 경계와 구조화 오류 구현 -- domain과 외부 I/O를 분리한다.
- [x] `tests/domain/test_run_state.py`, `tests/batch/test_run_state.py`, `tests/sql/test_run_lineage.sql` -- 정상·실패·stale·동시성 경로 검증 -- 회귀와 DB-level fence를 고정한다.

**Acceptance Criteria:**
- Given migration을 적용하면, when schema를 조회하면, then `logical_runs`와 모든 runs 컬럼 및 5개 stage 초기 키/제약이 존재한다.
- Given 같은 logical key에 두 start 요청이 동시에 오면, when RPC가 실행되면, then 하나만 active fence를 획득하고 이력은 삭제되지 않는다.
- Given 유효한 run이 stage write를 요청하면, when expected status와 fence/lease가 일치하면, then idempotent 전이가 저장되고 다른 attempt에는 쓰이지 않는다.
- Given fence 또는 lease가 만료·불일치하면, when stage write/heartbeat/publish를 호출하면, then 거부되고 기존 유효 데이터는 변하지 않는다.
- Given heartbeat가 만료되면, when reaper가 실행되면, then salvage 상태를 CAS 처리하되 다른 active attempt가 있으면 failed로 끝난다.
- Given ready attempt의 candidates가 success이면, when `publish_attempt`를 호출하면, then serializable lock 안에서 current pointer와 published 상태가 함께 커밋된다.
- Given 필수 stage가 partial/failed이면, when `publish_attempt`를 호출하면, then rollback되고 complete pointer는 유지되며 partial은 latest partial 이력으로만 남는다.
- Given batch kind가 premarket/intraday이면, when publish가 성공하면, then `canonical_success_run_id`는 NULL이다.

## Design Notes

`lease_token`은 runs의 현재 lease 소유를 증명하는 opaque UUID로 두고, `fence_token`은 attempt 세대의 monotonic bigint으로 분리한다. Epic 1의 필수 stage는 candidates 하나이며 registry의 키 추가가 후속 에픽의 확장 지점이다. RPC 내부에서 logical row를 먼저 잠그고 pointer와 attempt 상태를 같은 transaction에서 갱신한다.

## Verification

**Commands:**
- `uv run --with pytest pytest tests/domain/test_run_state.py tests/batch/test_run_state.py -q` -- expected: all state and adapter tests pass.
- `uv run --with pandas --with numpy --with pyarrow --with pytest pytest backtest -q` -- expected: existing backtest regression suite passes unchanged.
- `npm run build -w apps/web` -- expected: production web build succeeds.
- `git diff --check` -- expected: no whitespace errors.

## Suggested Review Order

**Publication and persistence boundary**

- Logical run locking, attempt fencing, salvage, and atomic publication live in database RPCs.
  [`202609011600_create_run_lineage.sql:76`](../../infra/supabase/migrations/202609011600_create_run_lineage.sql#L76)

- The schema fixes five stage keys, attempt lineage, leases, pointers, and terminal status constraints.
  [`202609011600_create_run_lineage.sql:16`](../../infra/supabase/migrations/202609011600_create_run_lineage.sql#L16)

**Pure state contract**

- Domain code defines KST half-hour keys and forward-only stage transitions without external dependencies.
  [`run_state.py:46`](../../packages/domain/domain/run_state.py#L46)

- The verifier registry leaves later stage implementations as explicit extension points.
  [`stage_registry.py:18`](../../packages/domain/domain/stage_registry.py#L18)

**Batch boundary and verification**

- The gateway keeps Supabase RPC payloads and structured stale-fence errors outside the domain layer.
  [`run_state.py:31`](../../apps/batch/run_state.py#L31)

- Unit and SQL fixtures cover key creation, transitions, RPC arguments, partial state, and publication guards.
  [`test_run_state.py:1`](../../tests/domain/test_run_state.py#L1)
  [`test_run_lineage.sql:1`](../../tests/sql/test_run_lineage.sql#L1)
