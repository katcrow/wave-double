---
title: '다중 전략 후보 카드 우선 정렬'
type: 'feature'
created: '2026-10-02'
status: 'done'
baseline_commit: 'c69486fc4c1cf4cd47dd14f336043c2f7bd8b894'
review_loop_iteration: 0
context: ['C:/dev/wave-double/AGENTS.md']
---

<!-- 이 스펙은 메인 태깅 후보 카드 목록의 정렬만 다룬다. -->

<frozen-after-approval reason="human-owned intent — do not modify unless human renegotiates">

## Intent

**Problem:** 메인 태깅 후보 카드가 현재 종목코드 순으로 반환되어, 여러 전략에 동시에 채택된 종목이 거래대금이 큰 단일 전략 종목보다 뒤에 표시될 수 있다.

**Approach:** 현재 `active` 전략 수를 1순위로, 후보의 일간 거래대금을 2순위로, 종목코드를 3순위로 사용해 `get_today_candidate_cards()`의 서버 반환 순서를 바꾼다. 현재 카드의 태그·수급·테마 데이터와 클라이언트 필터 동작은 유지한다.

## Boundaries & Constraints

**Always:** 전략 개수는 현재 attempt의 `candidate_tags.status = 'active'`인 서로 다른 전략만 센다. 정렬은 `active 전략 수 DESC`, `candidates.trading_value DESC`, `ticker ASC` 순서다. SQL을 단일 정렬 출처로 유지하고 attempt 범위·기존 카드 shape·vanished 전략 표시·테마 정렬을 보존한다.

**Never:** 상단의 별도 거래대금 참고 카드, 후보 선별·태깅 배치, 전략 계산, 필터 의미, 운영 migration을 수정하지 않는다. `vanished` 전략을 현재 다중 전략 우선순위에 포함하지 않는다. 기존 migration 파일은 수정하지 않고 UTC 시각 forward-only migration을 추가한다.

## I/O & Edge-Case Matrix

| Scenario | Input / State | Expected Output / Behavior | Error Handling |
|----------|--------------|---------------------------|----------------|
| MULTI_ACTIVE_FIRST | 후보 A는 active 전략 3개·거래대금 100억, 후보 B는 active 전략 1개·거래대금 500억 | A가 먼저 반환된다 | 정상 반환 |
| SAME_ACTIVE_COUNT | active 전략 수가 같은 후보들의 거래대금이 서로 다름 | 거래대금 DESC로 정렬한다 | 정상 반환 |
| TIE_BREAK | active 전략 수와 거래대금이 같은 후보 | ticker ASC로 결정한다 | 정상 반환 |
| VANISHED_ONLY | active 0개, vanished 전략만 존재하는 후보 | 기본 활성 목록에서는 기존 필터로 숨겨지고, 포함 필터에서는 우선순위 0으로 처리된다 | vanished를 active 개수에 포함하지 않음 |

</frozen-after-approval>

## Code Map

- `infra/supabase/migrations/202610020900_persist_candidate_themes_and_candidate_card.sql:146-222` -- 현재 `get_today_candidate_cards(uuid)`의 JSON 집계, active/vanished 전략 집계, attempt-scoped 후보 조인과 기존 ticker ASC 정렬. 신규 migration이 `create or replace function`으로 갱신할 직접 기준이다.
- `infra/supabase/migrations/202610011700_expand_strategy_l.sql` -- 현재 운영 migration의 최신 전략 범위와 forward-only migration 규약을 확인할 기준이다.
- `apps/web/lib/candidate-cards.ts:64-88` -- RPC 배열 순서를 재정렬하지 않고 view model으로 보존하는 클라이언트 경계. SQL 정렬 단일 출처를 유지한다.
- `apps/web/lib/dashboard-types.ts:198-216` -- `get_today_candidate_cards()` 반환 shape 타입. 응답 필드를 추가하지 않으므로 기존 타입을 유지한다.
- `apps/web/lib/candidate-filters.ts:149-163` -- 필터가 입력 순서를 보존하는 경계. 정렬을 클라이언트로 옮기지 않는다.
- `tests/sql/test_get_today_candidate_cards.sql` -- 카드 중복·태그 상태·수급 결측 SQL fixture. 다중 active 전략, 거래대금 역전, 동률 ticker tie-break를 추가한다.
- `apps/web/lib/candidate-cards.test.ts` -- 카드 view model이 RPC 입력 순서를 보존하는 순수 테스트. 정렬을 재구현하지 않는 계약을 보강한다.

## Tasks & Acceptance

**Execution:**
- [x] `infra/supabase/migrations/202610021100_sort_candidate_cards_by_strategy_count.sql` -- `get_today_candidate_cards()`를 forward-only로 갱신하고 active 전략 개수·거래대금·ticker 정렬을 적용한다 -- 운영 DB 함수와 로컬 migration 흐름을 일치시킨다.
- [x] `tests/sql/test_get_today_candidate_cards.sql` -- 다중 전략 우선, 거래대금 2순위, ticker tie-break 및 vanished 제외 fixture를 추가한다 -- SQL 정렬 계약을 실제 DB에서 검증한다.
- [x] `apps/web/lib/candidate-cards.test.ts` -- RPC 입력 순서가 view model에서 보존되는 회귀를 명시한다 -- 웹이 SQL 결과를 뒤집지 않음을 보장한다.
- [x] `apps/web` 관련 테스트와 Playwright 대시보드 시나리오 -- 정렬된 카드 순서가 화면에 표시되는지 확인한다 -- 실제 렌더링 경계를 검증한다.

