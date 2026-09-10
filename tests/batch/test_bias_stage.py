from datetime import date
from types import SimpleNamespace
from uuid import uuid4

import pytest

from apps.batch import bias_stage as module
from apps.batch.ohlcv_cache import OhlcvCacheResult
from apps.batch.universe_signal import UniverseBackfillResult, UniverseSignalResult
from domain.ohlcv_cache import OhlcvCacheStatus

DAY = date(2026, 9, 10)


class Gateway:
    def __init__(self, fail=False):
        self.calls = []
        self.fail = fail

    def write_stage(self, *args, **kwargs):
        self.calls.append((args, kwargs))
        if self.fail:
            raise RuntimeError("stage write failed")


class Repository:
    def __init__(self, failure=None):
        self.failure = failure
        self.saved = []

    def fetch_population(self, *args):
        if self.failure == "read":
            raise RuntimeError("read failed")
        return []

    def append(self, *args):
        if self.failure == "append":
            raise RuntimeError("append failed")
        self.saved.append(args)


def setup(monkeypatch, *, backfill_error=False, ineligible=False, stale=False):
    calls = []

    def backfill(provider, repository, day, *, tickers=None):
        calls.append(tickers)
        requested = ["005930"] if tickers is None else tickers
        return UniverseBackfillResult(requested, initialized={
            t: OhlcvCacheResult(t, OhlcvCacheStatus.ERROR if backfill_error else OhlcvCacheStatus.READY, 120)
            for t in requested})

    def signals(loader, tickers, day, *, strategy_client=None):
        return UniverseSignalResult(day, 1, {"A": [] if ineligible else ["005930"]},
                                    ready_tickers=[] if ineligible else ["005930"],
                                    ineligible_tickers=["005930"] if ineligible else [],
                                    signal_dates={"005930": None if stale else date(2026, 9, 9)})

    monkeypatch.setattr(module, "backfill_universe_ohlcv", backfill)
    monkeypatch.setattr(module, "compute_universe_signals", signals)
    return calls


def run(gateway, repository, truncated=()):
    return module.run_bias_stage(gateway, repository, object(), object(), object(),
                                 "run", 1, "lease", DAY, truncated)


def test_empty_population_keeps_real_universe_and_three_sources(monkeypatch):
    calls = setup(monkeypatch)
    repository = Repository()
    result = run(Gateway(), repository)
    assert result.status == "success"
    assert calls == [None, []]  # 独立 백필, heartbeat 인자 자체가 없다.
    metrics = repository.saved[0][-2]
    assert len(metrics.as_rows()) == 3
    assert all(row.candidate_pop_signal_count == 0 and row.backtest_universe_signal_count == 1
               for row in metrics.by_source)


@pytest.mark.parametrize("options", [{"backfill_error": True}, {"ineligible": True}, {"stale": True}])
def test_partial_inputs_are_not_success_zero(monkeypatch, options):
    setup(monkeypatch, **options)
    repository = Repository()
    assert run(Gateway(), repository).status == "partial"
    assert repository.saved[0][-2].calculation_meta["status"] == "partial"


def test_alphanumeric_truncation_is_isolated_and_exposed(monkeypatch):
    calls = setup(monkeypatch)
    repository = Repository()
    result = run(Gateway(), repository, [SimpleNamespace(ticker="00088K", sources=())])
    assert result.status == "partial"
    assert calls == [None, []]
    assert repository.saved[0][-2].calculation_meta["truncated_attribution"]["unnormalizable_tickers"] == ["00088K"]


def test_numeric_truncation_is_independently_backfilled_and_load_error_is_partial(monkeypatch):
    calls = setup(monkeypatch)
    repository = Repository()
    result = run(Gateway(), repository, [SimpleNamespace(ticker="000660", sources=())])
    assert calls == [None, ["000660"]]
    assert result.status == "partial"
    assert repository.saved[0][-2].calculation_meta["truncated"]["error_tickers"] == ["000660"]


@pytest.mark.parametrize("failure", ["read", "append", "backfill", "compute"])
def test_stage_errors_are_isolated_and_failed_is_recorded(monkeypatch, failure):
    setup(monkeypatch)
    def fail(*args, **kwargs):
        raise RuntimeError("boom")
    if failure in ("backfill", "compute"):
        monkeypatch.setattr(module, "backfill_universe_ohlcv" if failure == "backfill" else "compute_bias_metrics", fail)
    gateway = Gateway()
    result = run(gateway, Repository(failure))
    assert result.status == "failed" and result.failure_recorded
    assert gateway.calls[-1][0][4:6] == ("running", "failed")


def test_failure_record_exception_also_isolated():
    result = run(Gateway(fail=True), Repository("read"))
    assert result.status == "failed" and not result.failure_recorded


def test_success_does_not_prewrite_running_before_idempotent_append(monkeypatch):
    setup(monkeypatch)
    gateway = Gateway()
    repository = Repository()
    event_id = uuid4()
    for _ in range(2):
        result = module.run_bias_stage(gateway, repository, object(), object(), object(),
                                       "run", 1, "lease", DAY, event_id=event_id)
        assert result.status == "success"
    assert gateway.calls == []
    assert repository.saved[0] == repository.saved[1]
