---
title: '종목 카드 오늘의 테마 실제 값 표시'
type: 'feature'
created: '2026-10-02'
status: 'done'
review_loop_iteration: 1
baseline_commit: '75ba813113100dd59355727fe7aa599b3db52799'
context: []
---

<frozen-after-approval reason="human-owned intent — do not modify unless human renegotiates">

## Intent

**Problem:** 오늘의 후보 카드와 거래대금 상위 참고 카드가 종목의 오늘 테마를 보여주지 못하고 `미확인`으로 표시한다. 현재 단일 `major_sector_name` 컬럼은 실제 원천과 연결되지 않았고, 종목별 다중 테마를 수집·저장하는 경로가 없다.

**Approach:** LS `t1532`의 종목별 테마 `tmname`/`tmcode`/`avgdiff`를 배치에서 조회해 후보 attempt에 다중 테마 스냅샷으로 저장하고, 일반 후보 카드와 거래대금 상위 참고 카드에 테마명과 테마 평균등락률을 전달한다. 개별 조회 실패는 후보 발행을 막지 않되 실패 후보는 `미확인`으로 남기며, 현재 published 후보는 별도 백필로 채운다.

## Boundaries & Constraints

**Always:** 테마는 브라우저가 아니라 배치 서버가 조회한다. 후보 attempt에 테마명·코드·평균등락률을 복사해 저장해 과거 카드가 현재 테마 변경에 따라 바뀌지 않게 한다. 응답에 유효한 테마가 없거나 조회가 실패하면 임의의 테마명을 만들지 않고 null을 유지한다. 카드에는 너무 많은 테마를 그대로 노출하지 않고 강세순 상위 테마와 나머지 개수를 일관되게 표시한다. 기존 후보·태그·수급 발행 계약과 테마 실패 격리 정책을 보존한다.

**Never:** `t3320`의 업종구분명을 테마명으로 사용하지 않는다. 카드 렌더 시 외부 LS API를 호출하지 않는다. 테마 수집 실패 때문에 후보 전체나 tags/publish를 실패시키지 않는다.

## I/O & Edge-Case Matrix

| Scenario | Input / State | Expected Output / Behavior | Error Handling |
|----------|--------------|---------------------------|----------------|
| HAPPY_PATH | `t1532`가 여러 `tmname`/`tmcode`/`avgdiff` 반환 | 후보 카드에 강세순 테마명과 등락률 표시 | N/A |
| EMPTY_SOURCE | 응답 배열이 비었거나 유효 테마 없음 | 테마 영역 `미확인` 표시 | 후보 발행 유지, 결과에 미수집 수 기록 |
| API_FAILURE | 후보 하나의 t1532 오류/timeout | 다른 후보는 계속 처리하고 해당 후보만 null | 후보 stage 실패로 전환하지 않음 |
| CURRENT_SNAPSHOT | 기존 published 후보에 테마 행이 없음 | 현재 카드 후보도 백필 후 실제 테마 표시 | 백필 실패 후보만 미확인 유지 |

</frozen-after-approval>

## Code Map

- `docs/api/ls-openapi/03-domestic-stock/sector.md:119-205` -- t1532 요청과 `tmname`/`tmcode`/`avgdiff` 응답 계약.
- `apps/batch/ls_client.py:20-48` -- TR별 REST path와 직렬/rate-limit 호출 경계; t1532 path를 추가한다.
- `apps/batch/candidate_stage.py:128-160,322-379` -- 후보 선택 직후 저장 payload를 만드는 지점; 테마 enrichment를 실패 격리로 삽입한다.
- `packages/domain/domain/candidate_selection.py:34-44` -- 후보 기본 payload 계약; 기존 선택·정렬 의미를 변경하지 않는다.
- `infra/supabase/migrations/202609011700_create_candidates.sql:5-25` -- 후보 attempt 합성키; 다중 테마 스냅샷 테이블의 FK 기준.
- `infra/supabase/migrations/202609301200_expand_top_trading_candidate_details.sql:6-96` -- 기존 단일 섹터 fallback과 top RPC; 새 테마 응답으로 대체·호환한다.
- `apps/web/lib/dashboard-types.ts:201-228`, `apps/web/lib/candidate-cards.ts:17-75` -- 일반 카드 RPC shape guard와 view model 확장 지점.
- `apps/web/components/dashboard/CandidateCard.tsx:57-92`, `apps/web/components/dashboard/TopTradingCandidates.tsx:28-46` -- 두 카드의 종목정보/지표 표시 위치.
- `e2e/candidate-surface-scenarios.spec.ts`, `e2e/authenticated-dashboard.spec.ts` -- 일반 카드와 상단 카드의 fixture 기반 브라우저 검증.

## Tasks & Acceptance

