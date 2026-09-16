"""Story 5.2: 유니버스 시그널 계산 + 독립 백필 테스트.

spec의 I/O 매트릭스 전 케이스(정상/이력부족/로드에러/계산에러/독립백필/티커정규화/
재현성)를 fake loader·fake provider·fake repository로 검증한다 -- 실 API·실 DB 없이.
"""

from __future__ import annotations

from datetime import date, timedelta

import pandas as pd
import pytest

from apps.batch.backtest_universe import BacktestUniverseFixtureError, load_backtest_universe
from apps.batch.ohlcv_cache import CachedTickerState, SupabaseOhlcvCacheRepository
from apps.batch.universe_signal import (
    STRATEGY_KEYS,
    backfill_universe_ohlcv,
    compute_universe_signals,
)
from backtest.strategy_api import StrategyResult
from domain.ohlcv_cache import MIN_HISTORY_TRADING_DAYS, OhlcvCacheStatus

TRADING_DAY = date(2026, 9, 9)


# --- fakes ------------------------------------------------------------------


def _frame(rows: int = MIN_HISTORY_TRADING_DAYS + 5) -> pd.DataFrame:
    index = pd.bdate_range(end=pd.Timestamp(TRADING_DAY), periods=rows)
    return pd.DataFrame(
        {
            "Open": 100.0,
            "High": 110.0,
            "Low": 90.0,
            "Close": 105.0,
            "Volume": 1000.0,
        },
        index=index,
    )


class FakeLoader:
    """``OhlcvDbClient`` fake. ticker -> DataFrame | OhlcvCacheStatus | Exception."""

    def __init__(self, mapping: dict[str, object], default: object | None = None) -> None:
        self._mapping = mapping
        self._default = default if default is not None else _frame()
        self.calls: list[tuple[str, date]] = []

    def load_ohlcv(self, ticker: str, cutoff: date):
        self.calls.append((ticker, cutoff))
        value = self._mapping.get(ticker, self._default)
        if isinstance(value, Exception):
            raise value
        return value


class FakeStrategyClient:
    """전략 A~H 마스크를 직접 지정하는 ``TagsClient`` fake.

    ``signals_by_ticker``는 ``{ticker: {strategy: 시그널 성립 여부}}``이며 성립은
    운영 태깅과 동일한 ``iloc[-1]``(당일 확정봉 -- "당일 봉이 최종봉" 원칙, Neo 확인,
    2026-09-16)에 True를 놓아 표현한다.
    """

    def __init__(
        self,
        signals_by_ticker: dict[str, dict[str, bool]] | None = None,
        *,
        overrides: dict[str, object] | None = None,
    ) -> None:
        self._signals = signals_by_ticker or {}
        self._overrides = overrides or {}
        self.calls: list[str] = []

    def compute(self, frame: pd.DataFrame, ticker: str) -> StrategyResult:
        self.calls.append(ticker)
        override = self._overrides.get(ticker)
        if isinstance(override, Exception):
            raise override
        if override is not None:
            return override
        wanted = self._signals.get(ticker, {})
        signals: dict[str, pd.Series] = {}
        for key in STRATEGY_KEYS:
            series = pd.Series(False, index=frame.index, dtype=bool)
            if wanted.get(key):
                series.iloc[-1] = True
            signals[key] = series
        return StrategyResult(
            ticker=ticker, status=OhlcvCacheStatus.READY, signals=signals, error=None
        )


class FakeProvider:
    def __init__(
        self,
        *,
        full_history: dict[str, object] | None = None,
        range_rows: dict[str, object] | None = None,
        pricechk_tickers: set[str] | None = None,
    ) -> None:
        self._full_history = full_history or {}
        self._range_rows = range_rows or {}
        self._pricechk_tickers = set(pricechk_tickers or ())
        self.full_history_calls: list[str] = []
        self.range_calls: list[tuple[str, object, date]] = []

    def _rows(self, count: int, start_day: int = 1, *, pricechk: int = 0) -> list[dict]:
        return [
            {
                "trading_day": date(2026, 1, 1) + timedelta(days=i + start_day),
                "open": 100,
                "high": 110,
                "low": 90,
                "close": 105,
                "volume": 1000,
                "pricechk": pricechk,
            }
            for i in range(count)
        ]

    def fetch_full_history(self, ticker: str, cutoff: date):
        self.full_history_calls.append(ticker)
        value = self._full_history.get(ticker, MIN_HISTORY_TRADING_DAYS)
        if isinstance(value, Exception):
            raise value
        return self._rows(int(value))

    def fetch_range(self, ticker: str, start, end: date):
        self.range_calls.append((ticker, start, end))
        value = self._range_rows.get(ticker, 1)
        if isinstance(value, Exception):
            raise value
        pricechk = 1 if ticker in self._pricechk_tickers else 0
        return self._rows(int(value), start_day=200, pricechk=pricechk)


