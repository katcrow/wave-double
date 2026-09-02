---
title: '백업 & 복원 검증'
type: 'feature'
created: '2026-09-02'
status: 'done'
baseline_revision: '58422516d0fcd8de918e8f88eb282836f7eeab0a'
review_loop_iteration: 0
followup_review_recommended: true
context:
  - '{project-root}/_bmad-output/planning-artifacts/architecture/architecture-wave-double-2026-08-31/ARCHITECTURE-SPINE.md'
warnings: [oversized]
deferred:
  - summary: >-
      `backup-restore-drill.yml`과 기존 `test.yml`의 `sql-outbox-tests` job이 모두 `postgres:16`
      floating tag를 다이제스트 고정 없이 사용하며, 실제 운영 Supabase 프로젝트의 Postgres
      major/minor 버전과 일치하는지 확인된 바 없다.
    evidence: |-
      blind-hunter 리뷰가 지적했고, `test.yml:74`가 이미 동일한 패턴(`postgres:16`, floating tag)을
      선례로 쓰고 있어 이번 스토리가 새로 도입한 위험이 아니라 기존 관례의 연장이다. 버전이
      갈리면 확장·wire format 차이로 드릴이 실제 운영 복원과 다르게 동작할 수 있으나, 현재
      리포지토리에는 운영 Supabase 프로젝트의 정확한 Postgres 버전을 코드에서 확인할 방법이 없다.
    location: >-
      .github/workflows/backup-restore-drill.yml, .github/workflows/test.yml:74
    severity: low
---

<intent-contract>

## Intent

**Problem:** 무료 Supabase 플랜에는 PITR이 없어, 운영 DB가 손상되면 실전 데이터를 영구히 잃을 수 있다. 현재 저장소에는 백업 워크플로·암호화·복원 검증이 전혀 없다(AD-17 결정만 존재, 구현 없음).
**Approach:** 6시간마다 transaction-consistent `pg_dump`를 생성해 `age`로 암호화하고 manifest(schema 버전·cutoff·checksum)와 함께 GitHub Actions artifact(14일 보관)로 남기는 워크플로, 그리고 분기 1회 최신 백업을 disposable Postgres에 복원해 migration 적용·smoke fixture·canonical pointer 정합·RPO/RTO를 검증하는 별도 워크플로를 신설한다. 실패 시 기존 dead-letter Issue 관례(AD-10)를 본떠 GitHub Issue를 생성한다.

## Boundaries & Constraints

**Always:** 백업은 `.github/workflows/backup.yml`에 `schedule:`(6시간 간격, UTC 0/6/12/18시)로만 정의하고, `pull_request` 트리거를 두지 않는다(스케줄 이벤트는 fork에서 실행되지 않으므로 AD-11이 구조적으로 충족됨 — `scheduled-batch.yml`과 동일 관례). `pg_dump`는 `--format=plain`으로 transaction-consistent(`--single-transaction` 또는 동등 옵션 근거를 Design Notes에 남길 것) 덤프를 생성한 뒤 `age -r <공개키>`로 암호화하고, 원본 평문 덤프는 워크플로 종료 전 삭제한다. Manifest(JSON)에는 `schema_migration_version`(`infra/supabase/migrations/`의 사전순 최신 파일명), `cutoff_utc`(pg_dump 시작 ISO8601), `checksum_sha256`(암호화 파일 기준)을 기록하고 암호화 백업 파일과 함께 `actions/upload-artifact@v4`(`retention-days: 14`)로 업로드한다. 실패 시(`if: failure()`) `GITHUB_TOKEN`(workflow `permissions: issues: write`)으로 `gh issue create`를 호출해 label `backup-failed`의 Issue를 남긴다(secret 값은 로그·본문에 노출 금지). 복원 검증은 `.github/workflows/backup-restore-drill.yml`에 분기 1회 schedule(1/4/7/10월 1일)과 `workflow_dispatch`(수동 검증용)를 두고, `test.yml`의 `sql-outbox-tests` job과 동일한 `services.postgres:16` disposable 컨테이너 패턴을 재사용한다. 드릴은 GitHub Actions REST API로 최신 `wave-double-backup-*` artifact를 찾아 다운로드 → `age -d`로 복호화 → 복원 → manifest의 `schema_migration_version`보다 사전순으로 뒤인 마이그레이션 파일이 있으면 순서대로 추가 적용 → `tests/sql/test_dashboard_snapshot.sql`과 `tests/sql/test_run_lineage.sql`을 실행(canonical pointer 정합·read-model 조회 계약 검증 겸용, 근거는 Design Notes)한다. 드릴은 manifest `cutoff_utc`와 현재 시각의 차이를 RPO 실측치로, 워크플로 job 소요 시간을 RTO 실측치로 각각 로그에 기록하고 RPO>6h 또는 실패 시 `restore-drill-failed` label Issue를 생성한다. 신규 GitHub Actions repository secret `SUPABASE_DB_URL`(직접 Postgres 연결 문자열, 비밀번호 포함), `BACKUP_AGE_PUBLIC_KEY`, `BACKUP_AGE_PRIVATE_KEY`(복원 드릴 전용)가 필요함과 그 등록 절차·age 키쌍 생성 절차·"복원 드릴 실패 시 production release before 재해결" 수동 게이트를 `docs/backup-restore.md`(신규)에 문서화한다.

