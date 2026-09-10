"""Story 5.4: 발행된 close 뒤에만 실행하는 독립 옵션 stage."""

from dataclasses import dataclass
from datetime import date
from uuid import UUID, uuid4

from domain.run_state import Stage, StageStatus

from .backtest_universe import BacktestUniverseFixtureError, normalize_ticker
from .bias_metrics import compute_bias_metrics, compute_truncated_signals
from .bias_repository import BiasRepositoryProtocol
from .universe_signal import backfill_universe_ohlcv, compute_universe_signals


@dataclass(frozen=True)
class BiasStageResult:
    status: str
    result_code: str
    event_id: str | None = None
    failure_recorded: bool = True


def _backfill_meta(result):
    return {"requested_count": result.universe_size, "ready_count": result.ready_count,
            "ineligible_count": result.ineligible_count, "error_count": result.error_count,
            "tickers": {t: {"status": r.status.value, "trading_days": r.trading_days}
                        for t, r in sorted(result.results.items())}}


def run_bias_stage(gateway, repository: BiasRepositoryProtocol, ohlcv_provider,
                   ohlcv_repository, ohlcv_loader, run_id, fence_token, lease_token,
                   trading_day: date, truncated_candidates=(), *, strategy_client=None,
                   event_id: UUID | None = None, expected_status=StageStatus.PENDING) -> BiasStageResult:
    """완료 lease heartbeat 없이 계산한다. 재계산은 새 event_id로 append한다."""
    request_id = event_id or uuid4()
    try:
        population = repository.fetch_population(run_id, fence_token, lease_token)
        universe_backfill = backfill_universe_ohlcv(ohlcv_provider, ohlcv_repository, trading_day)
        normalized = []
        for candidate in truncated_candidates:
            try:
                normalized.append(normalize_ticker(candidate.ticker))
            except BacktestUniverseFixtureError:
                pass  # compute_truncated_signals가 원문을 진단 메타에 남긴다.
        truncated_backfill = backfill_universe_ohlcv(
            ohlcv_provider, ohlcv_repository, trading_day, tickers=normalized)
        universe = compute_universe_signals(ohlcv_loader, None, trading_day,
                                            strategy_client=strategy_client)
        truncated = compute_truncated_signals(ohlcv_loader, truncated_candidates, trading_day,
                                              strategy_client=strategy_client)
        metrics = compute_bias_metrics(trading_day, population, universe, truncated=truncated)
        meta = metrics.calculation_meta
        meta["backfill"] = {"universe": _backfill_meta(universe_backfill),
                            "truncated": _backfill_meta(truncated_backfill)}
        # 두 집합이 각각 내부적으로 일정하더라도 서로 다른 확정봉이면 partial이다.
        dates = [r.latest_signal_date for r in (universe, truncated.signal_result)
                 if r.universe_size and r.latest_signal_date is not None]
        meta["cross_population_stale"] = len(set(dates)) > 1
        partial = meta["cross_population_stale"] or any(
            r.error_count or r.ineligible_count for r in (universe_backfill, truncated_backfill))
        partial = partial or any(r.error_count or r.ineligible_count or r.stale_signal_date_tickers
                                for r in (universe, truncated.signal_result))
        partial = partial or bool(meta["unknown_strategy_keys"]) or any(
            meta[section].get(key) for section, keys in (
                ("population", ("unattributed_tickers", "unnormalizable_tickers")),
                ("truncated_attribution", ("unattributed_tickers", "unnormalizable_tickers",
                                           "published_overlap_tickers"))) for key in keys)
        status = "partial" if partial else "success"
        meta["status"] = status
        repository.append(run_id, fence_token, lease_token, request_id, metrics, status)
        return BiasStageResult(status, "BIAS_PARTIAL" if partial else "BIAS_OK", str(request_id))
    except Exception as exc:  # noqa: BLE001 - 옵션 stage 실패를 격리하되 관측 가능하게 남긴다.
        recorded = False
        record_error: Exception | None = None
        try:
            # 성공 경로의 running/완료 전이는 append RPC 트랜잭션에 속한다.
            # 같은 이벤트 재전송 전 running을 쓰면 이미 저장된 이벤트의
            # idempotent 반환 뒤 running 상태만 남을 수 있으므로 피한다.
            gateway.write_stage(run_id, Stage.BIAS, fence_token, lease_token,
                                expected_status, StageStatus.RUNNING)
            gateway.write_stage(run_id, Stage.BIAS, fence_token, lease_token,
                                StageStatus.RUNNING, StageStatus.FAILED,
                                result={"result_code": "BIAS_FAILED", "event_id": str(request_id)})
            recorded = True
        except Exception as record_exc:  # noqa: BLE001 - 실패 기록 실패도 격리·노출한다.
            record_error = record_exc
        failure_detail = f"run_id={run_id} event_id={request_id} failure_recorded={recorded} message={exc}"
        if record_error is not None:
            failure_detail += f" record_error={record_error}"
        print(f"bias_status=failed result_code=BIAS_FAILED {failure_detail}")
        return BiasStageResult("failed", "BIAS_FAILED", str(request_id), recorded)