class FakeRepository:
    """``SupabaseOhlcvCacheRepository`` fake -- **stateful**.

    운영 저장소는 실 테이블을 조회하므로 방금 초기 적재한 티커가 곧바로
    ``existing_tickers``/``latest_state``에 잡힌다. fake도 ``upsert_rows``를 상태에
    반영해야 백필의 두 패스 상호작용(review P2)을 실제와 같게 검증할 수 있다.
    """

    def __init__(
        self,
        *,
        existing: set[str] | None = None,
        states: dict[str, CachedTickerState] | None = None,
        upsert_errors: set[str] | None = None,
    ) -> None:
        self._existing = set(existing or ())
        self._states = dict(states or {})
        self._upsert_errors = set(upsert_errors or ())
        self.existing_calls: list[list[str]] = []
        self.latest_state_calls: list[list[str]] = []
        self.upserts: list[str] = []

    @staticmethod
    def _validate(tickers: list[str]) -> None:
        # 운영 검증기를 그대로 호출한다 -- 규칙을 재구현하면 실제 계약과 어긋날 수 있다.
        SupabaseOhlcvCacheRepository._validate_tickers(tickers)

    def existing_tickers(self, tickers: list[str]) -> set[str]:
        self._validate(tickers)
        self.existing_calls.append(list(tickers))
        return {t for t in tickers if t in self._existing}

    def latest_state(self, tickers: list[str]) -> dict[str, CachedTickerState]:
        self._validate(tickers)
        self.latest_state_calls.append(list(tickers))
        return {t: s for t, s in self._states.items() if t in tickers}

    def upsert_rows(self, ticker: str, rows: list[dict], *, adjustment_version: int = 1) -> None:
        if ticker in self._upsert_errors:
            raise RuntimeError(f"upsert failed: {ticker}")
        self.upserts.append(ticker)
        self._existing.add(ticker)
        if rows:
            last = max(rows, key=lambda r: r["trading_day"])
            self._states[ticker] = CachedTickerState(
                last_trading_day=last["trading_day"],
                last_close=last["close"],
                adjustment_version=adjustment_version,
            )


class CountingHeartbeat:
    def __init__(self) -> None:
        self.beats = 0

    def beat(self) -> None:
        self.beats += 1


# --- HAPPY_PATH -------------------------------------------------------------


def test_happy_path_all_ready_and_signals_from_confirmed_bar():
    tickers = ["000070", "005930", "035420"]
    loader = FakeLoader({t: _frame() for t in tickers})
    client = FakeStrategyClient(
        {
            "005930": {"A": True, "F": True},
            "035420": {"B": True},
        }
    )

    result = compute_universe_signals(
        loader, tickers, TRADING_DAY, strategy_client=client
    )

    assert result.trading_day == TRADING_DAY
    assert result.universe_size == 3
    assert result.ready_count == 3
    assert result.ineligible_count == 0
    assert result.error_count == 0
    assert set(result.strategy_signals) == set(STRATEGY_KEYS)
    assert result.strategy_signals["A"] == ["005930"]
    assert result.strategy_signals["B"] == ["035420"]
    assert result.strategy_signals["C"] == []
    assert result.strategy_signals["F"] == ["005930"]
    assert result.signal_count("A") == 1


def test_full_universe_fixture_yields_ready_count_104():
    """AC: 유니버스 전원 120거래일 이상 캐시된 거래일이면 ineligible=0."""
    universe = load_backtest_universe()
    loader = FakeLoader({}, default=_frame())
    client = FakeStrategyClient({universe[0]: {"A": True}})

    result = compute_universe_signals(loader, None, TRADING_DAY, strategy_client=client)

    assert result.universe_size == len(universe) == 104
    assert result.ready_count == 104
    assert result.ineligible_count == 0
    assert result.error_count == 0
    assert result.strategy_signals["A"] == [universe[0]]


def test_last_bar_signal_is_counted_under_same_day_final_bar_rule():
    """"당일 봉이 최종봉" 원칙(Neo 확인, 2026-09-16): ``iloc[-1]`` 시그널도 확정으로 센다."""
    loader = FakeLoader({"005930": _frame()})
    client = FakeStrategyClient({"005930": {"A": True}})

    result = compute_universe_signals(loader, ["005930"], TRADING_DAY, strategy_client=client)

    assert result.ready_count == 1
    assert result.strategy_signals["A"] == ["005930"]