**Never:** 새 npm/pip 의존성을 추가하지 않는다(`postgresql-client`·`age`는 `apt-get`으로 러너에 설치하는 CI 전용 도구이며 프로젝트 의존성이 아니다, `test.yml`의 기존 `psql` 설치 관례와 동일). Vercel/Supabase 관리 콘솔에서 실제 secret을 등록하거나 age 키쌍을 생성하는 행위 자체는 이 세션에서 수행하지 않는다(계정 자격증명 부재, Manual checks로 위임 — story 1.11과 동일 패턴). production 배포를 실제로 차단하는 CI 게이트(예: Vercel 배포를 막는 별도 워크플로)는 만들지 않는다 — "release 차단"은 `docs/backup-restore.md`에 문서화된 수동 프로세스 요건이다(Vercel 자동배포를 막을 기존 메커니즘이 없음, story 1.11의 Manual-check 선례를 따름). 기존 `dispatch-outbox` dead-letter의 `GITHUB_DISPATCH_TOKEN` 기반 앱 레이어 fetch 방식을 그대로 복제하지 않는다(백업은 GitHub Actions 네이티브 컨텍스트이므로 `gh issue create`+`GITHUB_TOKEN`이 더 단순하고 충분하다).

</intent-contract>

## Code Map

- `.github/workflows/scheduled-batch.yml` -- 6시간 스케줄 cron 표현식·`concurrency.group`·secrets 주입 패턴의 참고 원형(신규 `backup.yml`이 그대로 본뜬다).
- `.github/workflows/test.yml:65-108` (`sql-outbox-tests` job) -- disposable `services.postgres:16` + `psql` client 설치 + `infra/supabase/migrations/*.sql` 순차 적용 패턴. `backup-restore-drill.yml`이 이 구조를 재사용한다.
- `apps/web/app/api/dispatch/worker/route.ts:140-176` (`createDeadLetterIssue`) -- AD-10 dead-letter Issue 생성의 기존 구현(앱 레이어, `GITHUB_DISPATCH_TOKEN` 기반). 백업 워크플로는 이를 그대로 재사용하지 않고 Actions 네이티브 `gh issue create`로 대체하되, title/label 명명 관례(`[backup] ...`, `backup-failed`)만 참고한다.
- `infra/supabase/migrations/` -- 13개 마이그레이션 파일, `YYYYMMDDHHMM_*.sql` 사전순 명명. manifest의 `schema_migration_version`은 이 디렉터리의 사전순 최신 파일명을 그대로 기록한다.
- `tests/sql/test_dashboard_snapshot.sql`, `tests/sql/test_run_lineage.sql` -- `begin`/`rollback` 감싼 자기완결 SQL fixture. 복원 드릴의 smoke test·canonical pointer 정합 확인에 그대로 재사용한다.
- `.env.example` -- 기존 secret 목록 관례. 이번 스토리의 신규 secret(`SUPABASE_DB_URL`, `BACKUP_AGE_PUBLIC_KEY`, `BACKUP_AGE_PRIVATE_KEY`)은 앱 런타임이 아닌 GitHub Actions 전용이므로 여기 추가하지 않고 `docs/backup-restore.md`에 별도 체크리스트로 문서화한다(스코프 결정, Design Notes 참고).
- `docs/deployment.md` -- story 1.11이 확립한 "계정 자격증명 필요 절차는 문서화 + Manual checks로 위임" 구조의 선례. `docs/backup-restore.md`가 동일 구조를 따른다.

