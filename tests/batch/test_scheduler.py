from datetime import date, datetime, time, timezone
from uuid import uuid4

from apps.batch.ls_client import LsResponse
from apps.batch.run_state import RunStateGateway
from apps.batch.scheduler import run_scheduled_batch
from domain.calendar import TradingCalendarEntry
from domain.ohlcv_cache import OhlcvCacheStatus
from domain.run_state import BatchKind, Trigger


class FakeProvider:
    def __init__(self, value=True):
        self.value = value
        self.calls = 0

    def has_daily_bar(self, trading_day):
        self.calls += 1
        return self.value


class RaisingProvider:
    def has_daily_bar(self, trading_day):
        raise TimeoutError("LS unavailable")


class FakeRepository:
    def __init__(self, cached=None, *, recent_open_days=None):
        self._cached = cached or {}
        self.saved = []
        self._recent_open_days = recent_open_days
        self.recent_open_days_calls = []

    def get(self, trading_day):
        return self._cached.get(trading_day)

    def upsert(self, decision):
        self.saved.append(decision)
        if decision.entry is not None:
            self._cached[decision.entry.trading_day] = decision.entry

    def recent_open_days(self, cutoff, count):
        self.recent_open_days_calls.append((cutoff, count))
        if self._recent_open_days is not None:
            return self._recent_open_days
        from datetime import timedelta
        return [cutoff - timedelta(days=offset) for offset in range(count)]


class FakeRpc:
    def __init__(self, attempt=None, replayed=False, raise_on=None):
        self.calls = []
        self.attempt = attempt
        self.replayed = replayed
        self.raise_on = raise_on or set()

    def rpc(self, function, params):
        self.calls.append((function, params))
        if function in self.raise_on:
            raise RuntimeError(f"{function} boom")
        if function == "start_attempt" and self.replayed:
            return {"replayed": True, "run_id": str(uuid4()), "logical_run_key": params["p_logical_run_key"]}
        if function == "start_attempt":
            return self.attempt
        return {"ok": True}


class FakeCandidateClient:
    def __init__(self, response=None):
        self.response = response if response is not None else LsResponse(data=[])
        self.calls = []

    def request(self, tr_code, params):
        self.calls.append((tr_code, params))
        return self.response


# --- Story 2.5: ohlcv 확보/갱신 + tags stage 배선용 fakes ---------------------


class FakeOhlcvProvider:
    def __init__(self):
        self.fetch_full_history_calls = []
        self.fetch_range_calls = []

    def fetch_full_history(self, ticker, cutoff):
        self.fetch_full_history_calls.append((ticker, cutoff))
        return []

    def fetch_range(self, ticker, start, end):
        self.fetch_range_calls.append((ticker, start, end))
        return []


class FakeOhlcvRepository:
    """existing_tickers가 전부 존재로 답해 initialize_new_ticker_history가 LS를
    호출하지 않게 하고, latest_state는 비워 update_existing_ticker_history도
    LS를 호출하지 않게 한다 -- 이 파일의 관심사는 배선(호출 순서/인자) 검증이다."""

    def __init__(self):
        self.existing_tickers_calls = []
        self.latest_state_calls = []

    def existing_tickers(self, tickers):
        self.existing_tickers_calls.append(list(tickers))
        return set(tickers)

    def latest_state(self, tickers):
        self.latest_state_calls.append(list(tickers))
        return {}

    def upsert_rows(self, ticker, rows, *, adjustment_version=1):
        raise AssertionError("upsert_rows should not be called given existing_tickers/latest_state stubs")


class FakeCandidateFetcher:
    def __init__(self, rows=None):
        self.rows = rows if rows is not None else []
        self.calls = []

    def fetch(self, run_id):
        self.calls.append(run_id)
        return self.rows


class FakeOhlcvLoader:
    def __init__(self, status=OhlcvCacheStatus.INELIGIBLE_INSUFFICIENT_HISTORY):
        self.status = status
        self.calls = []

    def load_ohlcv(self, ticker, cutoff):
        self.calls.append((ticker, cutoff))
        return self.status


class FakeTagsRepository:
    def __init__(self):
        self.upsert_calls = []
        self.sync_vanished_calls = []

    def upsert_tags(self, tags):
        self.upsert_calls.append(list(tags))
        return len(tags)

    def sync_vanished(self, run_id):
        self.sync_vanished_calls.append(run_id)
        return {"vanished_count": 0}


class FakeTaggedCandidateFetcher:
    def __init__(self, rows=None):
        self.rows = rows if rows is not None else []
        self.calls = []

    def fetch(self, run_id):
        self.calls.append(run_id)
        return self.rows


class FakeSupplyProvider:
    def __init__(self, by_ticker=None):
        self.by_ticker = by_ticker or {}
        self.calls = []

    def fetch(self, ticker, fromdt, todt):
        self.calls.append((ticker, fromdt, todt))
        outcome = self.by_ticker.get(ticker, [])
        if isinstance(outcome, Exception):
            raise outcome
        return outcome


class FakeProgramSupplyProvider:
    def __init__(self, by_ticker=None):
        self.by_ticker = by_ticker or {}
        self.calls = []

    def fetch(self, ticker, fromdt, todt):
        self.calls.append((ticker, fromdt, todt))
        outcome = self.by_ticker.get(ticker, [])
        if isinstance(outcome, Exception):
            raise outcome
        return outcome


class FakeSupplyRepository:
    def __init__(self):
        self.upsert_calls = []

    def upsert_rows(self, rows):
        self.upsert_calls.append(list(rows))
        return len(rows)


