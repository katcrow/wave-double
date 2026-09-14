# Deferred Work

## Deferred from: code review (2026-09-01)

- ~~Story 1.3: `logical_runs`와 `runs`의 RLS 정책을 확정한다. 현재 공개 API 테이블이지만 policy 없이 RLS를 활성화하면 배치·후속 dashboard read-model 경계까지 차단되므로, Story 1.8/1.10의 approved view/RPC와 함께 적용한다. 2026-09-01 실제 Supabase SQL fixture와 RPC 권한 검증은 통과했다.~~ **해결됨(2026-09-09, epic-1-retro-item-2 운영 검증).** 운영 프로젝트(`qqhjeumlecaudsiqhhdu`) 실측 결과 `logical_runs`/`runs` RLS 활성 4/4 확인. `epic-1-retro-item-2-production-verification-2026-09-09.md` 1절 표 참고.

## Deferred from: story 3.1 build verification (2026-09-03)

- ~~`tests/batch/test_scheduler.py`의 7개 테스트가 `result.status == "success"`를 기대하지만 실제로는 `"partial"`을 반환해 실패~~ **해결됨(2026-09-03, story 3.5 후속 조치).** 실제 원인은 `_STATUS_SEVERITY` 병합 로직이 아니라 `tests/batch/test_scheduler.py`의 `FakeTagsRepository`에 Story 2.8이 추가한 `sync_vanished` 메서드가 없었던 것 -- `tags_stage.py`가 태깅 성공 직후 `tags_repo.sync_vanished(run_id_str)`를 호출하는데, fake에 이 메서드가 없어 `AttributeError`가 나고 `except Exception: vanished_sync_failed = True`로 흡수되어 `error_count==0`(태깅 자체는 성공)임에도 전체 결과가 `partial`/`VANISHED_SYNC_FAILED`로 낮춰졌다. `FakeTagsRepository`에 `sync_vanished(self, run_id)`(반환 `{"vanished_count": 0}`)를 추가해 실제 `TagsRepositoryProtocol`과 일치시켜 해결. `uv run pytest` 241 passed(기존 234 + 이번에 복구된 7건).
- **(high)** `infra/supabase/migrations/202609012300_add_skip_attempt.sql`이 정의하는 `public.skip_attempt` RPC가 운영 Supabase project(`qqhjeumlecaudsiqhhdu`)에 실제로는 적용되어 있지 않다. `mcp__supabase__list_migrations` 결과에 해당 migration이 없고, `pg_proc` 직접 조회 결과도 0건으로 확인했다. 그런데 `apps/batch/run_state.py:229`는 이 함수를 `rpc("skip_attempt", ...)`로 호출하므로, 휴장일 skip 처리 경로가 실행되면 런타임에 실패한다. Story 3.1 리뷰 중 우연히 발견한, 이 스토리와 무관한 기존 운영 배포 누락이다. 원인(마이그레이션 자체가 원래 적용된 적이 없는지, 이후 어떤 변경으로 drop 되었는지)과 재적용은 별도로 처리 필요. **해결됨(2026-09-04).** 운영 project에 `public.skip_attempt(uuid, bigint, uuid, text)`를 재적용해 `pg_proc`에 존재하고, `proacl`이 `postgres`/`service_role`만 EXECUTE로 복원됨을 확인했다(휴장일 `runs` 스킵 종결 경로가 더 이상 런타임 실패하지 않는다).

## Deferred from: story 3.5 build verification (2026-09-03)

- `publish_attempt`(따라서 이 함수가 close 분기에서 호출하는 `emit_open_command`/`record_outcome_observation`/이번 스토리의 SUSPENDED 감지 루프 전체)는 여전히 어떤 실제 배치 오케스트레이터에도 연결되어 있지 않다(Story 3.1~3.4에서 반복 확인된 기존 gap과 동일). 이 상태에서는 SUSPENDED 전이가 실제로 발생해도 그것을 소비해 GitHub Issue를 생성하는 알림 배선을 추가할 방법이 없다 -- 트리거할 실제 이벤트가 없어 검증 불가능한 죽은 코드가 되기 때문이다(spec-3-5 Design Notes 참조). ~~알림 배선(Python/워크플로에서 `suspended_transitions`를 읽어 GitHub Issue를 생성하는 구현)은 `publish_attempt`의 프로덕션 배선 gap 해소 이후 별도 스토리에서 다뤄야 한다.~~ **프로덕션 배선 gap은 해소됨(2026-09-04).** `apps/batch/scheduler.py`의 `run_scheduled_batch`가 close 배치에서 candidates+tags가 모두 `success`로 끝난 경우에만 `gateway.publish()`(`publish_attempt` 3-arg)를 실제 호출하도록 배선했다. 발행 성공 시 `outcome_tracking` stage는 DB 트랜잭션 내에서 `success`로 기록되고, 발행 실패 시 `outcome_tracking: failed`로 기록해 배치를 `OUTCOME_PUBLISH_FAILED`로 종결한다(`tests/batch/test_scheduler.py`에 close 성공 발행/premarket·intraday·partial·tags-failed 미발행/발행 실패 5개 테스트 추가). **남은 항목:** `publish_attempt`가 반환하는 `suspended_transitions`(및 `tp_sl_transitions`)를 읽어 GitHub Issue 알림을 생성하는 구현은 여전히 미배선이다 -- 이제 그 이벤트가 실제로 발생 가능하므로 별도 스토리에서 다룬다.

