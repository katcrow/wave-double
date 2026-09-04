---
title: '전략 D(돌파3%기법) 계산 로직 코드화 및 백테스트 baseline 이식'
type: 'feature'
created: '2026-09-04'
status: 'done'
baseline_revision: 'a371b708e68e03311eaca65874a6ca76d6b65795'
baseline_commit: 'a371b708e68e03311eaca65874a6ca76d6b65795'
review_loop_iteration: 0
followup_review_recommended: true
context:
  - 'C:/dev/wave-double/_bmad-output/implementation-artifacts/epic-6-context.md'
warnings: []
deferred:
  - summary: >-
      백테스트 엔진은 OHLCV의 시가를 사용하지 않고 목표가·손절가에 정확 체결한 것으로 처리한다.
    evidence: |-
      기존 backtest/engine.py의 _exit_price_on_bar 계약이 open_ 인자를 받지만 가격 판정에 사용하지 않는다. 이번 스토리는 기존 엔진을 재사용했으며, 갭 체결 정책 변경은 별도 엔진 정책 스토리로 남긴다.
    location: >-
      backtest/engine.py:69-83
    severity: low
---

<intent-contract>

## Intent

**Problem:** 전략 D의 후보 A 파라미터가 문서에만 있어 운영 태깅에서 재사용할 수 없고, 백테스트 기대치가 실제 코드에서 재현 가능한 기준으로 남아 있지 않다.

**Approach:** 기존 `backtest`의 OHLCV 프레임→불리언 마스크 관례와 단일 엔진을 재사용하는 전략 D 계산 모듈을 추가하고, TP 3%·SL 5%·최대보유 20거래일을 포함한 재현 실행 경로와 baseline 근거를 고정한다.

## Boundaries & Constraints

**Always:** 후보 A의 N=20, W=3, VMR=0.95, SMA 240, Wilder RSI(10)의 6일 SMA 평활, RSI 42 상향돌파·최저 30, TP 3%·SL 5%·최대보유 20일을 사용한다. 고점 돌파·매집 확인·장기 이평 하단·RSI 상향돌파는 모두 AND이며, 마스크는 입력 인덱스를 보존하고 bool이어야 한다. 룩어헤드 없이 현재 봉 이전 데이터만 참조하는 조건은 테스트한다.

**Never:** 후보 B/C나 전략 A/B/C 계산식 수정, 신규 조건검색식·후보 원천 추가, 운영 태깅/API/DB/UI 연결, OOS 검증을 이 스토리에서 수행하지 않는다. 문서의 83.1%·77건을 코드 근거 없이 주장하지 않으며, 차이가 나면 사용 데이터·판정 규칙과 함께 원인을 기록한다.

## I/O & Edge-Case Matrix

| Scenario | Input / State | Expected Output / Behavior | Error Handling |
|----------|--------------|---------------------------|----------------|
| HAPPY_PATH | 유효한 정렬 OHLCV 프레임 | 동일 인덱스의 bool 시그널 마스크 | 오류 없음 |
| INSUFFICIENT_HISTORY | 240일 미만 프레임 | 계산은 수행하되 준비되지 않은 행은 False/NaN 제거 | 예외를 삼키지 않고 입력 계약 오류는 명시 |
| ZERO_VOLUME_WINDOW | 최근 거래량 최대가 0 | 매집 조건은 False | 0으로 나누지 않음 |
| LOOKAHEAD_GUARD | 오늘 고가/거래량을 미래 행에 바꾼 프레임 | 변경한 미래 값이 과거 신호를 바꾸지 않음 | 회귀 테스트 실패 |

</intent-contract>

## Code Map

- `docs/돌파3%기법_추가.md:12-48` -- 전략 D의 공통 진입식, 후보 A 파라미터, 청산 규칙과 문서 기대치.
- `backtest/indicator_opt/_signals.py:237-248, 471-476` -- 기존 Wilder RSI와 OBV 계산 관례. 신규 전략은 기존 범용 신호 레지스트리에 억지로 분해하지 않고 전략 전용 조합으로 유지한다.
- `backtest/indicator_opt/combine_strategies.py:31-61` -- 기존 전략 조합의 프레임→전략별 bool Series 반환 패턴. A/B/C 구현은 읽기 전용으로 재사용 경계를 확인한다.
- `backtest/indicator_opt/run.py:31-60` -- bool 마스크를 종가 진입 신호로 바꾸는 방식과 고정 TP/SL 인자 전달 관례.
- `backtest/engine.py:69-169` -- 동일 봉 SL 우선, 다음 봉부터 판정, 동시 1포지션, 거래비용 산식의 단일 원천. 기존 동작을 보존하면서 전략 D 최대보유를 지원할 위치.
- `backtest/data/loader.py:25-48` -- 기준 parquet 유니버스 로더. baseline 재현 실행은 이 로더를 사용한다.
- `_bmad-output/specs/spec-wave-double/backtest-baseline.md:1-27,54-93` -- 기존 baseline의 file:line 근거 형식·비용·편차 기록 규칙. 전략 D 절을 여기에 추가한다.
- `backtest/tests/test_strategy_api.py` 및 `backtest/tests/test_engine.py` -- 기존 API/엔진 회귀망. 신규 전략 계산과 선택적 최대보유 동작은 별도 테스트로 격리한다.

