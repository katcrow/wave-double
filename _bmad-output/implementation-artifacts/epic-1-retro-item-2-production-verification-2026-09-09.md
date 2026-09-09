# epic-1-retro-item-2 — 운영 Supabase 202609012200~202609021100 적용·검증 결과

- 대상 프로젝트: `qqhjeumlecaudsiqhhdu` (wave-double, dev/staging 없는 단일 운영 프로젝트)
- 검증일: 2026-09-09
- 검증 수단: supabase MCP `execute_sql` (읽기 조회 + `begin` … `rollback`으로 감싼 계약 probe)

## 1. migration 적용 상태 (실측)

`supabase_migrations.schema_migrations` 및 `pg_proc`/`information_schema` 실측 결과:

| 로컬 migration | 운영 반영 | 근거 |
| --- | --- | --- |
| 202609012200_add_candidate_fallback_support | 적용됨 | `epic1_fix_add_run_lineage_and_dashboard_snapshot` 스쿼시. 9-param `write_stage`(p_fallback_used)가 운영에 존재하고 `fallback_used` 기록이 동작 |
| 202609012300_add_skip_attempt | 적용됨 | 운영명 `add_skip_attempt_rpc`. `skip_attempt` 함수 존재 및 호출 성공 |
| 202609020000_create_dashboard_snapshot | 적용됨 | `get_dashboard_snapshot` 존재, `logical_runs`/`runs` RLS 활성(4/4) |
| 202609021000_create_dispatch_outbox | 적용됨 | `dispatch_request`/`dispatch_outbox` 테이블 2/2, 인덱스 2/2, RPC 5/5 |
| 202609021100_schedule_dispatch_worker_cron | **미적용(의도적)** | 운영에 `pg_cron`/`pg_net` 확장 0개. 아래 3절 참고 |

범위 내 함수 9종(`write_stage`, `write_candidates`, `skip_attempt`, `get_dashboard_snapshot`,
`request_manual_dispatch`, `claim_dispatch_outbox`, `advance_dispatch_outbox`,
`record_dispatch_receipt`, `reconcile_dispatch_outbox`)이 모두 운영 `public` 스키마에 존재한다.

## 2. RPC fixture probe 결과 — PASS

운영 프로젝트에서 `begin` … `rollback`으로 감싼 계약 probe를 실행했다(운영 상태 무변경).
검증 항목과 결과:

- `get_dashboard_snapshot()` — `result_code=OK`, `latest_attempt`/`complete_snapshot` 계약 키 존재.
  실측 응답은 운영 published attempt `c6ea80aa-91fe-4468-8dc1-2d7766b0cf9d`
  (`close:2026-09-09`, 전 stage success)를 반환했다.
- `request_manual_dispatch(...)` — 신규 요청이 `status=queued`/`reason=created`로 수락되고
  `dispatch_outbox` 행이 `queued`로 생성된다.
- 같은 idempotency key + 같은 payload hash 재요청 — `reason=replayed`(중복 행 없음).
- `claim_dispatch_outbox()` — queued 행을 claim해 비어 있지 않은 배열을 반환한다.
- `start_attempt` → `heartbeat_attempt` → `write_stage(pending→running→partial, fallback_used=true)`
  — 응답의 `fallback_used=true`로 202609012200 계약이 운영에서 성립함을 확인.
- `skip_attempt(...)` — running attempt에서 정상 종결.

최종 verdict row: `epic-1-retro-item-2 | PASS | cron_extensions=0`.

부수적으로 probe 과정에서 확인된 정상 동작 두 가지(결함 아님):
`write_stage`가 `candidates`를 `partial`로 닫으면 run이 `partial`이 되어 이후 `skip_attempt`가
`STALE_FENCE_OR_LEASE`로 거부되고, `trading_day`/`logical_run_key` 불일치도 거부된다.

## 3. worker cron — 미적용 상태와 그 이유 (남은 사람 작업)

`202609021100_schedule_dispatch_worker_cron.sql`은 운영에 적용하지 않았다.

- 운영에 `pg_cron`/`pg_net` 확장이 설치돼 있지 않다(실측 0개).
- 이 migration은 그 자체로 완결되지 않는다 — `app.settings.dispatch_worker_url`(배포 도메인)과
  `app.settings.cron_callback_secret`을 함께 설정해야 하고, 둘이 비면 `net.http_post`가 매 1분
  실패한다. 이 저장소와 `.env.local`에는 **배포 도메인이 기록돼 있지 않다**(`CRON_CALLBACK_SECRET`은
  있음). 잘못된 URL로 확장을 설치하면 운영에 매 1분 실패하는 cron job이 남는다.

따라서 이 조각은 사람 작업으로 남긴다. 필요한 조치는 다음 두 가지 중 하나다.

1. (설계 원안, AD-18) 운영에서 `pg_cron`/`pg_net`을 켜고 아래를 실행한 뒤 이 migration을 적용한다.
   ```sql
   alter database postgres set app.settings.dispatch_worker_url = 'https://<배포도메인>/api/dispatch/worker';
   alter database postgres set app.settings.cron_callback_secret = '<CRON_CALLBACK_SECRET과 동일한 값>';
   ```
2. 배포 도메인을 저장소 secret으로 등록하고 GitHub Actions cron이 `/api/dispatch/worker`를
   `x-cron-secret`으로 깨우게 한다(Vercel Hobby의 1분 cron 미지원 제약을 우회하는 대안).

현재 상태의 실질적 영향: **스케줄 배치는 정상이다**(`scheduled-batch.yml`의 cron이 직접
구동한다). 영향을 받는 것은 `request_manual_dispatch`로 큐잉된 **수동 dispatch**뿐이며, worker가
깨어나지 않으므로 `queued`에 머문다.

## 4. probe 중 발견해 수정한 결함

`apps/web/app/api/dispatch/worker/route.ts`의 `WORKFLOW_REF`가 `"main"`으로 하드코딩돼 있었다.
이 저장소의 default branch는 `master`이고 원격에 `main`은 없다(`origin/master`만 존재). 즉 worker가
깨어나더라도 workflow_dispatch가 `GITHUB_HTTP_422`로 실패하고, 그 실패가
`shouldDeadLetterAfterDispatchFailure` 경로를 타 수동 dispatch가 `dead_letter`로 닫혔을 것이다.

조치: ref 결정을 `lib/dispatch-outbox-worker.ts`의 순수 함수 `resolveWorkflowRef()`로 추출하고
기본값을 `master`로 바로잡았다(`GITHUB_DISPATCH_REF`로 덮어쓰기 가능). 회귀 테스트 5개를
`lib/dispatch-outbox-worker.test.ts`에 추가했다 — 기본값이 `master`인지, `main`이 아닌지,
환경변수 우선/공백 처리까지 고정한다.
