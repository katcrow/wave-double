---
title: '전략 E(익절2%_고정SL5%기법) 계산 로직 코드화 및 백테스트 baseline 이식'
type: 'feature'
created: '2026-09-04'
status: 'done'
baseline_revision: '2d201de0e8cf20f3e703f5cec31feb9fb14aa1e2'
baseline_commit: '2d201de0e8cf20f3e703f5cec31feb9fb14aa1e2'
review_loop_iteration: 0
followup_review_recommended: true
context:
  - 'C:/dev/wave-double/_bmad-output/implementation-artifacts/epic-6-context.md'
warnings: []
deferred:
  - summary: >-
      기존 백테스트 엔진의 고정 TP/SL 경로가 ATR 유효성 게이트를 계속 적용한다.
    evidence: |-
      `run_backtest()`는 고정 TP/SL 신호에도 진입 시점 ATR(14)가 유효하고 양수인지 먼저 확인한다. 전략 E의 고정 출구 자체에는 ATR이 필요하지 않지만 이 동작은 기존 엔진 계약이며 이번 스토리에서 변경하지 않았다.
    location: >-
      backtest/engine.py:116-119
    severity: medium
  - summary: >-
      기존 엔진은 갭 발생 시에도 고정 TP/SL 가격으로 체결한 것으로 계산한다.
    evidence: |-
      `_exit_price_on_bar()`는 `open_`을 인자로 받지만 TP/SL 도달 시 시가를 체결가로 사용하지 않는다. 이번 스토리는 기존 엔진을 재사용했으며 갭 체결 정책 변경은 별도 엔진 정책 작업으로 남긴다.
    location: >-
      backtest/engine.py:70-84
    severity: low
  - summary: >-
      기존 성과 집계는 여러 종목 거래를 단일 순서로 합산해 포트폴리오 동시보유 의미를 모델링하지 않는다.
    evidence: |-
      `summarize()`는 전달된 거래 순서로 복리 누적과 drawdown을 계산한다. 전략 E runner는 결과 결정성을 위해 거래를 정렬했지만 포지션 크기·동시보유 모델은 별도 성과 모델 범위다.
    location: >-
      backtest/metrics/metrics.py:38-86
    severity: low
---

<intent-contract>

## Intent

**Problem:** 전략 E의 SMA·OBV·ADX 조합과 고정 TP/SL 파라미터가 문서에만 있어 실제 백테스트 코드에서 재현 가능한 기준이 없다.

**Approach:** 기존 OHLCV→불리언 마스크 관례와 단일 백테스트 엔진을 재사용하는 전략 E 전용 모듈을 추가하고, 고정 관측창의 실행 결과·거래 상세·데이터 fingerprint를 baseline으로 기록한다.

## Boundaries & Constraints

**Always:** SMA20이 SMA60을 전일 이하에서 당일 초과로 상향 돌파하고, OBV가 20일 SMA를 상향 돌파하며, Wilder ADX(14)가 당일 20 이상인 세 조건을 AND로 계산한다. 진입은 시그널 당일 종가, TP는 +2%, 고정 SL은 -5%, 최대보유는 30거래 데이터 봉, 왕복 비용은 엔진 계약인 편도 0.0005×200=0.1%를 따른다. 입력 인덱스와 bool 마스크를 보존하고, 준비되지 않은 초기 행은 False로 처리하며 미래 행을 참조하지 않는다. baseline에는 문서 기대치와 현재 데이터의 실제 관측치를 분리하고 차이를 기록한다.

**Never:** 전략 A/B/C/D의 계산식이나 기존 엔진 기본 동작을 변경하지 않는다. `strategy_api.compute_abc` 일반화, DB/운영 태깅/API/UI 연결, OOS 검증, 신규 후보 원천은 이 스토리 범위가 아니다. 기존 `sig_adx()`의 추가 +DI/-DI 교차 조건을 문서의 ADX≥20 조건에 몰래 포함하지 않는다.

## I/O & Edge-Case Matrix

