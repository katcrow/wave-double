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


class FakeConditionLs:
    """t1866 목록 응답과 query_index별 t1859 응답을 흉내낸다.

    ``conditions``는 query_index -> LsResponse(또는 예외) 매핑이며, t1859 호출 시
    파라미터의 query_index로 조회한다. ``list_response``/``fallback_response``가
    Exception이면 그 자리에서 예외를 던진다.
    """

    def __init__(self, conditions, *, list_response=None, fallback_response=None):
        self.conditions = conditions
        self.list_response = list_response
        self.fallback_response = fallback_response
        self.calls: list[tuple[str, dict]] = []

    def request(self, tr_code, params):
        self.calls.append((tr_code, params))
        if tr_code == "t1866":
            response = self.list_response
        elif tr_code == "t1859":
            query_index = params["t1859InBlock"]["query_index"]
            if query_index not in self.conditions:
                raise AssertionError(f"unexpected query_index: {query_index}")
            response = self.conditions[query_index]
        elif tr_code == "t1856":
            response = self.fallback_response
        else:
            raise AssertionError(f"unexpected tr_code call: {tr_code}")
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


# --- 조건 묶음(t1866 → 조건별 t1859) 경로 ------------------------------------


CONDITIONS_2 = LsResponse(data={"t1866OutBlock": {"result_count": 2}, "t1866OutBlock1": [
    {"query_index": "neo0001", "group_name": "전략", "query_name": "A"},
    {"query_index": "neo0002", "group_name": "전략", "query_name": "B"},
]})


def _record(shcode, price, volume):
    return {"shcode": shcode, "hname": "종목", "price": price, "volume": volume, "sign": "2", "change": 0, "diff": "0.00"}


def test_condition_mode_fetches_list_and_runs_each_condition_serially():
    rpc = FakeRpc(attempt_payload())
    ls = FakeConditionLs(
        conditions={
            "neo0001": LsResponse(data={"t1859OutBlock1": [_record("005930", 100, 5)]}),
            "neo0002": LsResponse(data={"t1859OutBlock1": [_record("000660", 200, 5)]}),
        },
        list_response=CONDITIONS_2,
    )
    result = run_candidate_stage(
        RunStateGateway(rpc), ls, LogicalRunKey(date(2026, 9, 1), BatchKind.CLOSE), Trigger.SCHEDULE,
        condition_search_user_id="katcrow",
    )
    assert result.status == "success" and result.candidate_count == 2
    assert result.fallback_used is False
    assert [call[0] for call in ls.calls] == ["t1866", "t1859", "t1859"]
    assert ls.calls[0] == ("t1866", {"t1866InBlock": {"user_id": "katcrow", "gb": "0", "group_name": "", "cont": "", "cont_key": ""}})
    assert ls.calls[1] == ("t1859", {"t1859InBlock": {"query_index": "neo0001"}})
    assert ls.calls[2] == ("t1859", {"t1859InBlock": {"query_index": "neo0002"}})
    p_result = rpc.calls[-1][1]["p_result"]
    assert rpc.calls[-1][1]["p_status"] == "success"
    assert p_result["condition_count"] == 2
    assert p_result["condition_succeeded"] == 2
    assert p_result["condition_failed"] == 0
    assert rpc.calls[-1][1]["p_unprocessed_count"] == 0
    rows = rpc.calls[2][1]["p_candidates"]
    assert all(row["sources"] == [{"source": "t1859", "weight": 1.0}] for row in rows)


def test_condition_mode_partial_failure_records_failed_conditions_without_fallback():
    rpc = FakeRpc(attempt_payload())
    ls = FakeConditionLs(
        conditions={
            "neo0001": LsResponse(data={"t1859OutBlock1": [_record("005930", 100, 5)]}),
            "neo0002": LsResponse(result_code="HTTP_ERROR", message="down"),
            "neo0003": RuntimeError("boom"),
        },
        list_response=LsResponse(data={"t1866OutBlock1": [
            {"query_index": "neo0001"},
            {"query_index": "neo0002"},
            {"query_index": "neo0003"},
        ]}),
    )
    result = run_candidate_stage(
        RunStateGateway(rpc), ls, LogicalRunKey(date(2026, 9, 1), BatchKind.CLOSE), Trigger.MANUAL,
        condition_search_user_id="katcrow",
    )
    assert result.status == "partial" and result.result_code == "PARTIAL_CONDITION_FAILURE"
    assert result.candidate_count == 1
    assert result.fallback_used is False
    # t1856 폴백은 조건 일부 실패만으로는 호출되지 않는다.
    assert [call[0] for call in ls.calls] == ["t1866", "t1859", "t1859", "t1859"]
    assert rpc.calls[-1][1]["p_status"] == "partial"
    assert rpc.calls[-1][1]["p_fallback_used"] is False
    p_result = rpc.calls[-1][1]["p_result"]
    assert p_result["condition_count"] == 3
    assert p_result["condition_succeeded"] == 1
    assert p_result["condition_failed"] == 2
    assert p_result["result_code"] == "PARTIAL_CONDITION_FAILURE"
    assert p_result["failed_conditions"] == [
        {"query_index": "neo0002", "result_code": "HTTP_ERROR"},
        {"query_index": "neo0003", "result_code": "LS_REQUEST_ERROR"},
    ]
    rows = rpc.calls[2][1]["p_candidates"]
    assert len(rows) == 1
    assert rows[0]["ticker"] == "005930"


