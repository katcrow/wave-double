---
title: '전략 계산 API 일반화 (AD-5 addendum 2 확장, F)'
type: 'feature'
created: '2026-09-08'
baseline_commit: 'd8f42b7815f8f6cd84c6898c36d8be205095c4b8'
baseline_revision: 'd8f42b7815f8f6cd84c6898c36d8be205095c4b8'
status: 'done'
review_loop_iteration: 0
followup_review_recommended: true
context:
  - 'C:/dev/wave-double/_bmad-output/implementation-artifacts/epic-7-context.md'
warnings: []
deferred: []
---

<intent-contract>

## Intent

**Problem:** `backtest.strategy_api.compute_abc`가 A/B/C/D/E 5개 시그널만 반환해, Story 7.1에서 코드화된 전략 F(`strategy_f.py`)를 태깅 stage가 아직 사용할 수 없다.

**Approach:** Story 6.4(D/E 확장)와 동일한 패턴으로 `compute_strategy_f`를 공유 계산 API에 통합해 `StrategyResult`가 A/B/C/D/E/F 6개 시그널 키를 모두 반환하도록 확장하고, 골든 픽스처·참조 계산·Jaccard 회귀를 F까지 확장한다.

## Boundaries & Constraints

**Always:** 함수명(`compute_abc`)과 기존 A/B/C/D/E 결과·오류·이력 부족 상태 의미를 그대로 보존한다. F는 D/E와 같은 유효 OHLC 연속 구간별 계산·말단봉 제거·ATR(14) 실행 가능성 필터를 적용받는다. F 계산은 `strategy_f.compute_strategy_f`와 `STRATEGY_F_PARAMS`를 그대로 재사용한다(로직 재작성 금지). 골든 회귀는 F도 Jaccard ≥ 0.9 및 전 종목 READY를 요구한다.

**Never:** `compute_abc` 함수명을 바꾸거나 A/B/C/D/E 산식을 재작성하지 않는다. `candidate_tags` DB 저장(Story 7.2, 완료), outcome 판정 파라미터화(Story 7.4), 태깅 stage 연동(Story 7.5), UI 라벨/배지(Story 7.6)는 이 스토리 범위가 아니다. `strategy_f.py`의 진입/청산 파라미터나 시그널 계산 로직을 변경하지 않는다.

## I/O & Edge-Case Matrix

| Scenario | Input / State | Expected Output / Behavior | Error Handling |
|----------|--------------|---------------------------|----------------|
| HAPPY_PATH | 120거래일 이상 유효 OHLCV | READY, A/B/C/D/E/F 6키 인덱스 정렬 bool Series, F 파라미터 메타데이터 포함 | 오류 없음 |
| F_COMPUTE_FAILURE | `compute_strategy_f`가 예외 발생 | ERROR, 빈 signals, `SIGNAL_COMPUTE_ERROR`(strategy="F") | 예외 메시지 포함 |
| F_CONTRACT_VIOLATION | F 계산기가 bool 아닌/인덱스 불일치 Series 반환 | ERROR, 빈 signals, strategy="F" | typed error, 조용한 보정 없음 |
| INVALID_OHLC_SEGMENT | 유효하지 않은 OHLC 행 포함 프레임 | F도 D/E처럼 유효 구간만 계산, invalid 구간은 신호 없음 | 구간 분리 불가 입력만 typed error |

</intent-contract>

## Code Map

