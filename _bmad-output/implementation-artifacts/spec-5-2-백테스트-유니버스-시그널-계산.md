---
title: 'Story 5.2: 백테스트 유니버스 시그널 계산'
type: 'feature'
created: '2026-09-10'
status: 'done'
review_loop_iteration: 0
followup_review_recommended: true
context:
  - 'C:/dev/wave-double/_bmad-output/implementation-artifacts/epic-5-context.md'
warnings: ['oversized']
deferred:
  - summary: >-
      AGENTS.md에 문서화된 테스트 명령으로는 pyyaml이 없어 tests/tools/test_check_sprint_status.py
      3건이 ModuleNotFoundError로 실패한다.
    evidence: |-
      `uv run --with pandas --with numpy --with pyarrow --with pytest pytest`로 실행하면
      tools/check_sprint_status.py:37의 `import yaml`이 실패해 3건이 깨지고,
      `--with pyyaml`을 더하면 661건 전부 통과한다. 이 스토리와 무관한 선행 결함이며,
      고치려면 AGENTS.md(agent-context 문서) 또는 pyproject 의존성을 손대야 한다.
      후자는 epic-5 경로 manifest 범위를 벗어난다.
    location: >-
      AGENTS.md:23
    severity: medium
  - summary: >-
      운영 코드가 tests/ 아래 fixture를 읽으므로 배포 패키징이 tests/를 제외하면
      load_backtest_universe()가 깨진다.
    evidence: |-
      apps/batch/backtest_universe.py의 FIXTURE_PATH가 tests/fixtures/backtest_universe.json을
      가리킨다. 위치는 Story 5.2 AC("tests/fixtures 또는 그에 준하는 버전 고정 위치")가
      지정한 것이고 현재 배치는 리포지토리 체크아웃에서 실행되어 문제가 없다. Story 5.4의
      배치 배선 시 패키징 경계를 확인해야 한다.
    location: >-
      apps/batch/backtest_universe.py:25
    severity: low
baseline_revision: 'd236901e37eb459b2e8313f91165dbbe7417a70c'
baseline_commit: 'd236901e37eb459b2e8313f91165dbbe7417a70c'
---

<intent-contract>

## Intent

**Problem:** 편향 지표(FR-10)는 "백테스트 유니버스 ∩ 전략 시그널"을 후보 모집단 시그널과 대조해야 하지만, 유니버스 목록은 `yfinance`를 import하는 백테스트 전용 스크립트와 `backtest/data/raw/*.parquet` 디스크 상태에만 존재해 운영 배치가 참조할 수 없다. 게다가 Epic 2의 `daily_ohlcv` 적재는 후보 모집단 종목만 채우므로, 유니버스 종목 대부분이 `INELIGIBLE_INSUFFICIENT_HISTORY`로 계산 제외되어 지표 자체가 무의미해진다.

**Approach:** 유니버스 목록을 버전 고정 JSON fixture로 승격하고(원본과의 drift는 테스트가 막는다), 후보 모집단 멤버십과 무관하게 유니버스 종목의 `daily_ohlcv`를 독립 백필한 뒤, 운영 태깅과 동일한 `compute_abc` 진입점으로 임의 거래일의 전략 A~F 시그널 집합을 재현 가능하게 산출하는 순수 계산 함수를 만든다.

## Boundaries & Constraints

**Always:** 유니버스 fixture는 `backtest/data/raw/*_KS.parquet`가 확정하는 실제 백테스트 유니버스(현재 104종목, `backtest.data.loader.list_tickers()`와 동일 집합)를 권위로 삼고, 운영이 쓰는 6자리 코드와 백테스트가 쓰는 `.KS` 티커를 함께 보관한다. 전략 시그널은 `backtest.strategy_api.compute_abc`만으로 계산하고(AD-5) `build_signals`를 직접 호출하지 않으며, 지표 로직·`backtest/` 커널·`screen_abc.py`를 수정하지 않는다. 시그널 성립 봉은 운영 태깅과 동일하게 `signals[key].iloc[-2]`(D-1 확정봉)이다. 일봉 원천은 Epic 2 `daily_ohlcv`를 재사용하고(실전과 동일 기준), 백필은 `initialize_new_ticker_history`/`update_existing_ticker_history`를 그대로 재사용한다. 한 종목의 실패가 나머지를 막지 않고 종목별 상태(`READY`/`INELIGIBLE_INSUFFICIENT_HISTORY`/`ERROR`)가 집계로 노출된다. 같은 (유니버스, 거래일, `daily_ohlcv` 내용)에는 같은 결과가 나와야 한다. 운영 경로 코드는 `yfinance`나 `backtest.data.*`(parquet 의존)를 import하지 않는다.

