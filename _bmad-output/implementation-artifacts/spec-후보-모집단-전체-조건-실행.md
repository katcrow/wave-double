---
title: '후보 모집단 전체 조건 실행·통합'
type: 'feature'
created: '2026-09-14'
status: 'done'
baseline_commit: '4652489'
review_loop_iteration: 0
context:
  - C:/dev/wave-double/_bmad-output/implementation-artifacts/spec-1-5-후보-모집단-자동-갱신.md
  - C:/dev/wave-double/_bmad-output/implementation-artifacts/epic-1-context.md
---

<frozen-after-approval reason="human-owned intent — do not modify unless human renegotiates">

## Intent

**Problem:** 후보 모집단이 단일 `LS_QUERY_INDEX` 하나만 실행한다. 시크릿 미등록 시 `query_index=""`로 t1859를 호출해 LS가 후보 0건을 반환했고(2026-09-14 운영 검증에서 `intraday:2026-09-14:13:00` 후보 0건), 앞으로 Neo가 저장검색 조건을 더 등록해도 그 조건들은 자동으로 모집단에 반영되지 않는다.

**Approach:** 배치는 `LS_QUERY_INDEX` 대신 `LS_CONDITION_SEARCH_USER_ID`를 필수 환경변수로 받아, 실행 시마다 t1866으로 계정의 전체 서버저장검색 조건 목록을 조회하고 각 조건을 t1859로 직렬 실행해 레코드를 통합 후보 모집단으로 선별·저장한다. 조건 추가는 별도 설정 변경 없이 자동 반영된다.

## Boundaries & Constraints

**Always:** t1866 목록의 **모든** 조건을 실행한다(빈 목록은 실패로 기록, 조용한 성공 금지). 각 조건 응답은 source `t1859`로 통합해 기존 `merge_candidate_sources`·`candidate_source_contrib` 계약(weight 합계 1, M≤150 절단)을 그대로 사용한다. 일부 조건이 실패하면 성공한 조건만으로 후보를 구성하고 실패 조건 목록을 stage metadata로 남겨야 하며, 전부 실패했을 때만 기존 t1856 폴백을 시도한다. `selection_input_hash`는 조건 실행 순서대로 통합 raw에 대해 재현 가능해야 한다. 조건별 분해 저장은 없으며, `candidate_source_contrib.source` 도메인은 기존 `t1859|t1852|t1856`을 유지한다.

**Never:** 스키마·마이그레이션·`candidate_source_contrib`를 변경하지 않는다. `query_index`당 별도 run/stage를 만들지 않는다. t1859 조건 호출 실패 시 해당 조건만 위해 t1856 폴백을 일으키지 않는다. `LS_QUERY_INDEX` 환경변수 신규 사용을 허용하지 않는다.

## I/O & Edge-Case Matrix

| Scenario | Input / State | Expected Output / Behavior | Error Handling |
|----------|--------------|---------------------------|----------------|
| HAPPY_PATH | t1866이 조건 8개 반환, 전부 t1859 성공 | 8개 결과 records 통합 → 선별 → candidates success | 실패 조건 없음, metadata에 조건 수 기록 |
| PARTIAL_FAILURE | 조건 8개 중 2개 t1859 실패(HTTP/예외) | 성공 6개으로 후보 구성, stage는 `partial` | 실패 조건 `query_index`+`result_code`를 metadata로 기록 |
| ALL_FAILED | 조건 8개 전부 t1859 실패 | t1856 폴백 시도(기존 경로) | 폴백 성공 시 `fallback_used`, 실패 시 `CANDIDATE_SOURCES_EXHAUSTED` |
| EMPTY_CONDITION_LIST | t1866이 0개 조건 반환 | 후보 0건 `candidates` stage는 failed | `result_code: CONDITION_LIST_EMPTY` 기록 |
| T1866_FAILURE | t1866 자체 실패(예외/HTTP 오류/빈 응답) | 후보 0건 stage failed | `result_code: CONDITION_LIST_UNAVAILABLE` 기록 |

</frozen-after-approval>

## Code Map

