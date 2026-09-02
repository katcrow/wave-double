---
title: '후보 태깅 stage & 저장'
type: 'feature'
created: '2026-09-02'
status: 'done'
review_loop_iteration: 0
followup_review_recommended: true
baseline_revision: '73801f2d2322f85aef2215f4211041b145b4b3f1'
context:
  - '{project-root}/_bmad-output/implementation-artifacts/epic-2-context.md'
warnings: [oversized]
deferred:
  - summary: >-
      candidate_tags 일괄 upsert가 단일 batch POST라 한 행의 실패(FK 위반 등)가
      계산된 다른 모든 태그까지 전부 폐기시킨다.
    evidence: |-
      apps/batch/candidate_tags_repository.py의 upsert_tags는 all_tags 전체를
      한 번의 POST로 보내며, 실패 시 tags_stage 전체가 TAGS_PERSIST_FAILED로
      귀결된다. candidates/candidate_source_contrib의 write_candidates도 동일하게
      attempt 단위 단일 upsert이므로 이 스토리에 국한된 새 패턴이 아니라 배치
      파이프라인 전반의 기존 관례다. 종목별 부분 성공 저장으로 바꾸려면 저장
      계층 설계를 다시 논의해야 해 이번 스토리 범위를 벗어난다.
    location: apps/batch/candidate_tags_repository.py
    severity: medium
  - summary: >-
      태깅 stage(OHLCV 확보/갱신 포함)의 실행 시간이 길어지면 lease_seconds
      기본값(300초) 안에 못 끝나 lease가 만료될 위험이 있다.
    evidence: |-
      LS API TR별 1건/초 제한 하에서 신규 편입 종목이 많으면 initialize_new_ticker_history
      호출만으로도 수십~수백 초가 소요될 수 있다. run_tags_stage 시작부의 write_stage
      호출이 만료된 lease로 실패하면 예외가 상위(main())까지 전파돼 UNHANDLED_EXCEPTION으로
      종료된다. heartbeat_attempt를 스테이지 도중 호출하는 설계는 이번 스토리 범위 밖(모든
      장시간 stage에 공통되는 예산 설계 문제)이다.
    location: apps/batch/tags_stage.py
    severity: medium
  - summary: >-
      write_stage RPC는 tags stage가 candidates 완료 이후에만 시작되도록 DB
      레벨에서 강제하지 않는다 — 순서 보장은 scheduler.py 호출 순서에만 의존한다.
    evidence: |-
      write_stage(202609021800)는 상태 전이(pending→running→terminal)와
      fence/lease만 검증하며, p_stage='tags' 시작 전에 stage_status.candidates가
      success/partial인지는 확인하지 않는다. 현재 호출자가 scheduler.py 하나뿐이라
      실질 위험은 낮지만, 향후 재시도 경로나 수동 RPC 호출이 생기면 순서가
      깨질 수 있다.
    location: infra/supabase/migrations/202609021800_allow_multistage_write_stage.sql
    severity: low
  - summary: >-
      candidate_tags에 attempt_run_id 단일 컬럼 인덱스만 추가돼, Story 2.8(소멸
      판정)이 필요로 할 candidate_id 기준 attempt 간 조회나 Epic 3의 strategy/date
      기준 조회를 지원하지 않는다.
    evidence: |-
      candidate_tags_attempt_idx는 attempt_run_id만 커버한다. 소멸 판정·집계
      쿼리 패턴은 아직 확정되지 않았고 각 후속 스토리(2.8, Epic 3)가 자신의
      접근 패턴에 맞는 인덱스를 추가하는 편이 낫다.
    location: infra/supabase/migrations/202609021600_create_candidate_tags.sql
    severity: low
---

<intent-contract>

## Intent

**Problem:** 후보 모집단(Epic 1 `candidates`)은 확보되지만, 전략 A/B/C 시그널을 계산해 태깅하고 저장하는 실제 배치 stage가 없어 대시보드가 노출할 태깅 데이터가 없다. `daily_ohlcv` 확보(Story 2.1/2.2)와 `compute_abc`(Story 2.3)도 아직 `apps/batch/scheduler.py`에 연결되지 않았다(각 스토리가 Story 2.5에 위임).

