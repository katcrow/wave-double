---
title: 'Story 4.10: 힌트 배지 통합 & 필터'
type: 'feature'
created: '2026-09-09'
status: 'done'
baseline_revision: '94aea07eb5902a73c85494fae4d1907a10dee95e'
baseline_commit: '94aea07eb5902a73c85494fae4d1907a10dee95e'
review_loop_iteration: 0
followup_review_recommended: true
context:
  - 'C:/dev/wave-double/_bmad-output/implementation-artifacts/epic-4-context.md'
warnings: []
deferred:
  - summary: >-
      인증된 홈 화면의 힌트 배지·필터·초기화·키보드 상호작용 브라우저 E2E는 인증 fixture와 브라우저 런타임 부재로 실행하지 못했다.
    evidence: |-
      e2e/home.spec.ts는 미인증 redirect 2건만 통과했다. 인증 세션 fixture가 없고 Playwright MCP browser 목록도 빈 배열이었다.
    location: >-
      e2e/home.spec.ts
    severity: low
  - summary: >-
      CandidateList와 HomePage RPC wiring의 authenticated DOM/integration 자동 검증은 저장소에 React 통합 테스트 하네스가 없어 후속 fixture 준비 시 보강해야 한다.
    evidence: |-
      순수 함수 회귀와 typecheck/build는 통과했지만 실제 카드 배지 렌더 및 get_candidate_supply_hints 호출 인자 assertion은 실행되지 않았다.
    location: >-
      apps/web/components/dashboard/CandidateList.tsx
    severity: low
  - summary: >-
      기존 대시보드의 순차 RPC·무타임아웃·서버 대기 로딩 패턴은 이번 스토리에서 새로 도입한 결함이 아니므로 별도 성능 작업으로 남긴다.
    evidence: |-
      Story 4.10은 기존 서버 데이터 조회 흐름에 힌트 RPC와 client filter를 추가했으며, 기존 후보/evidence/market RPC도 동일한 순차 await 패턴을 사용한다.
    location: >-
      apps/web/app/page.tsx
    severity: low
---

<intent-contract>

## Intent

**Problem:** 현재 후보 카드에는 수급 부분결측 단서만 있고 Story 4.9의 `good/not_met/undetermined` 판정이 배지로 통합되지 않아, 여러 후보를 조건별로 빠르게 비교할 수 없다.

**Approach:** 서버에서 후보 카드·근거·힌트 RPC를 attempt 범위로 읽고, 직렬화 가능한 후보 필터 모델을 Client Component에 전달한다. 카드에는 힌트 3상태를 표시하고 전략·힌트·시그널 상태·원천·수급 결측 포함/제외 필터와 결과 0건 초기화를 제공한다.

## Boundaries & Constraints

**Always:** 힌트 상태는 RPC의 `hint_status`를 그대로 라벨링하며 UI에서 금융 판정이나 임계값을 재계산하지 않는다. 전략은 active/vanished 배열을 보존하고 시그널 상태는 active·vanished·혼합으로 명시한다. 원천은 근거 RPC의 `sources`만 사용한다. 수급 결측 제외는 D0 힌트가 pending/missing이거나 카드의 부분결측인 후보를 제외하며, RPC 실패는 판정 불가로 표시하고 별도 알림을 낸다. 모든 필터 컨트롤은 label/name과 키보드 조작을 제공하고, 0건이면 현재 필터와 전체 초기화 버튼을 보여준다.

**Never:** `supply_3day`/힌트 view 직접 SELECT, 브라우저에서 임계값 계산, 필터 선택 시 서버 데이터 변조, 결측을 `미충족`으로 위장, 전략 태그 링크를 필터 동작으로 변경, 기존 attempt 격리·근거 패널·시장 패널 동작을 깨뜨리지 않는다.

## I/O & Edge-Case Matrix

| Scenario | Input / State | Expected Output / Behavior | Error Handling |
|---|---|---|---|
| HINT_BADGE | RPC에 good/not_met/undetermined 행 | 카드에 `좋은 수급`/`미충족`/`판정 불가` 표시 | 힌트 행 없음도 판정 불가 |
| FILTER_MATCH | 전략·힌트·시그널·원천 조건 조합 | 모든 조건을 만족하는 후보만 표시 | 각 조건은 독립적으로 전체 옵션 제공 |
| EXCLUDE_MISSING | 부분결측 또는 pending/missing D0 후보 | 결측 후보 제외, 포함 선택 시 다시 표시 | 힌트 RPC 실패 시 제외 필터를 강제 적용하지 않음 |
| EMPTY_RESULT | 필터 결과 0건 | 적용 필터 요약과 `전체 초기화` 표시 | 초기화 후 전체 후보 복원 |

</intent-contract>

## Code Map

