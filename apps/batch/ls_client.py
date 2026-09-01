"""LS Open API의 공통 REST 경계.

TR별 rate limit과 재시도 정책을 한 곳에서 소유한다. 이 모듈 밖으로는
LS 응답 형식이나 HTTPX 예외를 노출하지 않는다.
"""

from __future__ import annotations

import time
from dataclasses import dataclass
from datetime import datetime, timezone
from email.utils import parsedate_to_datetime
from math import isfinite
from threading import Lock
from typing import Any, Callable, Protocol

import httpx


class TokenProvider(Protocol):
    def get_token(self) -> str: ...


class ConfigurationError(ValueError):
    """지원하지 않는 클라이언트 구성."""


@dataclass(frozen=True)
class LsClientConfig:
    endpoint: str = "https://openapi.ls-sec.co.kr:8080"
    personal_requests_per_second: float = 1.0
    max_retries: int = 3
    default_backoff_seconds: float = 1.0
    max_retry_after_seconds: float = 30.0
    budget_seconds: float = 30.0
    allow_cross_tr_parallel: bool = False
    mac_address: str | None = None

    def __post_init__(self) -> None:
        numeric_values = (self.personal_requests_per_second, self.default_backoff_seconds, self.max_retry_after_seconds, self.budget_seconds)
        if not all(isfinite(value) for value in numeric_values):
            raise ConfigurationError("rate, backoff, and budget values must be finite")
        if self.personal_requests_per_second <= 0:
            raise ConfigurationError("personal_requests_per_second must be positive")
        if self.max_retries < 0:
            raise ConfigurationError("max_retries must be non-negative")
        if self.default_backoff_seconds < 0 or self.max_retry_after_seconds < 0:
            raise ConfigurationError("backoff limits must be non-negative")
        if self.budget_seconds <= 0:
            raise ConfigurationError("budget_seconds must be positive")
        if self.allow_cross_tr_parallel:
            raise ConfigurationError("cross-TR parallelization is disabled until measured")


@dataclass(frozen=True)
class LsResponse:
    """호출 결과. 실패도 예외 대신 이 구조로 반환한다."""

    data: Any = None
    result_code: str = "OK"
    message: str = ""
    retryable: bool = False
    unprocessed_count: int = 0
    status_code: int | None = None

    @property
    def ok(self) -> bool:
        return self.result_code == "OK"


class _TokenBucket:
    """용량 1, TR별 refill rate를 가진 동시성 안전 token bucket."""

    def __init__(self, now: float, refill_rate: float) -> None:
        self.tokens = 1.0
        self.last_refill = now
        self.refill_rate = refill_rate
        self.lock = Lock()

    def reserve(self, now: float) -> float:
        elapsed = max(0.0, now - self.last_refill)
        self.tokens = min(1.0, self.tokens + elapsed * self.refill_rate)
        self.last_refill = now
        if self.tokens >= 1.0:
            self.tokens -= 1.0
            return 0.0
        wait = (1.0 - self.tokens) / self.refill_rate
        # 잠든 뒤 쓸 토큰을 지금 예약해야 뒤따른 caller가 같은 슬롯을 쓰지 않는다.
        self.tokens = 0.0
        self.last_refill = now + wait
        return wait


def _now_seconds(clock: Callable[[], float | datetime]) -> float:
    value = clock()
    if isinstance(value, datetime):
        return value.timestamp()
    return float(value)


def _as_utc_datetime(value: float | datetime) -> datetime:
    if isinstance(value, datetime):
        return value if value.tzinfo else value.replace(tzinfo=timezone.utc)
    return datetime.fromtimestamp(value, tz=timezone.utc)


