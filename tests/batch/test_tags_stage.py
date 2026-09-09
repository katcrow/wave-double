from datetime import date, datetime, timezone
from uuid import uuid4

import pandas as pd
import pytest

from apps.batch.candidate_tags_repository import CandidateTag
from apps.batch.run_state import RunStateGateway
from apps.batch.tags_stage import TaggedCandidate, run_tags_stage
from backtest.indicator_opt.strategy_d import STRATEGY_D_PARAMS
from backtest.indicator_opt.strategy_e import STRATEGY_E_PARAMS
from backtest.indicator_opt.strategy_f import STRATEGY_F_PARAMS
from backtest.strategy_api import StrategyError, StrategyErrorCode, StrategyResult
from domain.ohlcv_cache import OhlcvCacheStatus


class FakeRpc:
    def __init__(self):
        self.calls = []

    def rpc(self, function, params):
        self.calls.append((function, params))
        return {"ok": True}


class FakeCandidateRow:
    def __init__(self, candidate_id, ticker):
        self.candidate_id = candidate_id
        self.ticker = ticker


class FakeCandidateFetcher:
    def __init__(self, rows=None, error=None):
        self.rows = rows if rows is not None else []
        self.error = error
        self.calls = []

    def fetch(self, run_id):
        self.calls.append(run_id)
        if self.error is not None:
            raise self.error
        return self.rows


class FakeOhlcvLoader:
    def __init__(self, by_ticker):
        self.by_ticker = by_ticker
        self.calls = []

    def load_ohlcv(self, ticker, cutoff):
        self.calls.append((ticker, cutoff))
        return self.by_ticker[ticker]


class FakeStrategyClient:
    def __init__(self, by_ticker):
        self.by_ticker = by_ticker
        self.calls = []

    def compute(self, frame, ticker):
        self.calls.append(ticker)
        outcome = self.by_ticker[ticker]
        if isinstance(outcome, Exception):
            raise outcome
        return outcome


class FakeTagsRepository:
    def __init__(self, fail=False, *, sync_vanished_fail=False, vanished_count=0, fail_candidate_ids=None):
        self.fail = fail
        self.sync_vanished_fail = sync_vanished_fail
        self.vanished_count = vanished_count
        self.fail_candidate_ids = set(fail_candidate_ids or [])
        self.saved: list[CandidateTag] = []
        self.sync_vanished_calls: list[str] = []

    def upsert_tags(self, tags):
        if self.fail:
            raise RuntimeError("supabase upsert failed")
        if tags and tags[0].candidate_id in self.fail_candidate_ids:
            raise RuntimeError(f"supabase upsert failed for {tags[0].candidate_id}")
        self.saved.extend(tags)
        return len(tags)

    def sync_vanished(self, run_id):
        self.sync_vanished_calls.append(run_id)
        if self.sync_vanished_fail:
            raise RuntimeError("sync_vanished_tags rpc failed")
        return {"vanished_count": self.vanished_count}


def _frame(n: int = 3, *, last_signal_at_minus2: bool = False) -> pd.DataFrame:
    idx = pd.date_range("2026-08-01", periods=n, freq="D")
    return pd.DataFrame(
        {"Open": [1.0] * n, "High": [1.0] * n, "Low": [1.0] * n, "Close": [1.0] * n, "Volume": [1.0] * n},
        index=idx,
    )


def _signals(n: int, *, a_at_minus2: bool = False) -> dict[str, pd.Series]:
    idx = pd.date_range("2026-08-01", periods=n, freq="D")
    a = pd.Series(False, index=idx)
    if a_at_minus2:
        a.iloc[-2] = True
    b = pd.Series(False, index=idx)
    c = pd.Series(False, index=idx)
    return {"A": a, "B": b, "C": c}


def _ready_result(ticker: str, n: int, *, a_at_minus2: bool = False) -> StrategyResult:
    return StrategyResult(ticker=ticker, status=OhlcvCacheStatus.READY, signals=_signals(n, a_at_minus2=a_at_minus2), error=None)


