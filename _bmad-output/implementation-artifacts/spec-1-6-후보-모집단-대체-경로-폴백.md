---
title: '후보 모집단 대체 경로 폴백'
type: 'feature'
created: '2026-09-01'
status: 'done'
review_loop_iteration: 0
followup_review_recommended: true
context:
  - C:/dev/wave-double/_bmad-output/implementation-artifacts/epic-1-context.md
warnings: []
deferred: []
baseline_revision: '7418c17280fe7d8b4ad8033453aa3581136287fc'
baseline_commit: '7418c17280fe7d8b4ad8033453aa3581136287fc'
---

<intent-contract>

## Intent

**Problem:** 현재 candidates stage는 t1859 호출이 실패(세션/터미널 제약 등)하면 즉시 `failed`로 종결되어, 조건검색 세션 장애만으로 후보 모집단 갱신 전체가 중단된다. `runs.fallback_used`와 `candidate_source_contrib`의 다중 source 계약은 스키마에 이미 존재하지만 어느 RPC도 채우지 않는다.

**Approach:** t1859 실패(예외 또는 `response.ok=false`) 시 t1856("파일저장종목검색") 경로로 자동 재시도하고, 성공하면 `runs.fallback_used=true`를 기록한다. 후보 선별을 source별 결과를 종목코드로 합치는 일반화된 병합 규칙(우선순위 `t1859 > t1852 > t1856`, 최대 유효 거래대금)으로 확장하고, 두 경로 모두 실패하면 조용한 누락 없이 `partial`/`failed`로 `unprocessed_count`를 기록한다.

## Boundaries & Constraints

**Always:** 폴백 성공 시에만 `runs.fallback_used=true`를 기록한다(폴백 자체가 실패하면 false 유지). 병합된 각 후보는 `candidate_source_contrib`에 기여 source당 최소 1행, weight 합계 정확히 1을 유지하며 weight는 `(0,1]`이다. 동일 종목이 여러 source에서 유효 거래대금을 반환하면 저장값은 그 중 최댓값이며, primary source(최대 weight, 동률이면 `t1859>t1852>t1856` 우선순위)가 그 최댓값을 낸 source와 일치해야 한다. `candidates.source` 컬럼은 만들지 않는다(기존 계약 유지). t1859와 폴백이 모두 실패하면 candidates stage는 `partial` 또는 `failed`로 종결되고 `unprocessed_count`가 0보다 크게 기록된다.

**Never:** t1852를 동기 후보 조회 호출 대상으로 구현하지 않는다 — t1852는 등록/ack 전용 TR(`t1852OutBlock`에 `sresultflag`만 반환, 종목 행 없음)이라 이 배치 흐름에서 후보 데이터를 낼 수 없다. `source` enum과 우선순위 상수는 스키마 계약대로 `t1852`를 포함해 유지하되, 실제 폴백 호출은 t1856로 수행한다. 이후 에픽(태깅/outcome)의 source별 view나 화면 구분 UI는 이 story 범위가 아니다. Story 1.5의 단일 source(t1859) 선별 경로와 기존 테스트를 깨지 않는다.

## I/O & Edge-Case Matrix

| Scenario | Input / State | Expected Output / Behavior | Error Handling |
|----------|--------------|----------------------------|----------------|
| FALLBACK_SUCCESS | t1859 호출 예외 또는 `response.ok=false`, 이어진 t1856 호출 성공 | t1856 결과로 후보 선별·저장, `fallback_used=true`, stage `success`/`partial`(t1856 unprocessed 여부에 따라) | t1859 실패 사유는 result에 기록되지만 stage는 실패로 끝나지 않음 |
| BOTH_FAIL | t1859, t1856 모두 예외 또는 `response.ok=false` | candidates stage `failed`(또는 부분 데이터가 없으므로 `failed`), `unprocessed_count>0`, `fallback_used=false` | 두 실패의 result_code를 모두 result에 남겨 조용한 누락을 방지 |
| MULTI_SOURCE_MERGE | 동일 종목이 t1859·t1856 두 source에 서로 다른 유효 거래대금으로 존재(domain 단위 테스트 입력) | 저장값=두 값 중 최댓값, `candidate_source_contrib`에 두 source 행, weight 합계=1, primary source는 우선순위 규칙과 일치 | 값이 같으면 두 source 모두 기여로 기록(예: 균등 weight) |
| INVALID_VALUE_ACROSS_SOURCES | 한 source는 유효값, 다른 source는 null/비유한값 | 유효한 source만 기여로 채택, 무효 source는 그 종목에 기여하지 않음(전체 종목 제외 아님) | 모든 source가 무효면 기존 규칙대로 제외+excluded_count 증가 |

