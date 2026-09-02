---
title: '인증 & 수동 트리거'
type: 'feature'
created: '2026-09-02'
status: 'done'
baseline_revision: '7832f653702d3ef272a98d3f944662700444ed39'
review_loop_iteration: 1
followup_review_recommended: true
context:
  - '{project-root}/_bmad-output/planning-artifacts/architecture/architecture-wave-double-2026-08-31/ARCHITECTURE-SPINE.md'
warnings: [oversized]
deferred:
  - summary: >-
      tests/sql/test_dispatch_outbox.sql이 CI에 연결되지 않아 자동 회귀 검증이 없다.
    evidence: |-
      .github/workflows/test.yml에는 psql/Postgres를 실행하는 스텝이 전혀 없다. story 1.8부터
      이어진 프로젝트 전역의 기존 공백이며, 로컬 개발 환경에도 psql/docker/Postgres가 없어
      이번 세션에서 SQL fixture를 직접 실행해 검증하지 못했다.
    location: >-
      tests/sql/test_dispatch_outbox.sql, .github/workflows/test.yml
    severity: medium
  - summary: >-
      새 server-only 환경변수는 실제로 .env.local(gitignored)에 "Story 1.10" 섹션으로
      이미 문서화돼 있다 -- 리뷰 2개 패스의 "문서화가 없다"는 지적은 부정확했다(리뷰
      에이전트가 gitignored 파일을 열어보지 않고 리포 전체 grep만으로 판단한 결과로
      보인다). 남은 실질적 gap은 커밋되는 .env.example이 없어 신규 환경(다른 개발자,
      CI, 다른 배포 대상)에서는 이 목록을 볼 수 없다는 점뿐이다.
    evidence: |-
      .env.local을 직접 열어 확인한 결과 OPERATOR_ALLOWLIST/GITHUB_DISPATCH_TOKEN/
      CRON_CALLBACK_SECRET/GITHUB_REPO_OWNER/GITHUB_REPO_NAME/SUPABASE_JWKS_URL/
      SUPABASE_JWT_ISSUER/SUPABASE_SERVICE_ROLE_KEY가 전부 "Story 1.10" 주석 섹션
      아래 나열돼 있고, 코드가 읽는 이름과 정확히 일치한다(구현 서브에이전트가 이번
      세션에서 추가). 다만 이 파일에 story 1.10 이전부터 있던 미사용 `INTERNAL_CRON_SECRET`
      (어떤 코드도 참조하지 않음)과 신규 `CRON_CALLBACK_SECRET`이 같은 용도를 가리키는
      두 개의 이름으로 공존한다 -- 주석으로 "같은 값을 쓴다"고만 안내할 뿐 코드로 통합
      되어 있지 않아 향후 혼동 소지가 있다. 이 리포에는 .env.example 자체가 story 1.10
      이전부터 없었다(gitignore된 .env.local만 존재).
    location: >-
      .env.local(미버전관리), apps/web/lib/supabase-service.ts, apps/web/app/api/dispatch/worker/route.ts
    severity: low
---

<intent-contract>

## Intent

**Problem:** `/`의 수동 실행 버튼은 항상 `disabled`이고 public 리포지토리의 배치 실행 경로에 인증이 전혀 없어, Neo가 브라우저에서 배치를 즉시 재실행할 수 없고 비인가 실행/secret 노출 위험을 막을 장치도 없다(AD-7/AD-18).
**Approach:** Supabase Auth email OTP/magic link 단일 운영자 세션 + server-side allowlist를 추가하고, `dispatch_request`/`dispatch_outbox` 테이블과 idempotent dispatch RPC로 인증된 POST를 큐에 적재한 뒤, `pg_cron`이 매 1분 `pg_net`으로 깨우는 Next.js server-only outbox worker route가 `scheduled-batch.yml`을 `workflow_dispatch`하고 상태를 추적한다.

## Boundaries & Constraints

**Always:** 브라우저는 publishable key + RLS `SELECT`만 가진다. dispatch route(`POST /api/dispatch`)는 JWKS 서명/issuer/audience/expiry/sub 검증, `SameSite=Strict` double-submit CSRF, 사용자별 rate limit을 통과해야 하며, 통과 후 단일 DB RPC로 `dispatch_request`+`dispatch_outbox`를 원자적으로 생성한다. 같은 `idempotency_key`+`payload_hash`는 기존 `dispatch_request_id`를 replay하고, 같은 key+다른 hash는 `409`다. 대상 `logical_run_key`에 이미 `active_attempt_run_id`가 있으면(스케줄 진행 중 포함) 새 dispatch를 `409`로 거부하고 기존 attempt의 `run_id`/`started_at`/`trigger`를 응답에 포함한다(1.3 fence 모델과 일관 -- `start_attempt`의 supersede 분기는 재사용하지 않는다, `infra/supabase/migrations/202609011600_create_run_lineage.sql:102-105`). outbox worker는 `FOR UPDATE SKIP LOCKED`+만료 lease로 claim하고 `queued→accepted→started→completed|failed|dead_letter`로만 전이한다 -- **`started`는 종결 상태가 아니다**: 배치가 실제로 끝나면(연결된 `runs.run_id`의 `status`가 `published|partial|skipped`면 `completed`, `failed|superseded|cancelled`면 `failed`) outbox worker가 매 tick마다 `started` 행을 이 기준으로 `completed`/`failed`로 닫는다(폴링 대상이며, receipt 폴링과 별개 경로). `queued` 상태에서 GitHub dispatch 호출 자체가 반복 실패하는 경우에도 receipt 미도달과 동일한 시도 횟수 상한을 적용해 결국 `dead_letter`로 전이해야 한다(무한 재시도 금지 -- `claim_dispatch_outbox`의 `attempts` 카운터는 `queued`에서의 dispatch 재시도와 `accepted`에서의 receipt 폴링 재시도를 하나로 합산해도 되지만, 어느 쪽이든 상한에 닿으면 반드시 `dead_letter`로 닫혀야 한다). `dead_letter` 전이 시 AD-10 계약대로 GitHub Issue를 생성하고, 생성 호출의 실패(`!response.ok`/예외)는 로그로 남긴다(secret은 남기지 않는다) -- 실패해도 outbox 상태 전이 자체는 유지한다(재시도로 상태를 되돌리지 않는다). GitHub PAT/워커 공유 secret은 server-only 환경변수(`GITHUB_DISPATCH_TOKEN`, `CRON_CALLBACK_SECRET`)로만 존재하고 `NEXT_PUBLIC_*`에 두지 않으며, `CRON_CALLBACK_SECRET` 비교는 CSRF 검증과 동일하게 `timingSafeEqual`을 쓴다(길이 우선 비교 후 상수시간 비교). 수동 트리거로 생성된 `runs.trigger`는 `manual`이다. 수동 실행 버튼이 요청하는 `batch_kind`/`logical_run_key`는 `latest_attempt.batch_kind`(대시보드 스냅샷에 이미 존재, `apps/web/lib/dashboard-types.ts`)에서 도출한다 -- `latest_attempt`가 없을 때만 `close`로 대체한다(하드코딩 금지: 재실행 대상은 마지막으로 실행/실패한 배치와 같아야 한다). `request_manual_dispatch`는 `p_trading_day`가 `p_logical_run_key`에 내포된 날짜와 일치하는지 검증하고 불일치 시 예외를 낸다.
**Never:** 새 npm/pip 의존성을 추가하지 않는다(GitHub API는 fetch 직접 호출). Supabase Edge Function(Deno)을 신설하지 않는다 -- 이 리포는 지금까지 `apps/web`(Next.js server route)만을 유일한 server-only 런타임으로 써왔고 planning 문서 어디에도 Edge Function 언급이 없으므로, outbox worker도 Next.js route handler로 둔다(설계 근거는 Design Notes 참고). `/runs`/`/` UI의 카드·패널·필터를 추가하지 않는다(Epic 1 범위 아님). LS token/GitHub token을 로그·워크플로 출력에 남기지 않는다.

