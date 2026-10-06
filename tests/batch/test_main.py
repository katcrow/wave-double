import argparse
from datetime import datetime, timezone

import pytest

from apps.batch import __main__ as batch_main
from apps.batch.scheduler import SchedulerResult, is_scheduled_execution_allowed
from domain.run_state import Trigger


def _args(batch_kind="close", *, trigger="schedule", dispatch_request_id=None, logical_run_key=None):
    return argparse.Namespace(
        batch_kind=batch_kind,
        trigger=trigger,
        dispatch_request_id=dispatch_request_id,
        logical_run_key=logical_run_key,
    )


def test_require_env_raises_system_exit_when_missing(monkeypatch):
    monkeypatch.delenv("SUPABASE_URL", raising=False)
    with pytest.raises(SystemExit):
        batch_main._require_env("SUPABASE_URL")


def test_run_raises_system_exit_when_required_env_missing(monkeypatch):
    monkeypatch.delenv("SUPABASE_URL", raising=False)
    monkeypatch.setenv("SUPABASE_SERVICE_ROLE_KEY", "key")
    monkeypatch.setenv("LS_APP_KEY", "app-key")
    monkeypatch.setenv("LS_APP_SECRET", "app-secret")
    with pytest.raises(SystemExit):
        batch_main.run(_args(), now_kst=datetime(2026, 10, 1, 19, 40))


def test_run_raises_system_exit_when_condition_search_user_id_missing(monkeypatch):
    monkeypatch.setenv("SUPABASE_URL", "https://example.supabase.co")
    monkeypatch.setenv("SUPABASE_SERVICE_ROLE_KEY", "key")
    monkeypatch.setenv("LS_APP_KEY", "app-key")
    monkeypatch.setenv("LS_APP_SECRET", "app-secret")
    monkeypatch.delenv("LS_CONDITION_SEARCH_USER_ID", raising=False)
    with pytest.raises(SystemExit):
        batch_main.run(_args(), now_kst=datetime(2026, 10, 1, 19, 40))


@pytest.mark.parametrize("status", ["success", "skipped", "partial"])
def test_main_exit_code_zero_for_non_failed_status(monkeypatch, status):
    monkeypatch.setattr(
        batch_main,
        "run",
        lambda args, **kwargs: SchedulerResult(status, "OK"),
    )
    exit_code = batch_main.main(["--batch-kind", "close"])
    assert exit_code == 0


def test_main_exit_code_one_for_failed_status(monkeypatch):
    monkeypatch.setattr(
        batch_main,
        "run",
        lambda args, **kwargs: SchedulerResult("failed", "SOME_ERROR"),
    )
    exit_code = batch_main.main(["--batch-kind", "close"])
    assert exit_code == 1


def test_main_prints_run_id_and_logical_run_key_when_present(monkeypatch, capsys):
    monkeypatch.setattr(
        batch_main,
        "run",
        lambda args, **kwargs: SchedulerResult(
            "skipped", "HOLIDAY", skip_reason="holiday", run_id="abc-123", logical_run_key="close:2026-09-01"
        ),
    )
    exit_code = batch_main.main(["--batch-kind", "close"])
    assert exit_code == 0
    captured = capsys.readouterr()
    assert "run_id=abc-123" in captured.out
    assert "logical_run_key=close:2026-09-01" in captured.out


def test_main_catches_exception_from_run_and_reports_failed(monkeypatch, capsys):
    def _raise(args, **kwargs):
        raise RuntimeError("boom: gateway rpc failed")

    monkeypatch.setattr(batch_main, "run", _raise)
    exit_code = batch_main.main(["--batch-kind", "close"])
    assert exit_code == 1
    captured = capsys.readouterr()
    assert "status=failed" in captured.out


def test_bias_failure_is_visible_but_cli_success_is_preserved(monkeypatch, capsys):
    monkeypatch.setattr(batch_main, "run", lambda args: SchedulerResult(
        "success", "OK", published=True, bias_status="failed", bias_result_code="BIAS_FAILED"))
    assert batch_main.main(["--batch-kind", "close"]) == 0
    assert "bias_status=failed bias_result_code=BIAS_FAILED" in capsys.readouterr().out


def test_parse_args_defaults_trigger_to_schedule_with_no_dispatch_request_id():
    args = batch_main._parse_args(["--batch-kind", "close"])
    assert args.trigger == "schedule"
    assert args.dispatch_request_id is None
    assert args.logical_run_key is None


def test_parse_args_accepts_trigger_and_dispatch_request_id():
    args = batch_main._parse_args(
        ["--batch-kind", "close", "--trigger", "manual", "--dispatch-request-id", "abc-123", "--logical-run-key", "close:2026-10-02"]
    )
    assert args.trigger == "manual"
    assert args.dispatch_request_id == "abc-123"
    assert args.logical_run_key == "close:2026-10-02"


