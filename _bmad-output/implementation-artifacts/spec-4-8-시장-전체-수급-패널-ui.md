---
title: 'Story 4.8: 시장 전체 수급 패널 UI'
type: 'feature'
created: '2026-09-08'
status: 'done'
review_loop_iteration: 0
followup_review_recommended: true
baseline_revision: '534c03918f6dc5f883468b7380e5c1a5fc37bef5'
baseline_commit: '534c03918f6dc5f883468b7380e5c1a5fc37bef5'
context:
  - 'C:/dev/wave-double/_bmad-output/implementation-artifacts/epic-4-context.md'
warnings: []
deferred:
  - summary: >-
      인증된 complete snapshot을 대상으로 하는 시장 패널 브라우저 E2E fixture가 없어 CI에서 실제 데이터 탭 표면을 자동 검증하지 못한다.
    evidence: |-
      e2e/home.spec.ts는 미인증 redirect만 실행하며 인증 세션과 운영 complete snapshot fixture를 만들지 않는다. Playwright MCP로 현재 운영 데이터 없음 상태의 탭·URL·반응형·화살표 키 표면은 수동 확인했다.
    location: >-
      e2e/home.spec.ts
    severity: low
---

<intent-contract>

## Intent

**Problem:** 현재 홈에는 후보별 수급 근거만 있어 종목 데이터가 비어 있는 장중에 코스피/코스닥 시장 전체 흐름을 참고할 수 없다.

**Approach:** complete snapshot의 attempt에 귀속된 `market_supply` 행을 읽기 전용 RPC로 조회하고, 홈에 KOSPI/KOSDAQ 탭 패널을 추가한다. 외인·기관·개인·프로그램을 숫자와 방향 막대로 표시하며 시장 수급의 장중 신선도와 참고 성격을 명시한다.

## Boundaries & Constraints

**Always:** 요청한 `run_id`의 published complete snapshot 데이터만 읽고, 시장은 KOSPI/KOSDAQ 두 탭으로 고정한다. 네 투자자 지표는 원본 부호를 보존해 숫자와 매수/매도 방향 막대를 함께 표시하고, 0은 중립으로 표시한다. 패널에는 항상 `장중 참고` 라벨을 고정하고 시장 수급 전용 신선도 문구(예: `장중에도 갱신될 수 있음`)를 후보 수급과 구분해 표시한다. 탭 선택은 URL의 `market` 쿼리로 보존하며 허용되지 않은 값은 KOSPI로 정규화한다. 데이터 없음·RPC 실패는 빈 패널이나 정상 데이터로 위장하지 않고 명시적 상태로 렌더링한다.

**Never:** `market_supply` 테이블을 브라우저에서 직접 조회하거나 RLS를 우회하지 않는다. UI에서 수급 힌트·금융 판단·임계값을 계산하지 않는다. 기존 `get_dashboard_snapshot`, 후보 카드/evidence RPC, 후보 카드 레이아웃과 태그 동작을 변경하지 않는다. 실제 값의 부호를 절댓값으로 바꿔 방향을 잃거나 매수 권고 문구를 사용하지 않는다.

## I/O & Edge-Case Matrix

| Scenario | Input / State | Expected Output / Behavior | Error Handling |
|---|---|---|---|
| HAPPY_PATH | complete snapshot, 두 시장의 당일 행 | 기본 KOSPI 탭에서 네 지표를 숫자+방향 막대로 표시 | 없음 |
| TAB_PERSISTENCE | `?market=KOSDAQ` 또는 탭 클릭 | KOSDAQ 선택이 URL에 반영되고 새로고침 후 유지 | 잘못된 값은 KOSPI로 정규화 |
| INTRADAY | complete snapshot batch가 premarket/intraday | 상단 `장중 참고`와 시장 전용 신선도 문구를 함께 표시 | 후보 수급 신선도와 혼동하지 않음 |
| EMPTY_OR_ERROR | market section 없음, 행 부족, RPC 실패 | 패널은 유지하고 "시장 수급을 확인할 수 없습니다" 상태 표시 | 오류는 서버 로그에 기록하고 후보 화면은 계속 렌더 |