| Scenario | Input / State | Expected Output / Behavior | Error Handling |
|----------|--------------|---------------------------|----------------|
| HAPPY_PATH | 유효한 오름차순 OHLCV 프레임 | 동일 인덱스의 bool 전략 E 마스크 및 고정 TP/SL 신호 | 오류 없음 |
| INSUFFICIENT_HISTORY | SMA60·OBV20·ADX14 준비 전 프레임 | 해당 행은 무신호이며 계산 가능한 이후 행만 평가 | 입력 계약 위반은 명시적 오류 |
| LOOKAHEAD_GUARD | 미래 봉의 값만 변경한 프레임 | 변경한 미래 값이 이전 행의 신호를 바꾸지 않음 | 회귀 테스트 실패 |
| EXIT_BOUNDARY | 다음 봉에서 TP/SL 동시 도달 또는 30번째 봉 미도달 | SL 우선, 아니면 30번째 봉 종가 max_hold 청산 | 엔진 결과 사유로 확인 |

</intent-contract>

## Code Map

- `docs/익절2%_고정SL5%기법_추가.md:16-48` -- 전략 E의 세 진입 조건, TP/SL·최대보유·비용·기대치 원문.
- `backtest/indicator_opt/strategy_d.py:29-110` -- 전략 전용 파라미터 dataclass, 입력/파라미터 검증, baseline 관측창 패턴을 재사용하되 D 조건은 변경하지 않는다.
- `backtest/indicator_opt/strategy_d.py:160-285` -- bool 마스크·고정 TP/SL 신호·엔진 runner·결과 fingerprint/CSV 생성 구조의 재사용 기준.
- `backtest/indicator_opt/_signals.py:36-38,65-69,107-124,471-476` -- cross-up, SMA GC, OBV 계산 참고. 기존 `sig_adx`는 +DI 교차를 포함하므로 E의 단순 ADX 조건에는 직접 사용하지 않는다.
- `backtest/indicators/__init__.py` -- SMA/OBV/ADX의 저수준 지표 구현 및 NaN/워밍업 관례.
- `backtest/engine.py:30-169` -- `TradeParams`, 다음 봉부터의 TP/SL 판정, SL 우선, 선택적 `max_holding_bars`, 왕복 비용 산식. 기본값은 유지한다.
- `backtest/data/loader.py:25-48` -- 기준 parquet 유니버스 `load_all()`와 종목별 프레임 로딩.
- `backtest/metrics/metrics.py:70-86` -- 비용 차감 후 승률·PF 집계.
- `_bmad-output/specs/spec-wave-double/backtest-baseline.md:17-68` -- 전략 D baseline의 file:line 근거·관측창·통제 비교·편차 기록 형식.
- `backtest/tests/test_strategy_d.py`, `backtest/tests/test_engine.py` -- 기존 회귀망과 전략 전용 경계 테스트 구조. E 테스트는 별도 파일로 격리한다.

## Tasks & Acceptance

**Execution:**
- [x] `backtest/indicator_opt/strategy_e.py` -- 전략 E 파라미터 상수, 입력 검증, SMA20/60 GC·OBV20 MA cross·ADX14≥20 AND 마스크, 종가 고정 TP2%/SL5% 신호, 30봉 runner와 CLI를 추가한다 -- 운영/API 후속 스토리가 재사용할 계산 경계를 만든다.
- [x] `backtest/tests/test_strategy_e.py` -- 각 조건 독립 경계, 워밍업, bool/인덱스, 룩어헤드, 파라미터·입력 오류, TP/SL·max_hold·runner wiring 회귀를 추가한다 -- 문서 계약과 엔진 연결을 자동 검증한다.
- [x] `_bmad-output/specs/spec-wave-double/backtest-baseline.md` -- 전략 E 파라미터·실제 실행 명령·문서 기대치·현재 parquet 관측 결과와 file:line 근거를 추가한다 -- 수치의 출처와 편차를 추적 가능하게 한다.
- [x] `backtest/results/indicator_opt/strategy_e_baseline.csv` 및 `backtest/results/indicator_opt/strategy_e_baseline_trades.csv` -- 고정 관측창 실행 결과와 거래 상세를 생성한다 -- baseline을 재현·감사 가능하게 한다.

