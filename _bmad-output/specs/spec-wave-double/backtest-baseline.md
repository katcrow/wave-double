# Backtest Baseline & Strategy Definitions

> Companion: 확정 전략 정의와 백테스트 기대치. 실전 성과 대조(CAP-7), 전략 태깅(CAP-2)의 근거.
> **2026-08-31 갱신** — 아래 판정 룰·비용·산식은 추정이 아니라 `backtest/` 실제 코드에서 확인한 값이며, 각 항목에 `file:line`을 병기한다. 실전 구현은 이 값을 그대로 재현해야 한다(FR-3, FR-8, FR-9).

## 확정 전략 3종 (docs/보조지표-최적화결과.md 기반)

- **전략 A** — (RSI+CCI & OBV) ∪ (RSI+IBS & OBV) ∪ (RSI+ADX & OBV), OBV window=3, ADX 25 완화
  - 실행: `python -m backtest.indicator_opt.union` (기존 CSV: `union_top3_plus_obv.csv`)
- **전략 B** — 일봉 스토캐스틱 %K(14-3) 쌍바닥 + 주봉 %K(20-3) 우상향
  - 실행: `python -m backtest.indicator_opt.stoch_db --k-period 14 --threshold 20 --weekly --wk-period 20 --wd-period 3`
- **전략 C** — 스토캐스틱 3바닥 하락 다이버전스 (K5·D3·div20·gap5)
  - 실행: `python -m backtest.indicator_opt.run --indicator div_stoch3`

전략 파라미터 상수는 `backtest/indicator_opt/combine_strategies.py:24-27`(`STOCH_DB`, `DIV3`)과 `backtest/indicator_opt/union.py`(`TOP3`, `VOLUME`)에 고정되어 있다.

## 전략 D — 돌파3%기법 후보 A

전략 D는 `docs/돌파3%기법_추가.md`의 후보 A를 사용한다. 파라미터는
`backtest/indicator_opt/strategy_d.py:26-41`의 `StrategyDParams`에 고정되어
있으며, N=20 고점 돌파·W=3 거래량 비율 <0.95·종가<SMA240·Wilder
RSI(10)의 6일 SMA가 전일 42 미만에서 당일 42 이상(동시에 30 이상)인 네
조건을 AND로 결합한다(`strategy_d.py:86-113`). 고점 돌파는 설계 결정에 따라
`High > 직전 20봉 High 최고값`으로 해석한다.

고정 익절 3%와 고정 손절 5%는 `strategy_d.py:116-135`에서 진입 종가를
기준으로 생성하고, 기존 단일 엔진에 왕복 0.1% 비용과 최대보유 20봉을
전달한다(`strategy_d.py:138-168`). 엔진은 기본값 `max_holding_bars=None`일
때 기존 동작을 유지하며, 옵션이 지정된 경우 TP/SL(SL 우선)을 먼저 판정한
뒤 최대보유일 종가로 `max_hold` 청산한다(`engine.py:21-41, 140-170`).

### 전략 D 재현 실행 결과

실행 명령:

```text
uv run --with pandas --with numpy --with pyarrow python -m backtest.indicator_opt.strategy_d --start 2020-08-03 --end 2026-08-27
```

CLI 기본값은 `--start 2020-08-03 --end 2026-08-27`이며, runner가 이 경계를
각 parquet 프레임에 적용한다(`strategy_d.py:26-27, 197-235, 267-276`). 같은
경계는 `--start YYYY-MM-DD --end YYYY-MM-DD`로 명시해 재현할 수 있다. 현재
기준 parquet 104종목(`backtest/data/loader.py:25-48`)을 이 고정 관측창으로
실행한 결과는 `backtest/results/indicator_opt/strategy_d_baseline.csv`에 저장된다.
실행 명령에 경계를 직접 써도 같은 결과를 얻는다. 결과 CSV에는 파라미터·데이터
fingerprint와 입력 품질 제외 행 수를 함께 기록한다. OHLCV 계약에 맞지 않는
244개 행은 baseline 계산에서 제외했으며, 직접 호출하는 전략 계산 함수는 이런
입력을 계속 오류로 거부한다. 이번 실행의 fingerprint는
`65909d5abd5edf8f7ca508567493b714d133743af80e2acd1a77493b7fb1780e`이다.

