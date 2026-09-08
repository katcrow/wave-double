from __future__ import annotations

from unittest.mock import patch

import numpy as np
import pandas as pd
import pytest

from backtest.strategy_api import (
    SL_PRIORITY,
    StrategyErrorCode,
    StrategyResult,
    compute_abc,
)
from backtest.indicator_opt.strategy_d import STRATEGY_D_PARAMS
from backtest.indicator_opt.strategy_e import STRATEGY_E_PARAMS
from backtest.indicator_opt.strategy_f import STRATEGY_F_PARAMS


def _make_df(n: int = 200, *, close_nan: int | None = None) -> pd.DataFrame:
    dates = pd.date_range("2024-01-02", periods=n, freq="B")
    rng = np.random.RandomState(42)
    close = 100.0 + np.cumsum(rng.randn(n) * 0.5)
    if close_nan is not None:
        close[close_nan] = np.nan
    df = pd.DataFrame(
        {
            "Open": close - rng.uniform(0, 0.3, n),
            "High": close + rng.uniform(0.2, 1.0, n),
            "Low": close - rng.uniform(0.2, 1.0, n),
            "Close": close,
            "Volume": rng.randint(1000, 50000, n).astype(float),
        },
        index=dates,
    )
    df["High"] = df[["High", "Open", "Close"]].max(axis=1)
    df["Low"] = df[["Low", "Open", "Close"]].min(axis=1)
    return df


class TestSLPriorityConstant:
    def test_sl_priority_is_true(self) -> None:
        assert SL_PRIORITY is True


class TestInsufficientHistory:
    def test_returns_ineligible(self) -> None:
        df = _make_df(n=50)
        result = compute_abc(df, ticker="T")
        assert result.status == "INELIGIBLE_INSUFFICIENT_HISTORY"
        assert result.signals == {}
        assert result.error is None

    def test_malformed_short_frame_is_error(self) -> None:
        df = _make_df(n=50).drop(columns="Volume")

        result = compute_abc(df, ticker="T")

        assert result.status == "ERROR"
        assert result.error is not None
        assert result.error.code == StrategyErrorCode.SIGNAL_COMPUTE_ERROR


class TestNonFiniteInput:
    @pytest.mark.parametrize(
        "col_name,idx",
        [("Close", 50), ("Open", 10), ("High", 60), ("Low", 30), ("Volume", 70)],
    )
    def test_nan_in_column(self, col_name: str, idx: int) -> None:
        df = _make_df(n=200)
        df.loc[df.index[idx], col_name] = np.nan
        result = compute_abc(df, ticker="T")
        assert result.status == "ERROR"
        assert result.error is not None
        assert result.error.code == StrategyErrorCode.SIGNAL_COMPUTE_ERROR
        assert result.error.strategy is None
        assert result.signals == {}

    def test_inf_in_close(self) -> None:
        df = _make_df(n=200)
        df.loc[df.index[100], "Close"] = np.inf
        result = compute_abc(df, ticker="T")
        assert result.status == "ERROR"
        assert result.error is not None
        assert result.error.code == StrategyErrorCode.SIGNAL_COMPUTE_ERROR


class TestInvalidInputStructure:
    def test_missing_ohlcv_column_is_typed_error(self) -> None:
        df = _make_df(n=200).drop(columns="Volume")
        result = compute_abc(df, ticker="T")

        assert result.status == "ERROR"
        assert result.signals == {}
        assert result.error is not None
        assert result.error.code == StrategyErrorCode.SIGNAL_COMPUTE_ERROR
        assert "OHLCV 컬럼" in result.error.message

    def test_non_dataframe_is_typed_error(self) -> None:
        result = compute_abc(None, ticker="T")  # type: ignore[arg-type]

        assert result.status == "ERROR"
        assert result.error is not None
        assert result.error.code == StrategyErrorCode.SIGNAL_COMPUTE_ERROR


class TestStrictBuildSignalsRaises:
    def test_raises_on_bad_input(self) -> None:
        df = _make_df(n=200)
        with patch(
            "backtest.strategy_api.build_signals",
            side_effect=ValueError("mocked indicator failure"),
        ):
            result = compute_abc(df, ticker="T")
        assert result.status == "ERROR"
        assert result.error is not None
        assert result.error.code == StrategyErrorCode.SIGNAL_COMPUTE_ERROR
        assert "mocked indicator failure" in result.error.message

    def test_build_signals_strict_true_raises(self) -> None:
        from backtest.indicator_opt.combine_strategies import build_signals

        df = _make_df(n=200)
        with patch(
            "backtest.indicator_opt.combine_strategies.get_signal_fn",
            side_effect=RuntimeError("boom"),
        ):
            with pytest.raises(RuntimeError, match="boom"):
                build_signals(df, 3.0, 3.0, "T", strict=True)


