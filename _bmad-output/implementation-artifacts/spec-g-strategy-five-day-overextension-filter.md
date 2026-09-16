---
title: '전략 G 5일 고점 대비 과열 종목 제외'
type: 'feature'
created: '2026-09-16'
status: 'done'
review_loop_iteration: 0
baseline_commit: '95373e6fbd72a7c6d93c9d9803c9563f9fe4aae7'
context: []
---

<frozen-after-approval reason="human-owned intent — do not modify unless human renegotiates">

## Intent

**Problem:** 전략 G(양음돌파패턴)가 거래량 돌파와 풀백 이후에도 이미 단기간 급등한 종목을 후보로 관측하고 있어, 진입 후보의 과열 구간을 추가로 걸러야 한다.

**Approach:** 전략 G의 최종 진입 마스크에 신호일 직전 5개 거래일의 고가 최고값을 기준으로 한 과열 필터를 추가한다. 신호일 종가가 해당 최고값보다 5%를 초과하면 신호를 제외하고, 정확히 5% 이내인 신호는 유지한다.

## Boundaries & Constraints

**Always:** 기존 거래량 돌파 양봉 → 음봉 풀백 → 풀백 고가 돌파 조건은 그대로 유지한다. 5일은 달력일이 아니라 OHLCV의 직전 5개 거래행이며, 기준 가격은 `High`다. 신호일 자체는 기준 구간에 포함하지 않는다. 유효한 OHLCV 입력 검증과 A~H 전략 API의 boolean mask/파라미터 계약을 깨뜨리지 않는다.

**Never:** 전략 A~F 또는 H의 조건을 변경하지 않는다. 청산 파라미터, Supabase 스키마/데이터, 후보 UI, 기존 baseline 결과 파일을 이 작업에서 변경하지 않는다. 현재 종가보다 미래 데이터를 참조하거나, 정확히 5%인 경계값을 제외하지 않는다.

## I/O & Edge-Case Matrix

| Scenario | Input / State | Expected Output / Behavior | Error Handling |
|----------|--------------|-----------------------------|----------------|
| 과열 신호 | 기존 G 조건을 만족하고 `Close > max(직전 5개 High) * 1.05` | 해당 행의 G mask는 `False` | N/A |
| 허용 경계 | 기존 G 조건을 만족하고 `Close == max(직전 5개 High) * 1.05` | 해당 행의 G mask는 `True` | N/A |
| 일반 신호 | 기존 G 조건을 만족하고 종가가 직전 5일 고점의 5% 이내 | 기존과 동일하게 `True` | N/A |
| 다른 전략 | A~F/H 계산 요청 | 결과와 파라미터 계약 불변 | N/A |

</frozen-after-approval>

## Code Map

- `backtest/indicator_opt/strategy_g.py:40-110` -- `StrategyGParams`와 입력 검증. 새 필터는 고정된 G 진입 규칙으로 두며 기존 청산 파라미터 계약은 유지한다.
- `backtest/indicator_opt/strategy_g.py:209-249` -- `compute_strategy_g`가 `_breakout_pullback_mask` 결과를 최종 G 진입 mask로 반환하는 지점. 직전 5개 `High` rolling 최고값과 신호일 `Close` 비교를 이 경계에 적용한다.
- `backtest/indicator_opt/strategy_custom_vol_breakout_pullback.py:38-77` -- 기존 거래량 돌파/음봉 풀백 검출 로직. 재사용하며 수정하지 않는다.
- `backtest/strategy_api.py:23-57,260-280` -- A~H 전략 API 등록 및 G 파라미터 메타데이터 소비 지점. 회귀 확인 대상이며 변경하지 않는다.
- `backtest/tests/test_params_sql_parity.py:8-72` -- 전략 파라미터 및 SQL 청산 계약 회귀 테스트. 새 필터가 기존 파라미터 parity를 바꾸지 않는지 확인한다.
- `backtest/tests/test_strategy_g.py` -- 최소 OHLCV fixture로 과열 제외, 정확히 5% 경계 유지, 일반 G 신호 유지, 입력 mask 형태를 검증할 신규 단위 테스트.

## Tasks & Acceptance

**Execution:**
- [x] `backtest/indicator_opt/strategy_g.py` -- 직전 5개 거래일 `High` 최고값 대비 신호일 `Close`의 5% 초과 상승을 최종 G mask에서 제외하도록 구현한다 -- 급등 후보를 G 전략에서 제거한다.
- [x] `backtest/tests/test_strategy_g.py` -- 기존 G 패턴 fixture와 경계값을 구성해 필터의 과열/경계/일반 동작 및 mask 계약을 단위 테스트한다 -- 회귀 가능한 증거를 남긴다.

**Acceptance Criteria:**
- Given 기존 양음돌파패턴 조건을 만족하는 종목, when 신호일 종가가 직전 5개 거래일 고가 최고값보다 5% 초과 높으면, then 전략 G 신호가 생성되지 않는다.
- Given 기존 양음돌파패턴 조건을 만족하는 종목, when 신호일 종가가 직전 5개 거래일 고가 최고값보다 정확히 5% 높으면, then 전략 G 신호가 유지된다.
- Given 기존 조건과 과열 필터를 함께 계산할 때, when `compute_abc`가 A~H를 계산하면, then 모든 전략 mask의 인덱스/boolean 타입과 G 이외 전략 결과가 기존 계약을 유지한다.

