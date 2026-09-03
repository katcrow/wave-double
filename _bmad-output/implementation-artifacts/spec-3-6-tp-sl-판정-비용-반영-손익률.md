---
title: 'Story 3.6: TP/SL 판정 & 비용 반영 손익률'
type: 'feature'
created: '2026-09-03'
status: 'done'
baseline_revision: '9a70fb42306d46f3b2f09c2e8458de82fc92c9d0'
baseline_commit: '9a70fb42306d46f3b2f09c2e8458de82fc92c9d0'
review_loop_iteration: 0
followup_review_recommended: false
context:
  - '_bmad-output/implementation-artifacts/epic-3-context.md'
warnings: ['oversized']
deferred:
  - summary: >-
      outcome_events_open_command_key_idx 유니크 인덱스 이름이 여전히 "open_command_key"로만
      되어 있어, Story 3.5(SUSPENDED)와 3.6(TP/SL)이 같은 인덱스를 재사용하는 현재 범위를
      반영하지 못한다.
    evidence: |-
      202609031500_create_emit_open_command.sql:10-11에서 outcome_events(logical_run_key,
      ticker, strategy, command_type) 유니크 인덱스를 OPEN 전용으로 생성했고, 그 시점 이름을
      그대로 유지한 채 3.5가 SUSPENDED에, 이번 3.6이 TP/SL에 재사용했다(blind-hunter 리뷰 발견,
      2026-09-03). 기능적 문제는 없으나(값만 다를 뿐 컬럼 구조는 동일) 이름이 실제 역할을
      반영하지 못해 향후 독자를 혼란시킬 수 있다. 이 오도하는 이름은 3.5가 SUSPENDED로 처음
      재사용을 시작한 시점부터의 기존 공백이라 3.6만의 문제가 아니다.
    location: >-
      infra/supabase/migrations/202609031500_create_emit_open_command.sql:10
    severity: low
  - summary: >-
      publish_attempt 함수의 comment on function 문자열이 "Story 1.x~3.6"처럼 스토리마다
      누적 서술되는 인라인 변경 이력이라, 3.7/3.8/3.9가 이어질수록 무한정 길어진다.
    evidence: |-
      202609031700/202609031800/202609032000 각 migration이 이전 comment 전체 서술을
      유지한 채 자신의 절만 덧붙이는 패턴을 반복한다(blind-hunter 리뷰 발견, 2026-09-03).
      Story 3.5부터 이미 존재하던 문서화 관행이며 이번 스토리가 새로 만든 패턴이 아니다.
    location: >-
      infra/supabase/migrations/202609032000_judge_tp_sl_outcomes.sql:228
    severity: low
---

<intent-contract>

## Intent

**Problem:** OPEN outcome의 일자별 관찰치(Story 3.4)가 쌓여도 TP/SL을 자동 판정해 terminal 상태로 전이하는 로직이 없어, 백테스트와 비교 가능한 실전 승률 데이터를 얻을 수 없다.
**Approach:** `publish_attempt`를 다시 `create or replace`해, close 분기의 SUSPENDED 감지 루프(Story 3.5) 바로 뒤에 TP/SL 판정 루프를 추가한다. 그 시점에 `status='OPEN'`이고 `entry_date < 오늘`인 outcome만 대상으로, 오늘자 `outcome_observations`(Story 3.4가 이미 기록)의 고가/저가로 SL 우선 판정 후 `outcome_events`에 idempotent하게 `TP`/`SL` 이벤트를 append하고 `candidate_outcome`을 terminal로 전이한다.

## Boundaries & Constraints

