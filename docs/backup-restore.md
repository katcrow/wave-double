# 백업 & 복원 검증 가이드 (spec-1-12)

이 문서는 spec-1-12(백업 & 복원 검증, AD-17)의 산출물이다. `.github/workflows/backup.yml`과
`.github/workflows/backup-restore-drill.yml`이 무엇을 자동으로 하는지, 그리고 이 세션(에이전트)이
계정 자격증명 부재로 실제 실행할 수 없는 절차(age 키쌍 생성, GitHub secret 등록)를 Neo가 수행하는
방법을 다룬다(story 1.11 `docs/deployment.md`와 동일한 Manual-check 위임 패턴).

## 배경: 왜 필요한가

무료 Supabase 플랜에는 PITR(Point-In-Time Recovery)이 없다. 운영 DB가 손상되면 실전 데이터를
영구히 잃을 수 있다. `backup.yml`이 6시간마다 암호화된 `pg_dump`를 GitHub Actions artifact로
남기고, `backup-restore-drill.yml`이 분기 1회 그 백업이 실제로 복원 가능한지 검증한다.

목표: **RPO 6시간, RTO 8시간**(ARCHITECTURE-SPINE.md AD-17).

## ① age 키쌍 생성

age는 백업 파일을 암호화하는 데 쓰는 공개키 암호화 도구다. 로컬 머신(또는 안전한 환경)에서
1회만 생성한다.

```bash
# age-keygen은 apt/brew/scoop 등으로 설치 가능하다 (https://github.com/FiloSottile/age)
age-keygen -o wave-double-backup-key.txt
```

출력 예시:

```
# created: 2026-09-02T00:00:00Z
# public key: age1xxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxxx
AGE-SECRET-KEY-1XXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXXX
```

- `# public key: age1...` 줄의 값이 `BACKUP_AGE_PUBLIC_KEY`다.
- `AGE-SECRET-KEY-1...` 줄이 `BACKUP_AGE_PRIVATE_KEY`다.

**이 파일(`wave-double-backup-key.txt`)을 안전한 곳(예: 비밀번호 관리자)에 별도 보관하고,
저장소에는 절대 커밋하지 않는다.** 개인키를 잃으면 기존 백업을 아무도 복호화할 수 없다.

## ② GitHub repository secret 등록

GitHub 저장소 > Settings > Secrets and variables > Actions > "New repository secret"에서
아래 3개를 등록한다.

| Secret 이름 | 값 | 용도 |
| --- | --- | --- |
| `SUPABASE_DB_URL` | Supabase 대시보드 > Project Settings > Database > Connection string(직접 Postgres 연결, 비밀번호 포함) | `backup.yml`이 `pg_dump`로 연결 |
| `BACKUP_AGE_PUBLIC_KEY` | ①의 `age1...` 공개키 | `backup.yml`이 백업을 암호화 |
| `BACKUP_AGE_PRIVATE_KEY` | ①의 `AGE-SECRET-KEY-1...` 개인키 | `backup-restore-drill.yml`이 복원 검증 시에만 복호화 |

주의:
- `SUPABASE_DB_URL`은 비밀번호를 포함한 연결 문자열이므로 절대 로그·Issue 본문·코드에 남기지
  않는다. 두 워크플로 모두 이 값을 셸 변수로만 다루고 echo하지 않는다.
- `BACKUP_AGE_PRIVATE_KEY`는 `backup.yml`에는 필요 없다(공개키만 있으면 암호화 가능). 복원
  드릴에만 등록한다 — 이렇게 하면 매 6시간 실행되는 백업 워크플로가 개인키를 다룰 필요가 없어
  노출 표면이 줄어든다.
- `.env.example`에는 추가하지 않는다. 이 3개 secret은 앱 런타임(Vercel)이 아니라 GitHub Actions
  전용이기 때문이다(스코프 결정).

## ③ 두 워크플로가 자동으로 하는 일

