---
title: 'Story 3.7: TIMEOUT 컷오프 확정 & 추적 대상 유계화'
type: 'feature'
created: '2026-09-03'
status: 'done'
baseline_revision: 'e4577c8dd64f4f85f9bd124e2c40e2d742e2ae1b'
baseline_commit: 'e4577c8dd64f4f85f9bd124e2c40e2d742e2ae1b'
review_loop_iteration: 0
followup_review_recommended: false
context:
  - '_bmad-output/implementation-artifacts/epic-3-context.md'
warnings: ['oversized']
deferred:
  - summary: >-
      traded_days_since_entry 계산이 SUSPENDED 상태에서도 daily_ohlcv가 존재하는 한 계속
      outcome_observations를 'OK'로 기록하므로, Story 3.8이 SUSPENDED→OPEN 복귀를 구현하면
      복귀 이후 컷오프 판정이 SUSPENDED로 보낸 기간만큼 앞당겨질 위험이 있다.
    evidence: |-
      publish_attempt의 track_row 관찰 루프(202609031700 이후 불변)는 status not in
      ('TP','SL','TIMEOUT')인 모든 행에 대해 record_outcome_observation을 호출하며, 이는
      SUSPENDED 상태도 포함한다. daily_ohlcv에 유효 데이터가 있는 한 SUSPENDED 기간에도
      outcome_observations 행이 계속 'OK'로 쌓이고, 3.7의 traded_days_since_entry는 이
      행들을 그대로 카운트한다(blind-hunter 리뷰 발견, 2026-09-03). epics AC의
      "거래정지 기간(일봉이 없는 기간)"은 daily_ohlcv 결측을 뜻하는 별개 개념이라 3.7 자체의
      AC 위반은 아니지만, 3.8 구현 시 반드시 재검토가 필요하다.
    location: >-
      infra/supabase/migrations/202609032100_confirm_timeout_cutoff.sql (tpsl_row 루프의
      traded_days_since_entry count 쿼리)
    severity: medium
---

<intent-contract>

## Intent

**Problem:** OPEN outcome이 TP/SL(Story 3.6)에 도달하지 못한 채 무한정 남으면 추적 대상 수가 계속 늘어나 유계성이 깨진다.
**Approach:** Story 3.6이 이미 도는 TP/SL 판정 루프(`publish_attempt`) 안에서, TP/SL 미충족 시 `outcome_observations` 행 수로 계산한 `traded_days_since_entry`(휴장일·거래정지 자동 제외, `daily_ohlcv` 유효 관측만 카운트)가 그 outcome에 저장된 `cutoff_n`(기본 30) 이상이면 오늘 종가 기준 실손익으로 TIMEOUT을 확정한다. 별도 루프를 추가하지 않고 기존 TP/SL 루프를 확장해 3.6이 남긴 "네 번째 순회 시 잠금 경합 재검토" 잔여 위험을 회피한다.

## Boundaries & Constraints

**Always:** 판정 대상은 Story 3.6과 동일한 재조회 `status='OPEN' and entry_date < logical_row.trading_day` 행이며 SUSPENDED는 자연히 제외된다. SL/TP를 TIMEOUT보다 먼저 확인한다(같은 날 셋 다 조건이 겹치면 SL > TP > TIMEOUT 우선순위). `traded_days_since_entry` = `outcome_observations`에서 `outcome_id`가 같고 `evaluation_trading_day > entry_date`이고 `result_code='OK'`인 행의 개수(휴장일·`MISSING_DAILY_OHLCV`/`INVALID_DAILY_OHLCV`로 기록되지 않은 거래정지일은 애초에 행이 없어 자동 제외 — Story 3.4의 기존 동작 재사용, 신규 daily_ohlcv 재조회 없음). `cutoff_n`은 각 행에 이미 저장된 값(`candidate_outcome.cutoff_n`, 기본 30)을 그대로 읽어 비교한다(전역 상수나 설정 재조회 금지 — 이후 기본값이 바뀌어도 이미 생성된 행은 재계산되지 않음, 스키마 기본값이 이미 이 불변식을 보장). TIMEOUT 확정 시 `exit_price`는 오늘 관찰의 `close`(임계값이 아닌 실제 종가), `return_pct`는 `(close/entry_price-1)*100 - 0.1`(왕복 비용 차감, `backtest/engine.py`의 `gross-cost_rate*200`와 동일 산식이나 TP/SL과 달리 고정값이 아닌 실측치)로 기록한다. TP/SL/TIMEOUT 모든 terminal 전이 시 `candidate_outcome.holding_days`를 그 시점의 `traded_days_since_entry` 값으로 함께 기록한다(3.4~3.6이 비워둔 채 남긴 컬럼을 이 스토리에서 채운다 — AC가 요구하는 "실제 보유거래일수" 정의와 TIMEOUT 컷오프가 동일 원천을 쓰므로). TIMEOUT도 기존 `outcome_events_open_command_key_idx(logical_run_key,ticker,strategy,command_type)`를 `command_type='TIMEOUT'`로 그대로 재사용한다.