**Approach:** 후보별로 `daily_ohlcv`(없으면 확보/증분 갱신) → `compute_abc` 순으로 시그널을 계산해 `candidate_tags`에 저장하는 `tags` stage를 신설하고, `run_candidate_stage` 성공/부분성공 뒤 `run_scheduled_batch`에서 ohlcv 확보/갱신 → tags stage 순으로 실행하도록 배선한다. `publish_attempt`/`get_dashboard_snapshot`을 확장해 `tags` stage를 발행 필수 조건·스냅샷 section에 포함시킨다.

## Boundaries & Constraints

**Always:**
- `candidate_tags`(tag_id PK, candidate_id, strategy `A|B|C`, signal_date, attempt_run_id, tagged_at, status `active|vanished` default `active`, params_meta jsonb, UNIQUE(candidate_id, strategy, attempt_run_id)) 마이그레이션을 추가하고, `candidate_source_contrib`와 동일하게 `foreign key (candidate_id, attempt_run_id) references candidates(candidate_id, attempt_run_id)`를 건다(참조 무결성 — candidate_id는 attempt_run_id와 합성키). RLS는 `enable row level security`만 적용(정책 없음, 기존 candidates 패턴).
- OHLCV 로더는 `daily_ohlcv` 조회 시 반드시 `trading_day=lte.{cutoff}` 필터를 적용한다(미래 거래일 데이터가 신호 계산에 유입되는 look-ahead 방지 — cutoff는 tagging 대상 `trading_day`).
- 종목별 처리 결과를 `ineligible`(이력 부족, `domain.ohlcv_cache.MIN_HISTORY_TRADING_DAYS` 미만 또는 `compute_abc`의 `INELIGIBLE_INSUFFICIENT_HISTORY`)과 `error`(로딩 실패/`SIGNAL_COMPUTE_ERROR`)로 **구분**해 집계한다. `stage-write` RPC의 `unprocessed_count`는 error만 반영하고, ineligible 개수는 `result.ineligible_count`에 별도 기록한다(둘 다 조용히 누락되지 않되, 의미가 다른 상태를 혼동하지 않는다).
- 하나 이상의 전략 태그가 부여된 종목만 저장한다. error가 하나라도 있으면 stage 결과를 `partial`, 없으면(ineligible만 있어도) `success`로 기록한다.
- `run_scheduled_batch`는 candidates stage가 `success`/`partial`일 때만 이어서 ohlcv 확보(신규: `initialize_new_ticker_history`)/증분 갱신(기존: `update_existing_ticker_history`) 후 tags stage를 실행한다. candidates가 `failed`/휴장(skip)이면 이후 stage를 실행하지 않는다(기존 조기 반환 유지).
- `batch_kind`를 `params_meta`에 포함해 close/intraday 태깅을 구분하고, close 배치 태깅만 Epic 3 outcome 생성 자격을 갖는다는 사실을 stage 결과(`result.batch_kind`)로 노출한다(자격 판정 로직 자체는 Epic 3 범위).
- `domain/run_state.py`의 `REQUIRE_STAGES`에 `Stage.TAGS`를 추가하고 `domain/stage_registry.py`에 `verify_tags`를 등록한다(둘 다 이미 `Stage.TAGS` enum·`write_stage` RPC 화이트리스트에 존재 — 애플리케이션 계약만 확장).
- `publish_attempt`는 `stage_status->>'tags' = 'success'`를 추가 게이트로 요구하고, `get_dashboard_snapshot()`은 `tags` section(`tag_count`)을 `available_partial_sections`에 포함한다.

**Never:**
- `combine_strategies`/`strategy_api`/`screen_abc.py`의 지표 로직을 변경하지 않는다.
- `vanished` 상태 판정(장중 시그널 소멸)은 구현하지 않는다 — 신규 태그는 항상 `status='active'`로 삽입한다(Story 2.8 범위).
- `candidate_outcome` 생성 자격 판정 로직 자체(Epic 3)는 구현하지 않는다 — 이 story는 배치 종류를 결과에 노출만 한다.
- 후보가 하나도 없거나 fetch 자체가 실패한 경우를 조용히 "빈 성공"으로 만들지 않는다 — 후보 목록 조회 실패는 stage `failed`로 기록한다(기존 `apps/batch/candidate_fetcher.py` 프로토타입의 예외 흡수→`[]` 반환 패턴은 채택하지 않는다).