</intent-contract>

## Code Map

- `apps/batch/candidate_stage.py:68-76` -- t1859 예외/`not response.ok` 즉시 실패 분기. 두 지점 모두 t1856 폴백 재시도를 감싸도록 확장. `_response_records()`(42-48)에 `t1856OutBlock1` 키 추가.
- `apps/batch/candidate_stage.py:51-60` -- `run_candidate_stage()` 시그니처에 폴백 요청 파라미터(예: `fallback_params: dict | None`) 추가 필요 -- 기존 `request_params` 구성(67행) 패턴 재사용.
- `packages/domain/domain/candidate_selection.py:20-27,92-136` -- `SelectedCandidate`에 source 없음, `select_candidates()`는 단일 flat 레코드 리스트만 처리하고 동일 ticker 재등장을 단순 제외(129행)한다. source별 결과를 병합하는 신규 함수 필요(기존 `select_candidates`/`_records`/`_first`/`_input_hash`는 그대로 재사용).
- `apps/batch/run_state.py:92-125` -- `write_stage()`에 `p_fallback_used` 파라미터가 없음. `fallback_used: bool = False` 인자를 추가하고 RPC 파라미터에 `p_fallback_used`를 실어 보낸다.
- `apps/batch/run_state.py:127-143` -- `write_candidates()` 시그니처는 그대로 두되, 호출자가 넘기는 `candidates` 각 항목에 `sources: [{source, weight}, ...]`를 추가로 실어 보낸다(RPC가 이를 소비).
- `infra/supabase/migrations/202609012100_harden_run_and_candidate_contracts.sql:28-44` -- `write_stage` RPC: `p_fallback_used boolean default false` 파라미터와 `fallback_used = fallback_used or p_fallback_used` update 추가(forward-only 신규 migration에서 `create or replace`).
- `infra/supabase/migrations/202609012100_harden_run_and_candidate_contracts.sql:46-65` -- `write_candidates` RPC: `insert into candidate_source_contrib(...) values (..., 't1859', 1.0)` 하드코딩을 제거하고, 각 candidate item의 `sources` jsonb 배열을 순회하며 `(source, weight)` 행을 삽입하고 항목별 weight 합계=1을 검증하는 로직으로 대체. 함수 시그니처가 바뀌지 않으면(같은 `p_candidates jsonb`) 기존 `revoke/grant`(파일 끝 82-89행 상당)는 재적용 불필요 -- 시그니처 유지 확인.
- `infra/supabase/migrations/202609011700_create_candidates.sql:17-25` -- `candidate_source_contrib` 스키마(다중 source, weight 계약)는 이미 이 story 요구를 만족하므로 스키마 변경 불필요.
- `docs/api/ls-openapi/03-domestic-stock/stock-search.md:412-523,527-648` -- t1852(등록/ack, 종목 행 없음)와 t1856(`t1856OutBlock1`: `shcode,hname,price,volume` 등, t1859와 동일 필드 별칭) 요청/응답 계약 근거.
- `tests/batch/test_candidate_stage.py` -- `FakeLs`가 단일 TR(t1859)만 가정. 다중 TR을 흉내내는 fake로 확장 필요(폴백 성공/양쪽 실패 케이스).
- `tests/domain/test_candidate_selection.py:41-47` -- 기존 동일 ticker 중복 처리(단순 제외) 테스트는 단일-source 경로 그대로 유지. 신규 병합 함수용 테스트를 별도로 추가.
- `tests/sql/test_candidates.sql` -- 다중 source contrib/`fallback_used` 검증 SQL fixture 확장 패턴의 기반.

## Tasks & Acceptance

