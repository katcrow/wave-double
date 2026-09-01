"""조건검색 후보를 외부 의존성 없이 재현 가능하게 정규화·선별한다."""

from __future__ import annotations

import hashlib
import json
import math
from dataclasses import dataclass
from typing import Any, Iterable, Mapping


MAX_CANDIDATES = 150
_TICKER_KEYS = ("ticker", "symbol", "code", "종목코드", "shcode")
_NAME_KEYS = ("name", "종목명", "hname")
_VALUE_KEYS = ("trading_value", "trade_value", "거래대금", "거래대금액", "value")
_PRICE_KEYS = ("price", "현재가")
_VOLUME_KEYS = ("volume", "거래량")

# 스키마 계약(candidate_source_contrib.source)이 지정한 원천 우선순위.
# t1852는 등록/ack 전용 TR이라 실제로 후보를 내지 못하지만, 우선순위 상수에는 유지한다(AD-21 계약).
SOURCE_PRIORITY: tuple[str, ...] = ("t1859", "t1852", "t1856")


@dataclass(frozen=True)
class SourceContribution:
    source: str
    weight: float

    def as_dict(self) -> dict[str, Any]:
        return {"source": self.source, "weight": self.weight}


@dataclass(frozen=True)
class SelectedCandidate:
    ticker: str
    name: str | None
    trading_value: float
    sources: tuple[SourceContribution, ...] = ()

    def as_dict(self) -> dict[str, Any]:
        payload: dict[str, Any] = {"ticker": self.ticker, "name": self.name, "trading_value": self.trading_value}
        if self.sources:
            payload["sources"] = [source.as_dict() for source in self.sources]
        return payload


@dataclass(frozen=True)
class CandidateSelection:
    candidates: tuple[SelectedCandidate, ...]
    truncated_candidates: tuple[SelectedCandidate, ...]
    selection_input_hash: str
    original_count: int
    excluded_count: int
    truncated_count: int

    @property
    def metadata(self) -> dict[str, Any]:
        return {
            "selection_input_hash": self.selection_input_hash,
            "original_count": self.original_count,
            "candidate_count": len(self.candidates),
            "excluded_count": self.excluded_count,
            "truncated_count": self.truncated_count,
        }

    @property
    def all_candidates(self) -> tuple[SelectedCandidate, ...]:
        return self.candidates + self.truncated_candidates


def _first(record: Mapping[str, Any], keys: tuple[str, ...]) -> Any:
    for key in keys:
        if key in record:
            return record[key]
    return None


def _canonical(value: Any) -> Any:
    """JSON hash가 입력 순서와 Python의 비표준 NaN 표현에 흔들리지 않게 한다."""
    if isinstance(value, Mapping):
        return {str(k): _canonical(value[k]) for k in sorted(value, key=lambda item: str(item))}
    if isinstance(value, (list, tuple)):
        items = [_canonical(item) for item in value]
        return sorted(items, key=lambda item: json.dumps(item, ensure_ascii=False, sort_keys=True, separators=(",", ":")))
    if isinstance(value, float) and not math.isfinite(value):
        return str(value).lower()
    if isinstance(value, (str, int, float, bool)) or value is None:
        return value
    return str(value)


def _input_hash(records: Any) -> str:
    payload = json.dumps(_canonical(records), ensure_ascii=False, sort_keys=True, separators=(",", ":"), allow_nan=False)
    return hashlib.sha256(payload.encode("utf-8")).hexdigest()


def _records(data: Iterable[Any] | Mapping[str, Any] | None) -> list[Any]:
    if data is None:
        return []
    if isinstance(data, Mapping):
        for key in ("candidates", "results", "items", "data", "종목", "output"):
            if key in data:
                value = data[key]
                return list(value) if isinstance(value, (list, tuple)) else []
        return [data]
    return list(data)


def _parse_item(item: Any) -> tuple[str, float, str | None] | None:
    """레코드 하나를 (ticker, trading_value, name)으로 정규화한다. 무효하면 None."""
    if not isinstance(item, Mapping):
        return None
    ticker_value = _first(item, _TICKER_KEYS)
    value = _first(item, _VALUE_KEYS)
    if value is None:
        price = _first(item, _PRICE_KEYS)
        volume = _first(item, _VOLUME_KEYS)
        if price is not None and volume is not None:
            try:
                value = float(price) * float(volume)
            except (TypeError, ValueError):
                value = None
    try:
        ticker = str(ticker_value).strip() if ticker_value is not None else ""
        trading_value = float(value)
    except (TypeError, ValueError):
        ticker, trading_value = "", float("nan")
    if not ticker or not math.isfinite(trading_value):
        return None
    name_value = _first(item, _NAME_KEYS)
    name = str(name_value).strip() if name_value is not None and str(name_value).strip() else None
    return ticker, trading_value, name