## Deferred from: story 3.5 code review (2026-09-03)

- **(medium)** `emit_open_command`(Story 3.2, `infra/supabase/migrations/202609031501_fix_emit_open_command_review_patch.sql:57`)의 재진입 방지(ALREADY_OPEN) 가드가 `status = 'OPEN'`만 확인한다. `candidate_outcome_one_open_per_ticker_strategy_idx`는 `status='OPEN'`에만 걸린 partial unique index이고 `(ticker,strategy,entry_date)` unique 제약도 `entry_date`가 다르면 막지 못하므로, `SUSPENDED` 상태인 (ticker,strategy)를 이후 배치가 재태깅하면 새 `candidate_outcome` 행이 중복 생성될 수 있다. ~~`SUSPENDED`는 Story 3.5가 처음 실제로 도달 가능하게 만든 상태라 이전에는 이 경로가 도달 불가능했다(2026-09-03 code review, blind-hunter 발견). epics.md의 Story 3.1 AC는 OPEN 중복 방지만 명시하고 SUSPENDED 재진입은 다루지 않아 원 스펙의 공백이며, Story 3.8(correction 이벤트 메커니즘)이 SUSPENDED 복귀/재진입 정책을 정의할 때 함께 다뤄야 한다.~~ **해결됨(2026-09-04, Story 3.8의 `202609032200_add_outcome_correction_mechanism.sql`).** `emit_open_command`의 재진입 가드를 `status in ('OPEN','SUSPENDED','DELISTED')`로 넓혔고, SUSPENDED/DELISTED는 진입일과 무관하게 항상 `skipped:true`(`ALREADY_TRACKED_SUSPENDED`/`ALREADY_DELISTED`)로 재진입을 막아 중복 행 생성을 차단한다. 운영 project(`qqhjeumlecaudsiqhhdu`)에 적용돼 있고 `tests/sql/test_outcome_open_command.sql`(SUSPENDED 재태깅 스킵 시나리오)로 검증된다.
- ~~**(low)** `daily_ohlcv.close`(Story 2.1, `infra/supabase/migrations/202609021500_create_daily_ohlcv.sql`)에 양수 제약이 없어(NaN/Infinity만 배제), 전일 종가가 0이면 Story 3.5의 갭 안전망 계산(`v_prev_close <> 0` 가드)이 나눗셈 예외 대신 감지를 조용히 건너뛴다. `pricechk`도 없는 상태에서 전일 종가가 0이면 어떤 경로로도 이상이 감지되지 않는다(2026-09-03 code review, blind-hunter 발견). `daily_ohlcv` 스키마 자체의 기존 공백이며, 이 컬럼에 양수 체크 제약을 추가하는 것은 Story 2.1 스키마의 몫이다.~~ **해결됨(2026-09-14).** `infra/supabase/migrations/202609141300_add_daily_ohlcv_close_positive_check.sql`로 `check (close > 0)` 제약 추가, 기존 데이터 위반 0건 확인 후 운영 project에 적용.

## Deferred from: Story 4.1 Epic 7 contract review (2026-09-08)

- source_spec: `_bmad-output/implementation-artifacts/spec-4-1-epic7-계약-보강.md`
  summary: 컴파일된 Epic 4 context의 수동 보강 내용을 원천 planning artifact와 동기화하는 생성 파이프라인을 정리한다.
  evidence: `epic-4-context.md`는 planning artifact에서 재생성되는 캐시 문서이므로 수동으로 추가한 운영/전략 계약이 재생성 시 덮어써질 수 있다. 이번 보강에서는 유효한 최신 context를 유지했지만, 생성기 입력과 캐시 동기화 정책은 별도 프로세스 작업이다.

## Deferred from: code review of story-5-6 (2026-09-10)

