---
title: '전략 계산 API 일반화'
type: 'feature'
created: '2026-09-04'
baseline_revision: '99ee3b46c49abbb433d004f44143bdcc12dbd386'
baseline_commit: '99ee3b46c49abbb433d004f44143bdcc12dbd386'
status: 'done'
review_loop_iteration: 0
followup_review_recommended: true
context:
  - 'C:/dev/wave-double/_bmad-output/implementation-artifacts/epic-6-context.md'
warnings: []
deferred: []
---

<intent-contract>

## Intent

**Problem:** `backtest.strategy_api.compute_abc`가 A/B/C 시그널만 반환해 운영 태깅이 Story 6.1/6.2의 D/E 계산을 사용할 수 없다.

**Approach:** 하위호환 함수명과 공통 `StrategyResult` 계약을 유지하면서 D/E 계산기를 같은 진입점에 통합하고, 골든 픽스처·참조 계산·Jaccard 회귀를 다섯 전략으로 확장한다.

## Boundaries & Constraints

**Always:** A/B/C 결과와 기존 오류·이력 부족 상태 의미를 보존한다. 반환 시그널은 동일 프레임 인덱스의 bool Series이며 키는 정확히 A/B/C/D/E다. D/E 계산은 기존 전용 계산 함수와 동일한 파라미터·지표를 사용한다. 입력 오류는 typed error로 드러내고, 골든 회귀는 전략별 Jaccard ≥ 0.9 및 모든 대상 READY를 요구한다. 운영과 백테스트가 같은 API를 계속 사용한다.

**Never:** `compute_abc` 이름을 변경하거나 기존 A/B/C 산식을 재작성하지 않는다. 후보 태깅 stage의 D/E 저장, DB migration, outcome 판정, UI 라우트는 구현하지 않는다(후속 스토리). 비정상 OHLC 행을 정상 봉으로 연결해 D/E 지표가 오염되게 하지 않는다.

## I/O & Edge-Case Matrix

| Scenario | Input / State | Expected Output / Behavior | Error Handling |
|----------|--------------|---------------------------|----------------|
| HAPPY_PATH | 120거래일 이상 유효 OHLCV | READY, A/B/C/D/E 키의 인덱스 정렬 bool Series, 전략별 파라미터 메타데이터 반환 | 오류 없음 |
| INSUFFICIENT_HISTORY | 120일 미만 프레임 | 기존과 같은 INELIGIBLE 상태, 빈 signals | 오류 없음 |
| NON_FINITE_INPUT | OHLCV에 NaN/Inf | ERROR, 빈 signals, `SIGNAL_COMPUTE_ERROR` | 오류에 원인과 실패 전략을 기록 |
| INVALID_OHLC_SEGMENT | 유효하지 않은 OHLC 행이 포함된 프레임 | 유효 구간만 계산하고 invalid 행은 신호 없음; 유효한 다른 종목 처리를 막지 않음 | 구간 분리가 불가능한 입력만 typed error |

</intent-contract>

## Code Map

- `backtest/strategy_api.py:1-285` -- `StrategyResult`, typed error, `compute_abc`, A/B/C의 전체 프레임 계산과 D/E의 유효 구간 조립·공통 실행 가능성 필터. 함수명·기존 상태 계약을 보존하고 D/E를 통합한다.
- `backtest/indicator_opt/strategy_d.py:29-219` -- `StrategyDParams`, `compute_strategy_d`, 입력 검증과 D 시그널 계산. 전용 계산기와 파라미터를 재사용한다.
- `backtest/indicator_opt/strategy_e.py:33-274` -- `StrategyEParams`, `compute_strategy_e`, 입력 검증과 E 시그널 계산. 전용 계산기와 파라미터를 재사용한다.
- `backtest/indicator_opt/combine_strategies.py:31-61` -- 기존 A/B/C 참조 구현의 `build_signals` 반환 순서와 strict 오류 동작.
- `backtest/tests/test_strategy_api.py:1-320` -- API 상태·입력 오류·A/B/C 마스크·5전략 실행 가능성·D/E 양성/실패·invalid 구간 회귀.
- `backtest/tests/test_golden_fixture.py:20-280` -- 골든 키 목록, 독립 참조 계산, 신규 API 집합, 전략별 Jaccard·READY·목록 스키마 gate.
- `tests/fixtures/golden/generate_golden.py:80-270` -- 고정 OHLCV에서 5전략 참조·신규 결과를 계산하고 빈 전략·Jaccard를 검증하는 픽스처 생성 경로.
- `tests/fixtures/golden/golden_signals.json` 및 `tests/fixtures/golden/README.md` -- 다섯 전략 키와 확정 스키마·재생성 설명을 보관한다.
- `apps/batch/tags_stage.py:28-80` -- 현재 A/B/C만 소비하는 후속 stage 경계. 이번 스토리에서는 동작을 변경하지 않고 API의 확장 결과가 후속 6.6에서 소비될 수 있게 한다.

## Tasks & Acceptance

