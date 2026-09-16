"""Story 5.2: 백테스트 유니버스 일봉 독립 백필 + 유니버스 전략 시그널 계산.

편향 지표(FR-10)는 임의 거래일에 대해 "백테스트 유니버스 ∩ 전략 시그널"을 후보 모집단
시그널과 대조한다. 이 모듈은 그 좌변을 만드는 **순수 계산 경계**이며 Story 5.3(교집합·
차집합·기회누락 산식)과 Story 5.4(``bias_events`` append·stage 배선)가 소비한다.
**이 모듈은 ``bias_events``/``bias_event_by_source``에 쓰지 않는다.**

두 개의 진입점:

- ``backfill_universe_ohlcv`` -- 유니버스 티커의 ``daily_ohlcv``를 **후보 모집단 멤버십과
  무관하게** 독립 적재/증분 갱신한다. Epic 2의 ``initialize_new_ticker_history``/
  ``update_existing_ticker_history``를 그대로 재사용하고, 후보 적재 경로
  (``scheduler.py``의 기존 두 호출)는 건드리지 않는다 -- 유니버스 백필은 별도 호출로만
  더한다(배선은 Story 5.4).
- ``compute_universe_signals`` -- 실전 태깅과 **동일한** ``daily_ohlcv`` 로더에서 프레임을
  받아 ``backtest.strategy_api.compute_abc``만으로 전략 A~H 시그널 종목 집합을 산출한다.
  시그널 성립 봉은 운영 태깅과 같은 ``signals[key].iloc[-1]``(당일 확정봉, 2026-09-16 변경)다.

한 종목의 실패가 나머지를 막지 않고, 종목별 상태(``READY``/
``INELIGIBLE_INSUFFICIENT_HISTORY``/``ERROR``)가 집계로 노출된다. 모든 유니버스 종목은
반드시 세 버킷 중 정확히 하나에 들어간다(``ready+ineligible+error == universe_size``).
같은 (유니버스, 거래일, ``daily_ohlcv`` 내용)에는 정렬된 동일 결과가 나온다.

**의존성 사실(부정확한 주장 정정, review P1).** 이 모듈이 보장하는 것은 (a) ``yfinance``
미의존, (b) parquet 파일을 읽지 않음, (c) 유니버스 목록은 fixture JSON에서만 옴,
(d) ``backtest.data.*``를 **직접** import하지 않음이다. 다만 AD-5 공유 진입점
``backtest.strategy_api``를 경유하면 ``backtest.indicator_opt.combine_strategies``가
``backtest.data.loader``를 **전이적으로** import한다. ``backtest/data/loader.py``는 import
시점에 parquet을 읽지 않으므로(경로 상수 정의뿐) 부작용이 없고, 이는 기존
``apps/batch/tags_stage.py``도 이미 동일한 조건이다. 즉 "운영 코드는 ``backtest.data.*``를
import하지 않는다"는 서술은 사실이 아니며, 정확한 서술은 "직접 import하지 않고 전이
import에도 import 시점 부작용이 없다"다.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date
from typing import Sequence

import pandas as pd

from backtest.strategy_api import _STRATEGY_KEYS
from domain.ohlcv_cache import AdjustmentFlag, OhlcvCacheStatus

from .backtest_universe import load_backtest_universe, normalize_ticker
from .heartbeat import HeartbeatPolicy
from .ohlcv_cache import (
    LsOhlcvCacheProvider,
    OhlcvCacheResult,
    SupabaseOhlcvCacheRepository,
    initialize_new_ticker_history,
    update_existing_ticker_history,
)
from .ohlcv_cache_loader import OhlcvDbClient
from .tags_stage import DefaultStrategyClient, TagsClient, _extract_signal_date

# 단일 원천 파생: 전략 키는 ``compute_abc``가 채우는 키 집합(AD-5)이 권위다. 여기서 다시
# 열거하면 신규 전략이 추가될 때 유니버스 쪽에서 조용히 빠진다(review P8).
STRATEGY_KEYS: tuple[str, ...] = tuple(_STRATEGY_KEYS)


@dataclass(frozen=True)
class UniverseBackfillResult:
    """유니버스 독립 백필의 종목별 결과와 집계."""

    tickers: list[str]
    initialized: dict[str, OhlcvCacheResult] = field(default_factory=dict)
    updated: dict[str, OhlcvCacheResult] = field(default_factory=dict)
    adjustment_flags: list[AdjustmentFlag] = field(default_factory=list)

    @property
    def results(self) -> dict[str, OhlcvCacheResult]:
        """종목별 최종 상태.

        두 패스는 서로 배타적인 티커 집합을 다룬다 -- 이번 실행에서 초기 적재된 티커는
        증분 패스에 넘기지 않으므로(review P2) ``initialized``와 ``updated``의 키가
        겹치지 않는다. 그럼에도 어느 패스에도 결과가 없는 티커가 생길 수 있으므로
        (예: ``existing_tickers``와 ``latest_state``가 불일치) 그 티커는 조용히 사라지지
        않고 명시적 ``ERROR``로 드러낸다 -- ``ready+ineligible+error == universe_size``
        불변식을 구조적으로 보장한다(review P3).
        """
        merged: dict[str, OhlcvCacheResult] = dict(self.initialized)
        merged.update(self.updated)
        for ticker in self.tickers:
            if ticker not in merged:
                merged[ticker] = OhlcvCacheResult(
                    ticker,
                    OhlcvCacheStatus.ERROR,
                    0,
                    "백필 결과 누락: 초기 적재·증분 갱신 어느 패스에도 결과가 없습니다",
                )
        return merged

    def _count(self, status: OhlcvCacheStatus) -> int:
        return sum(1 for r in self.results.values() if r.status is status)

    @property
    def universe_size(self) -> int:
        return len(self.tickers)

    @property
    def ready_count(self) -> int:
        return self._count(OhlcvCacheStatus.READY)

    @property
    def ineligible_count(self) -> int:
        return self._count(OhlcvCacheStatus.INELIGIBLE_INSUFFICIENT_HISTORY)

    @property
    def error_count(self) -> int:
        return self._count(OhlcvCacheStatus.ERROR)


@dataclass(frozen=True)
class UniverseSignalResult:
    """임의 거래일에 대한 유니버스 시그널 계산 결과.

    ``signal_dates``는 종목별로 **실제 확정된 시그널 봉 날짜**(프레임의 ``iloc[-1]``
    인덱스, 2026-09-16부터 "당일 봉이 최종봉"). ``load_ohlcv``는 ``trading_day`` 이하의
    행을 그대로 주므로, 정상 종목은 ``iloc[-1]``이 ``trading_day``와 같지만 캐시가
    T-10에서 끝난 종목은 그보다 이른 날짜가 나온다. 요청 거래일만 남기면 편향 지표의
    두 집합이 서로 다른 날을 비교하게 되므로(review P4) 종목별 날짜를 그대로 노출한다.
    날짜를 뽑을 수 없는 종목(프레임이 비어 있는 등)은 ``None``이다.

    ``stale_signal_date_tickers``는 **유니버스가 실제로 도달한 최신 확정봉 날짜**
    (``latest_signal_date``)를 기준으로, 그보다 이른(또는 미확인) 종목만 골라낸다 --
    캘린더 조회 없이 "이 종목만 다른 날을 보고 있다"를 정확히 잡는다.
    """

    trading_day: date
    universe_size: int
    strategy_signals: dict[str, list[str]]
    ready_tickers: list[str] = field(default_factory=list)
    ineligible_tickers: list[str] = field(default_factory=list)
    error_tickers: list[str] = field(default_factory=list)
    signal_dates: dict[str, date | None] = field(default_factory=dict)

    @property
    def latest_signal_date(self) -> date | None:
        """유니버스가 실제로 도달한 최신 확정봉 날짜(뒤처짐 판정의 기준선)."""
        observed = [d for d in self.signal_dates.values() if d is not None]
        return max(observed) if observed else None

    @property
    def stale_signal_date_tickers(self) -> list[str]:
        """확정봉이 ``latest_signal_date``보다 이른(또는 미확인) 종목들.

        Story 5.3은 이 목록으로 "같은 날을 비교하고 있는가"를 확인한다. 비어 있으면
        모든 종목이 같은 확정봉을 보고 있다는 뜻이다.
        """
        baseline = self.latest_signal_date
        if baseline is None:
            return sorted(self.signal_dates)
        return sorted(
            ticker
            for ticker, signal_day in self.signal_dates.items()
            if signal_day is None or signal_day < baseline
        )

    @property
    def ready_count(self) -> int:
        return len(self.ready_tickers)

    @property
    def ineligible_count(self) -> int:
        return len(self.ineligible_tickers)

    @property
    def error_count(self) -> int:
        return len(self.error_tickers)

    def signal_count(self, strategy: str) -> int:
        return len(self.strategy_signals.get(strategy, []))


def _normalized_universe(tickers: Sequence[str] | None) -> list[str]:
    """fixture 기본값 또는 주어진 목록을 6자리 코드로 정규화(중복 제거·정렬)한다.

    fixture는 ``.KS`` 티커도 함께 보관하므로 호출자가 그 표현을 넘길 수 있다.
    ``SupabaseOhlcvCacheRepository._validate_tickers``가 ``isalnum()``을 강제하므로
    ``.KS``는 여기서 반드시 제거된다(정규화 불가면 예외).
    """
    source = load_backtest_universe() if tickers is None else list(tickers)
    return sorted({normalize_ticker(t) for t in source})


def backfill_universe_ohlcv(
    provider: LsOhlcvCacheProvider,
    repository: SupabaseOhlcvCacheRepository,
    cutoff: date,
    *,
    tickers: Sequence[str] | None = None,
    heartbeat: HeartbeatPolicy | None = None,
) -> UniverseBackfillResult:
    """유니버스 종목의 ``daily_ohlcv``를 후보 모집단 멤버십과 무관하게 백필한다.

    ``initialize_new_ticker_history``(미캐시 종목 전체 이력)와
    ``update_existing_ticker_history``(캐시된 종목 증분)를 순서대로 호출한다. 두 함수 모두
    종목 단위 부분 성공을 허용하므로 한 종목의 실패가 나머지를 막지 않는다.

    증분 패스에는 **이번 실행에서 초기 적재하지 않은**(=이전부터 캐시돼 있던) 티커만
    넘긴다. 운영 ``latest_state``는 실 테이블을 조회하므로 방금 적재한 티커가 증분 패스에도
    잡히는데, 그러면 (1) 초기 적재의 실제 ``row_count``가 증분의 ``READY row_count=0``으로
    덮이고 (2) 저장 이력이 cutoff보다 이르면 티커당 불필요한 ``fetch_range``가 한 번 더
    나간다. 첫 실행이 흔한 경우이므로 여기서 잘라낸다(review P2).
    """
    universe = _normalized_universe(tickers)
    if not universe:
        return UniverseBackfillResult(tickers=[])

    initialized = initialize_new_ticker_history(
        universe, provider, repository, cutoff, heartbeat=heartbeat
    )
    previously_cached = [t for t in universe if t not in initialized]
    incremental = update_existing_ticker_history(
        previously_cached, provider, repository, cutoff, heartbeat=heartbeat
    )
    return UniverseBackfillResult(
        tickers=universe,
        initialized=dict(initialized),
        updated=dict(incremental.results),
        adjustment_flags=list(incremental.adjustment_flags),
    )


def compute_universe_signals(
    ohlcv_loader: OhlcvDbClient,
    tickers: Sequence[str] | None,
    trading_day: date,
    *,
    strategy_client: TagsClient | None = None,
    heartbeat: HeartbeatPolicy | None = None,
) -> UniverseSignalResult:
    """유니버스 전략 A~F 시그널 종목 집합과 종목별 상태 집계를 산출한다.

    프레임 원천은 실전 태깅과 동일한 ``daily_ohlcv`` 로더이고, 시그널은
    ``compute_abc``(``DefaultStrategyClient``, ``exclude_terminal_bar=False``)만으로
    계산한다. 시그널 성립 판정은 운영 태깅과 동일한
    ``len(series) >= 1 and bool(series.iloc[-1])``(당일 확정봉 — Neo 확인, 2026-09-16)다.

    모든 유니버스 종목은 ready/ineligible/error 중 정확히 하나에 들어가며(루프의 모든
    분기가 한 버킷에 append한 뒤 종료), READY 종목은 ``signal_dates``에 확정 봉 날짜를
    남긴다.
    """
    client = strategy_client or DefaultStrategyClient()
    universe = _normalized_universe(tickers)

    signals: dict[str, list[str]] = {key: [] for key in STRATEGY_KEYS}
    ready: list[str] = []
    ineligible: list[str] = []
    errors: list[str] = []
    signal_dates: dict[str, date | None] = {}

    for ticker in universe:
        if heartbeat is not None:
            heartbeat.beat()

        try:
            load_result = ohlcv_loader.load_ohlcv(ticker, trading_day)
        except Exception:
            errors.append(ticker)
            continue

        if not isinstance(load_result, pd.DataFrame):
            if load_result is OhlcvCacheStatus.INELIGIBLE_INSUFFICIENT_HISTORY:
                ineligible.append(ticker)
            else:
                errors.append(ticker)
            continue

        try:
            result = client.compute(load_result, ticker)
        except Exception:
            errors.append(ticker)
            continue

        if result.status is OhlcvCacheStatus.INELIGIBLE_INSUFFICIENT_HISTORY:
            ineligible.append(ticker)
            continue
        if result.status is OhlcvCacheStatus.ERROR or result.error is not None:
            # 전략 키를 부분 반영하지 않는다 -- 계산 실패 종목은 어느 집합에도 넣지 않는다.
            errors.append(ticker)
            continue

        ready.append(ticker)
        # 운영 태깅(``tags_stage``)과 **같은 추출기**로 종목별 확정 봉 날짜를 남긴다.
        signal_dates[ticker] = _extract_signal_date(load_result)
        for key in STRATEGY_KEYS:
            series = result.signals.get(key)
            if series is not None and len(series) >= 1 and bool(series.iloc[-1]):
                signals[key].append(ticker)

    return UniverseSignalResult(
        trading_day=trading_day,
        universe_size=len(universe),
        strategy_signals={key: sorted(values) for key, values in signals.items()},
        ready_tickers=sorted(ready),
        ineligible_tickers=sorted(ineligible),
        error_tickers=sorted(errors),
        signal_dates={t: signal_dates[t] for t in sorted(signal_dates)},
    )


__all__ = [
    "STRATEGY_KEYS",
    "UniverseBackfillResult",
    "UniverseSignalResult",
    "backfill_universe_ohlcv",
    "compute_universe_signals",
]
