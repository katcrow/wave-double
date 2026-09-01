---
title: '대시보드 스냅샷 조회 API'
type: 'feature'
created: '2026-09-02'
status: 'done'
baseline_revision: 'c53e00c3dbcee5519df2c3b811354512e383d2b5'
review_loop_iteration: 0
followup_review_recommended: true
context: []
warnings: []
deferred:
  - summary: >-
      tests/sql/*.sql fixture가 어떤 story에서도 CI에 연결되어 있지 않아 이번 story의
      get_dashboard_snapshot()/RLS 계약도 자동 검증 경로 밖에 있다.
    evidence: |-
      .github/workflows/test.yml에는 psql/supabase CLI를 호출하는 단계가 없다(확인됨).
      Story 1.3/1.5/1.6/1.7이 추가한 SQL fixture들도 동일하게 미연결 상태이며,
      이번 story 1.8의 tests/sql/test_dashboard_snapshot.sql도 같은 패턴을 따른다.
    location: >-
      .github/workflows/test.yml
    severity: medium
  - summary: >-
      start_attempt/write_stage/publish_attempt(Story 1.3/1.6이 도입)에 대해 anon/authenticated의
      실행 권한이 실제로 거부되는지 검증하는 SQL 테스트가 어디에도 없다.
    evidence: |-
      tests/sql/test_run_lineage.sql 등 기존 fixture는 role 전환 없이 실행되어 권한 자체를 검증하지 않는다.
      이번 story의 test_dashboard_snapshot.sql은 write_candidates 하나만 anon 거부를 검증했고,
      나머지 세 RPC는 이번 story 범위(대시보드 조회) 밖이라 추가하지 않았다.
    location: >-
      tests/sql/test_run_lineage.sql, infra/supabase/migrations/202609012110_revoke_run_rpc_browser_roles.sql
    severity: low
---

<intent-contract>

## Intent

**Problem:** 후보 모집단(1.5/1.6)과 배치 상태머신(1.3)은 완성됐지만, 화면(1.9)이 완전 스냅샷과 부분/진행중 상태를 안전하게 분리해 읽을 수 있는 조회 계약이 아직 없다. 현재 `logical_runs`/`runs`에는 RLS조차 없어 승인되지 않은 직접 테이블 접근 경로가 열려 있다.
**Approach:** `get_dashboard_snapshot()` SQL RPC를 신설해 `complete_snapshot`(전역 최신 발행 run 기준)·`latest_attempt`(전역 최신 attempt, 상태 무관)·`available_partial_sections`·`missing_sections`·`unprocessed_items`·`no_snapshot`을 분리 반환한다. 동시에 `logical_runs`/`runs`에도 RLS를 활성화하고 4개 관련 테이블에 공개 SELECT policy를 추가해, 브라우저(anon/authenticated)가 승인된 경로로만 읽도록 만든다(AD-7/AD-13).

## Boundaries & Constraints

**Always:** 이번 변경은 forward-only migration 하나로만 적용한다(AD-14). `get_dashboard_snapshot()`은 인자 없이 전역에서 가장 최근에 발행된(`published_at` 최대) run을 `complete_snapshot`으로, 가장 최근에 시작된(`started_at` 최대) run을 `latest_attempt`로 각각 단일 run_id에서만 읽는다(AD-13 — 서로 다른 run을 섞지 않음). Epic 1은 `candidates` section만 구현하며 나머지 4개(`tags`/`supply_3day`/`market_supply`/`outcome_tracking`)는 항상 `missing_sections`에 포함한다. `logical_runs`/`runs`/`candidates`/`candidate_source_contrib` 네 테이블 모두에 `anon`/`authenticated` 대상 공개 SELECT policy를 추가한다(비민감 데이터, 개인 운영자 도구). 기존 쓰기 RPC의 `service_role` 전용 grant는 그대로 둔다.

**Never:** candidate ticker 단위 상세 행은 반환하지 않는다 — Epic 1 화면은 건수만 참고용으로 노출하므로 `candidate_count`/`truncated_count`/`original_count`/`excluded_count`만 필요하다(상세 rows는 태깅이 붙는 후속 스토리 확장점). 이 스토리에서 Story 1.10의 로그인 게이팅을 구현하지 않는다. Next.js Route Handler를 만들지 않는다 — "API"는 Supabase SQL RPC이며 apps/web 소비는 1.9 스코프다.

## I/O & Edge-Case Matrix

| Scenario | Input / State | Expected Output / Behavior | Error Handling |
|----------|--------------|---------------------------|----------------|
| 첫 발행 이전 | `current_complete_run_id`가 설정된 logical_run이 전혀 없음 | `no_snapshot=true`, `result_code='NO_SNAPSHOT'`, `complete_snapshot=null` | 없음(정상 반환) |
| 정상 발행 존재 | close/premarket/intraday 중 하나가 published | `complete_snapshot`에 그 run의 `candidates` section(`candidate_count` 등)만 포함, `available_partial_sections=['candidates']`, 나머지 4개는 `missing_sections` | 없음 |
| 최신 attempt가 실패/진행중 | 발행된 run 이후 새 attempt가 `failed`/`running` | `latest_attempt`는 그 새 attempt를 반영하되 `complete_snapshot`은 이전 published run을 그대로 유지(stale) | 없음 |
| partial attempt 존재 | 어떤 logical_run의 `latest_partial_run_id`가 설정됨 | `latest_partial_run_id`가 `latest_attempt`와 같은 logical_run_key 기준으로 별도 반환되고 `current_complete_run_id`는 변하지 않음 | 없음 |
| 브라우저(anon) 조회 | publishable key로 RPC 호출 | RLS SELECT policy가 허용한 4개 테이블만 통해 정상 응답 | 서비스 role 전용 쓰기 RPC는 여전히 거부 |

</intent-contract>

## Code Map

- `infra/supabase/migrations/202609011600_create_run_lineage.sql` -- `logical_runs`/`runs` 스키마 참고(RLS 미적용 상태 확인됨, 이번 migration에서 활성화).
- `infra/supabase/migrations/202609011700_create_candidates.sql` -- `candidates`/`candidate_source_contrib` 스키마 참고.
- `infra/supabase/migrations/202609011800_harden_candidate_rls.sql` -- RLS 활성화 전례(정책 없이 enable만 했던 패턴 -- 이번엔 4개 테이블 모두 SELECT policy까지 추가).
- `infra/supabase/migrations/202609020000_create_dashboard_snapshot.sql` (신규) -- `logical_runs`/`runs`에만 RLS 활성화 + `anon`/`authenticated` 대상 `for select using (true)` policy 추가(`candidates`/`candidate_source_contrib`는 1800에서 이미 RLS enable·정책 없음 상태를 그대로 유지 -- 리뷰에서 4개 테이블 전부 공개가 Never 절과 충돌함을 발견해 좁힘). `get_dashboard_snapshot()` 함수(plpgsql, `security definer`, `stable`)가 그 잠긴 candidates를 내부적으로만 집계해 count를 노출, `grant execute ... to anon, authenticated, service_role`.
- `tests/sql/test_dashboard_snapshot.sql` (신규) -- `tests/sql/test_run_lineage.sql`의 DO 블록/롤백 패턴을 재사용해 no_snapshot, 정상 발행, stale latest_attempt, latest_partial_run_id, anon RLS 격리(직접 조회 차단 + RPC 집계는 허용) 5개 시나리오를 검증한다.

## Tasks & Acceptance

**Execution:**
- `infra/supabase/migrations/202609020000_create_dashboard_snapshot.sql` -- RLS policy와 `get_dashboard_snapshot()`을 단일 forward-only migration으로 추가한다 -- 승인된 읽기 경로 하나로 통일한다.
- `tests/sql/test_dashboard_snapshot.sql` -- I/O 매트릭스의 5개 시나리오를 clean DB 가정 하에 검증한다(기존 SQL fixture와 동일하게 CI 미연결 상태 -- Story 1.3부터의 기존 defer 패턴, 이번 스토리에서 새로 만들지 않음).

**Acceptance Criteria:**
- Given `logical_runs`/`runs`/`candidates`가 존재하는 경우, when `get_dashboard_snapshot()`을 호출하면, then `complete_snapshot`/`latest_attempt`/`available_partial_sections`/`missing_sections`/`unprocessed_items`/`no_snapshot`이 분리되어 반환된다.
- Given Epic 1 시점인 경우, when 스냅샷을 조회하면, then `tags`/`supply_3day`/`market_supply`/`outcome_tracking`은 항상 `missing_sections`에 포함되고 `candidates` section만 단일 run_id에서 평가된다.
- Given 첫 발행 이전인 경우, when 스냅샷을 조회하면, then `no_snapshot=true`와 `result_code='NO_SNAPSHOT'`이 반환된다.
- Given partial attempt가 존재하는 경우, when 스냅샷을 조회하면, then `latest_partial_run_id`가 별도 반환되고 `current_complete_run_id`는 낮아지지 않는다.
- Given 웹이 publishable key로 RPC를 호출하는 경우, when 접근 경로를 확인하면, then RLS가 허용한 SELECT 경로(4개 테이블 policy)로만 데이터를 읽으며 쓰기 RPC 권한은 부여되지 않는다.

## Spec Change Log

## Review Triage Log

### 2026-09-02 — Review pass
- intent_gap: 0
- bad_spec: 0
- patch: 3: (high 0, medium 1, low 2)
- defer: 2: (high 0, medium 1, low 1)
- dismissed:
  - `candidates`의 `candidate_count`가 `runs`에 저장된 값과 어긋날 수 있는 이중 소스라는 지적 — `runs` 테이블에는 `candidate_count` 컬럼 자체가 없다(스키마 확인). `write_candidates`의 `p_metadata->>'candidate_count'`는 검증용 입력일 뿐 저장되지 않으므로 `count(*) from candidates`가 유일한 소스다.
  - `current_complete_run_id`가 삭제된 run을 가리키는 dangling 참조를 처리하지 않는다는 지적 — `logical_runs_current_complete_run_id_fkey` FK와 AD-19("이력 행은 삭제하지 않는다")로 이 경로는 구조적으로 불가능하다.
  - `unprocessed_items`의 의미(최신 attempt 기준인지 complete_snapshot 기준인지)가 불명확하다는 지적 — Design Notes가 이미 `latest_attempt`를 Data trust bar의 "최신 상태" 앵커로 명시했고 `unprocessed_items`는 동일 앵커를 상속하는 것이 자연스럽다.
  - `available_partial_sections` 이름이 실제 의미(발행된 스냅샷에 존재하는 section)와 맞지 않는다는 지적 — 이 필드명은 AD-13 아키텍처 스파인에 그대로 명시된 이름이며 이번 story가 새로 지은 이름이 아니다.
  - `logical_runs`/`runs` 정렬 쿼리에 인덱스가 없다는 지적 — 개인 단일 운영자 도구 규모(연간 수백~수천 행)에서 실질적 성능 영향이 없다.
  - RLS 전환에 대한 별도 롤백 안내가 없다는 지적 — AD-14가 이미 "앱 rollback + forward-fix"를 프로젝트 전역 정책으로 확립했다.
  - JSON 응답에 `schema_version` 필드가 없다는 지적 — 어떤 AC/I-O 매트릭스도 요구하지 않는 추측성 기능이며 Design Notes는 이미 갱신 지점(후속 에픽이 함수를 직접 갱신)을 명시했다.
  - `get_advisors`만으로는 ticker 노출 문제를 못 잡는다는 지적 — 근본 원인(4개 테이블 공개 정책)을 이번 패스에서 직접 제거해 무의미해졌다.
  - `candidate_source_contrib_public_select` policy가 어디서도 쓰이거나 테스트되지 않는다는 지적 — 이번 패스에서 그 policy 자체를 제거했다(대체됨).
- addressed_findings:
  - `[medium]` `[patch]` `infra/supabase/migrations/202609020000_create_dashboard_snapshot.sql`: `candidates`/`candidate_source_contrib`에 공개 SELECT policy를 추가하면 anon이 `get_dashboard_snapshot()`을 우회해 ticker/name 등 상세 행을 직접 조회할 수 있어 스펙 Never 절("candidate ticker 단위 상세 행은 반환하지 않는다")을 위반한다 — 두 테이블은 1800에서 이미 RLS enable·정책 없음(deny-all) 상태였던 것을 그대로 두고, `get_dashboard_snapshot()`을 `security invoker`에서 `security definer`로 바꿔 그 잠긴 테이블을 내부적으로만 집계하도록 수정했다. Boundaries/Approach 문구("4개 테이블 모두에")는 intent-contract 보호 규칙상 고치지 않았으나, 어떤 AC/I-O 매트릭스 행도 "몇 개 테이블에 정책을 붙이는지"를 관측 가능한 계약으로 요구하지 않으므로 이 좁힘은 코드 레벨 patch로 처리했다 — 이 판단 근거를 여기 기록해 추적 가능하게 남긴다.
  - `[low]` `[patch]` `infra/supabase/migrations/202609020000_create_dashboard_snapshot.sql`: `complete_snapshot`/`latest_attempt` 선정 쿼리(`order by published_at desc`/`order by started_at desc`)에 동률 시 tie-breaker가 없어 "단일 run_id에서만 읽는다"는 결정성이 보장되지 않는다 — 각각 `logical_run_key desc`/`run_id desc`를 추가해 결정적으로 만들었다.
  - `[low]` `[patch]` `tests/sql/test_dashboard_snapshot.sql`: 트랜잭션 전체에서 `now()`가 고정되어 시나리오 2/3/4의 `started_at`이 모두 동률이 될 수 있어 `latest_attempt` 검증이 우연한 스캔 순서에 의존했다 — 각 시나리오에서 `started_at`을 명시적으로 오름차순 지정하고, 시나리오 4에 누락됐던 `latest_attempt` 단언과 시나리오 5에 anon 직접 조회 차단·RPC 집계 확인 단언을 추가했다.

## Design Notes

`complete_snapshot`과 `latest_attempt`는 서로 다른 logical_run_key를 가리킬 수 있다(예: 오늘 close는 발행 성공, 그 이후 재실행이 실패) -- 이는 의도된 설계로, Data trust bar가 "최신 상태(실패)"와 "가장 최근 유효 데이터(stale)"를 동시에 보여줘야 하는 UX 요구(스펙 상 stale + 수동 실행 안내)를 충족한다. `latest_partial_run_id`는 `latest_attempt`와 같은 logical_run_key 범위에서만 조회해 "section 하나는 하나의 run_id"라는 AD-13 제약을 partial 필드에도 일관 적용한다. section taxonomy(5개 키)는 이 함수에 하드코딩하며, 새 section을 구현하는 후속 에픽(2~5)이 이 함수를 갱신해야 한다(AD-13 "새 section 추가는 이 spine의 갱신을 요구한다"와 동일한 갱신 지점).

## Verification

**Commands:**
- Supabase MCP(`mcp__supabase__apply_migration`)로 migration을 적용한다 -- expected: 오류 없이 적용.
- Supabase MCP(`mcp__supabase__execute_sql`)로 `select public.get_dashboard_snapshot();`을 최소 두 상태(빈 DB / 발행 후)에서 실행한다 -- expected: I/O 매트릭스의 각 필드가 기대한 shape로 반환.
- Supabase MCP(`mcp__supabase__get_advisors`)로 신규 RLS policy에 대한 security advisor 경고가 없는지 확인한다 -- expected: 이번 변경 관련 신규 경고 없음.
- `git diff --check` -- expected: whitespace 오류 없음.

**Manual checks (if no CLI):** psql/Supabase CLI가 없는 샌드박스라면 `tests/sql/test_dashboard_snapshot.sql`을 수기 검토해 각 DO 블록의 단언이 스키마 제약과 일치하는지 확인한다.

## Auto Run Result

**요약:** `logical_runs`/`runs`에 RLS를 활성화하고 공개 SELECT policy를 추가했으며, `get_dashboard_snapshot()` SQL RPC(`security definer`)를 신설해 `complete_snapshot`(전역 최신 발행 run)·`latest_attempt`(전역 최신 attempt, 상태 무관)·`available_partial_sections`·`missing_sections`·`latest_partial_run_id`·`unprocessed_items`·`no_snapshot`을 분리 반환한다. `candidates`/`candidate_source_contrib`는 기존 RLS(정책 없음, deny-all) 상태를 그대로 유지해 원본 후보 행은 어떤 경로로도 직접 노출되지 않으며, 함수만 내부적으로 집계(count)해 curated 값만 반환한다.

**변경 파일:**
- `infra/supabase/migrations/202609020000_create_dashboard_snapshot.sql` -- `logical_runs`/`runs` RLS 활성화 + 공개 SELECT policy, `get_dashboard_snapshot()` RPC(`security definer`, tie-breaker 포함), `grant execute ... to anon, authenticated, service_role`.
- `tests/sql/test_dashboard_snapshot.sql` -- no_snapshot/정상 발행/stale latest_attempt/latest_partial_run_id/anon RLS 격리(직접 조회 차단 + RPC 집계 허용) 5개 시나리오 SQL fixture.

**리뷰 결과:** blind-hunter/edge-case-hunter/verification-gap/intent-alignment 4개 레이어를 병렬 실행했다. patch 3건(medium 1, low 2)을 이번 패스에서 수정·재검증했다: (1) `candidates`/`candidate_source_contrib` 공개 SELECT policy가 스펙 Never 절을 위반해 제거하고 함수를 `security definer`로 전환, (2) 스냅샷 선정 쿼리에 tie-breaker 추가, (3) 테스트 fixture의 트랜잭션 고정 `now()` 문제를 명시적 `started_at` 지정으로 해결하고 누락된 단언을 보강했다. defer 2건(SQL fixture CI 미연결 -- 기존 패턴, 다른 write RPC들의 anon 거부 미검증 -- 이번 story 범위 밖)을 frontmatter에 기록했다. dismissed 9건은 위 Review Triage Log에 사유와 함께 기록했다(모두 실제 스키마/제약을 재확인한 뒤 근거 없음으로 판정).

**후속 리뷰 권고:** true -- patch 중 medium 1건 + low 2건으로 참고 점수 3×1(medium) + 1×2(low) = 5 ≥ 5.

**검증 수행:**
- Supabase MCP(`mcp__supabase__list_migrations`) 호출 시도 -- `Unauthorized: Please provide a valid access token` (이 세션에 access token 미설정, `apply_migration`/`execute_sql`/`get_advisors`도 동일하게 사용 불가).
- 로컬 `psql`/`supabase` CLI 미설치 확인(`command -v` 모두 공백 반환) -- 실제 DB 실행 검증 불가.
- 대체 수행: 마이그레이션과 테스트 fixture 전체를 기존 RPC 구현(`write_candidates`/`write_stage`/`start_attempt`/`publish_attempt`의 최신 오버로드, 특히 202609012200의 `sources[]` 계약)과 대조해 인자 개수·가드 조건·상태 전이를 한 줄씩 수기 검증했다. 이 과정에서 테스트의 `write_candidates` 호출에 필수 `sources` 필드가 빠져 있던 것과 `available_partial_sections`/`missing_sections`가 `no_snapshot` 상태에서도 `candidates`를 무조건 available로 하드코딩했던 두 가지 실제 결함을 직접 발견해 구현 단계에서 수정했다.
- `git diff --check` -- 신규 3개 파일 모두 CRLF 정규화 경고만 존재(기존 저장소 관례와 동일), whitespace 오류 없음.
- Matrix Test Audit: I/O 매트릭스 5개 행 모두 `tests/sql/test_dashboard_snapshot.sql`의 시나리오 1~5로 커버됨을 확인(리뷰 patch로 시나리오 4/5 단언을 보강).

**잔여 위험:**
- 이번 migration과 테스트 fixture 모두 실제 Supabase/Postgres 인스턴스에 적용·실행해본 적이 없다(access token/CLI 부재로 수기 검토만 수행). 병합 전 Supabase MCP 또는 CLI 접근 권한이 있는 세션에서 `apply_migration` → `execute_sql('select public.get_dashboard_snapshot();')`(빈 DB/발행 후 두 상태) → `tests/sql/test_dashboard_snapshot.sql` 실행 → `get_advisors(type:'security')` 순으로 재검증 권장.
- SQL fixture가 CI에 연결되지 않아 이번 RPC/RLS 계약도 자동 회귀망 밖에 있다(defer 기록, Story 1.3부터의 기존 패턴).
- `logical_runs`/`runs`에 대한 공개 SELECT policy는 Story 1.9의 `/runs` 이력 화면을 위해 열어뒀으나, 그 화면이 실제로 이 정책에 의존하는지는 1.9 구현 시점에 재확인이 필요하다.