**Never:** SUSPENDED→정상 복귀, DELISTED 종결, correction event를 구현하지 않는다(Story 3.8/3.9 범위). `emit_open_command`/`record_outcome_observation`/SUSPENDED 루프의 로직·호출 순서를 변경하지 않는다. 새 API 엔드포인트나 UI를 추가하지 않는다 — "추적 대상 API 조회 제외"는 이미 존재하는 `status not in ('TP','SL','TIMEOUT')` 필터(3.4의 관찰 루프 등)가 TIMEOUT을 자동으로 포함하므로 별도 구현이 불필요하다. `cutoff_n`을 위한 신규 설정 함수(예: `price_adjustment_gap_threshold()`류)를 만들지 않는다 — 값은 이미 행마다 저장되어 있다.

## I/O & Edge-Case Matrix

| Scenario | Input / State | Expected Output / Behavior | Error Handling |
|----------|--------------|---------------------------|----------------|
| 컷오프 도달 | OPEN, `traded_days_since_entry`=30(=cutoff_n), TP/SL 미충족 | status=TIMEOUT, exit_price=오늘 close, return_pct=(close/entry-1)*100-0.1, holding_days=30 | 없음 |
| 컷오프 미도달 | `traded_days_since_entry`=29, TP/SL 미충족 | 판정 없음, OPEN 유지 | 없음 |
| TP·TIMEOUT 동시충족 | `traded_days_since_entry`>=30 이고 오늘 고가>=entry×1.03 | TP가 우선 확정(TIMEOUT 아님) | 없음 |
| SL·TIMEOUT 동시충족 | `traded_days_since_entry`>=30 이고 오늘 저가<=entry×0.97 | SL이 우선 확정(TIMEOUT 아님) | 없음 |
| 거래정지 기간 존재 | entry 이후 5거래일 관측 + 10일 거래정지(daily_ohlcv 없음) + 25거래일 추가 관측 | `traded_days_since_entry`=30(거래정지 10일 미포함), 그 시점에 TIMEOUT | 없음 |
| 재시도(동일 attempt 재발행) | 이미 `(logical_run_key,ticker,strategy,'TIMEOUT')` 이벤트 존재 | 새 이벤트/전이 없이 재확인만 | 없음 |
| TP 확정 시 holding_days | 관측 10일차에 TP 조건 충족 | status=TP(3.6 로직 유지)와 함께 holding_days=10 기록 | 없음 |

</intent-contract>

## Code Map

- `infra/supabase/migrations/202609032000_judge_tp_sl_outcomes.sql` -- 현재 `publish_attempt`의 권위 있는 최신 정의(create or replace 대상 baseline). TP/SL 판정 루프(약 152-198행, `tpsl_row` 순회)를 확장해 TIMEOUT 분기와 `holding_days` 기록을 추가한다. 별도 루프 신설 금지(3.6 잔여 위험 참고).
- `infra/supabase/migrations/202609031700_record_close_batch_observations.sql` -- `record_outcome_observation`/`outcome_observations` 스키마. `result_code`는 항상 'OK'만 기록됨(3.4)을 재확인 -- `traded_days_since_entry` 카운트 조건에 `result_code='OK'`를 명시해도 실질적으로 전체 행과 동일하지만 의도를 명확히 한다.
- `infra/supabase/migrations/202609031300_create_outcome_schema.sql:39-46` -- `candidate_outcome.cutoff_n`(기본 30, not null), `holding_days`(기본 0, not null) 컬럼. `status` check가 이미 `TIMEOUT` 포함. 스키마 변경 불필요.
- `infra/supabase/migrations/202609031500_create_emit_open_command.sql:10-11` -- `outcome_events_open_command_key_idx`. `command_type='TIMEOUT'`도 동일 index로 커버.
- `backtest/engine.py:152-153` -- `gross=(exit/entry-1)*100`, `net=gross-cost_rate*200`. TIMEOUT의 실측 종가 기반 산식이 이와 동일 비용 반영 방식임을 Design Notes에서 확인한다.
- `tests/sql/test_run_lineage.sql:387-` (Story 3.5 SUSPENDED 시나리오 이후, 3.6 TP/SL 시나리오 뒤) -- 이 스토리의 TIMEOUT 시나리오를 이어붙일 지점. `outcome_observations`를 직접 insert해 29~30개 관측을 미리 채우는 방식으로 30거래일 경과를 시뮬레이션한다(매 배치를 30번 실행하지 않음).

