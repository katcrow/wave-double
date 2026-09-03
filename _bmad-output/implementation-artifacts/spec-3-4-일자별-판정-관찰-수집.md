---
title: 'Story 3.4: 일자별 판정 관찰 수집'
type: 'feature'
created: '2026-09-03'
status: 'done'
baseline_revision: '10c08888c40f89640916480c9c25f4e8614bca0d'
baseline_commit: '10c08888c40f89640916480c9c25f4e8614bca0d'
review_loop_iteration: 0
followup_review_recommended: false
context:
  - '_bmad-output/implementation-artifacts/epic-3-context.md'
warnings: ['oversized']
deferred: []
---

<intent-contract>

## Intent

**Problem:** Story 3.2/3.3이 OPEN outcome을 생성하기 시작했지만, 이후 거래일의 고가/저가/종가를 `outcome_observations`에 쌓는 로직이 전혀 없다. Story 3.6의 TP/SL 판정과 Story 3.7의 TIMEOUT 판정이 딛고 설 관찰 데이터가 없으면 두 스토리 모두 구현할 수 없다.
**Approach:** `publish_attempt`를 다시 `create or replace`해, `batch_kind='close'`일 때 기존 OPEN 발행 루프 다음으로 terminal이 아닌(`status not in ('TP','SL','TIMEOUT')`) 모든 `candidate_outcome` 행을 순회하며, 신규 idempotent RPC `record_outcome_observation(outcome_id, ticker, evaluation_trading_day)`을 호출해 `daily_ohlcv`의 해당 거래일 고가/저가/종가를 `outcome_observations`에 기록한다. 같은 트랜잭션 안에서 실행되지만, 개별 티커의 `daily_ohlcv` 결측은 (미해결 SUSPENDED/DELISTED 후보 지점을 위해) 전체 publish를 rollback시키지 않고 그 티커만 이번 거래일 관찰 없이 건너뛴다(Boundaries 참조).

## Boundaries & Constraints

**Always:** `publish_attempt`의 `batch_kind='close'` 분기에서, 기존 `emit_open_command` 루프가 끝난 뒤 `select outcome_id, ticker from candidate_outcome where status not in ('TP','SL','TIMEOUT') for update`로 추적 대상을 조회하고(방금 이 루프에서 새로 OPEN된 outcome도 포함), 각 행마다 `record_outcome_observation(outcome_id, ticker, logical_row.trading_day)`를 호출한다. `record_outcome_observation`은 `daily_ohlcv`에서 `(ticker, trading_day=p_evaluation_trading_day)`의 high/low/close를 조회해 `outcome_observations(outcome_id, evaluation_trading_day, high, low, close, result_code='OK')`를 insert하되, `on conflict (outcome_id, evaluation_trading_day) do nothing`으로 멱등을 보장하고(이미 존재하면 새 행을 만들지 않고 기존 값을 반환), `daily_ohlcv`에 해당 티커/거래일 행이 없으면 insert를 시도하지 않고 `recorded:false, reason:'MISSING_DAILY_OHLCV'`를 반환한다 -- 이 경우도 정상 반환이며 예외를 던지지 않는다(Story 3.5/3.9가 아직 없어 SUSPENDED/DELISTED 감지가 불가능한 상태에서, 오래된 다른 종목의 결측이 오늘자 candidate/tag 발행 전체를 막지 않도록 하기 위함 -- Story 3.4 AC4의 "이후 스토리에서 자동판정 제외 대상으로 확장될 지점" 문구와 정합).