## I/O & Edge-Case Matrix

| Scenario | Input / State | Expected Output / Behavior | Error Handling |
|----------|--------------|---------------------------|----------------|
| 미인증 접속 | 세션 쿠키 없음 | `/`는 로그인 화면으로 리다이렉트, allowlist 밖 사용자는 OTP 검증 성공해도 dispatch 거부 | `403`(allowlist), 리다이렉트(무세션) |
| 정상 dispatch | 인증됨, CSRF 유효, 활성 attempt 없음 | `dispatch_request`+`dispatch_outbox(queued)` 생성, `202` | 없음 |
| 재요청(같은 key+hash) | 동일 idempotency_key/payload_hash | 기존 `dispatch_request_id` replay, 새 행 없음 | 없음(idempotent 성공) |
| 재요청(같은 key+다른 hash) | 동일 key, 다른 payload | 신규 생성 거부 | `409` |
| 활성 attempt 존재 | 대상 logical_run_key에 `active_attempt_run_id` 있음 | 신규 dispatch 거부, 기존 attempt 정보 반환 | `409` |
| CSRF/rate limit 실패 | 토큰 불일치 또는 한도 초과 | dispatch 미생성 | `403`/`429` |
| outbox lease 만료(receipt 없음) | `accepted` 상태에서 lease 만료, receipt 미도달 | 재발송 없이 receipt 폴링 재시도, 일정 시간 초과 시 `dead_letter` | GitHub Issue 생성(AD-10) |
| 배치 정상 종료 | outbox `started` + 연결된 `runs.status`가 `published/partial/skipped` | outbox가 `completed`로 전이 | 없음 |
| 배치 실패 종료 | outbox `started` + 연결된 `runs.status`가 `failed/superseded/cancelled` | outbox가 `failed`로 전이 | 없음 |

</intent-contract>

## Code Map

- `apps/web/lib/dashboard-types.ts:25,36,53,86` -- `DashboardSnapshot.latest_attempt.batch_kind`(및 `complete_snapshot.sections.*.batch_kind`)가 이미 노출돼 있다. 수동 실행 버튼은 이 값을 읽어 재실행 대상 `batch_kind`를 정한다(하드코딩 금지).
- `infra/supabase/migrations/202609011600_create_run_lineage.sql:runs.status` -- `running|ready_to_publish|published|partial|failed|skipped|superseded|cancelled` CHECK. `published|partial|skipped`는 종결-성공류, `failed|superseded|cancelled`는 종결-실패류로 간주해 outbox `completed`/`failed` 매핑에 쓴다(`running`/`ready_to_publish`는 미종결).
- `infra/supabase/migrations/202609011600_create_run_lineage.sql`, `202609012100_harden_run_and_candidate_contracts.sql` -- `logical_runs`/`runs` fence(`fence_token bigint`)/lease(`lease_token uuid`, `lease_expires_at`) 패턴과 `start_attempt` RPC(`202609011600` 71-115행) 원본. 신규 dispatch RPC는 이 fence 검증 관용구를 그대로 따르되, `start_attempt`의 supersede 분기(102-105행)는 호출하지 않고 별도 읽기전용 가드로 409를 판정한다.
- `infra/supabase/migrations/202609012300_add_skip_attempt.sql` -- 가장 최근 RPC 추가 사례(명명/권한 부여 패턴 참고용).
- `apps/batch/scheduler.py:47-95` (`run_scheduled_batch`) -- `Trigger.SCHEDULE`이 하드코딩된 두 지점(68행, 89행 부근 `run_candidate_stage` 호출). `trigger: Trigger` 매개변수를 추가해 관통시킨다.
- `apps/batch/__main__.py:33-36`(`_parse_args`), `:39-63`(`run`) -- CLI에 `--trigger {schedule,manual}`(default schedule)와 `--dispatch-request-id`(선택) 인자를 추가하고 `run()`에서 `run_scheduled_batch(..., trigger=Trigger(args.trigger))`로 전달, 성공 시 `gateway`로 dispatch 영수증 기록.
- `apps/batch/run_state.py`(`RunStateGateway`, `:64` 부근) -- 새 메서드 `record_dispatch_receipt(dispatch_request_id, run_id)` 추가, 신규 RPC `record_dispatch_receipt` 래핑.
- `.github/workflows/scheduled-batch.yml` -- `workflow_dispatch.inputs`에 `dispatch_request_id`(optional) 추가, "Determine batch kind" 스텝 옆에 trigger 판정 추가(`DISPATCH_BATCH_KIND` 있으면 `manual`, 아니면 `schedule`), "Run scheduled batch" 스텝 커맨드에 `--trigger`/`--dispatch-request-id` 전달. 이 파일 자체가 outbox worker가 호출할 고정 대상(owner/repo/workflow file/`ref=main`, AD-7).
- `apps/web/lib/supabase-browser.ts` -- 유일한 기존 Supabase 클라이언트(browser, `persistSession:false`). 신규 서버 클라이언트(`@supabase/ssr`, 이미 의존성 등록됨)는 별도 파일로 분리한다.
- `apps/web/components/dashboard/DataTrustBar.tsx:21-28` -- 현재 항상 `disabled`인 버튼. `onManualTrigger`(또는 내부 `fetch('/api/dispatch', ...)`) 핸들러와 진행중 상태를 연결한다.
- `apps/web/next.config.ts`(`loadRootEnvFile`) -- 루트 `.env.local` 병합기. 신규 server-only 키(`GITHUB_DISPATCH_TOKEN`, `CRON_CALLBACK_SECRET`, `SUPABASE_JWT_ISSUER` 등)는 이 파일을 통해 로드된다.
- (review pass 1 KEEP) 1차 구현의 다음 설계는 그대로 유지한다 -- Next.js `proxy.ts`(Next 16 명칭, `middleware.ts` 아님) 낙관적 세션 리다이렉트 + `/api/dispatch`의 독립 JWKS 검증(`node:crypto`만 사용, 새 의존성 없음) 2단 방어, `lib/csrf-constants.ts`(클라이언트/서버 공유 이름 상수)와 `lib/dispatch.ts`(node:crypto 순수 함수) 분리, `lib/rate-limit.ts` 추출 및 단위 테스트, RPC 응답의 `{status:'queued'|'conflict', reason, ...}` 관용구(= `start_attempt`의 `replayed` 패턴과 동일 계열).
- `apps/web/lib/trust-bar.ts`, `trust-bar.test.ts` -- `deriveTrustBarState`가 이미 `triggerLabel`을 계산; dispatch 진행중/거부(409) 상태 문구 추가 지점.
- `e2e/home.spec.ts`, `playwright.config.ts` -- 로그인 플로우/수동 트리거 E2E 추가 위치(루트 `e2e/`).
- `.github/workflows/test.yml` -- 신규 pytest(`tests/batch/test_scheduler.py` 등 trigger 전달 케이스)와 web unit 테스트는 기존 스텝이 자동 포함하므로 추가 스텝 불필요.

