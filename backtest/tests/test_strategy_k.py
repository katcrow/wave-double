"""전략 K(장단기 이평 이격 + 단기 변곡) 계산·ATR 청산 회귀 테스트."""

import numpy as np
import pandas as pd
import pytest

from backtest.engine import TradeParams, run_backtest
from backtest.indicator_opt.strategy_k import (
    STRATEGY_K_PARAMS,
    StrategyKParams,
    compute_strategy_k,
    run_strategy_k_backtest,
    strategy_k_signals,
    validate_strategy_k_params,
)


def _turn_up_frame() -> pd.DataFrame:
    """단기이평(2봉) 최소제곱 기울기가 index 8에서 하락→상승 변곡하는 소형 프레임.

    close: 100→104까지 상승 후 104→102로 눌렸다가 102→107로 재상승.
    단기이평(2봉)은 index 8에서만 slope(전일<=0 → 당일>0)로 전환된다.
    """

    close = np.array(
        [100, 101, 102, 103, 104, 103, 102, 103, 104, 105, 106, 107],
        dtype=float,
    )
    dates = pd.date_range("2024-01-01", periods=len(close), freq="B")
    return pd.DataFrame(
        {
            "Open": close,
            "High": close + 0.5,
            "Low": close - 0.5,
            "Close": close,
            "Volume": np.full(len(close), 100.0),
        },
        index=dates,
    )


def _test_params() -> StrategyKParams:
    return StrategyKParams(
        long_window=4,
        short_window=2,
        long_angle_bars=2,
        long_angle_min=0.0,
        long_angle_max=45.0,
        deviation_pct=50.0,
        slope_window=2,
        tp_atr=3.0,
        sl_atr=2.0,
        atr_window=3,
    )


def test_compute_strategy_k_returns_bool_mask_and_one_signal() -> None:
    frame = _turn_up_frame()
    params = _test_params()

    mask = compute_strategy_k(frame, params)

    assert mask.index.equals(frame.index)
    assert mask.dtype == bool
    assert mask.sum() == 1
    assert mask.to_numpy().tolist().index(True) == 8


def test_strategy_k_signals_has_no_fixed_tp_sl_and_uses_close_price() -> None:
    frame = _turn_up_frame()
    params = _test_params()

    signals = strategy_k_signals(frame, ticker="TEST", params=params)

    assert len(signals) == 1
    signal = signals[0]
    assert signal.ticker == "TEST"
    assert signal.date == frame.index[8]
    assert signal.price == pytest.approx(104.0)
    # ATR 기반 청산에 위임하도록 고정 손절/익절을 지정하지 않는다.
    assert signal.stop_price is None
    assert signal.take_profit_pct is None
    assert signal.take_profit_price is None


def test_strategy_k_signal_runs_through_engine_with_atr_exit() -> None:
    frame = _turn_up_frame()
    params = _test_params()
    signals = strategy_k_signals(frame, ticker="TEST", params=params)

    trade_params = TradeParams(
        tp_atr=params.tp_atr,
        sl_atr=params.sl_atr,
        atr_window=params.atr_window,
        cost_rate=params.cost_rate,
        max_holding_bars=params.max_holding_bars,
        tp_first=params.tp_first,
    )
    trades = run_backtest(frame, signals, trade_params, ticker="TEST")

    assert len(trades) == 1
    trade = trades[0]
    assert trade.entry_date == frame.index[8]
    assert trade.entry_price == pytest.approx(104.0)
    assert trade.exit_reason in {"tp", "sl", "end", "max_hold"}


def test_validate_strategy_k_params_rejects_short_window_not_below_long_window() -> None:
    with pytest.raises(ValueError):
        validate_strategy_k_params(StrategyKParams(long_window=10, short_window=10))


def test_validate_strategy_k_params_rejects_bad_angle_bounds() -> None:
    with pytest.raises(ValueError):
        validate_strategy_k_params(
            StrategyKParams(long_angle_min=5.0, long_angle_max=1.0)
        )


def test_run_strategy_k_backtest_end_to_end_on_synthetic_data() -> None:
    frame = _turn_up_frame()
    params = _test_params()
    data = {"TEST": frame}

    result = run_strategy_k_backtest(
        data=data,
        params=params,
        start=frame.index[0],
        end=frame.index[-1],
    )

    assert result["strategy"] == "K"
    assert result["n_tickers"] == 1
    assert result["n_signals"] == 1
    assert result["n_trades"] == 1
    assert result["trades"][0]["ticker"] == "TEST"


def test_strategy_k_default_params_are_valid() -> None:
    validate_strategy_k_params(STRATEGY_K_PARAMS)