## Tasks & Acceptance

**Execution:**
- `.github/workflows/backup.yml`(신규) -- 6시간 cron(UTC 0/6/12/18시) + `workflow_dispatch`, `pg_dump --format=plain --single-transaction` → `age` 암호화 → manifest(JSON) 생성 → `actions/upload-artifact@v4`(`retention-days: 14`) 업로드 → 실패 시 `gh issue create`(label `backup-failed`) -- AD-17의 백업 절반(생성·암호화·보관·알림)을 구현.
- `.github/workflows/backup-restore-drill.yml`(신규) -- 분기 1회 schedule + `workflow_dispatch`, 최신 backup artifact 탐색·다운로드 → `age -d` 복호화 → disposable Postgres 복원 → 신규 마이그레이션 적용 → `test_dashboard_snapshot.sql`/`test_run_lineage.sql` 실행 → RPO/RTO 실측 로그 → 실패 시 `gh issue create`(label `restore-drill-failed`) -- AD-17의 나머지 절반(분기 복원 검증)을 구현.
- `docs/backup-restore.md`(신규) -- age 키쌍 생성 절차, GitHub repository secret(`SUPABASE_DB_URL`/`BACKUP_AGE_PUBLIC_KEY`/`BACKUP_AGE_PRIVATE_KEY`) 등록 절차, 복원 드릴 실패 시 수동 release 차단 프로세스, RPO 6h/RTO 8h 목표와 실측치 확인 방법을 문서화.

**Acceptance Criteria:**
- Given `backup.yml`이 트리거되면, when `pg_dump`·암호화·manifest 생성이 모두 성공하면, then 암호화된 덤프와 manifest가 하나의 artifact로 14일 보관 설정과 함께 업로드된다.
- Given `backup.yml`의 어느 스텝이든 실패하면, when 워크플로가 종료되면, then `backup-failed` label의 GitHub Issue가 생성되고 secret 값은 Issue 본문·로그 어디에도 노출되지 않는다.
- Given `backup-restore-drill.yml`이 트리거되면, when 최신 backup artifact를 disposable Postgres에 복원하고 필요한 마이그레이션을 추가 적용하면, then `test_dashboard_snapshot.sql`과 `test_run_lineage.sql`이 모두 통과하고 RPO/RTO 실측치가 워크플로 로그에 기록된다.
- Given fork 저장소인 경우, when `backup.yml`/`backup-restore-drill.yml`의 schedule 트리거 조건을 확인하면, then GitHub의 기본 동작상 fork에서는 schedule 이벤트가 실행되지 않아 production secret이 fork에 노출되지 않음이 `docs/backup-restore.md`에 근거와 함께 문서화된다.
- Given `docs/backup-restore.md`의 절차대로 age 키쌍을 생성하고 GitHub secret을 등록하면(Manual, 자격증명 필요), when 두 워크플로를 최초 1회 `workflow_dispatch`로 수동 실행하면, then 위 AC들이 실제 운영 환경에서도 통과함을 확인할 수 있다.

## Spec Change Log

## Review Triage Log

