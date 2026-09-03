---
title: '장중 시그널 유지·소멸 표시'
type: 'feature'
created: '2026-09-03'
status: 'done'
review_loop_iteration: 0
followup_review_recommended: true
baseline_revision: 'b84a72b578be7c30ffb65d3d1ce04328acae9fa9'
context:
  - '{project-root}/_bmad-output/implementation-artifacts/epic-2-context.md'
warnings: [oversized]
deferred:
  - summary: >-
      "장중 화면 라벨"(complete_snapshot.batch_kind !== 'close'일 때 "장중 참고 · 최종 추천
      미확정" 고정 표시) I/O 매트릭스 행에 자동화(e2e) 테스트가 없다.
    evidence: |-
      apps/web/app/page.tsx는 인증 보호된 async 서버 컴포넌트라 렌더 결과에 대한 단위 테스트가
      불가능하고, 이 저장소에는 인증된 세션을 발급하는 e2e 픽스처가 없다(Story 1.10부터
      e2e/manual-trigger.spec.ts, e2e/home.spec.ts, Story 2.7 spec Auto Run Result에서도 동일하게
      문서화된 저장소 전반의 기존 제약). 이번 스토리가 새로 만든 결함이 아니라 같은 제약이 새
      조건부 렌더에도 그대로 적용된 것이다. 나머지 6개 매트릭스 행(소멸 감지/모집단 이탈/수집
      실패/직전 attempt 없음/부분 재태깅/sync_vanished_tags 실패)은 모두 pytest·node --test·SQL
      fixture로 커버되고 실행·통과가 확인됐다.
    location: apps/web/app/page.tsx
    severity: low
---

<intent-contract>

## Intent

**Problem:** 이전 attempt(예: 09:30 장중 배치)에서 태깅됐던 종목이 이후 attempt(11:00)에서 재계산 결과 시그널을 잃으면, 후보 카드에서 조용히 사라진다 — 사용자는 이것이 "시그널 소멸"인지 "모집단 이탈"(조건검색 결과에서 빠짐)인지 "수집 실패"(Epic 1 부분성공)인지 구분할 수 없다. 또한 장중 화면에 "최종 추천 아님" 고정 라벨이 없다.

**Approach:** `candidate_tags.status`는 이미 `'vanished'`를 지원한다(Story 2.5, 아직 미사용). 신규 SQL 함수 `sync_vanished_tags(p_run_id)`가 tags stage 직후 실행되어, 같은 거래일 직전 attempt에서 `active`였던 (ticker, strategy)가 현재 attempt에서 재태깅되지 않았는데 ticker가 여전히 현재 `candidates`에 있으면 현재 attempt 소유 `candidate_tags` 행을 `status='vanished'`로 추가 삽입한다(과거 attempt 행은 불변 유지, append-only 원칙). `get_today_candidate_cards()`는 vanished 태그도 포함해 카드를 유지하고 `vanished_strategies`를 노출한다. ticker가 현재 `candidates`에 아예 없으면(모집단 이탈/수집 실패) 신규 `get_today_disappeared_candidates(p_run_id)`가 현재 attempt의 `runs.stage_status->>'candidates'` 값으로 두 원인을 구분해 반환한다. 프론트는 소멸 배지, 이탈/수집실패 목록, 장중 고정 라벨을 렌더링한다.

## Boundaries & Constraints

**Always:**
- `sync_vanished_tags(p_run_id uuid) returns jsonb`(security definer): `runs`/`logical_runs.trading_day`로 같은 거래일의 "직전 attempt"(started_at 기준 바로 이전, `stage_status->>'tags'` in `('success','partial')`)를 찾는다. 없으면 no-op(`{"vanished_count":0}`).
- 직전 attempt의 `active` 태그 중 (ticker, strategy)가 현재 attempt에 `active`로 없고, ticker가 현재 attempt `candidates`에 존재하면, 현재 attempt의 `candidate_id`로 `candidate_tags(status='vanished', signal_date=직전 signal_date, params_meta=직전 params_meta)`를 삽입한다(`on conflict (candidate_id, strategy, attempt_run_id) do nothing`). 과거 attempt 행은 절대 UPDATE하지 않는다.
- `apps/batch/tags_stage.py`: `tags_repo.upsert_tags()` 성공 후 `tags_repo.sync_vanished(run_id)` 호출. 실패해도 이미 저장된 active 태그는 유지하고, `error_count==0`이었다면 stage를 `partial`/`result_code="VANISHED_SYNC_FAILED"`로 기록한다(조용한 실패 금지). 성공/스킵 시 `result` payload에 `vanished_count`를 포함한다.
- `get_today_candidate_cards(p_run_id)`: `candidate_tags.status in ('active','vanished')`로 INNER JOIN 조건을 넓히고, `strategies`(active만, 기존 유지)와 신규 `vanished_strategies`(vanished만, 정렬)를 별도 배열로 반환한다. D0 dedupe 로직은 그대로 유지한다.
- `get_today_disappeared_candidates(p_run_id uuid) returns jsonb`(security definer, anon/authenticated/service_role grant): 같은 거래일 직전 attempt에서 `active`였던 ticker 중 현재 attempt `candidates`에 없는 것을 조회. `reason`은 현재 attempt `runs.stage_status->>'candidates' = 'success'`면 `'population_dropout'`, 그 외(`partial`/`failed`)면 `'collection_failure'`. `{ticker, name, reason, strategies}` 배열 반환.
- 프론트(`apps/web/lib/dashboard-types.ts`, `candidate-cards.ts`): `TodayCandidateCardRow`에 `vanished_strategies: string[]` 추가. `CandidateCardViewModel`에 `vanishedStrategies: string[]`/`isFullyVanished: boolean`(active 태그 0건 + vanished 태그 존재) 추가. 신규 `DisappearedCandidateRow`/`buildDisappearedCandidateViewModels()`.
- `CandidateCard.tsx`: `isFullyVanished`면 카드에 "소멸" 배지(예: `candidate-card--vanished` 클래스 + "시그널 소멸" 텍스트)를 표시하되 카드 자체는 목록에서 제외하지 않는다.
- 신규 컴포넌트(예: `DisappearedCandidatesNotice.tsx`): `get_today_disappeared_candidates` 결과를 ticker·사유 문구("모집단 이탈" / "수집 실패")로 렌더링. 카드 그리드와 별개 영역.
- `apps/web/app/page.tsx`: `complete_snapshot.batch_kind !== 'close'`이면 "장중 참고 · 최종 추천 미확정" 고정 라벨을 표시(UJ-2). `get_today_disappeared_candidates(complete_snapshot.run_id)`도 `get_today_candidate_cards`와 같은 조건(`complete_snapshot` 존재 시)으로 호출하고 실패 시 기존 `candidateCardsFetchFailed` 패턴과 동일하게 로깅 후 조용히 생략(신규 기능 실패가 기존 카드 렌더를 막지 않음).
- `apps/web/app/globals.css`: 소멸 배지, 이탈/수집실패 안내, 장중 라벨 스타일을 기존 토큰(`--color-caution`, `--color-ink-muted`, `.candidate-card__notice` 패턴)으로 추가.

**Never:**
- 당일 가격/등락률 표시(AC/컬럼 없음, 여전히 범위 밖)는 이번 스토리에서 구현하지 않는다.
- 과거 attempt의 `candidate_tags` 행을 UPDATE하지 않는다(append-only, AD-19 유지) — 소멸 표시는 항상 현재 attempt 소유 신규 행으로 기록한다.
- Epic 3 outcome 생성 자격 판정 로직은 만들지 않는다(`batch_kind` 노출만, 자격 판정은 Epic 3 범위).
- `candidates`/`runs`/`logical_runs` 기존 컬럼·제약을 변경하지 않는다(신규 함수만 추가).

## I/O & Edge-Case Matrix

| Scenario | Input / State | Expected Output / Behavior | Error Handling |
|----------|--------------|---------------------------|----------------|
| 소멸 감지 | 직전 attempt A전략 active, 현재 attempt 재태깅 안 됨, ticker는 현재 candidates에 존재 | 현재 attempt에 `status='vanished'` 태그 삽입, 카드에 "소멸" 표시로 유지 | No error expected |
| 모집단 이탈 | 직전 attempt active, ticker가 현재 attempt candidates에 없음, 현재 attempt candidates stage='success' | `get_today_disappeared_candidates`가 `reason='population_dropout'` 반환 | No error expected |
| 수집 실패 | 위와 동일하되 현재 attempt candidates stage='partial'/'failed' | `reason='collection_failure'` 반환 | No error expected |
| 직전 attempt 없음(당일 최초) | 같은 거래일 이전 attempt 없음 | `sync_vanished_tags`가 no-op(`vanished_count=0`), 소멸/이탈 없음 | No error expected |
| 부분 재태깅 | 후보가 A,B로 active였다가 A만 재태깅 | 카드에 `strategies=["A"]`, `vanished_strategies=["B"]` 둘 다 표시(카드는 정상 노출) | No error expected |
| 장중 화면 라벨 | `complete_snapshot.batch_kind='intraday'` | "장중 참고 · 최종 추천 미확정" 고정 표시 | No error expected |
| sync_vanished_tags 실패 | RPC 예외 발생, active 태깅은 이미 저장됨 | stage `partial`, `result_code='VANISHED_SYNC_FAILED'`, active 태그는 유실 없음 | 로깅 + stage 상태 반영 |

</intent-contract>

## Code Map

- `infra/supabase/migrations/202609021600_create_candidate_tags.sql` -- `status check (active, vanished)` 이미 존재(스키마 변경 불필요).
- `infra/supabase/migrations/202609011600_create_run_lineage.sql` -- `logical_runs.trading_day`(직접 컬럼), `runs.stage_status`(jsonb, `candidates`/`tags` 키), `runs.started_at` -- 직전 attempt 조회 기준.
- `infra/supabase/migrations/202609022200_fix_get_today_candidate_cards_d0_dedupe.sql` -- 현재 `get_today_candidate_cards` 최종본, `strategies`/D0 dedupe 로직 참고 및 교체 대상(신규 migration에서 `create or replace`).
- `apps/batch/tags_stage.py:173-225` -- `upsert_tags` 성공 직후 지점, `result_common`/stage 판정 로직 -- `sync_vanished` 호출 삽입 지점.
- `apps/batch/candidate_tags_repository.py` -- `SupabaseCandidateTagsRepository.upsert_tags()` 패턴(PostgREST 직접 호출) -- 신규 `sync_vanished(run_id)` 메서드가 `/rest/v1/rpc/sync_vanished_tags`를 동일 패턴으로 호출.
- `apps/web/lib/dashboard-types.ts:86-92` -- `TodayCandidateCardRow` -- `vanished_strategies` 추가 지점.
- `apps/web/lib/candidate-cards.ts` -- `buildCandidateCardViewModels()` -- `vanishedStrategies`/`isFullyVanished` 계산 추가.
- `apps/web/components/dashboard/CandidateCard.tsx:6-7` -- "장중 소멸 표시(Story 2.8)는 범위 아니다" 주석이 있던 지점, 이번 스토리의 실제 구현 지점.
- `apps/web/app/page.tsx:35-48` -- `get_today_candidate_cards` 호출부 패턴(complete_snapshot 조건, 실패 로깅) -- `get_today_disappeared_candidates` 호출과 장중 라벨 조건 추가 지점.
- `apps/web/app/globals.css:330-416` -- `.candidate-card`/`.candidate-card__notice`/`.strategy-tag` 기존 스타일 -- 신규 클래스가 참고할 토큰/패턴.
- `tests/batch/test_tags_stage.py`, `tests/batch/test_candidate_tags_repository.py` -- `FakeTagsRepository`/`FakeRpc` 패턴 -- 신규 테스트가 따를 구조.
- `tests/sql/test_get_today_candidate_cards.sql`, `.github/workflows/test.yml:108` -- SQL 테스트 등록 목록(`sql-outbox-tests`) -- 신규 파일 추가 지점.
- `apps/web/lib/candidate-cards.test.ts` -- `row()` 픽스처 헬퍼 패턴 -- 확장 테스트가 따를 구조.

## Tasks & Acceptance

**Execution:**
- `infra/supabase/migrations/202609031000_create_sync_vanished_tags.sql` -- `sync_vanished_tags(p_run_id uuid)` 함수 생성(security definer, service_role만 grant) -- 소멸 감지·삽입.
- `infra/supabase/migrations/202609031100_add_vanished_strategies_to_get_today_candidate_cards.sql` -- `get_today_candidate_cards` 본문 교체(`status in ('active','vanished')` JOIN, `vanished_strategies` 추가) -- 카드에 소멸 노출.
- `infra/supabase/migrations/202609031200_create_get_today_disappeared_candidates.sql` -- `get_today_disappeared_candidates(p_run_id uuid)` 생성(anon/authenticated/service_role grant) -- 이탈/수집실패 구분 조회.
- `tests/sql/test_sync_vanished_tags.sql` -- 소멸 삽입/직전attempt없음/이미소멸 재실행 idempotency 시나리오 -- 회귀 방지, `.github/workflows/test.yml` `sql-outbox-tests`에 등록.
- `tests/sql/test_get_today_disappeared_candidates.sql` -- population_dropout/collection_failure 분기 시나리오 -- 회귀 방지, 동일 워크플로에 등록.
- 기존 `tests/sql/test_get_today_candidate_cards.sql` 확장 -- `vanished_strategies` 필드 검증 케이스 추가.
- `apps/batch/candidate_tags_repository.py` -- `TagsRepositoryProtocol`/`SupabaseCandidateTagsRepository`에 `sync_vanished(run_id: str) -> dict` 추가.
- `apps/batch/tags_stage.py` -- `upsert_tags` 성공 후 `sync_vanished` 호출, 실패 시 `partial`/`VANISHED_SYNC_FAILED` 처리, `TagsStageResult`에 `vanished_count` 추가.
- `tests/batch/test_tags_stage.py`, `tests/batch/test_candidate_tags_repository.py` -- I/O 매트릭스의 소멸 성공/실패/직전attempt없음 케이스 -- 회귀 방지.
- `apps/web/lib/dashboard-types.ts` -- `TodayCandidateCardRow.vanished_strategies`, 신규 `DisappearedCandidateRow` 타입 추가.
- `apps/web/lib/candidate-cards.ts` -- `vanishedStrategies`/`isFullyVanished` 계산, 신규 `buildDisappearedCandidateViewModels()`.
- `apps/web/lib/candidate-cards.test.ts` -- 부분 재태깅/완전 소멸 케이스 추가.
- `apps/web/lib/disappeared-candidates.test.ts` -- 신규, 이탈/수집실패 뷰모델 유닛 테스트.
- `apps/web/components/dashboard/CandidateCard.tsx` -- 소멸 배지 렌더.
- `apps/web/components/dashboard/DisappearedCandidatesNotice.tsx` -- 신규, 이탈/수집실패 목록 렌더.
- `apps/web/app/page.tsx` -- 장중 고정 라벨, `get_today_disappeared_candidates` 호출 및 렌더 통합.
- `apps/web/app/globals.css` -- 소멸 배지/이탈-실패 안내/장중 라벨 스타일 추가.

**Acceptance Criteria:**
- Given 09:30 배치에서 태깅된 종목이 11:00 배치에서 재태깅되지 않고 여전히 후보 모집단에 있는 경우, when tags stage가 완료되면, then 해당 태그가 `vanished`로 기록되고 카드가 "소멸" 표시로 목록에 남는다(사라지지 않음).
- Given 종목이 소멸/모집단 이탈/수집 실패 중 하나로 목록에서 빠지는 경우, when 화면에 표시하면, then 세 상태가 서로 다른 문구/배지로 구분된다.
- Given `candidate_tags`를 `run_id`/`tagged_at` 단위로 조회하는 경우, when 당일 여러 attempt를 비교하면, then 언제 태깅됐고 언제 소멸했는지 추적 가능하다.
- Given 장중 배치(`batch_kind != 'close'`)로 만들어진 `complete_snapshot`인 경우, when `/`에 접속하면, then "장중 참고 · 최종 추천 미확정"이 고정 표시된다.

## Spec Change Log

## Review Triage Log

### 2026-09-03 — Review pass
- intent_gap: 0
- bad_spec: 0
- patch: 5 (high 0, medium 0, low 5)
- defer: 0
- dismissed:
  - `sync_vanished_tags`가 `on conflict (candidate_id, strategy, attempt_run_id) do nothing`에 필요한 unique 제약이 없을 수 있다는 주장(blind-hunter) — `202609021600_create_candidate_tags.sql`에 정확히 그 3-컬럼 unique 제약이 이미 존재한다(Story 2.5).
  - `sync_vanished_tags`는 `RUN_NOT_FOUND`를 raise하고 `get_today_disappeared_candidates`는 같은 조건에서 조용히 `[]`를 반환해 두 신규 RPC의 실패 시맨틱이 다르다는 주장(blind-hunter + edge-case-hunter, 동일 근본원인) — 전자는 service_role 전용 내부 배치 RPC(잘못된 run_id는 배치 버그이므로 즉시 실패가 맞음)이고 후자는 anon/authenticated에 공개된 대시보드 RPC(오래된 캐시된 run_id로 페이지가 죽으면 안 되므로 graceful degrade가 맞음) — 역할이 다른 두 RPC의 의도된 설계 차이이지 결함이 아니다.
  - 전략이 A/B/C 3종뿐인데 `vanishedStrategies`/이탈 목록의 전략 배열에 `MAX_VISIBLE_TAGS` 같은 접힘 처리가 없다는 주장(blind-hunter) — Story 2.7 스펙이 이미 확정한 근거(전략 3종뿐이라 배지 폭 문제가 물리적으로 발생하지 않음)와 동일하게 적용되며, 이번 목록들은 배지가 아니라 줄바꿈 가능한 텍스트라 폭 제약 자체가 없다.
  - `sync_vanished_tags`가 `trading_day`만으로 직전 attempt를 찾아 intraday→close 전환 구간도 비교 대상에 포함시킨다는 주장(blind-hunter) — 에픽 목표("이전 배치에서 태깅되었으나 최신 배치에서 사라진 종목은 소멸 상태로 표시")가 batch_kind로 범위를 제한하지 않으며, Epic 3 outcome 자격 판정(Never 절에서 범위 밖으로 명시)에는 영향을 주지 않으므로 의도된 동작이다.
  - `get_today_disappeared_candidates`가 `stage_status->>'candidates'`의 `NULL`/누락 값을 테스트하지 않았다는 주장(blind-hunter) — `runs.stage_status`는 `run_stage_values` check 제약으로 5개 키 모두 `pending/running/success/failed/partial` 중 하나만 허용해 `NULL`이 스키마상 불가능하다.
  - `202609031100` 마이그레이션이 `create or replace`만 쓰고 grant를 재선언하지 않아 향후 리팩터링(drop+create로 변경 시) 시 권한이 조용히 사라질 수 있다는 주장(blind-hunter) — 현재 동작은 Postgres의 `CREATE OR REPLACE` 권한 보존 규칙상 정확하며, 실제 프로덕션에서 `pg_proc.proacl`로 anon/authenticated/service_role grant가 모두 정상 확인됨. 지적 자체도 "현재는 맞다"고 인정한 가상의 미래 리스크.
  - `DisappearedCandidatesNotice`가 `ticker`를 React key로 쓰는데 티커별 1행 보장이 TS 레이어에 문서화되지 않았다는 주장(blind-hunter) — SQL의 `group by c.ticker, c.name`이 이미 그 불변식을 강제하며, 현재 코드에서 위반 가능한 경로가 없다.
  - Python 유닛테스트(Fake repo)와 실제 Postgres RPC 간 통합 테스트가 없다는 주장(blind-hunter) — 이 저장소의 모든 기존 stage(2.1~2.7)가 동일하게 "유닛 테스트(Fake 의존성) + 별도 SQL fixture" 분리 패턴을 쓰며, 이번 스토리만의 새로운 공백이 아니다.
  - `CandidateCard`/`DisappearedCandidatesNotice`에 React Testing Library 수준의 렌더 테스트가 없다는 주장(blind-hunter) — 이 저장소에는 어떤 대시보드 컴포넌트에도 그런 렌더 테스트가 없다(전부 뷰모델 순수 함수 단위 테스트만 존재, Story 2.7과 동일 관례).
  - 스펙 Approach 문단이 "직전 attempt의 stage_status"라고 써서 Always 절("현재 attempt")과 스스로 모순된다는 주장(edge-case-hunter) — 실제 SQL 구현과 Always 절은 처음부터 올바르게 "현재 attempt"를 사용했고, Approach 문단의 단어 선택 오류일 뿐 코드에는 영향이 없다. 리뷰 루프 밖에서 스펙 문구만 직접 정정했다(코드 재생성 불필요).
  - `.github/workflows/test.yml`에 `sql-outbox-tests`라는 이름의 단계가 없다는 주장(edge-case-hunter) — `sql-outbox-tests:`는 job id(65번째 줄)이며 스펙의 Code Map 인용이 가리키는 것도 job id다. 그 안의 step 표시명("Run Epic 1 SQL fixtures")은 이번 스토리 이전부터 있던 것으로 무관하다.
  - `buildDisappearedCandidateViewModels()`가 스펙 Tasks에는 `candidate-cards.ts`에 추가한다고 적혀 있는데 실제로는 별도 파일 `disappeared-candidates.ts`에 구현됐다는 주장(edge-case-hunter, 낮은 확신) — 관심사 분리 관점에서 더 나은 구조이며 기능·테스트 커버리지에 차이가 없어 코드를 스펙에 맞춰 되돌릴 이유가 없는 사소한 스펙 서술 차이.
- addressed_findings:
  - `[low]` `[patch]` `CandidateCard.tsx`가 완전 소멸 카드에 "시그널 소멸" 배지와 "소멸: ..." 안내문을 동시에 렌더링해 정보가 중복됐다(blind-hunter) — 안내문을 `!isFullyVanished && vanishedStrategies.length > 0`(부분 재태깅 케이스 전용)일 때만 렌더링하도록 수정했다.
  - `[low]` `[patch]` `TagsStageResult`에 `vanished_sync_failed` 필드가 없어 DB에 저장된 JSON 결과(`result_common["vanished_sync_failed"]`)와 달리 타입화된 반환값만 보는 Python 호출자는 combined 실패(에러+소멸동기화 실패 동시 발생)를 감지할 수 없었다(blind-hunter) — `TagsStageResult.vanished_sync_failed: bool = False` 필드를 추가하고 두 실패 분기 모두에서 `True`로 설정, 테스트에 단언을 추가했다.
  - `[low]` `[patch]` `sync_vanished_tags` 실패 + `error_count==0`일 때 `unprocessed_count=0`으로 `partial` stage를 기록해, 대시보드 trust bar가 "부분성공 · 미처리 0건"이라는 자기모순적 문구를 표시했다(verification-gap, 스펙이 인용한 AD-5 "조용한 실패 금지" 취지를 이 경로에서 스스로 위반) — 해당 `write_stage` 호출의 `unprocessed_count`를 `0`에서 `1`로 바꿔 "부분성공 · 미처리 1건"으로 문구 모순을 해소하고 테스트에 단언을 추가했다.
  - `[low]` `[patch]` I/O 매트릭스 "장중 화면 라벨" 행의 판정 로직(`isIntradaySnapshot`)이 `page.tsx`에 인라인으로만 존재해 렌더링과 분리된 순수 로직조차 유닛 테스트가 전혀 없었다(blind-hunter) — `apps/web/lib/dashboard-types.ts`에 `isIntradaySnapshot()`을 추출해 `page.tsx`에서 import하도록 바꾸고, `dashboard-types.test.ts`를 신규 작성해 4개 케이스(close/intraday/premarket/스냅샷 없음)를 검증했다(렌더링 자체의 e2e 공백은 기존에 문서화된 저장소 전반의 제약으로 deferred 항목에 남겨둔다).
  - `[low]` `[patch]` `sync_vanished_tags`/`get_today_disappeared_candidates`가 같은 거래일의 실패한 중간 attempt를 건너뛰고 그 이전 성공/부분성공 attempt를 비교 대상으로 찾는 로직(`stage_status->>'tags' in ('success','partial')` 필터)이 새로 추가됐는데 이를 직접 검증하는 테스트 시나리오가 없었다(blind-hunter) — `tests/sql/test_sync_vanished_tags.sql`에 시나리오 6(attempt1 success → attempt2 failed → attempt3 현재)을 추가해 실패한 attempt2를 건너뛰고 attempt1을 올바르게 비교 대상으로 찾는 것을 검증했다.

## Design Notes

- **왜 과거 attempt를 UPDATE하지 않고 현재 attempt에 새 `vanished` 행을 삽입하는가**: `candidate_tags`의 FK는 `(candidate_id, attempt_run_id)`가 같은 attempt의 `candidates` 행을 가리켜야 한다. `candidate_id`는 attempt마다 새로 생성되므로(재사용 불가), 소멸 상태는 오직 "이 ticker가 여전히 존재하는 attempt"(현재 attempt) 소유 행으로만 표현 가능하다. 이는 이 저장소의 attempt-scoped append-only 원칙(AD-19)과도 일치한다.
- **모집단 이탈 vs 수집 실패 구분 근거**: ticker별 수집 실패 상세는 어느 테이블에도 저장되지 않는다(Epic 1은 `excluded_count`/`unprocessed_count` 등 집계치만 저장). 대신 현재 attempt의 `runs.stage_status->>'candidates'`가 `'success'`(완전 성공)면 이탈은 조건검색 결과 변화로 판정하고, `'partial'`/`'failed'`면 그 attempt의 후보 수집 자체가 불완전했으므로 보수적으로 `'collection_failure'`로 분류한다(AD-5 "조용한 누락 금지" — 애매하면 실패 쪽으로 표시).
- **직전 attempt 판정 범위를 "같은 거래일"로 제한하는 이유**: 다음 거래일 premarket 배치와 전일 close 배치는 서로 다른 모집단/시그널 문맥이라 비교 대상이 아니다(AC3 "당일 태깅 변화 추이"에 명시).

## Verification

**Commands:**
- `cd apps/web && node --test lib/**/*.test.ts` -- expected: 신규/확장 케이스 포함 전체 통과.
- `cd apps/web && npx tsc --noEmit` -- expected: clean.
- `python -m pytest tests/batch/test_tags_stage.py tests/batch/test_candidate_tags_repository.py` -- expected: 전체 통과.
- `git diff --check` -- expected: whitespace 오류 없음.

**Manual checks (if no CLI):**
- 신규 3개 migration을 운영 Supabase(qqhjeumlecaudsiqhhdu)에 적용 후, 같은 거래일에 attempt 2개(A: active 태그 포함, B: 그 중 하나 미태깅)를 시딩해 `sync_vanished_tags(B)` 실행 → `candidate_tags`에 `attempt_run_id=B`, `status='vanished'` 행 생성 확인. `get_today_candidate_cards(B)`가 해당 카드를 `vanished_strategies`와 함께 반환하는지, `get_today_disappeared_candidates(B)`가 이탈/실패 케이스를 올바른 `reason`으로 반환하는지 SQL로 직접 확인(롤백 트랜잭션 사용).

## Auto Run Result

- **구현 요약:** Story 2.8 "장중 시그널 유지·소멸 표시"를 구현했다. 신규 `sync_vanished_tags(p_run_id)` RPC가 tags stage 직후 실행되어 같은 거래일 직전 attempt에서 active였던 (ticker, strategy)가 현재 attempt에서 재태깅되지 않았지만 ticker가 여전히 현재 `candidates`에 있으면 현재 attempt 소유 `candidate_tags` 행을 `status='vanished'`로 추가 삽입한다(과거 attempt 행은 절대 UPDATE하지 않음, append-only). `get_today_candidate_cards()`는 vanished 태그가 있는 후보도 카드로 유지하며 `vanished_strategies`를 노출하고, 신규 `get_today_disappeared_candidates(p_run_id)`는 ticker가 현재 `candidates`에 아예 없는 경우(모집단 이탈/수집 실패)를 현재 attempt의 candidates stage 상태로 구분해 반환한다. 프론트는 소멸 배지, 부분 재태깅 안내, 모집단 이탈/수집 실패 목록, "장중 참고 · 최종 추천 미확정" 고정 라벨을 렌더링한다.
- **변경 파일(누적, 리뷰 패치 포함):**
  - `infra/supabase/migrations/202609031000_create_sync_vanished_tags.sql` — `sync_vanished_tags(p_run_id)` RPC(service_role 전용). 같은 거래일 직전 attempt(started_at 기준, tags stage success/partial)를 찾아 소멸 태그를 현재 attempt 소유로 삽입.
  - `infra/supabase/migrations/202609031100_add_vanished_strategies_to_get_today_candidate_cards.sql` — `get_today_candidate_cards()`가 `status in ('active','vanished')`로 조인 범위를 넓히고 `strategies`(active)/`vanished_strategies`(vanished)를 분리 반환하도록 교체(D0 dedupe 로직은 그대로 유지).
  - `infra/supabase/migrations/202609031200_create_get_today_disappeared_candidates.sql` — 모집단 자체에서 빠진 ticker를 `population_dropout`/`collection_failure`로 구분해 반환하는 신규 RPC(anon/authenticated/service_role grant).
  - `apps/batch/candidate_tags_repository.py` — `sync_vanished(run_id)` 메서드 추가(PostgREST RPC 호출).
  - `apps/batch/tags_stage.py` — `upsert_tags` 성공 후 `sync_vanished` 호출, 실패 시 `partial`/`VANISHED_SYNC_FAILED` 처리(리뷰 패치: `unprocessed_count=1`로 trust bar 문구 모순 해소, `TagsStageResult.vanished_sync_failed` 필드 추가).
  - `apps/web/lib/dashboard-types.ts` — `TodayCandidateCardRow.vanished_strategies`, 신규 `DisappearedCandidateRow`/`DisappearedReason`, 리뷰 패치로 신규 `isIntradaySnapshot()` 순수 함수 추출.
  - `apps/web/lib/candidate-cards.ts` — `vanishedStrategies`/`isFullyVanished` 계산 추가.
  - `apps/web/lib/disappeared-candidates.ts`(신규) — `buildDisappearedCandidateViewModels()`, `DISAPPEARED_REASON_LABEL`("모집단 이탈"/"수집 실패").
  - `apps/web/components/dashboard/CandidateCard.tsx` — "시그널 소멸" 배지(완전 소멸), 소멸 전략 안내문(부분 재태깅 전용, 리뷰 패치로 완전 소멸과 중복 렌더 제거).
  - `apps/web/components/dashboard/DisappearedCandidatesNotice.tsx`(신규) — 모집단 이탈/수집 실패 목록 렌더.
  - `apps/web/app/page.tsx` — 장중 고정 라벨(`isIntradaySnapshot` 사용), `get_today_disappeared_candidates` 호출 및 렌더 통합.
  - `apps/web/app/globals.css` — 소멸 배지/이탈-실패 안내/장중 라벨 스타일 추가.
  - 테스트: `tests/sql/test_sync_vanished_tags.sql`(신규, 시나리오 6개), `tests/sql/test_get_today_disappeared_candidates.sql`(신규, 시나리오 3개), `tests/sql/test_get_today_candidate_cards.sql`(확장), `tests/batch/test_tags_stage.py`/`test_candidate_tags_repository.py`(확장), `apps/web/lib/candidate-cards.test.ts`(확장), `apps/web/lib/disappeared-candidates.test.ts`(신규), `apps/web/lib/dashboard-types.test.ts`(신규, 리뷰 패치), `.github/workflows/test.yml`(신규 SQL fixture 2개 등록).
- **리뷰 결과:** 4개 레이어(blind-hunter, edge-case-hunter, verification-gap, intent-alignment) 실행 → patch 5건(전부 low) 전부 수정, intent_gap 0, bad_spec 0, defer 0, dismissed 11건(스키마 제약 오인, 의도된 설계 차이, Story 2.7 선례와 동일한 관례, 스펙 서술 오류(코드 무관) 등). intent-alignment 감사 결과 diff는 지시의 (a)~(d) 절(빌드·검수·보완작업·필요 시 e2e 판단)까지를 구현했고, (e) 스프린트 동기화와 (f) 커밋은 이 리뷰 시점 이후 단계로 계획대로 남아있음을 확인했다.
- **추적 리뷰 권장:** `true`(patch 5건 전부 low, 3×medium(0)+1×low(5)=5 ≥ 5 임계값 충족 — 개별 결함의 심각도가 아니라 이번 패스에서 고친 patch 건수가 임계값을 넘겨 트리거된 것으로, 남은 리스크가 크다는 의미는 아니다).
- **수행한 검증:**
  - `node --test lib/**/*.test.ts`(apps/web) — 71/71 통과(리뷰 패치 후 재실행, 신규 `dashboard-types.test.ts` 4건 포함).
  - `npx tsc --noEmit`(apps/web) — clean.
  - `uv run --with pytest pytest tests/batch/test_tags_stage.py tests/batch/test_candidate_tags_repository.py` — 18/18 통과(리뷰 패치 후 재실행).
  - `git diff --check` — whitespace 오류 없음.
  - 신규/확장된 SQL fixture 3개(`test_sync_vanished_tags.sql`의 시나리오 6개 포함, `test_get_today_disappeared_candidates.sql`, `test_get_today_candidate_cards.sql` 확장분) 전부를 라이브 Supabase(qqhjeumlecaudsiqhhdu)에서 `begin`/`rollback` 트랜잭션으로 이 세션이 직접 재실행해 통과를 독립 확인(구현 서브에이전트의 자체 보고에만 의존하지 않음). 롤백 후 테스트 데이터(`2099-0*` logical_run_key) 잔여 0건 확인.
  - `pg_proc.proacl` 조회로 `sync_vanished_tags`는 `service_role`만, `get_today_candidate_cards`/`get_today_disappeared_candidates`는 `anon/authenticated/service_role` 모두 grant됨을 라이브 DB에서 직접 확인.
  - Matrix Test Audit: I/O 매트릭스 7개 행 중 6개가 자동화 테스트로 커버·실행·통과 확인됨. 나머지 1개("장중 화면 라벨"의 실제 렌더링)는 인증 세션 e2e 픽스처 부재라는 저장소 전반의 기존 제약(Story 2.7에서도 동일하게 문서화)으로 자동화 불가 — 리뷰 패치로 그 판정 로직(`isIntradaySnapshot`)만은 유닛 테스트를 추가해 공백을 좁혔다.
- **잔여 리스크:** ① "장중 화면 라벨"의 실제 DOM 렌더링은 여전히 자동화 테스트가 없다(defer, low, 저장소 전반의 기존 제약, frontmatter `deferred`에 기록). ② 대시보드 컴포넌트(`CandidateCard`, `DisappearedCandidatesNotice`) 전반에 렌더링 수준(React Testing Library 등) 테스트가 없다(이 저장소의 기존 관례와 동일, 신규 리스크 아님). ③ Epic 4(수급 수집)·실제 트래픽 미존재로 이번 스토리의 소멸/이탈/수집실패 분기는 SQL 계약 수준에서만 검증됐고 실사용자 데이터로는 아직 관측되지 않았다(Story 2.5~2.7과 동일한 기존 제약).
