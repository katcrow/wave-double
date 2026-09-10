---
title: 'Story 5.4: 편향 계산 close 배치 연결 & append'
type: feature
created: '2026-09-10'
status: done
baseline_revision: '8505a4f9742dd1728551a0d90e3dc85557684028'
review_loop_iteration: 0
followup_review_recommended: false
context:
  - 'C:/dev/wave-double/AGENTS.md'
  - 'C:/dev/wave-double/_bmad-output/implementation-artifacts/epic-5-context.md'
warnings: [oversized]
deferred:
  - summary: >-
      AGENTS.md에 추가된 Supabase 연결 정보 확인 정책 블록을 리뷰 레이어가
      부수 변경으로 지적했다. 에이전트 컨텍스트 문서 편집을 요구하는 finding은
      패치하지 않고 지연한다.
    evidence: |-
      B14/D7이 AGENTS.md의 Supabase 연결 정보 확인 정책 블록을 지적했다.
      워크플로 규칙상 에이전트 컨텍스트 문서(AGENTS.md 등)를 고치는 finding은
      defer, never patch다. 다만 해당 블록은 이 빌드의 Design Notes가 명시적
      허가(사용자 요청, 세션 허가된 변경)로 선언했고 diff에 포함되어 최종
      커밋에 남는다. 후속 스토리에서 블록 위치·내용의 필요성을 재검토할 수 있다.
    location: AGENTS.md
    severity: medium
---

<intent-contract>

## Intent

**Problem:** 5.1의 원장과 5.2/5.3의 계산은 준비됐지만 실제 종가 배치가 편향을 계산·append하지 않는다.

**Approach:** 성공적으로 발행된 close attempt 뒤에 독립 옵션 `bias` stage를 실행한다. canonical 후보·태그·기여를 읽고 유니버스와 절단 종목의 일봉을 독립 확보해 기존 계산 함수를 재사용한다. 메타 1행과 source 3행, stage 완료를 원자적으로 기록한다.

## Boundaries & Constraints

**Always:** canonical published close만 계산한다. REPLAYED는 재계산하지 않는다(정상 일 1회). 별도의 명시적 재계산은 새 이벤트 ID로 append하고 같은 ID 재전송은 중복 생성하지 않는다. source 권위는 해당 attempt의 candidate_source_contrib이며 candidate_tags의 active 시그널만 사용한다. 절단 종목은 같은 실행의 selection에서 전달한다. 부분 데이터 오류는 메타와 partial 상태에 노출하고 미수집을 성공 0으로 숨기지 않는다. bias 실패·실패 상태 기록 실패 모두 이미 발행된 후보/outcome 및 배치 성공을 보존한다. source 3행 전체를 갖춘 이벤트만 저장한다. 운영 Supabase MCP로 migration·권한·명시적 pass rollback fixture를 검증한다. post-publish에는 기존 active-attempt heartbeat를 사용하지 않는다. published close의 run/fence/lease identity와 canonical 여부를 검증하되 이미 완료된 attempt의 lease 만료 자체는 bias 쓰기를 차단하지 않는다.

**Never:** REQUIRED_STAGES와 AD-13의 5개 section taxonomy를 변경하지 않는다. 기존 stage의 published 쓰기 금지를 약화하지 않는다. 기존 migration을 수정하지 않는다. backtest 커널·기존 계산 산식·UI를 변경하지 않는다. premarket/intraday/휴장/replay/publish 실패에서 bias 계산·백필을 호출하지 않는다. 토큰·키를 출력하지 않는다.

## I/O & Edge-Case Matrix

