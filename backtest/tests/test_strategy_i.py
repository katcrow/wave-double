"""전략 I 계산·고정 청산 회귀 테스트."""

from dataclasses import replace
import sys

import numpy as np
import pandas as pd
import pytest

import backtest.indicator_opt.strategy_i as strategy_i
from backtest.engine import (
    EXIT_END, EXIT_TP, TradeParams, run_backtest,
)
from backtest.indicator_opt.strategy_i import (
    BASELINE_END,
    BASELINE_START,
    CANDIDATE_A,
    STRATEGY_I_PARAMS,
    _TRADE_COLUMNS,
    _baseline_row,
    _box_range,
    compute_strategy_i,
    run_strategy_i_backtest,
    strategy_i_signals,
    validate_strategy_i_params,
)
from backtest.indicator_opt._signals import SimpleSignal


def _strategy_i_frame(n: int = 300) -> tuple[pd.DataFrame, int]:
    """박스(횡보) 후 종가 돌파 + 거래량 증가가 정확히 한 번 나오는 프레임."""
    dates = pd.date_range("2024-01-01", periods=n, freq="B")
    close = np.empty(n)
    close[:250] = 100.0
    close[250:] = 105.0
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
    signal_position = 250
    frame.iloc[signal_position, frame.columns.get_loc("High")] = (
        close[signal_position] + 30.0
    )
    frame.iloc[signal_position, frame.columns.get_loc("Volume")] = 200.0
    return frame, signal_position


def test_strategy_i_returns_bool_mask_and_one_signal() -> None:
    frame, signal_position = _strategy_i_frame()

    mask = compute_strategy_i(frame)

    assert mask.index.equals(frame.index)
    assert mask.dtype == bool
    assert bool(mask.iloc[signal_position])
    assert int(mask.sum()) == 1


def test_box_range_excludes_signal_bar_itself() -> None:
    frame, signal_position = _strategy_i_frame()

    box_top, box_bottom = _box_range(frame, CANDIDATE_A.box_window)

    prior_high = frame["High"].iloc[signal_position - 20 : signal_position].max()
    prior_low = frame["Low"].iloc[signal_position - 20 : signal_position].min()
    assert box_top.iloc[signal_position] == pytest.approx(prior_high)
    assert box_bottom.iloc[signal_position] == pytest.approx(prior_low)
    assert frame["Close"].iloc[signal_position] > box_top.iloc[signal_position]


def test_breakout_requires_close_above_box_top() -> None:
    frame, signal_position = _strategy_i_frame()
    assert compute_strategy_i(frame).iloc[signal_position]

    box_top = _box_range(frame, CANDIDATE_A.box_window)[0].iloc[signal_position]
    pos = signal_position
    frame.iloc[pos, frame.columns.get_loc("Close")] = box_top
    frame.iloc[pos, frame.columns.get_loc("Open")] = box_top
    frame.iloc[pos, frame.columns.get_loc("Low")] = box_top - 1.0

    assert not compute_strategy_i(frame).iloc[signal_position]


def test_volume_rise_above_previous_bar_is_required() -> None:
    frame, signal_position = _strategy_i_frame()
    assert compute_strategy_i(frame).iloc[signal_position]

    frame.iloc[signal_position, frame.columns.get_loc("Volume")] = 100.0

    assert not compute_strategy_i(frame).iloc[signal_position]