**Acceptance Criteria:**
- Given 유효 OHLCV 프레임, when 전략 E 계산 함수를 호출하면, then SMA20/60 골든크로스 AND OBV20일 MA 상향돌파 AND ADX14≥20만 만족한 동일 인덱스 bool 마스크를 반환한다.
- Given 준비 이력이 부족하거나 미래 봉 값이 변경된 경우, when 계산하면, then 준비 전 행은 False이고 미래 데이터 변경은 이전 신호에 영향을 주지 않는다.
- Given 전략 E 신호를 기준 parquet와 고정 관측창으로 실행하면, when 재현 명령을 수행하면, then TP2%·고정 SL5%·최대보유30봉·왕복비용0.1%·SL 우선이 적용된 거래 수·승률·PF·평균수익과 fingerprint가 baseline 및 상세 CSV에 기록된다.
- Given 원문 기대치(승률 78.2%·PF 1.34·78건)가 현재 데이터와 다를 수 있는 경우, when baseline을 작성하면, then 기대치와 실제 관측치를 구분하고 데이터/판정 규칙 차이를 근거와 함께 기록하며 코드 근거 없는 일치를 주장하지 않는다.
- Given 기존 backtest 회귀 테스트와 신규 E 테스트를 실행하면, then 기존 동작을 변경하지 않고 모든 테스트가 통과한다.

## Spec Change Log

- 2026-09-04: 전략 E 전용 계산·고정 TP/SL·30봉 runner와 Wilder ADX 저수준 계산을 구현하고, 현재 parquet 기준 baseline(19건/73.68%/PF 1.0431)을 기록했다.

## Review Triage Log

### 2026-09-04 — Review pass
- intent_gap: 0
- bad_spec: 0
- patch: 7: (high 0, medium 4, low 3)
- defer: 3: (high 0, medium 1, low 2)
- dismissed:
  - 문서의 “강한 하락 추세 배제” 설명과 ADX-only 계산의 차이 — 이 스토리의 intent-contract가 `ADX(14) ≥ 20`만 canonical 조건으로 명시하고 +DI/-DI 교차를 금지하므로 ADX-only 구현이 의도에 부합한다.
  - 고정 TP/SL에서 갭 시 시가 체결을 반영해야 한다는 주장 — 해당 동작은 스토리 변경 전에 존재한 엔진 정책이고 intent-contract가 기존 엔진 재사용을 요구하므로 이월 항목으로 기록했다.
  - 여러 종목의 복리·drawdown이 동시보유 포트폴리오를 의미하지 않는다는 주장 — 기존 `summarize()` 계약의 범위이며 이번 스토리는 전략 E 계산·baseline 이식만 다루므로 이월 항목으로 기록했다.
  - 관측창 종료 직전 거래를 censor해야 한다는 주장 — 기존 엔진의 데이터 끝 `end` 청산 계약과 스토리의 baseline 재현 요구에 따라 현재 관측값을 포함하는 것이 명시된 동작이다.
- addressed_findings:
  - `[medium]` `[patch]` ADX Wilder seed·window validation·trusted vector test를 추가하고 ADX threshold 경계를 고정했다.
  - `[medium]` `[patch]` 전체 이력으로 지표를 계산하고 관측창 내 신호만 엔진에 전달해 warmup/경계 누락을 보정했다.
  - `[medium]` `[patch]` invalid OHLCV 행을 runner 계산에서 분리해 invalid 구간이 연속 봉으로 연결되지 않게 했다.
  - `[medium]` `[patch]` custom params·timezone·SMA/OBV 동률 경계의 실행 경로를 테스트했다.
  - `[low]` `[patch]` ticker 길이와 정렬된 입력/거래 순서로 fingerprint와 집계 결과를 결정적으로 만들었다.
  - `[low]` `[patch]` invalid 행도 fingerprint에 포함해 데이터 변경 감사를 가능하게 했다.
  - `[low]` `[patch]` zero-trade 상세 CSV의 고정 헤더와 CLI 파일 산출을 검증했다.

