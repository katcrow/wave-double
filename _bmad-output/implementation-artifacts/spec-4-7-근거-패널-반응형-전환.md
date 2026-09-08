---
title: 'Story 4.7: 근거 패널 반응형 전환'
type: 'feature'
created: '2026-09-08'
status: 'done'
baseline_revision: '170938563d45c2bc7b5d62dbd492f268ec826c7b'
baseline_commit: '170938563d45c2bc7b5d62dbd492f268ec826c7b'
review_loop_iteration: 0
followup_review_recommended: true
context:
  - 'C:/dev/wave-double/_bmad-output/implementation-artifacts/epic-4-context.md'
warnings: []
deferred:
  - summary: >-
      인증된 후보 fixture가 없어 보호 홈에서 실제 desktop/mobile/200% 브라우저 레이아웃과 접근성 트리를 자동 검증하지 못한다.
    evidence: |-
      e2e/home.spec.ts는 인증 세션을 발급하지 못해 /와 /runs 미인증 redirect만 실행하며, 후보 패널은 운영 Supabase fixture와 인증 세션이 함께 필요하다. 이 제약은 Story 4.6부터 이어졌다.
    location: >-
      e2e/home.spec.ts:10
    severity: medium
---

<intent-contract>

## Intent

**Problem:** 현재 Evidence panel은 7개 지표를 한 줄에 배치한 고정 폭 표만 제공해 좁은 화면에서 가로 스크롤에 의존한다. 모바일과 확대 상태에서도 거래일별 근거를 빠르게 읽을 수 있어야 한다.

**Approach:** 기존의 의미론적 3행 표를 데스크톱 표현으로 유지하고, 768px 미만에서는 같은 정규화 view model을 날짜별 카드로 렌더링한다. 반응형 표현은 CSS breakpoint로 전환하며 숫자 단위·기준일·상태 라벨과 기존 접근성 계약을 보존한다.

## Boundaries & Constraints

**Always:** D0/D-1/D-2 순서와 confirmed 0, pending, missing 표시 의미를 유지한다. 1200px 이상에서는 3행 표를 가로 스크롤 없이 고정된 패널 표면으로 표시하고, 768px 미만에서는 각 날짜가 독립 카드가 되어 지표가 줄바꿈 가능한 label/value 쌍으로 표시되게 한다. 표에는 caption과 행/열 헤더를 유지하며 모바일 카드에도 날짜와 각 값의 명시적 label을 제공한다. 200% 확대에서 텍스트와 값이 컨테이너 밖으로 잘리지 않는다.

**Never:** 수급 힌트·금융 판단을 UI에서 계산하지 않는다. RPC, DB schema, 기존 `get_dashboard_snapshot()`/카드 데이터 계약, 4-6의 상태·provenance·토글 동작을 변경하지 않는다. 모바일에서 모든 열을 한 줄에 우겨넣거나 단순히 고정 표를 숨겨 데이터 접근을 없애지 않는다.

## I/O & Edge-Case Matrix

| Scenario | Input / State | Expected Output / Behavior | Error Handling |
|----------|--------------|---------------------------|----------------|
| DESKTOP | viewport >= 1200px, 3 slots | semantic table with exactly D0/D-1/D-2 rows and units | Existing fetch/empty state remains unchanged |
| MOBILE | viewport < 768px, 3 slots | three date cards; each metric has a visible label and value | No horizontal clipping or forced one-line row |
| ZOOM | 200% browser zoom / narrow CSS viewport | card labels, dates, status, and values remain readable within the panel | Long text wraps; no hidden overflow of content |
| PARTIAL_STATUS | pending/missing slot or confirmed 0 | same status/zero semantics as desktop | Missing/pending remains distinguishable from numeric 0 |

</intent-contract>

## Code Map

- `apps/web/components/dashboard/CandidateEvidencePanel.tsx` -- `normalizeCandidateEvidence()` 결과를 사용하는 현재 3행 semantic table. 데스크톱 table과 모바일 날짜별 카드의 단일 데이터 소스 및 `formatEvidence*` 표시 경계를 재사용한다.
- `apps/web/app/globals.css` -- `.candidate-evidence-table`의 현재 최소 폭/overflow 규칙과 767px breakpoint 위치. desktop/mobile surface 전환, 카드 grid, 줄바꿈·overflow 안전 규칙을 여기에 둔다.
- `apps/web/lib/candidate-evidence.ts` -- D0/D-1/D-2 정렬, confirmed/pending/missing 상태, 숫자·날짜 포맷의 순수 함수. Story 4-7에서 수정하지 않고 UI가 이를 재사용한다.
- `apps/web/lib/candidate-evidence.test.ts` -- 상태·슬롯 순서·0 표시 회귀 테스트. 반응형 DOM의 의미 보존은 컴포넌트 구조와 가능한 브라우저 검증으로 확인한다.
- `apps/web/lib/candidate-evidence-view.ts` -- table/card가 공유하는 7개 지표 정의, 표시 포맷, 상태 라벨, 안전한 기준일 변환을 순수 함수로 제공한다.
- `e2e/home.spec.ts` -- 보호 라우트 redirect만 자동화된 현재 e2e 경계. 인증 fixture가 없으면 반응형 후보 panel 브라우저 실행 불가 사유를 기록한다.
- `apps/web/AGENTS.md` -- Next.js 16 변경 가이드 확인 및 웹 작업 규칙. 코드 작성 전 `node_modules/next/dist/docs/`의 관련 문서를 읽는다.

