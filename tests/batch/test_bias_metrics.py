"""Story 5.3: 편향 지표 계산 로직 테스트.

spec의 I/O 매트릭스 9개 시나리오 전부와, 알려진 소규모 입력에 대한 교집합·차집합·
기회누락의 수치적 정확성을 source별로 고정한다. ``bias_event_by_source``의 check 제약
4개를 산출값에 직접 적용하는 불변식 테스트가 포함되며, 실 DB·실 API 없이 fake
loader/strategy client만 쓴다(Story 5.2 테스트와 동일 패턴).
"""

from __future__ import annotations

from datetime import date

import pandas as pd
import pytest

from apps.batch.bias_metrics import (
    BIAS_SOURCES,
    BiasMetricsInvariantError,
    PopulationSignal,
    SourceBiasMetrics,
    TruncatedSignals,
    compute_bias_metrics,
    compute_truncated_signals,
    resolve_primary_source,
)
from apps.batch.universe_signal import STRATEGY_KEYS, UniverseSignalResult, compute_universe_signals
from backtest.strategy_api import StrategyResult
from domain.candidate_selection import SOURCE_PRIORITY, SelectedCandidate, SourceContribution
from domain.ohlcv_cache import MIN_HISTORY_TRADING_DAYS, OhlcvCacheStatus

TRADING_DAY = date(2026, 9, 9)


# --- fakes ------------------------------------------------------------------


def _frame(rows: int = MIN_HISTORY_TRADING_DAYS + 5) -> pd.DataFrame:
    index = pd.bdate_range(end=pd.Timestamp(TRADING_DAY), periods=rows)
    return pd.DataFrame(
        {"Open": 100.0, "High": 110.0, "Low": 90.0, "Close": 105.0, "Volume": 1000.0},
        index=index,
    )


class FakeLoader:
    def __init__(self, mapping: dict[str, object] | None = None, default: object | None = None) -> None:
        self._mapping = mapping or {}
        self._default = default if default is not None else _frame()

    def load_ohlcv(self, ticker: str, cutoff: date):
        value = self._mapping.get(ticker, self._default)
        if isinstance(value, Exception):
            raise value
        return value


class FakeStrategyClient:
    """``{ticker: {strategy: 성립여부}}``. 성립은 D-1 확정봉(``iloc[-2]``)에 True."""

    def __init__(self, signals_by_ticker: dict[str, dict[str, bool]] | None = None) -> None:
        self._signals = signals_by_ticker or {}

    def compute(self, frame: pd.DataFrame, ticker: str) -> StrategyResult:
        wanted = self._signals.get(ticker, {})
        signals: dict[str, pd.Series] = {}
        for key in STRATEGY_KEYS:
            series = pd.Series(False, index=frame.index, dtype=bool)
            if wanted.get(key):
                series.iloc[-2] = True
            signals[key] = series
        return StrategyResult(ticker=ticker, status=OhlcvCacheStatus.READY, signals=signals, error=None)


# --- helpers ----------------------------------------------------------------

A = STRATEGY_KEYS[0]
B = STRATEGY_KEYS[1] if len(STRATEGY_KEYS) > 1 else STRATEGY_KEYS[0]


def _contrib(source: str, weight: float = 1.0) -> SourceContribution:
    return SourceContribution(source=source, weight=weight)


def _pop(ticker: str, source: str, strategies: tuple[str, ...] = (A,)) -> PopulationSignal:
    return PopulationSignal(ticker=ticker, strategies=strategies, sources=(_contrib(source),))


def _universe(signals: dict[str, list[str]], *, size: int | None = None, **kwargs) -> UniverseSignalResult:
    full = {key: [] for key in STRATEGY_KEYS}
    full.update({k: sorted(v) for k, v in signals.items()})
    ready = sorted({t for v in full.values() for t in v})
    return UniverseSignalResult(
        trading_day=TRADING_DAY,
        universe_size=size if size is not None else len(ready),
        strategy_signals=full,
        ready_tickers=kwargs.pop("ready_tickers", ready),
        signal_dates=kwargs.pop("signal_dates", {t: date(2026, 9, 8) for t in ready}),
        **kwargs,
    )