| Scenario | Input / State | Expected Output / Behavior | Error Handling |
|---|---|---|---|
| CLOSE | 필수 stage 및 close 발행 성공 | publish 뒤 bias, 메타 1행+source 3행, stage success | 없음 |
| SKIP | premarket/intraday/휴장/replay/발행 실패 | bias 및 유니버스 백필 미호출 | 기존 결과 유지 |
| FAILURE | 백필/조회/계산/append 예외 | bias failed, published 및 전체 성공 유지 | 실패기록 예외도 격리 |
| PARTIAL | 유니버스/절단 미수집·ineligible·계산 오류·stale | 진단 메타와 partial, 성공 0으로 위장하지 않음 | 종목별 격리 |
| EMPTY | 정상 입력에 후보 시그널 없음 | source 3개 0 모집단 행과 실제 유니버스 수치 | 정상 관측 |
| LINEAGE | 다른 attempt/vanished 태그/다중 source | canonical attempt active 태그만 primary source로 귀속 | 잘못된 canonical 요청 거부 |
| ATOMIC | 잘못된 source/카운트/불완전 행 | 이벤트·source·success 상태 모두 부분 기록 없음 | SQL 예외 |
| RETRY | 같은 이벤트 ID와 같은 payload 재전송 / 새 ID 재계산 | 같은 ID 1회만 / 새 ID append, 과거 보존 | 같은 ID 다른 내용 거부 |
| FENCE | 비-close/비canonical/잘못된 token/기존 stage published 쓰기 | 모두 거부, 올바른 published close bias만 허용 | SQL 예외 |

</intent-contract>

## Code Map

- `apps/batch/scheduler.py` — run_scheduled_batch의 publish 성공 뒤 옵션 실행. SchedulerResult에 bias 상태·코드 추가하되 severity 합산 제외.
- `apps/batch/__main__.py` — ExitStack adapter 생성과 scheduler 주입. 실제 CLI가 bias를 빠뜨리지 않게 연결.
- `apps/batch/universe_signal.py` — backfill_universe_ohlcv, compute_universe_signals 재사용. post-publish heartbeat 미사용.
- `apps/batch/bias_metrics.py` — PopulationSignal, compute_truncated_signals, compute_bias_metrics, as_rows 재사용. 영숫자 절단 티커 격리 보존.
- `apps/batch/candidate_stage.py` — selection.truncated_candidates는 메모리에만 존재, 상위 M 밖 티커를 DB 재조회로 복원할 수 없음.
- `apps/batch/run_state.py` — RunStateGateway.write_stage 및 RPC envelope 처리 재사용.
- `packages/domain/domain/run_state.py` — Stage.BIAS 추가, REQUIRED_STAGES 유지.
- `infra/supabase/migrations/202609021900_write_stage_reacts_to_tags_completion.sql` — 기존 write_stage는 published 전면 거부. forward migration에서 bias 전용 분기만 추가.
- `infra/supabase/migrations/202609091700_create_bias_events.sql` — 원장 스키마와 check 및 append-only guard. source 권한·view의 canonical 조인 보존.
- `infra/supabase/migrations/202609081000_create_market_supply.sql` — publish 후 active_attempt_run_id를 비우므로 기존 heartbeat guard 사용 불가.
- `tests/batch/test_scheduler.py`, `tests/batch/test_bias_metrics.py`, `tests/batch/test_universe_signal.py` — fake 및 회귀 검증 재사용.
- `tools/check_sprint_status.py`, `tools/epic-path-manifests/epic-5.txt` — 최종 상태 동기화 및 scope 경로 등록.

## Tasks & Acceptance