</intent-contract>

## Code Map

- `apps/web/app/page.tsx` -- complete snapshot의 `run_id`를 얻는 서버 표면. 후보 RPC와 독립적으로 시장 수급 read RPC를 호출하고, 실패가 기존 후보 렌더를 막지 않도록 연결한다.
- `apps/web/components/dashboard/MarketSupplyPanel.tsx` -- `useSearchParams` 기반 KOSPI/KOSDAQ 탭과 접근 가능한 tablist, 네 지표의 숫자·방향 막대·상태 문구를 렌더링하는 client boundary.
- `apps/web/lib/market-supply.ts` -- 시장 행 런타임 가드, 시장별 view model, 유한 숫자·부호·막대 폭/방향 표시 포맷을 순수 함수로 둔다. 금융 힌트 계산은 포함하지 않는다.
- `apps/web/lib/dashboard-types.ts` -- `MarketSupplyRpcRow`와 market enum 등 서버 RPC 반환 타입을 추가한다. 기존 snapshot 타입은 보존한다.
- `apps/web/app/globals.css` -- dark console 토큰을 사용한 패널·탭·숫자·방향 막대·반응형 스타일과 200% 확대 줄바꿈 경계를 둔다.
- `infra/supabase/migrations/202609081300_create_get_market_supply.sql`, `infra/supabase/migrations/202609081301_harden_market_supply_read_acl.sql` -- RLS가 활성화된 `market_supply`를 직접 노출하지 않고 published complete attempt에 한정해 읽는 security-definer RPC와 원본 테이블 SELECT 차단을 추가한다.
- `packages/read-model/src/database.types.ts` -- 새 read RPC 함수 시그니처를 generated read-model 계약에 반영한다.
- `apps/web/lib/market-supply.test.ts`, `apps/web/lib/dashboard-types.test.ts`, `tests/sql/test_get_market_supply.sql` -- 시장 정규화, 부호/0, malformed row, 시장 선택 경계와 운영 attempt/권한 격리를 검증한다.
- `e2e/home.spec.ts` -- 인증 fixture가 있으면 탭/URL 보존의 outer-surface smoke를 추가하고, 없으면 기존 미인증 redirect 범위를 유지한다.

## Tasks & Acceptance

**Execution:**
- `infra/supabase/migrations/202609081300_create_get_market_supply.sql`, `infra/supabase/migrations/202609081301_harden_market_supply_read_acl.sql` -- published complete snapshot의 `p_run_id`에 속한 KOSPI/KOSDAQ 당일 행만 반환하는 read RPC와 원본 SELECT 차단을 추가한다 -- 브라우저가 RLS 우회 없이 시장 데이터를 읽게 한다.
- `apps/web/lib/dashboard-types.ts`, `packages/read-model/src/database.types.ts` -- RPC 반환 타입과 함수 계약을 추가한다 -- 서버/클라이언트 데이터 경계를 고정한다.
- `apps/web/lib/market-supply.ts`, `apps/web/lib/market-supply.test.ts` -- 행 검증·시장별 선택·부호/0·막대 view model과 오류 경계를 구현·테스트한다 -- UI가 금융 판단을 계산하지 않게 한다.
- `apps/web/components/dashboard/MarketSupplyPanel.tsx`, `apps/web/app/page.tsx` -- 패널을 홈에 연결하고 URL 탭 상태·오류/빈 상태·장중 라벨을 구현한다 -- AC의 실제 홈 표면을 완성한다.
- `apps/web/app/globals.css` -- 패널의 탭, 숫자, 방향 막대, 반응형/확대 안전 스타일을 추가한다 -- 기존 후보 카드와 dark console UX를 보존한다.
- `e2e/home.spec.ts` -- 실행 가능한 인증 fixture에서 탭과 새로고침 URL 보존을 검증한다 -- 인증 fixture가 없으면 그 검증 범위를 명시한다.
- `tests/sql/test_get_market_supply.sql`, `.github/workflows/test.yml` -- 두 시장의 부호/0, 미발행 attempt 차단과 table/RPC ACL을 rollback fixture로 검증하고 CI에 등록한다 -- 운영 read 계약의 회귀를 막는다.

