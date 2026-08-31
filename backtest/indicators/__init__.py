"""기술적 지표 모듈

- SMA: 단순이동평균 (장기선 L, 단기선 S)
- angle_k: k봉간 일평균 수익률 기준 각도 [도] (scale-independent slope)
- MACD: 표준 MACD(12,26,9) + 시그널선 상향돌파 신호
- ATR: 평균진폭 (목표/손절 계산용)
"""

from __future__ import annotations

import numpy as np
import pandas as pd

# ── 이동평균 ──────────────────────────────────────────────────────────────


def sma(series: pd.Series, window: int) -> pd.Series:
    """단순이동평균 (SMA)"""
    return series.rolling(window=window, min_periods=window).mean()


# ── 각도 ──────────────────────────────────────────────────────────────────


def angle_k(ma: pd.Series, k: int) -> pd.Series:
    """k봉간 일평균 수익률 기준 각도 (도).

    angle_k(t) = atan( (MA_t - MA_{t-k}) / (k * MA_{t-k}) ) * (180/pi)

    - 스케일 독립, 부호 유지 (우상향 +, 우하향 -, 횡보 0)
    - MA: SMA 혹은 EMA 어떤 이동평균이든 적용 가능
    """
    ma_prev = ma.shift(k)
    with np.errstate(divide="ignore", invalid="ignore"):
        ratio = (ma - ma_prev) / (ma_prev * k)
        angle = np.degrees(np.arctan(ratio))
    return pd.Series(angle, index=ma.index)


# ── MACD ──────────────────────────────────────────────────────────────────


def macd(
    close: pd.Series, fast: int = 12, slow: int = 26, signal: int = 9
) -> pd.DataFrame:
    """표준 MACD. 컬럼: macd, signal, hist, golden (시그널선 상향돌파 봉)."""
    ema_fast = close.ewm(span=fast, adjust=False).mean()
    ema_slow = close.ewm(span=slow, adjust=False).mean()
    macd_line = ema_fast - ema_slow
    signal_line = macd_line.ewm(span=signal, adjust=False).mean()
    hist = macd_line - signal_line
    golden = (macd_line > signal_line) & (macd_line.shift(1) <= signal_line.shift(1))
    return pd.DataFrame(
        {"macd": macd_line, "signal": signal_line, "hist": hist, "golden": golden},
        index=close.index,
    )


# ── 스토캐스틱 ────────────────────────────────────────────────────────────


def stochastic(
    close: pd.Series,
    high: pd.Series,
    low: pd.Series,
    k_period: int = 5,
    k_smooth: int = 3,
    d_period: int = 3,
) -> pd.DataFrame:
    """스토캐스틱 (fast %K, slow %D, 골든크로스).

    - raw %K = (Close - n일 최저) / (n일 최고 - n일 최저) * 100
    - %K(fast) = raw %K를 k_smooth일 평활
    - %D(slow) = %K를 d_period일 평활
    - bull = fast %K > slow %D (매수 상태)
    - golden = %K가 %D를 상향돌파한 봉 (전환시점)
    """
    ll = low.rolling(k_period, min_periods=k_period).min()
    hh = high.rolling(k_period, min_periods=k_period).max()
    with np.errstate(divide="ignore", invalid="ignore"):
        raw_k = (close - ll) / (hh - ll) * 100.0
    k = raw_k.rolling(k_smooth, min_periods=1).mean()
    d = k.rolling(d_period, min_periods=1).mean()
    golden = (k > d) & (k.shift(1) <= d.shift(1))
    return pd.DataFrame(
        {"stoch_k": k, "stoch_d": d, "stoch_bull": k > d, "stoch_golden": golden},
        index=close.index,
    )


# ── OBV ───────────────────────────────────────────────────────────────────


def obv(close: pd.Series, volume: pd.Series) -> pd.Series:
    """On-Balance Volume: 주가 상승일 +거래량, 하락일 -거래량 누적."""
    direction = np.sign(close.diff()).fillna(0.0)
    return (direction * volume).cumsum()


def obv_cross(close: pd.Series, volume: pd.Series, window: int = 20) -> pd.DataFrame:
    """OBV와 그 SMA의 상향돌파 (골든크로스) + 추세 필터.

    - bulk = OBV > OBV_SMA (누적 매집 추세)
    - golden = OBV가 OBV_SMA를 상향돌파한 봉 (매집 전환시점)
    """
    obv_series = obv(close, volume)
    ma = obv_series.rolling(window, min_periods=window).mean()
    golden = (obv_series > ma) & (obv_series.shift(1) <= ma.shift(1))
    return pd.DataFrame(
        {"obv": obv_series, "obv_ma": ma, "obv_bull": obv_series > ma, "obv_golden": golden},
        index=close.index,
    )


