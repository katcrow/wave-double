---
title: 'Story 4.4: 빈 수급 적재 방지 가드'
type: 'feature'
created: '2026-09-08'
status: 'done'
review_loop_iteration: 0
followup_review_recommended: false
baseline_commit: '00d9eee9cbc7443942bba236dcddd42ddac46331'
baseline_revision: '00d9eee9cbc7443942bba236dcddd42ddac46331'
context:
  - 'C:/dev/wave-double/_bmad-output/implementation-artifacts/epic-4-context.md'
warnings: [oversized]
deferred: []
---

<intent-contract>

## Intent

**Problem:** 장중 t1702/t1637의 전부 0 응답은 실제 순매수 0이 아니라 아직 확정되지 않은 값일 수 있는데, 현재 stage가 이를 즉시 `confirmed`로 저장해 수급 힌트를 오염시킨다.

**Approach:** D0의 네 투자자 필드가 모두 0이면 bounded semantic retry를 한 번 더 수행한다. intraday에서 재시도 후에도 0이면 네 필드를 NULL + `pending`으로 저장하고, close에서는 16:00 확정 실행의 재확인 값을 실제 0으로 보존한다. 조회 실패는 가격 확보 여부에 따라 `missing` 행 또는 후보 단위 partial로 기록한다.

## Boundaries & Constraints

**Always:** D-2/D-1/D0의 가격 행과 attempt 귀속을 유지한다. D0에서만 장중 전부 0 가드를 적용하며, `confirmed`는 네 값이 모두 실측된 경우에만 사용한다. `pending`/`missing` 행의 네 수급 필드는 모두 NULL이고, stage result에는 결측 ticker와 원인을 남긴다. 기존 `Supply3DayRepository` conflict target, stage-write RPC, A~F active-tag 소비 계약을 유지한다.

**Never:** 0을 NULL 대신 임의의 0이 아닌 값으로 보정하지 않는다. t1636을 사용하거나 새 테이블·기존 migration을 수정하지 않는다. t1702 실패로 가격 필수가 없는 행을 억지로 삽입하지 않으며, 이번 스토리에서 UI를 구현하지 않는다.

## I/O & Edge-Case Matrix

| Scenario | Input / State | Expected Output / Behavior | Error Handling |
|----------|--------------|---------------------------|----------------|
| D0_ZERO_INTRADAY | D0 네 값이 모두 0, 재시도도 0 | D0 네 값 NULL, `pending`; D-2/D-1은 기존 값 보존 | stage는 성공 또는 다른 후보 결측 시 partial |
| D0_ZERO_CLOSE | close 실행, 재시도 후 D0 네 값 0 | D0의 실제 0 네 값과 `confirmed` 저장 | publish 전제인 supply success 유지 |
| PROGRAM_LOOKUP_FAILED | t1702 가격 성공, t1637 실패 | 세 슬롯 가격 유지, 네 수급 NULL + `missing` | 해당 ticker를 포함한 stage partial |
| PRICE_LOOKUP_FAILED | t1702 실패 | 해당 후보 행 미저장 | ticker를 unprocessed로 남기고 stage partial |

</intent-contract>

## Code Map

- `apps/batch/supply_stage.py:66-255` -- 후보별 t1702/t1637 오케스트레이션, `SupplyRow` 조립, partial 결과와 stage-write 경계. D0 semantic retry와 pending/missing 판정의 구현 지점.
- `apps/batch/scheduler.py:188-221,230-242` -- `BatchKind.INTRADAY|CLOSE`를 supply stage에 전달하고 partial/failed 시 close publish를 차단하는 배선.
- `apps/batch/supply_3day_repository.py:16-48,84-97` -- nullable 네 수급 필드와 status payload, attempt별 멱등 upsert; 변경하지 않고 저장 계약을 재사용한다.
- `apps/batch/ls_supply_provider.py:16-75` -- t1702의 가격·외인·기관·개인 파싱 및 0 보존.
- `apps/batch/ls_program_supply_provider.py:16-85` -- t1637 `svolume` 파싱 및 유한값 검증.
- `infra/supabase/migrations/202609022000_create_supply_3day.sql:17-38` -- pending/missing NULL과 confirmed 제약의 원본 계약; 신규 migration 불필요.
- `tests/batch/test_supply_stage.py` -- 정상 confirmed, 후보별 실패 격리, 3슬롯·attempt 귀속을 검증하는 회귀 표면.
- `tests/batch/test_scheduler.py:394-479` -- supply partial/failed 전파와 close publish 차단 회귀 표면.
- `tests/sql/test_supply_3day.sql:124-148` -- 운영 DB에서 pending/missing의 NULL 계약을 검증하는 fixture에 가드 상태 단언을 추가한다.

## Tasks & Acceptance

