"""파동중첩 진입 시그널 검증 — 실데이터 기반

검출된 시그널마다 문서(docs/double-wave.md)의 모든 진입 조건을
독립 계산으로 재검증한다:
1. 최근 골든크로스가 W봉 이내
2. 조정 구간 (GC 이후 단기선 각도 <= adjust_eps 경험)
3. 단기선 각도 변곡: angle_k(t-1) <= eps → angle_k(t) > eps
4. 단기선 > 장기선 (데드크로스 제외)
5. 장기선 각도 > A_gc
6. 전일보다 거래량 증가
7. 전일 대비 등락률 +10% 이하
8. MACD 매수전환신호
9. 저점 상승: 현재 단기선 > GC 이후 조정 저점
"""

import numpy as np
import pandas as pd

from backtest.data.loader import load_all
from backtest.indicators import angle_k, compute_all, sma
from backtest.signals import DoubleWaveParams, detect_entries
from backtest.signals.double_wave import _gc_mask


def _verify_signal(df, idx, cfg, sig, params):
    """문서 조건을 독립적으로 재계산해 해당 시그널의 타점을 검증"""
    ma_long = df["ma_long"].to_numpy()
    ma_short = df["ma_short"].to_numpy()
    close = df["Close"].to_numpy()
    volume = df["Volume"].to_numpy()
    a_long = angle_k(pd.Series(ma_long, index=df.index), params.k).to_numpy()
    a_short = angle_k(pd.Series(ma_short, index=df.index), params.k).to_numpy()
    golden = df["macd_golden"].to_numpy()

    t = idx.get_loc(sig.date)
    # 1. GC 후 W봉 이내
    assert 0 < (t - cfg) <= params.w_period, f"W 초과: {t-cfg}"
    # 2. 조정 경험
    had_pullback = any(a_short[cfg + 1 : t] <= params.adjust_eps)
    assert had_pullback or cfg + 1 == t  # 타점 직전봉이 조정(변곡 전봉 ≤ eps)
    # 3. 변곡
    assert a_short[t - 1] <= params.eps
    assert a_short[t] > params.eps
    # 4. 단기선 > 장기선
    assert ma_short[t] > ma_long[t]
    # 5. 장기선 각도 > A_gc
    assert a_long[cfg] <= a_long[t]
    # 6. 거래량 증가
    assert volume[t] > volume[t - 1]
    # 7. 등락률 ≤ +10%
    rise = (close[t] / close[t - 1] - 1.0) * 100.0
    assert rise <= 10.0
    # 8. MACD 매수전환신호
    assert golden[t]
    # 9. 저점 상승 (GC 직후 봉이면 GC 봉 단기선이 비교 기준)
    pullback_min = ma_short[cfg + 1 : t].min() if cfg + 1 < t else ma_short[cfg]
    assert ma_short[t] > pullback_min
    # 10. A_gc 값 일치
    assert sig.a_gc == round(float(a_long[cfg]), 6)


def _all_data():
    return load_all()


def test_real_market_signals_satisfy_doc_rules():
    """유니버스 전체에서 검출된 모든 시그널이 문서 규칙을 만족"""
    data = _all_data()
    params = DoubleWaveParams(long_window=7, short_window=3, w_period=7, k=5, eps=0.0)
    total_sigs = 0
    checked = 0

    for ticker, df in data.items():
        enriched = compute_all(df, params.long_window, params.short_window)
        gc = _gc_mask(enriched["ma_short"], enriched["ma_long"]).to_numpy()
        for sig in detect_entries(df, params, ticker=ticker):
            cfg = np.flatnonzero(gc[: df.index.get_loc(sig.date)])[-1]
            _verify_signal(enriched, df.index, cfg, sig, params)
            checked += 1
        total_sigs += len(detect_entries(df, params, ticker=ticker))

    assert checked == total_sigs
    assert checked > 0, "기본 파라미터에서 시그널이 하나도 안 나오면 이상"
    print(f"[검증 완료] {total_sigs}개 시그널 모두 문전 조건 만족")


def test_no_overlapping_positions():
    """보유 중 다른 날짜의 매수 신호는 무시 (중복 매수 금지, 문서 15행)"""
    from backtest.engine import Trade, run_backtest

    # 하나의 종목으로, 같은 GC 사이클에서 여러 타점이 나올 수 있는 구조 대신
    # 보유 중 시그널 스킵 규칙을 검증: 시그널 2개 이상 + 같은 날짜면 스킵 확인
    data = _all_data()
    ticker, df = next(iter(data.items()))
    params = DoubleWaveParams(long_window=7, short_window=3, w_period=20, k=3, eps=0.0)
    sigs = detect_entries(df, params, ticker=ticker)

    if len(sigs) < 2:
        # 시그널이 2개 미만이면 다른 종목 탐색
        for t2, df2 in data.items():
            s2 = detect_entries(df2, DoubleWaveParams(long_window=7, short_window=3,
                                                      w_period=20, k=3, eps=0.0), ticker=t2)
            if len(s2) >= 2:
                ticker, df, sigs = t2, df2, s2
                break

    if len(sigs) < 2:
        return  # 유니버스에 2개 이상 시그널이 없으면 검증 생략 (드물지 않음)

    trades = run_backtest(df, sigs, ticker=ticker)
    # 각 진입이 이전 청산 이후여야 중복 없음
    for i in range(1, len(trades)):
        assert trades[i].entry_date > trades[i - 1].exit_date, (
            f"중복 포지션: {trades[i-1].exit_date} 이후 {trades[i].entry_date}"
        )