def _assert_db_checks(row: SourceBiasMetrics) -> None:
    """``bias_event_by_source``의 check 제약 4개(+ 음수 금지)를 그대로 적용한다."""
    assert row.candidate_pop_signal_count >= 0
    assert row.backtest_universe_signal_count >= 0
    assert row.intersection_count >= 0
    assert row.diff_count >= 0
    assert row.missed_opportunity_count >= 0
    assert row.intersection_count <= min(
        row.candidate_pop_signal_count, row.backtest_universe_signal_count
    )
    assert row.diff_count <= row.candidate_pop_signal_count
    assert row.diff_count >= row.candidate_pop_signal_count - row.intersection_count
    assert row.missed_opportunity_count >= (
        row.backtest_universe_signal_count - row.intersection_count
    )


# --- source 귀속 -------------------------------------------------------------


def test_source_domain_is_derived_from_candidate_selection() -> None:
    assert BIAS_SOURCES == tuple(SOURCE_PRIORITY)
    assert set(BIAS_SOURCES) == {"t1859", "t1852", "t1856"}


def test_resolve_primary_source_prefers_higher_weight() -> None:
    assert (
        resolve_primary_source([_contrib("t1856", 0.9), _contrib("t1859", 0.1)]) == "t1856"
    )


def test_resolve_primary_source_ties_break_on_priority() -> None:
    # MULTI_SOURCE_CANDIDATE: t1856(w=0.5)·t1859(w=0.5) -> priority 우선인 t1859.
    assert resolve_primary_source([_contrib("t1856", 0.5), _contrib("t1859", 0.5)]) == "t1859"
    assert resolve_primary_source([_contrib("t1859", 0.5), _contrib("t1856", 0.5)]) == "t1859"


def test_resolve_primary_source_accepts_mappings_and_rejects_unknown() -> None:
    assert resolve_primary_source([{"source": "t1852", "weight": 0.3}]) == "t1852"
    assert resolve_primary_source([]) is None
    assert resolve_primary_source(None) is None
    assert resolve_primary_source([_contrib("t9999", 1.0)]) is None


# --- I/O 매트릭스 -------------------------------------------------------------


def test_happy_path_numeric_accuracy_per_source() -> None:
    """HAPPY_PATH: 알려진 소규모 입력의 5개 카운트를 source별로 수치 고정한다."""
    population = [
        _pop("000001", "t1859"),  # 유니버스와 겹침
        _pop("000002", "t1859"),  # 모집단 전용
        _pop("000003", "t1856"),  # 유니버스와 겹침
        _pop("000004", "t1852"),  # 모집단 전용
    ]
    universe = _universe({A: ["000001", "000003", "000005"], B: ["000006"]})
    # U = {1,3,5,6} -> 4종목
    result = compute_bias_metrics(TRADING_DAY, population, universe)

    assert [r.source for r in result.by_source] == list(BIAS_SOURCES)

    t1859 = result.row("t1859")
    assert (t1859.candidate_pop_signal_count, t1859.backtest_universe_signal_count) == (2, 4)
    assert (t1859.intersection_count, t1859.diff_count, t1859.missed_opportunity_count) == (1, 1, 3)

    t1856 = result.row("t1856")
    assert (t1856.candidate_pop_signal_count, t1856.intersection_count) == (1, 1)
    assert (t1856.diff_count, t1856.missed_opportunity_count) == (0, 3)

    t1852 = result.row("t1852")
    assert (t1852.candidate_pop_signal_count, t1852.intersection_count) == (1, 0)
    assert (t1852.diff_count, t1852.missed_opportunity_count) == (1, 4)

    for row in result.by_source:
        assert row.backtest_universe_signal_count == 4  # source 축 없음: 전역 동일값
        _assert_db_checks(row)


