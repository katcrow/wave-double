"""VWAP 상향 회복 전략의 조건·경계·러너 회귀 테스트."""

from dataclasses import replace
import sys

import numpy as np
import pandas as pd
import pytest

import backtest.indicator_opt.strategy_vwap_recovery as strategy
from backtest.indicator_opt._signals import SimpleSignal
from backtest.indicator_opt.strategy_vwap_recovery import (
    BASELINE_END,
    BASELINE_START,
    EXIT_CLOSE_PROFIT,
    EXIT_SL,
    EXIT_TP,
    STRATEGY_VWAP_RECOVERY_PARAMS,
    _TRADE_COLUMNS,
    _baseline_row,
    compute_vwap_recovery,
    rolling_vwap,
    run_vwap_recovery,
    run_vwap_recovery_backtest,
    validate_strategy_vwap_recovery_params,
    vwap_recovery_signals,
)


def _recovery_frame(n: int = 50, signal_position: int = 35) -> tuple[pd.DataFrame, int]:
    dates = pd.date_range("2024-01-01", periods=n, freq="B")
    frame = pd.DataFrame(
        {
            "Open": np.full(n, 100.0),
            "High": np.full(n, 101.0),
            "Low": np.full(n, 99.0),
            "Close": np.full(n, 100.0),
            "Volume": np.full(n, 100.0),
        },
        index=dates,
    )
    frame.iloc[signal_position] = [100.0, 102.0, 99.6, 101.0, 120.0]
    frame.iloc[signal_position + 1] = [101.0, 102.0, 99.0, 101.5, 100.0]
    return frame, signal_position


def test_all_four_entry_conditions_are_required() -> None:
    frame, signal_position = _recovery_frame()
    assert compute_vwap_recovery(frame).iloc[signal_position]

    mutations = {
        "recovery": {"Close": 99.0, "Low": 98.8},
        "bullish": {"Open": 101.0},
        "retest": {"Low": 90.0},
        "volume": {"Volume": 100.0},
    }
    for field_values in mutations.values():
        mutated = frame.copy()
        for field, value in field_values.items():
            mutated.iloc[signal_position, mutated.columns.get_loc(field)] = value
        assert not compute_vwap_recovery(mutated).iloc[signal_position]


def test_recovery_accepts_previous_close_equal_to_previous_vwap() -> None:
    frame, signal_position = _recovery_frame()
    vwap = rolling_vwap(frame, 30)
    assert frame["Close"].iloc[signal_position - 1] == pytest.approx(
        vwap.iloc[signal_position - 1]
    )
    assert compute_vwap_recovery(frame).iloc[signal_position]


def test_future_values_do_not_change_past_signal() -> None:
    frame, signal_position = _recovery_frame()
    expected = compute_vwap_recovery(frame)
    mutated = frame.copy()
    mutated.iloc[signal_position + 1, mutated.columns.get_loc("High")] = 1e9
    mutated.iloc[signal_position + 1, mutated.columns.get_loc("Volume")] = 1e12
    actual = compute_vwap_recovery(mutated)
    pd.testing.assert_series_equal(
        actual.iloc[: signal_position + 1], expected.iloc[: signal_position + 1]
    )


def test_warmup_zero_volume_and_invalid_rows_produce_no_signal() -> None:
    frame, signal_position = _recovery_frame()
    warmup = compute_vwap_recovery(frame.iloc[:30])
    assert not warmup.any()

    zero_volume = frame.copy()
    zero_volume.iloc[signal_position - 15 : signal_position, zero_volume.columns.get_loc("Volume")] = 0.0
    assert not compute_vwap_recovery(zero_volume).iloc[signal_position]

    invalid = frame.copy()
    invalid.iloc[20, invalid.columns.get_loc("Close")] = np.nan
    assert not compute_vwap_recovery(invalid).iloc[signal_position]


def test_rolling_vwap_uses_typical_price_volume_weighting() -> None:
    frame = pd.DataFrame(
        {
            "Open": [100.0, 100.0, 100.0],
            "High": [102.0, 104.0, 106.0],
            "Low": [98.0, 100.0, 102.0],
            "Close": [100.0, 102.0, 104.0],
            "Volume": [100.0, 100.0, 200.0],
        },
        index=pd.date_range("2024-01-01", periods=3, freq="B"),
    )
    actual = rolling_vwap(frame, 3).iloc[-1]
    expected = ((100.0 * 100.0) + (102.0 * 100.0) + (104.0 * 200.0)) / 400.0
    assert actual == pytest.approx(expected)


