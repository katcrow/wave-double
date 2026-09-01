"""t1857 스케줄 오케스트레이터: 휴장/개장 분기와 candidate stage 위임.

GitHub Actions cron이 호출하는 orchestrator 진입점의 핵심 로직. 휴장 판정은
``resolve_for_schedule``(캐시 우선)로만 하고, 개장일에는 기존
``run_candidate_stage``를 ``Trigger.SCHEDULE``로 위임한다.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime

from domain.calendar import CalendarStatus, floor_to_half_hour
from domain.run_state import BatchKind, LogicalRunKey, Trigger

from .calendar import CalendarRepository, DailyBarProvider, resolve_for_schedule
from .candidate_stage import CandidateClient, CandidateStageResult, run_candidate_stage
from .run_state import RunStateGateway, parse_attempt


@dataclass(frozen=True)
class SchedulerResult:
    status: str
    result_code: str
    candidate_count: int = 0
    fallback_used: bool = False
    skip_reason: str | None = None
    run_id: str | None = None
    logical_run_key: str | None = None


def _build_logical_run_key(batch_kind: BatchKind, now_kst: datetime) -> LogicalRunKey:
    trading_day = now_kst.date()
    if batch_kind is BatchKind.INTRADAY:
        slot = floor_to_half_hour(now_kst).time()
        return LogicalRunKey(trading_day, batch_kind, slot)
    return LogicalRunKey(trading_day, batch_kind)


def _from_candidate_result(result: CandidateStageResult) -> SchedulerResult:
    return SchedulerResult(
        result.status,
        result.result_code,
        candidate_count=result.candidate_count,
        fallback_used=result.fallback_used,
    )


def run_scheduled_batch(
    batch_kind: BatchKind | str,
    now_kst: datetime,
    calendar_repository: CalendarRepository,
    daily_bar_provider: DailyBarProvider,
    gateway: RunStateGateway,
    candidate_client: CandidateClient,
    *,
    query_index: str | None = None,
    lease_seconds: int = 300,
) -> SchedulerResult:
    """휴장이면 attempt를 시작한 뒤 즉시 skip 처리하고, 개장일이면 candidate stage로 위임한다."""
    kind = batch_kind if isinstance(batch_kind, BatchKind) else BatchKind(batch_kind)
    key = _build_logical_run_key(kind, now_kst)

    decision = resolve_for_schedule(key.trading_day, daily_bar_provider, calendar_repository)

    if decision.status is CalendarStatus.CLOSED:
        started = gateway.start_attempt(key, Trigger.SCHEDULE, lease_seconds=lease_seconds)
        if isinstance(started, dict) and started.get("replayed"):
            return SchedulerResult(
                "success",
                "REPLAYED",
                run_id=str(started.get("run_id")) if started.get("run_id") is not None else None,
                logical_run_key=str(started.get("logical_run_key"))
                if started.get("logical_run_key") is not None
                else None,
            )
        attempt = parse_attempt(started)
        gateway.skip(attempt.run_id, attempt.fence_token, attempt.lease_token, "holiday")
        return SchedulerResult(
            "skipped",
            "HOLIDAY",
            skip_reason="holiday",
            run_id=str(attempt.run_id),
            logical_run_key=attempt.logical_run_key,
        )

    # OPEN 또는 CALENDAR_UNAVAILABLE(일봉 조회 실패)은 모두 휴장이 아니므로 정상 진행한다.
    result = run_candidate_stage(
        gateway,
        candidate_client,
        key,
        Trigger.SCHEDULE,
        query_index=query_index,
        lease_seconds=lease_seconds,
    )
    return _from_candidate_result(result)


__all__ = ["SchedulerResult", "run_scheduled_batch"]
