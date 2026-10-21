---
title: '종가배팅 참고확률을 상단 컴팩트 칩으로 이동'
type: 'refactor'
created: '2026-10-21'
status: 'done'
review_loop_iteration: 0
baseline_commit: 'acf8803373c683bf73ba0e0d609041884ca6319c'
context:
  - '{project-root}/AGENTS.md'
---

<frozen-after-approval reason="human-owned intent — do not modify unless human renegotiates">

## Intent

**Problem:** 종가배팅 참고확률은 코스피·코스닥 숫자 두 개와 기준 시각이 핵심인데, 페이지 맨 아래 큰 섹션(`market-supply-panel` 스타일)을 차지해 공간 낭비가 크고 종가배팅 판단 시점에 눈에 잘 띄지 않는다.

**Approach:** 확률 표시를 상단 데이터 신뢰도 바와 같은 행에 놓이는 별도 컴팩트 칩(서버 컴포넌트)으로 바꾼다. 신뢰도 바 컴포넌트 내부에는 합치지 않고, 두 요소를 감싸는 상단 행이 좁은 화면에서 자동 줄바꿈되게 한다.

## Boundaries & Constraints

**Always:** '참고용' 표시 유지. 확률 조회는 스냅샷 존재/오류와 독립(스냅샷 오류 화면에도 칩 표시). 기준일·목표일·마지막 계산 시각·검증 상태 정보는 칩 안에 남긴다(긴 설명 문구는 `<details>`로 접기). 기존 디자인 토큰(`--space-*`, `--color-*`, `--font-size-*`)만 사용.

**Never:** `DataTrustBar.tsx` 수정 또는 그 `role="status" aria-live` 영역 안에 확률 배치. 확률 RPC·DB·배치 변경. 후보 순서/주문 동작 변경. 새 의존성 추가.

## I/O & Edge-Case Matrix

| Scenario | Input / State | Expected Output / Behavior | Error Handling |
|----------|--------------|---------------------------|----------------|
| 정상 | 오늘 `trading_day` 행 | 칩에 코스피 %, 코스닥 % (소수 1자리), 날짜·계산시각·검증상태 메타 | N/A |
| 직전값 | `trading_day` ≠ 오늘 KST | 값 표시 + "직전값" 배지 | N/A |
| 값 없음 | row null, 실패 아님 | 칩에 "아직 계산 전" 짧은 문구 | N/A |
| 조회 실패 | fetchFailed true | 칩에 "불러오기 실패" 짧은 문구 | 페이지 나머지 정상 렌더 |

</frozen-after-approval>

## Code Map

- `apps/web/components/dashboard/MarketProbabilityPanel.tsx` -- 현재 큰 섹션 렌더. 칩 마크업으로 교체(파일명/기본 export명은 `MarketProbabilityChip`로 변경). `percent()`, stale 판정(`trading_day !== todayKst`), `Intl` 시각 포맷 재사용.
- `apps/web/app/page.tsx:48` -- 스냅샷 오류 분기에서 패널 렌더. 제목 아래로 이동.
- `apps/web/app/page.tsx:216,247` -- `DataTrustBar` 렌더(216)와 하단 패널(247). 247 제거, 216을 상단 행 래퍼로 감싸고 칩 추가.
- `apps/web/app/globals.css:238-249` -- `.data-trust-bar`가 `margin: 0 0 var(--space-6)` 보유. 래퍼가 하단 여백을 갖도록 래퍼 안에서는 margin 0.
- `apps/web/app/globals.css:1908-1957` -- `.market-supply-panel*` 스타일(수급 패널이 계속 사용 — 삭제 금지). `__intraday-label` 배지 스타일을 칩 배지 참고용으로 재사용 가능.
- `apps/web/lib/dashboard-types.ts:19-40` -- `MarketIndexProbabilityRpcRow` 타입/가드. 읽기 전용.
- `e2e/tracking.spec.ts:40` -- "데이터 신뢰도" 텍스트만 확인. 확률 셀렉터를 쓰는 테스트는 없음(컴포넌트 렌더 테스트 없음, `node --test lib/**/*.test.ts`만 존재).

## Tasks & Acceptance

**Execution:**
- [x] `apps/web/lib/market-probability.ts` (+ `.test.ts`) -- 순수 함수 `deriveMarketProbabilityChipState(row, fetchFailed, todayKst)`로 상태(`failed`/`empty`/`ready` + `stale`)와 표시 문자열(퍼센트) 도출 -- I/O 매트릭스 4케이스 단위 테스트 가능하게 분리.
- [x] `apps/web/components/dashboard/MarketProbabilityChip.tsx` -- 기존 Panel 파일을 대체. `<aside aria-label="종가배팅 참고 확률">` 안에 라벨 "종가배팅 참고" + "참고용" 배지, 코스피/코스닥 값(`<dl>`), 한 줄 메타, 직전값 배지, `<details><summary>ⓘ</summary>` 설명 문구 -- 섹션 → 칩.
- [x] `apps/web/app/page.tsx` -- 정상 분기: `<div className="dashboard-top-row">`로 `DataTrustBar`+칩 감싸기, 하단 패널 제거. 오류 분기: 제목 아래에 칩 렌더 -- 위치 이동.
- [x] `apps/web/app/globals.css` -- `.dashboard-top-row`(flex, wrap, gap, 하단 여백), 그 안의 `.data-trust-bar`(flex 1 1 420px, margin 0), `.market-probability-chip*`(flex 0 1 320px, surface-raised 배경, 값은 `--font-size-data`·tabular-nums), 767px 이하에서 칩 전체폭 -- 레이아웃.