def _error_result(ticker: str) -> StrategyResult:
    return StrategyResult(
        ticker=ticker, status=OhlcvCacheStatus.ERROR, signals={},
        error=StrategyError(code=StrategyErrorCode.SIGNAL_COMPUTE_ERROR, strategy=None, message="boom"),
    )


def _run(rpc, candidate_fetcher, ohlcv_loader, tags_repo, strategy_client, *, batch_kind="close"):
    gateway = RunStateGateway(rpc)
    run_id = uuid4()
    lease_token = uuid4()
    return run_tags_stage(
        gateway, candidate_fetcher, ohlcv_loader, tags_repo,
        run_id, 1, lease_token, date(2026, 9, 1),
        strategy_client=strategy_client, batch_kind=batch_kind,
    )


# --- I/O & Edge-Case Matrix --------------------------------------------------


def test_normal_tagging_all_ready_with_signal_is_success():
    frame = _frame(3)
    fetcher = FakeCandidateFetcher([FakeCandidateRow("c1", "005930")])
    loader = FakeOhlcvLoader({"005930": frame})
    strategy = FakeStrategyClient({"005930": _ready_result("005930", 3, a_at_minus2=True)})
    tags_repo = FakeTagsRepository()
    rpc = FakeRpc()

    result = _run(rpc, fetcher, loader, tags_repo, strategy)

    assert result.status == "success"
    assert result.result_code == "OK"
    assert result.tagged_count == 1
    assert result.error_count == 0
    assert result.ineligible_count == 0
    assert len(tags_repo.saved) == 1
    assert tags_repo.saved[0].strategy == "A"
    write_stage_calls = [c for c in rpc.calls if c[0] == "write_stage"]
    assert [c[1]["p_status"] for c in write_stage_calls] == ["running", "success"]
    assert write_stage_calls[-1][1]["p_unprocessed_count"] == 0


def test_partial_signal_compute_error_on_one_ticker_others_still_saved():
    frame = _frame(3)
    fetcher = FakeCandidateFetcher([FakeCandidateRow("c1", "005930"), FakeCandidateRow("c2", "000660")])
    loader = FakeOhlcvLoader({"005930": frame, "000660": frame})
    strategy = FakeStrategyClient({
        "005930": _error_result("005930"),
        "000660": _ready_result("000660", 3, a_at_minus2=True),
    })
    tags_repo = FakeTagsRepository()
    rpc = FakeRpc()

    result = _run(rpc, fetcher, loader, tags_repo, strategy)

    assert result.status == "partial"
    assert result.result_code == "PARTIAL_TAGGING"
    assert result.error_count == 1
    assert result.tagged_count == 1
    assert len(tags_repo.saved) == 1
    write_stage_calls = [c for c in rpc.calls if c[0] == "write_stage"]
    assert write_stage_calls[-1][1]["p_status"] == "partial"
    assert write_stage_calls[-1][1]["p_unprocessed_count"] == 1


def test_insufficient_history_is_ineligible_not_error_and_stage_stays_success():
    frame = _frame(3)
    fetcher = FakeCandidateFetcher([FakeCandidateRow("c1", "005930"), FakeCandidateRow("c2", "000660")])
    loader = FakeOhlcvLoader({
        "005930": OhlcvCacheStatus.INELIGIBLE_INSUFFICIENT_HISTORY,
        "000660": frame,
    })
    strategy = FakeStrategyClient({"000660": _ready_result("000660", 3, a_at_minus2=True)})
    tags_repo = FakeTagsRepository()
    rpc = FakeRpc()

    result = _run(rpc, fetcher, loader, tags_repo, strategy)

    assert result.status == "success"
    assert result.error_count == 0
    assert result.ineligible_count == 1
    assert result.tagged_count == 1
    write_stage_calls = [c for c in rpc.calls if c[0] == "write_stage"]
    assert write_stage_calls[-1][1]["p_status"] == "success"
    assert write_stage_calls[-1][1]["p_unprocessed_count"] == 0
    assert write_stage_calls[-1][1]["p_result"]["ineligible_count"] == 1


