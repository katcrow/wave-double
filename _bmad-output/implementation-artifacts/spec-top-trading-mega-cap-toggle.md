---
title: '거래대금 상위 후보 대형주(삼성전자·SK하이닉스) 포함/제외 토글'
type: 'feature'
created: '2026-10-02'
status: 'done'
baseline_commit: 'f6908c0aff2020175a4bbee8938cdd9dc94021bb'
review_loop_iteration: 0
context: []
---

<frozen-after-approval reason="human-owned intent — do not modify unless human renegotiates">

## Intent

**Problem:** 삼성전자(005930)·SK하이닉스(000660)는 거래대금이 항상 커서 `거래대금 상위 후보` 3칸을 자주 차지해, 다른 후보를 비교할 공간이 줄어든다.

**Approach:** 상위 후보 RPC가 제외 ticker 배열을 받아 조회 단계에서 제외한 뒤 상위 3개를 반환하게 하고, 서버가 '제외'/'포함' 두 목록을 모두 조회해 섹션의 토글로 전환한다. 기본값은 '제외'다. 프로그램 수급 수집 대상도 제외 모드 상위 3개까지 넓혀 새로 올라온 후보가 미확인으로 남지 않게 한다.

## Boundaries & Constraints

**Always:** 제외 모드도 후보가 3개 이상이면 항상 3개를 표시한다(화면 필터가 아니라 SQL에서 제외 후 `limit 3`). 기존 snapshot lineage, 정렬(trading_value DESC, ticker ASC), 지표 계산은 그대로 둔다. 기본 선택은 '제외'이고, 새로 고치면 다시 '제외'로 시작한다(저장하지 않음). 제외 대상은 코드 상수 `['005930', '000660']` 하나로 관리하고, web과 batch에 같은 값을 둔다.

**Never:** 토글할 때 클라이언트에서 다시 조회하지 않는다. 제외 대상을 관리하는 UI나 DB 테이블을 만들지 않는다. 후보 카드 목록(`CandidateList`)과 기존 필터 동작은 바꾸지 않는다.

## I/O & Edge-Case Matrix

| Scenario | Input / State | Expected Output / Behavior | Error Handling |
|----------|--------------|---------------------------|----------------|
| DEFAULT_EXCLUDE | 상위 5개에 005930·000660 포함 | 기본 '제외' 화면에 두 종목을 뺀 상위 3개, 순위 1~3 | N/A |
| TOGGLE_INCLUDE | 사용자가 '전체'를 선택 | 기존과 같은 상위 3개 | N/A |
| NOT_IN_TOP | 두 종목이 후보에 없음 | 두 모드의 결과가 같음 | N/A |
| FEW_CANDIDATES | 제외 후 남은 후보가 2개 이하 | 남은 후보만 표시 | N/A |
| ONE_MODE_FAILS | 한쪽 RPC만 실패하거나 응답 shape가 다름 | 섹션 유지, 실패한 모드를 선택하면 "표시할 후보가 없습니다" | console.error 기록 |
| BOTH_EMPTY | 두 목록 모두 비어 있음 | 섹션 숨김(기존 동작) | N/A |

</frozen-after-approval>

## Code Map

