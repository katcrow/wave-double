"""Story 5.2: 백테스트 유니버스 fixture drift 테스트.

fixture(`tests/fixtures/backtest_universe.json`)가 권위 원천
(`backtest.data.loader.list_tickers()`)과 어긋나면 CI가 막는다. `fetch_kospi200.py`는
모듈 최상단에서 `yfinance`를 import하므로 **정적 파싱으로만** 대조한다.
"""

from __future__ import annotations

import ast
import json
import os
import subprocess
import sys
from pathlib import Path

import pytest

from apps.batch.backtest_universe import (
    EXPECTED_SOURCE_OF_TRUTH,
    FIXTURE_PATH,
    BacktestUniverseFixtureError,
    load_backtest_universe,
    load_backtest_universe_tickers,
    normalize_ticker,
)

_REPO_ROOT = Path(__file__).resolve().parents[2]
_FETCH_SCRIPT = _REPO_ROOT / "backtest" / "data" / "fetch_kospi200.py"
_DOC_PATH = _REPO_ROOT / "tests" / "fixtures" / "BACKTEST_UNIVERSE.md"

# BACKTEST_UNIVERSE.md에 기록된 "다운로드 실패 4종목"(선언 108 - 실측 104).
MISSING_FROM_DISK = {"000060", "003410", "012270", "012510"}
EXPECTED_COUNT = 104
DECLARED_COUNT = 108


def _declared_codes() -> set[str]:
    """`fetch_kospi200.py`의 선언 목록을 AST로 추출(yfinance import 회피).

    파일 전체 정규식은 주석·미래의 다른 리터럴까지 집계하므로(review P7) `KOSPI200…`
    이름에 대입되는 **list 리터럴**만 파싱한다.
    """
    tree = ast.parse(_FETCH_SCRIPT.read_text(encoding="utf-8"))
    codes: set[str] = set()
    for node in ast.walk(tree):
        if not isinstance(node, ast.Assign) or not isinstance(node.value, ast.List):
            continue
        if not any(
            isinstance(target, ast.Name) and target.id.startswith("KOSPI200")
            for target in node.targets
        ):
            continue
        for element in node.value.elts:
            if isinstance(element, ast.Constant) and isinstance(element.value, str):
                codes.add(normalize_ticker(element.value))
    return codes


@pytest.fixture(scope="module")
def disk_universe() -> set[str]:
    """권위 원천(`list_tickers()`). parquet은 커밋돼 있으므로 부재는 skip이 아니라 실패다."""
    pytest.importorskip("pandas")
    from backtest.data.loader import list_tickers

    tickers = list_tickers()
    assert tickers, (
        "backtest/data/raw에 parquet이 없어 drift 대조가 불가하다. parquet은 커밋돼 있어야 "
        "하므로 이는 유일한 권위 대조가 사라진 상태이며 skip이 아니라 실패로 다룬다."
    )
    return {t.split(".", 1)[0] for t in tickers}


# --- fixture 계약 -----------------------------------------------------------


def test_load_backtest_universe_returns_sorted_six_digit_codes():
    codes = load_backtest_universe()
    assert len(codes) == EXPECTED_COUNT
    assert codes == sorted(codes)
    assert len(set(codes)) == len(codes)
    assert all(len(c) == 6 and c.isdigit() for c in codes)


def test_fixture_declares_source_of_truth_and_matching_count():
    payload = json.loads(FIXTURE_PATH.read_text(encoding="utf-8"))
    assert payload["source_of_truth"] == EXPECTED_SOURCE_OF_TRUTH
    assert payload["count"] == len(payload["tickers"]) == EXPECTED_COUNT


def test_fixture_keeps_both_ticker_representations():
    tickers = load_backtest_universe_tickers()
    assert all(t.yahoo_ticker == f"{t.code}.KS" for t in tickers)


def test_normalize_ticker_strips_ks_suffix():
    assert normalize_ticker("005930.KS") == "005930"
    assert normalize_ticker("005930") == "005930"


@pytest.mark.parametrize("bad", ["", "5930", "00593A", "1234567"])
def test_normalize_ticker_rejects_non_six_digit(bad):
    with pytest.raises(BacktestUniverseFixtureError):
        normalize_ticker(bad)


# --- 로드 시점 검증 ---------------------------------------------------------


def _write_fixture(tmp_path: Path, payload: dict) -> Path:
    path = tmp_path / "universe.json"
    path.write_text(json.dumps(payload, ensure_ascii=False), encoding="utf-8")
    return path