**Never:** `bias_events`/`bias_event_by_source`에 쓰지 않는다(적재는 Story 5.4, 교집합·차집합·기회누락 산식은 Story 5.3). 새 `Stage` enum 값·`write_stage` 계약·`scheduler.py` 배선을 추가하지 않는다(Story 5.4). migration을 추가하지 않는다. 후보 모집단 적재 경로(`scheduler.py`의 기존 두 호출)의 티커 목록을 바꾸지 않는다 — 유니버스 백필은 별도 호출로만 더한다. fixture를 `fetch_kospi200.py`의 선언 목록(108종목)으로 대체하지 않는다.

## I/O & Edge-Case Matrix

| Scenario | Input / State | Expected Output / Behavior | Error Handling |
|---|---|---|---|
| HAPPY_PATH | 유니버스 104종목 전원 120거래일 이상 캐시됨, 거래일 T | 종목별 `READY`, 전략 A~F별 시그널 종목 집합(D-1 봉 기준), `ready_count=104` | 없음 |
| SHORT_HISTORY | 일부 종목이 T까지 120행 미만 | 해당 종목만 `INELIGIBLE_INSUFFICIENT_HISTORY`로 집계, 시그널 집합에서 제외, 나머지는 정상 산출 | 실패 아님 |
| LOAD_ERROR | 특정 종목 `load_ohlcv`가 `ERROR` 반환 또는 예외 | 해당 종목만 `ERROR` 집계, 나머지 종목 계산 계속 | 종목 단위 격리 |
| COMPUTE_ERROR | `compute_abc`가 `status=ERROR`/`error` 반환 | 해당 종목만 `ERROR` 집계, 전략 키는 부분 반영하지 않음 | 종목 단위 격리 |
| BACKFILL_INDEPENDENT | 유니버스 종목이 후보 모집단에 전혀 없음 | 후보 멤버십과 무관하게 전체 이력 적재/증분 갱신 수행 | 종목별 부분 성공 허용 |
| BACKFILL_TICKER_FORM | fixture의 `.KS` 티커 | 6자리 코드로 정규화해 전달(`SupabaseOhlcvCacheRepository._validate_tickers`의 `isalnum()` 통과) | 정규화 불가 시 fixture 로드 시점 예외 |
| FIXTURE_DRIFT | fixture가 `list_tickers()`와 불일치 | 테스트 실패 | 명시적 assert |
| REPRODUCIBLE | 같은 캐시·거래일로 두 번 실행 | 동일한 전략별 종목 집합(정렬된 결정론적 결과) | 없음 |

</intent-contract>

## Code Map