| 전략 | 시그널 | 거래수 | 승 | 패 | 승률 | PF | 평균수익 | 평균보유 | max_hold | 월간 거래 |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| D 후보 A | 19 | 19 | 15 | 4 | 78.95% | 2.1324 | +1.2158% | 4.53봉 | 0 | 0.2603 |

TP 15건은 비용 차감 후 +2.9%, SL 4건은 −5.1%로 기록되었다. 문서의
83.1%·77건은 현재 저장소의 기준 parquet와 위 canonical 판정 규칙으로
재현되지 않았다. 해당 수치를 만든 과거 데이터 스냅샷 또는 판정 코드가
저장소에 없어 차이의 단일 원인을 확정할 수 없으므로, 이 구현은 문서
기대치를 코드 근거로 주장하지 않고 관측값과 재현 조건을 함께 고정한다.
개별 거래 감사 자료는 `backtest/results/indicator_opt/strategy_d_baseline_trades.csv`에
저장되며, 이번 19건에는 거래량 0 봉 또는 |일간 등락| 25% 초과 봉이 포함된 거래가
각각 0건이었다.

동일 fingerprint·관측창에서 문서의 모호한 해석만 바꾼 통제 비교도 77건을 재현하지
못했다. `High` 돌파·현재 포함 거래량 창·RSI 평활은 19건/78.95%, 거래량을 직전
창과 비교하면 24건/83.33%, `Close` 돌파·현재 포함 창은 27건/66.67%, 평활 없는
RSI는 2건/50.00%였다. 따라서 현재 저장소에서 확인 가능한 차이는 과거 스냅샷 또는
보존되지 않은 원본 판정 구현의 차이로 남긴다.

### 전략 D — OOS(워크포워드) 검증 (Story 6.8, 2026-09-07)

`docs/돌파3%기법_추가.md`가 자체적으로 권고한 워크포워드 검증이다. 파라미터·엔진은
변경하지 않고(`strategy_d.py`/`engine.py` 그대로), 전체 관측창(2020-08-03~2026-08-27)을
in-sample(앞 4년, 2020-08-03~2024-08-27)과 OOS/holdout(뒤 2년, 이후 미사용 구간,
2024-08-28~2026-08-27)으로 시간순 분할해 각각 재실행했다. 파라미터가 이 저장소
데이터로 재적합된 적이 없으므로, 이 분할은 데이터 누출 방지가 아니라 "다른 시기에도
같은 규칙이 유지되는가"를 확인하는 목적이다.

실행 명령:

```text
uv run --with pandas --with numpy --with pyarrow python -m backtest.indicator_opt.strategy_d --start 2020-08-03 --end 2024-08-27 --output backtest/results/indicator_opt/strategy_d_oos_insample.csv
uv run --with pandas --with numpy --with pyarrow python -m backtest.indicator_opt.strategy_d --start 2024-08-28 --end 2026-08-27 --output backtest/results/indicator_opt/strategy_d_oos_holdout.csv
```

| 구간 | 관측창 | 종목수 | 시그널 | 거래수 | 승 | 패 | 승률 | PF | 평균수익 | 월간 거래 | data_fingerprint |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| in-sample | 2020-08-03~2024-08-27 | 98 | 13 | 13 | 10 | 3 | 76.92% | 1.8954 | +1.054% | 0.2653 | `a0af62663042e97e89b299f7623003fadf2893fc9dcc46927890630e8edb9de7` |
| OOS(holdout) | 2024-08-28~2026-08-27 | 104 | 4 | 4 | 3 | 1 | 75.00% | 1.7059 | +0.900% | 0.1600 | `302476fe706a6378b32914d87029bc41bd22546b75bfb237771f00283752bda7` |

결과 CSV: `backtest/results/indicator_opt/strategy_d_oos_insample.csv`(+`_trades.csv`),
`backtest/results/indicator_opt/strategy_d_oos_holdout.csv`(+`_trades.csv`). D는
`strategy_d.py`가 fingerprint를 **윈도우 적용 후 프레임**에서 계산하므로(구간별로
필터링된 유효 행이 다름) 두 구간의 fingerprint가 서로 다르며, 종목수(98→104)는
일부 종목이 in-sample 구간 이후에 상장해 뒤 구간에서만 유효 데이터를 갖기 때문이다
(`backtest/data/loader.py:25-50`).

