---
title: '240이평 아래 단기 이평선 상향돌파 그리드 백테스트'
type: 'feature'
created: '2026-09-16'
status: 'done'
review_loop_iteration: 0
baseline_commit: 'a8c1437b985861e4b930d1d96a09ce2b5cf200e3'
context: []
---

<frozen-after-approval reason="human-owned intent — do not modify unless human renegotiates">

## Intent

**Problem:** 240일 이동평균 아래에서 단기 이동평균선을 상향 돌파하는 종목을 매수하는 규칙의 성과를 이평 기간별로 확인할 필요가 있다.

**Approach:** SMA 3~120을 각각 독립적으로 시험하고, 신호일 종가가 SMA240 아래이며 SMA20>SMA60인 상향 교차만 종가 진입 신호로 만든다. 진입 후 +3% 익절/+3% 손절을 적용해 기간별 성과와 거래 상세를 CSV로 저장한다.

## Boundaries & Constraints

**Always:** 상향 교차는 전일 종가가 해당 SMA 이하이고 당일 종가가 SMA 초과로 마감한 경우다. 신호일 SMA240 아래, 신호일 SMA20>SMA60을 모두 요구한다. 청산은 다음 봉부터 평가하며 같은 봉에 TP와 SL이 모두 닿으면 TP 우선이다. 같은 종목의 새 진입은 직전 포지션 청산 이후에만 허용한다. OHLCV 유효성·시간순서·워밍업을 지킨다.

**Never:** 미래 봉을 신호 계산에 사용하지 않는다. 기존 전략 A~K, 운영 API, 사용자가 이미 변경한 파일과 결과물을 수정하지 않는다. 익절·손절 외 임의의 보유기간 제한이나 분할청산을 추가하지 않는다.

## I/O & Edge-Case Matrix

| Scenario | Input / State | Expected Output / Behavior | Error Handling |
|---|---|---|---|
| 유효한 돌파 | Close[t-1]≤SMA[t-1], Close[t]>SMA[t], Close[t]<SMA240[t], SMA20[t]>SMA60[t] | t에 1건의 진입 신호 | N/A |
| 조건 불충족 | 240이평 이상 또는 SMA20≤SMA60 또는 교차 아님 | 신호 없음 | N/A |
| 동시 TP/SL | 다음 봉 High가 TP 이상이고 Low가 SL 이하 | TP 가격·익절 사유로 종료 | 익절 우선 |
| 보유 중 재신호 | 같은 종목에 청산 전 추가 신호 | 추가 진입하지 않음 | 엔진의 종목별 last-exit 제약 |
| 워밍업 부족 | SMA240 계산값이 없는 구간 | 신호 없음 | N/A |

</frozen-after-approval>

## Code Map

- `backtest/indicator_opt/strategy_ma240_breakout.py` -- 기존 240이평 돌파 탐색 코드와 고정 결과 저장 관례를 참고한다. 기존 파일은 수정하지 않는다.
- `backtest/indicator_opt/strategy_k.py:279-415` -- 입력 검증, 유효 구간 분리, 관측창·지문·요약·CSV 저장 패턴을 재사용한다.
- `backtest/engine.py:run_backtest` -- 종목별 `last_exit_idx`로 청산 전 재진입을 차단하고 고정 TP/SL 및 `tp_first`를 처리한다.
- `backtest/metrics/metrics.py:summarize` -- 거래 수, 승률, PF, 누적수익률, MDD를 계산한다.
- `backtest/data/loader.py:load_all` -- 기존 parquet OHLCV 유니버스를 읽는 데이터 원천이다.
- `backtest/tests/test_engine.py` -- TP/SL 동시 도달과 동일 종목 재진입 제약의 기존 계약을 확인한다.

## Tasks & Acceptance

**Execution:**
- [x] `backtest/indicator_opt/strategy_ma_under_240.py` -- SMA 기간별 신호 계산, 고정 TP/SL 백테스트, 3~120 그리드 실행 및 CSV 출력을 구현한다 -- 사용자가 요청한 실험을 재현 가능하게 한다.
- [x] `backtest/tests/test_strategy_ma_under_240.py` -- 교차·필터·워밍업·익절우선·재진입 차단을 합성 OHLCV로 검증한다 -- 핵심 규칙의 회귀망을 만든다.

**Acceptance Criteria:**
- Given 유효 OHLCV와 SMA 기간 p, when 네 가지 진입 조건이 동시에 충족되면, then 해당 날짜에만 p 전략의 신호가 생성된다.
- Given 3≤p≤120, when 그리드 백테스트를 실행하면, then 모든 기간의 요약 행과 거래 상세가 생성되고 기간별 거래가 서로 섞이지 않는다.
- Given 보유 중인 종목에 후속 신호가 발생하면, when 기존 포지션이 아직 청산되지 않았으면, then 후속 진입은 생성되지 않는다.
- Given 다음 봉에서 TP와 SL이 동시에 도달하면, when 청산을 판정하면, then +3% 목표가를 익절 사유로 기록한다.

## Spec Change Log

## Review Triage Log

- 자동 리뷰 서브에이전트는 현재 세션에서 사용할 수 없어 실행하지 못했다. 대신 변경 파일 직접 검토, 매트릭스 5개 행을 커버하는 테스트, targeted/full 회귀 및 실제 그리드 실행으로 확인했다.

## Verification

**Commands:**
- `uv run --with pytest pytest backtest/tests/test_strategy_ma_under_240.py backtest/tests/test_engine.py` -- expected: all targeted tests pass.
- `uv run --with pytest pytest backtest/tests` -- expected: full backtest regression passes.
- `uv run python -m backtest.indicator_opt.strategy_ma_under_240` -- expected: 118개 기간의 요약/거래 CSV 생성 및 결과 출력.

실행 결과(2026-09-16): targeted 12 passed, 전체 backtest 253 passed. 실제 그리드 118개 기간 실행 완료.

## Design Notes

각 이평 기간은 독립적인 전략 곡선으로 비교한다. 한 기간 안에서는 신호 목록을 날짜순으로 정렬하고 엔진이 청산 전 재진입을 차단한다. 신호가 데이터 마지막 봉에 있으면 이후 청산 판정이 불가능하므로 엔진 계약에 따라 거래에서 제외한다.
