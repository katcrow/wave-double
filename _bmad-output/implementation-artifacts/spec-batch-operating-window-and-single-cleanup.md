---
title: '배치 운영시간 가드와 용량관리 스케줄 단일화'
type: 'bugfix'
created: '2026-10-02'
status: 'done'
baseline_commit: 'ecf631cc6e8e349c4f8da09742ce0483fb724836'
review_loop_iteration: 1
context: []
---

<frozen-after-approval reason="human-owned intent — do not modify unless human renegotiates">

## Intent

**Problem:** GitHub Actions의 19:40 close 예약 이벤트가 지연되어 10월 1일 01:30 KST에 실행되었고, 실행 시각을 재검사하지 않아 장외 배치가 후보·수급·Outcome 파이프라인을 시작했다. 또한 자동 배치 스케줄이 GitHub schedule과 Supabase pg_cron에 중복되고, 용량관리도 GitHub workflow와 Supabase pg_cron에 중복되어 있다.

**Approach:** 자동 배치 발화는 Supabase pg_cron outbox 경로 하나로 유지하고 GitHub workflow는 workflow_dispatch 전용으로 바꾼다. CLI와 DB 경계에 KST 운영시간 가드를 추가해 예약 실행은 08:00~20:00 안에서만 허용하고, close는 19:30~20:00 안에서만 허용한다. 용량관리는 Supabase pg_cron의 00:00 KST 작업만 남긴다.

## Boundaries & Constraints

**Always:** close 19:40 실행은 허용한다. manual 실행은 기존 수동 테스트 계약을 보존한다. 장외 예약 실행은 attempt를 생성하거나 후보/태그/수급/Outcome 데이터를 쓰지 않고 명확한 차단 결과를 남긴다. 비밀값은 로그·문서·커밋에 노출하지 않는다.

**Never:** GitHub Actions의 지연된 schedule 이벤트를 자동 배치 실행 경로로 신뢰하지 않는다. Outcome 저장 계약이나 후보 선정 규칙을 변경하지 않는다. 용량관리에서 outcome_events, outcome_observations, candidate_outcome을 삭제 대상으로 확장하지 않는다.

## I/O & Edge-Case Matrix

| Scenario | Input / State | Expected Output / Behavior | Error Handling |
|----------|--------------|---------------------------|----------------|
| 정상 장중 | 예약 intraday, KST 08:00~19:59 | 배치가 기존 pipeline으로 진행 | N/A |
| 정상 close | 예약 close, KST 19:30~19:59 | close가 publish/Outcome 경로로 진행 | N/A |
| 지연 예약 | 예약 close/intraday, KST 20:00 이후 또는 08:00 이전 | 배치 차단, attempt 미생성 | `SCHEDULE_OUTSIDE_OPERATING_WINDOW` |
| 수동 실행 | manual trigger, 운영시간 외 포함 | 기존 수동 계약대로 실행 | 기존 오류 계약 유지 |
| 용량관리 | Supabase pg_cron 00:00 KST | `purge_old_attempt_data(7)` 1회 실행 | GitHub cleanup workflow는 실행되지 않음 |

</frozen-after-approval>

## Code Map

- `.github/workflows/scheduled-batch.yml` -- 현재 intraday/close GitHub schedule과 workflow_dispatch 입력 분기. schedule 제거 및 수동 디스패치 전용 전환 대상.
- `.github/workflows/nightly-cleanup.yml` -- GitHub 용량관리 중복 경로. 삭제 대상.
- `apps/batch/__main__.py` -- CLI 진입점. 예약 실행의 KST 운영시간 사전 차단과 테스트 연결 대상.
- `apps/batch/scheduler.py` -- 배치 종류와 logical run key를 조합하는 오케스트레이터. 운영시간 정책의 재사용 가능한 순수 함수 위치.
- `tests/batch/test_main.py` -- CLI trigger 전달 회귀망. 장외 예약 차단 및 장중/수동 허용 테스트 추가 대상.
- `tests/batch/test_scheduler.py` -- 기존 후보·태그·수급·publish 회귀망. 운영시간 정책 함수의 경계 테스트를 별도 추가.
- `tests/sql/test_batch_operating_window.sql` -- runs/dispatch_request DB trigger와 manual 예외의 실제 SQL fixture.
- `infra/supabase/migrations/202609211200_switch_intraday_start_to_08_10.sql` -- 운영 스케줄의 권위 있는 KST 08:10~19:10 intraday/19:40 close 계약.
- `infra/supabase/migrations/202609161100_schedule_purge_old_attempt_data_cron.sql` -- 유지할 Supabase 00:00 KST 용량관리 cron.
- `infra/supabase/migrations/202610021000_enforce_batch_operating_window.sql` -- 예약 run/자동 dispatch가 장외에서 DB에 진입하지 못하도록 추가할 forward-only trigger guard.

## Tasks & Acceptance

**Execution:**
- [x] `.github/workflows/scheduled-batch.yml` -- `on.schedule`를 제거하고 workflow_dispatch 전용으로 전환하며, schedule 입력이 남아도 close 기본값으로 fallback하지 않게 한다.
- [x] `.github/workflows/nightly-cleanup.yml` -- GitHub 중복 용량관리 workflow를 제거해 Supabase pg_cron만 남긴다.
- [x] `apps/batch/scheduler.py`, `apps/batch/__main__.py` -- 예약 실행 운영시간 정책을 구현하고 장외 실행을 side-effect 전에 차단한다.
- [x] `tests/batch/test_main.py`, `tests/batch/test_scheduler.py` -- 08:00/20:00 및 close window 경계, manual 예외, 차단 결과를 검증한다.
- [x] `infra/supabase/migrations/202610021000_enforce_batch_operating_window.sql` -- `runs`와 자동 scheduler dispatch의 DB 경계에 예약 시간 trigger를 추가한다.