## Tasks & Acceptance

**Execution:**
- [x] `apps/web/components/dashboard/CandidateEvidencePanel.tsx` -- 기존 정규화 슬롯을 desktop table과 mobile date-card 두 표현에 연결하고 label/value·기준일·상태를 명시한다 -- 좁은 화면에서도 표 정보를 잃지 않게 한다.
- [x] `apps/web/app/globals.css` -- >=1200px table, <768px mobile card 전환 및 200% 확대 시 줄바꿈/비절단 스타일을 추가한다 -- UX-DR14/15와 기존 dark console 토큰을 지킨다.
- [x] `apps/web/lib/candidate-evidence.test.ts` -- 모바일 표현에 필요한 슬롯·값·상태 계약의 회귀 사례를 보강한다 -- confirmed 0과 pending/missing의 의미가 양쪽 표현에서 유지됨을 증명한다.
- [x] `apps/web/lib/candidate-evidence-view.ts` -- table/card 공통 지표·상태 표시 경계를 분리한다 -- 두 responsive surface의 매핑 drift를 막는다.
- [x] `e2e/home.spec.ts` -- 실행 가능한 인증 fixture가 있는 경우 1200px/모바일 panel 렌더를 검증하고, 없으면 기존 redirect 범위와 제약을 기록한다 -- 실제 outer surface 검증 범위를 명확히 한다.

**Acceptance Criteria:**
- Given 화면 폭이 1200px 이상일 때, when 근거 패널을 열면, then D0/D-1/D-2가 고정된 3행 semantic table로 표시되고 7개 지표의 열 헤더와 단위가 보인다.
- Given 화면 폭이 768px 미만일 때, when 근거 패널을 열면, then 각 거래일이 독립 카드로 전환되고 지표가 한 줄에 압축되지 않으며 날짜·기준일·label/value가 함께 보인다.
- Given 브라우저 확대가 200%일 때, when 패널 내용을 확인하면, then 날짜·상태·숫자·단위가 패널 밖으로 잘리거나 숨겨지지 않고 필요한 텍스트가 줄바꿈된다.
- Given pending, missing, confirmed 0 데이터가 있을 때, when desktop 또는 mobile 표현을 확인하면, then 각각 "미확정", "미수집", 숫자 "0"으로 구분된다.
- Given 근거 데이터가 비어 있거나 RPC가 실패할 때, when 패널을 열면, then 기존의 빈 상태/로드 실패 메시지가 유지되고 반응형 전환이 해당 상태를 깨뜨리지 않는다.

## Spec Change Log

## Review Triage Log

### 2026-09-08 — Review pass
- intent_gap: 0
- bad_spec: 0
- patch: 5 (medium 3, low 2)
- defer: 1 (medium 1)
- dismissed:
  - 768–1199px 동작이 명세되지 않았다는 주장 — Story AC는 >=1200px과 <768px 두 표면만 명시하며, 해당 범위의 wrap 보강은 명세를 위반하지 않는 방어적 구현이다.
  - 완료 전 스펙의 Verification에 관찰 결과가 없다는 주장 — review 전 계획 스펙의 정상적인 상태이며 Finalize 단계에서 실제 결과를 기록한다.
  - 커밋 완료가 diff 자체로 증명되지 않는다는 주장 — Git 커밋은 diff 내용이 아니라 version-control 상태로 검증하는 워크플로우 산출물이다.
  - 전체 React DOM 렌더 테스트가 없다는 주장 중 인증 fixture가 반드시 필요하다는 부분 — 해당 보호 홈 fixture 부재는 이번 변경으로 생긴 결함이 아니라 기존 4-6부터 이어진 환경 제약이다.
- addressed_findings:
  - `[medium]` `[patch]` 200% 확대의 중간 CSS viewport에서 기존 720px 표가 가로 스크롤에 의존할 수 있음 — 768–1199px에서도 표를 컨테이너 폭에 맞추고 셀 줄바꿈을 허용했다.
  - `[medium]` `[patch]` Evidence panel 범위를 넘어 후보 카드 그리드 폭을 바꾸는 규칙 — 와이드 breakpoint의 전역 grid 변경을 제거하고 모바일 최소 track만 안전하게 제한했다.
  - `[medium]` `[patch]` 모바일 날짜 카드 article에 개별 accessible name이 없음 — slot/기준일을 가진 sr-only heading과 aria-labelledby를 추가했다.
  - `[low]` `[patch]` 빈 trading_day가 빈 기준일과 빈 datetime을 만들 수 있음 — 공통 안전 기준일 변환으로 "거래일 없음"을 렌더링한다.
  - `[low]` `[patch]` 모바일 숫자 값이 anywhere 줄바꿈으로 불필요하게 분리될 수 있음 — 숫자 값에 break-word와 normal word-break를 적용하고 tabular numerics를 사용했다.