## Tasks & Acceptance

**Execution:**
- `infra/supabase/migrations/202609021000_create_dispatch_outbox.sql` -- `dispatch_request(dispatch_request_id uuid PK default gen_random_uuid(), idempotency_key text, payload_hash text, requested_by text, logical_run_key text, created_at timestamptz default now(), UNIQUE(idempotency_key))`와 `dispatch_outbox(outbox_id uuid PK default gen_random_uuid(), dispatch_request_id uuid FK UNIQUE, status text CHECK IN (queued,accepted,started,completed,failed,dead_letter) default 'queued', lease_token uuid, lease_expires_at timestamptz, run_id uuid FK→runs null, github_run_id bigint null, attempts int default 0, updated_at timestamptz default now())` 생성, `request_manual_dispatch(p_idempotency_key, p_payload_hash, p_requested_by, p_logical_run_key, p_trading_day, p_batch_kind)` RPC(같은 key+hash replay/다른 hash 409/활성 attempt 409/`p_trading_day`가 `p_logical_run_key`의 날짜와 불일치하면 예외, `start_attempt` 미호출) 및 `claim_dispatch_outbox(p_worker_lease_seconds)`(`FOR UPDATE SKIP LOCKED`), `record_dispatch_receipt(p_dispatch_request_id, p_run_id)`, `advance_dispatch_outbox(p_outbox_id, p_status, ...)` RPC 정의, `service_role` 전용 grant -- 1.3 hardening 마이그레이션과 동일한 revoke/grant 관용구.
- `infra/supabase/migrations/202609021000_create_dispatch_outbox.sql` -- `reconcile_dispatch_outbox()` RPC(신규) 추가: `dispatch_outbox.status='started'`이고 `run_id`가 채워진 행을 `runs`와 조인해 `runs.status`가 `published|partial|skipped`면 `completed`, `failed|superseded|cancelled`면 `failed`로 전이(둘 다 아니면 -- `running`/`ready_to_publish` -- 건드리지 않음). lease 불필요(오직 조회 후 갱신, 동시 호출은 단순 update로 충돌 없음). `service_role` 전용 grant.
- `tests/sql/test_dispatch_outbox.sql`(신규) -- replay/409/claim/dead_letter 전이/`reconcile_dispatch_outbox`의 completed·failed 매핑/`trading_day` 불일치 거부를 `raise exception` 스타일로 검증 -- I/O 매트릭스 커버리지.
- `apps/batch/scheduler.py` -- `run_scheduled_batch`에 `trigger: Trigger = Trigger.SCHEDULE` 매개변수 추가, 하드코딩 두 지점을 교체하고 `dispatch_request_id`가 있으면 성공/스킵 후 `gateway.record_dispatch_receipt(...)` 호출 -- 이 호출은 `try/except`로 감싸 실패해도 배치 자체 결과(`SchedulerResult`)에는 영향을 주지 않고 로그만 남긴다(영수증 기록 실패로 정상 종료된 배치가 `failed`로 오판되지 않게 한다).
- `apps/batch/run_state.py` -- `record_dispatch_receipt` 메서드 추가.
- `apps/batch/__main__.py` -- `--trigger`/`--dispatch-request-id` 인자 추가, `run()`에 전달.
- `tests/batch/test_scheduler.py` -- `trigger=Trigger.MANUAL` 경로와 영수증 기록 단위 테스트 추가.
- `tests/batch/test_candidate_stage.py` -- `run_candidate_stage`의 `started.get("replayed")` 분기(비휴장일 replay)에 `dispatch_request_id`를 함께 넘겼을 때 `record_dispatch_receipt`가 올바른 `run_id`로 호출되는지 검증하는 케이스 추가(현재 `FakeRpc`는 `start_attempt`에서 `replayed: True`를 반환하는 경로를 커버하지 않는다).
- `.github/workflows/scheduled-batch.yml` -- `workflow_dispatch.inputs.dispatch_request_id` 추가, trigger 판정 스텝, batch 실행 커맨드에 인자 전달.
- `apps/web/lib/supabase-server.ts`(신규) -- `@supabase/ssr`의 `createServerClient`로 쿠키 기반 세션 클라이언트 생성(로그인 콜백/세션 확인용).
- `apps/web/lib/auth-allowlist.ts`(신규) -- server-side subject allowlist 판정 순수 함수(환경변수 기반 이메일 목록).
- `apps/web/app/login/page.tsx`(신규) -- OTP/magic link 요청 폼(디자인 신규 요건 없음, 최소 기능).
- `apps/web/app/auth/callback/route.ts`(신규) -- magic link 콜백, 세션 교환.
- `apps/web/middleware.ts`(신규) -- 미인증 시 `/login`으로 리다이렉트(단, `/login`, `/auth/*`, `/api/*` 제외 -- 각 API route가 이미 자체 인증을 한다).
- `apps/web/lib/dispatch.ts`(신규) -- idempotency key 생성/payload hash(SHA-256)/CSRF 토큰 검증 순수 함수.
- `apps/web/lib/dispatch.test.ts`(신규) -- hash 결정성, CSRF 불일치, allowlist 거부 케이스.
- `apps/web/lib/jwt-verify.ts`(신규) -- JWKS 기반 서명(RS256/ES256)/issuer/audience/expiry/sub 검증(`node:crypto`만 사용).
- `apps/web/lib/jwt-verify.test.ts`(신규) -- 로컬에서 생성한 RSA 또는 EC 키쌍과 수제 JWKS로 정상 토큰 수락, 그리고 잘못된 서명/issuer/audience/만료/`sub` 누락 각각의 거부를 검증한다(이 route가 통과하는 유일한 인가 게이트이므로 반드시 실행되는 단위 테스트가 있어야 한다).
- `apps/web/lib/rate-limit.ts`(신규), `rate-limit.test.ts`(신규) -- dispatch route의 사용자별 rate limit 순수 함수와 한도 이내/초과/윈도우 만료 케이스.
- `apps/web/app/api/dispatch/route.ts`(신규) -- JWT/CSRF/rate limit 검증 후 `request_manual_dispatch` 호출, 202/403/409/429 응답.
- `apps/web/app/api/dispatch/worker/route.ts`(신규, `CRON_CALLBACK_SECRET` 헤더 검증 -- `timingSafeEqual`로 비교) -- `claim_dispatch_outbox` 호출 후 GitHub `workflow_dispatch` REST 호출(fetch), 상태 전이, lease 만료+receipt 미도달 시 `dead_letter`+GitHub Issue 생성(fetch, 실패 시 로그만 남기고 outbox 상태는 유지). `queued` 상태에서 dispatch 호출 자체가 계속 실패하는 행도 `accepted`/receipt-폴링 행과 동일한 시도 상한을 넘기면 `dead_letter`로 닫는다(무한 재시도 금지). 매 tick 끝에 `reconcile_dispatch_outbox` RPC를 한 번 호출해 `started` 행을 정리한다.
- `infra/supabase/migrations/202609021100_schedule_dispatch_worker_cron.sql`(신규) -- `pg_cron`/`pg_net` extension 활성화, 1분 간격으로 `pg_net.http_post`가 `/api/dispatch/worker`를 `CRON_CALLBACK_SECRET` 헤더와 함께 호출하는 `cron.schedule` 등록.
- `apps/web/components/dashboard/DataTrustBar.tsx` -- 버튼 `disabled` 제거, 클릭 시 `snapshot.latest_attempt?.batch_kind`(없으면 `close`)로 `batchKind`/`logicalRunKey`를 도출해 `/api/dispatch` POST, 진행중/거부 상태를 `deriveTrustBarState` 문구로 반영.
- `apps/web/lib/trust-bar.ts`, `trust-bar.test.ts` -- dispatch 진행중/409 문구 케이스 추가.
- `e2e/home.spec.ts` 또는 신규 `e2e/manual-trigger.spec.ts` -- 미인증 리다이렉트, 인증 후 버튼 활성화 확인(실제 GitHub 호출은 mock/skip). 실제 인증 세션 발급이 CI에서 불가능하면 그 특정 케이스만 spec의 Verification `Manual checks`로 옮기고 사유를 명시한다.