**Execution:**
- [x] `apps/batch/theme_enrichment.py`, `apps/batch/candidate_stage.py`, `apps/batch/ls_client.py` -- t1532 응답 파서와 후보별 격리 수집을 추가하고 후보 테마 payload를 만든다.
- [x] `infra/supabase/migrations/202610020900_persist_candidate_themes_and_candidate_card.sql` -- attempt-scoped `candidate_themes` 테이블과 write/read RPC의 테마 저장·반환을 추가한다.
- [x] `apps/web/lib/dashboard-types.ts`, `apps/web/lib/candidate-cards.ts`, `apps/web/components/dashboard/CandidateCard.tsx`, `apps/web/components/dashboard/TopTradingCandidates.tsx` -- 두 카드에 강세순 테마와 등락률을 전달·표시한다.
- [x] `tools/backfill_candidate_themes.py`와 관련 테스트 -- 현재 published attempt의 기존 후보를 t1532로 백필하고 재실행 가능한 결과를 남긴다.
- [x] `tests/batch/*`, `tests/sql/*`, `apps/web/lib/*test.ts`, `e2e/*` -- 정상/결측/부분실패, 다중 테마 정렬, `미확인` fallback을 회귀 검증한다.

**Acceptance Criteria:**
- Given 후보의 t1532 응답에 여러 테마가 있을 때, when 배치가 후보를 저장하면, then 두 카드 surface가 `avgdiff` 내림차순 테마명과 등락률을 표시한다.
- Given 일부 후보의 테마 API가 실패할 때, when 배치가 완료되면, then 성공 후보는 테마를 갖고 실패 후보만 `미확인`이며 후보/tag/publish는 정상 진행된다.
- Given 현재 published 후보에 테마 행이 없을 때, when 백필을 실행하면, then 성공한 후보의 attempt-scoped 테마 행이 채워지고 카드 RPC가 이를 반환한다.
- Given 카드 RPC가 빈 테마 배열을 반환할 때, when 화면을 렌더링하면, then `테마` 라벨은 유지되고 값만 `미확인`으로 표시된다.

## Spec Change Log

## Review Triage Log

- `PATCHED` -- FK에 `ON DELETE CASCADE`가 없어 후보 purge 뒤 고아 테마가 남을 수 있다는 지적을 반영했다. 초기 migration과 forward hardening migration 모두에 cascade를 적용하고 purge SQL 테스트를 운영 DB에서 통과시켰다.
- `PATCHED` -- 백필이 기존 테마를 삭제 후 재생성해 역사 스냅샷을 변경하거나 삭제 중 유실할 수 있다는 지적을 반영했다. 기존 행이 있는 후보는 건너뛰고, insert는 `ignore-duplicates`로 멱등 처리한다.
- `PATCHED` -- 명시적 `--run-id`가 과거/비발행 attempt를 가리킬 수 있다는 지적을 반영했다. published 상태와 `logical_runs.current_complete_run_id`를 모두 검증한다.
- `PATCHED` -- malformed t1532 성공 응답을 빈 응답으로 오인할 수 있다는 지적을 반영했다. 응답 형식을 엄격히 판정하고 해당 후보만 failed 집계한다.
- `PATCHED` -- 장시간 t1532 순차 조회 중 lease가 만료될 수 있다는 지적을 반영했다. 10건마다 후보 stage heartbeat를 시도하며 heartbeat 자체 실패는 보조 기능으로 격리한다.
- `PATCHED` -- 비문자열 `tmcode`/`tmname`, malformed 후보 REST row를 묵인할 수 있다는 지적을 반영했다. 두 경계 모두 명시적 오류로 처리한다.
- `PATCHED` -- 백필 실패가 프로세스 종료 코드에 반영되지 않는다는 지적을 반영했다. 하나라도 t1532 조회 실패가 있으면 exit code 2를 반환한다.
- `PATCHED` -- 상단 카드의 테마 표시 개수가 별도 숫자로 고정될 수 있다는 지적을 반영했다. 공통 `MAX_VISIBLE_THEMES`를 사용한다.
- `PATCHED` -- scheduler가 theme client를 candidate stage까지 전달하는지 직접 검증할 수 없다는 지적을 반영했다. 전달 assertion 테스트를 추가했다.
- `PATCHED` -- t1532 REST path, 후보별 부분 실패, 3개 초과 테마 표시, 백필 기존 행 보존에 대한 검증 공백을 각각 테스트로 보완했다.
- `DISMISSED` -- `collected_at`을 카드에 노출하지 않는다는 지적은 현재 frozen intent와 acceptance에 없는 운영 메타데이터 요구사항이다.
- `DISMISSED` -- 실패한 ticker별 상세 목록/RPC 하위 호환 fallback/RLS 전용 테스트/별도 백필 workflow 지적은 현재 acceptance 범위를 넓히지 않으며, aggregate stage metadata와 운영 수동 backfill 계약으로 충분하다.
- `DEFERRED` -- 기존 generated `database.types.ts`의 테마 타입 재생성은 현재 코드 경로가 신규 테이블 타입을 직접 import하지 않고 migration/RPC 계약으로 동작하므로 별도 타입 생성 작업으로 남긴다.
- `PATCHED` -- HTTP 200이지만 LS `rsp_cd`가 오류이거나 테마 행이 malformed인 응답을 빈 정상 응답으로 처리하지 않고 후보별 failed로 집계한다.
- `PATCHED` -- 테마 조회 heartbeat를 호출 횟수 고정 방식에서 기존 시간 기반 `LeaseHeartbeat` 정책으로 연결하고 연속 실패 한도를 적용했다.
- `PATCHED` -- 백필은 기본 snapshot 경로도 current complete 검증을 수행하며, 각 insert 직전 lineage를 재검증하고 한 후보의 REST write 실패는 다음 후보로 격리한다.
- `PATCHED` -- 카드 RPC SQL fixture에 theme code·평균등락률·빈 배열 fallback과 purge cascade 검증을 추가했다.
- `PATCHED` -- 브라우저 mock이 카드 RPC의 `p_run_id`를 검증하고, 일반 카드의 상위 3개와 `+N`, scheduler publish 지속을 E2E/통합 테스트로 보완했다.
- `DISMISSED` -- malformed 테마 배열 하나 때문에 전체 RPC 결과를 행 단위 정규화하자는 지적은 RPC shape 계약을 위반한 서버 응답을 전체 read-model 오류로 처리하는 기존 경계 정책과 일관되므로 현재 범위에서는 적용하지 않는다.
- `DISMISSED` -- 동일 `tmcode`의 상충 응답을 별도 오류로 만들자는 지적은 LS 응답의 중복 행을 현재 코드의 명시적 마지막 행 결정 규칙으로 정규화하고, 테마 수집 실패 격리 범위를 불필요하게 넓히지 않기 위해 적용하지 않는다.

