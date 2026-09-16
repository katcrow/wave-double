---
title: '240이평 아래 돌파 전략 의미 있는 양봉 필터 그리드'
type: 'feature'
created: '2026-09-16'
status: 'done'
review_loop_iteration: 0
baseline_commit: '1120125'
context: []
---

<frozen-after-approval reason="human-owned intent — do not modify unless human renegotiates">

## Intent

**Problem:** 단순 이평선 돌파봉 대신 몸통과 종가 위치가 좋은 양봉만 진입시키는 것이 유효한지 확인한다.

**Approach:** K/D 동시 상승 스토캐스틱 조건을 고정하고, 양봉 필터를 없음·몸통비율·ATR 추가·전체 품질의 4단계로 나누어 SMA3~120 그리드를 비교한다.

## Boundaries & Constraints

**Always:** 몸통비율은 0.55 이상, ATR 단계는 몸통이 ATR14의 0.5배 이상, 전체 단계는 종가 위치 0.75 이상과 윗꼬리 비율 0.25 이하를 추가한다. TP/SL은 3%, 익절 우선, 종목별 청산 전 재진입 차단을 유지한다.

**Never:** 기존 공통 지표와 운영 전략 API를 수정하지 않는다. 이전 쌍바닥·K/D 상승 결과 파일을 덮어쓰지 않는다.

## I/O & Edge-Case Matrix

| Scenario | Input / State | Expected Output / Behavior | Error Handling |
|---|---|---|---|
| 몸통 통과 | 양봉이고 몸통/전체범위≥0.55 | body 단계 통과 | N/A |
| ATR 통과 | 몸통≥ATR14×0.5 | atr 단계 통과 | ATR NaN이면 차단 |
| 전체 통과 | 종가위치≥0.75, 윗꼬리≤0.25 | full 단계 통과 | 범위 0이면 차단 |

</frozen-after-approval>

## Code Map

- `backtest/indicator_opt/strategy_ma_under_240.py` -- `_candle_filter`와 candle별 별도 결과 저장을 구현한다.
- `backtest/tests/test_strategy_ma_under_240.py` -- 단계별 양봉 필터 회귀를 검증한다.

## Tasks & Acceptance

**Execution:**
- [x] `backtest/indicator_opt/strategy_ma_under_240.py` -- 4단계 양봉 필터와 SMA3~120 실행을 추가한다 -- 단계별 비교 결과를 만든다.
- [x] `backtest/tests/test_strategy_ma_under_240.py` -- 몸통비율과 전체 필터 경계를 검증한다 -- 필터 계약을 고정한다.

**Acceptance Criteria:**
- Given candle mode를 all로 실행하면, when 그리드가 끝나면, then 4개 결과 폴더에 각각 118개 이평선 요약이 생성된다.
- Given full 필터를 적용하면, when 양봉 조건이 충족되지 않으면, then 해당 봉은 진입하지 않는다.

## Spec Change Log

## Review Triage Log

## Verification

**Commands:**
- `uv run --with pytest pytest backtest/tests/test_strategy_ma_under_240.py` -- expected: 6 passed.
- `uv run --with pytest pytest backtest/tests` -- expected: 255 passed.
- `uv run python -m backtest.indicator_opt.strategy_ma_under_240 --stoch-mode rising --candle-mode all` -- expected: 4개 결과 폴더 생성.

실행 결과(2026-09-16): 신규 6개, 전체 255개 테스트 통과. 4개 모드 모두 118개 기간 실행 완료.
