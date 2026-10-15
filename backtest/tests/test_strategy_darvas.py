"""다바스 박스 탐지·진입·결합 백테스트 회귀 테스트.

합성 프레임으로 박스 형성 → 상단 돌파 / 하단 반등 / 결합 중복보유 금지를 검증한다.
"""

import numpy as np
import pandas as pd
import pytest

from backtest.engine import TradeParams, run_backtest
from backtest.indicator_opt.strategy_darvas import (
    BREAKOUT,
    COMBINED,
    DARVAS_PARAMS,
    REBOUND,
    DarvasParams,
    _collect_trades,
    darvas_masks,
    darvas_masks_full,
    darvas_signals,
    run_darvas_backtest,
    run_darvas_grid,
    validate_darvas_params,
)


def _frame(high, low, close) -> pd.DataFrame:
    close_arr = np.array(close, dtype=float)
    dates = pd.date_range("2024-01-01", periods=len(close_arr), freq="B")
    return pd.DataFrame(
        {
            "Open": close_arr,
            "High": np.array(high, dtype=float),
            "Low": np.array(low, dtype=float),
            "Close": close_arr,
            "Volume": np.full(len(close_arr), 100.0),
        },
        index=dates,
    )


# confirm_days=2, high_lookback=3 기준:
#   idx2 신고가 12 → idx3·idx4 고가 하락(2일) → 상단 12 확정
#   idx5 저가 10.4 → idx6·idx7 저가 상승(2일) → 하단 10.4 확정, idx8부터 박스 활성
_BASE_H = [10, 11, 12, 11.5, 11.0, 10.8, 11.0, 11.5]
_BASE_L = [9, 10, 11, 10.8, 10.5, 10.4, 10.7, 11.1]
_BASE_C = [9.5, 10.5, 11.5, 11.0, 10.8, 10.6, 10.9, 11.4]


def _breakout_frame() -> pd.DataFrame:
    high = _BASE_H + [12.5, 12.0]
    low = _BASE_L + [11.5, 11.6]
    close = _BASE_C + [12.4, 11.8]
    return _frame(high, low, close)


def _rebound_frame() -> pd.DataFrame:
    high = _BASE_H + [10.7, 10.9]
    low = _BASE_L + [10.2, 10.4]
    close = _BASE_C + [10.5, 10.7]
    return _frame(high, low, close)


def _combined_frame() -> pd.DataFrame:
    # idx8 하단 반등, idx10 상단 돌파 (같은 박스 안에서 순차 발생)
    high = _BASE_H + [10.7, 11.0, 12.5]
    low = _BASE_L + [10.2, 10.6, 11.0]
    close = _BASE_C + [10.5, 10.9, 12.4]
    return _frame(high, low, close)


def _test_params(**overrides) -> DarvasParams:
    base = dict(confirm_days=2, high_lookback=3, atr_window=3)
    base.update(overrides)
    return DarvasParams(**base)


def test_breakout_mask_fires_on_ceiling_break_day() -> None:
    brk, reb = darvas_masks(_breakout_frame(), _test_params())

    assert brk.dtype == bool and reb.dtype == bool
    assert brk.sum() == 1
    assert int(np.flatnonzero(brk.to_numpy())[0]) == 8
    assert reb.sum() == 0


def test_rebound_mask_fires_on_failed_floor_break_day() -> None:
    brk, reb = darvas_masks(_rebound_frame(), _test_params())

    assert reb.sum() == 1
    assert int(np.flatnonzero(reb.to_numpy())[0]) == 8
    assert brk.sum() == 0


def test_combined_mode_is_union_of_both_signals() -> None:
    frame = _combined_frame()
    params = _test_params()

    brk, reb = darvas_masks(frame, params)
    assert int(np.flatnonzero(brk.to_numpy())[0]) == 10
    assert int(np.flatnonzero(reb.to_numpy())[0]) == 8

    combined = darvas_signals(frame, ticker="T", params=params, mode=COMBINED)
    assert [s.date for s in combined] == [frame.index[8], frame.index[10]]

    assert len(darvas_signals(frame, ticker="T", params=params, mode=BREAKOUT)) == 1
    assert len(darvas_signals(frame, ticker="T", params=params, mode=REBOUND)) == 1


