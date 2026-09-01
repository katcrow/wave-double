from datetime import date
from uuid import uuid4

import pytest

from apps.batch.run_state import RunStateError, RunStateGateway
from domain.run_state import BatchKind, LogicalRunKey, StageStatus, Trigger


class FakeRpc:
    def __init__(self):
        self.calls = []

    def rpc(self, function, params):
        self.calls.append((function, params))
        return {"ok": True}


class ErrorResponse:
    error = {"code": "STALE_FENCE_OR_LEASE", "message": "lease expired", "retryable": False}


class ErrorRpc:
    def rpc(self, function, params):
        return ErrorResponse()


class ObjectError:
    code = "RATE_LIMIT_EXHAUSTED"
    message = "try later"
    retryable = True


class ObjectErrorResponse:
    error = ObjectError()


class ObjectErrorRpc:
    def rpc(self, function, params):
        return ObjectErrorResponse()


class DictErrorRpc:
    def rpc(self, function, params):
        return {"error": {"code": "EXPECTED_STATUS_MISMATCH", "message": "stale expected status", "retryable": False}}


def test_gateway_passes_logical_key_and_trigger_to_start_rpc():
    client = FakeRpc()
    gateway = RunStateGateway(client)
    gateway.start_attempt(LogicalRunKey(date(2026, 9, 1), BatchKind.CLOSE), Trigger.MANUAL)
    assert client.calls[0] == ("start_attempt", {
        "p_logical_run_key": "close:2026-09-01",
        "p_trading_day": "2026-09-01",
        "p_batch_kind": "close",
        "p_trigger": "manual",
        "p_lease_seconds": 300,
    })


def test_gateway_includes_fence_lease_and_expected_status_in_stage_write():
    client = FakeRpc()
    gateway = RunStateGateway(client)
    run_id, lease = uuid4(), uuid4()
    gateway.write_stage(run_id, "candidates", 4, lease, StageStatus.PENDING, StageStatus.RUNNING)
    params = client.calls[0][1]
    assert params["p_run_id"] == str(run_id)
    assert params["p_fence_token"] == 4
    assert params["p_lease_token"] == str(lease)
    assert params["p_expected_status"] == "pending"


def test_gateway_rejects_negative_unprocessed_count_before_rpc():
    client = FakeRpc()
    with pytest.raises(ValueError, match="non-negative"):
        RunStateGateway(client).write_stage(uuid4(), "candidates", 1, uuid4(), "pending", "running", unprocessed_count=-1)
    assert client.calls == []


def test_gateway_rejects_non_positive_fence_and_non_mapping_result_before_rpc():
    client = FakeRpc()
    gateway = RunStateGateway(client)
    with pytest.raises(ValueError, match="positive"):
        gateway.publish(uuid4(), 0)
    with pytest.raises(TypeError, match="dictionary"):
        gateway.write_stage(uuid4(), "candidates", 1, uuid4(), "pending", "running", result=[])
    assert client.calls == []


def test_gateway_reuses_same_rpc_contract_for_heartbeat_and_publish():
    client = FakeRpc()
    gateway = RunStateGateway(client)
    run_id, lease = uuid4(), uuid4()
    gateway.heartbeat(run_id, 2, lease)
    gateway.publish(run_id, 2)
    assert [call[0] for call in client.calls] == ["heartbeat_attempt", "publish_attempt"]
    assert client.calls[0][1] == {"p_run_id": str(run_id), "p_fence_token": 2, "p_lease_token": str(lease), "p_lease_seconds": 300}
    assert client.calls[1][1] == {"p_run_id": str(run_id), "p_fence_token": 2}


def test_gateway_preserves_structured_fence_and_lease_errors():
    gateway = RunStateGateway(ErrorRpc())
    with pytest.raises(RunStateError, match="lease expired") as raised:
        gateway.publish(uuid4(), 1)
    assert raised.value.code == "STALE_FENCE_OR_LEASE"
    assert raised.value.retryable is False


def test_gateway_preserves_retryable_from_object_error():
    with pytest.raises(RunStateError) as raised:
        RunStateGateway(ObjectErrorRpc()).publish(uuid4(), 1)
    assert raised.value.code == "RATE_LIMIT_EXHAUSTED"
    assert raised.value.retryable is True


def test_gateway_reads_error_from_dict_response():
    with pytest.raises(RunStateError, match="stale expected status") as raised:
        RunStateGateway(DictErrorRpc()).publish(uuid4(), 1)
    assert raised.value.code == "EXPECTED_STATUS_MISMATCH"


def test_gateway_reaper_passes_optional_observation_time():
    client = FakeRpc()
    RunStateGateway(client).reap()
    assert client.calls == [("reap_expired_attempts", {})]


def test_gateway_reaper_sends_observation_time_when_supplied():
    from datetime import datetime, timezone

    client = FakeRpc()
    RunStateGateway(client).reap(now=datetime(2026, 9, 1, tzinfo=timezone.utc))
    assert client.calls == [("reap_expired_attempts", {"p_now": "2026-09-01T00:00:00+00:00"})]