**Acceptance Criteria:**
- Given migration 적용, when `dispatch_request`/`dispatch_outbox`를 조회하면, then 스키마와 RPC가 존재한다.
- Given 미인증 상태로 `/`에 접속하면, when 페이지가 로드되면, then `/login`으로 리다이렉트된다.
- Given allowlist 밖 이메일로 OTP 인증에 성공하면, when 수동 실행을 시도하면, then dispatch 권한이 거부된다.
- Given 인증된 Neo가 수동 실행 버튼을 누르면, when dispatch route가 검증을 통과하면, then 단일 RPC로 `dispatch_request`+`dispatch_outbox`가 함께 생성된다.
- Given outbox worker가 `queued` 행을 claim하면, when GitHub workflow dispatch를 호출하면, then 상태가 `accepted`로 전이하고, batch 첫 스텝이 같은 `dispatch_request_id`로 `run_id`를 idempotent 기록해 `started`가 된다.
- Given `dead_letter` 전이가 커밋되면, when 알림 계약을 확인하면, then GitHub Issue가 생성되고 대시보드/이력에서 조용히 묻히지 않는다.
- Given 수동 트리거 배치가 실행되면, when `runs`를 조회하면, then `trigger='manual'`이다.
- Given 브라우저 코드를 감사하면, when `NEXT_PUBLIC_*`을 확인하면, then Supabase secret/LS token/GitHub token이 없다.
- Given outbox 행이 `started`이고 연결된 `run_id`의 배치가 종결되면, when outbox worker가 다음 tick에서 `reconcile_dispatch_outbox`를 호출하면, then 행이 `completed` 또는 `failed`로 전이한다(영구히 `started`로 남지 않는다).
- Given `queued` 상태의 outbox 행이 GitHub dispatch 호출에 반복 실패하면, when 시도 횟수가 상한을 넘으면, then `dead_letter`로 전이하고 GitHub Issue가 생성된다(무한 재시도로 남지 않는다).
- Given `latest_attempt.batch_kind`가 `premarket` 또는 `intraday`인 상태에서 수동 실행 버튼을 누르면, when dispatch 요청을 확인하면, then `close`가 아니라 해당 `batch_kind`로 요청된다.