def test_combined_backtest_forbids_duplicate_holding_per_ticker() -> None:
    frame = _combined_frame()
    # 넓은 TP/SL + 최대보유 없음 → 첫 거래가 끝까지 보유, 이후 신호는 중복으로 스킵된다.
    params = _test_params(tp_atr=100.0, sl_atr=100.0, max_holding_bars=None)
    signals = darvas_signals(frame, ticker="T", params=params, mode=COMBINED)

    trades = run_backtest(
        frame,
        signals,
        TradeParams(tp_atr=100.0, sl_atr=100.0, atr_window=3),
        ticker="T",
    )

    assert len(trades) == 1
    assert trades[0].entry_date == frame.index[8]


def test_run_darvas_backtest_end_to_end_per_mode() -> None:
    data = {"BO": _breakout_frame(), "RE": _rebound_frame()}
    params = _test_params()

    for mode, ticker in ((BREAKOUT, "BO"), (REBOUND, "RE"), (COMBINED, "BO")):
        result = run_darvas_backtest(
            data=data,
            params=params,
            mode=mode,
            start=pd.Timestamp("2024-01-01"),
            end=pd.Timestamp("2024-12-31"),
        )
        assert result["mode"] == mode
        assert result["strategy"] == "DARVAS"
        assert result["n_signals"] >= 1


def test_run_darvas_grid_reports_all_modes() -> None:
    data = {"BO": _breakout_frame(), "RE": _rebound_frame()}

    grid = run_darvas_grid(
        confirm_days=(2,),
        high_lookback=3,
        data=data,
        min_trades=1,
    )

    assert set(grid["mode"]) == {"breakout", "rebound", "combined"}
    assert len(grid) == 3
    assert (grid["confirm_days"] == 2).all()


def test_validate_darvas_params_rejects_bad_values() -> None:
    with pytest.raises(ValueError):
        validate_darvas_params(DarvasParams(confirm_days=0))
    with pytest.raises(ValueError):
        validate_darvas_params(DarvasParams(high_lookback=1))
    with pytest.raises(ValueError):
        validate_darvas_params(DarvasParams(tp_atr=0.0))


def test_darvas_signals_rejects_unknown_mode() -> None:
    with pytest.raises(ValueError):
        darvas_signals(_breakout_frame(), params=_test_params(), mode="nope")


def test_default_params_are_valid() -> None:
    validate_darvas_params(DARVAS_PARAMS)


def test_default_exit_path_matches_engine() -> None:
    """기본 플래그(ATR TP/SL, floor off)에서 시뮬레이터가 엔진과 동일 결과를 낸다."""
    data = {
        "BO": _breakout_frame(),
        "RE": _rebound_frame(),
        "CO": _combined_frame(),
    }
    params = _test_params(tp_atr=3.0, sl_atr=2.0, max_holding_bars=None)
    start, end = pd.Timestamp("2024-01-01"), pd.Timestamp("2024-12-31")

    got, _ = _collect_trades(data, params, COMBINED, start, end)

    expected = []
    trade_params = TradeParams(tp_atr=3.0, sl_atr=2.0, atr_window=3)
    for ticker, frame in data.items():
        signals = darvas_signals(frame, ticker=ticker, params=params, mode=COMBINED)
        expected.extend(run_backtest(frame, signals, trade_params, ticker=ticker))
    expected.sort(key=lambda t: (t.entry_date, t.ticker, t.exit_date))

    assert [t.to_dict() for t in got] == [t.to_dict() for t in expected]


def test_floor_exit_fires_on_box_floor_break() -> None:
    # idx8 상단 돌파(진입) → idx9 저가 10.0 < 박스 하단 10.4 이탈
    frame = _frame(
        _BASE_H + [12.5, 11.0],
        _BASE_L + [11.5, 10.0],
        _BASE_C + [12.4, 10.2],
    )
    params = _test_params(exit_atr_sl=False, exit_atr_tp=False, exit_floor=True)
    start, end = pd.Timestamp("2024-01-01"), pd.Timestamp("2024-12-31")

    trades, _ = _collect_trades({"T": frame}, params, BREAKOUT, start, end)

    assert len(trades) == 1
    assert trades[0].entry_date == frame.index[8]
    assert trades[0].exit_reason == "floor"
    assert trades[0].exit_price == pytest.approx(10.4)


