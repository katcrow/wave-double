from datetime import date
from uuid import uuid4

import pytest

from apps.batch.ls_market_index_provider import MarketIndexBar
from apps.batch.ls_market_macro_provider import MarketMacroQuote
from apps.batch.ls_market_program_supply_provider import MarketProgramSupplyBar
from apps.batch.ls_market_supply_provider import MarketSupplyBar
from apps.batch.market_supply_repository import MarketMacroRow, MarketSupplyRow
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
    def __init__(self, fail=False, macro_fail=False):
        self.fail = fail
        self.macro_fail = macro_fail
        self.saved: list[MarketSupplyRow] = []
        self.macro_saved: list[MarketMacroRow] = []

    def upsert_macro_rows(self, rows):
        if self.macro_fail:
            raise RuntimeError("macro upsert failed")
        self.macro_saved.extend(rows)
        return len(rows)

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


def _indexes():
    return {
        "KOSPI": MarketIndexBar("KOSPI", 6943.9, -0.85, 402, 76, 466),
        "KOSDAQ": MarketIndexBar("KOSDAQ", 914.7, 2.4, 954, 145, 726),
    }


def _macros():
    return {
        "CME@NQ": MarketMacroQuote("CME@NQ", 31351.5, 33.75, 0.11, date(2026, 8, 31)),
        "USDKRWSMBS": MarketMacroQuote("USDKRWSMBS", 1343.4, -1.0, -0.07, DAY),
    }


def _run(investors=None, programs=None, repo=None, kind=BatchKind.INTRADAY, indexes=None, macros=None):
    rpc = FakeRpc()
    run_id = uuid4()
    repo = repo or FakeRepository()
    result = run_market_supply_stage(
        RunStateGateway(rpc),
        FakeInvestorProvider(_investors() if investors is None else investors),
        FakeProgramProvider(_programs() if programs is None else programs),
        repo, run_id, 1, uuid4(), DAY, kind,
        market_index_provider=None if indexes is None else FakeProgramProvider(indexes),
        market_macro_provider=None if macros is None else FakeProgramProvider(macros),
        market_macro_repo=None if macros is None else repo,
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


def test_index_provider_fills_index_fields_per_market():
    repo = FakeRepository()
    result, _ = _run(repo=repo, indexes=_indexes())

    assert result.status == "success"
    assert {
        row.market: (
            row.index_price, row.index_change_rate,
            row.advancing_count, row.unchanged_count, row.declining_count,
        )
        for row in repo.saved
    } == {
        "KOSPI": (6943.9, -0.85, 402, 76, 466),
        "KOSDAQ": (914.7, 2.4, 954, 145, 726),
    }


def test_index_failure_keeps_supply_row_and_success_status():
    repo = FakeRepository()
    result, rpc = _run(
        repo=repo,
        indexes={"KOSPI": RuntimeError("t1511 unavailable"), "KOSDAQ": _indexes()["KOSDAQ"]},
    )

    assert result.status == "success"
    by_market = {row.market: row for row in repo.saved}
    assert by_market["KOSPI"].foreign_net == 100.0
    assert by_market["KOSPI"].index_change_rate is None
    assert by_market["KOSPI"].advancing_count is None
    assert by_market["KOSDAQ"].index_change_rate == 2.4
    final = [call for call in rpc.calls if call[0] == "write_stage"][-1]
    assert final[1]["p_status"] == "success"
    assert final[1]["p_result"]["index_errors"] == [{"market": "KOSPI", "message": "t1511 unavailable"}]


def test_index_provider_returning_other_market_is_treated_as_index_failure():
    repo = FakeRepository()
    result, rpc = _run(repo=repo, indexes={"KOSPI": _indexes()["KOSDAQ"], "KOSDAQ": _indexes()["KOSDAQ"]})

    assert result.status == "success"
    assert {row.market: row.index_change_rate for row in repo.saved} == {"KOSPI": None, "KOSDAQ": 2.4}


def test_market_supply_row_db_payload_includes_nullable_index_fields():
    row = MarketSupplyRow(str(uuid4()), "KOSPI", DAY, 1, 2, 3, 4)
    payload = row.as_db_row()

    assert {key: payload[key] for key in (
        "index_price", "index_change_rate", "advancing_count", "unchanged_count", "declining_count",
    )} == dict.fromkeys(
        ("index_price", "index_change_rate", "advancing_count", "unchanged_count", "declining_count"), None,
    )
    with pytest.raises(ValueError):
        MarketSupplyRow(str(uuid4()), "KOSPI", DAY, 1, 2, 3, 4, index_change_rate=float("inf"))
    with pytest.raises(ValueError):
        MarketSupplyRow(str(uuid4()), "KOSPI", DAY, 1, 2, 3, 4, advancing_count=-1)


def test_macro_provider_saves_one_row_per_symbol():
    repo = FakeRepository()
    result, rpc = _run(repo=repo, macros=_macros())

    assert result.status == "success"
    assert [(row.symbol, row.price, row.change_rate, row.quote_date, row.trading_day) for row in repo.macro_saved] == [
        ("CME@NQ", 31351.5, 0.11, date(2026, 8, 31), DAY),
        ("USDKRWSMBS", 1343.4, -0.07, DAY, DAY),
    ]
    final = [call for call in rpc.calls if call[0] == "write_stage"][-1]
    assert final[1]["p_result"]["macro_count"] == 2
    assert final[1]["p_result"]["macro_errors"] == []


def test_macro_failures_never_change_stage_status():
    repo = FakeRepository()
    result, rpc = _run(
        repo=repo,
        macros={"CME@NQ": RuntimeError("t3521 unavailable"), "USDKRWSMBS": _macros()["CME@NQ"]},
    )

    assert result.status == "success"
    assert len(repo.saved) == 2
    assert repo.macro_saved == []
    final = [call for call in rpc.calls if call[0] == "write_stage"][-1]
    assert final[1]["p_status"] == "success"
    assert [error["symbol"] for error in final[1]["p_result"]["macro_errors"]] == ["CME@NQ", "USDKRWSMBS"]


def test_macro_persist_failure_is_recorded_only():
    repo = FakeRepository(macro_fail=True)
    result, rpc = _run(repo=repo, macros=_macros())

    assert result.status == "success"
    final = [call for call in rpc.calls if call[0] == "write_stage"][-1]
    assert final[1]["p_result"]["macro_count"] == 0
    assert final[1]["p_result"]["macro_errors"] == [{"symbol": "*", "message": "persist failed: macro upsert failed"}]


def test_market_macro_row_validates_and_serializes():
    row = MarketMacroRow(str(uuid4()), DAY, "CME@NQ", 31351.5, 33.75, 0.11, None)
    payload = row.as_db_row()

    assert payload["symbol"] == "CME@NQ"
    assert payload["quote_date"] is None
    assert payload["trading_day"] == "2026-09-01"
    with pytest.raises(ValueError):
        MarketMacroRow(str(uuid4()), DAY, "NYM@CL", 1, 0, 0, None)
    with pytest.raises(ValueError):
        MarketMacroRow(str(uuid4()), DAY, "CME@NQ", 1, 0, float("nan"), None)