- `apps/batch/__main__.py:61` -- `query_index = os.environ.get("LS_QUERY_INDEX")` → `condition_search_user_id = _require_env("LS_CONDITION_SEARCH_USER_ID")`로 교체해 빈 값 재발 방지. `run_scheduled_batch(...)` 인자도 교체.
- `apps/batch/candidate_stage.py:45-146` -- `run_candidate_stage`에 `condition_search_user_id` 파라미터 추가. t1866 조회 → 조건 목록 추출 → 조건별 t1859 직렬 호출 → `_response_records` 결과를 `{"t1859": combined_records}`로 합쳐 기존 `merge_candidate_sources` 호출(`:124`). 기존 `query_index` 파라미터·t1856 폴백 경로(`:93-121`)는 하위 호환용 단일 경로로 유지. `_response_records`(`:36-42`)는 t1866OutBlock1 추출 미지원이므로 t1866 전용 추출이 필요하거나 재사용.
- `apps/batch/scheduler.py:163,213-221` -- `query_index` 인자를 `condition_search_user_id`로 교체해 candidate_stage로 전달.
- `apps/batch/ls_client.py:24-31` -- `DEFAULT_PATH_BY_TR`에 `"t1866": "/stock/item-search"` 추가(path 명시 호출 불필요).
- `.github/workflows/scheduled-batch.yml:95` -- `LS_QUERY_INDEX: ${{ secrets.LS_QUERY_INDEX }}` → `LS_CONDITION_SEARCH_USER_ID: ${{ secrets.LS_CONDITION_SEARCH_USER_ID }}`.
- `tests/batch/test_candidate_stage.py` -- 단일 `query_index` 경로 테스트(`:150-156`)는 유지, 복수 조건·부분 실패·전체 실패·t1866 실패·빈 목록 테스트 추가.
- `tests/batch/test_main.py:123,163` -- fake `run_scheduled_batch` 시그니처에 새 인자 반영.
- `packages/domain/domain/candidate_selection.py:164-231` -- `merge_candidate_sources` 재사용(변경 없음). 동일 source 내 종목 중복은 최대 거래대금 채택·excluded 증가로 처리됨.

## Tasks & Acceptance

**Execution:**
- [x] `apps/batch/candidate_stage.py` -- `run_candidate_stage`를 확장해 `condition_search_user_id`가 주어지면 t1866 조회(재사용 추출 함수) → 각 조건 t1859 직렬 호출 → 성공/실패 분기 → `{"t1859": records}` 통합 선별. 실패 조건 metadata·`CONDITION_LIST_EMPTY`/`CONDITION_LIST_UNAVAILABLE` result_code·전부 실패 시에만 기존 폴백 유지.
- [x] `apps/batch/__main__.py` -- `LS_QUERY_INDEX` → `LS_CONDITION_SEARCH_USER_ID`(`_require_env`)로 교체하고 `run_scheduled_batch` 호출 인자 갱신.
- [x] `apps/batch/scheduler.py` -- `condition_search_user_id` 파라미터로 교체·전달.
- [x] `apps/batch/ls_client.py` -- `DEFAULT_PATH_BY_TR`에 t1866 등록.
- [x] `.github/workflows/scheduled-batch.yml` -- 시크릿명 교체.
- [x] `tests/batch/test_candidate_stage.py` -- I/O 매트릭스 각 행 단위 테스트 추가(복수 조건 성공, 부분 실패 metadata, 전부 실패→폴백, 빈 목록, t1866 실패).
- [x] `tests/batch/test_main.py` -- fake 시그니처 갱신 + `LS_CONDITION_SEARCH_USER_ID` 필수 처리 검증.

**Acceptance Criteria:**
- Given `LS_CONDITION_SEARCH_USER_ID`가 설정되어 있고, when 배치를 실행하면, then t1866이 반환한 전체 조건이 각각 t1859로 호출되고 그 결과가 통합 선별되어 저장된다(조건 수는 stage metadata에 기록).
- Given 실행할 조건이 0개면, when candidates stage를 완료하면, then `failed`와 `CONDITION_LIST_EMPTY`가 기록된다.
- Given 일부 조건만 실패하면, when candidates stage를 완료하면, then 성공 조건의 후보만 저장되고 `partial` + 실패 조건별 `query_index`/`result_code` metadata가 기록되며 폴백은 호출되지 않는다.
- Given 전체 조건이 실패하면, when candidates stage를 완료하면, then 기존 t1856 폴백이 시도되고 그 결과에 따라 `fallback_used`/`CANDIDATE_SOURCES_EXHAUSTED`가 기록된다.
- Given 유효 조건으로 실행하면, when 후보를 검증하면, then source 도메인·weight 합계·M≤150 절단·`selection_input_hash` 재현성이 기존 계약과 동일하다.
- Given `LS_QUERY_INDEX`가 없어도, when 배치를 실행하면, then 후보 수집이 성공한다(더 이상 빈 query_index로 t1859를 호출하지 않는다).

## Spec Change Log

<!-- Empty until the first bad_spec loopback in step-04. -->

## Review Triage Log

<!-- Append-only. Populated by step-04 on every review pass: each dismissed finding with the
     reason that disposed of its claim. Empty until the first review pass. -->

