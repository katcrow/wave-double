---
title: '운영·백테스트 공유 전략 API 진입점'
type: 'feature'
created: '2026-09-02'
status: 'done'
baseline_revision: '149560b225dcfb0cff2194c3c33051c903a3fa89'
review_loop_iteration: 0
followup_review_recommended: false
context:
  - '{project-root}/_bmad-output/implementation-artifacts/epic-2-context.md'
  - '{project-root}/_bmad-output/planning-artifacts/architecture/architecture-wave-double-2026-08-31/ARCHITECTURE-SPINE.md'
warnings: [oversized]
deferred: []
---

<intent-contract>

## Intent

**Problem:** 운영(실전 태깅)과 백테스트가 각자 다른 전략 수식으로 진화하면 재현성이 깨진다. 기존 backtest의 `build_signals`는 지표 예외를 `try/except: pass`로 삼켜 무신호로 숨기므로(AD-5에서 반복 금지), 실전에서 재사용할 typed error 경계가 없다. Story 2.1/2.2가 `ohlcv_cache` 상태(READY/INELIGIBLE/ERROR) 계약을 제공하지만, 이를 소비해 A/B/C 시그널을 계산하는 공유 공개 API가 아직 없다.

**Approach:** `backtest/strategy_api.py`에 `compute_abc(frame, *, ticker="") -> StrategyResult` 공개 API를 신설한다. 기존 `indicator_opt/combine_strategies.build_signals`를 strict 모드로 호출해 A/B/C 시그널 마스크를 계산하고, 백테스트 엔진의 숨은 필터 3건(ATR(14) 게이트·마지막 봉 폐기·최소 보유 1봉)과 TP/SL SL-우선 규칙을 동일하게 적용·노출한다. 예외는 삼키지 않고 typed `SIGNAL_COMPUTE_ERROR`로 반환한다.

## Boundaries & Constraints

**Always:**
- `backtest/strategy_api.py`를 신설하며 `compute_abc(frame: pd.DataFrame, *, ticker: str = "") -> StrategyResult`가 유일 공개 진입점이다. `frame`은 `DatetimeIndex`와 제목 대문자 OHLCV 컬럼(`Open`/`High`/`Low`/`Close`/`Volume`) 계약을 갖는다.
- `StrategyResult`는 frozen dataclass로 `ticker: str`, `status: OhlcvCacheStatus`, `signals: dict[str, pd.Series]`(키 `"A"`/`"B"`/`"C"`, 값은 필터 적용된 bool 마스크), `error: StrategyError | None`을 가진다.
- 파라미터 상수는 기존 고정값을 그대로 재사용한다: `union.TOP3`, `union.VOLUME`(OBV window=3), `combine_strategies.STOCH_DB`(k14/D3/thr20/wk20/wd3), `DIV3`(k5/D3/div20/gap5), `sig_stoch_db_weekly_k`, `sig_div_stoch3`. 지표 로직은 변경하지 않는다.
- `build_signals`에 `strict: bool = False` 키워드 인자를 추가한다. 기본값이므로 기존 callers(`screen_abc.py`, `combine_strategies.run_combined`) 동작 불변. `strict=True`일 때 내부의 `try/except: pass`를 `raise`로 바꿔 예외를 삼키지 않는다.
- 숨은 필터를 시그널 마스크에 적용한다: (1) ATR(14) 게이트 — `backtest.indicators.atr`(window=14)이 신호 봉에서 `finite & > 0`이어야 신호 유효, (2) 마지막 봉 시그널 폐기 — 마지막 행의 신호를 제거(최소 보유 1봉 보장: 폐기로 인해 항상 판단할 후속 봉이 존재), (3) 최소 보유 1봉은 (2)에 암묵 포함.
- TP/SL SL-우선 규칙은 결과에서 재사용 가능한 공개 상수(예: `SL_PRIORITY = True`)와 규칙 주석으로 노출한다(Epic 3에서 재사용 대상). 이 스토리에서는 시그널 마스크에 이 규칙을 새 추출 로직으로 확장 구현하지 않는다.
- 이력 부족 판정: `frame`의 행 수가 `MIN_HISTORY_TRADING_DAYS`(120) 미만이면 `INELIGIBLE_INSUFFICIENT_HISTORY`를 반환한다(신호 계산 없음).
- 테스트는 `backtest/tests/test_strategy_api.py`에 추가한다(기존 backtest 커널 관례).

