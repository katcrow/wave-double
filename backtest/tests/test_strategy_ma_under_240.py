"""240이평 아래 단기 이평선 돌파 전략의 핵심 규칙 테스트."""

import numpy as np
import pandas as pd
import pytest

from backtest.engine import TradeParams, run_backtest
from backtest.indicator_opt._signals import SimpleSignal
from backtest.indicator_opt.strategy_ma_under_240 import (
    MaUnder240Params,
    run_strategy_ma_backtest,
    strategy_ma_signals,
)
import backtest.indicator_opt.strategy_ma_under_240 as strategy_module


def _frame(values: list[float]) -> pd.DataFrame:
    close = np.asarray(values, dtype=float)
    return pd.DataFrame({"Open": close, "High": close, "Low": close, "Close": close, "Volume": 1_000}, index=pd.date_range("2020-01-01", periods=len(close), freq="D"))


def test_requires_240_below_and_20_above_60() -> None:
    close = [100.0] * 240 + [100.0, 100.0, 100.0, 100.0]
    close[239] = 110.0
    close[240] = 90.0
    close[241] = 91.0
    close[242] = 95.0
    close[243] = 96.0
    frame = _frame(close)
    assert strategy_ma_signals(frame, 3, ticker="T") == []


def test_detects_strict_upward_cross_with_filters() -> None:
    close = [100.0] * 180 + list(np.linspace(100.0, 110.0, 60)) + [90.0, 90.0, 100.0, 100.0]
    frame = _frame(close)
    stoch_db = pd.Series(False, index=frame.index)
    stoch_db.iloc[242] = True
    signals = strategy_ma_signals(frame, 3, ticker="T", stoch_db=stoch_db)
    assert [s.date for s in signals] == [frame.index[242]]
    assert signals[0].take_profit_pct == 3.0


def test_stochastic_double_bottom_is_required(monkeypatch: pytest.MonkeyPatch) -> None:
    close = [100.0] * 180 + list(np.linspace(100.0, 110.0, 60)) + [90.0, 90.0, 100.0, 100.0]
    frame = _frame(close)
    monkeypatch.setattr(
        strategy_module,
        "sig_stoch_double_bottom",
        lambda frame, **kwargs: pd.Series(False, index=frame.index),
    )
    assert strategy_ma_signals(frame, 3, ticker="T") == []

    allowed = pd.Series(False, index=frame.index)
    allowed.iloc[242] = True
    monkeypatch.setattr(strategy_module, "sig_stoch_double_bottom", lambda frame, **kwargs: allowed)
    assert [s.date for s in strategy_ma_signals(frame, 3, ticker="T")] == [frame.index[242]]


def test_tp_first_and_same_ticker_reentry_are_engine_contracts() -> None:
    frame = _frame([100.0] * 25)
    frame.iloc[16, frame.columns.get_loc("High")] = 104.0
    frame.iloc[16, frame.columns.get_loc("Low")] = 96.0
    frame.iloc[17, frame.columns.get_loc("High")] = 104.0
    signals = [
        SimpleSignal("T", frame.index[15], 100.0, take_profit_pct=3.0, stop_price=97.0),
        SimpleSignal("T", frame.index[16], 100.0, take_profit_pct=3.0, stop_price=97.0),
    ]
    trades = run_backtest(frame, signals, TradeParams(cost_rate=0, tp_first=True), ticker="T")
    assert len(trades) == 1
    assert trades[0].exit_reason == "tp"


def test_grid_runs_every_requested_window() -> None:
    frame = _frame([100.0] * 260)
    result = run_strategy_ma_backtest({"T": frame}, MaUnder240Params(ma_min=3, ma_max=5), start=None, end=None)
    assert [row["ma_window"] for row in result["summary"]] == [3, 4, 5]