class TestLastBarDiscarded:
    def test_last_bar_signal_only_empty_mask(self) -> None:
        df = _make_df(n=200)
        dummy_mask = pd.Series(False, index=df.index)
        dummy_mask.iloc[-1] = True

        with patch(
            "backtest.strategy_api.build_signals",
            return_value=(dummy_mask.copy(), dummy_mask.copy(), dummy_mask.copy()),
        ):
            result = compute_abc(df, ticker="T")
        assert result.status == "READY"
        assert result.error is None
        assert not result.signals["A"].any()
        assert not result.signals["B"].any()
        assert not result.signals["C"].any()

    def test_last_bar_is_discarded_for_d_and_e(self) -> None:
        df = _make_df(n=200)
        last_bar = pd.Series(False, index=df.index)
        last_bar.iloc[-1] = True

        with patch(
            "backtest.strategy_api.build_signals",
            return_value=(last_bar.copy(), last_bar.copy(), last_bar.copy()),
        ), patch(
            "backtest.strategy_api.compute_strategy_d", return_value=last_bar.copy()
        ), patch(
            "backtest.strategy_api.compute_strategy_e", return_value=last_bar.copy()
        ), patch(
            "backtest.strategy_api.compute_strategy_f", return_value=last_bar.copy()
        ):
            result = compute_abc(df, ticker="T")

        assert result.status == "READY"
        assert all(
            not result.signals[key].any() for key in ("A", "B", "C", "D", "E", "F")
        )


class TestATRFilter:
    def test_signal_on_zero_atr_row_excluded(self) -> None:
        df = _make_df(n=200)
        mid = len(df) // 2
        dummy_mask = pd.Series(False, index=df.index)
        dummy_mask.iloc[mid] = True

        atr_series = pd.Series(1.0, index=df.index)
        atr_series.iloc[mid] = 0.0

        with patch(
            "backtest.strategy_api.build_signals",
            return_value=(dummy_mask.copy(), pd.Series(False, index=df.index), pd.Series(False, index=df.index)),
        ), patch("backtest.strategy_api.atr", return_value=atr_series):
            result = compute_abc(df, ticker="T")
        assert result.status == "READY"
        assert not result.signals["A"].iloc[mid]

    def test_signal_on_nan_atr_row_excluded(self) -> None:
        df = _make_df(n=200)
        mid = len(df) // 2
        dummy_mask = pd.Series(False, index=df.index)
        dummy_mask.iloc[mid] = True

        atr_series = pd.Series(1.0, index=df.index)
        atr_series.iloc[mid] = np.nan

        with patch(
            "backtest.strategy_api.build_signals",
            return_value=(dummy_mask.copy(), pd.Series(False, index=df.index), pd.Series(False, index=df.index)),
        ), patch("backtest.strategy_api.atr", return_value=atr_series):
            result = compute_abc(df, ticker="T")
        assert result.status == "READY"
        assert not result.signals["A"].iloc[mid]


class TestNormalCompute:
    def test_returns_ready_with_masks(self) -> None:
        df = _make_df(n=200)
        result = compute_abc(df, ticker="T")
        assert result.ticker == "T"
        assert result.status == "READY"
        assert result.error is None
        assert set(result.signals) == {"A", "B", "C", "D", "E", "F"}
        for key in ("A", "B", "C", "D", "E", "F"):
            assert result.signals[key].index.equals(df.index)
            assert result.signals[key].dtype == bool
            assert len(result.signals[key]) == 200
        assert not result.signals["A"].iloc[-1]
        assert not result.signals["B"].iloc[-1]
        assert not result.signals["C"].iloc[-1]
        assert result.params_meta["D"] == STRATEGY_D_PARAMS.as_dict()
        assert result.params_meta["E"] == STRATEGY_E_PARAMS.as_dict()
        assert result.params_meta["F"] == STRATEGY_F_PARAMS.as_dict()
        assert set(result.params_meta) == {"A", "B", "C", "D", "E", "F"}
        for key in ("A", "B", "C"):
            assert result.params_meta[key] == {
                "atr_window": 14,
                "take_profit_pct": 3.0,
                "stop_loss_pct": 3.0,
                "max_holding_bars": 30,
            }
        assert result.strategy_params is result.params_meta