**Acceptance Criteria:**
- Given 데스크톱 폭(≥1200px), when 대시보드를 열면, then 신뢰도 바와 확률 칩이 같은 행에 나란히 보이고 하단의 큰 확률 섹션은 더 이상 없다.
- Given 모바일 폭(375px), when 대시보드를 열면, then 칩이 신뢰도 바 아래로 줄바꿈되고 가로 스크롤이 생기지 않는다.
- Given 스냅샷 RPC 오류, when 대시보드를 열면, then 오류 문구와 함께 확률 칩이 표시된다.
- Given 칩의 ⓘ, when 펼치면, then 기존 설명 문구("오늘 종가보다 다음 거래일 고가가 높을 확률 …")가 보인다.

## Spec Change Log

## Review Triage Log

- [dismiss] 확률 0.9995 이상/0.0005 미만이 100.0%/0.0%로 반올림 -- 기존 패널과 동일한 `toFixed(1)` 동작이며 이번 변경이 만든 문제가 아님(표시 정책 변경은 범위 밖).
- [dismiss] 배지 CSS가 `.market-supply-panel__intraday-label`과 중복 -- 수급 패널 스타일과 결합을 피하려는 의도적 분리, 기능 영향 없음.
- [dismiss] `todayKst` 계산이 컴포넌트 안에서 `new Date()`를 직접 읽음 -- 기존 패널과 동일, stale 판정 자체는 순수 함수로 테스트됨.
- [dismiss] 메타 줄 날짜 형식 불일치, `feature_as_of`/`model_version` 미표시 -- 기존 패널과 동일한 정보 구성, 이번 범위 밖.
- [dismiss] "fetchFailed인데 row 있음" 조합이 page.tsx상 불가능 -- 순수 함수의 우선순위 계약을 고정하는 테스트로 무해.
- [dismiss] spec 상태/Verification 기록 누락 -- 워크플로가 이후 단계에서 갱신하는 항목.
- [defer] 주말·휴장일·당일 첫 슬롯 전에도 "직전값" 배지 표시 -- 기존 패널의 `trading_day !== todayKst` 판정을 그대로 이어받은 기존 문제.
- [defer] 오래된 정도(N일 전) 구분 없음 -- 기존 판정 정책 문제.
- [defer] ⓘ 펼침/메타 줄 줄바꿈 시 `align-items: stretch`로 신뢰도 바 높이도 함께 늘어남 -- 외형상 문제(낮음), 사용 영향 미미.

## Verification

**Commands:**
- `npm test` (cwd `apps/web`) -- expected: 신규 market-probability 테스트 포함 전부 통과
- `npm run typecheck` (cwd `apps/web`) -- expected: 오류 0
- `npm run build` (cwd `apps/web`) -- expected: 성공

**Manual checks (if no CLI):**
- 로컬 대시보드를 1280px·375px에서 스크린샷으로 확인(칩 위치, 줄바꿈, 가로 스크롤 없음, 콘솔 오류 0).

## Suggested Review Order

**상단 행 배치**

- 신뢰도 바와 칩을 같은 행에 두되 컴포넌트는 분리(aria-live 영역 밖)
  [`page.tsx:218`](../../apps/web/app/page.tsx#L218)

- 스냅샷 오류 시에도 alert 다음에 칩을 독립 표시
  [`page.tsx:48`](../../apps/web/app/page.tsx#L48)

- flex-grow 999/1 조합으로 같은 행이면 바가 공간 차지, 줄바꿈되면 칩 전체폭
  [`globals.css:254`](../../apps/web/app/globals.css#L254)

**칩 표시와 상태**

- 라벨·배지·값·메타·직전값 안내를 한 칩에 압축, 긴 설명은 details로 접음
  [`MarketProbabilityChip.tsx:18`](../../apps/web/components/dashboard/MarketProbabilityChip.tsx#L18)

- 실패 > 없음 > 준비(+stale) 우선순위를 순수 함수로 분리
  [`market-probability.ts:19`](../../apps/web/lib/market-probability.ts#L19)

- 칩 스타일, stale 배지 modifier, ⓘ focus-visible
  [`globals.css:269`](../../apps/web/app/globals.css#L269)

**테스트**

- I/O 매트릭스 4케이스 단위 테스트
  [`market-probability.test.ts:1`](../../apps/web/lib/market-probability.test.ts#L1)

- e2e mock에 확률 RPC 추가(오늘 KST 행)
  [`mock-supabase-server.mjs:118`](../../e2e/mock-supabase-server.mjs#L118)

- 대시보드 e2e에서 칩·퍼센트·직전값 부재 단언
  [`authenticated-dashboard.spec.ts:37`](../../e2e/authenticated-dashboard.spec.ts#L37)