## Spec Change Log

## Review Triage Log

- Blind #1(최소 길이와 `max_pullback`의 관계)은 기존 동작이며 이번 필터가 만든 회귀가 아니므로 deferred 처리했다.
- Blind #2(십진 5% 경계의 부동소수점 오판)는 실제 가능성을 확인해 tolerance와 십진 경계 테스트를 추가했다.
- Blind #3(경계 테스트가 같은 산식으로 임계값 생성)는 실제 검증 공백을 확인해 `3.80 → 3.99` 테스트를 추가했다.
- Blind #4(주말/휴장일 테스트 부재)는 구현이 달력일이 아닌 행 기반 rolling을 사용하고 있어 런타임 결함이 아니며, 영업일 fixture로 보강했다.
- Blind #5(`High`와 `Close`가 같은 fixture)는 기준 고가가 종가보다 높은 돌파봉으로 바꾸고 경계 테스트로 보강했다.
- Blind #6(미래 데이터 누수 테스트 부재)은 실제 검증 공백을 확인해 이후 행 변경 불변성 테스트를 추가했다.
- Blind #7(비기본 파라미터 테스트 부재)은 새 규칙이 고정 계약이고 기존 파라미터 검증 범위 밖이므로 dismissed 처리했다.
- Blind #8(필터 상수의 params 메타데이터 미포함)은 고정 진입 규칙을 청산 파라미터에 섞지 않는 현재 계약이 의도된 것이므로 dismissed 처리했다.
- Blind #9(`strategy_g_signals` 테스트 부재)은 실제 소비 경로 공백을 확인해 경계/과열 신호 변환 테스트를 추가했다.
- Blind #10(`run_strategy_g_backtest` 직접 테스트 부재)은 실행기가 변경되지 않았고 전체 커널 회귀가 통과해 이번 변경의 검증 결함으로 확인되지 않아 dismissed 처리했다.
- Blind #11(API mock 경로)은 실제 `compute_abc` 경로의 mask 계약 테스트가 존재하고 전체 회귀가 통과해 dismissed 처리했다.
- Blind #12(invalid segment rolling 혼합)은 백테스트가 유효 구간별로 함수를 호출하고 직접 함수는 invalid OHLCV를 거부하므로 dismissed 처리했다.
- Blind #13~#14(골든 fixture의 G/H 및 A~F/H 비교 부재)는 기존 골든 fixture 범위와 무관한 제안이며, 변경된 G 경로의 직접 회귀 테스트가 있어 dismissed 처리했다.
- Blind #15와 Verification #1(필터 전 baseline 산출물의 최신성)은 별도 baseline 재생성 작업으로 묶어 deferred 처리했다.
- Blind #16(검증 결과가 spec에 기록되지 않음)은 targeted 39 passed와 전체 168 passed의 실제 결과를 Verification에 기록했다.
- Blind #17(matrix에 추가 경계가 없음)은 frozen intent에 없는 별도 요구이고 현재 입력 검증/워밍업 guard가 처리하므로 dismissed 처리했다.
- Blind #18(Code Map line drift)은 비동작 문서 정합성 문제로 확인해 현재 구현 위치로 갱신했다.
- Blind #19~#22 및 Edge #1~#2(AGENTS 정책/관리 블록 변경)는 사용자 기존 변경이며 이번 story가 원인이 아니므로 deferred 처리하고 파일을 보존했다.

## Verification

**Commands:**
- `uv run --with pytest pytest backtest/tests/test_strategy_g.py backtest/tests/test_strategy_api.py backtest/tests/test_params_sql_parity.py` -- expected: all targeted strategy and API/parity tests pass.
- `uv run --with pytest pytest backtest/tests` -- expected: complete backtest regression suite passes.

실행 결과(2026-09-16): targeted suite `39 passed in 1.48s`, 전체 backtest suite `168 passed in 67.35s`.

## Suggested Review Order

**과열 필터 진입 경계**

- 최종 G 마스크에 기존 패턴과 5일 고점 필터를 결합합니다.
  [`strategy_g.py:209`](../../backtest/indicator_opt/strategy_g.py#L209)

- 신호일을 제외한 직전 5개 `High`와 엄격한 5% 초과 규칙을 적용합니다.
  [`strategy_g.py:236`](../../backtest/indicator_opt/strategy_g.py#L236)

- 십진 호가의 정확한 경계를 부동소수점 오차로부터 보호합니다.
  [`strategy_g.py:245`](../../backtest/indicator_opt/strategy_g.py#L245)

**회귀 및 소비 경로**

- 일반·경계·과열 입력에서 최종 boolean mask 결과를 고정합니다.
  [`test_strategy_g.py:39`](../../backtest/tests/test_strategy_g.py#L39)

- 필터 결과가 실제 `SimpleSignal` 생성까지 전달되는지 확인합니다.
  [`test_strategy_g.py:78`](../../backtest/tests/test_strategy_g.py#L78)

- 신호 이후 데이터 변경이 과거 신호에 영향을 주지 않음을 검증합니다.
  [`test_strategy_g.py:62`](../../backtest/tests/test_strategy_g.py#L62)

- 기존 사용자 변경과 별도 후속 작업을 커밋에 보존했음을 확인합니다.
  [`AGENTS.md:1`](../../AGENTS.md#L1)
  [`deferred-work.md:1`](deferred-work.md#L1)
