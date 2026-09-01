---
title: '프로젝트 스캐폴딩 & 개발 환경 고정'
type: 'feature'
created: '2026-09-01'
status: 'done'
baseline_revision: 'b78141403d4d5624ee2263efcd80adaf6a58ea9d'
review_loop_iteration: 0
followup_review_recommended: true
context:
  - _bmad-output/planning-artifacts/architecture/architecture-wave-double-2026-08-31/ARCHITECTURE-SPINE.md
  - _bmad-output/specs/spec-wave-double/SPEC.md
  - _bmad-output/specs/spec-wave-double/backtest-baseline.md
warnings: [oversized]
deferred:
  - summary: >-
      Python 정밀 버전 편차(스펀 3.12.14 vs 로컬 uv 3.12.13)를 스파인 갱신으로 조정
    evidence: |-
      Windows uv 0.11.28 관리 인덱스에 cpython-3.12.14-windows-x86_64 다운로드가 없어 로컬은 가장 가까운 3.12.13으로 해석함. CI(setup-python 3.12.14)는 Linux에서 정상 동작. 스파인 "실패하면 이 spine을 갱신한다" 규칙과 정합되도록 아키텍처 스파인 업데이트 결정 필요.
    location: >-
      pyproject.toml:8
    severity: medium
  - summary: >-
      apps/batch에 pandas/pyarrow 의존성 미선언 (후속 스토리가 batch 로직 구현 시 필요)
    evidence: |-
      uv 워크스페이스에서 member 의존성은 상위로 자동 전파되지 않음. batch가 실제 LS/Supabase 로직(LS 1.3+)을 작성할 때 pandas/pyarrow import를 위해 자체 선언이 필요.
    location: >-
      apps/batch/pyproject.toml
    severity: low
  - summary: >-
      Pretendard 타이포그래피가 globals.css에 미적용
    evidence: |-
      UX 디자인 토큰 구현은 후속 UI 스토리(1.9) 범위이며 스캐폴딩 단계에선 의도적으로 미적용. UI 스토리에서 반영 필요.
    location: >-
      apps/web/app/globals.css
    severity: low
  - summary: >-
      ESLint/lint 설정 부재
    evidence: |-
      스펙의 검증 게이트는 typecheck/build이며 lint는 미요구. 코드 품질 강화를 위한 후속 항목으로 기록.
    severity: low
  - summary: >-
      backtest가 pytest를 dev 의존성으로 미선언 (AGENTS.md의 --with pytest 관례 사용)
    evidence: |-
      `uv run --with pytest`는 ephemeral 오버라이드로 AGENTS.md 관례와 일치하나 lockfile에 pytest 버전이 고정되지 않음. 필요 시 dev-dependency로 고정 고려.
    location: >-
      backtest/pyproject.toml
    severity: low
---

<intent-contract>

## Intent

**Problem:** wave-double의 배치·웹·DB 계약을 한 저장소에서 독립적으로 개발할 기본 골격(모노레포 구조, 고정 런타임, CI, 마이그레이션 규약)이 아직 없다. 도구가 아직 존재하지 않아 이후 에픽 1~5의 모든 스토리가 개발을 시작할 기반이 없다.

**Approach:** 아키텍처 스파인의 "Stack & Structural Seed"를 기준으로 Python(uv) 워크스페이스와 JS(npm workspaces) 모노레포를 만들고, 고정 버전의 lockfile, Supabase 마이그레이션 디렉터리·규약, CI 테스트 워크플로를 세운다. 기존 `backtest/` 커널은 로직 변경 없이 워크스페이스에 편입하고, 그 전체 테스트가 회귀망이므로 반드시 통과해야 한다.

## Boundaries & Constraints