def tags_deps(*, candidate_rows=None, ohlcv_status=OhlcvCacheStatus.INELIGIBLE_INSUFFICIENT_HISTORY,
              tagged_candidate_rows=None, supply_by_ticker=None):
    """tags/supply 파이프라인 배선에 필요한 신규 의존성을 fresh하게 만들어 반환한다."""
    return {
        "ohlcv_provider": FakeOhlcvProvider(),
        "ohlcv_repository": FakeOhlcvRepository(),
        "candidate_fetcher": FakeCandidateFetcher(candidate_rows),
        "ohlcv_loader": FakeOhlcvLoader(ohlcv_status),
        "tags_repository": FakeTagsRepository(),
        "tagged_candidate_fetcher": FakeTaggedCandidateFetcher(tagged_candidate_rows),
        "supply_provider": FakeSupplyProvider(supply_by_ticker),
        "program_supply_provider": FakeProgramSupplyProvider(),
        "supply_repository": FakeSupplyRepository(),
    }


def attempt_payload(logical_run_key="close:2026-09-01"):
    return {
        "run_id": str(uuid4()),
        "logical_run_key": logical_run_key,
        "attempt_no": 1,
        "fence_token": 1,
        "lease_token": str(uuid4()),
        "lease_expires_at": datetime.now(timezone.utc).isoformat(),
    }


def test_holiday_skips_without_calling_candidate_client():
    cached_closed = TradingCalendarEntry(date(2026, 9, 1), False)
    repo = FakeRepository(cached={date(2026, 9, 1): cached_closed})
    rpc = FakeRpc(attempt=attempt_payload())
    gateway = RunStateGateway(rpc)
    candidate_client = FakeCandidateClient()
    provider = FakeProvider()
    deps = tags_deps()

    result = run_scheduled_batch(
        BatchKind.CLOSE,
        datetime(2026, 9, 1, 8, 30),
        repo,
        provider,
        gateway,
        candidate_client,
        deps["ohlcv_provider"],
        deps["ohlcv_repository"],
        deps["candidate_fetcher"],
        deps["ohlcv_loader"],
        deps["tags_repository"],
        deps["tagged_candidate_fetcher"], deps["supply_provider"],
        deps["program_supply_provider"], deps["supply_repository"],
    )

    assert result.status == "skipped"
    assert result.skip_reason == "holiday"
    assert provider.calls == 0
    assert candidate_client.calls == []
    assert [call[0] for call in rpc.calls] == ["start_attempt", "skip_attempt"]
    skip_call = rpc.calls[-1][1]
    assert skip_call["p_skip_reason"] == "holiday"
    # 휴장은 candidates stage 자체가 실행되지 않으므로 ohlcv/tags 파이프라인도 실행되지 않는다.
    assert deps["candidate_fetcher"].calls == []
    assert deps["ohlcv_provider"].fetch_full_history_calls == []


def test_open_day_delegates_to_candidate_stage_with_schedule_trigger():
    cached_open = TradingCalendarEntry(date(2026, 9, 1), True, time(9), time(15, 30))
    repo = FakeRepository(cached={date(2026, 9, 1): cached_open})
    rpc = FakeRpc(attempt=attempt_payload())
    gateway = RunStateGateway(rpc)
    candidate_client = FakeCandidateClient(LsResponse(data=[{"ticker": "005930", "trading_value": 1}]))
    deps = tags_deps()

    result = run_scheduled_batch(
        BatchKind.CLOSE,
        datetime(2026, 9, 1, 16, 0),
        repo,
        FakeProvider(),
        gateway,
        candidate_client,
        deps["ohlcv_provider"],
        deps["ohlcv_repository"],
        deps["candidate_fetcher"],
        deps["ohlcv_loader"],
        deps["tags_repository"],
        deps["tagged_candidate_fetcher"], deps["supply_provider"],
        deps["program_supply_provider"], deps["supply_repository"],
    )

    assert result.status == "success"
    assert result.candidate_count == 1
    start_params = rpc.calls[0][1]
    assert start_params["p_trigger"] == "schedule"
    assert start_params["p_batch_kind"] == "close"


def test_success_candidates_stage_wires_ohlcv_and_tags_pipeline():
    cached_open = TradingCalendarEntry(date(2026, 9, 1), True, time(9), time(15, 30))
    repo = FakeRepository(cached={date(2026, 9, 1): cached_open})
    attempt = attempt_payload()
    rpc = FakeRpc(attempt=attempt)
    gateway = RunStateGateway(rpc)
    candidate_client = FakeCandidateClient(LsResponse(data=[{"ticker": "005930", "trading_value": 1}]))
    deps = tags_deps()

    result = run_scheduled_batch(
        BatchKind.CLOSE,
        datetime(2026, 9, 1, 16, 0),
        repo,
        FakeProvider(),
        gateway,
        candidate_client,
        deps["ohlcv_provider"],
        deps["ohlcv_repository"],
        deps["candidate_fetcher"],
        deps["ohlcv_loader"],
        deps["tags_repository"],
        deps["tagged_candidate_fetcher"], deps["supply_provider"],
        deps["program_supply_provider"], deps["supply_repository"],
    )

    assert result.status == "success"
    # ohlcv 확보/갱신이 후보 티커 목록으로 호출된다(초기화/증분 갱신 각 1회씩).
    assert deps["ohlcv_repository"].existing_tickers_calls == [["005930"]]
    assert deps["ohlcv_repository"].latest_state_calls == [["005930"]]
    # tags stage가 이어서 실행되어 후보 조회 + write_stage 호출이 발생한다.
    assert deps["candidate_fetcher"].calls == [attempt["run_id"]]
    write_stage_calls = [call for call in rpc.calls if call[0] == "write_stage"]
    tags_stage_calls = [call for call in write_stage_calls if call[1]["p_stage"] == "tags"]
    assert [call[1]["p_status"] for call in tags_stage_calls] == ["running", "success"]
    # Story 4.1: tags stage 직후 supply stage도 배선되어 태깅된 후보 조회 + write_stage가 발생한다.
    supply_stage_calls = [call for call in write_stage_calls if call[1]["p_stage"] == "supply_3day"]
    assert [call[1]["p_status"] for call in supply_stage_calls] == ["running", "success"]


# --- Story 4.1: supply stage 배선 --------------------------------------------


