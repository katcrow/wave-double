"""파동중첩 매수 진입 시그널 (double-wave.md)

전략 흐름:
1. 골든크로스 (S일선 상향돌파 L일선) — 타점이 GC로부터 W봉 이내
2. 이후 단기선 하락/횡보 (조정) 겪음 — 각도로 판단, 기간 제한 없음
3. 타점 봉: 아래 모든 조건 충족 시 매수
   - 단기선 각도 변곡: angle_k(t-1) <= eps → angle_k(t) > eps
   - 단기선 > 장기선 (데드크로스 탈락)
   - 장기선 각도 > A_gc (골든크로스 시점 장기선 각도)
   - 거래량 전일 대비 증가
   - 전일 대비 등락률 +10% 이하
   - MACD 매수전환신호 (MACD 시그널선 상향돌파)
   - 현재 단기선 > 골든크로스 이후 조정 저점 (저점 상승)
   - 저점 상승 폭 >= pullback_rise_pct (매수 시점 강화)
"""

from __future__ import annotations

from dataclasses import asdict, dataclass

import numpy as np
import pandas as pd

from ..indicators import angle_k, compute_all


@dataclass
class DoubleWaveParams:
    """파동중첩 전략 파라미터 (백테스트 그리드 변수)"""

    long_window: int = 7  # L 장기선 (SMA)
    short_window: int = 3  # S 단기선 (SMA)
    w_period: int = 7  # W 골든크로스 근접도 (봉 이내)
    k: int = 5  # 각도 측정 구간
    eps: float = 0.0  # 양판별 임계 (도)
    adjust_eps: float = 0.0  # 조정 판단 임계 (각도 <= 이 값이면 조정 경험)
    max_rise_pct: float = 10.0  # 전일 대비 등락률 상한 (%)
    pullback_rise_pct: float = 0.0  # 저점 상승 폭 최소 (%) — 타점 단기선이 조정 저점 대비
    macd_fast: int = 12
    macd_slow: int = 26
    macd_signal: int = 9
    stoch_k: int = 5  # 스토캐스틱 %K 주기
    stoch_d: int = 3  # 스토캐스틱 %D 주기
    stoch_smooth: int = 3  # 스토캐스틱 %K 평활 주기
    obv_window: int = 20
    rsi_window: int = 14
    cci_window: int = 20
    filter_mode: str = "macd"  # macd | stoch | obv | obv_bull | rsi | rsi_cross | cci | cci_cross

    def as_dict(self) -> dict:
        return asdict(self)


@dataclass
class EntrySignal:
    """타점 1개 = 진입 시그널"""

    ticker: str
    date: pd.Timestamp  # 타점 봉 (장 마감가로 매수 가정)
    gc_date: pd.Timestamp  # 기준이 된 최근 골든크로스 봉
    a_gc: float  # 골든크로스 시점 장기선 각도
    price: float  # 진입가 = 타점 봉 종가
    short_ma: float
    long_ma: float
    pullback_min: float  # GC 이후 조정 저점 (단기선 최저)
    take_profit_pct: float | None = None  # 고정 익절 (미지정 시 ATR 기반)
    take_profit_price: float | None = None  # 고정 익절가 (지정 시 우선)
    stop_price: float | None = None  # 고정 손절가 (미지정 시 ATR 기반)


def _gc_mask(ma_short: pd.Series, ma_long: pd.Series) -> pd.Series:
    """골든크로스: 단기선이 장기선을 상향 돌파한 봉"""
    return (ma_short > ma_long) & (ma_short.shift(1) <= ma_long.shift(1))


