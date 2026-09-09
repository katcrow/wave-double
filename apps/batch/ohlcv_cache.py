"""신규 편입 종목의 일봉 이력 초기 적재.

이미 ``daily_ohlcv``에 이력이 있는 티커는 이번 스토리 범위 밖(Story 2.2 증분 갱신)이므로
LS를 호출하지 않는다. ``ls_daily_bar.py``의 단일 콜 요청 구성 스타일과
``supabase_client.py``의 service-role REST 직접 upsert 패턴을 그대로 재사용한다.
"""

from __future__ import annotations

from dataclasses import dataclass, field
from datetime import date, timedelta
from typing import Any, Protocol

import httpx

from domain.ohlcv_cache import MIN_HISTORY_TRADING_DAYS, AdjustmentFlag, OhlcvCacheStatus

from .ls_client import LsResponse
from .heartbeat import HeartbeatPolicy

TR_CODE = "t8410"
QRYCNT = 120
QRYCNT_MAX = 500  # t8410 비압축 상한(OPENAPI는 압축 미제공) -- fetch_range/corporate-action 재구축이 사용.
CORPORATE_ACTION_GAP_THRESHOLD = 0.30


class OhlcvClient(Protocol):
    def request(self, tr_code: str, params: dict[str, Any]) -> LsResponse: ...


@dataclass(frozen=True)
class OhlcvCacheResult:
    ticker: str
    status: OhlcvCacheStatus
    trading_days: int
    message: str = ""


class LsOhlcvCacheProvider:
    """``t8410``(qrycnt=120) 단일 콜로 한 종목의 전체 이력을 조회한다."""

    def __init__(self, client: OhlcvClient) -> None:
        self._client = client

    def fetch_full_history(self, ticker: str, cutoff: date) -> list[dict[str, Any]]:
        response = self._client.request(
            TR_CODE,
            {
                "t8410InBlock": {
                    "shcode": ticker,
                    "gubun": "2",
                    "qrycnt": QRYCNT,
                    "sdate": "",
                    "edate": cutoff.strftime("%Y%m%d"),
                    "cts_date": "",
                    "comp_yn": "N",
                    "sujung": "Y",
                }
            },
        )
        if not response.ok:
            raise RuntimeError(
                f"LS daily bar history fetch failed: {response.result_code} {response.message}".rstrip()
            )
        return [_normalize_row(row) for row in _rows(response.data)]

    def fetch_range(self, ticker: str, start: date | None, end: date) -> list[dict[str, Any]]:
        """``t8410``(qrycnt=500)으로 ``[start, end]`` 구간(양끝 포함)을 조회한다.

        ``start``가 ``None``이면 가용 전체 이력(최대 500거래일)을 조회한다(corporate-action
        재구축 경로). 각 행에 원본 ``pricechk``(없으면 ``None``)를 포함해 반환한다.
        """
        response = self._client.request(
            TR_CODE,
            {
                "t8410InBlock": {
                    "shcode": ticker,
                    "gubun": "2",
                    "qrycnt": QRYCNT_MAX,
                    "sdate": start.strftime("%Y%m%d") if start else "",
                    "edate": end.strftime("%Y%m%d"),
                    "cts_date": "",
                    "comp_yn": "N",
                    "sujung": "Y",
                }
            },
        )
        if not response.ok:
            raise RuntimeError(
                f"LS daily bar range fetch failed: {response.result_code} {response.message}".rstrip()
            )
        return [_normalize_row(row, include_pricechk=True) for row in _rows(response.data)]


def _rows(data: Any) -> list[dict[str, Any]]:
    if isinstance(data, dict):
        rows = data.get("t8410OutBlock1")
        if isinstance(rows, list):
            return rows
    raise RuntimeError("LS daily bar response malformed: missing/non-list t8410OutBlock1")


