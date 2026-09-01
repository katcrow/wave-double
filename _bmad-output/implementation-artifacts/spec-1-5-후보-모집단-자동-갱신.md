---
title: '후보 모집단 자동 갱신'
type: 'feature'
created: '2026-09-01'
status: 'done'
review_loop_iteration: 0
followup_review_recommended: true
context:
  - C:/dev/wave-double/_bmad-output/implementation-artifacts/epic-1-context.md
warnings: []
deferred: []
baseline_revision: '869491cc1a2c46ec3ed0823e03d14073c11adeee'
baseline_commit: 'a4a235bbd0de4537d12bc8ecb7951757ba8bd9ac'
---

<intent-contract>

## Intent

**Problem:** 이후 전략 태깅·수급·성과 추적의 입력인 조건검색식 후보 모집단을 실행 계보와 연결해 저장하는 기능이 없다. 후보가 150종목을 넘을 때의 절단과 원본 입력 규모가 보존되지 않으면 기회 누락을 관측할 수 없다.

**Approach:** LS 공통 클라이언트로 받은 t1859 결과를 정규화·결정론적으로 선별하고, Story 1.3의 stage-write 계약과 연결되는 candidates 및 source contribution 저장 모델을 추가한다. 후보가 0건인 정상 응답은 성공으로 기록한다.

## Boundaries & Constraints

**Always:** 모든 후보 행은 `attempt_run_id`와 `trading_day`를 갖고, 후보 ID는 attempt 범위에서 유일해야 한다. 거래대금이 null 또는 유한하지 않은 입력은 제외한다. 상한은 150이며 거래대금 내림차순, ticker 오름차순으로 결정한다. `candidate_source_contrib`의 source는 `t1859|t1852|t1856`, weight는 양수여야 하며 Story 1.5에서는 성공한 t1859에 대해 1.0으로 기록한다. selection input hash와 original/excluded/truncated count를 동일 artifact에 대해 재현 가능하게 계산한다.

**Never:** `candidates.source` 컬럼을 만들지 않는다. Story 1.6의 t1852/t1856 폴백을 선행 구현하지 않는다. domain/backtest에 Supabase·HTTP·LS 응답 형식을 넣지 않는다. 부분/실패 stage를 성공 또는 publish 가능 상태로 위장하지 않는다.

## I/O & Edge-Case Matrix

| Scenario | Input / State | Expected Output / Behavior | Error Handling |
|----------|--------------|----------------------------|----------------|
| HAPPY_PATH | t1859의 유효 후보 150건 이하 | 후보와 contribution을 저장하고 candidates stage를 success로 기록 | 오류 없음 |
| TRUNCATED | 유효 후보 151건 이상 | 상위 150건 저장, 나머지는 `truncated=true`, runs에 절단 수 기록 | 원본·저장 수 차이를 metadata로 설명 |
| INVALID_VALUE | 거래대금 null/NaN/inf 또는 필수 ticker 누락 | 해당 입력 제외, 구조화 result code와 excluded count 기록 | 유효 후보가 없으면 정상 0건 success |
| EMPTY_SUCCESS | t1859 정상 응답이 빈 목록 | 행 없이 candidate_count=0으로 candidates success | 호출 실패와 구분 |

</intent-contract>

## Code Map

- `infra/supabase/migrations/202609011600_create_run_lineage.sql` -- `runs`의 selection/count 메타데이터와 `write_stage` RPC를 제공하므로 후보 migration이 이 계약을 확장한다.
- `apps/batch/ls_client.py:L140-L190` -- 임의 TR 요청과 구조화 응답(`result_code`, `data`, `unprocessed_count`)을 제공하는 t1859 호출 경계.
- `apps/batch/run_state.py:L74-L103` -- stage 입력 검증과 Supabase RPC 호출 adapter; 후보 stage 시작/완료에 재사용한다.
- `packages/domain/domain/run_state.py:L37-L140` -- 순수 stage 상태·publish 규칙. 후보 선별 규칙은 이 계층에 외부 I/O 없이 둔다.
- `infra/supabase/migrations/README.md` -- 단일 UTC timestamp, forward-only migration 규칙.
- `tests/sql/test_run_lineage.sql` -- clean DB에서 RPC 및 stage 상태를 검증하는 기존 SQL 회귀망.

## Tasks & Acceptance

**Execution:**
- [x] `packages/domain/domain/candidate_selection.py` -- 후보 입력 정규화, 결정론적 정렬/150건 절단, SHA-256 input hash와 metadata 반환 -- DB/LS 의존 없는 재현 가능한 선별 규칙을 만든다.
- [x] `infra/supabase/migrations/202609011700_create_candidates.sql` -- attempt-scoped candidates와 candidate_source_contrib 테이블, 제약/인덱스 및 후보 stage 저장 RPC를 추가한다 -- AD-2/AD-12/AD-16을 영속 계약으로 고정한다.
- [x] `apps/batch/candidate_stage.py` -- t1859 호출 결과를 선별하고 stage 시작·행 저장·metadata 기록·success/failed 완료를 조정한다 -- 공통 LS client와 run-state를 연결한다.
- [x] `tests/domain/test_candidate_selection.py` -- 정렬, 동률, invalid value, 150건 절단, 빈 입력과 hash 재현성을 검증한다.
- [x] `tests/batch/test_candidate_stage.py` -- 정상·빈 성공·호출 실패 및 stage RPC payload를 외부 LS 없이 검증한다.
- [x] `tests/sql/test_candidates.sql` -- 제약, source contribution, duplicate 방지, stage 결과와 run metadata를 local SQL fixture에서 검증한다.