## Spec Change Log

### 2026-09-02 — bad_spec 루프백 (review pass 1)
- **트리거:** `dispatch_outbox`가 `started` 이후 종결 상태(`completed`/`failed`)에 도달하는 경로가 스펙 Tasks에 전혀 없었다(Boundaries의 "Always"는 6개 상태 전이를 전부 약속했지만, 그 전이를 누가/언제 호출하는지가 누락됨) -- 1차 구현은 스펙 그대로 구현했을 뿐이라 이 결함은 구현이 아니라 스펙 책임이다. 함께 발견된 관련 결함(수동 실행 버튼의 `batch_kind` 하드코딩, JWT 검증기 테스트 부재, cron secret 비-상수시간 비교, `trading_day`/`logical_run_key` 불일치 미검증, 영수증 기록 예외가 배치 전체를 실패시킬 수 있는 문제, `queued` 상태에서 GitHub dispatch 반복 실패 시 무한 재시도, dead-letter Issue 생성 실패 미처리, replay 분기의 영수증 기록 테스트 누락)도 같은 재파생 사이클에 묶어 함께 반영한다.
- **수정 내용:** Boundaries "Always"에 outbox `started`→종결 규칙(`reconcile_dispatch_outbox` RPC), cron secret 상수시간 비교, `trading_day` 검증, 수동 버튼의 `batch_kind` 도출 규칙을 추가. I/O 매트릭스에 배치 정상/실패 종료 2행 추가. Code Map에 `dashboard-types.ts`의 `batch_kind` 노출 지점과 `runs.status` 종결 분류를 추가. Tasks에 `reconcile_dispatch_outbox` RPC, `jwt-verify.test.ts`/`rate-limit.ts`+테스트, `test_candidate_stage.py`의 replay 분기 테스트, 영수증 기록 `try/except`, `queued` 무한 재시도 방지, dead-letter Issue 실패 로깅을 추가. Acceptance Criteria에 위 3개 신규 불변식을 검증하는 항목 3개 추가.
- **피한 known-bad 상태:** dispatch 감사 테이블(`dispatch_outbox`)이 영구히 `started`로 남아 운영 이력이 부정확해지는 것, 수동 재실행이 실제로 실패한 배치 종류가 아니라 항상 `close`만 재시도하는 것, 보안 게이트(JWT 검증)에 실행되는 테스트가 하나도 없는 것.
- **KEEP:** Next.js `proxy.ts`(Next 16 명칭) 낙관적 리다이렉트 + `/api/dispatch`의 독립 JWKS 검증 2단 방어 구조, `lib/csrf-constants.ts`/`lib/dispatch.ts` 분리, RPC 응답의 `{status, reason}` 관용구, outbox worker를 별도 런타임 없이 Next.js route로 유지하는 결정(Design Notes) -- 모두 1차 구현에서 잘 동작했으므로 재파생 시 그대로 유지한다.

## Review Triage Log

### 2026-09-02 — Review pass
- intent_gap: 0
- bad_spec: 1: (high 1)
- patch: 0
- defer: 1: (medium 1)
- dismissed:
  - "workflow_dispatch에서 batch_kind가 기본값(`close`)으로 남으면 trigger 판정이 schedule로 잘못된다"는 지적 -- `inputs.batch_kind`는 `workflow_dispatch`에 정의된 `default: "close"` 때문에 사람이 값을 바꾸지 않아도 항상 `"close"`(비어있지 않음)로 평가되므로, 실제로는 어떤 `workflow_dispatch` 호출도 `DISPATCH_BATCH_KIND`가 빈 문자열이 되지 않는다(빈 문자열은 오직 `schedule` 이벤트에서만 발생). 주장된 결과가 실제로 발생하지 않아 반증됨.
  - "outbox worker가 GitHub workflow_dispatch로 배치를 다시 트리거해 dispatch_request_id가 schedule 트리거와 함께 전달될 수 있다"는 지적 -- `dispatch_request_id` workflow 입력은 outbox worker가 보내는 `workflow_dispatch` 호출에서만 채워지며, 그 호출은 항상 위 trigger 판정 로직에 의해 `manual`로 귀결된다. 두 값이 서로 다른 이벤트 경로로 갈라질 방법이 없어 도달 불가능한 상태.
  - "`request_manual_dispatch` 성공 응답에서 `data`가 null일 수 있어 `data.dispatch_request_id` 접근이 깨질 수 있다"는 지적 -- RPC의 모든 코드 경로가 `return jsonb_build_object(...)`로 항상 완전한 객체를 반환하도록 SQL로 보장돼 있다(story 1.8/1.9에서 동일 패턴이 이미 같은 이유로 반증된 전례가 있음).
  - "`proxy.ts`(낙관적 `getUser` 체크)와 `/api/dispatch`(독립 JWKS 검증)가 서로 다른 세션 검증 전략을 쓰는 것이 결함"이라는 지적 -- 의도된 2단 방어다: `proxy.ts`는 리다이렉트용 낙관적 체크임을 스스로 주석에 명시하고, AD-7은 dispatch route가 별도로 JWKS 서명/issuer/audience/expiry/sub를 검증하도록 명시적으로 요구한다. 서로 다른 목적의 두 검증이 다른 것은 결함이 아니라 스펙이 요구한 설계다.
  - "in-memory rate limiter가 서버리스 다중 인스턴스에서 우회될 수 있다"는 지적 -- 스펙의 Never 절(새 의존성 금지)과 단일 운영자 전제 하에 이미 의도적으로 받아들인 트레이드오프이며, 코드 주석에도 명시돼 있다. 새로 발견된 결함이 아니다.
  - "로그인/OTP 요청 경로에 앱 레벨 rate limit이 없다"는 지적 -- Supabase Auth의 email OTP 발송 자체가 플랫폼 레벨에서 이메일별/프로젝트별 rate limit을 이미 강제한다. 이 스토리의 Always 절은 dispatch route의 rate limit만 명시적으로 요구하며, OTP 발송은 그 범위 밖이다.
  - "intraday `logical_run_key` 정규식이 실제 장중 시간대(09:00-15:30)를 벗어난 슬롯도 통과시킨다"는 지적 -- 동일한 느슨함이 `start_attempt`(story 1.3, 변경 없음)에 이미 존재하는 선례이며 이번 변경이 새로 도입한 결함이 아니다.
  - "`advance_dispatch_outbox` RPC 호출이 GitHub dispatch 성공 직후 실패하면 같은 배치가 중복 발송될 수 있다"는 지적 -- 실제로 발생 가능하지만, story 1.3의 fence 모델(`start_attempt`의 supersede 분기)이 이미 동시 attempt를 안전하게 처리하도록 설계돼 있어 결과가 낭비된 GitHub Actions 실행 1회에 그치고 데이터 훼손으로 이어지지 않는다(low severity로 판단, 이번 재파생 범위에서는 별도 조치 없이 다음 패스에서 재평가).