**Always:**
- 파일·디렉터리 배치는 아키텍처 스파인의 "Stack & Structural Seed"와 일치한다: `apps/web`, `apps/batch`, `packages/domain`, `packages/read-model`, `backtest/`, `infra/supabase/migrations/`, `.github/workflows/`, `tests/fixtures/`.
- 런타임 버전은 스파인 Stack에 고정된 exact version(Python 3.12.14, pandas 3.0.5, NumPy 2.5.2, HTTPX 0.28.1, PyArrow 25.0.1, Node 24.20.0 LTS, Next.js 16.3.3, React/react-dom 19.2.8, TypeScript 5.9.3, supabase-js 2.112.4, @supabase/ssr 0.12.4, Playwright 1.62.1)을 따른다. 첫 lockfile은 이 exact version으로 생성한다.
- `backtest/` 커널의 로직을 변경하지 않는다(이식만). 이식 후 `backtest` 전체 테스트가 통과해야 한다.
- 런타임 고정은 lockfile + setup action(`actions/setup-python`/`actions/setup-node`)으로 한다(AD-11: runner preinstall 의존 금지).
- `apps/*`만 외부 I/O·프레임워크를 소유하고, `packages/domain`·`backtest`는 순수 계약만 노출한다(AD-1).
- DB contract는 Supabase CLI 단일 timestamp migration(`YYYYMMDDHHMM_description.sql`)이 권위다(AD-14).
- 언어 규약(파이썬 snake_case, TS PascalCase/함수 camelCase/라우트 kebab-case, DB snake_case)을 디렉터리 생성 시 준수한다.

**Never:**
- `backtest` 전략/지표 로직을 재작성하거나 버전을 임의로 낮추지 않는다. 호환 실패 시 스파인을 갱신한다.
- secrets(`.env.local` 등)를 커밋/트래킹하지 않는다. `.env.local`을 `.gitignore`에 유지한다.
- 도메인/전략이 Next.js·Supabase SDK·GitHub SDK·LS HTTP 형식을 import하지 않도록 구조만 세운다(AD-1).
- production migration·배치를 로컬/CI에서 실행하지 않는다(AD-11). 스토리 1-1은 스캐폴딩·로컬 검증만.

## I/O & Edge-Case Matrix

| Scenario | Input / State | Expected Output / Behavior | Error Handling |
|----------|--------------|---------------------------|----------------|
| PY_WORKSPACE | `uv.lock` 생성, `backtest/` 편입 | pip freeze에 스파인 고정 버전 존재, `backtest` pytest 16개 전부 통과 | 버전 불일치 시 스파인 갱신(임의 다운 금지) |
| JS_WORKSPACE | `npm install` 실행 | `package-lock.json`에 Next 16.3.3 등 고정 버전 해석, workspace 2개(`web`,`read-model`) 인식 | 독립 설치·버전 상승 없이 lockfile 기반 고정 |
| MIGRATION_DIR | `infra/supabase/migrations/` 생성 | `YYYYMMDDHHMM_*.sql` 명명 규약 README 존재, 빈 디렉터리로 시작 | 규약 위반 시 프로세스 실패 |
| CI_TEST | workflow 실행 | `ubuntu-24.04`, setup action으로 고정 런타임 설치, backtest 테스트 통과 | 테스트 실패 시 workflow 실패(regression 게이트) |

</intent-contract>

## Code Map

- `backtest/` -- 이미 존재하는 전략·지표·엔진 커널(이식 대상, 로직 변경 금지). `backtest/tests/`가 회귀망(현재 16 passed, `uv run --with pandas --with numpy --with pyarrow --with pytest pytest backtest -q`).
- `backtest/run.py` -- 백테스트 CLI 진입점(그대로 유지).
- `.env.local` -- Supabase/LS 자격증명(트래킹 금지, 참고용 로드).
- `.gitignore` -- 현재 `.env.local` 등 포함. 노드·uv 산출물 누락.
- `docs/` -- 기존 보조지표 문서. LS OpenAPI 참조 `docs/api/ls-openapi/`.
- `(신규) pyproject.toml` -- Python direct dependency authority + uv workspace 루트.
- `(신규) uv.lock` -- Python exact transitive lock.
- `(신규) .python-version` -- Python 3.12.14 고정.
- `(신규) package.json` -- npm workspaces 루트.
- `(신규) package-lock.json` -- JS exact transitive lock.
- `(신규) .nvmrc`, `engines` -- Node 24.20.0 고정.
- `(신규) apps/web` -- Next App Router 스캐폴드(보호 라우트).
- `(신규) apps/batch` -- Python CLI/오케스트레이터 스캐폴드.
- `(신규) packages/domain` -- 순수 규칙 패키지 스캐폴드.
- `(신규) packages/read-model` -- 생성 DB 타입·조회 계약 스캐폴드.
- `(신규) infra/supabase/migrations/` -- AD-14 single timestamp migration 규약.
- `(신규) .github/workflows/` -- CI 테스트 워크플로.
- `(신규) tests/fixtures/` -- golden signal·SQL parity·LS sample 위치.