**Never:**
- 배치 오케스트레이션(`apps/batch/__main__.py`/`scheduler.py`/`candidate_stage.py`)에 연결하지 않는다(Story 2.5 범위).
- `compute_abc`가 Supabase/ohlcv_cache 저장소를 직접 참조하지 않는다. ohlcv_cache `READY` 게이트(어떤 종목을 계산 대상에 넣을지)는 호출자(Story 2.5)의 몫이며, `compute_abc`는 프레임 차원의 computability만 검사한다.
- 기존 `build_signals`의 기본 동작·시그니처를 바꾸지 않는다(`strict=False` 원복 보장, 기존 테스트 불변).
- 지표 수식·파라미터 값을 변경하지 않는다(재사용 상수 원문 유지).
- 골든 픽스처 회귀 테스트(Story 2.4)는 범위 밖 — 만들지 않는다. `compute_abc`는 이후 Story 2.4가 소비할 수 있도록 마스크를 온전히 반환한다.

## I/O & Edge-Case Matrix

| Scenario | Input / State | Expected Output / Behavior | Error Handling |
|----------|--------------|---------------------------|----------------|
| 정상 계산 | 충분 이력(≥120행) frame, 계산 가능 | `READY`, `signals`에 A/B/C 마스크(ATR(14)·마지막 봉 필터 적용), `error=None` | No error expected |
| 이력 부족 | 행 수 < 120 | `INELIGIBLE_INSUFFICIENT_HISTORY`, `signals={}`, `error=None` | No error expected |
| 비유한 입력 | `Close` 등에 NaN/Inf 포함 | `ERROR`, `error.code=SIGNAL_COMPUTE_ERROR`(strategy=None) | typed error 반환, 시스템 예외 미출구 |
| 지표 계산 예외 | strict 모드에서 지표 함수가 예외 | `ERROR`, `error.code=SIGNAL_COMPUTE_ERROR` | typed error 반환 |
| 마지막 봉 신호 | 신호가 마지막 행에만 존재 | `READY`, 해당 신호가 결과 마스크에서 제외(빈 마스크) | No error expected |
| ATR(14) 불유효 봉 신호 | 신호 봉의 ATR(14)이 non-finite 또는 ≤0 | `READY`, 해당 신호 제외 | No error expected |

</intent-contract>

## Code Map

- `backtest/strategy_api.py` -- 신규 모듈. `StrategyError`/`StrategyErrorCode`(=`SIGNAL_COMPUTE_ERROR`)/`StrategyResult`와 `compute_abc`를 정의하는 이번 스토리의 핵심 산출물.
- `backtest/indicator_opt/combine_strategies.py:31-55` (`build_signals`) -- A/B/C 마스크 합성 로직. `strict` 키워드 인자를 추가해 오류 숨김을 끈다(기본값 불변). `STOCH_DB`(25)와 `DIV3`(28) 상수는 재사용 원문.
- `backtest/indicator_opt/union.py:29-37` (`TOP3`/`VOLUME`/`OBV_WINDOW_DEFAULT=3`) -- 전략 A 필터·파라미터의 단일 원천. `_signals.py`의 `get_signal_fn`으로 지표 함수를 호출한다.
- `backtest/indicators/__init__.py:118-137` (`atr`) -- ATR(14) 게이트에 사용하는 엔진 표준 ATR(`run_backtest`와 동일 구현). 신호 봉 유효성의 진실 원천.
- `backtest/engine.py:66-79` (`_exit_price_on_bar`) -- TP/SL SL-우선 규칙의 단일 원천(Epic 3 재사용 참조). `strategy_api`는 이 규칙을 상수+주석으로 재현해 노출.
- `backtest/engine.py:114-117` (`run_backtest`의 `e >= len-1` / `atr finiteness`) -- 마지막 봉 폐기·ATR 게이트의 확인 지점.
- `packages/domain/domain/ohlcv_cache.py` -- `OhlcvCacheStatus`/`MIN_HISTORY_TRADING_DAYS`(120)의 단일 원천. `StrategyResult.status`가 재사용.
- `backtest/tests/test_engine.py` -- 엔진 규칙(TP/SL, ATR 게이트, 마지막 봉) 테스트 관례. `test_strategy_api.py`가 필터 기대값의 참고.
- `_bmad-output/planning-artifacts/epics.md:614-641` -- Story 2.3 AC 원문(A/B/C 상수, 숨은 필터 3건, SL-우선, typed error, 상태 구분).

