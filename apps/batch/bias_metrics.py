"""Story 5.3: 모집단 편향 지표(source별 5개 카운트) 순수 계산 로직.

Story 5.2(``universe_signal``)가 백테스트 유니버스 시그널 집합을, Epic 2 태깅
(``tags_stage``)이 후보 모집단 시그널 집합을 만든다. 이 모듈은 그 둘을 대조해
``bias_event_by_source`` 한 행이 요구하는 5개 카운트를 **source별로** 산출한다.

**이 모듈은 DB에 쓰지 않는다.** ``bias_events``/``bias_event_by_source`` 적재와 stage
배선은 Story 5.4의 몫이고, 여기서는 Supabase 클라이언트를 import하지 않는다.

산식 (``P_s`` = primary source가 s인 published 후보 중 시그널 성립 종목,
``U`` = 유니버스 시그널 종목, ``T_s`` = primary source가 s인 절단 종목 중 시그널 성립 종목)::

    pop_s          = |P_s|
    universe_count = |U|                      # 모든 s에 동일(유니버스에는 source 축이 없다)
    intersection_s = |P_s ∩ U|
    diff_s         = |P_s - U|
    missed_s       = |(U ∪ T_s) - P_s|

``T_s ∩ P_s = ∅``(절단 종목은 published가 아니다)이므로 ``missed_s``는 항상
``universe_count - intersection_s`` 이상이며, 절단분이 유니버스와 겹치면 자동으로 한 번만
세어진다.

카운트는 **전략 A~F 합집합 기준 종목 수**다 -- ``bias_event_by_source``에 전략 축이 없기
때문이다. 전략별 분해는 ``calculation_meta.by_strategy``에만 담는다.

source 도메인은 ``domain.candidate_selection.SOURCE_PRIORITY``에서만 파생하며, 기여가 없는
source도 항상 null-safe 0 행으로 만든다(3행 고정). 반환 직전에 ``bias_event_by_source``의
check 제약 4개를 그대로 코드로 재검증하고, 위반 시 ``BiasMetricsInvariantError``로 중단한다.
"""

from __future__ import annotations

import math
from dataclasses import dataclass, field
from datetime import date
from typing import Any, Iterable, Mapping, Sequence

from domain.candidate_selection import (
    SOURCE_PRIORITY,
    SelectedCandidate,
    SourceContribution,
)

from .backtest_universe import BacktestUniverseFixtureError, normalize_ticker
from .heartbeat import HeartbeatPolicy
from .ohlcv_cache_loader import OhlcvDbClient
from .tags_stage import TagsClient
from .universe_signal import STRATEGY_KEYS, UniverseSignalResult, compute_universe_signals

#: ``bias_event_by_source.source`` check 제약과 동일한 도메인. 재열거하지 않고 파생한다.
BIAS_SOURCES: tuple[str, ...] = tuple(SOURCE_PRIORITY)

#: ``backtest_universe_signal_count``가 모든 source 행에 같은 값인 이유(문서·meta 공용).
UNIVERSE_COUNT_SEMANTICS = (
    "backtest_universe_signal_count는 백테스트 유니버스에 source 축이 없으므로 "
    "세 source 행 모두에 동일한 전역 값이 들어간다. source별로 달라지는 것은 "
    "intersection/diff/missed다."
)

#: ``missed_opportunity_count``는 source별로 더할 수 없다 -- Story 5.6/5.14 경고(review P6).
#: 각 source 행의 missed는 |U| 전체(그 source의 population을 뺀 값)를 포함하므로,
#: 세 행을 합하면 같은 유니버스 티커를 최대 3번 센다. 전체 기회 누락이 필요하면
#: 합산이 아니라 ``(U ∪ T) - P`` 를 티커 집합 수준에서 다시 계산해야 한다.
MISSED_AGGREGATION_WARNING = (
    "missed_opportunity_count는 source별 행을 합산할 수 없다. 각 행이 유니버스 전용 "
    "시그널을 중복 포함하므로 SUM은 실제 기회 누락 종목 수를 과대계상한다."
)