- `infra/supabase/migrations/202610020900_persist_candidate_themes_and_candidate_card.sql` -- 현재 `get_top_tagged_candidates(p_run_id uuid)` 정의(본문 복사 원본, `limit 3`), grant와 comment 포함
- `apps/web/app/page.tsx:76-95` -- 서버 컴포넌트가 상위 후보 RPC를 한 번 호출하고 `:193`에서 `<TopTradingCandidates candidates>`로 렌더
- `apps/web/lib/top-trading-candidates.ts` -- 행 검증, 뷰모델 생성, `TOP_TRADING_CANDIDATE_LIMIT`. 상수를 둘 자리
- `apps/web/components/dashboard/TopTradingCandidates.tsx` -- 현재 서버 컴포넌트, 빈 목록이면 `null` 반환
- `apps/web/app/globals.css:1146~` -- `.top-trading-candidates__*` 스타일(header는 flex)
- `apps/batch/tagged_candidate_fetcher.py:97` -- `rows[:3]`로 상위 3개 + active 태그 합집합을 프로그램 수급 수집 대상으로 정함
- `packages/read-model/src/database.types.ts` -- RPC Args 타입
- `e2e/mock-supabase-server.mjs:180` -- 상위 후보 mock, 현재 4행(005930, 000660, 035420, 051910)이고 body를 필터링하지 않음
- `e2e/authenticated-dashboard.spec.ts:35-47` -- 첫 항목 005930 등을 단언하므로 기본 '제외'에 맞춰 수정 필요
- Tests: `apps/web/lib/top-trading-candidates.test.ts`, `tests/batch/test_tagged_candidate_fetcher.py`, `tests/sql/test_get_top_tagged_candidates.sql`

## Tasks & Acceptance

**Execution:**
- [x] `infra/supabase/migrations/202610021700_top_trading_exclude_tickers.sql` -- `drop function public.get_top_tagged_candidates(uuid)` 후 `(p_run_id uuid, p_exclude_tickers text[] default '{}')`로 재생성. 본문은 기존 그대로 두고 후보 조건에 `and not (c.ticker = any(coalesce(p_exclude_tickers, '{}')))`만 추가. grant와 comment 재설정 -- overload 모호성을 막고 하위 호환을 유지
- [x] `tests/sql/test_get_top_tagged_candidates.sql` -- 제외 배열을 주면 다음 순위가 채워져 3개가 되는 케이스 추가
- [x] `packages/read-model/src/database.types.ts` -- Args에 `p_exclude_tickers?: string[]` 추가
- [x] `apps/web/lib/top-trading-candidates.ts` -- `TOP_TRADING_EXCLUDED_TICKERS = ["005930", "000660"] as const` export
- [x] `apps/web/app/page.tsx` -- 두 RPC(제외/포함)를 `Promise.all`로 조회하고, 각각 독립적으로 검증해 `excluded`/`all` 뷰모델을 만든다. 실패는 모드별로 기존처럼 로그만 남긴다
- [x] `apps/web/components/dashboard/TopTradingCandidates.tsx` -- `"use client"`. props `{ excludedCandidates, allCandidates }`. header에 2버튼 토글 그룹("삼성전자·SK하이닉스 제외" / "전체", `aria-pressed`) 추가, 기본값은 제외. 두 목록이 모두 비면 `null`, 선택한 목록만 비면 빈 상태 문구 표시
- [x] `apps/web/app/globals.css` -- 토글 스타일(기존 토큰 사용, 모바일에서 줄바꿈 허용)
- [x] `apps/batch/tagged_candidate_fetcher.py` -- `EXCLUDED_TOP_TICKERS` 상수를 두고, 수집 대상을 active ∪ 상위 3개 ∪ 제외 후 상위 3개로 확장
- [x] `tests/batch/test_tagged_candidate_fetcher.py` -- 두 종목이 상위에 있을 때 제외 후 상위 3개도 포함되는지 테스트
- [x] `apps/web/lib/top-trading-candidates.test.ts` -- 상수 값 단언
- [x] `e2e/mock-supabase-server.mjs` -- 5번째 행(068270 셀트리온, 80000000) 추가. `p_exclude_tickers`로 필터링 후 3개로 자름
- [x] `e2e/authenticated-dashboard.spec.ts` -- 기본 화면에 NAVER/LG화학/셀트리온이 보이는지 확인하고, '전체'를 누른 뒤 기존 005930 지표 단언 수행

