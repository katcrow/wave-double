---
title: '전략 F(각도 가속·이평선 쌍바닥 기법) 계산 로직 코드화 및 백테스트 baseline 이식'
type: 'feature'
created: '2026-09-07'
status: 'done'
baseline_revision: 'b14e3a07c3db2e85d31bc23c309c0b1c2e2e037b'
review_loop_iteration: 0
followup_review_recommended: true
context:
  - 'C:/dev/wave-double/_bmad-output/implementation-artifacts/epic-7-context.md'
warnings: []
deferred:
  - summary: >-
      Story 7.1은 계산 로직 코드화·baseline 이식까지만이며, `candidate_tags` 확장(7.2),
      전략 계산 API 일반화(7.3), outcome 판정 F 파라미터화(7.4), 운영 태깅 stage 반영(7.5),
      UI 라벨·배지·라우트(7.6), OOS 워크포워드 검증(7.7)은 이 스토리 범위 밖 후속 스토리다.
    evidence: |-
      epic-7-context.md의 Cross-Story Dependencies: "Story 7.1 ... is a hard prerequisite
      for Stories 7.2-7.6." Story 7.7(OOS)도 F의 "OOS unverified" 리스크가 미검증 상태로
      남아 있음을 명시.
    location: >-
      _bmad-output/implementation-artifacts/epic-7-context.md
    severity: low
---

<intent-contract>

## Intent

**Problem:** 전략 F(각도 가속·이평선 쌍바닥)의 계산 로직이 `docs/각도가속_이평쌍바닥기법_추가.md`에만 문서로 존재해 운영 태깅·API에서 재사용할 수 없고, 문서의 "표본 확대형" 기대치(승률 73.1%/PF 1.92/182건)가 코드로 재현 가능한 기준으로 남아 있지 않다.

**Approach:** 기존 전략 D/E와 동일한 OHLCV 프레임→불리언 마스크 관례와 단일 백테스트 엔진을 재사용하는 전략 F 계산 모듈을 추가하고, 로그가격 최소제곱 기울기 가속(`sig_angle_accel_ls` 재사용)과 이평선(MA16) 쌍바닥(`_double_bottom_signal` 재사용) 두 조건을 AND 결합해, TP 3%/SL 4%/tp_first=True를 포함한 재현 실행 경로와 baseline 근거를 고정한다.

## Boundaries & Constraints

**Always:** "표본 확대형" 파라미터(slope_window=30, accel_window=5, min_slope_delta=0.004, ma_db_window=16, TP 3%, SL 4%, tp_first=True, max_holding_bars=None, cost_rate=0.0005)를 사용한다. 각도 가속과 이평선 쌍바닥 조건은 모두 AND이며, 마스크는 입력 인덱스를 보존하고 bool이어야 한다. 룩어헤드 없이 현재 봉 이전 데이터만 참조하는 조건은 테스트한다. 신규 범용 신호 로직(`_linreg_slope`, `sig_angle_accel_ls`)은 `_signals.py`에 두어 전략 F 계산이 이를 직접 재사용하고, 로직을 중복 구현하지 않는다.

**Never:** 전략 A/B/C/D/E 계산식 수정, 신규 조건검색식·후보 원천 추가, `candidate_tags`/전략 계산 API/outcome 판정/운영 태깅/UI 연결(7.2-7.6 범위), OOS 워크포워드 검증(7.7 범위)을 이 스토리에서 수행하지 않는다. 문서의 73.1%·182건을 코드 근거 없이 주장하지 않으며, 파라미터 차이(0.0045 vs 0.004)가 나면 원인을 기록한다.

## I/O & Edge-Case Matrix

| Scenario | Input / State | Expected Output / Behavior | Error Handling |
|----------|--------------|---------------------------|----------------|
| HAPPY_PATH | 유효한 정렬 OHLCV 프레임, 가속+쌍바닥 동시 충족 봉 존재 | 해당 봉만 True인 동일 인덱스 bool 마스크 | 오류 없음 |
| NO_COINCIDENCE | 순수 상승 추세(가속·쌍바닥 미충족) | 전 구간 False | 예외 없음 |
| INSUFFICIENT_HISTORY | slope_window(30)/ma_db_window(16) 미만 프레임 | 워밍업 구간은 무신호 | 0 나눗셈·예외 없음 |
| SAME_BAR_TP_SL | 같은 봉에서 TP·SL 동시 도달 | tp_first=True이므로 TP(이익) 우선 청산 | 회귀 테스트로 고정 |
| TIMEZONE_MISMATCH | start/end 경계와 프레임 인덱스 timezone 불일치 | ValueError로 명시적 거부 | 조용한 무시 없음 |