def detect_entries(
    df: pd.DataFrame,
    params: DoubleWaveParams,
    ticker: str = "",
) -> list[EntrySignal]:
    """한 종목에서 파동중첩 진입 시그널을 모두 검출 (벡터화).

    각 골든크로스 사이클(GC → 다음 GC 직전)에서 첫 번째 타점만 사용.
    df: index=DatetimeIndex, 컬럼 Open/High/Low/Close/Volume
    """
    need = (
        max(params.k, params.long_window, params.short_window,
            params.stoch_k + params.stoch_smooth + params.stoch_d,
            params.macd_slow + params.macd_signal,
            params.obv_window, params.rsi_window, params.cci_window) + 2
    )
    if len(df) < need:
        return []

    df = compute_all(
        df,
        params.long_window,
        params.short_window,
        params.macd_fast,
        params.macd_slow,
        params.macd_signal,
        params.stoch_k,
        params.stoch_d,
        params.stoch_smooth,
        params.obv_window,
        params.rsi_window,
        params.cci_window,
    )
    n = len(df)

    ma_long = df["ma_long"].to_numpy()
    ma_short = df["ma_short"].to_numpy()
    close = df["Close"].to_numpy()
    volume = df["Volume"].to_numpy()
    angle_long = angle_k(df["ma_long"], params.k).to_numpy()
    angle_short = angle_k(df["ma_short"], params.k).to_numpy()

    # ── 보조지표 필터 선택 ─────────────────────────────────────────
    if params.filter_mode == "macd":
        filter_vec = df["macd_golden"].to_numpy()
    elif params.filter_mode == "stoch":
        filter_vec = df["stoch_golden"].to_numpy()
    elif params.filter_mode == "obv":
        filter_vec = df["obv_golden"].to_numpy()
    elif params.filter_mode == "obv_bull":
        filter_vec = df["obv_bull"].to_numpy()
    elif params.filter_mode == "rsi":
        rsi_series = df["rsi"]
        rsi_arr = rsi_series.to_numpy()
        filter_vec = (rsi_arr > 50.0) & (np.concatenate([[np.nan], rsi_arr[:-1]]) <= 50.0)
    elif params.filter_mode == "rsi_bull":
        filter_vec = df["rsi"].to_numpy() > 50.0
    elif params.filter_mode == "cci":
        cci_arr = df["cci"].to_numpy()
        filter_vec = (cci_arr > 0.0) & (np.concatenate([[np.nan], cci_arr[:-1]]) <= 0.0)
    elif params.filter_mode == "cci_bull":
        filter_vec = df["cci"].to_numpy() > 0.0
    else:
        raise ValueError(f"알 수 없는 filter_mode: {params.filter_mode}")
    filter_vec = np.nan_to_num(filter_vec, nan=False).astype(bool)

    gc = _gc_mask(df["ma_short"], df["ma_long"]).to_numpy()

    arange_n = np.arange(n)
    # ── 골든크로스 사이클 매핑 ─────────────────────────────────────
    # gc_region: 어떤 GC 이후인지 (0 = 아직 GC 없음), dist: 최근 GC로부터의 봉수
    gc_cum = np.maximum.accumulate(gc * arange_n)
    in_cycle = gc_cum > 0
    dist = arange_n - gc_cum

    # GC 봉 이후만 타점 가능 (dist >= 1)
    eligible = in_cycle & (dist >= 1)
    if not eligible.any():
        return []

    # ── 각 GC의 장기선 각도 A_gc를 해당 사이클 전체로 전파 ────────
    a_gc_at = np.where(in_cycle, angle_long[gc_cum], np.nan)

    # ── 조정/저점 기준은 '현재 GC의 다음 봉 ~ t-1' 구간 (현재 봉 제외) ──
    # GC 봉과 GC 이전은 NaN → groupby cummin이 해당 사이클부터 시작
    raw_angle = np.where(in_cycle, np.where(gc, np.nan, angle_short), np.nan)
    raw_ma = np.where(in_cycle, np.where(gc, np.nan, ma_short), np.nan)
    grp = pd.DataFrame(
        {
            "g": pd.Series(np.where(in_cycle, gc_cum, -1), index=df.index),
            "a": raw_angle,
            "m": raw_ma,
        }
    )
    # 사이클 내 누적 최소 (t 포함) → shift(1)로 현재 봉 제외 ──────────
    seg_min = grp.groupby("g", sort=False)["a"].cummin().shift(1).to_numpy()
    pullback_min = grp.groupby("g", sort=False)["m"].cummin().shift(1).to_numpy()

    # ── 타점 봉 조건 (모두 벡터) ─────────────────────────────────────
    cond = np.ones(n, dtype=bool)
    cond &= eligible
    cond &= dist <= params.w_period             # GC 후 W봉 이내
    cond &= seg_min <= params.adjust_eps        # 조정 경험
    cond &= np.concatenate([[False], angle_short[:-1]]) <= params.eps  # 전봉 우하향/횡보
    cond &= angle_short > params.eps            # 당봉 우상향 전환 (변곡)
    cond &= ma_short > ma_long                  # 데드크로스 제외
    cond &= a_gc_at < angle_long                # 장기선 각도 > A_gc
    cond &= volume > np.concatenate([[np.nan], volume[:-1]])  # 거래량 증가
    rise_pct = np.concatenate([[np.nan], close[:-1]]).astype(float)
    cond &= ((close / rise_pct - 1.0) * 100.0) <= params.max_rise_pct  # 등락률 상한
    cond &= filter_vec                        # 보조지표 전환신호 (macd/stoch/obv/rsi/cci)
    cond &= ma_short > pullback_min            # 저점 상승
    # 회복 폭 최소 (pullback_min 은 이 봉 변곡 시점엔 과거 저점)
    cond &= (ma_short - pullback_min) / pullback_min * 100.0 >= params.pullback_rise_pct

    candidates = np.flatnonzero(cond & in_cycle)
    if len(candidates) == 0:
        return []

    # ── 사이클당 첫 타점만 ──────────────────────────────────────────
    seen_gc: set = set()
    signals: list[EntrySignal] = []
    idx = df.index

    for t in candidates:
        gc_idx_of_t = int(gc_cum[t])
        if gc_idx_of_t in seen_gc:
            continue
        seen_gc.add(gc_idx_of_t)

        if t > gc_idx_of_t + 1:
            pullback_min_v = float(ma_short[gc_idx_of_t + 1 : t].min())
        else:
            pullback_min_v = float(ma_short[gc_idx_of_t])
        signals.append(
            EntrySignal(
                ticker=ticker,
                date=idx[t],
                gc_date=idx[int(gc_idx_of_t)],
                a_gc=round(float(angle_long[gc_idx_of_t]), 6),
                price=float(close[t]),
                short_ma=float(ma_short[t]),
                long_ma=float(ma_long[t]),
                pullback_min=round(pullback_min_v, 6),
            )
        )

    return signals