## Suggested Review Order

**배치 수집과 스냅샷 보존**

- 후보별 t1532 결과를 실패 격리·강세순 테마 스냅샷으로 정규화한다.
  [`theme_enrichment.py:79`](../../apps/batch/theme_enrichment.py#L79)

- 후보 저장 직전 lease를 갱신해 장시간 테마 조회 중 attempt 소유권을 보호한다.
  [`candidate_stage.py:146`](../../apps/batch/candidate_stage.py#L146)

- 현재 published snapshot만 백필하고, 실행 중 lineage 변경과 개별 쓰기 실패를 방어한다.
  [`backfill_candidate_themes.py:59`](../../tools/backfill_candidate_themes.py#L59)

**데이터베이스 계약과 정리**

- attempt-scoped 테마 행과 카드 RPC 반환 shape를 함께 정의한다.
  [`202610020900_persist_candidate_themes_and_candidate_card.sql:5`](../../infra/supabase/migrations/202610020900_persist_candidate_themes_and_candidate_card.sql#L5)

- 이미 적용된 운영 FK에도 후보 purge cascade를 forward migration으로 보장한다.
  [`202610020930_harden_candidate_themes_retention.sql:5`](../../infra/supabase/migrations/202610020930_harden_candidate_themes_retention.sql#L5)

**화면 표시와 회귀 검증**

- 일반 후보 카드에서 상위 테마와 평균등락률, 미확인 fallback을 표시한다.
  [`CandidateCard.tsx:84`](../../apps/web/components/dashboard/CandidateCard.tsx#L84)

- 거래대금 상위 카드도 동일한 테마 표시 정책을 사용한다.
  [`TopTradingCandidates.tsx:39`](../../apps/web/components/dashboard/TopTradingCandidates.tsx#L39)

- provider 오류·malformed 응답이 후보 단위 실패로 격리되는지 확인한다.
  [`test_theme_enrichment.py:30`](../../tests/batch/test_theme_enrichment.py#L30)

- 후보 purge가 연결된 테마 스냅샷까지 정리하는지 운영 SQL fixture로 확인한다.
  [`test_purge_old_attempt_data.sql:42`](../../tests/sql/test_purge_old_attempt_data.sql#L42)

## Verification

**Commands:**
- `uv run --with pytest pytest tests/batch tests/domain` -- expected: theme parser/enrichment and existing batch contracts pass.
- `npm test -- --runInBand` in `apps/web` -- expected: card view-model and shape guard tests pass.
- `npx tsc --noEmit` in `apps/web` -- expected: no TypeScript errors.
- `npx playwright test e2e/candidate-surface-scenarios.spec.ts e2e/authenticated-dashboard.spec.ts` -- expected: fixture cards show actual sector and null fallback.

**Manual checks (if no CLI):**
- 운영 migration 적용 후 current complete snapshot의 카드에서 `미확인`이 실제 업종명으로 바뀌는지 확인하고, 백필 결과와 미수집 수를 별도로 기록한다.
