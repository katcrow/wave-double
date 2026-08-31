"""보조지표별 매수 시그널 생성기 (docs/상승-보조지표-패턴.md 기반)

각 함수는 (df: OHLCV, **params) -> pd.Series[bool] (매수 신호 봉) 를 반환.
백테스트 엔진에서 각 시그널 봉의 종가로 진입 / ATR 기반 TP·SL 청산.

모든 지표는 벡터화로 계산되어 빠르며, 파라미터 최적화 그리드에 사용된다.
"""

from __future__ import annotations

from dataclasses import dataclass

import numpy as np
import pandas as pd


@dataclass
class SimpleSignal:
    """엔진 인터페이스와 호환되는 최소 진입 시그널 (종가 진입)"""

    ticker: str
    date: pd.Timestamp
    price: float
    stop_price: float | None = None
    take_profit_pct: float | None = None
    take_profit_price: float | None = None


# ── 기본 보조 함수 ──────────────────────────────────────────────────────────


def _sma(s: pd.Series, w: int) -> pd.Series:
    return s.rolling(w, min_periods=w).mean()


def _cross_up(a: pd.Series, b: pd.Series) -> pd.Series:
    return (a > b) & (a.shift(1) <= b.shift(1))


def _turn_up(a: pd.Series) -> pd.Series:
    return (a > a.shift(1)) & (a.shift(1) <= a.shift(2))


def _wma(s: pd.Series, w: int) -> pd.Series:
    if w < 1:
        w = 1
    weights = np.arange(1, w + 1).astype(float)
    return s.rolling(w, min_periods=w).apply(
        lambda x: float(np.dot(x, weights) / weights.sum()), raw=True
    )


def _true_range(h: pd.Series, l: pd.Series, c: pd.Series) -> pd.Series:
    pc = c.shift(1)
    return pd.concat([h - l, (h - pc).abs(), (l - pc).abs()], axis=1).max(axis=1)


def _atr(h: pd.Series, l: pd.Series, c: pd.Series, w: int = 14) -> pd.Series:
    return _true_range(h, l, c).ewm(alpha=1 / w, min_periods=w, adjust=False).mean()


# ── 1. 추세 추종 ────────────────────────────────────────────────────────────


def sig_sma_gc(df, short=5, long=20):
    """SMA 골든크로스: 단기 이평이 장기 이평을 상향 돌파"""
    s = _sma(df["Close"], short)
    l = _sma(df["Close"], long)
    return _cross_up(s, l)


def sig_ema_cross(df, span=20):
    """EMA 가격 돌파: 종가가 EMA를 상향 돌파"""
    e = df["Close"].ewm(span=span, adjust=False).mean()
    return _cross_up(df["Close"], e)


def sig_dema_turn(df, span=20):
    """DEMA 우상향 변곡: DEMA = 2*EMA - EMA(EMA)"""
    e1 = df["Close"].ewm(span=span, adjust=False).mean()
    e2 = e1.ewm(span=span, adjust=False).mean()
    dema = 2 * e1 - e2
    return _turn_up(dema)


def sig_hma_turn(df, n=9):
    """Hull MA 우상향 변곡"""
    half = max(int(n / 2), 1)
    sqrtn = max(int(np.sqrt(n)), 1)
    raw = 2 * _wma(df["Close"], half) - _wma(df["Close"], n)
    hma = _wma(raw, sqrtn)
    return _turn_up(hma)


def sig_macd(df, fast=12, slow=26, signal=9, require_zero=False):
    """MACD: MACD선이 시그널선을 상향 교차 (선택: 0선 위 조건)"""
    ef = df["Close"].ewm(span=fast, adjust=False).mean()
    es = df["Close"].ewm(span=slow, adjust=False).mean()
    macd_line = ef - es
    sig_line = macd_line.ewm(span=signal, adjust=False).mean()
    cross = _cross_up(macd_line, sig_line)
    if require_zero:
        return cross & (macd_line > 0)
    return cross


def sig_adx(df, length=14, threshold=20.0):
    """ADX/DMI: +DI가 -DI를 상향 돌파하고 ADX >= threshold"""
    up_move = df["High"].diff()
    down_move = -df["Low"].diff()
    plus_dm = np.where((up_move > down_move) & (up_move > 0), up_move, 0.0)
    minus_dm = np.where((down_move > up_move) & (down_move > 0), down_move, 0.0)
    tr = _true_range(df["High"], df["Low"], df["Close"])
    atr_s = tr.ewm(alpha=1 / length, min_periods=length, adjust=False).mean()
    plus_di = 100 * pd.Series(plus_dm, index=df.index).ewm(
        alpha=1 / length, min_periods=length, adjust=False
    ).mean() / atr_s
    minus_di = 100 * pd.Series(minus_dm, index=df.index).ewm(
        alpha=1 / length, min_periods=length, adjust=False
    ).mean() / atr_s
    dx = 100 * (plus_di - minus_di).abs() / (plus_di + minus_di)
    adx = dx.ewm(alpha=1 / length, min_periods=length, adjust=False).mean()
    cross = _cross_up(plus_di, minus_di)
    return cross & (adx >= threshold)


