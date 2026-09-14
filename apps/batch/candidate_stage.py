"""t1859 후보 모집단 stage 오케스트레이터.

`condition_search_user_id`가 주어지면 매 실행마다 t1866으로 계정의 서버저장검색 조건
목록을 조회해 각 조건을 t1859로 직렬 실행하고, 그 결과를 source ``t1859``로 통합·선별한다
(조건 추가는 설정 변경 없이 자동 반영). `query_index` 단일 파라미터는 기존 테스트·수동
디버그 호출을 위해 남겨두며 ``condition_search_user_id``가 None일 때만 단일 조건 경로로
동작한다(기존 동작 보존).
"""

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
CONDITION_LIST_TR = "t1866"
CONDITION_LIST_UNAVAILABLE = "CONDITION_LIST_UNAVAILABLE"
CONDITION_LIST_EMPTY = "CONDITION_LIST_EMPTY"
PARTIAL_CONDITION_FAILURE = "PARTIAL_CONDITION_FAILURE"


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


def _request_ok_or_code(ls_client: CandidateClient, tr_code: str, params: dict[str, Any]) -> tuple[LsResponse | None, str | None]:
    """LS 호출을 1회 시도해 ``(성공 응답, None)`` 또는 ``(None, 실패 코드)``를 반환한다."""
    try:
        response = ls_client.request(tr_code, params)
    except Exception:
        return None, "LS_REQUEST_ERROR"
    if not response.ok:
        return None, response.result_code
    return response, None


def _condition_query_indexes(response: LsResponse) -> tuple[str, ...] | None:
    """t1866 응답에서 서버저장검색 조건 query_index 목록을 순서대로 추출한다.

    빈 응답(``{"rsp_cd":"","rsp_msg":""}``)이나 파싱 불가 응답이면 None을 반환해 호출부가
    빈 query_index로 t1859를 호출하지 않게 한다. 정상 응답의 빈 목록은 ``()``로 반환한다.
    """
    data = response.data
    if not isinstance(data, dict):
        return None
    if data.get("rsp_cd") == "" and data.get("rsp_msg") == "":
        return None
    blocks = data.get("t1866OutBlock1")
    if not isinstance(blocks, (list, tuple)):
        return None
    indexes: list[str] = []
    for block in blocks:
        if not isinstance(block, dict):
            continue
        query_index = block.get("query_index")
        if query_index is None:
            continue
        value = str(query_index).strip()
        if value:
            indexes.append(value)
    return tuple(indexes)


def _record_failed_stage(
    gateway: RunStateGateway,
    attempt: Any,
    result_code: str,
    *,
    unprocessed_count: int = 1,
    cause_code: str | None = None,
) -> CandidateStageResult:
    result: dict[str, Any] = {"result_code": result_code}
    if cause_code is not None:
        result["t1866_result_code"] = cause_code
    if result_code == CONDITION_LIST_EMPTY:
        result["condition_count"] = 0
    gateway.write_stage(
        attempt.run_id, Stage.CANDIDATES, attempt.fence_token, attempt.lease_token,
        StageStatus.RUNNING, StageStatus.FAILED,
        result=result, unprocessed_count=unprocessed_count, fallback_used=False,
    )
    return CandidateStageResult("failed", result_code, 0, run_id=str(attempt.run_id))


