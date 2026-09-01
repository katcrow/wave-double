from datetime import date, datetime, time, timezone
from uuid import uuid4

from apps.batch.ls_client import LsResponse
from apps.batch.run_state import RunStateGateway
from apps.batch.scheduler import run_scheduled_batch
from domain.calendar import TradingCalendarEntry
from domain.run_state import BatchKind


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
    def __init__(self, cached=None):
        self._cached = cached or {}
        self.saved = []

    def get(self, trading_day):
        return self._cached.get(trading_day)

    def upsert(self, decision):
        self.saved.append(decision)
        if decision.entry is not None:
            self._cached[decision.entry.trading_day] = decision.entry


class FakeRpc:
    def __init__(self, attempt=None, replayed=False):
        self.calls = []
        self.attempt = attempt
        self.replayed = replayed

    def rpc(self, function, params):
        self.calls.append((function, params))
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

    result = run_scheduled_batch(
        BatchKind.CLOSE,
        datetime(2026, 9, 1, 8, 30),
        repo,
        provider,
        gateway,
        candidate_client,
    )

    assert result.status == "skipped"
    assert result.skip_reason == "holiday"
    assert provider.calls == 0
    assert candidate_client.calls == []
    assert [call[0] for call in rpc.calls] == ["start_attempt", "skip_attempt"]
    skip_call = rpc.calls[-1][1]
    assert skip_call["p_skip_reason"] == "holiday"


def test_open_day_delegates_to_candidate_stage_with_schedule_trigger():
    cached_open = TradingCalendarEntry(date(2026, 9, 1), True, time(9), time(15, 30))
    repo = FakeRepository(cached={date(2026, 9, 1): cached_open})
    rpc = FakeRpc(attempt=attempt_payload())
    gateway = RunStateGateway(rpc)
    candidate_client = FakeCandidateClient(LsResponse(data=[{"ticker": "005930", "trading_value": 1}]))

    result = run_scheduled_batch(
        BatchKind.CLOSE,
        datetime(2026, 9, 1, 16, 0),
        repo,
        FakeProvider(),
        gateway,
        candidate_client,
    )

    assert result.status == "success"
    assert result.candidate_count == 1
    start_params = rpc.calls[0][1]
    assert start_params["p_trigger"] == "schedule"
    assert start_params["p_batch_kind"] == "close"


def test_calendar_unavailable_is_treated_as_open_and_proceeds():
    repo = FakeRepository()
    rpc = FakeRpc(attempt=attempt_payload())
    gateway = RunStateGateway(rpc)
    candidate_client = FakeCandidateClient(LsResponse(data=[]))

    result = run_scheduled_batch(
        BatchKind.PREMARKET,
        datetime(2026, 9, 1, 8, 30),
        repo,
        RaisingProvider(),
        gateway,
        candidate_client,
    )

    assert result.status == "success"
    assert candidate_client.calls  # candidate stage was reached
    assert repo.saved == []  # UNAVAILABLE 결정은 캐시하지 않는다


def test_replayed_holiday_attempt_ends_without_skip_call():
    repo = FakeRepository(cached={date(2026, 9, 1): TradingCalendarEntry(date(2026, 9, 1), False)})
    rpc = FakeRpc(replayed=True)
    gateway = RunStateGateway(rpc)
    candidate_client = FakeCandidateClient()

    result = run_scheduled_batch(
        BatchKind.CLOSE,
        datetime(2026, 9, 1, 16, 0),
        repo,
        FakeProvider(),
        gateway,
        candidate_client,
    )

    assert result.status == "success"
    assert result.result_code == "REPLAYED"
    assert [call[0] for call in rpc.calls] == ["start_attempt"]
    assert candidate_client.calls == []


def test_intraday_slot_uses_floor_to_half_hour():
    cached_open = TradingCalendarEntry(date(2026, 9, 1), True, time(9), time(15, 30))
    repo = FakeRepository(cached={date(2026, 9, 1): cached_open})
    rpc = FakeRpc(attempt=attempt_payload("intraday:2026-09-01:09:00"))
    gateway = RunStateGateway(rpc)
    candidate_client = FakeCandidateClient(LsResponse(data=[]))

    run_scheduled_batch(
        BatchKind.INTRADAY,
        datetime(2026, 9, 1, 9, 7),
        repo,
        FakeProvider(),
        gateway,
        candidate_client,
    )

    start_params = rpc.calls[0][1]
    assert start_params["p_logical_run_key"] == "intraday:2026-09-01:09:00"