**Never:** `emit_open_command`(Story 3.2/3.3)의 로직·호출부를 수정하지 않는다 -- 새 루프는 그 뒤에 추가만 한다. TP/SL/TIMEOUT 판정(Story 3.6/3.7)이나 가격조정/SUSPENDED 감지(Story 3.5)를 구현하지 않는다 -- `result_code`는 이 스토리에서 항상 `'OK'`(정상 수집)만 쓰고 판정 결과 코드를 넣지 않는다. `daily_ohlcv` 결측을 이유로 `publish_attempt` 전체를 rollback시키지 않는다(위 Always 참조 -- `emit_open_command`의 `MISSING_DAILY_OHLCV_CLOSE`와는 의도적으로 다른 처리). `runs.stage_status`에 새 stage key를 추가하지 않는다(`run_stage_keys`/`run_stage_values` 체크 제약이 고정한 5개 키 -- candidates/tags/supply_3day/market_supply/outcome_tracking -- 를 그대로 두고, 이 스토리의 관찰 수집도 기존 `outcome_tracking` stage 안에서 수행한다). premarket/intraday 배치에서는 이 루프를 실행하지 않는다(AD-15와 동일 근거 -- `canonical_success_run_id`가 close에만 존재).

## I/O & Edge-Case Matrix

| Scenario | Input / State | Expected Output / Behavior | Error Handling |
|----------|--------------|---------------------------|----------------|
| OPEN outcome 1건, 종가 존재 | close 발행, 기존에 OPEN인 outcome 1건, 해당 티커의 오늘 거래일 `daily_ohlcv` 행 존재 | `outcome_observations`에 `(outcome_id, 오늘 거래일)` 1행 신규 insert, high/low/close가 `daily_ohlcv`와 일치, `result_code='OK'` | 없음 |
| 재시도(동일 거래일 재발행 없음, RPC 직접 재호출) | 이미 `(outcome_id, evaluation_trading_day)` observation이 존재 | 새 행을 만들지 않고 `recorded:true, replayed:true`로 기존 값 반환 | 없음 |
| 방금 신규 OPEN된 outcome도 관찰 대상 | close 발행에서 이번 attempt가 새로 OPEN시킨 outcome | 같은 트랜잭션 안에서 그 outcome도 오늘 거래일 관찰이 함께 기록됨(진입일 관찰) | 없음 |
| terminal 상태 outcome 제외 | `candidate_outcome`에 `status='TP'`인 행 존재 | 관찰 대상 조회에서 제외되어 `outcome_observations`에 해당 outcome의 오늘자 행이 생기지 않음 | 없음 |
| 추적 대상 티커의 daily_ohlcv 결측 | OPEN outcome의 티커에 오늘 거래일 `daily_ohlcv` 행 없음 | 그 outcome만 관찰 없이 건너뜀, `publish_attempt`는 정상적으로 커밋되고(candidate/tag/OPEN 발행 포함) `outcome_tracking='success'`로 종결 | 예외 없음(MISSING_DAILY_OHLCV_CLOSE와 달리 rollback하지 않음) |
| 활성 태그 0건 + OPEN outcome 0건 | close 발행, 추적 대상 없음 | 관찰 루프가 빈 채로 통과, 기존 3.3 동작(빈 OPEN 루프) 그대로 유지 | 없음 |

</intent-contract>

## Code Map