## Design Notes

문서의 ADX 조건은 `ADX(14) ≥ 20`으로만 명시되어 있으므로 Wilder ADX 값의 threshold 판정만 canonical로 삼는다. 이는 기존 `sig_adx()`의 +DI/-DI 교차까지 요구하는 구현과 의도적으로 다르다. “30일”은 기존 엔진의 `max_holding_bars=30`인 거래 데이터 봉으로 고정한다.

## Verification

**Commands:**
- `uv run --with pandas --with numpy --with pyarrow --with pytest pytest backtest/tests/test_strategy_e.py backtest/tests/test_engine.py -q` -- expected: 전략 E와 엔진 경계 테스트 통과.
- `uv run --with pandas --with numpy --with pyarrow --with pytest pytest backtest -q` -- expected: 전체 backtest 회귀 통과.
- `uv run --with pandas --with numpy --with pyarrow python -m backtest.indicator_opt.strategy_e --start 2020-08-03 --end 2026-08-27` -- expected: 전략 E baseline 요약/거래 CSV 생성 및 출력.
- `git diff --check` -- expected: 공백 오류 없음.

## Auto Run Result

Summary: 전략 E의 SMA20/60 골든크로스·OBV20일 이동평균 상향돌파·Wilder ADX14≥20 AND 계산, 고정 TP2%·SL5%·최대보유30거래봉, 관측창 baseline runner와 CLI를 구현하고 검수 보완까지 완료했다. 전체 이력 워밍업, invalid 구간 분리, timezone/파라미터 검증, 결정적 fingerprint·거래 정렬, zero-trade CSV 헤더를 추가했다.

Files changed:
- `backtest/indicator_opt/strategy_e.py` — 전략 E 계산·신호·baseline runner·CLI.
- `backtest/indicators/__init__.py` — 검증 가능한 표준 Wilder ADX.
- `backtest/tests/test_strategy_e.py` — 조건·지표·경계·runner·CLI 회귀 테스트.
- `_bmad-output/specs/spec-wave-double/backtest-baseline.md` — 전략 E file:line 근거와 관측 baseline.
- `backtest/results/indicator_opt/strategy_e_baseline.csv` — 집계 baseline(19건/14승/5패/73.68%/PF 1.0431).
- `backtest/results/indicator_opt/strategy_e_baseline_trades.csv` — 19건 거래 상세.
- `_bmad-output/implementation-artifacts/sprint-status.yaml` — Story 6-2 `done` 동기화.

Review findings breakdown: patch 7건(중간 4, 낮음 3)을 자동 보완했고, 기존 엔진 ATR 게이트·갭 체결 정책·다종목 포트폴리오 집계 의미 3건(중간 1, 낮음 2)을 이월했다. 4건은 스토리 계약 또는 기존 엔진 계약으로 인해 별도 수정 없이 기각했다.

Follow-up review recommendation: true (patched high 0, medium 4, low 3; score 15 = 3×4 + 3).

Verification: 지정 전략·엔진 테스트 47 passed, 전체 `pytest backtest -q` 121 passed, 기준 관측창 CLI 실행 성공, `compileall` 통과, `git diff --check` 통과. 최신 baseline fingerprint는 `b2e027e0f8155d3fbabfd310f52c31e82afd1079722ed579e98207ca112e73a3`이다.

Residual risks: 원문 기대치(78건·승률 78.2%·PF 1.34)는 현재 parquet와 canonical Wilder ADX 계산에서 재현되지 않으며 원본 스냅샷이 없어 단일 원인을 확정할 수 없다. OOS 검증·운영/API/DB/UI 연결은 후속 스토리 범위다. 이월한 엔진 ATR 게이트·갭 체결·다종목 포트폴리오 집계 의미는 별도 작업이 필요하다.