class LsClient:
    """모든 LS REST TR이 공유하는 순차 호출 클라이언트."""

    def __init__(
        self,
        token_provider: TokenProvider | Callable[[], str],
        *,
        config: LsClientConfig | None = None,
        http_client: httpx.Client | None = None,
        clock: Callable[[], float | datetime] | None = None,
        sleeper: Callable[[float], None] | None = None,
        mac_address: str | None = None,
    ) -> None:
        self.config = config or LsClientConfig()
        self._token_provider = token_provider
        self._http = http_client or httpx.Client()
        # HTTP-date 해석과 budget을 같은 시계로 다루기 위해 epoch seconds를 쓴다.
        self._clock = clock or time.time
        self._sleeper = sleeper or time.sleep
        self._mac_address = mac_address if mac_address is not None else self.config.mac_address
        self._limiters: dict[str, _TokenBucket] = {}
        self._limiters_lock = Lock()
        # LS 계정의 TR 간 한도 공유 여부가 실측되기 전에는 HTTP 경계를 직렬화한다.
        self._request_lock = Lock()

    def close(self) -> None:
        self._http.close()

    def __enter__(self) -> "LsClient":
        return self

    def __exit__(self, *_: object) -> None:
        self.close()

    def request(self, tr_code: str, params: dict[str, Any], *, path: str | None = None) -> LsResponse:
        """임의의 TR 코드와 JSON 파라미터를 공통 endpoint로 호출한다."""
        if not isinstance(tr_code, str) or not tr_code.strip():
            raise ValueError("tr_code must be a non-empty string")
        if not isinstance(params, dict):
            raise TypeError("params must be a dictionary")

        with self._request_lock:
            return self._request_serial(tr_code, params, path=path)

    def _request_serial(self, tr_code: str, params: dict[str, Any], *, path: str | None) -> LsResponse:

        started = _now_seconds(self._clock)
        attempts = 0
        while True:
            if not self._reserve_token(tr_code, started):
                return self._budget_result()

            try:
                remaining_budget = self.config.budget_seconds - (_now_seconds(self._clock) - started)
                if remaining_budget <= 0:
                    return self._budget_result()
                response = self._http.post(
                    self._url(path),
                    headers=self._headers(tr_code),
                    json=params,
                    timeout=remaining_budget,
                )
            except httpx.HTTPError as exc:
                if attempts >= self.config.max_retries:
                    return self._retry_exhausted("LS transport request failed")
                delay = self._default_backoff()
                if not self._wait_within_budget(delay, started):
                    return self._budget_result()
                self._sleeper(delay)
                attempts += 1
                continue

            if response.status_code == 429 or 500 <= response.status_code <= 599:
                if attempts >= self.config.max_retries:
                    return self._retry_exhausted(f"LS returned HTTP {response.status_code}", response.status_code)
                delay = self._retry_after(response.headers.get("Retry-After"))
                if not self._wait_within_budget(delay, started):
                    return self._budget_result()
                self._sleeper(delay)
                attempts += 1
                continue

            if response.status_code >= 400:
                return LsResponse(
                    result_code="HTTP_ERROR",
                    message=f"LS returned HTTP {response.status_code}",
                    status_code=response.status_code,
                )
            try:
                data = response.json()
            except ValueError:
                return LsResponse(result_code="INVALID_RESPONSE", message="LS response was not valid JSON")
            return LsResponse(data=data)

    def _url(self, path: str | None) -> str:
        if path is None:
            return self.config.endpoint
        if not path.strip():
            raise ValueError("path must be non-empty when supplied")
        return f"{self.config.endpoint.rstrip('/')}/{path.lstrip('/')}"

    def _headers(self, tr_code: str) -> dict[str, str]:
        token = self._token_provider() if callable(self._token_provider) else self._token_provider.get_token()
        headers = {
            "content-type": "application/json; charset=UTF-8",
            "authorization": f"Bearer {token}",
            "tr_cd": tr_code,
            "tr_cont": "N",
            "tr_cont_key": "",
        }
        if self._mac_address is not None:
            headers["mac_address"] = self._mac_address
        return headers

    def _reserve_token(self, tr_code: str, started: float) -> bool:
        now = _now_seconds(self._clock)
        with self._limiters_lock:
            limiter = self._limiters.get(tr_code)
            if limiter is None:
                limiter = _TokenBucket(now, self.config.personal_requests_per_second)
                self._limiters[tr_code] = limiter
        # 같은 TR의 token 예약과 sleeper를 직렬화해 동시 호출도 1건/초를 지킨다.
        with limiter.lock:
            wait = limiter.reserve(now)
            if not self._wait_within_budget(wait, started):
                return False
            if wait:
                self._sleeper(wait)
            # 실제 대기가 예정보다 길어져 budget을 넘은 경우 HTTP 요청을 보내지 않는다.
            return _now_seconds(self._clock) - started <= self.config.budget_seconds

    def _wait_within_budget(self, delay: float, started: float) -> bool:
        return _now_seconds(self._clock) - started + delay <= self.config.budget_seconds

    def _retry_after(self, value: str | None) -> float:
        if not value:
            return self._default_backoff()
        try:
            seconds = float(value.strip())
            if 0 <= seconds <= self.config.max_retry_after_seconds:
                return seconds
            return self._default_backoff()
        except ValueError:
            pass
        try:
            retry_at = parsedate_to_datetime(value)
            if retry_at.tzinfo is None:
                retry_at = retry_at.replace(tzinfo=timezone.utc)
            seconds = (retry_at - _as_utc_datetime(self._clock())).total_seconds()
            if 0 <= seconds <= self.config.max_retry_after_seconds:
                return seconds
        except (TypeError, ValueError, OverflowError):
            pass
        return self._default_backoff()

    def _default_backoff(self) -> float:
        return min(self.config.default_backoff_seconds, self.config.max_retry_after_seconds)

    @staticmethod
    def _budget_result() -> LsResponse:
        return LsResponse(result_code="BUDGET_EXHAUSTED", message="LS request wall-clock budget exhausted", retryable=True)

    @staticmethod
    def _retry_exhausted(message: str, status_code: int | None = None) -> LsResponse:
        return LsResponse(result_code="RATE_LIMIT_EXHAUSTED", message=message, retryable=True, status_code=status_code)