**해석:** 승률(76.92%→75.00%, −1.92%p)과 PF(1.8954→1.7059, −0.1895)는 소폭
하락했으나 방향과 크기 모두 완만해 뚜렷한 과적합 신호로 보기 어렵다. 다만 OOS
거래수가 4건으로 매우 적어(월간 신호 빈도 0.26건 기준 2년 구간에 예상 가능한
범위) 승률·PF 단독으로 결론을 과신하지 않는다.

**결정: 유지.** in-sample 대비 OOS 열화가 작고 승률/PF 모두 실전 채택 기준(승률
>50%, PF>1)을 유지하므로 파라미터 재조정이나 전략 보류 없이 현재 상태를 유지한다.
표본이 4건뿐이라는 한계는 이후 실전 거래가 누적되며 자연히 보강될 것으로 본다.

## 전략 E — 익절2%·고정 SL5% 기법

전략 E는 `docs/익절2%_고정SL5%기법_추가.md:12-44`의 세 조건을 사용한다.
`backtest/indicator_opt/strategy_e.py:28-46`에 SMA20/60, OBV20, Wilder
ADX14≥20, 고정 TP2%·SL5%·최대보유30봉·편도 비용 0.0005를 상수 파라미터로
고정했다. SMA20이 SMA60을 전일 이하에서 당일 초과로 상향 돌파하고, OBV가
OBV20 SMA를 같은 방식으로 상향 돌파하며, ADX14가 20 이상인 행만 AND로
선택한다(`strategy_e.py:225-250`). ADX는 `backtest/indicators/__init__.py:120-215`
의 Wilder 평활값만 사용하며, 기존 `sig_adx()`의 +DI/-DI 상향 교차 조건은
포함하지 않는다.

고정 TP/SL 신호와 엔진 wiring은 `strategy_e.py:254-355`에 있다. 진입은
신호 당일 종가이고, 단일 엔진이 진입 다음 봉부터 `high >= TP`, `low <= SL`을
판정하며 같은 봉이면 SL을 우선한다(`engine.py:71-84, 124-167`). 엔진의
왕복 비용 산식은 `cost_rate × 200`이고(`engine.py:177-178`), 성과 승률·PF는
비용 차감 후 `return_pct`를 사용한다(`metrics/metrics.py:62-86`). 기준 parquet
유니버스는 `data/loader.py:32-50`의 `load_all()`에서 로드한다.

### 전략 E 재현 실행 결과

실행 명령:

```text
uv run --with pandas --with numpy --with pyarrow python -m backtest.indicator_opt.strategy_e --start 2020-08-03 --end 2026-08-27
```

`strategy_e.py:24-25,142-230,275-401`은 각 전체 parquet 프레임을 먼저
검사·fingerprint하고, 유효 행의 연속 segment별로 워밍업·신호·엔진을 실행한
뒤 관측창 안의 신호·거래만 집계한다. invalid 행은 계산 segment에서 제외하지만
fingerprint와 품질 카운트에는 포함하며, ticker·거래 정렬로 결과를 결정적으로
만든다. 현재 기준 parquet 104종목에서의 결과는
`backtest/results/indicator_opt/strategy_e_baseline.csv`와 거래별
`backtest/results/indicator_opt/strategy_e_baseline_trades.csv`에 저장된다.
fingerprint는 `b2e027e0f8155d3fbabfd310f52c31e82afd1079722ed579e98207ca112e73a3`이다.

| 전략 | 시그널 | 거래수 | 승 | 패 | 승률 | PF | 평균수익 | 평균보유 | max_hold | 월간 거래 |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| E | 19 | 19 | 14 | 5 | 73.68% | 1.0431 | +0.0579% | 3.05봉 | 0 | 0.2603 |

TP 14건은 비용 차감 후 +1.9%, SL 5건은 −5.1%로 기록되었다. 문서 원문
기대치인 승률 78.2%·PF 1.34·78건(평균 +0.37%, 평균보유 3.6일)은 현재
저장소의 기준 parquet와 위 canonical 판정 규칙에서 재현되지 않는다. 보존된
과거 데이터 스냅샷이나 기대치를 만든 원본 판정 코드가 없으므로 차이의 단일
원인은 확정할 수 없다. 따라서 기대치와 현재 관측치를 분리해 기록하며, 코드
근거 없는 일치를 주장하지 않는다.

### 전략 E — OOS(워크포워드) 검증 (Story 6.8, 2026-09-07)