- `backtest/data/fetch_kospi200.py:12-333` -- 유니버스 원본 선언 `KOSPI200代表性`(305개 리터럴 → `sorted(set(...))`로 **108** unique), 접근자 `fetch_stock_list()`. 모듈 최상단에서 `yfinance`를 import하므로(`:9`, 미설치 환경) **운영 코드와 테스트 모두 이 모듈을 import하면 안 된다** — 정적 파싱으로만 대조한다.
- `backtest/data/loader.py:9,23,32` -- `DATA_DIR = .../raw`, `list_tickers()`(`*_KS.parquet` glob, sorted), `load_ticker()`. **실측 104개**로 에픽의 "104종목"과 정확히 일치하며 이것이 유니버스 권위다. 선언 108 - 실측 104의 차이는 `000060`/`003410`/`012270`/`012510`(다운로드 실패분)이다.
- `backtest/indicator_opt/screen_abc.py:18,29,37` -- `load_all()`로 디스크 유니버스를 암묵 사용하고 `build_signals`를 직접 호출한다. 이 스토리는 **이 경로를 재사용하지 않고 별도 구축**한다(epics.md:1398).
- `backtest/strategy_api.py:198` -- `def compute_abc(frame: pd.DataFrame, *, ticker: str = "") -> StrategyResult`. 입력 계약: `Open/High/Low/Close/Volume` 컬럼, 중복 없는 오름차순 `DatetimeIndex`, 숫자형, finite. 반환 `StrategyResult(ticker, status, signals: dict[str, pd.Series], error, params_meta)`; `signals` 키는 `_STRATEGY_KEYS=("A","B","C","D","E","F")`(`:26`)이고 값은 `frame.index`와 동일 인덱스의 bool Series(전 구간 마스크). `len(frame) < MIN_HISTORY_TRADING_DAYS`면 `INELIGIBLE_INSUFFICIENT_HISTORY`(`:209-212`).
- `apps/batch/tags_stage.py:37-40,76-80,158-162` -- 재사용할 두 관용구: `TagsClient` Protocol(`compute(frame, ticker) -> StrategyResult`)로 계산을 주입 가능하게 만드는 패턴과 `DefaultStrategyClient`, 그리고 **시그널 성립 판정 `len(series) >= 2 and bool(series.iloc[-2])`**. 유니버스 계산도 동일 규칙을 써야 실전과 같은 축이 된다. 종목별 예외 격리·`ineligible_count`/`error_count` 집계 방식(`:136-152`)도 여기가 기준.
- `apps/batch/ohlcv_cache_loader.py:33-36,85,123-140` -- `OhlcvDbClient` Protocol, `SupabaseOhlcvCacheLoader.load_ohlcv(ticker, cutoff) -> pd.DataFrame | OhlcvCacheStatus`, `load_batch(tickers, cutoff) -> dict[str, LoadResult]`(`LoadResult(ticker, status, frame, row_count)`). `trading_day ASC` + `compute_abc` 컬럼 계약을 이미 만족시켜 주므로 프레임 변환을 다시 만들지 않는다.
- `apps/batch/ohlcv_cache.py:154-157,249,320` -- `_validate_tickers`가 `isalnum()`을 요구하므로 **`.KS` 접미사는 반드시 제거**해야 한다. `initialize_new_ticker_history(candidates, provider, repository, cutoff, *, heartbeat=None)`(이미 캐시된 티커는 skip, <120행은 미저장 INELIGIBLE)와 `update_existing_ticker_history(tickers, provider, repository, cutoff, *, heartbeat=None)`를 유니버스 티커로 그대로 호출하면 독립 백필이 성립한다.
- `apps/batch/scheduler.py:234-235` -- 후보 모집단 결합 지점(`tickers = [c.ticker for c in result.selection.candidates]` 뒤 두 호출). **이 스토리는 이 코드를 수정하지 않고**, 유니버스 백필을 호출 가능한 함수로만 제공한다(배선은 5.4).
- `packages/domain/domain/ohlcv_cache.py:12-19` -- `OhlcvCacheStatus{READY, INELIGIBLE_INSUFFICIENT_HISTORY, ERROR}`, `MIN_HISTORY_TRADING_DAYS = 120`. 상태 표현은 새로 만들지 않고 이 enum을 쓴다.
- `tests/fixtures/golden/` -- fixture 규약의 기준: 커밋된 JSON + 곁에 있는 결정론적 생성기(`generate_golden.py`, `build_universe():95`) + drift 테스트(`backtest/tests/test_golden_fixture.py:257 test_recomputed_reference_matches`). Python 모듈 fixture는 쓰지 않는다. `README.md`가 스키마 계약 문서 형식의 선례다.
- `tests/batch/test_ohlcv_cache.py`, `tests/batch/test_tags_stage.py:184`, `tests/batch/test_scheduler.py:127` -- fake gateway/provider 주입 패턴. 유니버스 테스트도 실 API·실 DB 없이 fake로 검증한다.
- `AGENTS.md:23` -- 테스트 명령 `uv run --with pandas --with numpy --with pyarrow --with pytest pytest`. `pyproject.toml`의 `pythonpath = [".", "packages/domain"]`.
- `infra/supabase/migrations/202609091700_create_bias_events.sql:24` -- 이 스토리 산출물의 최종 소비처인 `bias_event_by_source.backtest_universe_signal_count`. 이번 스토리는 쓰지 않는다(5.3/5.4).
- `tools/epic-path-manifests/epic-5.txt` -- 신규 경로를 여기에 추가해야 epic 범위 게이트·회고 귀속이 성립한다.

