import argparse

import pytest

from apps.batch import __main__ as batch_main
from apps.batch.scheduler import SchedulerResult


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
