from uuid import uuid4

import pytest

from apps.batch.heartbeat import HeartbeatExhausted, LeaseHeartbeat
from apps.batch.run_state import RunStateGateway


class FakeRpc:
    def __init__(self):
        self.calls = []

    def rpc(self, function, params):
        self.calls.append((function, params))
        return {"ok": True, "lease_expires_at": "2026-09-01T16:05:00+00:00"}


class FlakyRpc:
    def __init__(self, failures_before_success):
        self.calls = []
        self._remaining_failures = failures_before_success

    def rpc(self, function, params):
        self.calls.append((function, params))
        if self._remaining_failures > 0:
            self._remaining_failures -= 1
            raise RuntimeError("network down")
        return {"ok": True}


class AlwaysFailRpc:
    def rpc(self, function, params):
        raise RuntimeError("network down")


def _make(gateway_rpc, *, interval_seconds=1.0, max_failures=3):
    return LeaseHeartbeat(
        RunStateGateway(gateway_rpc),
        uuid4(), 1, uuid4(),
        interval_seconds=interval_seconds, max_failures=max_failures,
    )


def _advance(seconds):
    state = {"now": 0.0}

    def monotonic():
        return state["now"]

    return state, monotonic


def test_beat_skips_until_interval_elapses():
    rpc = FakeRpc()
    state, monotonic = _advance(0.0)
    hb = _make(rpc, interval_seconds=60.0)
    hb._monotonic = monotonic

    hb.beat()      # first beat issues RPC
    hb.beat()      # within interval: skipped
    state["now"] = 30.0
    hb.beat()      # still within 60s window
    state["now"] = 61.0
    hb.beat()      # past interval: issues second RPC

    calls = [c[0] for c in rpc.calls]
    assert calls == ["heartbeat_attempt", "heartbeat_attempt"]
    assert hb.beat_count == 2
    assert hb.failures == 0


def test_beat_passes_run_fence_lease_tokens_and_lease_seconds():
    rpc = FakeRpc()
    run_id = uuid4()
    lease_token = uuid4()
    hb = LeaseHeartbeat(
        RunStateGateway(rpc), run_id, 7, lease_token,
        lease_seconds=600, interval_seconds=1e-9,
    )
    hb.beat()

    function, params = rpc.calls[0]
    assert function == "heartbeat_attempt"
    assert params["p_run_id"] == str(run_id)
    assert params["p_fence_token"] == 7
    assert params["p_lease_token"] == str(lease_token)
    assert params["p_lease_seconds"] == 600


def test_recovery_after_transient_errors_within_max_failures():
    rpc = FlakyRpc(failures_before_success=2)
    hb = _make(rpc, max_failures=5, interval_seconds=1e-9)
    hb.beat()
    assert hb.failures == 1
    hb.beat()
    assert hb.failures == 2
    hb.beat()   # recovers
    assert hb.failures == 2
    assert hb.beat_count == 1


def test_exhausted_after_consecutive_failures_reaches_max():
    rpc = AlwaysFailRpc()
    hb = _make(rpc, max_failures=3, interval_seconds=1e-9)
    with pytest.raises(HeartbeatExhausted) as exc:
        hb.beat()
        hb.beat()
        hb.beat()
    assert "3" in str(exc.value)
    assert hb.failures == 3


def test_validation_rejects_non_positive_parameters():
    rpc = FakeRpc()
    with pytest.raises(ValueError):
        _make(rpc, interval_seconds=0.0)
    with pytest.raises(ValueError):
        _make(rpc, max_failures=0)
    with pytest.raises(ValueError):
        LeaseHeartbeat(RunStateGateway(rpc), uuid4(), 1, uuid4(), lease_seconds=0)
    with pytest.raises(ValueError):
        LeaseHeartbeat(RunStateGateway(rpc), uuid4(), 1, uuid4(), lease_seconds=-1)