## Tasks & Acceptance

**Execution:**
- `tests/fixtures/backtest_universe.json` -- 실측 유니버스 104종목을 `{"source_of_truth": "backtest/data/raw/*_KS.parquet", "count": 104, "tickers": [{"code": "000070", "yahoo_ticker": "000070.KS"}, ...]}` 형태의 커밋 fixture로 승격한다(코드 오름차순) -- 운영 배치가 `yfinance`/parquet 없이 유니버스를 import할 수 있게 한다.
- `tests/fixtures/generate_backtest_universe.py` -- `list_tickers()`에서 fixture를 결정론적으로 재생성하는 생성기를 둔다 -- golden fixture 규약과 동일하게 수작업 편집이 아닌 재생성으로 갱신되게 한다.
- `tests/fixtures/BACKTEST_UNIVERSE.md` -- fixture 스키마 계약과 "선언 108 vs 실측 104" 차이(및 누락 4종목)를 명시 기록한다 -- 숫자 불일치가 조용한 오해로 남지 않게 한다.
- `apps/batch/backtest_universe.py` -- fixture를 읽어 6자리 코드 리스트를 반환하는 로더(`load_backtest_universe()`)를 둔다. 코드 형식(6자리 숫자)·중복·개수 일관성을 로드 시점에 검증한다 -- 운영 경로가 백테스트 모듈에 의존하지 않게 한다.
- `apps/batch/universe_signal.py` -- (a) `backfill_universe_ohlcv(...)`: 유니버스 티커로 `initialize_new_ticker_history` + `update_existing_ticker_history`를 후보 멤버십과 무관하게 호출하고 종목별 결과를 집계한다. (b) `compute_universe_signals(ohlcv_loader, tickers, trading_day, *, strategy_client=None, heartbeat=None) -> UniverseSignalResult`: `compute_abc`로 전략 A~F별 시그널 종목 집합(정렬)과 `ready/ineligible/error` 카운트를 산출한다 -- Story 5.3이 소비할 순수 계산 경계를 만든다.
- `tests/batch/test_backtest_universe.py` -- fixture drift 테스트: fixture 티커 집합이 `list_tickers()`와 정확히 일치하고, `fetch_kospi200.py`의 선언 목록(정적 파싱으로 추출)의 부분집합이며, 문서에 적힌 누락 4종목이 실제 차집합과 일치하는지 검증한다 -- 원본과 값이 어긋나면 CI가 막는다.
- `tests/batch/test_universe_signal.py` -- I/O 매트릭스 전 케이스(정상/이력부족/로드에러/계산에러/독립백필/티커정규화/재현성)를 fake loader·fake provider·fake repository로 검증한다 -- 실 API·실 DB 없이 회귀망을 만든다.
- `tools/epic-path-manifests/epic-5.txt` -- 이 스토리의 신규 경로와 spec 파일을 추가한다 -- epic 범위 게이트를 유지한다.

