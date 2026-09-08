from datetime import date
from uuid import uuid4

import httpx
import pytest

from apps.batch.ls_program_supply_provider import ProgramSupplyBar
from apps.batch.ls_supply_provider import SupplyBar
from apps.batch.run_state import RunStateGateway
from apps.batch.supply_3day_repository import SupplyRow
from apps.batch.supply_stage import run_supply_stage
from apps.batch.tagged_candidate_fetcher import TaggedCandidateFetcher


class FakeRpc:
    def __init__(self):
        self.calls = []

    def rpc(self, function, params):
        self.calls.append((function, params))
        return {"ok": True}


class FakeCandidateRow:
    def __init__(self, candidate_id, ticker, strategies=None):
        self.candidate_id = candidate_id
        self.ticker = ticker
        self.strategies = strategies or []


class FakeTaggedFetcher:
    def __init__(self, rows=None, error=None):
        self.rows = rows if rows is not None else []
        self.error = error
        self.calls = []

    def fetch(self, run_id):
        self.calls.append(run_id)
        if self.error is not None:
            raise self.error
        return self.rows


class FakeCalendarClient:
    def __init__(self, days=None, error=None):
        self.days = days if days is not None else []
        self.error = error
        self.calls = []

    def recent_open_days(self, cutoff, count):
        self.calls.append((cutoff, count))
        if self.error is not None:
            raise self.error
        return self.days


class FakeSupplyProvider:
    def __init__(self, by_ticker):
        self.by_ticker = by_ticker
        self.calls = []

    def fetch(self, ticker, fromdt, todt):
        self.calls.append((ticker, fromdt, todt))
        outcome = self.by_ticker[ticker]
        if isinstance(outcome, Exception):
            raise outcome
        return outcome


class FakeProgramSupplyProvider:
    def __init__(self, by_ticker):
        self.by_ticker = by_ticker
        self.calls = []

    def fetch(self, ticker, fromdt, todt):
        self.calls.append((ticker, fromdt, todt))
        outcome = self.by_ticker[ticker]
        if isinstance(outcome, Exception):
            raise outcome
        return outcome


class FakeSupplyRepo:
    def __init__(self, fail=False):
        self.fail = fail
        self.saved: list[SupplyRow] = []

    def upsert_rows(self, rows):
        if self.fail:
            raise RuntimeError("supabase upsert failed")
        self.saved.extend(rows)
        return len(rows)


D2 = date(2026, 8, 28)
D1 = date(2026, 8, 31)
D0 = date(2026, 9, 1)


def _bars(ticker: str, *, missing_day: date | None = None) -> list[SupplyBar]:
    all_bars = {
        D2: SupplyBar(D2, 100.0, 1.0, 1000.0, -10.0, 20.0, 30.0),
        D1: SupplyBar(D1, 101.0, 1.5, 1100.0, -11.0, 21.0, 31.0),
        D0: SupplyBar(D0, 102.0, 2.0, 1200.0, -12.0, 22.0, 32.0),
    }
    if missing_day is not None:
        del all_bars[missing_day]
    return list(all_bars.values())


def _program_bars(*, missing_day: date | None = None) -> list[ProgramSupplyBar]:
    all_bars = {
        D2: ProgramSupplyBar(D2, 10.0),
        D1: ProgramSupplyBar(D1, 20.0),
        D0: ProgramSupplyBar(D0, 30.0),
    }
    if missing_day is not None:
        del all_bars[missing_day]
    return list(all_bars.values())


def _run(rpc, tagged_fetcher, calendar_client, supply_provider, supply_repo, program_provider=None):
    gateway = RunStateGateway(rpc)
    run_id = uuid4()
    lease_token = uuid4()
    if program_provider is None:
        program_provider = FakeProgramSupplyProvider({
            candidate.ticker: _program_bars() for candidate in tagged_fetcher.rows
        })
    return run_supply_stage(
        gateway, tagged_fetcher, calendar_client, supply_provider, program_provider, supply_repo,
        run_id, 1, lease_token, D0,
    )


# --- I/O & Edge-Case Matrix --------------------------------------------------


