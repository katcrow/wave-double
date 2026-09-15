"""Story 2.5/6.6/7.5: 후보 태깅 stage 오케스트레이터.

candidates stage(screen)가 성공/부분성공한 뒤, 후보 모집단 한정으로 전략
A/B/C/D/E/F/G/H 시그널을 계산하고 ``candidate_tags``에 저장한다. F는 각도가속·
이평선 쌍바닥(slope-acceleration + moving-average double-bottom) 기법이다.
G는 양음돌파패턴(거래량돌파양봉+음봉풀백+고가돌파), H는 240이평돌파+120이평
우상향필터다(2026-09-15 추가, docs/양음돌파패턴.md·docs/240이평돌파_120이평우상향필터.md).

``ineligible``(이력 부족)과 ``error``(로딩 실패/``SIGNAL_COMPUTE_ERROR``)를 명확히
구분해 집계한다 -- 전자는 정상적으로 태깅 대상에서 제외된 것이고, 후자만 stage
``partial`` 판정과 ``unprocessed_count``에 반영한다(story 2.5 Always 규칙, AD-5
"조용한 누락 금지"의 취지: 실패와 정상 제외를 혼동하지 않는다).

후보 목록 조회(``candidate_fetcher``) 자체의 실패는 조용한 빈 성공으로 만들지
않고 stage를 명시적으로 ``failed``로 기록한다.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date, datetime, timezone
from typing import Any, Protocol
from uuid import UUID

import pandas as pd

from backtest.strategy_api import StrategyResult, compute_abc
from domain.ohlcv_cache import MIN_HISTORY_TRADING_DAYS, OhlcvCacheStatus
from domain.run_state import Stage, StageStatus

from .candidate_tags_repository import CandidateTag, TagsRepositoryProtocol
from .heartbeat import HeartbeatPolicy
from .ohlcv_cache_loader import OhlcvDbClient
from .run_state import RunStateGateway

_STRATEGY_KEYS = ("A", "B", "C", "D", "E", "F", "G", "H")


class TagsClient(Protocol):
    """전략 시그널 계산을 위한 프로토콜. compute_abc를 캡슐화."""

    def compute(self, frame: pd.DataFrame, ticker: str) -> StrategyResult: ...


class CandidateFetcherProtocol(Protocol):
    """``candidates`` 테이블에서 attempt별 후보 목록을 조회하는 프로토콜."""

    def fetch(self, run_id: str) -> list[Any]: ...


@dataclass(frozen=True)
class TaggedCandidate:
    """태깅이 완료된 단일 종목 결과."""

    ticker: str
    candidate_id: str
    strategies: list[str]  # ["A"], ["A", "F"], etc.
    signal_date: date | None = None


@dataclass
class TagsStageResult:
    """tags stage의 최종 결과."""

    status: str  # "success" | "partial" | "failed"
    result_code: str
    tagged_count: int = 0
    error_count: int = 0
    ineligible_count: int = 0
    vanished_count: int = 0
    persist_failed_count: int = 0
    batch_kind: str = "close"
    tagged_candidates: list[TaggedCandidate] = field(default_factory=list)
    run_id: str | None = None
    vanished_sync_failed: bool = False


class DefaultStrategyClient:
    """``backtest.strategy_api.compute_abc``를 직접 호출하는 기본 구현."""

    def compute(self, frame: pd.DataFrame, ticker: str) -> StrategyResult:
        return compute_abc(frame, ticker=ticker)


def run_tags_stage(
    gateway: RunStateGateway,
    candidate_fetcher: CandidateFetcherProtocol,
    ohlcv_loader: OhlcvDbClient,
    tags_repo: TagsRepositoryProtocol,
    run_id: UUID | str,
    fence_token: int | str,
    lease_token: UUID | str,
    trading_day: date,
    *,
    strategy_client: TagsClient | None = None,
    batch_kind: str = "close",
    heartbeat: HeartbeatPolicy | None = None,
) -> TagsStageResult:
    """tags stage를 실행한다.

    ``batch_kind``: 배치 유형(close/intraday/premarket). 장중 배치의 태깅은 참고
    표시 전용이며, close 배치의 태깅만 이후 Epic 3의 outcome 생성 자격을 가진다
    (자격 판정 로직 자체는 Epic 3 범위, 이 stage는 결과에 노출만 한다).

    한 종목의 실패가 나머지 종목 처리를 막지 않는다. error가 하나라도 있으면
    stage 결과를 ``partial``로, 없으면(ineligible만 있어도) ``success``로 기록한다.
    """
    client = strategy_client or DefaultStrategyClient()
    run_uuid = run_id if isinstance(run_id, UUID) else UUID(str(run_id))
    lease_uuid = lease_token if isinstance(lease_token, UUID) else UUID(str(lease_token))
    fence_int = int(fence_token)
    run_id_str = str(run_id)

    gateway.write_stage(
        run_uuid, Stage.TAGS, fence_int, lease_uuid,
        StageStatus.PENDING, StageStatus.RUNNING,
    )

    try:
        candidates = candidate_fetcher.fetch(run_id_str)
    except Exception as exc:
        result = {"result_code": "CANDIDATE_FETCH_FAILED", "message": str(exc), "batch_kind": batch_kind}
        gateway.write_stage(
            run_uuid, Stage.TAGS, fence_int, lease_uuid,
            StageStatus.RUNNING, StageStatus.FAILED,
            result=result,
        )
        return TagsStageResult(
            "failed", "CANDIDATE_FETCH_FAILED", batch_kind=batch_kind, run_id=run_id_str
        )

    params_meta = _build_params_meta(batch_kind)
    tagged_candidates: list[TaggedCandidate] = []
    all_tags: list[CandidateTag] = []
    error_count = 0
    ineligible_count = 0

    for cand in candidates:
        if heartbeat is not None:
            heartbeat.beat()
        load_result = ohlcv_loader.load_ohlcv(cand.ticker, trading_day)
        if isinstance(load_result, OhlcvCacheStatus):
            if load_result is OhlcvCacheStatus.INELIGIBLE_INSUFFICIENT_HISTORY:
                ineligible_count += 1
            else:
                error_count += 1
            continue

        try:
            result: StrategyResult = client.compute(load_result, cand.ticker)
        except Exception:
            error_count += 1
            continue

        if result.status is OhlcvCacheStatus.INELIGIBLE_INSUFFICIENT_HISTORY:
            ineligible_count += 1
            continue
        if result.status is OhlcvCacheStatus.ERROR or result.error is not None:
            error_count += 1
            continue

        strategies = [
            key
            for key in _STRATEGY_KEYS
            if (series := result.signals.get(key)) is not None and len(series) >= 2 and bool(series.iloc[-2])
        ]
        if not strategies:
            continue

        signal_date = _extract_signal_date(load_result)
        tagged_candidates.append(TaggedCandidate(cand.ticker, cand.candidate_id, strategies, signal_date))
        for strategy_key in strategies:
            all_tags.append(
                CandidateTag(
                    candidate_id=cand.candidate_id,
                    strategy=strategy_key,
                    signal_date=signal_date or trading_day,
                    attempt_run_id=run_id_str,
                    params_meta=params_meta,
                )
            )

    # 저장 실패 격리(epic-2-retro item-11, F4): 태그 전체를 단일 batch로 보내면
    # 한 행의 실패(FK 위반 등)가 다른 종목의 계산 결과까지 폐기한다. 후보별로
    # 그룹핑해 각 후보의 태그를 따로 upsert하고, 실패한 후보만 격리해 나머지는
    # 보존한다. 전부 실패하면 기존과 동일하게 TAGS_PERSIST_FAILED로 종료하고,
    # 일부만 실패하면 해당 후보 수를 persist_failed_count로 노출해 partial로 기록한다.
    saved_count = 0
    persist_failed_count = 0
    persist_error_message: str | None = None
    if all_tags:
        tags_by_candidate: dict[str, list[CandidateTag]] = {}
        for tag in all_tags:
            tags_by_candidate.setdefault(tag.candidate_id, []).append(tag)
        for candidate_id, candidate_tags in tags_by_candidate.items():
            try:
                saved_count += tags_repo.upsert_tags(candidate_tags)
            except Exception as exc:
                persist_failed_count += 1
                persist_error_message = str(exc)

    if persist_failed_count > 0 and saved_count == 0:
        result = {
            "result_code": "TAGS_PERSIST_FAILED",
            "message": persist_error_message or "all candidate tag upserts failed",
            "tagged_count": 0,
            "error_count": error_count,
            "ineligible_count": ineligible_count,
            "persist_failed_count": persist_failed_count,
            "batch_kind": batch_kind,
        }
        gateway.write_stage(
            run_uuid, Stage.TAGS, fence_int, lease_uuid,
            StageStatus.RUNNING, StageStatus.FAILED,
            result=result, unprocessed_count=error_count + persist_failed_count,
        )
        return TagsStageResult(
            "failed", "TAGS_PERSIST_FAILED",
            tagged_count=0, error_count=error_count, ineligible_count=ineligible_count,
            persist_failed_count=persist_failed_count,
            batch_kind=batch_kind, tagged_candidates=tagged_candidates, run_id=run_id_str,
        )

    if persist_failed_count > 0 and saved_count > 0:
        # 일부 후보만 저장에 실패했다. 실패한 후보를 격리해 나머지는 보존된 상태이므로
        # partial로 기록한다. 부분 저장된 active 태그만으로 소멸 판정을 수행하면 불완전한
        # 집합을 기준으로 잘못 vanished로 표시할 수 있어 소멸 동기화는 건너뛴다(후속 배치가
        # 재동기화한다).
        result = {
            "result_code": "TAGS_PERSIST_PARTIAL",
            "message": persist_error_message or "some candidate tag upserts failed",
            "tagged_count": saved_count,
            "candidate_count": len(candidates),
            "error_count": error_count,
            "ineligible_count": ineligible_count,
            "persist_failed_count": persist_failed_count,
            "batch_kind": batch_kind,
        }
        gateway.write_stage(
            run_uuid, Stage.TAGS, fence_int, lease_uuid,
            StageStatus.RUNNING, StageStatus.PARTIAL,
            result=result, unprocessed_count=error_count + persist_failed_count,
        )
        return TagsStageResult(
            "partial", "TAGS_PERSIST_PARTIAL",
            tagged_count=saved_count, error_count=error_count, ineligible_count=ineligible_count,
            persist_failed_count=persist_failed_count,
            batch_kind=batch_kind, tagged_candidates=tagged_candidates, run_id=run_id_str,
        )

    # Story 2.8: active 태그 upsert가 끝난 뒤 같은 attempt에 대해 소멸 태그를 동기화한다.
    # 실패해도 이미 저장된 active 태그는 유지한다 -- 조용한 실패 금지를 위해 error_count==0이었던
    # 경우(원래는 success였을 경우)에 한해 stage를 partial/VANISHED_SYNC_FAILED로 낮춘다.
    vanished_count = 0
    vanished_sync_failed = False
    try:
        sync_result = tags_repo.sync_vanished(run_id_str)
        if isinstance(sync_result, dict):
            vanished_count = int(sync_result.get("vanished_count", 0) or 0)
    except Exception:
        vanished_sync_failed = True

    result_common = {
        "tagged_count": saved_count,
        "candidate_count": len(candidates),
        "ineligible_count": ineligible_count,
        "vanished_count": vanished_count,
        "batch_kind": batch_kind,
    }

    if vanished_sync_failed and error_count == 0:
        result = {"result_code": "VANISHED_SYNC_FAILED", **result_common}
        gateway.write_stage(
            run_uuid, Stage.TAGS, fence_int, lease_uuid,
            StageStatus.RUNNING, StageStatus.PARTIAL,
            result=result, unprocessed_count=1,
        )
        return TagsStageResult(
            "partial", "VANISHED_SYNC_FAILED",
            tagged_count=saved_count, error_count=error_count, ineligible_count=ineligible_count,
            vanished_count=vanished_count, batch_kind=batch_kind,
            tagged_candidates=tagged_candidates, run_id=run_id_str,
            vanished_sync_failed=True,
        )

    if error_count > 0:
        result_code = "PARTIAL_TAGGING"
        if vanished_sync_failed:
            result_common["vanished_sync_failed"] = True
        result = {"result_code": result_code, **result_common}
        gateway.write_stage(
            run_uuid, Stage.TAGS, fence_int, lease_uuid,
            StageStatus.RUNNING, StageStatus.PARTIAL,
            result=result, unprocessed_count=error_count,
        )
        return TagsStageResult(
            "partial", result_code,
            tagged_count=saved_count, error_count=error_count, ineligible_count=ineligible_count,
            vanished_count=vanished_count, batch_kind=batch_kind,
            tagged_candidates=tagged_candidates, run_id=run_id_str,
            vanished_sync_failed=vanished_sync_failed,
        )

    result = {"result_code": "OK", **result_common}
    gateway.write_stage(
        run_uuid, Stage.TAGS, fence_int, lease_uuid,
        StageStatus.RUNNING, StageStatus.SUCCESS,
        result=result, unprocessed_count=0,
    )
    return TagsStageResult(
        "success", "OK",
        tagged_count=saved_count, ineligible_count=ineligible_count, vanished_count=vanished_count,
        batch_kind=batch_kind, tagged_candidates=tagged_candidates, run_id=run_id_str,
    )


def _build_params_meta(batch_kind: str) -> dict[str, Any]:
    """시그널 계산 파라미터 스냅샷을 생성한다(재현성 검증용)."""
    from backtest.indicator_opt.combine_strategies import DIV3, STOCH_DB
    from backtest.indicator_opt.strategy_d import STRATEGY_D_PARAMS
    from backtest.indicator_opt.strategy_e import STRATEGY_E_PARAMS
    from backtest.indicator_opt.strategy_f import STRATEGY_F_PARAMS
    from backtest.indicator_opt.strategy_g import STRATEGY_G_PARAMS
    from backtest.indicator_opt.strategy_h import STRATEGY_H_PARAMS
    from backtest.indicator_opt.union import TOP3, VOLUME

    return {
        "batch_kind": batch_kind,
        "atr_window": 14,
        "obv_volume_indicators": [
            {"name": name, "params": params}
            for _, name, params in VOLUME
        ],
        "strategy_a_pairs": [
            {"label": label, "ind_a": ind_a, "ind_a_params": params_a, "ind_b": ind_b, "ind_b_params": params_b}
            for label, ind_a, params_a, ind_b, params_b in TOP3
        ],
        "strategy_b_stoch_db": STOCH_DB,
        "strategy_c_div3": DIV3,
        "strategy_d_params": STRATEGY_D_PARAMS.as_dict(),
        "strategy_e_params": STRATEGY_E_PARAMS.as_dict(),
        "strategy_f_params": STRATEGY_F_PARAMS.as_dict(),
        "strategy_g_params": STRATEGY_G_PARAMS.as_dict(),
        "strategy_h_params": STRATEGY_H_PARAMS.as_dict(),
        "min_history_days": MIN_HISTORY_TRADING_DAYS,
        "generated_at": datetime.now(timezone.utc).isoformat(),
    }


def _extract_signal_date(frame: pd.DataFrame) -> date | None:
    """시그널이 발생한 거래일을 추출한다.

    신호는 마지막-1 봉(``iloc[-2]``)에서 확인하므로(마지막 봉 폐기 필터), 해당 봉의
    거래일(DatetimeIndex)을 반환한다. 인덱스가 2행 미만이면 None을 반환한다.
    """
    if len(frame.index) < 2:
        return None
    idx_value = frame.index[-2]
    if hasattr(idx_value, "date"):
        return idx_value.date()
    if isinstance(idx_value, str):
        return date.fromisoformat(idx_value)
    return None


__all__ = [
    "TagsClient",
    "CandidateFetcherProtocol",
    "DefaultStrategyClient",
    "TaggedCandidate",
    "TagsStageResult",
    "run_tags_stage",
]
