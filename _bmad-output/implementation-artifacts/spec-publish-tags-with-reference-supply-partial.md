---
title: '수급 부분실패와 무관한 태깅 후보 발행'
type: 'feature'
created: '2026-09-29'
status: 'done'
review_loop_iteration: 0
baseline_commit: '74097a4d05c240bbe39357d902973cc505def508'
context: ['C:/dev/wave-double/AGENTS.md']
---

<frozen-after-approval reason="human-owned intent — do not modify unless human renegotiates">

## Intent

**Problem:** 후보 태깅은 정상 완료됐지만 `supply_3day` 또는 `market_supply`의 부분/전체 실패가 배치 발행을 막아 대시보드가 이전 태깅 결과에 머문다. 수급은 태깅 자격의 필수 입력이 아니라 후보 판단을 돕는 참고값이다.

**Approach:** candidates와 tags가 성공하면 수급 stage가 `success`, `partial`, `failed`여도 해당 attempt를 발행한다. 수급 데이터가 없는 종목·시장은 기존 결측/판정불가 경계를 유지하고, 수급 오류 자체는 stage 결과와 대시보드 최신 상태에 계속 노출한다.

## Boundaries & Constraints

**Always:** 후보 모집단(candidates)은 성공이어야 한다. tags stage는 성공이어야 한다. 수급 stage는 계속 실행하고 오류·미처리 종목을 `stage_results`에 남긴다. close 발행의 outcome은 태그와 기존 OHLCV/outcome 계약만 사용한다. forward-only migration만 추가한다.

**Never:** 수급 오류를 성공으로 위장하거나 수급 결측을 `good`/`not_met`로 판정하지 않는다. candidates partial/failed 또는 tags partial/failed를 발행 허용 대상으로 확대하지 않는다. 기존 applied migration을 수정하지 않는다.

## I/O & Edge-Case Matrix

| Scenario | Input / State | Expected Output / Behavior | Error Handling |
|----------|--------------|---------------------------|----------------|
| SUPPLY_PARTIAL | candidates success, tags success, supply/market partial | publish_attempt 성공, current_complete_run_id가 최신 attempt로 이동, 수급 결측은 그대로 표시 | batch 결과는 partial과 원래 result_code를 유지 |
| SUPPLY_FAILED | candidates success, tags success, supply 또는 market failed | 태깅 후보 발행, supply/market stage 실패 정보 유지 | 후보 카드의 수급은 판정불가/결측 경계 적용 |
| TAGS_PARTIAL | candidates success, tags partial | 발행하지 않음 | 기존 partial 경계 유지 |
| CANDIDATES_PARTIAL | candidates partial | 발행하지 않음 | 기존 모집단 누락 방지 |

</frozen-after-approval>

## Code Map

- `apps/batch/scheduler.py` -- `run_scheduled_batch()`의 publish 게이트가 현재 supply/market success까지 요구한다. candidates 결과와 tags 결과를 기준으로 게이트를 분리한다.
- `tests/batch/test_scheduler.py` -- intraday/close publish 및 partial supply 회귀 테스트를 추가하고 기존 candidates/tags 실패 비발행 테스트를 보존한다.
- `infra/supabase/migrations/202609211000_exclude_strategy_i_from_publish_outcome.sql` -- 운영 `publish_attempt`의 현재 함수 기준본. 수급/시장수급 success guard를 제거한 forward-only 함수 migration을 추가한다.
- `infra/supabase/migrations/202609081000_create_market_supply.sql` 및 `202609070900_supply_3day_publish_guard.sql` -- 기존 수급 발행 가드와 snapshot 계약의 의도·함수 shape를 확인하는 참고 기준이다.
- `apps/web/app/page.tsx`, `apps/web/lib/dashboard-types.ts` -- published attempt의 tags/candidate는 렌더하고 수급 section 부재를 기존 결측/판정불가 UI로 처리하는 경계를 확인한다.

## Tasks & Acceptance

**Execution:**
- [x] `apps/batch/scheduler.py` -- candidates success + tags success를 발행 최소조건으로 조정하고 supply/market 상태는 결과·관측값으로만 유지한다.
- [x] `tests/batch/test_scheduler.py` -- supply partial/failed publish 허용과 candidates/tags 실패 비발행을 검증한다.
- [x] `infra/supabase/migrations/202609291800_publish_tags_without_supply_success.sql` -- 최신 `publish_attempt`를 보존하면서 supply/market success guard만 제거한다.
- [x] `apps/web` 관련 타입/테스트 -- 기존 카드 조회 경계가 tags만으로 published 후보를 렌더하는지 확인하고, 수급 결측을 정상값으로 추정하지 않는 운영 fixture로 검증한다. 소스 변경은 필요하지 않았다.

**Acceptance Criteria:**
- Given candidates와 tags가 success이고 supply_3day가 partial/failed일 때, when 배치가 종료되면, then publish_attempt가 성공하고 최신 태깅 후보가 대시보드에 노출된다.
- Given candidates 또는 tags가 partial/failed일 때, when 배치가 종료되면, then publish_attempt를 호출하지 않는다.
- Given published attempt의 수급 section이 없을 때, when 카드가 렌더되면, then 수급을 정상값으로 추정하지 않고 결측/판정불가로 표시한다.

## Spec Change Log

## Review Triage Log

