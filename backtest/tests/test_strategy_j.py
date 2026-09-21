"""전략 J(VWAP 지지) 계산·고정 청산 회귀 테스트."""

from dataclasses import replace
import sys

import numpy as np
import pandas as pd
import pytest

import backtest.indicator_opt.strategy_j as strategy_j
from backtest.engine import EXIT_SL, EXIT_TP, TradeParams, run_backtest
from backtest.indicator_opt.strategy_j import (
    BASELINE_END,
    BASELINE_START,
    CANDIDATE_A,
    STRATEGY_J_PARAMS,
    _TRADE_COLUMNS,
    _baseline_row,
    compute_strategy_j,
    rolling_vwap,
    run_strategy_j_backtest,
    strategy_j_signals,
    validate_strategy_j_params,
)
from backtest.indicator_opt._signals import SimpleSignal


def _flat_vwap_frame(n: int = 60) -> pd.DataFrame:
    """거래량 균일 → VWAP == 당일 typical price 롤링 평균과 근접한 평탄 프레임."""

    dates = pd.date_range("2024-01-01", periods=n, freq="B")
    close = np.full(n, 100.0)
    return pd.DataFrame(
        {
            "Open": close,
            "High": close + 1.0,
            "Low": close - 1.0,
            "Close": close,
            "Volume": np.full(n, 100.0),
        },
        index=dates,
    )


def _strategy_j_frame(window: int = 20) -> tuple[pd.DataFrame, int]:
    """VWAP 지지(전일 위 마감 → 당일 저가 근접 → 당일 위 마감)가 한 번 나오는 프레임.

    베이스 구간의 저가(95.0)는 VWAP(~98.5) 대비 band 밖에 멀리 있어 신호가 발화하지
    않고, 신호 봉만 저가를 VWAP band 안으로 눌렀다가 VWAP 위에서 마감시킨다.
    """

    n = window + 40
    dates = pd.date_range("2024-01-01", periods=n, freq="B")
    frame = pd.DataFrame(
        {
            "Open": 100.0,
            "High": 100.5,
            "Low": 95.0,
            "Close": 100.0,
            "Volume": 100.0,
        },
        index=dates,
    )
    signal_position = window + 10

    open_col = frame.columns.get_loc("Open")
    high_col = frame.columns.get_loc("High")
    low_col = frame.columns.get_loc("Low")
    close_col = frame.columns.get_loc("Close")

    # 신호 봉: 저가가 VWAP band 안까지 눌렸다가 VWAP 위에서 마감
    frame.iloc[signal_position, open_col] = 100.0
    frame.iloc[signal_position, low_col] = 99.8
    frame.iloc[signal_position, high_col] = 101.5
    frame.iloc[signal_position, close_col] = 101.0

    return frame, signal_position


def test_strategy_j_returns_bool_mask_and_one_signal() -> None:
    frame, signal_position = _strategy_j_frame(CANDIDATE_A.vwap_window)

    mask = compute_strategy_j(frame)

    assert mask.index.equals(frame.index)
    assert mask.dtype == bool
    assert bool(mask.iloc[signal_position])
    assert int(mask.sum()) == 1


def test_rolling_vwap_uses_typical_price_volume_weighting() -> None:
    n = 10
    frame = pd.DataFrame(
        {
            "Open": [100.0] * n,
            "High": [102.0] * n,
            "Low": [98.0] * n,
            "Close": [100.0] * n,
            "Volume": [100.0] * n,
        },
        index=pd.date_range("2024-01-01", periods=n, freq="B"),
    )
    vwap = rolling_vwap(frame, window=5)
    typical = (102.0 + 98.0 + 100.0) / 3.0
    assert vwap.iloc[4] == pytest.approx(typical)
    assert pd.isna(vwap.iloc[3])


def test_prev_close_above_vwap_is_required() -> None:
    frame, signal_position = _strategy_j_frame(CANDIDATE_A.vwap_window)
    assert compute_strategy_j(frame).iloc[signal_position]

    vwap = rolling_vwap(frame, CANDIDATE_A.vwap_window)
    prev_pos = signal_position - 1
    close_col = frame.columns.get_loc("Close")
    low_col = frame.columns.get_loc("Low")
    below_vwap = float(vwap.iloc[prev_pos] - 1.0)
    frame.iloc[prev_pos, low_col] = min(frame.iloc[prev_pos, low_col], below_vwap)
    frame.iloc[prev_pos, close_col] = below_vwap

    assert not compute_strategy_j(frame).iloc[signal_position]


def test_low_must_be_within_band_of_vwap() -> None:
    frame, signal_position = _strategy_j_frame(CANDIDATE_A.vwap_window)
    assert compute_strategy_j(frame).iloc[signal_position]

    low_col = frame.columns.get_loc("Low")
    frame.iloc[signal_position, low_col] = 80.0  # VWAP 대비 훨씬 아래로 이탈

    assert not compute_strategy_j(frame).iloc[signal_position]
    relaxed = compute_strategy_j(
        frame, replace(CANDIDATE_A, vwap_band_pct=25.0)
    )
    assert relaxed.iloc[signal_position]