def _valid_payload() -> dict:
    return {
        "source_of_truth": EXPECTED_SOURCE_OF_TRUTH,
        "count": 2,
        "tickers": [
            {"code": "000070", "yahoo_ticker": "000070.KS"},
            {"code": "005930", "yahoo_ticker": "005930.KS"},
        ],
    }


def test_load_accepts_minimal_valid_fixture(tmp_path):
    assert load_backtest_universe(_write_fixture(tmp_path, _valid_payload())) == [
        "000070",
        "005930",
    ]


def test_load_rejects_count_mismatch(tmp_path):
    payload = _valid_payload()
    payload["count"] = 3
    with pytest.raises(BacktestUniverseFixtureError, match="count"):
        load_backtest_universe(_write_fixture(tmp_path, payload))


def test_load_rejects_duplicate_codes(tmp_path):
    payload = _valid_payload()
    payload["tickers"][1] = {"code": "000070", "yahoo_ticker": "000070.KS"}
    with pytest.raises(BacktestUniverseFixtureError, match="중복"):
        load_backtest_universe(_write_fixture(tmp_path, payload))


def test_load_rejects_unsorted_codes(tmp_path):
    payload = _valid_payload()
    payload["tickers"].reverse()
    with pytest.raises(BacktestUniverseFixtureError, match="오름차순"):
        load_backtest_universe(_write_fixture(tmp_path, payload))


def test_load_rejects_bad_code_format(tmp_path):
    payload = _valid_payload()
    payload["tickers"][0] = {"code": "70", "yahoo_ticker": "70.KS"}
    with pytest.raises(BacktestUniverseFixtureError):
        load_backtest_universe(_write_fixture(tmp_path, payload))


def test_load_rejects_code_yahoo_mismatch(tmp_path):
    payload = _valid_payload()
    payload["tickers"][0]["yahoo_ticker"] = "000071.KS"
    with pytest.raises(BacktestUniverseFixtureError, match="불일치"):
        load_backtest_universe(_write_fixture(tmp_path, payload))


def test_load_rejects_wrong_source_of_truth(tmp_path):
    payload = _valid_payload()
    payload["source_of_truth"] = "somewhere/else"
    with pytest.raises(BacktestUniverseFixtureError, match="source_of_truth"):
        load_backtest_universe(_write_fixture(tmp_path, payload))


def test_load_rejects_missing_file(tmp_path):
    with pytest.raises(BacktestUniverseFixtureError):
        load_backtest_universe(tmp_path / "nope.json")


# --- drift 대조 -------------------------------------------------------------


def test_fixture_matches_disk_universe_exactly(disk_universe):
    fixture_codes = set(load_backtest_universe())
    assert fixture_codes == disk_universe, (
        "fixture drift: tests/fixtures/generate_backtest_universe.py로 재생성하라. "
        f"fixture-disk={sorted(fixture_codes - disk_universe)} "
        f"disk-fixture={sorted(disk_universe - fixture_codes)}"
    )


def test_fixture_is_subset_of_declared_list():
    fixture_codes = set(load_backtest_universe())
    declared = _declared_codes()
    assert declared, "fetch_kospi200.py 정적 파싱 실패"
    assert fixture_codes <= declared, sorted(fixture_codes - declared)


def test_declared_minus_fixture_matches_documented_missing_four():
    declared = _declared_codes()
    fixture_codes = set(load_backtest_universe())
    assert len(declared) == DECLARED_COUNT
    assert declared - fixture_codes == MISSING_FROM_DISK


def test_document_records_the_missing_four_and_counts():
    doc = _DOC_PATH.read_text(encoding="utf-8")
    for code in MISSING_FROM_DISK:
        assert code in doc, f"BACKTEST_UNIVERSE.md에 누락 종목 {code} 기록 없음"
    assert str(DECLARED_COUNT) in doc and str(EXPECTED_COUNT) in doc


# --- 운영 경로 격리 ---------------------------------------------------------


def _imported_module_names(path: Path) -> set[str]:
    """AST로 실제 import 대상 모듈명만 수집한다(docstring 언급은 무시)."""
    tree = ast.parse(path.read_text(encoding="utf-8"))
    names: set[str] = set()
    for node in ast.walk(tree):
        if isinstance(node, ast.Import):
            names.update(alias.name for alias in node.names)
        elif isinstance(node, ast.ImportFrom) and node.module:
            names.add(node.module)
    return names