def test_supply_stage_runs_after_tags_with_tagged_candidates():
    """태깅된 후보가 있으면 supply stage가 종목당 1콜로 t1702를 호출하고 행을 저장한다."""
    cached_open = TradingCalendarEntry(date(2026, 9, 1), True, time(9), time(15, 30))
    repo = FakeRepository(
        cached={date(2026, 9, 1): cached_open},
        recent_open_days=[date(2026, 9, 1), date(2026, 8, 31), date(2026, 8, 28)],
    )
    attempt = attempt_payload()
    rpc = FakeRpc(attempt=attempt)
    gateway = RunStateGateway(rpc)
    candidate_client = FakeCandidateClient(LsResponse(data=[{"ticker": "005930", "trading_value": 1}]))
    from apps.batch.ls_supply_provider import SupplyBar
    from apps.batch.ls_program_supply_provider import ProgramSupplyBar

    d2, d1, d0 = date(2026, 8, 28), date(2026, 8, 31), date(2026, 9, 1)
    bars = [
        SupplyBar(d2, 100.0, 1.0, 1000.0, -10.0, 20.0, 30.0),
        SupplyBar(d1, 101.0, 1.5, 1100.0, -11.0, 21.0, 31.0),
        SupplyBar(d0, 102.0, 2.0, 1200.0, -12.0, 22.0, 32.0),
    ]
    from collections import namedtuple

    TaggedRow = namedtuple("TaggedRow", ["candidate_id", "ticker"])
    deps = tags_deps(
        tagged_candidate_rows=[TaggedRow("c1", "005930")],
        supply_by_ticker={"005930": bars},
    )
    deps["program_supply_provider"] = FakeProgramSupplyProvider({
        "005930": [
            ProgramSupplyBar(d2, 10.0),
            ProgramSupplyBar(d1, 20.0),
            ProgramSupplyBar(d0, 30.0),
        ]
    })
    deps["ohlcv_repository"] = FakeOhlcvRepository()

    result = run_scheduled_batch(
        BatchKind.CLOSE,
        datetime(2026, 9, 1, 16, 0),
        repo,
        FakeProvider(),
        gateway,
        candidate_client,
        deps["ohlcv_provider"],
        deps["ohlcv_repository"],
        deps["candidate_fetcher"],
        deps["ohlcv_loader"],
        deps["tags_repository"],
        deps["tagged_candidate_fetcher"], deps["supply_provider"],
        deps["program_supply_provider"], deps["supply_repository"],
    )

    assert result.status == "success"
    assert result.supply_status == "success"
    assert deps["supply_provider"].calls == [("005930", d2, d0)]
    assert deps["program_supply_provider"].calls == [("005930", d2, d0)]
    assert len(deps["supply_repository"].upsert_calls[0]) == 3
    write_stage_calls = [call for call in rpc.calls if call[0] == "write_stage"]
    supply_stage_calls = [call for call in write_stage_calls if call[1]["p_stage"] == "supply_3day"]
    assert [call[1]["p_status"] for call in supply_stage_calls] == ["running", "success"]


def test_intraday_scheduler_keeps_all_zero_d0_pending_and_retries_semantically():
    """실제 intraday scheduler 경로가 batch kind를 전달해 D0 all-zero를 pending으로 저장한다."""
    cached_open = TradingCalendarEntry(date(2026, 9, 1), True, time(9), time(15, 30))
    d2, d1, d0 = date(2026, 8, 28), date(2026, 8, 31), date(2026, 9, 1)
    repo = FakeRepository(
        cached={d0: cached_open},
        recent_open_days=[d0, d1, d2],
    )
    attempt = attempt_payload("intraday:2026-09-01:09:30")
    rpc = FakeRpc(attempt=attempt)
    gateway = RunStateGateway(rpc)
    candidate_client = FakeCandidateClient(LsResponse(data=[{"ticker": "005930", "trading_value": 1}]))
    from collections import namedtuple
    from apps.batch.ls_supply_provider import SupplyBar
    from apps.batch.ls_program_supply_provider import ProgramSupplyBar

    TaggedRow = namedtuple("TaggedRow", ["candidate_id", "ticker"])
    zero_bars = [
        SupplyBar(d2, 100.0, 1.0, 1000.0, -10.0, 20.0, 30.0),
        SupplyBar(d1, 101.0, 1.5, 1100.0, -11.0, 21.0, 31.0),
        SupplyBar(d0, 102.0, 2.0, 1200.0, 0.0, 0.0, 0.0),
    ]
    deps = tags_deps(
        tagged_candidate_rows=[TaggedRow("c1", "005930")],
        supply_by_ticker={"005930": zero_bars},
    )
    deps["program_supply_provider"] = FakeProgramSupplyProvider({
        "005930": [
            ProgramSupplyBar(d2, 10.0),
            ProgramSupplyBar(d1, 20.0),
            ProgramSupplyBar(d0, 0.0),
        ]
    })

    result = run_scheduled_batch(
        BatchKind.INTRADAY,
        datetime(2026, 9, 1, 9, 30),
        repo,
        FakeProvider(),
        gateway,
        candidate_client,
        deps["ohlcv_provider"],
        deps["ohlcv_repository"],
        deps["candidate_fetcher"],
        deps["ohlcv_loader"],
        deps["tags_repository"],
        deps["tagged_candidate_fetcher"], deps["supply_provider"],
        deps["program_supply_provider"], deps["supply_repository"],
    )

    assert result.status == "success"
    assert result.supply_status == "success"
    assert deps["supply_provider"].calls == [("005930", d2, d0), ("005930", d2, d0)]
    assert deps["program_supply_provider"].calls == [("005930", d2, d0), ("005930", d2, d0)]
    rows = {row.slot: row for row in deps["supply_repository"].upsert_calls[0]}
    assert rows["D0"].investor_net_status == "pending"
    assert (rows["D0"].foreign_net, rows["D0"].institution_net,
            rows["D0"].individual_net, rows["D0"].program_net) == (None, None, None, None)