**Acceptance Criteria:**
- Given fixture만 있고 `yfinance`·`backtest.data`가 import 불가한 환경일 때, when `apps.batch.backtest_universe.load_backtest_universe()`를 호출하면, then 104개 6자리 코드가 오름차순으로 반환된다.
- Given 유니버스 종목이 후보 모집단에 하나도 포함되지 않았을 때, when 유니버스 백필을 실행하면, then 후보 멤버십과 무관하게 그 종목들의 `daily_ohlcv` 적재/갱신이 시도되고 종목별 결과가 반환된다.
- Given 유니버스 전원의 일봉이 120거래일 이상 캐시된 임의 거래일일 때, when 유니버스 시그널 계산을 실행하면, then 전략 A~F 6개 키 각각에 대해 D-1 확정봉 기준 시그널 종목 집합이 산출되고 `ineligible` 카운트가 0이다.
- Given 일봉 원천을 확인할 때, when 계산 경로를 추적하면, then 프레임이 실전 태깅과 동일한 `daily_ohlcv` 로더에서 나오고 시그널이 `compute_abc`만으로 계산됨이 코드와 fixture 계약 문서로 확인된다.
- Given 동일한 캐시 상태와 거래일일 때, when 계산을 두 번 실행하면, then 전략별 종목 집합이 완전히 동일하다.
- Given 저장소 상태를 확인할 때, when `bias_events`/`bias_event_by_source`를 조회하면, then 이 스토리 코드가 쓴 행이 없다(적재는 5.4 범위).
- Given 테스트를 실행할 때, when `uv run --with pandas --with numpy --with pyarrow --with pytest pytest`를 돌리면, then 신규 테스트를 포함해 전부 통과하고 기존 `backtest/` 커널·골든 픽스처 테스트가 회귀하지 않는다.

## Spec Change Log

## Review Triage Log

### 2026-09-10 — Review pass
- intent_gap: 0
- bad_spec: 0
- patch: 9: (high 0, medium 5, low 4)
- defer: 2: (high 0, medium 1, low 1)
- dismissed:
  - 첫 실행에 유니버스 티커당 `fetch_range`가 추가로 ~104회 나간다 — `update_existing_ticker_history`의 `last_trading_day >= cutoff` 가드가 정상 거래일에는 재조회를 막으므로 주장한 호출 폭증 경로가 없다(초기 적재 결과가 증분 결과로 덮이는 별개 결함은 P2로 수정).
  - `load_ohlcv`가 `OhlcvCacheStatus.READY` 센티넬을 반환하면 ERROR로 오분류된다 — `SupabaseOhlcvCacheLoader.load_ohlcv`는 DataFrame 또는 `INELIGIBLE_INSUFFICIENT_HISTORY`/`ERROR`만 반환하고 READY를 반환하는 경로가 없다.
  - READY 결과의 `signals`에 전략 키가 없으면 무신호와 구분되지 않는다 — `compute_abc`는 성공 경로에서 A~F 6키를 항상 채우므로 키 누락 상태가 발생하지 않는다.
  - `normalize_ticker` 예외가 종목 단위 격리 원칙을 깨고 배치 전체를 중단시킨다 — intent-contract I/O 매트릭스가 "정규화 불가 시 fixture 로드 시점 예외"로 명시한 의도된 동작이다.
  - `.KS` 아닌 접미사(`005930.KQ`)가 조용히 허용된다 — 6자리 코드로 정규화되고 운영 표현은 코드뿐이라 결과 집합이 동일하다.
  - `trading_day`에 휴장일·미래일 검증이 없다 — 에픽이 "임의 거래일"을 요구하고 거래일 권위는 `logical_run_key`(Story 5.4)에 있다.
  - `frozen=True`가 얕아 소비자가 결과를 변형할 수 있고 `results`가 매 접근마다 재계산된다 — 실제 변형 소비자가 없고 유니버스 104종목 규모에서 성능 영향이 없다(cosmetic).
  - 생성기에 `--check` 모드가 없어 CI가 fixture 재생성 동등성을 증명하지 못한다 — drift 테스트가 `fixture == list_tickers()`를 직접 강제해 동일한 보장을 이미 제공한다.
  - Story 5.4용 publishable 판정 임계값·health 신호가 없다 — 편향 지표 발행 판정은 Story 5.3/5.4의 AC이며 이 변경이 유발한 결함이 아니다.
  - 스프린트 동기화와 git 커밋이 안 됐다 — 이 워크플로우 Finalize 단계의 절차이며 코드 결함이 아니다.
  - 운영 배치 배선(`scheduler.py`)과 e2e가 없어 AC4의 "방지한다"가 실증되지 않았다 — close 배치 배선은 Story 5.4의 AC가 명시적으로 소유한다. 다만 실증 자체는 유효한 지적이므로 운영 Supabase 실측으로 대체 확인했다(아래 Auto Run Result).