def test_ready_but_no_signal_produces_no_tag_and_no_error():
    frame = _frame(3)
    fetcher = FakeCandidateFetcher([FakeCandidateRow("c1", "005930")])
    loader = FakeOhlcvLoader({"005930": frame})
    strategy = FakeStrategyClient({"005930": _ready_result("005930", 3, a_at_minus2=False)})
    tags_repo = FakeTagsRepository()
    rpc = FakeRpc()

    result = _run(rpc, fetcher, loader, tags_repo, strategy)

    assert result.status == "success"
    assert result.tagged_count == 0
    assert result.error_count == 0
    assert result.ineligible_count == 0
    assert tags_repo.saved == []


def test_candidate_fetch_failure_records_failed_stage_without_silent_empty_success():
    fetcher = FakeCandidateFetcher(error=RuntimeError("candidates fetch boom"))
    loader = FakeOhlcvLoader({})
    strategy = FakeStrategyClient({})
    tags_repo = FakeTagsRepository()
    rpc = FakeRpc()

    result = _run(rpc, fetcher, loader, tags_repo, strategy)

    assert result.status == "failed"
    assert result.result_code == "CANDIDATE_FETCH_FAILED"
    write_stage_calls = [c for c in rpc.calls if c[0] == "write_stage"]
    assert [c[1]["p_status"] for c in write_stage_calls] == ["running", "failed"]
    assert tags_repo.saved == []


def test_ohlcv_loader_error_status_counts_as_error_not_ineligible():
    fetcher = FakeCandidateFetcher([FakeCandidateRow("c1", "005930")])
    loader = FakeOhlcvLoader({"005930": OhlcvCacheStatus.ERROR})
    strategy = FakeStrategyClient({})
    tags_repo = FakeTagsRepository()
    rpc = FakeRpc()

    result = _run(rpc, fetcher, loader, tags_repo, strategy)

    assert result.status == "partial"
    assert result.error_count == 1
    assert result.ineligible_count == 0


def test_tags_persist_failure_records_failed_stage():
    frame = _frame(3)
    fetcher = FakeCandidateFetcher([FakeCandidateRow("c1", "005930")])
    loader = FakeOhlcvLoader({"005930": frame})
    strategy = FakeStrategyClient({"005930": _ready_result("005930", 3, a_at_minus2=True)})
    tags_repo = FakeTagsRepository(fail=True)
    rpc = FakeRpc()

    result = _run(rpc, fetcher, loader, tags_repo, strategy)

    assert result.status == "failed"
    assert result.result_code == "TAGS_PERSIST_FAILED"
    write_stage_calls = [c for c in rpc.calls if c[0] == "write_stage"]
    assert write_stage_calls[-1][1]["p_status"] == "failed"


def test_multiple_strategies_on_same_ticker_are_all_tagged():
    n = 3
    idx = pd.date_range("2026-08-01", periods=n, freq="D")
    signals = {
        "A": pd.Series([False, True, False], index=idx),
        "B": pd.Series([False, True, False], index=idx),
        "C": pd.Series(False, index=idx),
    }
    result_obj = StrategyResult(ticker="005930", status=OhlcvCacheStatus.READY, signals=signals, error=None)
    frame = _frame(n)
    fetcher = FakeCandidateFetcher([FakeCandidateRow("c1", "005930")])
    loader = FakeOhlcvLoader({"005930": frame})
    strategy = FakeStrategyClient({"005930": result_obj})
    tags_repo = FakeTagsRepository()
    rpc = FakeRpc()

    result = _run(rpc, fetcher, loader, tags_repo, strategy)

    assert result.status == "success"
    assert len(tags_repo.saved) == 2
    assert {tag.strategy for tag in tags_repo.saved} == {"A", "B"}
    assert result.tagged_candidates[0].strategies == ["A", "B"]