def test_strict_cross_only_fires_first_breakout_in_an_uptrend() -> None:
    """추세 상승 구간에서 strict_cross 기본값은 첫 교차 봉만 신호로 잡는다.

    터치 조건을 비활성화해 strict_cross 로직만 고립해서 검증한다. 박스 정의가
    도입되면 상승 추세에선 폭/드리프트 조건으로 곧 박스가 무효화되어 반복 발화가
    자연히 막히므로, 여기선 폭/드리프트를 유지하면서 연속 돌파 봉을 만들어
    strict_cross의 교차 봉 필터 동작을 확인한다.
    """
    n = 280
    dates = pd.date_range("2024-01-01", periods=n, freq="B")
    close = np.full(n, 100.0)
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
    first_break = 250
    # 3연속 상승 돌파 봉 (첫 봉만 박스 안 정착 후 교차)
    heights = (106.0, 108.0, 110.0)
    for step, level in enumerate(heights):
        pos = first_break + step
        frame.iloc[pos, frame.columns.get_loc("Open")] = level - 2.0
        frame.iloc[pos, frame.columns.get_loc("Close")] = level
        frame.iloc[pos, frame.columns.get_loc("High")] = level + 1.0
        frame.iloc[pos, frame.columns.get_loc("Low")] = 99.5
        frame.iloc[pos, frame.columns.get_loc("Volume")] = 200.0 + step * 100.0

    no_touch_params = replace(CANDIDATE_A, box_touches_required=False)

    strict = compute_strategy_i(frame, no_touch_params)
    assert int(strict.sum()) == 1
    assert bool(strict.iloc[first_break])

    permissive = compute_strategy_i(
        frame,
        replace(no_touch_params, strict_cross=False),
    )
    # 첫 두 돌파 봉은 유효 박스로 남아 발화하고, 세 번째 봉은 박스 드리프트
    # 상한(3%) 때문에 복귀한다 — strict_cross는 연속 돌파 1회만 허용함을 보증.
    assert int(permissive.sum()) == 2


def test_box_width_ratio_filter_is_effective() -> None:
    frame, signal_position = _strategy_i_frame()
    assert compute_strategy_i(frame).iloc[signal_position]

    # 박스 창 안 두 봉의 저가를 내려 폭을 기본 한계(0.20)를 초과하게 만든다.
    wide = frame.copy()
    for offset in (6, 20):
        pos = signal_position - offset
        wide.iloc[pos, wide.columns.get_loc("Low")] = 82.0

    assert not compute_strategy_i(wide).iloc[signal_position]
    relaxed = compute_strategy_i(
        wide, replace(CANDIDATE_A, box_width_ratio_max=0.30)
    )
    assert relaxed.iloc[signal_position]


def test_box_drift_filter_is_effective() -> None:
    frame, signal_position = _strategy_i_frame()
    assert compute_strategy_i(frame).iloc[signal_position]

    # 박스 창 내 종가를 지속 상승시키면 정규화 slope(총 드리프트)로 무효 처리된다.
    trending = frame.copy()
    for offset in range(20):
        pos = signal_position - 1 - offset
        level = 100.0 + (19 - offset) * 0.35  # 총 약 +6.6% 상승 드리프트
        trending.iloc[pos, trending.columns.get_loc("High")] = level + 1.0
        trending.iloc[pos, trending.columns.get_loc("Open")] = level
        trending.iloc[pos, trending.columns.get_loc("Close")] = level + 0.8
        trending.iloc[pos, trending.columns.get_loc("Low")] = level - 1.0
    pos = signal_position
    box_top = trending["High"].iloc[pos - 20 : pos].max()
    trending.iloc[pos, trending.columns.get_loc("Open")] = 108.0
    trending.iloc[pos, trending.columns.get_loc("Close")] = box_top + 0.5
    trending.iloc[pos, trending.columns.get_loc("High")] = box_top + 1.0
    trending.iloc[pos, trending.columns.get_loc("Low")] = 99.0

    assert not compute_strategy_i(
        trending, replace(CANDIDATE_A, strict_cross=False)
    ).iloc[signal_position]
    loose_drift = compute_strategy_i(
        trending, replace(CANDIDATE_A, strict_cross=False, box_drift_max=0.08)
    )
    assert loose_drift.iloc[signal_position]