- `infra/supabase/migrations/202609031600_link_publish_attempt_to_outcome.sql` -- 현재 `publish_attempt(p_run_id, p_fence_token, p_lease_token)`의 권위 있는 최신 정의(create or replace 대상 baseline). close 분기의 `emit_open_command` 루프(관련 라인) 바로 뒤에 관찰 수집 루프를 추가한다(AD-14, Story 3.2/3.3의 forward-migration 선례를 따름).
- `infra/supabase/migrations/202609031500_create_emit_open_command.sql` -- 신규 `record_outcome_observation` RPC가 따라야 할 idempotent 패턴의 선례(멱등 key 조회 → insert on conflict do nothing → found 여부로 신규/replay 분기 → jsonb 반환). `security definer`, `set search_path = public`, `revoke ... from public, anon, authenticated; grant ... to service_role` 컨벤션도 동일하게 따른다.
- `infra/supabase/migrations/202609031300_create_outcome_schema.sql:19-29` -- `outcome_observations(outcome_id, evaluation_trading_day, high, low, close, result_code)` PK 및 not-null/양수 체크. append-only 트리거(UPDATE/DELETE/TRUNCATE 거부)가 이미 걸려 있어 이 스토리는 INSERT 경로만 추가하면 된다.
- `infra/supabase/migrations/202609031400_harden_outcome_schema_invariants.sql:5-8` -- `outcome_observations_high_low_close_order` 체크(`high >= low and close between low and high`)가 이미 존재하므로, `daily_ohlcv`의 high/low/close를 그대로 넣으면 이 체크를 통과한다(입력 데이터가 이미 OHLC 불변식을 만족).
- `infra/supabase/migrations/202609021500_create_daily_ohlcv.sql:6-17` -- `daily_ohlcv(ticker, trading_day, open, high, low, close, volume, adjusted, adjustment_version, pricechk)` PK `(ticker, trading_day)`. 관찰 수집의 유일한 시세 출처(Story 2.2 증분 갱신 산출물, NFR-9 adjusted 기준).
- `infra/supabase/migrations/202609011600_create_run_lineage.sql:33,42-51` -- `run_stage_keys`/`run_stage_values` 체크 제약이 `stage_status`를 정확히 5개 키로 고정한다 -- 새 stage key를 추가하려면 이 체크 제약도 함께 바꿔야 하므로, 이 스토리는 새 키를 만들지 않고 기존 `outcome_tracking` 안에서 처리한다(Boundaries 참조).
- `tests/sql/test_run_lineage.sql:114-159` -- Story 3.3의 `close:2099-01-07` 시나리오(활성 태그 2건 → OPEN outcome 2건)가 이 스토리의 "방금 신규 OPEN된 outcome도 관찰 대상" 시나리오의 자연스러운 확장 지점이다 -- 같은 attempt의 `publish_attempt` 호출 뒤에 `outcome_observations` assertion을 추가할 수 있다.
- `apps/batch/run_state.py:206-212` -- Python `RunStateGateway.publish()`는 정의돼 있지만 `apps/batch/` 어디에서도 호출되지 않는 기존 gap(Story 3.1~3.3에서도 동일)이다. 이 스토리도 SQL fixture(`tests/sql/*.sql`)로만 검증하며, Python 배선은 범위 밖이다(기존 선례와 동일).

## Tasks & Acceptance

**Execution:**
- `infra/supabase/migrations/202609031700_record_close_batch_observations.sql` -- 신규 함수 `public.record_outcome_observation(p_outcome_id uuid, p_ticker text, p_evaluation_trading_day date) returns jsonb`를 `emit_open_command`와 동일한 컨벤션(security definer, idempotent insert-on-conflict, `service_role`에만 execute grant)으로 생성하고, `publish_attempt`를 `create or replace`해 close 분기의 OPEN 루프 뒤에 `candidate_outcome where status not in ('TP','SL','TIMEOUT')`을 순회하며 이 함수를 호출하는 두 번째 루프를 추가 -- Story 3.6/3.7의 판정 로직이 소비할 관찰 데이터를 매 close 배치마다 축적하기 위해서다.
- `tests/sql/test_run_lineage.sql` -- 기존 `close:2099-01-07` 시나리오에 `outcome_observations` 2행(각 신규 OPEN outcome의 진입일 관찰) 생성 검증을 추가하고, 새 시나리오로 (a) 기존에 OPEN이던 outcome이 다음 거래일 close 발행에서 관찰이 추가되는 경우, (b) 재시도 시 새 행이 생기지 않는 멱등 검증, (c) 추적 대상 티커의 `daily_ohlcv` 결측이 그 outcome만 건너뛰고 나머지 publish는 정상 커밋됨을 검증하는 시나리오를 추가 -- I/O 매트릭스 전 항목을 커버하기 위해서다.
- `packages/read-model/src/database.types.ts` -- 운영 project에 migration 적용 후 Supabase 생성 타입 갱신 확인(Args/Returns가 opaque `Json`이라 실질 드리프트는 없을 가능성이 높지만 Story 3.1~3.3과 동일하게 확인 절차를 거친다).

