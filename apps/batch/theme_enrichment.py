"""후보 종목의 당일 테마를 LS t1532에서 수집한다.

테마는 후보 attempt의 스냅샷으로 저장되며, 한 종목의 조회 실패가 후보 stage
전체를 실패시키지 않도록 호출별로 격리한다.
"""

from __future__ import annotations

from dataclasses import dataclass
from math import isfinite
from typing import Any, Callable, Protocol, Sequence

from .ls_client import LsResponse


THEME_TR = "t1532"


class ThemeClient(Protocol):
    def request(self, tr_code: str, params: dict[str, Any]) -> LsResponse: ...


@dataclass(frozen=True)
class CandidateTheme:
    theme_code: str
    theme_name: str
    average_change_pct: float

    def as_dict(self) -> dict[str, Any]:
        return {
            "theme_code": self.theme_code,
            "theme_name": self.theme_name,
            "average_change_pct": self.average_change_pct,
        }


@dataclass(frozen=True)
class ThemeEnrichmentResult:
    themes_by_ticker: dict[str, tuple[CandidateTheme, ...]]
    empty_tickers: tuple[str, ...]
    failed_tickers: tuple[str, ...]
    requested_count: int
    success_count: int
    empty_count: int
    failed_count: int


def parse_theme_response(response: LsResponse) -> tuple[CandidateTheme, ...]:
    """t1532 응답에서 유효한 테마를 강세순으로 추출한다."""
    if not response.ok or not isinstance(response.data, dict):
        return ()
    response_code = response.data.get("rsp_cd")
    if response_code is not None and response_code != "00000":
        raise ValueError(f"t1532 returned rsp_cd={response_code!r}")
    raw_rows = response.data.get("t1532OutBlock")
    if not isinstance(raw_rows, (list, tuple)):
        return ()

    themes: dict[str, CandidateTheme] = {}
    for raw in raw_rows:
        if not isinstance(raw, dict):
            raise ValueError("t1532 contained a malformed theme row")
        code_value = raw.get("tmcode")
        name_value = raw.get("tmname")
        if not isinstance(code_value, str) or not isinstance(name_value, str):
            raise ValueError("t1532 theme code/name is not a string")
        code = code_value.strip()
        name = name_value.strip()
        try:
            average_change_pct = float(raw.get("avgdiff"))
        except (TypeError, ValueError):
            raise ValueError("t1532 theme average change is not numeric")
        if not code or not name or not isfinite(average_change_pct):
            raise ValueError("t1532 theme row has an invalid value")
        themes[code] = CandidateTheme(code, name, average_change_pct)
    return tuple(sorted(themes.values(), key=lambda item: (-item.average_change_pct, item.theme_code)))


def enrich_candidate_themes(
    tickers: Sequence[str],
    client: ThemeClient,
    on_progress: Callable[[], None] | None = None,
) -> ThemeEnrichmentResult:
    """후보 티커별 t1532 조회를 수행하고 호출 실패를 후보 단위로 격리한다."""
    themes_by_ticker: dict[str, tuple[CandidateTheme, ...]] = {}
    success_count = 0
    empty_count = 0
    failed_count = 0
    empty_tickers: list[str] = []
    failed_tickers: list[str] = []
    for raw_ticker in tickers:
        ticker = str(raw_ticker).strip()
        if not ticker:
            failed_count += 1
            failed_tickers.append(ticker)
            continue
        try:
            if on_progress is not None:
                on_progress()
            response = client.request(THEME_TR, {"t1532InBlock": {"shcode": ticker}})
            if not response.ok:
                failed_count += 1
                failed_tickers.append(ticker)
                continue
            if not isinstance(response.data, dict):
                failed_count += 1
                failed_tickers.append(ticker)
                continue
            response_code = response.data.get("rsp_cd")
            if response_code is not None and response_code != "00000":
                failed_count += 1
                failed_tickers.append(ticker)
                continue
            raw_rows = response.data.get("t1532OutBlock")
            if not isinstance(raw_rows, (list, tuple)):
                failed_count += 1
                failed_tickers.append(ticker)
                continue
            themes = parse_theme_response(response)
        except Exception:  # noqa: BLE001 - 한 종목 조회 실패는 전체 후보를 막지 않는다.
            failed_count += 1
            failed_tickers.append(ticker)
            continue
        if themes:
            themes_by_ticker[ticker] = themes
            success_count += 1
        else:
            empty_count += 1
            empty_tickers.append(ticker)
    return ThemeEnrichmentResult(
        themes_by_ticker=themes_by_ticker,
        empty_tickers=tuple(empty_tickers),
        failed_tickers=tuple(failed_tickers),
        requested_count=len(tickers),
        success_count=success_count,
        empty_count=empty_count,
        failed_count=failed_count,
    )


__all__ = [
    "CandidateTheme",
    "THEME_TR",
    "ThemeEnrichmentResult",
    "enrich_candidate_themes",
    "parse_theme_response",
]