**Execution:**
- `apps/batch/bias_repository.py` — canonical population RPC 및 원자 append RPC adapter/Protocol 구현. request UUID 재시도 보존.
- `apps/batch/bias_stage.py` — 유니버스+절단 독립 백필, 기존 계산, partial 판정, 원자 append, 예외 격리 구현.
- `apps/batch/scheduler.py`, `apps/batch/__main__.py`, `packages/domain/domain/run_state.py` — close 발행 뒤 실행 및 실제 CLI 주입, 옵션 상태 모델 추가.
- `infra/supabase/migrations/202609100200_bias_close_stage.sql` — 실제 최신 write_stage 원형을 유지하는 bias 분기, canonical population 읽기, 검증된 원자 append RPC. public/anon/authenticated 실행 차단, service_role만 허용. 기존 published 성공은 유지. old runs의 누락 bias 키는 pending 취급. SQL 상태 변경은 기존 stage-write를 사용한다.
- `tests/batch/test_bias_stage.py`, `tests/batch/test_bias_repository.py`, `tests/batch/test_scheduler.py`, `tests/domain/test_run_state.py` — matrix 전 행 및 CLI 배선 테스트. 실제 파일 위치에 맞춰 기존 테스트 수정.
- `tests/sql/test_bias_close_stage.sql` — 운영 MCP 실행 가능한 rollback fixture. 원자성·계보·재전송·권한·기존 stage 보호·발행 격리를 명시적 pass로 반환.
- `tools/epic-path-manifests/epic-5.txt` — 변경 경로 등록.

**Acceptance Criteria:**
- Given close 발행 성공, when bias stage가 끝나면, then source별 계산이 메타 1행과 분해 3행으로 함께 append되고 stage-write RPC로 완료가 기록된다.
- Given 비-close 또는 재생 실행, when scheduler를 실행하면, then bias 계산과 독립 백필은 실행되지 않는다.
- Given 편향 처리 실패, when 결과를 확인하면, then 독립 bias 상태만 실패이며 후보·태그·수급·outcome 발행과 대시보드 taxonomy는 영향을 받지 않는다.
- Given 운영 프로젝트, when SQL fixture 및 catalog/ACL 확인을 수행하면, then 실제 RPC 원자성·계보·쓰기 권한 검증이 pass이고 fixture 잔여 데이터는 없다.

## Spec Change Log

## Review Triage Log

### 2026-09-10 — Review pass

- intent_gap: 0
- bad_spec: 0
- patch: 3 (high 0, medium 3, low 0)
- defer: 1 (medium 1)
- dismissed:
  - B5 bias_stage import 순서 — repo에 ruff/isort 설정이 없어 순서 검사기 자체가 존재하지 않음(patch 아님).
  - B6 counting jsonb_agg — 빈 입력에서 jsonb_agg는 배열이 아닌 NULL을 반환하며 `NOT NULL` 어서션과 모순 없이 `'[]'::jsonb`와 동등(NOT NULL 어서션과 모순 없음).
  - B7 write_stage 시그니처 — 마이그레이션이 기존 정의와 동일한 9-arg 원형을 정확히 유지해 overload가 없음.
  - B8 bias_event_by_source 소스 유일성 — `(bias_event_id, source)` PK가 이미 202609091700에 존재해 중복 최우선 행이 불가.
  - B11 example_annot count — meta는 항상 키 시딩과 함께 build되어 누락 상태가 없음.
  - B12 signal_result None — 계산 그래프상 None이 도달할 수 없음.
  - B13 retryable 래핑 누락 — `_call`이 모든 예외를 retryable `RunStateError`로 래핑해 스케줄러 catch가 실제 오류를 숨기지 않음.
  - B16 isinstance 배선 — 두 경로(주입/미주입)를 stub shape 검증으로 커버해 충분.
  - B4 bias 실행 훅 누락 — CLI는 항상 adapter를 주입하며 미주입 시 실행되지 않음(의도된 확장점).
  - B10 failure_recorded 노출 — 성공 경로에서 미사용은 노출 API 의도, 가독성 무해.
  - D1 SchedulerResult 구조 변화 수용 — 스펙이 상태 재작성을 허용하고 기존 5-Section taxonomy·REQUIRED_STAGES는 보존됨.
  - D2 initial_stage_status 시딩 — enum 미러로 production 소비자가 없어 부수 영향 없음.
  - D3 replay 차단 — 스케줄러 게이트 외에도 DB canonical 제약이 재계산을 차단해 다른 창에서도 안전.
  - D6 truncated 전달 — selection.truncated_candidates를 그대로 전달하는 1줄 pass-through가 의도된 배선.