**Acceptance Criteria:**
- Given `/`에 complete market snapshot이 있을 때, when Market supply panel을 보면, then KOSPI/KOSDAQ 탭별 외인·기관·개인·프로그램이 숫자와 방향 막대로 표시된다.
- Given 탭을 전환할 때, when URL과 새로고침 결과를 확인하면, then 선택된 시장이 `market` 쿼리로 보존되고 허용된 탭만 활성화된다.
- Given 시장 수급이 후보 수급과 다른 신선도를 가질 때, when 패널 상단을 보면, then 시장 전용 신선도 문구와 `장중 참고` 라벨이 고정 표시된다.
- Given 0 또는 음수 순매수 값이 있을 때, when 지표를 보면, then 숫자 0/음수와 중립/매도 방향이 원본 부호대로 구분되고 매수 권고 표현이 없다.
- Given market RPC가 실패하거나 데이터가 없을 때, when 홈을 렌더링하면, then 명시적 상태가 보이고 기존 후보 카드·실패 알림·태그 동작은 유지된다.

## Spec Change Log

## Review Triage Log

### 2026-09-08 — Review pass
- intent_gap: 0
- bad_spec: 0
- patch: 7 (medium 2, low 5)
- defer: 1 (low 1)
- dismissed:
  - 세 번째 시장 RPC로 인한 순차 요청 지연 — 동적 홈의 기존 RPC 순서와 일관된 읽기 경로이며 지연 위반이 관찰되지 않아 이번 AC 실패로 확인되지 않았다.
  - 컴포넌트 렌더 테스트 부재 — 저장소에 React 컴포넌트 테스트 하네스가 없고 Playwright MCP 수동 outer-surface 확인 및 순수 함수 회귀로 현재 검증 경계를 확인했다.
  - RPC 실패 시 재시도 버튼 부재 — Story 4.8 AC에는 재시도 액션이 없으며 기존 전역 새로고침 동작으로 복구할 수 있어 이번 변경의 결함으로 확정하지 않았다.
  - 배치 종류별 신선도/오래됨 계산 부재 — 의도는 시장 수급에 고정된 `장중에도 갱신될 수 있음`과 `장중 참고` 문구를 요구하며 별도 age 계산을 요구하지 않는다.
  - JSON numeric의 JavaScript 정밀도 우려 — 현재 read-model과 웹 타입이 수치를 number로 계약하고 있으며 실제 운영 fixture에서 문제를 재현하지 못해 추정 위험으로 남겼다.
  - stage 비성공·다른 logical run 추가 fixture 제안 — RPC의 published/current pointer/stage 조건을 직접 확인했고, 추가 케이스 부재만으로 현재 코드의 노출 결과를 입증하지 못했다.
  - 검증 섹션에 production 결과가 없다는 지적 — review 시점까지의 실행 결과를 아래 Auto Run Result에 기록하는 workflow 산출물이며 구현 결함이 아니다.
  - `handleMarketTabArrowNavigation`·3초 timeout을 전제로 한 edge finding — 해당 심볼과 timeout 구현은 현재 diff에 존재하지 않아 주장된 위치/결과를 재현할 수 없었다.
- addressed_findings:
  - `[medium]` `[patch]` ARIA tab의 비활성 탭이 화살표 키로 도달되지 않음 — Arrow/Home/End 이동과 포커스 이동을 추가했다.
  - `[medium]` `[patch]` malformed trading_day/collected_at이 정상 행으로 렌더될 수 있음 — 날짜·datetime 런타임 검증과 회귀 테스트를 추가했다.
  - `[low]` `[patch]` 1 미만의 유효 수치가 0으로 보이고 상대 막대 스케일이 축소됨 — 표시 정밀도와 epsilon 기준을 보완했다.
  - `[low]` `[patch]` 최대값 대비 작은 유효 수치의 막대가 반올림 0으로 사라질 수 있음 — nonzero 값의 최소 1% 표시를 추가했다.
  - `[low]` `[patch]` 양·음 막대가 같은 방향으로 자라 부호 방향이 약함 — 중앙 기준선과 양/음 반대 확장을 적용했다.
  - `[low]` `[patch]` RPC 실패와 데이터 없음 문구가 동일함 — 실패 전용 alert 문구를 분리했다.
  - `[low]` `[patch]` 운영 SQL fixture가 실제 anon RPC와 current attempt 경계를 충분히 증명하지 않음 — anon 호출, 기준일 필터, 이전 published attempt 격리와 전체 값 assertion을 추가했다.