**Acceptance Criteria:**
- Given candidates migration을 적용하면, when 스키마를 조회하면, then attempt-scoped `candidates`와 `(candidate_id, attempt_run_id, source)` PK의 `candidate_source_contrib`가 존재하고 `candidates.source`는 존재하지 않는다.
- Given t1859가 유효 후보를 반환하면, when screen stage를 실행하면, then 유효 후보가 거래대금 내림차순·ticker 오름차순으로 최대 150건 저장되고 각 contribution weight 합계가 1이다.
- Given 반환 후보가 150건을 초과하면, when 저장을 완료하면, then 상위 150건만 `truncated=false`, 제외 입력은 절단 metadata로 설명되고 `runs.truncated_count`가 정확하다.
- Given 같은 input artifact를 두 번 선별하면, when 결과 metadata를 비교하면, then selection input hash와 후보 순서/집합이 동일하다.
- Given t1859가 빈 정상 응답이면, when stage-write를 완료하면, then candidate_count=0인 `success`가 되고 `failed`가 아니다.
- Given t1859 호출 자체가 실패하면, when stage를 완료하면, then candidates는 `failed`와 구조화 result code를 기록하며 성공 후보로 publish되지 않는다.

## Design Notes

선별 함수는 입력을 원본 순서와 무관하게 canonical JSON으로 해시한다. ticker는 문자열로 정규화하고 거래대금은 finite 실수만 허용한다. 저장 RPC는 run의 fence/lease를 검증한 뒤 후보 행과 contribution을 같은 transaction에서 기록하고, stage 완료 metadata를 `runs`에 반영한다. 1.5는 t1859만 다루며 source별 분해와 폴백은 1.6에서 확장한다.

## Verification

**Commands:**
- `uv run --with pytest pytest tests/domain/test_candidate_selection.py tests/batch/test_candidate_stage.py -q` -- expected: all candidate selection/stage tests pass.
- `uv run --with pandas --with numpy --with pyarrow --with pytest pytest tests/domain tests/batch -q` -- expected: existing domain/batch regression passes.
- `uv run --with pandas --with numpy --with pyarrow --with pytest pytest backtest -q` -- expected: existing backtest regression passes unchanged.
- `git diff --check` -- expected: no whitespace errors.

## Review Triage Log

### Review Findings — 2026-09-01 hardening pass

- [x] [Review][Patch] 상위 150건만 candidates에 저장하고 절단분은 metadata로 보존 [`apps/batch/candidate_stage.py`](../../../apps/batch/candidate_stage.py)
- [x] [Review][Patch] 후보 write metadata/상한 검증, stage result 영속화, contribution publication guard 추가 [202609012100_harden_run_and_candidate_contracts.sql]
- [x] [Review][Patch] partial 응답의 유효 후보를 보존하고 query index 전달을 회귀 테스트로 고정 [apps/batch/candidate_stage.py, tests/batch/test_candidate_stage.py]

#### Dismissed

- write_candidates 응답 유실 후 같은 attempt 재호출의 candidate UUID 충돌 — 현재 orchestrator는 재실행 시 새 fence attempt를 발급하며, 동일 attempt 재호출 경로는 없다.

### 2026-09-01 — Review pass
- intent_gap: 0
- bad_spec: 0
- patch: 4: (high 2, medium 2, low 0)
- defer: 2: (high 1, medium 1, low 0)
- dismissed:
  - ticker 형식 확대 검증 — 현재 계약은 비어 있지 않은 ticker와 unique 제약만 요구한다.
  - Decimal 전환 — 현재 기능 실패를 입증하지 못한 후속 정밀도 계약이다.
  - raw hash 필드 범위 — 동일 input artifact 재현성 계약을 충족한다.
  - UUID의 cross-attempt 안정성 — candidate_id가 attempt-scoped라는 계약과 일치한다.
  - 기존 runs/logical_runs 보안 경고 — Story 1.3 선행 변경이며 이번 story의 후보 writer에는 별도 권한 제한을 적용했다.
- addressed_findings:
  - `[high]` `[patch]` 실제 t1859 응답 shape 미처리 — OutBlock1과 shcode/hname/price/volume, query_index를 지원.
  - `[medium]` `[patch]` 실패·부분 응답 상태 부정확 — 예외는 failed, 미처리 항목은 partial로 기록.
  - `[high]` `[patch]` 후보 테이블 외부 노출 — RLS 활성화 및 writer RPC PUBLIC 실행 권한 제거.
  - `[medium]` `[patch]` 절단·중복 보존 불일치 — 절단 행 marker와 ticker dedupe 추가.

## Auto Run Result

Status: done

**구현 요약:** t1859 실응답을 해석하는 후보 stage, 결정론적 선별·중복 제거·150건 절단, attempt-scoped 후보와 source contribution 저장, 실패/부분/빈 성공 상태 구분을 구현했다. 후보 테이블 RLS와 server-side writer 권한 제한을 추가했다.

**변경 파일:** `packages/domain/domain/candidate_selection.py`, `apps/batch/candidate_stage.py`, `apps/batch/run_state.py`, 후보 schema/RPC 및 RLS·권한 forward migrations, 관련 domain/batch/SQL 테스트, `sprint-status.yaml`.

**검증:** 후보 테스트 10 passed, domain/batch 58 passed, backtest 16 passed, `git diff --check` 통과. `npx supabase 2.116.0`으로 연결된 Supabase PostgreSQL 17.6에 migrations를 적용했고, 실제 SQL fixture·스키마/RLS·writer 권한을 원격 SQL로 확인했다. UI 변경이 없어 Playwright E2E는 불필요했다.

**잔여 위험:** 기존 Story 1.3의 `logical_runs`/`runs` RLS 및 SECURITY DEFINER 권한 경고가 남아 있다. 실제 LS 자격 증명을 사용한 t1859 호출과 scheduler 연결은 후속 story 범위다.
