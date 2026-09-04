"""전략 D 계산·고정 청산 회귀 테스트."""

from dataclasses import replace

import numpy as np
import pandas as pd
import pytest

import backtest.indicator_opt.strategy_d as strategy_d
from backtest.engine import (
    EXIT_END, EXIT_MAX_HOLD, EXIT_SL, EXIT_TP, TradeParams, run_backtest,
)
from backtest.indicator_opt.strategy_d import (
    BASELINE_END,
    BASELINE_START,
    CANDIDATE_A,
    _baseline_row,
    compute_strategy_d,
    run_strategy_d_backtest,
    strategy_d_signals,
    validate_strategy_d_params,
)
from backtest.indicator_opt._signals import SimpleSignal


def _strategy_d_frame(n: int = 300) -> tuple[pd.DataFrame, int]:
    dates = pd.date_range("2024-01-01", periods=n, freq="B")
    close = np.empty(n)
    close[:250] = 100.0 - np.arange(250) * 0.08
    close[250:] = 80.0 + np.arange(n - 250) * 0.5
    frame = pd.DataFrame(
        {
            "Open": close,
            "High": close + 1.0,
            "Low": close - 1.0,
            "Close": close,
            "Volume": np.full(n, 100.0),
        },
        index=dates,
    )
    signal_position = 255
    # 직전 3봉 거래량 최대값보다 충분히 작고, 직전 20봉 고점을 돌파한다.
    frame.iloc[253, frame.columns.get_loc("Volume")] = 100.0
    frame.iloc[254, frame.columns.get_loc("Volume")] = 200.0
    frame.iloc[signal_position, frame.columns.get_loc("High")] = (
        close[signal_position] + 30.0
    )
    return frame, signal_position


def test_strategy_d_returns_bool_mask_and_all_four_conditions() -> None:
    frame, signal_position = _strategy_d_frame()

    mask = compute_strategy_d(frame)

    assert mask.index.equals(frame.index)
    assert mask.dtype == bool
    assert bool(mask.iloc[signal_position])
    assert int(mask.sum()) == 1


@pytest.mark.parametrize("mutation", ["breakout", "volume", "long_sma"])
def test_each_entry_condition_is_required(mutation: str) -> None:
    frame, signal_position = _strategy_d_frame()
    assert compute_strategy_d(frame).iloc[signal_position]

    if mutation == "breakout":
        frame.iloc[signal_position, frame.columns.get_loc("High")] = (
            frame["High"].iloc[254]
        )
    elif mutation == "volume":
        frame.iloc[signal_position, frame.columns.get_loc("Volume")] = 200.0
    else:
        frame.iloc[signal_position, frame.columns.get_loc("Close")] = 200.0
        frame.iloc[signal_position, frame.columns.get_loc("Open")] = 200.0
        frame.iloc[signal_position, frame.columns.get_loc("High")] = 201.0

    assert not compute_strategy_d(frame).iloc[signal_position]


def test_rsi_breakout_is_required_independently(monkeypatch: pytest.MonkeyPatch) -> None:
    frame, signal_position = _strategy_d_frame()
    assert compute_strategy_d(frame).iloc[signal_position]

    # 다른 세 조건을 만드는 OHLCV는 그대로 두고 RSI 상향돌파만 제거한다.
    monkeypatch.setattr(
        strategy_d,
        "rsi",
        lambda close, window: pd.Series(50.0, index=close.index),
    )

    assert not compute_strategy_d(frame).iloc[signal_position]


def test_zero_volume_window_is_false_without_division_error() -> None:
    frame, signal_position = _strategy_d_frame()
    frame.iloc[253:255, frame.columns.get_loc("Volume")] = 200.0
    frame.iloc[signal_position, frame.columns.get_loc("Volume")] = 0.0

    mask = compute_strategy_d(frame)

    assert mask.dtype == bool
    assert not mask.iloc[signal_position]
    assert mask.notna().all()