- 판정: patch 3건(medium 1, low 2)을 적용, defer 4건, dismissed 13건으로 분류했다. bad_spec·intent_gap은 없다.

  **Dismissed (검증으로 반박 또는 기존 동작 계약):**
  - "전부 OK인데 전 조건 0건이면 SUCCESS로 조용히 종결될 수 있다" — 사고의 원인은 빈 query_index였고 이제 제거됨. 유효 조건들이 실제로 0건을 반환하는 것은 정상 검색 결과(실측에서도 katcrow 0005/0007이 0건). 빈 query_index 보호와 조건 실행 자체가 목표의 핵심이며, 0건 성공은 `test_empty_success_is_not_failed`의 기존 계약과 일치.
  - "bundle 성공 경로가 `result_code="OK"`를 하드코딩" — `LsClient`는 HTTP 성공 시 항상 `result_code="OK"`를 세팅(candidate_stage.py:213)하므로 단일 경로의 `active_response.result_code`와 사실상 동일. 결과 차이가 없음.
  - "`params`/`query_index`가 condition_search_user_id와 함께 주어지면 조용히 무시" — `__main__.py:125`는 user_id 단독 전달이며, 스펙 자체가 "user_id가 None일 때만 query_index 사용"이라 명시. 두 경로는 상호배타적으로 설계됨.
  - "새 필수 env 때문에 GH secret `LS_CONDITION_SEARCH_USER_ID`가 모든 cron의 하드 전제조건" — 반은 사실이지만 결함 아님: 미등록 시 이전처럼 조용히 후보 0건이 아닌 명시적 실패(SystemExit)로 바뀌어 관측 가능. 시크릿 등록은 배포 절차(deferred로 기록).
  - "프로덕션 단일 query 경로가 dead code가 되어 두 경로가 드리프트" — 스펙이 명시적으로 하위 호환·디버그용 유지 요구에서 비롯된 의도적 설계.
  - "serial fan-out이 lease 300s 초과" — 실측 조건 8개·1건/초·budget 30s로 ~9s 내 완료. 조건 수 폭증은 dehydrated(pagination과 함께 deferred 기록).
  - "조건 폭증 시 pagination 미처리" — 실측 8건이 1페이지 내에 모두 존재. deferred로 기록.
  - "partial+`unprocessed_count=0`이 기존 불변식과 다름" — 기존 single 경로의 partial 계약(unprocessed>0)은 유지되고, 조건 묶음의 실패는 metadata(condition_failed/failed_conditions)로 기록됨. 혼동 소지는 있으나 결과값 보전은 metadata가 담당.
  - "`_condition_query_indexes`가 블록 query_index 공백을 조용히 skip" — 실측 응답의 모든 조건 블록은 유효 query_index 보유. 공백 query_index는 서버저장검색 조건 생성 규칙상 존재하지 않으며 단위 테스트에서 0건·빈 응답 등 엣지는 커버됨.
  - "ls_client.request가 None을 반환하면 `response.ok` AttributeError" — `CandidateClient` 계약이 LsResponse 반환을 보장(기반 클래스도 항상 LsResponse 반환), 실제 호출 경로에 None 반환 구현체가 없음. 기존 단일 경로 코드도 동일 구조로 이상 경로만 상속.
  - "t1866 성공 응답 body에 인식 불가 키 → dict 1건이 excluded" — `_response_records`는 인식 키를 우선 추출하므로 dict 전체가 항상 저장되는 것은 아님. 실측 응답 shape(t1859OutBlock1/t1866OutBlock1 배열) 확인으로 반박.
  - "Code Map 라인번호가 구현 후 어긋남" — 스펙 문서의 참조 정확도 문제일 뿐 구현 대상이 아님(리뷰 1 pass 후 상태). 코드 Map은 구현 전 안내용이며 발견 지점 나열 순서상 차이 없음.
  - "t1866 0건 계정이 OutBlock1 생략 시 CONDITION_LIST_UNAVAILABLE 오판" — 실측 정상 응답은 t1866OutBlock1 배열을 반환하고, 빈 배열일 때만 `()`로 정상 처리됨. OutBlock1 자체를 생략한 형태는 실측되지 않았으며 이 경우 UNAVAILABLE이 안전한 기본값(조용한 EMPTY 오판보다 관측 가능).

## Design Notes

기존 `run_candidate_stage`의 폴백 구조는 1차 응답 단일 실패를 전제로 한다. 이번 변경은 그 전제를 "조건 묶음"으로 확장한다:

