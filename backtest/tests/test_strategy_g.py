from __future__ import annotations

import numpy as np
import pandas as pd
import pytest

from backtest.indicator_opt.strategy_g import compute_strategy_g, strategy_g_signals


def _make_g_frame(signal_close: float) -> pd.DataFrame:
    rows = [
        (100.0, 100.0, 99.0, 100.0, 100.0),
        (100.0, 100.0, 99.0, 100.0, 100.0),
        (100.0, 100.0, 99.0, 100.0, 100.0),
        (100.0, 100.0, 99.0, 100.0, 100.0),
        (100.0, 100.0, 99.0, 100.0, 100.0),
        (100.0, 108.0, 100.0, 107.0, 200.0),  # 7%+ 양봉 돌파, High 기준 고점
        (105.0, 105.0, 101.0, 102.0, 150.0),  # 음봉 풀백
        (100.0, signal_close, 99.0, signal_close, 200.0),  # 고가 돌파 후보
        (100.0, 100.0, 99.0, 100.0, 100.0),
        (100.0, 100.0, 99.0, 100.0, 100.0),
    ]
    return pd.DataFrame(
        rows,
        index=pd.bdate_range("2026-01-01", periods=len(rows)),
        columns=["Open", "High", "Low", "Close", "Volume"],
    )


@pytest.mark.parametrize(
    ("signal_close", "expected_signal"),
    [
        (110.0, True),
        (108.0 * 1.05, True),
        (108.0 * 1.05 + 0.01, False),
    ],
    ids=["within-limit", "exactly-five-percent", "over-limit"],
)
def test_strategy_g_filters_close_over_previous_five_day_high(
    signal_close: float, expected_signal: bool
) -> None:
    frame = _make_g_frame(signal_close)

    mask = compute_strategy_g(frame)

    assert mask.index.equals(frame.index)
    assert mask.dtype == bool
    assert bool(mask.iloc[7]) is expected_signal
    assert int(mask.sum()) == int(expected_signal)


def test_strategy_g_does_not_change_non_signal_rows() -> None:
    frame = _make_g_frame(110.0)

    mask = compute_strategy_g(frame)

    expected = np.zeros(len(frame), dtype=bool)
    expected[7] = True
    np.testing.assert_array_equal(mask.to_numpy(), expected)


def test_strategy_g_does_not_use_future_highs_for_the_signal_day() -> None:
    frame = _make_g_frame(110.0)
    future_changed = frame.copy()
    future_changed.loc[future_changed.index[8], "High"] = 1_000.0
    future_changed.loc[future_changed.index[8], "Close"] = 1_000.0

    pd.testing.assert_series_equal(
        compute_strategy_g(frame), compute_strategy_g(future_changed)
    )


@pytest.mark.parametrize(
    ("signal_close", "expected_signal_count"),
    [(108.0 * 1.05, 1), (108.0 * 1.05 + 0.01, 0)],
    ids=["boundary-kept", "over-limit-filtered"],
)
def test_strategy_g_signals_follow_the_filtered_mask(
    signal_close: float, expected_signal_count: int
) -> None:
    frame = _make_g_frame(signal_close)

    signals = strategy_g_signals(frame, ticker="TEST")

    assert len(signals) == expected_signal_count
    if signals:
        assert signals[0].ticker == "TEST"
        assert signals[0].date == frame.index[7]
        assert signals[0].price == signal_close


def test_strategy_g_keeps_decimal_five_percent_boundary() -> None:
    rows = [
        (3.5, 3.5, 3.4, 3.5, 100.0),
        (3.5, 3.5, 3.4, 3.5, 100.0),
        (3.5, 3.5, 3.4, 3.5, 100.0),
        (3.5, 3.5, 3.4, 3.5, 100.0),
        (3.5, 3.5, 3.4, 3.5, 100.0),
        (3.5, 3.8, 3.5, 3.75, 200.0),  # 7%+ 양봉 돌파
        (3.7, 3.7, 3.5, 3.6, 150.0),  # 음봉 풀백
        (3.5, 3.99, 3.4, 3.99, 200.0),  # 3.8 대비 십진 기준 정확히 5%
        (3.5, 3.5, 3.4, 3.5, 100.0),
        (3.5, 3.5, 3.4, 3.5, 100.0),
    ]
    frame = pd.DataFrame(
        rows,
        index=pd.bdate_range("2026-02-02", periods=len(rows)),
        columns=["Open", "High", "Low", "Close", "Volume"],
    )

    mask = compute_strategy_g(frame)

    assert bool(mask.iloc[7])