def test_supply_stage_failure_surfaces_in_scheduler_result_and_blocks_publish():
    """supply stage가 failed로 종결되면 배치 전체 결과도 failed여야 하고 publish_attempt는 호출되지 않는다."""
    cached_open = TradingCalendarEntry(date(2026, 9, 1), True, time(9), time(15, 30))
    repo = FakeRepository(cached={date(2026, 9, 1): cached_open})
    attempt = attempt_payload()
    rpc = FakeRpc(attempt=attempt)
    gateway = RunStateGateway(rpc)
    candidate_client = FakeCandidateClient(LsResponse(data=[{"ticker": "005930", "trading_value": 1}]))

    class RaisingTaggedCandidateFetcher:
        def fetch(self, run_id):
            raise RuntimeError("candidate_tags fetch boom")

    deps = tags_deps()
    deps["tagged_candidate_fetcher"] = RaisingTaggedCandidateFetcher()

    result = run_scheduled_batch(
        BatchKind.CLOSE,
        datetime(2026, 9, 1, 16, 0),
        repo,
        FakeProvider(),
        gateway,
        candidate_client,
        deps["ohlcv_provider"],
        deps["ohlcv_repository"],
        deps["candidate_fetcher"],
        deps["ohlcv_loader"],
        deps["tags_repository"],
        deps["tagged_candidate_fetcher"], deps["supply_provider"],
        deps["program_supply_provider"], deps["supply_repository"],
    )

    assert result.status == "failed"
    assert result.supply_status == "failed"
    assert result.supply_result_code == "TAGGED_CANDIDATE_FETCH_FAILED"
    assert _publish_attempt_calls(rpc) == []


def test_partial_program_supply_surfaces_in_scheduler_result_and_blocks_publish():
    """후보별 t1637 실패는 supply partial로 전파되고 close publish를 막아야 한다."""
    cached_open = TradingCalendarEntry(date(2026, 9, 1), True, time(9), time(15, 30))
    repo = FakeRepository(
        cached={date(2026, 9, 1): cached_open},
        recent_open_days=[date(2026, 9, 1), date(2026, 8, 31), date(2026, 8, 28)],
    )
    attempt = attempt_payload()
    rpc = FakeRpc(attempt=attempt)
    gateway = RunStateGateway(rpc)
    candidate_client = FakeCandidateClient(LsResponse(data=[{"ticker": "005930", "trading_value": 1}]))
    from collections import namedtuple
    from apps.batch.ls_supply_provider import SupplyBar

    TaggedRow = namedtuple("TaggedRow", ["candidate_id", "ticker"])
    d2, d1, d0 = date(2026, 8, 28), date(2026, 8, 31), date(2026, 9, 1)
    deps = tags_deps(
        tagged_candidate_rows=[TaggedRow("c1", "005930")],
        supply_by_ticker={
            "005930": [
                SupplyBar(d2, 100.0, 1.0, 1000.0, -10.0, 20.0, 30.0),
                SupplyBar(d1, 101.0, 1.5, 1100.0, -11.0, 21.0, 31.0),
                SupplyBar(d0, 102.0, 2.0, 1200.0, -12.0, 22.0, 32.0),
            ]
        },
    )
    deps["program_supply_provider"] = FakeProgramSupplyProvider({"005930": RuntimeError("t1637 unavailable")})

    result = run_scheduled_batch(
        BatchKind.CLOSE,
        datetime(2026, 9, 1, 16, 0),
        repo,
        FakeProvider(),
        gateway,
        candidate_client,
        deps["ohlcv_provider"],
        deps["ohlcv_repository"],
        deps["candidate_fetcher"],
        deps["ohlcv_loader"],
        deps["tags_repository"],
        deps["tagged_candidate_fetcher"], deps["supply_provider"],
        deps["program_supply_provider"], deps["supply_repository"],
    )

    assert result.status == "partial"
    assert result.supply_status == "partial"
    assert result.supply_result_code == "PARTIAL_SUPPLY"
    assert len(deps["supply_repository"].upsert_calls) == 1
    missing_rows = deps["supply_repository"].upsert_calls[0]
    assert len(missing_rows) == 3
    assert all(row.investor_net_status == "missing" for row in missing_rows)
    assert all(
        value is None
        for row in missing_rows
        for value in (row.foreign_net, row.institution_net, row.individual_net, row.program_net)
    )
    assert _publish_attempt_calls(rpc) == []


def test_premarket_does_not_run_supply_stage():
    """리뷰 patch: premarket 시점엔 당일(D0) 거래 데이터가 아직 없어 t1702가 D0을 누락시키고
    모든 태깅된 후보가 상시 error(partial)로 집계된다 -- supply stage 자체를 호출하지 않아야 한다."""
    cached_open = TradingCalendarEntry(date(2026, 9, 1), True, time(9), time(15, 30))
    repo = FakeRepository(cached={date(2026, 9, 1): cached_open})
    rpc = FakeRpc(attempt=attempt_payload())
    gateway = RunStateGateway(rpc)
    candidate_client = FakeCandidateClient(LsResponse(data=[{"ticker": "005930", "trading_value": 1}]))
    from collections import namedtuple

    TaggedRow = namedtuple("TaggedRow", ["candidate_id", "ticker"])
    deps = tags_deps(tagged_candidate_rows=[TaggedRow("c1", "005930")])

    result = run_scheduled_batch(
        BatchKind.PREMARKET,
        datetime(2026, 9, 1, 8, 30),
        repo,
        FakeProvider(),
        gateway,
        candidate_client,
        deps["ohlcv_provider"],
        deps["ohlcv_repository"],
        deps["candidate_fetcher"],
        deps["ohlcv_loader"],
        deps["tags_repository"],
        deps["tagged_candidate_fetcher"], deps["supply_provider"],
        deps["program_supply_provider"], deps["supply_repository"],
    )

    assert result.status in ("success", "partial")
    assert result.supply_status is None
    assert result.supply_result_code is None
    assert deps["tagged_candidate_fetcher"].calls == []
    assert deps["supply_provider"].calls == []
    assert deps["program_supply_provider"].calls == []
    write_stage_calls = [call for call in rpc.calls if call[0] == "write_stage"]
    supply_stage_calls = [call for call in write_stage_calls if call[1]["p_stage"] == "supply_3day"]
    assert supply_stage_calls == []


