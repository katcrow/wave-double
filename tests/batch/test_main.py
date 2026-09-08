import argparse

import pytest

from apps.batch import __main__ as batch_main
from apps.batch.scheduler import SchedulerResult
from domain.run_state import Trigger


def _args(batch_kind="close"):
    return argparse.Namespace(batch_kind=batch_kind)


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
        batch_main.run(_args())


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


def test_parse_args_defaults_trigger_to_schedule_with_no_dispatch_request_id():
    args = batch_main._parse_args(["--batch-kind", "close"])
    assert args.trigger == "schedule"
    assert args.dispatch_request_id is None


def test_parse_args_accepts_trigger_and_dispatch_request_id():
    args = batch_main._parse_args(
        ["--batch-kind", "close", "--trigger", "manual", "--dispatch-request-id", "abc-123"]
    )
    assert args.trigger == "manual"
    assert args.dispatch_request_id == "abc-123"


class _FakeCloseable:
    """SUPABASE/LS 클라이언트 생성자를 대체하는 최소 stub. contextlib.closing이 요구하는 close()만 있다."""

    def __init__(self, *args, **kwargs):
        pass

    def close(self):
        pass


def test_run_forwards_trigger_and_dispatch_request_id_to_run_scheduled_batch(monkeypatch):
    """apps/batch/__main__.py의 --trigger/--dispatch-request-id CLI 인자가 run_scheduled_batch까지
    실제로 전달되는지 검증한다 -- 기존 테스트는 run() 자체를 monkeypatch하거나 run_scheduled_batch를
    직접 호출해 이 경로(argparse -> run() -> run_scheduled_batch)를 우회했다."""
    monkeypatch.setenv("SUPABASE_URL", "https://example.supabase.co")
    monkeypatch.setenv("SUPABASE_SERVICE_ROLE_KEY", "service-role-key")
    monkeypatch.setenv("LS_APP_KEY", "app-key")
    monkeypatch.setenv("LS_APP_SECRET", "app-secret")

    monkeypatch.setattr(batch_main, "SupabaseRpcClient", _FakeCloseable)
    monkeypatch.setattr(batch_main, "SupabaseCalendarRepository", _FakeCloseable)
    monkeypatch.setattr(batch_main, "LsOAuthTokenProvider", _FakeCloseable)
    monkeypatch.setattr(batch_main, "LsClient", _FakeCloseable)

    captured: dict[str, object] = {}

    def _fake_run_scheduled_batch(batch_kind, moment, calendar_repository, daily_bar_provider, gateway, ls_client, ohlcv_provider, ohlcv_repository, candidate_fetcher, ohlcv_loader, tags_repository, tagged_candidate_fetcher, supply_provider, program_supply_provider, supply_repository, *, query_index=None, trigger=None, dispatch_request_id=None):
        captured["batch_kind"] = batch_kind
        captured["ls_client"] = ls_client
        captured["supply_provider"] = supply_provider
        captured["program_supply_provider"] = program_supply_provider
        captured["trigger"] = trigger
        captured["dispatch_request_id"] = dispatch_request_id
        return SchedulerResult("success", "OK")

    monkeypatch.setattr(batch_main, "run_scheduled_batch", _fake_run_scheduled_batch)

    args = batch_main._parse_args(
        ["--batch-kind", "close", "--trigger", "manual", "--dispatch-request-id", "req-1"]
    )
    result = batch_main.run(args)

    assert result.status == "success"
    assert captured["batch_kind"] == "close"
    assert captured["supply_provider"]._client is captured["ls_client"]
    assert captured["program_supply_provider"]._client is captured["ls_client"]
    assert captured["trigger"] == Trigger.MANUAL
    assert captured["dispatch_request_id"] == "req-1"


def test_run_defaults_to_schedule_trigger_with_no_dispatch_request_id(monkeypatch):
    monkeypatch.setenv("SUPABASE_URL", "https://example.supabase.co")
    monkeypatch.setenv("SUPABASE_SERVICE_ROLE_KEY", "service-role-key")
    monkeypatch.setenv("LS_APP_KEY", "app-key")
    monkeypatch.setenv("LS_APP_SECRET", "app-secret")

    monkeypatch.setattr(batch_main, "SupabaseRpcClient", _FakeCloseable)
    monkeypatch.setattr(batch_main, "SupabaseCalendarRepository", _FakeCloseable)
    monkeypatch.setattr(batch_main, "LsOAuthTokenProvider", _FakeCloseable)
    monkeypatch.setattr(batch_main, "LsClient", _FakeCloseable)

    captured: dict[str, object] = {}

    def _fake_run_scheduled_batch(batch_kind, moment, calendar_repository, daily_bar_provider, gateway, ls_client, ohlcv_provider, ohlcv_repository, candidate_fetcher, ohlcv_loader, tags_repository, tagged_candidate_fetcher, supply_provider, program_supply_provider, supply_repository, *, query_index=None, trigger=None, dispatch_request_id=None):
        captured["trigger"] = trigger
        captured["dispatch_request_id"] = dispatch_request_id
        return SchedulerResult("success", "OK")

    monkeypatch.setattr(batch_main, "run_scheduled_batch", _fake_run_scheduled_batch)

    args = batch_main._parse_args(["--batch-kind", "close"])
    batch_main.run(args)

    assert captured["trigger"] == Trigger.SCHEDULE
    assert captured["dispatch_request_id"] is None