def test_normal_all_candidates_produce_three_rows_confirmed():
    fetcher = FakeTaggedFetcher([FakeCandidateRow("c1", "005930")])
    calendar = FakeCalendarClient([D0, D1, D2])  # descending, as recent_open_days returns
    provider = FakeSupplyProvider({"005930": _bars("005930")})
    program_provider = FakeProgramSupplyProvider({"005930": _program_bars()})
    repo = FakeSupplyRepo()
    rpc = FakeRpc()

    result = _run(rpc, fetcher, calendar, provider, repo, program_provider)

    assert result.status == "success"
    assert result.result_code == "OK"
    assert result.row_count == 3
    assert result.error_count == 0
    assert len(repo.saved) == 3
    slots = {row.slot: row for row in repo.saved}
    assert slots["D-2"].trading_day == D2
    assert slots["D-1"].trading_day == D1
    assert slots["D0"].trading_day == D0
    assert {row.slot: row.program_net for row in repo.saved} == {"D-2": 10.0, "D-1": 20.0, "D0": 30.0}
    assert slots["D0"].change_pct == 2.0  # diff carried through unchanged (no recompute)
    assert slots["D0"].investor_net_status == "confirmed"
    assert slots["D0"].program_net == 30.0
    assert slots["D0"].foreign_net == 22.0
    assert slots["D0"].institution_net == 32.0
    assert slots["D0"].individual_net == -12.0
    # 후보당 1콜, fromdt=D-2, todt=D0.
    assert provider.calls == [("005930", D2, D0)]
    assert program_provider.calls == [("005930", D2, D0)]
    write_stage_calls = [c for c in rpc.calls if c[0] == "write_stage"]
    assert [c[1]["p_status"] for c in write_stage_calls] == ["running", "success"]
    assert write_stage_calls[-1][1]["p_unprocessed_count"] == 0


def test_f_only_and_multi_tag_candidates_each_make_one_supply_call():
    fetcher = FakeTaggedFetcher([
        FakeCandidateRow("c1", "005930", ["F"]),
        FakeCandidateRow("c2", "000660", ["A", "F"]),
    ])
    calendar = FakeCalendarClient([D0, D1, D2])
    provider = FakeSupplyProvider({"005930": _bars("005930"), "000660": _bars("000660")})
    repo = FakeSupplyRepo()
    rpc = FakeRpc()

    result = _run(rpc, fetcher, calendar, provider, repo)

    assert result.status == "success"
    assert len(repo.saved) == 6
    assert provider.calls == [
        ("005930", D2, D0),
        ("000660", D2, D0),
    ]
    for candidate_id in ("c1", "c2"):
        candidate_rows = [row for row in repo.saved if row.candidate_id == candidate_id]
        assert len(candidate_rows) == 3
        assert {row.slot for row in candidate_rows} == {"D-2", "D-1", "D0"}


def test_real_tagged_fetcher_f_only_candidate_reaches_supply_stage_once():
    def handler(request):
        if request.url.path == "/rest/v1/candidate_tags":
            assert request.url.params["status"] == "eq.active"
            assert "strategy" not in request.url.params
            return httpx.Response(200, json=[{"candidate_id": "f-only"}])
        assert request.url.path == "/rest/v1/candidates"
        return httpx.Response(200, json=[{"candidate_id": "f-only", "ticker": "005930"}])

    tagged_fetcher = TaggedCandidateFetcher(
        "https://example.supabase.co",
        "service-role-key",
        http_client=httpx.Client(transport=httpx.MockTransport(handler)),
    )
    calendar = FakeCalendarClient([D0, D1, D2])
    provider = FakeSupplyProvider({"005930": _bars("005930")})
    repo = FakeSupplyRepo()
    rpc = FakeRpc()

    try:
        result = _run(
            rpc,
            tagged_fetcher,
            calendar,
            provider,
            repo,
            FakeProgramSupplyProvider({"005930": _program_bars()}),
        )
    finally:
        tagged_fetcher.close()

    assert result.status == "success"
    assert len(repo.saved) == 3
    assert provider.calls == [("005930", D2, D0)]


def test_per_ticker_api_failure_is_error_others_still_saved():
    fetcher = FakeTaggedFetcher([FakeCandidateRow("c1", "005930"), FakeCandidateRow("c2", "000660")])
    calendar = FakeCalendarClient([D0, D1, D2])
    provider = FakeSupplyProvider({
        "005930": RuntimeError("LS t1702 lookup failed: HTTP_ERROR"),
        "000660": _bars("000660"),
    })
    repo = FakeSupplyRepo()
    rpc = FakeRpc()

    result = _run(rpc, fetcher, calendar, provider, repo)

    assert result.status == "partial"
    assert result.result_code == "PARTIAL_SUPPLY"
    assert result.error_count == 1
    assert result.row_count == 3
    assert len(repo.saved) == 3
    write_stage_calls = [c for c in rpc.calls if c[0] == "write_stage"]
    assert write_stage_calls[-1][1]["p_status"] == "partial"
    assert write_stage_calls[-1][1]["p_unprocessed_count"] == 1


