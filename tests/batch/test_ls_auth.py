import httpx
import pytest

from apps.batch.ls_auth import LsAuthError, LsOAuthTokenProvider


def make_provider(handler, **kwargs):
    transport = httpx.MockTransport(handler)
    return LsOAuthTokenProvider("app-key", "app-secret", http_client=httpx.Client(transport=transport), **kwargs)


def test_get_token_posts_client_credentials_form():
    seen = []

    def handler(request):
        seen.append(request)
        return httpx.Response(200, json={"access_token": "tok-123", "token_type": "Bearer", "expires_in": 86400})

    provider = make_provider(handler)
    token = provider.get_token()
    assert token == "tok-123"
    assert seen[0].url == httpx.URL("https://openapi.ls-sec.co.kr:8080/oauth2/token")
    assert seen[0].headers["content-type"] == "application/x-www-form-urlencoded"
    body = seen[0].content.decode()
    assert "grant_type=client_credentials" in body
    assert "appkey=app-key" in body
    assert "appsecretkey=app-secret" in body
    assert "scope=oob" in body


def test_get_token_caches_for_process_lifetime():
    calls = []

    def handler(request):
        calls.append(request)
        return httpx.Response(200, json={"access_token": "cached-token"})

    provider = make_provider(handler)
    first = provider.get_token()
    second = provider.get_token()
    assert first == second == "cached-token"
    assert len(calls) == 1


def test_get_token_raises_structured_error_on_http_failure():
    provider = make_provider(lambda request: httpx.Response(401, json={"error": "invalid_client"}))
    with pytest.raises(LsAuthError):
        provider.get_token()


def test_get_token_raises_on_transport_failure():
    def raises(request):
        raise httpx.ConnectError("boom", request=request)

    provider = make_provider(raises)
    with pytest.raises(LsAuthError):
        provider.get_token()


def test_get_token_raises_when_access_token_missing():
    provider = make_provider(lambda request: httpx.Response(200, json={"token_type": "Bearer"}))
    with pytest.raises(LsAuthError):
        provider.get_token()


def test_constructor_rejects_empty_credentials():
    with pytest.raises(ValueError):
        LsOAuthTokenProvider("", "secret")
    with pytest.raises(ValueError):
        LsOAuthTokenProvider("key", "")
