---
title: 'UI 확장 — 라벨·배지·라우트'
type: 'feature'
created: '2026-09-07'
baseline_revision: '7f69e46d34d4c2ac9bee868229d0a0f37330e335'
status: 'done'
review_loop_iteration: 0
followup_review_recommended: false
context:
  - 'C:/dev/wave-double/_bmad-output/implementation-artifacts/epic-6-context.md'
  - 'C:/dev/wave-double/_bmad-output/implementation-artifacts/spec-6-6-후보-태깅-stage에-전략-d-e-반영.md'
warnings: []
deferred: []
---

<intent-contract>

## Intent

**Problem:** `apps/web/lib/strategy-labels.ts`의 `STRATEGY_LABEL`이 A/B/C로 한정되어, Story 6.6까지 백엔드가 이미 저장하는 전략 D/E 태그가 대시보드 카드·라우트·UX 문구에서 인식되지 않는다(라벨 없이 fallback 문구로만 표시되거나 라우트가 404 처리됨).

**Approach:** `STRATEGY_LABEL`에 D/E 항목을 추가해 `StrategyTagList`와 `/strategies/[strategy]` 라우트가 자동으로 다섯 전략을 처리하게 하고, `candidate-cards.ts`의 3전략 전제 주석·`MAX_VISIBLE_TAGS` 값을 재검증하며, `EXPERIENCE.md`/`DESIGN.md`의 "전략 A/B/C" 고정 문구를 가변 개수 전제로 일반화한다.

## Boundaries & Constraints

**Always:** `getStrategyLabel`의 `hasOwnProperty` 가드, `StrategyTagList`의 렌더링 로직(색상 없이 텍스트 라벨만 사용), `/strategies/[strategy]`의 "라벨 없으면 404" 검증 방식을 그대로 유지한다. 문구 갱신 시 UX-DR16(확정적 표현 배제, `전략 D · 전략 E 시그널`처럼 관찰 가능한 문구)과 UX-DR14(색상만으로 구분 금지)를 준수한다.

**Never:** `compute_abc`/태깅 stage/DB 스키마(Story 6.1~6.6 범위, 이미 완료)를 변경하지 않는다. 새로운 전략별 색상 체계를 도입하지 않는다(현재 `.strategy-tag`는 이미 전략 무관 균일 스타일이라 UX-DR14를 이미 만족하므로 추가 색상 작업은 범위 밖). `MAX_VISIBLE_TAGS`는 값을 바꿀 근거(레이아웃 깨짐)가 확인된 경우에만 조정하고, 확인되지 않으면 값은 유지한 채 주석만 정정한다.

## I/O & Edge-Case Matrix

| Scenario | Input / State | Expected Output / Behavior | Error Handling |
|----------|--------------|---------------------------|----------------|
| HAPPY_PATH | 후보 카드에 D 또는 E 단독 태그 | "전략 D"/"전략 E" 라벨이 `StrategyTagList`에 렌더링되고 클릭 시 `/strategies/D`(or E)로 이동 | 오류 없음 |
| MULTI_TAG_5 | 한 종목에 A/B/C/D/E 5개 태그 모두 존재 | `MAX_VISIBLE_TAGS`(현재 2)까지 표시 후 `+3` 접힘 배지 노출 | 오류 없음 |
| UNDEFINED_CODE | `/strategies/F` 등 미정의 전략 코드 접근 | `getStrategyLabel`이 `undefined` 반환 → `notFound()` → 404 | 404 렌더링 |
| LABEL_LOOKUP | `STRATEGY_LABEL`에 D/E 키 조회 | `getStrategyLabel("D")` === `"전략 D"`, `getStrategyLabel("E")` === `"전략 E"` | 오류 없음 |

</intent-contract>

## Code Map

