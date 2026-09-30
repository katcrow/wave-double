---
title: '거래대금 상위 태깅 후보 요약'
type: 'feature'
created: '2026-09-30'
status: 'done'
baseline_revision: '989de87e7d16c13c3db035cc901410cd31b0ec0e'
baseline_commit: '989de87e7d16c13c3db035cc901410cd31b0ec0e'
review_loop_iteration: 0
followup_review_recommended: true
context: ['C:/dev/wave-double/AGENTS.md']
warnings: []
deferred: []
---

<intent-contract>

## Intent

**Problem:** 오늘 태깅된 후보가 여러 종목일 때, 전체 후보 카드를 훑기 전에 거래대금이 큰 종목을 빠르게 참고할 수 있는 상단 요약 영역이 없다.

**Approach:** 기존 카드 RPC와 분리된 전용 RPC에서 현재 실행의 active 태그 후보 중 일간 거래대금 상위 3개만 조회하고, 기존 후보 목록 위에 참고용 카드로 표시한다.

## Boundaries & Constraints

**Always:** 동일한 complete snapshot의 run_id와 trading_day를 사용한다. 전략 종류와 무관하게 active 태그 후보를 포함한다. 거래대금 DESC, 동률이면 ticker ASC로 정렬한다. 3개 미만이면 존재하는 후보만 표시하며, 기존 후보 목록·필터·수급 표시를 유지한다.

**Never:** 전략 판정, 후보 선별, 배치 stage, 태그 저장 규칙을 변경하지 않는다. vanished 태그만 남은 후보를 오늘 태깅 후보로 간주하지 않는다. 다른 실행의 거래대금이나 실시간 재조회 값을 섞지 않는다. 신규 영역의 실패가 기존 후보 카드 렌더링을 막지 않는다.

## I/O & Edge-Case Matrix

| Scenario | Input / State | Expected Output / Behavior | Error Handling |
|----------|--------------|---------------------------|----------------|
| HAPPY_PATH | 같은 published run에 active 태그 후보 4개와 유효한 trading_value 존재 | 상위 3개를 거래대금 내림차순으로 표시 | No error expected |
| TIE_BREAK | trading_value가 같은 후보가 여러 개 | ticker 오름차순으로 순위를 확정 | No error expected |
| FEWER_THAN_THREE | active 태그 후보가 1~2개 | 존재하는 후보만 표시 | No error expected |
| NO_ACTIVE_CANDIDATES | 카드 응답에 vanished-only 후보만 있거나 후보가 없음 | 요약 영역을 표시하지 않음 | 기존 빈 상태와 후보 목록은 유지 |
| FETCH_OR_SHAPE_ERROR | 후보 카드 RPC 실패 또는 trading_value shape 오류 | 요약 영역만 생략 | 기존 후보 카드 오류 처리는 기존 계약대로 유지 |

</intent-contract>

## Code Map

- `infra/supabase/migrations/202609031100_add_vanished_strategies_to_get_today_candidate_cards.sql` -- 현재 `get_today_candidate_cards(uuid)`의 최종 반환 shape와 active/vanished 태그 집계 기준. 기존 카드 RPC 계약은 새 기능으로 깨지지 않게 유지한다.
- `infra/supabase/migrations/202609011700_create_candidates.sql` -- 후보별 `trading_value` 저장 컬럼과 비유한 숫자 방지 제약의 기준.
- `apps/web/app/page.tsx` -- complete snapshot의 run_id로 후보 카드 RPC를 호출하고 후보 목록 위에 새 요약 영역을 배치할 서버 컴포넌트.
- `apps/web/lib/dashboard-types.ts` -- 기존 카드 RPC 계약을 보존하고 새 `TopTradingCandidateRpcRow` shape를 검증한다.
- `apps/web/lib/top-trading-candidates.ts` -- 전용 RPC 응답을 안전한 상단 요약 뷰모델로 변환하고 거래대금 표시 형식을 제공한다.
- `apps/web/components/dashboard/CandidateList.tsx` -- 기존 필터와 전체 후보 목록을 렌더링한다. 새 요약은 이 필터와 독립적으로 동작해야 한다.
- `apps/web/app/globals.css` -- 기존 dark-console 카드 토큰과 반응형 breakpoint를 재사용해 상단 3개 요약 영역을 추가한다.
- `tests/sql/test_get_top_tagged_candidates.sql` -- active/vanished-only, 상위 3개, 동률 정렬 SQL fixture.
- `apps/web/lib/top-trading-candidates.test.ts` -- 전용 RPC 응답의 상위 3개·동률·빈 상태 회귀 테스트.
- `e2e/authenticated-dashboard.spec.ts` -- 인증 대시보드의 외부 화면에서 상단 요약 제목·순위·거래대금 표시를 검증한다.

## Tasks & Acceptance

