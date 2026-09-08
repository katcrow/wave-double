---
title: 'UI 확장 — 라벨·배지·라우트 (F)'
type: 'feature'
created: '2026-09-08'
baseline_revision: 'd3b5b663606b6894b1a5c2dd404e1de3b0ed5967'
status: 'done'
review_loop_iteration: 0
followup_review_recommended: false
context:
  - 'C:/dev/wave-double/_bmad-output/implementation-artifacts/epic-7-context.md'
warnings: []
deferred:
  - summary: >-
      apps/web/lib/candidate-cards.ts:4의 Design Notes 주석("현재 최대 5종")이 전략 F 추가로
      실제 최대 6종이 됐는데도 갱신되지 않아 stale하다.
    evidence: |-
      MAX_VISIBLE_TAGS=2이고 slice/hidden-count 절단 로직 자체는 태그 개수와 무관하게 동작해
      기능 결함은 아니지만, 주석의 "(현재 최대 5종)"이라는 구체적 수치가 이제 부정확하다.
      Story 7.5(태깅 stage에 F 반영)가 완료된 시점부터 이미 부정확해졌던 기존 문제이며,
      candidate-cards.ts는 spec-7-6의 Never 목록(변경 금지 대상)이라 이번 스토리 범위 밖이다.
    location: >-
      apps/web/lib/candidate-cards.ts:4
    severity: low
---

<intent-contract>

## Intent

**Problem:** `apps/web/lib/strategy-labels.ts`의 `STRATEGY_LABEL`이 A/B/C/D/E로 한정돼 있어, Story 7.1~7.5로 이미 계산·태깅되는 전략 F가 대시보드 배지(`StrategyTagList`)와 `/strategies/[strategy]` 페이지에서 라벨 없이(`전략 F` 폴백 텍스트로만) 노출되고, F 전용 설명 페이지가 없다(`getStrategyLabel("F")`가 `undefined`를 반환해 `notFound()` 처리됨).

**Approach:** `STRATEGY_LABEL`에 `F: "전략 F"`를 추가한다. `StrategyTagList.tsx`·`/strategies/[strategy]/page.tsx`·배지 CSS(`globals.css`)는 이미 전략 키 개수와 무관하게 `getStrategyLabel`을 통해 동작하도록 일반화돼 있어(Epic 6/7 선행 스토리로 확인됨) 이 매핑 한 줄 추가만으로 여섯 전략 모두가 요구된 방식대로 렌더링된다.

## Boundaries & Constraints

**Always:** `STRATEGY_LABEL`은 라벨의 단일 출처로 유지하고(`StrategyTagList`/`/strategies/[strategy]` 양쪽이 계속 이 맵 하나만 공유), `getStrategyLabel`의 own-property 검사(prototype pollution 방지)를 그대로 보존한다. 배지는 색상 없이 텍스트 라벨만으로 전략을 구분하는 기존 스타일을 유지한다(UX-DR14).

**Never:** `StrategyTagList.tsx`, `/strategies/[strategy]/page.tsx`, `globals.css`의 `.strategy-tag*` 규칙, `candidate-cards.ts`(+N 접힘 로직)를 변경하지 않는다 — 이미 전략 키 개수에 무관하게 동작하며 이번 스토리 범위 밖이다. F의 실제 설명/성과 콘텐츠(플레이스홀더 텍스트를 실제 성과 데이터로 채우는 것)는 범위 밖이다(`/tracking`과 동일하게 다른 전략들도 아직 플레이스홀더다 — 6.6/Epic 6이 이미 확립한 선례, 이번 스토리로 새로 만드는 격차가 아니다).

## I/O & Edge-Case Matrix

| Scenario | Input / State | Expected Output / Behavior | Error Handling |
|----------|--------------|---------------------------|----------------|
| HAPPY_PATH | `getStrategyLabel("F")` 호출 | `"전략 F"` 반환 | 오류 없음 |
| DASHBOARD_BADGE | 후보 카드의 `visibleStrategies`에 `"F"` 포함 | `StrategyTagList`가 `/strategies/F` 링크의 `전략 F` 배지를 렌더링(다른 전략과 동일한 가로 나열/`+N` 접힘 규칙) | 오류 없음 |
| ROUTE_F | `/strategies/F` 요청 | `전략 F` 제목과 준비 중 문구를 렌더링(200) | 없음 |
| ROUTE_UNDEFINED | `/strategies/G`(정의되지 않은 코드) 요청 | 여전히 404(`notFound()`) | Next.js `notFound()` |