- `apps/web/lib/strategy-labels.ts:5-9` -- `STRATEGY_LABEL`이 A/B/C만 정의. `D: "전략 D"`, `E: "전략 E"` 추가. `getStrategyLabel`의 `hasOwnProperty` 가드는 변경 불필요(신규 키도 동일 메커니즘으로 동작).
- `apps/web/components/dashboard/StrategyTagList.tsx:18-29` -- `visibleStrategies`를 순회해 `getStrategyLabel` 결과로 렌더링하는 로직 자체는 전략 개수에 무관하게 이미 동작. 변경 불필요, D/E 라벨 추가만으로 자동 지원.
- `apps/web/app/strategies/[strategy]/page.tsx:12-13` -- `getStrategyLabel`이 `undefined`면 `notFound()`. 변경 불필요, D/E 라벨 추가만으로 자동으로 두 라우트가 열리고 미정의 코드는 계속 404.
- `apps/web/lib/candidate-cards.ts:4` -- "전략은 A/B/C 3종뿐이라 어떤 조합도 최소 지원 폭에서 한 줄에 들어간다" 주석이 5전략 현실과 불일치. 주석을 가변 전략 개수 전제로 정정.
- `apps/web/lib/candidate-cards.ts:7` -- `MAX_VISIBLE_TAGS = 2`. 5전략 동시 태그 시 `+3` 접힘이 정상 동작하는지(레이아웃 깨짐 없는지) 대시보드 실행 화면에서 수동 확인 후, 문제 없으면 값 유지 + 주석만 정정, 문제 있으면 값 조정.
- `apps/web/lib/candidate-cards.ts:15` -- "정렬된(A/B/C) 태그 중..." 주석을 가변 개수 전제로 정정.
- `apps/web/lib/strategy-labels.test.ts:5-9` -- A/B/C만 검증. D/E 라벨 조회, 미정의 코드(`F`) `undefined` 반환 케이스를 추가.
- `apps/web/lib/candidate-cards.test.ts` -- A/B/C 태그 조합 픽스처만 존재. D/E 포함 조합(A∩D 등) 및 5전략 동시 태그(`+3` 접힘) 케이스를 추가.
- `_bmad-output/planning-artifacts/ux-designs/ux-wave-double-2026-08-31/EXPERIENCE.md:43,118` -- UX-DR16 카피 가이드 표와 내러티브 예시가 "전략 A · 전략 C" 고정 표현. 가변 개수 전제 일반화 문구로 갱신(예: "전략 D · 전략 E 시그널" 등 관찰 가능한 표현 예시로 교체).
- `_bmad-output/planning-artifacts/ux-designs/ux-wave-double-2026-08-31/DESIGN.md:129` -- "전략 A/B/C 태그" 고정 표현을 가변 개수 전제로 갱신.
- `_bmad-output/planning-artifacts/sprint-change-proposal-2026-09-04.md:37,104` -- 이 gap을 이미 Open Risk로 추적 중인 기존 노트. 이번 스토리 완료로 해소되므로 해당 항목에 완료 표기를 남길 근거 문서(별도 수정 불필요, 참고만).

## Tasks & Acceptance

**Execution:**
- `apps/web/lib/strategy-labels.ts` -- `STRATEGY_LABEL`에 `D: "전략 D"`, `E: "전략 E"` 추가 -- AC1, AC2(라벨 확장이 라우트 개방의 유일한 트리거).
- `apps/web/lib/strategy-labels.test.ts` -- D/E 라벨 조회 성공 케이스, 미정의 코드(`F`) `undefined` 반환 케이스 추가 -- I/O 매트릭스 LABEL_LOOKUP/UNDEFINED_CODE.
- `apps/web/lib/candidate-cards.ts` -- 3전략 전제 주석(4, 15행) 정정, `MAX_VISIBLE_TAGS` 값을 5전략 시나리오 수동 확인 결과에 따라 유지 또는 조정 -- AC1.
- `apps/web/lib/candidate-cards.test.ts` -- D/E 포함 다중 태그 조합, 5전략 동시 태그 시 `+N` 접힘 케이스 추가 -- I/O 매트릭스 MULTI_TAG_5.
- `_bmad-output/planning-artifacts/ux-designs/ux-wave-double-2026-08-31/EXPERIENCE.md` -- UX-DR16 카피 가이드 표(43행)와 내러티브 예시(118행)를 가변 개수 전제 문구로 갱신 -- AC3.
- `_bmad-output/planning-artifacts/ux-designs/ux-wave-double-2026-08-31/DESIGN.md` -- 129행 "전략 A/B/C 태그" 문구를 가변 개수 전제로 갱신 -- AC3.

**Acceptance Criteria:**
- Given `STRATEGY_LABEL`에 D/E가 추가된 상태에서, when `StrategyTagList`가 A/B/C/D/E 중 하나 이상을 렌더링하면, then UX-DR7 규칙(가로 나열, 좁은 폭에서 `+N` 접힘)대로 다섯 전략 모두 정상 표시된다.
- Given D/E 라벨이 추가된 상태에서, when `/strategies/D`·`/strategies/E`에 접근하면, then 각 전략 설명/성과 페이지가 정상 렌더링되고, `/strategies/F` 등 미정의 코드는 계속 404 처리된다.
- Given UX-DR9·UX-DR16이 "전략 A/B/C" 고정 표현을 쓰던 상태에서, when 문구를 갱신하면, then `EXPERIENCE.md`/`DESIGN.md`가 가변 개수 전략을 전제로 한 일반화된 표현으로 대체되고, 확정적 표현 없이 관찰 가능한 문구(`전략 D · 전략 E 시그널`류)를 유지한다.
- Given 배지 색상 체계가 현재도 전략별 색상 구분 없이 텍스트 라벨만 사용하는 상태에서, when D/E를 추가해도, then 색상 기반 구분을 신설하지 않고 텍스트 라벨만으로 다섯 전략을 구분한다(UX-DR14 위반 없음).