## Tasks & Acceptance

**Execution:**
- `backtest/strategy_api.py` -- `StrategyErrorCode`(StrEnum `SIGNAL_COMPUTE_ERROR`), `StrategyError(frozen)`(code/strategy/message), `StrategyResult(frozen)`(ticker/status/signals/error), `compute_abc` 구현. `build_signals(... , strict=True)`를 호출하고, non-finite 입력·지표 예외를 `ERROR`/typed error로, 행 < 120을 `INELIGIBLE`로, 정상을 `READY`로 분기. ATR(14)·마지막 봉 필터를 각 전략 마스크에 적용하고 `signals={"A":..,"B":..,"C":..}`로 반환.
- `backtest/indicator_opt/combine_strategies.py` -- `build_signals`에 `strict: bool = False` 추가. `strict=True`일 때 OBV/조합/B/C 블록의 `try/except: pass`를 `raise`로 변경(스텝별 개별 예외 전파). 기본값 동작 불변 확인.
- `backtest/tests/test_strategy_api.py` -- I/O 매트릭스 6개 시나리오 + 숨은 필터(ATR 게이트·마지막 봉 폐기) + strict 없음(기존 `build_signals` 불변) 단위 테스트. 기존 backtest 테스트는 수정하지 않는다.

**Acceptance Criteria:**
- Given 충분 이력(≥120행)의 임의 일봉 frame일 때, when `compute_abc`를 호출하면, then `READY`와 함께 A/B/C 시그널 마스크가 `TOP3`/`VOLUME`(window=3)/`STOCH_DB`/`DIV3` 상수로 계산되어 반환되고 ATR(14)·마지막 봉 필터가 적용된다.
- Given `Close`에 NaN/Inf 등 비유한 값이 포함된 frame일 때, when `compute_abc`를 호출하면, then `ERROR`와 `SIGNAL_COMPUTE_ERROR` typed error가 반환되고 raw 예외가 밖으로 새지 않는다.
- Given 행 수가 120 미만인 frame일 때, when `compute_abc`를 호출하면, then `INELIGIBLE_INSUFFICIENT_HISTORY`가 반환되고 신호 계산이 일어나지 않는다.
- Given 마지막 봉에만 신호가 있거나 ATR(14)이 불유효한 봉에 신호가 있을 때, when `compute_abc`를 호출하면, then 해당 신호가 결과 마스크에서 제외된다(조용한 누락이 아닌 엔진 규칙 반영).
- Given `build_signals(..., strict=False)`(기본값)일 때, when `screen_abc.py`/`combine_strategies.run_combined`이 기존처럼 호출하면, then 기존 예외 삼킴 동작이 그대로 유지된다(회귀 없음).

## Spec Change Log

## Review Triage Log

