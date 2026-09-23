---
title: '성과 검증 사후 결과 추적 종목명 표시 수정'
type: 'bugfix'
created: '2026-09-23'
status: 'in-review'
review_loop_iteration: 0
baseline_commit: '3f8da251a90d90409e91ba48544cf3a11299e406'
context: []
---

<frozen-after-approval reason="human-owned intent — do not modify unless human renegotiates">

## Intent

**Problem:** 성과 검증의 사후 결과 추적에서 종목코드는 표시되지만 종목명은 반환·렌더링 계약에 없어 사용자가 어떤 종목인지 바로 식별할 수 없다. 현재 RPC는 `candidate_outcome`의 ticker만 반환하고, 원천 `candidates`는 보존 기간 만료 시 정리될 수 있다.

**Approach:** outcome 생성 시 후보 종목명을 장기 보존 가능한 outcome projection과 OPEN 이벤트 payload에 스냅샷하고, 기존 결과는 현재 보존된 후보 데이터로 안전하게 보강한다. 추적 RPC와 브라우저 타입 검증에 nullable name을 추가한 뒤, 데스크톱 표와 모바일 카드에서 종목명과 종목코드를 함께 표시한다.

## Boundaries & Constraints

**Always:** 기존 ticker·전략·상태·정렬·필터·최대 500건 계약을 유지한다. 종목명이 없거나 공백이면 null로 두고 화면은 종목코드를 fallback으로 표시한다. outcome 이벤트와 projection의 append-only/SECURITY DEFINER/ACL 계약 및 기존 전략 범위를 보존한다. 기존 백테스트 변경은 건드리지 않는다.

**Never:** 브라우저가 `candidates` 또는 `candidate_outcome`을 직접 SELECT하도록 권한을 넓히지 않는다. 이미 적용된 migration을 수정하지 않는다. 종목명을 별도 실시간 외부 API 호출이나 클라이언트 재계산으로 표시하지 않는다.

## I/O & Edge-Case Matrix

| Scenario | Input / State | Expected Output / Behavior | Error Handling |
|----------|--------------|---------------------------|----------------|
| 이름 있는 신규 outcome | 후보 ticker/name과 OPEN 이벤트가 존재 | RPC row에 `name`과 `ticker`가 함께 반환되고 표·카드에 둘 다 표시 | N/A |
| 기존 outcome 보강 | projection name이 null이고 같은 logical run의 후보 name이 존재 | migration/backfill 후 name이 보존되어 표시 | N/A |
| 이름 없는/정리된 후보 | name이 null 또는 원천 후보가 없음 | RPC는 유효한 null name을 반환하고 화면은 ticker를 종목명 대체값으로 표시 | shape 검증 실패 없이 처리 |
| 이벤트 재생 | OPEN payload에 name이 있는 장부를 rebuild | 재구축 projection의 name이 유지됨 | payload 필수 기존 검증은 유지 |

</frozen-after-approval>

## Code Map

- `infra/supabase/migrations/202609031300_create_outcome_schema.sql` -- `candidate_outcome`의 현재 projection 구조와 ticker/전략 자연키를 정의하는 기준 migration; 직접 수정하지 않고 forward-only migration을 추가한다.
- `infra/supabase/migrations/202609151700_expand_strategy_gh.sql` -- 현재 운영 `emit_open_command`와 `get_outcome_tracking_rows` 본문; 신규 outcome name 스냅샷과 RPC 반환 필드를 이어 붙일 기준이다.
- `infra/supabase/migrations/202609051200_create_rebuild_outcome_projection.sql` -- outcome event replay로 projection을 재생성하는 `rebuild_outcome_projection`; OPEN payload의 name 보존을 반영해야 한다.
- `infra/supabase/migrations/202609141800_add_purge_old_attempt_data.sql` -- 7일 이후 candidates가 정리될 수 있음을 보여주는 운영 경계; name을 candidates에만 의존하지 않는다.
- `tests/sql/test_get_outcome_tracking_rows.sql` -- RPC 행 키·타입·정렬·필터·ACL fixture; name 반환과 null fallback 계약을 추가한다.
- `apps/web/lib/dashboard-types.ts` -- `OutcomeTrackingRpcRow` 브라우저 타입에 nullable `name`을 추가한다.
- `apps/web/lib/outcome-tracking.ts` -- RPC row shape validator의 허용 키와 타입을 갱신한다.
- `apps/web/components/tracking/OutcomeTrackingPanel.tsx` -- 표/반응형 카드에서 종목명과 ticker를 함께 렌더링하는 화면 경계다.
- `apps/web/lib/outcome-tracking.test.ts` -- name 포함/누락 row shape와 기존 포맷·집계 회귀를 검증한다.
- `e2e/mock-supabase-server.mjs`, `e2e/tracking.spec.ts` -- mock RPC 계약과 인증 화면에서 종목명·코드 동시 표시를 검증한다.