class _FakeCloseable:
    """SUPABASE/LS 클라이언트 생성자를 대체하는 최소 stub. contextlib.closing이 요구하는 close()만 있다."""

    def __init__(self, *args, **kwargs):
        pass

    def close(self):
        pass


class _FakeRpcClient(_FakeCloseable):
    def __init__(self, *args, **kwargs):
        self.calls = []

    def rpc(self, function, params):
        self.calls.append((function, params))
        return {"data": {"status": "failed"}}


def test_run_rejects_out_of_window_scheduled_dispatch_without_ls_clients(monkeypatch):
    monkeypatch.setenv("SUPABASE_URL", "https://example.supabase.co")
    monkeypatch.setenv("SUPABASE_SERVICE_ROLE_KEY", "service-role-key")
    monkeypatch.delenv("LS_APP_KEY", raising=False)
    monkeypatch.delenv("LS_APP_SECRET", raising=False)
    monkeypatch.delenv("LS_CONDITION_SEARCH_USER_ID", raising=False)
    rpc_client = _FakeRpcClient()
    monkeypatch.setattr(batch_main, "SupabaseRpcClient", lambda *args, **kwargs: rpc_client)

    args = batch_main._parse_args(
        [
            "--batch-kind", "close", "--dispatch-request-id", "dispatch-1",
            "--logical-run-key", "close:2026-10-01",
        ]
    )
    result = batch_main.run(args, now_kst=datetime(2026, 10, 1, 1, 30))

    assert result.result_code == "SCHEDULE_OUTSIDE_OPERATING_WINDOW"
    assert rpc_client.calls == [
        (
            "reject_scheduled_dispatch",
            {"p_dispatch_request_id": "dispatch-1", "p_reason": "SCHEDULE_OUTSIDE_OPERATING_WINDOW"},
        )
    ]


def test_run_forwards_trigger_and_dispatch_request_id_to_run_scheduled_batch(monkeypatch):
    """apps/batch/__main__.py의 --trigger/--dispatch-request-id CLI 인자가 run_scheduled_batch까지
    실제로 전달되는지 검증한다 -- 기존 테스트는 run() 자체를 monkeypatch하거나 run_scheduled_batch를
    직접 호출해 이 경로(argparse -> run() -> run_scheduled_batch)를 우회했다."""
    monkeypatch.setenv("SUPABASE_URL", "https://example.supabase.co")
    monkeypatch.setenv("SUPABASE_SERVICE_ROLE_KEY", "service-role-key")
    monkeypatch.setenv("LS_APP_KEY", "app-key")
    monkeypatch.setenv("LS_APP_SECRET", "app-secret")
    monkeypatch.setenv("LS_CONDITION_SEARCH_USER_ID", "katcrow")

    monkeypatch.setattr(batch_main, "SupabaseRpcClient", _FakeCloseable)
    monkeypatch.setattr(batch_main, "SupabaseCalendarRepository", _FakeCloseable)
    monkeypatch.setattr(batch_main, "LsOAuthTokenProvider", _FakeCloseable)
    monkeypatch.setattr(batch_main, "LsClient", _FakeCloseable)

    captured: dict[str, object] = {}

    def _fake_run_scheduled_batch(batch_kind, moment, calendar_repository, daily_bar_provider, gateway, ls_client, ohlcv_provider, ohlcv_repository, candidate_fetcher, ohlcv_loader, tags_repository, tagged_candidate_fetcher, supply_provider, program_supply_provider, supply_repository, market_supply_provider, market_program_supply_provider, market_supply_repository, *, condition_search_user_id=None, trigger=None, dispatch_request_id=None, logical_run_key=None, bias_repository=None, strategy_i_supply_provider=None, theme_client=None, market_index_provider=None):
        captured["bias_repository"] = bias_repository
        captured["batch_kind"] = batch_kind
        captured["ls_client"] = ls_client
        captured["supply_provider"] = supply_provider
        captured["program_supply_provider"] = program_supply_provider
        captured["market_supply_provider"] = market_supply_provider
        captured["trigger"] = trigger
        captured["dispatch_request_id"] = dispatch_request_id
        captured["logical_run_key"] = logical_run_key
        captured["condition_search_user_id"] = condition_search_user_id
        captured["strategy_i_supply_provider"] = strategy_i_supply_provider
        captured["theme_client"] = theme_client
        captured["market_index_provider"] = market_index_provider
        return SchedulerResult("success", "OK")

    monkeypatch.setattr(batch_main, "run_scheduled_batch", _fake_run_scheduled_batch)

    args = batch_main._parse_args(
        ["--batch-kind", "close", "--trigger", "manual", "--dispatch-request-id", "req-1"]
    )
    result = batch_main.run(args)

    assert result.status == "success"
    assert captured["batch_kind"] == "close"
    assert isinstance(captured["bias_repository"], batch_main.SupabaseBiasRepository)
    assert captured["supply_provider"]._client is captured["ls_client"]
    assert captured["program_supply_provider"]._client is captured["ls_client"]
    assert captured["market_index_provider"]._client is captured["ls_client"]
    assert captured["trigger"] == Trigger.MANUAL
    assert captured["dispatch_request_id"] == "req-1"
    assert captured["logical_run_key"] is None
    assert captured["condition_search_user_id"] == "katcrow"
    assert captured["strategy_i_supply_provider"] is captured["supply_provider"]
    assert captured["theme_client"] is captured["ls_client"]