**Acceptance Criteria:**
- Given 같은 후보 태깅 attempt에 active 전략 3개인 후보와 active 전략 1개인 후보가 있고 후자의 거래대금이 더 클 때, when 카드를 조회하면, then 전략 3개 후보가 먼저 표시된다.
- Given active 전략 수가 같은 후보들이 있을 때, when 카드를 조회하면, then 거래대금 DESC와 ticker ASC tie-break가 적용된다.
- Given vanished 전략만 있는 후보가 있을 때, when 정렬 기준을 계산하면, then vanished 전략은 active 전략 수에 포함되지 않는다.
- Given 기존 카드 데이터와 필터가 있을 때, when 대시보드를 렌더링하면, then 전략·수급·테마·필터·오류 경계가 기존과 동일하게 동작한다.

## Design Notes

정렬 우선순위의 예시는 다음과 같다.

| 후보 | active 전략 수 | 거래대금 | 순위 |
|---|---:|---:|---:|
| A | 3 | 100억 | 1 |
| B | 1 | 500억 | 2 |
| C | 1 | 300억 | 3 |

`get_today_candidate_cards()`는 화면에 거래대금 필드를 표시하지 않아도 SQL 내부의 `c.trading_value`로 정렬할 수 있다. 응답 shape를 불필요하게 확장하지 않아 기존 클라이언트 계약을 최소 변경으로 유지한다.

## Review Triage Log

- patch: SQL fixture가 후보 ticker를 중복 생성하고 같은 active 전략 수 후보의 거래대금을 모두 100으로 넣어 2순위 정렬을 검증하지 못하던 문제를 수정했다. active 3개 우선, 거래대금 DESC, ticker ASC tie-break, vanished 제외를 서로 구분하는 fixture로 보강했다.
- dismissed: `get_today_candidate_cards()`의 published/current-complete lineage guard를 추가하라는 지적은 기존 RPC 계약을 바꾸는 범위이며, 이 변경은 정렬만 수정한다. 호출자는 `get_dashboard_snapshot()`의 complete snapshot run_id를 전달하고 기존 attempt 범위를 유지한다.
- dismissed: SECURITY DEFINER search_path 지적은 기존 함수의 사전 상태이며 이번 변경으로 새로 발생한 동작이 아니다. 현재 migration은 기존 공개 권한과 함수 경계를 그대로 보존한다.
- dismissed: 클라이언트 단위 테스트와 Playwright mock이 SQL 정렬 자체를 증명하지 못한다는 지적은 맞지만, 두 테스트의 목적은 서버 반환 순서 보존과 화면 렌더링이며 SQL 정렬 계약은 보강한 Supabase fixture의 책임이다.
- dismissed: 필터 후 순서·attempt 격리 지적은 `filterCandidateItems()`가 기존 배열을 `filter`로만 축소하고 RPC SQL이 `where c.attempt_run_id = p_run_id`를 유지하므로 이번 정렬 변경으로 깨지지 않는다.
- deferred: 실제 운영 Supabase에 migration을 적용하고 SQL fixture를 실행하는 검증은 현재 세션에 Supabase MCP/로컬 PostgreSQL 도구가 없어 수행하지 못했다. 운영 반영 전 대상 프로젝트에서 migration·fixture·catalog/grant를 실행해야 한다.

## Verification

**Commands:**
- `npm test` in `apps/web` -- expected: 웹 단위 테스트 통과.
- `npm run typecheck` in `apps/web` -- expected: 타입 검사 통과.
- `npm run build` in `apps/web` -- expected: production build 통과.
- `git diff --check` -- expected: whitespace 오류 없음.
- `python tools/check_migration_order.py` -- expected: 신규 migration 순서 확인; 기존 repository 문제는 별도 보고.
- Supabase MCP로 migration 적용 및 `tests/sql/test_get_today_candidate_cards.sql` 실행 -- expected: 다중 전략/거래대금/ticker 정렬 fixture pass.
- Playwright MCP 대시보드 확인 -- expected: 메인 후보 카드가 다중 전략 우선 순서로 렌더링.

## Suggested Review Order

**서버 정렬 계약**

- active 전략 수를 계산하고 거래대금·ticker 순서로 JSON 배열을 만든다.
  [`202610021100_sort_candidate_cards_by_strategy_count.sql:4`](../../infra/supabase/migrations/202610021100_sort_candidate_cards_by_strategy_count.sql#L4)

- 기존 attempt 범위와 태그 상태별 카드 shape를 그대로 유지한다.
  [`202610021100_sort_candidate_cards_by_strategy_count.sql:36`](../../infra/supabase/migrations/202610021100_sort_candidate_cards_by_strategy_count.sql#L36)

**회귀 검증**

- 다중 전략 우선, 거래대금 DESC, ticker tie-break, vanished 제외를 함께 검증한다.
  [`test_get_today_candidate_cards.sql:94`](../../tests/sql/test_get_today_candidate_cards.sql#L94)

- 클라이언트가 서버가 정한 카드 순서를 변경하지 않음을 고정한다.
  [`candidate-cards.test.ts:160`](../../apps/web/lib/candidate-cards.test.ts#L160)

- 실제 브라우저에서 다중 전략 후보가 첫 카드로 렌더링되는지 확인한다.
  [`candidate-surface-scenarios.spec.ts:126`](../../e2e/candidate-surface-scenarios.spec.ts#L126)