def test_touch_requirement_is_effective_and_optional() -> None:
    frame, signal_position = _strategy_i_frame()
    assert compute_strategy_i(frame).iloc[signal_position]

    # 박스 상단 터치를 1회로 줄이면 기본(터치 요구)에서 무효가 되고,
    # 해제하면 다시 신호가 난다.
    sparse = frame.copy()
    for offset in range(20):
        pos = signal_position - 1 - offset
        sparse.iloc[pos, sparse.columns.get_loc("High")] = 100.5
    sparse.iloc[signal_position - 1, sparse.columns.get_loc("High")] = 101.0

    assert not compute_strategy_i(sparse).iloc[signal_position]
    no_touch = compute_strategy_i(
        sparse, replace(CANDIDATE_A, box_touches_required=False)
    )
    assert no_touch.iloc[signal_position]


def test_chase_entry_cap_excludes_too_far_above_box_top_entry() -> None:
    frame, signal_position = _strategy_i_frame()
    box_top = _box_range(frame, CANDIDATE_A.box_window)[0].iloc[signal_position]
    assert compute_strategy_i(frame).iloc[signal_position]

    # 신호 봉 종가를 박스상단 대비 +20%로 띄우면 기본 캡(+10%)에서 제외되고,
    # 캡을 크게 풀면 다시 포함된다.
    pos = signal_position
    far_close = box_top * 1.2
    frame.iloc[pos, frame.columns.get_loc("Close")] = far_close
    frame.iloc[pos, frame.columns.get_loc("Open")] = far_close
    frame.iloc[pos, frame.columns.get_loc("High")] = far_close + 10.0
    frame.iloc[pos, frame.columns.get_loc("Low")] = far_close - 1.0

    assert not compute_strategy_i(frame).iloc[signal_position]
    relaxed = compute_strategy_i(
        frame, replace(CANDIDATE_A, max_entry_over_top_pct=30.0)
    )
    assert relaxed.iloc[signal_position]


@pytest.mark.parametrize(
    ("field", "value"),
    [
        ("box_window", 1.5),
        ("box_window", 0),
        ("min_box_bars", 0),
        ("box_width_ratio_max", 0.0),
        ("box_width_ratio_max", 1.5),
        ("box_drift_max", -0.1),
        ("box_touch_zone_pct", 1.0),
        ("box_touches_min", 0),
        ("box_touches_required", "yes"),
        ("max_entry_over_top_pct", 0),
        ("max_entry_over_top_pct", float("nan")),
        ("take_profit_pct", 0),
        ("take_profit_pct", float("inf")),
        ("stop_loss_pct", -1),
        ("max_holding_bars", 0),
        ("max_holding_bars", 1.5),
        ("cost_rate", -0.01),
    ],
)
def test_invalid_strategy_parameters_are_rejected(field: str, value) -> None:
    frame, _ = _strategy_i_frame()
    params = replace(CANDIDATE_A, **{field: value})

    with pytest.raises(ValueError):
        compute_strategy_i(frame, params)


@pytest.mark.parametrize("mutation", ["duplicate", "ohlc", "negative_volume"])
def test_strategy_i_frame_contract_is_rejected(mutation: str) -> None:
    frame, _ = _strategy_i_frame()
    if mutation == "duplicate":
        frame.columns = ["Open", "High", "Low", "Close", "Close"]
    elif mutation == "ohlc":
        frame.iloc[100, frame.columns.get_loc("High")] = 1.0
    else:
        frame.iloc[100, frame.columns.get_loc("Volume")] = -1.0

    with pytest.raises(ValueError):
        compute_strategy_i(frame)


def test_insufficient_history_is_safe_and_silent() -> None:
    frame, _ = _strategy_i_frame()
    frame = frame.iloc[:CANDIDATE_A.box_window].copy()

    mask = compute_strategy_i(frame)

    assert mask.index.equals(frame.index)
    assert mask.dtype == bool
    assert not mask.any()


def test_invalid_input_contract_is_explicit() -> None:
    frame, _ = _strategy_i_frame()
    frame = frame.drop(columns="Volume")

    with pytest.raises(ValueError, match="OHLCV 컬럼"):
        compute_strategy_i(frame)