def test_empty_source_yields_null_safe_zero_row() -> None:
    """EMPTY_SOURCE: 기여 0건인 source도 행이 생성되고 missed=유니버스 시그널 수."""
    population = [_pop("000001", "t1859")]
    universe = _universe({A: ["000001", "000007"]})
    result = compute_bias_metrics(TRADING_DAY, population, universe)

    assert len(result.by_source) == 3
    row = result.row("t1852")
    assert row.candidate_pop_signal_count == 0
    assert row.intersection_count == 0
    assert row.diff_count == 0
    assert row.missed_opportunity_count == 2
    _assert_db_checks(row)


def test_multi_source_candidate_counted_once_on_primary() -> None:
    """MULTI_SOURCE_CANDIDATE: 분할 계상 없이 tie-break 우선 source에만 계상."""
    population = [
        PopulationSignal(
            ticker="000001",
            strategies=(A,),
            sources=(_contrib("t1856", 0.5), _contrib("t1859", 0.5)),
        )
    ]
    result = compute_bias_metrics(TRADING_DAY, population, _universe({A: ["000001"]}))
    assert result.row("t1859").candidate_pop_signal_count == 1
    assert result.row("t1856").candidate_pop_signal_count == 0
    assert sum(r.candidate_pop_signal_count for r in result.by_source) == 1


def test_truncated_signal_added_to_missed_without_double_counting() -> None:
    """TRUNCATED_SIGNAL: 절단 시그널이 missed에 가산되고 유니버스와 겹치면 1회만."""
    population = [_pop("000001", "t1859")]
    universe = _universe({A: ["000001", "000002"]})
    truncated_result = _universe({A: ["000002", "000003"]})  # 000002는 유니버스와 겹침
    truncated = TruncatedSignals(
        signal_result=truncated_result,
        sources_by_ticker={
            "000002": (_contrib("t1859"),),
            "000003": (_contrib("t1859"),),
        },
    )
    result = compute_bias_metrics(TRADING_DAY, population, universe, truncated=truncated)

    row = result.row("t1859")
    # (U ∪ T) - P = {000002, 000003} -> 2 (000002 중복 계상 없음)
    assert row.missed_opportunity_count == 2
    assert row.backtest_universe_signal_count == 2
    assert row.intersection_count == 1
    meta = result.calculation_meta["by_source"]["t1859"]
    assert meta["truncated_signal_tickers"] == ["000002", "000003"]
    assert meta["truncated_only_missed_count"] == 1
    _assert_db_checks(row)


def test_truncated_uncomputable_is_excluded_and_exposed_in_meta() -> None:
    """TRUNCATED_UNCOMPUTABLE: 이력 부족/오류 절단 종목은 missed에 넣지 않고 meta로 노출."""
    loader = FakeLoader(
        {
            "000010": _frame(),
            "000011": OhlcvCacheStatus.INELIGIBLE_INSUFFICIENT_HISTORY,
            "000012": RuntimeError("boom"),
        }
    )
    truncated_candidates = [
        SelectedCandidate("000010", "A", 10.0, (_contrib("t1859"),)),
        SelectedCandidate("000011", "B", 9.0, (_contrib("t1859"),)),
        SelectedCandidate("000012", "C", 8.0, (_contrib("t1859"),)),
    ]
    truncated = compute_truncated_signals(
        loader,
        truncated_candidates,
        TRADING_DAY,
        strategy_client=FakeStrategyClient({"000010": {A: True}}),
    )
    assert truncated.signal_result.strategy_signals[A] == ["000010"]
    assert truncated.signal_result.ineligible_tickers == ["000011"]
    assert truncated.signal_result.error_tickers == ["000012"]

    result = compute_bias_metrics(TRADING_DAY, [], _universe({}), truncated=truncated)
    assert result.row("t1859").missed_opportunity_count == 1
    meta = result.calculation_meta["truncated"]
    assert meta["computed"] is True
    assert meta["ineligible_tickers"] == ["000011"]
    assert meta["error_tickers"] == ["000012"]