- `backtest/strategy_api.py:11-44` -- import에 `from .indicator_opt.strategy_f import STRATEGY_F_PARAMS, compute_strategy_f` 추가, `_STRATEGY_KEYS`를 `("A","B","C","D","E","F")`로, `_STRATEGY_PARAMS`에 `"F": STRATEGY_F_PARAMS.as_dict()` 추가.
- `backtest/strategy_api.py:234-253` -- D/E를 계산하는 `for key, calculator, params in (("D", ...), ("E", ...))` 루프에 `("F", compute_strategy_f, STRATEGY_F_PARAMS)` 항목을 추가한다. `compute_strategy_f(segment, params)` 시그니처가 `compute_strategy_d`/`compute_strategy_e`와 동일해 별도 어댑터 불필요.
- `backtest/strategy_api.py:255-260` -- `_apply_atr_last_bar_filters(signals, frame, segments, ("D", "E"))` 호출의 키 튜플에 `"F"`를 추가해 F도 말단봉·ATR 필터를 받도록 한다.
- `backtest/indicator_opt/strategy_f.py:243-267` -- `compute_strategy_f(frame, params=STRATEGY_F_PARAMS) -> pd.Series`. D/E와 동일한 (segment, params) 시그니처, bool Series 반환. 그대로 재사용.
- `backtest/tests/test_strategy_api.py:1-353` -- D/E 패턴(양성 마스크, 실패 typed error, 계약 위반, invalid 구간, 말단봉 discard)을 F에도 동일하게 추가한다. `STRATEGY_D_PARAMS`/`STRATEGY_E_PARAMS` import 옆에 `STRATEGY_F_PARAMS`를 추가.
- `backtest/tests/test_golden_fixture.py:20-32,95-166` -- `_GOLDEN_KEYS`를 `("A","B","C","D","E","F")`로 확장하고, `_reference_signals`/`_new_signals`의 D/E 참조 계산 블록에 `compute_strategy_f` import 및 F 항목을 추가한다.
- `tests/fixtures/golden/generate_golden.py:38-54,106-181` -- `_GOLDEN_KEYS`를 6키로 확장하고 `compute_reference`/`compute_new`의 D/E 블록에 F를 추가(`from backtest.indicator_opt.strategy_f import compute_strategy_f`).
- `tests/fixtures/golden/golden_signals.json`, `tests/fixtures/golden/README.md` -- 재생성 도구 실행으로 F 시그널 키를 포함하도록 갱신하고, README의 스키마 설명(A/B/C/D/E → A-F)을 갱신한다.

## Tasks & Acceptance

**Execution:**
- `backtest/strategy_api.py` -- F 계산기·파라미터를 5전략 조립 로직에 통합(위 Code Map 3곳) -- 운영·백테스트 공유 진입점을 6전략 계약으로 확장한다.
- `backtest/tests/test_strategy_api.py` -- F 양성/실패/계약위반/invalid구간/말단봉 회귀와 `set(result.signals) == {"A".."F"}` 단언을 추가 -- API 확장의 호환성·실패 경계를 고정한다.
- `backtest/tests/test_golden_fixture.py`, `tests/fixtures/golden/generate_golden.py` -- F 독립 참조 계산과 Jaccard/READY 게이트를 6전략으로 확장 -- 실제 고정 데이터에서 F 계산기와 공유 API의 정합을 증명한다.
- `tests/fixtures/golden/golden_signals.json`, `tests/fixtures/golden/README.md` -- 재생성 도구로 F 시그널 집합을 반영하고 스키마 문서를 갱신 -- 픽스처가 F 키 누락을 허용하지 않게 한다.

**Acceptance Criteria:**
- Given Epic 6이 확장한 `compute_abc(frame) -> StrategyResult`(A/B/C/D/E 5키)가 있는 경우, when Story 7.1의 F 계산 함수(`strategy_f.py`)를 통합하면, then 함수명은 유지되고 `StrategyResult`가 A/B/C/D/E/F 6개 시그널 키를 모두 포함한다.
- Given 골든 픽스처 회귀 테스트(Story 2.4/6.4)가 있는 경우, when `golden_signals.json`에 F 키를 추가하면, then F도 A-E와 동일하게 Jaccard ≥ 0.9 기준으로 검증되며 참조 구현은 `strategy_f.py`다.
- Given 기존 A/B/C/D/E API 회귀 테스트와 전체 backtest 테스트가 있는 경우, when 전체 검증을 실행하면, then 기존 동작 회귀 없이 통과한다.

## Review Triage Log