## Tasks & Acceptance

**Execution:**
- `pyproject.toml` 생성 -- `[project]` deps 고정(pandas 3.0.5, numpy 2.5.2, httpx 0.28.1, pyarrow 25.0.1), `requires-python = "==3.12.14"`, `[tool.uv]` workspace로 `backtest`, `apps/batch`, `packages/domain` 멤버화.
- `.python-version` 생성 -- `3.12.14` 고정.
- `uv lock` 실행 -- `uv.lock`에 exact transitive 해석 생성.
- `backtest/` 이식 검증 -- 워크스페이스에 편입 후 `uv run --with pandas --with numpy --with pyarrow --with pytest pytest backtest -q`가 기존과 동일하게 통과하는지 확인(로직 무변경).
- `apps/batch/pyproject.toml` + `apps/batch/` 초기 패키지 -- Python 배치 진입점 스캐폴드(외부 I/O 소유).
- `packages/domain/pyproject.toml` + 초기 패키지 -- 순수 규칙, I/O 금지, 외부 라이브러리 import 금지.
- `package.json` 생성 -- `workspaces: ["apps/web", "packages/read-model"]`, `engines.node = ">=24.20.0"`, TS 5.9.3 devDependency.
- `.nvmrc` 생성 -- `24.20.0`.
- `apps/web/` Next App Router 스캐폴드 -- Next 16.3.3, React 19.2.8, TS, `@supabase/supabase-js` 2.112.4, `@supabase/ssr` 0.12.4 설치, 최소 홈 라우트 생성(빌드 성공 확인용).
- `packages/read-model/package.json` + 초기 TS -- 생성 DB 타입 스캐폴드(비어 있음, 구조만).
- `npm install` 실행 -- `package-lock.json`에 고정 버전 해석, workspace 2개 인식 확인.
- `infra/supabase/migrations/README.md` + `.gitkeep` -- AD-14 `YYYYMMDDHHMM_description.sql` 명명 규약 기록, 빈 시작.
- `.github/workflows/test.yml` -- `ubuntu-24.04`, `actions/setup-python`(3.12.14) + `actions/setup-node`(24.20.0), backtest pytest + JS typecheck 실행(json 파생).
- `tests/fixtures/.gitkeep` -- golden·parity·LS sample 디렉터리 스캐폴드.
- `.gitignore` 확장 -- `node_modules/`, `.next/`, `.venv/`, `.pytest_cache/`, `dist/`, `__pycache__/` 추가.

**Acceptance Criteria:**
- Given 새 Python 워크스페이스, when `uv run --with pandas --with numpy --with pyarrow --with pytest pytest backtest -q`를 실행하면, then 기존 `backtest` 테스트(16 passed)가 그대로 통과한다(로직 무변경 증명).
- Given `uv.lock`, when `uv lock` 후 의존성 트리를 조회하면, then pandas 3.0.5·numpy 2.5.2·httpx 0.28.1·pyarrow 25.0.1 등 스파인 고정 버전이 exact로 해석된다.
- Given npm workspaces, when `npm install` 후 `npm ls next react typescript`, then Next 16.3.3·React 19.2.8·TS 5.9.3가 설치되어 있고 workspace `web`과 `read-model`이 인식된다.
- Given 워크스페이스 루트, when `npx tsc --noEmit`(또는 typecheck 스크립트)을 실행하면, then 앱/패키지 TS가 타입 에러 없이 컴파일된다.
- Given `infra/supabase/migrations/`, when README를 확인하면, then `YYYYMMDDHHMM_description.sql` 단일 timestamp migration 명명 규약이 기록되어 있다.
- Given CI workflow, when test job이 `ubuntu-24.04`에서 실행되면, then setup action으로 고정 런타임을 설치하고 backtest 테스트가 통과한다.
- Given 저장소 상태, when `git status`를 확인하면, then `.env.local`·node_modules·`.next`·`.venv`가 트래킹되지 않는다.

## Spec Change Log