def test_all_zero_volume_window_is_false_without_division_error() -> None:
    frame, signal_position = _strategy_d_frame()
    frame.iloc[253:256, frame.columns.get_loc("Volume")] = 0.0

    mask = compute_strategy_d(frame)

    assert not mask.iloc[signal_position]
    assert mask.dtype == bool
    assert mask.notna().all()


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("breakout_window", 1.5),
        ("volume_window", 0),
        ("long_sma_window", True),
        ("rsi_period", -1),
        ("rsi_smooth", 0),
        ("max_holding_bars", 0),
        ("volume_ratio_max", np.nan),
        ("volume_ratio_max", 1.1),
        ("rsi_threshold", np.inf),
        ("rsi_min", 50.0),
        ("take_profit_pct", 0),
        ("stop_loss_pct", -1),
        ("cost_rate", -0.01),
    ],
)
def test_invalid_strategy_parameters_are_rejected(field: str, value) -> None:
    frame, _ = _strategy_d_frame()
    params = replace(CANDIDATE_A, **{field: value})

    with pytest.raises(ValueError):
        compute_strategy_d(frame, params)


@pytest.mark.parametrize("mutation", ["duplicate", "ohlc", "negative_volume"])
def test_strategy_d_frame_contract_is_rejected(mutation: str) -> None:
    frame, _ = _strategy_d_frame()
    if mutation == "duplicate":
        frame.columns = ["Open", "High", "Low", "Close", "Close"]
    elif mutation == "ohlc":
        frame.iloc[100, frame.columns.get_loc("High")] = 1.0
    else:
        frame.iloc[100, frame.columns.get_loc("Volume")] = -1.0

    with pytest.raises(ValueError):
        compute_strategy_d(frame)


def test_insufficient_history_is_safe_and_silent() -> None:
    frame, _ = _strategy_d_frame()
    frame = frame.iloc[:239].copy()

    mask = compute_strategy_d(frame)

    assert mask.index.equals(frame.index)
    assert mask.dtype == bool
    assert not mask.any()


def test_invalid_input_contract_is_explicit() -> None:
    frame, _ = _strategy_d_frame()
    frame = frame.drop(columns="Volume")

    with pytest.raises(ValueError, match="OHLCV 컬럼"):
        compute_strategy_d(frame)


def test_future_high_or_volume_changes_do_not_change_past_signal() -> None:
    frame, signal_position = _strategy_d_frame()
    expected = compute_strategy_d(frame)
    mutated = frame.copy()
    mutated.iloc[signal_position + 1, mutated.columns.get_loc("High")] = 1e9
    mutated.iloc[signal_position + 1, mutated.columns.get_loc("Volume")] = 1e12

    actual = compute_strategy_d(mutated)

    pd.testing.assert_series_equal(
        actual.iloc[: signal_position + 1], expected.iloc[: signal_position + 1]
    )


def test_strategy_d_signals_have_fixed_exit_parameters() -> None:
    frame, signal_position = _strategy_d_frame()

    signals = strategy_d_signals(frame, ticker="T")

    signal = next(item for item in signals if item.date == frame.index[signal_position])
    assert signal.price == pytest.approx(frame["Close"].iloc[signal_position])
    assert signal.take_profit_pct == CANDIDATE_A.take_profit_pct
    assert signal.stop_price == pytest.approx(signal.price * 0.95)


def test_engine_applies_optional_max_holding_without_changing_default() -> None:
    frame = pd.DataFrame(
        {
            "Open": [100.0] * 6,
            "High": [101.0] * 6,
            "Low": [99.0] * 6,
            "Close": [100.0, 100.0, 101.0, 101.0, 103.0, 103.0],
            "Volume": [1000.0] * 6,
        },
        index=pd.date_range("2025-01-01", periods=6, freq="B"),
    )
    signal = SimpleSignal(
        ticker="T",
        date=frame.index[1],
        price=100.0,
        take_profit_pct=50.0,
        stop_price=50.0,
    )

    trades = run_backtest(
        frame,
        [signal],
        TradeParams(atr_window=1, cost_rate=0.0, max_holding_bars=3),
        ticker="T",
    )

    assert len(trades) == 1
    assert trades[0].exit_reason == EXIT_MAX_HOLD
    assert trades[0].exit_date == frame.index[4]
    assert trades[0].holding_bars == 3
    assert trades[0].exit_price == pytest.approx(103.0)


