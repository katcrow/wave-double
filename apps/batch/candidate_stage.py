"""t1859 후보 모집단 stage 오케스트레이터."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from typing import Any, Protocol
from uuid import uuid4

from domain.candidate_selection import CandidateSelection, merge_candidate_sources
from domain.run_state import LogicalRunKey, Stage, StageStatus, Trigger

from .ls_client import LsResponse
from .run_state import RunStateGateway, parse_attempt, safe_record_dispatch_receipt

PRIMARY_TR = "t1859"
FALLBACK_TR = "t1856"


class CandidateClient(Protocol):
    def request(self, tr_code: str, params: dict[str, Any]) -> LsResponse: ...


@dataclass(frozen=True)
class CandidateStageResult:
    status: str
    result_code: str
    candidate_count: int
    selection: CandidateSelection | None = None
    fallback_used: bool = False
    run_id: str | None = None
    fence_token: int | None = None
    lease_token: str | None = None


def _response_records(response: LsResponse) -> Any:
    data = response.data
    if isinstance(data, dict):
        for key in ("t1859OutBlock1", "t1856OutBlock1", "candidates", "results", "items", "data"):
            if key in data:
                return data[key]
    return data


def run_candidate_stage(
    gateway: RunStateGateway,
    ls_client: CandidateClient,
    key: LogicalRunKey,
    trigger: Trigger,
    params: dict[str, Any] | None = None,
    *,
    query_index: str | None = None,
    fallback_params: dict[str, Any] | None = None,
    lease_seconds: int = 300,
    dispatch_request_id: str | None = None,
) -> CandidateStageResult:
    """한 attempt의 candidates stage를 성공/실패로 종결한다.

    t1859가 예외를 던지거나 ``response.ok`` 가 False면 t1856 경로로 자동 재시도한다.
    폴백 호출 자체가 성공했을 때만 ``runs.fallback_used`` 를 true로 기록하며, 두 경로가
    모두 실패하면 두 result_code를 모두 남기고 stage는 조용히 성공 처리되지 않는다.

    ``dispatch_request_id``가 주어지면(수동 트리거) run_id가 확정되는 즉시(재생 포함)
    ``record_dispatch_receipt``를 호출해 outbox를 ``started``로 전이시킨다(AD-18 "workflow
    첫 단계"). 영수증 기록 실패는 배치 결과에 영향을 주지 않는다.
    """
    started = gateway.start_attempt(key, trigger, lease_seconds=lease_seconds)
    if isinstance(started, dict) and started.get("replayed"):
        replayed_run_id = started.get("run_id")
        safe_record_dispatch_receipt(gateway, dispatch_request_id, replayed_run_id)
        return CandidateStageResult(
            "success", "REPLAYED", 0, run_id=str(replayed_run_id) if replayed_run_id is not None else None
        )
    attempt = parse_attempt(started)
    safe_record_dispatch_receipt(gateway, dispatch_request_id, attempt.run_id)
    gateway.write_stage(attempt.run_id, Stage.CANDIDATES, attempt.fence_token, attempt.lease_token, StageStatus.PENDING, StageStatus.RUNNING)
    request_params = params if params is not None else {"t1859InBlock": {"query_index": query_index or ""}}

    primary_response: LsResponse | None = None
    primary_failure_code: str | None = None
    try:
        primary_response = ls_client.request(PRIMARY_TR, request_params)
    except Exception:
        primary_failure_code = "LS_REQUEST_ERROR"
    else:
        if not primary_response.ok:
            primary_failure_code = primary_response.result_code

    active_source = PRIMARY_TR
    active_response = primary_response if primary_failure_code is None else None
    fallback_used = False

    if active_response is None:
        fallback_request_params = fallback_params if fallback_params is not None else {"t1856InBlock": {}}
        fallback_response: LsResponse | None = None
        fallback_failure_code: str | None = None
        try:
            fallback_response = ls_client.request(FALLBACK_TR, fallback_request_params)
        except Exception:
            fallback_failure_code = "LS_REQUEST_ERROR"
        else:
            if not fallback_response.ok:
                fallback_failure_code = fallback_response.result_code

        if fallback_response is not None and fallback_failure_code is None:
            fallback_used = True
            active_source = FALLBACK_TR
            active_response = fallback_response
        else:
            unprocessed = max(
                primary_response.unprocessed_count if primary_response is not None else 0,
                fallback_response.unprocessed_count if fallback_response is not None else 0,
                1,
            )
            result = {
                "result_code": "CANDIDATE_SOURCES_EXHAUSTED",
                "t1859_result_code": primary_failure_code,
                "t1856_result_code": fallback_failure_code,
            }
            gateway.write_stage(attempt.run_id, Stage.CANDIDATES, attempt.fence_token, attempt.lease_token, StageStatus.RUNNING, StageStatus.FAILED, result=result, unprocessed_count=unprocessed, fallback_used=False)
            return CandidateStageResult("failed", "CANDIDATE_SOURCES_EXHAUSTED", 0, fallback_used=False, run_id=str(attempt.run_id))

    try:
        selection = merge_candidate_sources({active_source: _response_records(active_response)})
    except Exception:
        gateway.write_stage(attempt.run_id, Stage.CANDIDATES, attempt.fence_token, attempt.lease_token, StageStatus.RUNNING, StageStatus.FAILED, result={"result_code": "INVALID_RESPONSE", "message": "LS response could not be normalized"}, fallback_used=fallback_used)
        return CandidateStageResult("failed", "INVALID_RESPONSE", 0, fallback_used=fallback_used, run_id=str(attempt.run_id))
    # 상한 밖 종목은 runs.truncated_count로만 보존한다. candidates에는 상위 150건만 남긴다.
    rows = [
        {"candidate_id": str(uuid4()), **candidate.as_dict(), "truncated": False}
        for candidate in selection.candidates
    ]
    try:
        gateway.write_candidates(attempt.run_id, attempt.fence_token, attempt.lease_token, rows, selection.metadata)
    except Exception:
        gateway.write_stage(attempt.run_id, Stage.CANDIDATES, attempt.fence_token, attempt.lease_token, StageStatus.RUNNING, StageStatus.FAILED, result={"result_code": "CANDIDATE_PERSIST_FAILED", "message": "candidate persistence failed"}, fallback_used=fallback_used)
        return CandidateStageResult("failed", "CANDIDATE_PERSIST_FAILED", 0, fallback_used=fallback_used, run_id=str(attempt.run_id))

    fallback_note = {"t1859_result_code": primary_failure_code} if fallback_used else {}
    if active_response.unprocessed_count > 0:
        result = {"result_code": "UNPROCESSED_ITEMS", **selection.metadata, **fallback_note}
        gateway.write_stage(attempt.run_id, Stage.CANDIDATES, attempt.fence_token, attempt.lease_token, StageStatus.RUNNING, StageStatus.PARTIAL, result=result, unprocessed_count=active_response.unprocessed_count, fallback_used=fallback_used)
        return CandidateStageResult("partial", "UNPROCESSED_ITEMS", len(selection.candidates), selection, fallback_used=fallback_used, run_id=str(attempt.run_id), fence_token=attempt.fence_token, lease_token=str(attempt.lease_token))
    result = {"result_code": active_response.result_code, **selection.metadata, **fallback_note}
    gateway.write_stage(attempt.run_id, Stage.CANDIDATES, attempt.fence_token, attempt.lease_token, StageStatus.RUNNING, StageStatus.SUCCESS, result=result, unprocessed_count=active_response.unprocessed_count, fallback_used=fallback_used)
    return CandidateStageResult("success", active_response.result_code, len(selection.candidates), selection, fallback_used=fallback_used, run_id=str(attempt.run_id), fence_token=attempt.fence_token, lease_token=str(attempt.lease_token))


__all__ = ["CandidateStageResult", "run_candidate_stage"]
