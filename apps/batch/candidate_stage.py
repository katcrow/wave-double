"""t1859 후보 모집단 stage 오케스트레이터."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from typing import Any, Protocol
from uuid import UUID, uuid4

from domain.candidate_selection import CandidateSelection, select_candidates
from domain.run_state import LogicalRunKey, Stage, StageStatus, Trigger

from .ls_client import LsResponse
from .run_state import Attempt, RunStateGateway, RunStateError


class CandidateClient(Protocol):
    def request(self, tr_code: str, params: dict[str, Any]) -> LsResponse: ...


@dataclass(frozen=True)
class CandidateStageResult:
    status: str
    result_code: str
    candidate_count: int
    selection: CandidateSelection | None = None


def _attempt(value: Any) -> Attempt:
    if isinstance(value, list):
        value = value[0] if value else {}
    if hasattr(value, "data"):
        value = value.data
    if not isinstance(value, dict):
        raise RunStateError("INVALID_ATTEMPT", "start_attempt returned invalid data")
    try:
        return Attempt(UUID(str(value["run_id"])), str(value["logical_run_key"]), int(value["attempt_no"]), int(value["fence_token"]), UUID(str(value["lease_token"])), value["lease_expires_at"])
    except (KeyError, TypeError, ValueError) as exc:
        raise RunStateError("INVALID_ATTEMPT", "start_attempt returned incomplete data") from exc


def _response_records(response: LsResponse) -> Any:
    data = response.data
    if isinstance(data, dict):
        for key in ("t1859OutBlock1", "candidates", "results", "items", "data"):
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
    lease_seconds: int = 300,
) -> CandidateStageResult:
    """한 attempt의 candidates stage를 성공/실패로 종결한다."""
    started = gateway.start_attempt(key, trigger, lease_seconds=lease_seconds)
    if isinstance(started, dict) and started.get("replayed"):
        return CandidateStageResult("success", "REPLAYED", 0)
    attempt = _attempt(started)
    gateway.write_stage(attempt.run_id, Stage.CANDIDATES, attempt.fence_token, attempt.lease_token, StageStatus.PENDING, StageStatus.RUNNING)
    request_params = params if params is not None else {"t1859InBlock": {"query_index": query_index or ""}}
    try:
        response = ls_client.request("t1859", request_params)
    except Exception as exc:
        gateway.write_stage(attempt.run_id, Stage.CANDIDATES, attempt.fence_token, attempt.lease_token, StageStatus.RUNNING, StageStatus.FAILED, result={"result_code": "LS_REQUEST_ERROR", "message": str(exc)})
        return CandidateStageResult("failed", "LS_REQUEST_ERROR", 0)
    if not response.ok:
        result = {"result_code": response.result_code, "message": response.message}
        gateway.write_stage(attempt.run_id, Stage.CANDIDATES, attempt.fence_token, attempt.lease_token, StageStatus.RUNNING, StageStatus.FAILED, result=result, unprocessed_count=response.unprocessed_count)
        return CandidateStageResult("failed", response.result_code, 0)
    if response.unprocessed_count > 0:
        gateway.write_stage(attempt.run_id, Stage.CANDIDATES, attempt.fence_token, attempt.lease_token, StageStatus.RUNNING, StageStatus.PARTIAL, result={"result_code": "UNPROCESSED_ITEMS", "unprocessed_count": response.unprocessed_count}, unprocessed_count=response.unprocessed_count)
        return CandidateStageResult("partial", "UNPROCESSED_ITEMS", 0)
    try:
        selection = select_candidates(_response_records(response))
    except Exception as exc:
        gateway.write_stage(attempt.run_id, Stage.CANDIDATES, attempt.fence_token, attempt.lease_token, StageStatus.RUNNING, StageStatus.FAILED, result={"result_code": "INVALID_RESPONSE", "message": str(exc)})
        return CandidateStageResult("failed", "INVALID_RESPONSE", 0)
    rows = [
        {"candidate_id": str(uuid4()), **candidate.as_dict(), "truncated": truncated}
        for truncated, candidates in ((False, selection.candidates), (True, selection.truncated_candidates))
        for candidate in candidates
    ]
    gateway.write_candidates(attempt.run_id, attempt.fence_token, attempt.lease_token, rows, selection.metadata)
    result = {"result_code": response.result_code, **selection.metadata}
    gateway.write_stage(attempt.run_id, Stage.CANDIDATES, attempt.fence_token, attempt.lease_token, StageStatus.RUNNING, StageStatus.SUCCESS, result=result, unprocessed_count=response.unprocessed_count)
    return CandidateStageResult("success", response.result_code, len(selection.candidates), selection)


__all__ = ["CandidateStageResult", "run_candidate_stage"]