- addressed_findings:
  - `[medium]` `[patch]` P1 전이적 import 주장 부정확 + 가드 테스트 공허 — `universe_signal.py`가 `strategy_api → combine_strategies:17`을 경유해 `backtest.data.loader`를 전이 import함을 확인. 문서·docstring을 실제 보장(yfinance 미의존/parquet 미독/fixture 단일 원천/직접 import 없음)으로 정정하고, 가드 테스트를 모듈별로 분리해 서브프로세스에서 실제 도달 집합을 검증.
  - `[medium]` `[patch]` P2 증분 패스가 갓 초기화된 티커를 덮어 row_count를 0으로 만들고 불필요한 LS 재조회 유발 — 증분 패스를 이전부터 캐시된 티커로 한정. fake repository를 stateful로 바꿔 두 패스 상호작용을 실제로 관측.
  - `[medium]` `[patch]` P3 버킷 합계가 universe_size와 어긋날 수 있음 — 어느 패스에도 없는 티커를 명시적 `ERROR`로 드러내고 `ready+ineligible+error == universe_size` 불변식을 양쪽 결과에 테스트로 고정.
  - `[medium]` `[patch]` P4 확정 시그널 봉 날짜 미노출로 뒤처진 캐시가 다른 날로 비교됨 — `signal_dates`/`latest_signal_date`/`stale_signal_date_tickers` 노출. **초기 수정의 판정 기준(요청 거래일 일치)이 잘못됨을 운영 실측으로 발견해 재수정**: 확정봉은 정의상 요청 거래일의 직전 거래일이라 정상 종목 104개 전부가 stale로 표시됐다. 기준선을 "유니버스가 도달한 최신 확정봉"으로 바꿔 재확인(stale=[]).
  - `[medium]` `[patch]` P5 `adjustment_flags` 어서션 무효(`== []`만 단정, fake가 flag를 만들지 않아 필드를 지워도 통과) — `pricechk` 행과 ±30% 초과 갭 케이스로 ticker/date까지 검증. 백필 heartbeat 호출 횟수도 고정.
  - `[low]` `[patch]` P6 실 커널로 비어있지 않은 시그널을 내는 테스트 없음 — golden fixture 실데이터로 실 `compute_abc`를 돌려 `iloc[-2]`(True)/`iloc[-1]`(False) 구분을 검증.
  - `[low]` `[patch]` P7 drift 대조가 parquet 부재 시 skip으로 무력화 + 선언 목록 정규식 파싱 — skip을 실패로 바꾸고 `_declared_codes()`를 `KOSPI200…` 대입식만 읽는 AST 파싱으로 교체.
  - `[low]` `[patch]` P8 `STRATEGY_KEYS` 중복 상수로 신규 전략이 조용히 누락될 수 있음 — `backtest.strategy_api._STRATEGY_KEYS`에서 파생 + 동일성 테스트.
  - `[low]` `[patch]` P9 빈 유니버스 경로 무테스트 / `lru_cache` 탈출구 없음 / fake가 운영 검증기 규칙을 재구현 — 각각 테스트 추가, `clear_universe_cache()` 공개, 운영 `_validate_tickers` 직접 호출로 교체.

## Design Notes

**"104종목"의 정체와 fixture 권위 선택.** 후보가 셋이다 — `fetch_kospi200.fetch_stock_list()`(선언 108), `loader.list_tickers()`(실측 104), `generate_golden.build_universe(day)`(120일 게이트 통과 98). 에픽이 말하는 104는 **실측 104와 정확히 일치**하고(직접 확인), 백테스트가 실제로 계산한 대상도 이 집합이므로(`screen_abc`가 `load_all()`을 쓴다) fixture 권위는 `list_tickers()`다. 98은 특정 거래일 파생값이므로 fixture가 아니라 런타임 게이트로 남는다. AC의 "원본 스크립트와 값이 어긋나지 않음"은 "fixture ⊆ 선언 목록 + 차집합이 문서에 적힌 4종목과 일치"로 검증한다 — 선언 목록과의 완전 일치를 요구하면 다운로드 실패 4종목 때문에 항상 실패한다.