### 2026-09-02 — Review pass
- intent_gap: 0
- bad_spec: 0
- patch: 2: (high 0, medium 1, low 1)
- defer: 0
- dismissed:
  - "`_check_non_finite_ohlvc`가 Volume도 검사하지만 이름이 OHLC를 암시한다" — 함수명이 이미 `ohlvc`(OHLCV)로 Volume 포함을 정확히 표현하며, spec Tasks가 "required OHLVC columns"으로 명시한다.
  - "`_apply_atr_last_bar_filters`의 마지막 봉 폐기 테스트가 mock상 마지막 봉만 커버하고 ATR 필터와의 조합을 놓친다" — 마지막 봉 폐기와 ATR 게이트는 각각 독립 테스트로 검증됐고, 두 규칙의 조합은 구현이 이미 올바르게 처리하는 단순 교집합이므로 결함이 아니다.
  - "`compute_abc`의 TP/SL 3.0, 3.0 매직 넘버가 조정 여지가 없다" — `build_signals`는 `tp_pct`/`sl_pct`를 전혀 사용하지 않으므로 이 값이 산출되는 A/B/C 마스크에 아무 영향이 없다(무의미한 dead 인자, 사전존재).
  - "strict 재-raise가 일관적이지 않고 strict=False 개발 중 조용한 빈 마스크가 데이터 이슈를 숨긴다" — 4개 try/except 블록 모두 `if strict: raise`로 균일하며, strict=False가 조용히 삼키는 것은 spec이 요구하는 하위 호환 기본값으로 의도된 동작이다.
  - "`_apply_atr_last_bar_filters`가 raw의 A/B/C 키를 검증하지 않아 KeyError 가능" — `compute_abc`는 build_signals의 고정 3-튜플로 `raw`를 항상 구성하므로 키가 항상 존재하며, 런타임에서 KeyError로 이어질 경로가 없다.
  - "`StrategyError.strategy` 필드가 현재 None만 사용돼 dead code" — spec상 필드는 typed 계약의 일부이며 frame 차원 오류에서 None으로 남는 것이 맞고, 정확성에 영향이 없다(부분 계산 배제는 의도).
  - "거래일 공백(비연속 날짜) index에 대한 테스트가 없다" — 모든 지표 계산·ATR 게이트는 위치 기반 또는 groupby 기반이라 휴일 공백이 결과를 바꾸지 않으며, `freq="B"` 픽스처가 대표적이다.
  - "Volume의 NaN을 가격 NaN과 동일하게 오류 처리해 과격하다" — spec Tasks가 필수 OHLVC 컬럼(Volume 포함)의 non-finite 검사를 명시하며, OBV/CMF가 Volume을 쓰므로 손상 Volume을 오류 처리하는 것은 AD-5의 조용한 누락 금지와 일치한다.
  - "`build_signals`의 `tp_pct`/`sl_pct`가 사용되지 않는 죽은 파라미터다" — 사전존재하던 vestigial 파라미터로, 이 diff에서 지표 계산에 영향이 없어 변경하지 않아도 결과에 영향이 없다.
  - "단일 `SIGNAL_COMPUTE_ERROR` 코드가 enum을 불필요하게 만든다" — intent가 명명한 코드가 정확히 그 값이며, `message` 필드가 non-finite vs 지표 예외를 이미 구분한다.
  - "전략 A만 실패·B/C 성공하는 부분 성공 시나리오 테스트가 없다" — strict 모드는 프레임 내 첫 지표 예외에서 전체를 ERROR로 처리하는 설계이며, "한 종목 오류가 나머지를 막지 않음"은 배치 루프(Story 2.5) 속성으로 단일 프레임 속성이 아니다.
  - "`SL_PRIORITY`가 아무데서도 안 쓰이는 forward-looking 데드 코드다" — spec이 Epic 3 재사용 계약으로 SL_PRIORITY 상수+주석 노출을 명시적으로 요구하는 의도된 산출물이다.
  - intent-alignment divergence 6건(엔진 행동 충실도 미검증·마스크 finiteness 미검증·strict 전 루프 커버리지·실제 마지막 봉 신호 테스트·재현성 범위) — 엔진 충실도 검증은 Story 2.4 골든 픽스처가 담당(명시적 범위 밖), build_signals는 `fillna(False)`로 bool 마스크를 반환해 finiteness가 보장되며, strict 재-raise는 단일 `get_signal_fn` patch로 모든 루프 커버(먼저 실행되는 루프가 raise), 실제 경로 마지막 봉은 TestNormalCompute가 커버한다.
