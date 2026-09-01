# Reviewer Gate — Technology Currency & Platform Fit

- **대상:** `ARCHITECTURE-SPINE.md` (2026-08-31 draft)
- **검증 기준일:** 2026-09-01 (Asia/Seoul)
- **검증 방법:** 문서에 명명된 런타임·프레임워크·SDK·관리형 기능을 공식 문서, 공식 릴리스 페이지, 공식 패키지 레지스트리와 대조했다. 저장소에는 아직 `package.json`, lockfile, `pyproject.toml`, `uv.lock`이 없으므로 현재 Stack 표가 유일한 cold-start 버전 권위다.
- **판정:** **REJECT — 구현 착수 전 보완 필수.** Node.js 20과 Next.js 14는 이미 공식 지원이 끝났고, AD-19의 PostgreSQL DDL은 실행 불가능하다. AD-18의 reconciler 폴백 중 GitHub Actions 30초 스케줄도 플랫폼이 지원하지 않는다. 나머지 구성요소는 교체·계약 보완 후 사용할 수 있다.

## Findings

### TC-01 — 웹 런타임 seed가 EOL/unsupported이며 현재 Supabase SDK로 안전하게 전진할 수 없다 (BLOCKER)

**문서 위치:** Stack `ARCHITECTURE-SPINE.md:267-274`

- Node.js `20.18.0 LTS`는 기준일 현재 LTS가 아니다. Node 공식 수명표에서 v20은 **2026-03-24 EOL**이며 보안 수정이 중단됐다. 현재 LTS 라인은 v24이고 기준일 최신 Krypton patch는 **24.20.0**이다.
- Next.js `14.2.15 LTS`도 현재 LTS가 아니다. Next 공식 지원 정책은 **16.x Active LTS**, **15.x Maintenance LTS**, **14.x unsupported**로 명시한다. 공식 2026-08 보안 공지는 16.3.3 또는 15.5.24로 즉시 갱신하도록 요구했고, 2026-09-01 npm `latest`는 **16.3.4**다.
- React/React DOM 18.3.1은 React 19 전환 경고용 릴리스로는 실재하지만, Next 16 App Router의 현재 기준은 React 19.2다. Stack에 있는 `react-dom`도 React와 동일 patch로 맞춰야 한다.
- `@supabase/supabase-js 2.45.6`, `@supabase/ssr 0.5.1`, Playwright 1.48.1은 모두 2024 seed다. 기준일 공식 registry stable은 각각 **2.112.4**, **0.12.5**, **1.62.1**이며, 현행 `supabase-js`는 Node **>=22**를 요구하므로 EOL Node 20을 유지한 채 SDK만 갱신할 수도 없다.

**영향:** 공개 웹/dispatch 인증 경계가 지원 종료 런타임과 프레임워크 위에서 시작한다. 보안 patch를 받지 못하며, 구현 직후 SDK 업그레이드가 Node major 업그레이드를 연쇄 요구한다.

**필수 보완:** cold-start seed를 최소 `Node.js 24.20.0 LTS`, `Next.js 16.3.4`, `React/react-dom 19.2.8`, `@supabase/supabase-js 2.112.4`, `@supabase/ssr 0.12.5`, `Playwright 1.62.1`로 갱신한다. TypeScript는 현재 registry latest 7.0.2지만 Next 16의 공식 최소는 5.1이므로, 호환성 우선이면 5.9.3을 명시적으로 선택하고 TS 7 승격 조건을 남겨도 된다. exact pin과 frozen install을 첫 구현 커밋부터 강제한다.

