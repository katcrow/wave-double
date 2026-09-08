"""Story 4.1: 태깅된 후보의 3일치(D-2/D-1/D0) 가격·수급 수집 stage.

candidates/tags stage 뒤에 배선되어, 태깅된(``candidate_tags.status='active'``)
각 후보에 대해 LS ``t1702``를 후보당 1콜(fromdt=D-2 거래일, todt=D0) 호출하고,
``trading_calendar`` 기준 정확한 3거래일에 매핑해 ``supply_3day``에 저장한다.

한 종목의 실패(비-ok 응답, 예상 3거래일 중 누락된 날짜)가 나머지 후보 처리를
막지 않고 error로 집계한다(``tags_stage.py`` 패턴). 태깅된 후보가 없으면 0행
처리로 success를 기록한다(에러 아님).
"""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from typing import Any, Protocol
from uuid import UUID

from domain.run_state import Stage, StageStatus

from .ls_program_supply_provider import ProgramSupplyBar
from .ls_supply_provider import SupplyBar
from .run_state import RunStateGateway
from .supply_3day_repository import Supply3DayRepositoryProtocol, SupplyRow

_EXPECTED_TRADING_DAY_COUNT = 3


class TaggedCandidateFetcherProtocol(Protocol):
    """``candidate_tags``(active) 기반 태깅된 후보 조회 프로토콜."""

    def fetch(self, run_id: str) -> list[Any]: ...


class CalendarDaysProvider(Protocol):
    """``trading_calendar``에서 최근 개장일을 조회하는 프로토콜."""

    def recent_open_days(self, cutoff: date, count: int) -> list[date]: ...


class SupplyProviderProtocol(Protocol):
    """LS ``t1702`` 조회 프로토콜."""

    def fetch(self, ticker: str, fromdt: date, todt: date) -> list[SupplyBar]: ...


class ProgramSupplyProviderProtocol(Protocol):
    """LS ``t1637`` 일자별 프로그램 순매수 조회 프로토콜."""

    def fetch(self, ticker: str, fromdt: date, todt: date) -> list[ProgramSupplyBar]: ...


@dataclass
class SupplyStageResult:
    """supply stage의 최종 결과."""

    status: str  # "success" | "partial" | "failed"
    result_code: str
    row_count: int = 0
    error_count: int = 0
    candidate_count: int = 0
    run_id: str | None = None
    unprocessed_tickers: tuple[str, ...] = ()