## Tasks & Acceptance

**Execution:**
- `infra/supabase/migrations/202609032100_confirm_timeout_cutoff.sql` -- `publish_attempt`를 `create or replace`해 기존 TP/SL 루프의 `tpsl_row` select에 `cutoff_n`을 추가하고, SL/TP 미충족 시 `traded_days_since_entry`(오늘 관측 포함, `outcome_observations` count)를 계산해 `cutoff_n` 이상이면 TIMEOUT 확정(exit_price=오늘 close, return_pct=실측 비용반영값)한다. TP/SL/TIMEOUT 모든 분기에서 `candidate_outcome.holding_days`를 그 시점 `traded_days_since_entry`로 함께 갱신한다.
- `tests/sql/test_run_lineage.sql` -- I/O 매트릭스 7개 시나리오를 커버하는 fixture를 기존 3.6 시나리오 뒤에 추가.
- `packages/read-model/src/database.types.ts` -- 운영 project에 migration 적용 후 Supabase 생성 타입 갱신 확인(함수 시그니처 불변이므로 diff 없을 수 있음, 확인만).

**Acceptance Criteria:**
- Given outcome이 생성되는 경우, when `cutoff_n`을 확인하면, then 생성 시점에 저장된 값(기본 30)이 그대로 판정에 쓰이고 이후 기본값이 바뀌어도 재계산되지 않는다.
- Given 진입 후 실거래 30일(휴장일·거래정지 제외) 내 TP/SL 미도달인 경우, when 컷오프 판정을 실행하면, then 30번째 실거래일 종가 기준 비용반영 손익률과 함께 TIMEOUT으로 확정된다.
- Given TIMEOUT으로 확정된 경우, when 이후 배치가 추적 대상을 산출하면, then 기존 `status not in ('TP','SL','TIMEOUT')` 필터에서 자동 제외된다.
- Given 거래정지 기간이 존재하는 경우, when 컷오프를 계산하면, then 그 기간은 `traded_days_since_entry`에서 제외되어 TIMEOUT이 그만큼 지연된다.
- Given TP/SL/TIMEOUT 중 하나로 확정되는 경우, when `holding_days`를 조회하면, then 실제 보유거래일수(휴장일·거래정지 제외)가 기록되어 있다.

## Spec Change Log

## Review Triage Log

