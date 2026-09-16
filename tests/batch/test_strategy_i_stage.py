from dataclasses import dataclass
from datetime import date, datetime, time
from uuid import uuid4

import pandas as pd
import pytest

from apps.batch.candidate_tags_repository import CandidateTag
from apps.batch.run_state import RunStateGateway
from apps.batch.strategy_i_stage import (
    _STRATEGY_I,
    _has_dual_bull,
    _is_not_bullish,
    is_strategy_i_window,
    run_strategy_i_stage,
)
from domain.ohlcv_cache import OhlcvCacheStatus
from domain.run_state import Stage, StageStatus


# ---------------------------------------------------------------------------
# Fake / test helpers
# ---------------------------------------------------------------------------

class FakeRpc:
    def __init__(self, *, fail_write_stage=False):
        self.calls: list[tuple[str, dict]] = []
        self.fail_write_stage = fail_write_stage

    def rpc(self, function, params):
        self.calls.append((function, params))
        if function == "write_stage" and self.fail_write_stage:
            raise RuntimeError("supabase write_stage failed")
        return {"ok": True}


class FakeCandidateRow:
    def __init__(self, candidate_id, ticker):
        self.candidate_id = candidate_id
        self.ticker = ticker


class FakeCandidateFetcher:
    def __init__(self, rows=None, error=None):
        self.rows = rows if rows is not None else []
        self.error = error
        self.calls: list[str] = []

    def fetch(self, run_id):
        self.calls.append(run_id)
        if self.error is not None:
            raise self.error
        return self.rows


class FakeOhlcvLoader:
    def __init__(self, by_ticker):
        self.by_ticker = by_ticker
        self.calls: list[tuple[str, date]] = []

    def load_ohlcv(self, ticker, cutoff):
        self.calls.append((ticker, cutoff))
        return self.by_ticker[ticker]


@dataclass
class _FakeSupplyBar:
    """t1702 SupplyBar를 흉내 낸 간이 객체."""
    foreign_net: float
    institution_net: float


class FakeSupplyProvider:
    def __init__(self, by_ticker):
        self.by_ticker = by_ticker
        self.calls: list[tuple[str, date, date]] = []

    def fetch(self, ticker, fromdt, todt):
        self.calls.append((ticker, fromdt, todt))
        outcome = self.by_ticker[ticker]
        if isinstance(outcome, Exception):
            raise outcome
        return outcome


class FakeTagsRepository:
    def __init__(self, fail=False):
        self.fail = fail
        self.saved: list[CandidateTag] = []
        self.calls: list[list[CandidateTag]] = []

    def upsert_tags(self, tags):
        self.calls.append(tags)
        if self.fail:
            raise RuntimeError("supabase upsert failed")
        self.saved.extend(tags)
        return len(tags)


def _frame(*, open_: float = 100.0, close: float = 98.0) -> pd.DataFrame:
    """마지막 봉 하나만 있는 OHLCV DataFrame을 만든다.

    기본값은 음봉(Close < Open). 양봉을 테스트하려면 close > open_을 전달한다.
    """
    idx = pd.DatetimeIndex([date(2026, 9, 16)])
    return pd.DataFrame(
        {"Open": [open_], "High": [max(open_, close)], "Low": [min(open_, close)],
         "Close": [close], "Volume": [1000]},
        index=idx,
    )


def _make_run(gateway, rpc, candidates, ohlcv_loader, supply_provider, tags_repo,
              trading_day=None, **run_kwargs):
    run_id = uuid4()
    lease_token = uuid4()
    fence_token = 1
    result = run_strategy_i_stage(
        gateway, candidates, ohlcv_loader, supply_provider, tags_repo,
        run_id, fence_token, lease_token, trading_day or date(2026, 9, 16),
        **run_kwargs,
    )
    return result, rpc, ohlcv_loader, supply_provider, tags_repo


# ---------------------------------------------------------------------------
# Unit tests for helper functions
# ---------------------------------------------------------------------------

