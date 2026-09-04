"""전략 E 계산·고정 청산 회귀 테스트."""

from dataclasses import replace
import sys

import numpy as np
import pandas as pd
import pytest

import backtest.indicator_opt.strategy_e as strategy_e
from backtest.engine import (
    EXIT_MAX_HOLD,
    EXIT_SL,
    Trade,
    TradeParams,
    run_backtest,
)
from backtest.indicator_opt._signals import SimpleSignal
from backtest.indicator_opt.strategy_e import (
    BASELINE_END,
    BASELINE_START,
    STRATEGY_E_PARAMS,
    _TRADE_COLUMNS,
    _baseline_row,
    compute_strategy_e,
    run_strategy_e_backtest,
    strategy_e_signals,
    validate_strategy_e_params,
)
from backtest.indicators import adx


SIGNAL_POSITION = 61


def _strategy_e_frame(n: int = 160) -> pd.DataFrame:
    """SMA GC·OBV GC·ADX 조건이 61번째 봉에서 함께 성립하는 고정 fixture."""

    close = np.r_[
        np.linspace(100.0, 80.0, SIGNAL_POSITION),
        [280.0],
        np.full(n - SIGNAL_POSITION - 1, 280.0),
    ]
    volume = np.full(n, 1_000.0)
    volume[SIGNAL_POSITION] = 1_000_000.0
    return pd.DataFrame(
        {
            "Open": close,
            "High": close + 1.0,
            "Low": close - 1.0,
            "Close": close,
            "Volume": volume,
        },
        index=pd.date_range("2024-01-01", periods=n, freq="B"),
    )


def _install_controlled_filters(
    monkeypatch: pytest.MonkeyPatch,
    frame: pd.DataFrame,
    obv_cross: bool = True,
    adx_value: float = 30.0,
) -> None:
    values = np.zeros(len(frame))
    if obv_cross:
        values[SIGNAL_POSITION:] = 1.0
    monkeypatch.setattr(
        strategy_e,
        "obv",
        lambda close, volume: pd.Series(values, index=frame.index),
    )
    monkeypatch.setattr(
        strategy_e,
        "adx",
        lambda high, low, close, window: pd.Series(
            adx_value, index=frame.index, dtype=float
        ),
    )


def test_strategy_e_returns_bool_mask_and_all_three_conditions() -> None:
    frame = _strategy_e_frame()

    mask = compute_strategy_e(frame)

    assert mask.index.equals(frame.index)
    assert mask.dtype == bool
    assert bool(mask.iloc[SIGNAL_POSITION])


@pytest.mark.parametrize("condition", ["sma", "obv", "adx"])
def test_each_entry_condition_is_required(
    condition: str, monkeypatch: pytest.MonkeyPatch
) -> None:
    frame = _strategy_e_frame()
    _install_controlled_filters(monkeypatch, frame)
    assert compute_strategy_e(frame).iloc[SIGNAL_POSITION]

    if condition == "sma":
        frame.iloc[SIGNAL_POSITION, frame.columns.get_loc("Close")] = 80.0
        frame.iloc[SIGNAL_POSITION, frame.columns.get_loc("Open")] = 80.0
        frame.iloc[SIGNAL_POSITION, frame.columns.get_loc("High")] = 81.0
        frame.iloc[SIGNAL_POSITION, frame.columns.get_loc("Low")] = 79.0
    elif condition == "obv":
        _install_controlled_filters(monkeypatch, frame, obv_cross=False)
    else:
        _install_controlled_filters(monkeypatch, frame, adx_value=19.999)

    assert not compute_strategy_e(frame).iloc[SIGNAL_POSITION]


def test_adx_uses_wilder_seed_and_recursive_smoothing() -> None:
    high = pd.Series([10.0, 12.0, 13.0, 15.0, 14.0, 16.0, 17.0, 16.0, 18.0, 19.0])
    low = pd.Series([8.0, 9.0, 10.0, 11.0, 10.0, 12.0, 13.0, 12.0, 14.0, 15.0])
    close = pd.Series([9.0, 11.0, 12.0, 14.0, 11.0, 15.0, 16.0, 13.0, 17.0, 18.0])

    actual = adx(high, low, close, window=3)

    assert actual.iloc[:5].isna().all()
    np.testing.assert_allclose(
        actual.iloc[5:].to_numpy(),
        [
            75.5244755245,
            76.7264619439,
            61.9762693774,
            62.0154671902,
            65.1693380589,
        ],
        rtol=0,
        atol=1e-10,
    )