def test_close_must_finish_above_vwap() -> None:
    frame, signal_position = _strategy_j_frame(CANDIDATE_A.vwap_window)
    assert compute_strategy_j(frame).iloc[signal_position]

    vwap = rolling_vwap(frame, CANDIDATE_A.vwap_window)
    close_col = frame.columns.get_loc("Close")
    low_col = frame.columns.get_loc("Low")
    below_vwap = float(vwap.iloc[signal_position] - 0.5)
    frame.iloc[signal_position, low_col] = min(frame.iloc[signal_position, low_col], below_vwap)
    frame.iloc[signal_position, close_col] = below_vwap

    assert not compute_strategy_j(frame).iloc[signal_position]


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("vwap_window", 1.5),
        ("vwap_window", 0),
        ("vwap_band_pct", 0.0),
        ("vwap_band_pct", 60.0),
        ("take_profit_pct", 0),
        ("take_profit_pct", float("inf")),
        ("stop_loss_pct", -1),
        ("stop_loss_pct", 100),
        ("tp_first", "yes"),
        ("max_holding_bars", 0),
        ("max_holding_bars", 1.5),
        ("cost_rate", -0.01),
    ],
)
def test_invalid_strategy_parameters_are_rejected(field: str, value) -> None:
    frame, _ = _strategy_j_frame(CANDIDATE_A.vwap_window)
    params = replace(CANDIDATE_A, **{field: value})

    with pytest.raises(ValueError):
        compute_strategy_j(frame, params)


@pytest.mark.parametrize("mutation", ["duplicate", "ohlc", "negative_volume"])
def test_strategy_j_frame_contract_is_rejected(mutation: str) -> None:
    frame, _ = _strategy_j_frame(CANDIDATE_A.vwap_window)
    if mutation == "duplicate":
        frame.columns = ["Open", "High", "Low", "Close", "Close"]
    elif mutation == "ohlc":
        frame.iloc[10, frame.columns.get_loc("High")] = 1.0
    else:
        frame.iloc[10, frame.columns.get_loc("Volume")] = -1.0

    with pytest.raises(ValueError):
        compute_strategy_j(frame)


def test_insufficient_history_is_safe_and_silent() -> None:
    frame, _ = _strategy_j_frame(CANDIDATE_A.vwap_window)
    frame = frame.iloc[: CANDIDATE_A.vwap_window].copy()

    mask = compute_strategy_j(frame)

    assert mask.index.equals(frame.index)
    assert mask.dtype == bool
    assert not mask.any()


def test_invalid_input_contract_is_explicit() -> None:
    frame, _ = _strategy_j_frame(CANDIDATE_A.vwap_window)
    frame = frame.drop(columns="Volume")

    with pytest.raises(ValueError, match="OHLCV 컬럼"):
        compute_strategy_j(frame)


def test_future_ohlcv_changes_do_not_change_past_signal() -> None:
    frame, signal_position = _strategy_j_frame(CANDIDATE_A.vwap_window)
    expected = compute_strategy_j(frame)
    mutated = frame.copy()
    mutated.iloc[signal_position + 1, mutated.columns.get_loc("High")] = 1e9
    mutated.iloc[signal_position + 1, mutated.columns.get_loc("Volume")] = 1e12

    actual = compute_strategy_j(mutated)

    pd.testing.assert_series_equal(
        actual.iloc[: signal_position + 1], expected.iloc[: signal_position + 1]
    )


def test_strategy_j_signals_use_fixed_exit_parameters() -> None:
    frame, signal_position = _strategy_j_frame(CANDIDATE_A.vwap_window)

    signals = strategy_j_signals(frame, ticker="T")

    signal = next(item for item in signals if item.date == frame.index[signal_position])
    vwap = rolling_vwap(frame, CANDIDATE_A.vwap_window)
    assert signal.price == pytest.approx(frame["Close"].iloc[signal_position])
    assert signal.take_profit_pct == CANDIDATE_A.take_profit_pct
    assert signal.stop_price == pytest.approx(
        vwap.iloc[signal_position] * (1.0 - CANDIDATE_A.stop_loss_pct / 100.0)
    )


def test_engine_exits_next_day_tp_or_forced_close() -> None:
    frame = pd.DataFrame(
        {
            "Open": [100.0, 100.0, 100.0, 100.0],
            "High": [101.0, 101.0, 105.0, 101.0],
            "Low": [99.0, 99.0, 99.0, 99.0],
            "Close": [100.0, 100.0, 103.0, 100.0],
            "Volume": [1000.0] * 4,
        },
        index=pd.date_range("2025-01-01", periods=4, freq="B"),
    )
    signal = SimpleSignal("T", frame.index[1], 100.0, stop_price=95.0, take_profit_pct=4.0)

    trades = run_backtest(
        frame,
        [signal],
        TradeParams(atr_window=1, max_holding_bars=1, tp_first=True, cost_rate=0.0),
        ticker="T",
    )

    assert trades[0].exit_reason == EXIT_TP
    assert trades[0].exit_price == pytest.approx(104.0)