## I/O & Edge-Case Matrix

| Scenario | Input / State | Expected Output / Behavior | Error Handling |
|----------|--------------|---------------------------|----------------|
| 정상 태깅 | 후보 N종목, 전 종목 READY+시그널 존재 | 전 종목 태깅·저장, stage `success` | No error expected |
| 일부 SIGNAL_COMPUTE_ERROR | 후보 중 일부 `compute_abc` 예외/ERROR | 정상 종목은 저장, stage `partial`, `unprocessed_count`=error 수 | 명시 partial + error 목록 |
| 이력 부족 종목 | 후보 중 일부 120거래일 미만 | 해당 종목 태깅 제외, `result.ineligible_count`에 기록, error로 집계 안 함 | No error(명시적 제외) |
| 시그널 없음 | READY이나 A/B/C 모두 미발생 | 태그 미부여, error/ineligible 아님 | No error expected |
| 후보 조회 실패 | candidate fetch RPC/REST 예외 | stage `failed`, 조용한 빈 성공 금지 | 명시 실패 |
| candidates stage 실패/휴장 | candidates `failed` 또는 skip | ohlcv/tags stage 미실행 | 조기 반환 유지 |

</intent-contract>

## Code Map

- `infra/supabase/migrations/202609021600_create_candidate_tags.sql` (신규) -- `candidate_tags` 테이블 + FK(candidate_id, attempt_run_id)→candidates + RLS enable. `202609011800_harden_candidate_rls.sql` 패턴 재사용.
- `infra/supabase/migrations/202609021700_add_tags_to_publish_and_snapshot.sql` (신규) -- `publish_attempt`(`202609012100_harden_run_and_candidate_contracts.sql`의 최신 버전 기반 `create or replace`)에 tags 게이트 추가, `get_dashboard_snapshot()`(`202609020000_create_dashboard_snapshot.sql` 최신본 기반)에 tags section 추가.
- `packages/domain/domain/run_state.py:53` (`REQUIRE_STAGES`) -- `(Stage.CANDIDATES, Stage.TAGS)`로 확장.
- `packages/domain/domain/stage_registry.py:13-20` -- `verify_tags` 추가, `StageRegistry.__init__` 기본 매핑에 등록.
- `apps/batch/candidate_stage.py:43-145` (`run_candidate_stage`) -- 후보 저장 패턴(`gateway.write_stage` PENDING→RUNNING→SUCCESS/PARTIAL/FAILED, `unprocessed_count`) 참고. 수정하지 않음.
- `apps/batch/run_state.py:132-167` (`RunStateGateway.write_stage`) -- tags stage 기록에 그대로 재사용(신규 RPC 불필요, `p_stage="tags"`는 이미 DB 화이트리스트에 존재).
- `apps/batch/ohlcv_cache.py` (전체, Story 2.1/2.2 산출물) -- `initialize_new_ticker_history`/`update_existing_ticker_history`/`SupabaseOhlcvCacheRepository`를 그대로 호출해 태깅 전 `daily_ohlcv`를 확보/갱신한다(신규 구현 아님, 오케스트레이션 연결만).
- `packages/domain/domain/ohlcv_cache.py` -- `MIN_HISTORY_TRADING_DAYS`(120), `OhlcvCacheStatus` 재사용(하드코딩 금지).
- `backtest/strategy_api.py:62` (`compute_abc(frame, *, ticker="") -> StrategyResult`) -- 유일한 시그널 계산 진입점. `StrategyResult.status`(READY/INELIGIBLE_INSUFFICIENT_HISTORY/ERROR)·`signals`(전략별 bool Series, 마지막 봉 폐기 필터 기반영)·`error`(SIGNAL_COMPUTE_ERROR) 계약.
- `apps/batch/candidate_fetcher.py` (신규 재작성 대상) -- `candidates` 테이블에서 `attempt_run_id`로 `candidate_id`+`ticker` 재조회. **실패 시 예외를 흡수하지 않고 전파**하도록 재작성(현 프로토타입의 `except Exception: return []` 제거).
- `apps/batch/ohlcv_cache_loader.py` (신규 재작성 대상) -- `daily_ohlcv`→DataFrame 로더. **`trading_day<=cutoff` 필터 추가**(현 프로토타입은 전체 이력을 무필터 조회).
- `apps/batch/candidate_tags_repository.py` (신규 재작성 대상) -- `candidate_tags` upsert(`on_conflict=candidate_id,strategy,attempt_run_id`). 구조는 기존 프로토타입 유지.
- `apps/batch/tags_stage.py` (신규 재작성 대상) -- stage 오케스트레이터. ineligible/error 분리 집계로 재작성(현 프로토타입은 둘을 `error_count`로 합산).
- `apps/batch/scheduler.py:99-108` (`run_scheduled_batch`) -- `run_candidate_stage` 뒤 ohlcv 확보/갱신 + tags stage 호출을 추가(현재 미배선 — Story 2.1/2.2/2.5 명시적 위임 지점).
- `apps/batch/__main__.py:52-76` (`run`) -- LS daily bar provider(t8410)·`SupabaseOhlcvCacheRepository`·`SupabaseCandidateTagsRepository`·candidate fetcher 구성을 추가해 `run_scheduled_batch`에 전달.
- `tests/batch/test_candidate_stage.py`, `tests/batch/test_ohlcv_cache.py` -- Fake gateway/LS 클라이언트 컨벤션 재사용.
- `tests/sql/test_dashboard_snapshot.sql` -- tags section 반영 케이스 추가 참고 대상.