def select_candidates(data: Iterable[Any] | Mapping[str, Any] | None, *, limit: int = MAX_CANDIDATES) -> CandidateSelection:
    """유효한 후보만 거래대금 DESC, ticker ASC로 정렬하고 상한을 적용한다."""
    if limit <= 0:
        raise ValueError("limit must be positive")
    raw = _records(data)
    valid: list[SelectedCandidate] = []
    excluded = 0
    for item in raw:
        parsed = _parse_item(item)
        if parsed is None:
            excluded += 1
            continue
        ticker, trading_value, name = parsed
        valid.append(SelectedCandidate(ticker=ticker, name=name, trading_value=trading_value))
    valid.sort(key=lambda candidate: (-candidate.trading_value, candidate.ticker))
    unique: list[SelectedCandidate] = []
    seen: set[str] = set()
    for candidate in valid:
        if candidate.ticker in seen:
            excluded += 1
            continue
        seen.add(candidate.ticker)
        unique.append(candidate)
    selected = tuple(unique[:limit])
    truncated_candidates = tuple(unique[limit:])
    truncated = len(truncated_candidates)
    return CandidateSelection(selected, truncated_candidates, _input_hash(raw), len(raw), excluded, truncated)


def merge_candidate_sources(
    sources_data: Mapping[str, Iterable[Any] | Mapping[str, Any] | None],
    *,
    limit: int = MAX_CANDIDATES,
    priority: tuple[str, ...] = SOURCE_PRIORITY,
) -> CandidateSelection:
    """source별 원시 응답을 종목코드 기준으로 병합한다.

    각 종목의 저장값은 유효 거래대금 중 최댓값이며, 그 최댓값을 낸 source(들)만
    ``candidate_source_contrib`` 기여자로 채택한다(동률이면 균등 weight, 합계는 항상 1).
    primary source는 기여자 중 ``priority`` 순위가 가장 높은 source다. 무효값을 낸
    source는 해당 종목에 기여하지 않되, 다른 source가 유효하면 종목 자체는 제외되지 않는다.
    """
    if limit <= 0:
        raise ValueError("limit must be positive")

    original_count = 0
    excluded = 0
    # ticker -> {source: (value, name)}
    per_ticker: dict[str, dict[str, tuple[float, str | None]]] = {}
    combined_raw: dict[str, list[Any]] = {}

    for source, data in sources_data.items():
        raw = _records(data)
        combined_raw[source] = raw
        original_count += len(raw)
        best_in_source: dict[str, tuple[float, str | None]] = {}
        for item in raw:
            parsed = _parse_item(item)
            if parsed is None:
                excluded += 1
                continue
            ticker, trading_value, name = parsed
            current = best_in_source.get(ticker)
            if current is None:
                best_in_source[ticker] = (trading_value, name)
            elif trading_value > current[0]:
                excluded += 1
                best_in_source[ticker] = (trading_value, name)
            else:
                excluded += 1
        for ticker, (value, name) in best_in_source.items():
            per_ticker.setdefault(ticker, {})[source] = (value, name)

    def _priority_rank(source: str) -> int:
        return priority.index(source) if source in priority else len(priority)

    merged: list[SelectedCandidate] = []
    for ticker, by_source in per_ticker.items():
        max_value = max(value for value, _ in by_source.values())
        contributing = sorted(
            (source for source, (value, _) in by_source.items() if value == max_value),
            key=_priority_rank,
        )
        excluded += len(by_source) - len(contributing)
        weight = 1.0 / len(contributing)
        primary = contributing[0]
        name = by_source[primary][1]
        if name is None:
            name = next((candidate_name for _, candidate_name in by_source.values() if candidate_name), None)
        sources = tuple(SourceContribution(source=source, weight=weight) for source in contributing)
        merged.append(SelectedCandidate(ticker=ticker, name=name, trading_value=max_value, sources=sources))

    merged.sort(key=lambda candidate: (-candidate.trading_value, candidate.ticker))
    selected = tuple(merged[:limit])
    truncated_candidates = tuple(merged[limit:])
    truncated = len(truncated_candidates)
    return CandidateSelection(selected, truncated_candidates, _input_hash(combined_raw), original_count, excluded, truncated)


__all__ = [
    "MAX_CANDIDATES",
    "SOURCE_PRIORITY",
    "CandidateSelection",
    "SelectedCandidate",
    "SourceContribution",
    "select_candidates",
    "merge_candidate_sources",
]