def test_program_api_failure_is_error_others_still_saved():
    fetcher = FakeTaggedFetcher([FakeCandidateRow("c1", "005930"), FakeCandidateRow("c2", "000660")])
    calendar = FakeCalendarClient([D0, D1, D2])
    supply_provider = FakeSupplyProvider({"005930": _bars("005930"), "000660": _bars("000660")})
    program_provider = FakeProgramSupplyProvider({
        "005930": RuntimeError("LS t1637 lookup failed: HTTP_ERROR"),
        "000660": _program_bars(),
    })
    repo = FakeSupplyRepo()
    rpc = FakeRpc()

    result = _run(rpc, fetcher, calendar, supply_provider, repo, program_provider)

    assert result.status == "partial"
    assert result.error_count == 1
    assert result.row_count == 3
    assert all(row.candidate_id == "c2" for row in repo.saved)


def test_program_missing_or_duplicate_day_is_error_without_partial_rows():
    fetcher = FakeTaggedFetcher([FakeCandidateRow("c1", "005930"), FakeCandidateRow("c2", "000660")])
    calendar = FakeCalendarClient([D0, D1, D2])
    supply_provider = FakeSupplyProvider({"005930": _bars("005930"), "000660": _bars("000660")})
    duplicate = _program_bars() + [ProgramSupplyBar(D0, 999.0)]
    program_provider = FakeProgramSupplyProvider({
        "005930": _program_bars(missing_day=D1),
        "000660": duplicate,
    })
    repo = FakeSupplyRepo()
    rpc = FakeRpc()

    result = _run(rpc, fetcher, calendar, supply_provider, repo, program_provider)

    assert result.status == "partial"
    assert result.error_count == 2
    assert result.row_count == 0
    assert repo.saved == []


def test_missing_expected_trading_day_in_response_is_error_not_silently_dropped():
    fetcher = FakeTaggedFetcher([FakeCandidateRow("c1", "005930")])
    calendar = FakeCalendarClient([D0, D1, D2])
    provider = FakeSupplyProvider({"005930": _bars("005930", missing_day=D1)})
    repo = FakeSupplyRepo()
    rpc = FakeRpc()

    result = _run(rpc, fetcher, calendar, provider, repo)

    assert result.status == "partial"
    assert result.result_code == "PARTIAL_SUPPLY"
    assert result.error_count == 1
    assert result.row_count == 0
    assert repo.saved == []


def test_duplicate_trading_day_in_response_is_error_not_silently_overwritten():
    """리뷰 patch: 같은 candidate에 동일 trading_day를 가진 중복 행이 응답에 있으면
    dict comprehension이 조용히 마지막 행으로 덮어쓰지 않고 error로 집계해야 한다."""
    fetcher = FakeTaggedFetcher([FakeCandidateRow("c1", "005930"), FakeCandidateRow("c2", "000660")])
    calendar = FakeCalendarClient([D0, D1, D2])
    duplicate_bars = _bars("005930") + [SupplyBar(D0, 999.0, 9.0, 9999.0, -9.0, 9.0, 9.0)]
    provider = FakeSupplyProvider({
        "005930": duplicate_bars,
        "000660": _bars("000660"),
    })
    repo = FakeSupplyRepo()
    rpc = FakeRpc()

    result = _run(rpc, fetcher, calendar, provider, repo)

    assert result.status == "partial"
    assert result.result_code == "PARTIAL_SUPPLY"
    assert result.error_count == 1
    assert result.row_count == 3
    assert len(repo.saved) == 3
    # 중복 응답을 받은 005930의 행은 저장되지 않았어야 한다(조용한 덮어쓰기 금지).
    assert all(row.candidate_id != "c1" for row in repo.saved)