</intent-contract>

## Code Map

- `docs/각도가속_이평쌍바닥기법_추가.md:12-48` -- 전략 F의 공통 진입식("표본 확대형" 파라미터)과 청산 규칙, 문서 기대치.
- `backtest/indicator_opt/_signals.py:97-113` -- `_linreg_slope`(rolling 최소제곱 기울기), 신규 범용 헬퍼.
- `backtest/indicator_opt/_signals.py:130-143` -- `sig_angle_accel_ls`(로그가격 기울기 가속), 전략 F가 직접 호출해 로직 중복을 피한다.
- `backtest/indicator_opt/_signals.py:332-372` -- 기존 `_double_bottom_signal`(범용 쌍바닥 탐지기), 읽기 전용 재사용.
- `backtest/indicator_opt/strategy_f.py` -- 전략 F 전용 계산·신호 변환·고정창 baseline runner(신규 파일).
- `backtest/engine.py:33-49,69-95,153-169` -- `TradeParams.tp_first`/`_exit_price_on_bar` 우선순위 분기(Story 6-2에서 이미 추가), 전략 F가 그대로 재사용.
- `backtest/data/loader.py:25-48` -- 기준 parquet 유니버스 로더. baseline 재현 실행이 사용.
- `_bmad-output/specs/spec-wave-double/backtest-baseline.md:192-218` -- 전략 F 절(파라미터·재현 실행 결과·해석·결정).
- `backtest/tests/test_strategy_f.py`, `backtest/tests/test_engine.py` -- 신규/기존 회귀망.

## Tasks & Acceptance

**Execution:**
- [x] `backtest/indicator_opt/strategy_f.py` -- `StrategyFParams`, 룩어헤드 없는 가속+쌍바닥 AND 마스크(`sig_angle_accel_ls` 재사용), 고정 TP/SL 신호 변환, 고정창 재현 baseline runner 추가 -- 7.2-7.6이 재사용할 계산 경계를 만든다.
- [x] `backtest/tests/test_strategy_f.py` -- 조건별 경계, 입력 검증, 룩어헤드, 청산 우선순위, runner wiring 회귀 테스트, 그리고 가속·쌍바닥이 실제로 동시 충족되는 fixture로 happy-path를 검증 -- 리뷰에서 지적된 "항상 무신호인 fixture로 인한 공허한 테스트"를 해소한다.
- [x] `_bmad-output/specs/spec-wave-double/backtest-baseline.md` -- 전략 F 파라미터·실행 명령·재현 결과·해석·결정 추가, "후보 A" 오기재를 "표본 확대형"으로 정정 -- 기대치와 코드 재현치 차이를 추적 가능하게 하고 문서 간 일관성을 맞춘다.
- [x] `backtest/indicator_opt/strategy_f.py` -- `compute_strategy_f`가 인라인 재구현 대신 `sig_angle_accel_ls`를 직접 호출하도록 리팩터 -- 가속 로직 이중 구현(사실상 죽은 코드 `sig_angle_accel_ls`)을 제거해 향후 수정이 한 곳에만 반영되게 한다.
- [x] `backtest/indicator_opt/strategy_f.py` -- MA(16) 워밍업 구간을 `0.0`으로 채워 쌍바닥 탐지기에 넣지 않고, 실제로 계산된 값만 잘라 넣은 뒤 워밍업 구간은 항상 무신호로 고정 -- 세그먼트 재시작 시 패딩-실값 경계가 가짜 첫 저점으로 오인되어 허위 시그널이 발생하던 정식 리뷰 확인 결함을 제거한다.