**Execution:**
- [x] `backtest/strategy_api.py` -- D/E 계산기와 전략별 파라미터 메타데이터를 통합하고 invalid OHLC 구간을 안전하게 다루는 공통 조립 로직을 추가한다 -- 운영·백테스트의 단일 진입점을 다섯 전략 계약으로 확장한다.
- [x] `backtest/tests/test_strategy_api.py` -- 다섯 키·bool mask·전략 파라미터·기존 상태/오류·invalid 구간 회귀를 검증한다 -- API 호환성과 실패 경계를 고정한다.
- [x] `backtest/tests/test_golden_fixture.py`, `tests/fixtures/golden/generate_golden.py` -- D/E 참조 계산, 픽스처 키 완비, 전략별 Jaccard 및 READY assertion을 추가한다 -- 실제 고정 데이터에서 계산기와 공유 API의 정합을 증명한다.
- [x] `tests/fixtures/golden/golden_signals.json`, `tests/fixtures/golden/README.md` -- D/E 시그널 집합과 다섯 전략 스키마를 갱신한다 -- 픽스처가 수동 편집·키 누락을 허용하지 않게 한다.

**Acceptance Criteria:**
- Given 기존 `compute_abc(frame)` 호출자가 있는 경우, when API를 호출하면, then 함수명·ticker·status·A/B/C 결과 의미는 유지되고 `signals`에 D/E가 추가된다.
- Given 유효한 120일 이상 OHLCV 프레임인 경우, when API가 성공하면, then A/B/C/D/E 각각에 프레임과 같은 인덱스의 bool Series와 전략별 청산 파라미터가 반환된다.
- Given D/E 전용 계산기가 계산하는 경우, when API 결과를 참조 구현과 비교하면, then 다섯 전략 모두 Jaccard ≥ 0.9이고 기준 픽스처의 모든 종목이 READY다.
- Given NaN/Inf 또는 계산 예외가 있는 경우, when API가 해당 종목을 처리하면, then ERROR와 `SIGNAL_COMPUTE_ERROR`가 반환되고 조용한 빈 신호로 변환되지 않는다.
- Given 기존 A/B/C API 회귀 테스트와 전체 backtest 테스트가 있는 경우, when 전체 검증을 실행하면, then 기존 동작 회귀 없이 통과한다.

## Design Notes

기존 A/B/C의 계산 의미를 보존하기 위해 A/B/C는 기존처럼 전체 유효 프레임에서 한 번 계산하고, D/E는 엄격한 OHLC 관계 검증이 가능한 연속 구간별로 계산한다. D/E 결과는 원래 인덱스로 재구성하며, 모든 전략에 마지막 평가 불가 봉·ATR(14) 무효 봉·invalid 행 신호를 제거하는 공통 실행 가능성 필터를 적용한다. 구조 오류와 NaN/Inf, 유효 구간 부재는 `SIGNAL_COMPUTE_ERROR`로 반환하고, 계산기 결과의 인덱스·bool 계약 위반도 조용히 보정하지 않는다.

## Spec Change Log

- 2026-09-04 review 보완: A/B/C 전체 프레임 의미 보존과 D/E 구간 분리를 명시하고, 마지막 봉·ATR·invalid 행 필터와 계산기 출력 계약을 구현·검증 범위에 고정했다. 기존 A/B/C golden 기준의 불필요한 재기준화와 조용한 신호 소실을 방지한다.

## Review Triage Log

### 2026-09-04 — Review pass
- intent_gap: 0
- bad_spec: 0
- patch: 8: (high 0, medium 6, low 2)
- defer: 0
- dismissed:
  - A/B/C 메타데이터에 모든 지표 파라미터가 필요하다는 finding — 캡처된 intent가 요구하는 메타데이터는 전략별 청산 파라미터이며, 전체 지표 스냅샷은 이번 API 계약 범위가 아니다.
  - A/B/C 계산 실패의 개별 전략 식별이 필요하다는 finding — 기존 `build_signals`가 A/B/C를 하나의 strict 호출로 계산하고 intent가 기존 오류 의미 보존을 요구하므로 `strategy=None` 호환성을 유지했다.
  - D/E 참조가 동일 계산기를 사용해 독립성이 부족하다는 finding — intent와 계획이 Story 6.1/6.2의 전용 계산기를 참조 구현으로 지정했으며, API 조립 회귀를 별도로 검증하는 구조다.
  - generator가 기존 golden 파일을 읽지 않는다는 finding — generator는 명시적 재생성 도구이고 저장 golden의 회귀 검증은 `test_golden_fixture.py`가 담당한다.
  - `screen_abc.py`와 전용 runner까지 단일 진입점으로 바꿔야 한다는 finding — 이번 intent는 `compute_abc` 반환 계약과 golden gate 확장이며, 기존 스크리닝 CLI·후속 태깅 소비자 변경은 후속 통합 범위다.
  - 태깅 stage가 아직 A/B/C만 소비한다는 finding — 명세의 Never 및 Code Map에 Story 6.6 후속 범위로 명시되어 있다.