### `backup.yml` (6시간마다: UTC 00/06/12/18시, 그리고 `workflow_dispatch`로 수동 실행 가능)

1. `pg_dump --format=plain --single-transaction --no-owner --no-privileges`로 transaction-consistent
   덤프를 만든다.
   - `--single-transaction`: 하나의 REPEATABLE READ 스냅샷으로 전체 덤프를 읽어
     transaction-consistent를 보장하는 표준 방법이다.
   - `--format=plain`: 복원 시 `pg_restore`라는 별도 도구를 새로 들이지 않고, 이 저장소가 이미
     쓰는 `psql -f` 패턴(`test.yml`의 `sql-outbox-tests`)을 그대로 재사용하기 위함이다.
   - `--no-owner --no-privileges`: 복원 대상인 disposable Postgres(`postgres:16` 컨테이너)에는
     Supabase 전용 role(`anon`/`authenticated`/`service_role` 등)이 없다. 이 role을 참조하는
     `OWNER TO` / `GRANT` 구문이 덤프에 남아 있으면 plain `psql -f` 복원이 role 부재로 깨진다.
     데이터·스키마 자체의 transaction-consistency와는 무관한 순수 이식성 옵션이다.
2. `age -r <공개키>`로 암호화하고 평문 덤프는 즉시 삭제한다.
3. manifest.json(`schema_migration_version`, `cutoff_utc`, `checksum_sha256`)을 만든다.
4. 암호화 백업 + manifest를 `wave-double-backup-<타임스탬프>` 이름의 artifact로
   `actions/upload-artifact@v4`(`retention-days: 14`)에 업로드한다.
5. 어느 스텝이든 실패하면 `backup-failed` label의 GitHub Issue를 만든다(secret 값은 노출하지
   않는다).

### `backup-restore-drill.yml` (분기 1회: 1/4/7/10월 1일 UTC 00:00, 그리고 `workflow_dispatch`로 수동 실행 가능)

1. GitHub Actions REST API(`gh api .../actions/artifacts`)로 만료되지 않은
   `wave-double-backup-*` artifact 중 가장 최신 것을 찾아 다운로드한다.
2. manifest의 `checksum_sha256`과 다운로드한 암호화 파일의 실제 체크섬을 비교해 무결성을
   확인한다.
3. `age -d`로 복호화한다(이때만 `BACKUP_AGE_PRIVATE_KEY`를 사용).
4. `test.yml`의 `sql-outbox-tests` job과 동일한 disposable `postgres:16` 컨테이너에 복원한다.
5. manifest의 `schema_migration_version`보다 사전순으로 뒤인 migration 파일이 있으면 순서대로
   추가 적용한다(`pg_cron`/`pg_net`이 필요한 migration은 CI에 없으므로 기존 관례대로 건너뛴다).
6. `tests/sql/test_dashboard_snapshot.sql`(read-model 조회 계약)과
   `tests/sql/test_run_lineage.sql`(canonical pointer 정합)을 실행한다.
   - `packages/read-model`은 아직 "구조만"이라 실제 DB 코드젠 파이프라인이 없다. AC의
     "read-model 생성" 검증은 `get_dashboard_snapshot()` RPC를 호출하는
     `test_dashboard_snapshot.sql` 통과로 대체한다 — 이것이 이 저장소에 실제로 존재하는 유일한
     read-model 검증 수단이다.
7. RPO(=manifest `cutoff_utc`와 드릴 실행 시각의 차이)와 RTO(=이 job의 실제 소요 시간)를
   워크플로 로그에 기록한다.
   - RTO는 job의 실제 소요 시간(수 분)이며, 사람의 실제 장애 대응 시간을 포함한 완전한 RTO
     시뮬레이션이 아니다. "자동화된 복원 절차 자체가 8시간보다 훨씬 빠르게 완료 가능함"을
     보이는 하한 근거임을 여기 명시한다.
8. RPO가 6시간을 초과하거나 어느 스텝이든 실패하면 `restore-drill-failed` label의 GitHub Issue를
   만든다.