def test_params_meta_and_batch_kind_are_recorded_on_saved_tags():
    frame = _frame(3)
    fetcher = FakeCandidateFetcher([FakeCandidateRow("c1", "005930")])
    loader = FakeOhlcvLoader({"005930": frame})
    strategy = FakeStrategyClient({"005930": _ready_result("005930", 3, a_at_minus2=True)})
    tags_repo = FakeTagsRepository()
    rpc = FakeRpc()

    result = _run(rpc, fetcher, loader, tags_repo, strategy, batch_kind="intraday")

    assert result.batch_kind == "intraday"
    saved = tags_repo.saved[0]
    assert saved.params_meta["batch_kind"] == "intraday"
    assert saved.params_meta["min_history_days"] == 120
    assert saved.params_meta["strategy_d_params"] == STRATEGY_D_PARAMS.as_dict()
    assert saved.params_meta["strategy_e_params"] == STRATEGY_E_PARAMS.as_dict()
    assert saved.params_meta["strategy_f_params"] == STRATEGY_F_PARAMS.as_dict()
    write_stage_calls = [c for c in rpc.calls if c[0] == "write_stage"]
    assert write_stage_calls[-1][1]["p_result"]["batch_kind"] == "intraday"


def test_strategy_d_and_e_signals_are_tagged():
    n = 3
    idx = pd.date_range("2026-08-01", periods=n, freq="D")
    signals = {
        "A": pd.Series(False, index=idx),
        "B": pd.Series(False, index=idx),
        "C": pd.Series(False, index=idx),
        "D": pd.Series([False, True, False], index=idx),
        "E": pd.Series([False, True, False], index=idx),
    }
    result_obj = StrategyResult(ticker="005930", status=OhlcvCacheStatus.READY, signals=signals, error=None)
    frame = _frame(n)
    fetcher = FakeCandidateFetcher([FakeCandidateRow("c1", "005930")])
    loader = FakeOhlcvLoader({"005930": frame})
    strategy = FakeStrategyClient({"005930": result_obj})
    tags_repo = FakeTagsRepository()
    rpc = FakeRpc()

    result = _run(rpc, fetcher, loader, tags_repo, strategy)

    assert result.status == "success"
    assert len(tags_repo.saved) == 2
    assert {tag.strategy for tag in tags_repo.saved} == {"D", "E"}
    assert result.tagged_candidates[0].strategies == ["D", "E"]


def test_strategy_a_and_d_multi_tag_on_same_ticker():
    n = 3
    idx = pd.date_range("2026-08-01", periods=n, freq="D")
    signals = {
        "A": pd.Series([False, True, False], index=idx),
        "B": pd.Series(False, index=idx),
        "C": pd.Series(False, index=idx),
        "D": pd.Series([False, True, False], index=idx),
        "E": pd.Series(False, index=idx),
    }
    result_obj = StrategyResult(ticker="005930", status=OhlcvCacheStatus.READY, signals=signals, error=None)
    frame = _frame(n)
    fetcher = FakeCandidateFetcher([FakeCandidateRow("c1", "005930")])
    loader = FakeOhlcvLoader({"005930": frame})
    strategy = FakeStrategyClient({"005930": result_obj})
    tags_repo = FakeTagsRepository()
    rpc = FakeRpc()

    result = _run(rpc, fetcher, loader, tags_repo, strategy)

    assert result.status == "success"
    assert len(tags_repo.saved) == 2
    assert {tag.strategy for tag in tags_repo.saved} == {"A", "D"}
    assert result.tagged_candidates[0].strategies == ["A", "D"]


def test_strategy_e_only_signal_is_tagged():
    n = 3
    idx = pd.date_range("2026-08-01", periods=n, freq="D")
    signals = {
        "A": pd.Series(False, index=idx),
        "B": pd.Series(False, index=idx),
        "C": pd.Series(False, index=idx),
        "D": pd.Series(False, index=idx),
        "E": pd.Series([False, True, False], index=idx),
    }
    result_obj = StrategyResult(ticker="005930", status=OhlcvCacheStatus.READY, signals=signals, error=None)
    frame = _frame(n)
    fetcher = FakeCandidateFetcher([FakeCandidateRow("c1", "005930")])
    loader = FakeOhlcvLoader({"005930": frame})
    strategy = FakeStrategyClient({"005930": result_obj})
    tags_repo = FakeTagsRepository()
    rpc = FakeRpc()

    result = _run(rpc, fetcher, loader, tags_repo, strategy)

    assert result.status == "success"
    assert len(tags_repo.saved) == 1
    assert tags_repo.saved[0].strategy == "E"
    assert result.tagged_candidates[0].strategies == ["E"]


