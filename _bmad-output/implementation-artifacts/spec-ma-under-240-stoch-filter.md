---
title: '240이평 아래 돌파 전략 스토캐스틱 쌍바닥 필터'
type: 'feature'
created: '2026-09-16'
status: 'done'
review_loop_iteration: 0
baseline_commit: 'd99cf54'
context: []
---

<frozen-after-approval reason="human-owned intent — do not modify unless human renegotiates">

## Intent

**Problem:** 기존 240이평 아래 단기 이평선 돌파 전략은 단기 반등이 충분히 확인되지 않은 신호도 진입 대상으로 포함한다.

**Approach:** 기존 이평선 돌파·SMA240 하회·SMA20>SMA60 조건에 스토캐스틱 5-3-3 %K 쌍바닥 확정 신호를 추가하고, 같은 TP/SL과 종목별 재진입 제약으로 SMA3~120 그리드를 재실행한다.

## Boundaries & Constraints

**Always:** 스토캐스틱은 기존 `sig_stoch_double_bottom`의 5-3-3 계산과 threshold 30 기준을 사용한다. 모든 기존 이평 조건과 +3%/-3% 익절·손절, 익절 우선, 동일 종목 단일 포지션 규칙을 유지한다. 미래 데이터로 현재 신호를 앞당기지 않는다.

**Never:** 기존 전략 A~K와 공통 스토캐스틱 구현을 수정하지 않는다. 운영 전략 API에 등록하지 않는다. threshold나 스토캐스틱 기간을 그리드 최적화 대상으로 확장하지 않는다.

## I/O & Edge-Case Matrix

| Scenario | Input / State | Expected Output / Behavior | Error Handling |
|---|---|---|---|
| 필터 통과 | 이평선 조건과 5-3-3 쌍바닥 확정이 같은 봉 | 진입 신호 생성 | N/A |
| 필터 차단 | 이평선 조건은 충족하지만 쌍바닥 확정 없음 | 진입 신호 없음 | N/A |
| 기존 조건 보존 | 쌍바닥이 있어도 SMA240 하회·SMA20>SMA60·상향교차 중 하나가 거짓 | 진입 신호 없음 | N/A |

</frozen-after-approval>

## Code Map

- `backtest/indicator_opt/strategy_ma_under_240.py:91-126` -- 기존 SMA240/20/60 및 선택 SMA 교차 마스크에 스토캐스틱 필터를 결합한다.
- `backtest/indicator_opt/strategy_ma_under_240.py:129-171` -- 종목별 기간 그리드 실행과 공통 엔진 TP/SL 경로. 변경하지 않고 결과를 재실행한다.
- `backtest/indicator_opt/_signals.py:sig_stoch_double_bottom` -- 기존 5-3-3 %K 쌍바닥 확정 신호의 단일 원천이다.
- `backtest/engine.py:run_backtest` -- 익절 우선과 동일 종목 청산 전 재진입 차단을 제공한다.
- `backtest/tests/test_strategy_ma_under_240.py` -- 이평선 전략의 기존 회귀 테스트에 필터 통과·차단 케이스를 추가한다.

## Tasks & Acceptance

**Execution:**
- [ ] `backtest/indicator_opt/strategy_ma_under_240.py` -- 5-3-3 쌍바닥 확정 마스크를 기존 진입 조건에 AND 결합한다 -- 반등 확인 없는 돌파를 제외한다.
- [ ] `backtest/tests/test_strategy_ma_under_240.py` -- 필터 통과·차단 및 기존 조건 보존을 검증한다 -- 조건 조합 회귀를 고정한다.

**Acceptance Criteria:**
- Given 이평선 돌파 조건과 5-3-3 K 쌍바닥 신호가 같은 봉에 존재하면, when 진입 마스크를 계산하면, then 해당 이평 기간의 신호가 생성된다.
- Given 이평선 돌파만 존재하고 K 쌍바닥 신호가 없으면, when 진입 마스크를 계산하면, then 신호가 생성되지 않는다.
- Given K 쌍바닥 신호가 있어도 기존 이평 조건이 거짓이면, when 진입 마스크를 계산하면, then 신호가 생성되지 않는다.

## Spec Change Log

## Review Triage Log

## Verification

**Commands:**
- `uv run --with pytest pytest backtest/tests/test_strategy_ma_under_240.py` -- expected: 신규·기존 전략 테스트 통과.
- `uv run --with pytest pytest backtest/tests` -- expected: 전체 백테스트 회귀 통과.
- `uv run python -m backtest.indicator_opt.strategy_ma_under_240` -- expected: 필터 적용된 SMA 3~120 결과 CSV 생성.

실행 결과(2026-09-16): 신규 테스트 5개, 전체 백테스트 254개 통과. 실제 SMA 3~120 118개 그리드를 완료했으며 쌍바닥 필터 적용 후 총 118개 기간의 요약과 거래 CSV를 갱신했다.