def _normalize_row(row: dict[str, Any], *, include_pricechk: bool = False) -> dict[str, Any]:
    try:
        raw_date = str(row["date"])
        trading_day = date.fromisoformat(f"{raw_date[:4]}-{raw_date[4:6]}-{raw_date[6:8]}")
    except (KeyError, TypeError, ValueError) as exc:
        raise RuntimeError(f"LS daily bar response malformed: invalid date in row {row!r}") from exc
    normalized = {
        "trading_day": trading_day,
        "open": row.get("open"),
        "high": row.get("high"),
        "low": row.get("low"),
        "close": row.get("close"),
        "volume": row.get("jdiff_vol"),
    }
    if include_pricechk:
        normalized["pricechk"] = row.get("pricechk")
    return normalized


class SupabaseOhlcvCacheRepository:
    """``daily_ohlcv`` 테이블에 대한 ``GET``/``POST {url}/rest/v1/daily_ohlcv`` adapter.

    ``SupabaseCalendarRepository``와 동일하게 attempt-scoped가 아닌 테이블에 대한
    service-role REST 직접 접근만 쓴다.
    """

    def __init__(
        self,
        base_url: str,
        service_role_key: str,
        *,
        http_client: httpx.Client | None = None,
        timeout: float = 30.0,
    ) -> None:
        if not base_url or not service_role_key:
            raise ValueError("base_url and service_role_key must be non-empty")
        self._base_url = base_url.rstrip("/")
        self._key = service_role_key
        self._http = http_client or httpx.Client()
        self._timeout = timeout

    def close(self) -> None:
        self._http.close()

    def __enter__(self) -> "SupabaseOhlcvCacheRepository":
        return self

    def __exit__(self, *_: object) -> None:
        self.close()

    @staticmethod
    def _validate_tickers(tickers: list[str]) -> None:
        for ticker in tickers:
            if not ticker.isalnum():
                raise ValueError(f"invalid ticker for PostgREST in.() filter: {ticker!r}")

    def existing_tickers(self, tickers: list[str]) -> set[str]:
        if not tickers:
            return set()
        self._validate_tickers(tickers)
        response = self._http.get(
            f"{self._base_url}/rest/v1/daily_ohlcv",
            headers=self._headers(),
            params={
                "ticker": f"in.({','.join(tickers)})",
                "select": "ticker",
            },
            timeout=self._timeout,
        )
        response.raise_for_status()
        rows = response.json()
        if not isinstance(rows, list):
            raise RuntimeError("Supabase daily_ohlcv response malformed: expected a list")
        return {row["ticker"] for row in rows}

    def latest_state(self, tickers: list[str]) -> dict[str, "CachedTickerState"]:
        """이미 캐시된 각 티커의 최신 저장 거래일 상태를 조회한다.

        ``existing_tickers``와 동일하게 PostgREST distinct 미지원으로 인해
        ``order=trading_day.desc``로 정렬한 뒤 티커별 첫 등장 행(=최신 거래일)만 취한다
        (완전한 distinct는 아니며, 전체 다운로드보다 나은 절충 -- Story 2.1과 동일한 한계).
        """
        if not tickers:
            return {}
        self._validate_tickers(tickers)
        response = self._http.get(
            f"{self._base_url}/rest/v1/daily_ohlcv",
            headers=self._headers(),
            params={
                "ticker": f"in.({','.join(tickers)})",
                "select": "ticker,trading_day,close,adjustment_version",
                "order": "trading_day.desc",
            },
            timeout=self._timeout,
        )
        response.raise_for_status()
        rows = response.json()
        if not isinstance(rows, list):
            raise RuntimeError("Supabase daily_ohlcv response malformed: expected a list")
        states: dict[str, CachedTickerState] = {}
        for row in rows:
            ticker = row["ticker"]
            if ticker in states:
                continue
            states[ticker] = CachedTickerState(
                last_trading_day=date.fromisoformat(str(row["trading_day"])),
                last_close=row["close"],
                adjustment_version=row["adjustment_version"],
            )
        return states

    def upsert_rows(
        self, ticker: str, rows: list[dict[str, Any]], *, adjustment_version: int = 1
    ) -> None:
        payload = [
            {
                "ticker": ticker,
                "trading_day": row["trading_day"].isoformat() if hasattr(row["trading_day"], "isoformat") else row["trading_day"],
                "open": row["open"],
                "high": row["high"],
                "low": row["low"],
                "close": row["close"],
                "volume": row["volume"],
                "adjusted": True,
                "adjustment_version": adjustment_version,
                "pricechk": row.get("pricechk"),
            }
            for row in rows
        ]
        response = self._http.post(
            f"{self._base_url}/rest/v1/daily_ohlcv",
            headers={**self._headers(), "Prefer": "resolution=merge-duplicates"},
            params={"on_conflict": "ticker,trading_day"},
            json=payload,
            timeout=self._timeout,
        )
        response.raise_for_status()

    def _headers(self) -> dict[str, str]:
        return {
            "content-type": "application/json",
            "apikey": self._key,
            "authorization": f"Bearer {self._key}",
        }