**Acceptance Criteria:**
- Given close 배치 발행 시점에 OPEN 상태의 outcome이 있는 경우, when `publish_attempt`가 실행되면, then 그 outcome의 해당 거래일 고가/저가/종가가 `daily_ohlcv`에서 조회되어 `outcome_observations(outcome_id, evaluation_trading_day)`에 기록된다.
- Given 동일 `(outcome_id, evaluation_trading_day)`에 대해 `record_outcome_observation`이 재호출되는 경우, when observation을 다시 기록하려 하면, then 새 행을 만들지 않고 기존 observation을 멱등하게 반환한다.
- Given 관찰 대상을 산출하는 경우, when `candidate_outcome`을 조회하면, then terminal 상태(`TP`/`SL`/`TIMEOUT`)의 outcome은 이번 관찰 루프에서 제외된다.
- Given 추적 대상 티커의 오늘 거래일 `daily_ohlcv` 행이 없는 경우, when 관찰 루프가 이를 만나면, then 그 outcome만 관찰 없이 건너뛰고 `publish_attempt`는 예외 없이 정상 커밋된다(candidate/tag/OPEN 발행 포함).

## Spec Change Log

## Review Triage Log

### 2026-09-03 — Review pass
- intent_gap: 0
- bad_spec: 0
- patch: 1: (high 0high, medium 1medium, low 0low)
- defer: 0
- dismissed:
  - `record_outcome_observation`가 `p_outcome_id`/`p_ticker`의 대응 관계를 검증하지 않는다는 지적(blind-hunter/edge-case-hunter 중복 제기) — 유일한 호출부(`publish_attempt`의 신규 루프)가 같은 `candidate_outcome` 행에서 `outcome_id`와 `ticker`를 함께 조회해 넘기므로 실제로는 어긋날 수 없고, 이 RPC는 `service_role`에만 execute가 부여돼 다른 호출부도 없다.
  - `daily_ohlcv` 행이 존재하지만 high/low/close가 NULL일 수 있다는 지적(blind-hunter) — 반증됨: `daily_ohlcv.high/low/close`는 `202609021500_create_daily_ohlcv.sql`에서 이미 `not null`이라 이 상태 자체가 불가능하다.
  - `daily_ohlcv`의 `adjusted`/`adjustment_version`을 필터링하지 않는다는 지적(blind-hunter) — 반증됨: `daily_ohlcv`의 PK가 `(ticker, trading_day)`라 그 날짜의 유일한(=현재 adjusted) 행만 존재하므로 필터링할 대상이 없다.
  - 관찰 기록 전에 `pricechk`(가격조정 마커)를 확인하지 않는다는 지적(blind-hunter) — intent-contract Never 절 기준 범위 밖(이상 감지는 Story 3.5).
  - `publish_attempt`의 신규 관찰 루프가 `logical_run_key`/거래일로 범위를 좁히지 않고 전체 non-terminal `candidate_outcome`을 매 close 발행마다 스캔·잠금한다는 지적(blind-hunter/edge-case-hunter/verification-gap 3중 제기) — AC가 요구하는 동작 자체다(태깅 시점과 무관하게 모든 OPEN outcome이 매일 관찰돼야 함); 추적 대상은 NFR-7과 Story 3.7의 컷오프로 유계이며, 동일한 순차 RPC/잠금 시간 우려가 이미 Story 3.2/3.3 리뷰에서 실측 근거 없는 조기 최적화로 기각된 선례가 있다.
  - `anon`/`authenticated`에 대한 execute 거부를 검증하는 negative test가 없다는 지적(blind-hunter) — 동일 패턴인 Story 3.2의 `emit_open_command`도 이런 테스트가 없고 그때도 요구되지 않은 기존 컨벤션과 일치.
  - `outcome_observations`에 RLS 정책/read-model 노출이 없다는 지적(blind-hunter) — 이 스토리 범위 밖(소비하는 UI 없음)이며 `deferred-work.md`의 Story 1.3 RLS 정책 항목으로 이미 별도 추적 중인 기존 미해결 사안이다.
  - premarket/intraday에서 이 관찰 루프가 실행되지 않음을 검증하는 테스트가 없다는 지적(blind-hunter) — 신규 루프는 기존 OPEN 발행 루프와 동일한 `if logical_row.batch_kind = 'close'` 블록(202609031600에서 변경 없음) 안에 중첩돼 동일한 구조적 보호를 상속하며, verification-gap 리뷰어가 이를 직접 추적해 gap 없음을 확인했다.
  - `publish_attempt`가 `record_outcome_observation`의 세부 jsonb 반환값(recorded/skipped)을 버린다는 지적(blind-hunter) — Story 3.3 리뷰에서 `emit_open_command`의 동일한 반환값 폐기에 대해 이미 검토·기각된 것과 같은 저장소 컨벤션(실패는 예외로만 신호, 세부 결과는 소비하지 않음).
  - 이 루프의 테이블 전체 `for update` 잠금이 향후 Story 3.6/3.7의 정산 쓰기와 잠금 경합을 일으킬 수 있다는 지적(blind-hunter) — 아직 존재하지 않는 미래 스토리에 대한 추측이며 이 diff의 실제 결함이 아니다.
  - `daily_ohlcv` 결측으로 건너뛴 날짜가 이후 배치에서도 소급 채워지지 않음(영구 결측)을 검증하는 테스트가 없다는 지적(blind-hunter) — Design Notes에 이미 의도된 동작으로 문서화돼 있고, 소급 채움 코드 경로 자체가 없어 테스트할 대상이 없다.
  - 이미 발행된 attempt에 대한 `publish_attempt` 재호출(정상 오케스트레이션 재시도) 테스트가 없다는 지적(blind-hunter) — 이 diff와 무관한 기존 `CANONICAL_ALREADY_PUBLISHED`/publish guard 동작이며 Story 1.3/3.3 테스트가 이미 다룬다.
  - `baseline_revision`이 조작됐을 수 있다는 지적(blind-hunter) — 반증됨: `git rev-parse HEAD` 결과(`10c08888c40f89640916480c9c25f4e8614bca0d`)와 정확히 일치하며 세션 시작 시점 git log의 축약 해시 `10c0888`과도 정합한다.