def test_no_universe_signal_leaves_only_truncated_missed() -> None:
    """NO_UNIVERSE_SIGNAL: universe=0, intersection=0, missed=source별 절단 시그널 수."""
    universe = _universe({}, size=104, ready_tickers=["000001"], signal_dates={"000001": date(2026, 9, 8)})
    truncated = TruncatedSignals(
        signal_result=_universe({A: ["000050"]}),
        sources_by_ticker={"000050": (_contrib("t1856"),)},
    )
    result = compute_bias_metrics(TRADING_DAY, [_pop("000001", "t1859")], universe, truncated=truncated)

    for row in result.by_source:
        assert row.backtest_universe_signal_count == 0
        assert row.intersection_count == 0
        _assert_db_checks(row)
    assert result.row("t1856").missed_opportunity_count == 1
    assert result.row("t1859").missed_opportunity_count == 0
    assert result.calculation_meta["universe"]["universe_size"] == 104


def test_stale_universe_bar_is_recorded_not_failed() -> None:
    """STALE_UNIVERSE_BAR: 뒤처진 확정봉 종목은 계산을 막지 않고 meta로 기록된다."""
    universe = _universe(
        {A: ["000001", "000002"]},
        signal_dates={"000001": date(2026, 9, 8), "000002": date(2026, 8, 20)},
    )
    result = compute_bias_metrics(TRADING_DAY, [_pop("000001", "t1859")], universe)
    assert result.calculation_meta["universe"]["stale_signal_date_tickers"] == ["000002"]
    assert result.calculation_meta["universe"]["latest_signal_date"] == "2026-09-08"
    assert result.row("t1859").backtest_universe_signal_count == 2


def test_constraint_selfcheck_raises_on_bad_values() -> None:
    """CONSTRAINT_SELFCHECK: check 제약을 깨는 값은 반환 전에 예외로 중단된다."""
    from apps.batch import bias_metrics as module

    bad = SourceBiasMetrics("t1859", 1, 2, 3, 0, 0)  # intersection > 두 집합 크기
    with pytest.raises(BiasMetricsInvariantError):
        module._check_row(bad)
    with pytest.raises(BiasMetricsInvariantError):
        module._check_row(SourceBiasMetrics("t1859", -1, 0, 0, 0, 0))
    with pytest.raises(BiasMetricsInvariantError):
        module._check_row(SourceBiasMetrics("t1859", 3, 0, 0, 1, 0))  # diff < pop - inter
    with pytest.raises(BiasMetricsInvariantError):
        module._check_row(SourceBiasMetrics("t1859", 0, 3, 0, 0, 1))  # missed < uni - inter


def test_reproducible_for_same_input() -> None:
    """REPRODUCIBLE: 같은 입력으로 두 번 실행하면 완전히 동일한 결과."""
    population = [_pop("000003", "t1856"), _pop("000001", "t1859"), _pop("000002", "t1859")]
    universe = _universe({A: ["000001"], B: ["000003", "000009"]})
    truncated = TruncatedSignals(
        signal_result=_universe({A: ["000077"]}),
        sources_by_ticker={"000077": (_contrib("t1852"),)},
    )
    first = compute_bias_metrics(TRADING_DAY, population, universe, truncated=truncated)
    second = compute_bias_metrics(TRADING_DAY, list(reversed(population)), universe, truncated=truncated)
    assert first.by_source == second.by_source
    assert first.calculation_meta == second.calculation_meta


# --- 부가 불변식 -------------------------------------------------------------