**`.KS` 접미사.** fixture가 두 표현을 함께 담고 운영 경로는 `code`만 쓴다. `SupabaseOhlcvCacheRepository._validate_tickers`가 `isalnum()`을 강제하므로 `.KS`가 새면 적재 전체가 거부된다.

**시그널 성립 봉.** `compute_abc`는 전 구간 마스크를 주고 어느 봉을 볼지는 호출자가 정한다. 운영 태깅이 `iloc[-2]`(D-1 확정봉)를 쓰므로 유니버스도 같아야 한다 — `iloc[-1]`을 쓰면 편향 지표의 두 집합이 서로 다른 날을 비교하게 된다.

## Verification

**Commands:**
- `uv run --with pandas --with numpy --with pyarrow --with pytest pytest tests/batch/test_backtest_universe.py tests/batch/test_universe_signal.py` -- expected: 신규 테스트 전부 통과
- `uv run --with pandas --with numpy --with pyarrow --with pytest pytest` -- expected: 전체 스위트 통과(기존 커널·골든 픽스처 회귀 없음)
- `python tools/check_epic_scope.py --epic 5 --range d236901..HEAD` -- expected: 범위 이탈 경로 없음
- `python tools/check_sprint_status.py` -- expected: 통과

## Auto Run Result

Status: done

### 구현 요약

백테스트 유니버스(104종목)를 운영 배치가 참조할 수 있는 버전 고정 JSON fixture로 승격하고, 후보 모집단 멤버십과 무관한 `daily_ohlcv` 독립 백필과 `compute_abc` 단일 진입점 기반 유니버스 시그널 계산 경계를 만들었다. `bias_events` 적재·close 배치 배선·migration은 Story 5.3/5.4 몫으로 남겼다(스펙 Never).

"104종목"의 권위는 `backtest/data/raw/*_KS.parquet` 실측(= `loader.list_tickers()`)이며 에픽의 숫자와 정확히 일치한다. `fetch_kospi200.py`의 선언 목록은 108종목이고 차이 4종목(`000060`/`003410`/`012270`/`012510`)은 다운로드 실패분으로, drift 테스트가 `fixture ⊆ 선언 목록` + `차집합 == 문서의 4종목`으로 고정한다.

### 변경 파일

- `tests/fixtures/backtest_universe.json` — 유니버스 104종목 fixture(`code` + `yahoo_ticker`, 코드 오름차순).
- `tests/fixtures/generate_backtest_universe.py` — `list_tickers()`에서 fixture를 결정론적으로 재생성하는 생성기(수작업 편집 금지).
- `tests/fixtures/BACKTEST_UNIVERSE.md` — fixture 스키마 계약, "선언 108 vs 실측 104 vs 골든 98" 대조표, 모듈별 의존성 보장, 확정봉·뒤처짐 판정 근거, 재생성 절차.
- `apps/batch/backtest_universe.py` — fixture 로더(`load_backtest_universe`/`load_backtest_universe_tickers`/`normalize_ticker`/`clear_universe_cache`). `backtest` 패키지 전면 미의존.
- `apps/batch/universe_signal.py` — `backfill_universe_ohlcv`(Epic 2 적재 함수 2개 재사용, 후보 멤버십 무관)와 `compute_universe_signals`(`compute_abc`만 사용, `iloc[-2]` D-1 확정봉, 종목 단위 격리, 결정론적 정렬 결과).
- `tests/batch/test_backtest_universe.py` — fixture 계약·drift·의존성 격리 테스트 25건.
- `tests/batch/test_universe_signal.py` — I/O 매트릭스 전 케이스 + 불변식·실 커널·라이브 규약 테스트 40건.
- `tools/epic-path-manifests/epic-5.txt` — 신규 경로 8개 + 이 spec 추가.