def test_condition_mode_all_failed_triggers_t1856_fallback_success():
    rpc = FakeRpc(attempt_payload())
    ls = FakeConditionLs(
        conditions={
            "neo0001": LsResponse(result_code="COND_SESSION_ERROR", message="closed"),
            "neo0002": RuntimeError("boom"),
        },
        list_response=CONDITIONS_2,
        fallback_response=LsResponse(data={"t1856OutBlock1": [_record("000001", 100, 5)]}),
    )
    result = run_candidate_stage(
        RunStateGateway(rpc), ls, LogicalRunKey(date(2026, 9, 1), BatchKind.CLOSE), Trigger.SCHEDULE,
        condition_search_user_id="katcrow",
    )
    assert result.status == "success" and result.candidate_count == 1
    assert result.fallback_used is True
    assert [call[0] for call in ls.calls] == ["t1866", "t1859", "t1859", "t1856"]
    assert rpc.calls[-1][1]["p_status"] == "success"
    assert rpc.calls[-1][1]["p_fallback_used"] is True
    p_result = rpc.calls[-1][1]["p_result"]
    assert p_result["t1859_result_code"] == "COND_SESSION_ERROR,LS_REQUEST_ERROR"
    assert p_result["condition_count"] == 2
    assert p_result["condition_succeeded"] == 0
    assert p_result["condition_failed"] == 2
    assert p_result["failed_conditions"] == [
        {"query_index": "neo0001", "result_code": "COND_SESSION_ERROR"},
        {"query_index": "neo0002", "result_code": "LS_REQUEST_ERROR"},
    ]
    rows = rpc.calls[2][1]["p_candidates"]
    assert rows[0]["ticker"] == "000001"
    assert rows[0]["sources"] == [{"source": "t1856", "weight": 1.0}]


def test_condition_mode_all_failed_and_fallback_fails_records_exhausted():
    rpc = FakeRpc(attempt_payload())
    ls = FakeConditionLs(
        conditions={
            "neo0001": LsResponse(result_code="COND_SESSION_ERROR", message="closed"),
            "neo0002": LsResponse(result_code="HTTP_ERROR", message="down"),
        },
        list_response=CONDITIONS_2,
        fallback_response=LsResponse(result_code="HTTP_ERROR", message="down"),
    )
    result = run_candidate_stage(
        RunStateGateway(rpc), ls, LogicalRunKey(date(2026, 9, 1), BatchKind.CLOSE), Trigger.MANUAL,
        condition_search_user_id="katcrow",
    )
    assert result.status == "failed" and result.result_code == "CANDIDATE_SOURCES_EXHAUSTED"
    assert result.fallback_used is False
    assert [call[0] for call in ls.calls] == ["t1866", "t1859", "t1859", "t1856"]
    p_result = rpc.calls[-1][1]["p_result"]
    assert rpc.calls[-1][1]["p_status"] == "failed"
    assert p_result["t1859_result_code"] == "COND_SESSION_ERROR,HTTP_ERROR"
    assert p_result["t1856_result_code"] == "HTTP_ERROR"
    assert p_result["failed_conditions"] == [
        {"query_index": "neo0001", "result_code": "COND_SESSION_ERROR"},
        {"query_index": "neo0002", "result_code": "HTTP_ERROR"},
    ]
    assert rpc.calls[-1][1]["p_unprocessed_count"] > 0


def test_condition_mode_empty_condition_list_records_condition_list_empty():
    rpc = FakeRpc(attempt_payload())
    ls = FakeConditionLs({}, list_response=LsResponse(data={"t1866OutBlock1": [], "t1866OutBlock": {"result_count": 0}}))
    result = run_candidate_stage(
        RunStateGateway(rpc), ls, LogicalRunKey(date(2026, 9, 1), BatchKind.CLOSE), Trigger.SCHEDULE,
        condition_search_user_id="katcrow",
    )
    assert result.status == "failed" and result.result_code == "CONDITION_LIST_EMPTY"
    assert [call[0] for call in ls.calls] == ["t1866"]
    assert rpc.calls[-1][1]["p_status"] == "failed"
    assert rpc.calls[-1][1]["p_result"]["condition_count"] == 0