def test_invariants_hold_across_input_combinations() -> None:
    """어떤 조합에서도 check 제약 4개를 위반하지 않는다."""
    combos = [
        ([], None, None),
        ([_pop("000001", "t1859")], None, None),
        ([], _universe({A: ["000001", "000002"]}), None),
        (
            [_pop("000001", "t1859"), _pop("000002", "t1852"), _pop("000003", "t1856")],
            _universe({A: ["000002", "000004"], B: ["000005"]}),
            TruncatedSignals(
                signal_result=_universe({A: ["000004", "000006"]}),
                sources_by_ticker={
                    "000004": (_contrib("t1852"),),
                    "000006": (_contrib("t1856"),),
                },
            ),
        ),
    ]
    for population, universe, truncated in combos:
        result = compute_bias_metrics(TRADING_DAY, population, universe, truncated=truncated)
        assert len(result.by_source) == 3
        for row in result.by_source:
            _assert_db_checks(row)


def test_meta_exposes_universe_health_and_strategy_breakdown() -> None:
    universe = _universe(
        {A: ["000001"], B: ["000002"]},
        size=5,
        ineligible_tickers=["000090"],
        error_tickers=["000091"],
    )
    result = compute_bias_metrics(TRADING_DAY, [_pop("000001", "t1859", (A,))], universe)
    meta = result.calculation_meta
    assert meta["universe"]["ineligible_tickers"] == ["000090"]
    assert meta["universe"]["error_tickers"] == ["000091"]
    assert meta["universe"]["signal_count"] == 2
    assert meta["by_strategy"][A]["backtest_universe_signal_count"] == 1
    assert meta["by_strategy"][A]["by_source"]["t1859"]["intersection_count"] == 1
    assert meta["count_semantics"]
    assert meta["universe_count_semantics"]


def test_unattributed_population_is_exposed_not_silently_counted() -> None:
    population = [PopulationSignal(ticker="000001", strategies=(A,), sources=())]
    result = compute_bias_metrics(TRADING_DAY, population, _universe({}))
    assert sum(r.candidate_pop_signal_count for r in result.by_source) == 0
    assert result.calculation_meta["population"]["unattributed_tickers"] == ["000001"]


def test_population_ticker_deduplicated_and_normalized() -> None:
    population = [_pop("000001.KS", "t1859"), _pop("000001", "t1856")]
    result = compute_bias_metrics(TRADING_DAY, population, _universe({A: ["000001"]}))
    assert result.row("t1859").candidate_pop_signal_count == 1
    assert result.row("t1856").candidate_pop_signal_count == 0


def test_compute_truncated_signals_reuses_universe_entry_point() -> None:
    """절단 시그널도 운영과 같은 D-1 확정봉 규칙(``compute_universe_signals``)으로 계산."""
    loader = FakeLoader()
    client = FakeStrategyClient({"000021": {A: True}, "000022": {}})
    candidates = [
        SelectedCandidate("000022", "B", 9.0, (_contrib("t1856"),)),
        SelectedCandidate("000021", "A", 10.0, (_contrib("t1859"),)),
    ]
    truncated = compute_truncated_signals(loader, candidates, TRADING_DAY, strategy_client=client)
    reference = compute_universe_signals(
        FakeLoader(), ["000021", "000022"], TRADING_DAY, strategy_client=FakeStrategyClient({"000021": {A: True}})
    )
    assert truncated.signal_result.strategy_signals == reference.strategy_signals
    assert truncated.sources_by_ticker["000021"] == (_contrib("t1859"),)


def test_compute_truncated_signals_with_no_candidates() -> None:
    truncated = compute_truncated_signals(FakeLoader(), [], TRADING_DAY)
    assert truncated.signal_result.universe_size == 0
    assert truncated.sources_by_ticker == {}
    result = compute_bias_metrics(TRADING_DAY, [], None, truncated=truncated)
    assert result.calculation_meta["universe"]["computed"] is False
    assert all(r.missed_opportunity_count == 0 for r in result.by_source)