def test_run_defaults_to_schedule_trigger_with_no_dispatch_request_id(monkeypatch):
    monkeypatch.setenv("SUPABASE_URL", "https://example.supabase.co")
    monkeypatch.setenv("SUPABASE_SERVICE_ROLE_KEY", "service-role-key")
    monkeypatch.setenv("LS_APP_KEY", "app-key")
    monkeypatch.setenv("LS_APP_SECRET", "app-secret")
    monkeypatch.setenv("LS_CONDITION_SEARCH_USER_ID", "katcrow")

    monkeypatch.setattr(batch_main, "SupabaseRpcClient", _FakeCloseable)
    monkeypatch.setattr(batch_main, "SupabaseCalendarRepository", _FakeCloseable)
    monkeypatch.setattr(batch_main, "LsOAuthTokenProvider", _FakeCloseable)
    monkeypatch.setattr(batch_main, "LsClient", _FakeCloseable)

    captured: dict[str, object] = {}

    def _fake_run_scheduled_batch(batch_kind, moment, calendar_repository, daily_bar_provider, gateway, ls_client, ohlcv_provider, ohlcv_repository, candidate_fetcher, ohlcv_loader, tags_repository, tagged_candidate_fetcher, supply_provider, program_supply_provider, supply_repository, market_supply_provider, market_program_supply_provider, market_supply_repository, *, condition_search_user_id=None, trigger=None, dispatch_request_id=None, logical_run_key=None, bias_repository=None, strategy_i_supply_provider=None, theme_client=None, market_index_provider=None):
        captured["trigger"] = trigger
        captured["dispatch_request_id"] = dispatch_request_id
        captured["logical_run_key"] = logical_run_key
        captured["condition_search_user_id"] = condition_search_user_id
        captured["strategy_i_supply_provider"] = strategy_i_supply_provider
        return SchedulerResult("success", "OK")

    monkeypatch.setattr(batch_main, "run_scheduled_batch", _fake_run_scheduled_batch)

    args = batch_main._parse_args(["--batch-kind", "close"])
    batch_main.run(args, now_kst=datetime(2026, 10, 1, 19, 40))

    assert captured["trigger"] == Trigger.SCHEDULE
    assert captured["dispatch_request_id"] is None
    assert captured["logical_run_key"] is None
    assert captured["condition_search_user_id"] == "katcrow"


@pytest.mark.parametrize(
    ("batch_kind", "moment", "allowed"),
    [
        ("intraday", datetime(2026, 10, 1, 8, 0), True),
        ("intraday", datetime(2026, 10, 1, 19, 29), True),
        ("intraday", datetime(2026, 10, 1, 19, 30), False),
        ("intraday", datetime(2026, 10, 1, 19, 59), False),
        ("close", datetime(2026, 10, 1, 19, 49), True),
        ("close", datetime(2026, 10, 1, 19, 50), False),
        ("close", datetime(2026, 10, 1, 19, 40), True),
        ("close", datetime(2026, 10, 1, 1, 30), False),
        ("intraday", datetime(2026, 10, 1, 20, 0), False),
        ("premarket", datetime(2026, 10, 1, 9, 0), False),
        ("close", datetime(2026, 10, 1, 10, 30, tzinfo=timezone.utc), True),
        ("close", datetime(2026, 10, 1, 11, 0, tzinfo=timezone.utc), False),
    ],
)
def test_scheduled_execution_window_policy(batch_kind, moment, allowed):
    assert is_scheduled_execution_allowed(batch_kind, moment) is allowed


def test_run_skips_out_of_window_schedule_before_constructing_clients(monkeypatch):
    monkeypatch.setenv("SUPABASE_URL", "https://example.supabase.co")
    monkeypatch.setenv("SUPABASE_SERVICE_ROLE_KEY", "service-role-key")
    monkeypatch.setenv("LS_APP_KEY", "app-key")
    monkeypatch.setenv("LS_APP_SECRET", "app-secret")
    monkeypatch.setenv("LS_CONDITION_SEARCH_USER_ID", "katcrow")

    def _unexpected_client(*args, **kwargs):
        raise AssertionError("장외 예약 실행은 외부 클라이언트를 만들면 안 된다")

    monkeypatch.setattr(batch_main, "SupabaseRpcClient", _unexpected_client)
    args = batch_main._parse_args(["--batch-kind", "close"])

    result = batch_main.run(args, now_kst=datetime(2026, 10, 1, 1, 30))

    assert result.status == "skipped"
    assert result.result_code == "SCHEDULE_OUTSIDE_OPERATING_WINDOW"
    assert result.skip_reason == "outside_operating_window"