def test_loader_receives_trading_day_as_cutoff():
    loader = FakeLoader({"005930": _frame()})
    compute_universe_signals(
        loader, ["005930"], TRADING_DAY, strategy_client=FakeStrategyClient()
    )
    assert loader.calls == [("005930", TRADING_DAY)]


def test_heartbeat_beats_once_per_ticker():
    heartbeat = CountingHeartbeat()
    compute_universe_signals(
        FakeLoader({}),
        ["000070", "005930"],
        TRADING_DAY,
        strategy_client=FakeStrategyClient(),
        heartbeat=heartbeat,
    )
    assert heartbeat.beats == 2


# --- SHORT_HISTORY ----------------------------------------------------------


def test_short_history_isolated_as_ineligible_from_loader_status():
    loader = FakeLoader(
        {
            "000070": OhlcvCacheStatus.INELIGIBLE_INSUFFICIENT_HISTORY,
            "005930": _frame(),
        }
    )
    client = FakeStrategyClient({"005930": {"A": True}})

    result = compute_universe_signals(
        loader, ["000070", "005930"], TRADING_DAY, strategy_client=client
    )

    assert result.ineligible_tickers == ["000070"]
    assert result.ready_tickers == ["005930"]
    assert result.error_count == 0
    assert result.strategy_signals["A"] == ["005930"]


def test_short_history_isolated_as_ineligible_from_compute_status():
    loader = FakeLoader({"000070": _frame(rows=50), "005930": _frame()})
    client = FakeStrategyClient(
        {"005930": {"A": True}},
        overrides={
            "000070": StrategyResult(
                ticker="000070",
                status=OhlcvCacheStatus.INELIGIBLE_INSUFFICIENT_HISTORY,
                signals={},
                error=None,
            )
        },
    )

    result = compute_universe_signals(
        loader, ["000070", "005930"], TRADING_DAY, strategy_client=client
    )

    assert result.ineligible_tickers == ["000070"]
    assert result.ready_tickers == ["005930"]
    assert result.strategy_signals["A"] == ["005930"]


def test_real_compute_abc_marks_short_history_ineligible():
    """기본 strategy_client는 ``compute_abc``다 -- 실 계산 경로로 이력부족을 확인한다."""
    loader = FakeLoader({"005930": _frame(rows=MIN_HISTORY_TRADING_DAYS - 1)})

    result = compute_universe_signals(loader, ["005930"], TRADING_DAY)

    assert result.ineligible_tickers == ["005930"]
    assert result.ready_count == 0
    assert result.error_count == 0
    assert all(result.strategy_signals[key] == [] for key in STRATEGY_KEYS)


# --- LOAD_ERROR -------------------------------------------------------------


def test_load_error_status_isolated_per_ticker():
    loader = FakeLoader({"000070": OhlcvCacheStatus.ERROR, "005930": _frame()})
    client = FakeStrategyClient({"005930": {"C": True}})

    result = compute_universe_signals(
        loader, ["000070", "005930"], TRADING_DAY, strategy_client=client
    )

    assert result.error_tickers == ["000070"]
    assert result.ready_tickers == ["005930"]
    assert result.strategy_signals["C"] == ["005930"]


def test_load_exception_isolated_per_ticker():
    loader = FakeLoader({"000070": RuntimeError("boom"), "005930": _frame()})
    client = FakeStrategyClient({"005930": {"C": True}})

    result = compute_universe_signals(
        loader, ["000070", "005930"], TRADING_DAY, strategy_client=client
    )

    assert result.error_tickers == ["000070"]
    assert result.ready_tickers == ["005930"]


# --- COMPUTE_ERROR ----------------------------------------------------------


def test_compute_error_status_does_not_partially_apply_strategy_keys():
    error_signals = {
        key: pd.Series([False, True], index=pd.bdate_range("2026-09-07", periods=2))
        for key in STRATEGY_KEYS
    }
    client = FakeStrategyClient(
        {"005930": {"A": True}},
        overrides={
            "000070": StrategyResult(
                ticker="000070",
                status=OhlcvCacheStatus.ERROR,
                signals=error_signals,
                error=None,
            )
        },
    )
    loader = FakeLoader({})

    result = compute_universe_signals(
        loader, ["000070", "005930"], TRADING_DAY, strategy_client=client
    )

    assert result.error_tickers == ["000070"]
    assert result.strategy_signals["A"] == ["005930"]
    for key in STRATEGY_KEYS:
        assert "000070" not in result.strategy_signals[key]