- addressed_findings:
  - `[medium]` `[patch]` VG1 CI 미등록 — `.github/workflows/test.yml` 고정 목록에 신규/수정 테스트 등록(domain job에 `test_run_state.py`, scheduler job에 `test_bias_repository.py`·`test_bias_stage.py`).
  - `[medium]` `[patch]` B1/B2/B17 예외 진단 부재 — `bias_stage.py` 실패 경로에 run_id/event_id/failure_recorded 진단 print, `scheduler.py` 경계 except에 예외 print, `_from_candidate_result` docstring에 bias_result 의미 명시.
  - `[medium]` `[patch]` VG2 payload 키 미고정 — `SourceBiasMetrics.as_dict()` 키 회귀 테스트(+`as_rows()` 원문 행 단언)와 SQL fixture population sources 키(`source`/`weight`) 단언 추가.
  - defer(B14/D7): AGENTS.md 정책 블록 — 워크플로 규칙에 따라 패치하지 않음. Design Notes 허가로 diff에 포함되어 최종 커밋에 남음.

## Auto Run Result

**Summary of implemented change**

close 배치가 publish 성공 뒤 `bias` 옵션 stage를 실행한다. canonical active 후보·기여를 읽고 유니버스와 절단 종목을 독립 백필해 기존 계산 함수를 재사용하며, 메타 1행과 source 3행, stage 완료를 원자적 append RPC(`append_bias_event`)로 기록한다. REPLAYED·비-close·publish 실패·재계산 금지 시그널에서 bias·백필을 호출하지 않는다. 실패·부분 데이터는 독립 bias 상태와 진단 메타로 노출돼 후보·태그·수급·outcome 발행과 대시보드 taxonomy를 보존한다.

**Files changed**

- `apps/batch/bias_repository.py` (신규) — canonical population RPC(`get_bias_population`)과 원자 append RPC(`append_bias_event`) adapter/Protocol, retry·rerun 브리지.
- `apps/batch/bias_stage.py` (신규) — 유니버스+절단 독립 백필, 기존 `compute_bias_metrics`/`compute_truncated_signals` 재사용, partial 판정, 원자 append, 실패·실패기록 예외 격리 + 진단 출력.
- `apps/batch/bias_metrics.py` — reuse 전용 확장(부분 신호/절단 전파).
- `apps/batch/scheduler.py` — `run_scheduled_batch` publish 성공 뒤 bias 옵션 실행, `SchedulerResult`에 bias 상태/코드(severity 합산 제외) 추가, 경계 예외 진단.
- `apps/batch/__main__.py` — CLI ExitStack adapter 생성·주입.
- `apps/batch/run_state.py` — `_call` 재시도 브리지.
- `packages/domain/domain/run_state.py` — `Stage.BIAS`, `initial_stage_status` 시딩, `write_stage` 검증 준수.
- `infra/supabase/migrations/202609100200_bias_close_stage.sql` (신규) — write_stage bias 분기(기존 published 성공 보존, old runs 누락 키 pending 취급), `get_bias_population`, 검증된 원자 `append_bias_event`, anon/authenticated 실행 차단·service_role만 허용.
- `tests/batch/test_bias_repository.py`, `tests/batch/test_bias_stage.py`, `tests/sql/test_bias_close_stage.sql` (신규) — 어댑터/스테이지/SQL rollback fixture.
- `tests/batch/test_scheduler.py`, `tests/domain/test_run_state.py`, `tests/batch/test_main.py` — 배선·모델 확장 반영.
- `.github/workflows/test.yml` — 신규·수정 테스트 CI 고정 목록 등록(VG1 패치).
- `tools/epic-path-manifests/epic-5.txt` — 변경 경로 등록.
- `AGENTS.md` — Supabase 연결 정보 확인 정책 블록(Design Notes 허가, defer 기록).

