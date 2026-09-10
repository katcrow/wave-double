# 백테스트 유니버스 fixture (Story 5.2)

편향 지표(FR-10)는 임의 거래일에 대해 **"백테스트 유니버스 ∩ 전략 시그널"** 을 후보
모집단 시그널과 대조한다. 그런데 유니버스 목록은 원래 `yfinance`를 import하는 백테스트
전용 스크립트와 `backtest/data/raw/*.parquet` 디스크 상태에만 존재해 운영 배치가 참조할
수 없었다. `backtest_universe.json`은 그 목록을 **버전 고정 fixture로 승격**한 것이고,
운영 경로는 `apps.batch.backtest_universe.load_backtest_universe()`로만 이 값을 읽는다.

## 운영 경로가 실제로 보장하는 것 (정정)

초기 서술("운영 코드는 `yfinance`/`backtest.data.*`를 import하지 않는다")은 **부정확했다**.
실제 보장은 다음과 같다.

| 보장 | `apps/batch/backtest_universe.py` | `apps/batch/universe_signal.py` |
|---|---|---|
| `yfinance` 미의존 | 예 | 예 |
| parquet 파일을 읽지 않음 | 예 | 예 |
| 유니버스 목록은 fixture JSON에서만 옴 | 예 | 예(이 모듈 경유) |
| `backtest` 패키지 전면 미의존 | **예**(테스트가 서브프로세스로 고정) | 아니오 — 아래 참조 |

`universe_signal.py`는 AD-5 공유 진입점 `backtest.strategy_api`를 import하고, 그 경유로
`backtest.indicator_opt.combine_strategies`(`:17 from ..data.loader import load_all`)가
**`backtest.data.loader`를 전이적으로 import**한다. 즉 운영 경로에 `backtest.data.loader`
모듈이 들어온다. 다만 `backtest/data/loader.py`는 **import 시점에 parquet을 읽지 않으므로**
(경로 상수 정의뿐) 부작용이 없고, 기존 `apps/batch/tags_stage.py`도 이미 동일한 조건이다
(pre-existing). 따라서 `universe_signal.py`에 대한 정확한 서술은 "`backtest.data.*`를
**직접** import하지 않으며, 전이 import에도 import 시점 부작용이 없다"다.

이 구분은 `tests/batch/test_backtest_universe.py`가 그대로 고정한다 —
`backtest_universe.py`는 `backtest.*` 전면 차단 서브프로세스에서 동작해야 하고,
`universe_signal.py`는 `yfinance`만 차단한 서브프로세스에서 import되어야 하며
`backtest.data`를 직접 import하지 않아야 한다.

## 스키마 계약 — `backtest_universe.json`

```json
{
  "source_of_truth": "backtest/data/raw/*_KS.parquet",
  "count": 104,
  "tickers": [
    { "code": "000070", "yahoo_ticker": "000070.KS" }
  ]
}
```

- `source_of_truth` — 권위 원천의 고정 문자열. 변경 시 이 문서와 drift 테스트를 함께 갱신한다.
- `count` — `tickers` 길이와 **정확히 일치**해야 한다(로드 시점 검증).
- `tickers` — `code` 오름차순. 중복 금지.
  - `code` — 운영이 쓰는 **6자리 숫자 종목코드**. `daily_ohlcv.ticker`, LS `t8410` `shcode`,
    `SupabaseOhlcvCacheRepository._validate_tickers`(`isalnum()` 요구)와 같은 표현이다.
  - `yahoo_ticker` — 백테스트가 쓰는 `.KS` 접미사 표현. **운영 경로는 이 값을 쓰지 않는다.**
    `.KS`가 적재 경로로 새면 `_validate_tickers`가 `isalnum()` 위반으로 배치 전체를 거부한다.

## "선언 108 vs 실측 104"

유니버스 후보가 셋이고 숫자가 서로 다르다. 조용한 오해로 남지 않게 명시한다.