## Tasks & Acceptance

**Execution:**
- [x] `backtest/indicator_opt/strategy_d.py` -- 후보 A 파라미터 상수, 룩어헤드 없는 4조건 AND 마스크, 고정 TP/SL·최대보유를 사용하는 재현 실행 진입점 추가 -- 운영/API 스토리가 재사용할 계산 경계를 만든다.
- [x] `backtest/engine.py` -- 기존 기본값을 바꾸지 않는 선택적 최대보유 지원이 필요할 때만 최소 변경 -- 전략 D 청산 규칙을 엔진 중복 없이 실행한다.
- [x] `backtest/tests/test_strategy_d.py` -- 조건별 경계, 0 거래량, 인덱스·bool, 룩어헤드와 청산 회귀 테스트 추가 -- 문서 계약을 자동 검증한다.
- [x] `_bmad-output/specs/spec-wave-double/backtest-baseline.md` -- 전략 D 파라미터·실제 실행 명령·실행 결과와 file:line 근거 추가 -- 기대치와 차이를 추적 가능하게 한다.

**Acceptance Criteria:**
- Given 후보 A 파라미터의 유효 OHLCV 프레임, when 전략 D 계산 함수를 호출하면, then 고점 돌파 AND 매집 확인 AND Close<SMA240 AND 평활 RSI의 전일<42·당일≥42·당일≥30을 모두 만족한 행만 True인 동일 인덱스 bool Series를 반환한다.
- Given 조건 계산에 필요한 이력이 부족하거나 거래량 창이 0인 경우, when 계산하면, then 초기 행은 무신호이며 0 나눗셈·미래 데이터 참조 없이 안정적으로 처리된다.
- Given 전략 D 시그널을 기준 데이터로 백테스트하면, when 재현 명령을 실행하면, then TP3%·SL5%·최대보유20일·왕복비용0.1% 및 SL 우선 규칙이 코드로 적용되고 거래수·승률·PF·평균수익이 baseline에 기록된다.
- Given 기존 A/B/C 테스트와 백테스트 전체 회귀망, when 신규 테스트와 기존 명령을 실행하면, then 기존 동작은 변하지 않고 전략 D 테스트가 통과한다.

## Spec Change Log

- 2026-09-04: 후보 A 전략 D 전용 계산·재현 실행 경로와 엔진 선택적 최대보유를 구현하고, 현재 parquet 기준 baseline(19건/78.95%/PF 2.1324)을 기록했다.

## Review Triage Log

### 2026-09-04 — Review pass
- intent_gap: 0
- bad_spec: 0
- patch: 14: (high 0, medium 8, low 6)
- defer: 1: (high 0, medium 0, low 1)
- dismissed:
  - 기존 Wilder RSI의 초기값·평균손실 0 처리 — 전략 D 기본 파라미터는 SMA240 워밍업 이후에만 신호가 가능하므로 이 기존 구현의 초기 구간이 D 결과에 영향을 주지 않는다.
  - raw n_signals와 실행 거래 수를 하나로 합쳐야 한다는 주장 — 러너는 원시 시그널과 엔진 통과 거래를 의도적으로 별도 집계하며, baseline CSV에 두 값을 모두 기록한다.
  - caller가 커스텀 파라미터를 전달할 수 있다는 주장 — 기본값은 CANDIDATE_A로 고정되고, 명시적 파라미터 인자는 통제 비교와 테스트를 위한 기존 확장 경계다.
  - unified diff의 절대 경로 헤더 — 이는 리뷰용 임시 diff 생성기의 표현이며 저장소 파일 내용이나 실제 패치 경로가 아니다.
- addressed_findings:
  - `[medium]` `[patch]` RSI 조건 독립 검증 누락 — RSI가 거짓이면 나머지 조건이 참이어도 신호가 되지 않는 테스트를 추가했다.
  - `[medium]` `[patch]` 0 거래량 신호 허용 — 현재 거래량 0을 매집 조건에서 제외하고 양수 과거 창·현재 0 경계를 테스트했다.
  - `[low]` `[patch]` 입력 OHLCV 계약 검증 부족 — 중복 컬럼·양수 가격·비음수 거래량·High/Low 관계를 검증한다.
  - `[medium]` `[patch]` 전략 파라미터 유효성 검증 부족 — 윈도우·RSI·TP/SL·비용·최대보유의 타입·범위를 명시적으로 검증한다.
  - `[medium]` `[patch]` max_holding_bars 조기 반환 전 검증 누락 — 빈 신호와 짧은 프레임에서도 잘못된 설정을 거부한다.
  - `[medium]` `[patch]` 최대보유일의 TP/SL 우선 경계 미검증 — 최대보유일 SL 우선, 조기 TP/SL, 데이터 조기 종료를 테스트한다.
  - `[low]` `[patch]` 기본 max_holding_bars 동작 검증 부족 — 제한 없음과 제한이 데이터 종료 시 동일하게 end가 되는 경계를 추가했다.
  - `[medium]` `[patch]` 러너의 비용·최대보유 전달 검증 부족 — spy로 TradeParams 전달값을 검증한다.
  - `[low]` `[patch]` 결과 CSV의 파라미터 가시성 부족 — param_* 컬럼으로 평탄화했다.
  - `[medium]` `[patch]` baseline 관측창 미고정 — 2020-08-03~2026-08-27 기본 경계를 코드에 추가했다.
  - `[low]` `[patch]` aggregate 결과 감사성 부족 — 데이터 fingerprint와 거래 상세 CSV를 추가했다.
  - `[medium]` `[patch]` 문서 모호성에 대한 controlled variant 증거 부족 — High/Close, 거래량 창, RSI 평활 변형 결과를 baseline에 기록했다.
  - `[low]` `[patch]` 월간 빈도 누락 — 73개월 기준 0.2603건을 결과와 문서에 기록했다.
  - `[low]` `[patch]` D 전용 데이터 품질 영향 누락 — 거래 구간의 거래량 0 및 25% 초과 갭 포함 거래가 각각 0건임을 기록했다.