**Acceptance Criteria:**
- Given "표본 확대형" 파라미터의 유효 OHLCV 프레임, when 전략 F 계산 함수를 호출하면, then 로그가격 30봉 최소제곱 기울기가 5봉 전 대비 0.004 이상 가속 AND 이평선(MA16) 쌍바닥 넥라인 상향 돌파를 모두 만족한 행만 True인 동일 인덱스 bool Series를 반환한다.
- Given 가속·쌍바닥 조건이 실제로 동시에 성립하는 fixture, when 전략 F 계산 함수를 호출하면, then 예상 위치에서 정확히 시그널이 발생하고(공허하지 않은 happy-path 검증), 순수 상승 추세처럼 조건이 성립하지 않는 프레임에서는 전 구간 무신호다.
- Given 전략 F 시그널을 기준 데이터로 백테스트하면, when 재현 명령을 실행하면, then TP3%/SL4%/tp_first=True/왕복비용 0.1%가 코드로 적용되고 거래수/승률/PF/평균수익이 baseline에 기록되며, 재실행 시 fingerprint와 수치가 동일하게 재현된다.
- Given 기존 A/B/C/D/E 테스트와 백테스트 전체 회귀망, when 신규 테스트와 기존 명령을 실행하면, then 기존 동작은 변하지 않고 전략 F 테스트가 통과한다.

## Spec Change Log

_없음. draft 루프백 없이 최초 작성에서 바로 ready-for-dev 기준을 충족._

## Review Triage Log

### 2026-09-07 — Review pass
- intent_gap: 0
- bad_spec: 0
- patch: 4: (high 1, medium 2, low 1)
- defer: 0
- dismissed:
  - `min_slope_delta` 문서값(0.0045)과 코드값(0.004) 불일치를 재지적하는 항목 — 이미 `backtest-baseline.md`와 `sprint-change-proposal-2026-09-07.md`에 의도적 차이로 기록되어 있어 재작업 대상이 아니다.
  - `ma_db.fillna(0.0)` 워밍업 구간의 "유령 저점" 가능성 — 첫 유효 MA 값을 유지하는 대안과 비교한 차등 테스트에서 동일한 시그널 위치가 나와 실제 결함으로 확인되지 않았다. **(정정: 아래 2026-09-07 정식 리뷰 패스에서 이 차등 테스트가 실제로는 결함을 재현하지 못하는 시나리오였음이 드러나 재검증했고, 실제 결함으로 확인되어 patch로 수정했다. 이 항목의 기각은 철회한다.)**

### 2026-09-07 — Review pass (blind-hunter / edge-case-hunter / verification-gap / intent-alignment, 4-layer 병렬)
- intent_gap: 0
- bad_spec: 0
- patch: 4: (high 1, medium 0, low 3)
- defer: 0
- dismissed:
  - `min_slope_delta` 문서값(0.0045)과 이에 따른 문서-baseline 수치 차이(73.1%/182건 vs 코드 재현치) — 이미 기록된 의도적 파라미터 차이이며, 이번 패스에서 버그 수정 경위까지 baseline 문서에 추가로 설명해 추적성을 보강했다(신규 결함 아님).
  - `_validate_params`의 `max_holding = int(max_holding)`가 "계산만 하고 사용되지 않는 죽은 코드"라는 주장 — 바로 다음 줄의 `1 <= max_holding <= _MAX_WINDOW` 범위 검사에서 이 재할당된 값을 실제로 사용하므로 주장이 성립하지 않는다.
  - `_validate_frame`/`_valid_ohlcv_rows`의 OHLC 일관성 규칙 이중 구현 — `backtest/indicator_opt/strategy_d.py:113,144`와 `strategy_e.py:120,142`에 동일한 이중 검증 패턴이 이미 존재하는 기존 저장소 관례이며, 이 스토리가 새로 만든 문제가 아니다.
  - `sig_angle_accel`/`sig_angle_accel_ls`(및 신규 `_REGISTRY` 그리드 항목)에 대한 전용 단위 테스트 부재 — `_signals.py`의 기존 35개 `sig_*` 헬퍼 전부가 전용 단위 테스트 없이 전략 모듈을 통한 간접 검증(또는 grid-search 도구를 통한 검증)만 받는 기존 관례이며, `sig_angle_accel_ls`는 `strategy_f.py`의 테스트 스위트로 간접 검증된다.
  - `StrategyFParams.tp_first=True`가 엔진 기본값(False)과 다른데 근거가 없다는 주장 — `docs/각도가속_이평쌍바닥기법_추가.md`의 공통 구조에 `tp_first: True`가 명시적으로 규정되어 있어 재량적 선택이 아니다.
  - 전략 F에 대한 OOS(워크포워드) 검증 부재 — epic-7-context.md Cross-Story Dependencies에 따라 Story 7.7의 범위이며, 이 스펙의 frontmatter `deferred`에 이미 추적되어 있다.
  - 음수 Close가 `sig_angle_accel_ls`의 `log()`에 전달되면 조용히 NaN이 된다는 주장 — 이 스토리의 유일한 호출 경로(`compute_strategy_f`)는 `sig_angle_accel_ls` 호출 전에 `_validate_frame`이 이미 0 이하 가격을 예외로 거부하므로, 이 경로로는 도달 불가능하다.
  - `_linreg_slope`가 `window<2`를 조용히 2로 보정한다는 주장 — `compute_strategy_f`를 통한 호출은 `_validate_params`가 `slope_window > accel_window >= 1`을 강제해 항상 `slope_window >= 2`이며, `_REGISTRY` grid 항목도 window ∈ {10,20,30}만 사용해 이 경로로는 도달 불가능하다.
  - `_linreg_slope`의 `rolling().apply(raw=True)` 및 신규 grid(216+36 combo) 성능 미검증 — 이 스토리의 인수인계 범위(계산 로직·baseline 재현)와 무관한 기존 grid-search 도구 성능 문제이며, 이번 변경의 소비자(baseline 재현·향후 태깅)에 대한 구체적 소비 경로가 확인되지 않았다.
