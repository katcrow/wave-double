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

from domain.run_state import BatchKind, Stage, StageStatus

from .ls_program_supply_provider import ProgramSupplyBar
from .ls_supply_provider import SupplyBar
from .run_state import RunStateGateway
from .supply_3day_repository import Supply3DayRepositoryProtocol, SupplyRow

_EXPECTED_TRADING_DAY_COUNT = 3
_SEMANTIC_RETRY_COUNT = 1


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
    batch_kind: BatchKind | str = BatchKind.INTRADAY,
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
    kind = batch_kind if isinstance(batch_kind, BatchKind) else BatchKind(batch_kind)
    if kind is BatchKind.PREMARKET:
        raise ValueError("supply stage does not support premarket batches")

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

        try:
            by_day = _index_bars(bars, ordered_days, "t1702")
        except ValueError:
            record_candidate_error(cand.ticker, "t1702: expected exactly three unique trading days")
            continue

        try:
            program_bars = program_supply_provider.fetch(cand.ticker, d_minus_2, d0)
        except Exception as exc:
            _append_missing_rows(all_rows, cand, run_id_str, ordered_days, slot_by_day, by_day)
            record_candidate_error(cand.ticker, f"t1637: {exc}")
            continue

        try:
            program_by_day = _index_program_bars(program_bars, ordered_days)
        except ValueError as exc:
            _append_missing_rows(all_rows, cand, run_id_str, ordered_days, slot_by_day, by_day)
            record_candidate_error(cand.ticker, f"t1637: {exc}")
            continue

        d0_bar = by_day[d0]
        d0_program = program_by_day[d0]
        status = "confirmed"
        if _all_zero(
            d0_bar.foreign_net,
            d0_bar.institution_net,
            d0_bar.individual_net,
            d0_program.program_net,
        ):
            try:
                retry_bars = _fetch_semantic_retry(
                    supply_provider, cand.ticker, d_minus_2, d0, _SEMANTIC_RETRY_COUNT,
                )
                retry_program_bars = _fetch_semantic_retry(
                    program_supply_provider, cand.ticker, d_minus_2, d0, _SEMANTIC_RETRY_COUNT,
                )
                by_day = _index_bars(retry_bars, ordered_days, "t1702")
                program_by_day = _index_program_bars(retry_program_bars, ordered_days)
            except Exception as exc:
                # 가격은 첫 t1702 응답에서 확보했으므로 세 슬롯은 보존하되,
                # 재시도로도 투자자 수급 확정에 실패한 사실은 missing으로 표시한다.
                _append_missing_rows(all_rows, cand, run_id_str, ordered_days, slot_by_day, by_day)
                record_candidate_error(cand.ticker, f"semantic retry: {exc}")
                continue

            d0_bar = by_day[d0]
            d0_program = program_by_day[d0]
            if _all_zero(
                d0_bar.foreign_net,
                d0_bar.institution_net,
                d0_bar.individual_net,
                d0_program.program_net,
            ):
                if kind is BatchKind.INTRADAY:
                    status = "pending"

        try:
            all_rows.extend(
                _build_candidate_rows(
                    cand,
                    run_id_str,
                    ordered_days,
                    slot_by_day,
                    by_day,
                    program_by_day,
                    investor_net_status=status,
                )
            )
        except (TypeError, ValueError) as exc:
            record_candidate_error(cand.ticker, f"supply invariant: {exc}")

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


def _index_bars(bars: list[Any], ordered_days: list[date], source: str) -> dict[date, Any]:
    """응답 날짜를 엄격히 검증해 조용한 중복/누락/범위 밖 저장을 막는다."""
    if len(bars) != len({bar.trading_day for bar in bars}):
        raise ValueError(f"{source}: duplicate trading day")
    by_day = {bar.trading_day: bar for bar in bars}
    if set(by_day) != set(ordered_days):
        raise ValueError(f"{source}: expected exactly three unique trading days")
    return by_day


def _index_program_bars(
    bars: list[ProgramSupplyBar], ordered_days: list[date],
) -> dict[date, ProgramSupplyBar]:
    """t1637은 그 날 프로그램 순매수 체결이 없으면 행 자체를 생략한다 -- 누락된
    거래일은 실제 데이터 부재이므로 순매수 0으로 채운다. 중복/범위 밖 거래일은
    여전히 응답 손상으로 간주해 거부한다(조용한 덮어쓰기 금지)."""
    if len(bars) != len({bar.trading_day for bar in bars}):
        raise ValueError("t1637: duplicate trading day")
    by_day = {bar.trading_day: bar for bar in bars}
    unexpected = set(by_day) - set(ordered_days)
    if unexpected:
        raise ValueError(f"t1637: unexpected trading day outside requested window: {sorted(unexpected)}")
    for day in ordered_days:
        by_day.setdefault(day, ProgramSupplyBar(trading_day=day, program_net=0.0))
    return by_day


def _fetch_semantic_retry(provider: Any, ticker: str, fromdt: date, todt: date, retries: int) -> list[Any]:
    """의미적으로 의심스러운 all-zero 응답에 한정된 bounded retry."""
    if retries != 1:
        raise ValueError("semantic retry budget must remain one bounded retry")
    return provider.fetch(ticker, fromdt, todt)


def _all_zero(*values: float | None) -> bool:
    return all(value == 0 for value in values)


def _build_candidate_rows(
    candidate: Any,
    run_id: str,
    ordered_days: list[date],
    slot_by_day: dict[date, str],
    by_day: dict[date, SupplyBar],
    program_by_day: dict[date, ProgramSupplyBar],
    *,
    investor_net_status: str,
) -> list[SupplyRow]:
    rows: list[SupplyRow] = []
    for day in ordered_days:
        bar = by_day[day]
        is_pending = investor_net_status == "pending" and day == ordered_days[-1]
        rows.append(
            SupplyRow(
                candidate_id=candidate.candidate_id,
                attempt_run_id=run_id,
                trading_day=day,
                slot=slot_by_day[day],
                close=bar.close,
                volume=bar.volume,
                change_pct=bar.change_pct,
                foreign_net=None if is_pending else bar.foreign_net,
                institution_net=None if is_pending else bar.institution_net,
                individual_net=None if is_pending else bar.individual_net,
                program_net=None if is_pending else program_by_day[day].program_net,
                investor_net_status="pending" if is_pending else "confirmed",
            )
        )
    return rows


def _append_missing_rows(
    all_rows: list[SupplyRow],
    candidate: Any,
    run_id: str,
    ordered_days: list[date],
    slot_by_day: dict[date, str],
    by_day: dict[date, SupplyBar],
) -> None:
    for day in ordered_days:
        bar = by_day[day]
        all_rows.append(
            SupplyRow(
                candidate_id=candidate.candidate_id,
                attempt_run_id=run_id,
                trading_day=day,
                slot=slot_by_day[day],
                close=bar.close,
                volume=bar.volume,
                change_pct=bar.change_pct,
                foreign_net=None,
                institution_net=None,
                individual_net=None,
                program_net=None,
                investor_net_status="missing",
            )
        )