- `apps/web/app/page.tsx` -- complete snapshot의 `run_id`로 `get_candidate_supply_hints`를 호출하고 RPC 오류/shape를 기존 후보 렌더와 독립적으로 처리한다.
- `apps/web/lib/dashboard-types.ts`, `apps/web/lib/supply-hints.ts` -- Story 4.9 hint row 타입·literal validator를 재사용한다.
- `apps/web/lib/candidate-cards.ts` -- 카드 원시 행을 뷰모델로 바꾸며 전체 전략 배열을 필터용으로 보존한다.
- `apps/web/lib/candidate-filters.ts` -- 후보 메타 조합, active/vanished/mixed 시그널 상태, 결측 판정, AND 필터와 현재 필터 라벨을 순수 함수로 둔다.
- `apps/web/components/dashboard/CandidateList.tsx` -- 직렬화 가능한 후보·근거·힌트 props를 받아 필터 컨트롤, 0건 상태, 카드 목록을 렌더하는 client boundary다.
- `apps/web/components/dashboard/CandidateCard.tsx`, `apps/web/app/globals.css` -- 카드의 3상태 힌트 배지·결측 단서와 접근 가능한 필터/배지 시각 스타일을 구현한다.
- `apps/web/lib/candidate-filters.test.ts`, `apps/web/lib/candidate-cards.test.ts`, `apps/web/lib/supply-hints.test.ts` -- 조합 필터, 결측 경계, RPC 상태 계약을 회귀 검증한다.
- `e2e/home.spec.ts` -- 인증 fixture가 있으면 실제 카드 배지·필터·초기화 outer surface를 검증하고, 없으면 미인증 redirect만 실행한 사실을 기록한다.

## Tasks & Acceptance

**Execution:**
- [x] `apps/web/app/page.tsx`, `apps/web/components/dashboard/CandidateList.tsx` -- 힌트 RPC를 서버에서 읽어 카드 목록에 전달하고 필터 상호작용을 통합한다 -- 실제 홈 표면을 완성한다.
- [x] `apps/web/lib/candidate-cards.ts`, `apps/web/lib/candidate-filters.ts` -- 전체 전략·원천·시그널·결측 메타와 순수 AND 필터를 구현한다 -- UI 계산 드리프트를 막는다.
- [x] `apps/web/components/dashboard/CandidateCard.tsx`, `apps/web/app/globals.css` -- 힌트 3상태 배지, 결측 안내, 필터 레이아웃과 focus 상태를 추가한다 -- UX-DR4/DR14/DR17을 충족한다.
- [x] `apps/web/lib/candidate-filters.test.ts`, `apps/web/lib/candidate-cards.test.ts`, `apps/web/lib/supply-hints.test.ts` -- good/not_met/undetermined, 결측 포함/제외, 다중 조건·0건·초기화를 검증한다 -- 회귀망을 만든다.
- [x] `e2e/home.spec.ts` -- 실행 가능한 인증 fixture에서 카드 배지와 필터 조작을 검증한다 -- fixture가 없으면 미인증 범위를 유지하고 명시한다.

**Acceptance Criteria:**
- Given Story 4.9 RPC 결과가 있을 때, when 후보 카드를 렌더링하면, then 세 hint 상태가 각각 확정 문구로 표시된다.
- Given 전략/힌트/시그널 상태/원천 필터를 선택할 때, when 목록을 확인하면, then 모든 선택 조건을 만족하는 후보만 남고 전략 태그 링크는 기존 라우트로 이동한다.
- Given 부분결측 또는 pending/missing D0 후보일 때, when 수급 결측 제외를 선택하면, then 해당 후보가 제외되고 포함을 선택하면 다시 표시된다.
- Given 결과가 0건일 때, when 화면을 확인하면, then 현재 적용 필터와 한 번의 `전체 초기화` 조작이 표시된다.
- Given 키보드만 사용하는 경우, when 필터를 조작하면, then 모든 옵션·초기화·카드 배지에 접근할 수 있다.

## Spec Change Log

## Review Triage Log

### 2026-09-09 — Review pass
- intent_gap: 0
- bad_spec: 0
- patch: 10 (medium 3, low 7)
- defer: 3 (low 3)
- dismissed:
  - 다른 attempt의 유효한 힌트 행이 렌더될 수 있다는 주장 — Story 4.9 RPC가 published current complete attempt와 candidate trading_day를 SQL에서 제한하고, 이번 patch도 서버에서 run_id/거래일을 재확인해 결과를 검증하지 못했다.
  - 카드 li 자체가 키보드 Enter를 처리하지 않는다는 주장 — 기존 근거 토글 button이 키보드 조작 표면이며 이번 AC는 필터 옵션의 키보드 접근성을 요구하므로 해당 결함은 이번 변경의 필수 표면이 아니다.
  - 각 정적 배지를 live region으로 둘 필요가 있다는 주장 — 실제로는 과도한 반복 읽기 위험이 확인되어 role=status를 제거했다.
  - source 옵션이 evidence 실패 시 설명 없이 사라진다는 주장 — 실패 문구를 `원천 정보를 불러오지 못했습니다`로 추가해 해소했다.
  - stale 전략/원천 필터가 refresh 후 남는다는 주장 — 현재 옵션과 선택값을 effect에서 교집합으로 정리해 해소했다.
  - 인증 브라우저 테스트가 없다는 주장 중 구현 실패라는 부분 — 인증 fixture와 브라우저 런타임 부재로 실행 불가한 검증 공백이며 deferred로 기록했다.
  - loading/skeleton이 없다는 주장 — 기존 홈의 모든 RPC가 서버 렌더 await 패턴을 사용하고 이번 스토리의 새 요구사항은 skeleton 추가가 아니므로 pre-existing 성능 범위로 defer했다.