### 2026-09-08 — Review pass (blind-hunter / edge-case-hunter / verification-gap / intent-alignment, 4-layer 병렬)
- intent_gap: 0
- bad_spec: 0
- patch: 6: (high 0, medium 0, low 6)
- defer: 0
- dismissed:
  - (blind-hunter) `baseline_commit`/`baseline_revision` 프론트매터 중복 필드 — 지적 자체는 사실이나 수정이 이 빌드가 구현 중인 스펙(`spec-7-3-...md`) 자체를 편집하는 것이라 워크플로 규칙상 기각한다.
  - (blind-hunter) Spec Change Log/Review Triage Log/Auto Run Result/Residual risks 섹션이 아직 비어 있다는 지적 — Review Triage Log는 이 리뷰 패스가, Auto Run Result는 이어지는 Finalize 단계가 채우도록 설계된 순서이며, 지적된 시점(리뷰 실행 전 diff 스냅샷)에서는 아직 비어 있는 것이 정상이다.
  - (blind-hunter) 전략 F 신호 밀도(32종목)가 D(3)·E(1) 대비 10~30배 많다는 지적 — 참조 계산과 신규 API 계산이 동일한 `compute_strategy_f`를 호출해 Jaccard 1.0000으로 완전 일치하므로, 신호 밀도 자체는 Story 7.1에서 이미 검토·baseline 이식된 `strategy_f.py`(표본 확대형 파라미터로 의도적으로 설계됨)의 특성이지 이번 API 통합 변경이 유발한 문제가 아니다.
  - (blind-hunter) Code Map의 `backtest/strategy_api.py` 라인 번호가 변경 후 실제 라인과 어긋난다는 지적 — 수정은 이 스펙 파일 자체 편집이라 워크플로 규칙상 기각한다.
  - (blind-hunter) F 전용 짧은 유효 구간(D/E는 충분하지만 F의 slope_window=30+accel_window=5/ma_db_window=16에는 부족한 구간) 엣지케이스 테스트 부재 — `_linreg_slope`(`window<2`면 2로 보정, `rolling(..., min_periods=window)`)와 `_double_bottom_signal`(`range(2, n)`으로 n<3이면 루프 미실행)을 직접 확인한 결과 짧은 구간에서도 예외 없이 전부 NaN/빈 배열 → `fillna(False)`로 안전하게 all-False로 축퇴하며, 이는 D/E의 rolling 기반 지표와 동일한 처리 패턴이다. 실제 결함 아님.
  - (blind-hunter) 말단봉 discard 필터가 F의 신호 구성(기울기 회귀+쌍바닥)에 의미적으로 적절한지 검증하는 전용 테스트가 없다는 지적 — D/E에도 동일하게 전략별 근거 테스트 없이 범용 실행가능성 필터로 재사용되는 기존 패턴이며, 구체적으로 어떤 시나리오에서 부적절한지 제시되지 않아 근거 불충분.
  - (blind-hunter) 이 diff에 스프린트 상태 동기화 반영이 없다는 지적 — 사용자 지시 순서(개발→검수/보완→e2e→**스프린트 동기화**→커밋)상 스프린트 동기화는 이 리뷰 이후 별도 단계로 예정되어 있어 이 시점에 diff에 없는 것이 정상이다.
  - (blind-hunter) 6키로 확장된 `StrategyResult`가 기존 5키만 순회하는 소비자를 깨뜨리지 않는다는 명시적 회귀 테스트가 없다는 지적 — 고정 키 하위집합만 순회하는 소비자(`apps/batch/tags_stage.py`의 자체 5키 상수 등)는 dict에 새 키가 추가돼도 깨지지 않으며, 이는 Story 6.4의 5키 확장 때도 동일하게 적용된 전례이자 전체 backtest 스위트 152건 통과로 실증된다. 구체적 깨짐 시나리오 미제시.
  - (intent-alignment) 리뷰 반복 카운터·상태가 아직 "in-review"/0이고 e2e·스프린트 동기화·git 커밋이 diff에 반영되지 않았다는 관찰 — 사용자 지시 순서상 이 리뷰 패스 자체가 "검수" 단계이고 e2e 필요성 판단·동기화·커밋은 이 패스 완료 이후 순서이므로 예상된 상태다(결함 아님). 이 스토리는 backtest Python API·고정 fixture만 다루고 UI/DB/런타임 표면이 없어 e2e는 불필요하다고 판단한다.