def test_holiday_gap_calendar_mapping_is_exact_not_approximated_by_calendar_days():
    """연휴 직후: recent_open_days가 반환한 실제 거래일 3건을 그대로 D-2/D-1/D0에 매핑한다
    (달력일로 근사하지 않는다). 예: 목/금/월요일이 최근 3개장일이면 D-2=목, D-1=금, D0=월.
    """
    thursday = date(2026, 8, 27)
    friday = date(2026, 8, 28)
    monday = date(2026, 8, 31)
    fetcher = FakeTaggedFetcher([FakeCandidateRow("c1", "005930")])
    calendar = FakeCalendarClient([monday, friday, thursday])  # descending
    bars = [
        SupplyBar(thursday, 100.0, 1.0, 1000.0, -10.0, 20.0, 30.0),
        SupplyBar(friday, 101.0, 1.5, 1100.0, -11.0, 21.0, 31.0),
        SupplyBar(monday, 102.0, 2.0, 1200.0, -12.0, 22.0, 32.0),
    ]
    provider = FakeSupplyProvider({"005930": bars})
    repo = FakeSupplyRepo()
    rpc = FakeRpc()

    gateway = RunStateGateway(rpc)
    result = run_supply_stage(
        gateway, fetcher, calendar, provider,
        FakeProgramSupplyProvider({
            "005930": [
                ProgramSupplyBar(thursday, 10.0),
                ProgramSupplyBar(friday, 20.0),
                ProgramSupplyBar(monday, 30.0),
            ]
        }),
        repo, uuid4(), 1, uuid4(), monday,
    )

    assert result.status == "success"
    slots = {row.slot: row for row in repo.saved}
    assert slots["D-2"].trading_day == thursday
    assert slots["D-1"].trading_day == friday
    assert slots["D0"].trading_day == monday
    assert provider.calls == [("005930", thursday, monday)]


def test_no_tagged_candidates_is_success_with_zero_rows_and_no_calendar_or_provider_calls():
    fetcher = FakeTaggedFetcher([])
    calendar = FakeCalendarClient([D0, D1, D2])
    provider = FakeSupplyProvider({})
    repo = FakeSupplyRepo()
    rpc = FakeRpc()

    result = _run(rpc, fetcher, calendar, provider, repo)

    assert result.status == "success"
    assert result.result_code == "OK"
    assert result.row_count == 0
    assert result.candidate_count == 0
    assert calendar.calls == []
    assert provider.calls == []
    write_stage_calls = [c for c in rpc.calls if c[0] == "write_stage"]
    assert [c[1]["p_status"] for c in write_stage_calls] == ["running", "success"]


def test_tagged_candidate_fetch_failure_records_failed_stage_without_silent_empty_success():
    fetcher = FakeTaggedFetcher(error=RuntimeError("candidate_tags fetch boom"))
    calendar = FakeCalendarClient([D0, D1, D2])
    provider = FakeSupplyProvider({})
    repo = FakeSupplyRepo()
    rpc = FakeRpc()

    result = _run(rpc, fetcher, calendar, provider, repo)

    assert result.status == "failed"
    assert result.result_code == "TAGGED_CANDIDATE_FETCH_FAILED"
    write_stage_calls = [c for c in rpc.calls if c[0] == "write_stage"]
    assert [c[1]["p_status"] for c in write_stage_calls] == ["running", "failed"]
    assert repo.saved == []


def test_calendar_lookup_failure_records_failed_stage():
    fetcher = FakeTaggedFetcher([FakeCandidateRow("c1", "005930")])
    calendar = FakeCalendarClient(error=RuntimeError("trading_calendar boom"))
    provider = FakeSupplyProvider({})
    repo = FakeSupplyRepo()
    rpc = FakeRpc()

    result = _run(rpc, fetcher, calendar, provider, repo)

    assert result.status == "failed"
    assert result.result_code == "CALENDAR_LOOKUP_FAILED"


def test_calendar_insufficient_trading_days_records_failed_stage():
    fetcher = FakeTaggedFetcher([FakeCandidateRow("c1", "005930")])
    calendar = FakeCalendarClient([D0, D1])  # only 2, not 3
    provider = FakeSupplyProvider({})
    repo = FakeSupplyRepo()
    rpc = FakeRpc()

    result = _run(rpc, fetcher, calendar, provider, repo)

    assert result.status == "failed"
    assert result.result_code == "CALENDAR_INSUFFICIENT_TRADING_DAYS"


def test_supply_persist_failure_records_failed_stage():
    fetcher = FakeTaggedFetcher([FakeCandidateRow("c1", "005930")])
    calendar = FakeCalendarClient([D0, D1, D2])
    provider = FakeSupplyProvider({"005930": _bars("005930")})
    repo = FakeSupplyRepo(fail=True)
    rpc = FakeRpc()

    result = _run(rpc, fetcher, calendar, provider, repo)

    assert result.status == "failed"
    assert result.result_code == "SUPPLY_PERSIST_FAILED"
    write_stage_calls = [c for c in rpc.calls if c[0] == "write_stage"]
    assert write_stage_calls[-1][1]["p_status"] == "failed"