- addressed_findings:
  - none
- deferred:
  - `tests/sql/test_dispatch_outbox.sql`이 `.github/workflows/test.yml` CI에 연결되지 않아 자동 회귀 검증이 없다 -- story 1.8부터 이어진 프로젝트 전역의 기존 공백(로컬/CI 어디에도 Postgres 실행 환경이 없음)이며 이번 스토리가 새로 만든 문제가 아니다. `deferred` 프런트매터에 기록.

### 2026-09-02 — Review pass
- intent_gap: 0
- bad_spec: 0
- patch: 4: (high 1, medium 1, low 2)
- defer: 1: (low 1)
- dismissed:
  - "`proxy.ts`의 `advance_dispatch_outbox`가 전이 순서를 강제하지 않아 임의 상태로 되돌릴 수 있다"는 지적 -- 실제 호출자는 outbox worker(`accepted`/`dead_letter`만 전달)와 `record_dispatch_receipt`(별도 함수, `started`만 설정) 둘뿐이며 둘 다 항상 순방향으로만 호출한다. RPC 자체가 방어적이지 않은 건 사실이나 현재 호출 경로로는 도달 불가능해 실질적 결함이 없다.
  - "두 동시 `request_manual_dispatch` 호출이 아직 `logical_runs` 행이 없는 신규 key에 대해 활성 attempt 가드를 동시에 통과할 수 있다"는 지적 -- 실제로 가능하지만, 이후 GitHub Actions에서 배치가 `start_attempt`를 호출하는 시점에 1.3의 fence 모델이 두 번째 attempt를 supersede해 안전하게 수렴시킨다(1차 패스에서 동일 계열 지적을 같은 근거로 기각한 전례와 동일). 결과는 낭비된 GitHub Actions 실행 1회뿐 데이터 훼손이 없다.
  - "`proxy.ts`의 `supabase.auth.getUser()`가 Supabase Auth 장애 시 예외를 던져 모든 요청이 깨질 수 있다"는 지적 -- `@supabase/ssr`/`@supabase/supabase-js`의 인증 메서드는 네트워크/서비스 오류를 `{data, error}` 결과 객체로 반환하도록 문서화돼 있고 예외를 던지지 않는다. 주장의 전제(예외를 던진다)가 실제 라이브러리 계약과 다르다.
  - "JWKS 응답에 `keys` 배열이 없으면 분류되지 않은 TypeError가 발생한다"는 지적 -- 실제로 가능하지만 결과가 500(안전한 실패)일 뿐 인가 우회로 이어지지 않는다. JWKS 엔드포인트 설정 오류라는 매우 드문 경로이며 어떤 AC도 이 경로의 에러 코드 분류를 요구하지 않는다.
  - "`ClaimedOutboxRow.status`가 `started`를 포함하지만 `claim_dispatch_outbox`는 `queued`/`accepted`만 반환해 죽은 타입"이라는 지적, "`processRow` 최상단의 `attempts > MAX_ATTEMPTS` 체크가 하위 분기의 `attempts >= MAX_ATTEMPTS`보다 먼저 걸릴 수 없어 사실상 중복"이라는 지적 -- 둘 다 사실이지만 동작에 영향이 없는 코스메틱/사문화된 코드 지적이며 어떤 AC도 위반하지 않는다.
  - "in-memory rate limiter의 `Map`이 오래된 subject 키를 정리하지 않아 메모리 누수 가능성이 있다"는 지적 -- 1차 패스에서 이미 같은 in-memory rate limiter 트레이드오프(신규 의존성 금지, 단일 운영자 전제)를 근거로 기각한 사안과 같은 계열이며 새로 발견된 결함이 아니다.
  - "`dispatch_request`가 `batch_kind`를 저장하지 않아 outbox worker가 `logical_run_key`를 문자열 분할해 재도출한다"는 지적 -- 사실이나 `logical_run_key` 자체가 이미 `batch_kind`를 canonical하게 포함하는 형식(`{batch_kind}:{date}[:{time}]`)이라 별도 컬럼 저장은 중복 저장이며, `request_manual_dispatch`가 이미 형식을 정규식으로 검증해 분할 결과가 항상 유효함을 보장한다. 정보 손실이나 오동작 경로가 없다.
  - "`/api/dispatch` route와 `/api/dispatch/worker` route 자체(HTTP 핸들러 전체 흐름)를 실행하는 테스트가 없다"는 지적 -- 이 프로젝트의 기존 관례(story 1.8/1.9)도 Next.js route/서버 컴포넌트 핸들러 자체는 단위 테스트하지 않고 e2e+추출된 순수 함수 단위 테스트로 검증해 왔다(예: `get_dashboard_snapshot` 호출부, `/runs` 조회 로직 모두 핸들러 레벨 테스트가 없음). 이 스토리도 같은 관례를 따라 JWT/CSRF/rate-limit/idempotency/allowlist 순수 함수는 모두 단위 테스트가 있다 -- 새로운 결함이 아니라 이 리포가 채택한 기존 테스트 전략의 범위 밖이다. `deferred`에 향후 개선 항목으로 기록한다.
