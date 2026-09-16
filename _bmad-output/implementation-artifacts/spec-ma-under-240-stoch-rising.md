---
title: '240이평 아래 돌파 전략 스토캐스틱 K/D 상승 필터'
type: 'feature'
created: '2026-09-16'
status: 'done'
review_loop_iteration: 0
baseline_commit: '287c5ff'
context: []
---

<frozen-after-approval reason="human-owned intent — do not modify unless human renegotiates">

## Intent

**Problem:** 스토캐스틱 쌍바닥 확정 필터 대신 더 단순한 K/D 상승 필터의 성과를 비교한다.

**Approach:** 기존 240이평 하회·SMA20>SMA60·선택 SMA 상향돌파 조건에 5-3-3 slow K와 D가 모두 전일보다 상승하는 조건을 AND 결합해 SMA3~120을 재실행한다.

## Boundaries & Constraints

**Always:** 기존 `stochastic` 계산의 5-3-3 slow K/D를 사용하고 K[t]>K[t-1], D[t]>D[t-1]을 동시에 요구한다. TP/SL 3%, 익절 우선, 종목별 청산 전 재진입 차단은 유지한다.

**Never:** 기존 공통 지표나 운영 전략 API를 수정·등록하지 않는다. 쌍바닥 결과를 덮어쓰지 않는다.

## I/O & Edge-Case Matrix

| Scenario | Input / State | Expected Output / Behavior | Error Handling |
|---|---|---|---|
| 상승 필터 통과 | K와 D가 모두 전일보다 큼 | 이평 조건 충족 시 신호 | N/A |
| 상승 필터 차단 | K 또는 D가 하락/동일 | 신호 없음 | N/A |
| 초기 구간 | K/D가 NaN | 신호 없음 | N/A |

</frozen-after-approval>

## Code Map

- `backtest/indicator_opt/strategy_ma_under_240.py` -- `stoch_mode='rising'`과 5-3-3 K/D 상승 마스크, 별도 결과 폴더를 제공한다.
- `backtest/indicators/__init__.py:64-88` -- 기존 stochastic 5-3-3 계산 원천이다.
- `backtest/tests/test_strategy_ma_under_240.py` -- 필터 조합 회귀 테스트다.

## Tasks & Acceptance

**Execution:**
- [x] `backtest/indicator_opt/strategy_ma_under_240.py` -- K/D 동시 상승 모드를 추가하고 그리드를 실행한다 -- 비교 가능한 결과를 만든다.
- [x] `backtest/tests/test_strategy_ma_under_240.py` -- 상승·차단·기존 조건을 검증한다 -- 회귀를 고정한다.

**Acceptance Criteria:**
- Given K와 D가 모두 상승하고 이평 조건이 충족되면, when 신호를 계산하면, then 진입 신호가 생성된다.
- Given K 또는 D가 상승하지 않으면, when 신호를 계산하면, then 진입 신호가 생성되지 않는다.

## Spec Change Log

## Review Triage Log

## Verification

**Commands:**
- `uv run --with pytest pytest backtest/tests/test_strategy_ma_under_240.py` -- expected: 5 passed.
- `uv run --with pytest pytest backtest/tests` -- expected: 254 passed.
- `uv run python -m backtest.indicator_opt.strategy_ma_under_240 --stoch-mode rising` -- expected: 118개 기간 결과 생성.

실행 결과(2026-09-16): 신규 5개, 전체 254개 테스트 통과. K/D 동시 상승 조건으로 118개 기간 그리드 완료. 최고 PF는 SMA109 1.0198, 최고 누적수익률도 SMA109의 -3.57%였다.