**Always:** 판정 대상은 SUSPENDED 감지 루프 실행 **이후** 재조회한 `status='OPEN'` 행만이다(같은 attempt에서 방금 SUSPENDED로 전이된 행은 자연히 제외 — 이것이 "3.5 미수행 또는 이미 SUSPENDED면 판정 보류" 가드의 구현이다). `entry_date < logical_row.trading_day`인 행만 판정하여 진입 당일 판정을 막는다(최소 보유 1거래일). 오늘자 `outcome_observations`(`outcome_id`, `evaluation_trading_day=오늘`) 행이 없으면(daily_ohlcv 결측/무효로 3.4가 기록하지 않은 경우) 판정을 건너뛴다 — 새로 daily_ohlcv를 재조회하지 않고 3.4가 이미 검증한 관찰만 근거로 쓴다. SL(`저가 <= 진입가×0.97`)을 TP(`고가 >= 진입가×1.03`)보다 먼저 확인해 같은 날 둘 다 충족하면 SL이 확정된다. `exit_price`는 각각 정확히 `entry_price×0.97`(SL) / `entry_price×1.03`(TP)로 기록하고 `return_pct`는 왕복 비용 0.1%p 차감한 고정값 `-3.1`(SL) / `2.9`(TP)로 기록한다(백테스트 엔진 `backtest/engine.py`의 `gross - cost_rate*200` 산식과 동일 결과). 이벤트 멱등 키는 기존 `outcome_events_open_command_key_idx(logical_run_key,ticker,strategy,command_type)`를 `command_type='TP'/'SL'`에도 그대로 재사용한다(신규 index 불필요). `publish_attempt` 반환 jsonb에 이번 attempt에서 신규 terminal 전이된 outcome을 `tp_sl_transitions` 배열(`outcome_id`,`ticker`,`strategy`,`status`,`exit_price`,`return_pct`)로 노출한다(Story 3.5 `suspended_transitions`와 동일 패턴, additive 필드).

**Never:** TIMEOUT 컷오프 확정이나 `holding_days`/`cutoff_n` 계산을 구현하지 않는다(Story 3.7 범위, 값은 기존 default 유지). SUSPENDED→정상 복귀나 DELISTED 종결, correction event를 구현하지 않는다(Story 3.8/3.9 범위). `record_outcome_observation`/SUSPENDED 감지 루프의 로직·호출 순서를 변경하지 않는다 — 새 루프는 그 뒤에 추가만 한다. terminal(TP/SL) 이미 도달한 행을 다시 조회하거나 갱신하지 않는다(불변 invariant, `status='OPEN'` 필터로 자연히 배제). `daily_ohlcv`를 직접 재조회하지 않는다(오늘자 `outcome_observations`만 근거로 삼아 3.4의 검증을 재사용).

## I/O & Edge-Case Matrix

| Scenario | Input / State | Expected Output / Behavior | Error Handling |
|----------|--------------|---------------------------|----------------|
| TP 확정 | OPEN outcome, entry_date<오늘, 오늘 관찰 고가>=entry×1.03, 저가>entry×0.97 | status=TP, exit_price=entry×1.03, return_pct=2.9, outcome_events에 TP 1행 | 없음 |
| SL 확정 | OPEN outcome, entry_date<오늘, 오늘 관찰 저가<=entry×0.97 | status=SL, exit_price=entry×0.97, return_pct=-3.1, outcome_events에 SL 1행 | 없음 |
| 동일일 TP·SL 동시 충족 | 오늘 관찰 고가>=entry×1.03 이고 저가<=entry×0.97 | SL이 우선 확정(TP 아님) | 없음 |
| 진입 당일 | entry_date = 오늘(logical_row.trading_day) | 판정 없음, OPEN 유지(임계값 충족해도 무시) | 없음 |
| 임계값 미달 | 오늘 관찰 고가<entry×1.03 이고 저가>entry×0.97 | 판정 없음, OPEN 유지 | 없음 |
| 이미 SUSPENDED(같은 attempt에서 방금 전이 포함) | candidate_outcome.status가 SUSPENDED | 판정 대상에서 제외, TP/SL 미확정 | 없음 |
| 오늘 관찰 없음 | 오늘 `outcome_observations` 행 없음(daily_ohlcv 결측/무효) | 판정 건너뜀, OPEN 유지 | 없음 |
| terminal 재판정 시도 | status가 이미 TP/SL | 판정 대상 쿼리(`status='OPEN'`)에서 애초에 제외 | 없음 |
| 재시도(동일 attempt 재발행) | 이미 `(logical_run_key,ticker,strategy,'TP'|'SL')` 이벤트 존재 | 새 이벤트/전이 없이 재확인만 | 없음 |

</intent-contract>

## Code Map