**Execution:**
- [x] `apps/batch/supply_stage.py` -- D0 전부 0 감지, bounded semantic retry, intraday pending/close confirmed-zero, t1637 실패 missing 행을 구현 -- 조용한 0 오염과 행 유실 방지.
- [x] `apps/batch/scheduler.py` -- batch kind를 supply stage에 전달 -- close 확정과 intraday 미확정 정책을 구분.
- [x] `tests/batch/test_supply_stage.py` -- 재시도 성공/실패, pending/confirmed-zero, missing, 혼합 후보 partial을 검증 -- 가드 경계 회귀 방지.
- [x] `tests/batch/test_scheduler.py` -- partial supply가 scheduler 결과와 close publish 조건에 반영되는지 보강 -- 운영 발행 차단 보장.
- [x] `tests/sql/test_supply_3day.sql` -- pending/missing의 네 NULL 및 confirmed 실제 0을 운영 DB fixture로 assert -- schema 제약과 저장 결과 증명.

**Acceptance Criteria:**
- Given t1702/t1637의 D0 외인·기관·개인·프로그램이 모두 0이면, when supply stage가 응답을 처리하면, then bounded retry 후에도 0인 intraday D0은 NULL + `pending`으로 저장되고 0으로 확정되지 않는다.
- Given semantic retry 중 실제 값이 확보되면, when 행을 저장하면, then 해당 D0은 네 실측값 + `confirmed`이고 실제 0인 개별 필드도 0으로 보존된다.
- Given close 확정 실행에서 재시도 후 네 값이 실제 0이면, when 행을 저장하면, then 네 값 0 + `confirmed`로 저장되어 pending과 구분된다.
- Given t1637 조회가 실패하고 t1702 가격은 확보되면, when stage가 후보를 처리하면, then 세 슬롯의 가격은 저장되고 네 수급은 NULL + `missing`, 후보 목록과 원인은 stage result에 남는다.
- Given 한 후보가 결측이고 다른 후보가 정상인 경우, when 배치가 완료되면, then 정상 후보 행은 저장되고 supply stage는 `partial`이며 close publish는 호출되지 않는다.
- Given t1702 조회가 실패한 경우, when 배치가 완료되면, then 가격 필수 컬럼이 없는 행은 생성하지 않고 ticker를 unprocessed로 남긴다.

## Spec Change Log

## Review Triage Log

## Design Notes

D0만 의미적 가드 대상인 이유는 D-2/D-1은 이미 확정된 과거 거래일이고, 장중 미확정 신호는 당일 행에 한정되기 때문이다. `run_supply_stage`에는 batch kind를 명시적으로 전달해 close의 최종 0과 intraday의 pending을 구분한다. t1702 실패는 `close`/`volume`/`change_pct` NOT NULL 계약 때문에 missing 행을 만들 수 없으므로 partial로 관측하고, t1637 실패는 t1702 가격을 활용해 상태가 표시되는 행을 남긴다.

## Verification

**Commands:**
- `uv run --with pytest pytest tests/batch/test_supply_stage.py tests/batch/test_scheduler.py -q` -- 신규 가드·partial·publish 차단 회귀가 통과한다.
- `uv run --with pandas --with numpy --with pyarrow --with pytest pytest` -- 전체 Python/backtest 회귀가 통과한다.
- `git diff --check` -- 공백 오류가 없다.

**Manual checks (if no CLI):**
- 운영 Supabase MCP에서 수정된 SQL fixture를 rollback 가능한 transaction으로 실행해 pending/missing NULL, confirmed 실제 0, stage result 계약을 명시적으로 확인한다.
- UI 변경이 없으므로 Playwright E2E는 실행하지 않는다.

## Suggested Review Order

**D0 의미적 가드와 행 상태 분기**

- stage 진입점에서 batch kind와 후보별 저장 경계를 확인한다.
  [`supply_stage.py:66`](../../apps/batch/supply_stage.py#L66)

- all-zero 재시도 후 pending/confirmed/missing 행을 조립한다.
  [`supply_stage.py:156`](../../apps/batch/supply_stage.py#L156)

- pending과 missing이 네 수급 컬럼을 NULL로 만드는 공통 저장 경계를 확인한다.
  [`supply_stage.py:320`](../../apps/batch/supply_stage.py#L320)

**배치 전파와 발행 차단**

- scheduler가 close/intraday batch kind를 supply stage에 전달한다.
  [`scheduler.py:210`](../../apps/batch/scheduler.py#L210)

- t1637 결측이 partial과 publish 차단으로 노출되는지 검증한다.
  [`test_scheduler.py:432`](../../tests/batch/test_scheduler.py#L432)

**회귀·운영 계약**

- all-zero 재시도 결과와 후보별 결측 격리를 확인한다.
  [`test_supply_stage.py:199`](../../tests/batch/test_supply_stage.py#L199)

- 운영 schema fixture에서 actual zero와 pending/missing NULL을 확인한다.
  [`test_supply_3day.sql:25`](../../tests/sql/test_supply_3day.sql#L25)
