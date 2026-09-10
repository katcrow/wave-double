"""Story 5.4: canonical population 읽기와 원자적 편향 append RPC."""

from typing import Any, Protocol
from uuid import UUID

from domain.candidate_selection import SourceContribution

from .bias_metrics import BiasMetricsResult, PopulationSignal
from .run_state import RpcClient, RunStateError, RunStateGateway


class BiasRepositoryProtocol(Protocol):
    def fetch_population(self, run_id: str, fence_token: int, lease_token: str) -> list[PopulationSignal]: ...

    def append(self, run_id: str, fence_token: int, lease_token: str, event_id: UUID,
               metrics: BiasMetricsResult, status: str) -> Any: ...


class SupabaseBiasRepository:
    """공유 RPC client의 수명은 CLI ExitStack이 관리한다."""

    def __init__(self, client: RpcClient) -> None:
        self._gateway = RunStateGateway(client)

    @staticmethod
    def _identity(run_id, fence_token, lease_token):
        return {"p_run_id": str(run_id), "p_fence_token": fence_token,
                "p_lease_token": str(lease_token)}

    def fetch_population(self, run_id, fence_token, lease_token):
        rows = self._gateway._call("get_bias_population", self._identity(run_id, fence_token, lease_token))
        if not isinstance(rows, list):
            raise ValueError("invalid canonical bias population response")
        return [PopulationSignal(
            ticker=str(row["ticker"]), strategies=tuple(row["strategies"]),
            sources=tuple(SourceContribution(source=s["source"], weight=float(s["weight"]))
                          for s in row["sources"]),
        ) for row in rows]

    def append(self, run_id, fence_token, lease_token, event_id, metrics, status):
        params = {**self._identity(run_id, fence_token, lease_token),
                  "p_event_id": str(event_id), "p_calculation_meta": metrics.calculation_meta,
                  "p_rows": metrics.as_rows(), "p_status": status}
        # 응답 유실 뒤 재전송에도 같은 UUID와 계산 payload를 보존한다.
        for attempt in range(2):
            try:
                return self._gateway._call("append_bias_event", params)
            except RunStateError as exc:
                if attempt or not exc.retryable:
                    raise