- `infra/supabase/migrations/202609031800_detect_price_adjustment_suspension.sql` -- 현재 `publish_attempt`의 권위 있는 최신 정의(create or replace 대상 baseline). SUSPENDED 감지 루프(66-138행) 바로 뒤에 TP/SL 판정 루프를 추가한다.
- `infra/supabase/migrations/202609031700_record_close_batch_observations.sql` -- `record_outcome_observation` 정의. 오늘자 `outcome_observations`(high/low, `(outcome_id,evaluation_trading_day)` PK)를 이 스토리가 그대로 조회해 재사용한다(재검증 없음).
- `infra/supabase/migrations/202609031500_create_emit_open_command.sql:10-11` -- `outcome_events_open_command_key_idx(logical_run_key,ticker,strategy,command_type)` 선례. `command_type='TP'/'SL'`도 같은 index가 커버하므로 신규 index 불필요.
- `infra/supabase/migrations/202609031300_create_outcome_schema.sql:32-53` -- `candidate_outcome` 컬럼 정의(`exit_date`,`exit_price`,`return_pct`,`status` check가 이미 `TP`/`SL` 포함). 스키마 변경 불필요.
- `backtest/engine.py:152-153` -- `gross = (exit_price/entry_price-1)*100`, `net = gross - cost_rate*200`(cost_rate=0.0005) 산식 선례. 이 스토리의 고정값(+2.9/-3.1)이 이 산식과 정확히 일치함을 Design Notes에서 확인한다.
- `tests/sql/test_run_lineage.sql:387-533` (`close:2099-01-11` SUSPENDED 시나리오) -- 이번 스토리의 TP/SL 시나리오를 자연스럽게 이어붙일 지점. 신규 티커로 TP/SL/동시충족/진입당일/미달/재시도 케이스를 추가한다.

## Tasks & Acceptance

**Execution:**
- `infra/supabase/migrations/202609032000_judge_tp_sl_outcomes.sql` -- `publish_attempt`를 `create or replace`해 SUSPENDED 루프 뒤에 TP/SL 판정 루프를 추가한다: `status='OPEN' and entry_date < logical_row.trading_day`인 `candidate_outcome`을 `for update`로 순회 → 오늘자 `outcome_observations` 조회(없으면 skip) → SL 우선 판정 → 확정 시 `outcome_events` insert(`on conflict (logical_run_key,ticker,strategy,command_type) do nothing`) + `candidate_outcome` terminal 갱신(`status`,`exit_date`,`exit_price`,`return_pct`) + 반환 jsonb `tp_sl_transitions` 배열에 누적.
- `tests/sql/test_run_lineage.sql` -- I/O 매트릭스 9개 시나리오를 커버하는 fixture를 기존 close 시나리오에 추가.
- `packages/read-model/src/database.types.ts` -- 운영 project에 migration 적용 후 Supabase 생성 타입 갱신 확인(함수 시그니처 불변이므로 diff 없을 수 있음, 확인만).

**Acceptance Criteria:**
- Given OPEN 상태 outcome의 진입일이 있는 경우, when 판정을 시작하면, then 진입 다음 거래일부터 판정하며 진입일 당일에는 TP/SL이 발생하지 않는다.
- Given 관찰치의 고가가 진입가×1.03 이상인 경우, when 판정하면, then TP로 확정된다(등호 포함).
- Given 관찰치의 저가가 진입가×0.97 이하인 경우, when 판정하면, then SL로 확정된다(등호 포함).
- Given 동일 거래일에 TP·SL 조건이 모두 충족되는 경우, when 우선순위를 적용하면, then SL이 우선 확정된다.
- Given TP 또는 SL이 확정되는 경우, when 손익률을 기록하면, then 왕복 0.1% 비용 차감 후 TP는 정확히 +2.9%, SL은 정확히 -3.1%로 기록된다.
- Given terminal 상태(TP/SL)가 확정된 경우, when 이후 배치가 같은 outcome을 다시 판정하려 하면, then 이미 terminal이므로 재판정하지 않는다.
- Given 아직 SUSPENDED 감지가 수행되지 않았거나 이미 SUSPENDED로 판정된 경우, when TP/SL 판정을 시도하면, then 판정은 보류되며 자동 확정되지 않는다.

## Spec Change Log

## Review Triage Log