def test_all_five_strategies_signal_on_same_ticker():
    n = 3
    idx = pd.date_range("2026-08-01", periods=n, freq="D")
    signals = {key: pd.Series([False, True, False], index=idx) for key in ("A", "B", "C", "D", "E")}
    result_obj = StrategyResult(ticker="005930", status=OhlcvCacheStatus.READY, signals=signals, error=None)
    frame = _frame(n)
    fetcher = FakeCandidateFetcher([FakeCandidateRow("c1", "005930")])
    loader = FakeOhlcvLoader({"005930": frame})
    strategy = FakeStrategyClient({"005930": result_obj})
    tags_repo = FakeTagsRepository()
    rpc = FakeRpc()

    result = _run(rpc, fetcher, loader, tags_repo, strategy)

    assert result.status == "success"
    assert len(tags_repo.saved) == 5
    assert {tag.strategy for tag in tags_repo.saved} == {"A", "B", "C", "D", "E"}
    assert result.tagged_candidates[0].strategies == ["A", "B", "C", "D", "E"]


def test_strategy_d_signal_compute_error_counts_as_error_not_silently_dropped():
    frame = _frame(3)
    fetcher = FakeCandidateFetcher([FakeCandidateRow("c1", "005930"), FakeCandidateRow("c2", "000660")])
    loader = FakeOhlcvLoader({"005930": frame, "000660": frame})
    error_result = StrategyResult(
        ticker="005930", status=OhlcvCacheStatus.ERROR, signals={},
        error=StrategyError(code=StrategyErrorCode.SIGNAL_COMPUTE_ERROR, strategy="D", message="strategy D boom"),
    )
    strategy = FakeStrategyClient({
        "005930": error_result,
        "000660": _ready_result("000660", 3, a_at_minus2=True),
    })
    tags_repo = FakeTagsRepository()
    rpc = FakeRpc()

    result = _run(rpc, fetcher, loader, tags_repo, strategy)

    assert result.status == "partial"
    assert result.result_code == "PARTIAL_TAGGING"
    assert result.error_count == 1
    assert result.tagged_count == 1
    assert len(tags_repo.saved) == 1
    assert tags_repo.saved[0].strategy == "A"


def test_strategy_f_only_signal_is_tagged():
    n = 3
    idx = pd.date_range("2026-08-01", periods=n, freq="D")
    signals = {
        "A": pd.Series(False, index=idx),
        "B": pd.Series(False, index=idx),
        "C": pd.Series(False, index=idx),
        "D": pd.Series(False, index=idx),
        "E": pd.Series(False, index=idx),
        "F": pd.Series([False, True, False], index=idx),
    }
    result_obj = StrategyResult(ticker="005930", status=OhlcvCacheStatus.READY, signals=signals, error=None)
    frame = _frame(n)
    fetcher = FakeCandidateFetcher([FakeCandidateRow("c1", "005930")])
    loader = FakeOhlcvLoader({"005930": frame})
    strategy = FakeStrategyClient({"005930": result_obj})
    tags_repo = FakeTagsRepository()
    rpc = FakeRpc()

    result = _run(rpc, fetcher, loader, tags_repo, strategy)

    assert result.status == "success"
    assert len(tags_repo.saved) == 1
    assert tags_repo.saved[0].strategy == "F"
    assert result.tagged_candidates[0].strategies == ["F"]


def test_strategy_a_and_f_multi_tag_on_same_ticker():
    n = 3
    idx = pd.date_range("2026-08-01", periods=n, freq="D")
    signals = {
        "A": pd.Series([False, True, False], index=idx),
        "B": pd.Series(False, index=idx),
        "C": pd.Series(False, index=idx),
        "D": pd.Series(False, index=idx),
        "E": pd.Series(False, index=idx),
        "F": pd.Series([False, True, False], index=idx),
    }
    result_obj = StrategyResult(ticker="005930", status=OhlcvCacheStatus.READY, signals=signals, error=None)
    frame = _frame(n)
    fetcher = FakeCandidateFetcher([FakeCandidateRow("c1", "005930")])
    loader = FakeOhlcvLoader({"005930": frame})
    strategy = FakeStrategyClient({"005930": result_obj})
    tags_repo = FakeTagsRepository()
    rpc = FakeRpc()

    result = _run(rpc, fetcher, loader, tags_repo, strategy)

    assert result.status == "success"
    assert len(tags_repo.saved) == 2
    assert {tag.strategy for tag in tags_repo.saved} == {"A", "F"}
    assert result.tagged_candidates[0].strategies == ["A", "F"]