def test_floor_exit_off_holds_to_end() -> None:
    # exit_floor=False + ATR TP/SL을 아주 넓게 → 데이터 끝까지 보유(end)
    frame = _frame(
        _BASE_H + [12.5, 11.0],
        _BASE_L + [11.5, 10.0],
        _BASE_C + [12.4, 10.2],
    )
    params = _test_params(tp_atr=100.0, sl_atr=100.0, exit_floor=False)
    start, end = pd.Timestamp("2024-01-01"), pd.Timestamp("2024-12-31")

    trades, _ = _collect_trades({"T": frame}, params, BREAKOUT, start, end)

    assert len(trades) == 1
    assert trades[0].exit_reason == "end"


def test_validate_rejects_all_exits_disabled() -> None:
    with pytest.raises(ValueError):
        validate_darvas_params(
            DarvasParams(exit_atr_tp=False, exit_atr_sl=False, exit_floor=False)
        )
    with pytest.raises(ValueError):
        validate_darvas_params(DarvasParams(exit_floor=1))  # type: ignore[arg-type]


def test_darvas_masks_full_exposes_box_floor_and_ceiling() -> None:
    brk, _reb, floor, ceiling = darvas_masks_full(_breakout_frame(), _test_params())

    pos = int(np.flatnonzero(brk.to_numpy())[0])
    assert ceiling.iloc[pos] == pytest.approx(12.0)
    assert floor.iloc[pos] == pytest.approx(10.4)


def test_min_box_width_filters_narrow_boxes() -> None:
    # _breakout_frame: 천장 12, 바닥 10.4 → 폭 (12-10.4)/10.4 ≈ 0.1538
    frame = _breakout_frame()
    assert len(darvas_signals(frame, params=_test_params(min_box_width=0.10),
                              mode=BREAKOUT)) == 1
    assert len(darvas_signals(frame, params=_test_params(min_box_width=0.20),
                              mode=BREAKOUT)) == 0

    start, end = pd.Timestamp("2024-01-01"), pd.Timestamp("2024-12-31")
    kept, _ = _collect_trades(
        {"T": frame}, _test_params(min_box_width=0.10), BREAKOUT, start, end
    )
    dropped, _ = _collect_trades(
        {"T": frame}, _test_params(min_box_width=0.20), BREAKOUT, start, end
    )
    assert len(kept) == 1
    assert len(dropped) == 0


def test_validate_rejects_negative_min_box_width() -> None:
    with pytest.raises(ValueError):
        validate_darvas_params(DarvasParams(min_box_width=-0.1))
    with pytest.raises(ValueError):
        validate_darvas_params(DarvasParams(trail_atr=0.0))


def test_trailing_stop_exits_after_ratchet() -> None:
    # idx8 진입(close 12.4) → idx9 고가 14 로 러닝하이 갱신 → idx10 저가 12.0 이
    # 트레일선(러닝하이 14 - 1.0*ATR)을 밑돌면 trail 청산.
    frame = _frame(
        _BASE_H + [12.5, 14.0, 12.6],
        _BASE_L + [11.5, 12.2, 12.0],
        _BASE_C + [12.4, 13.5, 12.1],
    )
    params = _test_params(
        exit_atr_tp=False, exit_atr_sl=False, exit_floor=False, trail_atr=1.0,
    )
    start, end = pd.Timestamp("2024-01-01"), pd.Timestamp("2024-12-31")

    trades, _ = _collect_trades({"T": frame}, params, BREAKOUT, start, end)

    assert len(trades) == 1
    assert trades[0].exit_reason == "trail"
    assert trades[0].entry_date == frame.index[8]
    assert trades[0].exit_date == frame.index[10]