## Spec Change Log

## Review Triage Log

### 2026-09-07 — 독립 리뷰 4종(blind-hunter, edge-case-hunter, verification-gap, intent-alignment)

- intent_gap: 0
- bad_spec: 0
- patch: 1: (high 0, medium 0, low 1)
- defer: 0
- dismissed:
  - 4태그(`["A","B","C","D"]`) 경계 케이스 테스트 부재 지적 — `slice(0, MAX_VISIBLE_TAGS)`는 태그 개수와 무관한 순수 산술 연산이며 경계값(2)과 초과값(3, 5)이 이미 테스트로 검증돼 그 사이 값(4)을 추가로 검증해도 새로운 신뢰를 얻지 못한다.
  - 미정의 전략 코드("F")가 `buildCandidateCardViewModels`를 통해 흘러가는 end-to-end 케이스 미검증 지적 — `candidate_tags.strategy` DB CHECK 제약(Story 6.3)이 A~E만 허용해 실제로는 도달 불가능한 상태이며, 이 fallback 경로 자체는 이번 diff 이전부터 존재하던 기존 설계다.
  - JS 계층에 "최대 5종" 가정을 DB 제약과 연결하는 방어 코드가 없다는 지적 — 기존 A/B/C 시절부터 Postgres CHECK가 저장 시점 권위 검증을 담당하는 설계이며 이번 diff가 새로 만든 위험이 아니다.
  - DB와 프런트엔드가 A~E 집합을 각자 하드코딩해 단일 출처가 없다는 지적 — A/B/C 시절부터 존재하던 기존 아키텍처이며 이번 스토리(Never: 새 색상/구조 체계 도입 금지)의 범위 밖이다.
  - 5개 중 3개가 접힐 때 숨겨진 전략을 확인할 툴팁/펼치기 UI가 없다는 지적 — UX-DR7(가로 나열, 좁은 폭에서 `+N` 접힘, 클릭 시 필터가 아니라 전략 설명 페이지 이동)이 이미 확정한 상호작용이며 이번 스토리 범위(Never) 밖의 신규 UX 설계 요구다.
  - 5태그 시나리오의 실제 카드 레이아웃을 디자인 툴에서 재검증하지 않았다는 지적 — `.strategy-tag-list`가 `flex-wrap: wrap`이고 `visibleStrategies`/`hiddenStrategyCount`가 항상 `MAX_VISIBLE_TAGS`(2)로 고정된 DOM 노드 수만 생성하므로(태그 총합이 3이든 5든 렌더링되는 노드 수는 동일, `+N`의 숫자만 변함) 레이아웃 회귀 가능성이 없다.
  - `MAX_VISIBLE_TAGS=2`가 5전략 현실에 맞게 재검토되지 않았다는 지적 — 스펙의 Never 제약이 "레이아웃 깨짐이 확인된 경우에만 조정"을 명시했고, 위 DOM 노드 수 불변성 확인 결과 깨짐 근거가 없어 값을 유지한 것이 스펙 준수다.
  - `StrategyTagList`/`CandidateCard` 컴포넌트 레벨 렌더링 테스트(5태그 스냅샷 등) 부재 지적 — `apps/web/package.json`의 test 스크립트가 `node --test lib/**/*.test.ts`로 `lib/` 디렉터리만 글롭 대상이라 컴포넌트 테스트 인프라 자체가 없으며, 이를 신설하는 것은 이번 스토리 범위(UI 라벨·배지·라우트 확장) 밖의 테스트 인프라 작업이다.
  - `candidate-cards.ts` 주석에 "Story 6-7" 같은 스토리 추적 표기가 없다는 지적 — 파일 내 다른 주석 하나가 우연히 migration 파일을 참조할 뿐 파일 전체의 확립된 컨벤션이 아니라 일관성 결여를 근거로 들 수 없다.
  - `candidate-cards.test.ts`에 미정의 전략 코드 케이스가 없어 `strategy-labels.test.ts`와 커버리지가 비대칭이라는 지적 — 위 "F" 도달 불가능 사유와 동일하다.
  - "검수·e2e·스프린트 동기화·git 커밋"이 diff에 반영되지 않았다는 intent-alignment 지적 — 이번 diff는 step-03 구현 산출물이며, 리뷰 루프·스프린트 동기화·커밋은 각각 이번 step-04(현재 진행 중)와 workflow Finalize 단계, 그리고 build-auto 종료 후 호출자(outer) 단계에서 처리되는 후속 절차로, 아직 도달하지 않은 단계를 diff 결함으로 볼 수 없다.