## ④ fork 저장소에서 secret이 노출되지 않는 이유

두 워크플로 모두 `schedule:`과 `workflow_dispatch:`만 트리거로 두고 `pull_request:`는 두지
않는다. GitHub의 기본 동작상 **schedule 이벤트는 fork 저장소에서 실행되지 않는다**(fork는
자신의 schedule을 default branch 기준으로만 실행하며, upstream 저장소의 schedule 워크플로가
fork에서 트리거되는 일은 없다). `workflow_dispatch`도 저장소 자체(fork가 아닌 upstream)에서
쓰기 권한이 있는 사람만 실행할 수 있다. 따라서 fork에서 온 PR이 이 두 워크플로를 실행해
`SUPABASE_DB_URL`/`BACKUP_AGE_PRIVATE_KEY` 같은 production secret을 훔쳐볼 방법이 구조적으로
없다(AD-11). 이는 `scheduled-batch.yml`이 이미 따르는 것과 동일한 관례다.

## ⑤ 복원 드릴 실패 시 수동 release 차단 프로세스

이 저장소에는 Vercel 배포를 실제로 막는 CI 게이트가 없다(story 1.11 참고, Vercel의 자동
push-to-deploy를 막을 기존 메커니즘이 없다). 그래서 "release 차단"은 **사람이 지키는 수동
프로세스**다:

1. `backup-restore-drill.yml`이 실패했거나(`restore-drill-failed` Issue 생성) RPO가 6시간을
   초과하면, 그 Issue가 닫히기 전까지 **production(main 병합)으로 이어지는 배포를 보류한다.**
   Neo가 직접 main 병합/배포를 미룬다.
2. 원인을 조사한다(예: `SUPABASE_DB_URL` 만료, age 키 분실, migration 비호환, artifact 만료
   등).
3. 원인을 해결한 뒤 `backup-restore-drill.yml`을 `workflow_dispatch`로 재실행해 통과를
   확인한다.
4. 통과하면 해당 Issue를 close하고 release를 재개한다.

대량 오염 복구(실제 장애 시나리오)의 큰 흐름은 AD-17이 정한 대로 schedule 정지 → backup
선택/검증 → restore → canonical pointer 검증 → schedule 재개 순이다. production 대상의 구체적인
복구 명령(어느 schedule을 어떻게 멈추고 어떤 psql/Supabase CLI 명령으로 실제 복원하는지 등)은
이 문서의 범위가 아니다 — 실제 장애·드릴 시점에 그때의 Supabase 프로젝트 상태를 보고 확정한다.

## ⑥ 최초 1회 수동 검증 체크리스트 (Manual, 계정 자격증명 필요)

이 세션(에이전트)은 Vercel/Supabase/GitHub 계정 자격증명이 없어 아래를 실제로 실행할 수
없다. Neo가 아래를 1회 수행해 AC들이 실제 운영 환경에서도 통과함을 확인한다.

- [ ] ①의 절차대로 age 키쌍을 생성한다.
- [ ] ②의 절차대로 `SUPABASE_DB_URL`, `BACKUP_AGE_PUBLIC_KEY`, `BACKUP_AGE_PRIVATE_KEY` 3개
      GitHub repository secret을 등록한다.
- [ ] `backup.yml`을 Actions 탭에서 `workflow_dispatch`로 1회 수동 실행하고, artifact
      (`wave-double-backup-*`, 암호화 덤프 + manifest.json)가 생성되는지 확인한다.
- [ ] `backup-restore-drill.yml`을 `workflow_dispatch`로 1회 수동 실행하고, 로그에서 복원 성공,
      두 SQL fixture 통과, RPO/RTO 실측치 기록을 확인한다.
- [ ] 의도적으로 `SUPABASE_DB_URL`을 잘못된 값으로 바꿔 `backup.yml`을 실행해
      `backup-failed` label의 Issue가 실제로 생성되는지 확인한 뒤, 값을 원래대로 되돌린다.