def test_future_ohlcv_changes_do_not_change_past_signal() -> None:
    frame, signal_position = _strategy_i_frame()
    expected = compute_strategy_i(frame)
    mutated = frame.copy()
    mutated.iloc[signal_position + 1, mutated.columns.get_loc("High")] = 1e9
    mutated.iloc[signal_position + 1, mutated.columns.get_loc("Volume")] = 1e12

    actual = compute_strategy_i(mutated)

    pd.testing.assert_series_equal(
        actual.iloc[: signal_position + 1], expected.iloc[: signal_position + 1]
    )


def test_signal_bar_own_high_does_not_make_signal() -> None:
    frame, signal_position = _strategy_i_frame()
    changed = frame.copy()
    changed.iloc[signal_position, changed.columns.get_loc("High")] = 1e9

    expected = compute_strategy_i(frame)
    actual = compute_strategy_i(changed)

    pd.testing.assert_series_equal(actual, expected)


def test_strategy_i_signals_use_fixed_exit_parameters() -> None:
    frame, signal_position = _strategy_i_frame()

    signals = strategy_i_signals(frame, ticker="T")

    signal = next(item for item in signals if item.date == frame.index[signal_position])
    box_top = _box_range(frame, CANDIDATE_A.box_window)[0].iloc[signal_position]
    assert signal.price == pytest.approx(frame["Close"].iloc[signal_position])
    assert signal.take_profit_pct == CANDIDATE_A.take_profit_pct
    assert signal.stop_price == pytest.approx(box_top * (1.0 - 0.05))


def test_engine_exits_tp_and_sl_from_signal() -> None:
    frame = pd.DataFrame(
        {
            "Open": [100.0, 100.0, 100.0, 100.0, 100.0],
            "High": [101.0, 101.0, 105.0, 101.0, 101.0],
            "Low": [99.0, 99.0, 99.0, 94.0, 99.0],
            "Close": [100.0] * 5,
            "Volume": [1000.0] * 5,
        },
        index=pd.date_range("2025-01-01", periods=5, freq="B"),
    )
    signal = SimpleSignal("T", frame.index[1], 100.0, stop_price=95.0, take_profit_pct=4.0)

    trades = run_backtest(
        frame, [signal], TradeParams(atr_window=1, cost_rate=0.0), ticker="T"
    )

    assert trades[0].exit_reason == EXIT_TP
    assert trades[0].exit_price == pytest.approx(104.0)


def test_runner_records_fixed_observation_window_and_flattened_params() -> None:
    frame, _ = _strategy_i_frame()

    result = run_strategy_i_backtest(
        {"T": frame}, start=BASELINE_START, end=BASELINE_END
    )
    row = _baseline_row(result)

    assert result["strategy"] == "I"
    assert result["data_window_start"] == "2020-08-03"
    assert result["data_window_end"] == "2026-08-26"
    assert row["param_box_window"] == 20
    assert row["param_min_box_bars"] == 10
    assert row["param_box_width_ratio_max"] == 0.20
    assert row["param_box_drift_max"] == 0.03
    assert row["param_box_touch_zone_pct"] == 0.20
    assert row["param_box_touches_min"] == 2
    assert row["param_box_touches_required"] is True
    assert row["param_strict_cross"] is True
    assert row["param_max_entry_over_top_pct"] == 10.0
    assert row["param_take_profit_pct"] == 4.0
    assert row["param_stop_loss_pct"] == 5.0
    assert pd.isna(row["param_max_holding_bars"])
    assert row["param_cost_rate"] == 0.0005
    assert result["params"] == STRATEGY_I_PARAMS.as_dict()


def test_reproducible_runner_uses_strategy_i_parameters(monkeypatch) -> None:
    frame, _ = _strategy_i_frame()
    captured = {}

    def spy_run_backtest(frame, signals, trade_params, ticker=""):
        captured["trade_params"] = trade_params
        return []

    monkeypatch.setattr("backtest.indicator_opt.strategy_i.run_backtest", spy_run_backtest)

    result = run_strategy_i_backtest({"T": frame})

    assert result["strategy"] == "I"
    assert result["params"] == CANDIDATE_A.as_dict()
    assert captured["trade_params"].cost_rate == CANDIDATE_A.cost_rate
    assert captured["trade_params"].max_holding_bars == CANDIDATE_A.max_holding_bars