def sig_ichimoku(df, conversion=9, base=26, span=52):
    """일목균형표 삼역호전: 전환선>기준선, 주가>구름, 후행>26일전"""
    tenkan = (df["High"].rolling(conversion).max() + df["Low"].rolling(conversion).min()) / 2
    kijun = (df["High"].rolling(base).max() + df["Low"].rolling(base).min()) / 2
    senkou_a = (tenkan + kijun) / 2
    senkou_b = (df["High"].rolling(span).max() + df["Low"].rolling(span).min()) / 2
    cloud_top = pd.concat([senkou_a, senkou_b], axis=1).max(axis=1)
    cond1 = tenkan > kijun
    cond2 = df["Close"] > cloud_top
    cond3 = df["Close"] > df["Close"].shift(base)
    return cond1 & cond2 & cond3


def sig_aroon(df, n=25):
    """아룬 오실레이터 0선 상향 돌파"""
    up = df["High"].rolling(n + 1).apply(lambda x: n - np.argmax(x), raw=True)
    down = df["Low"].rolling(n + 1).apply(lambda x: n - np.argmin(x), raw=True)
    osc = up - down
    return _cross_up(osc, pd.Series(0.0, index=df.index))


def sig_supertrend(df, atr_period=10, multiplier=3.0):
    """슈퍼트렌드: 하락→상승 반전 (종가가 상단 밴드 돌파)"""
    hl2 = (df["High"] + df["Low"]) / 2
    a = _atr(df["High"], df["Low"], df["Close"], atr_period)
    basic_up = hl2 + multiplier * a
    basic_lo = hl2 - multiplier * a
    up = pd.Series(index=df.index, dtype=float)
    lo = pd.Series(index=df.index, dtype=float)
    trend = pd.Series(index=df.index, dtype=float)  # 1 상승, -1 하락
    prev_up = prev_lo = prev_tr = np.nan
    up_list, lo_list, tr_list = [], [], []
    for i in range(len(df)):
        cu = basic_up.iloc[i]
        cl = basic_lo.iloc[i]
        if np.isnan(prev_up):
            u = cu
            l = cl
        else:
            u = cu if (cu < prev_up or df["Close"].iloc[i - 1] > prev_up) else prev_up
            l = cl if (cl > prev_lo or df["Close"].iloc[i - 1] < prev_lo) else prev_lo
        if np.isnan(prev_tr):
            t = 1
        elif prev_tr == 1:
            t = 1 if df["Close"].iloc[i] <= prev_up else -1
        else:
            t = -1 if df["Close"].iloc[i] >= prev_lo else 1
        up_list.append(u)
        lo_list.append(l)
        tr_list.append(t)
        prev_up, prev_lo, prev_tr = u, l, t
    up = pd.Series(up_list, index=df.index)
    lo = pd.Series(lo_list, index=df.index)
    trend = pd.Series(tr_list, index=df.index)
    st = np.where(trend == 1, lo, up)
    # 상승 반전 봉: 종가가 슈퍼트렌드를 상향 돌파
    return (df["Close"].shift(1) <= pd.Series(st, index=df.index).shift(1)) & (
        df["Close"] > pd.Series(st, index=df.index)
    )


def sig_parabolic_sar(df, af_step=0.02, af_max=0.2):
    """파라볼릭 SAR: 점이 가격 위(하락) → 아래(상승)로 반전"""
    h = df["High"].to_numpy()
    l = df["Low"].to_numpy()
    c = df["Close"].to_numpy()
    n = len(df)
    sar = np.full(n, np.nan)
    trend = np.full(n, np.nan)  # 1 상승, -1 하락
    af = np.full(n, np.nan)
    ep = np.full(n, np.nan)
    sar[0] = l[0]
    trend[0] = 1
    af[0] = af_step
    ep[0] = h[0]
    for i in range(1, n):
        prev_sar = sar[i - 1]
        cur = prev_sar + af[i - 1] * (ep[i - 1] - prev_sar)
        if trend[i - 1] == 1:
            cur = min(cur, l[i - 1])
            if l[i] < cur:
                trend[i] = -1
                sar[i] = ep[i - 1]
                af[i] = af_step
                ep[i] = l[i]
            else:
                trend[i] = 1
                sar[i] = cur
                af[i] = min(af[i - 1] + af_step, af_max)
                ep[i] = max(ep[i - 1], h[i])
        else:
            cur = max(cur, h[i - 1])
            if h[i] > cur:
                trend[i] = 1
                sar[i] = ep[i - 1]
                af[i] = af_step
                ep[i] = h[i]
            else:
                trend[i] = -1
                sar[i] = cur
                af[i] = min(af[i - 1] + af_step, af_max)
                ep[i] = min(ep[i - 1], l[i])
    sar_s = pd.Series(sar, index=df.index)
    # 점이 가격 위 → 아래로 반전 (하락→상승)
    return (df["Close"].shift(1) <= sar_s.shift(1)) & (df["Close"] > sar_s)


# ── 2. 모멘텀 오실레이터 ────────────────────────────────────────────────────