**Acceptance Criteria:**
- Given 대시보드를 처음 열었을 때, when 섹션을 보면, then '삼성전자·SK하이닉스 제외' 버튼이 `aria-pressed=true`이고 두 종목이 목록에 없다.
- Given 마이그레이션이 적용됐을 때, when 기존처럼 `p_run_id`만 넘겨 호출하면, then 이전과 같은 결과를 반환한다.
- Given 제외 모드 상위 3개에 active 태그가 없는 후보가 있을 때, when 배치가 수급을 수집하면, then 그 후보도 프로그램 수급 수집 대상에 들어간다.

## Spec Change Log

## Review Triage Log

- 리뷰 1차(blind, edge-case, verification-gap). patch 2건 반영: (1) `p_exclude_tickers`에 NULL 원소가 있으면 모든 행이 걸러져 빈 결과가 나오던 문제를 `array_remove(..., null)`로 수정하고 SQL 테스트를 추가했다(운영 DB 재적용 완료). (2) web/batch 제외 상수가 서로 어긋나도 테스트가 실패하지 않던 문제는 TS 상수를 읽어 Python 상수와 비교하는 parity 테스트로 보완했다.
- 웹을 마이그레이션보다 먼저 배포하는 경우와 PostgREST 스키마 캐시 미갱신: 마이그레이션이 이미 운영 DB에 적용됐고, REST로 기존 호출·제외 호출·빈 배열 호출을 모두 확인했으므로 발생할 경로가 없어 기각했다.
- 실패한 쪽 모드에 "표시할 후보가 없습니다"가 보이고, 기본 '제외' 모드가 그대로 유지되는 것: 고정된 I/O 표 ONE_MODE_FAILS에 정한 동작이라 기각했다.
- 두 종목이 상위에 없으면 토글이 아무것도 바꾸지 않는 것: I/O 표 NOT_IN_TOP에 정한 동작이라 기각했다.
- 설명 문구와 순위 라벨이 제외 후 순위임을 밝히지 않는 것: 선택된 버튼(aria-pressed)이 모드를 나타내고 설명 문구도 여전히 정확해 화면상 결함이 아니므로 기각했다.
- 버튼 라벨이 상수에서 만들어지지 않는 것과 상수 테스트가 리터럴만 확인하는 것: 상수 중복은 Design Notes에서 받아들인 결정이고, 실제 위험인 web/batch 불일치는 parity 테스트로 해결했다.
- batch 합집합 테스트 보강(태그 겹침, 동률, 남은 후보 3개 미만): `[r for r in rows if ticker not in EXCLUDED][:3]`는 정렬된 rows 위에서 맞게 동작하고, 지적된 결함 경로가 없어 기각했다.
- 수급 수집 증가: 상위 3개와의 합집합이라 실행당 최대 2종목만 늘어 시간 제한에 영향이 없으므로 기각했다.
- 이전 overload 제거와 grant 검증 테스트 부재: 운영 DB에서 시그니처가 하나만 남았고 anon·authenticated 실행 권한이 있음을 확인했으며, 지적된 결과가 발생하지 않아 기각했다.
- anon이 배열 크기를 제한 없이 보낼 수 있는 것: run 하나 범위의 stable 조회이고 PostgREST 요청 크기 제한이 적용되며, 기존에도 anon이 같은 RPC를 호출할 수 있었으므로 기각했다.
- RPC 두 번 호출, "use client" 번들 크기: 후보 모집단이 작아(run 하나) 측정할 만한 비용이 없어 기각했다.
- aria-pressed 토글 패턴과 header gap: aria-pressed 토글 버튼은 표준 패턴이고, 기존 `.top-trading-candidates__header` 규칙에 이미 `gap`이 있어 기각했다.
- mock의 `.slice(0, 3)`: 실제 limit은 SQL 테스트와 뷰모델 slice가 검증하므로 가려지는 결함이 없어 기각했다.
- Python 중첩 comprehension 가독성: 동작 결함이 없는 스타일 문제라 기각했다.

## Design Notes

