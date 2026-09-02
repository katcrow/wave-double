from datetime import date

import httpx
import pandas as pd
import pytest

from apps.batch.ohlcv_cache_loader import SupabaseOhlcvCacheLoader
from domain.ohlcv_cache import MIN_HISTORY_TRADING_DAYS, OhlcvCacheStatus


def make_loader(handler):
    transport = httpx.MockTransport(handler)
    return SupabaseOhlcvCacheLoader(
        "https://example.supabase.co", "service-role-key", http_client=httpx.Client(transport=transport)
    )


def _row(day: str, close: float = 100.0) -> dict:
    return {"trading_day": day, "open": close, "high": close, "low": close, "close": close, "volume": 1}


def test_load_ohlcv_applies_trading_day_lte_cutoff_filter():
    def handler(request):
        assert request.url.params["ticker"] == "eq.005930"
        assert request.url.params["trading_day"] == "lte.2026-09-01"
        assert request.url.params["order"] == "trading_day.asc"
        return httpx.Response(200, json=[_row("2026-08-31"), _row("2026-09-01")])

    loader = make_loader(handler)
    frame = loader.load_ohlcv("005930", date(2026, 9, 1))
    assert isinstance(frame, pd.DataFrame)
    assert list(frame.columns) == ["Open", "High", "Low", "Close", "Volume"]
    assert len(frame) == 2


def test_load_ohlcv_preserves_trading_day_as_index_for_signal_date_extraction():
    def handler(request):
        return httpx.Response(200, json=[_row("2026-08-31"), _row("2026-09-01")])

    loader = make_loader(handler)
    frame = loader.load_ohlcv("005930", date(2026, 9, 1))
    assert list(frame.index.date) == [date(2026, 8, 31), date(2026, 9, 1)]


def test_load_ohlcv_empty_history_is_ineligible():
    loader = make_loader(lambda request: httpx.Response(200, json=[]))
    result = loader.load_ohlcv("005930", date(2026, 9, 1))
    assert result is OhlcvCacheStatus.INELIGIBLE_INSUFFICIENT_HISTORY


def test_load_ohlcv_http_failure_is_error():
    loader = make_loader(lambda request: httpx.Response(500, json={"message": "boom"}))
    result = loader.load_ohlcv("005930", date(2026, 9, 1))
    assert result is OhlcvCacheStatus.ERROR


def test_load_ohlcv_rejects_non_alnum_ticker_before_calling_supabase():
    calls = []

    def handler(request):
        calls.append(request)
        return httpx.Response(200, json=[])

    loader = make_loader(handler)
    result = loader.load_ohlcv("abc),(select", date(2026, 9, 1))
    assert result is OhlcvCacheStatus.ERROR
    assert calls == []


def test_load_ohlcv_malformed_row_missing_column_is_error():
    # 'close' 컬럼이 누락된 행 -- HTTP 호출 자체는 성공하지만 DataFrame 구성(컬럼 선택)이 실패해야 한다.
    malformed_row = {"trading_day": "2026-09-01", "open": 100.0, "high": 100.0, "low": 100.0, "volume": 1}
    loader = make_loader(lambda request: httpx.Response(200, json=[malformed_row]))
    result = loader.load_ohlcv("005930", date(2026, 9, 1))
    assert result is OhlcvCacheStatus.ERROR


def test_load_batch_marks_insufficient_rows_ineligible_using_domain_constant():
    days = pd.date_range("2026-01-01", periods=MIN_HISTORY_TRADING_DAYS - 1, freq="D")
    rows = [_row(day.date().isoformat()) for day in days]
    loader = make_loader(lambda request: httpx.Response(200, json=rows))
    results = loader.load_batch(["005930"], date(2026, 9, 1))
    assert results["005930"].status == OhlcvCacheStatus.INELIGIBLE_INSUFFICIENT_HISTORY
    assert results["005930"].trading_days == MIN_HISTORY_TRADING_DAYS - 1
