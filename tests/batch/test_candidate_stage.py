from datetime import date, datetime, timezone
from uuid import uuid4

from apps.batch.candidate_stage import run_candidate_stage
from apps.batch.ls_client import LsResponse
from apps.batch.run_state import RunStateGateway
from domain.run_state import BatchKind, LogicalRunKey, Trigger


class FakeRpc:
    def __init__(self, attempt, replayed_run_id=None):
        self.calls = []
        self.attempt = attempt
        self.replayed_run_id = replayed_run_id

    def rpc(self, function, params):
        self.calls.append((function, params))
        if function == "start_attempt":
            if self.replayed_run_id is not None:
                return {
                    "replayed": True,
                    "run_id": self.replayed_run_id,
                    "logical_run_key": params["p_logical_run_key"],
                }
            return self.attempt
        return {"ok": True}


class FakeLs:
    """단일 TR 응답(과거 계약) 또는 tr_code -> LsResponse 매핑을 흉내낸다."""

    def __init__(self, responses):
        self.responses = responses if isinstance(responses, dict) else {"t1859": responses}
        self.calls: list[tuple[str, dict]] = []

    def request(self, tr_code, params):
        self.calls.append((tr_code, params))
        if tr_code not in self.responses:
            raise AssertionError(f"unexpected tr_code call: {tr_code}")
        response = self.responses[tr_code]
        if isinstance(response, Exception):
            raise response
        return response


def attempt_payload():
    return {"run_id": str(uuid4()), "logical_run_key": "close:2026-09-01", "attempt_no": 1, "fence_token": 1, "lease_token": str(uuid4()), "lease_expires_at": datetime.now(timezone.utc).isoformat()}


def test_success_writes_candidates_and_completes_stage():
    rpc = FakeRpc(attempt_payload())
    result = run_candidate_stage(RunStateGateway(rpc), FakeLs(LsResponse(data=[{"ticker": "005", "trading_value": 2}, {"ticker": "001", "trading_value": 2}])), LogicalRunKey(date(2026, 9, 1), BatchKind.CLOSE), Trigger.MANUAL)
    assert result.status == "success" and result.candidate_count == 2
    assert result.fallback_used is False
    assert [call[0] for call in rpc.calls] == ["start_attempt", "write_stage", "write_candidates", "write_stage"]
    assert rpc.calls[-1][1]["p_status"] == "success"
    assert rpc.calls[-1][1]["p_fallback_used"] is False
    assert all(row["truncated"] is False for row in rpc.calls[2][1]["p_candidates"])
    assert all(row["sources"] == [{"source": "t1859", "weight": 1.0}] for row in rpc.calls[2][1]["p_candidates"])


def test_empty_success_is_not_failed():
    rpc = FakeRpc(attempt_payload())
    result = run_candidate_stage(RunStateGateway(rpc), FakeLs(LsResponse(data=[])), LogicalRunKey(date(2026, 9, 1), BatchKind.CLOSE), Trigger.SCHEDULE)
    assert result.status == "success" and result.candidate_count == 0
    assert rpc.calls[-1][1]["p_status"] == "success"


def test_primary_partial_success_does_not_trigger_fallback():
    rpc = FakeRpc(attempt_payload())
    ls = FakeLs({
        "t1859": LsResponse(data=[{"ticker": "005930", "trading_value": 100}], unprocessed_count=1),
        "t1856": LsResponse(data=[{"ticker": "000660", "trading_value": 200}]),
    })
    result = run_candidate_stage(RunStateGateway(rpc), ls, LogicalRunKey(date(2026, 9, 1), BatchKind.CLOSE), Trigger.MANUAL)
    assert result.status == "partial" and result.result_code == "UNPROCESSED_ITEMS"
    assert result.fallback_used is False
    assert [call[0] for call in ls.calls] == ["t1859"]
    assert rpc.calls[-1][1]["p_status"] == "partial"
    assert rpc.calls[-1][1]["p_fallback_used"] is False


def test_both_sources_failing_records_structured_failed_stage():
    rpc = FakeRpc(attempt_payload())
    ls = FakeLs({
        "t1859": LsResponse(result_code="HTTP_ERROR", message="unavailable", unprocessed_count=2),
        "t1856": LsResponse(result_code="HTTP_ERROR", message="unavailable"),
    })
    result = run_candidate_stage(RunStateGateway(rpc), ls, LogicalRunKey(date(2026, 9, 1), BatchKind.CLOSE), Trigger.MANUAL)
    assert result.status == "failed" and result.result_code == "CANDIDATE_SOURCES_EXHAUSTED"
    assert result.fallback_used is False
    assert [call[0] for call in ls.calls] == ["t1859", "t1856"]
    assert rpc.calls[-1][1]["p_status"] == "failed"
    assert rpc.calls[-1][1]["p_result"]["t1859_result_code"] == "HTTP_ERROR"
    assert rpc.calls[-1][1]["p_result"]["t1856_result_code"] == "HTTP_ERROR"
    assert rpc.calls[-1][1]["p_unprocessed_count"] > 0
    assert rpc.calls[-1][1]["p_fallback_used"] is False