## Tasks & Acceptance

**Execution:**
- `infra/supabase/migrations/202609021600_create_candidate_tags.sql` -- `candidate_tags` 테이블(FK 포함) 생성 -- AC1.
- `infra/supabase/migrations/202609021700_add_tags_to_publish_and_snapshot.sql` -- `publish_attempt`/`get_dashboard_snapshot` 확장 -- AC3.
- `packages/domain/domain/run_state.py`, `packages/domain/domain/stage_registry.py` -- `REQUIRE_STAGES`/`verify_tags` 추가 -- AC3.
- `apps/batch/candidate_fetcher.py`, `apps/batch/ohlcv_cache_loader.py`, `apps/batch/candidate_tags_repository.py`, `apps/batch/tags_stage.py` -- tags stage 구현(ineligible/error 분리, look-ahead 방지) -- AC2/AC4/AC5.
- `apps/batch/scheduler.py`, `apps/batch/__main__.py` -- ohlcv 확보/갱신 + tags stage를 배치 파이프라인에 배선 -- AC2.
- `tests/batch/test_tags_stage.py`, `tests/batch/test_scheduler.py`(있으면 확장, 없으면 신규) -- I/O 매트릭스 6개 시나리오 단위 테스트 -- 전체 AC.
- `tests/sql/test_candidate_tags.sql` -- FK/UNIQUE 제약 검증(pgTAP, 기존 `test_candidates.sql` 패턴) -- AC1.

**Acceptance Criteria:**
- Given migration 적용, when `candidate_tags` 스키마를 조회하면, then PK/FK/UNIQUE(candidate_id,strategy,attempt_run_id)가 정확히 존재한다.
- Given screen(candidates) stage 성공/부분성공, when tags stage가 실행되면, then 후보별 `daily_ohlcv`+`compute_abc` 호출로 시그널이 계산되고 발생 종목에 다중 태그가 부여·저장된다.
- Given tags stage 성공, when `write_stage`(tags,success) 호출 후 `get_dashboard_snapshot()`을 조회하면, then `tags`가 `available_partial_sections`에 포함되고 `publish_attempt`가 이제 tags success도 요구한다.
- Given 재현성 확인, when 저장된 태그의 `params_meta`를 조회하면, then 계산 시점 파라미터 스냅샷이 보존돼 있다.
- Given 일부 종목 `SIGNAL_COMPUTE_ERROR`, when tags stage 결과를 기록하면, then `partial`+`unprocessed_count`=error 수로 기록되고 정상 종목 태그는 그대로 저장된다.