**Acceptance Criteria:**
- Given 01:30 KST에 지연된 close schedule, when workflow/CLI/DB 경계를 통과하려 하면, then 후보·태그·수급·Outcome attempt 없이 `SCHEDULE_OUTSIDE_OPERATING_WINDOW`로 차단된다.
- Given KST 08:10~19:10 intraday 또는 19:40 close, when Supabase 자동 scheduler가 dispatch하면, then 기존 batch pipeline이 정상 실행된다.
- Given manual trigger, when 운영시간 밖에서 실행하면, then 운영시간 guard가 manual을 차단하지 않는다.
- Given 새벽 00:00 KST, when cron이 실행되면, then Supabase `purge_old_attempt_data(7)`만 실행되고 GitHub cleanup workflow 실행은 존재하지 않는다.
- Given migration 적용 후, when catalog/cron/job/function과 Actions workflow를 확인하면, then DB guard가 존재하고 자동 배치 schedule은 Supabase pg_cron 단일 경로이며 용량관리 cron은 하나다.

## Design Notes

GitHub schedule 이벤트는 예약된 cron 문자열을 유지한 채 실제 실행이 수시간 늦어질 수 있으므로, workflow 파일 제거만으로는 이미 대기 중인 이벤트를 보호할 수 없다. 따라서 Python 사전 가드와 DB `runs` INSERT 가드를 함께 둔다. Supabase 자동 dispatch는 현재 운영 DB에 적용된 08:10~19:10 intraday/19:40 close 계약을 유지하고, GitHub workflow는 outbox worker가 호출하는 `workflow_dispatch`만 수용한다.

## Verification

**Commands:**
- `uv run --with pytest pytest tests/batch/test_main.py tests/batch/test_scheduler.py -q` -- 관련 Python 회귀 테스트 통과.
- `uv run --with pytest pytest` -- 1002 passed; 기존 sprint-status fixture/PyYAML 환경 문제 3건은 변경 범위 밖에서 실패.
- `git diff --check` -- 공백 오류 없음.
- Supabase Management API targeted SQL -- migration 적용, trigger/function/catalog/cron 확인.
- GitHub Actions API -- 로컬 workflow 변경은 확인했으며, 원격 기본 브랜치 반영과 Actions 실행 증거는 push 이후 확인 대상으로 deferred.

## Review Triage Log

- **Patched:** outbox의 저장된 `logical_run_key` 전달, 운영 DB의 `:10` 슬롯과 Python/domain/web validator 정합성, strict `dispatch_trigger`, 장외 outbox 사전 종결, CLI/DB 운영시간 guard, aware datetime 변환, `clock_timestamp()`, SQL fixture와 경계 테스트, migration catalog provenance를 반영했다.
- **Dismissed:** 운영 catalog에서 확인되지 않은 이름의 추가 cleanup job, 이미 종료됐거나 실행 중일 수 있는 과거 GitHub cleanup run의 소급 취소, 과거 migration의 역사적 comment 정리는 현재 acceptance 범위가 아니며 live evidence와 충돌하지 않는다.
- **Deferred:** GitHub 기본 브랜치에 변경을 push하고 Actions/Vercel 실행 증거를 갱신하는 작업은 원격 변경 승인이 별도이므로 로컬 commit 이후 사용자 확인 대상으로 남겼다.

## Suggested Review Order

**자동 발화와 logical run 계보**

- outbox key를 보존해 지연 실행이 다른 거래일로 재계산되지 않게 한다.
  [`scheduler.py:98`](../../apps/batch/scheduler.py#L98)

- GitHub workflow는 Supabase outbox의 명시된 key와 trigger만 수용한다.
  [`scheduled-batch.yml:6`](../../.github/workflows/scheduled-batch.yml#L6)

- worker는 장외 자동 요청을 GitHub 호출 전에 terminal 처리한다.
  [`route.ts:86`](../../apps/web/app/api/dispatch/worker/route.ts#L86)

**운영시간 방어선과 DB 계약**

- CLI가 외부 client와 attempt 생성 전에 KST window를 검사한다.
  [`__main__.py:58`](../../apps/batch/__main__.py#L58)

- runs와 system scheduler dispatch의 INSERT 경계를 DB에서 재검사한다.
  [`202610021000_enforce_batch_operating_window.sql:10`](../../infra/supabase/migrations/202610021000_enforce_batch_operating_window.sql#L10)

- 장외 outbox를 attempt 없이 terminal failed로 닫는 RPC를 확인한다.
  [`202610021000_enforce_batch_operating_window.sql:62`](../../infra/supabase/migrations/202610021000_enforce_batch_operating_window.sql#L62)

**검증과 운영 단일화**

- 실제 trigger 예외와 manual 우회를 SQL fixture로 검증한다.
  [`test_batch_operating_window.sql:1`](../../tests/sql/test_batch_operating_window.sql#L1)

- KST 경계와 outbox worker의 자동 dispatch 판단을 회귀 테스트한다.
  [`test_main.py:220`](../../tests/batch/test_main.py#L220)

- 용량관리는 active pg_cron의 단일 purge job만 유지한다.
  [`202609161100_schedule_purge_old_attempt_data_cron.sql:15`](../../infra/supabase/migrations/202609161100_schedule_purge_old_attempt_data_cron.sql#L15)