def test_partial_candidates_stage_wires_ohlcv_and_tags_pipeline():
    cached_open = TradingCalendarEntry(date(2026, 9, 1), True, time(9), time(15, 30))
    repo = FakeRepository(cached={date(2026, 9, 1): cached_open})
    attempt = attempt_payload()
    rpc = FakeRpc(attempt=attempt)
    gateway = RunStateGateway(rpc)
    # unprocessed_count > 0 -- candidates stage가 partial로 종결된다.
    candidate_client = FakeCandidateClient(
        LsResponse(data=[{"ticker": "005930", "trading_value": 1}], unprocessed_count=1)
    )
    deps = tags_deps()

    result = run_scheduled_batch(
        BatchKind.CLOSE,
        datetime(2026, 9, 1, 16, 0),
        repo,
        FakeProvider(),
        gateway,
        candidate_client,
        deps["ohlcv_provider"],
        deps["ohlcv_repository"],
        deps["candidate_fetcher"],
        deps["ohlcv_loader"],
        deps["tags_repository"],
        deps["tagged_candidate_fetcher"], deps["supply_provider"],
        deps["program_supply_provider"], deps["supply_repository"],
    )

    assert result.status == "partial"
    # candidates가 partial이어도 ohlcv 확보/갱신 + tags stage가 그대로 배선된다(success/partial 모두 진행).
    assert deps["ohlcv_repository"].existing_tickers_calls == [["005930"]]
    assert deps["ohlcv_repository"].latest_state_calls == [["005930"]]
    assert deps["candidate_fetcher"].calls == [attempt["run_id"]]
    write_stage_calls = [call for call in rpc.calls if call[0] == "write_stage"]
    tags_stage_calls = [call for call in write_stage_calls if call[1]["p_stage"] == "tags"]
    assert [call[1]["p_status"] for call in tags_stage_calls] == ["running", "success"]


def test_tags_stage_failure_surfaces_in_scheduler_result_and_is_not_reported_as_success():
    """Story 2.5 코드 리뷰 발견(high) 수정 커버리지: 후보 재조회 실패로 tags stage가
    failed로 종결되면, run_scheduled_batch의 반환값도 success가 아니어야 하고
    tags stage 결과가 SchedulerResult에 노출되어야 한다."""
    cached_open = TradingCalendarEntry(date(2026, 9, 1), True, time(9), time(15, 30))
    repo = FakeRepository(cached={date(2026, 9, 1): cached_open})
    attempt = attempt_payload()
    rpc = FakeRpc(attempt=attempt)
    gateway = RunStateGateway(rpc)
    candidate_client = FakeCandidateClient(LsResponse(data=[{"ticker": "005930", "trading_value": 1}]))
    deps = tags_deps()

    class RaisingCandidateFetcher:
        def fetch(self, run_id):
            raise RuntimeError("candidate re-fetch boom")

    deps["candidate_fetcher"] = RaisingCandidateFetcher()

    result = run_scheduled_batch(
        BatchKind.CLOSE,
        datetime(2026, 9, 1, 16, 0),
        repo,
        FakeProvider(),
        gateway,
        candidate_client,
        deps["ohlcv_provider"],
        deps["ohlcv_repository"],
        deps["candidate_fetcher"],
        deps["ohlcv_loader"],
        deps["tags_repository"],
        deps["tagged_candidate_fetcher"], deps["supply_provider"],
        deps["program_supply_provider"], deps["supply_repository"],
    )

    # candidates stage 자체는 success였지만, tags stage가 failed면 전체 배치 결과도 failed여야 한다
    # -- 그래야 apps/batch/__main__.py의 CLI 종료 코드가 실제 실패를 반영한다.
    assert result.status == "failed"
    assert result.tags_status == "failed"
    assert result.tags_result_code == "CANDIDATE_FETCH_FAILED"
    write_stage_calls = [call for call in rpc.calls if call[0] == "write_stage"]
    tags_stage_calls = [call for call in write_stage_calls if call[1]["p_stage"] == "tags"]
    assert [call[1]["p_status"] for call in tags_stage_calls] == ["running", "failed"]


def test_tags_persist_failure_surfaces_as_failed_scheduler_result():
    """candidate_tags upsert 자체가 실패(TAGS_PERSIST_FAILED)하는 경로도 성공으로 보고되지 않는다."""
    cached_open = TradingCalendarEntry(date(2026, 9, 1), True, time(9), time(15, 30))
    repo = FakeRepository(cached={date(2026, 9, 1): cached_open})
    attempt = attempt_payload()
    rpc = FakeRpc(attempt=attempt)
    gateway = RunStateGateway(rpc)
    candidate_client = FakeCandidateClient(LsResponse(data=[{"ticker": "005930", "trading_value": 1}]))

    class RaisingTagsRepository:
        def upsert_tags(self, tags):
            raise RuntimeError("upsert boom")

    deps = tags_deps()
    deps["tags_repository"] = RaisingTagsRepository()

    result = run_scheduled_batch(
        BatchKind.CLOSE,
        datetime(2026, 9, 1, 16, 0),
        repo,
        FakeProvider(),
        gateway,
        candidate_client,
        deps["ohlcv_provider"],
        deps["ohlcv_repository"],
        deps["candidate_fetcher"],
        deps["ohlcv_loader"],
        deps["tags_repository"],
        deps["tagged_candidate_fetcher"], deps["supply_provider"],
        deps["program_supply_provider"], deps["supply_repository"],
    )

    # tags_stage는 all_tags가 비어도(후보 0건) upsert_tags를 호출하므로, upsert 자체가 예외를
    # 던지면 TAGS_PERSIST_FAILED로 종결되고 배치 전체 결과도 failed여야 한다.
    assert result.status == "failed"
    assert result.tags_status == "failed"
    assert result.tags_result_code == "TAGS_PERSIST_FAILED"


