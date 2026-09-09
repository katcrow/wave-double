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
| 202609021100_schedule_dispatch_worker_cron | **미적용(의도적)** | 확장은 설치 가능하지만 배포 도메인·secret이 어디에도 없다. 아래 3절 참고 |

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

## 3. worker cron — 미적용 상태와 남은 사람 작업 (2026-09-09 재조사)

`202609021100_schedule_dispatch_worker_cron.sql`은 운영에 적용하지 않았다. 처음에는 "확장이
없다"로만 파악했지만, `.env.local`과 Supabase 설정을 다시 조사해 정확한 차단 사유를 확정했다.

### 확장은 문제가 아니다 (설치 가능)

| 확장 | 사용 가능 버전 | 설치 상태 |
| --- | --- | --- |
| `pg_cron` | 1.6.4 | 미설치 |
| `pg_net` | 0.20.4 | 미설치 |

`pg_available_extensions` 실측 결과 둘 다 이 프로젝트에서 설치할 수 있다. 즉 확장 가용성은
차단 요인이 아니다.

### 진짜 차단 요인: 배포 도메인이 어디에도 없다

`app.settings.dispatch_worker_url`에 넣을 배포 도메인을 세 곳에서 찾지 못했다.

- 저장소: 배포 워크플로우도, 도메인을 담은 설정 파일도 없다(Vercel git 연동 추정).
- `.env.local`: 도메인을 담는 키 자체가 없다.
- Supabase auth 설정(Management API `/config/auth`): `site_url`이 아직
  **`http://localhost:3000`**이고 `uri_allow_list`는 빈 문자열이다.

Supabase auth가 여전히 localhost를 가리킨다는 것은 웹 앱이 실제로 배포되지 않았거나 배포
도메인이 어느 시스템에도 등록되지 않았음을 뜻한다. 잘못된 URL로 확장을 켜면 운영에 매 1분
실패하는 cron job이 남으므로 적용하지 않았다.

### `.env.local`의 빈 값 5개

`.env.local`에는 필요한 **키가 모두 선언돼 있지만 값이 빈 것이 5개**다. 키 존재만으로
"설정됨"으로 오판하기 쉬운 지점이라 명시해 둔다.

| 키 | 값 | 이 값이 없으면 |
| --- | --- | --- |
| `CRON_CALLBACK_SECRET` | 빈 문자열 | worker route가 `x-cron-secret`을 비교할 기준이 없어 모든 요청이 401 |
| `INTERNAL_CRON_SECRET` | 빈 문자열 | 미사용 별칭(위 키와 같은 용도) |
| `GITHUB_DISPATCH_TOKEN` | 빈 문자열 | worker가 workflow_dispatch/Issue 생성을 못 한다(`MISSING_GITHUB_CONFIGURATION`) |
| `GITHUB_REPO_OWNER` | 빈 문자열 | 동일 |
| `GITHUB_REPO_NAME` | 빈 문자열 | 동일 |

즉 cron을 켜도 **수동 dispatch 경로는 아직 끝까지 동작할 수 없다** — 깨우는 쪽(cron+secret)과
깨어난 뒤 호출하는 쪽(GitHub 토큰/저장소) 양쪽이 비어 있다.

### 필요한 것 (Neo 제공)

1. 배포 도메인 — `https://<도메인>/api/dispatch/worker`가 실제로 응답해야 한다.
2. `CRON_CALLBACK_SECRET` 값 — 임의의 긴 난수. `.env.local`, 호스팅 환경변수,
   `app.settings.cron_callback_secret` 세 곳에 같은 값을 넣는다.
3. `GITHUB_DISPATCH_TOKEN`(Actions: Read/Write + Issues: Read/Write), `GITHUB_REPO_OWNER`,
   `GITHUB_REPO_NAME`.

세 가지가 확보되면 남은 적용은 다음 순서다.