## Auto Run Result

Summary: 전략 D 후보 A의 네 가지 진입 조건, 고정 TP3%·SL5%·최대보유20일, 선택적 엔진 시간청산, 고정 관측창 baseline 실행을 구현했다. 현재 기준 parquet에서는 19건·15승·4패·승률 78.95%·PF 2.1324가 재현되며, 원문 기대치 83.1%·77건은 보존된 과거 스냅샷/판정 코드가 없어 통제 비교와 함께 차이로 기록했다.

Files changed:
- `backtest/indicator_opt/strategy_d.py` — 전략 D 계산·신호 변환·고정창 baseline runner·fingerprint·상세 거래 출력.
- `backtest/engine.py` — 기본 동작을 유지하는 선택적 max_holding_bars 및 입력 검증.
- `backtest/tests/test_strategy_d.py` — 조건·입력·룩어헤드·엔진 경계·runner wiring 회귀 테스트.
- `_bmad-output/specs/spec-wave-double/backtest-baseline.md` — 파라미터·관측창·결과·통제 비교·품질 근거.
- `backtest/results/indicator_opt/strategy_d_baseline.csv` — aggregate와 param_*·fingerprint 결과.
- `backtest/results/indicator_opt/strategy_d_baseline_trades.csv` — 19건 거래 상세.
- `_bmad-output/implementation-artifacts/epic-6-context.md` — Epic 6 개발 컨텍스트.
- `_bmad-output/implementation-artifacts/sprint-status.yaml` — Epic 6/Story 6-1 in-progress 동기화(최종화에서 done 전환).

Review findings breakdown: patch 14건(중간 8, 낮음 6)을 모두 수정했고, 기존 엔진의 갭 체결 정책 1건은 별도 스토리로 defer했다. dismissed 항목은 위 triage log에 각각 사유를 기록했다.

Follow-up review recommendation: true (patched high 0, medium 8, low 6; score 30 = 3×8 + 6).

Verification: 지정 전략·엔진 테스트 30 passed, 전체 `pytest backtest -q` 79 passed, `python -m backtest.indicator_opt.strategy_d` 실행 완료, fingerprint `d9c28ab5d01026b3ca9422a69bab301bd520af90547b4aac481056f42ef33e33` 확인, `git diff --check` 통과, `compileall` 통과.

Residual risks: 원문 83.1%·77건을 현재 저장소 데이터로 재현하지 못했고 원본 스냅샷이 없어 단일 원인을 확정할 수 없다. OOS와 운영/API/DB/UI 연결은 후속 스토리 범위이며, 기존 엔진의 갭 체결 정책은 defer 상태다.

## Design Notes

문서의 “고가(또는 종가)”는 후보명이 고점 돌파이고 핵심 조건이 신고가 돌파이므로 `High > 직전 20봉 High 최고값`을 canonical 해석으로 고정한다. RSI smooth는 Wilder RSI를 계산한 뒤 6일 단순평균을 적용한다. 이 해석과 문서 수치의 차이는 baseline에 관측값과 원인을 함께 남긴다.

## Verification

**Commands:**
- `uv run --with pandas --with numpy --with pyarrow --with pytest pytest backtest/tests/test_strategy_d.py backtest/tests/test_engine.py -q` -- expected: 신규 전략·엔진 경계 테스트 통과.
- `uv run --with pandas --with numpy --with pyarrow --with pytest pytest backtest -q` -- expected: 기존 backtest 회귀 없음.
- `uv run --with pandas --with numpy --with pyarrow python -m backtest.indicator_opt.strategy_d` -- expected: 기준 parquet에 대한 전략 D 결과 출력 및 baseline 수치 생성.
- `git diff --check` -- expected: 공백 오류 없음.

실행 결과: 지정 전략 D 테스트·엔진 회귀 18건 통과, `pytest backtest -q` 전체 54건 통과, 기준 parquet 실행 완료.