_Empty until first review loopback._

## Review Triage Log

### 2026-09-01 — Review pass
- intent_gap: 0
- bad_spec: 0
- patch: 5 (low 5)
- defer: 5 (medium 1, low 4)
- dismissed:
  - read-model/src/index.ts "참조되지만 생성되지 않음" — 반박됨: 파일이 실제로 존재(`export {};`)하며 diff에도 `packages/read-model/src/index.ts | 1 +`로 확인됨.
  - infra/supabase/migrations/.gitkeep 내용 포함 — 순수 미관상(none/cosmetic)이며 실질적 영향 경로가 입증되지 않아 기각.
- addressed_findings:
  - `[low]` `[patch]` CI test.yml에 `concurrency` 그룹 추가(중복/stale 실행 취소) — 적용 완료
  - `[low]` `[patch]` CI setup-uv에 `uv-version` 고정(0.11.28) — 적용 완료
  - `[low]` `[patch]` CI backtest 명령을 AGENTS.md 정식 명령(`--with pandas --with numpy --with pyarrow`)과 일치 — 적용 완료
  - `[low]` `[patch]` CI에 `npm run build`(웹 빌드) 게이트 추가 — 적용 완료
  - `[low]` `[patch]` `@types/react`/`@types/react-dom` exact 버전 고정 — 적용 완료

## Design Notes

- **단일 저장소 스캐폴딩 범위.** 스토리 1-1은 "골격 + 고정 환경"이다. 실제 스키마/스냅샷/전략 태깅 RPC/배치 로직은 이후 스토리(1.2~1.12)에서 채운다. 여기서는 빈 패키지·워크스페이스·규약·CI만 세우므로, 미완성 경고(예: `apps/web`가 아직 대시보드 로직 없음)는 의도된 상태다.
- **워크스페이스 경계.** `packages/domain`과 `backtest`는 순수 Python 계약만 노출(AD-1). `apps/batch`가 외부 I/O(LS·Supabase)를 소유. TS 측은 `packages/read-model`이 생성 타입만, `apps/web`이 UI·보호 라우트를 소유.
- **이식 vs 재작성.** `backtest`는 로직 보존이 AD 요건이다. 스캐폴딩은 이를 워크스페이스가 import 가능하게 배치·로드만 하며, `pyproject.toml`의 deps를 힌트로 `--with`를 lock으로 대체한다.
- **DB 권한 미확보.** 현재 Supabase MCP 토큰이 프로젝트 접근이 거부되어 실DB 마이그레이션 적용은 불가. 스토리 1-1은 로컬 디렉터리·규약만 스캐폴딩하고, 적용은 AD-14를 따르는 후속 스토리/배포 단계에서 수행. (Supabase CLI 미설치도 로컬 사유)

## Verification

**Commands:**
- `uv run --with pandas --with numpy --with pyarrow --with pytest pytest backtest -q` -- expected: 16 passed (기존 통과 유지, 로직 무변경)
- `uv lock` 후 `uv pip list` -- expected: pandas 3.0.5·numpy 2.5.2·httpx 0.28.1·pyarrow 25.0.1 exact
- `npm install` 후 `npm ls next react react-dom typescript @supabase/supabase-js @supabase/ssr` -- expected: 고정 버전 일치
- `npm run typecheck`(또는 `npx tsc --noEmit`) -- expected: 타입 에러 0
- `git status --porcelain` -- expected: secrets·산출물 미노출

**Manual checks (if no CLI):**
- `infra/supabase/migrations/README.md`에 `YYYYMMDDHHMM_description.sql` 규약 명시 확인
- 스파인 Stack과 각 패키지 선언 버전 일치 여부 눈으로 대조

## Auto Run Result

Status: done

**구현 요약:** 스토리 1-1(프로젝트 스캐폴딩 & 개발 환경 고정)을 구현함. 아키텍처 스파인의 "Stack & Structural Seed"를 기준으로 Python(uv) 워크스페이스와 JS(npm workspaces) 모노레포 골격을 세우고, 고정 버전 lockfile, Supabase 마이그레이션 규약 디렉터리, CI 테스트 워크플로, `.gitignore` 확장을 완료함. 기존 `backtest/` 커널은 로직 변경 없이 워크스페이스에 편입했고 전체 테스트가 통과함.