def sig_rsi(df, period=14, threshold=30, mode="cross"):
    """RSI: 과매도 기준선(threshold) 탈출 반등"""
    delta = df["Close"].diff()
    gain = delta.clip(lower=0.0)
    loss = -delta.clip(upper=0.0)
    ag = gain.ewm(alpha=1 / period, min_periods=period, adjust=False).mean()
    al = loss.ewm(alpha=1 / period, min_periods=period, adjust=False).mean()
    rs = ag / al.replace(0.0, np.nan)
    rsi = (100.0 - 100.0 / (1.0 + rs)).fillna(50.0)
    if mode == "cross":
        return (rsi.shift(1) <= threshold) & (rsi > threshold)
    return rsi > threshold  # bull


def sig_stoch(df, k_period=5, d_period=3, oversold=20):
    """스토캐스틱: %K가 %D를 과매도(oversold) 내 상향 교차"""
    ll = df["Low"].rolling(k_period).min()
    hh = df["High"].rolling(k_period).max()
    k = ((df["Close"] - ll) / (hh - ll) * 100.0).replace([np.inf, -np.inf], np.nan)
    k = k.rolling(3, min_periods=1).mean()
    d = k.rolling(d_period, min_periods=1).mean()
    return _cross_up(k, d) & (k <= oversold)


def sig_stoch_double_bottom(df, k_period=5, d_period=3, threshold=30.0):
    """스토캐스틱 %K 쌍바닥(Double Bottom) 매수.

    slow %K (5-3-3): 원시%K(5) → 3일 평활 → %D는 3일.
    매수 조건 (lookahead 없이 forward 순회):
      1. %K가 국소 저점 두 개(쌍바닥)를 형성, 둘 다 threshold(과매도) 하단
      2. 두 저점 사이 반등 고점(넥라인)이 존재
      3. 두 번째 저점이 첫 저점보다 낮지 않음 (높은 저점/동일 수준)
      4. %K가 그 넥라인을 상향 돌파하는 봉 → 매수
    """
    ll = df["Low"].rolling(k_period).min()
    hh = df["High"].rolling(k_period).max()
    k = ((df["Close"] - ll) / (hh - ll) * 100.0).replace([np.inf, -np.inf], np.nan)
    k = k.rolling(3, min_periods=1).mean()  # slow %K
    k = k.fillna(0.0)
    sig = _double_bottom_signal(k.to_numpy(dtype=float), threshold)

    return pd.Series(sig, index=df.index)


def _double_bottom_signal(vals, threshold):
    """범용 쌍바닥(Double Bottom) 신호. lookahead 없는 forward 순회.

    매수 조건:
      1. 시계열이 국소 저점 두 개(쌍바닥)를 형성, 둘 다 threshold 하단
      2. 두 저점 사이 반등 고점(넥라인) 존재, 저점들보다 높음
      3. 두 번째 저점이 첫 저점보다 낮지 않음 (동일/높은 저점 = higher low)
      4. 시계열이 그 넥라인을 상향 돌파하는 시점 → 시그널
    """
    n = len(vals)
    sig = np.zeros(n, dtype=bool)
    prev_trough_v = np.nan
    neck_v = np.nan      # 두 저점 사이 반등 고점(넥라인)
    pending = False      # 두 번째 저점 확인 대기

    for t in range(2, n):
        # 국소 저점: t-1에서 꺾임(하락→상승)이 확인된 시점
        if vals[t] > vals[t - 1] and vals[t - 1] <= vals[t - 2]:
            cur_v = vals[t - 1]
            if pending and prev_trough_v is not None:
                both_os = (prev_trough_v <= threshold) and (cur_v <= threshold)
                higher_low = (cur_v >= prev_trough_v - 1e-9)
                if both_os and higher_low and not np.isnan(neck_v):
                    if neck_v > max(prev_trough_v, cur_v):
                        neck2 = neck_v
                        # 이후 시계열이 넥라인을 상향 돌파 → 시그널
                        for tt in range(t, n):
                            if vals[tt] > neck2 and vals[tt - 1] <= neck2:
                                sig[tt] = True
                            # 돌파 전 다시 두 저점 아래로 가면 취소(쌍바닥 붕괴)
                            elif vals[tt] < min(prev_trough_v, cur_v):
                                break
            prev_trough_v = cur_v
            neck_v = np.nan
            pending = True
        elif vals[t] > vals[t - 1] and vals[t - 1] >= vals[t - 2]:
            # 국소 고점: t-1이 반등 고점 → 넥라인 업데이트
            if pending:
                neck_v = vals[t - 1] if np.isnan(neck_v) else max(neck_v, vals[t - 1])

    return sig


def _weekly_stoch_k(df, k_period=10, d_period=6):
    """주봉 slow 스토캐스틱 %K (k_period-d_period): daily 정렬값 반환.

    daily를 ISO주(월~금)로 리샘플링(주봉 OHLC, 현재 주는 WTD) 후
    raw %K(k_period) → slow %K(d_period 평활) 계산, 각 거래일의 소속 주 값으로 매핑.
    """
    prd = df.index.to_period("W-SUN")
    wf = pd.DataFrame({
        "wopen": df["Open"].groupby(prd).first(),
        "whigh": df["High"].groupby(prd).max(),
        "wlow": df["Low"].groupby(prd).min(),
        "wclose": df["Close"].groupby(prd).last(),
    })
    ll = wf["wlow"].rolling(k_period, min_periods=k_period).min()
    hh = wf["whigh"].rolling(k_period, min_periods=k_period).max()
    rng = (hh - ll).replace(0, np.nan)
    raw_k = (wf["wclose"] - ll) / rng * 100.0
    slow_k = raw_k.rolling(d_period, min_periods=1).mean()
    return slow_k.reindex(prd).to_numpy()