#: 카운트 컬럼의 전략 해석(전략 축이 없는 스키마에 대한 고정 해석).
COUNT_SEMANTICS = (
    "카운트는 전략 A~F 중 하나라도 시그널이 성립한 종목 수(합집합)이며, "
    "전략별 분해는 calculation_meta.by_strategy에만 있다."
)


class BiasMetricsInvariantError(RuntimeError):
    """산출값이 ``bias_event_by_source``의 check 제약을 위반할 때 발생한다."""


@dataclass(frozen=True)
class PopulationSignal:
    """시그널이 성립한 published 후보 한 건.

    ``tags_stage.TaggedCandidate``에는 source 정보가 없으므로, 같은 배치의
    ``SelectedCandidate.sources``(= ``candidate_source_contrib``의 원천)를 붙여
    이 자료구조로 넘긴다.
    """

    ticker: str
    strategies: tuple[str, ...] = ()
    sources: tuple[SourceContribution, ...] = ()


@dataclass(frozen=True)
class SourceBiasMetrics:
    """``bias_event_by_source`` 한 행에 해당하는 source별 카운트."""

    source: str
    candidate_pop_signal_count: int
    backtest_universe_signal_count: int
    intersection_count: int
    diff_count: int
    missed_opportunity_count: int

    def as_dict(self) -> dict[str, Any]:
        return {
            "source": self.source,
            "candidate_pop_signal_count": self.candidate_pop_signal_count,
            "backtest_universe_signal_count": self.backtest_universe_signal_count,
            "intersection_count": self.intersection_count,
            "diff_count": self.diff_count,
            "missed_opportunity_count": self.missed_opportunity_count,
        }


@dataclass(frozen=True)
class BiasMetricsResult:
    """한 거래일의 편향 계산 결과(회차 메타 + source별 3행)."""

    trading_day: date
    by_source: tuple[SourceBiasMetrics, ...]
    calculation_meta: dict[str, Any] = field(default_factory=dict)

    def row(self, source: str) -> SourceBiasMetrics:
        for item in self.by_source:
            if item.source == source:
                return item
        raise KeyError(source)

    def as_rows(self) -> list[dict[str, Any]]:
        return [item.as_dict() for item in self.by_source]


@dataclass(frozen=True)
class TruncatedSignals:
    """M=150 절단 종목의 시그널 계산 결과와 그 종목들의 source 기여."""

    signal_result: UniverseSignalResult
    sources_by_ticker: dict[str, tuple[SourceContribution, ...]] = field(default_factory=dict)
    #: 6자리 숫자 코드로 정규화할 수 없어 계산에서 격리된 절단 티커(원문).
    unnormalizable_tickers: tuple[str, ...] = ()


# --- source 귀속 -------------------------------------------------------------


def _finite_weight(value: Any) -> float:
    """NaN/±inf weight는 정렬 결정성을 깨뜨리므로 0.0으로 정규화한다(review P5).

    ``NaN``은 어떤 비교에도 False라 ``sort``의 결과가 입력 순서에 따라 달라진다 --
    같은 입력에 같은 결과라는 계약이 조용히 깨지는 경로다.
    """
    try:
        weight = float(value)
    except (TypeError, ValueError):
        return 0.0
    if not math.isfinite(weight):
        return 0.0
    return weight


def _coerce_contribution(item: Any) -> SourceContribution | None:
    if isinstance(item, SourceContribution):
        return SourceContribution(source=item.source, weight=_finite_weight(item.weight))
    if isinstance(item, Mapping):
        source = item.get("source")
        if source is None:
            return None
        return SourceContribution(source=str(source), weight=_finite_weight(item.get("weight", 0.0)))
    return None


def _priority_rank(source: str) -> int:
    return BIAS_SOURCES.index(source) if source in BIAS_SOURCES else len(BIAS_SOURCES)