**변경 파일:**
- `pyproject.toml`, `.python-version`, `uv.lock` -- Python 워크스페이스 루트와 고정 버전 lock. deps: pandas 3.0.5·numpy 2.5.2·httpx 0.28.1·pyarrow 25.0.1.
- `backtest/pyproject.toml` -- 기존 커널을 워크스페이스 멤버로 편입(로직 무변경).
- `apps/batch/` -- Python 배치 스캐폴드(외부 I/O 소유, httpx 고정).
- `packages/domain/` -- 순수 규칙 패키지 스캐폴드(I/O·외부 import 없음).
- `package.json`, `package-lock.json`, `.nvmrc`, `tsconfig.json` -- JS 워크스페이스 루트와 lock. Node 24.20.0.
- `apps/web/` -- Next.js 16.3.3 App Router 스캐폴드(React 19.2.8, TS 5.9.3, supabase-js 2.112.4, @supabase/ssr 0.12.4). 홈 라우트 빌드 성공 확인.
- `packages/read-model/` -- 생성 DB 타입 스캐폴드(빈 구조).
- `infra/supabase/migrations/` -- AD-14 단일 timestamp migration 규약 README + `.gitkeep`.
- `.github/workflows/test.yml` -- CI: backtest pytest + JS typecheck + 웹 빌드, concurrency 그룹, 고정 런타임.
- `tests/fixtures/.gitkeep` -- golden·parity·LS sample 위치.
- `playwright.config.ts`, `e2e/home.spec.ts` -- 웹 스캐폴드 홈 라우트 렌더링 검증용 Playwright smoke E2E(사용자 요청의 "필요시 e2e" 충족).
- `package.json`(`@playwright/test` 1.62.1, `test:e2e` 스크립트), CI에 E2E 스텝 추가.
- `.gitignore` -- node/uv 산출물, secrets 미노출.
- `_bmad-output/implementation-artifacts/epic-1-context.md`, `spec-1-1-*.md` -- 계획/실행 산출물.

**리뷰 파인딩:**
- 적용된 patch 5건(모두 low): CI concurrency 그룹, uv-version 고정, backtest 명령 정식화(`--with pandas/numpy/pyarrow`), 웹 빌드 게이트, `@types/*` exact 고정.
- defer 5건: 파이썬 정밀 버전 스파인 조정(medium), apps/batch pandas/pyarrow 의존성 예고(low), Pretendard 타이포(후속 UI 스토리, low), ESLint 미설정(low), pytest dev-의존 미선언(low).
- dismissed: read-model/index.ts "미생성" 주장(반박), .gitkeep 내용(미관·무의미).

**후속 리뷰 권장:** patched 5건 전부 low → 스코어 3×0 + 1×5 = 5 ≥ 5 → `true`.

**검증:**
- `uv run --with pandas --with numpy --with pyarrow --with pytest pytest backtest -q` → **16 passed** (회귀망 유지, 로직 무변경).
- Python lock 정밀 버전: pandas 3.0.5·numpy 2.5.2·httpx 0.28.1·pyarrow 25.0.1 exact 해석.
- `npm ls next react react-dom typescript @supabase/supabase-js @supabase/ssr` → 16.3.3/19.2.8/5.9.3/2.112.4/0.12.4, workspace web·read-model 인식.
- `npm run typecheck` → 0 에러.
- `npm run build -w apps/web` → 빌드 성공(라우트 `/`).
- `npm run test:e2e` → Playwright smoke 1 passed(홈 라우트 렌더링).
- `git status --porcelain` → secrets(node_modules/.next/.venv/.env.local) 미노출.

**잔여 리스크:**
- 파이썬 정밀 버전 편차(스파인 3.12.14 vs 로컬 3.12.13): CI는 Linux setup-python 3.12.14로 스파인과 정합, 로컬은 Windows uv 제약으로 3.12.13. 스파인 갱신 결정 필요(defer로 기록).
- Supabase 접근 토큰 미권한으로 실DB 마이그레이션 적용 불가 — 스토리 1-1은 로컬 규약·디렉터리 스캐폴딩만 담당(의도된 범위).
- GitHub 워크플로는 로컬에서 실제 실행 불가(적법성은 config 검토만).
