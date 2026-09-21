"""t1857 스케줄 오케스트레이터: 휴장/개장 분기와 candidate stage 위임.

GitHub Actions cron이 호출하는 orchestrator 진입점의 핵심 로직. 휴장 판정은
``resolve_for_schedule``(캐시 우선)로만 하고, 개장일에는 기존
``run_candidate_stage``를 ``Trigger.SCHEDULE``로 위임한다.
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import datetime

from domain.calendar import CalendarStatus, floor_to_intraday_slot
from domain.run_state import BatchKind, LogicalRunKey, Stage, StageStatus, Trigger

from .calendar import CalendarRepository, DailyBarProvider, resolve_for_schedule
from .bias_repository import BiasRepositoryProtocol
from .bias_stage import BiasStageResult, run_bias_stage
from .candidate_stage import CandidateClient, CandidateStageResult, run_candidate_stage
from .candidate_tags_repository import TagsRepositoryProtocol
from .heartbeat import HeartbeatPolicy, LeaseHeartbeat
from .ohlcv_cache import LsOhlcvCacheProvider, SupabaseOhlcvCacheRepository, initialize_new_ticker_history, update_existing_ticker_history
from .ohlcv_cache_loader import OhlcvDbClient
from .run_state import RunStateGateway, parse_attempt, safe_record_dispatch_receipt
from .supply_3day_repository import Supply3DayRepositoryProtocol
from .supply_stage import (
    ProgramSupplyProviderProtocol,
    SupplyProviderProtocol,
    SupplyStageResult,
    TaggedCandidateFetcherProtocol,
    run_supply_stage,
)
from .market_supply_repository import MarketSupplyRepositoryProtocol
from .market_supply_stage import (
    MarketProgramSupplyProviderProtocol,
    MarketSupplyProviderProtocol,
    MarketSupplyStageResult,
    run_market_supply_stage,
)
from .strategy_i_stage import (
    StrategyISupplyProviderProtocol,
    StrategyIResult,
    is_strategy_i_window,
    run_strategy_i_stage,
)
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
    supply_status: str | None = None
    supply_result_code: str | None = None
    market_supply_status: str | None = None
    market_supply_result_code: str | None = None
    published: bool = False
    outcome_tracking_status: str | None = None
    bias_status: str | None = None
    bias_result_code: str | None = None
    strategy_i_status: str | None = None
    strategy_i_result_code: str | None = None


def _build_logical_run_key(batch_kind: BatchKind, now_kst: datetime) -> LogicalRunKey:
    trading_day = now_kst.date()
    if batch_kind is BatchKind.INTRADAY:
        # 08:30 시작, 60분 간격(매시 30분), 19:30은 close 배치가 담당한다(Neo 확인, 2026-09-16).
        slot = floor_to_intraday_slot(now_kst, interval_minutes=60, offset_minutes=30).time()
        return LogicalRunKey(trading_day, batch_kind, slot)
    return LogicalRunKey(trading_day, batch_kind)


def _from_candidate_result(
    result: CandidateStageResult,
    tags_result: TagsStageResult | None = None,
    supply_result: SupplyStageResult | None = None,
    market_supply_result: MarketSupplyStageResult | None = None,
    *,
    published: bool = False,
    is_close_batch: bool = False,
    bias_result: BiasStageResult | None = None,
    strategy_i_result: StrategyIResult | None = None,
) -> SchedulerResult:
    """candidates stage 결과와(있다면) tags/supply stage 결과를 하나의 ``SchedulerResult``로 합친다.

    tags/supply stage가 실행됐다면 그 결과가 조용히 버려지지 않도록 ``tags_status``/
    ``tags_result_code``, ``supply_status``/``supply_result_code``로 노출하고, 전체
    ``status``도 세 stage 중 더 나쁜 쪽을 따르게 한다(하나라도 failed면 배치 전체가
    success로 보고되지 않는다).

    ``published``는 close/intraday 배치에서 publish_attempt 호출이 성공했는지 여부다.
    outcome_tracking stage는 close 배치일 때만 DB 단에서 'success'로 기록되므로(SQL의
    ``publish_attempt``가 batch_kind='close'에서만 outcome 발행 루프를 실행), intraday의
    ``published=True``를 outcome_tracking 성공으로 잘못 보고하지 않도록 ``is_close_batch``로
    구분한다.

    ``bias_result``(옵션)와 ``strategy_i_result``(옵션)는 배치 성공과 무관하게
    ``bias_status``/``bias_result_code``, ``strategy_i_status``/``strategy_i_result_code``로만
    노출하며, severity 합산에는 참여하지 않는다.
    """
    status = result.status
    tags_status: str | None = None
    tags_result_code: str | None = None
    if tags_result is not None:
        tags_status = tags_result.status
        tags_result_code = tags_result.result_code
        if _STATUS_SEVERITY.get(tags_result.status, 0) > _STATUS_SEVERITY.get(status, 0):
            status = tags_result.status
    supply_status: str | None = None
    supply_result_code: str | None = None
    if supply_result is not None:
        supply_status = supply_result.status
        supply_result_code = supply_result.result_code
        if _STATUS_SEVERITY.get(supply_result.status, 0) > _STATUS_SEVERITY.get(status, 0):
            status = supply_result.status
    market_supply_status: str | None = None
    market_supply_result_code: str | None = None
    if market_supply_result is not None:
        market_supply_status = market_supply_result.status
        market_supply_result_code = market_supply_result.result_code
        if _STATUS_SEVERITY.get(market_supply_result.status, 0) > _STATUS_SEVERITY.get(status, 0):
            status = market_supply_result.status
    result_code = result.result_code
    for stage_result in (tags_result, supply_result, market_supply_result):
        if stage_result is not None and stage_result.status != "success":
            result_code = stage_result.result_code
            break
    return SchedulerResult(
        status,
        result_code,
        candidate_count=result.candidate_count,
        fallback_used=result.fallback_used,
        run_id=result.run_id,
        tags_status=tags_status,
        tags_result_code=tags_result_code,
        supply_status=supply_status,
        supply_result_code=supply_result_code,
        market_supply_status=market_supply_status,
        market_supply_result_code=market_supply_result_code,
        published=published,
        outcome_tracking_status="success" if published and is_close_batch else None,
        bias_status=bias_result.status if bias_result else None,
        bias_result_code=bias_result.result_code if bias_result else None,
        strategy_i_status=strategy_i_result.status if strategy_i_result else None,
        strategy_i_result_code=strategy_i_result.result_code if strategy_i_result else None,
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
    tagged_candidate_fetcher: TaggedCandidateFetcherProtocol,
    supply_provider: SupplyProviderProtocol,
    program_supply_provider: ProgramSupplyProviderProtocol,
    supply_repository: Supply3DayRepositoryProtocol,
    market_supply_provider: MarketSupplyProviderProtocol | None = None,
    market_program_supply_provider: MarketProgramSupplyProviderProtocol | None = None,
    market_supply_repository: MarketSupplyRepositoryProtocol | None = None,
    *,
    condition_search_user_id: str | None = None,
    lease_seconds: int = 300,
    trigger: Trigger = Trigger.SCHEDULE,
    dispatch_request_id: str | None = None,
    strategy_client: TagsClient | None = None,
    bias_repository: BiasRepositoryProtocol | None = None,
    strategy_i_supply_provider: StrategyISupplyProviderProtocol | None = None,
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
        condition_search_user_id=condition_search_user_id,
        lease_seconds=lease_seconds,
        dispatch_request_id=dispatch_request_id,
    )

    # candidates가 success/partial이고 REPLAYED가 아닐 때만(fence_token 확정) 이어서
    # ohlcv 확보/갱신 후 tags stage를 실행한다. failed/skip(휴장)은 여기 도달하지 않거나
    # fence_token이 없어 자동으로 파이프라인을 건너뛴다.
    tags_result: TagsStageResult | None = None
    supply_result: SupplyStageResult | None = None
    market_supply_result: MarketSupplyStageResult | None = None
    strategy_i_result: StrategyIResult | None = None
    if result.status in ("success", "partial") and result.fence_token is not None:
        # item-11(F1, spec-2-5 deferred #2): 후보 수가 많거나 OHLCV 신규 적재가 길어지면
        # 기본 300초 lease 안에 tags stage가 끝나지 못할 수 있다. 같은 attempt로
        # 주기적으로 heartbeat를 보내 lease를 연장한다. refresh(종목 루프)와 tags stage의
        # 두 윈도우 모두 같은 policy 인스턴스를 공유하므로 lease 연장 주기가 중복되지
        # 않는다(LeaseHeartbeat가 내부적으로 마지막 beat를 기준으로 건너뛴다).
        heartbeat: HeartbeatPolicy | None = None
        if result.lease_token is not None:
            heartbeat = LeaseHeartbeat(
                gateway,
                result.run_id,
                result.fence_token,
                result.lease_token,
                lease_seconds=lease_seconds,
                logger=print,
            )
        tickers = [candidate.ticker for candidate in result.selection.candidates] if result.selection else []
        initialize_new_ticker_history(tickers, ohlcv_provider, ohlcv_repository, key.trading_day, heartbeat=heartbeat)
        update_existing_ticker_history(tickers, ohlcv_provider, ohlcv_repository, key.trading_day, heartbeat=heartbeat)
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
            heartbeat=heartbeat,
        )
        # 전략 I(음봉수급쌍끌이): 16:00~20:00 KST 윈도우에서만 실행. OHLCV 캐시 갱신
        # 이후(위 initialize/update) t1702 단일 거래일 조회로 오늘 양봉 여부와 외국인·기관
        # 쌍끌이 순매수를 판단해 candidate_tags에 strategy='I' 태그를 저장한다.
        # supply_3day보다 먼저 실행해야 한다 -- supply_3day는 tagged_candidate_fetcher로
        # "이 시점까지 태깅된" 후보만 수급을 수집하므로, I 태깅이 그 뒤에 일어나면
        # I 전용 후보(A~H 미해당)는 수급 증거 테이블에 영영 반영되지 않는다(Neo 확인,
        # 2026-09-16).
        if (
            result.status in ("success", "partial")
            and result.fence_token is not None
            and result.lease_token is not None
            and tags_result is not None
            and tags_result.status == "success"
            and is_strategy_i_window(now_kst)
            and strategy_i_supply_provider is not None
        ):
            try:
                strategy_i_result = run_strategy_i_stage(
                    gateway,
                    candidate_fetcher,
                    ohlcv_loader,
                    strategy_i_supply_provider,
                    tags_repository,
                    result.run_id,
                    result.fence_token,
                    result.lease_token,
                    key.trading_day,
                    heartbeat=heartbeat,
                )
            except Exception as exc:  # noqa: BLE001 - 전략 I 실패는 기존 배치 성공을 보존한다
                print(f"run_id={result.run_id} stage=strategy_i strategy_i_status=failed "
                      f"result_code=STRATEGY_I_FAILED message={exc}")
                strategy_i_result = StrategyIResult("failed", "STRATEGY_I_FAILED")

        # Story 4.1 review patch: close/intraday에서만 tags stage 직후 supply stage를 실행한다
        # (Story 4.3 장중 D0 누적 전제). premarket은 당일(D0) 거래 데이터가 아직 없어 t1702
        # 응답에 D0 날짜가 누락되므로, 실행하면 모든 태깅된 후보가 상시 error로 집계되어
        # supply stage가 매 premarket 배치마다 partial로 보고되고 LS API 호출도 낭비된다.
        if kind is not BatchKind.PREMARKET:
            supply_result = run_supply_stage(
                gateway,
                tagged_candidate_fetcher,
                calendar_repository,
                supply_provider,
                program_supply_provider,
                supply_repository,
                result.run_id,
                result.fence_token,
                result.lease_token,
                key.trading_day,
                batch_kind=kind,
            )
            if (
                market_supply_provider is not None
                and market_program_supply_provider is not None
                and market_supply_repository is not None
            ):
                market_supply_result = run_market_supply_stage(
                    gateway,
                    market_supply_provider,
                    market_program_supply_provider,
                    market_supply_repository,
                    result.run_id,
                    result.fence_token,
                    result.lease_token,
                    key.trading_day,
                    batch_kind=kind,
                )
            else:
                # 기존 외부 호출자의 시그니처 호환성. 실제 CLI는 항상 세 adapter를
                # 주입하므로 production 경로에서는 시장 stage를 건너뛰지 않는다.
                market_supply_result = None

    # Story 3.5 후속 조치(deferred-work gap 해소) + 대시보드 stale 스냅샷 수정
    # (2026-09-15): close/intraday가 candidates+tags+supply_3day+market_supply 모두
    # success로 종결되고 fence/lease가 확정된 경우 publish_attempt를 호출한다.
    # publish_attempt SQL은 batch_kind='close'일 때만 outcome 발행(emit_open_command)과
    # 일일 관찰·SUSPENDED/TP/SL/TIMEOUT 판정 루프를 실행하므로, intraday를 여기 포함해도
    # outcome 파이프라인은 그대로 close 전용으로 남는다 -- 대신 intraday도
    # current_complete_run_id/published_at을 갱신해 대시보드가 마지막 close가 아니라
    # 가장 최근 성공한 attempt(장중 포함)의 후보 수·카드를 보여주게 한다.
    # premarket은 supply_3day/market_supply stage 자체를 건너뛰므로(위 참고) 이 게이트를
    # 자연히 통과하지 못해 별도 제외가 필요 없다.
    published = False
    if (
        kind in (BatchKind.CLOSE, BatchKind.INTRADAY)
        and result.status == "success"
        and result.fence_token is not None
        and result.run_id is not None
        and result.lease_token is not None
        and tags_result is not None
        and tags_result.status == "success"
        and supply_result is not None
        and supply_result.status == "success"
        and market_supply_result is not None
        and market_supply_result.status == "success"
    ):
        try:
            gateway.publish(result.run_id, result.fence_token, result.lease_token)
            published = True
        except Exception as exc:  # noqa: BLE001 - 발행 실패를 구조화된 failed stage로 전환
            # outcome_tracking은 publish_attempt가 직접 'success'로 기록하므로(write_stage를
            # 거치지 않는다) publish 실패 시 항상 'pending'에 머물러 있다. write_stage의 일반
            # 전이 규칙은 pending -> failed를 바로 허용하지 않으므로 pending -> running ->
            # failed 두 단계로 기록한다. 이 기록 자체가 실패해도(예: 이미 다른 상태로 전이됨)
            # 원래 publish 실패 원인을 가리는 2차 미처리 예외를 만들지 않도록 흡수한다.
            try:
                gateway.write_stage(
                    result.run_id,
                    Stage.OUTCOME_TRACKING,
                    result.fence_token,
                    result.lease_token,
                    StageStatus.PENDING,
                    StageStatus.RUNNING,
                )
                gateway.write_stage(
                    result.run_id,
                    Stage.OUTCOME_TRACKING,
                    result.fence_token,
                    result.lease_token,
                    StageStatus.RUNNING,
                    StageStatus.FAILED,
                    result={"result_code": "OUTCOME_PUBLISH_FAILED", "message": str(exc)},
                )
            except Exception as record_exc:  # noqa: BLE001 - 원래 publish 실패 원인을 보존한다
                print(f"run_id={result.run_id} stage=outcome_tracking "
                      f"failed_to_record_failure={record_exc} publish_error={exc}")
            return SchedulerResult(
                "failed",
                "OUTCOME_PUBLISH_FAILED",
                candidate_count=result.candidate_count,
                fallback_used=result.fallback_used,
                run_id=result.run_id,
                tags_status=tags_result.status,
                tags_result_code=tags_result.result_code,
                supply_status=supply_result.status if supply_result is not None else None,
                supply_result_code=supply_result.result_code if supply_result is not None else None,
                market_supply_status=market_supply_result.status if market_supply_result is not None else None,
                market_supply_result_code=market_supply_result.result_code if market_supply_result is not None else None,
                published=False,
                outcome_tracking_status="failed",
            )

    bias_result = None
    if published and kind is BatchKind.CLOSE and bias_repository is not None:
        try:
            bias_result = run_bias_stage(
                gateway, bias_repository, ohlcv_provider, ohlcv_repository, ohlcv_loader,
                result.run_id, result.fence_token, result.lease_token, key.trading_day,
                result.selection.truncated_candidates if result.selection else (),
                strategy_client=strategy_client,
            )
        except Exception as exc:  # noqa: BLE001 - 옵션 stage의 예기치 않은 경계 오류도 이미 발행된 배치 성공을 보존한다.
            print(f"run_id={result.run_id} stage=bias bias_status=failed result_code=BIAS_FAILED "
                  f"failure_recorded=False message={exc}")
            bias_result = BiasStageResult("failed", "BIAS_FAILED", failure_recorded=False)
    return _from_candidate_result(result, tags_result, supply_result, market_supply_result,
                                  published=published, is_close_batch=kind is BatchKind.CLOSE,
                                  bias_result=bias_result, strategy_i_result=strategy_i_result)


__all__ = ["SchedulerResult", "run_scheduled_batch"]
