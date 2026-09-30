---
title: '거래대금 상위 후보의 태그 상태 독립 노출'
type: 'bugfix'
created: '2026-09-30'
status: 'done'
baseline_commit: 'b81c5885ae81970dfa8a6dc9d8be5600d65ba856'
review_loop_iteration: 0
context: ['C:/dev/wave-double/AGENTS.md']
---

<frozen-after-approval reason="human-owned intent — do not modify unless human renegotiates">

## Intent

**Problem:** 거래대금 상위 3개 영역이 `candidate_tags.status = 'active'`인 후보만 조회해, 오늘 후보가 태깅되지 않은 배치에서는 거래대금 상위 후보가 있어도 표시되지 않는다.

**Approach:** 기존 RPC의 complete snapshot lineage와 거래대금 정렬은 유지하고 active 태그 조인을 제거해, 같은 published run의 후보 모집단에서 거래대금 상위 3개를 반환한다. UI·fixture·E2E 문구와 기대값도 “태깅 후보”에서 일반 “후보” 기준으로 맞춘다.

## Boundaries & Constraints

**Always:** `current_complete_run_id`, `run_id`, `trading_day`가 일치하는 published snapshot만 사용한다. 거래대금 DESC, ticker ASC tie-breaker, 최대 3개, 유효 shape 검증, 기존 RPC 오류 경계는 유지한다. active·vanished·태그 없음 상태와 무관하게 candidates 행을 대상으로 한다.

**Never:** 후보 선별·태그 생성·배치 stage·기존 후보 카드 RPC의 동작을 변경하지 않는다. 다른 run, 다른 trading_day, 실시간 재조회 값을 섞지 않는다. 운영 DB에 적용된 migration을 수정하지 않고 forward-only migration으로 변경한다.

## I/O & Edge-Case Matrix

| Scenario | Input / State | Expected Output / Behavior | Error Handling |
|---|---|---|---|
| HAPPY_PATH | 같은 published run의 후보 4개, 태그 상태 혼합 | 거래대금 상위 3개 표시 | 정상 반환 |
| NO_ACTIVE_TAGS | 후보는 있으나 active 태그 0건 | 후보 거래대금 상위 3개 표시 | 빈 결과로 숨기지 않음 |
| VANISHED_OR_UNTAGGED | vanished 태그만 있거나 태그 행이 없음 | 해당 candidate도 거래대금 순위 대상 | 태그 상태로 제외하지 않음 |
| LINEAGE_MISMATCH | 다른 run/trading_day 후보가 함께 존재 | complete snapshot 행만 표시 | SQL lineage 조건으로 제외 |

</frozen-after-approval>

## Code Map

- `infra/supabase/migrations/202609301000_create_get_top_tagged_candidates.sql:6-49` -- 현재 RPC의 published lineage, candidate join, active 태그 EXISTS, 거래대금 정렬·LIMIT 기준. 기존 함수 시그니처를 유지한 forward-only replacement의 직접 대상이다.
- `infra/supabase/migrations/202609301100_include_all_candidates_in_top_trading.sql` -- active 태그 조건을 제거하고 candidates 모집단만 읽도록 운영 RPC를 갱신할 신규 migration 경로.
- `tests/sql/test_get_top_tagged_candidates.sql:5-122` -- 현재 active/vanished-only 배제 계약을 담은 SQL fixture. 태그 상태와 무관한 후보 노출·lineage fixture로 교체한다.
- `apps/web/app/page.tsx:75-97` -- complete snapshot의 run_id로 RPC를 호출하는 기존 독립 오류 경계. RPC 이름·호출 조건은 유지하고 회귀를 확인한다.
- `apps/web/components/dashboard/TopTradingCandidates.tsx:8-17` -- 빈 결과 숨김과 상단 제목/설명. “태깅 후보” 표현을 일반 후보 기준으로 변경한다.
- `e2e/mock-supabase-server.mjs:164-184`, `e2e/authenticated-dashboard.spec.ts:35-100`, `e2e/candidate-surface-scenarios.spec.ts:58-67` -- complete-vanish와 정상 화면의 상단 요약 mock/표면 기대값. active 태그 0건이어도 상단 요약이 표시되는 회귀를 고정한다.
- `apps/web/lib/top-trading-candidates.test.ts` -- 거래대금 정렬·lineage·shape 순수 함수 계약. 데이터 집합 의미 변경에도 기존 방어 검증을 유지한다.

## Tasks & Acceptance

**Execution:**
- [x] `infra/supabase/migrations/202609301100_include_all_candidates_in_top_trading.sql` -- 기존 RPC의 active 태그 EXISTS를 제거하고 candidate lineage 조건만 남긴다 -- 오늘 후보가 태깅 0건이어도 상위 순위를 반환한다.
- [x] `tests/sql/test_get_top_tagged_candidates.sql` -- active/vanished/무태그 후보와 lineage 불일치 fixture를 갱신한다 -- SQL이 태그 상태와 무관하게 정확히 3개를 반환함을 검증한다.
- [x] `apps/web/components/dashboard/TopTradingCandidates.tsx`, `apps/web/app/globals.css`, `apps/web/lib/dashboard-types.ts` -- 화면 문구와 주석을 일반 후보 기준으로 정리한다 -- 사용자에게 잘못된 태그 필터 의미를 전달하지 않는다.
- [x] `e2e/mock-supabase-server.mjs`, `e2e/authenticated-dashboard.spec.ts`, `e2e/candidate-surface-scenarios.spec.ts` -- active 태그 0건 시나리오에서 상단 3개를 검증한다 -- 운영 증상과 같은 회귀를 방지한다.