def _complete_stage(
    gateway: RunStateGateway,
    attempt: Any,
    *,
    source: str,
    records: Any,
    fallback_used: bool,
    primary_failure_code: str | None,
    success_result_code: str,
    unprocessed_count: int,
    extra_metadata: dict[str, Any] | None = None,
    force_partial: bool = False,
    partial_result_code: str | None = None,
) -> CandidateStageResult:
    """단일 source 응답을 선별·저장하고 stage를 success/partial로 종결한다.

    ``force_partial=True``면 후보가 저장된 상태에서도 stage를 ``partial``로 종결한다 --
    조건 묶음 경로에서 일부 조건이 실패했을 때 실패 조건은 후보에서 제외되지만 배치
    결과로 알려져야 한다(PARTIAL_CONDITION_FAILURE).
    """
    try:
        selection = merge_candidate_sources({source: records})
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
    extra = extra_metadata if extra_metadata is not None else {}
    if force_partial or unprocessed_count > 0:
        code = partial_result_code if force_partial else "UNPROCESSED_ITEMS"
        result = {"result_code": code, **selection.metadata, **extra, **fallback_note}
        gateway.write_stage(attempt.run_id, Stage.CANDIDATES, attempt.fence_token, attempt.lease_token, StageStatus.RUNNING, StageStatus.PARTIAL, result=result, unprocessed_count=unprocessed_count, fallback_used=fallback_used)
        return CandidateStageResult("partial", code, len(selection.candidates), selection, fallback_used=fallback_used, run_id=str(attempt.run_id), fence_token=attempt.fence_token, lease_token=str(attempt.lease_token))
    result = {"result_code": success_result_code, **selection.metadata, **extra, **fallback_note}
    gateway.write_stage(attempt.run_id, Stage.CANDIDATES, attempt.fence_token, attempt.lease_token, StageStatus.RUNNING, StageStatus.SUCCESS, result=result, unprocessed_count=unprocessed_count, fallback_used=fallback_used)
    return CandidateStageResult("success", success_result_code, len(selection.candidates), selection, fallback_used=fallback_used, run_id=str(attempt.run_id), fence_token=attempt.fence_token, lease_token=str(attempt.lease_token))


def _run_single_query(
    gateway: RunStateGateway,
    ls_client: CandidateClient,
    attempt: Any,
    *,
    params: dict[str, Any] | None = None,
    query_index: str | None = None,
    fallback_params: dict[str, Any] | None = None,
) -> CandidateStageResult:
    """기존 단일 ``query_index`` 경로: t1859 실패 시 t1856 폴백(하위 호환)."""
    request_params = params if params is not None else {"t1859InBlock": {"query_index": query_index or ""}}
    active_source = PRIMARY_TR
    active_response: LsResponse | None = None
    fallback_used = False

    primary_response, primary_failure_code = _request_ok_or_code(ls_client, PRIMARY_TR, request_params)
    if primary_failure_code is None:
        active_response = primary_response
    else:
        fallback_response, fallback_failure_code = _request_ok_or_code(
            ls_client, FALLBACK_TR, fallback_params if fallback_params is not None else {"t1856InBlock": {}}
        )
        if fallback_failure_code is None:
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

    return _complete_stage(
        gateway, attempt,
        source=active_source,
        records=_response_records(active_response),
        fallback_used=fallback_used,
        primary_failure_code=primary_failure_code,
        success_result_code=active_response.result_code,
        unprocessed_count=active_response.unprocessed_count,
    )