def test_failed_candidates_stage_does_not_run_ohlcv_or_tags_pipeline():
    cached_open = TradingCalendarEntry(date(2026, 9, 1), True, time(9), time(15, 30))
    repo = FakeRepository(cached={date(2026, 9, 1): cached_open})
    rpc = FakeRpc(attempt=attempt_payload())
    gateway = RunStateGateway(rpc)
    candidate_client = FakeCandidateClient(
        LsResponse(result_code="HTTP_ERROR", message="unavailable")
    )
    deps = tags_deps()

    result = run_scheduled_batch(
        BatchKind.CLOSE,
        datetime(2026, 9, 1, 16, 0),
        repo,
        FakeProvider(),
        gateway,
        candidate_client,
        deps["ohlcv_provider"],
        deps["ohlcv_repository"],
        deps["candidate_fetcher"],
        deps["ohlcv_loader"],
        deps["tags_repository"],
        deps["tagged_candidate_fetcher"], deps["supply_provider"],
        deps["program_supply_provider"], deps["supply_repository"],
    )

    assert result.status == "failed"
    assert deps["candidate_fetcher"].calls == []
    assert deps["ohlcv_repository"].existing_tickers_calls == []


def test_calendar_unavailable_is_treated_as_open_and_proceeds():
    repo = FakeRepository()
    rpc = FakeRpc(attempt=attempt_payload())
    gateway = RunStateGateway(rpc)
    candidate_client = FakeCandidateClient(LsResponse(data=[]))
    deps = tags_deps()

    result = run_scheduled_batch(
        BatchKind.PREMARKET,
        datetime(2026, 9, 1, 8, 30),
        repo,
        RaisingProvider(),
        gateway,
        candidate_client,
        deps["ohlcv_provider"],
        deps["ohlcv_repository"],
        deps["candidate_fetcher"],
        deps["ohlcv_loader"],
        deps["tags_repository"],
        deps["tagged_candidate_fetcher"], deps["supply_provider"],
        deps["program_supply_provider"], deps["supply_repository"],
    )

    assert result.status == "success"
    assert candidate_client.calls  # candidate stage was reached
    assert repo.saved == []  # UNAVAILABLE 결정은 캐시하지 않는다


def test_replayed_holiday_attempt_ends_without_skip_call():
    repo = FakeRepository(cached={date(2026, 9, 1): TradingCalendarEntry(date(2026, 9, 1), False)})
    rpc = FakeRpc(replayed=True)
    gateway = RunStateGateway(rpc)
    candidate_client = FakeCandidateClient()
    deps = tags_deps()

    result = run_scheduled_batch(
        BatchKind.CLOSE,
        datetime(2026, 9, 1, 16, 0),
        repo,
        FakeProvider(),
        gateway,
        candidate_client,
        deps["ohlcv_provider"],
        deps["ohlcv_repository"],
        deps["candidate_fetcher"],
        deps["ohlcv_loader"],
        deps["tags_repository"],
        deps["tagged_candidate_fetcher"], deps["supply_provider"],
        deps["program_supply_provider"], deps["supply_repository"],
    )

    assert result.status == "success"
    assert result.result_code == "REPLAYED"
    assert [call[0] for call in rpc.calls] == ["start_attempt"]
    assert candidate_client.calls == []


def test_replayed_success_attempt_does_not_run_ohlcv_or_tags_pipeline():
    cached_open = TradingCalendarEntry(date(2026, 9, 1), True, time(9), time(15, 30))
    repo = FakeRepository(cached={date(2026, 9, 1): cached_open})
    rpc = FakeRpc(replayed=True)
    gateway = RunStateGateway(rpc)
    candidate_client = FakeCandidateClient(LsResponse(data=[]))
    deps = tags_deps()

    result = run_scheduled_batch(
        BatchKind.CLOSE,
        datetime(2026, 9, 1, 16, 0),
        repo,
        FakeProvider(),
        gateway,
        candidate_client,
        deps["ohlcv_provider"],
        deps["ohlcv_repository"],
        deps["candidate_fetcher"],
        deps["ohlcv_loader"],
        deps["tags_repository"],
        deps["tagged_candidate_fetcher"], deps["supply_provider"],
        deps["program_supply_provider"], deps["supply_repository"],
    )

    assert result.status == "success"
    assert result.result_code == "REPLAYED"
    assert candidate_client.calls == []
    assert deps["candidate_fetcher"].calls == []
    assert deps["ohlcv_repository"].existing_tickers_calls == []


def test_intraday_slot_uses_floor_to_half_hour():
    cached_open = TradingCalendarEntry(date(2026, 9, 1), True, time(9), time(15, 30))
    repo = FakeRepository(cached={date(2026, 9, 1): cached_open})
    rpc = FakeRpc(attempt=attempt_payload("intraday:2026-09-01:09:00"))
    gateway = RunStateGateway(rpc)
    candidate_client = FakeCandidateClient(LsResponse(data=[]))
    deps = tags_deps()

    run_scheduled_batch(
        BatchKind.INTRADAY,
        datetime(2026, 9, 1, 9, 7),
        repo,
        FakeProvider(),
        gateway,
        candidate_client,
        deps["ohlcv_provider"],
        deps["ohlcv_repository"],
        deps["candidate_fetcher"],
        deps["ohlcv_loader"],
        deps["tags_repository"],
        deps["tagged_candidate_fetcher"], deps["supply_provider"],
        deps["program_supply_provider"], deps["supply_repository"],
    )

    start_params = rpc.calls[0][1]
    assert start_params["p_logical_run_key"] == "intraday:2026-09-01:09:00"


