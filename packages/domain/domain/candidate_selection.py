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


@dataclass(frozen=True)
class SelectedCandidate:
    ticker: str
    name: str | None
    trading_value: float

    def as_dict(self) -> dict[str, Any]:
        return {"ticker": self.ticker, "name": self.name, "trading_value": self.trading_value}


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


def _input_hash(records: list[Any]) -> str:
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


def select_candidates(data: Iterable[Any] | Mapping[str, Any] | None, *, limit: int = MAX_CANDIDATES) -> CandidateSelection:
    """유효한 후보만 거래대금 DESC, ticker ASC로 정렬하고 상한을 적용한다."""
    if limit <= 0:
        raise ValueError("limit must be positive")
    raw = _records(data)
    valid: list[SelectedCandidate] = []
    excluded = 0
    for item in raw:
        if not isinstance(item, Mapping):
            excluded += 1
            continue
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
            excluded += 1
            continue
        name_value = _first(item, _NAME_KEYS)
        name = str(name_value).strip() if name_value is not None and str(name_value).strip() else None
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


__all__ = ["MAX_CANDIDATES", "CandidateSelection", "SelectedCandidate", "select_candidates"]