</intent-contract>

## Code Map

- `apps/web/lib/strategy-labels.ts:1-11` -- `STRATEGY_LABEL`이 A~E만 정의(모듈 docstring도 "전략 A/B/C/D/E 표시 라벨"로 한정). `F: "전략 F"` 추가, docstring을 "A~F"로 갱신. `getStrategyLabel`(own-property 검사)은 전략 키 개수와 무관하게 동작하므로 변경 없음.
- `apps/web/lib/strategy-labels.test.ts:16-18` -- `getStrategyLabel("F")`가 `undefined`를 반환한다고 단언하는 기존 테스트가 이번 변경으로 깨진다. F를 "정의된 라벨" 그룹으로 옮기고, "정의되지 않은 전략 코드" 테스트는 F 대신 실제로 미정의인 코드(예 `"G"`)로 교체한다.
- `apps/web/components/dashboard/StrategyTagList.tsx` -- `getStrategyLabel`을 통해 라벨을 조회하고 `visibleStrategies`/`hiddenCount`를 그대로 렌더링(전략 키 목록을 하드코딩하지 않음, Epic 6에서 이미 가변 개수 대응 완료). 변경 없음, 그대로 소비.
- `apps/web/app/strategies/[strategy]/page.tsx` -- `getStrategyLabel(strategy)`가 `undefined`면 `notFound()`, 아니면 라벨을 렌더링. 전략 코드를 하드코딩하지 않으므로 변경 없음.
- `apps/web/app/globals.css:384-415` -- `.strategy-tag`/`.strategy-tag-list`/`.strategy-tag--more`가 전략별 색상 분기 없는 단일 스타일(텍스트 라벨만으로 구분, UX-DR14 요건이 이미 구조적으로 충족돼 있음). 변경 없음, 접근성 재확인만 수행.
- `apps/web/lib/candidate-cards.ts:42` -- `visibleStrategies: row.strategies.slice(0, MAX_VISIBLE_TAGS)`. 전략 개수를 하드코딩하지 않음(`array_agg(distinct t.strategy order by t.strategy)` 기반 정렬만 가정). 변경 없음.

## Tasks & Acceptance

**Execution:**
- `apps/web/lib/strategy-labels.ts` -- `STRATEGY_LABEL`에 `F: "전략 F"`를 추가하고 모듈 docstring을 "A~F"로 갱신한다 -- AC1.
- `apps/web/lib/strategy-labels.test.ts` -- F를 "정의된 라벨" 테스트로 이동(D/E 테스트 그룹에 추가하거나 별도 단언 추가)하고, "정의되지 않은 전략 코드" 테스트의 대상을 `"G"`로 교체한다 -- I/O 매트릭스 HAPPY_PATH/ROUTE_UNDEFINED.

**Acceptance Criteria:**
- Given `STRATEGY_LABEL`이 A/B/C/D/E로 한정된 경우, when F 라벨을 추가하면, then `StrategyTagList.tsx`가 여섯 전략 모두를 UX-DR7 규칙(가로 나열, 좁은 폭에서 `+N` 접힘)대로 렌더링한다(코드 변경 없이 데이터 매핑만으로 충족, StrategyTagList/candidate-cards가 이미 키 개수 불문 구조임을 Code Map에서 확인).
- Given `/strategies/[strategy]` 라우트가 A/B/C/D/E만 검증하는 경우, when F 경로를 추가하면, then 전략 설명/성과 페이지가 정상 렌더링되고(`/strategies/F` → 200, `전략 F` 제목), 정의되지 않은 전략 코드(`/strategies/G`)는 여전히 404 처리된다.
- Given 배지 색상 체계에 F가 추가되는 경우, when 접근성을 재확인하면, then 색상만으로 전략을 구분하지 않고(UX-DR14) 텍스트 라벨이 항상 함께 제공된다(현재 `.strategy-tag` 스타일이 전략별 색상 분기가 없는 단일 텍스트 배지 스타일임을 확인하는 것으로 충족, 코드 변경 불필요).

## Design Notes