**Execution:**
- [x] `infra/supabase/migrations/202609301000_create_get_top_tagged_candidates.sql` -- 동일 published run의 active 태그 후보를 거래대금 DESC/ticker ASC로 정렬해 3개만 반환하는 전용 RPC를 추가한다 -- 기존 카드 RPC와 오류 경계를 분리한다.
- [x] `apps/web/lib/dashboard-types.ts`, `apps/web/lib/top-trading-candidates.ts` -- 전용 RPC의 trading_value 타입·shape 검증과 요약 뷰모델을 추가한다 -- 정렬과 표시 단위를 별도 계약으로 고정한다.
- [x] `apps/web/components/dashboard/TopTradingCandidates.tsx`, `apps/web/app/page.tsx` -- 기존 카드 목록 위에 참고용 상위 3개 영역을 렌더링한다 -- 필터와 독립된 상단 요약을 제공한다.
- [x] `apps/web/app/globals.css` -- 데스크톱 3열 및 모바일 단일열 스타일을 추가한다 -- 기존 dark-console UX와 반응형 계약을 유지한다.
- [x] `apps/web/lib/top-trading-candidates.test.ts`, `tests/sql/test_get_top_tagged_candidates.sql`, `e2e/authenticated-dashboard.spec.ts` -- 정렬·태그 상태·빈 상태·표면 렌더링 회귀를 검증한다 -- 기존 카드와 신규 영역의 오류 경계를 고정한다.

**Acceptance Criteria:**
- Given complete snapshot과 active 태그 후보가 4개 이상일 때, when 대시보드를 열면, then 기존 후보 필터 위에 거래대금 상위 3개가 거래대금 DESC로 표시된다.
- Given 거래대금이 같은 후보가 있을 때, when 순위를 계산하면, then ticker ASC가 결정적 tie-breaker로 적용된다.
- Given 후보가 1~2개이거나 active 태그 후보가 없을 때, when 대시보드를 열면, then 가능한 후보만 표시하거나 요약 영역을 숨기고 기존 빈 상태를 유지한다.
- Given vanished-only 후보가 포함된 카드 응답일 때, when 상위 후보를 계산하면, then 해당 후보는 상위 3개에 포함되지 않는다.
- Given 요약 영역 데이터 shape가 잘못되거나 조회가 실패할 때, when 대시보드를 렌더링하면, then 기존 후보 카드 조회·오류 표면은 보존되고 새 요약만 생략된다.
- Given desktop 또는 mobile viewport일 때, when 인증 대시보드를 확인하면, then 요약 카드는 각각 3열 또는 단일열로 읽을 수 있고 종목명·ticker·일간 거래대금이 표시된다.

## Design Notes

상위 영역은 필터 결과가 아닌 “오늘 태깅된 전체 후보”의 참고 순위다. 따라서 사용자가 전략·수급·시그널 필터를 선택해도 상단 3개는 바뀌지 않는다. 거래대금은 별도 실시간 조회가 아니라 후보 모집단에 저장된 동일 실행의 값이며, 화면에는 원 단위 숫자를 한국어 숫자 형식으로 표시해 단위 변환 오해를 피한다.

## Verification

**Commands:**
- `npm test -- --runInBand` in `apps/web` -- expected: web unit tests pass.
- `npm run typecheck` in `apps/web` -- expected: TypeScript contracts pass.
- `npm run build` in `apps/web` -- expected: production build succeeds.
- `uv run --with pytest pytest tests/domain/test_candidate_selection.py -q` -- expected: existing trading_value ordering contract passes.
- `git diff --check` -- expected: no whitespace errors.
- `python tools/check_migration_order.py` -- expected: migration order check passes or any pre-existing repository issue is reported separately.
- `npm run test:e2e -- e2e/authenticated-dashboard.spec.ts` in `apps/web` -- expected: authenticated dashboard surface includes the new summary.

## Review Triage Log

### 2026-09-30 — Review pass

- intent_gap: 0
- bad_spec: 0
- patch: 4 (medium 4)
- defer: 1 (low 1)
- dismissed:
  - 이 작업은 전략 신호를 추가하는 것이 아니라 기존 active 태깅 후보를 참고용으로 정렬하는 기능이다. 별도 전략 조건을 도입하지 않았다.
  - 운영 migration parity 전체 검사는 기존 migration drift와 중복 timestamp가 있어 이 작업의 acceptance blocker로 분류하지 않았다. 신규 함수·grant·fixture는 별도로 검증했다.
  - ticker ASC 정렬의 DB/JS collation 차이는 시장 ticker가 고정 6자리 코드라는 전제에서 재현 가능한 문제로 확인되지 않아 유지 finding으로 남기지 않았다.