### 2026-09-03 — Review pass
- intent_gap: 0
- bad_spec: 0
- patch: 1: (high 0high, medium 1medium, low 0low)
- defer: 1: (high 0high, medium 1medium, low 0low)
- dismissed:
  - `traded_days_since_entry` 계산이 SUSPENDED 상태에서도 계속 기록되는 관찰치를 포함해 Story 3.8의 SUSPENDED→복귀 이후 컷오프를 앞당길 수 있다는 지적(blind-hunter) — epics AC의 "거래정지 기간(일봉이 없는 기간)"은 이 스펙의 Boundaries가 이미 명시한 대로 `daily_ohlcv` 결측 기간을 뜻하며 3.5의 SUSPENDED(가격조정 이상 감지) 상태와는 별개 개념이라 3.7 자체의 AC 위반은 아니다. 다만 3.8이 SUSPENDED 복귀를 구현할 때 실제로 영향을 줄 수 있는 유효한 선견 지적이라 defer로 남긴다.
  - "거래정지 기간" 테스트(ZZLIN26)가 daily_ohlcv 결측만 시뮬레이션하고 실제 SUSPENDED 상태에서의 관찰 지속 기록 케이스는 다루지 않는다는 지적(blind-hunter) — 위 항목과 동일하게 이 스펙이 정의한 "거래정지"는 일봉 결측이므로 테스트가 정확히 그 정의를 검증하고 있다.
  - TIMEOUT 재시도(idempotent retry) 테스트가 `publish_attempt`를 실제로 두 번 호출하지 않고 raw insert로만 검증한다는 지적(blind-hunter/verification-gap 공통) — `publish_attempt`는 발행 완료 후 같은 `run_id` 재호출 시 `STALE_FENCE_OR_LEASE`로, 다른 `run_id`로는 `CANONICAL_ALREADY_PUBLISHED`로 이 루프에 도달하기 전에 예외를 던져 이미 terminal인 outcome에 대해 이 루프의 on-conflict 분기가 실제로 재실행되는 경로 자체가 구조적으로 도달 불가능하다 -- 이 방어 코드는 Story 3.6에서 이미 검토·수용된 동일 패턴을 그대로 재사용한 것으로 3.7이 새로 만든 공백이 아니다.
  - `v_traded_days`를 SL/TP 분기 이전에 무조건 계산해 낭비라는 지적(blind-hunter) — TP/SL 분기도 이번 스토리부터 `holding_days`를 함께 기록해야 하므로 세 분기 모두 이 값이 필요해 무조건 계산이 실제로는 낭비가 아니다.
  - `v_new_event` 변수가 insert 결과를 받고도 이후 읽히지 않는다는 지적(blind-hunter) -- Story 3.5/3.6에서 이미 존재하던 동일 패턴을 그대로 재사용한 것으로 3.7이 새로 만든 공백이 아니다.
  - ZZLIN26 fixture의 관찰 종료일(2098-11-09)과 오늘(2099-01-14) 사이 약 66일의 달력 간격이 설명 없이 크다는 지적(blind-hunter) -- 다른 컷오프 시나리오(ZZLIN22/24/25도 진입일이 2098-11-01로 유사하게 먼 과거)도 30 실거래일을 채우기 위해 동일하게 긴 과거 진입일을 쓰므로 이 fixture만의 불일치가 아니라 컷오프 시나리오 전반의 공통 특성이다.
  - 스펙의 I/O 매트릭스 문구("5거래일+25거래일=30")와 실제 코드/테스트("5거래일+24거래일+오늘=30")의 세부 분해가 다르다는 지적(blind-hunter) -- 두 표현 모두 합계 30이라는 AC의 핵심 요구는 동일하게 충족하며 매트릭스는 예시적 서술이지 문자 그대로의 산식 명세가 아니다.
  - AC1(cutoff_n 불변성)이 실제로 기본값을 변경해보는 테스트로 검증되지 않았다는 지적(blind-hunter) -- 이 불변성은 애플리케이션 로직이 아니라 PostgreSQL의 컬럼 DEFAULT 의미론 자체(기존 행의 저장된 값은 DEFAULT 변경과 무관)에서 나오며, 코드가 전역 상수가 아닌 행에 저장된 `cutoff_n`을 읽는다는 사실은 이미 커스텀 cutoff_n(ZZLIN27) 테스트로 검증되어 있다.
  - `warnings: ['oversized']`에 대한 근거가 본문에 별도 서술되지 않는다는 지적(blind-hunter) -- Story 3.6도 동일하게 별도 서술 없이 이 필드를 사용한 기존 관행과 일치한다.
  - `database.types.ts` 확인 작업의 diff 증거 부재 지적(blind-hunter) -- 이 세션이 독립적으로 `generate_typescript_types` 결과를 기존 파일과 비교해 diff 없음을 직접 재확인했다(Story 3.6에서도 동일하게 dismiss된 선례와 일치).
  - `cutoff_n=1`처럼 매우 작은 값과 SL/TP가 같은 날 겹치는 경우가 매트릭스에 없다는 지적(blind-hunter) -- 분기 로직(SL>TP>TIMEOUT)은 `cutoff_n`의 크기와 무관하게 동일하게 동작하며, 우선순위 로직은 30일차(ZZLIN24/25)로, 커스텀 `cutoff_n`은 5일차(ZZLIN27)로 이미 각각 독립 검증되어 더 작은 값의 조합이 새로운 분기를 노출하지 않는다.
- addressed_findings:
  - `[medium]` `[patch]` `traded_days_since_entry` 계산에 미래 날짜(오늘 이후) 관측 행을 배제하는 상한 조건이 없다는 지적(edge-case-hunter) -- `evaluation_trading_day <= logical_row.trading_day` 조건을 추가해 수정.