### 2026-09-03 — Review pass
- intent_gap: 0
- bad_spec: 0
- patch: 0
- defer: 2: (high 0high, medium 0medium, low 2low)
- dismissed:
  - TP/SL 임계값(1.03/0.97)과 비용 반영 고정 수익률(2.9/-3.1)이 `price_adjustment_gap_threshold()`처럼 별도 함수로 추출되지 않고 하드코딩됐다는 지적(blind-hunter) — 이 값들은 epics.md Story 3.6 AC가 명시한 리터럴 값 자체이며, 3.5의 0.30(명시적으로 "조정 가능"해야 한다고 서술됨)과 달리 운영 조정 가능성이 요구되지 않는 스펙 고정값이라 추출할 이유가 없다.
  - 오늘자 `outcome_observations.high`/`low`가 NULL이면 판정이 조용히 no-op된다는 지적(blind-hunter) — `outcome_observations.high`/`low`는 `202609031300_create_outcome_schema.sql`에서 `not null and > 0` 제약이 있어 이 경로 자체가 존재하지 않는다.
  - `entry_price`가 NULL/비양수인 레거시 행에 대한 방어 로직이 없다는 지적(blind-hunter) — `candidate_outcome.entry_price`도 동일 스키마에서 `not null and > 0`으로 강제되어 도달 불가능하다.
  - `exit_price`가 실제 고가/저가가 아닌 임계값 자체로 고정되어 실제 손익을 과소평가하고 슬리피지 감사 정보가 없다는 지적(blind-hunter) — epics.md Story 3.6 AC가 "왕복 0.1% 비용 차감 후 TP는 정확히 +2.9%, SL은 정확히 -3.1%로 기록된다"고 명시적으로 요구한 스펙 자체의 의도이며, `backtest/engine.py`의 동일 산식과 정합성을 확보하기 위한 의도적 설계다.
  - premarket/intraday batch_kind에서 TP/SL 루프가 실제로 건너뛰어지는지 전용 테스트가 없다는 지적(blind-hunter) — 새 루프는 tag/관찰/SUSPENDED 루프와 동일하게 `if logical_row.batch_kind = 'close' then ... end if;` 블록 안에 중첩되어 구조적으로 자명하며, 이 구조적 가드는 Story 3.2~3.5도 별도 intraday 전용 테스트 없이 동일하게 신뢰해 온 선례와 일치한다.
  - 동일 (ticker,strategy)에 대해 두 OPEN 행이 동시에 존재해 멱등 키가 충돌할 수 있다는 지적(blind-hunter/edge-case-hunter 공통 우려) — `candidate_outcome_one_open_per_ticker_strategy_idx` partial unique index가 (ticker,strategy)당 OPEN을 최대 1개로 강제해 이 시나리오 자체가 스키마 수준에서 불가능함을 edge-case-hunter가 확인했다.
  - 동일일 TP·SL 동시 충족 테스트(ZZLIN16)가 정확히 양쪽 경계값(고가=103, 저가=97)이 아닌 여유 있는 값(고가 105, 저가 95)을 쓴다는 지적(blind-hunter) — 코드의 SL 우선 비교(`<=`/`>=`)는 경계값 정확도와 무관하게 동일한 분기를 타므로, 정확한 경계값 테스트가 추가돼도 다른 결함을 드러내지 못한다.
  - 계산된 `exit_price`에 반올림/스케일 정규화가 없어 `entry_price`의 정밀도에 따라 부정확해질 수 있다는 지적(blind-hunter) — PostgreSQL `numeric` 타입은 부동소수점이 아닌 정확한 십진 연산을 수행하므로 이 우려의 전제(부동소수점 오차) 자체가 이 데이터베이스 엔진에 적용되지 않는다.
  - `database.types.ts` 갱신 확인 작업이 실제로 수행됐다는 증거가 diff에 없다는 지적(blind-hunter) — verification-gap 리뷰가 독립적으로 해당 파일의 컬럼 타입이 이번 변경과 무관함(제네릭 `string` 타입, `publish_attempt` 시그니처 불변)을 확인해 diff 부재가 실제로 정확한 상태임을 검증했다.
  - `create or replace function`에 대한 별도 rollback/down migration이 없다는 지적(blind-hunter) — 이 저장소의 모든 이전 migration(Story 1.x~3.5)이 동일하게 forward-only이며 git 이력을 되돌림 경로로 삼는 기존 컨벤션과 일치해 이 스토리만의 새로운 공백이 아니다.
  - `publish_attempt`가 close attempt당 `candidate_outcome`을 세 번(관찰/SUSPENDED/TP·SL) 순회하는 성능 우려에 대한 대규모 데이터 테스트가 없다는 지적(blind-hunter) — 동일한 성격의 "전체 스캔" 우려가 Story 3.2~3.5 리뷰에서 실측 근거 없는 조기 최적화 우려로 반복 기각된 선례가 있고, 이번에도 구체적 재현이나 실측 근거가 제시되지 않았다.
  - 일봉 기준 SL-우선 판정이 실제 장중 체결 순서(TP가 먼저 도달한 후 SL로 반전 등)와 다를 수 있는 단순화라는 점이 별도로 명시되지 않았다는 지적(blind-hunter) — epics.md Story 3.6 AC가 "동일 거래일에 TP와 SL이 모두 충족되는 경우... SL이 우선 확정된다(보수적)"고 이 단순화 규칙 자체를 명시적으로 요구하고 있어 스펙이 의도한 설계이지 누락이 아니다.