def test_manual_trigger_is_passed_through_to_start_attempt():
    cached_open = TradingCalendarEntry(date(2026, 9, 1), True, time(9), time(15, 30))
    repo = FakeRepository(cached={date(2026, 9, 1): cached_open})
    rpc = FakeRpc(attempt=attempt_payload())
    gateway = RunStateGateway(rpc)
    candidate_client = FakeCandidateClient(LsResponse(data=[]))
    deps = tags_deps()

    result = run_scheduled_batch(
        BatchKind.CLOSE,
        datetime(2026, 9, 1, 16, 0),
        repo,
        FakeProvider(),
        gateway,
        candidate_client,
        deps["ohlcv_provider"],
        deps["ohlcv_repository"],
        deps["candidate_fetcher"],
        deps["ohlcv_loader"],
        deps["tags_repository"],
        deps["tagged_candidate_fetcher"], deps["supply_provider"],
        deps["program_supply_provider"], deps["supply_repository"],
        trigger=Trigger.MANUAL,
    )

    assert result.status == "success"
    start_params = rpc.calls[0][1]
    assert start_params["p_trigger"] == "manual"


def test_dispatch_receipt_recorded_after_open_day_success():
    cached_open = TradingCalendarEntry(date(2026, 9, 1), True, time(9), time(15, 30))
    repo = FakeRepository(cached={date(2026, 9, 1): cached_open})
    attempt = attempt_payload()
    rpc = FakeRpc(attempt=attempt)
    gateway = RunStateGateway(rpc)
    candidate_client = FakeCandidateClient(LsResponse(data=[]))
    deps = tags_deps()

    result = run_scheduled_batch(
        BatchKind.CLOSE,
        datetime(2026, 9, 1, 16, 0),
        repo,
        FakeProvider(),
        gateway,
        candidate_client,
        deps["ohlcv_provider"],
        deps["ohlcv_repository"],
        deps["candidate_fetcher"],
        deps["ohlcv_loader"],
        deps["tags_repository"],
        deps["tagged_candidate_fetcher"], deps["supply_provider"],
        deps["program_supply_provider"], deps["supply_repository"],
        trigger=Trigger.MANUAL,
        dispatch_request_id="dispatch-1",
    )

    assert result.status == "success"
    assert result.run_id == attempt["run_id"]
    receipt_calls = [call for call in rpc.calls if call[0] == "record_dispatch_receipt"]
    assert len(receipt_calls) == 1
    assert receipt_calls[0][1] == {"p_dispatch_request_id": "dispatch-1", "p_run_id": attempt["run_id"]}


def test_dispatch_receipt_recorded_on_holiday_skip():
    repo = FakeRepository(cached={date(2026, 9, 1): TradingCalendarEntry(date(2026, 9, 1), False)})
    attempt = attempt_payload()
    rpc = FakeRpc(attempt=attempt)
    gateway = RunStateGateway(rpc)
    candidate_client = FakeCandidateClient()
    deps = tags_deps()

    result = run_scheduled_batch(
        BatchKind.CLOSE,
        datetime(2026, 9, 1, 8, 30),
        repo,
        FakeProvider(),
        gateway,
        candidate_client,
        deps["ohlcv_provider"],
        deps["ohlcv_repository"],
        deps["candidate_fetcher"],
        deps["ohlcv_loader"],
        deps["tags_repository"],
        deps["tagged_candidate_fetcher"], deps["supply_provider"],
        deps["program_supply_provider"], deps["supply_repository"],
        dispatch_request_id="dispatch-holiday",
    )

    assert result.status == "skipped"
    receipt_calls = [call for call in rpc.calls if call[0] == "record_dispatch_receipt"]
    assert len(receipt_calls) == 1
    assert receipt_calls[0][1]["p_run_id"] == attempt["run_id"]


def test_dispatch_receipt_failure_does_not_fail_the_batch(capsys):
    cached_open = TradingCalendarEntry(date(2026, 9, 1), True, time(9), time(15, 30))
    repo = FakeRepository(cached={date(2026, 9, 1): cached_open})
    rpc = FakeRpc(attempt=attempt_payload(), raise_on={"record_dispatch_receipt"})
    gateway = RunStateGateway(rpc)
    candidate_client = FakeCandidateClient(LsResponse(data=[]))
    deps = tags_deps()

    result = run_scheduled_batch(
        BatchKind.CLOSE,
        datetime(2026, 9, 1, 16, 0),
        repo,
        FakeProvider(),
        gateway,
        candidate_client,
        deps["ohlcv_provider"],
        deps["ohlcv_repository"],
        deps["candidate_fetcher"],
        deps["ohlcv_loader"],
        deps["tags_repository"],
        deps["tagged_candidate_fetcher"], deps["supply_provider"],
        deps["program_supply_provider"], deps["supply_repository"],
        trigger=Trigger.MANUAL,
        dispatch_request_id="dispatch-fail",
    )

    assert result.status == "success"
    assert "DISPATCH_RECEIPT_FAILED" in capsys.readouterr().out


# --- Story 3.5 후속: close 배치 publish_attempt 배선 (deferred-work gap 해소) -------


def _publish_attempt_calls(rpc):
    return [call for call in rpc.calls if call[0] == "publish_attempt"]


def test_close_success_publishes_after_tags_stage():
    """close 배치가 candidates+tags success로 종결되면 publish_attempt를 실제 호출한다."""
    cached_open = TradingCalendarEntry(date(2026, 9, 1), True, time(9), time(15, 30))
    repo = FakeRepository(cached={date(2026, 9, 1): cached_open})
    attempt = attempt_payload()
    rpc = FakeRpc(attempt=attempt)
    gateway = RunStateGateway(rpc)
    candidate_client = FakeCandidateClient(LsResponse(data=[{"ticker": "005930", "trading_value": 1}]))
    deps = tags_deps()

    result = run_scheduled_batch(
        BatchKind.CLOSE,
        datetime(2026, 9, 1, 16, 0),
        repo,
        FakeProvider(),
        gateway,
        candidate_client,
        deps["ohlcv_provider"],
        deps["ohlcv_repository"],
        deps["candidate_fetcher"],
        deps["ohlcv_loader"],
        deps["tags_repository"],
        deps["tagged_candidate_fetcher"], deps["supply_provider"],
        deps["program_supply_provider"], deps["supply_repository"],
    )

    assert result.status == "success"
    assert result.published is True
    assert result.outcome_tracking_status == "success"
    pub_calls = _publish_attempt_calls(rpc)
    assert len(pub_calls) == 1
    assert pub_calls[0][1] == {
        "p_run_id": attempt["run_id"],
        "p_fence_token": attempt["fence_token"],
        "p_lease_token": attempt["lease_token"],
    }