### 리뷰 결과

- 리뷰 레이어 4종(blind-hunter, edge-case-hunter, verification-gap, intent-alignment) 실행.
- 패치 적용 9건: medium 5 / low 4 (P1~P9, 상세는 Review Triage Log).
- deferred 2건: AGENTS.md 테스트 명령의 pyyaml 누락(medium, 선행 결함), 운영 코드가 `tests/` fixture를 읽는 패키징 경계(low).
- dismissed 11건(각 사유는 Review Triage Log).
- Follow-up review 권고: **true** (패치 severity 기준 high 0, medium 5, low 4 → 3×5 + 1×4 = 19 ≥ 5).

### 검증

- `uv run --with pandas --with numpy --with pyarrow --with pytest pytest tests/batch/test_backtest_universe.py tests/batch/test_universe_signal.py -q` → 65 passed.
- `uv run --with pandas --with numpy --with pyarrow --with pyyaml --with pytest pytest -q` → **661 passed** (기준선 645 + 신규 16). AGENTS.md의 명령(pyyaml 없음)으로는 무관한 선행 결함 3건이 실패하며 deferred에 기록했다.
- `python tools/check_epic_scope.py --epic 5` → 변경 경로 전건이 epic-5 manifest 안에 있음.
- `python tools/check_sprint_status.py` → 통과.
- I/O 매트릭스 감사: 9개 행(HAPPY_PATH/SHORT_HISTORY/LOAD_ERROR/COMPUTE_ERROR/BACKFILL_INDEPENDENT/BACKFILL_TICKER_FORM/FIXTURE_DRIFT/REPRODUCIBLE) 전부 실행·통과한 테스트로 커버.
- **운영 Supabase 실측(2026-09-09 거래일).** UI 표면이 없는 계산 경계라 Playwright e2e는 해당하지 않으므로, 운영 `daily_ohlcv`에 직접 붙여 확인했다.
  - 유니버스 104종목 계산: `ready=0, ineligible=104` — 후보 모집단 종목만 적재돼 있어 유니버스 전체가 `INELIGIBLE_INSUFFICIENT_HISTORY`로 제외되는 상태를 **실측으로 확인**했다. 이것이 AC4가 막으려는 바로 그 상황이다. 2회 실행 결과가 동일해 재현성도 확인.
  - 후보 모집단에 없던 유니버스 2종목(`000070`/`000150`)을 `.KS` 표현으로 넘겨 독립 백필: `ineligible=2 → ready=2`, 각 120행 적재, 이후 계산에서 확정봉 `2026-09-08`이 정상 산출. 재실행 시 초기 적재가 건너뛰어지고 증분이 `rows=0`으로 끝나 멱등성과 P2 수정(중복 재조회 제거)도 확인.
  - 이 실측 과정에서 P4 초기 수정의 판정 기준 오류(정상 종목 전부가 stale로 표시됨)를 발견해 기준선을 최신 확정봉으로 재수정했고, 재실행에서 `stale=[]`를 확인했다.

### 잔여 리스크

- 유니버스 전체(104종목) 백필은 아직 운영에서 수행되지 않았다. 배선이 Story 5.4의 AC이고, LS `t8410`이 TR당 1req/s 직렬이라 콜드 스타트에 약 104초 + lease 연장이 필요하다. 5.4가 배선하기 전까지 편향 지표의 유니버스 측은 여전히 비어 있다.
- `STRATEGY_KEYS`가 `backtest.strategy_api._STRATEGY_KEYS`(비공개 이름)에서 파생된다. 단일 원천 유지가 중복 열거보다 안전하다고 판단했고 동일성 테스트로 고정했지만, 공개 별칭이 생기면 그쪽으로 옮기는 편이 낫다.
- fixture는 현재 디스크의 parquet 104개 스냅샷이다. `backtest/data/raw`가 바뀌면 생성기 재실행 + 문서의 4종목 표 + 테스트의 `MISSING_FROM_DISK`를 함께 갱신해야 하고, drift 테스트가 이를 강제한다.