Epic 6이 `StrategyTagList`/`candidate-cards.ts`/`/strategies/[strategy]`를 이미 "가변 개수 전략" 전제로 일반화해 뒀고(다중 태그 인프라, Story 6.6 선례), 배지 스타일도 애초에 전략별 색상 분기가 없는 단일 텍스트 스타일이라 UX-DR14 요건이 구조적으로 이미 충족돼 있다. 따라서 실제 남은 gap은 `STRATEGY_LABEL` 데이터 맵 한 줄(F 라벨)뿐이다 -- Story 7.5가 tags stage의 하드코딩된 5-전략 상수를 해소한 것과 정확히 같은 패턴.

## Verification

**Commands:**
- `npm test -w apps/web` (또는 `node --test apps/web/lib/strategy-labels.test.ts` 경로에 맞는 스크립트) -- expected: F 관련 갱신 테스트 포함 전체 통과.
- `npm run typecheck` -- expected: 통과.
- `npm run build -w apps/web` (또는 프로젝트 표준 빌드 스크립트) -- expected: `/strategies/[strategy]` 라우트 빌드 성공.

**Manual checks (if no CLI):**
- `/`, `/strategies/[strategy]`가 `proxy.ts`(AD-7)로 보호된 라우트라 실제 로그인 세션 없이는 e2e 자동화가 불가능하다(Story 1.10/spec-2-7이 이미 확립한 한계 — `e2e/home.spec.ts`/`manual-trigger.spec.ts` 주석 참고). Neo가 실제 브라우저로 로그인한 뒤 `/strategies/F`(정상 렌더링, `전략 F` 제목)와 `/strategies/G`(404), 그리고 F가 태깅된 후보가 있는 대시보드 화면에서 `전략 F` 배지 렌더링을 확인한다.

실행 결과:

- `npm test -w apps/web` -- 77 passed(전략 D/E/F 정의 라벨 테스트 포함, 회귀 없음).
- `npm run typecheck` -- 통과.
- `npm run build -w apps/web` -- 통과, `/strategies/[strategy]` 라우트 정상 빌드 확인.
- `git diff --check` -- 통과(공백 오류 없음).
- Matrix Test Audit: HAPPY_PATH는 `strategy-labels.test.ts`의 자동화 테스트로 실행·통과 확인. DASHBOARD_BADGE/ROUTE_F/ROUTE_UNDEFINED는 `proxy.ts`의 인증 게이트(AD-7) 때문에 CI/무인 실행에서 자동화할 수 없는 기존 한계(Story 1.10/spec-2-7 선례와 동일 근거, `StrategyTagList.tsx`/`page.tsx`가 전략 키 개수와 무관하게 동작함을 Code Map에서 코드로 직접 확인)이며, 실제 로그인 세션이 있는 Neo의 수동 확인으로 남겨둔다(신규 격차 아님, 선행 스토리들과 동일 관례).
- 매뉴얼 확인(로그인 세션 필요) 항목은 이번 자동 실행 범위에서 미실행 상태로 남아 있으며, 잔존 리스크로 추적한다(Neo의 실제 브라우저 확인 필요).

## Spec Change Log

## Review Triage Log