- addressed_findings:
  - `[high]` `[patch]` `apps/web/lib/supabase-service.ts`: 환경변수 이름이 `SUPABASE_SECRET_KEY`였는데 프로젝트 전체(워크플로/배치 CLI/기존 테스트)는 `SUPABASE_SERVICE_ROLE_KEY`를 쓴다 -- 실제 배포 시 기존 관례대로 시크릿을 설정하면 dispatch/worker route가 환경변수 누락으로 죽었을 것이다. `SUPABASE_SERVICE_ROLE_KEY`로 통일했다.
  - `[medium]` `[patch]` `apps/web/proxy.ts`: 공개 경로 목록이 `/api/dispatch/worker`만 제외해 `/api/dispatch`가 proxy의 세션 리다이렉트 대상이었다 -- 세션 없이 호출하면 route의 JSON 401 대신 `/login` HTML로 302 리다이렉트돼 `fetch()`가 200으로 오인하고, AD-7이 요구하는 dispatch route의 독립 JWKS 검증이 무력화됐다. `/api/*` 전체를 제외하도록 넓히고, 스펙 Code Map의 해당 문구도 함께 수정했다.
  - `[low]` `[patch]` `infra/supabase/migrations/202609021000_create_dispatch_outbox.sql`: `request_manual_dispatch`의 `trading_day` 검증이 `p_trading_day is null`일 때 `<>` 비교가 NULL이 되어 조용히 통과됐다(현재 유일한 호출자는 이미 non-empty string을 검증해 도달 불가하지만 RPC 자체의 방어가 없었다). NULL을 명시적으로 거부하도록 고치고 `tests/sql/test_dispatch_outbox.sql`에 케이스를 추가했다.
  - `[low]` `[patch]` `apps/web/lib/dispatch.test.ts`: 같은 파일의 다른 순수 함수는 모두 테스트가 있는데 `isValidLogicalRunKey`만 없었다 -- 배치 종류별 유효/무효 케이스를 추가했다.
- deferred:
  - `/api/dispatch`·`/api/dispatch/worker` route 핸들러 전체 흐름(요청→응답 매핑)에 대한 자동 테스트가 없다 -- 이 리포의 기존 관례(route/서버 컴포넌트는 e2e+추출된 순수 함수 단위 테스트로 검증)를 따른 것이라 이번 스토리가 새로 만든 공백은 아니지만, 개선 여지로 남긴다. `deferred` 프런트매터에는 별도 기록하지 않음(범위가 이 스토리 하나에 국한되지 않는 리포 전역 테스트 전략 논의 대상).

## Design Notes

Outbox worker 런타임: ARCHITECTURE-SPINE.md의 dispatch 흐름도(101-108행)는 `Worker[server-only outbox worker]`를 `Next[Next Node runtime]`과 별도 박스로 그리지만, 이 프로젝트는 지금까지 `apps/web`(Next.js) 외의 server-only 런타임(Supabase Edge Function 등)을 한 번도 도입하지 않았고 planning 문서 전체에 Edge Function/Deno/pg_net 관련 명시적 결정이 없다. Vercel Hobby는 1분 간격 cron을 지원하지 않으므로(AD-18이 명시한 "Supabase pg_cron 1분 scan"이 durable fallback인 이유), 타이머는 Supabase `pg_cron`이 맡고 실제 claim/GitHub 호출 로직은 기존 Next.js server route로 유지해 새 런타임 도입을 피한다 -- `pg_cron`이 `pg_net.http_post`로 그 route를 매분 깨우는 방식. 이 결정은 review 단계에서 재검토 가능하도록 이 노트에 근거를 남긴다.

`request_manual_dispatch`는 `start_attempt`를 호출하지 않는다 -- 실제 attempt 생성은 여전히 GitHub Actions에서 배치 CLI가 `start_attempt(..., Trigger.MANUAL)`을 호출할 때 일어난다(스케줄 경로와 동일). dispatch RPC는 큐잉과 409 가드만 담당해 `start_attempt`의 supersede 동작(202609011600:102-105)을 건드리지 않는다.

## Verification

**Commands:**
- `cd apps/web && npm run typecheck` -- expected: 오류 없음.
- `cd apps/web && npm run test` -- expected: `dispatch.test.ts`/`jwt-verify.test.ts`/`rate-limit.test.ts`/`trust-bar.test.ts` 신규 케이스 포함 전부 통과.
- `cd apps/web && npm run build` -- expected: `/login`, `/api/dispatch`, `/api/dispatch/worker` 라우트 생성 확인.
- `uv run pytest tests/batch/test_scheduler.py tests/batch/test_candidate_stage.py` -- expected: `Trigger.MANUAL` 경로와 replay 분기 영수증 기록 통과.
- `psql`로 `tests/sql/test_dispatch_outbox.sql` 실행 -- expected: replay/409/claim/dead_letter 케이스 전부 통과.
- `npm run test:e2e` -- expected: 로그인 리다이렉트/버튼 활성화 E2E 통과.

**Manual checks (if no CLI):**
- 실제 Supabase 프로젝트에 migration 적용 후 `curl`로 `request_manual_dispatch`를 중복 호출해 replay/409 응답을 직접 확인한다.

## Auto Run Result

**요약:** Supabase Auth email OTP/magic link 단일 운영자 세션 + server-side allowlist를 추가하고, `dispatch_request`/`dispatch_outbox` transactional outbox와 5개 RPC(`request_manual_dispatch`/`claim_dispatch_outbox`/`advance_dispatch_outbox`/`record_dispatch_receipt`/`reconcile_dispatch_outbox`)로 인증된 수동 배치 트리거를 구현했다. Next.js server-only `proxy.ts`(세션 리다이렉트)와 `/api/dispatch`(JWKS/CSRF/rate-limit 독립 검증)의 2단 방어, `pg_cron`+`pg_net`이 1분마다 깨우는 `/api/dispatch/worker`가 GitHub `workflow_dispatch`를 호출하고 lease/dead-letter/GitHub Issue 알림을 관리한다. 배치 CLI(`apps/batch`)는 `--trigger`/`--dispatch-request-id`를 받아 outbox에 receipt를 기록한다. 1차 구현 리뷰에서 outbox가 `started` 이후 영구히 종결되지 않는 스펙 누락(bad_spec)을 발견해 스펙을 보강하고 코드를 재파생했으며, 2차 리뷰에서 발견된 환경변수 이름 불일치·proxy 경로 과소 제외 등 4건을 patch로 수정했다.