- addressed_findings:
  - `[high]` `[patch]` (verification-gap·edge-case-hunter, 동일 근본원인) SMA(MA16) 워밍업 구간(첫 15봉)을 `0.0`으로 채운 뒤 `_double_bottom_signal(threshold=inf)`에 통째로 넣어, 패딩-실값 경계가 가짜 "첫 저점"으로 오인될 수 있음을 직접 재현으로 확인 — 특히 `run_strategy_f_backtest`가 종목별로 `_valid_segments`를 통해 세그먼트마다 MA를 새로 계산하므로(현재 기준 데이터에 244개 무효 OHLCV 행 존재), 실제 baseline에 허위 시그널이 섞여 있었다. `compute_strategy_f`를 실제로 계산된 MA 값만 잘라 `_double_bottom_signal`에 넣고 워밍업 구간은 항상 `False`로 고정하도록 수정했다(임의 프레임 길이에 견고하도록 `np.isnan` 기반 첫 유효 인덱스 사용). 수정 전 fixture(`_signal_frame`)도 이 버그에 의존해 통과하고 있었음을 발견해(2저점이 1저점보다 낮아 "higher low" 조건을 실제로는 만족하지 못했음) 진짜 오름차순 쌍바닥 형태로 재설계했다. 실데이터 baseline 재현 결과가 시그널 199→173건, 거래 194→168건, 승률 70.10%→70.83%, PF 1.6585→1.7178로 바뀌었고(여전히 채택 기준 충족), `backtest-baseline.md`와 `strategy_f_baseline*.csv`, `epic-7-context.md`를 모두 갱신했다.
  - `[low]` `[patch]` `_validate_params`의 `max_holding_bars` 범위 오류 메시지가 `f`-string이 아니어서 `_MAX_WINDOW`가 리터럴 문자열로 노출되는 버그 — `_validate_positive_integer`와 동일하게 `f"...{_MAX_WINDOW}..."`로 수정했다.
  - `[low]` `[patch]` `sig_angle_accel_ls`가 모듈 최상단에 이미 있는 `import numpy as np`를 두고 함수 내부에서 `from numpy import log as _np_log`를 중복 임포트 — `np.log`를 직접 사용하도록 정리했다.
  - `[low]` `[patch]` (edge-case-hunter claim) 스펙의 "룩어헤드 없이... 테스트한다"는 명시적 약속에도 불구하고 실제 룩어헤드 회귀 테스트가 존재하지 않음 — `test_future_values_do_not_change_past_signal`을 추가해 시그널 발생 이후 구간의 값을 변형해도 그 이전 마스크가 변하지 않음을 검증한다.