### 2026-09-08 — Review pass (blind-hunter / edge-case-hunter / verification-gap / intent-alignment, 4계층 병렬)
- intent_gap: 0
- bad_spec: 0
- patch: 1: (high 0, medium 0, low 1)
- defer: 1: (high 0, medium 0, low 1)
- dismissed:
  - (blind-hunter) 재컴파일된 `epic-7-context.md`가 기존(영문) 버전에 있던 백테스트 수치·버그 이력·OOS 구간·마이그레이션 파일명·진입조건 서술·"Story 7.6은 7.5에 의존"·상태(status) 아이콘 일반화를 누락했다는 지적 7건 — `compile-epic-context.md`(이 파일을 생성하는 작업 스펙) 자체가 "Scope aggressively", "No full copies... Always distill", "No story-level details", "800–1500 tokens 목표"를 명시적으로 요구하며, 위 항목들은 모두 스토리 레벨 세부사항(7.1/7.4/7.7 개별 스펙이 이미 보유) 또는 타 에픽(상태 배지) 범위라 이 작업의 정당한 압축 결과다. 이번 스토리(7.6)가 유발한 회귀가 아니라 compile 작업 자체의 설계된 동작.
  - (blind-hunter) 신규 Requirements 문구의 `t1859`/`104종목` 식별자가 근거 없이 도입됐다는 지적 — `_bmad-output/planning-artifacts/briefs/brief-wave-double-2026-08-31/brief.md:28`, `addendum.md:8,21,73,76`에서 이미 동일 식별자·수치가 정의돼 있음을 직접 확인, 환각이 아니다.
  - (blind-hunter) `apps/web/lib/candidate-cards.test.ts`에 6전략(A~F) 동시 존재 케이스가 없다는 지적 — `MAX_VISIBLE_TAGS=2`이고 `slice`/`Math.max(0, length - MAX_VISIBLE_TAGS)` 절단 로직은 태그 총개수와 무관하게 동작하며, 기존 `MULTI_TAG_5`(5개 초과 케이스)가 이미 "MAX 초과 시 접힘" 일반 동작을 증명한다. `candidate-cards.ts`는 이번 스토리의 Never 목록(불변 파일)이라 6-tag 전용 테스트 추가는 새 동작을 검증하지 않는다.
  - (blind-hunter) frontmatter `followup_review_recommended: false`가 매뉴얼 확인 미실행 상태와 모순된다는 지적 — 이 필드는 워크플로우 정의상 이번 리뷰 패스의 patch 심각도 집계로 Finalize 단계에서 산정되는 값이며(매뉴얼 확인 미실행 여부와 무관), 시점상 아직 계산 전이었다. 실제 계산은 아래 Finalize에서 수행.
  - (blind-hunter) 스프린트 상태 동기화 커밋이 이 diff에 없다는 지적 — spec-7-5 Review Triage Log에 이미 기록된 것과 동일 근거: 사용자 지시 순서(개발→검수/보완→e2e 필요성 판단→스프린트 동기화→커밋)상 스프린트 동기화는 리뷰 이후 순서라 예상된 상태.
  - (intent-alignment) DASHBOARD_BADGE/ROUTE_F/ROUTE_UNDEFINED의 AC 문구가 컴포넌트/라우트 동작을 서술하는데 diff의 테스트는 데이터 맵(`getStrategyLabel`) 단위테스트뿐이라는 지적 — `proxy.ts`(AD-7)가 `/`, `/strategies/[strategy]`를 인증 게이트로 보호해 실제 로그인 세션 없이는 CI에서 이 표면을 자동화할 수 없다(Story 1.10/spec-2-7이 이미 확립한 동일 한계, `e2e/home.spec.ts`·`manual-trigger.spec.ts` 주석 참고). `StrategyTagList.tsx`/`page.tsx`를 직접 읽어 전략 키 개수와 무관하게 동작함을 코드로 확인했고, 이 구조적 근거 + 확립된 프로젝트 관례가 "다중 해석 사이에 선택 근거가 없는 intent gap"이 아니라 유일하게 실행 가능한 해석(narrow reading)임을 뒷받침한다.
  - (intent-alignment) 서술적 감사 보고 — 4가지 방어 가능한 해석을 나열하고 diff가 narrow reading(reading 1)을 구현함을 확인. 위와 동일 근거로 다중 해석 사이 선택 근거 부재가 아니다.
  - (edge-case-hunter) 발견 없음(`[]`).
  - (verification-gap) 발견 없음("No verification gaps found.").
- addressed_findings:
  - `[low]` `[patch]` (blind-hunter) 스펙 Verification 절이 아직 존재하지 않는 `## Auto Run Result`의 Residual risks를 미리 참조하는 허공 참조였음 — Finalize에서 채워질 것을 전제하지 않도록 문구를 자기완결적으로 수정.
  - `[low]` `[defer]` (blind-hunter) `apps/web/lib/candidate-cards.ts:4`의 Design Notes 주석("전략은 A~E까지 가변 개수로 태깅될 수 있다(현재 최대 5종)")이 F 추가로 최대 6종이 됐음에도 갱신되지 않아 stale — 이 스토리 이전(7.5 완료 시점)부터 이미 부정확했던 기존 이슈이고 이 파일은 이번 스토리의 Never 목록(변경 금지 대상)이라 이번 diff가 유발한 회귀가 아니므로 defer로 기록.

## Auto Run Result