def initialize_new_ticker_history(
    candidates: list[str],
    provider: LsOhlcvCacheProvider,
    repository: SupabaseOhlcvCacheRepository,
    cutoff: date,
    *,
    heartbeat: HeartbeatPolicy | None = None,
) -> dict[str, OhlcvCacheResult]:
    """이미 이력이 있는 티커는 건너뛰고, 신규 편입 종목만 전체 이력을 적재한다.

    한 종목의 실패가 나머지 종목 처리를 막지 않는다(부분 성공 허용). 신규 티커 호출은
    순차 실행이며, ``LsClient``의 TR별 token bucket이 이미 1건/초를 강제하므로
    별도의 처리량 제한 로직을 추가하지 않는다(NFR-3). ``heartbeat``가 주어지면 종목
    하나를 처리할 때마다 ``beat()``를 호출해 lease를 연장한다(epic-2-retro item-11).
    """
    deduped_candidates = list(dict.fromkeys(candidates))

    try:
        existing = repository.existing_tickers(deduped_candidates)
    except Exception as exc:
        return {
            ticker: OhlcvCacheResult(ticker, OhlcvCacheStatus.ERROR, 0, str(exc))
            for ticker in deduped_candidates
        }

    new_tickers = [ticker for ticker in deduped_candidates if ticker not in existing]

    results: dict[str, OhlcvCacheResult] = {}
    for ticker in new_tickers:
        if heartbeat is not None:
            heartbeat.beat()
        try:
            rows = provider.fetch_full_history(ticker, cutoff)
        except Exception as exc:
            results[ticker] = OhlcvCacheResult(ticker, OhlcvCacheStatus.ERROR, 0, str(exc))
            continue

        if len(rows) < MIN_HISTORY_TRADING_DAYS:
            results[ticker] = OhlcvCacheResult(
                ticker, OhlcvCacheStatus.INELIGIBLE_INSUFFICIENT_HISTORY, len(rows)
            )
            continue

        try:
            repository.upsert_rows(ticker, rows)
        except Exception as exc:
            results[ticker] = OhlcvCacheResult(ticker, OhlcvCacheStatus.ERROR, len(rows), str(exc))
            continue

        results[ticker] = OhlcvCacheResult(ticker, OhlcvCacheStatus.READY, len(rows))

    return results


@dataclass(frozen=True)
class CachedTickerState:
    last_trading_day: date
    last_close: float
    adjustment_version: int


@dataclass
class IncrementalUpdateResult:
    results: dict[str, OhlcvCacheResult]
    adjustment_flags: list[AdjustmentFlag] = field(default_factory=list)


def _is_pricechk_flagged(pricechk: Any) -> bool:
    return pricechk is not None and pricechk != 0