## Spec Change Log

## Review Triage Log

### 2026-09-02 — Review pass
- intent_gap: 0
- bad_spec: 0
- patch: 6 (high 1, medium 2, low 3)
- defer: 4 (high 0, medium 2, low 2)
- dismissed:
  - candidate_fetcher.fetch()가 후보 0건을 반환해도 tags stage가 조용히 success로 끝난다(Never 규칙 위반 주장) — candidates stage가 write_candidates를 커밋한 뒤에야 tags stage가 시작되므로 같은 Postgres에서 read-committed 재조회는 즉시 그 행을 본다(복제 지연 없음). candidates>0인데 fetch가 0을 반환하는 경로는 이 설계에서 실현 가능한 경로가 없다.
  - SupabaseOhlcvCacheLoader.load_batch의 MIN_HISTORY_TRADING_DAYS 검사가 실제 호출 경로(load_ohlcv 직접 호출)에서 쓰이지 않는다 — compute_abc 자신이 동일 상수로 이력 부족을 권위 있게 판정하고 tags_stage가 그 결과(status)를 그대로 신뢰하므로 기능적 공백이 없다. load_batch는 그대로도 무해한 미사용 유틸리티다.
  - I/O 매트릭스 "SIGNAL_COMPUTE_ERROR" 행의 "명시 partial + error 목록" 문구가 종목별 에러 목록 미구현을 근거로 결함이라는 주장 — epics.md 원 AC(source of truth)는 "에러가 발생한 종목 수가 unprocessed_count로 함께 저장된다"만 요구하며 종목별 목록은 요구하지 않는다. 이 스토리의 Acceptance Criteria 섹션(epics.md와 일치)도 개수만 요구한다. 매트릭스 셀의 "+error 목록"은 계획 단계에서 spec-2-4 골든 픽스처 표현을 차용한 서술적 과잉 명세이며, 자매 stage(candidate_stage.py의 UNPROCESSED_ITEMS)도 개수만 보고하는 기존 관례와 일치한다.
  - candidate_fetcher가 중복 candidate_id 행을 반환할 수 있어 upsert가 깨질 수 있다는 주장 — candidate_id는 candidate_stage.py에서 uuid4()로 매 후보마다 새로 생성되고 candidates 테이블은 (candidate_id, attempt_run_id) UNIQUE 제약을 가지며, merge_candidate_sources가 저장 전 ticker 기준으로 이미 dedupe한다. 이 경로에서 중복 candidate_id 행이 나올 실현 가능한 경로가 없다.
  - candidate_fetcher.py의 row["candidate_id"]/row["ticker"] None 캐스팅 위험 주장 — candidates 테이블 스키마가 candidate_id를 PK로, ticker를 length>0 not-null CHECK로 강제해 PostgREST가 None을 반환할 스키마 경로가 없다.
  - get_dashboard_snapshot의 available_partial_sections가 tag_count=0인 published run에도 무조건 'tags'를 포함해 "허위로 가용 표시"한다는 주장 — 기존 'candidates' section도 candidate_count=0인 완결 run에 대해 동일하게 무조건 포함되는 사전 확립된 관례(이 diff 이전부터)이며, "section이 계산 완료됐다"와 "0건이다"는 서로 다른 정상 상태로 UI가 tag_count 자체로 구분한다.
  - iloc[-2]/index[-2] "마지막-1 봉" 관례가 tags_stage.py 두 곳(전략 판정, signal_date 추출)에 공유 상수 없이 중복된다 — 기능 결함이 아닌 사소한 리팩터링 기회이며 기존(스태시된) 프로토타입도 동일한 형태였다.
  - migration 202609021800의 정확한 버그 재현 시나리오("candidates 이후 tags의 pending→running이 STALE_FENCE_OR_LEASE로 거부되던 문제")를 이름이 명시하는 전용 테스트가 없다는 주장 — test_candidate_tags.sql·test_dashboard_snapshot.sql이 정확히 그 전이 경로를 실행해 통과를 확인하므로 커버리지 공백이 아니라 네이밍 선호의 문제다.
  - 부정확한 ticker(isalnum 실패)를 ineligible이 아닌 error로 분류하는 것이 "ineligible/error 구분을 훼손한다"는 주장 — ineligible은 정상적인 이력 부족(비즈니스 상태)이고 형식이 잘못된 ticker는 데이터 품질 문제이므로 error로 분류하는 것이 오히려 정확하다.
  - stage_registry.verify_tags가 candidate_tags 실체를 검증하지 않고 이름만 확인한다는 주장 — verify_candidates도 이 스토리 이전부터 동일한 얕은 검증이며, 검증 권위가 write_stage RPC에 있다는 사실은 docstring에 이미 명시돼 있다. 이 스토리가 새로 악화시킨 부분이 없다.