### 2026-09-02 — Review pass
- intent_gap: 0
- bad_spec: 0
- patch: 7: (high 1, medium 4, low 2)
- defer: 1: (low 1)
- dismissed:
  - "`pg_dump` 연결 실패 시 `SUPABASE_DB_URL`이 로그에 노출될 수 있다" — GitHub Actions는 저장소 secret으로 등록된 값과 정확히 일치하는 문자열을 모든 스텝의 stdout/stderr에서 자동으로 마스킹한다(서브프로세스인 `pg_dump`의 에러 출력 포함). 워크플로가 이 값을 직접 echo하지 않는 것과 무관하게 플랫폼 차원에서 이미 보장되는 동작이다.
  - "`docs/backup-restore.md`가 실제 프로덕션 재해복구(DR) runbook의 구체적 명령을 담고 있지 않다" — epics.md의 story 1.12 AC는 disposable Postgres 복원 드릴과 수동 release-block 절차 문서화만 요구하며, 실제 Supabase 프로젝트 대상 완전한 DR 명령 문서화는 AC 어디에도 없다. 이 세션에는 프로덕션 자격증명도 없어(spec Never 절) 검증 불가능한 구체적 명령을 미리 문서화하는 것은 오히려 위험하다.
  - "복원 드릴 실패의 유일한 알림 채널이 GitHub Issue라 Issue 생성 자체가 실패하면 알림이 없다(SPOF)" — story 1.10이 이미 확립한 AD-10 dead-letter 알림 관례(`apps/web/app/api/dispatch/worker/route.ts`)도 동일하게 GitHub Issue를 유일 채널로 쓰며 "실패는 로그만 남긴다"고 명시한다. 이번 스토리가 새로 도입한 결함이 아니라 리포지토리 전체가 이미 채택한 기존 아키텍처 결정이다.
  - "GitHub이 60일간 저장소에 활동이 없으면 scheduled workflow를 자동 비활성화한다" — 이 저장소는 `scheduled-batch.yml`이 거래일마다 하루 여러 번 실행되어 저장소 활동이 항상 유지되므로, 60일 무활동 조건에 도달할 실질적 경로가 없다.
  - "age 개인키 분실/유출 시 키 로테이션 절차가 문서화되어 있지 않다" — epics.md의 story 1.12 AC 5개 중 어느 것도 키 로테이션 절차를 요구하지 않는다(초기 키 생성·secret 등록·복원 드릴 검증만 요구). 현재 AC 충족 여부와 무관한 별도 운영 대비 항목이다.
  - "데이터 규모 증가에 따른 RTO 추세 모니터링이 없다" — epics.md AC는 "RPO/RTO 목표 충족 여부가 기록된다"만 요구하며, 이는 매 분기 드릴이 실측치를 로그에 남기는 것으로 이미 충족된다. 추세 추적은 AC가 요구하지 않는 별도 개선 항목이다.
- addressed_findings:
  - `[high]` `[patch]` `backup-restore-drill.yml`: production에 이미 적용된 `202609021100_schedule_dispatch_worker_cron.sql`(pg_cron/pg_net) 때문에 실제 `pg_dump` 백업 본문에 `CREATE EXTENSION pg_cron/pg_net`·관련 `COPY cron.*/net.*` 데이터·setval이 그대로 포함되어, extension이 없는 disposable Postgres 복원이 `ON_ERROR_STOP=1`로 매번 실패할 수 있었다(verification-gap이 발견, edge-case-hunter가 스케일 문제로 재확인). 복원 직전에 관련 구문/데이터 블록을 제거하는 스텝을 추가해 수정, YAML 파싱·Python 컴파일 재검증 통과.
  - `[medium]` `[patch]` `backup-restore-drill.yml`("Find latest backup artifact"): `gh api --paginate`와 `--jq`를 함께 쓰면 필터가 페이지 단위로 적용되어 "전체 중 최신"이 아니라 "각 페이지 중 최신"을 고를 위험이 있었다(blind-hunter, edge-case-hunter 공통 지적). `jq -s`로 전체 페이지를 모은 뒤 정렬·선택하도록 수정.
  - `[medium]` `[patch]` `backup.yml`/`backup-restore-drill.yml`: 두 job 모두 `timeout-minutes`가 없어 네트워크 호출이 멈추면 GitHub 기본 제한까지 무한정 실행될 위험이 있었다(blind-hunter, edge-case-hunter). `backup`은 20분, `restore-drill`은 30분으로 명시.
  - `[medium]` `[patch]` `backup.yml`/`backup-restore-drill.yml`("Create failure issue"): 지속 장애 시 매 실행마다 새 Issue가 쌓이는 스팸 위험이 있었다(blind-hunter). 같은 라벨의 열린 Issue가 이미 있으면 생성을 건너뛰도록 수정.
  - `[medium]` `[patch]` `backup-restore-drill.yml`("Download and decrypt latest backup"): manifest 필드가 검증 없이 `jq -r`로만 읽혀, 손상된 manifest의 `"null"` 문자열이 조용히 흘러들어가면 migration 비교 단계가 모든 대기 migration을 잘못 건너뛸 수 있었다(blind-hunter, edge-case-hunter 공통 지적). 두 필드 모두 빈 값/`"null"` 검사 후 실패하도록 수정.
  - `[low]` `[patch]` `backup-restore-drill.yml`("Measure RPO"): 잘못된 `cutoff_utc`나 시계 오차로 RPO가 음수가 되어도 그대로 통과할 위험이 있었다(edge-case-hunter). 음수면 명시적으로 실패하도록 수정.
  - `[low]` `[patch]` `docs/backup-restore.md`(§⑤): "다음 fenced runbook을 따른다"고 예고하고 실제 fenced 코드블록을 제공하지 않는 서술 불일치가 있었다(blind-hunter). 예고 문구를 제거하고 평범한 요약 문장으로 재작성.