@pytest.mark.parametrize("window", [True, 14.0, 0, -1])
def test_adx_rejects_invalid_window(window: object) -> None:
    values = pd.Series([1.0, 2.0, 3.0])

    with pytest.raises(ValueError, match="window"):
        adx(values, values, values, window=window)


def test_adx_threshold_includes_exactly_20(monkeypatch: pytest.MonkeyPatch) -> None:
    frame = _strategy_e_frame()
    _install_controlled_filters(monkeypatch, frame, adx_value=20.0)

    assert compute_strategy_e(frame).iloc[SIGNAL_POSITION]


def test_sma_and_obv_cross_accept_previous_equal_values(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    frame = _strategy_e_frame()
    _install_controlled_filters(monkeypatch, frame, adx_value=20.0)
    calls = 0

    def sma_with_equal_previous(series: pd.Series, window: int) -> pd.Series:
        nonlocal calls
        calls += 1
        values = np.zeros(len(frame))
        if calls == 1:
            values[SIGNAL_POSITION:] = 1.0
        return pd.Series(values, index=frame.index)

    monkeypatch.setattr(strategy_e, "sma", sma_with_equal_previous)
    mask = compute_strategy_e(frame)

    assert mask.iloc[SIGNAL_POSITION]
    assert calls == 3


def test_insufficient_history_is_false_and_preserves_index() -> None:
    frame = _strategy_e_frame().iloc[:59].copy()

    mask = compute_strategy_e(frame)

    assert mask.index.equals(frame.index)
    assert mask.dtype == bool
    assert not mask.any()


def test_future_values_do_not_change_past_signal() -> None:
    frame = _strategy_e_frame()
    expected = compute_strategy_e(frame)
    mutated = frame.copy()
    mutated.iloc[SIGNAL_POSITION + 1, mutated.columns.get_loc("High")] = 1e9
    mutated.iloc[SIGNAL_POSITION + 1, mutated.columns.get_loc("Close")] = 1e9
    mutated.iloc[SIGNAL_POSITION + 1, mutated.columns.get_loc("Volume")] = 1e12

    actual = compute_strategy_e(mutated)

    pd.testing.assert_series_equal(
        actual.iloc[: SIGNAL_POSITION + 1], expected.iloc[: SIGNAL_POSITION + 1]
    )


def test_strategy_e_signals_have_fixed_exit_parameters() -> None:
    frame = _strategy_e_frame()

    signals = strategy_e_signals(frame, ticker="T")

    signal = next(item for item in signals if item.date == frame.index[SIGNAL_POSITION])
    assert signal.price == pytest.approx(frame["Close"].iloc[SIGNAL_POSITION])
    assert signal.take_profit_pct == STRATEGY_E_PARAMS.take_profit_pct
    assert signal.stop_price == pytest.approx(signal.price * 0.95)


def _exit_fixture() -> pd.DataFrame:
    n = 33
    close = np.full(n, 100.0)
    return pd.DataFrame(
        {
            "Open": close,
            "High": close + 1.0,
            "Low": close - 1.0,
            "Close": close,
            "Volume": np.full(n, 1_000.0),
        },
        index=pd.date_range("2025-01-01", periods=n, freq="B"),
    )


def _fixed_signal(frame: pd.DataFrame) -> SimpleSignal:
    return SimpleSignal(
        ticker="T",
        date=frame.index[1],
        price=100.0,
        stop_price=95.0,
        take_profit_pct=2.0,
    )


def test_exit_boundary_is_sl_first_when_tp_and_sl_are_both_reached() -> None:
    frame = _exit_fixture()
    frame.iloc[2, frame.columns.get_loc("High")] = 103.0
    frame.iloc[2, frame.columns.get_loc("Low")] = 94.0

    trades = run_backtest(
        frame,
        [_fixed_signal(frame)],
        TradeParams(atr_window=1, cost_rate=STRATEGY_E_PARAMS.cost_rate, max_holding_bars=30),
        ticker="T",
    )

    assert len(trades) == 1
    assert trades[0].exit_reason == EXIT_SL
    assert trades[0].exit_price == pytest.approx(95.0)


def test_exit_boundary_uses_thirtieth_bar_close_for_max_hold() -> None:
    frame = _exit_fixture()
    frame.iloc[31, frame.columns.get_loc("Close")] = 101.0

    trades = run_backtest(
        frame,
        [_fixed_signal(frame)],
        TradeParams(atr_window=1, cost_rate=0.0, max_holding_bars=30),
        ticker="T",
    )

    assert len(trades) == 1
    assert trades[0].exit_reason == EXIT_MAX_HOLD
    assert trades[0].exit_date == frame.index[31]
    assert trades[0].holding_bars == 30
    assert trades[0].exit_price == pytest.approx(101.0)


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("sma_short_window", 60),
        ("sma_long_window", 0),
        ("obv_window", 1.5),
        ("adx_window", True),
        ("adx_threshold", np.inf),
        ("adx_threshold", 100.1),
        ("take_profit_pct", 0),
        ("stop_loss_pct", -1),
        ("stop_loss_pct", 100),
        ("max_holding_bars", 0),
        ("cost_rate", -0.01),
    ],
)
def test_invalid_strategy_parameters_are_rejected(field: str, value: object) -> None:
    params = replace(STRATEGY_E_PARAMS, **{field: value})

    with pytest.raises(ValueError):
        validate_strategy_e_params(params)


