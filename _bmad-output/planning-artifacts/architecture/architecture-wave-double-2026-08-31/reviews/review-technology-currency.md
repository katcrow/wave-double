# Reviewer Gate — Technology Currency & Fit (Final Re-review)

- **대상:** `ARCHITECTURE-SPINE.md` 수정본
- **기준일:** 2026-08-31 (Asia/Seoul)
- **렌즈:** named technology/version의 공식 소스·registry·현재 저장소 대조 및 요구 적합성
- **Verdict:** **CHANGES REQUIRED — 1 HIGH remaining.** 핵심 기술 조합과 요구 적합성은 확인됐고 이전 리뷰의 대부분이 해소됐다. 그러나 exact cold-start seed인 Node.js가 기준일 최신 24.x LTS patch가 아니므로 `verified-current` gate는 아직 통과하지 못한다.

## Remaining findings

### HIGH-1 — Node.js exact seed가 기준일 최신 LTS patch가 아니다

**Evidence**

- 수정본은 Node.js를 `24.17.0 LTS`로 고정했다.
- Node 공식 배포 인덱스에서 `24.17.0`은 2026-06-17 배포본이며, 기준일 최신 Krypton LTS는 **`24.20.0`**(2026-08-26, npm 11.19.0)이다.
- Node 24.x major 선택은 적절하다. Next.js 16.3.3은 Node `>=20.9.0`, `@supabase/supabase-js` 2.112.4는 Node `>=22.0.0`, Playwright 1.62.1은 Node `>=20`을 요구하므로 24.20.0과 모두 호환된다.

**Impact**

스파인이 exact version을 cold-start seed로 제시하는데 시작 시점부터 두 patch 뒤처진 런타임을 고정한다. 최신성뿐 아니라 이후 구현자가 “왜 24.17.0이어야 하는가”를 추측하게 한다.

**Disposition:** **autofix** — `Node.js 24.20.0 LTS`로 변경한다. 특별히 24.17.0을 유지해야 하는 검증된 호스팅 제약이 있다면 그 제약과 재검토 조건을 기록하되, 현재 스파인에는 그런 근거가 없다.

## Resolved / accepted findings

### RESOLVED — Next.js security-current patch

- 수정본의 **Next.js 16.3.3 Active LTS**는 npm `latest`이며, Next.js 공식 2026-08 보안 릴리스가 두 건의 Critical 취약점 대응을 위해 명시적으로 권고한 버전이다.
- React **19.2.8**은 Next 16.3.3 peer 범위와 호환된다.

### RESOLVED — 직접 toolchain과 Parquet/auth 의존성

- TypeScript **5.9.3**, `@supabase/ssr` **0.12.5**, Playwright **1.62.1**, PyArrow **25.0.1**이 Stack에 추가됐다.
- `@supabase/ssr` 0.12.5는 `@supabase/supabase-js ^2.112.4`를 요구하므로 선택한 2.112.4와 정확히 맞는다.
- Playwright 1.62.1은 Node >=20, PyArrow 25.0.1은 Python >=3.10을 요구하므로 선택한 런타임과 호환된다.
- PyArrow 추가로 기존 `pandas.read_parquet()` brownfield 경로의 실행 의존성이 명시됐다.
- AD-7이 Supabase JWKS 검증 방식을 명시해 dispatch 인증 경계가 구체화됐다.

### ACCEPTED WITH MEDIUM NOTE — TypeScript 5.9.3

- npm `latest`는 TypeScript **7.0.2**이지만, Next.js 16 공식 문서는 TypeScript **5.1+**를 지원하며 5.9.3은 해당 지원 범위 안이다.
- TypeScript 7은 2026-07 출시된 새 native port이고 Next 생태계 통합 이력이 짧다. 따라서 5.9.3을 호환성 우선 seed로 두는 것은 합리적이다.
- 다만 exact version 선정 근거가 memlog에 없다면 “TS7/Next 호환성 검증 후 승격”을 revisit condition으로 남기는 것이 좋다. 이는 gate-blocking High가 아니다.

### RESOLVED — manifest/lock 구조

- Structural Seed가 `pyproject.toml`, `uv.lock`, npm workspace `package.json`, `package-lock.json`을 명시한다.
- 실제 파일은 아직 생성 전이지만 이 문서는 cold-start build substrate이므로 구조 seed로 충분하다. 구현 첫 변경에서 lockfile을 함께 생성하고 CI에서 frozen install을 강제해야 한다.

### RESOLVED — Supabase engine 검증 과장