def run_supply_stage(
    gateway: RunStateGateway,
    tagged_fetcher: TaggedCandidateFetcherProtocol,
    calendar_client: CalendarDaysProvider,
    supply_provider: SupplyProviderProtocol,
    program_supply_provider: ProgramSupplyProviderProtocol,
    supply_repo: Supply3DayRepositoryProtocol,
    run_id: UUID | str,
    fence_token: int | str,
    lease_token: UUID | str,
    trading_day: date,
) -> SupplyStageResult:
    """supply stage를 실행한다.

    한 종목의 실패가 나머지 종목 처리를 막지 않는다. error가 하나라도 있으면
    stage 결과를 ``partial``로, 없으면 ``success``로 기록한다. 태깅된 후보 조회 자체의
    실패, 캘린더 조회 실패/부족(3거래일 미확보)은 stage 전체를 명시적으로 ``failed``로
    기록한다(조용한 빈 성공 금지, AD-5).
    """
    run_uuid = run_id if isinstance(run_id, UUID) else UUID(str(run_id))
    lease_uuid = lease_token if isinstance(lease_token, UUID) else UUID(str(lease_token))
    fence_int = int(fence_token)
    run_id_str = str(run_id)

    gateway.write_stage(
        run_uuid, Stage.SUPPLY_3DAY, fence_int, lease_uuid,
        StageStatus.PENDING, StageStatus.RUNNING,
    )

    try:
        candidates = tagged_fetcher.fetch(run_id_str)
    except Exception as exc:
        return _fail(
            gateway, run_uuid, fence_int, lease_uuid,
            "TAGGED_CANDIDATE_FETCH_FAILED", str(exc), run_id_str,
        )

    if not candidates:
        result = {"result_code": "OK", "row_count": 0, "candidate_count": 0}
        gateway.write_stage(
            run_uuid, Stage.SUPPLY_3DAY, fence_int, lease_uuid,
            StageStatus.RUNNING, StageStatus.SUCCESS,
            result=result, unprocessed_count=0,
        )
        return SupplyStageResult("success", "OK", row_count=0, candidate_count=0, run_id=run_id_str)

    try:
        recent_days = calendar_client.recent_open_days(trading_day, _EXPECTED_TRADING_DAY_COUNT)
    except Exception as exc:
        return _fail(
            gateway, run_uuid, fence_int, lease_uuid,
            "CALENDAR_LOOKUP_FAILED", str(exc), run_id_str,
        )

    if (
        len(recent_days) != _EXPECTED_TRADING_DAY_COUNT
        or len(set(recent_days)) != _EXPECTED_TRADING_DAY_COUNT
    ):
        return _fail(
            gateway, run_uuid, fence_int, lease_uuid,
            "CALENDAR_INSUFFICIENT_TRADING_DAYS",
            f"expected {_EXPECTED_TRADING_DAY_COUNT} open trading days on/before {trading_day.isoformat()}, "
            f"got {len(recent_days)}",
            run_id_str,
        )

    # recent_open_days는 내림차순(최신일 먼저)을 반환한다 -- 오름차순으로 재정렬해
    # D-2/D-1/D0에 정확히 대응시킨다.
    ordered_days = sorted(recent_days)
    d_minus_2, d_minus_1, d0 = ordered_days
    slot_by_day = {d_minus_2: "D-2", d_minus_1: "D-1", d0: "D0"}

    all_rows: list[SupplyRow] = []
    error_count = 0
    unprocessed_tickers: list[str] = []
    error_details: list[dict[str, str]] = []

    def record_candidate_error(ticker: str, reason: str) -> None:
        nonlocal error_count
        error_count += 1
        unprocessed_tickers.append(ticker)
        error_details.append({"ticker": ticker, "message": reason})

    for cand in candidates:
        try:
            bars = supply_provider.fetch(cand.ticker, d_minus_2, d0)
        except Exception as exc:
            record_candidate_error(cand.ticker, f"t1702: {exc}")
            continue

        if len(bars) != len({bar.trading_day for bar in bars}) or {
            bar.trading_day for bar in bars
        } != set(ordered_days):
            # 동일 trading_day의 중복 행 -- dict comprehension이 조용히 마지막 행으로
            # 덮어쓰지 않도록 error로 처리한다(조용한 덮어쓰기 금지). t1702도
            # 예상 거래일 외 응답을 저장하지 않는다.
            record_candidate_error(cand.ticker, "t1702: expected exactly three unique trading days")
            continue

        by_day = {bar.trading_day: bar for bar in bars}
        try:
            program_bars = program_supply_provider.fetch(cand.ticker, d_minus_2, d0)
        except Exception as exc:
            record_candidate_error(cand.ticker, f"t1637: {exc}")
            continue

        if len(program_bars) != len({bar.trading_day for bar in program_bars}):
            # 같은 날짜의 프로그램 행도 조용히 덮어쓰지 않는다.
            record_candidate_error(cand.ticker, "t1637: duplicate trading day")
            continue

        program_by_day = {bar.trading_day: bar for bar in program_bars}
        if set(program_by_day) != set(ordered_days):
            # 예상 3거래일 중 일부가 없거나 범위 밖 행만 반환된 경우다.
            record_candidate_error(cand.ticker, "t1637: expected exactly three trading days")
            continue

        candidate_rows: list[SupplyRow] = []
        for day in ordered_days:
            bar = by_day[day]
            candidate_rows.append(
                SupplyRow(
                    candidate_id=cand.candidate_id,
                    attempt_run_id=run_id_str,
                    trading_day=day,
                    slot=slot_by_day[day],
                    close=bar.close,
                    volume=bar.volume,
                    change_pct=bar.change_pct,
                    foreign_net=bar.foreign_net,
                    institution_net=bar.institution_net,
                    individual_net=bar.individual_net,
                    program_net=program_by_day[day].program_net,
                    investor_net_status="confirmed",
                )
            )
        all_rows.extend(candidate_rows)

    try:
        saved_count = supply_repo.upsert_rows(all_rows)
    except Exception as exc:
        result = {
            "result_code": "SUPPLY_PERSIST_FAILED",
            "message": str(exc),
            "row_count": 0,
            "error_count": error_count,
            "candidate_count": len(candidates),
            "unprocessed_tickers": unprocessed_tickers,
            "errors": error_details,
        }
        gateway.write_stage(
            run_uuid, Stage.SUPPLY_3DAY, fence_int, lease_uuid,
            StageStatus.RUNNING, StageStatus.FAILED,
            result=result, unprocessed_count=error_count,
        )
        return SupplyStageResult(
            "failed", "SUPPLY_PERSIST_FAILED",
            row_count=0, error_count=error_count, candidate_count=len(candidates), run_id=run_id_str,
            unprocessed_tickers=tuple(unprocessed_tickers),
        )

    result_common = {
        "row_count": saved_count,
        "candidate_count": len(candidates),
        "unprocessed_tickers": unprocessed_tickers,
        "errors": error_details,
    }

    if error_count > 0:
        result = {"result_code": "PARTIAL_SUPPLY", **result_common}
        gateway.write_stage(
            run_uuid, Stage.SUPPLY_3DAY, fence_int, lease_uuid,
            StageStatus.RUNNING, StageStatus.PARTIAL,
            result=result, unprocessed_count=error_count,
        )
        return SupplyStageResult(
            "partial", "PARTIAL_SUPPLY",
            row_count=saved_count, error_count=error_count, candidate_count=len(candidates), run_id=run_id_str,
            unprocessed_tickers=tuple(unprocessed_tickers),
        )

    result = {"result_code": "OK", **result_common}
    gateway.write_stage(
        run_uuid, Stage.SUPPLY_3DAY, fence_int, lease_uuid,
        StageStatus.RUNNING, StageStatus.SUCCESS,
        result=result, unprocessed_count=0,
    )
    return SupplyStageResult(
        "success", "OK", row_count=saved_count, candidate_count=len(candidates), run_id=run_id_str,
        unprocessed_tickers=(),
    )


def _fail(
    gateway: RunStateGateway,
    run_uuid: UUID,
    fence_int: int,
    lease_uuid: UUID,
    result_code: str,
    message: str,
    run_id_str: str,
) -> SupplyStageResult:
    result = {"result_code": result_code, "message": message}
    gateway.write_stage(
        run_uuid, Stage.SUPPLY_3DAY, fence_int, lease_uuid,
        StageStatus.RUNNING, StageStatus.FAILED,
        result=result,
    )
    return SupplyStageResult("failed", result_code, run_id=run_id_str)


__all__ = [
    "TaggedCandidateFetcherProtocol",
    "CalendarDaysProvider",
    "SupplyProviderProtocol",
    "ProgramSupplyProviderProtocol",
    "SupplyStageResult",
    "run_supply_stage",
]