@pytest.mark.parametrize("mutation", ["duplicate", "ohlc", "negative_volume"])
def test_strategy_e_frame_contract_is_rejected(mutation: str) -> None:
    frame = _strategy_e_frame()
    if mutation == "duplicate":
        frame.columns = ["Open", "High", "Low", "Close", "Close"]
    elif mutation == "ohlc":
        frame.iloc[10, frame.columns.get_loc("High")] = 1.0
    else:
        frame.iloc[10, frame.columns.get_loc("Volume")] = -1.0

    with pytest.raises(ValueError):
        compute_strategy_e(frame)


def test_invalid_input_contract_is_explicit() -> None:
    frame = _strategy_e_frame().drop(columns="Volume")

    with pytest.raises(ValueError, match="OHLCV 컬럼"):
        compute_strategy_e(frame)


def test_runner_uses_non_default_strategy_e_parameters(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    frame = _strategy_e_frame()
    captured: dict[str, object] = {}
    params = replace(
        STRATEGY_E_PARAMS,
        adx_threshold=25.0,
        take_profit_pct=3.0,
        stop_loss_pct=4.0,
        max_holding_bars=7,
        cost_rate=0.001,
    )

    def spy_run_backtest(frame, signals, trade_params, ticker=""):
        captured["signals"] = signals
        captured["trade_params"] = trade_params
        return []

    monkeypatch.setattr(strategy_e, "run_backtest", spy_run_backtest)
    result = run_strategy_e_backtest({"T": frame}, params=params)

    assert result["params"] == params.as_dict()
    assert captured["trade_params"].cost_rate == 0.001
    assert captured["trade_params"].max_holding_bars == 7
    signal = next(
        item for item in captured["signals"] if item.date == frame.index[SIGNAL_POSITION]
    )
    assert signal.take_profit_pct == 3.0
    assert signal.stop_price == pytest.approx(signal.price * 0.96)


def test_runner_uses_pre_start_history_for_warmup() -> None:
    frame = _strategy_e_frame()

    result = run_strategy_e_backtest(
        {"T": frame},
        start=frame.index[SIGNAL_POSITION],
        end=frame.index[100],
    )

    assert result["n_signals"] == 1
    assert result["n_trades"] == 1
    assert result["trades"][0]["entry_date"] == str(
        frame.index[SIGNAL_POSITION].date()
    )


def test_runner_applies_start_end_to_signals_and_trades(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    frame = _strategy_e_frame()
    dates = [frame.index[position] for position in (60, 61, 90, 91)]

    def fake_signals(segment, ticker="", params=STRATEGY_E_PARAMS):
        return [
            SimpleSignal(
                ticker=ticker,
                date=date,
                price=100.0,
                stop_price=95.0,
                take_profit_pct=2.0,
            )
            for date in dates
            if date in segment.index
        ]

    def fake_run_backtest(segment, signals, trade_params, ticker=""):
        assert all(
            frame.index[61] <= signal.date <= frame.index[90]
            for signal in signals
        )
        return [
            Trade(
                ticker=ticker,
                entry_date=signal.date,
                exit_date=signal.date,
                entry_price=signal.price,
                exit_price=signal.price + 1.0,
                return_pct=1.0,
                holding_bars=0,
                exit_reason="tp",
            )
            for signal in signals
        ]

    monkeypatch.setattr(strategy_e, "strategy_e_signals", fake_signals)
    monkeypatch.setattr(strategy_e, "run_backtest", fake_run_backtest)
    result = run_strategy_e_backtest(
        {"T": frame}, start=frame.index[61], end=frame.index[90]
    )

    assert result["n_signals"] == 2
    assert [trade["entry_date"] for trade in result["trades"]] == [
        str(frame.index[61].date()),
        str(frame.index[90].date()),
    ]


def test_runner_excludes_invalid_rows_and_splits_segments(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    frame = _strategy_e_frame()
    frame.iloc[30, frame.columns.get_loc("Close")] = np.nan
    segments: list[pd.DataFrame] = []

    def spy_run_backtest(segment, signals, trade_params, ticker=""):
        segments.append(segment)
        return []

    monkeypatch.setattr(strategy_e, "run_backtest", spy_run_backtest)
    result = run_strategy_e_backtest({"T": frame})

    assert result["invalid_ohlcv_rows"] == 1
    assert result["n_signals"] == 0
    assert [len(segment) for segment in segments] == [30, 129]
    assert all(np.isfinite(segment.to_numpy(dtype=float)).all() for segment in segments)


def test_runner_fingerprint_includes_invalid_rows() -> None:
    invalid = _strategy_e_frame()
    invalid.iloc[30, invalid.columns.get_loc("Close")] = np.nan
    changed_invalid = invalid.copy()
    changed_invalid.iloc[30, changed_invalid.columns.get_loc("Volume")] = 999.0

    first = run_strategy_e_backtest({"T": invalid})
    second = run_strategy_e_backtest({"T": changed_invalid})

    assert first["invalid_ohlcv_rows"] == second["invalid_ohlcv_rows"] == 1
    assert first["data_fingerprint"] != second["data_fingerprint"]
    assert first["n_signals"] == second["n_signals"] == 0


def test_runner_is_invariant_to_dictionary_order() -> None:
    first_frame = _strategy_e_frame()
    second_frame = _strategy_e_frame().copy()
    data_one = {"B": second_frame, "A": first_frame}
    data_two = {"A": first_frame, "B": second_frame}

    first = run_strategy_e_backtest(data_one)
    second = run_strategy_e_backtest(data_two)

    assert first["data_fingerprint"] == second["data_fingerprint"]
    assert first["trades"] == second["trades"]
    assert [
        (trade["entry_date"], trade["ticker"])
        for trade in first["trades"]
    ] == sorted(
        (trade["entry_date"], trade["ticker"])
        for trade in first["trades"]
    )


def test_runner_rejects_timezone_bound_mismatch() -> None:
    frame = _strategy_e_frame()
    frame.index = frame.index.tz_localize("UTC")

    with pytest.raises(ValueError, match="timezone"):
        run_strategy_e_backtest({"T": frame}, start="2024-01-01")


def test_cli_writes_nonempty_and_zero_trade_csv_headers(
    monkeypatch: pytest.MonkeyPatch, tmp_path
) -> None:
    frame = _strategy_e_frame()
    monkeypatch.setattr(strategy_e, "load_all", lambda: {"T": frame})

    summary_path = tmp_path / "summary.csv"
    monkeypatch.setattr(
        sys,
        "argv",
        [
            "strategy_e",
            "--output",
            str(summary_path),
            "--start",
            frame.index[61].date().isoformat(),
            "--end",
            frame.index[100].date().isoformat(),
        ],
    )
    strategy_e.main()
    trades_path = summary_path.with_name("summary_trades.csv")

    assert pd.read_csv(summary_path).loc[0, "n_trades"] == 1
    assert list(pd.read_csv(trades_path).columns) == list(_TRADE_COLUMNS)
    assert len(pd.read_csv(trades_path)) == 1

    zero_summary_path = tmp_path / "zero.csv"
    monkeypatch.setattr(
        sys,
        "argv",
        [
            "strategy_e",
            "--output",
            str(zero_summary_path),
            "--start",
            frame.index[0].date().isoformat(),
            "--end",
            frame.index[60].date().isoformat(),
        ],
    )
    strategy_e.main()
    zero_trades_path = zero_summary_path.with_name("zero_trades.csv")

    assert pd.read_csv(zero_summary_path).loc[0, "n_trades"] == 0
    assert zero_trades_path.read_text(encoding="utf-8").splitlines() == [
        ",".join(_TRADE_COLUMNS)
    ]


def test_runner_records_fixed_window_and_flattened_params() -> None:
    result = run_strategy_e_backtest(
        {"T": _strategy_e_frame()}, start=BASELINE_START, end=BASELINE_END
    )
    row = _baseline_row(result)

    assert result["data_window_start"] == "2020-08-03"
    assert result["data_window_end"] == "2026-08-27"
    assert row["param_sma_short_window"] == 20
    assert row["param_sma_long_window"] == 60
    assert row["param_obv_window"] == 20
    assert row["param_adx_window"] == 14
    assert row["param_adx_threshold"] == 20.0
    assert row["param_take_profit_pct"] == 2.0
    assert row["param_stop_loss_pct"] == 5.0
    assert row["param_max_holding_bars"] == 30
    assert row["param_cost_rate"] == 0.0005