def test_signals_enter_at_close_and_use_fixed_exit_levels() -> None:
    frame, signal_position = _recovery_frame()
    signal = vwap_recovery_signals(frame, ticker="T")[0]
    params = STRATEGY_VWAP_RECOVERY_PARAMS
    assert signal.date == frame.index[signal_position]
    assert signal.price == 101.0
    assert signal.take_profit_pct == params.take_profit_pct
    assert signal.stop_price == pytest.approx(101.0 * 0.96)


def _manual_frame(rows: list[dict[str, float]]) -> pd.DataFrame:
    frame = pd.DataFrame(rows, index=pd.date_range("2025-01-01", periods=len(rows), freq="B"))
    frame["Volume"] = frame.get("Volume", 1000.0)
    return frame[["Open", "High", "Low", "Close", "Volume"]]


def _signal(frame: pd.DataFrame, position: int, ticker: str = "T") -> SimpleSignal:
    return SimpleSignal(ticker, frame.index[position], float(frame["Close"].iloc[position]))


def test_same_bar_tp_and_sl_is_tp_first() -> None:
    frame = _manual_frame([
        {"Open": 100, "High": 100, "Low": 100, "Close": 100},
        {"Open": 100, "High": 104, "Low": 95, "Close": 100},
    ])
    trades = run_vwap_recovery(
        frame,
        [_signal(frame, 0)],
        replace(STRATEGY_VWAP_RECOVERY_PARAMS, cost_rate=0.0),
        ticker="T",
    )
    assert trades[0].exit_reason == EXIT_TP
    assert trades[0].exit_price == pytest.approx(103.0)


def test_default_round_trip_cost_is_deducted_from_trade_return() -> None:
    frame = _manual_frame([
        {"Open": 100, "High": 100, "Low": 100, "Close": 100},
        {"Open": 100, "High": 104, "Low": 99, "Close": 103},
    ])
    trades = run_vwap_recovery(frame, [_signal(frame, 0)], ticker="T")

    assert trades[0].return_pct == pytest.approx(2.9)


def test_profitable_close_forces_exit_but_equal_or_lower_close_holds() -> None:
    frame = _manual_frame([
        {"Open": 100, "High": 100, "Low": 100, "Close": 100},
        {"Open": 100, "High": 102, "Low": 99, "Close": 100},
        {"Open": 100, "High": 102, "Low": 99, "Close": 101},
    ])
    trades = run_vwap_recovery(
        frame, [_signal(frame, 0)], replace(STRATEGY_VWAP_RECOVERY_PARAMS, cost_rate=0.0)
    )
    assert trades[0].exit_reason == EXIT_CLOSE_PROFIT
    assert trades[0].exit_date == frame.index[2]
    assert trades[0].holding_bars == 2

    no_exit_frame = frame.iloc[:2]
    assert not run_vwap_recovery(no_exit_frame, [_signal(no_exit_frame, 0)])


def test_stop_loss_is_used_when_only_stop_is_reached() -> None:
    frame = _manual_frame([
        {"Open": 100, "High": 100, "Low": 100, "Close": 100},
        {"Open": 100, "High": 100, "Low": 95, "Close": 99},
    ])
    trades = run_vwap_recovery(frame, [_signal(frame, 0)], replace(
        STRATEGY_VWAP_RECOVERY_PARAMS, cost_rate=0.0
    ))
    assert trades[0].exit_reason == EXIT_SL
    assert trades[0].exit_price == pytest.approx(96.0)


def test_position_is_single_and_reentry_is_allowed_after_exit() -> None:
    frame = _manual_frame([
        {"Open": 100, "High": 100, "Low": 100, "Close": 100},
        {"Open": 100, "High": 102, "Low": 99, "Close": 100},
        {"Open": 100, "High": 102, "Low": 99, "Close": 101},
        {"Open": 100, "High": 100, "Low": 100, "Close": 100},
        {"Open": 100, "High": 104, "Low": 99, "Close": 103},
    ])
    signals = [_signal(frame, 0), _signal(frame, 1), _signal(frame, 3)]
    trades = run_vwap_recovery(frame, signals, replace(
        STRATEGY_VWAP_RECOVERY_PARAMS, cost_rate=0.0
    ))
    assert [trade.entry_date for trade in trades] == [frame.index[0], frame.index[3]]


def test_last_signal_without_next_bar_is_not_recorded() -> None:
    frame = _manual_frame([
        {"Open": 100, "High": 100, "Low": 100, "Close": 100},
    ])
    assert not run_vwap_recovery(frame, [_signal(frame, 0)])