## Tasks & Acceptance

**Execution:**
- [x] `infra/supabase/migrations/YYYYMMDDHHMM_add_outcome_tracking_name.sql` -- `candidate_outcome.name`을 추가하고 신규 OPEN 이벤트·projection·rebuild에 name snapshot 및 기존 데이터 보강을 forward-only로 구현 -- purge 이후에도 이름을 유지한다.
- [x] `tests/sql/test_get_outcome_tracking_rows.sql` -- name 포함 행, null name, OPEN payload replay, 기존 필터/ACL을 검증 -- DB 반환 계약의 회귀를 막는다.
- [x] `apps/web/lib/dashboard-types.ts`, `apps/web/lib/outcome-tracking.ts` -- nullable name 타입과 정확한 RPC shape 검증을 추가 -- 서버 RPC 오류를 조기에 차단한다.
- [x] `apps/web/components/tracking/OutcomeTrackingPanel.tsx`, `apps/web/lib/outcome-tracking.test.ts` -- 표와 카드에 name/ticker를 표시하고 fallback 및 validator 테스트를 추가 -- 사용자가 종목을 식별할 수 있게 한다.
- [x] `e2e/mock-supabase-server.mjs`, `e2e/tracking.spec.ts` -- mock outcome rows에 name을 포함하고 대표 종목명·코드 표시를 검증 -- 기존 E2E가 새 RPC shape와 함께 회귀하지 않게 한다.

**Acceptance Criteria:**
- Given name이 있는 outcome, when 성과 검증을 열면, then 사후 결과 추적의 표와 카드에 종목명과 종목코드가 함께 보인다.
- Given name이 null인 outcome, when 추적 결과를 렌더링하면, then 기존 종목코드는 유지되고 종목명 누락 때문에 전체 섹션이 실패하지 않는다.
- Given outcome projection을 event replay로 재구축하면, when OPEN payload에 name이 있으면, then 재구축 후에도 같은 name이 유지된다.
- Given 기존 상태·전략·ticker 필터와 ACL fixture, when RPC를 호출하면, then 기존 결과와 보안 경계가 유지되면서 name 필드만 계약에 추가된다.

## Spec Change Log

## Review Triage Log

## Verification

**Commands:**
- `npm --prefix apps/web test -- --runInBand` -- expected: outcome-tracking 관련 테스트 성공
- `npm --prefix apps/web run typecheck` -- expected: TypeScript 타입 검사 성공
- `git diff --check` -- expected: 공백/패치 오류 없음
- Supabase MCP로 forward migration 적용 후 `tests/sql/test_get_outcome_tracking_rows.sql` fixture 실행 -- expected: name/재생/ACL assertion pass

**Manual checks (if no CLI):**
- Playwright MCP로 `/tracking`의 사후 결과 추적 표와 모바일 카드에서 종목명·코드가 함께 표시되는지 확인한다.

**Verification results:**
- 웹 단위 테스트 138건, typecheck, production build, `git diff --check` 통과.
- Playwright MCP에서 데스크톱 표와 375px 모바일 카드에 `삼성전자`와 `005930`이 함께 표시되고 콘솔 오류가 없음을 확인.
- 로컬 환경에 `supabase`/`psql`/Docker가 없어 SQL fixture와 운영 migration 적용은 실행하지 못함. `.env.local`은 운영 프로젝트 `qqhjeumlecaudsiqhhdu.supabase.co`를 가리키지만, 현재 세션에 Supabase MCP가 노출되지 않아 운영 DB에는 아직 적용하지 않음.
- `python tools/check_migration_order.py`는 이번 변경과 무관한 기존 동일 timestamp migration 2건 때문에 실패함: `202609161200_expand_candidate_tags_strategy_i.sql`, `202609161200_relabel_market_supply_columns_to_amount.sql`.
