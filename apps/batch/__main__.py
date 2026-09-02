"""GH Actions cron이 호출하는 스케줄 배치 CLI 진입점.

``python -m apps.batch --batch-kind premarket|intraday|close`` 로 실행한다.
휴장·partial 결과는 정상 종료 코드(0)를 반환하고, ``failed`` 결과일 때만
비정상 종료 코드(1)를 반환한다.
"""

from __future__ import annotations

import argparse
import contextlib
import os
import sys
from datetime import datetime
from zoneinfo import ZoneInfo

from domain.run_state import Trigger

from .ls_auth import LsOAuthTokenProvider
from .ls_client import LsClient, LsClientConfig
from .ls_daily_bar import LsDailyBarProvider
from .run_state import RunStateGateway
from .scheduler import SchedulerResult, run_scheduled_batch
from .supabase_client import SupabaseCalendarRepository, SupabaseRpcClient

KST = ZoneInfo("Asia/Seoul")


def _require_env(name: str) -> str:
    value = os.environ.get(name)
    if not value:
        raise SystemExit(f"missing required environment variable: {name}")
    return value


def _parse_args(argv: list[str] | None) -> argparse.Namespace:
    parser = argparse.ArgumentParser(prog="python -m apps.batch")
    parser.add_argument("--batch-kind", required=True, choices=["premarket", "intraday", "close"])
    parser.add_argument("--trigger", default="schedule", choices=["schedule", "manual"])
    parser.add_argument("--dispatch-request-id", default=None)
    return parser.parse_args(argv)


def run(args: argparse.Namespace, *, now_kst: datetime | None = None) -> SchedulerResult:
    supabase_url = _require_env("SUPABASE_URL")
    service_role_key = _require_env("SUPABASE_SERVICE_ROLE_KEY")
    ls_app_key = _require_env("LS_APP_KEY")
    ls_app_secret = _require_env("LS_APP_SECRET")
    query_index = os.environ.get("LS_QUERY_INDEX")
    mac_address = os.environ.get("LS_MAC_ADDRESS")

    with contextlib.ExitStack() as stack:
        rpc_client = stack.enter_context(contextlib.closing(SupabaseRpcClient(supabase_url, service_role_key)))
        calendar_repository = stack.enter_context(
            contextlib.closing(SupabaseCalendarRepository(supabase_url, service_role_key))
        )
        token_provider = stack.enter_context(contextlib.closing(LsOAuthTokenProvider(ls_app_key, ls_app_secret)))
        ls_client = stack.enter_context(
            contextlib.closing(LsClient(token_provider, config=LsClientConfig(mac_address=mac_address)))
        )
        daily_bar_provider = LsDailyBarProvider(ls_client)
        gateway = RunStateGateway(rpc_client)

        moment = now_kst if now_kst is not None else datetime.now(KST)

        return run_scheduled_batch(
            args.batch_kind,
            moment,
            calendar_repository,
            daily_bar_provider,
            gateway,
            ls_client,
            query_index=query_index,
            trigger=Trigger(args.trigger),
            dispatch_request_id=args.dispatch_request_id,
        )


def main(argv: list[str] | None = None) -> int:
    args = _parse_args(argv)
    try:
        result = run(args)
    except SystemExit:
        raise
    except Exception as exc:  # noqa: BLE001 - CLI 최상위 경계에서 구조화 로그로 변환
        print(f"batch_kind={args.batch_kind} status=failed result_code=UNHANDLED_EXCEPTION message={exc}")
        return 1

    id_fields = ""
    if result.run_id is not None:
        id_fields += f" run_id={result.run_id}"
    if result.logical_run_key is not None:
        id_fields += f" logical_run_key={result.logical_run_key}"
    print(f"batch_kind={args.batch_kind} status={result.status} result_code={result.result_code}{id_fields}")
    return 1 if result.status == "failed" else 0


if __name__ == "__main__":
    sys.exit(main())