class TestIsStrategyIWindow:
    def test_16_00_is_in_window(self):
        assert is_strategy_i_window(datetime(2026, 9, 16, 16, 0)) is True

    def test_19_30_is_in_window(self):
        assert is_strategy_i_window(datetime(2026, 9, 16, 19, 30)) is True

    def test_15_59_is_out_of_window(self):
        assert is_strategy_i_window(datetime(2026, 9, 16, 15, 59)) is False

    def test_20_00_is_out_of_window(self):
        assert is_strategy_i_window(datetime(2026, 9, 16, 20, 0)) is False

    def test_midnight_is_out_of_window(self):
        assert is_strategy_i_window(datetime(2026, 9, 16, 0, 0)) is False


class TestIsNotBullish:
    def test_bearish_candle_is_not_bullish(self):
        frame = _frame(open_=100.0, close=98.0)
        assert _is_not_bullish(frame) is True

    def test_doji_is_not_bullish(self):
        frame = _frame(open_=100.0, close=100.0)
        assert _is_not_bullish(frame) is True

    def test_bullish_candle_is_not_accepted(self):
        frame = _frame(open_=100.0, close=102.0)
        assert _is_not_bullish(frame) is False

    def test_empty_frame_is_rejected(self):
        frame = pd.DataFrame(columns=["Open", "High", "Low", "Close", "Volume"])
        assert _is_not_bullish(frame) is False


class TestHasDualBull:
    def test_both_positive(self):
        bars = [_FakeSupplyBar(foreign_net=10.0, institution_net=5.0)]
        assert _has_dual_bull(bars) is True

    def test_foreign_zero(self):
        bars = [_FakeSupplyBar(foreign_net=0.0, institution_net=5.0)]
        assert _has_dual_bull(bars) is False

    def test_institution_zero(self):
        bars = [_FakeSupplyBar(foreign_net=10.0, institution_net=0.0)]
        assert _has_dual_bull(bars) is False

    def test_both_negative(self):
        bars = [_FakeSupplyBar(foreign_net=-1.0, institution_net=-2.0)]
        assert _has_dual_bull(bars) is False

    def test_empty_bars(self):
        assert _has_dual_bull([]) is False

    def test_missing_attributes(self):
        """foreign_net/institution_net이 없는 객체는 에러로 간주한다."""

        class BareBar:
            pass
        assert _has_dual_bull([BareBar()]) is False


# ---------------------------------------------------------------------------
# Integration-style tests for run_strategy_i_stage
# ---------------------------------------------------------------------------