def test_compute_error_field_set_counts_as_error():
    from backtest.strategy_api import StrategyError, StrategyErrorCode

    client = FakeStrategyClient(
        overrides={
            "000070": StrategyResult(
                ticker="000070",
                status=OhlcvCacheStatus.READY,
                signals={},
                error=StrategyError(
                    code=StrategyErrorCode.SIGNAL_COMPUTE_ERROR,
                    strategy=None,
                    message="bad",
                ),
            )
        }
    )
    result = compute_universe_signals(
        FakeLoader({}), ["000070"], TRADING_DAY, strategy_client=client
    )
    assert result.error_tickers == ["000070"]
    assert result.ready_count == 0


def test_compute_exception_isolated_per_ticker():
    client = FakeStrategyClient(
        {"005930": {"A": True}}, overrides={"000070": ValueError("kaboom")}
    )
    result = compute_universe_signals(
        FakeLoader({}), ["000070", "005930"], TRADING_DAY, strategy_client=client
    )
    assert result.error_tickers == ["000070"]
    assert result.ready_tickers == ["005930"]


# --- REPRODUCIBLE -----------------------------------------------------------


def test_same_cache_and_trading_day_produces_identical_result():
    tickers = ["035420", "000070", "005930"]  # 입력 순서가 뒤섞여 있어도 결정론적
    signals = {"005930": {"A": True, "B": True}, "035420": {"A": True}}

    first = compute_universe_signals(
        FakeLoader({}), tickers, TRADING_DAY, strategy_client=FakeStrategyClient(signals)
    )
    second = compute_universe_signals(
        FakeLoader({}), list(reversed(tickers)), TRADING_DAY,
        strategy_client=FakeStrategyClient(signals),
    )

    assert first.strategy_signals == second.strategy_signals
    assert first.strategy_signals["A"] == ["005930", "035420"]  # 정렬됨
    assert first.ready_tickers == second.ready_tickers == ["000070", "005930", "035420"]


def test_duplicate_input_tickers_are_deduped():
    result = compute_universe_signals(
        FakeLoader({}),
        ["005930", "005930.KS", "005930"],
        TRADING_DAY,
        strategy_client=FakeStrategyClient({"005930": {"A": True}}),
    )
    assert result.universe_size == 1
    assert result.strategy_signals["A"] == ["005930"]


# --- BACKFILL_TICKER_FORM ---------------------------------------------------


def test_ks_suffix_is_normalized_before_repository_validation():
    """fixture의 ``.KS`` 티커가 들어와도 6자리 코드로 정규화되어야 한다."""
    provider = FakeProvider()
    repository = FakeRepository()

    result = backfill_universe_ohlcv(
        provider, repository, TRADING_DAY, tickers=["005930.KS", "000070.KS"]
    )

    assert result.tickers == ["000070", "005930"]
    assert repository.existing_calls == [["000070", "005930"]]
    assert all(t.isalnum() for t in repository.existing_calls[0])
    assert provider.full_history_calls == ["000070", "005930"]


def test_signal_computation_also_normalizes_ks_suffix():
    loader = FakeLoader({})
    compute_universe_signals(
        loader, ["005930.KS"], TRADING_DAY, strategy_client=FakeStrategyClient()
    )
    assert loader.calls == [("005930", TRADING_DAY)]


@pytest.mark.parametrize("bad", ["A05930.KS", "abcdef", "5930", ""])
def test_unnormalizable_ticker_raises_at_load_time(bad):
    with pytest.raises(BacktestUniverseFixtureError):
        compute_universe_signals(
            FakeLoader({}), [bad], TRADING_DAY, strategy_client=FakeStrategyClient()
        )
    with pytest.raises(BacktestUniverseFixtureError):
        backfill_universe_ohlcv(FakeProvider(), FakeRepository(), TRADING_DAY, tickers=[bad])


# --- BACKFILL_INDEPENDENT ---------------------------------------------------


def test_backfill_runs_regardless_of_candidate_membership():
    """AC: 후보 모집단에 하나도 없는 유니버스 종목도 적재/갱신이 시도된다."""
    provider = FakeProvider()
    repository = FakeRepository(
        states={"000070": CachedTickerState(date(2026, 9, 1), 100.0, 1)},
        existing={"000070"},
    )

    result = backfill_universe_ohlcv(
        provider, repository, TRADING_DAY, tickers=["000070", "005930", "035420"]
    )

    # 미캐시 2종목은 전체 이력 적재, 캐시된 1종목은 증분 갱신
    assert provider.full_history_calls == ["005930", "035420"]
    assert [c[0] for c in provider.range_calls] == ["000070"]
    assert result.universe_size == 3
    assert set(result.results) == {"000070", "005930", "035420"}
    assert result.ready_count == 3
    assert result.error_count == 0