`docs/익절2%_고정SL5%기법_추가.md`가 자체적으로 권고한 워크포워드 검증이다.
전략 D와 동일하게 파라미터·엔진 변경 없이 전체 관측창을 in-sample(2020-08-03~
2024-08-27)/OOS(holdout, 2024-08-28~2026-08-27)로 시간순 분할해 각각 재실행했다.

실행 명령:

```text
uv run --with pandas --with numpy --with pyarrow python -m backtest.indicator_opt.strategy_e --start 2020-08-03 --end 2024-08-27 --output backtest/results/indicator_opt/strategy_e_oos_insample.csv
uv run --with pandas --with numpy --with pyarrow python -m backtest.indicator_opt.strategy_e --start 2024-08-28 --end 2026-08-27 --output backtest/results/indicator_opt/strategy_e_oos_holdout.csv
```

| 구간 | 관측창 | 종목수 | 시그널 | 거래수 | 승 | 패 | 승률 | PF | 평균수익 | 월간 거래 | data_fingerprint |
| --- | --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | --- |
| in-sample | 2020-08-03~2024-08-27 | 98 | 15 | 15 | 12 | 3 | 80.00% | 1.4902 | +0.500% | 0.3061 | `b2e027e0f8155d3fbabfd310f52c31e82afd1079722ed579e98207ca112e73a3` |
| OOS(holdout) | 2024-08-28~2026-08-27 | 104 | 4 | 4 | 2 | 2 | 50.00% | 0.3725 | −1.600% | 0.1600 | `b2e027e0f8155d3fbabfd310f52c31e82afd1079722ed579e98207ca112e73a3` |

결과 CSV: `backtest/results/indicator_opt/strategy_e_oos_insample.csv`(+`_trades.csv`),
`backtest/results/indicator_opt/strategy_e_oos_holdout.csv`(+`_trades.csv`). E는
`strategy_e.py:296-310`이 fingerprint를 **윈도우 적용 전 원본 전체 프레임**에서
계산하므로(구간 분할은 신호·거래 필터링에만 적용) in-sample/OOS 두 실행의
fingerprint가 동일하다 — 같은 104종목 parquet 원본을 사용했다는 근거이며 결함이
아니다. 종목수 차이(98→104)는 전략 D와 같은 사유(일부 종목의 늦은 상장)다.

**해석 — DEGRADED_OOS.** 승률은 80.00%→50.00%(−30.00%p), PF는 1.4902→0.3725로
in-sample 대비 뚜렷하게 열화했고 OOS 평균수익은 −1.600%로 순손실 구간이다.
다만 OOS 거래수가 4건(2승 2패)에 불과해 이 열화가 구조적 과적합인지 표본 변동인지
통계적으로 판별할 수 없다. 수치를 은폐하지 않고 그대로 기록한다.

**결정: 조건부 유지(모니터링 강화), 파라미터 재조정은 하지 않음.** 이 스토리
범위는 검증·기록이며 파라미터 재조정은 하지 않는다(Boundaries & Constraints).
표본이 4건뿐이라 즉시 보류를 결정할 만한 통계적 근거는 부족하나, 방향과 크기
(승률 −30%p, PF<1로 하락)가 커 리스크로 명시적으로 추적한다: (1) 실전 태깅된
전략 E 후보의 실제 outcome을 Epic 5 성과 비교 화면에서 우선 관찰 대상으로
표시하고, (2) OOS 표본이 20건 이상 누적되는 시점에 재평가해 유지/재조정/보류를
재결정한다. 재조정이 필요하다고 판단될 경우 실제 파라미터 변경은 이 스토리
범위 밖의 별도 스토리로 남긴다.

## 전략 F — 각도 가속·이평선 쌍바닥 기법

전략 F는 `docs/각도가속_이평쌍바닥기법_추가.md`의 "표본 확대형" 파라미터를 사용한다. 파라미터는
`backtest/indicator_opt/strategy_f.py:39-54`의 `StrategyFParams`에 고정되어
있으며, 로그가격 30봉 최소제곱 선형회귀 기울기가 5봉 전 대비 0.004 이상 가속되고,
이평선(MA16)이 쌍바닥(국소 저점 2개, 높은 저점) 후 넥라인을 상향 돌파하는 두 조건을
AND로 결합한다(`strategy_f.py:243-266`). 가속은 `sig_angle_accel_ls`(`_signals.py:130-143`,
내부적으로 `_linreg_slope`(`_signals.py:97-113`) 재사용)의 rolling 최소제곱 기울기를 사용하며,
쌍바닥은 `_double_bottom_signal`(`_signals.py:332-372`)의 범용 쌍바닥 탐지기를 사용한다.
이평선(SMA16)의 워밍업 구간(첫 15봉, `NaN`)은 리뷰에서 지적된 대로 `0.0`으로 채워
쌍바닥 판정에 넣지 않고, 실제로 계산된 값만 잘라 넣은 뒤 워밍업 구간을 항상 `False`로
고정한다(`strategy_f.py:260-264`) — 그렇지 않으면 워밍업 경계의 인위적인 0값이 가짜
"첫 저점"으로 오인되어, 특히 유효하지 않은 OHLCV로 구간이 분리되는 종목(세그먼트 재시작)에서
실제로는 없는 쌍바닥이 허위로 발생할 수 있다.