def update_existing_ticker_history(
    tickers: list[str],
    provider: LsOhlcvCacheProvider,
    repository: SupabaseOhlcvCacheRepository,
    cutoff: date,
    *,
    heartbeat: HeartbeatPolicy | None = None,
) -> IncrementalUpdateResult:
    """이미 캐시된 각 종목의 마지막 저장 거래일 다음부터 cutoff까지만 증분 조회한다.

    ``latest_state``에 없는 티커(이력 없음)는 이 함수의 관심사가 아니므로 결과에서
    제외한다(신규 편입은 ``initialize_new_ticker_history``의 몫). ``pricechk`` 또는
    ±30% 초과 갭이 관측된 거래일은 ``AdjustmentFlag``로 수집해 반환한다(Story 3.5가
    재조회 없이 소비). corporate-action(신규 행 중 하나 이상 ``pricechk`` 관측)이 감지되면
    가용 전체 이력(최대 500거래일)을 재조회·재저장하고 ``adjustment_version``을 1
    증가시킨다. 한 종목의 실패가 나머지 종목 처리를 막지 않는다(부분 성공 허용).
    ``heartbeat``가 주어지면 종목 하나를 처리할 때마다 ``beat()``를 호출해 lease를
    연장한다(epic-2-retro item-11).
    """
    deduped_tickers = list(dict.fromkeys(tickers))

    try:
        states = repository.latest_state(deduped_tickers)
    except Exception as exc:
        return IncrementalUpdateResult(
            results={
                ticker: OhlcvCacheResult(ticker, OhlcvCacheStatus.ERROR, 0, str(exc))
                for ticker in deduped_tickers
            },
            adjustment_flags=[],
        )

    results: dict[str, OhlcvCacheResult] = {}
    adjustment_flags: list[AdjustmentFlag] = []

    for ticker in deduped_tickers:
        state = states.get(ticker)
        if state is None:
            continue
        if heartbeat is not None:
            heartbeat.beat()

        if state.last_trading_day >= cutoff:
            results[ticker] = OhlcvCacheResult(ticker, OhlcvCacheStatus.READY, 0)
            continue

        try:
            new_rows = provider.fetch_range(ticker, state.last_trading_day + timedelta(days=1), cutoff)
        except Exception as exc:
            results[ticker] = OhlcvCacheResult(ticker, OhlcvCacheStatus.ERROR, 0, str(exc))
            continue

        if not new_rows:
            results[ticker] = OhlcvCacheResult(ticker, OhlcvCacheStatus.READY, 0)
            continue

        corporate_action = False
        prev_close = state.last_close
        ticker_flags: list[AdjustmentFlag] = []
        try:
            for row in new_rows:
                pricechk_flagged = _is_pricechk_flagged(row.get("pricechk"))
                if pricechk_flagged:
                    corporate_action = True
                gap_pct = (row["close"] - prev_close) / prev_close if prev_close else 0.0
                if pricechk_flagged or abs(gap_pct) > CORPORATE_ACTION_GAP_THRESHOLD:
                    ticker_flags.append(
                        AdjustmentFlag(ticker, row["trading_day"], pricechk_flagged, gap_pct)
                    )
                prev_close = row["close"]
        except Exception as exc:
            results[ticker] = OhlcvCacheResult(ticker, OhlcvCacheStatus.ERROR, 0, str(exc))
            continue

        if corporate_action:
            try:
                rebuilt_rows = provider.fetch_range(ticker, None, cutoff)
            except Exception as exc:
                results[ticker] = OhlcvCacheResult(ticker, OhlcvCacheStatus.ERROR, 0, str(exc))
                continue
            try:
                repository.upsert_rows(
                    ticker, rebuilt_rows, adjustment_version=state.adjustment_version + 1
                )
            except Exception as exc:
                results[ticker] = OhlcvCacheResult(
                    ticker, OhlcvCacheStatus.ERROR, len(rebuilt_rows), str(exc)
                )
                continue
            results[ticker] = OhlcvCacheResult(ticker, OhlcvCacheStatus.READY, len(rebuilt_rows))
            adjustment_flags.extend(ticker_flags)
            continue

        try:
            repository.upsert_rows(ticker, new_rows, adjustment_version=state.adjustment_version)
        except Exception as exc:
            results[ticker] = OhlcvCacheResult(
                ticker, OhlcvCacheStatus.ERROR, len(new_rows), str(exc)
            )
            continue
        results[ticker] = OhlcvCacheResult(ticker, OhlcvCacheStatus.READY, len(new_rows))
        adjustment_flags.extend(ticker_flags)

    return IncrementalUpdateResult(results=results, adjustment_flags=adjustment_flags)


__all__ = [
    "LsOhlcvCacheProvider",
    "SupabaseOhlcvCacheRepository",
    "OhlcvCacheResult",
    "CachedTickerState",
    "IncrementalUpdateResult",
    "initialize_new_ticker_history",
    "update_existing_ticker_history",
]
