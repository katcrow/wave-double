"""인디케이터 단위 테스트"""

import numpy as np
import pandas as pd
import pytest

from backtest.indicators import angle_k, atr, compute_all, macd, sma


def _series(vals):
    return pd.Series(vals, index=pd.date_range("2025-01-01", periods=len(vals), freq="D"))


def test_sma_basic():
    s = _series([1, 2, 3, 4, 5])
    out = sma(s, 3)
    assert np.isnan(out.iloc[0]) and np.isnan(out.iloc[1])
    assert out.iloc[2] == pytest.approx(2.0)
    assert out.iloc[4] == pytest.approx(4.0)


def test_angle_k_zero_for_flat():
    s = _series([100.0] * 20)
    out = angle_k(s, 5)
    # 처음 5개는 NaN (shift), 이후 0
    assert out.iloc[:5].isna().all()
    assert (out.iloc[5:] == 0.0).all()


def test_angle_k_up_is_positive_down_negative():
    up = _series(list(range(50, 100)))
    down = _series(list(range(80, 30, -1)))
    assert angle_k(up, 5).iloc[-1] > 0
    assert angle_k(down, 5).iloc[-1] < 0


def test_angle_k_scale_independent():
    # 가격 스케일이 달라도 각도 동일 (일평균 수익률 기준)
    a = _series([100.0 * (1.001) ** i for i in range(30)])
    b = _series([1.0 * (1.001) ** i for i in range(30)])
    assert angle_k(a, 5).iloc[-1] == pytest.approx(angle_k(b, 5).iloc[-1])


def test_macd_golden_cross_detected():
    # 상승 추세에서 골든크로스 발생해야 함
    n = 60
    rng = np.random.default_rng(42)
    price = 100 + np.cumsum(np.linspace(0.3, 0.0, n)) + rng.normal(0, 0.5, n)
    price[15:25] -= 3  # 초반 하락 → 이후 상승으로 골든크로스 유도
    close = pd.Series(price)
    out = macd(close)
    assert out["golden"].sum() >= 1


def test_atr_range():
    high = _series([10.0] * 30)
    low = _series([9.0] * 30)
    close = _series([9.5] * 30)
    out = atr(high, low, close, window=14)
    assert out.dropna().iloc[-1] == pytest.approx(1.0, abs=1e-6)


def test_compute_all_adds_columns():
    rng = np.random.default_rng(7)
    n = 100
    base = 50 + np.cumsum(rng.normal(0, 1, n))
    df = pd.DataFrame(
        {
            "Open": base,
            "High": base + 1,
            "Low": base - 1,
            "Close": base,
            "Volume": rng.integers(1000, 5000, n),
        },
        index=pd.date_range("2025-01-01", periods=n, freq="D"),
    )
    out = compute_all(df, 7, 3)
    for col in ["ma_long", "ma_short", "atr14", "macd", "macd_signal", "macd_golden"]:
        assert col in out.columns