## Design Notes

`pg_dump --single-transaction`은 REPEATABLE READ 스냅샷 하나로 전체 덤프를 읽어 "transaction-consistent"를 보장하는 표준 방법이며, `--format=plain`을 선택한 이유는 복원 시 이 저장소가 이미 쓰고 있는 `psql -f` 패턴(`test.yml`의 `sql-outbox-tests`)을 그대로 재사용해 `pg_restore`라는 별도 도구·포맷을 새로 들이지 않기 위함이다.

`packages/read-model`은 현재 "구조만"(실제 DB 코드젠 파이프라인 없음) 상태라, AC의 "read-model 생성"은 `get_dashboard_snapshot()` RPC를 호출하는 `test_dashboard_snapshot.sql` 통과로 대체 검증한다(읽기 계약이 복원 후에도 유효함을 확인하는 것이 이 저장소에서 실제로 존재하는 유일한 read-model 검증 수단). `test_run_lineage.sql`은 `logical_runs`의 canonical pointer 정합을 검증하므로 별도 canonical-pointer 전용 스크립트를 새로 만들지 않는다.

RTO 실측치는 CI job의 실제 소요 시간(수 분)으로 기록되며, 이는 사람의 실제 장애 대응 시간을 포함한 완전한 RTO 시뮬레이션이 아니라 "자동화된 복원 절차 자체가 8시간보다 훨씬 빠르게 완료 가능함"을 보이는 하한 근거임을 문서에 명시한다.

## Verification

**Commands:**
- `act -W .github/workflows/backup.yml` 또는 로컬 `bash` 스크립트 추출 실행(로컬 Docker 필요 시) -- expected: `pg_dump`→`age` 암호화→manifest 생성까지 로컬 disposable Postgres 대상으로 오류 없이 완료(단, 실제 프로덕션 `SUPABASE_DB_URL` 없이는 로컬 fixture DB로만 검증 가능).
- `npm run typecheck` -- expected: 오류 없음(신규 파일은 워크플로/문서뿐이라 영향 없음을 확인).

**Manual checks (if no CLI):**
- `age-keygen`으로 키쌍을 생성해 GitHub repository secret에 `BACKUP_AGE_PUBLIC_KEY`/`BACKUP_AGE_PRIVATE_KEY`로 등록하고, Supabase 대시보드에서 직접 연결 문자열을 `SUPABASE_DB_URL` secret으로 등록한다.
- `backup.yml`을 `workflow_dispatch`로 1회 수동 실행해 artifact(암호화 덤프+manifest)가 생성되는지 Actions 탭에서 확인한다.
- `backup-restore-drill.yml`을 `workflow_dispatch`로 1회 수동 실행해 복원·smoke test·RPO/RTO 로그가 성공적으로 기록되는지 확인한다.
- 의도적으로 `SUPABASE_DB_URL`을 잘못된 값으로 바꿔 `backup.yml`을 실행해 `backup-failed` Issue가 실제로 생성되는지 확인한 뒤 값을 원복한다.

## Auto Run Result

**요약:** AD-17(백업 & 복원 검증)을 구현했다: 6시간마다 transaction-consistent `pg_dump`를 `age`로 암호화해 manifest와 함께 GitHub Actions artifact(14일 보관)로 남기는 `backup.yml`, 그리고 분기 1회 최신 백업을 disposable Postgres에 복원해 신규 migration 적용·SQL fixture(read-model 계약·canonical pointer 정합)·RPO/RTO 실측을 검증하는 `backup-restore-drill.yml`을 신설했다. age 키쌍 생성·GitHub secret 등록·release 차단 수동 게이트는 `docs/backup-restore.md`에 문서화했다(계정 자격증명이 없어 이 세션에서 직접 수행 불가, story 1.11과 동일 패턴).