def sig_stoch_db_weekly_k(df, k_period=5, d_period=3, threshold=30.0,
                          wk_period=10, wd_period=6):
    """일봉 스토캐스틱 %K 쌍바닥 + 주봉 K 우상향 필터.

    기본 신호: sig_stoch_double_bottom (5-3-3 %K 쌍바닥, 넥라인 돌파)
    추가 필터: 당일이 속한 주봉(10-6-6) %K가 직전 주보다 조금이라도 우상향 (K > 전주 K)
    """
    base = sig_stoch_double_bottom(df, k_period=k_period, d_period=d_period, threshold=threshold)
    week_k = _weekly_stoch_k(df, wk_period, wd_period)
    wks = pd.Series(week_k, index=df.index)
    rising = wks > wks.shift(1)
    return base & rising.fillna(False)


def sig_cmo(df, period=9, signal=10):
    """Chande Momentum Oscillator: CMO가 자기 SMA 상향 돌파"""
    delta = df["Close"].diff()
    su = delta.clip(lower=0.0).rolling(period).sum()
    sd = (-delta.clip(upper=0.0)).rolling(period).sum()
    cmo = 100 * (su - sd) / (su + sd)
    m = cmo.rolling(signal, min_periods=signal).mean()
    return _cross_up(cmo, m)


def sig_williams_r(df, period=14, threshold=80):
    """Williams %R: -threshold(과매도) 탈출"""
    hh = df["High"].rolling(period).max()
    ll = df["Low"].rolling(period).min()
    wr = (hh - df["Close"]) / (hh - ll) * -100.0
    return (wr.shift(1) <= -threshold) & (wr > -threshold)


def sig_cci(df, period=20, threshold=100):
    """CCI: -threshold 침체선 탈출"""
    tp = (df["High"] + df["Low"] + df["Close"]) / 3
    ma = tp.rolling(period).mean()
    mad = tp.rolling(period).apply(lambda x: np.abs(x - x.mean()).mean(), raw=True)
    cci = (tp - ma) / (0.015 * mad.replace(0.0, np.nan))
    return (cci.shift(1) <= -threshold) & (cci > -threshold)


def sig_ao(df, fast=5, slow=34):
    """Awesome Oscillator 0선 돌파"""
    mp = (df["High"] + df["Low"]) / 2
    ao = mp.rolling(fast).mean() - mp.rolling(slow).mean()
    return _cross_up(ao, pd.Series(0.0, index=df.index))


def sig_tsi(df, r=25, s=13):
    """TSI 0선 상향 교차"""
    pc = df["Close"].diff()
    s1 = pc.ewm(alpha=1 / r, adjust=False).mean().ewm(alpha=1 / s, adjust=False).mean()
    s2 = pc.abs().ewm(alpha=1 / r, adjust=False).mean().ewm(alpha=1 / s, adjust=False).mean()
    tsi = 100 * s1 / s2
    return _cross_up(tsi, pd.Series(0.0, index=df.index))


def sig_vortex(df, n=14):
    """보텍스: VI+가 VI-를 상향 돌파"""
    vm_plus = (df["High"] - df["Low"].shift(1)).abs()
    vm_minus = (df["Low"] - df["High"].shift(1)).abs()
    tr = _true_range(df["High"], df["Low"], df["Close"])
    vi_plus = vm_plus.rolling(n).sum() / tr.rolling(n).sum()
    vi_minus = vm_minus.rolling(n).sum() / tr.rolling(n).sum()
    return _cross_up(vi_plus, vi_minus)


def sig_ibs(df, period=1, threshold=0.1):
    """Internal Bar Strength: 극단 과매도 (IBS <= threshold)"""
    rng = (df["High"] - df["Low"]).replace(0.0, np.nan)
    ibs = (df["Close"] - df["Low"]) / rng
    base = ibs <= threshold
    if period > 1:
        return base.rolling(period, min_periods=period).any()
    return base


# ── 3. 변동성 및 돌파 ───────────────────────────────────────────────────────


def sig_bollinger(df, period=20, dev=2.0, squeeze=20):
    """볼린저: 스퀴즈(밴드폭 최저) 후 종가 상단 밴드 돌파"""
    ma = df["Close"].rolling(period).mean()
    sd = df["Close"].rolling(period).std()
    upper = ma + dev * sd
    lower = ma - dev * sd
    bandwidth = (upper - lower) / ma
    is_squeezed = bandwidth == bandwidth.rolling(squeeze, min_periods=squeeze).min()
    return is_squeezed & (df["Close"].shift(1) <= upper.shift(1)) & (df["Close"] > upper)


def sig_donchian(df, n=20):
    """돈치안: 종가가 직전 n일 최고가를 돌파"""
    upper = df["High"].shift(1).rolling(n).max()
    return df["Close"] > upper