def test_module_does_not_touch_supabase_or_bias_tables() -> None:
    """적재는 Story 5.4의 몫 -- 지연 import·importlib까지 포함해 봉쇄한다(review P7)."""
    import io
    import subprocess
    import sys
    import tokenize
    from pathlib import Path

    from apps.batch import bias_metrics

    # 주석·문자열(docstring 포함)을 제거한 실행 코드만 검사한다 -- 지연 import와
    # importlib 우회까지 잡되 설명문의 단어에는 걸리지 않는다.
    source = Path(bias_metrics.__file__).read_text(encoding="utf-8")
    tokens = tokenize.generate_tokens(io.StringIO(source).readline)
    code = " ".join(
        tok.string for tok in tokens if tok.type not in (tokenize.STRING, tokenize.COMMENT)
    )
    for forbidden in ("supabase", "importlib", "postgrest", "httpx", "__import__"):
        assert forbidden not in code.lower(), forbidden
    for forbidden in ("insert", "upsert", "rpc", "bias_event_by_source"):
        assert forbidden not in code.lower(), forbidden

    # 모듈 import만으로 Supabase 클라이언트가 딸려오지 않아야 한다(격리 프로세스).
    # ``httpx``는 Story 5.2의 ``universe_signal`` 체인이 이미 전이 import하는 선행 사실이라
    # 이 스토리의 계약 대상이 아니다 -- Supabase 계열만 본다.
    root = Path(bias_metrics.__file__).resolve().parents[2]
    probe = (
        "import sys; import apps.batch.bias_metrics; "
        "print([n for n in sys.modules if n.split('.')[0] in "
        "{'supabase','postgrest','gotrue','storage3'}])"
    )
    import os

    env = dict(os.environ, PYTHONPATH=os.pathsep.join(p for p in sys.path if p))
    completed = subprocess.run(
        [sys.executable, "-c", probe], cwd=root, capture_output=True, text=True, env=env
    )
    assert completed.returncode == 0, completed.stderr
    assert completed.stdout.strip() == "[]", completed.stdout


# --- review 패치 회귀 --------------------------------------------------------


def test_unnormalizable_truncated_ticker_is_isolated_not_fatal() -> None:
    """P1: ``00088K`` 같은 영숫자 코드 하나가 전체 계산을 죽이지 않는다."""
    loader = FakeLoader()
    candidates = [
        SelectedCandidate("00088K", "Weird", 11.0, (_contrib("t1859"),)),
        SelectedCandidate("000021", "A", 10.0, (_contrib("t1859"),)),
    ]
    truncated = compute_truncated_signals(
        loader, candidates, TRADING_DAY, strategy_client=FakeStrategyClient({"000021": {A: True}})
    )
    assert truncated.unnormalizable_tickers == ("00088K",)
    assert truncated.signal_result.strategy_signals[A] == ["000021"]

    result = compute_bias_metrics(TRADING_DAY, [], _universe({}), truncated=truncated)
    assert result.row("t1859").missed_opportunity_count == 1
    assert result.calculation_meta["truncated_attribution"]["unnormalizable_tickers"] == ["00088K"]


def test_unnormalizable_population_ticker_is_isolated_and_exposed() -> None:
    population = [_pop("00088K", "t1859"), _pop("000001", "t1859")]
    result = compute_bias_metrics(TRADING_DAY, population, _universe({A: ["000001"]}))
    assert result.row("t1859").candidate_pop_signal_count == 1
    assert result.calculation_meta["population"]["unnormalizable_tickers"] == ["00088K"]


def test_trading_day_mismatch_is_rejected() -> None:
    """P2: append-only 저장소에 잘못 라벨링된 회차가 굳는 것을 막는다."""
    other_day = _universe({A: ["000001"]})
    object.__setattr__(other_day, "trading_day", date(2026, 9, 8))
    with pytest.raises(BiasMetricsInvariantError):
        compute_bias_metrics(TRADING_DAY, [], other_day)

    truncated = TruncatedSignals(signal_result=other_day, sources_by_ticker={})
    with pytest.raises(BiasMetricsInvariantError):
        compute_bias_metrics(TRADING_DAY, [], _universe({}), truncated=truncated)