- addressed_findings:
  - `[medium]` `[patch]` hint row가 없는 후보가 결측 제외 필터를 통과하던 문제를 `supplyMissing`으로 보완하고 카드에도 수급 미수집을 표시했다.
  - `[medium]` `[patch]` malformed 카드 RPC 행이 unchecked cast로 렌더를 중단할 수 있던 문제를 runtime row guard로 보완했다.
  - `[medium]` `[patch]` refresh/0건 상태에서 초기화가 사라지거나 중복되던 문제를 단일 reset surface로 보완했다.
  - `[low]` `[patch]` evidence/hint 중복 행의 배열 순서 의존성을 최신 거래일·수집 시각 선택으로 제거했다.
  - `[low]` `[patch]` 필터 결과 건수 live 안내를 추가했다.
  - `[low]` `[patch]` 정적 badge live-region 과다 읽기와 disclosure 설명 부족을 보완했다.
  - `[low]` `[patch]` evidence RPC 실패 시 원천 필터의 unavailable 이유를 표시했다.
  - `[low]` `[patch]` 힌트 RPC 행의 attempt/trading-day lineage를 서버에서 재확인했다.
  - `[low]` `[patch]` vanished/mixed signal, multi-source OR, no-hint 경계 회귀 테스트를 추가했다.
  - `[low]` `[patch]` malformed row guard 회귀 테스트를 추가했다.

## Design Notes

힌트 RPC가 active 후보마다 missing 행을 반환하므로 카드에 hint row가 없어도 `undetermined`로 안전하게 렌더링한다. 결측 제외는 카드의 기존 `supply_partial_missing`와 RPC의 `investor_net_status`를 함께 사용해 D0 전체 부재도 놓치지 않는다. 서버에서 읽은 `Map`은 Client Component 경계를 넘기지 않고 배열 props로 전달한다.

## Verification

**Commands:**
- `npm test` (in `apps/web`) -- expected: 기존 및 신규 웹 계약 테스트 전건 통과.
- `npm run typecheck` (in `apps/web`) -- expected: Next/TypeScript 오류 없음.
- `npm run build` (in `apps/web`) -- expected: production build 성공.
- `npx playwright test e2e/home.spec.ts` -- expected: 인증 fixture가 없으면 미인증 redirect 2건 통과, 미실행 표면을 기록.
- `git diff --check` -- expected: whitespace 오류 없음.

## Auto Run Result

- implementation: Story 4.9의 `get_candidate_supply_hints` RPC를 complete snapshot run_id로 호출하고, 후보 카드에 `좋은 수급`/`미충족`/`판정 불가 · 장 마감 후 확정` 배지를 통합했다. 전략·힌트·시그널 상태·원천·수급 결측 포함/제외를 조합하는 client filter와 0건 요약/전체 초기화를 추가했다.
- files: `apps/web/app/page.tsx`는 힌트 RPC와 lineage guard를 연결했고, `apps/web/components/dashboard/CandidateList.tsx`는 직렬화 props 기반 필터 UI를 제공하며, `CandidateCard.tsx`/`globals.css`는 배지·결측·접근성 스타일을 제공한다. `candidate-filters.ts`와 테스트는 메타 조합·AND/OR·결측·중복 경계를 고정하고, 카드 RPC row guard와 관련 회귀 테스트를 추가했다. Story spec과 sprint status를 갱신했다.
- review: blind hunter, edge-case hunter, verification-gap, intent-alignment 리뷰를 실행했다. patch 10건(중간 3, 낮음 7)을 모두 보완했고, pre-existing 또는 fixture 부재 3건은 deferred로 기록했으며 각 dismissed finding의 사유를 위에 남겼다.
- follow-up review recommendation: true; patched counts medium=3, low=7, score=16이다.
- verification: `apps/web`에서 `npm test` 113 passed, `npm run typecheck` 통과, `npm run build` 통과, `npx playwright test e2e/home.spec.ts` 2 passed, `git diff --check` 통과. 인증된 카드/필터 outer-surface는 인증 fixture 및 브라우저 런타임 부재로 실행하지 못했다.
- residual: 운영 Supabase RPC 자체 계약은 Story 4.9에서 검증된 것을 재사용하며 이번 스토리에는 DB migration이 없다. 인증된 카드/필터 DOM 및 HomePage RPC integration assertion은 fixture 준비 후 추가 검증이 필요하다. Node test의 기존 `MODULE_TYPELESS_PACKAGE_JSON` 경고는 실패가 아니다.
