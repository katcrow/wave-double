# Deferred Work

## Deferred from: code review (2026-09-01)

- Story 1.3: `logical_runs`와 `runs`의 RLS 정책을 확정한다. 현재 공개 API 테이블이지만 policy 없이 RLS를 활성화하면 배치·후속 dashboard read-model 경계까지 차단되므로, Story 1.8/1.10의 approved view/RPC와 함께 적용한다. 2026-09-01 실제 Supabase SQL fixture와 RPC 권한 검증은 통과했다.

## Deferred from: story 3.1 build verification (2026-09-03)

- `tests/batch/test_scheduler.py`의 7개 테스트(`test_open_day_delegates_to_candidate_stage_with_schedule_trigger`, `test_success_candidates_stage_wires_ohlcv_and_tags_pipeline`, `test_partial_candidates_stage_wires_ohlcv_and_tags_pipeline`, `test_calendar_unavailable_is_treated_as_open_and_proceeds`, `test_manual_trigger_is_passed_through_to_start_attempt`, `test_dispatch_receipt_recorded_after_open_day_success`, `test_dispatch_receipt_failure_does_not_fail_the_batch`)가 `result.status == "success"`를 기대하지만 실제로는 `"partial"`을 반환해 실패한다. Story 3.1 diff 적용 전 baseline(001346e)에서도 동일하게 실패함을 확인했으므로 Story 3.1과 무관한 기존 회귀다. `apps/batch/scheduler.py`의 candidates/tags stage 조합 status 판정 로직(`_STATUS_SEVERITY` 병합 부분)이 테스트 기대와 어긋난 것으로 보이며, Epic 2 태깅 stage 도입(story 2-5) 이후 회귀로 추정된다. 원인 규명과 수정은 이 스토리 범위 밖이라 별도로 처리 필요.
- **(high)** `infra/supabase/migrations/202609012300_add_skip_attempt.sql`이 정의하는 `public.skip_attempt` RPC가 운영 Supabase project(`qqhjeumlecaudsiqhhdu`)에 실제로는 적용되어 있지 않다. `mcp__supabase__list_migrations` 결과에 해당 migration이 없고, `pg_proc` 직접 조회 결과도 0건으로 확인했다. 그런데 `apps/batch/run_state.py:229`는 이 함수를 `rpc("skip_attempt", ...)`로 호출하므로, 휴장일 skip 처리 경로가 실행되면 런타임에 실패한다. Story 3.1 리뷰 중 우연히 발견한, 이 스토리와 무관한 기존 운영 배포 누락이다. 원인(마이그레이션 자체가 원래 적용된 적이 없는지, 이후 어떤 변경으로 drop 되었는지)과 재적용은 별도로 처리 필요.