| 원천 | 개수 | 성격 |
|---|---|---|
| `backtest/data/fetch_kospi200.py`의 `fetch_stock_list()` | **108** | 선언 목록(`sorted(set(...))` 후 unique). 다운로드를 시도할 대상. |
| `backtest/data/loader.py`의 `list_tickers()` | **104** | 실측. 실제로 parquet이 존재하고 백테스트가 계산한 대상. **fixture 권위.** |
| `tests/fixtures/golden/generate_golden.py`의 `build_universe(day)` | 98 | 특정 거래일까지 120거래일 이상인 파생 집합. fixture가 아니라 런타임 게이트. |

에픽이 말하는 "104종목"은 실측 104와 정확히 일치하고, `screen_abc`가 `load_all()`(=디스크
유니버스)로 계산하므로 **fixture 권위는 `list_tickers()`** 다.

선언 108 − 실측 104 = **다운로드 실패 4종목**:

| 종목코드 | 상태 |
|---|---|
| `000060` | 선언에는 있으나 `backtest/data/raw`에 parquet 없음(수집 실패) |
| `003410` | 동일 |
| `012270` | 동일 |
| `012510` | 동일 |

이 4종목은 백테스트가 실제로 계산한 적이 없으므로 유니버스에 포함하면 편향 지표의 두 집합이
서로 다른 모집단을 비교하게 된다. 따라서 fixture는 선언 목록과의 **완전 일치를 요구하지
않고**, `fixture ⊆ 선언 목록` + `차집합 == 위 4종목`으로 drift를 검증한다
(`tests/batch/test_backtest_universe.py`). `fetch_kospi200.py`는 모듈 최상단에서 `yfinance`를
import하므로 테스트도 이 모듈을 import하지 않고 **정적 파싱**으로만 대조한다.

## 일봉 원천 — 실전과 같은 축임의 근거

유니버스 시그널 계산(`apps/batch/universe_signal.py`)은

- 프레임을 Epic 2의 **`daily_ohlcv`** 로더(`OhlcvDbClient` = `SupabaseOhlcvCacheLoader`)에서 받고,
  이는 운영 태깅(`apps/batch/tags_stage.py`)이 쓰는 것과 **동일한 로더·동일한 테이블**이다.
- 시그널은 **`backtest.strategy_api.compute_abc`만으로** 계산한다(AD-5 공유 진입점).
  `build_signals`를 직접 호출하지 않고 `screen_abc.py`/parquet 경로를 쓰지 않는다.
- 시그널 성립 봉은 운영 태깅과 같은 **`signals[key].iloc[-2]`(D-1 확정봉)** 이다.
  `iloc[-1]`을 쓰면 편향 지표의 두 집합이 서로 다른 날을 비교하게 된다.
- 확정봉은 정의상 요청 거래일이 아니라 **그 직전 거래일**이다. 따라서 뒤처진 캐시 판정은
  요청 거래일과의 일치가 아니라 **유니버스가 도달한 최신 확정봉**(`latest_signal_date`)을
  기준선으로 삼는다(`stale_signal_date_tickers`). 요청 거래일 기준으로 판정하면 정상
  종목까지 전부 뒤처진 것으로 표시된다 — 운영 실측(2026-09-09)에서 확인한 사실이다.

유니버스 종목은 후보 모집단 멤버십과 무관하게 `backfill_universe_ohlcv()`로 독립 백필한다
(`initialize_new_ticker_history` + `update_existing_ticker_history` 재사용). 이 백필이 없으면
유니버스 종목 대부분이 `INELIGIBLE_INSUFFICIENT_HISTORY`로 제외되어 지표가 무의미해진다.

## 재생성 방법

fixture는 고정이며 테스트가 자동 재생성하지 않는다. **수작업 편집 금지** — 생성기로만 갱신한다.

```
uv run --with pandas --with numpy --with pyarrow \
  python tests/fixtures/generate_backtest_universe.py
```

`backtest/data/raw`의 parquet 집합이 바뀌면 생성기를 다시 돌리고, 위 "다운로드 실패 4종목"
표와 `tests/batch/test_backtest_universe.py`의 `MISSING_FROM_DISK`를 함께 갱신한다.