- `Supabase Postgres | provider-managed; engine version not bound`로 변경돼 실제 project가 없는 상태에서 검증일을 주장하던 문제가 해소됐다.
- advisory lock, RLS, view/RPC, `numeric`, `timestamptz`는 요구에 적합하다. project provision 시 실제 engine/service version과 local test image parity를 확인하면 된다.

### ACCEPTED — Python/data stack과 기존 코드 적합성

- Python **3.14.7**, pandas **3.0.5**, NumPy **2.5.2**, HTTPX **0.28.1**, PyArrow **25.0.1**은 기준일 정식 최신 release이며 서로의 Python 요구 조건을 충족한다.
- 이전 gate에서 Python 3.14 + pandas 3.0.5 + NumPy 2.5.2 + PyArrow로 기존 `backtest/tests`를 실행해 **16 passed**를 확인했다.
- HTTPX는 LS REST adapter에 적합하다. token bucket/backoff는 HTTPX 내장 기능이 아니며 AD-6대로 공통 adapter가 구현·테스트해야 한다.

### MEDIUM — `react-dom`이 Stack 표에 명시되지 않음

- Next 웹 런타임에는 `react-dom` 직접 의존성이 필요하고 기준일 npm `latest`는 React와 동일한 **19.2.8**이다.
- `package.json` 생성 시 `react`와 exact 동일 버전으로 pin해야 한다. Stack 표의 최소 seed 완결성을 위해 추가하는 편이 좋지만, 버전 선택이 사실상 React 행에서 결정되므로 본 gate의 High로 올리지는 않는다.

## Final verification matrix

| Named technology | Spine | 2026-08-31 registry/official result | Fit | Result |
| --- | --- | --- | --- | --- |
| Python | 3.14.7 | latest 3.14 patch | 기존 backtest와 검증됨 | PASS |
| pandas | 3.0.5 | PyPI latest | 기존 테스트 통과 | PASS |
| NumPy | 2.5.2 | PyPI latest | 기존 테스트 통과 | PASS |
| HTTPX | 0.28.1 | PyPI latest stable | LS adapter에 적합 | PASS |
| PyArrow | 25.0.1 | PyPI latest | Parquet 경로에 필요·적합 | PASS |
| Node.js | 24.17.0 LTS | latest 24.x LTS는 24.20.0 | 조합 호환성은 양호 | **UPDATE** |
| Next.js | 16.3.3 Active LTS | npm latest, 공식 보안 권고 | App Router/Route Handler에 적합 | PASS |
| React | 19.2.8 | npm latest | Next peer 범위 충족 | PASS |
| react-dom | 누락 | npm latest 19.2.8 | Next web에 필요 | MEDIUM ADD |
| TypeScript | 5.9.3 | latest는 7.0.2, Next 지원 범위 내 | 안정성 우선 선택으로 수용 | PASS / REVISIT |
| `@supabase/supabase-js` | 2.112.4 | npm latest, Node >=22 | Node 24와 호환 | PASS |
| `@supabase/ssr` | 0.12.5 | npm latest, supabase-js ^2.112.4 | 인증 경계에 적합 | PASS |
| Playwright | 1.62.1 | npm latest, Node >=20 | E2E에 적합 | PASS |
| Supabase Postgres | provider-managed | 실제 engine 의도적으로 미고정 | hosted 운영에 적합 | PASS / PROVISION CHECK |
| GitHub Actions runner | `ubuntu-24.04` | 공식 지원 label | public batch에 적합 | PASS |

## Sources

- [Python 3.14.7 release](https://www.python.org/downloads/release/python-3147/)
- [PyPI registry](https://pypi.org/)
- [Node.js 24.20.0 official archive](https://nodejs.org/en/download/archive/v24.20.0)
- [Node.js official distribution index](https://nodejs.org/dist/index.json)
- [Next.js August 2026 security release listing](https://nextjs.org/blog)
- [Next.js 16 upgrade requirements](https://nextjs.org/docs/app/guides/upgrading/version-16)
- [Next.js support policy](https://nextjs.org/support-policy)
- [npm registry](https://registry.npmjs.org/)
- [TypeScript 7 official release](https://devblogs.microsoft.com/typescript/announcing-typescript-7-0/)
- [Supabase platform version guidance](https://supabase.com/docs/guides/platform/upgrading)
- [GitHub-hosted runner labels](https://docs.github.com/en/actions/how-tos/write-workflows/choose-where-workflows-run/choose-the-runner-for-a-job)

## Gate recommendation

`Node.js 24.17.0 LTS`를 **24.20.0 LTS**로 갱신하면 기술 최신성의 남은 Critical/High는 없다. `react-dom 19.2.8` 명시는 구현 전 medium polish로 처리할 수 있다.