**Acceptance Criteria:**
- Given published complete snapshot에 후보가 있고 active 태그가 0건일 때, when 대시보드를 열면, then 거래대금 상위 후보가 최대 3개 표시된다.
- Given 후보들의 태그 상태가 active·vanished·없음으로 섞일 때, when RPC를 호출하면, then 태그 상태와 무관하게 거래대금 DESC/ticker ASC로 상위 3개를 반환한다.
- Given 다른 run 또는 trading_day 행이 존재할 때, when RPC를 호출하면, then 현재 complete snapshot의 행만 반환한다.
- Given 기존 top RPC가 오류 또는 malformed 응답일 때, when 대시보드를 렌더링하면, then 기존 후보 카드와 오류 경계는 유지되고 상단 영역만 생략된다.

## Spec Change Log

- 2026-09-30: 리뷰에서 완전 소멸 시나리오의 기존 카드 회귀 검증이 삭제된 점을 확인해, 상단 3개 검증과 카드·시그널 소멸 검증을 함께 유지하도록 보완했다.

## Review Triage Log

- patch: 완전 소멸 E2E가 기존 카드 검증을 잃지 않도록 소멸 필터 선택, 카드 표시, 시그널 상태, 카드 개수 assertion을 복원했다.
- dismissed: mock top RPC가 실제 태그 상태를 직접 표현하지 않는다는 지적은 SQL fixture가 DB 태그 상태를 검증하고 mock은 프론트 RPC 응답 경계를 검증하는 구조이므로 현재 변경의 결함이 아니다.
- dismissed: publish_attempt 경로와 null/non-published snapshot 추가 검증 지적은 읽기 RPC fixture의 기존 의도와 범위를 벗어나며, inner join lineage 계약은 유지된다.
- dismissed: truncated/numeric domain 지적은 이번 RPC 후보 집합 변경으로 새로 발생한 문제가 아니며 기존 후보 저장·shape guard 계약의 후속 범위다.
- dismissed: 일반 후보 표시 문구, snapshot 날짜 표시, 운영 RPC 함수명 변경 지적은 참고 순위·호환성 함수명이라는 승인된 의도와 충돌하거나 현재 사용자 요구에 필요하지 않다.
- deferred: 운영 migration 적용 및 live fixture 실행은 구현 단계의 remote operation 금지로 이 세션에서 수행하지 않았으며, 배포/운영 반영 단계에서 별도 확인한다.

## Design Notes

RPC 함수명 `get_top_tagged_candidates`는 이미 운영에 적용된 public 호출 계약이므로 이번 변경에서는 호환성을 위해 유지한다. 의미는 “태그된 후보”가 아니라 현재 complete snapshot 후보의 참고 순위로 좁혀 UI 명칭과 SQL comment를 함께 정정한다.

## Verification

**Commands:**
- `npm test -- --runInBand` in `apps/web` -- expected: 웹 단위 테스트 통과.
- `npm run typecheck` in `apps/web` -- expected: 타입 검사 통과.
- `npm run build` in `apps/web` -- expected: production build 통과.
- `git diff --check` -- expected: whitespace 오류 없음.
- `python tools/check_migration_order.py` -- expected: 신규 migration 순서 확인; 기존 repository 문제는 별도 보고.
- `npm run test:e2e -- e2e/authenticated-dashboard.spec.ts e2e/candidate-surface-scenarios.spec.ts` in `apps/web` -- expected: active 태그 0건 상단 요약 포함 표면 통과.
- 운영 Supabase SQL fixture -- expected: forward migration 적용 후 태그 상태 독립·lineage·정렬 계약 pass.

## Suggested Review Order

**운영 데이터 경계**

- active 태그 조건 없이 current complete snapshot 후보를 제한한다.
  [`202609301100_include_all_candidates_in_top_trading.sql:6`](../../infra/supabase/migrations/202609301100_include_all_candidates_in_top_trading.sql#L6)

- run 상태와 trading_day lineage를 유지해 다른 snapshot 혼입을 막는다.
  [`202609301100_include_all_candidates_in_top_trading.sql:28`](../../infra/supabase/migrations/202609301100_include_all_candidates_in_top_trading.sql#L28)

**화면 의미와 연결**

- 참고 순위가 태그 상태와 무관한 후보 모집단임을 화면에 명시한다.
  [`TopTradingCandidates.tsx:15`](../../apps/web/components/dashboard/TopTradingCandidates.tsx#L15)

- complete-vanish 시나리오에서도 카드와 거래대금 상위 3개를 함께 확인한다.
  [`candidate-surface-scenarios.spec.ts:58`](../../e2e/candidate-surface-scenarios.spec.ts#L58)

**회귀 fixture**

- 무태그·vanished·다른 거래일 후보의 포함/제외와 tie-break를 검증한다.
  [`test_get_top_tagged_candidates.sql:76`](../../tests/sql/test_get_top_tagged_candidates.sql#L76)

- 기존 오류 경계와 상단 제목 계약을 유지한다.
  [`authenticated-dashboard.spec.ts:35`](../../e2e/authenticated-dashboard.spec.ts#L35)