- addressed_findings:
  - `[medium]` `[patch]` `record_outcome_observation`이 `daily_ohlcv` 행의 "결측"만 방어하고 "존재하지만 값이 잘못된"(예: `high < low`, `outcome_observations_high_low_close_order` 위반) 경우는 방어하지 않아, insert 시 체크 제약 예외가 그대로 전파되어 `publish_attempt` 전체가 rollback된다는 지적(edge-case-hunter) — 이는 스토리 자신이 명시한 "오래된 종목의 데이터 문제가 오늘자 발행을 막지 않는다"는 설계 의도를 정확히 위반하는 실제 결함이다. `record_outcome_observation`에 insert 이전 OHLC 순서 검증(`v_high >= v_low and v_close between v_low and v_high`)을 추가해 위반 시 결측과 동일하게 `recorded:false`로 건너뛰도록 패치하고, 위반 fixture 시나리오를 추가한다.

## Design Notes

`daily_ohlcv`가 결측인 티커를 만나도 `publish_attempt` 전체를 rollback시키지 않는 것은 `emit_open_command`의 `MISSING_DAILY_OHLCV_CLOSE`(오늘 새로 태깅된 후보의 종가 결측 -- 이번 attempt의 candidate/tag 자체가 불완전하다는 신호)와 의도적으로 다른 처리다. 관찰 대상은 과거에 이미 OPEN된, 이번 attempt의 candidate/tag와 무관한 종목일 수 있어(거래정지·상장폐지 등, Story 3.5/3.9가 아직 없어 자동 분류 불가), 그 결측을 이유로 오늘자 후보 발행 전체를 막는 것은 과도한 blast radius다. 대신 그 outcome은 이번 거래일 관찰 없이 남고, 다음 close 배치가 재시도한다(멱등 insert-on-conflict라 여러 날의 데이터가 나중에 한꺼번에 채워지지 않고 그날 결측은 그날 결측으로 영구히 빈 채 남는다는 점에 유의 -- Story 3.6/3.7의 판정 로직이 이 gap을 어떻게 다룰지는 해당 스토리의 몫이다).

## Verification

