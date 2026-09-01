---
title: '스케줄 자동 배치 실행'
type: 'feature'
created: '2026-09-01'
status: 'done'
baseline_revision: '2a69cfaa10c0444478e1070219dae5e933ee3ce2'
review_loop_iteration: 0
followup_review_recommended: true
context: []
warnings: ['oversized']
deferred:
  - summary: >-
      SQL fixture(tests/sql/*.sql)가 어떤 story에서도 CI에 연결되어 있지 않아 skip_attempt를
      포함한 RPC의 fence/lease/상태 전이 계약이 병합을 막는 경로에서 전혀 검증되지 않는다.
    evidence: |-
      .github/workflows/test.yml에는 psql/supabase CLI를 호출하는 단계가 전혀 없다(grep 확인).
      Story 1.3/1.5/1.6이 추가한 test_run_lineage.sql/test_candidates.sql/test_candidates_fallback.sql도
      동일하게 미연결 상태이며, 이번 story 1.7의 test_skip_attempt.sql도 같은 패턴을 따랐다.
    location: >-
      .github/workflows/test.yml
    severity: medium
---

<intent-contract>

## Intent

**Problem:** 후보 모집단 갱신(1.5/1.6)과 배치 상태머신(1.3)은 완성됐지만, 이를 실제로 매 거래일 개장 전/장중 30분/종가 확정 시점에 자동 실행하는 스케줄러가 없다. 휴장일 판정(1.2)도 아직 어떤 실행 경로에도 연결되지 않았다.
**Approach:** GitHub Actions cron 워크플로가 신규 orchestrator 진입점(`apps/batch/__main__.py`)을 호출하고, 이 진입점은 캐시된 `trading_calendar`를 먼저 조회해(API 호출 없이) 휴장이면 `runs`에 `skip_reason=holiday`만 기록하고 종료하며, 개장일이면 기존 `run_candidate_stage`를 `trigger=schedule`로 위임한다.

## Boundaries & Constraints

**Always:** 휴장 판정은 캐시(`trading_calendar` 조회)를 먼저 사용하고, 캐시 미스일 때만 1.2의 `resolve_and_cache`(LS 일봉 조회 1콜)를 호출한다. `CALENDAR_UNAVAILABLE`은 휴장이 아니므로 정상 진행한다. 모든 GH Actions cron은 UTC로 쓰고 KST 환산 주석을 병기한다. 스케줄 실행은 항상 `Trigger.SCHEDULE`로 기록된다.

**Never:** 수동 트리거(dispatch_outbox, `manual`)는 구현하지 않는다(1.10). GH Actions `concurrency.group`을 유일한 동시성 방어로 삼지 않는다 — DB fence(1.3)가 최종 권위다. 장중 슬롯을 `intraday_slots()` 도메인 함수로 강제 계산하지 않는다 — 30분 경계 스냅은 새 순수 함수(`floor_to_half_hour`)로 충분하다.

## I/O & Edge-Case Matrix

| Scenario | Input / State | Expected Output / Behavior | Error Handling |
|----------|--------------|---------------------------|----------------|
| 휴장일 캐시 존재 | `trading_calendar`에 `is_open=false` 캐시 행 존재 | LS API 미호출, `start_attempt` 후 `skip_attempt(skip_reason='holiday')` 호출, `runs.status='skipped'` | 없음(정상 종료) |
| 개장일 캐시 존재 | `trading_calendar`에 `is_open=true` 캐시 행 존재 | `run_candidate_stage(..., Trigger.SCHEDULE)`로 위임 | candidate_stage 기존 오류 처리 그대로 |
| 캐시 없음 | 오늘자 캐시 행 없음 | `resolve_and_cache` 1회 호출(LS 일봉 1콜) 후 위 두 분기 중 하나로 진행 | 일봉 조회 실패 시 `CALENDAR_UNAVAILABLE` → 휴장 아님으로 간주하고 정상 진행 |
| 이미 canonical 발행됨(close, replay) | `start_attempt`가 `{"replayed": true}` 반환 | candidate_stage와 동일하게 재작업 없이 종료 | 없음 |
| 장중 슬롯 스냅 | 실행 시각 KST 09:07 | `floor_to_half_hour` → 09:00 슬롯의 `LogicalRunKey` | 슬롯이 30분 경계가 아니면 항상 내림 |

</intent-contract>

## Code Map

- `apps/batch/candidate_stage.py:33-43` -- private `_attempt()` 파서를 `run_state.py`로 옮겨 `parse_attempt()`로 공개하고 여기서 재사용(동작 변경 없음).
- `apps/batch/run_state.py:40-172` -- `RunStateGateway`에 `skip()` 메서드 추가(`skip_attempt` RPC 호출), `parse_attempt()` 함수 신설.
- `apps/batch/calendar.py:14-44` -- `CalendarRepository`에 `get(trading_day) -> TradingCalendarEntry | None` 추가, 캐시 우선 조회 함수 `resolve_for_schedule()` 신설(캐시 히트 시 `resolve_and_cache`/provider 호출 안 함).
- `packages/domain/domain/calendar.py:44-65` -- 순수 함수 `floor_to_half_hour(moment: datetime) -> datetime` 추가(장중 `LogicalRunKey` 슬롯 산출용, 초/마이크로초 버림 후 분을 00/30으로 내림).
- `infra/supabase/migrations/202609011600_create_run_lineage.sql:31` -- 참고: `runs.status` check 제약에 `skipped`가 이미 포함되어 있고 `skip_reason text` 컬럼도 이미 존재하므로 스키마 변경 불필요.
- `infra/supabase/migrations/202609012300_add_skip_attempt.sql` (신규) -- `skip_attempt(p_run_id, p_fence_token, p_lease_token, p_skip_reason)` RPC 추가. `write_stage`와 동일한 fence/lease/lease_expires_at 검증 패턴(`202609012200_add_candidate_fallback_support.sql:9-19` 참고), `stage_status`는 건드리지 않고 `status='skipped', skip_reason=p_skip_reason, finished_at=now()`만 갱신. `revoke ... from public, anon, authenticated` + `grant ... to service_role`(기존 파일들의 마지막 블록 패턴 재사용).
- `apps/batch/scheduler.py` (신규) -- `run_scheduled_batch(batch_kind, now_kst, calendar_repository, calendar_provider, gateway, candidate_client, query_index=None, lease_seconds=300)`: `LogicalRunKey` 구성(intraday는 `floor_to_half_hour(now_kst).time()`을 slot으로), `resolve_for_schedule()` 호출, 휴장이면 `gateway.start_attempt()` → `parse_attempt()`(replayed 시 그대로 반환) → `gateway.skip(..., 'holiday')`, 그 외에는 `candidate_stage.run_candidate_stage(gateway, candidate_client, key, Trigger.SCHEDULE, query_index=query_index, lease_seconds=lease_seconds)`로 위임.
- `apps/batch/supabase_client.py` (신규) -- `SupabaseRpcClient`(`RpcClient` 프로토콜 구현, `POST {url}/rest/v1/rpc/{fn}`, 4xx/5xx는 `{"error": {...}}`로 변환)와 `SupabaseCalendarRepository`(`get`/`upsert`, `GET`/`POST {url}/rest/v1/trading_calendar`, `Prefer: resolution=merge-duplicates`). `apps/batch/ls_client.py`의 httpx 사용 패턴을 모델로 한다.
- `apps/batch/ls_auth.py` (신규) -- `LsOAuthTokenProvider.get_token()`: `docs/api/ls-openapi/01-oauth-auth/issue-access-token.md`의 `POST /oauth2/token`(`grant_type=client_credentials, scope=oob`)을 호출해 `access_token`을 프로세스 수명 동안 캐시.
- `apps/batch/ls_daily_bar.py` (신규) -- `LsDailyBarProvider.has_daily_bar(trading_day)`: `candidate_stage.CandidateClient`와 동일한 `.request()` 프로토콜을 받아 `t8410`(`docs/api/ls-openapi/03-domestic-stock/chart.md:216-360`)을 기준 종목 `005930`(삼성전자, 상장폐지·거래정지 위험 최소)·`gubun=2`·`sujung=Y`로 조회하고 `t8410OutBlock1`에 `date == trading_day`가 있는지로 판정.
- `apps/batch/__main__.py` (신규) -- CLI 진입점(`python -m apps.batch --batch-kind premarket|intraday|close`). 환경변수(`SUPABASE_URL`, `SUPABASE_SERVICE_ROLE_KEY`, `LS_APP_KEY`, `LS_APP_SECRET`, `LS_QUERY_INDEX`, 선택적 `LS_MAC_ADDRESS`)로 위 어댑터들을 조립해 `run_scheduled_batch()` 호출, `failed`/`CANDIDATE_SOURCES_EXHAUSTED` 결과에서만 비정상 종료 코드를 반환한다(휴장·partial은 정상 종료).
- `.github/workflows/scheduled-batch.yml` (신규) -- premarket(`30 23 * * 0-4` UTC = KST 월~금 08:30)/intraday(`0,30 0-5 * * 1-5` + `0 6 * * 1-5` UTC = KST 09:00~15:00 30분 간격)/close(`0 7 * * 1-5` UTC = KST 16:00) 3개 `schedule` 트리거 + `workflow_dispatch`(수동 테스트용). `concurrency.group: wave-double-schedule-${{ github.event.schedule }}`(cron별 그룹, `cancel-in-progress: false` — 최종 권위는 DB fence).
- `.github/workflows/test.yml:34-35` -- "Scheduler tests (Python)" 단계를 추가해 신규 테스트 파일들을 CI에 연결.

## Tasks & Acceptance

**Execution:**
- `infra/supabase/migrations/202609012300_add_skip_attempt.sql` -- `skip_attempt` RPC를 forward-only migration으로 추가한다 -- 새 상태 전이를 위한 유일한 쓰기 경로를 만든다.
- `packages/domain/domain/calendar.py`, `apps/batch/calendar.py` -- `floor_to_half_hour`와 캐시 우선 `resolve_for_schedule`을 추가한다 -- 휴장 조회의 API-미호출 계약을 보장한다.
- `apps/batch/run_state.py`, `apps/batch/candidate_stage.py` -- `skip()`/`parse_attempt()`를 추가·재사용한다 -- 오케스트레이터와 candidate stage가 동일한 attempt 파싱을 공유한다.
- `apps/batch/scheduler.py` -- 휴장/개장 분기 오케스트레이션을 구현한다 -- 이 스토리의 핵심 계약.
- `apps/batch/supabase_client.py`, `apps/batch/ls_auth.py`, `apps/batch/ls_daily_bar.py`, `apps/batch/__main__.py` -- production 어댑터와 CLI 진입점을 구현한다 -- GH Actions가 실제로 호출할 수 있는 실행 가능한 스크립트를 만든다.
- `.github/workflows/scheduled-batch.yml` -- 3개 cron 스케줄과 concurrency.group을 정의한다 -- 자동 실행 계약을 만든다.
- `.github/workflows/test.yml` -- 신규 테스트를 CI에 연결한다.
- `tests/domain/test_calendar.py` -- `floor_to_half_hour`의 경계값(정각/30분/그 사이)을 검증한다.
- `tests/batch/test_calendar.py` -- `resolve_for_schedule`의 캐시 히트(provider 미호출)/미스(provider 1회 호출 후 캐시) 경로를 검증한다.
- `tests/batch/test_scheduler.py` -- 휴장 스킵(candidate_client 미호출), 개장 위임(`Trigger.SCHEDULE`로 `run_candidate_stage` 호출), `CALENDAR_UNAVAILABLE` 시 정상 진행, replayed 처리를 검증한다.
- `tests/batch/test_supabase_client.py`, `tests/batch/test_ls_auth.py` -- `httpx.MockTransport`로 요청 형태·오류 매핑·토큰 캐시를 검증한다(`tests/batch/test_ls_client.py` 패턴 재사용).
- `tests/sql/test_skip_attempt.sql` -- clean DB에서 `skip_attempt`가 `stage_status`는 그대로 두고 `status`/`skip_reason`/`finished_at`만 갱신함을 검증한다.

**Acceptance Criteria:**
- Given `.github/workflows/scheduled-batch.yml`에 스케줄이 정의된 경우, when 파일을 읽으면, then 개장 전 1회·장중 30분 간격·종가 확정 1회(cron `0 7 * * 1-5` UTC = 16:00 KST) cron이 UTC로 기술되고 각 항목에 KST 환산 주석이 있다.
- Given 오늘자 `trading_calendar` 캐시가 `is_open=false`인 경우, when `run_scheduled_batch`를 실행하면, then LS API가 호출되지 않고 `runs.status='skipped'`, `runs.skip_reason='holiday'`가 기록된다.
- Given 오늘자 `trading_calendar` 캐시가 없는 경우, when `run_scheduled_batch`를 실행하면, then 일봉 조회가 정확히 1회만 발생하고 그 결과로 캐시가 채워진 뒤 휴장/개장 분기가 그 결과를 따른다.
- Given 스케줄 트리거로 실행되는 경우, when `runs`에 기록하면, then `trigger='schedule'`로 구분 기록된다.
- Given `CALENDAR_UNAVAILABLE`(일봉 조회 실패)인 경우, when `run_scheduled_batch`를 실행하면, then 휴장으로 간주하지 않고 `run_candidate_stage`로 정상 진행한다.

## Spec Change Log

## Review Triage Log

### 2026-09-01 — Review pass
- intent_gap: 0
- bad_spec: 0
- patch: 7: (high 1, medium 2, low 4)
- defer: 1: (high 0, medium 0, low 1)
- dismissed:
  - concurrency.group이 지연된 실행을 다음날 같은 슬롯까지 막을 수 있다는 지적 — GH Actions 기본 job timeout(6시간)이 동일 cron 재발생 간격(24시간)보다 훨씬 짧아 실제로는 발생할 수 없는 경로다.
  - workflow_dispatch 수동 실행들이 concurrency group을 공유해 서로 대기한다는 지적 — 수동 트리거 UX는 이 스펙의 Boundaries가 명시한 대로 1.10의 범위이며, workflow_dispatch는 "수동 테스트용" 편의 기능일 뿐이다.
  - LS_QUERY_INDEX가 워크플로에서는 secret으로 참조되지만 코드에서는 optional로 처리돼 조용히 빈 문자열로 진행한다는 지적 — GH Secrets는 플랫폼이 "필수"를 강제하지 않으며, 비어 있으면 기존 `run_candidate_stage`(1.5/1.6)의 LS 실패/폴백 처리가 이미 이를 걸러낸다(조용한 성공이 아니다).
  - 신규 어댑터(SupabaseRpcClient, LsOAuthTokenProvider 등)에 재시도/backoff가 없다는 지적 — TR 수준 재시도는 이미 `ls_client.py`(1.4)가 소유하며, 30분/익일 스케줄 자체가 자연스러운 재시도 주기를 제공한다. 이 스토리의 AC는 이 계층의 재시도를 요구하지 않는다.
  - 실패 알림/notification 단계가 없다는 지적 — 능동 알림(AD-10, P1 GitHub Issue)은 별도 계약이며 이 스토리의 AC에 포함되지 않는다.
  - skip_attempt가 skip_reason을 enum으로 제약하지 않는다는 지적 — `skip_reason text`는 Story 1.3부터 무제약이었고 애플리케이션 코드는 항상 'holiday'만 보낸다.
  - skip_attempt가 lease_token/lease_expires_at을 건드리지 않는다는 지적 — `reap_expired_attempts`는 `status='running'`만 조회하며 skip_attempt는 항상 'running'에서 벗어나므로 완전히 무해하다(`write_stage`의 동일 전례와 일치).
  - 종가 배치 16:00 cron의 30분 여유가 문서화되지 않았다는 지적 — 근거(15:36 확정 실측)는 이미 PRD FR-6에 기록되어 있다.
  - test_scheduler.py의 FakeRpc가 위임된 write_stage 호출을 얕게만 검증한다는 지적 — `run_candidate_stage`의 내부 RPC 시퀀스는 `test_candidate_stage.py`가 이미 충분히 검증하며, scheduler 테스트는 위임 경계만 검증하는 것이 의도된 계층 분리다.
  - tzdata가 Windows에만 스코프됐다는 지적 — Ubuntu 24.04 러너는 시스템 tzdata를 기본 제공하므로 문제가 없고, 코드는 이미 올바르게 스코프돼 있다.
  - LS 토큰이 프로세스 수명 동안 캐시되는데 실행 시간과의 관계가 검증되지 않았다는 지적 — LS 토큰 유효기간은 86400초이고 배치 실행은 NFR-7 추정상 수 분 이내로, 여유가 매우 크다.
- addressed_findings:
  - `[high]` `[patch]` `apps/batch/ls_daily_bar.py`: `response.ok`가 true인데 `t8410OutBlock1`이 없거나 배열이 아니면 `_rows()`가 조용히 빈 목록을 반환해 `has_daily_bar()`가 `False`를 반환한다 — 실거래일이 영구적으로 휴장으로 캐시될 수 있어(Story 1.2의 "조회 실패를 is_open=false로 저장하지 않는다" 불변조건 위반) 이제 그 경우 예외를 던지도록 수정한다.
  - `[medium]` `[patch]` `apps/batch/calendar.py::resolve_for_schedule`: `repository.get()` 캐시 조회 실패가 감싸이지 않아 예외가 그대로 전파된다 — 캐시 미스와 동일하게 처리해 `resolve_and_cache`로 넘어가도록 수정한다.
  - `[medium]` `[patch]` `apps/batch/scheduler.py`/`apps/batch/__main__.py`: 게이트웨이 RPC 호출(특히 휴장 분기의 `start_attempt`/`skip`)이 실패하면 원시 traceback으로 종료돼 관측성이 떨어진다 — `main()`이 구조화된 `status=failed` 로그(가능하면 `run_id`/`logical_run_key` 포함)로 마무리하도록 예외 처리를 추가한다.
  - `[low]` `[patch]` `apps/batch/__main__.py::run()`: 생성한 어댑터(SupabaseRpcClient 등)가 close()되지 않는다 — try/finally로 정리한다.
  - `[low]` `[patch]` `apps/batch/__main__.py`에 대한 테스트가 전무하다 — 필수 환경변수 검증과 종료 코드 매핑을 검증하는 `tests/batch/test_main.py`를 추가한다.
  - `[low]` `[patch]` `.github/workflows/scheduled-batch.yml`: "Determine batch kind" case문의 wildcard가 실제 schedule 이벤트에서 매치 실패 시 조용히 close로 폴백한다 — schedule 트리거인데 매치가 없으면 명시적으로 실패하도록 강화한다.
  - `[low]` `[patch]` `apps/batch/scheduler.py::run_scheduled_batch`의 `calendar_provider` 파라미터명이 실제로는 `DailyBarProvider`를 받아 `CalendarRepository`와 혼동을 준다 — `daily_bar_provider`로 이름을 바꾼다.

## Design Notes

`concurrency.group`은 스케줄 트리거 시점에는 아직 `logical_run_key`(거래일·슬롯 포함)를 알 수 없으므로 cron 문자열(`github.event.schedule`) 단위로 근사한다 — 정확한 dedup은 여전히 1.3의 DB fence가 담당하며, 이는 이미 확립된 설계(AD-3)와 일치한다. `LsDailyBarProvider`의 기준 종목(005930)은 캘린더 판정 목적일 뿐 후보 모집단과 무관하며, 유동성이 가장 높아 상장폐지·거래정지로 인한 오판 위험이 최소인 종목을 선택했다. 장중 `LogicalRunKey` 슬롯은 `intraday_slots()`(1.2, 세션 범위 나열용)를 재사용하지 않고 `floor_to_half_hour(now_kst)`로 직접 계산한다 — 스케줄러는 "지금이 몇 시 슬롯인가"만 알면 되고, 세션 전체 슬롯 열거는 이 스토리의 소비처가 아니다.

## Verification

**Commands:**
- `uv run --with pytest pytest tests/domain/test_calendar.py tests/batch/test_calendar.py tests/batch/test_scheduler.py tests/batch/test_supabase_client.py tests/batch/test_ls_auth.py tests/batch/test_run_state.py tests/batch/test_candidate_stage.py -q` -- expected: 신규·기존 테스트 전체 통과.
- `uv run --with pandas --with numpy --with pyarrow --with pytest pytest tests/domain tests/batch -q` -- expected: 기존 domain/batch 회귀 통과.
- `uv run --with pandas --with numpy --with pyarrow --with pytest pytest backtest -q` -- expected: 기존 backtest 회귀 변화 없음.
- Supabase 로컬/원격 연결로 `tests/sql/test_run_lineage.sql`, `tests/sql/test_skip_attempt.sql` 적용 -- expected: 기존 및 신규 SQL fixture 통과.
- `git diff --check` -- expected: whitespace 오류 없음.

## Auto Run Result

**요약:** 후보 모집단 자동 갱신(1.5/1.6)·배치 상태머신(1.3)·거래 캘린더(1.2)를 매 거래일 개장 전/장중 30분/종가 확정 GitHub Actions cron에 실제로 연결하는 스케줄 오케스트레이터를 구현했다. 휴장 판정은 `trading_calendar` 캐시를 먼저 조회해(API 미호출) `skip_attempt`로 종결하고, 개장일에는 기존 `run_candidate_stage`를 `Trigger.SCHEDULE`로 위임한다. Production 어댑터(Supabase RPC/테이블, LS OAuth, LS 일봉 조회)와 CLI 진입점도 함께 구현했다.

**변경 파일:**
- `infra/supabase/migrations/202609012300_add_skip_attempt.sql` -- 휴장 스킵 종결용 `skip_attempt` RPC.
- `packages/domain/domain/calendar.py` -- `floor_to_half_hour` 순수 함수 추가.
- `apps/batch/calendar.py` -- `CalendarRepository.get()`, 캐시 우선 `resolve_for_schedule()`(캐시 읽기 실패도 안전 처리).
- `apps/batch/run_state.py` -- `parse_attempt()` 공개화, `RunStateGateway.skip()` 추가.
- `apps/batch/candidate_stage.py` -- 공유 `parse_attempt` 재사용(동작 변경 없음).
- `apps/batch/scheduler.py` -- 휴장/개장 분기 오케스트레이션(`run_scheduled_batch`), `SchedulerResult`에 `run_id`/`logical_run_key` 상관관계 필드 추가.
- `apps/batch/supabase_client.py` -- `SupabaseRpcClient`, `SupabaseCalendarRepository`(PostgREST 어댑터).
- `apps/batch/ls_auth.py` -- `LsOAuthTokenProvider`(OAuth 토큰 발급·캐시).
- `apps/batch/ls_daily_bar.py` -- `LsDailyBarProvider`(t8410 기반 휴장 판정), 응답 형태가 예상과 다르면 예외를 던지도록 처리.
- `apps/batch/__main__.py` -- CLI 진입점, 어댑터 조립, 예외를 구조화된 `status=failed` 로그로 변환, 어댑터 `close()` 보장.
- `.github/workflows/scheduled-batch.yml` -- premarket/intraday/close cron 3종 + `workflow_dispatch`, schedule 매치 실패 시 명시적 실패.
- `.github/workflows/test.yml` -- "Scheduler tests (Python)" 단계 추가.
- 테스트: `tests/domain/test_calendar.py`, `tests/batch/test_calendar.py`, `tests/batch/test_scheduler.py`, `tests/batch/test_supabase_client.py`, `tests/batch/test_ls_auth.py`, `tests/batch/test_ls_daily_bar.py`, `tests/batch/test_run_state.py`, `tests/batch/test_main.py`(신규), `tests/sql/test_skip_attempt.sql`.
- `apps/batch/pyproject.toml`, `uv.lock` -- Windows 전용 `tzdata` 의존성 추가(zoneinfo용).

**리뷰 결과:** blind-hunter/edge-case-hunter/verification-gap/intent-alignment 4개 레이어를 병렬 실행했다. patch 7건(high 1, medium 2, low 4)을 이번 패스에서 모두 수정·재검증했고, defer 1건(SQL fixture가 어떤 story에서도 CI에 연결되어 있지 않음 — Story 1.3부터의 기존 패턴, frontmatter `deferred`에 기록)을 남겼다. dismissed 11건은 위 Review Triage Log에 사유와 함께 기록했다(모두 실제 결과 경로를 재확인한 뒤 근거 없음으로 판정).

**후속 리뷰 권고:** true -- patch 중 high 심각도 1건이 있어 조건을 충족(참고 점수 산식: 3×2(medium) + 1×4(low) = 10).

**검증 수행:**
- `uv run --with pytest pytest tests/domain/test_calendar.py tests/batch/test_calendar.py tests/batch/test_scheduler.py tests/batch/test_supabase_client.py tests/batch/test_ls_auth.py tests/batch/test_ls_daily_bar.py tests/batch/test_run_state.py tests/batch/test_candidate_stage.py tests/batch/test_main.py -q` → 70 passed.
- `uv run --with pandas --with numpy --with pyarrow --with pytest pytest tests/domain tests/batch -q` → 114 passed.
- `uv run --with pandas --with numpy --with pyarrow --with pytest pytest backtest -q` → 16 passed.
- `git diff --check` → whitespace 오류 없음(CRLF 경고만 존재, 기존 저장소 관례와 동일).
- `tests/sql/test_run_lineage.sql`, `tests/sql/test_skip_attempt.sql` → 이 샌드박스에 `psql`/`supabase` CLI가 없어 실행하지 못함(defer 항목으로 기록). SQL은 `write_stage`/`start_attempt`의 fence/lease 검증 패턴을 그대로 따르도록 수기 검토했다.

**잔여 위험:**
- SQL fixture가 CI에 연결되지 않아 `skip_attempt`의 fence/lease/터미널 상태 가드가 자동 검증 경로 밖에 있다(defer 기록됨, Story 1.3부터의 기존 패턴).
- production Supabase/LS 자격증명으로 실제 GitHub Actions 실행은 아직 검증되지 않았다(GH Secrets 설정은 이 스토리 범위 밖).
- `concurrency.group`은 cron 문자열 근사치이며 정확한 dedup은 여전히 DB fence(1.3)에 의존한다(설계상 의도된 근사, Design Notes에 기록).
