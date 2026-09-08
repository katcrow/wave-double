"""t1601/t1631 시장 전체 수급 수집 stage."""

from __future__ import annotations

from dataclasses import dataclass
from datetime import date
from typing import Any, Protocol
from uuid import UUID

from domain.run_state import BatchKind, Stage, StageStatus

from .ls_market_program_supply_provider import MarketProgramSupplyBar
from .ls_market_supply_provider import MarketSupplyBar, MARKETS
from .market_supply_repository import MarketSupplyRepositoryProtocol, MarketSupplyRow
from .run_state import RunStateGateway


class MarketSupplyProviderProtocol(Protocol):
    def fetch(self) -> list[MarketSupplyBar]: ...


class MarketProgramSupplyProviderProtocol(Protocol):
    def fetch(self, market: str) -> MarketProgramSupplyBar: ...


@dataclass(frozen=True)
class MarketSupplyStageResult:
    status: str
    result_code: str
    row_count: int = 0
    error_count: int = 0
    run_id: str | None = None
    failed_markets: tuple[str, ...] = ()


def run_market_supply_stage(
    gateway: RunStateGateway,
    market_supply_provider: MarketSupplyProviderProtocol,
    market_program_supply_provider: MarketProgramSupplyProviderProtocol,
    market_supply_repo: MarketSupplyRepositoryProtocol,
    run_id: UUID | str,
    fence_token: int | str,
    lease_token: UUID | str,
    trading_day: date,
    batch_kind: BatchKind | str = BatchKind.INTRADAY,
) -> MarketSupplyStageResult:
    """두 시장을 독립 처리하고 성공한 시장의 스냅샷만 저장한다."""
    run_uuid = run_id if isinstance(run_id, UUID) else UUID(str(run_id))
    lease_uuid = lease_token if isinstance(lease_token, UUID) else UUID(str(lease_token))
    fence_int = int(fence_token)
    run_id_str = str(run_id)
    kind = batch_kind if isinstance(batch_kind, BatchKind) else BatchKind(batch_kind)
    if kind is BatchKind.PREMARKET:
        raise ValueError("market supply stage does not support premarket batches")

    gateway.write_stage(
        run_uuid, Stage.MARKET_SUPPLY, fence_int, lease_uuid,
        StageStatus.PENDING, StageStatus.RUNNING,
    )

    try:
        investor_bars = market_supply_provider.fetch()
        investor_by_market = _index_investor_bars(investor_bars)
    except Exception as exc:
        return _fail(
            gateway, run_uuid, fence_int, lease_uuid,
            "MARKET_INVESTOR_FETCH_FAILED", str(exc), run_id_str,
            failed_markets=MARKETS,
        )

    rows: list[MarketSupplyRow] = []
    failed_markets: list[str] = []
    errors: list[dict[str, str]] = []
    for market in MARKETS:
        try:
            investor = investor_by_market[market]
            program = market_program_supply_provider.fetch(market)
            if program.market != market:
                raise ValueError(f"program provider returned {program.market} for {market}")
            rows.append(
                MarketSupplyRow(
                    attempt_run_id=run_id_str,
                    market=market,
                    trading_day=trading_day,
                    foreign_net=investor.foreign_net,
                    institution_net=investor.institution_net,
                    individual_net=investor.individual_net,
                    program_net=program.program_net,
                )
            )
        except Exception as exc:
            failed_markets.append(market)
            errors.append({"market": market, "message": str(exc)})

    try:
        saved_count = market_supply_repo.upsert_rows(rows)
    except Exception as exc:
        return _fail(
            gateway, run_uuid, fence_int, lease_uuid,
            "MARKET_SUPPLY_PERSIST_FAILED", str(exc), run_id_str,
            failed_markets=tuple(MARKETS),
        )

    common = {
        "row_count": saved_count,
        "market_count": len(MARKETS),
        "failed_markets": failed_markets,
        "errors": errors,
    }
    if failed_markets:
        result = {"result_code": "PARTIAL_MARKET_SUPPLY", **common}
        gateway.write_stage(
            run_uuid, Stage.MARKET_SUPPLY, fence_int, lease_uuid,
            StageStatus.RUNNING, StageStatus.PARTIAL,
            result=result, unprocessed_count=len(failed_markets),
        )
        return MarketSupplyStageResult(
            "partial", "PARTIAL_MARKET_SUPPLY", saved_count, len(failed_markets),
            run_id_str, tuple(failed_markets),
        )

    result = {"result_code": "OK", **common}
    gateway.write_stage(
        run_uuid, Stage.MARKET_SUPPLY, fence_int, lease_uuid,
        StageStatus.RUNNING, StageStatus.SUCCESS,
        result=result, unprocessed_count=0,
    )
    return MarketSupplyStageResult("success", "OK", saved_count, run_id=run_id_str)


def _index_investor_bars(bars: list[MarketSupplyBar]) -> dict[str, MarketSupplyBar]:
    if not isinstance(bars, list):
        raise ValueError("t1601 provider must return a list")
    by_market: dict[str, MarketSupplyBar] = {}
    for bar in bars:
        if not isinstance(bar, MarketSupplyBar):
            raise ValueError("t1601 provider returned an invalid market row")
        if bar.market in by_market:
            raise ValueError(f"duplicate market row: {bar.market}")
        by_market[bar.market] = bar
    if not by_market:
        raise ValueError("t1601 provider must return at least one market row")
    return by_market


def _fail(
    gateway: RunStateGateway,
    run_uuid: UUID,
    fence_int: int,
    lease_uuid: UUID,
    result_code: str,
    message: str,
    run_id_str: str,
    *,
    failed_markets: tuple[str, ...],
) -> MarketSupplyStageResult:
    result = {
        "result_code": result_code,
        "message": message,
        "failed_markets": list(failed_markets),
    }
    gateway.write_stage(
        run_uuid, Stage.MARKET_SUPPLY, fence_int, lease_uuid,
        StageStatus.RUNNING, StageStatus.FAILED,
        result=result, unprocessed_count=len(failed_markets),
    )
    return MarketSupplyStageResult(
        "failed", result_code, run_id=run_id_str,
        error_count=len(failed_markets), failed_markets=failed_markets,
    )


__all__ = [
    "MarketProgramSupplyProviderProtocol",
    "MarketSupplyProviderProtocol",
    "MarketSupplyStageResult",
    "run_market_supply_stage",
]