**Execution:**
- `packages/domain/domain/candidate_selection.py` -- source별 레코드 리스트를 받아 종목코드 기준 병합(우선순위+최대 유효값, 기여 source별 weight 산출, 합계 1 보장)하는 신규 함수를 추가한다 -- DB/LS 의존 없이 재현 가능한 병합 규칙을 domain 계층에 둔다.
- `apps/batch/candidate_stage.py` -- t1859 예외/실패 시 t1856 재시도, 병합 함수 사용, `fallback_used` 전달, 양쪽 실패 시 result_code를 합쳐 `failed`/`partial`로 종결하는 로직을 구현한다 -- 조용한 누락 방지와 자동 폴백을 오케스트레이션 계층에서 담당한다.
- `apps/batch/run_state.py` -- `write_stage()`에 `fallback_used` 파라미터를 추가해 RPC로 전달한다 -- Python adapter가 새 RPC 파라미터를 노출한다.
- `infra/supabase/migrations/202609XXXXXX_add_candidate_fallback_support.sql` -- `write_stage`/`write_candidates` RPC를 위 계약대로 `create or replace`하고, 새/변경 파라미터가 있다면 동일한 `revoke/grant service_role` 패턴을 재적용한다 -- forward-only 신규 migration으로 기존 파일을 수정하지 않는다.
- `tests/domain/test_candidate_selection.py` -- 병합 함수의 우선순위·최대값·weight 합계·무효 source 케이스를 검증한다.
- `tests/batch/test_candidate_stage.py` -- 다중 TR fake로 폴백 성공, 양쪽 실패, `fallback_used` 기록 여부를 검증한다.
- `tests/sql/test_candidates_fallback.sql` -- 다중 source contrib 행과 `runs.fallback_used` 갱신을 clean DB에서 검증한다.

**Acceptance Criteria:**
- Given t1859 호출이 실패하면, when candidates stage가 이를 감지하면, then t1856 경로로 재시도하고 성공 시 `runs.fallback_used=true`가 기록된다.
- Given t1859와 t1856이 같은 종목에 서로 다른 유효 거래대금을 반환하면, when 후보 집합을 정규화하면, then 저장값은 최댓값이고 `candidate_source_contrib`에 기여 source별 행(weight 합계 1)이 기록되며 primary source는 우선순위 규칙과 일치한다.
- Given t1859와 t1856이 모두 실패하면, when candidates stage가 완료되면, then stage는 `partial` 또는 `failed`로 종결되고 `unprocessed_count`가 0보다 크며 `fallback_used`는 false로 유지된다.
- Given 폴백으로 채워진 candidates가 있으면, when `candidate_source_contrib`를 조회하면, then source 값으로 필터링 가능하며 t1859/t1856을 동일 모집단으로 가정하지 않는다.

## Design Notes

병합 함수는 domain 계층 순수 함수로 두고, 실제 오케스트레이터는 한 attempt당 t1859 또는 t1856 중 하나의 source 결과만 넘기는 경우가 대부분이다(t1859 실패 시에만 폴백이 실행되므로). 다중 source 병합 규칙(AC2)은 domain 단위 테스트에서 합성 다중-source 입력으로 직접 검증한다. 동일 최댓값을 여러 source가 함께 낸 경우의 weight 분배는 "기여 source 수로 균등 분배"를 기본 규칙으로 삼는다(예: 두 source가 기여하면 각 0.5) -- 합계 1과 `(0,1]` 제약을 항상 만족하며, primary source 결정은 동률 시 우선순위로 갈린다. `write_candidates` RPC의 `p_candidates` payload는 candidate 항목마다 `sources: [{source, weight}]` 배열을 포함하도록 확장한다.

## Verification

**Commands:**
- `uv run --with pytest pytest tests/domain/test_candidate_selection.py tests/batch/test_candidate_stage.py -q` -- expected: 신규 폴백/병합 테스트 포함 전체 통과.
- `uv run --with pandas --with numpy --with pyarrow --with pytest pytest tests/domain tests/batch -q` -- expected: 기존 domain/batch 회귀 통과.
- `uv run --with pandas --with numpy --with pyarrow --with pytest pytest backtest -q` -- expected: 기존 backtest 회귀 변화 없음.
- Supabase 로컬/원격 연결로 `tests/sql/test_candidates.sql`, `tests/sql/test_candidates_fallback.sql` 적용 -- expected: 기존 및 신규 SQL fixture 통과.
- `git diff --check` -- expected: whitespace 오류 없음.