def test_backfill_defaults_to_full_fixture_universe():
    provider = FakeProvider()
    repository = FakeRepository()

    result = backfill_universe_ohlcv(provider, repository, TRADING_DAY)

    assert result.tickers == load_backtest_universe()
    assert len(provider.full_history_calls) == 104


def test_backfill_isolates_per_ticker_failures():
    provider = FakeProvider(
        full_history={
            "005930": RuntimeError("LS down"),
            "035420": MIN_HISTORY_TRADING_DAYS - 10,  # 미저장 INELIGIBLE
        }
    )
    repository = FakeRepository()

    result = backfill_universe_ohlcv(
        provider, repository, TRADING_DAY, tickers=["000070", "005930", "035420"]
    )

    results = result.results
    assert results["000070"].status is OhlcvCacheStatus.READY
    assert results["005930"].status is OhlcvCacheStatus.ERROR
    assert results["035420"].status is OhlcvCacheStatus.INELIGIBLE_INSUFFICIENT_HISTORY
    assert (result.ready_count, result.error_count, result.ineligible_count) == (1, 1, 1)
    assert repository.upserts == ["000070"]


def test_backfill_surfaces_no_flags_when_nothing_is_flagged():
    provider = FakeProvider(range_rows={"000070": 2})
    repository = FakeRepository(
        existing={"000070"},
        states={"000070": CachedTickerState(date(2026, 9, 1), 105.0, 1)},
    )
    heartbeat = CountingHeartbeat()

    result = backfill_universe_ohlcv(
        provider, repository, TRADING_DAY, tickers=["000070"], heartbeat=heartbeat
    )

    assert result.results["000070"].status is OhlcvCacheStatus.READY
    assert result.adjustment_flags == []
    # 종목당 정확히 1회(증분 패스만 -- 초기 적재 대상이 아니다)
    assert heartbeat.beats == 1


def test_backfill_surfaces_pricechk_adjustment_flags_per_ticker_and_date():
    """AC 보강(review P5): 실제로 flag가 붙은 행이 ticker/date와 함께 노출돼야 한다."""
    provider = FakeProvider(range_rows={"000070": 2}, pricechk_tickers={"000070"})
    repository = FakeRepository(
        existing={"000070"},
        states={"000070": CachedTickerState(date(2026, 9, 1), 105.0, 1)},
    )

    result = backfill_universe_ohlcv(provider, repository, TRADING_DAY, tickers=["000070"])

    assert result.results["000070"].status is OhlcvCacheStatus.READY
    flags = result.adjustment_flags
    assert len(flags) == 2, flags
    assert {f.ticker for f in flags} == {"000070"}
    assert all(f.pricechk for f in flags)
    # 증분 조회가 돌려준 두 거래일이 그대로 flag의 date로 노출된다.
    assert sorted(f.trading_day for f in flags) == [date(2026, 7, 20), date(2026, 7, 21)]
    # corporate action이므로 전체 재조회 + adjustment_version 증가가 뒤따른다.
    assert [c[1] for c in provider.range_calls] == [date(2026, 9, 2), None]


def test_backfill_surfaces_gap_adjustment_flags_without_pricechk():
    """±30% 초과 갭만으로도 flag가 노출된다(pricechk는 0)."""
    provider = FakeProvider(range_rows={"000070": 1})
    repository = FakeRepository(
        existing={"000070"},
        # 직전 종가 10.0 -> 신규 종가 105.0: 갭 +950%
        states={"000070": CachedTickerState(date(2026, 9, 1), 10.0, 1)},
    )

    result = backfill_universe_ohlcv(provider, repository, TRADING_DAY, tickers=["000070"])

    assert len(result.adjustment_flags) == 1
    flag = result.adjustment_flags[0]
    assert flag.ticker == "000070"
    assert flag.pricechk is False
    assert flag.gap_pct > 0.3
    # pricechk가 없으므로 재조회는 없다(증분 1회뿐).
    assert len(provider.range_calls) == 1


# --- BACKFILL_TWO_PASS (review P2/P3) ---------------------------------------