- addressed_findings:
  - `[high]` `[patch]` tags stage 실패(후보 재조회 실패·전 종목 SIGNAL_COMPUTE_ERROR·태그 저장 실패)가 run_scheduled_batch의 반환값(SchedulerResult)·CLI 종료 코드·runs.status/finished_at 어디에도 반영되지 않아, 실제로는 태깅이 실패해도 배치 프로세스가 status=success·exit 0으로 끝난다 — apps/batch/scheduler.py가 run_tags_stage의 결과를 SchedulerResult에 반영하도록, 그리고 신규 migration으로 write_stage의 status/finished_at 갱신 로직이 tags stage 종결에도 반응하도록 수정.
  - `[medium]` `[patch]` SupabaseOhlcvCacheLoader.load_ohlcv의 DataFrame 구성(컬럼 rename·인덱스 설정·숫자 변환)이 HTTP 호출을 감싸는 try/except 밖에 있어, daily_ohlcv의 형식이 어긋난 행이 있으면 예외가 tags_stage 루프까지 그대로 전파된다 — try/except 범위를 DataFrame 구성까지 확장해 실패 시 OhlcvCacheStatus.ERROR를 반환하도록 수정.
  - `[medium]` `[patch]` 신규 tests/sql/test_candidate_tags.sql이 .github/workflows/test.yml의 SQL 픽스처 실행 목록에 배선되지 않아 CI에서 실행되지 않는다 — test.yml의 sql-outbox-tests 목록에 추가.
  - `[low]` `[patch]` TAGS_PERSIST_FAILED 결과(write_stage에 기록되는 result와 반환되는 TagsStageResult 양쪽)가 실제로는 아무 것도 저장되지 않았는데도 tagged_count=len(tagged_candidates)로 기록해 오해를 준다 — 두 위치 모두 tagged_count=0으로 수정.
  - `[low]` `[patch]` tests/batch/test_scheduler.py가 candidates stage의 "partial" 결과에서도 ohlcv/tags 파이프라인이 배선되는지 검증하는 테스트가 없다 — partial 분기 커버 테스트 추가.
  - `[low]` `[patch]` run_tags_stage의 tags_repo 인자와 run_scheduled_batch의 tags_repository 인자가 다른 신규 의존성들과 달리 Protocol 타입 없이 구체 클래스/Any로 선언돼 있다 — 두 곳 모두 최소 Protocol을 정의해 타입 힌트를 통일.

## Design Notes

기존 미커밋 프로토타입(`apps/batch/{candidate_fetcher,ohlcv_cache_loader,candidate_tags_repository,tags_stage}.py`, 두 마이그레이션)이 이번 스토리 범위와 거의 일치해 구조 참고용으로 stash 보관했다(`git stash list`). 그대로 채택하지 않는 이유 3가지: ① `ohlcv_cache_loader`가 `trading_day` 인자를 받고도 필터링하지 않아 look-ahead 위험이 있다. ② `tags_stage`가 "이력 부족"(정상적 제외 계약)과 "계산 오류"(진짜 실패)를 `error_count` 하나로 합쳐 `unprocessed_count`에 반영해, AD-5 "조용한 누락 금지"의 취지(실패와 정상 제외를 구분해 관찰 가능하게)를 흐린다. ③ `candidate_fetcher`가 모든 예외를 삼켜 빈 리스트를 반환해, 후보 조회 자체가 실패해도 tags stage가 "후보 0건 성공"으로 조용히 종결될 수 있다. ④ (구조적 공백) `scheduler.py`/`__main__.py` 어디에도 tags stage·ohlcv 확보/갱신 호출이 배선되지 않아, 코드가 존재해도 실제 배치에서 전혀 실행되지 않는다 — 이번 스토리의 핵심 결손.

