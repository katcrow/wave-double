---
title: '골든 픽스처 회귀 테스트'
type: 'feature'
created: '2026-09-02'
status: 'done'
review_loop_iteration: 0
followup_review_recommended: true
baseline_revision: '95f947926a39c0a0b223c9e3502c640cf1f66364'
context:
  - '{project-root}/_bmad-output/implementation-artifacts/epic-2-context.md'
  - '{project-root}/_bmad-output/planning-artifacts/architecture/architecture-wave-double-2026-08-31/ARCHITECTURE-SPINE.md'
warnings: [oversized]
deferred:
  - summary: >-
      골든 gate는 yfinance 파생 픽스처만 실행하며 운영 LS sujung 데이터를 compute_abc 없이는 하지 않는다.
    evidence: |-
      gate/재생성 도구 모두 backtest/data/raw/*.parquet에서 생성한 ohlcv_raw를 원천으로 쓴다. 운영 데이터 재현은 AD-5 조정-방식론 동등성 단발성 검증의 별도 대상이며, 이 story는 그 선행조건을 문서화했을 뿐 강제하지 않는다. 선행조건 완료 전에는 Jaccard 통과 자체가 운영 재현증명이 되지 않는다.
    location: backtest/tests/test_golden_fixture.py
    severity: high
  - summary: >-
      ohlcv_raw.json.gz(3.2MB)에 .gitattributes·크기 경고가 없다.
    evidence: |-
      향후 재생성이 종목·거래일을 늘리면 바이너리 픽스처가 repo를 조용히 비대화할 수 있다. 현재는 고정·결정적이고 크기가 수용 가능하다.
    location: tests/fixtures/golden/ohlcv_raw.json.gz
    severity: low
  - summary: >-
      backtest 테스트가 packages/domain을 pyproject pythonpath로 암묵 의존하고 CI 커맨드에는 보이지 않는다.
    evidence: |-
      CI의 `pytest backtest -q`는 `[tool.pytest.ini_options] pythonpath`에 의존해 strategy_api → domain import가 통과한다. Story 2-3 test_strategy_api에서 이미 확립된 관례이며, 명시화만 부족하다.
    location: .github/workflows/test.yml
    severity: low
---

<intent-contract>

## Intent

**Problem:** Backtest가 검증한 전략 A/B/C를 운영 태깅이 실제로 재현하는지 자동 확인할 gate가 없다. Story 2.3의 `compute_abc`는 신호 마스크를 내놓지만, 기존 `screen_abc.py` 산출물과 통계적으로 일치하는지 검증하는 회귀 gate가 없으면 태깅 재구현이 전략을 어긋나게 재현해도 눈치채지 못한다(AD-5 "조용한 누락 금지" 위반).

**Approach:** `tests/fixtures/golden/`에 거래일·종목집합·일봉 원본·참조 시그널 3파일을 고정하고, `backtest/tests/test_golden_fixture.py`가 `compute_abc` 결과를 `screen_abc.py` 방식의 참조와 전략별 Jaccard(≥0.9)로 대조한다. 빈 픽스처·키 불완비는 명시적 실패로 처리한다.

## Boundaries & Constraints

**Always:**
- `tests/fixtures/golden/`에 다음 3파일을 고정한다(Story 2.4 AC, AD-5):
  - `golden_day.json` — `{ "trading_day": "2026-08-26", "batch_kind": "close", "universe": ["종목코드…"] }`
  - `ohlcv_raw.json.gz` — `daily_ohlcv` 스키마 필드(`ticker`/`trading_day`/`open`/`high`/`low`/`close`/`volume`, `sujung=Y`)를 그 거래일까지 포함한 일봉 원본의 gzip 압축 JSON(AC의 "동일 형식의 압축 파일" 허용조항 사용). 종목별 컬럼형 배열로 인코딩한다.
  - `golden_signals.json` — `{ "trading_day", "strategy_signals": { "A": ["종목코드…"], "B": […], "C": […] } }`. 각 전략은 비어 있으면 안 된다.
- golden_day는 `2026-08-26`로 고정한다(대부분 종목의 마지막 완료 거래일; 08-27엔 45종목만 있어 제외). universe는 raw 일봉에서 해당 날짜까지 데이터가 **120행 이상**인 종목(98종목)으로 산출한다. 최소 120거래일 미만 종목은 계산 대상에서 제외된다(Story 2.1/2.3 계약).
- 참조 시그널은 `screen_abc.py`와 **동일한 호출 경로**(`combine_strategies.build_signals(frame, 3.0, 3.0, ticker)`, 기본 `strict=False`)로, 창 `[2026-01-01, trading_day]` 내 신호가 1개 이상 있는 종목의 집합이다(`screen_abc.screen()`의 기본 창과 일치).
- 회귀 gate(`test_golden_fixture.py`)는 다음을 검증한다: ① 3파일 존재·비공백·`strategy_signals` 키 완비(A/B/C)+비공백(빈 픽스처 명시적 실패), ② universe·신호 집합이 `ohlcv_raw`에 모두 존재, ③ `ohlcv_raw`로 참조를 재계산했을 때 저장된 `golden_signals`와 **정확히 일치**(참조 재현성), ④ `compute_abc` 결과와 전략별 Jaccard **모두 ≥ 0.9**, ⑤ 모든 universe 종목이 `READY`(INELIGIBLE/ERROR는 명시 실패·보고), ⑥ 미달 시 불일치 종목 목록(ref−new, new−ref) 출력.
- 판정 기준 문서화(AC): 완전 일치가 아닌 **통계적 유사도(Jaccard≥0.9)**가 기준이며, backtest(yfinance 배당조정)와 운영(LS `sujung`)의 조정-방식론 동등성이 별도 단발성 검증으로 확인된 후에만 이 gate가 유효함을 명시한다(AD-5). 이 문구는 `tests/fixtures/golden/README.md`·테스트 모듈 docstring·재생성 도구 주석에 둔다.
- 게이트는 CI에 포함된다: 테스트를 `backtest/tests/`에 두어 기존 `pytest backtest`(test.yml)가 자동 실행한다.
- 재생성 도구 `tests/fixtures/golden/generate_golden.py`를 제공한다(개발 유틸). 실행 시 3파일을 결정적으로 재생성하고, 재생성 결과 Jaccard≥0.9를 sanity로 강제한다.

**Never:**
- 지표 수식·파라미터·`combine_strategies`/`strategy_api` 로직을 변경하지 않는다(재현 gate가 대상 로직을 바꾸지 않음).
- `screen_abc.py`의 동작을 바꾸지 않는다.
- 배치 오케스트레이션(`apps/batch`) 연결은 Story 2.5 범위 — 하지 않는다.
- `golden_signals.json`을 수동 편집으로 gate를 통과시키는 방식을 만들지 않는다(③ 재현성 검사로 방어).
- 픽스처를 테스트가 자동 재생성하도록 하지 않는다 — 픽스처는 고정이며 재생성은 명시적 도구 실행으로만 가능하다.

## I/O & Edge-Case Matrix

| Scenario | Input / State | Expected Output / Behavior | Error Handling |
|----------|--------------|---------------------------|----------------|
| 정상 gate | 3파일 존재·비공백·키 완비, Jaccard≥0.9 | 통과(배포 허용), 전략별 Jaccard 출력 | No error expected |
| 빈 픽스처 | golden/ 파일 없음·비어있음·A/B/C 키 불완비 | 명시적 실패(빈 픽스처로 통과 불가, AD-5) | assertion 실패 |
| Jaccard 미달 | 어느 전략이 Jaccard<0.9 | 실패 + 불일치 종목 목록(ref−new, new−ref)과 원인 조사 정보 출력 | assertion + 목록 |
| 참조 불일치 | `ohlcv_raw` 재계산 ≠ 저장된 `golden_signals` | 실패(픽스처 오염·수동 편집 탐지) | assertion 실패 |
| non-READY 종목 | universe 내 compute_abc가 INELIGIBLE/ERROR | 명시 실패·해당 종목 보고(조용한 누락 금지) | assertion 실패 |
| Jaccard 1.0 | 현재 확정 픽스처(98종목) | A/B/C 모두 1.0으로 통과 | No error expected |

</intent-contract>

## Code Map

- `backtest/strategy_api.py` -- Story 2.3 산출물. `compute_abc(frame, *, ticker="") -> StrategyResult`가 회귀 gate의 신규 신호 원천. ATR(14)·마지막 봉 폐기 필터 적용, `READY`/`INELIGIBLE_INSUFFICIENT_HISTORY`/`ERROR` 상태.
- `backtest/indicator_opt/screen_abc.py:26-41` (`screen`) -- 참조 산출의 계약 원천. `build_signals(df, tp_pct, sl_pct, ticker)`를 전체 프레임에 호출한 뒤 `[start_ts, latest]` 윈도우로 시그널을 센다. golden 참조는 이 함수와 같은 호출·윈도우 규칙을 재현한다(함수 자체는 수정 금지).
- `backtest/indicator_opt/combine_strategies.py:31-61` (`build_signals`) -- A/B/C 마스크 합성. 참조와 신규 양쪽이 이 함수를 공유(참조는 기본 호출, `compute_abc`는 `strict=True`).
- `backtest/data/loader.py:44-49` (`load_all`) -- `backtest/data/raw/*.parquet` 로드. 재생성 도구의 데이터 원천(raw 104종목, 2020-08~2026-08).
- `backtest/data/raw/meta.json` -- raw 일봉 범위 확인(마지막 완료 거래일 2026-08-26/27 분포). golden_day 선택 근거.
- `backtest/tests/test_strategy_api.py` -- 기존 strategy_api 테스트 관례(import 경로 `backtest.strategy_api`, `_make_df` 헬퍼, 클래스 단위 테스트). 새 게이트 테스트가 이 디렉터리 관례를 따른다.
- `.github/workflows/test.yml:31-32` -- `pytest backtest -q`로 backtest 전 테스트를 CI에서 실행. 신규 게이트 테스트가 여기에 자동 포함된다.
- `pyproject.toml:18-19` (`[tool.pytest.ini_options] pythonpath = [".", "packages/domain"]`) -- `domain.ohlcv_cache` import가 pytest 환경에서만 통과. 테스트·재생성 도구 실행 시 `PYTHONPATH=packages/domain` 필요(재생성 도구), pytest는 자동.
- `tests/fixtures/.gitkeep` -- Story 1.1 스캐폴드 잔재. `golden/` 신설로 실제 내용이 생기므로 제거한다.

## Tasks & Acceptance

**Execution:**
- `tests/fixtures/golden/generate_golden.py` -- 신규 개발 유틸: raw parquet → golden_day/ohlcv_raw(gz)/golden_signals 3파일을 결정적으로 생성. golden_day·window·반올림 규칙을 상수로 고정하고, 재생성 시 참조 대비 `compute_abc` Jaccard≥0.9를 sanity로 강제. raw parquet 로드에 pyarrow 필요.
- `tests/fixtures/golden/golden_day.json` -- 생성물: `{"trading_day":"2026-08-26","batch_kind":"close","universe":[98종목]}`.
- `tests/fixtures/golden/ohlcv_raw.json.gz` -- 생성물: `{"sujung":"Y","ohlcv":{ticker:{trading_day/open/high/low/close/volume}}}`(open/high/low/close 4자리, volume 2자리 반올림), gzip.
- `tests/fixtures/golden/golden_signals.json` -- 생성물: `{"trading_day", "strategy_signals":{"A":[23종목],"B":[32종목],"C":[12종목]}}`.
- `tests/fixtures/golden/README.md` -- 3파일 스키마 계약·인코딩·재생성 방법·Jaccard 판정 기준·조정-방식론 선행조건 문서화(AC).
- `backtest/tests/test_golden_fixture.py` -- 신규: ①픽스처 존재/비공백/키 완비+비공백, ②집합 멤버십 일관성, ③참조 재현 정확 일치, ④Jaccard 게이트(전략별 ≥0.9, 미달 시 불일치 목록), ⑤전 종목 READY 강제.
- `tests/fixtures/.gitkeep` -- 제거(golden/로 대체).

**Acceptance Criteria:**
- Given 고정된 golden_day(2026-08-26)·98종목 universe·비어있지 않은 A/B/C 참조 시그널이 있을 때, when `test_golden_fixture.py`를 실행하면, then `compute_abc` 결과와 참조의 전략별 Jaccard가 모두 ≥0.9로 통과하고 각 Jaccard가 출력된다.
- Given `ohlcv_raw`로 frame을 재구성해 참조를 다시 계산하면, when 저장된 `golden_signals.json`과 비교하면, then 정확히 일치한다(참조 산출 재현성 — 수동 편집·오염 탐지).
- Given 어느 한 전략이라도 Jaccard<0.9이면, when gate를 실행하면, then 실패하며 불일치 종목 목록(ref−new, new−ref)이 출력된다(원인 조사 가능).
- Given 픽스처가 비어있거나 `strategy_signals` 키가 불완비이면, when 테스트를 실행하면, then 명시적으로 실패한다(빈 픽스처로 통과 불가, AD-5).
- Given universe 종목 중 하나라도 `compute_abc`가 `READY`가 아니면, when gate를 실행하면, then 조용히 제외되지 않고 명시 실패로 보고된다.
- Given gate가 배포 직전 CI에 포함되어야 하는 경우, when `.github/workflows/test.yml`의 `pytest backtest`가 실행되면, then 이 테스트가 포함되어 Jaccard 미달 시 배포가 차단된다.

## Spec Change Log

## Review Triage Log

### 2026-09-02 — Review pass
- intent_gap: 0
- bad_spec: 0
- patch: 6 (high 0, medium 2, low 4)
- defer: 3 (high 1, medium 0, low 2)
- dismissed:
  - Jaccard 실패 메시지가 ref−new/new−ref 라벨을 바꿨다 — 검증 결과 라벨이 수식과 정합(ref−new = `ref_set − new_set`, new−ref = `new_set − ref_set`)이고 gate·재생성 도구 양쪽 모두 동일 규칙.
  - 스펙 Design Notes의 08-27 수치 모순(48 vs 45) — 수정 대상이 빌드 중인 스펙이므로 규칙상 dismiss(도구 코드 리뷰 4개 은닉층 산출물).
  - 창 종점 08-26이 compute_abc 마지막 봉 폐기와 겹침 — 참조를 int창보다 짧게 바꾸면 screen_abc 창 계약(intent)과 충돌하고, 픽스처에 실제 발산 없음(Jaccard 1.0, 불일치 목록 공집합). Design Notes가 인지·기록.
  - ③ 참조 재현성 검사가 순환적 — 참조가 build_signals 출력으로 정의되는 것은 intent 설계이고, README는 '수동 편집·픽스처 오염 탐지'라는 정확한 기능만 주장한다.
  - 반올림·절단으로 golden_signals가 screen_abc 실제 출력과 다를 수 있음 — 절단(미래 봉 제거)은 look-ahead 없는 지표 계산에 구조적으로 무영향, 반올림(가격 4·거래량 2자리)은 실측 Jaccard 1.0으로 신호 비뒤집힘이 확인돼 현재 경로가 없음.
  - Jaccard가 빈 union에서 1.0 → ①(저장 시그널 비공백)+③(재계산==저장)이 게이트 실행 전 ref 비공백을 보장해 도달 불가.
  - NFR-6 문서 미갱신 — NFR-6 문서(epics.md NFR6, prd.md, api-map.md:sujung 검증 필요, validation-report M7)에 통계적 유사도 기준·조정-방식론 선행조건이 이미 문서화돼 실체 요건 충족.
  - ticker의 딕셔너리 키 인코딩 — README·스펙이 문서화했고 데이터 완전 회복 가능.
  - ohlcv_raw의 pricechk 누락 — AC 자체 필드 목록에 없고 지표 계산에 불필요, README가 실제 필드 문서화.
  - CI '선행 검증'이 별도 단계가 아니라 테스트 순서에 의존 — pytest가 정의 순서로 ① 클래스를 ④보다 먼저 실행하므로 실질 영향 없음.
  - 중첩 컬럼형 인코딩 vs 일봉 row 형태 — AC가 '동일 형식의 압축 파일' 허용 조항을 두고 스펙이 인코딩을 문서화.
  - 스펙 파일 자체 trailing newline 부재 — 수정 대상이 빌드 중인 스펙이므로 규칙상 dismiss.
- addressed_findings:
  - `[medium]` `[patch]` 재생성 도구 compute_new의 non-READY KeyError(신호 딕셔너리 빈 접근) — non-READY/빈 signals를 all-False로 처리하고 _assert_parity가 정렬된 non-READY 목록으로 명시 실패하도록 수정(조용한 누락 금지).
  - `[medium]` `[patch]` 잘못된 --trading-day의 빈 universe 재생성 + parity 통과 전 파일 기록 — build_universe 직후 빈 universe SystemExit 가드 추가, _assert_parity를 3파일 기록 이전으로 재배열(실패 시 권위 픽스처 보존).
  - `[low]` `[patch]` ohlcv_raw 데이터 무결성 invariants 부재 — universe와 ohlcv 키 집합 정확 일치, 종목별 6개 배열 길이 동일, trading_day 엄격 오름차순+중복 없음+golden 거래일 도달을 검증하는 테스트 3개 신규 추가(12 passed).
  - `[low]` `[patch]` golden_day.json·golden_signals.json trailing newline 부재 — 생성기가 `json.dumps(...) + "\n"`으로 기록(gzip mtime=0 결정성 유지).
  - `[low]` `[patch]` 재생성 명령 문서 불일치/중복(PYTHONPATH) — 스크립트가 sys.path를 자기 부트스트랩하므로 docstring·README를 `uv run --with ... python tests/fixtures/golden/generate_golden.py`로 통일.
  - `[low]` `[patch]` magic number 120 중복 — `domain.ohlcv_cache.MIN_HISTORY_TRADING_DAYS`를 import해 generator universe와 compute_abc 적격 판정의 임계값을 단일 원천으로 통합.

## Auto Run Result

- **구현 요약:** Story 2.4 골든 픽스처 회귀 gate를 구현했다. `tests/fixtures/golden/`에 golden_day(2026-08-26, universe 98종목)·ohlcv_raw(gzip, sujung=Y, mtime=0 결정적)·golden_signals(A 23/B 32/C 12) 3파일을 고정하고, `backtest/tests/test_golden_fixture.py`가 ①존재·비공백·키 완비, ②집합 멤버십(정확 일치·배열 길이·오름차순·golden일 도달), ③참조 재현 정확 일치, ④전략별 Jaccard≥0.9 게이트, ⑤전 종목 READY를 강제한다. 결정적 재생성 도구 `generate_golden.py`는 parity sanity(Jaccard≥0.9)를 파일 기록 전에 강제하고 non-READY·빈 universe를 명시 실패로 처리한다.
- **변경 파일:**
  - `tests/fixtures/golden/generate_golden.py` — 신규 결정적 재생성 도구(raw parquet → 3파일, parity 전 검증, mtime=0 gzip, domain MIN_HISTORY 상수 사용).
  - `tests/fixtures/golden/golden_day.json` — golden_day 2026-08-26·universe 98종목.
  - `tests/fixtures/golden/ohlcv_raw.json.gz` — universe별 전체 일봉 원본(sujung=Y, 컬럼형, 가격 4·거래량 2자리 반올림), 3.2MB gzip.
  - `tests/fixtures/golden/golden_signals.json` — 참조 시그널 A 23·B 32·C 12(오름차순).
  - `tests/fixtures/golden/README.md` — 3파일 스키마 계약·재생성·Jaccard 판정·AD-5 선행조건 문서(신규).
  - `backtest/tests/test_golden_fixture.py` — 회귀 gate 12개 테스트(신규, CI `pytest backtest`에 자동 포함).
  - `tests/fixtures/.gitkeep` — 삭제(golden/로 대체).
- **리뷰 결과:** patch 6건 전부 수정(medium 2, low 4) · deferred 3건 기록 · dismissed 12건(근거 포함). bad_spec·intent_gap 없음.
- **추적 리뷰 권장:** 이번 패스 patch 중 high 없음, score = 3×2(medium) + 1×4(low) = 10 ≥ 5 → **권장함**(deferred의 운영데이터 선행조건 검증 완료 시 재점검).
- **수행한 검증:**
  - `uv run --with pandas --with numpy --with pyarrow --with pytest pytest backtest/tests/test_golden_fixture.py -q -s` → **12 passed**, Jaccard A/B/C **1.0000** 출력.
  - `uv run --with pandas --with numpy --with pyarrow --with pytest pytest backtest -q` → **43 passed**(기존 회귀 없음).
  - `uv run --with pandas --with numpy --with pyarrow python tests/fixtures/golden/generate_golden.py --trading-day 2026-08-26` → universe 98, 참조 23/32/12, sanity Jaccard A/B/C 1.0000, 실행 2회 sha1 동일(결정적), 빈 universe(--trading-day 2020-01-05)는 "universe 비어 있음" SystemExit·파일 미기록.
  - `git diff --check` → whitespace 오류 없음(CRLF 안내 경고만).
- **잔여 리스크:** ① 골든 gate는 yfinance 파생 픽스처로만 동작 — 운영 LS sujung 재현은 AD-5 조정-방식론 동등성 단발성 검증이 완료된 후 유효(deferred, severity high). ② 픽스처 재생성 시 raw parquet 원천이 픽스처 오염 없이 유지돼야 함(③ 재현성 검사가 방어). ③ `*_raw.gzip` 크기(3.2MB)의 향후 비대화(deferred, low).

## Design Notes

golden 요일 선택: raw 데이터 마지막 거래일 분포는 08-27(48종목)·08-26(55종목)·06-30(1종목). 08-26은 98종목이 120행 이상을 가지는 최신 완료일이고, 08-27은 45종목만 가져 universe가 급감한다. 참조 시그널 집합은 08-24~08-26 모두 동일(23/32/12)해, 가장 universe가 큰 08-26을 고정했다.

참조 산출과 신규 산출의 차이는 결국 숨은 필터(ATR(14)·마지막 봉 폐기)뿐이다. compute_abc는 각 종목 프레임의 마지막 행(시그널 판정 창 밖) 신호만 제거하므로, 창 `[2026-01-01, trading_day]` 내 신호 집합에는 영향이 거의 없어 실측 Jaccard가 A/B/C 모두 1.0이다(관측證據). 0.9 임계값은 yfinance vs LS `sujung` 조정 차이가 신호 재현에 무시 가능하다는 가정의 여유분이다.

ohlcv_raw 반올림(가격 4자리·거래량 2자리)은 결정적 최소 표현을 위한 것이며, 참조와 신규 신호가 **같은 반올림 데이터에서** 계산되어 내부 정합을 해치지 않는다. gzip은 raw JSON 9.0MB → 3.1MB로 줄인다(AC의 압축 허용 조항).

재생성 도구는 `screen_abc.py`의 기본 창(`start=2026-01-01`)과 동일한 `WIN_START` 상수를 쓴다. 창 규칙을 어기면 참조가 저장된 golden_signals와 틀어져 ③ 재현성 검사가 잡아낸다.

## Verification

**Commands:**
- `PYTHONPATH=packages/domain uv run --with pandas --with numpy --with pyarrow --with pytest pytest backtest/tests/test_golden_fixture.py -q` -- expected: 신규 테스트 전부 통과(Jaccard A/B/C = 1.0).
- `uv run --with pandas --with numpy --with pyarrow --with pytest pytest backtest -q` -- expected: 기존 backtest 전체 회귀 없음.
- `PYTHONPATH=packages/domain uv run --with pandas --with numpy --with pyarrow python tests/fixtures/golden/generate_golden.py --trading-day 2026-08-26` -- expected: 3파일 재생성 + parity sanity(Jaccard≥0.9) 통과.
- `git diff --check` -- expected: whitespace 오류 없음.