def test_backtest_universe_module_does_not_import_backtest_at_all():
    """`backtest_universe.py`는 `backtest` 패키지 전면 미의존을 유지한다."""
    modules = _imported_module_names(_REPO_ROOT / "apps/batch/backtest_universe.py")
    for name in modules:
        assert name != "yfinance", name
        assert name != "backtest" and not name.startswith("backtest."), name


def test_universe_signal_module_avoids_yfinance_and_direct_backtest_data_import():
    """`universe_signal.py`의 실제 보장(review P1).

    이 모듈은 AD-5 공유 진입점 `backtest.strategy_api`를 import하고, 그 경유로
    `backtest.indicator_opt.combine_strategies`가 `backtest.data.loader`를 **전이적으로**
    import한다(기존 `tags_stage`도 동일, pre-existing). `backtest/data/loader.py`는 import
    시점에 parquet을 읽지 않으므로 무해하다. 따라서 여기서 고정하는 보장은 `yfinance`
    미의존 + `backtest.data`를 **직접** import하지 않음이다.
    """
    modules = _imported_module_names(_REPO_ROOT / "apps/batch/universe_signal.py")
    for name in modules:
        assert name != "yfinance", name
        assert name != "backtest.data" and not name.startswith("backtest.data."), name


def test_transitive_backtest_data_import_is_a_documented_fact():
    """전이 import 경로가 실제로 존재함을 사실로 고정한다(주장과 코드의 어긋남 방지)."""
    combine = _REPO_ROOT / "backtest" / "indicator_opt" / "combine_strategies.py"
    assert "from ..data.loader import load_all" in combine.read_text(encoding="utf-8")
    doc = _DOC_PATH.read_text(encoding="utf-8")
    assert "전이" in doc and "backtest.data.loader" in doc


_BLOCKER_PREAMBLE = """
import sys


class _Blocker:
    _blocked = BLOCKED_PLACEHOLDER

    def find_spec(self, name, path=None, target=None):
        for blocked in self._blocked:
            if name == blocked or name.startswith(blocked + "."):
                raise ImportError("blocked: " + name)
        return None


sys.meta_path.insert(0, _Blocker())
"""

_SUBPROCESS_SCRIPT = (
    _BLOCKER_PREAMBLE.replace("BLOCKED_PLACEHOLDER", '("yfinance", "backtest")')
    + """
from apps.batch.backtest_universe import load_backtest_universe

codes = load_backtest_universe()
assert len(codes) == EXPECTED_COUNT_PLACEHOLDER, len(codes)
assert codes == sorted(codes)
assert all(len(c) == 6 and c.isdigit() for c in codes)
print("OK")
"""
)

_SIGNAL_SUBPROCESS_SCRIPT = (
    _BLOCKER_PREAMBLE.replace("BLOCKED_PLACEHOLDER", '("yfinance",)')
    + """
import apps.batch.universe_signal as universe_signal

assert "yfinance" not in sys.modules
# 전이 import는 실제로 일어난다 -- import 시점 부작용이 없다는 것이 보장의 내용이다.
assert "backtest.data.loader" in sys.modules
assert len(universe_signal.STRATEGY_KEYS) == 8
print("OK")
"""
)


def _run_isolated(script: str) -> subprocess.CompletedProcess:
    env = dict(os.environ)
    env["PYTHONPATH"] = os.pathsep.join(
        [str(_REPO_ROOT), str(_REPO_ROOT / "packages" / "domain")]
    )
    return subprocess.run(
        [sys.executable, "-c", script],
        cwd=str(_REPO_ROOT),
        capture_output=True,
        text=True,
        env=env,
    )


def test_load_works_without_yfinance_or_backtest_importable():
    """AC: fixture만 있고 yfinance·backtest 전체가 import 불가한 환경에서도 104종목 반환."""
    script = _SUBPROCESS_SCRIPT.replace("EXPECTED_COUNT_PLACEHOLDER", str(EXPECTED_COUNT))
    proc = _run_isolated(script)
    assert proc.returncode == 0, proc.stderr
    assert "OK" in proc.stdout


def test_universe_signal_imports_without_yfinance():
    """`yfinance`만 차단한 서브프로세스에서 `apps.batch.universe_signal` import가 성공한다."""
    proc = _run_isolated(_SIGNAL_SUBPROCESS_SCRIPT)
    assert proc.returncode == 0, proc.stderr
    assert "OK" in proc.stdout