## Review Triage Log

### 2026-09-01 — Review pass

- intent_gap: 0
- bad_spec: 0
- patch: 4: (high 0, medium 2, low 2)
- defer: 0
- dismissed:
  - 다중 source 병합이 실제 오케스트레이터에서는 항상 단일 source로만 호출된다(t1859/t1856 동시 전달 없음) — 스펙 Design Notes가 "실제 오케스트레이터는 대부분 하나의 source만 넘기며, 다중 source 규칙은 domain 단위 테스트에서 합성 입력으로 검증한다"고 명시적으로 승인한 방식이며 AC2는 정규화 동작 자체를 요구할 뿐 특정 호출 경로를 요구하지 않는다.
  - I/O 매트릭스 MULTI_SOURCE_MERGE 행의 "두 source 행" 표현이 값이 다를 때도 두 행을 요구하는 것처럼 읽힐 수 있다 — 더 구체적인 Boundaries 텍스트("최댓값... 동률이면 우선순위")와 Design Notes가 weight 분배를 동률 케이스로만 한정함을 명시하며, 구현과 테스트가 이 단일하고 합리적인 해석을 일관되게 따른다.
  - `select_candidates()`가 `candidate_stage.py`에서 더 이상 호출되지 않아 사실상 미사용 — 저장소 전체 검색 결과 테스트 외 실제 호출자가 없어 현재 깨지는 경로가 없다.
  - `candidate_stage.py`의 `PRIMARY_TR`/`FALLBACK_TR`과 `candidate_selection.py`의 `SOURCE_PRIORITY`가 별도로 정의되어 있다 — 추측성 drift 우려이며 실제 실패 사례가 제시되지 않았다.
  - 양쪽 source 모두 실패 시 `unprocessed_count`를 최소 1로 강제한다 — 스펙 AC3가 "unprocessed_count가 0보다 크게" 기록될 것을 명시적으로 요구하므로 의도된 동작이다.
  - `write_stage`의 `fallback_used`가 실행 동안 단조 누적(sticky)된다 — 스펙의 "폴백 성공 시에만 true 기록(실패 시 false 유지)" 요구와 일치하며, 리셋을 요구하는 조항이 없고 실패 시나리오도 제시되지 않았다.
  - `merge_candidate_sources()`가 source 이름을 RPC보다 먼저 domain 계층에서 검증하지 않는다 — RPC가 잘못된 source를 정확히 거부함을 코드로 확인했으며, 계층 배치 선호일 뿐 실제 결함이 아니다.
  - 폴백 트리거에 대한 구조화 로깅/텔레메트리가 없다 — intent-contract가 요구하지 않는 범위 밖 항목이다.
  - `CANDIDATE_SOURCES_EXHAUSTED` 등 신규 계약에 대한 API 문서 갱신이 없다 — 스펙이 요구하지 않으며 Code Map의 문서 참조는 기존 TR 계약의 배경 근거일 뿐이다.
  - `test_candidates_fallback.sql`의 BOTH_FAIL 케이스가 Python 오케스트레이션과 SQL RPC를 하나의 테스트로 잇지 않는다 — 두 계층이 각각 FakeLs/FakeRpc 단위 테스트와 SQL fixture로 이미 독립적으로 검증되어 있어 추가 통합 테스트 없이도 탐지되지 않는 회귀 위험이 확인되지 않았다.
  - SQL fixture가 weight 합계 초과/음수/미지정 source 거부 케이스를 추가로 다루지 않는다 — 코드 검토 결과 해당 가드가 이미 올바르게 구현되어 있으며 추가 검증 필요성이 입증되지 않았다.
  - 이번 검증에 원격 Supabase Management API를 수동으로 사용해 로컬에서 반복 가능한 커맨드로 남지 않았다 — 이는 diff 자체의 결함이 아니라 이번 세션의 검증 방식에 대한 메모다.
  - `merge_candidate_sources()`의 동률 weight 분배가 3-way tie에서 부동소수점 오차로 정확히 1.0이 아닐 수 있다(예: 1/3×3=0.9999999999999999) — 현재 production/테스트 어디에서도 3개 이상 source가 동률로 도달하는 경로가 없고(실질 source는 t1859/t1856 둘뿐), 설령 도달하더라도 SQL의 0.0001 허용오차가 흡수해 실제 결과에 영향이 없다.