def test_unclosed_position_blocks_later_signals_until_data_end() -> None:
    frame = _manual_frame([
        {"Open": 100, "High": 100, "Low": 100, "Close": 100},
        {"Open": 100, "High": 100, "Low": 99, "Close": 99},
        {"Open": 99, "High": 99, "Low": 98, "Close": 98},
    ])
    signals = [_signal(frame, 0), _signal(frame, 1)]

    assert not run_vwap_recovery(
        frame,
        signals,
        replace(STRATEGY_VWAP_RECOVERY_PARAMS, cost_rate=0.0),
    )


def test_runner_applies_observation_window_after_warmup_and_flattens_result() -> None:
    frame, signal_position = _recovery_frame()
    result = run_vwap_recovery_backtest(
        {"T": frame}, start=frame.index[signal_position], end=frame.index[-1]
    )
    row = _baseline_row(result)
    assert result["strategy"] == "VWAP_RECOVERY"
    assert result["n_signals"] == 1
    assert result["params"] == STRATEGY_VWAP_RECOVERY_PARAMS.as_dict()
    assert row["param_vwap_window"] == 30
    assert row["param_volume_window"] == 15
    assert row["param_volume_multiplier"] == 1.2
    assert row["param_retest_band_pct"] == 0.5
    assert row["param_take_profit_pct"] == 3.0
    assert row["param_stop_loss_pct"] == 4.0
    assert row["param_cost_rate"] == 0.001
    assert result["data_window_start"] == str(frame.index[signal_position].date())


def test_runner_splits_invalid_segments_and_counts_valid_tickers(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    frame, _ = _recovery_frame()
    frame.iloc[20, frame.columns.get_loc("Close")] = np.nan
    segments: list[pd.DataFrame] = []

    def spy_run(segment, signals, params, ticker=""):
        segments.append(segment)
        return []

    monkeypatch.setattr(strategy, "run_vwap_recovery", spy_run)
    result = run_vwap_recovery_backtest({"T": frame})
    assert result["invalid_ohlcv_rows"] == 1
    assert result["n_tickers"] == 1
    assert result["n_signals"] == 0
    assert [len(segment) for segment in segments] == [20, len(frame) - 21]


def test_runner_is_invariant_to_dictionary_order() -> None:
    frame_a, _ = _recovery_frame()
    frame_b = frame_a.copy()
    frame_b.index = pd.date_range("2024-06-01", periods=len(frame_b), freq="B")
    first = run_vwap_recovery_backtest({"B": frame_b, "A": frame_a})
    second = run_vwap_recovery_backtest({"A": frame_a, "B": frame_b})
    assert first["data_fingerprint"] == second["data_fingerprint"]
    assert first["trades"] == second["trades"]


def test_cli_writes_summary_and_zero_trade_headers(
    monkeypatch: pytest.MonkeyPatch, tmp_path
) -> None:
    frame, _ = _recovery_frame()
    monkeypatch.setattr(strategy, "load_all", lambda: {"T": frame})
    summary_path = tmp_path / "summary.csv"
    monkeypatch.setattr(sys, "argv", ["strategy", "--output", str(summary_path)])
    strategy.main()
    trades_path = tmp_path / "summary_trades.csv"
    assert pd.read_csv(summary_path).loc[0, "n_trades"] >= 1
    assert list(pd.read_csv(trades_path).columns) == list(_TRADE_COLUMNS)

    zero_summary_path = tmp_path / "zero.csv"
    monkeypatch.setattr(
        sys, "argv", ["strategy", "--output", str(zero_summary_path), "--end", "2024-01-10"]
    )
    strategy.main()
    zero_trades_path = tmp_path / "zero_trades.csv"
    assert pd.read_csv(zero_summary_path).loc[0, "n_trades"] == 0
    assert zero_trades_path.read_text(encoding="utf-8").splitlines() == [
        ",".join(_TRADE_COLUMNS)
    ]


def test_parameter_contract_is_exposed() -> None:
    validate_strategy_vwap_recovery_params()
    with pytest.raises(ValueError):
        validate_strategy_vwap_recovery_params(
            replace(STRATEGY_VWAP_RECOVERY_PARAMS, vwap_window=0)
        )


def test_runner_rejects_timezone_bound_mismatch() -> None:
    frame, _ = _recovery_frame()
    frame.index = frame.index.tz_localize("UTC")
    with pytest.raises(ValueError, match="timezone"):
        run_vwap_recovery_backtest({"T": frame}, start="2024-01-01")


def test_reference_baseline_bounds_are_declared() -> None:
    assert str(BASELINE_START.date()) == "2020-08-03"
    assert str(BASELINE_END.date()) == "2026-08-27"
