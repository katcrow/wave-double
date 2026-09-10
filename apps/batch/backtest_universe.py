"""Story 5.2: 백테스트 유니버스 fixture 로더.

편향 지표(FR-10)의 "백테스트 유니버스 ∩ 전략 시그널"을 운영 배치가 계산할 수 있어야
하므로, 유니버스 목록을 버전 고정 fixture(``tests/fixtures/backtest_universe.json``)에서
읽는다. 이 모듈이 실제로 보장하는 것은 다음 세 가지다.

- ``yfinance``에 의존하지 않는다.
- parquet 파일을 읽지 않는다.
- 유니버스 목록은 fixture JSON에서만 온다(``backtest`` 패키지 전면 미의존 --
  ``backtest.*``가 import 불가한 환경에서도 동작한다. 테스트가 서브프로세스로 고정).

fixture 스키마 계약과 "선언 108 vs 실측 104" 차이는
``tests/fixtures/BACKTEST_UNIVERSE.md``에 기록되어 있고, 원본(``list_tickers()``)과의
drift는 ``tests/batch/test_backtest_universe.py``가 막는다.
"""

from __future__ import annotations

import json
from dataclasses import dataclass
from functools import lru_cache
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[2]
FIXTURE_PATH = _REPO_ROOT / "tests" / "fixtures" / "backtest_universe.json"
EXPECTED_SOURCE_OF_TRUTH = "backtest/data/raw/*_KS.parquet"


class BacktestUniverseFixtureError(ValueError):
    """fixture가 스키마 계약을 위반했을 때 로드 시점에 던진다."""


@dataclass(frozen=True)
class UniverseTicker:
    """유니버스 한 종목의 두 표현.

    ``code``는 운영(``daily_ohlcv.ticker``/LS ``shcode``)이 쓰는 6자리 숫자 코드,
    ``yahoo_ticker``는 백테스트가 쓰는 ``.KS`` 접미사 표현이다. 운영 경로는 ``code``만
    쓴다 -- ``SupabaseOhlcvCacheRepository._validate_tickers``가 ``isalnum()``을
    강제하므로 ``.KS``가 새면 적재 전체가 거부된다.
    """

    code: str
    yahoo_ticker: str


def normalize_ticker(ticker: str) -> str:
    """``'005930.KS'``/``'005930'`` -> ``'005930'``. 6자리 숫자가 아니면 예외."""
    code = str(ticker).strip().split(".", 1)[0]
    if len(code) != 6 or not code.isdigit():
        raise BacktestUniverseFixtureError(
            f"6자리 숫자 종목코드로 정규화할 수 없습니다: {ticker!r}"
        )
    return code


def _load_payload(path: Path) -> dict:
    try:
        raw = path.read_text(encoding="utf-8")
    except OSError as exc:
        raise BacktestUniverseFixtureError(
            f"유니버스 fixture를 읽을 수 없습니다: {path}"
        ) from exc
    try:
        payload = json.loads(raw)
    except json.JSONDecodeError as exc:
        raise BacktestUniverseFixtureError(
            f"유니버스 fixture가 올바른 JSON이 아닙니다: {path}"
        ) from exc
    if not isinstance(payload, dict):
        raise BacktestUniverseFixtureError("유니버스 fixture 최상위는 object여야 합니다")
    return payload


def _parse(payload: dict) -> list[UniverseTicker]:
    source = payload.get("source_of_truth")
    if source != EXPECTED_SOURCE_OF_TRUTH:
        raise BacktestUniverseFixtureError(
            f"source_of_truth 불일치: {source!r} != {EXPECTED_SOURCE_OF_TRUTH!r}"
        )
    entries = payload.get("tickers")
    if not isinstance(entries, list) or not entries:
        raise BacktestUniverseFixtureError("tickers는 비어 있지 않은 list여야 합니다")

    tickers: list[UniverseTicker] = []
    seen: set[str] = set()
    for entry in entries:
        if not isinstance(entry, dict):
            raise BacktestUniverseFixtureError(f"tickers 항목이 object가 아닙니다: {entry!r}")
        code = normalize_ticker(entry.get("code", ""))
        yahoo_ticker = str(entry.get("yahoo_ticker", ""))
        if normalize_ticker(yahoo_ticker) != code:
            raise BacktestUniverseFixtureError(
                f"code/yahoo_ticker 불일치: {code!r} vs {yahoo_ticker!r}"
            )
        if code in seen:
            raise BacktestUniverseFixtureError(f"중복 종목코드: {code}")
        seen.add(code)
        tickers.append(UniverseTicker(code=code, yahoo_ticker=yahoo_ticker))

    declared_count = payload.get("count")
    if declared_count != len(tickers):
        raise BacktestUniverseFixtureError(
            f"count 불일치: 선언 {declared_count!r} != 실제 {len(tickers)}"
        )

    codes = [t.code for t in tickers]
    if codes != sorted(codes):
        raise BacktestUniverseFixtureError("tickers는 code 오름차순이어야 합니다")
    return tickers


def load_backtest_universe_tickers(path: Path | str | None = None) -> list[UniverseTicker]:
    """fixture의 두 표현(``code``/``yahoo_ticker``)을 코드 오름차순으로 반환한다.

    ``path=None``(운영 기본값)이면 ``FIXTURE_PATH``를 **프로세스 단위로 캐싱**한다
    (``_cached_tickers``). 같은 프로세스에서 fixture 파일을 다시 생성했다면
    ``clear_universe_cache()``로 캐시를 비워야 새 값이 보인다. 명시적 ``path``를 주면
    캐시를 거치지 않고 매번 파싱한다.
    """
    if path is None:
        return list(_cached_tickers())
    return _parse(_load_payload(Path(path)))


def load_backtest_universe(path: Path | str | None = None) -> list[str]:
    """유니버스 6자리 종목코드를 오름차순으로 반환한다(운영 경로 진입점)."""
    return [t.code for t in load_backtest_universe_tickers(path)]


@lru_cache(maxsize=1)
def _cached_tickers() -> tuple[UniverseTicker, ...]:
    return tuple(_parse(_load_payload(FIXTURE_PATH)))


def clear_universe_cache() -> None:
    """기본 fixture 캐시를 비운다.

    ``_cached_tickers``는 인자가 없는 ``lru_cache``라 파일이 바뀌어도 낡은 값을 계속
    준다. fixture를 재생성한 뒤 같은 프로세스에서 다시 읽어야 할 때(생성기·테스트)
    쓰는 유일한 탈출구다.
    """
    _cached_tickers.cache_clear()


__all__ = [
    "FIXTURE_PATH",
    "EXPECTED_SOURCE_OF_TRUTH",
    "BacktestUniverseFixtureError",
    "UniverseTicker",
    "normalize_ticker",
    "clear_universe_cache",
    "load_backtest_universe",
    "load_backtest_universe_tickers",
]
