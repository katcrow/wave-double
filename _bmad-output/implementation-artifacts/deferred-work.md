# Deferred Work

## Deferred from: code review (2026-09-01)

- Story 1.3: `logical_runs`와 `runs`의 RLS 정책을 확정한다. 현재 공개 API 테이블이지만 policy 없이 RLS를 활성화하면 배치·후속 dashboard read-model 경계까지 차단되므로, Story 1.8/1.10의 approved view/RPC와 함께 적용한다. 2026-09-01 실제 Supabase SQL fixture와 RPC 권한 검증은 통과했다.

## Deferred from: story 3.1 build verification (2026-09-03)

- ~~`tests/batch/test_scheduler.py`의 7개 테스트가 `result.status == "success"`를 기대하지만 실제로는 `"partial"`을 반환해 실패~~ **해결됨(2026-09-03, story 3.5 후속 조치).** 실제 원인은 `_STATUS_SEVERITY` 병합 로직이 아니라 `tests/batch/test_scheduler.py`의 `FakeTagsRepository`에 Story 2.8이 추가한 `sync_vanished` 메서드가 없었던 것 -- `tags_stage.py`가 태깅 성공 직후 `tags_repo.sync_vanished(run_id_str)`를 호출하는데, fake에 이 메서드가 없어 `AttributeError`가 나고 `except Exception: vanished_sync_failed = True`로 흡수되어 `error_count==0`(태깅 자체는 성공)임에도 전체 결과가 `partial`/`VANISHED_SYNC_FAILED`로 낮춰졌다. `FakeTagsRepository`에 `sync_vanished(self, run_id)`(반환 `{"vanished_count": 0}`)를 추가해 실제 `TagsRepositoryProtocol`과 일치시켜 해결. `uv run pytest` 241 passed(기존 234 + 이번에 복구된 7건).
- **(high)** `infra/supabase/migrations/202609012300_add_skip_attempt.sql`이 정의하는 `public.skip_attempt` RPC가 운영 Supabase project(`qqhjeumlecaudsiqhhdu`)에 실제로는 적용되어 있지 않다. `mcp__supabase__list_migrations` 결과에 해당 migration이 없고, `pg_proc` 직접 조회 결과도 0건으로 확인했다. 그런데 `apps/batch/run_state.py:229`는 이 함수를 `rpc("skip_attempt", ...)`로 호출하므로, 휴장일 skip 처리 경로가 실행되면 런타임에 실패한다. Story 3.1 리뷰 중 우연히 발견한, 이 스토리와 무관한 기존 운영 배포 누락이다. 원인(마이그레이션 자체가 원래 적용된 적이 없는지, 이후 어떤 변경으로 drop 되었는지)과 재적용은 별도로 처리 필요.

## Deferred from: story 3.5 build verification (2026-09-03)

- `publish_attempt`(따라서 이 함수가 close 분기에서 호출하는 `emit_open_command`/`record_outcome_observation`/이번 스토리의 SUSPENDED 감지 루프 전체)는 여전히 어떤 실제 배치 오케스트레이터에도 연결되어 있지 않다(Story 3.1~3.4에서 반복 확인된 기존 gap과 동일). 이 상태에서는 SUSPENDED 전이가 실제로 발생해도 그것을 소비해 GitHub Issue를 생성하는 알림 배선을 추가할 방법이 없다 -- 트리거할 실제 이벤트가 없어 검증 불가능한 죽은 코드가 되기 때문이다(spec-3-5 Design Notes 참조). 알림 배선(Python/워크플로에서 `suspended_transitions`를 읽어 GitHub Issue를 생성하는 구현)은 `publish_attempt`의 프로덕션 배선 gap 해소 이후 별도 스토리에서 다뤄야 한다.

## Deferred from: story 3.5 code review (2026-09-03)

- **(medium)** `emit_open_command`(Story 3.2, `infra/supabase/migrations/202609031501_fix_emit_open_command_review_patch.sql:57`)의 재진입 방지(ALREADY_OPEN) 가드가 `status = 'OPEN'`만 확인한다. `candidate_outcome_one_open_per_ticker_strategy_idx`는 `status='OPEN'`에만 걸린 partial unique index이고 `(ticker,strategy,entry_date)` unique 제약도 `entry_date`가 다르면 막지 못하므로, `SUSPENDED` 상태인 (ticker,strategy)를 이후 배치가 재태깅하면 새 `candidate_outcome` 행이 중복 생성될 수 있다. `SUSPENDED`는 Story 3.5가 처음 실제로 도달 가능하게 만든 상태라 이전에는 이 경로가 도달 불가능했다(2026-09-03 code review, blind-hunter 발견). epics.md의 Story 3.1 AC는 OPEN 중복 방지만 명시하고 SUSPENDED 재진입은 다루지 않아 원 스펙의 공백이며, Story 3.8(correction 이벤트 메커니즘)이 SUSPENDED 복귀/재진입 정책을 정의할 때 함께 다뤄야 한다.
- **(low)** `daily_ohlcv.close`(Story 2.1, `infra/supabase/migrations/202609021500_create_daily_ohlcv.sql`)에 양수 제약이 없어(NaN/Infinity만 배제), 전일 종가가 0이면 Story 3.5의 갭 안전망 계산(`v_prev_close <> 0` 가드)이 나눗셈 예외 대신 감지를 조용히 건너뛴다. `pricechk`도 없는 상태에서 전일 종가가 0이면 어떤 경로로도 이상이 감지되지 않는다(2026-09-03 code review, blind-hunter 발견). `daily_ohlcv` 스키마 자체의 기존 공백이며, 이 컬럼에 양수 체크 제약을 추가하는 것은 Story 2.1 스키마의 몫이다.