def test_runner_excludes_invalid_rows_and_splits_segments(
    monkeypatch: pytest.MonkeyPatch,
) -> None:
    frame, _ = _strategy_i_frame()
    frame = frame.iloc[:150].copy()
    frame.iloc[30, frame.columns.get_loc("Close")] = np.nan
    segments: list[pd.DataFrame] = []

    def spy_run_backtest(segment, signals, trade_params, ticker=""):
        segments.append(segment)
        return []

    monkeypatch.setattr(strategy_i, "run_backtest", spy_run_backtest)
    result = run_strategy_i_backtest({"T": frame})

    assert result["invalid_ohlcv_rows"] == 1
    assert result["n_signals"] == 0
    assert [len(segment) for segment in segments] == [30, 119]
    assert all(np.isfinite(segment.to_numpy(dtype=float)).all() for segment in segments)


def test_runner_fingerprint_includes_invalid_rows() -> None:
    frame, _ = _strategy_i_frame()
    frame = frame.iloc[:150].copy()
    invalid = frame.copy()
    invalid.iloc[30, invalid.columns.get_loc("Close")] = np.nan
    changed_invalid = invalid.copy()
    changed_invalid.iloc[30, changed_invalid.columns.get_loc("Volume")] = 999.0

    first = run_strategy_i_backtest({"T": invalid})
    second = run_strategy_i_backtest({"T": changed_invalid})

    assert first["invalid_ohlcv_rows"] == second["invalid_ohlcv_rows"] == 1
    assert first["data_fingerprint"] != second["data_fingerprint"]
    assert first["n_signals"] == second["n_signals"] == 0


def test_runner_is_invariant_to_dictionary_order() -> None:
    frame_a, _ = _strategy_i_frame()
    frame_b, _ = _strategy_i_frame(n=320)
    data_one = {"B": frame_b, "A": frame_a}
    data_two = {"A": frame_a, "B": frame_b}

    first = run_strategy_i_backtest(data_one)
    second = run_strategy_i_backtest(data_two)

    assert first["data_fingerprint"] == second["data_fingerprint"]
    assert first["trades"] == second["trades"]


def test_runner_rejects_timezone_bound_mismatch() -> None:
    frame, _ = _strategy_i_frame()
    frame.index = frame.index.tz_localize("UTC")

    with pytest.raises(ValueError, match="timezone"):
        run_strategy_i_backtest({"T": frame}, start="2024-01-01")


def test_cli_writes_nonempty_and_zero_trade_csv_headers(
    monkeypatch: pytest.MonkeyPatch, tmp_path
) -> None:
    frame, _ = _strategy_i_frame()
    monkeypatch.setattr(strategy_i, "load_all", lambda: {"T": frame})

    summary_path = tmp_path / "summary.csv"
    monkeypatch.setattr(
        sys,
        "argv",
        [
            "strategy_i",
            "--output",
            str(summary_path),
            "--start",
            frame.index[0].date().isoformat(),
            "--end",
            frame.index[280].date().isoformat(),
        ],
    )
    strategy_i.main()
    trades_path = summary_path.with_name("summary_trades.csv")

    assert pd.read_csv(summary_path).loc[0, "n_trades"] >= 1
    assert list(pd.read_csv(trades_path).columns) == list(_TRADE_COLUMNS)

    zero_summary_path = tmp_path / "zero.csv"
    monkeypatch.setattr(
        sys,
        "argv",
        [
            "strategy_i",
            "--output",
            str(zero_summary_path),
            "--start",
            frame.index[0].date().isoformat(),
            "--end",
            frame.index[10].date().isoformat(),
        ],
    )
    strategy_i.main()
    zero_trades_path = zero_summary_path.with_name("zero_trades.csv")

    assert pd.read_csv(zero_summary_path).loc[0, "n_trades"] == 0
    assert zero_trades_path.read_text(encoding="utf-8").splitlines() == [
        ",".join(_TRADE_COLUMNS)
    ]