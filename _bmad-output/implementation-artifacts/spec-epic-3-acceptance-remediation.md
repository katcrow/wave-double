---
title: 'Epic 3 운영 수용 게이트 복구 및 후속 범위 정리'
type: 'feature'
created: '09-04-2026'
status: 'done'
review_loop_iteration: 0
context:
  - 'C:/dev/wave-double/_bmad-output/implementation-artifacts/epic-3-retro-09-04-2026.md'
  - 'C:/dev/wave-double/_bmad-output/implementation-artifacts/epic-3-context.md'
---

<frozen-after-approval reason="human-owned intent — do not modify unless human renegotiates">

## Intent

**Problem:** Epic 3 구현은 저장소에 존재하지만 운영 Supabase에 3.2~3.10 실행 계약이 적용되지 않아 실전 outcome 자동 적재를 증명할 수 없다. 또한 GitHub 알림과 자동 DELISTED는 후속 작업으로 최대한 늦춘다.

**Approach:** 운영 project에 현재 저장소 migration을 순서대로 적용하고 실제 fixture·function grant·RLS/catalog를 검증한다. local/production migration drift를 차단하는 gate와 correction/rebuild 경계 회귀를 보강하며, GitHub 알림·자동 DELISTED는 이번 수용 범위에서 제외하고 후속 backlog로 명시한다.

## Boundaries & Constraints

**Always:** 운영 project `qqhjeumlecaudsiqhhdu`만 사용한다. migration은 AD-14 순서로 적용한다. outcome_events/outcome_observations는 append-only, candidate_outcome은 guarded mutation, service_role 전용 RPC 원칙을 유지한다. 운영 DDL 적용 후 명시적 pass 결과와 migration/catalog/grant 증거를 남긴다. 기존 dirty worktree의 unrelated 변경은 보존하고 이번 변경 파일만 커밋한다.

**Never:** GitHub Issue 생성/close/escalation을 구현하지 않는다. LS 상태 기반 자동 DELISTED 감지를 구현하지 않는다. 기존 Epic 3 outcome 데이터가 있다면 삭제·재작성하지 않는다. production migration을 fixture 검증 없이 완료로 표시하지 않는다.

## I/O & Edge-Case Matrix

| Scenario | Input / State | Expected Output / Behavior | Error Handling |
|----------|--------------|----------------------------|----------------|
| production apply | 3.1 이후 local migration 순서 | 모든 migration 등록, RPC/function grant 존재 | 실패 migration에서 중단·원인 기록 |
| replay/idempotency | 동일 OPEN/observation/correction/rebuild 재시도 | 중복 event 없음, projection 정합 유지 | 명시적 fixture pass/fail |
| correction conflict | null/stale version, 빈 reason, unique 충돌 | 도메인 오류와 rollback | raw mutation 없음 |
| deferred scope | SUSPENDED/DELISTED 상태 | 수동 correction 경계만 유지 | 알림/자동감지는 후속 action |

</frozen-after-approval>

## Code Map

- `infra/supabase/migrations/202609031400_harden_outcome_schema_invariants.sql`~`202609051200_create_rebuild_outcome_projection.sql` -- 운영에 반영할 Epic 3 forward migration 권위 집합.
- `tests/sql/test_outcome_schema.sql`, `tests/sql/test_outcome_open_command.sql`, `tests/sql/test_run_lineage.sql`, `tests/sql/test_outcome_rebuild.sql` -- 실제 DB contract와 replay 회귀 fixture.
- `.github/workflows/test.yml:65-110` -- local PostgreSQL migration/fixture 실행 및 parity gate를 추가할 위치.
- `apps/batch/scheduler.py` -- close 성공 시 `publish_attempt`를 호출하는 현재 배선; alerts는 이번 범위에서 소비하지 않는다.
- `_bmad-output/planning-artifacts/epics.md:904-1045` -- 상위 acceptance에서 후속으로 제외할 GitHub/자동 DELISTED 범위.
- `_bmad-output/implementation-artifacts/epic-3-retro-09-04-2026.md` -- rejected 판정과 action item을 해결 상태로 갱신할 회고 기록.

## Tasks & Acceptance

**Execution:**

- [x] remediation spec과 회고에 GitHub 알림·자동 DELISTED 후속 범위를 기록한다 -- 이번 수용의 핵심 경계를 유지한다.
- [x] Epic 3 migration을 production에 적용한다 -- 실제 실행 계약을 복구한다.
- [x] Supabase MCP로 RPC/function grant/catalog와 SQL fixture를 검증한다 -- 로컬 테스트와 운영 증거를 분리한다.
- [x] migration order gate와 run-lineage explicit pass 회귀를 추가한다 -- 순서 drift와 빈 결과셋 오인을 줄인다.
- [x] 회고 verdict/action status를 갱신하고 변경 파일만 커밋한다 -- 수용 상태와 추적 상태를 일치시킨다.

**Acceptance Criteria:**

- Given production migration history, when Epic 3 migrations are applied, then all intended RPCs and service_role-only grants exist in `qqhjeumlecaudsiqhhdu`.
- Given production fixtures, when the outcome schema, OPEN, publish, correction, DELISTED boundary, and rebuild contracts run in rollback transactions, then each emits an explicit pass result and leaves no fixture rows.
- Given the same local migration set and production history, when the parity gate runs, then missing migration/RPC/grant fails the gate before deployment.
- Given the deferred notification scope, when Epic 3 is evaluated, then GitHub alerting and automatic DELISTED detection are recorded as follow-up work and do not block this slice.

## Spec Change Log

## Review Triage Log

## Design Notes

Production migration application is an authorized operational step under the repository policy, but verification must happen after each ordered migration. The deferred notification decision does not remove SUSPENDED/DELISTED projection states or manual correction; it only postpones external alert automation and automatic LS-status detection.

## Verification

**Commands:**

- `uv run --with pandas --with numpy --with pyarrow --with pytest pytest` -- expected: all Python tests pass.
- `npm test` -- expected: all web tests pass.
- `npm run typecheck` and `npm run build` -- expected: pass.
- Supabase MCP migration/catalog/grant/fixture queries -- expected: explicit production pass evidence.