- addressed_findings:
  - `[medium]` `[patch]` `backtest/strategy_api.py`(`compute_abc`): `_apply_atr_last_bar_filters`의 `atr()` 호출이 try/except 밖에 있어 ATR 계산이 예외를 던지면 raw 예외가 API 밖으로 새어 "시스템 예외 미출구" 계약을 위반할 수 있었다(edge-case-hunter). 필터 적용을 `build_signals` try/except 안으로 병합해 어떤 필터 단계 오류도 `ERROR`/`SIGNAL_COMPUTE_ERROR`로 래핑되도록 수정.
  - `[low]` `[patch]` `backtest/tests/test_strategy_api.py`: ATR 게이트의 `notna()`(NaN) 분기가 테스트되지 않았다(edge-case-hunter). NaN ATR 봉의 신호 제외 테스트를 추가(0값 분기와 함께 2개 분기 모두 커버).

## Design Notes

숨은 필터를 시그널 마스크로 옮기는 매핑: 엔진 `run_backtest`는 신호 봉 `e`에서 `e >= len(df)-1`이면 건너뛰고(마지막 봉 폐기), `atr_arr[e]`가 non-finite 또는 ≤0이면 건너뛴다(ATR 게이트). 최소 보유 1봉은 지연 루프가 `e+1`부터 시작하므로 항상 보장되며, 마지막 봉 폐기(`e ≤ len-2`)가 곧 "판단할 후속 봉 존재"를 보장한다. 따라서 `compute_abc`는 (1) 마지막 행의 신호 제거, (2) ATR(14)이 불유효한 봉의 신호 제거 두 규칙을 각 전략 마스크에 적용하면 엔진이 실제 진입할 신호 집합과 정확히 일치한다. 이는 Story 2.4 골든 픽스처가 `screen_abc.py` 결과와 전략별 Jaccard 유사도를 재는 기준으로 바르게 소비되게 한다.

`signals` 키는 `"A"/"B"/"C"` 대문자를 쓴다. Story 2.4 골든 픽스처의 `strategy_signals`가 이미 `{"A": [...]}` 대문자 계약이므로, 이 API가 그 계약과 정렬되어 이후 스토리의 소비 경계를 일치시킨다(운영 표기는 "전략 A/B/C").

비유한 입력 검사는 OHLVC 필수 컬럼에 대해 `np.isfinite`로 수행한다. 값이 하나라도 비유한하면 계산 전에 `ERROR`로 반환해 기존 `build_signals`가 NaN을 `fillna(False)`로 무신호 숨기던 경로를 차단한다(AD-5 "조용한 누락 금지").

## Verification

**Commands:**
- `uv run --with pandas --with numpy --with pyarrow --with pytest pytest backtest/tests/test_strategy_api.py -q` -- expected: 신규 테스트 전부 통과.
- `uv run --with pandas --with numpy --with pyarrow --with pytest pytest tests backtest/tests -q` -- expected: 기존 179개 + 신규 모두 통과(회귀 없음).
- `git diff --check` -- expected: whitespace 오류 없음.

## Auto Run Result

**요약:** 운영(실전 태깅)과 백테스트가 공유할 단일 전략 API 진입점인 `backtest/strategy_api.py`의 `compute_abc(frame, *, ticker="") -> StrategyResult`를 구현했다(AD-5, Epic 2 Story 2.3). `compute_abc`는 기존 `backtest/indicator_opt/combine_strategies.build_signals`를 `strict=True`로 호출해 A/B/C 시그널 마스크를 계산하고, 백테스트 엔진의 숨은 필터 3건(ATR(14) 게이트, 마지막 봉 폐기, 최소 보유 1봉)을 신호 마스크에 동일하게 적용한다. 예외는 삼키지 않고 typed `StrategyError(SIGNAL_COMPUTE_ERROR)`로 반환하며, 입력이 비유한(NaN/Inf)이거나 지표 계산이 실패하면 `ERROR` 상태, 이력이 120행 미만이면 `INELIGIBLE_INSUFFICIENT_HISTORY` 상태로 구분해 반환한다. 지표 수식·파라미터 상수(TOP3/VOLUME/STOCH_DB/DIV3)는 수정하지 않고 재사용했으며, 기존 `build_signals` 기본동작(strict=False)은 불변이어서 `screen_abc.py`/`combine_strategies.run_combined`은 회귀 없이 동작한다. TP/SL SL-우선 규칙은 Epic 3 재사용 계약으로 `SL_PRIORITY = True` 상수와 주석으로 노출했다. 배치 오케스트레이션 연결과 ohlcv_cache 저장소 접근은 spec의 Never 절대로 Story 2.5 범위에 남겨두었다.