- addressed_findings:
  - `[low]` `[patch]` `write_candidates`의 `sources` 배열에 동일 source가 중복되면 `ON CONFLICT ... DO UPDATE`가 행을 덮어써 저장된 weight 합계가 1이 아니게 된다 — 중복 source 검증 가드 추가.
  - `[low]` `[patch]` `merge_candidate_sources()`에서 종목이 여러 source에 유효값으로 존재하지만 최댓값을 내지 못한(cross-source 패자) 레코드가 `excluded_count`에 반영되지 않아 `original_count` 정합성이 깨진다 — 해당 레코드도 `excluded`에 반영하도록 수정.
  - `[medium]` `[patch]` `merge_candidate_sources()`(현재 유일한 production 경로)의 단일 source 내 종목 중복 처리(최댓값 유지) 로직이 테스트되지 않는다 — 기존 커버 테스트는 이제 미사용인 `select_candidates()`만 검증한다 — 신규 domain 테스트 추가.
  - `[medium]` `[patch]` t1859가 `ok=true`이지만 `unprocessed_count>0`인 부분 성공 상황에서 폴백이 트리거되지 않음을 검증하는 테스트가 없다(스펙의 "Never" 경계 조건) — 신규 batch 테스트 추가.

## Auto Run Result

**요약:** t1859(조건검색) 호출이 실패(예외 또는 `response.ok=false`)하면 t1856("파일저장종목검색")로 자동 폴백해 재시도하고, 성공하면 `runs.fallback_used=true`를 기록한다. 후보 선별은 source별 결과를 종목코드로 병합하는 `merge_candidate_sources()`로 확장되어(우선순위 `t1859>t1852>t1856`, 최대 유효 거래대금, 동률시 균등 weight) `candidate_source_contrib`에 다중 source 기여를 기록한다. t1859와 폴백이 모두 실패하면 `CANDIDATE_SOURCES_EXHAUSTED`로 `failed` 종결되고 `unprocessed_count>0`이 기록된다.

**변경 파일:**
- `apps/batch/candidate_stage.py` — t1859 실패 시 t1856 자동 재시도, `fallback_used` 추적, 양쪽 실패 시 `CANDIDATE_SOURCES_EXHAUSTED`로 종결하는 오케스트레이션 로직 추가.
- `apps/batch/run_state.py` — `write_stage()`에 `fallback_used` 파라미터를 추가해 RPC로 전달.
- `packages/domain/domain/candidate_selection.py` — `merge_candidate_sources()`/`SourceContribution`/`SOURCE_PRIORITY` 추가(순수 함수, source별 병합·weight 산출); 리뷰 패치로 cross-source에서 최댓값을 내지 못한 유효 레코드도 `excluded_count`에 반영하도록 수정.
- `infra/supabase/migrations/202609012200_add_candidate_fallback_support.sql` — `write_stage`/`write_candidates` RPC를 계약대로 `create or replace`; 리뷰 패치로 (a) 기존 8-param `write_stage` 오버로드를 명시적으로 `drop`해 positional 호출 모호성 제거, (b) `sources` 배열 내 중복 source 코드를 거부하는 가드 추가.
- `tests/domain/test_candidate_selection.py` — 병합 함수의 우선순위·최대값·weight 합계·무효 source 케이스 테스트 추가; 리뷰 패치로 단일 source 내 종목 중복 처리, cross-source 패자 제외 회계 테스트 추가.
- `tests/batch/test_candidate_stage.py` — 다중 TR fake로 폴백 성공/양쪽 실패/`fallback_used` 기록 테스트 추가; 리뷰 패치로 "primary 부분 성공 시 폴백 미트리거" 테스트 추가.
- `tests/sql/test_candidates_fallback.sql` — 다중 source contrib 행, `fallback_used` 갱신, weight 합계 거부를 검증하는 신규 fixture; 리뷰 준비 중 발견한 `run_id` 변수/컬럼명 충돌(ambiguous)을 `#variable_conflict use_variable` pragma로 수정.
- `tests/sql/test_candidates.sql` (story 1.5 기존 fixture) — `write_candidates()`가 이제 `sources` 배열을 필수로 요구하는 새 계약에 맞춰 후보 페이로드에 `sources` 필드를 추가(동작 자체는 story 1.5와 동일하게 유지).

