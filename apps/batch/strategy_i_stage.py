"""전략 I(음봉수급쌍끌이) stage 오케스트레이터.

후보 모집단(candidates stage 산출) 한정으로 다음 두 조건을 모두 만족하는 종목을
선별해 ``candidate_tags``에 ``strategy='I'`` 태그로 저장한다.

1. 오늘 캔들이 **양봉이 아니다**(시가 >= 종가 → 음봉 또는 도지).
2. 외국인 순매수(``t1702.tjj0016 > 0``) **그리고** 기관 순매수(``t1702.tjj0018 > 0``)
   — "쌍끌이 매수".

백테스트는 설계 전제로 불가하다(국면 데이터 t1702가 백테스트 데이터셋에 없다).
그러므로 이 stage는 기존 전략 A~H와 달리 ``backtest.strategy_api``를 호출하지 않고,
운영 수동 확인 전용으로 오후 4시~8시 사이의 배치 사이클에서만 실행된다(Neo 요청,
2026-09-16).

한 종목의 실패(API 실패, OHLCV 이력 부족, 응답 malformed 등)가 나머지 종목 처리
를 막지 않고 error로 집계한다(``tags_stage.py``/``supply_stage.py`` 패턴). 후보가
없으면 0행 처리로 success를 기록한다(에러 아님).
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date, datetime, time, timezone
from typing import Any, Protocol
from uuid import UUID

import pandas as pd

from domain.ohlcv_cache import OhlcvCacheStatus
from domain.run_state import Stage, StageStatus

from .candidate_tags_repository import CandidateTag, TagsRepositoryProtocol
from .heartbeat import HeartbeatPolicy
from .ohlcv_cache_loader import OhlcvDbClient
from .run_state import RunStateGateway

_STRATEGY_I = "I"

# 전략 I 실행 가능 시간대(한국): 16:00 이상 ~ 20:00 미만. 장 마감(15:30) 후 수급
# 데이터가 확정되는 16:00부터 확인 대시보드 반영 이전까지 매 사이클 반영한다.
_STRATEGY_I_START_HOUR = 16
_STRATEGY_I_END_HOUR = 20


class StrategyICandidateFetcherProtocol(Protocol):
    """``candidates`` 테이블에서 attempt별 후보 목록을 조회하는 프로토콜."""

    def fetch(self, run_id: str) -> list[Any]: ...


class StrategyISupplyProviderProtocol(Protocol):
    """LS ``t1702`` 조회 프로토콜(전략 I는 D0 1거래일만 필요)."""

    def fetch(self, ticker: str, fromdt: date, todt: date) -> list[Any]: ...


@dataclass(frozen=True)
class StrategyIResult:
    """전략 I stage의 최종 결과."""

    status: str  # "success" | "partial" | "failed"
    result_code: str
    tagged_count: int = 0
    error_count: int = 0
    ineligible_count: int = 0
    candidate_count: int = 0
    persist_failed_count: int = 0
    signal_date: date | None = None
    run_id: str | None = None


def is_strategy_i_window(now_kst: datetime) -> bool:
    """``now_kst``가 전략 I 실행 가능 시간대(16:00 <= 시각 < 20:00)인지 확인한다.

    16:00에 수급 데이터가 확정되고, 20:00 이후에는 다음날 장 전 데이터로 전이하므로
    그 사이 배치 사이클에서만 실행한다(Neo 확인, 2026-09-16).
    """
    return _STRATEGY_I_START_HOUR <= now_kst.hour < _STRATEGY_I_END_HOUR


@dataclass
class _RowState:
    ticker: str
    candidate_id: str
    signal_date: date | None = None
    error: str | None = None
    ineligible: bool = False


def _is_not_bullish(frame: pd.DataFrame) -> bool:
    """오늘(마지막 봉)이 양봉이 아닌지 판정한다.

    양봉은 ``Close > Open``. 음봉(``Close < Open``)과 도지(``Close == Open``) 모두
    "양봉이 아님"으로 처리한다(Neo 확인, 2026-09-16).
    """
    if len(frame) < 1:
        return False
    last = frame.iloc[-1]
    return bool(last["Close"] <= last["Open"])


def _extract_signal_date(frame: pd.DataFrame) -> date | None:
    """마지막 봉의 거래일(DatetimeIndex)을 추출한다(``tags_stage``와 동일 관례)."""
    if len(frame.index) < 1:
        return None
    idx_value = frame.index[-1]
    if hasattr(idx_value, "date"):
        return idx_value.date()
    if isinstance(idx_value, str):
        return date.fromisoformat(idx_value)
    return None


def _has_dual_bull(supply_rows: list[Any]) -> bool:
    """D0 단일 봉에서 외국인·기관 쌍끌이 순매수 여부를 판정한다.

    ``SupplyBar`` 계약(``foreign_net``/``institution_net``)을 기준으로 하며,
    둘 다 0보다 크면 쌍끌이로 판정한다.
    """
    if not supply_rows:
        return False
    last = supply_rows[-1]
    foreign_net = getattr(last, "foreign_net", None)
    institution_net = getattr(last, "institution_net", None)
    if foreign_net is None or institution_net is None:
        return False
    return float(foreign_net) > 0 and float(institution_net) > 0


def run_strategy_i_stage(
    gateway: RunStateGateway,
    candidate_fetcher: StrategyICandidateFetcherProtocol,
    ohlcv_loader: OhlcvDbClient,
    supply_provider: StrategyISupplyProviderProtocol,
    tags_repo: TagsRepositoryProtocol,
    run_id: UUID | str,
    fence_token: int | str,
    lease_token: UUID | str,
    trading_day: date,
    *,
    heartbeat: HeartbeatPolicy | None = None,
) -> StrategyIResult:
    """전략 I stage를 실행한다.

    한 종목의 실패가 나머지 종목 처리를 막지 않는다. error가 하나라도 있으면 stage
    결과를 ``partial``로, 없으면 ``success``로 기록한다. 후보 조회 자체의 실패는 stage
    전체를 명시적으로 ``failed``로 기록한다(조용한 빈 성공 금지, AD-5).
    """
    run_uuid = run_id if isinstance(run_id, UUID) else UUID(str(run_id))
    lease_uuid = lease_token if isinstance(lease_token, UUID) else UUID(str(lease_token))
    fence_int = int(fence_token)
    run_id_str = str(run_id)

    gateway.write_stage(
        run_uuid, Stage.STRATEGY_I, fence_int, lease_uuid,
        StageStatus.PENDING, StageStatus.RUNNING,
    )

    try:
        candidates = candidate_fetcher.fetch(run_id_str)
    except Exception as exc:
        result = {"result_code": "CANDIDATE_FETCH_FAILED", "message": str(exc)}
        gateway.write_stage(
            run_uuid, Stage.STRATEGY_I, fence_int, lease_uuid,
            StageStatus.RUNNING, StageStatus.FAILED,
            result=result,
        )
        return StrategyIResult("failed", "CANDIDATE_FETCH_FAILED", run_id=run_id_str)

    result: StrategyIResult = _compute_and_save(
        gateway, run_uuid, fence_int, lease_uuid, run_id_str,
        candidates, ohlcv_loader, supply_provider, tags_repo, trading_day,
        heartbeat=heartbeat,
    )
    return result


def _compute_and_save(
    gateway: RunStateGateway,
    run_uuid: UUID,
    fence_int: int,
    lease_uuid: UUID,
    run_id_str: str,
    candidates: list[Any],
    ohlcv_loader: OhlcvDbClient,
    supply_provider: StrategyISupplyProviderProtocol,
    tags_repo: TagsRepositoryProtocol,
    trading_day: date,
    *,
    heartbeat: HeartbeatPolicy | None = None,
) -> StrategyIResult:
    """후보별 전략 I 판정과 candidate_tags 저장을 수행한다."""

    all_tags: list[CandidateTag] = []
    error_count = 0
    ineligible_count = 0
    signal_date: date | None = None

    for cand in candidates:
        if heartbeat is not None:
            heartbeat.beat()
        ticker = getattr(cand, "ticker")
        candidate_id = getattr(cand, "candidate_id")

        load_result = ohlcv_loader.load_ohlcv(ticker, trading_day)
        if isinstance(load_result, OhlcvCacheStatus):
            if load_result is OhlcvCacheStatus.INELIGIBLE_INSUFFICIENT_HISTORY:
                ineligible_count += 1
            else:
                error_count += 1
            continue
        if not isinstance(load_result, pd.DataFrame) or len(load_result) < 1:
            error_count += 1
            continue

        try:
            supply_rows = supply_provider.fetch(ticker, trading_day, trading_day)
        except Exception:
            error_count += 1
            continue

        if not _is_not_bullish(load_result):
            continue  # 양봉이면 전략 I 대상 아님
        if not _has_dual_bull(supply_rows):
            continue  # 외국인·기관 쌍끌이가 아니면 대상 아님

        sig_date = _extract_signal_date(load_result)
        if signal_date is None or (sig_date is not None and sig_date > signal_date):
            signal_date = sig_date
        all_tags.append(
            CandidateTag(
                candidate_id=candidate_id,
                strategy=_STRATEGY_I,
                signal_date=sig_date or trading_day,
                attempt_run_id=run_id_str,
                params_meta={"batch_kind": "strategy_i", "rule": "not_bullish_and_dual_supply"},
            )
        )

    save_result = _persist_tags(gateway, run_uuid, fence_int, lease_uuid, run_id_str,
                                all_tags, error_count, ineligible_count,
                                len(candidates), signal_date, tags_repo)
    return save_result


def _persist_tags(
    gateway: RunStateGateway,
    run_uuid: UUID,
    fence_int: int,
    lease_uuid: UUID,
    run_id_str: str,
    all_tags: list[CandidateTag],
    error_count: int,
    ineligible_count: int,
    candidate_count: int,
    signal_date: date | None,
    tags_repo: TagsRepositoryProtocol,
) -> StrategyIResult:
    """candidate_tags 저장과 stage 상태 기록을 수행한다. 실패 격리는 tags_stage 패턴을 따른다."""
    saved_count = 0
    persist_failed_count = 0
    persist_error_message: str | None = None
    if all_tags:
        try:
            saved_count = tags_repo.upsert_tags(all_tags)
        except Exception as exc:
            persist_failed_count = len(all_tags)
            persist_error_message = str(exc)

    result_common = {
        "tagged_count": saved_count,
        "candidate_count": candidate_count,
        "ineligible_count": ineligible_count,
        "error_count": error_count,
        "signal_date": signal_date.isoformat() if signal_date else None,
    }

    if persist_failed_count > 0 and saved_count == 0:
        result = {"result_code": "STRATEGY_I_PERSIST_FAILED", "message": persist_error_message or "all tag upserts failed", **result_common}
        gateway.write_stage(
            run_uuid, Stage.STRATEGY_I, fence_int, lease_uuid,
            StageStatus.RUNNING, StageStatus.FAILED,
            result=result, unprocessed_count=error_count + persist_failed_count,
        )
        return StrategyIResult(
            "failed", "STRATEGY_I_PERSIST_FAILED",
            tagged_count=0, error_count=error_count, ineligible_count=ineligible_count,
            persist_failed_count=persist_failed_count, signal_date=signal_date, run_id=run_id_str,
        )

    if persist_failed_count > 0 and saved_count > 0:
        result = {"result_code": "STRATEGY_I_PERSIST_PARTIAL", "message": persist_error_message or "some tag upserts failed", **result_common}
        gateway.write_stage(
            run_uuid, Stage.STRATEGY_I, fence_int, lease_uuid,
            StageStatus.RUNNING, StageStatus.PARTIAL,
            result=result, unprocessed_count=persist_failed_count,
        )
        return StrategyIResult(
            "partial", "STRATEGY_I_PERSIST_PARTIAL",
            tagged_count=saved_count, error_count=error_count, ineligible_count=ineligible_count,
            persist_failed_count=persist_failed_count, signal_date=signal_date, run_id=run_id_str,
        )

    if error_count > 0:
        result = {"result_code": "PARTIAL_STRATEGY_I", **result_common}
        gateway.write_stage(
            run_uuid, Stage.STRATEGY_I, fence_int, lease_uuid,
            StageStatus.RUNNING, StageStatus.PARTIAL,
            result=result, unprocessed_count=error_count,
        )
        return StrategyIResult(
            "partial", "PARTIAL_STRATEGY_I",
            tagged_count=saved_count, error_count=error_count, ineligible_count=ineligible_count,
            signal_date=signal_date, run_id=run_id_str,
        )

    result = {"result_code": "OK", **result_common}
    gateway.write_stage(
        run_uuid, Stage.STRATEGY_I, fence_int, lease_uuid,
        StageStatus.RUNNING, StageStatus.SUCCESS,
        result=result, unprocessed_count=0,
    )
    return StrategyIResult(
        "success", "OK",
        tagged_count=saved_count, ineligible_count=ineligible_count,
        candidate_count=candidate_count, signal_date=signal_date, run_id=run_id_str,
    )


__all__ = [
    "StrategyICandidateFetcherProtocol",
    "StrategyISupplyProviderProtocol",
    "StrategyIResult",
    "is_strategy_i_window",
    "run_strategy_i_stage",
    "_STRATEGY_I_START_HOUR",
    "_STRATEGY_I_END_HOUR",
]