- addressed_findings:
  - `[low]` `[patch]` (edge-case-hunter) `_STRATEGY_PARAMS: dict[str, dict[str, int | float]]` 타입 애노테이션이 F의 `tp_first`(bool)·`max_holding_bars`(int | None) 필드를 반영하지 못함 — 애노테이션을 `dict[str, dict[str, int | float | bool | None]]`로 확장했다.
  - `[low]` `[patch]` (blind-hunter) `test_d_or_e_failure_is_typed_and_names_strategy`가 D/E/F로 파라미터화됐는데 이름이 "d_or_e"로 낡음 — `test_calculator_failure_is_typed_and_names_strategy`로 개명했다.
  - `[low]` `[patch]` (blind-hunter) `test_d_and_e_positive_masks_are_returned`가 D/E/F 모두 단언하는데 이름이 "d_and_e"로 낡음 — `test_d_e_f_positive_masks_are_returned`로 개명했다.
  - `[low]` `[patch]` (blind-hunter) `test_invalid_relationship_row_is_excluded_without_connecting_segments`의 `d_e_segments`/`fake_d_e` 변수명이 D/E/F 3개를 담게 됐는데도 D/E만 암시 — `d_e_f_segments`/`fake_segment_calculator`로 개명했다.
  - `[low]` `[patch]` (blind-hunter) `test_golden_fixture.py` 모듈 docstring이 "A/B/C/D/E"만 언급하고 F 미반영 — docstring을 "A/B/C/D/E/F"로 갱신했다.
  - `[low]` `[patch]` (blind-hunter) `tests/fixtures/golden/README.md` 최상단 제목이 "(Story 6.4)"로 남아 이번 F 확장(Story 7.3)을 반영하지 않음 — 제목을 "(Story 6.4/7.3)"으로 갱신했다.

## Verification

**Commands:**
- `uv run --with pandas --with numpy --with pyarrow --with pytest pytest backtest/tests/test_strategy_api.py backtest/tests/test_golden_fixture.py -q` -- expected: API 및 6전략 골든 회귀 통과.
- `uv run --with pandas --with numpy --with pyarrow --with pytest pytest backtest -q` -- expected: 전체 backtest 회귀 통과.
- `uv run --with pandas --with numpy --with pyarrow python tests/fixtures/golden/generate_golden.py` -- expected: 6전략 픽스처 sanity와 Jaccard 게이트 통과 후 결정적 파일 생성.
- `git diff --check` -- expected: 공백 오류 없음.

**Manual checks (if no CLI):**
- 없음(전부 CLI로 검증 가능; UI/DB 표면 없음).

## Auto Run Result

Summary: `backtest.strategy_api.compute_abc`가 A/B/C/D/E 5개 시그널만 반환하던 것을, Story 6.4(D/E 확장)와 동일한 패턴으로 Story 7.1의 `compute_strategy_f`/`STRATEGY_F_PARAMS`를 통합해 A/B/C/D/E/F 6개 시그널을 모두 반환하도록 확장했다. F는 D/E와 동일하게 유효 OHLC 연속 구간별 계산·말단봉 discard·ATR(14) 실행 가능성 필터를 적용받는다. 골든 픽스처와 참조 계산·Jaccard/READY 게이트도 F를 포함한 6전략으로 확장했다.