```sql
-- 1) 설정을 먼저 넣는다(비어 있으면 net.http_post가 매 분 실패한다)
alter database postgres set app.settings.dispatch_worker_url = 'https://<배포도메인>/api/dispatch/worker';
alter database postgres set app.settings.cron_callback_secret = '<CRON_CALLBACK_SECRET과 동일한 값>';
-- 2) 그 다음 202609021100 migration을 적용한다(확장 생성 + cron.schedule)
```

곁들여 확인할 것: Supabase auth `site_url`/`uri_allow_list`도 배포 도메인으로 갱신해야
로그인 리다이렉트가 성립한다(현재 localhost).

대안(확장을 켜지 않는 경로): 배포 도메인을 저장소 secret으로 등록하고 GitHub Actions cron이
`/api/dispatch/worker`를 `x-cron-secret`으로 깨운다. Vercel Hobby의 1분 cron 미지원 제약을
우회하려고 pg_cron을 택한 것이므로(AD-18), 5분 간격을 수용할 수 있으면 이쪽이 운영이 간단하다.

### 현재 상태의 실질적 영향

**스케줄 배치는 정상이다** — `scheduled-batch.yml`의 cron이 직접 구동한다. 영향을 받는 것은
`request_manual_dispatch`로 큐잉된 **수동 dispatch**뿐이며, worker가 깨어나지 않으므로
`queued`에 머문다.

## 4. probe 중 발견해 수정한 결함

`apps/web/app/api/dispatch/worker/route.ts`의 `WORKFLOW_REF`가 `"main"`으로 하드코딩돼 있었다.
이 저장소의 default branch는 `master`이고 원격에 `main`은 없다(`origin/master`만 존재). 즉 worker가
깨어나더라도 workflow_dispatch가 `GITHUB_HTTP_422`로 실패하고, 그 실패가
`shouldDeadLetterAfterDispatchFailure` 경로를 타 수동 dispatch가 `dead_letter`로 닫혔을 것이다.

조치: ref 결정을 `lib/dispatch-outbox-worker.ts`의 순수 함수 `resolveWorkflowRef()`로 추출하고
기본값을 `master`로 바로잡았다(`GITHUB_DISPATCH_REF`로 덮어쓰기 가능). 회귀 테스트 5개를
`lib/dispatch-outbox-worker.test.ts`에 추가했다 — 기본값이 `master`인지, `main`이 아닌지,
환경변수 우선/공백 처리까지 고정한다.

## 5. 배포 gate(item-15)를 운영 토큰으로 실제 실행하며 발견한 결함 2건

`.env.local`의 `SUPABASE_ACCESS_TOKEN`으로 `--gate`를 처음 끝까지 돌려보고 나서야 드러난
것들이다. 오프라인 테스트로는 잡히지 않는 live 경로였다.

1. **User-Agent 누락으로 항상 403.** `api.supabase.com`은 Cloudflare 뒤에 있고 기본
   User-Agent(urllib 등)를 `error code: 1010`과 함께 차단한다. 토큰이 유효해도 403이 오므로
   "토큰이 만료됐다"고 오진하게 된다(실제로 이 세션에서 그렇게 오판해 토큰에 권한이 없다고
   보고했다). `USER_AGENT`를 명시해 해결했고, 같은 토큰으로 `--gate`가 통과한다.
2. **다중 원소 `search_path`를 live에서 못 읽어 영구 WARN 6건.** `pg_proc.proconfig`는
   값에 쉼표가 있으면 원소를 따옴표로 감싼다(`{"search_path=pg_catalog, public"}`). 이전
   파서는 먼저 쉼표로 쪼개서 접두사를 검사했기 때문에 이 형태를 놓쳤고, `pg_catalog, public`
   으로 통일한 함수(epic-4-retro-item-33)마다 매 실행 WARN이 떴다. 노이즈가 진짜 drift를
   가리는 상태였다. `parse_live_search_path()`로 분리하고 회귀 테스트를 추가했다.

두 결함을 고친 뒤 `python tools/check_production_parity.py --gate`가 운영 실측 대비
**0 ERROR / 0 WARN**이고, 커밋된 baseline도 live 조회로 재생성해 손으로 만든 스냅샷과
동일함을 확인했다.