- `revoke select on table ... from public, anon, authenticated`가 실제로 anon/authenticated 역할의 SELECT를 차단하는지 검증하는 자동 테스트가 없다(`infra/supabase/migrations/202609101200_create_outcome_win_rate_pf_by_strategy_source.sql`). 현재는 Supabase 대시보드 수동 확인에만 의존한다("Manual checks" 섹션). Story 5-5의 동일 view(`candidate_outcome_win_rate_pf`)부터 있던 기존 gap으로, 향후 migration이 실수로 재부여(re-grant)해도 CI가 잡지 못한다. 두 view를 함께 다루는 별도 스토리/작업에서 anon/authenticated role로 실제 select 시도 후 실패를 assert하는 SQL 테스트를 추가해야 한다. (2026-09-10 code review 후속: story 5-7의 `candidate_outcome_win_rate_pf_by_strategy_gated` view도 동일한 gap을 갖는다 — 이제 2개가 아니라 3개 view가 이 자동 테스트 부재에 해당한다.) (2026-09-10 story 5-8 code review 후속: `candidate_outcome_win_rate_pf_ci_gated` view도 동일한 gap을 가져 4개 view로 늘었다.)
- ~~`tools/check_outcome_win_rate_pf_source_parity.py`의 SQL 리터럴 파서(`_extract_value_tuples`/`_split_preserving_quotes`)가 이스케이프된 따옴표(`''`)나 따옴표로 감싼 문자열 안의 괄호를 처리하지 못한다. 5-5의 `check_outcome_win_rate_pf_parity.py`에서 그대로 상속된 패턴이며, 두 도구 모두 현재 fixture 데이터(티커 등)에는 해당 문자가 없어 실제로 유발되지 않는다. fixture에 특수문자가 포함된 값이 추가될 일이 생기면 두 도구를 함께 강화해야 한다. (2026-09-10 code review 후속: story 5-7의 `tools/check_outcome_win_rate_pf_gate_parity.py`도 동일한 `_extract_value_tuples`/`_split_preserving_quotes` 패턴을 그대로 상속한 세 번째 사본이다 — 세 도구를 함께 강화해야 한다.) (2026-09-10 story 5-8 code review 후속: `tools/check_outcome_win_rate_pf_ci_parity.py`도 동일 패턴을 상속한 네 번째 사본이다.)~~ **해결됨(2026-09-14).** 4개 사본(`check_outcome_win_rate_pf_parity.py`/`_source_parity.py`/`_gate_parity.py`/`_ci_parity.py`) 모두에서 `_extract_value_tuples`가 따옴표 상태를 추적해 문자열 안의 괄호를 무시하고, `_split_preserving_quotes`와 `_raw_to_python`이 `''` 이스케이프를 리터럴 `'`로 복원하도록 동일하게 수정했다.

## Deferred from: code review of story-5-7 (2026-09-10)

- source_spec: `_bmad-output/implementation-artifacts/spec-5-7-표본-게이트-30건-처리.md`
  summary: `tools/production_parity_baseline.json`에 이번 스토리와 무관한 사전 drift(주로 `write_stage` 함수의 `search_path`가 `public`에서 `pg_catalog`로 바뀐 것)가 `--write-baseline` 갱신 과정에서 함께 반영됐다 — 원인을 확인하고 의도된 변경인지 문서화한다.
  evidence: 운영 DB에 `pg_proc.proconfig`를 직접 질의해 `write_stage`의 실제 `search_path`가 이미 `pg_catalog`임을 확인했다. 이 스토리의 마이그레이션(`202609101300_create_outcome_win_rate_pf_gated.sql`, `202609101400_fix_gated_profit_factor_comment.sql`)은 `write_stage`를 전혀 건드리지 않으므로, 이 값 변경은 이전 스토리(추정: 5-4 전후)에서 발생한 뒤 baseline에 반영되지 않고 있던 drift가 이번 갱신에서 우연히 함께 포착된 것이다. code review 3개 레이어(blind-hunter, edge-case-hunter, verification-gap) 모두 독립적으로 이 변경을 지적했다.
  **해결됨(2026-09-14).** 원인 확인: `epic-1-retro-item-2-production-verification-2026-09-09.md` 5절에서 다중 원소 `search_path`(`pg_catalog, public`) 파서 버그를 고치는 과정 중 `epic-4-retro-item-33`이 여러 함수의 `search_path`를 `public` → `pg_catalog, public`로 통일했음을 확인했다 — `write_stage`도 그 대상 중 하나였으므로 의도된 변경이다. baseline 값은 정확하며 추가 조치 불필요.

## Deferred from: code review of story-5-8 (2026-09-10)

- source_spec: `_bmad-output/implementation-artifacts/spec-5-8-95-신뢰구간-계산-기대치-판정.md`
  summary: `tools/check_production_parity.py`의 `--write-baseline` 경로가 `captured_at` 필드를 실제 오늘 날짜 대신 하드코딩된 리터럴 문자열 `"2026-09-09"`로 기록한다(`tools/check_production_parity.py:492`). 이 스토리에서 `--write-baseline`을 실행하자 `production_parity_baseline.json`의 `captured_at`이 `2026-09-10`(직전 값)에서 `2026-09-09`로 하루 뒤로 이동했다.
  evidence: `git log -p -L492,494:tools/check_production_parity.py`로 확인한 결과 이 하드코딩 리터럴은 2026-09-09에 도구가 최초 작성된 커밋(`89c2b19`)부터 그대로였다 — 이 스토리의 diff는 `tools/check_production_parity.py`를 전혀 수정하지 않았다(`git diff` 결과 없음). `captured_at`은 `tools/check_production_parity.py`의 어떤 패리티 비교 로직에도 쓰이지 않는 순수 정보성 필드임을 코드로 확인해, 검증(patiry gate) 자체의 신뢰성에는 영향이 없다. blind-hunter/edge-case-hunter/verification-gap 3개 레이어가 모두 독립적으로 이 날짜 역행을 지적했다.
  severity: low
  **해결됨(2026-09-14).** `tools/check_production_parity.py:492`의 하드코딩 리터럴을 `date.today().isoformat()`로 교체.