def test_python_checks_match_migration_sql() -> None:
    """P3: migration과 Python 자체 검증의 drift를 막는다(migration은 읽기만)."""
    import dataclasses
    import re
    from pathlib import Path

    from apps.batch import bias_metrics

    root = Path(bias_metrics.__file__).resolve().parents[2]
    sql = (
        root / "infra" / "supabase" / "migrations" / "202609091700_create_bias_events.sql"
    ).read_text(encoding="utf-8")

    match = re.search(r"source\s+text\s+not\s+null\s+check\s*\(\s*source\s+in\s*\(([^)]*)\)", sql)
    assert match is not None
    sql_sources = tuple(s.strip().strip("'") for s in match.group(1).split(","))
    assert set(sql_sources) == set(BIAS_SOURCES)

    for constraint in (
        "bias_event_by_source_intersection_within_sets",
        "bias_event_by_source_diff_within_population",
        "bias_event_by_source_diff_covers_population_only",
        "bias_event_by_source_missed_covers_universe_only",
    ):
        assert f"constraint {constraint}" in sql, constraint

    count_columns = {
        f.name for f in dataclasses.fields(SourceBiasMetrics) if f.name != "source"
    }
    assert count_columns == {
        "candidate_pop_signal_count",
        "backtest_universe_signal_count",
        "intersection_count",
        "diff_count",
        "missed_opportunity_count",
    }
    for column in count_columns:
        assert re.search(rf"^\s+{column}\s+integer\s+not\s+null", sql, re.MULTILINE), column


def test_result_level_selfcheck_rejects_bad_row_sets() -> None:
    """P4: 3행·source 도메인 일치·중복 없음."""
    from apps.batch import bias_metrics as module

    row = SourceBiasMetrics("t1859", 0, 0, 0, 0, 0)
    with pytest.raises(BiasMetricsInvariantError):
        module._check_rows([row])
    with pytest.raises(BiasMetricsInvariantError):
        module._check_rows([row, row, row])
    with pytest.raises(BiasMetricsInvariantError):
        module._check_rows([row, SourceBiasMetrics("t1852", 0, 0, 0, 0, 0), SourceBiasMetrics("t9999", 0, 0, 0, 0, 0)])
    module._check_rows(
        [SourceBiasMetrics(source, 0, 0, 0, 0, 0) for source in BIAS_SOURCES]
    )


def test_non_finite_weight_is_normalized_to_zero() -> None:
    """P5: NaN/inf weight가 정렬 결정성을 깨지 않는다."""
    nan = float("nan")
    assert resolve_primary_source([_contrib("t1856", nan), _contrib("t1852", 0.1)]) == "t1852"
    # NaN끼리면 둘 다 0.0이 되어 priority tie-break가 결정론적으로 적용된다.
    assert resolve_primary_source([_contrib("t1856", nan), _contrib("t1852", nan)]) == "t1852"
    assert resolve_primary_source([_contrib("t1852", nan), _contrib("t1856", nan)]) == "t1852"
    assert resolve_primary_source([{"source": "t1859", "weight": float("inf")}]) == "t1859"


def test_meta_exposes_unknown_strategy_and_published_overlap() -> None:
    """P6: 버려지는 전략 키와 T∩P 전제 위반, 절단 전용 가산분 보정."""
    population = [PopulationSignal("000001", ("ZZZ", A), (_contrib("t1859"),))]
    universe = _universe({A: ["000002"]})
    truncated = TruncatedSignals(
        signal_result=_universe({A: ["000001", "000003"]}),
        sources_by_ticker={"000001": (_contrib("t1859"),), "000003": (_contrib("t1859"),)},
    )
    result = compute_bias_metrics(TRADING_DAY, population, universe, truncated=truncated)

    meta = result.calculation_meta
    assert meta["unknown_strategy_keys"] == ["ZZZ"]
    assert meta["truncated_attribution"]["published_overlap_tickers"] == ["000001"]
    # T_s = {000001, 000003}, U = {000002}, P_s = {000001}
    # missed = (U ∪ T_s) - P_s = {000002, 000003} -> 2, 절단 전용 가산분은 000003 하나.
    assert result.row("t1859").missed_opportunity_count == 2
    assert meta["by_source"]["t1859"]["truncated_only_missed_count"] == 1
    assert meta["missed_aggregation_warning"]
    assert "합산" in meta["missed_aggregation_warning"]