class TestRunStrategyIStage:
    def test_single_candidate_meets_both_conditions_saves_tag(self):
        """음봉 + 외국인·기관 쌍끌이 → tag 저장."""
        rpc = FakeRpc()
        gateway = RunStateGateway(rpc)
        fetcher = FakeCandidateFetcher([FakeCandidateRow("c1", "005930")])
        ohlcv = FakeOhlcvLoader({"005930": _frame(open_=100.0, close=98.0)})
        supply = FakeSupplyProvider({
            "005930": [_FakeSupplyBar(foreign_net=10.0, institution_net=5.0)],
        })
        tags = FakeTagsRepository()

        result, _, _, _, tags = _make_run(
            gateway, rpc, fetcher, ohlcv, supply, tags,
        )

        assert result.status == "success"
        assert result.result_code == "OK"
        assert result.tagged_count == 1
        assert result.error_count == 0
        assert result.ineligible_count == 0
        assert len(tags.saved) == 1
        tag = tags.saved[0]
        assert tag.strategy == _STRATEGY_I
        assert tag.candidate_id == "c1"
        assert tag.signal_date == date(2026, 9, 16)
        assert tag.params_meta == {"batch_kind": "strategy_i", "rule": "not_bullish_and_dual_supply"}
        write_stage_calls = [c for c in rpc.calls if c[0] == "write_stage"]
        assert [c[1]["p_status"] for c in write_stage_calls] == ["running", "success"]

    def test_bullish_candle_is_skipped_no_tag(self):
        """양봉(Close > Open) → 전략 I 대상 아님, tag 저장 안 됨."""
        rpc = FakeRpc()
        gateway = RunStateGateway(rpc)
        fetcher = FakeCandidateFetcher([FakeCandidateRow("c1", "005930")])
        ohlcv = FakeOhlcvLoader({"005930": _frame(open_=100.0, close=102.0)})
        supply = FakeSupplyProvider({
            "005930": [_FakeSupplyBar(foreign_net=10.0, institution_net=5.0)],
        })
        tags = FakeTagsRepository()

        result, _, _, _, tags = _make_run(
            gateway, rpc, fetcher, ohlcv, supply, tags,
        )

        assert result.status == "success"
        assert result.tagged_count == 0
        assert tags.saved == []

    def test_only_foreign_net_buy_is_not_enough(self):
        """외국인만 순매수, 기관 0 → 쌍끌이 아님."""
        rpc = FakeRpc()
        gateway = RunStateGateway(rpc)
        fetcher = FakeCandidateFetcher([FakeCandidateRow("c1", "005930")])
        ohlcv = FakeOhlcvLoader({"005930": _frame(open_=100.0, close=98.0)})
        supply = FakeSupplyProvider({
            "005930": [_FakeSupplyBar(foreign_net=10.0, institution_net=0.0)],
        })
        tags = FakeTagsRepository()

        result, _, _, _, tags = _make_run(
            gateway, rpc, fetcher, ohlcv, supply, tags,
        )

        assert result.status == "success"
        assert result.tagged_count == 0
        assert tags.saved == []

    def test_only_institution_net_buy_is_not_enough(self):
        """기관만 순매수, 외국인 0 → 쌍끌이 아님."""
        rpc = FakeRpc()
        gateway = RunStateGateway(rpc)
        fetcher = FakeCandidateFetcher([FakeCandidateRow("c1", "005930")])
        ohlcv = FakeOhlcvLoader({"005930": _frame(open_=100.0, close=98.0)})
        supply = FakeSupplyProvider({
            "005930": [_FakeSupplyBar(foreign_net=0.0, institution_net=5.0)],
        })
        tags = FakeTagsRepository()

        result, _, _, _, tags = _make_run(
            gateway, rpc, fetcher, ohlcv, supply, tags,
        )

        assert result.status == "success"
        assert result.tagged_count == 0

    def test_no_candidates_is_success_with_zero_tags(self):
        """후보가 없으면 0행으로 success."""
        rpc = FakeRpc()
        gateway = RunStateGateway(rpc)
        fetcher = FakeCandidateFetcher([])
        ohlcv = FakeOhlcvLoader({})
        supply = FakeSupplyProvider({})
        tags = FakeTagsRepository()

        result, _, _, _, _ = _make_run(
            gateway, rpc, fetcher, ohlcv, supply, tags,
        )

        assert result.status == "success"
        assert result.result_code == "OK"
        assert result.tagged_count == 0
        assert result.candidate_count == 0
        write_stage_calls = [c for c in rpc.calls if c[0] == "write_stage"]
        assert [c[1]["p_status"] for c in write_stage_calls] == ["running", "success"]

    def test_candidate_fetch_failure_records_failed_stage(self):
        """후보 조회 실패 → FAILED + silent success 금지."""
        rpc = FakeRpc()
        gateway = RunStateGateway(rpc)
        fetcher = FakeCandidateFetcher(error=RuntimeError("boom"))
        ohlcv = FakeOhlcvLoader({})
        supply = FakeSupplyProvider({})
        tags = FakeTagsRepository()

        result, _, _, _, _ = _make_run(
            gateway, rpc, fetcher, ohlcv, supply, tags,
        )

        assert result.status == "failed"
        assert result.result_code == "CANDIDATE_FETCH_FAILED"
        write_stage_calls = [c for c in rpc.calls if c[0] == "write_stage"]
        assert [c[1]["p_status"] for c in write_stage_calls] == ["running", "failed"]
        assert tags.saved == []

    def test_ohlcv_insufficient_history_is_ineligible(self):
        """OHLCV 이력 부족 → ineligible_count 증가, tag 저장 안 됨."""
        rpc = FakeRpc()
        gateway = RunStateGateway(rpc)
        fetcher = FakeCandidateFetcher([FakeCandidateRow("c1", "005930")])
        ohlcv = FakeOhlcvLoader({"005930": OhlcvCacheStatus.INELIGIBLE_INSUFFICIENT_HISTORY})
        supply = FakeSupplyProvider({})
        tags = FakeTagsRepository()

        result, _, _, _, _ = _make_run(
            gateway, rpc, fetcher, ohlcv, supply, tags,
        )

        assert result.status == "success"
        assert result.ineligible_count == 1
        assert result.tagged_count == 0

    def test_ohlcv_error_is_error_count(self):
        """OHLCV 로딩 에러 → error_count 증가."""
        rpc = FakeRpc()
        gateway = RunStateGateway(rpc)
        fetcher = FakeCandidateFetcher([FakeCandidateRow("c1", "005930")])
        ohlcv = FakeOhlcvLoader({"005930": OhlcvCacheStatus.ERROR})
        supply = FakeSupplyProvider({})
        tags = FakeTagsRepository()

        result, _, _, _, _ = _make_run(
            gateway, rpc, fetcher, ohlcv, supply, tags,
        )

        assert result.status == "partial"
        assert result.error_count == 1
        assert result.tagged_count == 0

    def test_supply_fetch_error_is_error_count(self):
        """수급 조회 실패 → error_count 증가, tag 저장 안 됨."""
        rpc = FakeRpc()
        gateway = RunStateGateway(rpc)
        fetcher = FakeCandidateFetcher([FakeCandidateRow("c1", "005930")])
        ohlcv = FakeOhlcvLoader({"005930": _frame(open_=100.0, close=98.0)})
        supply = FakeSupplyProvider({"005930": RuntimeError("t1702 unavailable")})
        tags = FakeTagsRepository()

        result, _, _, _, _ = _make_run(
            gateway, rpc, fetcher, ohlcv, supply, tags,
        )

        assert result.status == "partial"
        assert result.error_count == 1
        assert tags.saved == []

    def test_multiple_candidates_one_pass_one_bullish_one_supply_error(self):
        """여러 후보 중 하나만 조건 충족, 나머지 양봉/에러 → partial."""
        rpc = FakeRpc()
        gateway = RunStateGateway(rpc)
        fetcher = FakeCandidateFetcher([
            FakeCandidateRow("c_pass", "005930"),
            FakeCandidateRow("c_bull", "000660"),
            FakeCandidateRow("c_err", "035720"),
        ])
        ohlcv = FakeOhlcvLoader({
            "005930": _frame(open_=100.0, close=98.0),  # 음봉
            "000660": _frame(open_=100.0, close=102.0),  # 양봉
            "035720": _frame(open_=100.0, close=98.0),   # 음봉
        })
        supply = FakeSupplyProvider({
            "005930": [_FakeSupplyBar(foreign_net=10.0, institution_net=5.0)],  # dual bull
            "000660": [_FakeSupplyBar(foreign_net=10.0, institution_net=5.0)],
            "035720": RuntimeError("boom"),  # supply error
        })
        tags = FakeTagsRepository()

        result, _, _, _, tags = _make_run(
            gateway, rpc, fetcher, ohlcv, supply, tags,
        )

        assert result.status == "partial"
        assert result.tagged_count == 1
        assert result.error_count == 1
        assert len(tags.saved) == 1
        assert tags.saved[0].candidate_id == "c_pass"
        write_stage_calls = [c for c in rpc.calls if c[0] == "write_stage"]
        assert [c[1]["p_status"] for c in write_stage_calls] == ["running", "partial"]

    def test_tags_repository_failure_records_failed_stage(self):
        """tag 저장 실패 → STRATEGY_I_PERSIST_FAILED."""
        rpc = FakeRpc()
        gateway = RunStateGateway(rpc)
        fetcher = FakeCandidateFetcher([FakeCandidateRow("c1", "005930")])
        ohlcv = FakeOhlcvLoader({"005930": _frame(open_=100.0, close=98.0)})
        supply = FakeSupplyProvider({
            "005930": [_FakeSupplyBar(foreign_net=10.0, institution_net=5.0)],
        })
        tags = FakeTagsRepository(fail=True)

        result, _, _, _, tags = _make_run(
            gateway, rpc, fetcher, ohlcv, supply, tags,
        )

        assert result.status == "failed"
        assert result.result_code == "STRATEGY_I_PERSIST_FAILED"
        assert result.persist_failed_count == 1
        write_stage_calls = [c for c in rpc.calls if c[0] == "write_stage"]
        assert [c[1]["p_status"] for c in write_stage_calls] == ["running", "failed"]

    def test_ohlcv_loader_receives_trading_day_as_cutoff(self):
        """ohlcv_loader.load_ohlcv가 trading_day를 cutoff로 받는지 확인."""
        rpc = FakeRpc()
        gateway = RunStateGateway(rpc)
        fetcher = FakeCandidateFetcher([FakeCandidateRow("c1", "005930")])
        ohlcv = FakeOhlcvLoader({"005930": _frame(open_=100.0, close=98.0)})
        supply = FakeSupplyProvider({
            "005930": [_FakeSupplyBar(foreign_net=10.0, institution_net=5.0)],
        })
        tags = FakeTagsRepository()

        _make_run(
            gateway, rpc, fetcher, ohlcv, supply, tags,
            trading_day=date(2026, 9, 20),
        )

        assert ohlcv.calls == [("005930", date(2026, 9, 20))]

    def test_supply_provider_receives_single_day_range(self):
        """supply_provider.fetch(fromdt=today, todt=today)인지 확인."""
        rpc = FakeRpc()
        gateway = RunStateGateway(rpc)
        fetcher = FakeCandidateFetcher([FakeCandidateRow("c1", "005930")])
        ohlcv = FakeOhlcvLoader({"005930": _frame(open_=100.0, close=98.0)})
        supply = FakeSupplyProvider({
            "005930": [_FakeSupplyBar(foreign_net=10.0, institution_net=5.0)],
        })
        tags = FakeTagsRepository()

        _make_run(
            gateway, rpc, fetcher, ohlcv, supply, tags,
            trading_day=date(2026, 9, 20),
        )

        assert supply.calls == [("005930", date(2026, 9, 20), date(2026, 9, 20))]

    def test_empty_ohlcv_frame_is_error(self):
        """OHLCV 빈 DataFrame은 error로 집계."""
        rpc = FakeRpc()
        gateway = RunStateGateway(rpc)
        fetcher = FakeCandidateFetcher([FakeCandidateRow("c1", "005930")])
        empty_frame = pd.DataFrame(columns=["Open", "High", "Low", "Close", "Volume"])
        empty_frame.index.name = "trading_day"
        ohlcv = FakeOhlcvLoader({"005930": empty_frame})
        supply = FakeSupplyProvider({"005930": []})
        tags = FakeTagsRepository()

        result, _, _, _, _ = _make_run(
            gateway, rpc, fetcher, ohlcv, supply, tags,
        )

        assert result.status == "partial"
        assert result.error_count == 1

    def test_doji_candle_passes_non_bullish_check(self):
        """도지(Open == Close) → 음봉 아님但仍非阳线 → tag 저장."""
        rpc = FakeRpc()
        gateway = RunStateGateway(rpc)
        fetcher = FakeCandidateFetcher([FakeCandidateRow("c1", "005930")])
        ohlcv = FakeOhlcvLoader({"005930": _frame(open_=100.0, close=100.0)})
        supply = FakeSupplyProvider({
            "005930": [_FakeSupplyBar(foreign_net=10.0, institution_net=5.0)],
        })
        tags = FakeTagsRepository()

        result, _, _, _, tags = _make_run(
            gateway, rpc, fetcher, ohlcv, supply, tags,
        )

        assert result.status == "success"
        assert result.tagged_count == 1
        assert tags.saved[0].strategy == _STRATEGY_I

    def test_write_stage_call_uses_strategy_i_stage(self):
        """gateway.write_stage가 Stage.STRATEGY_I를 사용하는지 확인."""
        rpc = FakeRpc()
        gateway = RunStateGateway(rpc)
        fetcher = FakeCandidateFetcher([])
        ohlcv = FakeOhlcvLoader({})
        supply = FakeSupplyProvider({})
        tags = FakeTagsRepository()

        run_strategy_i_stage(
            gateway, fetcher, ohlcv, supply, tags,
            uuid4(), 1, uuid4(), date(2026, 9, 16),
        )

        write_stage_calls = [c for c in rpc.calls if c[0] == "write_stage"]
        assert all(c[1]["p_stage"] == Stage.STRATEGY_I.value for c in write_stage_calls)