def test_all_six_strategies_signal_on_same_ticker():
    n = 3
    idx = pd.date_range("2026-08-01", periods=n, freq="D")
    signals = {key: pd.Series([False, True, False], index=idx) for key in ("A", "B", "C", "D", "E", "F")}
    result_obj = StrategyResult(ticker="005930", status=OhlcvCacheStatus.READY, signals=signals, error=None)
    frame = _frame(n)
    fetcher = FakeCandidateFetcher([FakeCandidateRow("c1", "005930")])
    loader = FakeOhlcvLoader({"005930": frame})
    strategy = FakeStrategyClient({"005930": result_obj})
    tags_repo = FakeTagsRepository()
    rpc = FakeRpc()

    result = _run(rpc, fetcher, loader, tags_repo, strategy)

    assert result.status == "success"
    assert len(tags_repo.saved) == 6
    assert {tag.strategy for tag in tags_repo.saved} == {"A", "B", "C", "D", "E", "F"}
    assert result.tagged_candidates[0].strategies == ["A", "B", "C", "D", "E", "F"]


def test_strategy_f_signal_compute_error_counts_as_error_not_silently_dropped():
    frame = _frame(3)
    fetcher = FakeCandidateFetcher([FakeCandidateRow("c1", "005930"), FakeCandidateRow("c2", "000660")])
    loader = FakeOhlcvLoader({"005930": frame, "000660": frame})
    error_result = StrategyResult(
        ticker="005930", status=OhlcvCacheStatus.ERROR, signals={},
        error=StrategyError(code=StrategyErrorCode.SIGNAL_COMPUTE_ERROR, strategy="F", message="strategy F boom"),
    )
    strategy = FakeStrategyClient({
        "005930": error_result,
        "000660": _ready_result("000660", 3, a_at_minus2=True),
    })
    tags_repo = FakeTagsRepository()
    rpc = FakeRpc()

    result = _run(rpc, fetcher, loader, tags_repo, strategy)

    assert result.status == "partial"
    assert result.result_code == "PARTIAL_TAGGING"
    assert result.error_count == 1
    assert result.tagged_count == 1
    assert len(tags_repo.saved) == 1
    assert tags_repo.saved[0].strategy == "A"


def test_signal_date_reflects_second_to_last_bar():
    n = 4
    idx = pd.date_range("2026-08-01", periods=n, freq="D")
    frame = pd.DataFrame(
        {"Open": [1.0] * n, "High": [1.0] * n, "Low": [1.0] * n, "Close": [1.0] * n, "Volume": [1.0] * n},
        index=idx,
    )
    signals = {
        "A": pd.Series([False, False, True, False], index=idx),
        "B": pd.Series(False, index=idx),
        "C": pd.Series(False, index=idx),
    }
    result_obj = StrategyResult(ticker="005930", status=OhlcvCacheStatus.READY, signals=signals, error=None)
    fetcher = FakeCandidateFetcher([FakeCandidateRow("c1", "005930")])
    loader = FakeOhlcvLoader({"005930": frame})
    strategy = FakeStrategyClient({"005930": result_obj})
    tags_repo = FakeTagsRepository()
    rpc = FakeRpc()

    result = _run(rpc, fetcher, loader, tags_repo, strategy)

    assert result.tagged_candidates[0].signal_date == idx[-2].date()
    assert tags_repo.saved[0].signal_date == idx[-2].date()


# --- Story 2.8: sync_vanished 통합 ------------------------------------------