# --- Story 5.4 seam ---------------------------------------------------------


def test_as_rows_shape_is_stable_for_append() -> None:
    """P8: Story 5.4가 그대로 append할 행 모양을 고정한다."""
    result = compute_bias_metrics(TRADING_DAY, [_pop("000001", "t1859")], _universe({A: ["000001"]}))
    rows = result.as_rows()
    assert [r["source"] for r in rows] == list(BIAS_SOURCES)
    assert all(
        set(r) == {
            "source",
            "candidate_pop_signal_count",
            "backtest_universe_signal_count",
            "intersection_count",
            "diff_count",
            "missed_opportunity_count",
        }
        for r in rows
    )
    assert rows[0] == result.row("t1859").as_dict()
    assert all(isinstance(v, int) for r in rows for k, v in r.items() if k != "source")


def test_row_lookup_raises_key_error_for_unknown_source() -> None:
    result = compute_bias_metrics(TRADING_DAY, [], _universe({}))
    with pytest.raises(KeyError):
        result.row("t9999")


def test_compute_truncated_signals_beats_heartbeat_per_ticker() -> None:
    class CountingHeartbeat:
        def __init__(self) -> None:
            self.beats = 0

        def beat(self) -> None:
            self.beats += 1

    heartbeat = CountingHeartbeat()
    candidates = [
        SelectedCandidate("000021", "A", 10.0, (_contrib("t1859"),)),
        SelectedCandidate("000022", "B", 9.0, (_contrib("t1856"),)),
        SelectedCandidate("00088K", "X", 8.0, (_contrib("t1856"),)),  # 격리 -- beat 없음
    ]
    compute_truncated_signals(
        FakeLoader(), candidates, TRADING_DAY, strategy_client=FakeStrategyClient(), heartbeat=heartbeat
    )
    assert heartbeat.beats == 2

    idle = CountingHeartbeat()
    compute_truncated_signals(FakeLoader(), [], TRADING_DAY, heartbeat=idle)
    assert idle.beats == 0


def test_reproducible_across_shuffled_source_and_mapping_order() -> None:
    """P8: population 순서뿐 아니라 sources·sources_by_ticker 순서도 결과에 영향이 없다."""
    pop_a = [
        PopulationSignal("000001", (A, B), (_contrib("t1859", 0.5), _contrib("t1856", 0.5))),
        PopulationSignal("000002", (A,), (_contrib("t1852", 0.4), _contrib("t1856", 0.4))),
    ]
    pop_b = [
        PopulationSignal("000002", (A,), (_contrib("t1856", 0.4), _contrib("t1852", 0.4))),
        PopulationSignal("000001", (B, A), (_contrib("t1856", 0.5), _contrib("t1859", 0.5))),
    ]
    universe = _universe({A: ["000001", "000009"]})
    trunc_result = _universe({A: ["000077", "000078"]})
    first = compute_bias_metrics(
        TRADING_DAY,
        pop_a,
        universe,
        truncated=TruncatedSignals(
            trunc_result,
            {"000077": (_contrib("t1852"),), "000078": (_contrib("t1859"),)},
        ),
    )
    second = compute_bias_metrics(
        TRADING_DAY,
        pop_b,
        universe,
        truncated=TruncatedSignals(
            trunc_result,
            {"000078": (_contrib("t1859"),), "000077": (_contrib("t1852"),)},
        ),
    )
    assert first.by_source == second.by_source
    assert first.calculation_meta == second.calculation_meta