- addressed_findings:
  - `[high]` `[patch]` `test_strategy_f.py`의 기존 fixture(`_strategy_f_frame`)가 어떤 파라미터로도 가속·쌍바닥 조건을 동시 충족하지 않아 happy-path 테스트가 공허하게 통과 — 실제로 두 조건이 동시 성립하는 `_signal_frame` fixture를 추가하고, `SIGNAL_POSITION`을 실제 발화 위치(174)로 갱신했으며, 무신호 회귀(`test_strategy_f_plain_uptrend_never_fires`)와 발화 회귀(`test_strategy_f_fires_when_accel_and_double_bottom_coincide`)를 모두 추가했다. 기존 exit-parameter 테스트도 이 fixture로 교체해 빈 리스트에 대한 공허한 루프 단언을 제거했다.
  - `[medium]` `[patch]` `backtest-baseline.md`가 전략 F를 "후보 A"로 오기재(원문 doc은 "표본 확대형" 단일 후보만 정의) — PRD/sprint-change-proposal과 일치하도록 "표본 확대형"으로 정정했다.
  - `[medium]` `[patch]` `compute_strategy_f`가 `_signals.py`에 이미 추가된 `sig_angle_accel_ls`와 동일한 가속 로직을 인라인으로 중복 구현 — `compute_strategy_f`가 `sig_angle_accel_ls`를 직접 호출하도록 리팩터해 로직 중복을 제거했다(재실행으로 fingerprint·baseline 수치 불변 확인).
  - `[low]` `[patch]` I/O 매트릭스의 `INSUFFICIENT_HISTORY` 행을 커버하는 테스트 누락(구현 단계 Matrix Test Audit에서 발견) — `test_insufficient_history_is_false_and_preserves_index`를 추가해 slope_window 미만 프레임에서 무신호·인덱스 보존·예외 없음을 검증한다.

## Design Notes

MA 쌍바닥은 `threshold=float("inf")`로 호출해 "국소 저점 수준" 제약을 사실상 비활성화한다 — 문서의 쌍바닥 조건은 절대적 과매도 수준이 아니라 형태(저점-넥라인-higher low-돌파) 자체이므로, 기존 범용 `_double_bottom_signal`의 threshold 파라미터를 그대로 재사용하되 무제한으로 열어 형태 매칭만 적용한다. 이는 전략 E의 스토캐스틱 쌍바닥과 달리 F가 오실레이터 과매도 구간이 아닌 이평선 자체의 형태를 보기 때문이다.

## Verification

**Commands:**
- `uv run --with pandas --with numpy --with pyarrow --with pytest pytest backtest/tests/test_strategy_f.py backtest/tests/test_engine.py -q` -- expected: 신규 전략 테스트 전부 통과.
- `uv run --with pandas --with numpy --with pyarrow --with pytest pytest backtest -q` -- expected: 기존 backtest 전체 회귀 없음.
- `PYTHONIOENCODING=utf-8 uv run --with pandas --with numpy --with pyarrow python -m backtest.indicator_opt.strategy_f --start 2020-08-03 --end 2026-08-27` -- expected: 기준 parquet에 대한 전략 F 결과가 커밋된 baseline CSV(승률 70.83%/PF 1.7178/168건)와 fingerprint까지 동일하게 재현.
- `git add --refresh -- . && git diff --check` -- expected: 공백 오류 없음.

**e2e/수동 테스트 적용 여부:** 이 스토리의 변경은 `backtest/` 순수 계산·백테스트 로직에 한정되며 `apps/web`, API 라우트, DB 마이그레이션, UI를 전혀 건드리지 않는다(7.2-7.6에서 다룰 범위). 따라서 브라우저/API e2e 테스트는 적용 대상이 아니며, `pytest backtest -q` 전체 회귀와 CLI 재현 실행이 이 스토리의 end-to-end 검증에 해당한다.

실행 결과: `test_strategy_f.py` 17건 통과(리팩터·fixture·매트릭스·룩어헤드·워밍업버그 수정 후), `pytest backtest -q` 전체 149건 통과, 전략 F CLI 재실행 결과가 수정된 `strategy_f_baseline.csv`(승률 70.83%/PF 1.7178/168건)와 fingerprint(`b2e027e0f8155d3fbabfd310f52c31e82afd1079722ed579e98207ca112e73a3`)까지 완전히 일치, `git diff --check` 통과.

## Auto Run Result

Summary: 전략 F(각도 가속·이평선 쌍바닥, "표본 확대형" 파라미터)의 계산 로직을 `strategy_f.py`로 코드화하고 기준 parquet에 대한 재현 baseline을 고정했다. 세션 시작 시점에 이미 대부분 구현되어 있던 코드를 인수받아, 자체 self-review와 4계층(blind-hunter/edge-case-hunter/verification-gap/intent-alignment) 정식 리뷰를 거쳐 실질적 결함(워밍업 패딩으로 인한 허위 쌍바닥 시그널)을 발견·수정했고, 그 결과 baseline 수치가 변경되었다(승률 70.83%/PF 1.7178/168건, 여전히 채택 기준 충족).