def test_sync_vanished_is_called_after_upsert_and_vanished_count_is_recorded():
    frame = _frame(3)
    fetcher = FakeCandidateFetcher([FakeCandidateRow("c1", "005930")])
    loader = FakeOhlcvLoader({"005930": frame})
    strategy = FakeStrategyClient({"005930": _ready_result("005930", 3, a_at_minus2=True)})
    tags_repo = FakeTagsRepository(vanished_count=2)
    rpc = FakeRpc()

    result = _run(rpc, fetcher, loader, tags_repo, strategy)

    assert result.status == "success"
    assert result.result_code == "OK"
    assert result.vanished_count == 2
    assert len(tags_repo.sync_vanished_calls) == 1
    write_stage_calls = [c for c in rpc.calls if c[0] == "write_stage"]
    assert write_stage_calls[-1][1]["p_result"]["vanished_count"] == 2


def test_sync_vanished_failure_with_no_tagging_errors_records_partial_vanished_sync_failed():
    frame = _frame(3)
    fetcher = FakeCandidateFetcher([FakeCandidateRow("c1", "005930")])
    loader = FakeOhlcvLoader({"005930": frame})
    strategy = FakeStrategyClient({"005930": _ready_result("005930", 3, a_at_minus2=True)})
    tags_repo = FakeTagsRepository(sync_vanished_fail=True)
    rpc = FakeRpc()

    result = _run(rpc, fetcher, loader, tags_repo, strategy)

    assert result.status == "partial"
    assert result.result_code == "VANISHED_SYNC_FAILED"
    assert result.vanished_count == 0
    assert result.vanished_sync_failed is True
    # active 태깅은 유실 없이 이미 저장되어 있다.
    assert len(tags_repo.saved) == 1
    write_stage_calls = [c for c in rpc.calls if c[0] == "write_stage"]
    assert write_stage_calls[-1][1]["p_status"] == "partial"
    assert write_stage_calls[-1][1]["p_result"]["result_code"] == "VANISHED_SYNC_FAILED"
    assert write_stage_calls[-1][1]["p_unprocessed_count"] == 1


def test_sync_vanished_failure_alongside_tagging_error_keeps_partial_tagging_code():
    frame = _frame(3)
    fetcher = FakeCandidateFetcher([FakeCandidateRow("c1", "005930"), FakeCandidateRow("c2", "000660")])
    loader = FakeOhlcvLoader({"005930": frame, "000660": frame})
    strategy = FakeStrategyClient({
        "005930": _error_result("005930"),
        "000660": _ready_result("000660", 3, a_at_minus2=True),
    })
    tags_repo = FakeTagsRepository(sync_vanished_fail=True)
    rpc = FakeRpc()

    result = _run(rpc, fetcher, loader, tags_repo, strategy)

    assert result.status == "partial"
    assert result.result_code == "PARTIAL_TAGGING"
    assert result.error_count == 1
    assert result.vanished_sync_failed is True
    write_stage_calls = [c for c in rpc.calls if c[0] == "write_stage"]
    assert write_stage_calls[-1][1]["p_result"]["vanished_sync_failed"] is True


# --- epic-2-retro item-11: 후보별 저장 격리 + heartbeat ------------------------


def test_all_persist_failures_stay_failed_tags_persist_failed():
    """모든 후보의 upsert가 실패하면(격리 후에도) 기존처럼 TAGS_PERSIST_FAILED로 실패 처리한다."""
    frame = _frame(3)
    fetcher = FakeCandidateFetcher([
        FakeCandidateRow("c1", "005930"), FakeCandidateRow("c2", "000660"),
    ])
    loader = FakeOhlcvLoader({"005930": frame, "000660": frame})
    strategy = FakeStrategyClient({
        "005930": _ready_result("005930", 3, a_at_minus2=True),
        "000660": _ready_result("000660", 3, a_at_minus2=True),
    })
    tags_repo = FakeTagsRepository(fail_candidate_ids={"c1", "c2"})
    rpc = FakeRpc()

    result = _run(rpc, fetcher, loader, tags_repo, strategy)

    assert result.status == "failed"
    assert result.result_code == "TAGS_PERSIST_FAILED"
    assert result.persist_failed_count == 2
    assert result.tagged_count == 0
    assert len(tags_repo.saved) == 0
    write_stage_calls = [c for c in rpc.calls if c[0] == "write_stage"]
    assert [c[1]["p_status"] for c in write_stage_calls] == ["running", "failed"]
    assert write_stage_calls[-1][1]["p_unprocessed_count"] == 2