def sig_ttm_squeeze(df, bb_period=20, bb_dev=2.0, kc_period=20, kc_mult=1.5):
    """TTM Squeeze: 이전 스퀴즈 상태에서 발사 + 양의 모멘텀"""
    ma = df["Close"].rolling(bb_period).mean()
    sd = df["Close"].rolling(bb_period).std()
    bb_u = ma + bb_dev * sd
    bb_l = ma - bb_dev * sd
    tr = _true_range(df["High"], df["Low"], df["Close"])
    kema = df["Close"].ewm(span=kc_period, adjust=False).mean()
    kc_u = kema + kc_mult * tr.ewm(span=kc_period, adjust=False).mean()
    kc_l = kema - kc_mult * tr.ewm(span=kc_period, adjust=False).mean()
    squeeze_on_prev = (bb_u.shift(1) < kc_u.shift(1)) & (bb_l.shift(1) > kc_l.shift(1))
    squeeze_fired_now = (bb_u >= kc_u) | (bb_l <= kc_l)
    hist = (df["Close"] - df["Close"].shift(1))
    mom = hist.rolling(20, min_periods=20).sum()
    return squeeze_on_prev & squeeze_fired_now & (mom > 0)


# ── 4. 거래량 및 수급 ───────────────────────────────────────────────────────


def sig_cmf(df, period=20):
    """Chaikin Money Flow: 0선 상향 돌파"""
    rng = (df["High"] - df["Low"]).replace(0.0, np.nan)
    mfm = ((df["Close"] - df["Low"]) - (df["High"] - df["Close"])) / rng
    mfv = mfm * df["Volume"]
    cmf = mfv.rolling(period).sum() / df["Volume"].rolling(period).sum()
    return _cross_up(cmf, pd.Series(0.0, index=df.index))


def sig_obv(df, window=20):
    """OBV: OBV가 자기 SMA를 상향 돌파"""
    direction = np.sign(df["Close"].diff()).fillna(0.0)
    obv = (direction * df["Volume"]).cumsum()
    ma = obv.rolling(window, min_periods=window).mean()
    return _cross_up(obv, ma)


def sig_vixfix(df, period=22, peak_ratio=0.9):
    """Williams VixFix: 패닉 피크 후 꺾임"""
    hh = df["Close"].rolling(period).max()
    vf = (hh - df["Low"]) / hh * 100.0
    peak = vf.rolling(period).max()
    return (vf.shift(1) >= peak.shift(1) * peak_ratio) & (vf < vf.shift(1))


# ── 4b. 다이버전스 ───────────────────────────────────────────────────────────


def _price_troughs(price):
    """국소 저점 (index, value) 목록. 양쪽 이웃보다 낮은 봉."""
    return [(i, price[i]) for i in range(1, len(price) - 1)
            if price[i] < price[i - 1] and price[i] < price[i + 1]]


def _bullish_divergence_signal(price, ind, confirm, div_window=14, min_gap=2):
    """가격 신저가 + 지표 상위 저점(불리시 다이버전스) 후 확정 시그널.

    lookahead 없는 forward 순회:
      1. 가격 국소 저점 두 개(인접)를 찾음
      2. 두 번째 저점이 첫 저점보다 낮음(가격 신저가) & 지표값은 더 높음(상위 저점)
      3. 두 번째 저점 이후 확정(confirm) 봉 → 매수
      4. 확정 전에 가격이 두 번째 저점 아래로 내려가면 취소
    """
    n = len(price)
    troughs = _price_troughs(price)
    sig = np.zeros(n, dtype=bool)
    for a in range(len(troughs) - 1):
        i1, v1 = troughs[a]
        i2, v2 = troughs[a + 1]
        gap = i2 - i1
        if gap < min_gap or gap > div_window:
            continue
        if v2 < v1 and ind[i2] > ind[i1]:
            for c in range(i2 + 1, n):
                if confirm[c]:
                    sig[c] = True
                    break
                if price[c] < v2:
                    break
    return sig


def sig_div_rsi(df, period=14, div_window=14, min_gap=2, thr_cross=30.0):
    """RSI 하락(불리시) 다이버전스: 가격 신저가 + RSI 상위 저점 후 RSI 기준선 상향교차"""
    delta = df["Close"].diff()
    gain = delta.clip(lower=0.0)
    loss = -delta.clip(upper=0.0)
    ag = gain.ewm(alpha=1 / period, min_periods=period, adjust=False).mean()
    al = loss.ewm(alpha=1 / period, min_periods=period, adjust=False).mean()
    rs = ag / al.replace(0.0, np.nan)
    rsi = (100.0 - 100.0 / (1.0 + rs)).fillna(50.0)
    confirm = _cross_up(rsi, pd.Series(thr_cross, index=df.index)).to_numpy(dtype=bool)
    sig = _bullish_divergence_signal(
        df["Close"].to_numpy(dtype=float),
        rsi.to_numpy(dtype=float), confirm, div_window, min_gap,
    )
    return pd.Series(sig, index=df.index)


def sig_div_macd(df, fast=12, slow=26, signal=9, div_window=14, min_gap=2):
    """MACD 하락(불리시) 다이버전스: 가격 신저가 + MACD선 상위 저점 후 골든크로스"""
    ef = df["Close"].ewm(span=fast, adjust=False).mean()
    es = df["Close"].ewm(span=slow, adjust=False).mean()
    macd_line = ef - es
    sig_line = macd_line.ewm(span=signal, adjust=False).mean()
    confirm = _cross_up(macd_line, sig_line).to_numpy(dtype=bool)
    sig = _bullish_divergence_signal(
        df["Close"].to_numpy(dtype=float),
        macd_line.to_numpy(dtype=float), confirm, div_window, min_gap,
    )
    return pd.Series(sig, index=df.index)