**리뷰 결과:** blind-hunter, edge-case-hunter, verification-gap, intent-alignment 4개 레이어를 모두 실행. intent_gap 0, bad_spec 0, patch 4 (medium 2, low 2), defer 0. Dismissed 13건(사유는 `## Review Triage Log`에 기록) — 주로 스펙의 Design Notes/Boundaries로 이미 해소된 해석 모호성, 현재 호출자가 없어 재현 불가능한 가정, 스펙이 명시적으로 요구하는 동작을 오해한 지적들. Addressed(patch) 4건:
- `[low]` `write_candidates`의 `sources` 배열 내 source 중복이 `ON CONFLICT` 업서트로 조용히 weight 합계를 깨뜨리는 문제 — 중복 거부 가드 추가, 원격 DB에서 거부 동작 재확인.
- `[low]` `merge_candidate_sources()`의 cross-source 패자 레코드가 `excluded_count`에 반영되지 않아 `original_count` 정합성이 깨지는 문제 — 회계 로직 수정.
- `[medium]` 유일한 production 경로인 `merge_candidate_sources()`의 단일 source 내 종목 중복 처리가 무테스트였던 문제 — 신규 domain 테스트 2건 추가.
- `[medium]` primary 부분 성공(`ok=true`, `unprocessed_count>0`) 시 폴백이 트리거되지 않음을 보장하는 테스트가 없던 문제 — 신규 batch 테스트 추가.

**후속 리뷰 권고:** `followup_review_recommended: true` — patch 심각도 점수 = 3×medium(2) + 1×low(2) = 8 ≥ 5 (high 0건이지만 점수 기준 충족).

**검증 수행:**
- `uv run --with pytest pytest tests/domain/test_candidate_selection.py tests/batch/test_candidate_stage.py -q` — 23 passed (패치 후 +3).
- `uv run --with pandas --with numpy --with pyarrow --with pytest pytest tests/domain tests/batch -q` — 72 passed.
- `uv run --with pandas --with numpy --with pyarrow --with pytest pytest backtest -q` — 16 passed.
- `git diff --check` — 이상 없음.
- 원격 Supabase 프로젝트(`qqhjeumlecaudsiqhhdu`, 사용자 승인 하에 Management API 직접 호출로 접근 — 로컬 CLI/Docker 부재)에 `infra/supabase/migrations/*.sql` 전체를 순서대로 적용(빈 스키마였음), `tests/sql/test_candidates.sql`·`tests/sql/test_candidates_fallback.sql` 통과(각 `rollback;`으로 스키마만 남고 테스트 데이터는 미잔존), 패치 후 마이그레이션 재적용 및 두 fixture 재통과 확인, 중복 source 거부 가드는 별도 임시 sanity-check SQL(적용 후 롤백)로 직접 확인.

**잔여 리스크:**
- 다중 source 병합(cross-source, 서로 다른 값)은 실제 오케스트레이터에서 도달 불가(t1856은 t1859 실패 시에만 호출)하며 domain 단위 테스트로만 검증된다 — 스펙 Design Notes가 명시적으로 승인한 설계이지만, 향후 실제로 두 source가 동시에 유효 데이터를 내는 경로가 추가된다면 end-to-end 검증이 필요하다.
- 이번 세션의 SQL 검증은 로컬 Supabase CLI/Docker가 없어 원격 프로젝트의 Management API를 수동으로 사용했다 — 반복 가능한 로컬 커맨드로 남아있지 않으므로, 이후 세션에서는 `supabase start` 등 로컬 스택을 우선 시도할 것을 권장.
- 3-source 이상 동률 시 weight 부동소수점 합이 정확히 1.0이 아닐 수 있으나(SQL 허용오차 0.0001로 흡수, 실제 source는 2개뿐이라 현재 도달 불가) 향후 source 종류가 늘어나면 재검토 필요.
