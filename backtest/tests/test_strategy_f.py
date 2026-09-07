"""전략 F(가속·이평선 쌍바닥) 계산·고정 청산 회귀 테스트."""

from dataclasses import replace
import sys

import numpy as np
import pandas as pd
import pytest

import backtest.indicator_opt.strategy_f as strategy_f
from backtest.engine import (
    EXIT_MAX_HOLD,
    EXIT_SL,
    EXIT_TP,
    Trade,
    TradeParams,
    run_backtest,
)
from backtest.indicator_opt._signals import SimpleSignal
from backtest.indicator_opt.strategy_f import (
    BASELINE_END,
    BASELINE_START,
    STRATEGY_F_PARAMS,
    _TRADE_COLUMNS,
    _baseline_row,
    compute_strategy_f,
    run_strategy_f_backtest,
    strategy_f_signals,
    validate_strategy_f_params,
)

SIGNAL_POSITION = 174


def _strategy_f_frame(n: int = 200) -> pd.DataFrame:
    """가속·쌍바닥 조건이 성립하지 않는 순수 상승 추세 fixture (형태/검증 테스트 전용)."""

    t = np.arange(n, dtype=float)
    close = 50.0 + 0.12 * t + 2.0 * np.sin(t / 3.0)
    close = np.maximum(close, 1.0)
    return pd.DataFrame(
        {
            "Open": close,
            "High": close + 0.5,
            "Low": close - 0.5,
            "Close": close,
            "Volume": np.full(n, 1_000.0),
        },
        index=pd.date_range("2024-01-01", periods=n, freq="B"),
    )


def _signal_frame(n: int = 260) -> pd.DataFrame:
    """가속(각도 가속) AND 쌍바닥(이평선) 두 조건이 실제로 동시 충족되는 fixture.

    0~99봉: 완만한 상승. 100~179봉: 쌍바닥(1저점 → 넥라인 → 2저점(higher low)
    → 가속 돌파) 패턴. 180~259봉: 로그수익률이 선형으로 커지는 추가 가속 랠리.
    `SIGNAL_POSITION`(174)에서 이평선(MA16) 쌍바닥 넥라인 돌파와 로그가격
    최소제곱 기울기 가속이 동시에 성립해 전략 F 시그널이 발생한다.
    """

    close = np.empty(n, dtype=float)
    close[:100] = 100.0 + 0.02 * np.arange(100)

    dip_len = 80
    delay = 6
    seg = np.zeros(dip_len)
    seg[0:20] = -np.linspace(0.0, 8.0, 20)  # 1저점(-8)
    seg[20:40] = -8.0 + np.linspace(0.0, 5.0, 20)  # 넥라인(-3)
    seg[40:60] = -3.0 - np.linspace(0.0, 4.0, 20)  # 2저점(-7, 1저점보다 높은 저점)
    seg[60 : 60 + delay] = -7.0
    ramp_len = dip_len - 60 - delay
    seg[60 + delay : 80] = -7.0 + np.linspace(0.0, 1.0, ramp_len) ** 2 * 60.0  # 가속 돌파
    close[100:180] = close[99] + seg

    daily_log_return = np.linspace(0.01, 0.05, n - 180)
    close[180:] = close[179] * np.exp(np.cumsum(daily_log_return))

    return pd.DataFrame(
        {
            "Open": close,
            "High": close + 0.5,
            "Low": close - 0.5,
            "Close": close,
            "Volume": np.full(n, 1_000.0),
        },
        index=pd.date_range("2024-01-01", periods=n, freq="B"),
    )


def test_strategy_f_returns_bool_mask_and_preserves_index() -> None:
    frame = _strategy_f_frame()

    mask = compute_strategy_f(frame)

    assert mask.index.equals(frame.index)
    assert mask.dtype == bool


def test_strategy_f_fires_when_accel_and_double_bottom_coincide() -> None:
    frame = _signal_frame()

    mask = compute_strategy_f(frame)

    assert mask.iloc[SIGNAL_POSITION]
    assert mask.sum() == 1


def test_strategy_f_plain_uptrend_never_fires() -> None:
    mask = compute_strategy_f(_strategy_f_frame())

    assert not mask.any()


def test_future_values_do_not_change_past_signal() -> None:
    frame = _signal_frame()
    expected = compute_strategy_f(frame)

    mutated = frame.copy()
    future = slice(SIGNAL_POSITION + 1, None)
    mutated.loc[mutated.index[future], ["Open", "High", "Low", "Close"]] *= 5.0

    actual = compute_strategy_f(mutated)

    assert actual.iloc[: SIGNAL_POSITION + 1].equals(expected.iloc[: SIGNAL_POSITION + 1])


def test_insufficient_history_is_false_and_preserves_index() -> None:
    frame = _strategy_f_frame().iloc[:29].copy()

    mask = compute_strategy_f(frame)

    assert mask.index.equals(frame.index)
    assert mask.dtype == bool
    assert not mask.any()


def test_strategy_f_requires_slope_greater_than_accel_window() -> None:
    params = replace(STRATEGY_F_PARAMS, slope_window=3, accel_window=5)

    with pytest.raises(ValueError, match="slope_window"):
        compute_strategy_f(_strategy_f_frame(), params)


def test_strategy_f_invalid_parameters_are_rejected() -> None:
    bad = [
        ("slope_window", 1),
        ("accel_window", 0),
        ("ma_db_window", True),
        ("min_slope_delta", 0),
        ("take_profit_pct", 0),
        ("stop_loss_pct", 100),
        ("cost_rate", -0.01),
        ("tp_first", "yes"),
    ]

    for field, value in bad:
        params = replace(STRATEGY_F_PARAMS, **{field: value})
        with pytest.raises(ValueError):
            validate_strategy_f_params(params)