- addressed_findings:
  - none

## Design Notes

`return_pct` 고정값(+2.9/-3.1)의 근거: `backtest/engine.py`의 실현 손익 산식은 `gross=(exit_price/entry_price-1)*100`, `net=gross-cost_rate*200`(`cost_rate=0.0005`, 왕복 0.1%). `exit_price`를 TP/SL 임계값 자체(진입가×1.03 / ×0.97, 실제 도달한 고가/저가가 아님)로 고정하면 `gross`가 정확히 ±3.0이 되어 `net`이 +2.9/-3.1로 정확히 일치한다. 이는 백테스트와 동일 기준으로 비교 가능해야 한다는 에픽 목표(Goal)와 정합한다.

## Verification

**Commands:**
- `psql -v ON_ERROR_STOP=1 "$DATABASE_URL" -f tests/sql/test_run_lineage.sql` -- expected: 모든 assertion 통과 후 rollback.
- `npm run typecheck` -- expected: 갱신된 DB 타입을 소비하는 TypeScript 전체 통과.
- `uv run --with pandas --with numpy --with pyarrow --with pytest pytest` -- expected: 기존 batch/domain 회귀망 통과(`tests/batch/test_scheduler.py`의 7건은 Story 3.1~3.5에서도 동일하게 확인된 baseline 실패로 이 스토리와 무관).
- `git diff --check` -- expected: 공백 오류 없음.

**Manual checks (if no CLI):**
- Supabase MCP로 운영 project(`qqhjeumlecaudsiqhhdu`)에 migration 적용, `publish_attempt` 함수 정의 갱신 및 fixture pass를 확인한다.
- UI 변경이 없는 DB 전용 스토리이므로 Playwright E2E는 적용 대상이 아니다(Story 3.1~3.5와 동일 판단).

## Auto Run Result

**구현 요약:** 운영 Supabase project(`qqhjeumlecaudsiqhhdu`)에 `publish_attempt`를 다시 `create or replace`해, Story 3.5의 SUSPENDED 감지 루프 뒤에 TP/SL 판정 루프를 추가했다. 그 시점에 재조회한 `status='OPEN' and entry_date < 오늘`인 `candidate_outcome`만 대상으로, 오늘자 `outcome_observations`(Story 3.4가 이미 기록, `daily_ohlcv` 재조회 없음)의 고가/저가로 SL(`저가<=entry×0.97`)을 TP(`고가>=entry×1.03`)보다 먼저 확인해 동일일 동시 충족 시 SL을 우선 확정한다. 확정 시 `outcome_events`에 `command_type='TP'/'SL'`을 기존 `outcome_events_open_command_key_idx`로 idempotent하게 append하고 `candidate_outcome`을 terminal로 전이하며(`exit_date`/`exit_price`/`return_pct`), `exit_price`는 임계값 자체(entry×0.97/1.03)로, `return_pct`는 왕복 0.1% 비용 차감 고정값(-3.1/2.9)으로 기록한다(`backtest/engine.py`의 `gross-cost_rate*200` 산식과 정확히 일치). 반환 jsonb에 `tp_sl_transitions` 배열을 추가로 노출한다. TIMEOUT 컷오프(Story 3.7)와 SUSPENDED 복귀(Story 3.8)는 범위 밖으로 명시적으로 남겼다.

**변경 파일:**
- `infra/supabase/migrations/202609032000_judge_tp_sl_outcomes.sql` -- 신규. `publish_attempt`에 TP/SL 판정 루프 추가.
- `tests/sql/test_run_lineage.sql` -- I/O 매트릭스 9개 시나리오(`close:2099-01-13`, ZZLIN14~21: TP, SL, 동일일 동시충족(SL우선), 진입당일 제외, 임계값 미달, 이미 SUSPENDED 제외, 관찰 없음 skip, terminal 재판정 제외, 재시도 idempotency)를 추가. 기존 Story 3.5 시나리오(ZZLIN10)의 entry_price/daily_ohlcv 값을 조정해 새 TP/SL 판정과 우연히 충돌하지 않도록 보강.
- `packages/read-model/src/database.types.ts` -- 확인 결과 diff 없음(`publish_attempt` 시그니처 불변, Supabase 생성 타입은 함수 comment를 반영하지 않음).