def resolve_primary_source(sources: Iterable[Any] | None) -> str | None:
    """weight 내림차순 → ``SOURCE_PRIORITY`` 순으로 단일 primary source를 고른다.

    ``candidate_source_contrib``와 같은 규칙이며, 한 후보가 여러 source에 기여해도
    분할 계상하지 않는다(정수 카운트 컬럼과 맞지 않는다). weight 동률이면
    ``SOURCE_PRIORITY``가 결정론적 tie-break다. 기여가 없거나 도메인 밖 source뿐이면
    ``None``을 돌려주고, 호출자는 이를 미귀속으로 노출한다.
    """
    if not sources:
        return None
    contributions = [c for c in (_coerce_contribution(s) for s in sources) if c is not None]
    known = [c for c in contributions if c.source in BIAS_SOURCES]
    if not known:
        return None
    known.sort(key=lambda c: (-c.weight, _priority_rank(c.source), c.source))
    return known[0].source


def _normalize(ticker: str) -> str | None:
    """6자리 숫자 코드로 정규화한다. 불가능하면 ``None``(계산 대상에서 격리).

    ``compute_universe_signals``는 정규화 불가 티커에 예외를 던지므로, 여기서 원문을
    그대로 흘려보내면 종목 하나 때문에 전체 계산이 죽는다(review P1). KRX에는
    ``00088K`` 같은 영숫자 코드가 실재한다. 격리된 티커는 조용히 사라지지 않고
    ``calculation_meta``의 ``unnormalizable_tickers``로 노출된다.
    """
    try:
        return normalize_ticker(ticker)
    except BacktestUniverseFixtureError:
        return None


# --- 절단 종목 시그널 어댑터 --------------------------------------------------


def compute_truncated_signals(
    ohlcv_loader: OhlcvDbClient,
    truncated_candidates: Sequence[SelectedCandidate],
    trading_day: date,
    *,
    strategy_client: TagsClient | None = None,
    heartbeat: HeartbeatPolicy | None = None,
) -> TruncatedSignals:
    """M=150으로 절단된 종목의 시그널을 ``compute_universe_signals``로 계산한다.

    절단 종목은 ``candidates`` 테이블에 저장되지 않으므로(``candidate_stage``는 상위 150건만
    insert한다) DB 재조회로는 얻을 수 없고, 같은 배치의
    ``CandidateSelection.truncated_candidates``를 그대로 받아야 한다.

    시그널 성립 판정이 운영 태깅과 **동일한 D-1 확정봉**이어야 하므로 판정 로직을 새로
    쓰지 않고 Story 5.2의 진입점을 절단 티커 목록에 재사용한다. 계산 불가 종목
    (이력 부족·로드/계산 오류)은 시그널 집합에 들어가지 않고
    ``ineligible_tickers``/``error_tickers``로 노출된다.

    정규화 불가 티커(예: ``00088K``)는 ``compute_universe_signals`` 호출 **전에** 걸러낸다 --
    그대로 넘기면 종목 하나가 전체 계산을 예외로 중단시킨다. 격리된 티커는
    ``TruncatedSignals.unnormalizable_tickers``와 ``calculation_meta``로 노출되어
    TRUNCATED_UNCOMPUTABLE과 같은 "종목 단위 격리"가 이 경로에서도 성립한다(review P1).
    """
    sources_by_ticker: dict[str, tuple[SourceContribution, ...]] = {}
    unnormalizable: list[str] = []
    for candidate in truncated_candidates:
        ticker = _normalize(candidate.ticker)
        if ticker is None:
            unnormalizable.append(str(candidate.ticker))
            continue
        sources_by_ticker[ticker] = tuple(getattr(candidate, "sources", ()) or ())

    tickers = sorted(sources_by_ticker)
    if not tickers:
        empty = UniverseSignalResult(
            trading_day=trading_day,
            universe_size=0,
            strategy_signals={key: [] for key in STRATEGY_KEYS},
        )
        return TruncatedSignals(
            signal_result=empty,
            sources_by_ticker={},
            unnormalizable_tickers=tuple(sorted(unnormalizable)),
        )

    result = compute_universe_signals(
        ohlcv_loader,
        tickers,
        trading_day,
        strategy_client=strategy_client,
        heartbeat=heartbeat,
    )
    return TruncatedSignals(
        signal_result=result,
        sources_by_ticker=sources_by_ticker,
        unnormalizable_tickers=tuple(sorted(unnormalizable)),
    )