## Design Notes

TIMEOUT의 `return_pct`는 TP/SL(고정 +2.9/-3.1)과 달리 실측 종가 기반이라 값이 매번 다르다 -- 이는 epics AC "30거래일째 종가 기준 손익률(비용차감 후 실제 종가 손익)"의 명시적 요구이며, TP/SL의 "임계값 자체로 고정" 설계와 의도적으로 다른 취급이다. `holding_days`를 이번에 처음 채우는 이유: 3.4~3.6은 컬럼 존재에도 갱신 로직이 없었고(기본값 0 방치), 3.7 AC가 이 컬럼과 TIMEOUT 판정이 "동일 원천"이라 명시해 지금이 자연스러운 완성 지점이다.

## Verification

**Commands:**
- `psql -v ON_ERROR_STOP=1 "$DATABASE_URL" -f tests/sql/test_run_lineage.sql` -- expected: 모든 assertion 통과 후 rollback.
- `npm run typecheck` -- expected: 갱신된 DB 타입을 소비하는 TypeScript 전체 통과.
- `uv run --with pandas --with numpy --with pyarrow --with pytest pytest` -- expected: 기존 batch/domain 회귀망 통과.
- `git diff --check` -- expected: 공백 오류 없음.

**Manual checks (if no CLI):**
- Supabase MCP로 운영 project(`qqhjeumlecaudsiqhhdu`)에 migration 적용, `publish_attempt` 함수 정의 갱신 및 fixture pass를 확인한다.
- UI 변경이 없는 DB 전용 스토리이므로 Playwright E2E는 적용 대상이 아니다(Story 3.1~3.6과 동일 판단).

## Auto Run Result

**구현 요약:** 운영 Supabase project(`qqhjeumlecaudsiqhhdu`)에서 `publish_attempt`를 다시 `create or replace`해, Story 3.6의 TP/SL 판정 루프(`tpsl_row` 순회)를 확장했다. 별도 루프를 신설하지 않고, SL/TP 미충족 시 `outcome_observations`에서 `evaluation_trading_day > entry_date`이고 `result_code='OK'`인 행 수(`traded_days_since_entry`, 휴장일·거래정지 자동 제외)를 계산해 그 행에 이미 저장된 `cutoff_n`(전역 재조회 없음, 기본 30) 이상이면 오늘 종가 기준 실손익(`(close/entry_price-1)*100-0.1`)으로 TIMEOUT을 확정한다. TP/SL/TIMEOUT 세 분기 모두에서 `candidate_outcome.holding_days`를 그 시점 `traded_days_since_entry`로 함께 기록해, 3.4~3.6이 기본값 0으로 비워둔 컬럼을 처음 채웠다. 리뷰에서 edge-case-hunter가 발견한 "미래 날짜 관측 행이 카운트에 상한 없이 포함될 수 있다"는 지적을 반영해, 같은 세션 안에서 forward-only 패치 migration(`202609032101`)으로 `evaluation_trading_day <= logical_row.trading_day` 상한을 추가했다(원본 `202609032100`은 이미 운영에 적용된 뒤라 수정하지 않고 새 migration으로 표현 -- 이 저장소의 AD-14 관행).

**변경 파일:**
- `infra/supabase/migrations/202609032100_confirm_timeout_cutoff.sql` -- 신규. TIMEOUT 판정 및 `holding_days` 기록 추가.
- `infra/supabase/migrations/202609032101_fix_timeout_cutoff_review_patch.sql` -- 신규. 리뷰에서 발견된 미래 날짜 관측 카운트 누락 상한을 `create or replace`로 패치.
- `tests/sql/test_run_lineage.sql` -- I/O 매트릭스 7개 시나리오(ZZLIN22~28: 컷오프 도달/미도달, TP·SL이 TIMEOUT보다 우선, 거래정지 기간 제외, 커스텀 `cutoff_n`, 재시도 idempotency, TP 확정 시 `holding_days`)와, 리뷰 패치 회귀 시나리오(ZZLIN29: 미래 날짜 관측 행이 카운트에서 제외되는지) 1개를 추가.
- `_bmad-output/implementation-artifacts/sprint-status.yaml` -- `3-7-timeout-컷오프-확정-추적-대상-유계화`를 `backlog`에서 `done`으로 갱신.