**Review findings breakdown**

- patches applied: 3(medium 3) — VG1 CI 등록, B1/B2/B17 예외 진단, VG2 payload 키 고정. Verification 통과.
- deferred: 1(medium 1) — B14/D7 AGENTS.md 정책 블록(에이전트 컨텍스트 문서 규칙상 패치 안 함, diff 포함).
- dismissed: B4, B5, B6, B7, B8, B10, B11, B12, B13, B16, D1, D2, D3, D6 — 각각의 주장 지점에서 검증 실패 또는 의도된 동작. 상세는 Review Triage Log.

**Follow-up review recommendation**

- patched severity counts: high 0, medium 3, low 0 → score = 3×1 = 3 (< 5).
- `followup_review_recommended: false`.

**Verification performed**

- `uv run --with pandas --with numpy --with pyarrow --with pyyaml --with pytest pytest -q` → **719 passed**.
- `python tools/check_migration_order.py` → migration order contract passed (68 files).
- `uv run --with pyyaml python tools/check_sprint_status.py` → 계약 통과(action item 38건).
- `git diff --check` → whitespace 오류 없음(LF→CRLF 경고만).
- 운영 Supabase MCP: migration `20260910020000_bias_close_stage` 적용 기록 확인 → catalog(함수 존재, proacl postgres/service_role만) 확인 → fixture 실행 시 **9개 시나리오 전부 pass**(real publish·multi-stage, empty population, canonical lineage, 원자 append·만료 lease, idempotent/conflict/recalculation, 원자 rollback·source 검증, fence/canonical/기존 stage guard, 실패 시 발행 보존, rpc_acl) → 잔여 행 0(runs/candidates/market_supply/bias_events 모두 0) 확인.
- UI 변경이 없어 Playwright UI e2e 부재는 해당하지 않음. scheduler 통합 테스트와 실제 DB RPC fixture로 배치 경계 검증.

**Residual risks**

- 재계산 failure 시 `expected_status=pending` 불일치로 DB가 stale success를 유지할 수 있으나 이번 패치의 진단 print가 현장 관측 가능하게 만듦(low).
- 실패 기록의 두 비원자 write 사이 크래시 시 `bias`가 running에 잔류 가능 — 전 스테이지 공통 패턴으로 기존 리스크(low).
- `oversized` warning: 이 빌드가 재사용형 계산 함수까지 diff에 포함해 스펙이 커졌지만 동작 보존 확인 완료(low).

## Design Notes

후보 발행 후 canonical source를 읽는다. 완료된 run에 대한 bias 권한은 canonical identity와 fence/lease token으로 검증하며 active lease 연장을 요구하지 않는다. 사용자 요청으로 먼저 추가한 AGENTS.md 정책은 이 세션의 허가된 변경이며 최종 커밋에 포함한다. 코드 구현 담당은 migration과 fixture 파일을 준비하고 운영 적용은 부모 에이전트가 MCP로 실행한다. migration 미적용 상태를 완료로 보고하지 않는다.

## Verification

- `uv run --with pandas --with numpy --with pyarrow --with pyyaml --with pytest pytest -q` — 전체 회귀 통과.
- `python tools/check_migration_order.py` — migration 순서 통과.
- `uv run --with pyyaml python tools/check_sprint_status.py` — 상태 검증 통과(최종 동기화는 부모).
- `git diff --check` — whitespace 오류 없음.
- 운영 Supabase MCP: migration 적용 전 catalog 확인, 적용 후 fixture pass/ACL/migration 기록 및 잔여 행 검증.
- UI 변경이 없어 Playwright UI e2e는 해당하지 않는다. scheduler 통합 테스트와 실제 DB RPC fixture로 배치 경계를 검증한다.