def test_premarket_and_intraday_do_not_publish():
    """publish_attempt는 close 배치에만 배선된다(premarket/intraday 미호출)."""
    cached_open = TradingCalendarEntry(date(2026, 9, 1), True, time(9), time(15, 30))
    repo = FakeRepository(cached={date(2026, 9, 1): cached_open})

    for kind, moment in ((BatchKind.PREMARKET, datetime(2026, 9, 1, 8, 30)),
                         (BatchKind.INTRADAY, datetime(2026, 9, 1, 9, 7))):
        rpc = FakeRpc(attempt=attempt_payload())
        gateway = RunStateGateway(rpc)
        candidate_client = FakeCandidateClient(LsResponse(data=[{"ticker": "005930", "trading_value": 1}]))
        deps = tags_deps()
        result = run_scheduled_batch(
            kind, moment,
            repo, FakeProvider(), gateway, candidate_client,
            deps["ohlcv_provider"], deps["ohlcv_repository"],
            deps["candidate_fetcher"], deps["ohlcv_loader"], deps["tags_repository"],
        deps["tagged_candidate_fetcher"], deps["supply_provider"],
        deps["program_supply_provider"], deps["supply_repository"],
        )
        assert result.status in ("success", "partial")
        assert result.published is False
        assert _publish_attempt_calls(rpc) == []


def test_partial_candidates_stage_does_not_publish():
    """candidates가 partial이면 publish_attempt를 호출하지 않는다(필수 stage success 보장 필요)."""
    cached_open = TradingCalendarEntry(date(2026, 9, 1), True, time(9), time(15, 30))
    repo = FakeRepository(cached={date(2026, 9, 1): cached_open})
    rpc = FakeRpc(attempt=attempt_payload())
    gateway = RunStateGateway(rpc)
    candidate_client = FakeCandidateClient(
        LsResponse(data=[{"ticker": "005930", "trading_value": 1}], unprocessed_count=1)
    )
    deps = tags_deps()

    result = run_scheduled_batch(
        BatchKind.CLOSE,
        datetime(2026, 9, 1, 16, 0),
        repo, FakeProvider(), gateway, candidate_client,
        deps["ohlcv_provider"], deps["ohlcv_repository"],
        deps["candidate_fetcher"], deps["ohlcv_loader"], deps["tags_repository"],
        deps["tagged_candidate_fetcher"], deps["supply_provider"],
        deps["program_supply_provider"], deps["supply_repository"],
    )

    assert result.status == "partial"
    assert result.published is False
    assert _publish_attempt_calls(rpc) == []


def test_tags_failure_does_not_publish():
    """tags stage가 failed면 publish_attempt를 호출하지 않는다."""
    cached_open = TradingCalendarEntry(date(2026, 9, 1), True, time(9), time(15, 30))
    repo = FakeRepository(cached={date(2026, 9, 1): cached_open})
    rpc = FakeRpc(attempt=attempt_payload())
    gateway = RunStateGateway(rpc)
    candidate_client = FakeCandidateClient(LsResponse(data=[{"ticker": "005930", "trading_value": 1}]))

    class RaisingCandidateFetcher:
        def fetch(self, run_id):
            raise RuntimeError("boom")

    deps = tags_deps()
    deps["candidate_fetcher"] = RaisingCandidateFetcher()

    result = run_scheduled_batch(
        BatchKind.CLOSE,
        datetime(2026, 9, 1, 16, 0),
        repo, FakeProvider(), gateway, candidate_client,
        deps["ohlcv_provider"], deps["ohlcv_repository"],
        deps["candidate_fetcher"], deps["ohlcv_loader"], deps["tags_repository"],
        deps["tagged_candidate_fetcher"], deps["supply_provider"],
        deps["program_supply_provider"], deps["supply_repository"],
    )

    assert result.status == "failed"
    assert result.published is False
    assert _publish_attempt_calls(rpc) == []


def test_publish_failure_marks_outcome_tracking_failed_and_fails_batch():
    """publish_attempt가 실패하면 outcome_tracking stage를 failed로 기록하고 배치를 failed로 보고한다."""
    cached_open = TradingCalendarEntry(date(2026, 9, 1), True, time(9), time(15, 30))
    repo = FakeRepository(cached={date(2026, 9, 1): cached_open})
    attempt = attempt_payload()
    rpc = FakeRpc(attempt=attempt, raise_on={"publish_attempt"})
    gateway = RunStateGateway(rpc)
    candidate_client = FakeCandidateClient(LsResponse(data=[{"ticker": "005930", "trading_value": 1}]))
    deps = tags_deps()

    result = run_scheduled_batch(
        BatchKind.CLOSE,
        datetime(2026, 9, 1, 16, 0),
        repo, FakeProvider(), gateway, candidate_client,
        deps["ohlcv_provider"], deps["ohlcv_repository"],
        deps["candidate_fetcher"], deps["ohlcv_loader"], deps["tags_repository"],
        deps["tagged_candidate_fetcher"], deps["supply_provider"],
        deps["program_supply_provider"], deps["supply_repository"],
    )

    assert result.status == "failed"
    assert result.result_code == "OUTCOME_PUBLISH_FAILED"
    assert result.published is False
    assert result.outcome_tracking_status == "failed"
    write_stage_calls = [call for call in rpc.calls if call[0] == "write_stage"]
    outcome_calls = [call for call in write_stage_calls if call[1]["p_stage"] == "outcome_tracking"]
    # 성공 시 outcome_tracking success는 publish_attempt 내부(DB 트랜잭션)가 기록하므로,
    # 오케스트레이터는 실패 시에만 failed로 기록한다(running 기록 없음).
    assert [call[1]["p_status"] for call in outcome_calls] == ["failed"]