고정 익절 3%와 고정 손절 4%는 `strategy_f.py:265-283`에서 진입 종가를
기준으로 생성하고, `tp_first=True` 옵션이 같은 봉 TP·SL 동시 도달 시
익절 우선을 적용한다(`strategy_f.py:302-306`). 기존 단일 엔진에 왕복 0.1%
비용을 전달한다. 엔진은 기본값 `max_holding_bars=None`으로 최대보유 제한이
없다.

### 전략 F 재현 실행 결과

실행 명령:

```text
PYTHONIOENCODING=utf-8 uv run --with pandas --with numpy --with pyarrow python -m backtest.indicator_opt.strategy_f --start 2020-08-03 --end 2026-08-27
```

CLI 기본값은 `--start 2020-08-03 --end 2026-08-27`이며, runner가 이 경계를
각 parquet 프레임에 적용한다(`strategy_f.py:35-36, 286-371`). 같은 경계는
`--start YYYY-MM-DD --end YYYY-MM-DD`로 명시해 재현할 수 있다. 현재 기준
parquet 104종목(`backtest/data/loader.py:25-48`)을 이 고정 관측창으로 실행한
결과는 `backtest/results/indicator_opt/strategy_f_baseline.csv`에 저장된다.

| 전략 | 시그널 | 거래수 | 승 | 패 | 승률 | PF | 평균수익 | 평균보유 | max_hold | 월간 거래 |
| --- | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: | ---: |
| F | 173 | 168 | 119 | 49 | 70.83% | 1.7178 | +0.8583% | 1.94봉 | 0 | 2.3014 |

fingerprint는 `b2e027e0f8155d3fbabfd310f52c31e82afd1079722ed579e98207ca112e73a3`이다.
F는 E와 동일하게 fingerprint를 윈도우 적용 전 원본 전체 프레임에서 계산한다.

104종목 중 244개 OHLCV 행이 유효하지 않아(`invalid_ohlcv_rows`) 해당 종목들은
그 지점에서 관측 구간이 여러 세그먼트로 분리되고(`strategy_f.py:_valid_segments`),
이 중 일부 세그먼트 경계에서 위에서 설명한 워밍업 0값 오탐이 발생해 리뷰 이전에는
시그널 199건·거래 194건·승률 70.10%·PF 1.6585로 과대 집계됐다. 워밍업 구간을
항상 `False`로 고정한 수정 후 재현한 위 수치(173/168/70.83%/1.7178)가 최종
baseline이다.

**해석:** 승률 70.83%, PF 1.7178로 A/B/C 기준치와 비교해도 양호하며, TP 3%/SL 4%의
대칭 구조와 평균 보유 1.94봉의 짧은 회전이 특징이다. 월간 2.3건으로 빈도는 낮으나
평균 수익 +0.86%로 "짧게 먹고 나오는" 성격이 명확하다.

**결정: 유지.** 승률>50%, PF>1의 실전 채택 기준을 충족하고, 과적합 우려가 적은
단순 조건(기울기 비교 + 패턴 인식)이므로 현재 상태를 유지한다.

## 백테스트 기대치 (104종목, 73개월, TP+3%/SL−3%)

| 전략 | 거래수 | 승 | 패 | 승률 | PF | 평균 보유 | 최대 보유 |
| --- | --- | --- | --- | --- | --- | --- | --- |
| A | 147 | 101 | 46 | 68.71% | 2.0540 | 2.51봉 | 15봉 |
| B | 541 | 373 | 168 | 68.95% | 2.0770 | 3.58봉 | 44봉 |
| C | 50 | 33 | 17 | 66.00% | 1.8159 | 3.52봉 | 26봉 |

