from datetime import date
from uuid import uuid4

import pytest

from apps.batch.ls_market_program_supply_provider import MarketProgramSupplyBar
from apps.batch.ls_market_supply_provider import MarketSupplyBar
from apps.batch.market_supply_repository import MarketSupplyRow
from apps.batch.market_supply_stage import run_market_supply_stage
from apps.batch.run_state import RunStateGateway
from domain.run_state import BatchKind


class FakeRpc:
    def __init__(self):
        self.calls = []

    def rpc(self, function, params):
        self.calls.append((function, params))
        return {"ok": True}


class FakeInvestorProvider:
    def __init__(self, outcome):
        self.outcome = outcome
        self.calls = 0

    def fetch(self):
        self.calls += 1
        if isinstance(self.outcome, Exception):
            raise self.outcome
        return self.outcome


class FakeProgramProvider:
    def __init__(self, outcomes):
        self.outcomes = outcomes
        self.calls = []

    def fetch(self, market):
        self.calls.append(market)
        outcome = self.outcomes[market]
        if isinstance(outcome, Exception):
            raise outcome
        return outcome


class FakeRepository:
    def __init__(self, fail=False):
        self.fail = fail
        self.saved: list[MarketSupplyRow] = []

    def upsert_rows(self, rows):
        if self.fail:
            raise RuntimeError("market upsert failed")
        self.saved.extend(rows)
        return len(rows)


DAY = date(2026, 9, 1)


def _investors():
    return [MarketSupplyBar("KOSPI", 100, 200, -300), MarketSupplyBar("KOSDAQ", -10, -20, 30)]


def _programs():
    return {"KOSPI": MarketProgramSupplyBar("KOSPI", 40), "KOSDAQ": MarketProgramSupplyBar("KOSDAQ", -50)}


def _run(investors=None, programs=None, repo=None, kind=BatchKind.INTRADAY):
    rpc = FakeRpc()
    run_id = uuid4()
    result = run_market_supply_stage(
        RunStateGateway(rpc),
        FakeInvestorProvider(_investors() if investors is None else investors),
        FakeProgramProvider(_programs() if programs is None else programs),
        repo or FakeRepository(), run_id, 1, uuid4(), DAY, kind,
    )
    return result, rpc


def test_happy_path_saves_one_row_per_market_and_succeeds():
    repo = FakeRepository()
    result, rpc = _run(repo=repo)

    assert result.status == "success"
    assert result.row_count == 2
    assert {row.market for row in repo.saved} == {"KOSPI", "KOSDAQ"}
    assert {
        row.market: (
            row.foreign_net,
            row.institution_net,
            row.individual_net,
            row.program_net,
            row.trading_day,
        )
        for row in repo.saved
    } == {
        "KOSPI": (100.0, 200.0, -300.0, 40.0, DAY),
        "KOSDAQ": (-10.0, -20.0, 30.0, -50.0, DAY),
    }
    assert all(row.attempt_run_id for row in repo.saved)
    assert [call[1]["p_status"] for call in rpc.calls if call[0] == "write_stage"] == ["running", "success"]


def test_one_program_market_failure_preserves_other_row_and_records_partial():
    repo = FakeRepository()
    result, rpc = _run(programs={"KOSPI": RuntimeError("t1631 unavailable"), "KOSDAQ": _programs()["KOSDAQ"]}, repo=repo)

    assert result.status == "partial"
    assert result.failed_markets == ("KOSPI",)
    assert [row.market for row in repo.saved] == ["KOSDAQ"]
    final = [call for call in rpc.calls if call[0] == "write_stage"][-1]
    assert final[1]["p_status"] == "partial"
    assert final[1]["p_result"]["failed_markets"] == ["KOSPI"]


def test_one_malformed_t1601_market_preserves_the_other_market_row():
    repo = FakeRepository()
    result, rpc = _run(
        investors=[MarketSupplyBar("KOSDAQ", -10, -20, 30)],
        repo=repo,
    )

    assert result.status == "partial"
    assert result.failed_markets == ("KOSPI",)
    assert [row.market for row in repo.saved] == ["KOSDAQ"]


def test_malformed_investor_response_fails_without_writing_rows():
    repo = FakeRepository()
    result, rpc = _run(investors=RuntimeError("missing t1601 block"), repo=repo)

    assert result.status == "failed"
    assert result.failed_markets == ("KOSPI", "KOSDAQ")
    assert repo.saved == []
    final = [call for call in rpc.calls if call[0] == "write_stage"][-1]
    assert final[1]["p_status"] == "failed"


def test_premarket_is_rejected_before_stage_write_or_api_call():
    with pytest.raises(ValueError, match="premarket"):
        _run(kind=BatchKind.PREMARKET)


def test_market_supply_row_rejects_non_finite_values_and_unknown_market():
    with pytest.raises(ValueError):
        MarketSupplyRow(str(uuid4()), "OTHER", DAY, 1, 2, 3, 4)
    with pytest.raises(ValueError):
        MarketSupplyRow(str(uuid4()), "KOSPI", DAY, float("nan"), 2, 3, 4)