## Design Notes

데스크톱 표는 accessibility tree와 screen reader의 행/열 관계를 위해 semantic DOM을 유지하고, 모바일은 동일한 `viewModel.slots`에서 명시적 heading과 `dl` label/value를 가진 날짜 카드로 전환한다. responsive breakpoint가 데이터 정렬·상태 의미를 분기하지 않도록 공통 지표·포맷 함수를 사용한다.

## Verification

**Commands:**
- `npm test` -- expected: web 순수 함수 전체 통과.
- `npm run typecheck` -- expected: TypeScript 오류 없음.
- `npm run build` -- expected: Next.js production build 통과.
- `npx playwright test e2e/home.spec.ts` -- expected: 인증 가능한 redirect 범위 통과; 후보 fixture가 없으면 해당 범위와 미실행 사유 기록.
- `git diff --check` -- expected: whitespace 오류 없음.

**Manual checks (if no CLI):**
- 인증된 홈에서 1280px와 375px로 후보 panel을 열어 desktop table/mobile cards, 200% 확대 줄바꿈, table headers와 값 단위를 확인한다.

## Suggested Review Order

**반응형 표현과 데이터 단일 소스**

- 7개 지표 정의와 동일 슬롯 매핑이 table/card 표현을 함께 구동한다.
  [`candidate-evidence-view.ts:9`](../../apps/web/lib/candidate-evidence-view.ts#L9)

- 모바일 카드는 D0/D-1/D-2와 기준일, 상태, 명시적 label/value를 그대로 노출한다.
  [`CandidateEvidencePanel.tsx:118`](../../apps/web/components/dashboard/CandidateEvidencePanel.tsx#L118)

**레이아웃·확대 안전성**

- 대형 화면에서 펼친 카드를 grid 전체 행으로 확장하고 표를 고정 레이아웃으로 바꿔 가로 스크롤을 없앤다.
  [`globals.css:565`](../../apps/web/app/globals.css#L565)

- 768px 미만에서 표 대신 줄바꿈 가능한 날짜별 카드와 상태별 surface를 표시한다.
  [`globals.css:587`](../../apps/web/app/globals.css#L587)

**회귀와 검증 범위**

- 정규화 view model과 공통 표시 함수가 7개 지표와 confirmed/pending 상태를 보존하는지 검증한다.
  [`candidate-evidence.test.ts:82`](../../apps/web/lib/candidate-evidence.test.ts#L82)

- 인증 fixture 부재로 responsive panel 브라우저 검증이 제외된 현재 e2e 경계를 확인한다.
  [`home.spec.ts:10`](../../e2e/home.spec.ts#L10)

## Auto Run Result

- implementation: Evidence panel에 기존 슬롯 view model을 공유하는 desktop semantic table과 768px 미만 날짜별 카드 표현을 추가했다. 1200px 이상에서는 펼친 후보 카드가 grid 전체 폭을 사용하고, 중간 폭에서도 표 셀 줄바꿈이 가능하다.
- files: `CandidateEvidencePanel.tsx`는 table/card와 접근성 heading을 렌더링하고, `candidate-evidence-view.ts`는 7개 지표·상태·기준일 표시를 공통화하며, `globals.css`는 breakpoint·확대 안전 레이아웃을 제공한다. 테스트와 e2e 주석 및 sprint status/spec도 갱신했다.
- review: patch 5건(중간 3, 낮음 2)을 적용했다. defer 1건(중간 1)은 인증 후보 fixture 부재로 보호 홈의 실제 viewport/접근성 브라우저 검증을 수행할 수 없는 기존 제약이다. dismissed 4건은 명세에 없는 768–1199px 동작 주장, review 전 Verification 미기록 주장, 커밋이 diff에 나타나야 한다는 주장, 인증 fixture가 반드시 필요하다는 테스트 주장 중 환경 제약 부분이며 각각 triage log에 사유를 기록했다.
- follow-up review recommendation: patch counts medium=3, low=2; score=11 (3×3+2)로 `true`다.
- verification: `npm test` 최종 92 passed, `npm run typecheck` passed, `npm run build` passed, `npx playwright test e2e/home.spec.ts` 2 passed, `git diff --check` passed. Playwright MCP로 `/`, `/runs`, `/tracking`을 확인했고 console error 0건이었다. 보호 홈에는 인증 후보 fixture가 없어 실제 Evidence panel viewport/200% 검증은 deferred로 남겼다.
- residual: Supabase/RPC/schema 변경은 없어 운영 DB 검증은 실행하지 않았다. Node의 기존 `MODULE_TYPELESS_PACKAGE_JSON` 경고는 테스트 통과를 막지 않는 저장소 기존 경고다.