def test_strategy_f_signals_have_fixed_exit_parameters() -> None:
    frame = _signal_frame()
    params = replace(STRATEGY_F_PARAMS)
    signals = strategy_f_signals(frame, ticker="T", params=params)

    assert len(signals) == 1
    for signal in signals:
        assert signal.take_profit_pct == params.take_profit_pct
        assert signal.stop_price == pytest.approx(signal.price * 0.96)


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
        stop_price=96.0,
        take_profit_pct=3.0,
    )


def test_exit_boundary_is_tp_first_when_tp_and_sl_are_both_reached() -> None:
    frame = _exit_fixture()
    frame.iloc[2, frame.columns.get_loc("High")] = 103.0
    frame.iloc[2, frame.columns.get_loc("Low")] = 92.0

    trades = run_backtest(
        frame,
        [_fixed_signal(frame)],
        TradeParams(atr_window=1, cost_rate=0.0, tp_first=True, max_holding_bars=30),
        ticker="T",
    )

    assert len(trades) == 1
    assert trades[0].exit_reason == EXIT_TP
    assert trades[0].exit_price == pytest.approx(103.0)


def test_exit_boundary_is_sl_first_when_tp_flag_off() -> None:
    frame = _exit_fixture()
    frame.iloc[2, frame.columns.get_loc("High")] = 103.0
    frame.iloc[2, frame.columns.get_loc("Low")] = 92.0

    trades = run_backtest(
        frame,
        [_fixed_signal(frame)],
        TradeParams(atr_window=1, cost_rate=0.0, tp_first=False, max_holding_bars=30),
        ticker="T",
    )

    assert len(trades) == 1
    assert trades[0].exit_reason == EXIT_SL
    assert trades[0].exit_price == pytest.approx(96.0)


def test_exit_boundary_uses_last_bar_close_for_max_hold() -> None:
    frame = _exit_fixture()
    frame.iloc[31, frame.columns.get_loc("Close")] = 101.0

    trades = run_backtest(
        frame,
        [_fixed_signal(frame)],
        TradeParams(atr_window=1, cost_rate=0.0, tp_first=True, max_holding_bars=30),
        ticker="T",
    )

    assert len(trades) == 1
    assert trades[0].exit_reason == EXIT_MAX_HOLD
    assert trades[0].holding_bars == 30


def test_runner_uses_non_default_strategy_f_parameters(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    frame = _strategy_f_frame()
    captured: dict[str, object] = {}
    params = replace(
        STRATEGY_F_PARAMS,
        take_profit_pct=3.0,
        stop_loss_pct=4.0,
        cost_rate=0.001,
    )

    def spy_run_backtest(frame, signals, trade_params, ticker=""):
        captured["signals"] = signals
        captured["trade_params"] = trade_params
        return []

    monkeypatch.setattr(strategy_f, "run_backtest", spy_run_backtest)
    result = run_strategy_f_backtest({"T": frame}, params=params)

    assert result["params"] == params.as_dict()
    assert captured["trade_params"].cost_rate == 0.001
    assert captured["trade_params"].tp_first is True


def test_runner_fingerprint_is_invariant_to_dictionary_order() -> None:
    frame_a = _strategy_f_frame()
    frame_b = _strategy_f_frame().copy()

    first = run_strategy_f_backtest({"B": frame_b, "A": frame_a})
    second = run_strategy_f_backtest({"A": frame_a, "B": frame_b})

    assert first["data_fingerprint"] == second["data_fingerprint"]
    assert first["trades"] == second["trades"]


def test_runner_records_fixed_window_and_flattened_params() -> None:
    result = run_strategy_f_backtest(
        {"T": _strategy_f_frame()}, start=BASELINE_START, end=BASELINE_END
    )
    row = _baseline_row(result)

    assert result["data_window_start"] == "2020-08-03"
    assert result["data_window_end"] == "2026-08-27"
    assert row["param_slope_window"] == 30
    assert row["param_accel_window"] == 5
    assert row["param_ma_db_window"] == 16
    assert row["param_take_profit_pct"] == 3.0
    assert row["param_stop_loss_pct"] == 4.0
    assert row["param_tp_first"] is True


def test_cli_writes_nonempty_and_zero_trade_csv_headers(
    monkeypatch: pytest.MonkeyPatch, tmp_path
) -> None:
    frame = _strategy_f_frame()
    monkeypatch.setattr(strategy_f, "load_all", lambda: {"T": frame})

    summary_path = tmp_path / "summary.csv"
    monkeypatch.setattr(
        sys,
        "argv",
        [
            "strategy_f",
            "--output",
            str(summary_path),
            "--start",
            frame.index[0].date().isoformat(),
            "--end",
            frame.index[60].date().isoformat(),
        ],
    )
    strategy_f.main()
    trades_path = summary_path.with_name("summary_trades.csv")

    assert list(pd.read_csv(trades_path).columns) == list(_TRADE_COLUMNS)


def test_runner_is_invariant_to_dictionary_order_trades_sorted() -> None:
    frame_a = _strategy_f_frame()
    frame_b = _strategy_f_frame().copy()

    first = run_strategy_f_backtest({"B": frame_b, "A": frame_a})

    assert [
        (trade["entry_date"], trade["ticker"])
        for trade in first["trades"]
    ] == sorted(
        (trade["entry_date"], trade["ticker"])
        for trade in first["trades"]
    )


def test_runner_rejects_timezone_bound_mismatch() -> None:
    frame = _strategy_f_frame()
    frame.index = frame.index.tz_localize("UTC")

    with pytest.raises(ValueError, match="timezone"):
        run_strategy_f_backtest({"T": frame}, start="2024-01-01")