# --- 편향 지표 ---------------------------------------------------------------


def _signal_union(result: UniverseSignalResult | None) -> set[str]:
    if result is None:
        return set()
    union: set[str] = set()
    for key in STRATEGY_KEYS:
        union.update(result.strategy_signals.get(key, []))
    return union


def _signal_result_meta(result: UniverseSignalResult | None) -> dict[str, Any]:
    """미수집과 실제 0을 구분할 수 있게 종목별 상태를 그대로 노출한다."""
    if result is None:
        return {
            "computed": False,
            "universe_size": 0,
            "signal_count": 0,
            "ready_count": 0,
            "ineligible_count": 0,
            "error_count": 0,
            "ineligible_tickers": [],
            "error_tickers": [],
            "stale_signal_date_tickers": [],
            "latest_signal_date": None,
        }
    latest = result.latest_signal_date
    return {
        "computed": True,
        "universe_size": result.universe_size,
        "signal_count": len(_signal_union(result)),
        "ready_count": result.ready_count,
        "ineligible_count": result.ineligible_count,
        "error_count": result.error_count,
        "ineligible_tickers": sorted(result.ineligible_tickers),
        "error_tickers": sorted(result.error_tickers),
        "stale_signal_date_tickers": sorted(result.stale_signal_date_tickers),
        "latest_signal_date": latest.isoformat() if latest is not None else None,
    }


def _check_row(row: SourceBiasMetrics) -> None:
    """``bias_event_by_source``의 check 제약을 코드로 그대로 재검증한다."""
    values = (
        row.candidate_pop_signal_count,
        row.backtest_universe_signal_count,
        row.intersection_count,
        row.diff_count,
        row.missed_opportunity_count,
    )
    if any(v < 0 for v in values):
        raise BiasMetricsInvariantError(f"음수 카운트가 산출되었습니다: {row.as_dict()}")
    if row.intersection_count > min(row.candidate_pop_signal_count, row.backtest_universe_signal_count):
        raise BiasMetricsInvariantError(
            f"intersection_count가 두 집합 크기를 넘습니다: {row.as_dict()}"
        )
    if row.diff_count > row.candidate_pop_signal_count:
        raise BiasMetricsInvariantError(f"diff_count가 모집단 크기를 넘습니다: {row.as_dict()}")
    if row.diff_count < row.candidate_pop_signal_count - row.intersection_count:
        raise BiasMetricsInvariantError(
            f"diff_count가 모집단 전용분보다 작습니다: {row.as_dict()}"
        )
    if row.missed_opportunity_count < row.backtest_universe_signal_count - row.intersection_count:
        raise BiasMetricsInvariantError(
            f"missed_opportunity_count가 유니버스 전용분보다 작습니다: {row.as_dict()}"
        )


def _check_rows(rows: Sequence[SourceBiasMetrics]) -> None:
    """결과 단위 자체 검증: 정확히 3행, source가 도메인과 정확히 일치, 중복 없음.

    ``bias_event_by_source``의 PK는 (회차, source)이므로 중복 source는 적재 시점에야
    깨진다. append-only 저장소에서는 그때 이미 늦으므로 여기서 막는다(review P4).
    """
    if len(rows) != len(BIAS_SOURCES):
        raise BiasMetricsInvariantError(
            f"source 행 수가 {len(BIAS_SOURCES)}가 아닙니다: {[r.source for r in rows]}"
        )
    sources = [row.source for row in rows]
    if len(set(sources)) != len(sources):
        raise BiasMetricsInvariantError(f"source 행이 중복되었습니다: {sources}")
    if set(sources) != set(BIAS_SOURCES):
        raise BiasMetricsInvariantError(
            f"source 집합이 도메인과 다릅니다: {sources} != {list(BIAS_SOURCES)}"
        )