# ── RSI ───────────────────────────────────────────────────────────────────


def rsi(close: pd.Series, window: int = 14) -> pd.Series:
    """상대강도지수 (Wilder 평활)."""
    delta = close.diff()
    gain = delta.clip(lower=0.0)
    loss = -delta.clip(upper=0.0)
    avg_gain = gain.ewm(alpha=1 / window, min_periods=window, adjust=False).mean()
    avg_loss = loss.ewm(alpha=1 / window, min_periods=window, adjust=False).mean()
    rs = avg_gain / avg_loss.replace(0.0, np.nan)
    out = 100.0 - 100.0 / (1.0 + rs)
    return out.fillna(50.0)


# ── CCI ───────────────────────────────────────────────────────────────────


def cci(
    high: pd.Series,
    low: pd.Series,
    close: pd.Series,
    window: int = 20,
) -> pd.Series:
    """Commodity Channel Index."""
    tp_m = (high + low + close) / 3.0
    sma_tp = tp_m.rolling(window, min_periods=window).mean()
    mad = tp_m.rolling(window, min_periods=window).apply(
        lambda x: np.abs(x - x.mean()).mean(), raw=True
    )
    return (tp_m - sma_tp) / (0.015 * mad.replace(0.0, np.nan))


# ── ATR ───────────────────────────────────────────────────────────────────


def atr(
    high: pd.Series,
    low: pd.Series,
    close: pd.Series,
    window: int = 14,
) -> pd.Series:
    """평균진폭 (Average True Range).

    TR = max(high-low, |high-prev_close|, |low-prev_close|)
    ATR = Wilder smoothing (EWM alpha=1/window)
    """
    prev_close = close.shift(1)
    tr = pd.concat(
        [
            high - low,
            (high - prev_close).abs(),
            (low - prev_close).abs(),
        ],
        axis=1,
    ).max(axis=1)
    return tr.ewm(alpha=1 / window, min_periods=window, adjust=False).mean()


# ── 지표 일괄 계산 ────────────────────────────────────────────────────────


def compute_all(
    df: pd.DataFrame,
    long_window: int,
    short_window: int,
    macd_fast: int = 12,
    macd_slow: int = 26,
    macd_signal: int = 9,
    stoch_k: int = 5,
    stoch_d: int = 3,
    stoch_smooth: int = 3,
    obv_window: int = 20,
    rsi_window: int = 14,
    cci_window: int = 20,
) -> pd.DataFrame:
    """한 종목 프레임에 파동중첩 전략에 필요한 지표를 모두 추가.

    df: index=DatetimeIndex, 컬럼 Open/High/Low/Close/Volume
    반환: 원본 + ma_long, ma_short, atr14, macd/stoch/obv/rsi/cci
    """
    out = df.copy()
    out["ma_long"] = sma(out["Close"], long_window)
    out["ma_short"] = sma(out["Close"], short_window)
    out["atr14"] = atr(out["High"], out["Low"], out["Close"])
    macd_df = macd(out["Close"], fast=macd_fast, slow=macd_slow, signal=macd_signal)
    out["macd"] = macd_df["macd"]
    out["macd_signal"] = macd_df["signal"]
    out["macd_golden"] = macd_df["golden"]
    stoch_df = stochastic(
        out["Close"], out["High"], out["Low"],
        k_period=stoch_k, k_smooth=stoch_smooth, d_period=stoch_d,
    )
    out["stoch_k"] = stoch_df["stoch_k"]
    out["stoch_d"] = stoch_df["stoch_d"]
    out["stoch_bull"] = stoch_df["stoch_bull"]
    out["stoch_golden"] = stoch_df["stoch_golden"]
    obv_df = obv_cross(out["Close"], out["Volume"], window=obv_window)
    out["obv"] = obv_df["obv"]
    out["obv_ma"] = obv_df["obv_ma"]
    out["obv_bull"] = obv_df["obv_bull"]
    out["obv_golden"] = obv_df["obv_golden"]
    out["rsi"] = rsi(out["Close"], window=rsi_window)
    cci_series = cci(out["High"], out["Low"], out["Close"], window=cci_window)
    out["cci"] = cci_series
    return out