## Design Notes

시장 패널은 서버에서 snapshot의 attempt를 전달받고 client component는 탭 상태만 관리한다. 방향 막대의 최대 폭은 화면용 상대 스케일일 뿐 힌트 임계값이나 투자 판단을 의미하지 않으며, 0은 중립 색상/폭으로 렌더링한다. 시장별 행이 일부만 오면 해당 탭은 오류 상태로 표시하고 다른 탭과 후보 카드 렌더는 보존한다.

## Verification

**Commands:**
- `npm test` -- expected: 웹 순수 함수 전체 통과.
- `npm run typecheck` -- expected: TypeScript 오류 없음.
- `npm run build` -- expected: Next.js production build 통과.
- `npx playwright test e2e/home.spec.ts` -- expected: 인증 가능한 redirect 또는 시장 패널 smoke 통과; fixture가 없으면 미인증 범위와 사유를 기록.
- `git diff --check` -- expected: whitespace 오류 없음.
- Supabase MCP `apply_migration` + `execute_sql` -- expected: 운영 프로젝트 RPC 권한·published attempt 격리·두 시장 반환·오류 경계를 explicit pass row로 확인.

## Auto Run Result

- implementation: published complete attempt 전용 `get_market_supply` read RPC와 원본 테이블 SELECT 차단 migration을 추가하고, 홈 후보 목록 아래에 KOSPI/KOSDAQ URL 탭 시장 수급 패널을 연결했다. 네 지표의 부호·0·상대 중앙 막대·수집 시각과 `장중 참고`/시장 전용 신선도 문구를 표시한다.
- files: `MarketSupplyPanel.tsx`, `market-supply.ts`, `dashboard-types.ts`, `page.tsx`, `globals.css`, read-model 타입, forward-only migrations, SQL fixture/CI, e2e 검증 범위 주석, sprint status를 갱신했다.
- review: patch 7건(중간 2, 낮음 5)을 적용했고, 기존 인증 fixture 부재 1건(낮음)을 defer했다. 나머지 성능·재시도·추가 fixture·정밀도 우려와 존재하지 않는 edge finding은 triage log에서 사유를 기록해 종결했다.
- follow-up review recommendation: true; patched counts medium=2, low=5, score=11 (3×2 + 5)이다.
- verification: `npm test` 98 passed, `npm run typecheck` passed, `npm run build` passed, `npx playwright test e2e/home.spec.ts` 2 passed, `python tools/check_migration_order.py` passed (57 files), `git diff --check` passed. Playwright MCP로 인증된 로컬 홈의 1280px/375px 렌더, KOSDAQ URL 탭, invalid market의 KOSPI 정규화, ArrowLeft 탭 이동, 콘솔 error 0건을 확인했다. 운영 Supabase 프로젝트에 `202609081301_harden_market_supply_read_acl`을 적용했고, RPC 권한/원본 SELECT 차단 및 `tests/sql/test_get_market_supply.sql` fixture가 `story_4_8_market_supply_read: pass`를 반환했다.
- residual: 운영 프로젝트에는 현재 complete snapshot 데이터가 없어 실제 수치가 있는 KOSPI/KOSDAQ 패널을 운영 브라우저에서 확인하지 못했다. CI 인증 fixture 부재로 실제 데이터 패널의 Playwright 자동 검증은 defer했으며, 운영 데이터가 생성되면 패널 값·양 시장 탭을 재확인해야 한다. Node의 기존 `MODULE_TYPELESS_PACKAGE_JSON` 경고는 테스트 통과를 막지 않았다.