## Verification

**Commands:**
- `uv run --with pandas --with numpy --with pyarrow --with httpx --with pytest pytest tests/batch tests/domain -q` -- expected: 신규 tags stage 테스트 포함 전체 통과, 기존 회귀 없음.
- `uv run --with pandas --with numpy --with pyarrow --with httpx --with pytest pytest backtest -q` -- expected: golden fixture(Story 2.4) 포함 기존 43+개 테스트 회귀 없음(compute_abc 미변경 확인).
- `git diff --check` -- expected: whitespace 오류 없음.

**Manual checks (if no CLI):**
- 신규 마이그레이션 2건을 Supabase 프로젝트(qqhjeumlecaudsiqhhdu)에 직접 적용하고, `candidate_tags` 스키마·FK·`publish_attempt`/`get_dashboard_snapshot` 갱신을 실제 조회로 확인한다(단일 프로젝트, dev/staging 분리 없음 — 운영 적용이 곧 검증).

## Auto Run Result

- **구현 요약:** Story 2.5 후보 태깅 stage를 신설했다. `candidates` stage 성공/부분성공 뒤 `daily_ohlcv` 확보/증분 갱신(Story 2.1/2.2 산출물 재사용) → `compute_abc`(Story 2.3) 호출 → `candidate_tags` 저장 순으로 `apps/batch/scheduler.py`에 배선했다. 이력 부족(`ineligible`)과 계산 오류(`error`)를 분리 집계해 `unprocessed_count`가 진짜 실패만 반영하도록 했고, `daily_ohlcv` 조회에 `trading_day<=cutoff` look-ahead 방지 필터를 적용했다. `publish_attempt`가 `tags` stage 성공도 요구하도록, `get_dashboard_snapshot()`이 `tags` section을 반영하도록 확장했다. 리뷰에서 발견된 tags stage 실패가 배치 결과/DB 상태에 반영되지 않던 결함을 `SchedulerResult`(tags_status/tags_result_code 추가, 심각도 기준 status 합성)와 신규 migration(`write_stage`가 tags 종결에도 반응)으로 수정했다.
- **변경 파일:**
  - `apps/batch/candidate_fetcher.py` — 신규: `candidates` 재조회, 실패 시 예외 전파(흡수 금지).
  - `apps/batch/ohlcv_cache_loader.py` — 신규: `daily_ohlcv`→DataFrame 로더, look-ahead 필터, DataFrame 구성까지 포함한 예외 처리.
  - `apps/batch/candidate_tags_repository.py` — 신규: `candidate_tags` upsert adapter, `TagsRepositoryProtocol` 추가.
  - `apps/batch/tags_stage.py` — 신규: tags stage 오케스트레이터(ineligible/error 분리, params_meta 스냅샷, TAGS_PERSIST_FAILED 시 tagged_count=0 정정).
  - `apps/batch/scheduler.py` — `run_scheduled_batch`가 ohlcv 확보/갱신 + tags stage를 배선, tags 결과를 `SchedulerResult`(신규 `tags_status`/`tags_result_code` 필드, 심각도 기반 status 합성)에 반영.
  - `apps/batch/candidate_stage.py` — `CandidateStageResult`에 `fence_token`/`lease_token` 추가(tags stage가 같은 attempt lease를 이어 쓰기 위함).
  - `apps/batch/__main__.py` — 신규 어댑터(OHLCV provider/repository/loader, candidate fetcher, tags repository) 구성·전달.
  - `packages/domain/domain/run_state.py`, `packages/domain/domain/stage_registry.py` — `REQUIRED_STAGES`에 `Stage.TAGS` 추가, `verify_tags` 등록.
  - `infra/supabase/migrations/202609021600_create_candidate_tags.sql` — `candidate_tags` 테이블(합성키 FK·UNIQUE·RLS enable).
  - `infra/supabase/migrations/202609021700_add_tags_to_publish_and_snapshot.sql` — `publish_attempt` tags 게이트, `get_dashboard_snapshot()` tags section.
  - `infra/supabase/migrations/202609021800_allow_multistage_write_stage.sql` — 구현 중 발견한 버그 수정: candidates 완료 후 다른 stage의 정상 전이가 `STALE_FENCE_OR_LEASE`로 거부되던 단일-stage 가정 제거.
  - `infra/supabase/migrations/202609021900_write_stage_reacts_to_tags_completion.sql` — 리뷰에서 발견한 버그 수정: `write_stage`의 `runs.status`/`finished_at` 갱신이 `tags` stage 종결에도 반응하도록 확장.
  - `.github/workflows/test.yml` — 신규 SQL 픽스처(`test_candidate_tags.sql`)를 CI 목록에 배선.
  - `tests/batch/{test_candidate_fetcher,test_candidate_tags_repository,test_ohlcv_cache_loader,test_tags_stage}.py` — 신규 단위 테스트. `tests/batch/{test_main,test_scheduler}.py`, `tests/domain/test_run_state.py` — 신규 의존성/합성 status/`REQUIRED_STAGES` 반영 확장.
  - `tests/sql/test_candidate_tags.sql` — 신규 PK/FK/UNIQUE/CHECK/RLS pgTAP 픽스처(+ tags 실패/부분 시나리오의 runs.status 반영 검증 추가).
  - `tests/sql/{test_dashboard_snapshot,test_dispatch_outbox,test_run_lineage}.sql` — tags stage 성공 기록을 publish 전제조건에 추가.
