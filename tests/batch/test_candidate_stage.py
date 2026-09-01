from datetime import date, datetime, timezone
from uuid import uuid4

from apps.batch.candidate_stage import run_candidate_stage
from apps.batch.ls_client import LsResponse
from apps.batch.run_state import RunStateGateway
from domain.run_state import BatchKind, LogicalRunKey, Trigger


class FakeRpc:
    def __init__(self, attempt):
        self.calls = []
        self.attempt = attempt

    def rpc(self, function, params):
        self.calls.append((function, params))
        return self.attempt if function == "start_attempt" else {"ok": True}


class FakeLs:
    def __init__(self, response):
        self.response = response
        self.params = None

    def request(self, tr_code, params):
        assert tr_code == "t1859"
        self.params = params
        return self.response


def attempt_payload():
    return {"run_id": str(uuid4()), "logical_run_key": "close:2026-09-01", "attempt_no": 1, "fence_token": 1, "lease_token": str(uuid4()), "lease_expires_at": datetime.now(timezone.utc).isoformat()}


def test_success_writes_candidates_and_completes_stage():
    rpc = FakeRpc(attempt_payload())
    result = run_candidate_stage(RunStateGateway(rpc), FakeLs(LsResponse(data=[{"ticker": "005", "trading_value": 2}, {"ticker": "001", "trading_value": 2}])), LogicalRunKey(date(2026, 9, 1), BatchKind.CLOSE), Trigger.MANUAL)
    assert result.status == "success" and result.candidate_count == 2
    assert [call[0] for call in rpc.calls] == ["start_attempt", "write_stage", "write_candidates", "write_stage"]
    assert rpc.calls[-1][1]["p_status"] == "success"
    assert all(row["truncated"] is False for row in rpc.calls[2][1]["p_candidates"])


def test_empty_success_is_not_failed():
    rpc = FakeRpc(attempt_payload())
    result = run_candidate_stage(RunStateGateway(rpc), FakeLs(LsResponse(data=[])), LogicalRunKey(date(2026, 9, 1), BatchKind.CLOSE), Trigger.SCHEDULE)
    assert result.status == "success" and result.candidate_count == 0
    assert rpc.calls[-1][1]["p_status"] == "success"


def test_call_failure_records_structured_failed_stage():
    rpc = FakeRpc(attempt_payload())
    result = run_candidate_stage(RunStateGateway(rpc), FakeLs(LsResponse(result_code="HTTP_ERROR", message="unavailable", unprocessed_count=2)), LogicalRunKey(date(2026, 9, 1), BatchKind.CLOSE), Trigger.MANUAL)
    assert result.status == "failed" and result.result_code == "HTTP_ERROR"
    assert rpc.calls[-1][1]["p_status"] == "failed"
    assert rpc.calls[-1][1]["p_result"]["result_code"] == "HTTP_ERROR"


def test_truncated_candidates_are_written_with_marker():
    rpc = FakeRpc(attempt_payload())
    records = [{"ticker": f"{i:03d}", "trading_value": i} for i in range(151)]
    result = run_candidate_stage(RunStateGateway(rpc), FakeLs(LsResponse(data=records)), LogicalRunKey(date(2026, 9, 1), BatchKind.CLOSE), Trigger.SCHEDULE)
    rows = rpc.calls[2][1]["p_candidates"]
    assert result.candidate_count == 150
    assert len(rows) == 150
    assert all(row["truncated"] is False for row in rows)
    assert rpc.calls[2][1]["p_metadata"]["truncated_count"] == 1


def test_parses_t1859_response_and_sends_query_index():
    rpc = FakeRpc(attempt_payload())
    response = LsResponse(data={"t1859OutBlock1": [{"shcode": "000001", "hname": "A", "price": 100, "volume": 5}]})
    ls = FakeLs(response)
    run_candidate_stage(RunStateGateway(rpc), ls, LogicalRunKey(date(2026, 9, 1), BatchKind.CLOSE), Trigger.SCHEDULE, query_index="neo0001")
    assert rpc.calls[0][1]["p_batch_kind"] == "close"
    assert ls.params == {"t1859InBlock": {"query_index": "neo0001"}}