def test_backfill_does_not_re_update_tickers_initialized_in_this_run():
    """이번 실행에서 초기 적재된 티커는 증분 패스에서 제외된다.

    운영 저장소는 실 테이블을 조회하므로(=stateful fake) 제외하지 않으면 초기 적재의
    실제 row_count가 증분의 ``READY row_count=0``으로 덮이고, 티커당 불필요한
    ``fetch_range``가 한 번 더 나간다(review P2).
    """
    provider = FakeProvider(range_rows={"000070": 3})
    repository = FakeRepository(
        existing={"000070"},
        states={"000070": CachedTickerState(date(2026, 9, 1), 105.0, 1)},
    )

    result = backfill_universe_ohlcv(
        provider, repository, TRADING_DAY, tickers=["000070", "005930", "035420"]
    )

    # 신규 2종목은 전체 이력만, 기존 1종목은 증분만 -- 서로 겹치지 않는다.
    assert provider.full_history_calls == ["005930", "035420"]
    assert [c[0] for c in provider.range_calls] == ["000070"]
    assert set(result.initialized) == {"005930", "035420"}
    assert set(result.updated) == {"000070"}

    results = result.results
    assert set(results) == {"000070", "005930", "035420"}
    # 초기 적재 row_count가 증분의 0으로 덮이지 않는다.
    assert results["005930"].trading_days == MIN_HISTORY_TRADING_DAYS
    assert results["035420"].trading_days == MIN_HISTORY_TRADING_DAYS
    assert results["000070"].trading_days == 3
    assert (result.ready_count, result.ineligible_count, result.error_count) == (3, 0, 0)
    assert repository.upserts == ["005930", "035420", "000070"]


def test_backfill_buckets_sum_to_universe_size_even_with_missing_results():
    """어느 패스에도 결과가 없는 티커는 사라지지 않고 명시적 ERROR로 드러난다(review P3)."""

    class InconsistentRepository(FakeRepository):
        # existing_tickers는 "있다"고 하지만 latest_state에는 없는 불일치 상태.
        def existing_tickers(self, tickers: list[str]) -> set[str]:
            super().existing_tickers(tickers)
            return set(tickers)

    provider = FakeProvider()
    repository = InconsistentRepository()

    result = backfill_universe_ohlcv(
        provider, repository, TRADING_DAY, tickers=["000070", "005930"]
    )

    assert provider.full_history_calls == []
    assert set(result.results) == {"000070", "005930"}
    assert all(
        r.status is OhlcvCacheStatus.ERROR and "누락" in r.message
        for r in result.results.values()
    )
    assert (
        result.ready_count + result.ineligible_count + result.error_count
        == result.universe_size
        == 2
    )


def test_backfill_buckets_sum_to_universe_size_in_mixed_run():
    provider = FakeProvider(
        full_history={
            "005930": RuntimeError("LS down"),
            "035420": MIN_HISTORY_TRADING_DAYS - 10,
        }
    )
    repository = FakeRepository(
        existing={"000070"},
        states={"000070": CachedTickerState(date(2026, 9, 1), 105.0, 1)},
    )

    result = backfill_universe_ohlcv(
        provider, repository, TRADING_DAY, tickers=["000070", "005930", "035420"]
    )

    assert (
        result.ready_count + result.ineligible_count + result.error_count
        == result.universe_size
        == 3
    )


def test_backfill_with_empty_universe_is_a_noop():
    provider = FakeProvider()
    repository = FakeRepository()

    result = backfill_universe_ohlcv(provider, repository, TRADING_DAY, tickers=[])

    assert result.tickers == []
    assert result.results == {}
    assert provider.full_history_calls == []
    assert repository.existing_calls == []


# --- 범위 경계(5.4/5.3으로 미룬 것) ----------------------------------------


def test_module_does_not_write_bias_tables_or_stages():
    from pathlib import Path

    source = (
        Path(__file__).resolve().parents[2] / "apps" / "batch" / "universe_signal.py"
    ).read_text(encoding="utf-8")
    for forbidden in ("write_stage", "Stage.", "rest/v1", "run_state"):
        assert forbidden not in source, forbidden


# --- 버킷 불변식 / 빈 유니버스 (review P3, P9a) ------------------------------


def test_signal_buckets_sum_to_universe_size():
    """모든 종목은 ready/ineligible/error 중 정확히 하나에 들어간다."""
    loader = FakeLoader(
        {
            "000070": OhlcvCacheStatus.INELIGIBLE_INSUFFICIENT_HISTORY,
            "005930": _frame(),
            "035420": RuntimeError("boom"),
            "051910": OhlcvCacheStatus.ERROR,
        }
    )
    tickers = ["000070", "005930", "035420", "051910"]

    result = compute_universe_signals(
        loader, tickers, TRADING_DAY, strategy_client=FakeStrategyClient()
    )

    assert (
        result.ready_count + result.ineligible_count + result.error_count
        == result.universe_size
        == 4
    )
    buckets = result.ready_tickers + result.ineligible_tickers + result.error_tickers
    assert sorted(buckets) == tickers
    assert len(set(buckets)) == len(buckets)