def test_partial_persist_failure_isolates_bad_candidate_and_keeps_rest():
    """한 후보의 upsert 실패가 나머지 후보 저장을 막지 않고 partial로 기록한다(item-11 F4)."""
    frame = _frame(3)
    fetcher = FakeCandidateFetcher([
        FakeCandidateRow("c1", "005930"), FakeCandidateRow("c2", "000660"), FakeCandidateRow("c3", "035720"),
    ])
    loader = FakeOhlcvLoader({"005930": frame, "000660": frame, "035720": frame})
    strategy = FakeStrategyClient({
        "005930": _ready_result("005930", 3, a_at_minus2=True),
        "000660": _ready_result("000660", 3, a_at_minus2=True),
        "035720": _ready_result("035720", 3, a_at_minus2=True),
    })
    tags_repo = FakeTagsRepository(fail_candidate_ids={"c2"})
    rpc = FakeRpc()

    result = _run(rpc, fetcher, loader, tags_repo, strategy)

    assert result.status == "partial"
    assert result.result_code == "TAGS_PERSIST_PARTIAL"
    assert result.persist_failed_count == 1
    assert result.tagged_count == 2
    assert {tag.candidate_id for tag in tags_repo.saved} == {"c1", "c3"}
    assert {tag.strategy for tag in tags_repo.saved} == {"A"}
    write_stage_calls = [c for c in rpc.calls if c[0] == "write_stage"]
    assert [c[1]["p_status"] for c in write_stage_calls] == ["running", "partial"]
    assert write_stage_calls[-1][1]["p_unprocessed_count"] == 1
    # 부분 저장된 집합 기준으로 소멸 판정을 내리면 안 되므로 sync_vanished는 건너뛴다.
    assert tags_repo.sync_vanished_calls == []


def test_no_tags_skips_persist_entirely():
    """태깅된 후보가 없으면 upsert 자체를 호출하지 않는다(item-11 F4: 빈 배치 실패 회피)."""
    frame = _frame(3)
    fetcher = FakeCandidateFetcher([FakeCandidateRow("c1", "005930")])
    loader = FakeOhlcvLoader({"005930": frame})
    strategy = FakeStrategyClient({"005930": _ready_result("005930", 3, a_at_minus2=False)})

    class ExplodingTagsRepository:
        def upsert_tags(self, tags):
            raise AssertionError("upsert_tags must not be called with empty tags")

        def sync_vanished(self, run_id):
            return {"vanished_count": 0}

    rpc = FakeRpc()
    result = _run(rpc, fetcher, loader, ExplodingTagsRepository(), strategy)

    assert result.status == "success"
    assert result.result_code == "OK"
    assert result.tagged_count == 0


def test_heartbeat_is_called_per_candidate_in_tags_stage():
    """tags stage는 후보마다 heartbeat.beat()를 호출해 lease를 연장한다(item-11 F1)."""
    frame = _frame(3)
    fetcher = FakeCandidateFetcher([
        FakeCandidateRow("c1", "005930"), FakeCandidateRow("c2", "000660"),
    ])
    loader = FakeOhlcvLoader({"005930": frame, "000660": frame})
    strategy = FakeStrategyClient({
        "005930": _ready_result("005930", 3, a_at_minus2=True),
        "000660": _ready_result("000660", 3, a_at_minus2=True),
    })
    tags_repo = FakeTagsRepository()
    rpc = FakeRpc()

    class RecordingHeartbeat:
        def __init__(self):
            self.beats = 0

        def beat(self):
            self.beats += 1

    hb = RecordingHeartbeat()
    run_id = uuid4()
    gateway = RunStateGateway(rpc)
    result = run_tags_stage(
        gateway, fetcher, loader, tags_repo, run_id, 1, uuid4(), date(2026, 9, 1),
        strategy_client=strategy, batch_kind="close", heartbeat=hb,
    )

    assert result.status == "success"
    assert hb.beats == 2