원천: `backtest/results/indicator_opt/combined_A_B_C.csv`.

> ⚠️ **이 PF는 왕복 거래비용 0.1%가 이미 반영된 값이다.** 비용이 없다면 PF는 `p/(1−p)` = A 2.195 / B 2.215 / C 1.941 이 된다. 실전 outcome에 비용을 적용하지 않으면 실전이 항상 더 좋아 보이므로, **FR-9는 반드시 동일 비용 모델로 계산해야 한다.**

> ⚠️ **생존편향 미보정.** 데이터 유니버스는 yfinance 다운로드 성공 종목 전량이며 티커 목록에 상장폐지 표기 종목이 섞여 있다(`backtest/data/fetch_kospi200.py`). 위 승률은 이 편향을 보정하지 않은 값이다.

### 데이터 품질 — 2026-08-31 전수 스캔 결과

yfinance 데이터셋(104종목)에 **기업행위 미반영 인공물**이 존재한다.

| 이상 유형 | 종목 | 일수 |
| --- | --- | --- |
| \|일간 등락\| > 25% (미반영 분할·무상증자 의심) | 43 | 114 |
| 거래량 0 (거래정지 구간에 가격 전일값 유지) | 97 | 1,676 |

확인 사례: **000070은 2025-11-24 3:2 무상증자(배율 1.4986)를 yfinance가 반영하지 않아 `−45.73%` 하루 낙폭이 인공물로 남아 있다.** 직전 5거래일은 거래량 0에 가격 고정. LS `t8410 sujung=Y`는 이 기업행위를 정상 조정하므로, **실전 데이터가 백테스트 데이터보다 오히려 깨끗하다.**

**실제 거래에 닿는 오염률 (진입~청산 구간에 인공물 포함):**

| 전략 | 총 거래 | 인공 갭 포함 | 거래량 0 포함 | 합계 |
| --- | --- | --- | --- | --- |
| A | 147 | 0 (0.0%) | 4 (2.7%) | **2.7%** |
| B | 541 | 3 (0.6%) | 19 (3.5%) | **4.1%** |
| C | 50 | 0 (0.0%) | 3 (6.0%) | **6.0%** |

**결론: 위 기대치는 무효화되지 않는다.** 위험한 유형(인공 갭)은 B에서 0.6%뿐이고, 거래량 0 구간은 가격이 전일값으로 유지되어 TP/SL을 발동시키지 않고 보유 기간만 늘린다. 다만 **기대치를 인용할 때 이 오염률(2.7~6.0%)을 함께 인지**해야 하며, FR-9의 대조에서 백테스트 쪽에 이 정도의 잡음이 섞여 있다고 보아야 한다.

> **수정주가 기준은 통일하지 않기로 결정했다(2026-08-31).** LS로 백테스트 데이터를 재수집(104종목 × 3콜 ≈ 6분)하면 기준 불일치와 위 인공물이 모두 해소되나 baseline 수치가 바뀐다. 현행 유지를 택했으므로 **FR-3의 골든 픽스처는 완전 일치가 아니라 Jaccard ≥ 0.9로 판정**한다.

## 실전 판정 룰 — 코드 확인 완료

단일 엔진 `run_backtest()` (`backtest/engine.py:82-169`)가 A/B/C 전 경로에서 사용된다.