def _check_trading_day(trading_day: date, result: UniverseSignalResult | None, label: str) -> None:
    """입력 시그널 집합이 요청 거래일과 같은 날인지 확인한다(review P2).

    ``bias_events``는 append-only라 잘못 라벨링된 회차를 사후 수정할 수 없다 -- 다른 날의
    시그널 집합이 이 거래일 행으로 굳는 것을 계산 단계에서 막는다.
    """
    if result is None:
        return
    if result.trading_day != trading_day:
        raise BiasMetricsInvariantError(
            f"{label} 시그널의 거래일이 요청 거래일과 다릅니다: "
            f"{result.trading_day} != {trading_day}"
        )


def compute_bias_metrics(
    trading_day: date,
    population_signals: Sequence[PopulationSignal],
    universe_result: UniverseSignalResult | None,
    *,
    truncated: TruncatedSignals | None = None,
) -> BiasMetricsResult:
    """source별 5개 카운트와 ``calculation_meta``를 산출한다.

    ``population_signals``는 시그널이 성립한 published 후보만 담는다(태깅 결과를 그대로
    쓰고 재계산하지 않는다). ``universe_result``는 Story 5.2의 유니버스 계산 결과,
    ``truncated``는 ``compute_truncated_signals``의 결과다. 둘 다 ``None``이면 각각 빈
    집합으로 취급하되 ``calculation_meta``에 ``computed=false``로 남겨 미수집과 실제 0을
    구분한다.

    반환 전에 DB check 제약 4개와 결과 단위 불변식(3행·source 도메인 일치)을 자체 검증하며,
    입력 시그널 집합의 거래일이 ``trading_day``와 다르면 중단한다. 같은 입력에는 정렬된
    동일 결과가 나온다.
    """
    _check_trading_day(trading_day, universe_result, "universe")
    _check_trading_day(
        trading_day, truncated.signal_result if truncated is not None else None, "truncated"
    )

    universe_signals = _signal_union(universe_result)
    universe_count = len(universe_signals)

    truncated_result = truncated.signal_result if truncated is not None else None
    truncated_signals = _signal_union(truncated_result)
    truncated_sources = truncated.sources_by_ticker if truncated is not None else {}

    # published 후보: primary source별로 단일 귀속(분할 계상 금지).
    population_by_source: dict[str, set[str]] = {source: set() for source in BIAS_SOURCES}
    population_strategies: dict[str, dict[str, set[str]]] = {
        source: {key: set() for key in STRATEGY_KEYS} for source in BIAS_SOURCES
    }
    unattributed_population: set[str] = set()
    seen_population: set[str] = set()
    unnormalizable_population: set[str] = set()
    unknown_strategy_keys: set[str] = set()

    for signal in population_signals:
        ticker = _normalize(signal.ticker)
        if ticker is None:
            # 정규화 불가 티커는 유니버스/절단 집합과 대조할 수 없으므로 격리하고 노출한다.
            unnormalizable_population.add(str(signal.ticker))
            continue
        if ticker in seen_population:
            continue
        seen_population.add(ticker)
        primary = resolve_primary_source(signal.sources)
        if primary is None:
            unattributed_population.add(ticker)
            continue
        population_by_source[primary].add(ticker)
        for strategy in signal.strategies or ():
            if strategy in population_strategies[primary]:
                population_strategies[primary][strategy].add(ticker)
            else:
                # ``by_strategy``에서 조용히 버려지는 전략 키를 드러낸다(review P6).
                unknown_strategy_keys.add(str(strategy))

    # 절단 종목: 시그널이 성립한 것만 primary source별로 귀속.
    truncated_by_source: dict[str, set[str]] = {source: set() for source in BIAS_SOURCES}
    unattributed_truncated: set[str] = set()
    for ticker in sorted(truncated_signals):
        primary = resolve_primary_source(truncated_sources.get(ticker))
        if primary is None:
            unattributed_truncated.add(ticker)
            continue
        truncated_by_source[primary].add(ticker)

    all_population_tickers: set[str] = set(unattributed_population)
    for tickers_for_source in population_by_source.values():
        all_population_tickers |= tickers_for_source

    rows: list[SourceBiasMetrics] = []
    meta_by_source: dict[str, Any] = {}
    for source in BIAS_SOURCES:
        population = population_by_source[source]
        truncated_for_source = truncated_by_source[source]
        intersection = population & universe_signals
        diff = population - universe_signals
        missed = (universe_signals | truncated_for_source) - population

        row = SourceBiasMetrics(
            source=source,
            candidate_pop_signal_count=len(population),
            backtest_universe_signal_count=universe_count,
            intersection_count=len(intersection),
            diff_count=len(diff),
            missed_opportunity_count=len(missed),
        )
        _check_row(row)
        rows.append(row)

        meta_by_source[source] = {
            "population_tickers": sorted(population),
            "intersection_tickers": sorted(intersection),
            "diff_tickers": sorted(diff),
            "truncated_signal_tickers": sorted(truncated_for_source),
            # 유니버스에도 population에도 없어서 "절단분 때문에" 늘어난 실제 가산분.
            # population을 함께 빼지 않으면 실제 missed 증가분과 어긋난다(review P6c).
            "truncated_only_missed_count": len(
                truncated_for_source - universe_signals - population
            ),
        }

    _check_rows(rows)

    by_strategy: dict[str, Any] = {}
    for key in STRATEGY_KEYS:
        universe_for_strategy = set(
            universe_result.strategy_signals.get(key, []) if universe_result is not None else []
        )
        by_strategy[key] = {
            "backtest_universe_signal_count": len(universe_for_strategy),
            "by_source": {
                source: {
                    "candidate_pop_signal_count": len(population_strategies[source][key]),
                    "intersection_count": len(
                        population_strategies[source][key] & universe_for_strategy
                    ),
                    "diff_count": len(population_strategies[source][key] - universe_for_strategy),
                }
                for source in BIAS_SOURCES
            },
        }

    calculation_meta: dict[str, Any] = {
        "story": "5.3",
        "trading_day": trading_day.isoformat(),
        "strategy_keys": list(STRATEGY_KEYS),
        "sources": list(BIAS_SOURCES),
        "count_semantics": COUNT_SEMANTICS,
        "universe_count_semantics": UNIVERSE_COUNT_SEMANTICS,
        "universe": _signal_result_meta(universe_result),
        "truncated": _signal_result_meta(truncated_result),
        "missed_aggregation_warning": MISSED_AGGREGATION_WARNING,
        "unknown_strategy_keys": sorted(unknown_strategy_keys),
        "population": {
            "input_count": len(population_signals),
            "distinct_ticker_count": len(seen_population),
            "attributed_count": sum(len(v) for v in population_by_source.values()),
            "unattributed_tickers": sorted(unattributed_population),
            "unnormalizable_tickers": sorted(unnormalizable_population),
        },
        "truncated_attribution": {
            "signal_count": len(truncated_signals),
            "unattributed_tickers": sorted(unattributed_truncated),
            "unnormalizable_tickers": sorted(
                truncated.unnormalizable_tickers if truncated is not None else ()
            ),
            # 산식은 ``T_s ∩ P_s = ∅``(절단 종목은 published가 아니다)를 전제한다.
            # 깨지면 입력이 오염된 것이므로 조용히 넘기지 않고 드러낸다(review P6b).
            "published_overlap_tickers": sorted(truncated_signals & all_population_tickers),
        },
        "by_source": meta_by_source,
        "by_strategy": by_strategy,
    }

    return BiasMetricsResult(
        trading_day=trading_day,
        by_source=tuple(rows),
        calculation_meta=calculation_meta,
    )


__all__ = [
    "BIAS_SOURCES",
    "MISSED_AGGREGATION_WARNING",
    "BiasMetricsInvariantError",
    "BiasMetricsResult",
    "PopulationSignal",
    "SourceBiasMetrics",
    "TruncatedSignals",
    "compute_bias_metrics",
    "compute_truncated_signals",
    "resolve_primary_source",
]