**리뷰 findings 분류:** patch 0건, defer 2건(모두 low: `outcome_events_open_command_key_idx` 인덱스 이름이 OPEN 전용 명명을 유지한 채 SUSPENDED/TP/SL까지 재사용되는 명명 불일치, `publish_attempt` comment가 스토리마다 무한정 누적되는 인라인 변경 이력), dismissed 12건(하드코딩된 TP/SL 임계값·고정 수익률[epics AC 명시 리터럴], observation/entry_price NULL 방어 부재[스키마 NOT NULL로 도달 불가], exit_price 임계값 고정[스펙이 명시한 의도], premarket/intraday 전용 테스트 부재[구조적 중첩으로 자명, 기존 선례], 동일 (ticker,strategy) 중복 OPEN 충돌 우려[partial unique index로 불가능], 동일일 동시충족 테스트가 여유 마진 사용[분기 로직이 마진과 무관], exit_price 반올림 부재[numeric은 정확한 십진 연산], database.types.ts 확인 증거 부재[verification-gap이 독립 확인], rollback migration 부재[저장소 전체 컨벤션], 3회 전체 스캔 성능 우려[Story 3.2~3.5에서 반복 기각된 미실측 우려], SL-우선 규칙이 실제 장중 순서와 다를 수 있다는 점 미기재[epics AC가 이 단순화 자체를 명시] -- 세부 근거는 Review Triage Log 참고).

**후속 리뷰 권고:** `false`(patch 0건 → 3×0+1×0=0 < 5).

**검증 수행:**
- Supabase MCP `execute_sql`로 운영 project에서 `tests/sql/test_run_lineage.sql` 전체를 독립적으로(구현 subagent와 별개로 이 세션이 직접) `begin;...rollback;`으로 감싸 재실행 -- 예외 없이 통과.
- `npm run typecheck` -- 통과(이 세션이 직접 재실행).
- `uv run --with pandas --with numpy --with pyarrow --with pytest pytest` -- 241 passed, 0 failed(이 세션이 직접 재실행; Story 3.5까지 존재하던 `tests/batch/test_scheduler.py` baseline 실패는 이번 baseline 커밋 이전에 이미 해소되어 있었다).
- `git diff --check` -- 공백 오류 없음(CRLF 관련 무해한 경고만 존재).
- Matrix Test Audit: I/O 매트릭스 9개 행 모두 실행되어 통과한 테스트로 커버됨을 확인.
- 4개 독립 리뷰 레이어(blind-hunter, edge-case-hunter, verification-gap, intent-alignment)를 병렬 실행 후 모든 finding을 개별 검증 -- 실제 결함으로 확인된 항목 없이 2건은 defer, 나머지는 스키마 불변식·기존 선례·스펙 자체 의도와 일치해 dismiss.
- UI 변경이 없는 DB 전용 스토리라 Playwright E2E는 적용 대상이 아니며 실행하지 않았다(spec 자체 판단과 Story 3.1~3.5 선례 일치).

**잔여 위험:**
- `outcome_events_open_command_key_idx` 인덱스 이름이 SUSPENDED/TP/SL까지 재사용하는 현재 역할을 반영하지 못한다(defer, low, Story 3.5부터의 기존 공백).
- `publish_attempt`의 `comment on function`이 스토리마다 이력을 계속 덧붙이는 방식이라 3.7/3.8/3.9가 이어질수록 무한정 길어진다(defer, low, Story 3.5부터의 기존 관행).
- Story 3.5가 남긴 잔여 위험(emit_open_command의 SUSPENDED 재진입 가드 미비, daily_ohlcv 0/음수 종가 무방비, `publish_attempt` 프로덕션 미배선)은 이 스토리와 무관하게 여전히 미해결이다(`deferred-work.md` 참조).
- `publish_attempt`가 close attempt당 `candidate_outcome`을 세 번(관찰/SUSPENDED/TP·SL) 순회한다 -- Story 3.2~3.5와 동일한 이유로 현재는 AC가 요구하는 정상 동작이자 NFR-7로 유계이지만, Story 3.7의 TIMEOUT 컷오프가 같은 행 집합에 네 번째 순회를 추가하면 잠금 경합을 재검토할 필요가 있다.