def _run_condition_bundle(
    gateway: RunStateGateway,
    ls_client: CandidateClient,
    attempt: Any,
    condition_search_user_id: str,
    *,
    fallback_params: dict[str, Any] | None = None,
) -> CandidateStageResult:
    """t1866 조건 목록을 조회해 각 조건을 t1859로 직렬 실행하고 통합·선별한다.

    조건 목록 실패는 ``CONDITION_LIST_UNAVAILABLE``, 0건 목록은 ``CONDITION_LIST_EMPTY``로
    failed stage를 기록한다. 일부 조건만 실패하면 성공 조건의 후보만 저장하고 실패 조건을
    metadata로 남긴다(partial). 전부 실패했을 때만 기존 t1856 폴백을 시도한다.
    """
    list_response, list_failure_code = _request_ok_or_code(
        ls_client,
        CONDITION_LIST_TR,
        {"t1866InBlock": {"user_id": condition_search_user_id, "gb": "0", "group_name": "", "cont": "", "cont_key": ""}},
    )
    if list_failure_code is not None:
        return _record_failed_stage(gateway, attempt, CONDITION_LIST_UNAVAILABLE, cause_code=list_failure_code)
    condition_indexes = _condition_query_indexes(list_response)
    if condition_indexes is None:
        return _record_failed_stage(gateway, attempt, CONDITION_LIST_UNAVAILABLE)
    if not condition_indexes:
        return _record_failed_stage(gateway, attempt, CONDITION_LIST_EMPTY, unprocessed_count=0)

    combined_records: list[Any] = []
    condition_failures: list[dict[str, str]] = []
    succeeded = 0
    unprocessed_sum = 0
    for query_index in condition_indexes:
        response, failure_code = _request_ok_or_code(ls_client, PRIMARY_TR, {"t1859InBlock": {"query_index": query_index}})
        if failure_code is not None:
            condition_failures.append({"query_index": query_index, "result_code": failure_code})
            continue
        chunks = _response_records(response)
        if isinstance(chunks, (list, tuple)):
            combined_records.extend(chunks)
        else:
            combined_records.append(chunks)
        succeeded += 1
        unprocessed_sum += response.unprocessed_count

    meta = {
        "condition_count": len(condition_indexes),
        "condition_succeeded": succeeded,
        "condition_failed": len(condition_failures),
    }
    if condition_failures:
        meta["failed_conditions"] = condition_failures
    if succeeded >= 1:
        if condition_failures:
            return _complete_stage(
                gateway, attempt,
                source=PRIMARY_TR,
                records=combined_records,
                fallback_used=False,
                primary_failure_code=None,
                success_result_code="OK",
                unprocessed_count=unprocessed_sum,
                force_partial=True,
                partial_result_code=PARTIAL_CONDITION_FAILURE,
                extra_metadata=meta,
            )
        return _complete_stage(
            gateway, attempt,
            source=PRIMARY_TR,
            records=combined_records,
            fallback_used=False,
            primary_failure_code=None,
            success_result_code="OK",
            unprocessed_count=unprocessed_sum,
            extra_metadata=meta,
        )

    # 전부 실패 → 기존 유일한 폴백 경로(t1856)를 시도한다. 실패 원인이 된 각 조건의
    # result_code를 t1859_result_code에 누적(쉼표 결합)해 빈 값으로 조용히 넘어가지 않게 한다.
    primary_failure_code = ",".join(sorted({failure["result_code"] for failure in condition_failures})) or "LS_REQUEST_ERROR"
    fallback_response, fallback_failure_code = _request_ok_or_code(
        ls_client, FALLBACK_TR, fallback_params if fallback_params is not None else {"t1856InBlock": {}}
    )
    if fallback_failure_code is None:
        return _complete_stage(
            gateway, attempt,
            source=FALLBACK_TR,
            records=_response_records(fallback_response),
            fallback_used=True,
            primary_failure_code=primary_failure_code,
            success_result_code=fallback_response.result_code,
            unprocessed_count=fallback_response.unprocessed_count,
            extra_metadata=meta,
        )
    unprocessed = max(
        unprocessed_sum,
        fallback_response.unprocessed_count if fallback_response is not None else 0,
        1,
    )
    result = {
        "result_code": "CANDIDATE_SOURCES_EXHAUSTED",
        "t1859_result_code": primary_failure_code,
        "t1856_result_code": fallback_failure_code,
        **meta,
    }
    gateway.write_stage(attempt.run_id, Stage.CANDIDATES, attempt.fence_token, attempt.lease_token, StageStatus.RUNNING, StageStatus.FAILED, result=result, unprocessed_count=unprocessed, fallback_used=False)
    return CandidateStageResult("failed", "CANDIDATE_SOURCES_EXHAUSTED", 0, fallback_used=False, run_id=str(attempt.run_id))


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
    condition_search_user_id: str | None = None,
) -> CandidateStageResult:
    """한 attempt의 candidates stage를 성공/실패로 종결한다.

    ``condition_search_user_id``가 주어지면 t1866으로 계정의 전체 조건 목록을 조회해 각
    조건을 t1859로 직렬 실행하고(성공 조건이 1개 이상이면) 그 결과를 source ``t1859``로
    통합·선별한다. 조건이 하나도 성공하지 못했을 때만 기존 t1856 경로로 자동 재시도한다.
    폴백 호출 자체가 성공했을 때만 ``runs.fallback_used`` 를 true로 기록하며, 두 경로가
    모두 실패하면 두 result_code를 모두 남기고 stage는 조용히 성공 처리되지 않는다.

    ``query_index`` 단일 파라미터는 ``condition_search_user_id``가 None일 때만 사용하는
    하위 호환 경로다(t1859 실패 시 t1856 폴백 -- 기존 동작 보존).

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

    if condition_search_user_id is not None:
        return _run_condition_bundle(
            gateway,
            ls_client,
            attempt,
            condition_search_user_id,
            fallback_params=fallback_params,
        )
    return _run_single_query(
        gateway,
        ls_client,
        attempt,
        params=params,
        query_index=query_index,
        fallback_params=fallback_params,
    )


__all__ = ["CandidateStageResult", "run_candidate_stage"]