**변경 파일:**
- `infra/supabase/migrations/202609021000_create_dispatch_outbox.sql`(신규) -- `dispatch_request`/`dispatch_outbox` 스키마와 5개 RPC.
- `infra/supabase/migrations/202609021100_schedule_dispatch_worker_cron.sql`(신규) -- `pg_cron`/`pg_net` 1분 스케줄(배포 후 `app.settings` 값 설정 필요, migration 주석에 문서화).
- `tests/sql/test_dispatch_outbox.sql`(신규) -- replay/409/trading_day 불일치/claim/dead_letter/reconcile 케이스(로컬 Postgres 부재로 미실행, `deferred` 기록).
- `apps/batch/{scheduler,run_state,candidate_stage,__main__}.py` -- `trigger`/`dispatch_request_id` 관통, `record_dispatch_receipt`/`safe_record_dispatch_receipt`(실패 격리).
- `.github/workflows/scheduled-batch.yml` -- `dispatch_request_id` 입력, trigger 판정, CLI 인자 전달.
- `apps/web/proxy.ts`(신규) -- Next 16 `middleware.ts`→`proxy.ts` 세션 리다이렉트, `/api/*`는 각 route 자체 인증에 맡긴다.
- `apps/web/lib/{jwt-verify,csrf-constants,dispatch,rate-limit,auth-allowlist,supabase-server,supabase-service,supabase-browser-auth}.ts`(신규) -- JWKS 검증(node:crypto), CSRF, idempotency/payload-hash/logical-run-key 검증, rate limit, allowlist, 서버/서비스 클라이언트. 전부 단위 테스트 동반.
- `apps/web/app/login/page.tsx`, `app/auth/callback/route.ts`(신규) -- OTP 요청 폼(에러 표시 포함), 세션 교환.
- `apps/web/app/api/dispatch/route.ts`, `app/api/dispatch/worker/route.ts`(신규) -- 인증된 dispatch 큐잉, outbox worker(claim/GitHub 호출/dead-letter/reconcile).
- `apps/web/components/dashboard/DataTrustBar.tsx`, `lib/trust-bar.ts` -- 버튼 활성화, `latest_attempt.batch_kind` 기반 재실행 대상 도출, 진행중/거부 문구.
- `e2e/home.spec.ts`(갱신), `e2e/manual-trigger.spec.ts`(신규) -- 미인증 리다이렉트, 로그인 폼, worker route 시크릿 검증.

**리뷰 결과:**
- **Review pass 1** (blind-hunter/edge-case-hunter/verification-gap/intent-alignment 병렬): bad_spec 1건(outbox `started` 종결 경로 누락 -- 스펙 Boundaries가 약속한 전이를 Tasks가 구현하지 않음) 발견, 관련 결함 7건을 같은 스펙 보강에 묶어 코드 재파생. dismissed 7건(반증 또는 기존 전례와 동일한 트레이드오프). defer 1건(SQL fixture CI 미연결, story 1.8부터의 기존 공백).
- **Review pass 2**: patch 4건 수정 -- `[high]` `SUPABASE_SECRET_KEY`/`SUPABASE_SERVICE_ROLE_KEY` 환경변수 이름 불일치(배포 시 기능 전체가 죽었을 결함), `[medium]` `proxy.ts`가 `/api/dispatch`를 세션 리다이렉트 대상에서 빼먹어 AD-7의 독립 JWKS 검증이 무력화되던 결함, `[low]` `request_manual_dispatch`의 `trading_day` NULL 바이패스, `[low]` `isValidLogicalRunKey` 테스트 누락. dismissed 7건(대부분 1.3 fence 모델의 안전망으로 이미 흡수되거나, 라이브러리 계약과 다른 전제, 또는 기존 테스트 전략 범위 밖). defer 1건(route 핸들러 전체 흐름 테스트 부재, 리포 전역 전략 논의 대상).
- **followup_review_recommended: true** -- 이번 패스에서 high severity patch 1건이 확정돼 자동으로 true(공식: high 존재 시 무조건 true).

**검증 수행:**
- `cd apps/web && npm run typecheck` -- 통과(오류 없음).
- `cd apps/web && npm run test` -- 36/36 통과(JWT 서명/issuer/audience/expiry/sub 8케이스, CSRF, idempotency hash, rate limit, allowlist, trust-bar dispatch 상태, `isValidLogicalRunKey` 포함).
- `cd apps/web && npm run build` -- 성공, `/login`·`/api/dispatch`·`/api/dispatch/worker`·`/auth/callback` 라우트 생성 확인.
- `uv run pytest`(전체) -- 137개 전부 통과(신규 manual-trigger/replay-receipt 케이스 포함).
- `npm run test:e2e`(`home.spec.ts`+`manual-trigger.spec.ts`) -- 4/4 통과.
- SQL 마이그레이션/RPC는 코드 리뷰로 직접 라인 단위 검증(fence/lease 관용구, NULL 가드, 상태 전이 CHECK)했으나 실제 Postgres 실행 검증은 로컬/CI 모두 환경 부재로 수행하지 못함 -- `deferred`에 기록.

**잔여 위험:**
- `tests/sql/test_dispatch_outbox.sql`이 실제 Postgres에서 한 번도 실행되지 않았다(로컬 psql/docker 부재, CI도 미연결) -- story 1.8부터 이어진 프로젝트 전역 공백. 실 배포 전 반드시 실제 Supabase 프로젝트(또는 로컬 스택)에서 이 fixture와 `psql` curl 수동 검증을 수행해야 한다.
- `infra/supabase/migrations/202609021100_schedule_dispatch_worker_cron.sql`은 배포 후 Supabase Vault/`app.settings`에 실제 URL과 `CRON_CALLBACK_SECRET`을 수동으로 설정해야 동작한다(마이그레이션 자체가 값 부재 시 안전하게 no-op).
- 인증된 세션에서의 실제 수동 트리거 왕복(로그인→버튼 활성화→dispatch→GitHub 호출)은 실제 이메일 OTP 수신이 필요해 이번 세션에서도, CI에서도 자동 검증하지 못했다 -- 배포 후 사람이 직접 확인해야 한다(spec Verification의 Manual checks).
- `/api/dispatch`·`/api/dispatch/worker` route 핸들러 자체(HTTP 요청→응답 전체 흐름)를 실행하는 자동 테스트가 없다(이 리포의 기존 route 테스트 관례를 따른 결과).