- addressed_findings:
  - `[medium]` `[patch]` D/E 마지막 봉·ATR 실행 가능성 누락 — 다섯 전략 공통 필터와 구간 말단 필터를 적용하고 회귀 테스트를 추가했다.
  - `[medium]` `[patch]` 짧은 malformed 입력의 INELIGIBLE 오분류 — 구조·유한성 검증을 이력 길이 판정보다 먼저 수행했다.
  - `[medium]` `[patch]` 유효 구간 부재의 성공 오분류 — 명시적 typed error와 테스트를 추가했다.
  - `[medium]` `[patch]` 계산기 결과 인덱스·dtype 조용한 보정 — exact index와 bool dtype 계약을 검증하고 위반을 typed error로 전환했다.
  - `[medium]` `[patch]` A/B/C segmented rebaseline로 기존 의미 변경 — A/B/C 전체 프레임 계산을 복원하고 D/E만 segmented 처리했다.
  - `[medium]` `[patch]` generator strict/빈 전략 gate 누락 — A/B/C 참조를 strict 호출로 바꾸고 빈 참조 시 생성을 중단했다.
  - `[low]` `[patch]` golden 목록 스키마 검증 부족 — 정렬·중복 검사를 추가했다.
  - `[low]` `[patch]` D/E 양성·메타데이터 스키마 검증 부족 — 5키·전략별 파라미터·양성 mask 테스트를 추가했다.

## Verification

**Commands:**
- `uv run --with pandas --with numpy --with pyarrow --with pytest pytest backtest/tests/test_strategy_api.py backtest/tests/test_golden_fixture.py -q` -- expected: API 및 다섯 전략 골든 회귀 통과.
- `uv run --with pandas --with numpy --with pyarrow --with pytest pytest backtest -q` -- expected: 전체 backtest 회귀 통과.
- `uv run --with pandas --with numpy --with pyarrow python tests/fixtures/golden/generate_golden.py` -- expected: 다섯 전략 픽스처 sanity와 Jaccard gate 통과 후 결정적 파일 생성.
- `git diff --check` -- expected: 공백 오류 없음.

실행 결과:

- `pytest backtest/tests/test_strategy_api.py backtest/tests/test_golden_fixture.py -q` — 36 passed.
- `pytest backtest -q` — 130 passed.
- `python tests/fixtures/golden/generate_golden.py` — A/B/C/D/E Jaccard 1.0000, universe 98종목, 전 종목 READY; A 23·B 32·C 12·D 3·E 1.
- `python -m compileall -q ...` — 통과.
- `git diff --check` — 통과.
- 별도 Playwright·Supabase 검증 — 이번 변경은 backtest Python API와 고정 fixture만 다루며 UI·DB 표면이 없어 실행하지 않았다.

## Auto Run Result

Summary: `compute_abc`의 하위호환 진입점을 유지하면서 A/B/C/D/E 시그널과 전략별 청산 메타데이터를 반환하도록 확장했다. A/B/C 전체 프레임 의미는 보존하고 D/E는 invalid OHLC 구간을 연결하지 않도록 분리 계산했으며, 다섯 전략의 마지막 평가 불가 봉·ATR 무효·invalid 행을 공통 필터링했다. 골든 fixture와 Jaccard/READY gate도 5전략으로 확장했다.

Files changed:
- `backtest/strategy_api.py` — 5전략 조립, 파라미터 메타데이터, typed error, 구간·실행 가능성 검증.
- `backtest/tests/test_strategy_api.py` — 5키·메타데이터·양성 신호·실패·invalid 입력 회귀.
- `backtest/tests/test_golden_fixture.py` — 5전략 독립 참조와 Jaccard/READY/스키마 gate.
- `tests/fixtures/golden/generate_golden.py` — 5전략 deterministic 재생성 및 strict/빈 전략 gate.
- `tests/fixtures/golden/golden_signals.json`, `tests/fixtures/golden/README.md` — 5전략 fixture 스키마·결과 기록.
- `_bmad-output/implementation-artifacts/epic-6-context.md` — 최신 Epic 6 컨텍스트 재생성.
- `_bmad-output/implementation-artifacts/sprint-status.yaml` — Story 6-4를 in-progress로 동기화.

Review findings breakdown: patch 8건(중간 6, 낮음 2)을 수정했고, intent_gap·bad_spec·defer는 0건이다. 위 triage log의 6건은 기존 A/B/C 의미·입력 검증·실행 가능성·생성 gate를 보완했고, 2건은 스키마·양성 테스트 보강이다. 나머지 finding은 캡처된 intent의 범위와 기존 호환성 계약에 따라 기각했다.

Follow-up review recommendation: true (patched high 0, medium 6, low 2; score 20 = 3×6 + 1×2).

Residual risks: OOS/워크포워드와 LS 조정-방식론 동등성은 별도 Epic 6.8/운영 검증 범위다. `screen_abc.py`·태깅 stage의 D/E 소비 및 DB/outcome/UI 연결은 후속 Story 6.5~6.7에서 진행한다. 로컬 Docker/Postgres와 Playwright는 이번 변경 표면에 없어 실행하지 않았다.