| 항목 | 확정값 | 근거 |
| --- | --- | --- |
| 진입가 | 시그널 **당일 종가** (다음날 시가 아님) | `indicator_opt/run.py:44` |
| 판정 시작 | 진입 **다음 봉(e+1)**부터. 시그널 당일 봉은 판정 대상이 아니며 **최소 보유 1봉** | `engine.py:137` |
| TP | `entry × 1.03`, 조건 **`high >= tp`** (등호 포함), 체결가 = `tp` 정확값 | `engine.py:127`, `engine.py:77` |
| SL | `entry × 0.97`, 조건 **`low <= sl`** (등호 포함), 체결가 = `sl` 정확값(갭다운 미반영) | `indicator_opt/run.py:47`, `engine.py:75` |
| **동일봉 TP·SL 동시 도달** | **SL 우선 (보수적).** `low <= sl` 분기가 `high >= tp` 보다 먼저 평가된다 | `engine.py:75-78` |
| **거래비용** | **왕복 0.1%** (`cost_rate=0.0005 × 200`)를 수익률에서 차감 → TP 실현 **+2.9%**, SL **−3.1%** | `engine.py:31`, `engine.py:153` |
| 최대 보유(시간 청산) | **없음.** 데이터 끝까지 미청산이면 마지막 봉 종가로 강제 청산(`exit_reason="end"`)하며 트레이드에 포함된다. **A/B/C 모두 `end` 0건** | `engine.py:146-150` |
| 재진입 | **종목당 동시 1포지션.** 보유 중 발생한 시그널은 폐기(대기열 없음). 청산 봉과 **같은 날** 시그널도 스킵, 그 다음 봉부터 재진입 가능 | `engine.py:112-113` |
| 승률 산식 | `n_win / n_trades`. `n_win` = **비용 차감 후 `return_pct > 0`** 건수. 분모는 tp/sl/end 전부 포함 | `metrics/metrics.py:70-72` |
| PF 산식 | `sum(return_pct > 0) / abs(sum(return_pct < 0))`, **비용 차감 후 실제 수익률** 기준 | `metrics/metrics.py:80-86` |
| 수정주가 | yfinance `auto_adjust=True` — **분할 + 배당** 모두 소급 조정 | `data/fetch_kospi200.py:360-367` |

### 엔진의 숨은 필터 3건 (실전 재현 시 반드시 반영)

1. **ATR(14) 유효성 게이트** (`engine.py:116`) — 고정 TP/SL 모드인데도 `ATR(14)`가 finite & > 0 이어야 진입한다. 결과적으로 각 종목 **초기 약 14봉의 시그널이 무조건 폐기**된다. 고정 임계 모드에서 ATR은 사용되지 않으므로 **의도치 않은 잔재로 보이며, 의도 확인이 필요하다.** `[검증 필요]`
2. **마지막 봉 시그널 폐기** (`engine.py:114`) — `e >= len(df) - 1` 이면 진입하지 않는다.
3. **최소 보유 1봉** (`engine.py:137`) — 위 표의 "판정 시작" 항목과 동일. 시그널 당일에는 TP/SL이 발생할 수 없다.

## 실전(V1)에서 백테스트와 달라지는 점 — 명시적 편차

실전은 백테스트에 없는 규칙을 하나 도입한다. FR-9의 대조 시 이 편차를 인지해야 한다.

- **추적 컷오프 N = 30 거래일** (백테스트에는 시간 청산이 없음). 진입 후 30거래일 내 TP/SL 미도달 시 `TIMEOUT`으로 확정하고 30거래일째 종가 손익률을 기록한다.
- **측정된 왜곡 (analysis_cutoff.py, 미러 검증 6자리 일치):**

  | N | A TIMEOUT | A PF차 | B TIMEOUT | B PF차 | C TIMEOUT | C PF차 |
  | --- | --- | --- | --- | --- | --- | --- |
  | 5 | 9.52% | −0.1764 | 18.30% | **+0.2422** | 16.00% | −0.0135 |
  | 20 | 0% | ±0 | 0.74% | +0.0233 | 4.00% | +0.1853 |
  | **30** | **0%** | **±0** | **0.37%** | **+0.0125** | **0%** | **±0** |
  | 60 | 0% | ±0 | 0% | ±0 | 0% | ±0 |

  N=30 채택 근거: A·C는 왜곡 0, B만 2건(0.37%, PF +0.0125)으로 무시 가능. 96~99%가 15봉 내 청산되므로 N을 키워도 추적 대상 수(P)는 사실상 증가하지 않는다.
- 재현 스크립트: `_bmad-output/planning-artifacts/prds/prd-wave-double-2026-08-31/analysis_cutoff.py` (읽기 전용, `engine.py` 로직 미러링).

## 대조 시 유의

- 실전은 조건검색식 **후보 모집단 한정** 시그널이므로 104종목 전체 백테스트와 대상이 다르다(모집단 편향). 직접 비교가 아니라 **FR-10의 편향 지표와 함께** 해석한다.
- **수정주가 기준 정합 `[검증 필요]`**: 백테스트는 yfinance 배당조정가, 실전은 LS `t8410`/`t8451`의 `sujung` 플래그(국내 관행상 통상 분할만 조정)를 쓴다. 기준이 다르면 태깅이 재현되지 않으므로, 동일 종목·기간으로 실측 대조해 차이를 확인해야 한다. **FR-3의 골든 픽스처 회귀 대조의 선행 조건이다.**