- addressed_findings:
  - `[medium][patch]` 상단 카드의 종목명이 기존 `조정후보` heading과 충돌하던 문제를 일반 텍스트 요소로 변경하고 E2E count assertion으로 고정했다.
  - `[medium][patch]` 상단 전용 RPC의 transport 예외가 기존 후보 목록을 가리던 문제를 독립 `try/catch` 오류 경계로 수정했다.
  - `[medium][patch]` RPC SQL의 run lineage·signal date 누락 및 이름/거래대금 입력 검증 취약점을 같은 lineage/date 조건과 안전한 숫자·이름 fallback으로 보강했다.
  - `[medium][patch]` E2E에 top 3·동률·top RPC 오류·complete 빈 상태·기존 후보 필터와의 독립성 검증을 추가했다.
- follow-up review recommendation: true (medium 4, score 12; 재검토 권고는 후속 작업 큐에 기록하되 현재 패치에서 발견된 항목은 모두 addressed 상태다).

## Suggested Review Order

**데이터 경계와 lineage**

- complete snapshot의 published run과 trading_day를 SQL에서 함께 고정한다.
  [`202609301000_create_get_top_tagged_candidates.sql:8`](../../infra/supabase/migrations/202609301000_create_get_top_tagged_candidates.sql#L8)

- active 태그만 존재하는 후보를 거래대금·ticker 순으로 제한한다.
  [`202609301000_create_get_top_tagged_candidates.sql:28`](../../infra/supabase/migrations/202609301000_create_get_top_tagged_candidates.sql#L28)

**서버 렌더링과 오류 경계**

- 카드 RPC와 상단 요약 RPC의 실패 경계를 분리해 기존 화면을 보존한다.
  [`page.tsx:72`](../../apps/web/app/page.tsx#L72)

- 동일 lineage의 유효 행만 화면 모델로 변환한다.
  [`top-trading-candidates.ts:47`](../../apps/web/lib/top-trading-candidates.ts#L47)

**표면과 반응형 표시**

- 상단 순위 카드에 종목명·ticker·원 단위 거래대금을 표시한다.
  [`TopTradingCandidates.tsx:8`](../../apps/web/components/dashboard/TopTradingCandidates.tsx#L8)

- 데스크톱 3열과 모바일 단일열 레이아웃을 정의한다.
  [`globals.css:1177`](../../apps/web/app/globals.css#L1177)

**회귀 검증**

- 상위 3개·동률·빈 상태·lineage 필터를 순수 함수로 검증한다.
  [`top-trading-candidates.test.ts:40`](../../apps/web/lib/top-trading-candidates.test.ts#L40)

- active/vanished-only와 SQL 정렬 계약을 fixture로 검증한다.
  [`test_get_top_tagged_candidates.sql:52`](../../tests/sql/test_get_top_tagged_candidates.sql#L52)

- 인증 화면의 요약 표시와 오류 경계를 Playwright 시나리오로 검증한다.
  [`authenticated-dashboard.spec.ts:34`](../../e2e/authenticated-dashboard.spec.ts#L34)

## Auto Run Result

### Summary

오늘의 active 태깅 후보 중 일간 거래대금 상위 3개를 기존 후보 목록과 독립적인 참고 영역으로 표시한다. 후보 목록의 필터를 바꿔도 상단 요약은 유지되며, 전용 RPC 실패나 빈 결과는 기존 대시보드 화면을 가리지 않는다.

### Files changed

- `infra/supabase/migrations/202609301000_create_get_top_tagged_candidates.sql`
- `apps/web/app/page.tsx`
- `apps/web/components/dashboard/TopTradingCandidates.tsx`
- `apps/web/lib/dashboard-types.ts`
- `apps/web/lib/top-trading-candidates.ts`
- `apps/web/lib/top-trading-candidates.test.ts`
- `apps/web/app/globals.css`
- `e2e/authenticated-dashboard.spec.ts`
- `e2e/candidate-surface-scenarios.spec.ts`
- `e2e/mock-supabase-server.mjs`
- `tests/sql/test_get_top_tagged_candidates.sql`

### Verification

- 웹 단위 테스트: 145 passed
- `npm run typecheck`: passed
- `npm run build`: passed
- Python candidate ordering regression: 13 passed
- `git diff --check`: passed
- Playwright MCP 수동 검증: top 3, 동률 정렬, 필터 독립성, top RPC 오류, complete 빈 상태, desktop 3열/mobile 1열 확인
- 운영 Supabase에서 신규 RPC 존재·권한·migration 기록을 확인하고 SQL fixture를 rollback 경계로 실행
- `python tools/check_migration_order.py`: 기존 `202609161200` 중복 timestamp로 실패; 신규 변경과 무관한 기존 repository issue
- production parity gate: 기존 migration drift 10건과 warning 11건이 남아 있어 전체 parity pass로 주장하지 않음

### Delivery

- 기준 구현 commit: `774e24ca28370ffb64e6b341ee940e49b5df6989`
- review patch는 최종 검증 후 별도 commit으로 기록한다.
- 웹 push/Vercel 배포는 명시 요청 범위가 아니므로 수행하지 않았다.