**변경 파일:**
- `backtest/strategy_api.py` — `StrategyErrorCode`(SIGNAL_COMPUTE_ERROR)/`StrategyError`/`StrategyResult` frozen 계약과 `compute_abc` 공개 API, `SL_PRIORITY` 상수, ATR(14)·마지막 봉 필터, non-finite/이력 부족 게이트.
- `backtest/indicator_opt/combine_strategies.py` — `build_signals`에 `strict: bool = False` 키워드 추가. strict=True일 때 4개 try/except 블록이 `if strict: raise`로 예외를 재전파(기본값 동작 불변).
- `backtest/tests/test_strategy_api.py` — 15개 테스트(I/O 매트릭스 6행 전부 + strict 하위호환 + NaN ATR 분기).

**리뷰 결과 (2026-09-02 pass):** blind-hunter/edge-case-hunter/verification-gap/intent-alignment 4개 레이어 병렬 실행. patch 2건(medium 1, low 1) 전부 수정·재검증 완료 — (1) `atr()` 호출이 try/except 밖에서 이루어져 ATR 계산 오류 시 raw 예외가 API 밖으로 새어 "시스템 예외 미출구" 계약을 위반할 여지가 있던 문제를 필터 적용 전부를 try/except 안으로 병합해 해결, (2) ATR 게이트의 NaN(`notna()`) 분기 테스트 추가. dismissed 17건 — OHLCV 네이밍(함수명이 이미 Volume 포함), 마지막 봉+ATR 조합 테스트(각각 독립 검증·단순 교집합), 무의미한 TP/SL 인자(사전존재 dead arg), strict 기본 하위호환(의도), 불가능한 KeyError 경로(char→always 구성), strategy 필드 dead(단일 프레임 오류 설계), 거래일 공백(위치/groupby 기반 무영향), Volume NaN 처리(spec Tasks가 명시), 죽은 build_signals 파라미터(사전존재), 단일 enum 코드(intent 명시), 부분 성공(Story 2.5 배치 루프 속성), SL_PRIORITY(명시적 Epic 3 계약), intent-alignment divergence 6건(골든 픽스처는 Story 2.4 범위, bool 마스크 finiteness 보장, strict 전 루프 커버, 실제 마지막 봉 커버). defer 0건. 세부 근거는 Review Triage Log 참고.

**Follow-up review recommendation:** `false` (patch 1×medium + 1×low = 3×1 + 1×1 = 4 < 5, high 없음).

**검증 수행:**
- `uv run --with pandas --with numpy --with pyarrow --with pytest pytest backtest/tests/test_strategy_api.py -q` — 15 passed(패치 후 NaN ATR 테스트 1개 추가).
- `uv run --with pandas --with numpy --with pyarrow --with pytest pytest tests backtest/tests -q` — 194 passed(기존 179 + 신규 15), 회귀 없음.
- `git diff --check` — whitespace 오류 없음(CRLF/LF 알림만).
- I/O & Edge-Case Matrix 6개 시나리오 전부 커버하는 테스트가 실행·통과함을 확인(matrix test audit 통과).

**잔여 위험:**
- `compute_abc`는 아직 어떤 배치 진입점에도 연결되지 않았다(스펙 범위) — Story 2.5가 이를 `tags` stage에 연결해 ohlcv_cache `READY` 종목에 대해 실제 호출해야 동작한다.
- 재현성(운영 마스크가 엔진 매매 행동과 통계적으로 일치하는지) 검증은 Story 2.4 골든 픽스처(Jaccard ≥ 0.9)가 별도로 담당하며 spec 범위 밖이다.
- `StrategyResult.signals`의 A/B/C 키 대문자 계약은 Story 2.4 골든 픽스처 형식과 정렬되도록 선택한 것으로, 그 스토리에서 최종 소비 경계로 확정 필요.