- 성공 조건 ≥1 → 폴백 없이 통합 선별. stage 결과 `result.metadata`에 `condition_count`(전체), `condition_succeeded`, `condition_failed`와 실패 배열을 넣는다.
- 성공 조건 =0 → 기존 폴백 블록(`:93-121`)으로 이동해 t1856 폴백을 일으킨다. 이때 실패의 원인이 된 각 조건의 `result_code`를 `t1859_result_code` 대신 함께 기록할 수 있게 단일 실패 metadata 형태에 누적한다(복수값은 쉼표 결합 또는 목록).
- `query_index` 단일 파라미터는 기존 테스트·수동 디버그 호출을 위해 유지하되, `condition_search_user_id`가 None일 때만 기본 경로로 사용한다(기존 동작 보존).
- t1866 응답에서 조건 목록은 `t1866OutBlock1[].query_index`로 추출하고, 빈 응답(`{"rsp_cd":"","rsp_msg":""}`)이면 `CONDITION_LIST_UNAVAILABLE`로 처리해 빈 query_index로 t1859를 호출하지 않는다.

## Verification

**Commands:**
- `uv run --with pytest pytest tests/batch/test_candidate_stage.py tests/batch/test_main.py -q` -- expected: new multi-condition tests + existing single-index tests pass.
- `uv run --with pandas --with numpy --with pyarrow --with pytest pytest tests/domain tests/batch -q` -- expected: domain/batch regression passes unchanged.
- `uv run --with pandas --with numpy --with pyarrow --with pytest pytest backtest -q` -- expected: backtest regression passes unchanged.
- `git diff --check` -- expected: no whitespace errors.

**Manual checks (if no CLI):**
- 실제 `LS_CONDITION_SEARCH_USER_ID=katcrow`로 t1866 → 전체 조건 조회 → 각 조건 t1859 성공을 로컬 스크립트로 확인한 뒤, GH Actions dispatch 실행에서 후보 수집 성공과 `condition_count` metadata를 superset 운영 DB에서 확인한다.

## Suggested Review Order

**엔트리 포인트 — 조건 묶음 경로의 접근 이해**

- 모든 조건을 t1866으로 조회해 각각 t1859로 직렬 실행하는 핵심 분기 허브
  [`candidate_stage.py:361`](../../apps/batch/candidate_stage.py#L361)

**조건 묶음 실행·실패 분기**

- t1866 호출·조건 추출·성공/실패 집계 후 통합 선별·폴백 결정을 담은 본체
  [`candidate_stage.py:217`](../../apps/batch/candidate_stage.py#L217)
- 전 조건 실패 시에만 t1856 폴백, 실패 원인 코드를 t1859_result_code에 누적
  [`candidate_stage.py:290`](../../apps/batch/candidate_stage.py#L290)
- empty/파싱 불가 응답을 거부해 빈 query_index로 t1859 호출을 원천 차단
  [`candidate_stage.py:67`](../../apps/batch/candidate_stage.py#L67)

**stage 종결·저장 계약**

- 통합 선별·candidates 저장·success/partial/failed 기록을 단일화한 도우미
  [`candidate_stage.py:116`](../../apps/batch/candidate_stage.py#L116)
- 부분 실패 시 failed_conditions metadata로 실패 조건을 보존하는 partial 종결
  [`candidate_stage.py:263`](../../apps/batch/candidate_stage.py#L263)

**배선 — env·스케줄러·워크플로**

- `LS_QUERY_INDEX` 대신 `LS_CONDITION_SEARCH_USER_ID`를 필수로 읽는 진입점
  [`__main__.py:61`](../../apps/batch/__main__.py#L61)
- 스케줄러 인자 검증 없이 candidate stage로 그대로 전달
  [`scheduler.py:163`](../../apps/batch/scheduler.py#L163)
- GitHub Actions 시크릿명 교체(등록 누락 시 명시적 실패)
  [`scheduled-batch.yml:95`](../../.github/workflows/scheduled-batch.yml#L95)
- t1866 요청이 REST path 없이도 공통 클라이언트가 라우팅하도록 등록
  [`ls_client.py:30`](../../apps/batch/ls_client.py#L30)

**테스트**

- 조건 8개 직렬 실행·부분 실패 metadata·전부 실패 폴백·빈 목록/실패 목록 커버
  [`test_candidate_stage.py:265`](../../tests/batch/test_candidate_stage.py#L265)
- scheduler→candidate_stage의 user_id 전달 홉이 끊겨도 잡히게 고정한 배선 테스트
  [`test_scheduler.py:335`](../../tests/batch/test_scheduler.py#L335)
- env 필수화·CLI 전달 검증
  [`test_main.py:26`](../../tests/batch/test_main.py#L26)

> Ctrl+click (Cmd+click on macOS) the links in the Suggested Review Order to jump to each stop.