**Commands:**
- `psql -v ON_ERROR_STOP=1 "$DATABASE_URL" -f tests/sql/test_run_lineage.sql` -- expected: 모든 assertion 통과 후 rollback.
- `npm run typecheck` -- expected: 갱신된 DB 타입을 소비하는 TypeScript 전체 통과.
- `uv run --with pandas --with numpy --with pyarrow --with pytest pytest` -- expected: 기존 batch/domain 회귀망 통과(baseline에 존재하는 무관한 실패 제외, `tests/batch/test_scheduler.py`의 7건은 Story 3.1~3.3에서도 동일하게 확인된 baseline 실패).
- `git diff --check` -- expected: 공백 오류 없음.

**Manual checks (if no CLI):**
- Supabase MCP로 운영 project(`qqhjeumlecaudsiqhhdu`)에 migration 적용, `publish_attempt`/`record_outcome_observation` 함수 정의 갱신 및 fixture pass를 확인한다.
- UI 변경이 없는 DB 전용 스토리이므로 Playwright E2E는 적용 대상이 아니다(Story 3.1~3.3과 동일 판단 -- 이 데이터를 소비하는 UI는 아직 존재하지 않는다).

## Auto Run Result

**구현 요약:** 운영 Supabase project(`qqhjeumlecaudsiqhhdu`)에서 신규 RPC `record_outcome_observation(p_outcome_id, p_ticker, p_evaluation_trading_day)`을 만들고 `publish_attempt`를 다시 `create or replace`했다. `record_outcome_observation`은 `daily_ohlcv`에서 `(ticker,trading_day)` 고가/저가/종가를 조회해 `outcome_observations`에 idempotent insert-on-conflict로 기록하며, 해당 행이 없으면(`MISSING_DAILY_OHLCV`) 또는 있어도 OHLC 순서가 무효하면(`INVALID_DAILY_OHLCV`, 리뷰 패치로 추가) 예외 없이 `recorded:false`를 반환한다. `publish_attempt`는 `batch_kind='close'`일 때 기존 OPEN 발행 루프 뒤에 `candidate_outcome where status not in ('TP','SL','TIMEOUT')`을 순회하며 이 함수를 호출하는 두 번째 루프를 추가했다 -- 새 stage key 없이 기존 `outcome_tracking` stage 안에서 처리된다. `daily_ohlcv` 결측/무효 데이터는 그 티커만 건너뛰고 `publish_attempt` 전체를 rollback시키지 않아, 과거에 이미 OPEN된 종목의 데이터 문제가 오늘자 candidate/tag/OPEN 발행을 막지 않는다(emit_open_command의 `MISSING_DAILY_OHLCV_CLOSE`와 의도적으로 다른 처리).

**변경 파일:**
- `infra/supabase/migrations/202609031700_record_close_batch_observations.sql` -- 신규 `record_outcome_observation` RPC 생성(emit_open_command와 동일한 security definer/idempotent/service_role-only 컨벤션), `publish_attempt`에 관찰 수집 루프 추가. 리뷰 패치로 OHLC 순서 무효 검증 가드와 코멘트를 추가.
- `tests/sql/test_run_lineage.sql` -- 기존 `close:2099-01-07` 시나리오에 신규 OPEN outcome의 진입일 관찰 검증을 추가하고, 신규 `close:2099-01-10` 시나리오로 기존 OPEN outcome의 다음 거래일 관찰 추가, terminal(TP) 제외, daily_ohlcv 결측 시 그 outcome만 건너뜀, 멱등 재시도를 검증. 리뷰 패치로 OHLC 순서 무효(`low>high`) 시나리오와 그 경우에도 publish가 정상 커밋됨을 검증하는 assertion을 추가.
- `packages/read-model/src/database.types.ts` -- 운영 project에서 생성한 최신 타입으로 갱신(`record_outcome_observation` RPC 항목 추가, `publish_attempt` 시그니처는 불변).