def test_engine_forces_exit_after_one_bar_when_no_tp_sl_hit() -> None:
    frame = pd.DataFrame(
        {
            "Open": [100.0, 100.0, 100.0, 100.0],
            "High": [101.0, 101.0, 101.5, 101.0],
            "Low": [99.0, 99.0, 99.5, 99.0],
            "Close": [100.0, 100.0, 101.0, 100.0],
            "Volume": [1000.0] * 4,
        },
        index=pd.date_range("2025-01-01", periods=4, freq="B"),
    )
    signal = SimpleSignal("T", frame.index[1], 100.0, stop_price=95.0, take_profit_pct=4.0)

    trades = run_backtest(
        frame,
        [signal],
        TradeParams(atr_window=1, max_holding_bars=1, tp_first=True, cost_rate=0.0),
        ticker="T",
    )

    assert trades[0].exit_date == frame.index[2]
    assert trades[0].exit_price == pytest.approx(101.0)


def test_runner_records_fixed_observation_window_and_flattened_params() -> None:
    frame, _ = _strategy_j_frame(CANDIDATE_A.vwap_window)

    result = run_strategy_j_backtest({"T": frame}, start=BASELINE_START, end=BASELINE_END)
    row = _baseline_row(result)

    assert result["strategy"] == "J"
    assert row["param_vwap_window"] == 20
    assert row["param_vwap_band_pct"] == 2.0
    assert row["param_take_profit_pct"] == 3.0
    assert row["param_stop_loss_pct"] == 5.0
    assert row["param_max_holding_bars"] == 1
    assert row["param_tp_first"] is True
    assert row["param_cost_rate"] == 0.0005
    assert result["params"] == STRATEGY_J_PARAMS.as_dict()


def test_runner_excludes_invalid_rows_and_splits_segments(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    frame, _ = _strategy_j_frame(CANDIDATE_A.vwap_window)
    frame.iloc[30, frame.columns.get_loc("Close")] = np.nan
    segments: list[pd.DataFrame] = []

    def spy_run_backtest(segment, signals, trade_params, ticker=""):
        segments.append(segment)
        return []

    monkeypatch.setattr(strategy_j, "run_backtest", spy_run_backtest)
    result = run_strategy_j_backtest({"T": frame})

    assert result["invalid_ohlcv_rows"] == 1
    assert [len(segment) for segment in segments] == [30, len(frame) - 31]


def test_runner_is_invariant_to_dictionary_order() -> None:
    frame_a, _ = _strategy_j_frame(CANDIDATE_A.vwap_window)
    frame_b, _ = _strategy_j_frame(CANDIDATE_A.vwap_window)
    frame_b = frame_b.set_axis(
        pd.date_range("2024-06-01", periods=len(frame_b), freq="B")
    )
    data_one = {"B": frame_b, "A": frame_a}
    data_two = {"A": frame_a, "B": frame_b}

    first = run_strategy_j_backtest(data_one)
    second = run_strategy_j_backtest(data_two)

    assert first["data_fingerprint"] == second["data_fingerprint"]
    assert first["trades"] == second["trades"]


def test_runner_rejects_timezone_bound_mismatch() -> None:
    frame, _ = _strategy_j_frame(CANDIDATE_A.vwap_window)
    frame.index = frame.index.tz_localize("UTC")

    with pytest.raises(ValueError, match="timezone"):
        run_strategy_j_backtest({"T": frame}, start="2024-01-01")


def test_cli_writes_nonempty_and_zero_trade_csv_headers(
    monkeypatch: pytest.MonkeyPatch, tmp_path
) -> None:
    frame, _ = _strategy_j_frame(CANDIDATE_A.vwap_window)
    monkeypatch.setattr(strategy_j, "load_all", lambda: {"T": frame})

    summary_path = tmp_path / "summary.csv"
    monkeypatch.setattr(
        sys,
        "argv",
        [
            "strategy_j",
            "--output",
            str(summary_path),
            "--start",
            frame.index[0].date().isoformat(),
            "--end",
            frame.index[-1].date().isoformat(),
        ],
    )
    strategy_j.main()
    trades_path = summary_path.with_name("summary_trades.csv")

    assert pd.read_csv(summary_path).loc[0, "n_trades"] >= 1
    assert list(pd.read_csv(trades_path).columns) == list(_TRADE_COLUMNS)

    zero_summary_path = tmp_path / "zero.csv"
    monkeypatch.setattr(
        sys,
        "argv",
        [
            "strategy_j",
            "--output",
            str(zero_summary_path),
            "--start",
            frame.index[0].date().isoformat(),
            "--end",
            frame.index[10].date().isoformat(),
        ],
    )
    strategy_j.main()
    zero_trades_path = zero_summary_path.with_name("zero_trades.csv")

    assert pd.read_csv(zero_summary_path).loc[0, "n_trades"] == 0
    assert zero_trades_path.read_text(encoding="utf-8").splitlines() == [
        ",".join(_TRADE_COLUMNS)
    ]


def test_validate_strategy_j_params_exposes_contract() -> None:
    validate_strategy_j_params(STRATEGY_J_PARAMS)
    with pytest.raises(ValueError):
        validate_strategy_j_params(replace(STRATEGY_J_PARAMS, vwap_window=0))
