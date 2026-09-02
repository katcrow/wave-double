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
from .candidate_tags_repository import TagsRepositoryProtocol
from .ohlcv_cache import LsOhlcvCacheProvider, SupabaseOhlcvCacheRepository, initialize_new_ticker_history, update_existing_ticker_history
from .ohlcv_cache_loader import OhlcvDbClient
from .run_state import RunStateGateway, parse_attempt, safe_record_dispatch_receipt
from .tags_stage import CandidateFetcherProtocol, TagsClient, TagsStageResult, run_tags_stage

# status를 "얼마나 나쁜가"로 정렬한다 -- candidates/tags 결과를 합칠 때 더 나쁜 쪽이 이긴다.
_STATUS_SEVERITY = {"success": 0, "partial": 1, "failed": 2}


@dataclass(frozen=True)
class SchedulerResult:
    status: str
    result_code: str
    candidate_count: int = 0
    fallback_used: bool = False
    skip_reason: str | None = None
    run_id: str | None = None
    logical_run_key: str | None = None
    tags_status: str | None = None
    tags_result_code: str | None = None


def _build_logical_run_key(batch_kind: BatchKind, now_kst: datetime) -> LogicalRunKey:
    trading_day = now_kst.date()
    if batch_kind is BatchKind.INTRADAY:
        slot = floor_to_half_hour(now_kst).time()
        return LogicalRunKey(trading_day, batch_kind, slot)
    return LogicalRunKey(trading_day, batch_kind)


def _from_candidate_result(
    result: CandidateStageResult, tags_result: TagsStageResult | None = None
) -> SchedulerResult:
    """candidates stage 결과와(있다면) tags stage 결과를 하나의 ``SchedulerResult``로 합친다.

    tags stage가 실행됐다면 그 결과가 조용히 버려지지 않도록 ``tags_status``/
    ``tags_result_code``로 노출하고, 전체 ``status``도 두 stage 중 더 나쁜 쪽을
    따르게 한다(tags가 failed면 배치 전체가 success로 보고되지 않는다).
    """
    status = result.status
    tags_status: str | None = None
    tags_result_code: str | None = None
    if tags_result is not None:
        tags_status = tags_result.status
        tags_result_code = tags_result.result_code
        if _STATUS_SEVERITY.get(tags_result.status, 0) > _STATUS_SEVERITY.get(status, 0):
            status = tags_result.status
    return SchedulerResult(
        status,
        result.result_code,
        candidate_count=result.candidate_count,
        fallback_used=result.fallback_used,
        run_id=result.run_id,
        tags_status=tags_status,
        tags_result_code=tags_result_code,
    )


def run_scheduled_batch(
    batch_kind: BatchKind | str,
    now_kst: datetime,
    calendar_repository: CalendarRepository,
    daily_bar_provider: DailyBarProvider,
    gateway: RunStateGateway,
    candidate_client: CandidateClient,
    ohlcv_provider: LsOhlcvCacheProvider,
    ohlcv_repository: SupabaseOhlcvCacheRepository,
    candidate_fetcher: CandidateFetcherProtocol,
    ohlcv_loader: OhlcvDbClient,
    tags_repository: TagsRepositoryProtocol,
    *,
    query_index: str | None = None,
    lease_seconds: int = 300,
    trigger: Trigger = Trigger.SCHEDULE,
    dispatch_request_id: str | None = None,
    strategy_client: TagsClient | None = None,
) -> SchedulerResult:
    """휴장이면 attempt를 시작한 뒤 즉시 skip 처리하고, 개장일이면 candidate stage로 위임한다.

    candidates stage가 success/partial이면 이어서 일봉 이력을 확보/갱신
    (``initialize_new_ticker_history``/``update_existing_ticker_history``)한 뒤
    tags stage(``run_tags_stage``)를 실행한다. candidates가 failed/휴장(skip)이면
    이후 stage를 실행하지 않는다(story 2.5 Always 규칙). REPLAYED(이전 attempt 재생)는
    fence_token/lease_token이 없어 이 파이프라인을 건너뛴다 -- 이미 이전 attempt에서
    완결된 발행이다.

    ``dispatch_request_id``가 주어지면(수동 트리거로 GitHub Actions가 CLI를 호출한 경우)
    run_id가 확정되는 즉시 dispatch outbox에 receipt를 기록한다(AD-18). 기록 실패는
    ``safe_record_dispatch_receipt``가 흡수하므로 이 함수의 반환 결과에는 영향이 없다.
    """
    kind = batch_kind if isinstance(batch_kind, BatchKind) else BatchKind(batch_kind)
    key = _build_logical_run_key(kind, now_kst)

    decision = resolve_for_schedule(key.trading_day, daily_bar_provider, calendar_repository)

    if decision.status is CalendarStatus.CLOSED:
        started = gateway.start_attempt(key, trigger, lease_seconds=lease_seconds)
        if isinstance(started, dict) and started.get("replayed"):
            replayed_run_id = started.get("run_id")
            safe_record_dispatch_receipt(gateway, dispatch_request_id, replayed_run_id)
            return SchedulerResult(
                "success",
                "REPLAYED",
                run_id=str(replayed_run_id) if replayed_run_id is not None else None,
                logical_run_key=str(started.get("logical_run_key"))
                if started.get("logical_run_key") is not None
                else None,
            )
        attempt = parse_attempt(started)
        safe_record_dispatch_receipt(gateway, dispatch_request_id, attempt.run_id)
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
        trigger,
        query_index=query_index,
        lease_seconds=lease_seconds,
        dispatch_request_id=dispatch_request_id,
    )

    # candidates가 success/partial이고 REPLAYED가 아닐 때만(fence_token 확정) 이어서
    # ohlcv 확보/갱신 후 tags stage를 실행한다. failed/skip(휴장)은 여기 도달하지 않거나
    # fence_token이 없어 자동으로 파이프라인을 건너뛴다.
    tags_result: TagsStageResult | None = None
    if result.status in ("success", "partial") and result.fence_token is not None:
        tickers = [candidate.ticker for candidate in result.selection.candidates] if result.selection else []
        initialize_new_ticker_history(tickers, ohlcv_provider, ohlcv_repository, key.trading_day)
        update_existing_ticker_history(tickers, ohlcv_provider, ohlcv_repository, key.trading_day)
        tags_result = run_tags_stage(
            gateway,
            candidate_fetcher,
            ohlcv_loader,
            tags_repository,
            result.run_id,
            result.fence_token,
            result.lease_token,
            key.trading_day,
            strategy_client=strategy_client,
            batch_kind=kind.value,
        )

    return _from_candidate_result(result, tags_result)


__all__ = ["SchedulerResult", "run_scheduled_batch"]