class TestInvalidOhlcSegments:
    def test_no_valid_ohlc_segment_is_typed_error(self) -> None:
        df = _make_df(n=200)
        df["High"] = df["Low"] - 1.0

        result = compute_abc(df, ticker="T")

        assert result.status == "ERROR"
        assert result.signals == {}
        assert result.error is not None
        assert result.error.code == StrategyErrorCode.SIGNAL_COMPUTE_ERROR
        assert "유효한 OHLCV 구간" in result.error.message

    def test_invalid_relationship_row_is_excluded_without_connecting_segments(self) -> None:
        df = _make_df(n=200)
        df["Open"] = df["Close"]
        df["High"] = df["Close"] + 1.0
        df["Low"] = df["Close"] - 1.0
        invalid = 100
        df.iloc[invalid, df.columns.get_loc("High")] = 1.0
        segment_masks: list[pd.Index] = []
        d_e_f_segments: list[pd.Index] = []

        def fake_build(frame, *_args, **_kwargs):
            segment_masks.append(frame.index)
            mask = pd.Series(False, index=frame.index)
            mask.iloc[-1] = True
            return mask.copy(), mask.copy(), mask.copy()

        def fake_segment_calculator(frame, *_args, **_kwargs):
            d_e_f_segments.append(frame.index)
            mask = pd.Series(False, index=frame.index)
            mask.iloc[-1] = True
            return mask

        with patch("backtest.strategy_api.build_signals", side_effect=fake_build), patch(
            "backtest.strategy_api.compute_strategy_d", side_effect=fake_segment_calculator
        ), patch(
            "backtest.strategy_api.compute_strategy_e", side_effect=fake_segment_calculator
        ), patch(
            "backtest.strategy_api.compute_strategy_f", side_effect=fake_segment_calculator
        ):
            result = compute_abc(df, ticker="T")

        assert result.status == "READY"
        assert len(segment_masks) == 1
        assert segment_masks[0].equals(df.index)
        assert len(d_e_f_segments) == 6
        assert all(result.signals[key].dtype == bool for key in result.signals)
        assert all(not result.signals[key].iloc[invalid] for key in result.signals)
        # A/B/C preserve full-frame calculation; D/E/F terminal segment bars are filtered.
        assert not result.signals["D"].iloc[invalid - 1]
        assert not result.signals["E"].iloc[invalid - 1]
        assert not result.signals["F"].iloc[invalid - 1]

    @pytest.mark.parametrize(
        ("calculator", "strategy"),
        [
            ("compute_strategy_d", "D"),
            ("compute_strategy_e", "E"),
            ("compute_strategy_f", "F"),
        ],
    )
    def test_calculator_failure_is_typed_and_names_strategy(
        self, calculator: str, strategy: str
    ) -> None:
        df = _make_df(n=200)
        with patch(
            f"backtest.strategy_api.{calculator}",
            side_effect=RuntimeError("계산기 오류"),
        ):
            result = compute_abc(df, ticker="T")

        assert result.status == "ERROR"
        assert result.signals == {}
        assert result.error is not None
        assert result.error.code == StrategyErrorCode.SIGNAL_COMPUTE_ERROR
        assert result.error.strategy == strategy
        assert "계산기 오류" in result.error.message

    @pytest.mark.parametrize(
        ("calculator", "strategy"),
        [
            ("compute_strategy_d", "D"),
            ("compute_strategy_e", "E"),
            ("compute_strategy_f", "F"),
        ],
    )
    def test_calculator_contract_violation_is_typed_error(
        self, calculator: str, strategy: str
    ) -> None:
        df = _make_df(n=200)
        invalid_mask = pd.Series(1, index=df.index, dtype="int64")

        with patch(f"backtest.strategy_api.{calculator}", return_value=invalid_mask):
            result = compute_abc(df, ticker="T")

        assert result.status == "ERROR"
        assert result.signals == {}
        assert result.error is not None
        assert result.error.code == StrategyErrorCode.SIGNAL_COMPUTE_ERROR
        assert result.error.strategy == strategy

    def test_d_e_f_positive_masks_are_returned(self) -> None:
        df = _make_df(n=200)
        positive = pd.Series(False, index=df.index)
        positive.iloc[100] = True

        with patch(
            "backtest.strategy_api.compute_strategy_d", return_value=positive.copy()
        ), patch(
            "backtest.strategy_api.compute_strategy_e", return_value=positive.copy()
        ), patch(
            "backtest.strategy_api.compute_strategy_f", return_value=positive.copy()
        ):
            result = compute_abc(df, ticker="T")

        assert result.status == "READY"
        assert result.signals["D"].iloc[100]
        assert result.signals["E"].iloc[100]
        assert result.signals["F"].iloc[100]


class TestBuildSignalsDefaultSwallows:
    def test_default_does_not_raise(self) -> None:
        from backtest.indicator_opt.combine_strategies import build_signals

        df = _make_df(n=200)
        with patch(
            "backtest.indicator_opt.combine_strategies.get_signal_fn",
            side_effect=RuntimeError("should be swallowed"),
        ):
            a, b, c = build_signals(df, 3.0, 3.0, "T")
        assert isinstance(a, pd.Series)
        assert isinstance(b, pd.Series)
        assert isinstance(c, pd.Series)
        assert not a.any()
        assert not b.any()
        assert not c.any()