두 목록을 모두 서버에서 미리 받는 이유: 페이지가 서버 컴포넌트에서 Supabase를 조회하고 있어, 토글할 때 다시 조회하려면 클라이언트 Supabase나 route가 새로 필요하다. RPC 한 번 추가(병렬)가 가장 작은 변경이다. 제외 목록 상수가 web/batch 두 곳에 중복되지만 값이 2개뿐이라, 공유 설정을 만드는 것보다 주석으로 서로를 가리키는 편이 낫다.

## Verification

**Commands:**
- `npm test` -- expected: web 단위 테스트 통과
- `npm run typecheck -w apps/web` -- expected: 오류 없음
- `uv run pytest tests/batch/test_tagged_candidate_fetcher.py` -- expected: 통과
- `npx playwright test e2e/authenticated-dashboard.spec.ts e2e/candidate-surface-scenarios.spec.ts` -- expected: 통과
- SQL 테스트(`tests/sql/test_get_top_tagged_candidates.sql`)는 마이그레이션 적용 후 운영 DB에서 실행해 통과를 확인한다(트랜잭션 안에서 실행 후 rollback)

## Suggested Review Order

**조회 단계 제외(DB)**

- 제외는 `limit 3` 전에 적용해 항상 3개를 채우고, NULL 원소는 무시한다
  [`202610021700_top_trading_exclude_tickers.sql:79`](../../infra/supabase/migrations/202610021700_top_trading_exclude_tickers.sql#L79)

**서버 조회와 토글 화면**

- '제외'/'전체'를 병렬로 받고, 모드별로 따로 검증해 실패를 서로 격리한다
  [`page.tsx:81`](../../apps/web/app/page.tsx#L81)
- 기본값은 '제외'이고 저장하지 않는다. 다시 조회하지 않고 미리 받은 목록만 바꾼다
  [`TopTradingCandidates.tsx:25`](../../apps/web/components/dashboard/TopTradingCandidates.tsx#L25)
- 두 목록이 모두 비면 섹션을 숨기고, 선택한 목록만 비면 빈 상태 문구를 보여 준다
  [`TopTradingCandidates.tsx:27`](../../apps/web/components/dashboard/TopTradingCandidates.tsx#L27)
- 제외 대상 상수는 하나다(batch와 parity 테스트로 묶음)
  [`top-trading-candidates.ts:10`](../../apps/web/lib/top-trading-candidates.ts#L10)

**프로그램 수급 수집 대상(배치)**

- 제외 모드 상위 3개도 수집해, 새로 올라온 후보가 미확인으로 남지 않게 한다
  [`tagged_candidate_fetcher.py:104`](../../apps/batch/tagged_candidate_fetcher.py#L104)

**테스트와 주변 변경**

- 제외 후 채움, 기존 호출 호환, NULL, 남은 후보 부족 케이스
  [`test_get_top_tagged_candidates.sql:242`](../../tests/sql/test_get_top_tagged_candidates.sql#L242)
- web/batch 제외 상수 parity
  [`test_tagged_candidate_fetcher.py:179`](../../tests/batch/test_tagged_candidate_fetcher.py#L179)
- 기본 '제외' 화면과 '전체' 전환 E2E
  [`authenticated-dashboard.spec.ts:39`](../../e2e/authenticated-dashboard.spec.ts#L39)
- '제외' 조회만 실패하는 시나리오
  [`authenticated-dashboard.spec.ts:114`](../../e2e/authenticated-dashboard.spec.ts#L114)
- mock이 실제 RPC처럼 제외한 뒤 3개로 자른다
  [`mock-supabase-server.mjs:205`](../../e2e/mock-supabase-server.mjs#L205)
- RPC 인자 타입, 토글 스타일
  [`database.types.ts:1083`](../../packages/read-model/src/database.types.ts#L1083)
  [`globals.css:1267`](../../apps/web/app/globals.css#L1267)