**공식 근거:** [Node release status](https://nodejs.org/en/about/previous-releases), [Node EOL 설명](https://nodejs.org/en/about/eol), [Next.js support policy](https://nextjs.org/support-policy), [Next.js 16 upgrade requirements](https://nextjs.org/docs/app/guides/upgrading/version-16), [Next.js blog/security releases](https://nextjs.org/blog), [React versions](https://react.dev/versions), [supabase-js releases](https://github.com/supabase/supabase-js/releases), [supabase SSR releases](https://github.com/supabase/ssr/releases), [Playwright release notes](https://playwright.dev/docs/release-notes), [npm registry](https://registry.npmjs.org/)

### TC-02 — Python major는 유지 가능하지만 exact data stack은 2024 patch에 고정돼 있다 (HIGH)

**문서 위치:** Stack `ARCHITECTURE-SPINE.md:262-266`

| 구성요소 | 문서 seed | 2026-09-01 공식 stable | 판정 |
| --- | ---: | ---: | --- |
| Python | 3.12.7 | 3.12.14 (동일 major), 3.14.7 (최신 feature line) | 3.12는 지원 중이나 patch 갱신 필요 |
| pandas | 2.2.2 | 3.0.5 | 대폭 후행; 3.0은 breaking migration 필요 |
| NumPy | 1.26.4 | 2.5.2 | 두 major 세대 후행 |
| HTTPX | 0.27.2 | 0.28.1 | patch/minor 갱신 필요 |
| PyArrow | 15.0.1 | 25.0.1 | 10 major 후행 |

Python 3.12 자체는 2028년까지 security maintenance 대상이므로 major 강제 교체 사유는 없다. 다만 3.12.7은 3.12.14로 대체됐다. pandas 3.0은 기본 string dtype과 Copy-on-Write 등 동작 변경이 있으므로 단순 숫자 치환은 위험하다. AD-5의 golden Jaccard gate와 기존 backtest 테스트로 2.3 경유 경고 제거 후 3.0을 검증해야 한다.

**필수 보완:** 위험이 낮은 선택은 먼저 `Python 3.12.14 + HTTPX 0.28.1`로 보안 patch를 닫고, pandas/NumPy/PyArrow는 호환성 branch에서 `3.0.5/2.5.2/25.0.1` 조합을 골든 fixture로 검증하는 것이다. 완전 cold start라면 Python 3.14.7까지 한 번에 검증할 수 있으나, 기존 `backtest` 호환성 증거 없이 최신 major라는 이유만으로 고정하지 않는다.

**공식 근거:** [Python 3.12 releases](https://www.python.org/doc/versions/), [Python 3.14.7](https://www.python.org/downloads/release/python-3147/), [pandas 3.0 release notes](https://pandas.pydata.org/docs/whatsnew/v3.0.0.html), [pandas release index](https://pandas.pydata.org/docs/whatsnew/index.html), [NumPy releases](https://numpy.org/news/), [Apache Arrow releases](https://arrow.apache.org/release/), [HTTPX official repository/releases](https://github.com/encode/httpx/releases), [PyPI registry](https://pypi.org/)

### TC-03 — AD-19의 canonical partial unique index는 PostgreSQL에서 생성할 수 없다 (BLOCKER)

**문서 위치:** `ARCHITECTURE-SPINE.md:238`

다음 predicate는 다른 테이블을 읽는 subquery를 포함한다.

```sql
WHERE contrib_run_id IN (
  SELECT canonical_attempt_run_id FROM logical_runs
)
```

PostgreSQL은 index predicate가 해당 테이블 행의 컬럼만 참조하도록 제한하며 subquery와 aggregate를 금지한다. 따라서 이 DDL은 Supabase Postgres engine version과 무관하게 migration에서 실패한다.

**필수 보완:** canonical contribution 전용 테이블을 `(logical_run_key, candidate_id)` PK로 분리하거나, 동일 테이블에 transaction이 관리하는 `is_canonical`/`canonical_generation` 컬럼을 두고 그 **로컬 컬럼만** 사용하는 partial unique index로 바꾼다. canonical 전환은 `logical_runs` 행 잠금과 이전/신규 canonical 전환을 하나의 RPC transaction에서 수행해야 한다.

**공식 근거:** [PostgreSQL `CREATE INDEX`](https://www.postgresql.org/docs/current/sql-createindex.html)

### TC-04 — outbox reconciler의 세 가지 실행 수단이 동등하지 않고 GitHub 30초 폴백은 불가능하다 (HIGH)

**문서 위치:** `ARCHITECTURE-SPINE.md:228-229`

- **pg_cron 10초:** 실재하고 적합하다. Supabase Cron은 초 단위 실행을 지원하며 공식 quickstart는 Postgres `15.1.1.61+` 조건을 명시한다. upstream pg_cron도 `'10 seconds'`를 지원한다. 다만 문서는 engine version을 bind하지 않으므로 project provision acceptance check가 필요하다.
- **GitHub Actions 30초:** 불가능하다. `schedule`의 최단 주기는 **5분**이다. scheduled workflow는 default branch에서만 실행되고, 고부하 시 지연 또는 drop될 수 있으며 public repository가 60일 비활성일 때 자동 비활성화될 수 있다. 따라서 low-latency outbox 복구나 유일한 분기 restore-drill 증거로 사용할 수 없다.
- **LISTEN/NOTIFY worker:** 가능하지만 persistent session 계약이 빠졌다. `LISTEN` 등록은 세션 종료 시 사라지며 notification은 durable queue가 아니다. Supavisor transaction mode는 `LISTEN/NOTIFY`와 session advisory lock을 지원하지 않으므로 direct connection 또는 session mode의 장기 실행 worker가 필요하다. worker는 시작 시 outbox를 먼저 scan하고 이후 notification을 wake-up hint로만 사용해야 한다.
- **Database Webhooks:** row event 후 외부 HTTP endpoint를 비동기로 호출하는 `pg_net` wrapper다. DB 내부 reconciler 함수를 직접 실행하는 LISTEN 대체물이 아니다. 수신 endpoint, 인증, retry/dead-letter, 중복 전달 처리가 별도 계약이어야 한다. `pg_net` API는 Supabase 문서상 beta다.

**필수 보완:** primary를 `persistent worker + direct/session-mode connection` 또는 `Database Webhook -> authenticated worker/Edge Function` 중 하나로 고정한다. 두 방식 모두 lease 기반 outbox scan을 권위로 삼고 notification/webhook은 wake-up hint로만 취급한다. fallback은 검증된 Supabase `pg_cron '10 seconds'`로 고정하고 GitHub 30초 문구를 삭제한다. GitHub는 5분 이상의 최종 dead-man sweep 용도로만 둘 수 있다.

**공식 근거:** [Supabase Cron](https://supabase.com/docs/guides/cron), [Supabase Cron quickstart](https://supabase.com/docs/guides/cron/quickstart), [pg_cron syntax](https://github.com/citusdata/pg_cron), [GitHub workflow schedule](https://docs.github.com/en/actions/reference/workflows-and-actions/workflow-syntax#onschedule), [GitHub scheduled event caveats](https://docs.github.com/en/actions/reference/workflows-and-actions/events-that-trigger-workflows#schedule), [PostgreSQL LISTEN](https://www.postgresql.org/docs/current/sql-listen.html), [PostgreSQL NOTIFY](https://www.postgresql.org/docs/current/sql-notify.html), [Supabase connection modes](https://supabase.com/docs/guides/database/connecting-to-postgres), [Supabase Database Webhooks](https://supabase.com/docs/guides/database/webhooks), [Supabase pg_net](https://supabase.com/docs/guides/database/extensions/pg_net)

### TC-05 — migration의 `up/down` 쌍 계약과 Supabase CLI의 실제 migration 모델이 일치하지 않는다 (HIGH)

**문서 위치:** `ARCHITECTURE-SPINE.md:60`

Supabase CLI의 권위 있는 migration 파일 형식은 `supabase/migrations/<timestamp>_<name>.sql` 단일 파일이다. `supabase migration down`은 별도 `.down.sql` 쌍을 실행하는 계약이 아니라 선택한 버전까지 DB 상태를 reset/replay하는 명령으로 문서화되어 있다. 따라서 “`supabase migration` 사용 + 모든 migration은 up/down 쌍 + CI에서 down 실행”은 구현자가 동시에 만족할 수 있는 구체 계약이 아니다. `schema_version`도 Supabase가 이미 관리하는 `supabase_migrations.schema_migrations`와 이중 권위가 된다.

**필수 보완:** 둘 중 하나를 선택한다.

1. Supabase CLI를 권위로 쓸 경우 forward-only additive migration, `db reset --last/--version`을 이용한 재구축 테스트, PITR/forward-fix rollback을 계약으로 삼고 custom `schema_version`을 제거한다.
2. `.up.sql/.down.sql` 쌍이 불변식이면 `golang-migrate`를 유일한 migration runner로 정하고 Supabase CLI는 local services/types 용도로만 제한한다.

운영에서 destructive `migration down --linked`를 rollback 절차로 사용하면 안 된다.

**공식 근거:** [Supabase CLI migration reference](https://supabase.com/docs/reference/cli/supabase-migration), [Supabase database migrations](https://supabase.com/docs/guides/deployment/database-migrations), [golang-migrate migration format](https://github.com/golang-migrate/migrate/blob/master/MIGRATIONS.md)

### TC-06 — GitHub concurrency는 적합하지만 실제 expression과 충돌 도메인을 명시해야 한다 (MEDIUM)

**문서 위치:** `ARCHITECTURE-SPINE.md:73,222`

`cancel-in-progress: true`와 DB fence를 함께 쓰는 방향은 적합하다. 다만 `group: logical_run_key`를 그대로 쓰면 문자열 상수 하나가 되어 모든 logical run이 같은 그룹에 들어간다. 실제 workflow에서는 `${{ inputs.logical_run_key }}` 같은 expression으로 전달해야 하며, 서로 다른 workflow도 같은 repository concurrency namespace를 공유한다. group 이름은 case-insensitive이므로 logical key의 대소문자 정규화도 DB와 일치해야 한다.

**필수 보완:** 예를 들어 `group: wave-double-${{ inputs.logical_run_key }}`처럼 실제 YAML을 고정하고, schedule/manual 모두 동일한 canonical serialization을 사용하도록 contract test를 둔다. GitHub 취소는 DB transaction과 원자적이지 않으므로 현재 fence/CAS가 최종 권위라는 문구는 유지한다.

**공식 근거:** [GitHub Actions concurrency](https://docs.github.com/en/actions/reference/workflows-and-actions/workflow-syntax#concurrency)

## 확인된 적합 항목

- Supabase `publishable key`/`secret key` 명칭과 browser/server secret 분리는 현재 플랫폼 방향과 맞다.
- PostgreSQL `timestamptz`, partial unique index 자체, RLS, advisory lock, `numeric`, JSONB, view/RPC 사용은 hosted Supabase에 적합하다. 단, AD-19처럼 타 테이블 subquery를 predicate에 넣는 구체 DDL은 제외한다.
- Supabase Cron/pg_cron의 10초 schedule은 provider provision 시 engine 최소 버전을 확인한다는 조건으로 적합하다.
- GitHub Actions `concurrency.cancel-in-progress`는 지원되며 DB fencing과 병행하는 선택이 타당하다.
- `ubuntu-22.04` hosted runner label은 기준일에도 공식 지원된다. 다만 cold-start라면 `ubuntu-24.04`가 현재 기본 Ubuntu LTS에 가깝고, exact runtime은 `setup-node`/`setup-python` 또는 `uv`로 명시해야 runner preinstall에 의존하지 않는다.
- 2026-02부터 GitHub workflow dispatch API는 `return_run_details`를 사용하면 run ID/URL을 직접 반환할 수 있다. AD-18의 `github_dispatch_id`는 이 기능과 API version을 명시해 polling correlation을 단순화할 수 있다.

## 구현 전 최소 보완 순서

1. TC-03의 실행 불가능한 index DDL을 교체한다.
2. TC-01의 EOL Node/unsupported Next 조합을 지원 중인 LTS 조합으로 갱신하고 lockfile을 생성한다.
3. TC-04의 reconciler 배포·연결·fallback 계약을 하나의 실행 가능한 경로로 고정한다.
4. TC-05에서 migration runner와 rollback 모델을 하나만 선택한다.
5. Python data stack 업그레이드를 AD-5 golden fixture로 검증하고 exact pin을 확정한다.

위 1~4가 스파인에 반영되기 전에는 technology-currency gate를 통과시키면 안 된다.