Files changed:
- `backtest/strategy_api.py` — F import, `_STRATEGY_KEYS`/`_STRATEGY_PARAMS` 확장, D/E 계산 루프와 ATR/말단봉 필터 키 튜플에 F 추가, 파라미터 메타데이터 타입 애노테이션 확장.
- `backtest/tests/test_strategy_api.py` — F 양성 마스크·계산 실패 typed error·계약 위반·invalid 구간·말단봉 discard 회귀와 `set(result.signals) == {"A".."F"}` 단언 추가, 리뷰 패치로 낡은 D/E 전용 테스트명·변수명을 D/E/F 반영 이름으로 개명.
- `backtest/tests/test_golden_fixture.py` — `_GOLDEN_KEYS`를 6키로 확장, F 독립 참조 계산(`compute_strategy_f`) 추가, docstring을 F 포함으로 갱신.
- `tests/fixtures/golden/generate_golden.py` — `_GOLDEN_KEYS` 6키 확장 및 F 참조 계산 추가.
- `tests/fixtures/golden/golden_signals.json` — 재생성 도구로 F 시그널 32종목 추가(A-E 기존 값은 byte-identical 보존).
- `tests/fixtures/golden/README.md` — 스키마 설명을 A-F로 갱신하고 헤딩을 "Story 6.4/7.3"으로 갱신.
- `_bmad-output/implementation-artifacts/spec-7-3-전략-계산-api-일반화-ad-5-확장-f.md` — 신규 스펙 문서(본 파일).

Review findings breakdown (2026-09-08, 4계층 정식 리뷰 패스): patch 6건(low 6) 모두 수정 — `_STRATEGY_PARAMS` 타입 애노테이션이 F의 bool/Optional 필드를 반영하지 못한 문제, D/E 전용으로 남아있던 테스트명 2건·변수명 1건, `test_golden_fixture.py` docstring과 `README.md` 헤딩의 F 미반영 2건. dismissed 9건은 위 Review Triage Log에 각각 근거와 함께 기록(프론트매터/Code Map 지적은 이 스펙 자체 편집이라 워크플로 규칙상 기각, 미완성 섹션은 이 리뷰·Finalize 단계가 순서대로 채우는 것이 정상, F 신호 밀도는 Story 7.1에서 이미 검토된 전략 특성이자 Jaccard 1.0000으로 참조와 완전 일치, 짧은 구간 엣지케이스는 `_linreg_slope`/`_double_bottom_signal` 코드 확인 결과 이미 안전하게 all-False로 축퇴, 말단봉 필터 전용 근거 테스트 부재는 D/E도 동일한 기존 패턴, 스프린트 동기화는 사용자 지시 순서상 이 리뷰 이후 단계, 6키 확장이 고정 5키 소비자를 깨지 않음은 Story 6.4 전례와 전체 스위트 통과로 실증).

Follow-up review recommendation: true (patched low 6; score 6 = 1×6 ≥ 5).

Verification: `pytest backtest/tests/test_strategy_api.py backtest/tests/test_golden_fixture.py -q` — 40 passed. `pytest backtest -q`(전체) — 152 passed. `python tests/fixtures/golden/generate_golden.py` — A/B/C/D/E/F sanity Jaccard 전부 1.0000, universe 98종목, F 32종목/D 3종목/E 1종목 매칭, 결정적 재생성 후 diff 변화 없음(golden_day.json/ohlcv_raw.json.gz는 universe·OHLCV 불변이라 무변경). `git diff --check` — 공백 오류 없음(LF/CRLF 경고만 존재, 실제 diff 이슈 아님). e2e/브라우저 테스트는 이 스토리 범위(순수 backtest Python API·고정 fixture, UI/DB/런타임 표면 없음)에 해당하지 않아 적용하지 않았다.

Residual risks: F의 outcome 판정 파라미터화(Story 7.4)가 완료되기 전까지 `candidate_outcome_strategy_check`/`guard_outcome_strategy_snapshot()`은 여전히 A-E만 허용해 F 전략의 outcome 판정은 동작하지 않는다(Story 7.4 범위로 이미 추적). 태깅 stage(`apps/batch/tags_stage.py`)는 아직 자체 5키 상수를 사용해 F 태그를 저장하지 않는다(Story 7.5 범위로 이미 추적, 이번 6키 확장으로 인한 회귀 아님). UI 라벨/배지·OOS 워크포워드 검증은 각각 7.6/7.7 후속 스토리 범위다.

