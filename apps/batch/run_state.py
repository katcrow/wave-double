"""Supabase RPC와 배치 오케스트레이터 사이의 run-state adapter."""

from dataclasses import dataclass
from datetime import datetime
from typing import Any, Protocol
from uuid import UUID

from domain.run_state import BatchKind, LogicalRunKey, Stage, StageStatus, Trigger, validate_stage


class RpcClient(Protocol):
    def rpc(self, function: str, params: dict[str, Any]) -> Any: ...


class RunStateError(RuntimeError):
    """RPC가 반환한 안전한 구조화 오류."""

    def __init__(self, code: str, message: str, *, retryable: bool = False) -> None:
        super().__init__(message)
        self.code = code
        self.message = message
        self.retryable = retryable


@dataclass(frozen=True)
class Attempt:
    run_id: UUID
    logical_run_key: str
    attempt_no: int
    fence_token: int
    lease_token: UUID
    lease_expires_at: datetime


@dataclass(frozen=True)
class RpcResult:
    data: Any


class RunStateGateway:
    def __init__(self, client: RpcClient) -> None:
        self._client = client

    def _call(self, function: str, params: dict[str, Any]) -> Any:
        try:
            response = self._client.rpc(function, params)
            if hasattr(response, "execute"):
                response = response.execute()
            error = response.get("error") if isinstance(response, dict) else getattr(response, "error", None)
            if error:
                self._raise_error(error)
            return getattr(response, "data", response)
        except RunStateError:
            raise
        except Exception as exc:
            raise RunStateError("RPC_ERROR", str(exc), retryable=True) from exc

    @staticmethod
    def _raise_error(error: Any) -> None:
        if isinstance(error, dict):
            raise RunStateError(
                str(error.get("code", "RPC_ERROR")),
                str(error.get("message", "run-state RPC failed")),
                retryable=bool(error.get("retryable", False)),
            )
        raise RunStateError(
            str(getattr(error, "code", "RPC_ERROR")),
            str(getattr(error, "message", error)),
            retryable=bool(getattr(error, "retryable", False)),
        )

    def start_attempt(
        self,
        key: LogicalRunKey,
        trigger: Trigger,
        *,
        lease_seconds: int = 300,
    ) -> Any:
        if lease_seconds <= 0:
            raise ValueError("lease_seconds must be positive")
        return self._call(
            "start_attempt",
            {
                "p_logical_run_key": key.value,
                "p_trading_day": key.trading_day.isoformat(),
                "p_batch_kind": key.batch_kind.value,
                "p_trigger": trigger.value,
                "p_lease_seconds": lease_seconds,
            },
        )

    def write_stage(
        self,
        run_id: UUID,
        stage: str | Stage,
        fence_token: int,
        lease_token: UUID,
        expected_status: str | StageStatus,
        status: str | StageStatus,
        *,
        result: dict[str, Any] | None = None,
        unprocessed_count: int = 0,
    ) -> Any:
        if fence_token <= 0:
            raise ValueError("fence_token must be positive")
        if unprocessed_count < 0:
            raise ValueError("unprocessed_count must be non-negative")
        if result is not None and not isinstance(result, dict):
            raise TypeError("result must be a dictionary")
        validate_stage(stage)
        expected = StageStatus(expected_status).value
        target = StageStatus(status).value
        return self._call(
            "write_stage",
            {
                "p_run_id": str(run_id),
                "p_stage": str(stage),
                "p_fence_token": fence_token,
                "p_lease_token": str(lease_token),
                "p_expected_status": expected,
                "p_status": target,
                "p_result": result or {},
                "p_unprocessed_count": unprocessed_count,
            },
        )

    def write_candidates(
        self,
        run_id: UUID,
        fence_token: int,
        lease_token: UUID,
        candidates: list[dict[str, Any]],
        metadata: dict[str, Any],
    ) -> Any:
        if fence_token <= 0:
            raise ValueError("fence_token must be positive")
        if not isinstance(candidates, list) or not isinstance(metadata, dict):
            raise TypeError("candidates and metadata must be mappings")
        return self._call("write_candidates", {
            "p_run_id": str(run_id), "p_fence_token": fence_token,
            "p_lease_token": str(lease_token), "p_candidates": candidates,
            "p_metadata": metadata,
        })

    def heartbeat(self, run_id: UUID, fence_token: int, lease_token: UUID, *, lease_seconds: int = 300) -> Any:
        if fence_token <= 0:
            raise ValueError("fence_token must be positive")
        if lease_seconds <= 0:
            raise ValueError("lease_seconds must be positive")
        return self._call(
            "heartbeat_attempt",
            {
                "p_run_id": str(run_id),
                "p_fence_token": fence_token,
                "p_lease_token": str(lease_token),
                "p_lease_seconds": lease_seconds,
            },
        )

    def reap(self, *, now: datetime | None = None) -> Any:
        params = {} if now is None else {"p_now": now.isoformat()}
        return self._call("reap_expired_attempts", params)

    def publish(self, run_id: UUID, fence_token: int, lease_token: UUID) -> Any:
        if fence_token <= 0:
            raise ValueError("fence_token must be positive")
        return self._call(
            "publish_attempt",
            {"p_run_id": str(run_id), "p_fence_token": fence_token, "p_lease_token": str(lease_token)},
        )