def test_compute_with_empty_universe_returns_empty_result():
    """빈 유니버스: 로더를 부르지 않고 6개 전략 키가 모두 빈 리스트로 나온다."""
    loader = FakeLoader({})

    result = compute_universe_signals(
        loader, [], TRADING_DAY, strategy_client=FakeStrategyClient()
    )

    assert result.universe_size == 0
    assert result.trading_day == TRADING_DAY
    assert loader.calls == []
    assert set(result.strategy_signals) == set(STRATEGY_KEYS)
    assert all(result.strategy_signals[key] == [] for key in STRATEGY_KEYS)
    assert result.ready_tickers == result.ineligible_tickers == result.error_tickers == []
    assert result.signal_dates == {}
    assert result.latest_signal_date is None
    assert result.stale_signal_date_tickers == []
    assert result.ready_count + result.ineligible_count + result.error_count == 0


# --- 확정 시그널 봉 날짜 (review P4) ----------------------------------------


def _frame_ending(last_day: date, rows: int = MIN_HISTORY_TRADING_DAYS + 5) -> pd.DataFrame:
    index = pd.bdate_range(end=pd.Timestamp(last_day), periods=rows)
    return pd.DataFrame(
        {"Open": 100.0, "High": 110.0, "Low": 90.0, "Close": 105.0, "Volume": 1000.0},
        index=index,
    )


def test_signal_dates_expose_the_actual_confirmed_bar_per_ticker():
    """캐시가 뒤처진 종목은 다른 달력일의 봉으로 판정되므로 그 날짜를 노출해야 한다.

    "당일 봉이 최종봉" 원칙(Neo 확인, 2026-09-16)에 따라 확정봉은 각 종목 프레임의
    마지막 행(``iloc[-1]``) 그 자체다 -- 더 이상 하루 전으로 미루지 않는다.
    """
    stale_last_day = date(2026, 8, 26)  # 요청 거래일보다 열흘 이상 이르다
    loader = FakeLoader(
        {
            "005930": _frame(),  # TRADING_DAY까지 최신
            "000070": _frame_ending(stale_last_day),  # 뒤처진 캐시
        }
    )
    client = FakeStrategyClient({"005930": {"A": True}, "000070": {"A": True}})

    result = compute_universe_signals(
        loader, ["000070", "005930"], TRADING_DAY, strategy_client=client
    )

    # 최신 캐시 종목의 확정봉 = 요청 거래일 그 자체(당일 봉이 최종봉)
    assert result.signal_dates == {"000070": stale_last_day, "005930": TRADING_DAY}
    # 뒤처짐 기준선은 요청 거래일이 아니라 유니버스가 실제 도달한 최신 확정봉이다.
    assert result.latest_signal_date == TRADING_DAY
    assert result.stale_signal_date_tickers == ["000070"]
    assert result.strategy_signals["A"] == ["000070", "005930"]


def test_uniformly_fresh_universe_reports_no_stale_ticker():
    """모든 종목이 같은 확정봉(=요청 거래일)을 보고 있으면 stale 목록은 비어 있다."""
    result = compute_universe_signals(
        FakeLoader({"005930": _frame(), "000070": _frame()}),
        ["000070", "005930"],
        TRADING_DAY,
        strategy_client=FakeStrategyClient(),
    )

    assert result.signal_dates == {"000070": TRADING_DAY, "005930": TRADING_DAY}
    assert result.latest_signal_date == TRADING_DAY
    assert result.stale_signal_date_tickers == []


def test_signal_dates_only_cover_ready_tickers():
    loader = FakeLoader(
        {
            "000070": OhlcvCacheStatus.INELIGIBLE_INSUFFICIENT_HISTORY,
            "005930": _frame(),
        }
    )
    result = compute_universe_signals(
        loader, ["000070", "005930"], TRADING_DAY, strategy_client=FakeStrategyClient()
    )
    assert set(result.signal_dates) == {"005930"}


# --- 실 커널(compute_abc) 비어있지 않은 시그널 (review P6) -------------------