def sig_div_stoch(df, k_period=5, d_period=3, div_window=14, min_gap=2):
    """스토캐스틱 하락(불리시) 다이버전스: 가격 신저가 + %K 상위 저점 후 %K/%D 상향교차"""
    ll = df["Low"].rolling(k_period).min()
    hh = df["High"].rolling(k_period).max()
    k = ((df["Close"] - ll) / (hh - ll) * 100.0).replace([np.inf, -np.inf], np.nan)
    k = k.rolling(3, min_periods=1).mean()
    d = k.rolling(d_period, min_periods=1).mean()
    confirm = _cross_up(k, d).to_numpy(dtype=bool)
    sig = _bullish_divergence_signal(
        df["Close"].to_numpy(dtype=float),
        k.fillna(0.0).to_numpy(dtype=float), confirm, div_window, min_gap,
    )
    return pd.Series(sig, index=df.index)


def sig_div_obv(df, window=20, div_window=14, min_gap=2):
    """OBV 하락(불리시) 다이버전스: 가격 신저가 + OBV 상위 저점 후 OBV SMA 상향교차"""
    direction = np.sign(df["Close"].diff()).fillna(0.0)
    obv = (direction * df["Volume"]).cumsum()
    ma = obv.rolling(window, min_periods=window).mean()
    confirm = _cross_up(obv, ma).to_numpy(dtype=bool)
    sig = _bullish_divergence_signal(
        df["Close"].to_numpy(dtype=float),
        obv.to_numpy(dtype=float), confirm, div_window, min_gap,
    )
    return pd.Series(sig, index=df.index)


def _triple_bottom_div_signal(price, ind, confirm, div_window=30, min_gap=3):
    """가격 하락/횡보(3 연속 신저가 or 동일) + 지표 3 연속 상위 저점 = 트리플 다이버전스.

    lookahead 없는 forward 순회:
      1. 가격 국소 저점 3개(연속)를 찾음
      2. 가격 저점 3개: P1 >= P2 >= P3 (하락 또는 횡보)
      3. 지표 저점 3개: I1 < I2 < I3 (지표는 계속 상위 저점 = 하락다이버전스 강화)
      4. 셋째 저점 이후 확정(confirm) 봉 → 매수
      5. 확정 전 가격이 셋째 저점 아래로 내려가면 취소
    """
    n = len(price)
    troughs = _price_troughs(price)
    sig = np.zeros(n, dtype=bool)
    for a in range(len(troughs) - 2):
        (i1, p1), (i2, p2), (i3, p3) = troughs[a], troughs[a + 1], troughs[a + 2]
        if i2 - i1 < min_gap or i3 - i2 < min_gap:
            continue
        if i3 - i1 > div_window:
            continue
        price_desc = p1 >= p2 - 1e-9 and p2 >= p3 - 1e-9   # 하락/횡보
        ind_asc = ind[i1] < ind[i2] < ind[i3]               # 지표 상위 저점 3연속
        if price_desc and ind_asc:
            for c in range(i3 + 1, n):
                if confirm[c]:
                    sig[c] = True
                    break
                if price[c] < p3:
                    break
    return sig


def sig_div_stoch3(df, k_period=5, d_period=3, div_window=30, min_gap=3):
    """스토캐스틱 트리플(3바닥) 하락 다이버전스:
    가격 3 연속 신저가/횡보 + %K 3 연속 상위 저점 후 %K/%D 상향교차"""
    ll = df["Low"].rolling(k_period).min()
    hh = df["High"].rolling(k_period).max()
    k = ((df["Close"] - ll) / (hh - ll) * 100.0).replace([np.inf, -np.inf], np.nan)
    k = k.rolling(3, min_periods=1).mean()
    d = k.rolling(d_period, min_periods=1).mean()
    confirm = _cross_up(k, d).to_numpy(dtype=bool)
    sig = _triple_bottom_div_signal(
        df["Close"].to_numpy(dtype=float),
        k.fillna(0.0).to_numpy(dtype=float), confirm, div_window, min_gap,
    )
    return pd.Series(sig, index=df.index)


# ── 5. 복합 시스템 ──────────────────────────────────────────────────────────


def sig_elder_triple(df, long_frame=250, mid_frame=22, pull=3):
    """엘더 삼중스크린: 장·중기 우상향 + 단기 풀백 저점"""
    long_ok = df["Close"] > df["Close"].shift(long_frame)
    mid_ok = df["Close"] > df["Close"].shift(mid_frame)
    pullback = df["Close"] == df["Close"].rolling(pull, min_periods=pull).min()
    return long_ok & mid_ok & pullback


# ── 레지스트리 ───────────────────────────────────────────────────────────────


def get_signal_fn(name: str):
    """지표 이름 → 시그널 함수"""
    return _REGISTRY[name]["fn"]


def param_grid(name: str) -> list[dict]:
    """지표 이름 → 파라미터 그리드"""
    return _REGISTRY[name]["grid"]


def param_names(name: str) -> list[str]:
    return _REGISTRY[name]["names"]