**리뷰 findings 분류:** patch 1건(medium, 미래 날짜 관측 카운트 상한 누락 -- 패치 완료), defer 1건(medium, Story 3.8의 SUSPENDED 복귀 구현 시 재검토 필요), dismissed 11건(SUSPENDED 상태에서의 관찰 지속 기록은 3.7 자체 AC 범위 밖[일봉 결측만이 3.7이 정의한 "거래정지"], 관련 테스트 커버리지 지적 2건은 위와 동일 근거로 dismiss, TIMEOUT 재시도 테스트의 얕음[publish_attempt의 STALE_FENCE_OR_LEASE/CANONICAL_ALREADY_PUBLISHED 가드로 이 경로 재실행 자체가 구조적으로 도달 불가능, 3.6의 기존 수용 패턴], `v_traded_days` 무조건 계산[TP/SL 분기도 holding_days 필요], `v_new_event` 미사용 변수[3.5/3.6 기존 패턴], fixture 날짜 간격[다른 컷오프 시나리오와 공통 특성], 매트릭스 문구와 코드 분해 차이[합계 30은 동일], cutoff_n 불변성 미검증[PostgreSQL DEFAULT 의미론 자체가 보장, 커스텀 cutoff_n 테스트로 이미 간접 검증], oversized 경고 근거 미서술[3.6과 동일 관행], database.types.ts 확인 증거 부재[이 세션이 독립 재확인], 작은 cutoff_n 조합 미검증[분기 로직이 크기 무관 동일] -- 세부 근거는 Review Triage Log 참고).

**후속 리뷰 권고:** `false`(patch 1건 medium → 3×1+1×0=3 < 5, high 없음).

**검증 수행:**
- Supabase MCP `apply_migration`으로 운영 project에 `202609032100`, 이어서 리뷰 패치 `202609032101`을 순차 적용 -- `list_migrations`로 둘 다 등록됨을 확인.
- 이 세션이 독립적으로(구현 subagent와 별개로) I/O 매트릭스 7개 시나리오를 재구성해 운영 project에서 `begin;...rollback;`으로 감싸 재실행 -- 예외 없이 통과, rollback 후 잔류 행 없음을 `select`로 재확인.
- 패치 이후: 리뷰 패치 회귀 시나리오(미래 날짜 관측 배제)를 `begin;...rollback;`으로 독립 실행 -- 통과. 기존 컷오프 도달(ZZLIN22)·커스텀 cutoff_n(ZZLIN27) 시나리오를 패치된 함수로 재실행해 회귀 없음을 확인.
- `npm run typecheck` -- 통과(이 세션이 직접 재실행).
- `uv run --with pandas --with numpy --with pyarrow --with pytest pytest` -- 241 passed, 0 failed(이 세션이 직접 재실행).
- `git diff --check` -- 공백 오류 없음(CRLF 관련 무해한 경고만 존재).
- Matrix Test Audit: I/O 매트릭스 7개 행 모두 실행되어 통과한 테스트로 커버됨을 확인.
- 4개 독립 리뷰 레이어(blind-hunter, edge-case-hunter, verification-gap, intent-alignment)를 병렬 실행 후 모든 finding을 개별 검증 -- 1건은 patch로 반영, 1건은 defer, 나머지는 스펙 자체 정의·구조적 도달 불가능성·기존 선례와 일치해 dismiss.
- UI 변경이 없는 DB 전용 스토리라 Playwright E2E는 적용 대상이 아니며 실행하지 않았다(spec 자체 판단과 Story 3.1~3.6 선례 일치, intent-alignment 리뷰도 이 판단을 재확인).

**잔여 위험:**
- `traded_days_since_entry`가 SUSPENDED 상태에서도 daily_ohlcv가 유효한 한 계속 'OK' 관찰을 카운트한다 -- Story 3.8이 SUSPENDED→OPEN 복귀를 구현할 때 재검토가 필요하다(defer, medium).
- Story 3.5/3.6이 남긴 잔여 위험(emit_open_command의 SUSPENDED 재진입 가드 미비, daily_ohlcv 0/음수 종가 무방비, `outcome_events_open_command_key_idx` 인덱스 이름이 여러 command_type을 재사용, `publish_attempt` comment의 무한 누적)은 이 스토리와 무관하게 여전히 미해결이다(`deferred-work.md` 참조).