def test_real_compute_abc_yields_non_empty_signals_from_golden_data():
    """실데이터 + 실 ``compute_abc``로 (a) 비어있지 않은 시그널 (b) exclude_terminal_bar 구분.

    golden fixture(`tests/fixtures/golden/ohlcv_raw.json.gz`)에서 ``180640``의 전략 F
    조건은 **2026-08-25**에 성립하고 2026-08-26에는 성립하지 않는다(크로스 시점 자체가
    08-25라 다음날엔 조건이 자연히 꺼진다 -- "지연"이 아니라 조건 자체가 그 날짜에만
    참이다). 백테스트 커널 기본값(``exclude_terminal_bar=True``)에서는 08-26까지의
    데이터 중 08-25가 ``iloc[-2]``로 확정되고 마지막 행(08-26, ``iloc[-1]``)은 폐기된다.
    반면 "당일 봉이 최종봉" 원칙(``exclude_terminal_bar=False`` -- 운영 태깅 기본,
    Neo 확인 2026-09-16)에서는 08-25가 실제로 프레임의 마지막 행일 때(=cutoff가
    08-25일 때) 그 시그널이 그대로 확정된다.
    """
    import gzip
    import json
    from pathlib import Path

    from backtest.strategy_api import compute_abc

    golden_day = date(2026, 8, 26)
    signal_day = date(2026, 8, 25)
    raw_path = (
        Path(__file__).resolve().parents[1] / "fixtures" / "golden" / "ohlcv_raw.json.gz"
    )
    with gzip.open(raw_path, "rb") as handle:
        ohlcv = json.loads(handle.read().decode("utf-8"))["ohlcv"]

    def frame_of(yahoo_ticker: str) -> pd.DataFrame:
        columns = ohlcv[yahoo_ticker]
        return pd.DataFrame(
            {
                "Open": columns["open"],
                "High": columns["high"],
                "Low": columns["low"],
                "Close": columns["close"],
                "Volume": columns["volume"],
            },
            index=pd.DatetimeIndex(pd.to_datetime(pd.Series(columns["trading_day"]))),
        )

    signal_ticker = "180640"
    frames_full = {t: frame_of(f"{t}.KS") for t in (signal_ticker, "005930", "000070")}

    # (b) 커널 기본값(exclude_terminal_bar=True, 백테스트 규칙)에서는 08-25가
    # iloc[-2]로 확정되고 08-26(iloc[-1], 마지막 행)은 폐기된다.
    kernel = compute_abc(frames_full[signal_ticker], ticker=signal_ticker)
    assert kernel.status is OhlcvCacheStatus.READY, kernel.error
    assert bool(kernel.signals["F"].iloc[-2]) is True
    assert bool(kernel.signals["F"].iloc[-1]) is False
    assert frames_full[signal_ticker].index[-1].date() == golden_day

    # (a) "당일 봉이 최종봉" 원칙(기본 strategy_client=DefaultStrategyClient,
    # exclude_terminal_bar=False)에서는 cutoff=08-25로 로드된 프레임(08-25가 마지막
    # 행)을 줘야 그날 확정된 시그널이 그대로 잡힌다 -- 운영에서 그날의 daily_ohlcv
    # 로더가 실제로 반환하는 모양과 같다.
    frames_up_to_signal_day = {
        t: frame[frame.index <= pd.Timestamp(signal_day)] for t, frame in frames_full.items()
    }
    assert frames_up_to_signal_day[signal_ticker].index[-1].date() == signal_day

    result = compute_universe_signals(
        FakeLoader(dict(frames_up_to_signal_day)), list(frames_up_to_signal_day), signal_day
    )

    assert result.ready_count == 3
    assert result.error_count == 0
    assert result.strategy_signals["F"] == [signal_ticker]
    assert any(result.strategy_signals[key] for key in STRATEGY_KEYS)
    assert result.signal_dates[signal_ticker] == signal_day


# --- 상수 단일 원천 / 캐시 탈출구 (review P8, P9b) ---------------------------


def test_strategy_keys_match_strategy_api_single_source():
    from backtest.strategy_api import _STRATEGY_KEYS

    assert tuple(STRATEGY_KEYS) == tuple(_STRATEGY_KEYS)


def test_universe_fixture_cache_can_be_cleared(tmp_path, monkeypatch):
    """``_cached_tickers``는 키 없는 lru_cache라 재생성 후 캐시를 비워야 새 값이 보인다."""
    import apps.batch.backtest_universe as bu

    original = load_backtest_universe()
    assert len(original) == 104

    payload = {
        "source_of_truth": bu.EXPECTED_SOURCE_OF_TRUTH,
        "count": 1,
        "tickers": [{"code": "005930", "yahoo_ticker": "005930.KS"}],
    }
    fake_fixture = tmp_path / "backtest_universe.json"
    fake_fixture.write_text(str(payload).replace("'", '"'), encoding="utf-8")
    monkeypatch.setattr(bu, "FIXTURE_PATH", fake_fixture)

    # 캐시를 비우지 않으면 낡은 값이 그대로 보인다.
    assert bu.load_backtest_universe() == original

    bu.clear_universe_cache()
    try:
        assert bu.load_backtest_universe() == ["005930"]
    finally:
        monkeypatch.undo()
        bu.clear_universe_cache()

    assert bu.load_backtest_universe() == original