def label(name: str) -> str:
    return _REGISTRY[name]["label"]


_REGISTRY: dict[str, dict] = {
    "sma_gc": {
        "label": "SMA 골든크로스",
        "fn": sig_sma_gc,
        "names": ["short", "long"],
        "grid": [
            {"short": s, "long": l}
            for s in (3, 5, 10, 20, 50)
            for l in (20, 50, 100, 200, 250)
            if s < l
        ],
    },
    "ema_cross": {
        "label": "EMA 가격돌파",
        "fn": sig_ema_cross,
        "names": ["span"],
        "grid": [{"span": s} for s in (5, 10, 20, 30, 50, 100, 200)],
    },
    "dema_turn": {
        "label": "DEMA 변곡",
        "fn": sig_dema_turn,
        "names": ["span"],
        "grid": [{"span": s} for s in (5, 10, 20, 30, 50)],
    },
    "hma_turn": {
        "label": "Hull MA 변곡",
        "fn": sig_hma_turn,
        "names": ["n"],
        "grid": [{"n": s} for s in (9, 15, 21, 34, 55)],
    },
    "macd": {
        "label": "MACD",
        "fn": sig_macd,
        "names": ["fast", "slow", "signal", "require_zero"],
        "grid": [],
    },
    "adx": {
        "label": "ADX/DMI",
        "fn": sig_adx,
        "names": ["length", "threshold"],
        "grid": [
            {"length": ln, "threshold": th}
            for ln in (10, 14, 20)
            for th in (15.0, 20.0, 25.0, 30.0)
        ],
    },
    "ichimoku": {
        "label": "일목균형표",
        "fn": sig_ichimoku,
        "names": ["conversion", "base", "span"],
        "grid": [
            {"conversion": 9, "base": 26, "span": 52},
            {"conversion": 9, "base": 20, "span": 40},
            {"conversion": 5, "base": 12, "span": 26},
        ],
    },
    "aroon": {
        "label": "아룬 오실레이터",
        "fn": sig_aroon,
        "names": ["n"],
        "grid": [{"n": s} for s in (14, 18, 25, 30)],
    },
    "supertrend": {
        "label": "슈퍼트렌드",
        "fn": sig_supertrend,
        "names": ["atr_period", "multiplier"],
        "grid": [
            {"atr_period": ap, "multiplier": m}
            for ap in (7, 10, 14)
            for m in (2.0, 3.0, 4.0)
        ],
    },
    "parabolic_sar": {
        "label": "파라볼릭 SAR",
        "fn": sig_parabolic_sar,
        "names": ["af_step", "af_max"],
        "grid": [
            {"af_step": s, "af_max": m}
            for s in (0.01, 0.02, 0.03)
            for m in (0.15, 0.2, 0.3)
        ],
    },
    "rsi": {
        "label": "RSI",
        "fn": sig_rsi,
        "names": ["period", "threshold"],
        "grid": [
            {"period": p, "threshold": t}
            for p in (2, 5, 9, 14, 21)
            for t in (20.0, 25.0, 30.0, 35.0, 50.0)
        ],
    },
    "stoch": {
        "label": "스토캐스틱",
        "fn": sig_stoch,
        "names": ["k_period", "d_period", "oversold"],
        "grid": [
            {"k_period": k, "d_period": d, "oversold": o}
            for k in (5, 9, 14)
            for d in (3, 5)
            for o in (20, 30, 40)
        ],
    },
    "stoch_double_bottom": {
        "label": "스토캐스틱 K 쌍바닥",
        "fn": sig_stoch_double_bottom,
        "names": ["k_period", "d_period", "threshold"],
        "grid": [
            {"k_period": k, "d_period": d, "threshold": th}
            for k in (5, 9, 14)
            for d in (3, 5)
            for th in (20.0, 30.0, 40.0)
        ],
    },
    "stoch_db_weekly_k": {
        "label": "스토캐스틱 K 쌍바닥 + 주봉 K 우상향",
        "fn": sig_stoch_db_weekly_k,
        "names": ["k_period", "d_period", "threshold", "wk_period", "wd_period"],
        "grid": [
            {"k_period": 5, "d_period": 3, "threshold": th, "wk_period": 10, "wd_period": 6}
            for th in (20.0, 30.0, 40.0)
        ],
    },
    "cmo": {
        "label": "CMO",
        "fn": sig_cmo,
        "names": ["period", "signal"],
        "grid": [
            {"period": p, "signal": s}
            for p in (5, 9, 14, 20)
            for s in (3, 5, 10)
        ],
    },
    "williams_r": {
        "label": "윌리엄스 %R",
        "fn": sig_williams_r,
        "names": ["period", "threshold"],
        "grid": [
            {"period": p, "threshold": t}
            for p in (9, 14, 20)
            for t in (70, 80, 90)
        ],
    },
    "cci": {
        "label": "CCI",
        "fn": sig_cci,
        "names": ["period", "threshold"],
        "grid": [
            {"period": p, "threshold": t}
            for p in (10, 14, 20, 30)
            for t in (80, 100, 150, 200)
        ],
    },
    "ao": {
        "label": "Awesome Oscillator",
        "fn": sig_ao,
        "names": ["fast", "slow"],
        "grid": [
            {"fast": f, "slow": s}
            for f in (5, 10, 15)
            for s in (34, 20, 40)
            if f < s
        ],
    },
    "tsi": {
        "label": "TSI",
        "fn": sig_tsi,
        "names": ["r", "s"],
        "grid": [
            {"r": r, "s": s}
            for r in (13, 25, 30)
            for s in (7, 13, 20)
        ],
    },
    "vortex": {
        "label": "보텍스",
        "fn": sig_vortex,
        "names": ["n"],
        "grid": [{"n": s} for s in (10, 14, 16, 20, 26)],
    },
    "ibs": {
        "label": "IBS",
        "fn": sig_ibs,
        "names": ["threshold", "period"],
        "grid": [
            {"threshold": t, "period": p}
            for t in (0.05, 0.1, 0.15, 0.2, 0.3)
            for p in (1, 2, 3)
        ],
    },
    "bollinger": {
        "label": "볼린저 스퀴즈",
        "fn": sig_bollinger,
        "names": ["period", "dev", "squeeze"],
        "grid": [
            {"period": 20, "dev": d, "squeeze": sq}
            for d in (2.0, 2.5, 3.0)
            for sq in (10, 20)
        ],
    },
    "donchian": {
        "label": "돈치안 돌파",
        "fn": sig_donchian,
        "names": ["n"],
        "grid": [{"n": s} for s in (10, 20, 30, 55, 100)],
    },
    "ttm_squeeze": {
        "label": "TTM Squeeze",
        "fn": sig_ttm_squeeze,
        "names": ["bb_period", "bb_dev", "kc_period", "kc_mult"],
        "grid": [
            {"bb_period": 20, "bb_dev": 2.0, "kc_period": 20, "kc_mult": m}
            for m in (1.5, 2.0, 3.0)
        ],
    },
    "cmf": {
        "label": "Chaikin Money Flow",
        "fn": sig_cmf,
        "names": ["period"],
        "grid": [{"period": s} for s in (10, 20, 30, 40, 60)],
    },
    "obv": {
        "label": "OBV",
        "fn": sig_obv,
        "names": ["window"],
        "grid": [{"window": s} for s in (10, 20, 30, 50, 100)],
    },
    "vixfix": {
        "label": "Williams VixFix",
        "fn": sig_vixfix,
        "names": ["period", "peak_ratio"],
        "grid": [
            {"period": p, "peak_ratio": r}
            for p in (10, 22, 34)
            for r in (0.8, 0.9, 0.99)
        ],
    },
    "elder_triple": {
        "label": "엘더 삼중스크린",
        "fn": sig_elder_triple,
        "names": ["long_frame", "mid_frame", "pull"],
        "grid": [
            {"long_frame": lf, "mid_frame": 22, "pull": 3}
            for lf in (120, 250, 500)
        ],
    },
    "div_rsi": {
        "label": "RSI 다이버전스",
        "fn": sig_div_rsi,
        "names": ["period", "div_window", "min_gap", "thr_cross"],
        "grid": [
            {"period": p, "div_window": w, "min_gap": mg, "thr_cross": tc}
            for p in (9, 14, 21)
            for w in (10, 14, 20, 30)
            for mg in (2, 3)
            for tc in (30.0, 50.0)
        ],
    },
    "div_macd": {
        "label": "MACD 다이버전스",
        "fn": sig_div_macd,
        "names": ["fast", "slow", "signal", "div_window", "min_gap"],
        "grid": [
            {"fast": f, "slow": s, "signal": sg, "div_window": w, "min_gap": mg}
            for f, s in ((8, 17), (12, 26), (10, 30))
            for sg in (9,)
            for w in (10, 14, 20, 30)
            for mg in (2, 3)
        ],
    },
    "div_stoch": {
        "label": "스토캐스틱 다이버전스",
        "fn": sig_div_stoch,
        "names": ["k_period", "d_period", "div_window", "min_gap"],
        "grid": [
            {"k_period": k, "d_period": d, "div_window": w, "min_gap": mg}
            for k in (5, 9, 14)
            for d in (3, 5)
            for w in (10, 14, 20, 30)
            for mg in (2, 3)
        ],
    },
    "div_stoch3": {
        "label": "스토캐스틱 3바닥 다이버전스",
        "fn": sig_div_stoch3,
        "names": ["k_period", "d_period", "div_window", "min_gap"],
        "grid": [
            {"k_period": k, "d_period": d, "div_window": w, "min_gap": mg}
            for k in (5, 9, 14)
            for d in (3, 5)
            for w in (20, 30, 45, 60)
            for mg in (3, 5)
        ],
    },
    "div_obv": {
        "label": "OBV 다이버전스",
        "fn": sig_div_obv,
        "names": ["window", "div_window", "min_gap"],
        "grid": [
            {"window": s, "div_window": w, "min_gap": mg}
            for s in (10, 20, 30)
            for w in (10, 14, 20, 30)
            for mg in (2, 3)
        ],
    },
}


# MACD 그리드는 별도 (require_zero 조합)
_MACD_GRID = [
    {"fast": f, "slow": s, "signal": sig, "require_zero": z}
    for f, s in ((8, 17), (12, 26), (10, 30), (5, 35))
    for sig in (5, 9)
    for z in (False, True)
]
_REGISTRY["macd"]["grid"] = _MACD_GRID
