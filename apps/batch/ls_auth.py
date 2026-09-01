"""LS Open API OAuth2 접근토큰 발급과 프로세스 수명 캐시."""

from __future__ import annotations

from threading import Lock

import httpx

DEFAULT_ENDPOINT = "https://openapi.ls-sec.co.kr:8080"


class LsAuthError(RuntimeError):
    """토큰 발급 실패를 안전하게 구조화한 예외."""


class LsOAuthTokenProvider:
    """``POST /oauth2/token``(client_credentials, scope=oob)으로 접근토큰을 발급한다.

    ``ls_client.TokenProvider`` 프로토콜을 만족하며, 발급된 토큰은 프로세스 수명
    동안 캐시한다(배치 실행은 짧게 끝나므로 만료 재발급을 다루지 않는다).
    """

    def __init__(
        self,
        app_key: str,
        app_secret: str,
        *,
        endpoint: str = DEFAULT_ENDPOINT,
        http_client: httpx.Client | None = None,
        timeout: float = 30.0,
    ) -> None:
        if not app_key or not app_secret:
            raise ValueError("app_key and app_secret must be non-empty")
        self._app_key = app_key
        self._app_secret = app_secret
        self._endpoint = endpoint.rstrip("/")
        self._http = http_client or httpx.Client()
        self._timeout = timeout
        self._token: str | None = None
        self._lock = Lock()

    def close(self) -> None:
        self._http.close()

    def __enter__(self) -> "LsOAuthTokenProvider":
        return self

    def __exit__(self, *_: object) -> None:
        self.close()

    def get_token(self) -> str:
        with self._lock:
            if self._token is None:
                self._token = self._issue_token()
            return self._token

    def _issue_token(self) -> str:
        try:
            response = self._http.post(
                f"{self._endpoint}/oauth2/token",
                headers={"content-type": "application/x-www-form-urlencoded"},
                data={
                    "grant_type": "client_credentials",
                    "appkey": self._app_key,
                    "appsecretkey": self._app_secret,
                    "scope": "oob",
                },
                timeout=self._timeout,
            )
        except httpx.HTTPError as exc:
            raise LsAuthError(f"LS token request failed: {exc}") from exc
        if response.status_code >= 400:
            raise LsAuthError(f"LS token request returned HTTP {response.status_code}")
        try:
            data = response.json()
        except ValueError as exc:
            raise LsAuthError("LS token response was not valid JSON") from exc
        token = data.get("access_token") if isinstance(data, dict) else None
        if not token:
            raise LsAuthError("LS token response missing access_token")
        return token


__all__ = ["LsAuthError", "LsOAuthTokenProvider"]