**변경 파일:**
- `.github/workflows/backup.yml`(신규) — 6시간 cron + `workflow_dispatch`, dump→암호화→manifest→artifact 업로드, 실패 시 GitHub Issue(라벨 `backup-failed`, 중복 방지).
- `.github/workflows/backup-restore-drill.yml`(신규) — 분기 1회 schedule + `workflow_dispatch`, 최신 artifact 탐색·검증·복호화→pg_cron/pg_net 구문 제거→disposable Postgres 복원→신규 migration 적용→SQL fixture 실행→RPO/RTO 로그, 실패 시 GitHub Issue(라벨 `restore-drill-failed`, 중복 방지).
- `docs/backup-restore.md`(신규) — age 키쌍 생성, 3개 GitHub secret 등록, 두 워크플로 동작 설명·설계 근거, fork 비노출 근거(AD-11), 수동 release 차단 프로세스, 최초 1회 수동 검증 체크리스트.

**리뷰 결과 (2026-09-02 pass):** blind-hunter/edge-case-hunter/verification-gap/intent-alignment 4개 레이어 병렬 실행. patch 7건(high 1, medium 4, low 2) 확정 및 전부 수정·재검증 완료 — 가장 중요한 것은 production에 이미 적용된 pg_cron/pg_net migration 때문에 실제 백업에는 해당 구문·데이터가 dump 본문에 그대로 포함되어 있어, extension이 없는 disposable Postgres 복원이 매번 실패할 뻔한 결함(high, verification-gap이 발견)을 복원 전 필터링 스텝으로 해결했다. 나머지 6건(artifact 페이지네이션 버그, job timeout 부재, Issue 스팸, manifest null 검증 부재, 음수 RPO 미방지, 문서의 미완성 참조)도 모두 수정했다. defer 1건(low) — `postgres:16` floating tag의 실제 운영 버전 불일치 가능성은 `test.yml`의 기존 관례 연장이라 frontmatter `deferred`에 기록. dismissed 6건 — 전부 GitHub Actions의 플랫폼 차원 secret 마스킹, epics.md AC 범위 밖, 기존 AD-10 아키텍처 결정, 또는 현재 저장소 사용 패턴상 발생 경로 없음을 근거로 기각(세부 근거는 Review Triage Log 참고).

**검증 수행:**
- `python3 -c "import yaml; yaml.safe_load(...)"` — 두 워크플로 YAML 모두 패치 전/후 파싱 성공.
- pg_cron/pg_net 필터링 Python 스크립트를 워크플로에서 추출해 `python3 -m py_compile`로 컴파일 검증 통과, 필터링 로직을 실제 `202609021100_schedule_dispatch_worker_cron.sql` 내용과 대조해 pg_dump 산출물(CREATE EXTENSION·COPY cron.job 데이터·setval)을 정확히 겨냥함을 확인.
- `npm run typecheck` — 기존 베이스라인 오류(story 1.11에서도 동일하게 기록된 `@/lib/*` path-alias 미해결)와 동일, 이번 변경과 무관함을 `git diff`로 확인(TS 파일 미변경).
- `act`/`docker` 로컬 미설치로 워크플로의 실제 실행(로컬 dry-run)은 수행하지 못했다 — spec Verification 자체가 이 경우를 "로컬 Docker 필요 시" 조건부로 명시하고 있다.

**잔여 위험:**
- 두 워크플로 모두 GitHub Actions에서 실제로 한 번도 실행된 적이 없다(신규 secret 미등록, 로컬 실행 도구 부재) — `docs/backup-restore.md`의 최초 1회 수동 검증 체크리스트(age 키쌍 생성→secret 등록→`workflow_dispatch` 수동 실행→의도적 실패 유도)를 Neo가 직접 수행해야 story 1.12의 실사용 목표(실제 백업·복원 가능함이 검증됨)가 완성된다.
- `postgres:16` floating tag가 실제 운영 Supabase Postgres 버전과 정확히 일치하는지는 미확인 상태다(frontmatter `deferred` 기록, `test.yml`부터의 기존 관례).