def test_condition_mode_t1866_exception_records_condition_list_unavailable():
    rpc = FakeRpc(attempt_payload())
    ls = FakeConditionLs({}, list_response=RuntimeError("list unavailable"))
    result = run_candidate_stage(
        RunStateGateway(rpc), ls, LogicalRunKey(date(2026, 9, 1), BatchKind.CLOSE), Trigger.SCHEDULE,
        condition_search_user_id="katcrow",
    )
    assert result.status == "failed" and result.result_code == "CONDITION_LIST_UNAVAILABLE"
    assert [call[0] for call in ls.calls] == ["t1866"]
    assert rpc.calls[-1][1]["p_status"] == "failed"


def test_condition_mode_t1866_http_error_records_condition_list_unavailable():
    rpc = FakeRpc(attempt_payload())
    ls = FakeConditionLs({}, list_response=LsResponse(result_code="HTTP_ERROR", message="unavailable"))
    result = run_candidate_stage(
        RunStateGateway(rpc), ls, LogicalRunKey(date(2026, 9, 1), BatchKind.CLOSE), Trigger.SCHEDULE,
        condition_search_user_id="katcrow",
    )
    assert result.status == "failed" and result.result_code == "CONDITION_LIST_UNAVAILABLE"
    assert [call[0] for call in ls.calls] == ["t1866"]
    assert rpc.calls[-1][1]["p_result"]["result_code"] == "CONDITION_LIST_UNAVAILABLE"
    assert rpc.calls[-1][1]["p_result"]["t1866_result_code"] == "HTTP_ERROR"


def test_condition_mode_empty_t1866_response_records_condition_list_unavailable():
    rpc = FakeRpc(attempt_payload())
    ls = FakeConditionLs({}, list_response=LsResponse(data={"rsp_cd": "", "rsp_msg": ""}))
    result = run_candidate_stage(
        RunStateGateway(rpc), ls, LogicalRunKey(date(2026, 9, 1), BatchKind.CLOSE), Trigger.SCHEDULE,
        condition_search_user_id="katcrow",
    )
    assert result.status == "failed" and result.result_code == "CONDITION_LIST_UNAVAILABLE"
    # 빈 query_index로 t1859를 날리지 않는다.
    assert [call[0] for call in ls.calls] == ["t1866"]


def test_condition_mode_dedupes_same_ticker_across_conditions_by_max_value():
    rpc = FakeRpc(attempt_payload())
    ls = FakeConditionLs(
        conditions={
            "neo0001": LsResponse(data={"t1859OutBlock1": [_record("005930", 100, 100)]}),
            "neo0002": LsResponse(data={"t1859OutBlock1": [_record("005930", 500, 100)]}),
        },
        list_response=CONDITIONS_2,
    )
    result = run_candidate_stage(
        RunStateGateway(rpc), ls, LogicalRunKey(date(2026, 9, 1), BatchKind.CLOSE), Trigger.SCHEDULE,
        condition_search_user_id="katcrow",
    )
    assert result.status == "success" and result.candidate_count == 1
    rows = rpc.calls[2][1]["p_candidates"]
    assert rows[0]["ticker"] == "005930"
    assert rows[0]["trading_value"] == 50000.0
    assert rows[0]["sources"] == [{"source": "t1859", "weight": 1.0}]
    assert rpc.calls[2][1]["p_metadata"]["excluded_count"] == 1


def test_condition_mode_truncates_merged_pool_to_150():
    rpc = FakeRpc(attempt_payload())
    cond1 = [{"ticker": f"t{i:04d}", "trading_value": 1000 + i} for i in range(100)]
    cond2 = [{"ticker": f"u{i:04d}", "trading_value": 500 + i} for i in range(100)]
    ls = FakeConditionLs(
        conditions={
            "neo0001": LsResponse(data=cond1),
            "neo0002": LsResponse(data=cond2),
        },
        list_response=CONDITIONS_2,
    )
    result = run_candidate_stage(
        RunStateGateway(rpc), ls, LogicalRunKey(date(2026, 9, 1), BatchKind.CLOSE), Trigger.SCHEDULE,
        condition_search_user_id="katcrow",
    )
    assert result.status == "success" and result.candidate_count == 150
    rows = rpc.calls[2][1]["p_candidates"]
    assert len(rows) == 150
    assert all(row["truncated"] is False for row in rows)
    assert rpc.calls[2][1]["p_metadata"]["truncated_count"] == 50
    assert rpc.calls[2][1]["p_metadata"]["original_count"] == 200