def test_max_holding_day_keeps_sl_priority() -> None:
    frame = pd.DataFrame(
        {
            "Open": [100.0] * 5,
            "High": [101.0, 101.0, 101.0, 101.0, 110.0],
            "Low": [99.0, 99.0, 99.0, 99.0, 90.0],
            "Close": [100.0] * 5,
            "Volume": [1000.0] * 5,
        },
        index=pd.date_range("2025-01-01", periods=5, freq="B"),
    )
    signal = SimpleSignal("T", frame.index[1], 100.0, stop_price=95.0, take_profit_pct=5.0)

    trades = run_backtest(
        frame, [signal], TradeParams(atr_window=1, cost_rate=0.0, max_holding_bars=3), ticker="T"
    )

    assert trades[0].exit_reason == EXIT_SL
    assert trades[0].exit_date == frame.index[4]
    assert trades[0].exit_price == pytest.approx(95.0)


@pytest.mark.parametrize(
    ("field", "expected_reason"),
    [("high", EXIT_TP), ("low", EXIT_SL)],
)
def test_tp_or_sl_before_max_holding_wins(field: str, expected_reason: str) -> None:
    frame = pd.DataFrame(
        {
            "Open": [100.0] * 5,
            "High": [101.0, 101.0, 104.0, 101.0, 101.0],
            "Low": [99.0, 99.0, 99.0, 99.0, 99.0],
            "Close": [100.0] * 5,
            "Volume": [1000.0] * 5,
        },
        index=pd.date_range("2025-01-01", periods=5, freq="B"),
    )
    if field == "low":
        frame.iloc[2, frame.columns.get_loc("Low")] = 94.0
    signal = SimpleSignal(
        "T", frame.index[1], 100.0, stop_price=95.0, take_profit_pct=3.0
    )

    trades = run_backtest(
        frame,
        [signal],
        TradeParams(atr_window=1, cost_rate=0.0, max_holding_bars=3),
        ticker="T",
    )

    assert trades[0].exit_reason == expected_reason
    assert trades[0].exit_date == frame.index[2]


def test_max_holding_uses_end_when_data_ends_first_and_default_is_unchanged() -> None:
    frame = pd.DataFrame(
        {
            "Open": [100.0] * 4,
            "High": [101.0] * 4,
            "Low": [99.0] * 4,
            "Close": [100.0] * 4,
            "Volume": [1000.0] * 4,
        },
        index=pd.date_range("2025-01-01", periods=4, freq="B"),
    )
    signal = SimpleSignal("T", frame.index[1], 100.0, stop_price=50.0, take_profit_pct=50.0)

    limited = run_backtest(frame, [signal], TradeParams(atr_window=1, cost_rate=0.0, max_holding_bars=20), ticker="T")
    default = run_backtest(frame, [signal], TradeParams(atr_window=1, cost_rate=0.0), ticker="T")

    assert limited[0].exit_reason == EXIT_END
    assert limited[0].exit_date == frame.index[-1]
    assert default[0].exit_reason == EXIT_END
    assert default[0].exit_date == frame.index[-1]


@pytest.mark.parametrize("value", [0, -1, 1.5, True])
def test_invalid_max_holding_is_rejected_before_early_return(value) -> None:
    with pytest.raises(ValueError, match="max_holding_bars"):
        run_backtest(pd.DataFrame(), [], TradeParams(max_holding_bars=value))


def test_reproducible_runner_uses_strategy_d_parameters(monkeypatch) -> None:
    frame, _ = _strategy_d_frame()
    captured = {}

    def spy_run_backtest(frame, signals, trade_params, ticker=""):
        captured["trade_params"] = trade_params
        return []

    monkeypatch.setattr("backtest.indicator_opt.strategy_d.run_backtest", spy_run_backtest)

    result = run_strategy_d_backtest({"T": frame})

    assert result["strategy"] == "D"
    assert result["params"] == CANDIDATE_A.as_dict()
    assert captured["trade_params"].cost_rate == CANDIDATE_A.cost_rate
    assert captured["trade_params"].max_holding_bars == CANDIDATE_A.max_holding_bars


def test_runner_records_fixed_observation_window_and_flattened_params() -> None:
    frame, _ = _strategy_d_frame()

    result = run_strategy_d_backtest(
        {"T": frame}, start=BASELINE_START, end=BASELINE_END
    )
    row = _baseline_row(result)

    assert result["data_window_start"] == "2020-08-03"
    assert result["data_window_end"] == "2026-08-27"
    assert row["param_breakout_window"] == 20
    assert row["param_volume_ratio_max"] == 0.95
    assert row["param_take_profit_pct"] == 3.0
    assert row["param_stop_loss_pct"] == 5.0
    assert row["param_max_holding_bars"] == 20
    assert row["param_cost_rate"] == 0.0005