def test_both_sources_raising_exceptions_records_failed_stage():
    rpc = FakeRpc(attempt_payload())
    ls = FakeLs({"t1859": RuntimeError("boom"), "t1856": RuntimeError("boom")})
    result = run_candidate_stage(RunStateGateway(rpc), ls, LogicalRunKey(date(2026, 9, 1), BatchKind.CLOSE), Trigger.MANUAL)
    assert result.status == "failed" and result.result_code == "CANDIDATE_SOURCES_EXHAUSTED"
    assert rpc.calls[-1][1]["p_result"]["t1859_result_code"] == "LS_REQUEST_ERROR"
    assert rpc.calls[-1][1]["p_result"]["t1856_result_code"] == "LS_REQUEST_ERROR"
    assert rpc.calls[-1][1]["p_unprocessed_count"] >= 1


def test_fallback_success_after_primary_exception_records_fallback_used():
    rpc = FakeRpc(attempt_payload())
    ls = FakeLs({
        "t1859": RuntimeError("session unavailable"),
        "t1856": LsResponse(data={"t1856OutBlock1": [{"shcode": "000001", "hname": "A", "price": 100, "volume": 5}]}),
    })
    result = run_candidate_stage(RunStateGateway(rpc), ls, LogicalRunKey(date(2026, 9, 1), BatchKind.CLOSE), Trigger.SCHEDULE)
    assert result.status == "success" and result.candidate_count == 1
    assert result.fallback_used is True
    assert [call[0] for call in ls.calls] == ["t1859", "t1856"]
    assert rpc.calls[-1][1]["p_fallback_used"] is True
    assert rpc.calls[-1][1]["p_result"]["t1859_result_code"] == "LS_REQUEST_ERROR"
    rows = rpc.calls[2][1]["p_candidates"]
    assert rows[0]["sources"] == [{"source": "t1856", "weight": 1.0}]


def test_fallback_success_after_primary_response_not_ok():
    rpc = FakeRpc(attempt_payload())
    ls = FakeLs({
        "t1859": LsResponse(result_code="COND_SESSION_ERROR", message="condition session closed"),
        "t1856": LsResponse(data={"t1856OutBlock1": [{"shcode": "000001", "hname": "A", "price": 100, "volume": 5}]}, unprocessed_count=1),
    })
    result = run_candidate_stage(RunStateGateway(rpc), ls, LogicalRunKey(date(2026, 9, 1), BatchKind.CLOSE), Trigger.MANUAL)
    assert result.status == "partial" and result.candidate_count == 1
    assert result.fallback_used is True
    assert rpc.calls[-1][1]["p_status"] == "partial"
    assert rpc.calls[-1][1]["p_fallback_used"] is True


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
    assert ls.calls[0] == ("t1859", {"t1859InBlock": {"query_index": "neo0001"}})


def test_fallback_uses_supplied_fallback_params():
    rpc = FakeRpc(attempt_payload())
    ls = FakeLs({
        "t1859": LsResponse(result_code="COND_SESSION_ERROR", message="closed"),
        "t1856": LsResponse(data={"t1856OutBlock1": []}),
    })
    run_candidate_stage(
        RunStateGateway(rpc),
        ls,
        LogicalRunKey(date(2026, 9, 1), BatchKind.CLOSE),
        Trigger.SCHEDULE,
        fallback_params={"t1856InBlock": {"sFileData": "base64=="}},
    )
    assert ls.calls[1] == ("t1856", {"t1856InBlock": {"sFileData": "base64=="}})


def test_replayed_attempt_records_dispatch_receipt_with_replayed_run_id():
    replayed_run_id = str(uuid4())
    rpc = FakeRpc(attempt_payload(), replayed_run_id=replayed_run_id)
    result = run_candidate_stage(
        RunStateGateway(rpc),
        FakeLs(LsResponse(data=[])),
        LogicalRunKey(date(2026, 9, 1), BatchKind.CLOSE),
        Trigger.MANUAL,
        dispatch_request_id="dispatch-replay",
    )
    assert result.status == "success" and result.result_code == "REPLAYED"
    assert result.run_id == replayed_run_id
    assert [call[0] for call in rpc.calls] == ["start_attempt", "record_dispatch_receipt"]
    assert rpc.calls[1][1] == {"p_dispatch_request_id": "dispatch-replay", "p_run_id": replayed_run_id}


def test_replayed_attempt_without_dispatch_request_id_skips_receipt():
    replayed_run_id = str(uuid4())
    rpc = FakeRpc(attempt_payload(), replayed_run_id=replayed_run_id)
    result = run_candidate_stage(
        RunStateGateway(rpc),
        FakeLs(LsResponse(data=[])),
        LogicalRunKey(date(2026, 9, 1), BatchKind.CLOSE),
        Trigger.SCHEDULE,
    )
    assert result.status == "success" and result.result_code == "REPLAYED"
    assert [call[0] for call in rpc.calls] == ["start_attempt"]


def test_success_path_records_dispatch_receipt_with_run_id():
    attempt = attempt_payload()
    rpc = FakeRpc(attempt)
    result = run_candidate_stage(
        RunStateGateway(rpc),
        FakeLs(LsResponse(data=[{"ticker": "005930", "trading_value": 1}])),
        LogicalRunKey(date(2026, 9, 1), BatchKind.CLOSE),
        Trigger.MANUAL,
        dispatch_request_id="dispatch-success",
    )
    assert result.status == "success"
    assert result.run_id == attempt["run_id"]
    assert rpc.calls[1][0] == "record_dispatch_receipt"
    assert rpc.calls[1][1] == {"p_dispatch_request_id": "dispatch-success", "p_run_id": attempt["run_id"]}
