"""백테스트 유니버스 fixture 결정적 재생성 도구 (Story 5.2 개발 유틸).

``backtest/data/raw/*_KS.parquet``가 확정하는 **실측 백테스트 유니버스**를
``tests/fixtures/backtest_universe.json``으로 승격한다. 운영 배치(`apps/batch`)는
``yfinance``나 parquet 없이 이 JSON만 읽어 유니버스를 알 수 있다
(`apps.batch.backtest_universe.load_backtest_universe`).

권위는 ``backtest.data.loader.list_tickers()``다 -- ``fetch_kospi200.py``의 선언
목록(108종목)이 아니다. 차이(다운로드 실패 4종목)와 그 근거는
``tests/fixtures/BACKTEST_UNIVERSE.md``에 기록되어 있고
``tests/batch/test_backtest_universe.py``의 drift 테스트가 강제한다.

실행: ``uv run --with pandas --with numpy --with pyarrow \
      python tests/fixtures/generate_backtest_universe.py``
"""
from __future__ import annotations

import json
import sys
from pathlib import Path

_REPO_ROOT = Path(__file__).resolve().parents[2]
for _p in (_REPO_ROOT, _REPO_ROOT / "packages" / "domain"):
    if str(_p) not in sys.path:
        sys.path.insert(0, str(_p))

from backtest.data.loader import list_tickers  # noqa: E402

FIXTURE_PATH = Path(__file__).resolve().parent / "backtest_universe.json"
SOURCE_OF_TRUTH = "backtest/data/raw/*_KS.parquet"


def build_fixture() -> dict:
    """``list_tickers()``에서 fixture 페이로드를 결정적으로 만든다(코드 오름차순)."""
    entries = []
    for yahoo_ticker in sorted(list_tickers()):
        code = yahoo_ticker.split(".", 1)[0]
        if len(code) != 6 or not code.isdigit():
            raise SystemExit(f"예상치 못한 티커 형식: {yahoo_ticker!r}")
        entries.append({"code": code, "yahoo_ticker": yahoo_ticker})
    entries.sort(key=lambda e: e["code"])
    codes = [e["code"] for e in entries]
    if len(set(codes)) != len(codes):
        raise SystemExit("중복 종목코드가 있습니다")
    return {
        "source_of_truth": SOURCE_OF_TRUTH,
        "count": len(entries),
        "tickers": entries,
    }


def main() -> None:
    payload = build_fixture()
    FIXTURE_PATH.write_text(
        json.dumps(payload, ensure_ascii=False, indent=2) + "\n", encoding="utf-8"
    )
    print(f"{FIXTURE_PATH} 재생성 완료: {payload['count']}종목")


if __name__ == "__main__":
    main()