Summary: `apps/web/lib/strategy-labels.ts`의 `STRATEGY_LABEL`이 A~E로만 한정돼 있어 Story 7.1~7.5로 이미 계산·태깅 가능해진 전략 F가 대시보드 배지와 `/strategies/[strategy]` 페이지에서 라벨 없이 노출되던 것을, `STRATEGY_LABEL`에 `F: "전략 F"` 한 줄을 추가해 해결했다. `StrategyTagList.tsx`/`/strategies/[strategy]/page.tsx`/`globals.css`/`candidate-cards.ts`는 Epic 6에서 이미 전략 키 개수와 무관하게 동작하도록 일반화돼 있어(가변 개수 다중 태그 인프라, 색상 분기 없는 단일 텍스트 배지 스타일) 코드 변경이 필요 없었다.

Files changed:
- `apps/web/lib/strategy-labels.ts` — `STRATEGY_LABEL`에 `F: "전략 F"` 추가, 모듈 docstring을 "A~F"로 갱신.
- `apps/web/lib/strategy-labels.test.ts` — `getStrategyLabel("F")` 기대값을 `undefined`에서 `"전략 F"`로 이동(정의된 라벨 테스트군에 병합), "정의되지 않은 전략 코드" 테스트 대상을 실제 미정의 코드 `"G"`로 교체.
- `_bmad-output/implementation-artifacts/epic-7-context.md` — 캐시된 Epic 7 컨텍스트가 최신 계획 문서보다 오래돼(step-01 유효성 검사 실패) 재컴파일(별도 subagent, `compile-epic-context.md` 규칙에 따라 재작성).
- `_bmad-output/implementation-artifacts/spec-7-6-ui-확장-라벨-배지-라우트-f.md` — 신규 스펙 문서(본 파일).

Review findings breakdown (2026-09-08, 4계층 병렬 리뷰 패스): patch 1건(low 1) 수정 — 스펙 Verification 절의 허공 참조(존재하지 않는 섹션 선참조)를 자기완결적 문구로 수정. defer 1건(low 1) — `candidate-cards.ts`의 stale "현재 최대 5종" 주석(이 스토리 이전부터 존재한 기존 이슈, 이번 diff가 손댈 수 없는 파일이라 frontmatter `deferred`에 기록). dismissed 9건(위 Review Triage Log에 각각 근거 기록: epic-context 재컴파일의 내용 압축은 `compile-epic-context.md` 자체 규칙에 따른 정당한 동작 7건, t1859/104종목 식별자는 브리프 문서에 이미 근거 있음, 6-tag 전용 테스트 부재는 count-agnostic 절단 로직과 out-of-scope 파일이라 불필요, `followup_review_recommended` 조기 우려는 필드 산정 시점 오해, 스프린트 동기화 미포함은 예상된 순서, DASHBOARD_BADGE/ROUTE_F/ROUTE_UNDEFINED가 컴포넌트/라우트 테스트가 아닌 데이터맵 단위테스트로만 검증됨은 AD-7 인증 게이트로 인한 확립된 프로젝트 관례). intent_gap·bad_spec 없음.

Follow-up review recommendation: false (패치 low 1건; 점수 1×1=1 < 5, high 없음).

Verification: `npm test -w apps/web` 77 passed(전략 D/E/F 정의 라벨 테스트 포함, 회귀 없음), `npm run typecheck` 통과, `npm run build -w apps/web` 통과(`/strategies/[strategy]` 라우트 정상 빌드), `git diff --check` 통과(공백 오류 없음). Matrix Test Audit: HAPPY_PATH는 자동화 테스트로 실행·통과 확인. DASHBOARD_BADGE/ROUTE_F/ROUTE_UNDEFINED는 `proxy.ts`(AD-7) 인증 게이트로 CI에서 자동화 불가능한 기존 프로젝트 한계(Story 1.10/spec-2-7 선례)이며, 코드 직접 확인(`StrategyTagList.tsx`/`page.tsx`가 전략 키 개수 불문 동작)으로 구조적 충족을 확인했다. 리뷰 패치 1건 반영 후 재검증 통과.

Residual risks: `/strategies/F`(정상 렌더링) · `/strategies/G`(404) · F 태깅된 후보의 대시보드 배지 렌더링은 실제 로그인 세션이 필요해 이번 자동 실행에서 브라우저로 직접 확인하지 못했다(Neo의 수동 확인 필요, 확립된 프로젝트 관례상 신규 격차 아님). `candidate-cards.ts`의 stale 주석은 별도 defer 항목으로 추적 중이다. Story 7.7(OOS 검증)은 이 스토리 범위 밖으로 별도 추적 중이다.

