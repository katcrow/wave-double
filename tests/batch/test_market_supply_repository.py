from datetime import date
from datetime import datetime
from uuid import uuid4

import httpx

from apps.batch.market_supply_repository import MarketSupplyRow, SupabaseMarketSupplyRepository


def test_upsert_uses_attempt_market_day_natural_key_and_serializes_rows():
    seen = []

    def handler(request):
        seen.append(request)
        return httpx.Response(201, json=[])

    repo = SupabaseMarketSupplyRepository(
        "https://example.supabase.co", "service-role",
        http_client=httpx.Client(transport=httpx.MockTransport(handler)),
    )
    try:
        run_id = str(uuid4())
        count = repo.upsert_rows([MarketSupplyRow(run_id, "KOSPI", date(2026, 9, 1), 1, 2, -3, 4)])
    finally:
        repo.close()

    assert count == 1
    assert seen[0].url.path == "/rest/v1/market_supply"
    assert seen[0].url.params["on_conflict"] == "attempt_run_id,market,trading_day"
    assert seen[0].headers["authorization"] == "Bearer service-role"
    assert seen[0].content.find(b'"market":"KOSPI"') >= 0


def test_row_rejects_datetime_as_trading_day_and_string_numeric_values():
    run_id = str(uuid4())
    try:
        MarketSupplyRow(run_id, "KOSPI", datetime(2026, 9, 1), 1, 2, 3, 4)
    except TypeError:
        pass
    else:
        raise AssertionError("datetime must not be accepted as a date-only trading_day")
    try:
        MarketSupplyRow(run_id, "KOSPI", date(2026, 9, 1), "1", 2, 3, 4)
    except ValueError:
        pass
    else:
        raise AssertionError("string numeric values must be rejected at the repository boundary")