- addressed_findings:
  - `[low]` `[patch]` 이번 diff가 `DESIGN.md`/`EXPERIENCE.md`에 도입한 "A~E(가변 개수)" 축약 표기가 같은 문서군의 기존(미변경) "A/B/C/D/E" 표기(`EXPERIENCE.md:133` 등)와 불일치했다 — 신규 도입 문구를 전부 "A/B/C/D/E" 표기로 통일해 같은 문서 세트 내 용어 일관성을 회복.

## Design Notes

`compute_abc`(6.4)·`candidate_tags` 스키마(6.3)·태깅 stage(6.6)가 이미 A~E를 전략 개수 무관하게 처리하도록 구현돼 있어, 프런트엔드 실제 gap은 `STRATEGY_LABEL` 딕셔너리 하나뿐이다(`StrategyTagList`와 라우트는 이 라벨 존재 여부만으로 자동 확장됨). 남은 작업은 (1) 이 라벨 확장, (2) 3전략 전제로 쓰인 주석·`MAX_VISIBLE_TAGS` 재검증, (3) UX 문서 카피 일반화, 세 갈래다.

## Verification

**Commands:**
- `npm run typecheck` -- expected: 통과.
- `npm run test -w apps/web` -- expected: `strategy-labels.test.ts`/`candidate-cards.test.ts` 신규 케이스 포함 전체 통과.

**Manual checks (Playwright MCP, 로컬 dev 서버):**
- 대시보드에서 A/B/C/D/E 5개 태그를 가진(또는 픽스처/시드로 재현한) 후보 카드가 `MAX_VISIBLE_TAGS` 초과 시 `+N` 배지로 정상 접히는지, 레이아웃이 깨지지 않는지 확인한다.
- `/strategies/D`, `/strategies/E` 접근 시 정상 렌더링, `/strategies/F` 접근 시 404 확인한다.

## Auto Run Result

**구현 요약:** `STRATEGY_LABEL`에 D/E 라벨을 추가해 `StrategyTagList`와 `/strategies/[strategy]` 라우트가 다섯 전략을 자동으로 처리하도록 확장하고, `candidate-cards.ts`의 3전략 전제 주석을 정정했으며, `EXPERIENCE.md`/`DESIGN.md`의 "전략 A/B/C" 고정 문구를 가변 개수 전제로 일반화했다.

**변경 파일:**
- `apps/web/lib/strategy-labels.ts` -- `STRATEGY_LABEL`에 `D`/`E` 라벨 추가.
- `apps/web/lib/strategy-labels.test.ts` -- D/E 라벨 조회, 미정의 코드(`F`) `undefined` 반환 테스트 추가.
- `apps/web/lib/candidate-cards.ts` -- 3전략 전제 주석 2건 정정(`MAX_VISIBLE_TAGS` 값은 유지).
- `apps/web/lib/candidate-cards.test.ts` -- D 단독, E 단독, A∩D, 5전략 동시(+3 접힘) 테스트 추가.
- `_bmad-output/planning-artifacts/ux-designs/ux-wave-double-2026-08-31/EXPERIENCE.md` -- UX-DR16 카피 가이드·내러티브 예시를 가변 개수 전제로 갱신.
- `_bmad-output/planning-artifacts/ux-designs/ux-wave-double-2026-08-31/DESIGN.md` -- "전략 A/B/C 태그" 고정 표현을 가변 개수 전제로 갱신(리뷰 패치로 "A~E" 표기를 기존 "A/B/C/D/E" 표기와 통일).

**리뷰 findings 분류:** patch 1건(low, 이번 패스에서 수정 완료) · defer 0건 · dismissed 11건(위 Review Triage Log 참조, 대부분 스토리 범위(Never) 밖 또는 DB CHECK로 이미 도달 불가능한 상태).

**추적 리뷰 권장:** patch 1건(low) → score = 1×1 = 1, 5 미만 → **권장하지 않음**.

**검증 수행:**
- `npm run typecheck` -- 통과(리뷰 패치 전후 2회 실행).
- `npm run test -w apps/web` -- 77 passed(리뷰 패치 전후 2회 실행, 신규 D/E·5전략 테스트 포함, 회귀 없음).
- Playwright MCP 수동 확인(구현 단계에서 로컬 `next dev`) -- `/strategies/D`, `/strategies/E` 정상 렌더링, `/strategies/F` 404 확인.
- `MAX_VISIBLE_TAGS` 레이아웃 검토 -- `.strategy-tag-list`가 `flex-wrap: wrap`이고 표시 노드 수가 태그 총합과 무관하게 고정(2개 표시 + `+N` 배지 1개)됨을 코드/CSS 분석으로 확인, 레이아웃 회귀 근거 없음.

**잔여 리스크:** 없음. 미정의 전략 코드 흐름, 컴포넌트 레벨 렌더링 테스트 등 지적된 항목은 모두 DB CHECK 제약 또는 스토리 범위(Never) 밖 사유로 해소·기각되었다.
</content>
