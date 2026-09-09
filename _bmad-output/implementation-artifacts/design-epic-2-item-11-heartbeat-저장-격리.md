---
title: 'Design: 장시간 tags stage의 heartbeat/lease 연장과 저장 실패 격리'
type: 'design'
created: '2026-09-09'
status: 'done'
epic: 2
context:
  - 'C:/dev/wave-double/_bmad-output/implementation-artifacts/epic-2-retro-09-03-2026.md'
  - 'C:/dev/wave-double/_bmad-output/implementation-artifacts/spec-2-5-후보-태깅-stage-저장.md'
---

# epic-2-retro item-11: 장시간 tags stage heartbeat/lease 연장 + 저장 실패 격리

## Intent

**Problem:** 두 deferred 항목이 남아 있다.

1. **lease 만료(F3, spec-2-5 deferred #2):** tags stage가 후보별 OHLCV 로딩·계산·저장을 순차 수행하는데, LS API TR별 1건/초 제한 하에서 신규 편입 종목이나 후보가 많으면 기본 `lease_seconds=300` 안에 끝나지 못한다(`initialize_new_ticker_history` 호출만으로도 수십~수백 초). lease가 만료되면 stage write가 `STALE_FENCE_OR_LEASE`로 거부되어 정상 계산 결과가 폐기된다.
2. **저장 실패 전량 폐기(F4, spec-2-5 deferred #1):** `upsert_tags(all_tags)`가 전체를 단일 batch POST로 보내 한 행의 실패(FK 위반 등)가 다른 종목의 계산 결과까지 전부 폐기한다.

**Approach:** 이미 DB에 존재하는 `heartbeat_attempt` RPC(`RunStateGateway.heartbeat`)를 배치 파이프라인에 배선한다 — stage 루프가 종목/후보 하나를 처리할 때마다 heartbeat 정책의 `beat()`를 호출해 실행 중 lease를 주기적으로 연장한다. 저장은 후보 단위로 격리해 부분 실패가 다른 후보의 결과를 폐기하지 않게 한다.

## Pathways

### F1 — heartbeat로 lease 연장

- **신규 `apps/batch/heartbeat.py`:** `HeartbeatPolicy` 프로토콜(`beat()`)과 기본 구현 `LeaseHeartbeat`를 정의한다.
  - `LeaseHeartbeat(gateway, run_id, fence_token, lease_token, *, lease_seconds, interval_seconds, max_failures)`.
  - `interval_seconds`(기본 60초)마다 한 번만 `gateway.heartbeat(run_id, fence_token, lease_token, lease_seconds=...)`를 호출한다. 종류 다수의 `beat()` 호출 중 실제 RPC는 interval 경과 후 1회뿐이라 네트워크 비용이 절약된다.
  - heartbeat 호출 실패는 계산을 중단시키지 않고 `failures`를 누적해 `max_failures`(기본 3) 이상이면 `HeartbeatExhausted`를 던진다 — 단일 일시적 실패로 정상 계산을 버리지 않으면서, 지속 네트워크 단절로 lease 연장이 불가능한 경우를 조기에 표면화한다.
  - lease_token은 RPC가 회전하지 않고 고정이다(`heartbeat_attempt`는 lease_expires_at만 갱신, `infra/supabase/migrations/202609011600_create_run_lineage.sql:152-163`).
- **배선 지점(모두 선택적 인자로 주입):**
  - `run_tags_stage(..., heartbeat: HeartbeatPolicy | None = None)` — 후보별 루프 상단에서 `beat()`.
  - `initialize_new_ticker_history(..., heartbeat=None)` / `update_existing_ticker_history(..., heartbeat=None)` — 신규/기존 티커별 루프에서 `beat()` (OHLCV refresh 윈도우도 lease 예산을 소모하므로).
  - `scheduler.run_scheduled_batch(...)` — candidate stage가 확정한 `run_id/fence_token/lease_token`으로 `LeaseHeartbeat`를 한 번 만들고 refresh + tags stage가 공유한다. 두 윈도우가 같은 policy 인스턴스를 쓰므로 lease 연장이 중복 발사되지 않는다(`LeaseHeartbeat` 내부 건너뛰기).
- **예외 경로:** heartbeat 미주입 시 기존 동작과 100% 동일하다(테스트 회귀망이 이를 보장). 모든 기존 호출자는 선택적 인자이므로 시그니처 변경이 없다.

### F4 — 후보 단위 저장 격리

- `run_tags_stage`에서 `all_tags`를 `candidate_id`별로 그룹핑해 각 후보의 태그를 따로 `upsert_tags()`한다. 실패한 후보는 `persist_failed_count`로 집계하고 다음 후보로 진행한다.
- 결과 전이:
  - **전부 성공** → 기존 로직 유지(sync_vanished → OK/VANISHED_SYNC_FAILED/PARTIAL_TAGGING).
  - **일부 성공 + 일부 실패** → `partial` + `TAGS_PERSIST_PARTIAL`, `unprocessed_count = error_count + persist_failed_count`. 저장 성공한 후보의 태그는 보존된다. 부분 저장된 active 태그 집합은 불완전하므로 이번 attempt에서 소멸 판정(`sync_vanished`)을 수행하지 않는다 — 잘못된 vanished 표시를 피하고 후속 attempt가 재동기화한다.
  - **전부 실패** → 기존 `failed` + `TAGS_PERSIST_FAILED` 유지.
  - **태깅된 후보 0건(all_tags 비어 있음)** → upsert 자체를 호출하지 않는다(빈 배치 실패 회피). 기존 동작은 빈 리스트로도 upsert를 호출했지만, 저장할 것이 없으면 호출할 이유가 없으므로 이 변경은 의도된 행동 수정이며 테스트를 함께 갱신한다.

## Boundaries & Constraints

**Always:** candidate_tags의 멱등 upsert 계약(`attempt_run_id` 포함), `write_stage`의 fence/lease 검증, 전략 A~F 결과, partial/failed 전파는 기존을 유지한다. heartbeat는 stage 계산 결과를 변경하지 않는다(순수 lease 연장 부수효과). 실패 격리는 후보 단위(React 레벨)로 하며 행 단위가 아니다 — 한 후보의 태그가 복수 전략이면 함께 성공/실패한다.

**Never:** lease를 무한대로 두거나 fence/lease 검증을 우회하지 않는다. `upsert_tags`의 행 단위 개별 요청으로 바꾸지 않는다(후보당 1회 batch POST 유지, TR 요청 폭증 방지). heartbeat 실패를 조용히 삼키는 기본값으로 두지 않는다(`max_failures` 도달 시 명시적 예외). supply/market_supply stage의 시그니처를 바꾸지 않는다(이번 설계 범위는 tags stage + OHLCV refresh 원도 + scheduler 오케스트레이션).

## I/O & Edge-Case Matrix

| Scenario | Input / State | Expected Output / Behavior |
|----------|--------------|---------------------------|
| LONG_TAGS | 후보 다수, 300초 초과 실행 | candidate마다 interval 경과 시 `heartbeat_attempt` RPC 호출, lease 연장 → stage write 성공 |
| NO_HEARTBEAT | heartbeat 미주입 | 기존 동작과 동일(회귀망 유지) |
| HEARTBEAT_NET_DOWN | 연속 RPC 실패 ≥ max_failures | `HeartbeatExhausted` 상위 전파 → UNHANDLED_EXCEPTION으로 관측(기존 lease 만료 신호와 동일한 실패 명시성) |
| EMPTY_TAGS | 태깅 결과 0건 | upsert 미호출, sync_vanished만 수행, success |
| PARTIAL_PERSIST | 후보 중 1건 upsert 실패 | 성공 후보 태그 저장 유지, `partial` + `TAGS_PERSIST_PARTIAL`, `sync_vanished` 생략, `persist_failed_count=1` |
| ALL_PERSIST_FAIL | 전 후보 upsert 실패 | `failed` + `TAGS_PERSIST_FAILED`(기존과 동일) |
| REFRESH_LONG | 신규 티커 다수, initialize에 수백 초 | 티커별 beat로 lease 연장 |

## Code Map

- `apps/batch/heartbeat.py` — 신규: `HeartbeatPolicy` / `LeaseHeartbeat` / `HeartbeatExhausted`.
- `apps/batch/tags_stage.py` — heartbeat 선택적 인자, 후보별 루프 beat, 후보 단위 upsert 격리, `TAGS_PERSIST_PARTIAL` 경로, `TagsStageResult.persist_failed_count`.
- `apps/batch/ohlcv_cache.py` — refresh 두 함수에 선택적 `heartbeat` 인자(티커별 루프 beat).
- `apps/batch/scheduler.py` — candidate stage 결과로 `LeaseHeartbeat` 생성, refresh + tags stage에 전달.
- `apps/batch/run_state.py:192` — 기존 `heartbeat()` RPC adapter(변경 없음).
- `infra/supabase/migrations/202609011600_create_run_lineage.sql:152-163` — 기존 `heartbeat_attempt` RPC(SQL 변경 없음).
- `tests/batch/test_heartbeat.py` — 신규: interval 건너뛰기/인자 전달/일시 실패 복구/`HeartbeatExhausted`/validation.
- `tests/batch/test_tags_stage.py` — 신규: 전부 실패·부분 실패 격리·빈 태그 upsert 미호출·후보별 heartbeat 호출.
- `tests/batch/test_ohlcv_cache.py` — 두 refresh 함수의 heartbeat 호출.
- `tests/batch/test_scheduler.py` — scheduler가 attempt의 fence/lease token으로 heartbeat 발사.

## Tasks & Acceptance

**Execution:**
- [x] `apps/batch/heartbeat.py` -- heartbeat 정책·서브헬퍼 구현.
- [x] `apps/batch/tags_stage.py` -- heartbeat 인자 + 후보 단위 저장 격리 + `TAGS_PERSIST_PARTIAL`.
- [x] `apps/batch/ohlcv_cache.py` -- refresh 루프 heartbeat.
- [x] `apps/batch/scheduler.py` -- `LeaseHeartbeat` 생성·배선.
- [x] `tests/batch/*` -- 위 4개 파일의 회귀·신규 테스트.

**Review (build/review evidence):**
- [x] `uv run --with pandas --with numpy --with pyarrow --with pytest pytest` 전체 518개 green 검증 완료(2026-09-09).

**AC — Given/When/Then:**
- Given 후보가 많아 300초 초과 실행, when tags stage가 후보를 처리하면, then interval 경과 시 `heartbeat_attempt` RPC로 lease가 연장된다.
- Given 후보 중 일부 upsert가 실패하면, when stage를 종결하면, then 성공 후보 태그는 보존되고 `partial`/`TAGS_PERSIST_PARTIAL`로 기록된다.
- Given 모든 후보 upsert가 실패하면, when stage를 종결하면, then `failed`/`TAGS_PERSIST_FAILED`로 기록된다(기존 계약 유지).
- Given 태깅 결과가 없으면, when stage를 종결하면, then upsert를 호출하지 않고 성공 처리된다.

## Design Notes

- **선택적 인자 채택 이유:** `TagsRepositoryProtocol`을 바꾸거나 stage를 heartbeat 필수로 만들지 않았다. 모든 기존 호출자·테스트가 인자 없이도 동작해 회귀 표면이 그대로 살아있고, 배선은 scheduler(유일한 production 호출자) 한 곳에만 둔다.
- **interval 기본값(60초) 대 lease(300초) 비율:** lease의 1/5 주기로 갱신해 RPC 비용과 안전 마진을 균형 잡았다. `reap_expired_attempts`가 lease 만료를 `failed`로 전이하는 경쟁을 피하기 위해 2~3번의 heartbeat 창이 lease 기간 안에 들어가도록 했다.
- **sync_vanished 생략 근거:** 일부 후보만 저장된 active 태그 집합으로 소멸 판정을 내리면 "저장되다 만" 후보를 소멸로 오판할 수 있다. 후속 attempt가 전체 태깅을 다시 저장하며 생략된 소멸 동기화를 자연 재수행한다.
- **신규 result code:** `TAGS_PERSIST_PARTIAL`은 scheduler의 `_STATUS_SEVERITY`에서 기존 `partial` 그룹으로 취급되며 close publish 차단 조건(`tags_result.status == "success"`)에 걸려 publish가 차단된다 — 부분 저장 성공으로 발행이 잘못 승인되지 않는다.
- **heartbeat 실패 = stage 실패가 아님:** heartbeat RPC의 일시적 실패는 계산을 중단시키지 않는다. 진짜 lease 만료는 최종 stage write가 `STALE_FENCE_OR_LEASE`로 거부되어 명시적으로 실패한다. `max_failures`는 "이미 거의 확실히 lease를 잃었다"고 판단되는 연속 실패에서만 조기 상승시킨다.
- **SQL 변경 없음:** `heartbeat_attempt` RPC와 `write_stage`/`reap_expired_attempts`가 이미 heartbeat 계약을 지원하므로 migration이 필요 없다(운영 적용·RPC 검증은 item-9에서 완료됨).