**리뷰 findings 분류:** patch 1건(적용 완료 -- OHLC 순서 무효 데이터가 publish_attempt 전체를 rollback시키는 결함[medium]), defer 0건, dismissed 13건(review triage log 참조 -- ticker/outcome_id 불일치·NULL OHLC·adjusted 필터링·pricechk 미확인은 반증되거나 범위 밖이었고, 전체 스캔+잠금·negative permission test·RLS 정책·premarket/intraday 미검증·반환값 폐기·미래 잠금 경합·영구 결측 미검증·재발행 미검증·baseline_revision 위조 의심은 모두 반증되거나 기존 컨벤션/선례와 일치하거나 이 스토리 범위 밖이었다).

**후속 리뷰 권고:** `false`(patch medium 1건 → 3×1=3 < 5).

**검증 수행:**
- Supabase MCP `execute_sql`로 운영 project에서 `tests/sql/test_run_lineage.sql` 전체(패치 전/후 각 1회, 총 2회)와 패치 검증용 축약 재현 스크립트(패치 후 1회)를 `begin;...rollback;`으로 감싸 실행 -- 모두 예외 없이 통과.
- `npm run typecheck` -- 통과(패치 전/후 각 1회).
- `uv run --with pandas --with numpy --with pyarrow --with pytest pytest` -- 234 passed, 7 failed(모두 `tests/batch/test_scheduler.py`, baseline(10c0888)에서도 동일하게 실패하는 기존 회귀로 이 스토리와 무관, Story 3.1~3.3에서도 동일하게 확인된 사항, 패치 전/후 동일하게 재확인).
- `git diff --check` -- 공백 오류 없음(CRLF 관련 무해한 경고만 존재).
- Matrix Test Audit: I/O 매트릭스의 6개 행 모두 실행되어 통과한 테스트로 커버됨을 확인(OHLC 순서 무효 케이스는 리뷰 패치로 보강된 시나리오가 커버).
- 운영 migration 이력 정리: 리뷰 패치 적용 중 구현 subagent가 이미 적용된 `202609031700` migration 파일을 in-place 수정 후 같은 이름으로 재적용해 `supabase_migrations.schema_migrations`에 동일 이름의 중복 행(버전 2개)이 남았음을 발견 -- 패치 이전 내용에 해당하는 오래된 버전(`20260903072725`) 행을 삭제해 로컬 파일(1개)과 운영 migration 이력(1개 행)을 다시 1:1로 맞췄다.
- UI 변경이 없는 DB 전용 스토리라 Playwright E2E는 적용 대상이 아니며 실행하지 않았다(spec 자체 판단과 Story 3.1~3.3 선례 일치).

**잔여 위험:**
- `publish_attempt`의 관찰 수집 루프는 매 close 발행마다 terminal이 아닌 모든 `candidate_outcome` 행을 전체 스캔·잠금한다 -- 현재 규모에서는 AC가 요구하는 정상 동작이자 NFR-7/Story 3.7의 컷오프로 유계이지만(Story 3.2/3.3 리뷰에서 동일 우려가 근거 없는 조기 최적화로 기각된 선례 있음), Story 3.6/3.7이 같은 행 집합에 쓰기 작업을 추가하면 잠금 경합을 재검토할 필요가 있다.
- `daily_ohlcv` 결측/무효로 건너뛴 거래일은 소급 채워지지 않고 영구히 빈 채로 남는다(Design Notes에 명시) -- Story 3.6/3.7의 판정 로직이 이 gap을 어떻게 다룰지는 아직 정의되지 않았다.
- `record_outcome_observation`이 스킵한 관찰(결측/무효) 건수는 `runs.stage_status`나 어떤 로그에도 집계되지 않아, 데이터 파이프라인 전반의 장애(예: `daily_ohlcv` 갱신 전면 실패)가 조용히 넘어갈 수 있다 -- Story 3.3의 emit_open_command 반환값 폐기와 동일한 기존 컨벤션이라 이번에는 패치하지 않았지만, AD-10의 능동 가시성 원칙에 비춰 향후 스토리(3.5의 알림 체계 등)에서 재검토할 가치가 있다.
- Story 3.1에서 기록된 `skip_attempt` RPC 운영 미적용 건은 이 스토리와 무관하게 여전히 미해결이다(`deferred-work.md` 참조).
