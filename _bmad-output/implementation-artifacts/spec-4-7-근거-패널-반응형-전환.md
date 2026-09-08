---
title: 'Story 4.7: 근거 패널 반응형 전환'
type: 'feature'
created: '2026-09-08'
status: 'done'
baseline_revision: '170938563d45c2bc7b5d62dbd492f268ec826c7b'
baseline_commit: '170938563d45c2bc7b5d62dbd492f268ec826c7b'
review_loop_iteration: 0
followup_review_recommended: false
context:
  - 'C:/dev/wave-double/_bmad-output/implementation-artifacts/epic-4-context.md'
warnings: []
deferred: []
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
- `e2e/home.spec.ts` -- 보호 라우트 redirect만 자동화된 현재 e2e 경계. 인증 fixture가 없으면 반응형 후보 panel 브라우저 실행 불가 사유를 기록한다.
- `apps/web/AGENTS.md` -- Next.js 16 변경 가이드 확인 및 웹 작업 규칙. 코드 작성 전 `node_modules/next/dist/docs/`의 관련 문서를 읽는다.

## Tasks & Acceptance

**Execution:**
- [x] `apps/web/components/dashboard/CandidateEvidencePanel.tsx` -- 기존 정규화 슬롯을 desktop table과 mobile date-card 두 표현에 연결하고 label/value·기준일·상태를 명시한다 -- 좁은 화면에서도 표 정보를 잃지 않게 한다.
- [x] `apps/web/app/globals.css` -- >=1200px table, <768px mobile card 전환 및 200% 확대 시 줄바꿈/비절단 스타일을 추가한다 -- UX-DR14/15와 기존 dark console 토큰을 지킨다.
- [x] `apps/web/lib/candidate-evidence.test.ts` -- 모바일 표현에 필요한 슬롯·값·상태 계약의 회귀 사례를 보강한다 -- confirmed 0과 pending/missing의 의미가 양쪽 표현에서 유지됨을 증명한다.
- [x] `e2e/home.spec.ts` -- 실행 가능한 인증 fixture가 있는 경우 1200px/모바일 panel 렌더를 검증하고, 없으면 기존 redirect 범위와 제약을 기록한다 -- 실제 outer surface 검증 범위를 명확히 한다.

**Acceptance Criteria:**
- Given 화면 폭이 1200px 이상일 때, when 근거 패널을 열면, then D0/D-1/D-2가 고정된 3행 semantic table로 표시되고 7개 지표의 열 헤더와 단위가 보인다.
- Given 화면 폭이 768px 미만일 때, when 근거 패널을 열면, then 각 거래일이 독립 카드로 전환되고 지표가 한 줄에 압축되지 않으며 날짜·기준일·label/value가 함께 보인다.
- Given 브라우저 확대가 200%일 때, when 패널 내용을 확인하면, then 날짜·상태·숫자·단위가 패널 밖으로 잘리거나 숨겨지지 않고 필요한 텍스트가 줄바꿈된다.
- Given pending, missing, confirmed 0 데이터가 있을 때, when desktop 또는 mobile 표현을 확인하면, then 각각 "미확정", "미수집", 숫자 "0"으로 구분된다.
- Given 근거 데이터가 비어 있거나 RPC가 실패할 때, when 패널을 열면, then 기존의 빈 상태/로드 실패 메시지가 유지되고 반응형 전환이 해당 상태를 깨뜨리지 않는다.

## Spec Change Log

## Design Notes

표는 accessibility tree와 screen reader의 행/열 관계를 위해 DOM에 유지하고, 모바일 카드만 별도 표현으로 제공한다. 두 표현은 동일한 `viewModel.slots`를 사용해 responsive breakpoint가 데이터 정렬·상태 의미를 분기하지 않도록 한다.

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
  [`CandidateEvidencePanel.tsx:22`](../../apps/web/components/dashboard/CandidateEvidencePanel.tsx#L22)

- 모바일 카드는 D0/D-1/D-2와 기준일, 상태, 명시적 label/value를 그대로 노출한다.
  [`CandidateEvidencePanel.tsx:142`](../../apps/web/components/dashboard/CandidateEvidencePanel.tsx#L142)

**레이아웃·확대 안전성**

- 대형 화면에서 표를 고정 레이아웃으로 바꾸고 카드 폭을 확보해 가로 스크롤을 없앤다.
  [`globals.css:565`](../../apps/web/app/globals.css#L565)

- 768px 미만에서 표 대신 줄바꿈 가능한 날짜별 카드와 상태별 surface를 표시한다.
  [`globals.css:587`](../../apps/web/app/globals.css#L587)

**회귀와 검증 범위**

- 정규화 view model이 7개 지표와 confirmed/pending 상태를 보존하는지 검증한다.
  [`candidate-evidence.test.ts:82`](../../apps/web/lib/candidate-evidence.test.ts#L82)

- 인증 fixture 부재로 responsive panel 브라우저 검증이 제외된 현재 e2e 경계를 확인한다.
  [`home.spec.ts:10`](../../e2e/home.spec.ts#L10)