- **리뷰 결과:** patch 6건 전부 수정(high 1, medium 2, low 3) · deferred 4건 기록(medium 2, low 2) · dismissed 9건(근거는 Review Triage Log 참조) · bad_spec·intent_gap 없음.
- **추적 리뷰 권장:** 이번 패스 patch 중 high 1건 포함 → **권장함**(score = high 존재로 즉시 true, 참고 score = 3×2(medium)+1×3(low) = 9).
- **수행한 검증:**
  - `uv run --with pandas --with numpy --with pyarrow --with httpx --with pytest pytest tests/batch tests/domain -q` → **193 passed**(패치 후 재실행, 회귀 없음).
  - `uv run --with pandas --with numpy --with pyarrow --with httpx --with pytest pytest backtest -q` → **43 passed**(compute_abc 미변경 확인).
  - `git diff --check` → whitespace 오류 없음(CRLF 안내 경고만).
  - 4개 마이그레이션(1600/1700/1800/1900) 전부 Supabase 프로젝트(qqhjeumlecaudsiqhhdu)에 직접 적용 확인(`list_migrations`로 검증) — 단일 프로젝트 정책에 따라 운영 적용이 곧 검증.
  - 라이브 Supabase에서 `candidate_tags` 스키마·FK·`publish_attempt`(`TAGS_STAGE_NOT_COMPLETE` 가드)·`get_dashboard_snapshot()`(`tag_count`/`available_partial_sections`) 트랜잭션 드라이런(롤백) 확인, tags 실패/부분 시 `runs.status` 반영 확인.
  - I/O 매트릭스 6개 시나리오 전부 전용 테스트로 커버(정상 태깅/일부 SIGNAL_COMPUTE_ERROR/이력 부족/시그널 없음/후보 조회 실패/candidates 실패-휴장 시 미실행).
- **잔여 리스크:** ① candidate_tags 일괄 upsert가 단일 batch POST라 한 행의 실패가 전부 폐기(defer, medium, 기존 batch 관례와 동일). ② 태깅 stage 실행 시간이 lease_seconds 기본값(300초)을 초과할 위험(defer, medium, 장시간 stage 공통 예산 설계 문제). ③ write_stage RPC가 tags 시작 전 candidates 완료를 DB 레벨로 강제하지 않음(defer, low, 현재 호출자가 scheduler.py 하나뿐). ④ candidate_tags 인덱스가 attempt_run_id만 커버(defer, low, Story 2.8/Epic 3가 자신의 접근 패턴에 맞게 추가 예정).