- [patch] 1차 리뷰가 지적한 domain/SQL 불일치: domain `can_publish()`도 reference supply가 pending/running이면 false가 되도록 맞추고, migration이 기존 supply success guard를 남긴 채 통과하지 않도록 보존 검사를 추가했다.
- [patch] close 후속 outcome과 partial/failed stage 결과 보존이 직접 검증되지 않음: 운영 rollback fixture에 close `candidate_outcome`, `outcome_events`, `outcome_tracking`, `stage_status`, `stage_results` 검증을 추가했다.
- [dismissed] 신규 diff가 잘렸다는 지적은 코드가 아니라 1차 리뷰용 임시 diff 생성 오류였고, 신규 파일 전체를 포함한 올바른 unified diff로 재생성했다.
- [dismissed] premarket 직접 RPC 발행 가능성은 기존 SQL 계약상 premarket 발행 fixture가 존재하고, 실제 scheduler는 `BatchKind`로 premarket publish를 호출하지 않는다. 이번 변경의 close/intraday scheduler 경계를 벗어난다.
- [dismissed] CLI가 reference stage 실패 시 non-zero를 반환한다는 지적은 stage 실패와 태깅 발행 성공을 동시에 보존하려는 명시적 결과 계약과 일치한다. 수급 오류를 숨기는 수정은 하지 않는다.
- [dismissed] evidence/hint/market RPC가 supply success가 아니면 정상값을 반환하지 않는다는 지적은 기존 결측/판정불가 경계이며, 새 fixture도 failed stage에서 정상 수급값을 노출하지 않는 것을 확인한다.
- [defer] optional market adapter 누락 시 호환성 fake 경로가 pending stage를 남길 수 있다는 지적은 production CLI가 항상 세 adapter를 주입하는 기존 경로의 별도 정리 과제다.
- [defer] published partial snapshot의 운영 `get_dashboard_snapshot()` section/UI/E2E 경계 검증은 production snapshot 함수 drift를 먼저 해결해야 한다. 이번 feature fixture는 pointer, card RPC, reference read RPC를 검증했다.
- [defer] partial 상태에서 수집된 일부 수급 행을 success와 함께 노출하는 read-model 확장은 현재 RPC의 기존 all-or-nothing 경계 변경이므로 별도 요구사항으로 분리한다.
- [dismissed] successful market snapshot 회귀가 새 fixture에서 제거됐다는 지적은 `tests/sql/test_market_supply.sql` 운영 실행이 통과했고, 기존 success contract는 별도 fixture로 유지된다.
- [dismissed] candidates/tags 실패의 database RPC 직접 fixture가 없다는 지적은 migration 보존 검사와 Python scheduler 회귀망으로 필수 게이트를 확인하며, 이번 변경은 해당 게이트의 완화를 하지 않는다.

## Design Notes

발행 성공과 데이터 완전성은 분리한다. 이번 변경에서 `published`는 태깅 후보를 사용할 수 있다는 뜻이며, 수급 완전성은 각 stage status와 UI 결측 상태가 표현한다. close outcome 발행은 수급에 의존하지 않으므로 태그가 확정된 후보의 후속 추적도 막지 않는다.

## Verification

**Commands:**
- `uv run --with pytest pytest tests/batch/test_scheduler.py -q` -- scheduler 회귀가 모두 통과한다.
- `uv run --with pytest pytest tests/batch/test_candidate_stage.py tests/batch/test_tags_stage.py -q` -- 후보/태깅 실패 경계가 유지된다.
- `uv run --with pytest pytest tests/batch/test_scheduler.py tests/batch/test_candidate_stage.py tests/batch/test_tags_stage.py tests/domain/test_run_state.py -q` -- 96개 통과.
- `git diff --check` -- 새 migration과 코드에 whitespace 오류가 없다.
- `python tools/check_migration_order.py` -- 기존 `202609161200` 중복으로 실패했다. 이번 migration이 추가한 오류가 아니다.
- 운영 Supabase에서 migration 적용 후 `publish_attempt` 카탈로그 가드 제거를 확인했다.
- 운영 rollback fixture와 `tests/sql/test_publish_tags_without_supply.sql`을 실행해 candidates/tags success + supply partial + market failed 상태가 발행되고 카드로 노출됨을 확인했다.
- `tests/sql/test_market_supply.sql`은 운영에서 통과했다. 기존 `tests/sql/test_supply_3day_publish_guard.sql`은 운영 `get_dashboard_snapshot()`이 tags/supply section을 반환하지 않는 사전 drift 때문에 snapshot 시나리오에서 실패했다.

## Suggested Review Order

**발행 경계**

- candidates/tags 성공만 태깅 발행을 허용하고 수급 terminal 상태를 보조 가드로 둔다.
  [`scheduler.py:366`](../../apps/batch/scheduler.py#L366)

- 운영 RPC는 수급 success 가드를 제거하되 pending/running과 핵심 안전 가드를 보존한다.
  [`202609291800_publish_tags_without_supply_success.sql:10`](../../infra/supabase/migrations/202609291800_publish_tags_without_supply_success.sql#L10)

- domain helper도 SQL과 동일하게 수급 진행 중 발행을 막고 partial/failed를 허용한다.
  [`run_state.py:58`](../../packages/domain/domain/run_state.py#L58)

**검증 경계**

- close 발행에서 outcome 생성과 reference stage 결과 보존을 운영 rollback fixture로 검증한다.
  [`test_publish_tags_without_supply.sql:59`](../../tests/sql/test_publish_tags_without_supply.sql#L59)

- scheduler partial supply와 candidates/tags 실패 경계를 회귀 테스트로 고정한다.
  [`test_scheduler.py:554`](../../tests/batch/test_scheduler.py#L554)

- domain 상태 판정이 필수 태깅과 참고 수급을 구분하는지 확인한다.
  [`test_run_state.py:45`](../../tests/domain/test_run_state.py#L45)