Files changed:
- `backtest/indicator_opt/strategy_f.py` — 전략 F 계산·신호 변환·baseline runner(신규); `sig_angle_accel_ls` 재사용 리팩터; MA 워밍업 구간을 항상 무신호로 고정하는 버그 수정; 오류 메시지 f-string 수정.
- `backtest/indicator_opt/_signals.py` — `_linreg_slope`/`sig_angle_accel`/`sig_angle_accel_ls`(신규); `sig_angle_accel_ls`의 중복 `numpy.log` 임포트 정리.
- `backtest/engine.py` — `TradeParams.tp_first`(같은 봉 TP·SL 동시 도달 시 우선순위 선택), `_exit_price_on_bar` 분기(Story 6-2에서 이미 도입, 전략 F가 재사용).
- `backtest/tests/test_strategy_f.py` — 조건별 경계·입력 검증·룩어헤드·청산 우선순위·runner wiring 테스트(신규 17건); 가속·쌍바닥이 실제로 동시 충족되는 `_signal_frame` fixture(진짜 오름차순 쌍바닥으로 재설계) 및 무신호/룩어헤드/워밍업 회귀 추가.
- `backtest/tests/test_engine.py` — `tp_first` 같은 봉 우선순위 회귀(Story 6-2에서 이미 추가).
- `_bmad-output/specs/spec-wave-double/backtest-baseline.md` — 전략 F 절(파라미터·재현 명령·결과·버그 수정 경위·해석·결정), "후보 A" 오기재를 "표본 확대형"으로 정정.
- `backtest/results/indicator_opt/strategy_f_baseline.csv`, `strategy_f_baseline_trades.csv` — 수정된 로직으로 재생성된 baseline(168건 거래 상세 포함).
- `_bmad-output/implementation-artifacts/epic-7-context.md` — Epic 7 개발 컨텍스트(신규, 정정된 baseline 수치 반영).
- `docs/각도가속_이평쌍바닥기법_추가.md` — 전략 F 원문 소스 문서(신규, 세션 시작 시점부터 존재).

Review findings breakdown (2026-09-07, 4계층 정식 리뷰 패스): patch 4건(high 1, medium 0, low 3) 모두 수정 — 워밍업 패딩 허위 쌍바닥(high, 실데이터 baseline 수치 변경 유발), `max_holding_bars` 오류 메시지 f-string 누락(low), `sig_angle_accel_ls` 중복 임포트(low), 룩어헤드 회귀 테스트 부재(low). dismissed 8건은 위 Review Triage Log에 각각 근거와 함께 기록(문서화된 기존 파라미터 차이, 반박된 죽은 코드 주장, D/E와 동일한 기존 검증 관례, 기존 미검증 `sig_*` 헬퍼 관례, 문서로 규정된 tp_first, 7.7 범위인 OOS 검증, 이 스토리 경로로는 도달 불가능한 두 개의 edge-case 주장). 이전 self-review 패스(patch 4건: high1/medium2/low1)의 dismissed 항목 중 "워밍업 유령 저점" 기각은 이번 패스에서 철회·정정했다.

Follow-up review recommendation: true (이번 패스 patched high 1건 포함).

Verification: `test_strategy_f.py` 17건, `pytest backtest -q` 전체 149건 통과. CLI 재현 결과가 `strategy_f_baseline.csv`(승률 70.83%/PF 1.7178/168건, fingerprint `b2e027e0f8155d3fbabfd310f52c31e82afd1079722ed579e98207ca112e73a3`)와 완전히 일치. `git diff --check` 통과. e2e/브라우저 테스트는 이 스토리 범위(순수 backtest 계산 로직, UI/API/DB 미접촉)에 해당하지 않아 적용하지 않았다.

Residual risks: OOS(워크포워드) 검증은 Story 7.7 범위로 남아 있어 "OOS unverified" 리스크가 유효하다(epic-7-context.md에 Medium으로 추적). `candidate_tags`/전략 계산 API/outcome 판정/운영 태깅/UI 연결은 7.2-7.6 후속 스토리 범위다. 문서("표본 확대형" 73.1%/182건)와 코드 재현치(70.83%/168건)의 잔여 차이는 `min_slope_delta` 0.0045 vs 0.004의 의도적 파라미터 차이에서 기인하며 baseline 문서에 근거와 함께 기록되어 있다.
