"""장시간 stage 실행 중 lease를 갱신하는 heartbeat 헬퍼.

tags/supply 등 후보별로 OHLCV 로딩·계산·저장을 수행하는 stage는 LS API TR별
1건/초 제한 하에서 ``lease_seconds`` 기본값(300초) 안에 끝나지 못할 수 있다
(epic-2-retro item-11, spec-2-5 deferred #2). lease가 만료되면 stage write가
``STALE_FENCE_OR_LEASE``로 거부돼 정상 계산 결과가 폐기된다.

이 모듈은 ``heartbeat_attempt`` RPC(``RunStateGateway.heartbeat``)를 주기적으로
호출해 실행 중 lease를 연장한다. 호출 주기는 ``interval_seconds``로 조정 가능하며,
마지막 heartbeat 이후 ``interval_seconds`` 미만이면 호출을 건너뛴다(네트워크 절약).
"""

from __future__ import annotations

import time
from typing import Callable, Protocol
from uuid import UUID

from .run_state import RunStateGateway


class HeartbeatPolicy(Protocol):
    """장시간 stage에서 주기적으로 lease를 갱신하는 정책.

    stage 루프가 한 종목(또는 한 배치의 종목군)을 처리할 때마다 ``beat()``를
    호출한다. 구현은 내부적으로 마지막 heartbeat 시각을 기억해 ``interval_seconds``
    이상 경과했을 때만 실제 RPC를 발행한다(호출 비용 절감).
    """

    def beat(self) -> None: ...


class LeaseHeartbeat:
    """``heartbeat_attempt`` RPC로 lease를 연장하는 기본 구현.

    실패(일시적 네트워크 오류 포함)는 RPC가 예외를 던지면 ``failures`` 카운터를
    증가시키고 로그로 남긴 뒤 잠자코 넘어간다 -- heartbeat 호출 자체의 실패가 stage
    계산을 중단시키지 않아야 하기 때문이다(단일 heartbeat 실패로 정상 계산을 버리는
    것보다, lease가 실제로 만료되면 최종 stage write가 ``STALE_FENCE_OR_LEASE``로
    거부되는 것이 더 정확한 실패 신호이다. 다만 재사용은 피하고자 heartbeat 실패가
    ``max_failures`` 이상 누적되면(예: 네트워크 단절) ``HeartbeatExhausted``를
    던진다).
    """

    def __init__(
        self,
        gateway: RunStateGateway,
        run_id: UUID | str,
        fence_token: int | str,
        lease_token: UUID | str,
        *,
        lease_seconds: int = 300,
        interval_seconds: float = 60.0,
        max_failures: int = 3,
        monotonic: Callable[[], float] = time.monotonic,
        logger: Callable[[str], None] | None = None,
    ) -> None:
        if lease_seconds <= 0:
            raise ValueError("lease_seconds must be positive")
        if interval_seconds <= 0:
            raise ValueError("interval_seconds must be positive")
        if max_failures <= 0:
            raise ValueError("max_failures must be positive")
        self._gateway = gateway
        self._run_id = run_id if isinstance(run_id, UUID) else UUID(str(run_id))
        self._fence_token = int(fence_token)
        self._lease_token = lease_token if isinstance(lease_token, UUID) else UUID(str(lease_token))
        self._lease_seconds = lease_seconds
        self._interval_seconds = interval_seconds
        self._max_failures = max_failures
        self._monotonic = monotonic
        self._logger = logger or (lambda _msg: None)
        self._last_beat: float | None = None
        self.failures = 0
        self.beat_count = 0

    def beat(self) -> None:
        now = self._monotonic()
        if self._last_beat is not None and now - self._last_beat < self._interval_seconds:
            return
        try:
            self._gateway.heartbeat(
                self._run_id,
                self._fence_token,
                self._lease_token,
                lease_seconds=self._lease_seconds,
            )
        except Exception as exc:  # noqa: BLE001 - heartbeat 실패는 일시적 네트워크 오류일 수 있다
            self.failures += 1
            self._logger(f"heartbeat failed (run={self._run_id}, failures={self.failures}): {exc}")
            if self.failures >= self._max_failures:
                raise HeartbeatExhausted(
                    f"lease heartbeat failed {self.failures} times consecutively (run={self._run_id})"
                ) from exc
            return
        self._last_beat = now
        self.beat_count += 1


class HeartbeatExhausted(RuntimeError):
    """연속 heartbeat 실패로 lease 갱신을 포기했음을 나타낸다."""


__all__ = ["HeartbeatPolicy", "LeaseHeartbeat", "HeartbeatExhausted"]