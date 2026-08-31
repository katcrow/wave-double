"""백테스트 엔진 테스트 — 목표/손절 도달 판단, 중복 포지션 방지, 비용

ATR 고정 구성: atr_window=1, TR=2 를 유지하도록 봉 설계
- 봉0: (100,100,100,100)  베이스
- 봉1: (100,101,99,100)   시그널 봉 → ATR=2, entry=100 → n=5이면 TP=110, SL=90
- 이후 봉들에서 TP/SL 도달 테스트
"""

import pandas as pd
import pytest

from backtest.data.loader import load_all
from backtest.engine import EXIT_END, EXIT_SL, EXIT_TP, TradeParams, run_backtest
from backtest.signals import DoubleWaveParams, EntrySignal, detect_entries


def _df_from(rows):
    df = pd.DataFrame(rows, columns=["Open", "High", "Low", "Close", "Volume"])
    df.index = pd.date_range("2025-01-01", periods=len(df), freq="D")
    return df


def _base_params():
    return TradeParams(tp_atr=5.0, sl_atr=5.0, atr_window=1)


def _sig(df, date_idx, price=100.0, gc_idx=0):
    return EntrySignal(
        ticker="T",
        date=df.index[date_idx],
        gc_date=df.index[gc_idx],
        a_gc=0.5,
        price=price,
        short_ma=price,
        long_ma=price * 0.99,
        pullback_min=price * 0.99,
    )


def test_tp_reached():
    df = _df_from(
        [
            (100, 100, 100, 100, 10000),
            (100, 101, 99, 100, 10000),  # 시그널 봉: ATR=2 → TP=110, SL=90
            (100, 115, 99, 110, 12000),  # 고가 115 >= 110 → 익절
        ]
    )
    trades = run_backtest(df, [_sig(df, 1)], _base_params(), ticker="T")
    assert len(trades) == 1
    assert trades[0].exit_reason == EXIT_TP
    assert trades[0].exit_price == pytest.approx(110.0)
    assert trades[0].holding_bars == 1


def test_sl_reached():
    df = _df_from(
        [
            (100, 100, 100, 100, 10000),
            (100, 101, 99, 100, 10000),
            (100, 101, 85, 90, 15000),  # 저가 85 <= 90 → 손절
        ]
    )
    trades = run_backtest(df, [_sig(df, 1)], _base_params(), ticker="T")
    assert len(trades) == 1
    assert trades[0].exit_reason == EXIT_SL
    assert trades[0].exit_price == pytest.approx(90.0)


def test_same_bar_tp_and_sl_takes_sl():
    df = _df_from(
        [
            (100, 100, 100, 100, 10000),
            (100, 101, 99, 100, 10000),
            (100, 115, 85, 100, 20000),  # TP(110)·SL(90) 동시 도달 → 손절 우선
        ]
    )
    trades = run_backtest(df, [_sig(df, 1)], _base_params(), ticker="T")
    assert trades[0].exit_reason == EXIT_SL
    assert trades[0].exit_price == pytest.approx(90.0)


def test_no_tp_sl_exit_at_end():
    df = _df_from(
        [
            (100, 100, 100, 100, 10000),
            (100, 101, 99, 100, 10000),
            (100, 104, 96, 103, 10000),
            (100, 104, 97, 103.5, 10000),
        ]
    )
    p = TradeParams(tp_atr=10.0, sl_atr=10.0, atr_window=1)  # TP=120, SL=80
    trades = run_backtest(df, [_sig(df, 1)], p, ticker="T")
    assert len(trades) == 1
    assert trades[0].exit_reason == EXIT_END
    assert trades[0].exit_price == pytest.approx(103.5)
    assert trades[0].holding_bars == 2


def test_holding_signal_skipped_no_duplicate():
    """보유 중 다른 날짜 시그널 → 무시 (문서 15행), 청산 후엔 재진입 가능"""
    df = _df_from(
        [
            (100, 100, 100, 100, 10000),
            (100, 101, 99, 100, 10000),  # A 진입 (TP110/SL90)
            (100, 104, 99, 103, 12000),  # B 시그널: 보유 중 → 무시
            (100, 115, 99, 110, 12000),  # A TP 청산
            (138, 140, 137, 138, 15000),  # C 시그널: 청산 후 → 진입
            (138, 142, 136, 141, 10000),  # C 종료 처리
        ]
    )
    p = _base_params()
    sigs = [_sig(df, 1), _sig(df, 2, price=103.0), _sig(df, 4, price=138.0)]
    trades = run_backtest(df, sigs, p, ticker="T")
    assert len(trades) == 2  # B는 무시
    assert trades[0].entry_date == df.index[1]
    assert trades[0].exit_reason == EXIT_TP
    assert trades[1].entry_date == df.index[4]


def test_cost_applied():
    df = _df_from(
        [
            (100, 100, 100, 100, 10000),
            (100, 101, 99, 100, 10000),
            (100, 115, 99, 110, 12000),  # TP 도달
        ]
    )
    p = TradeParams(tp_atr=5.0, sl_atr=5.0, atr_window=1, cost_rate=0.0005)
    trades = run_backtest(df, [_sig(df, 1)], p, ticker="T")
    gross = (110.0 / 100.0 - 1.0) * 100.0  # 10%
    assert trades[0].return_pct == pytest.approx(gross - 0.1)


def test_real_data_full_run():
    """실데이터 전체 유니버스 스모크 테스트"""
    data = load_all()
    params = DoubleWaveParams()
    tp = TradeParams()
    all_t = []
    for t, df in data.items():
        sigs = detect_entries(df, params, ticker=t)
        all_t.extend(run_backtest(df, sigs, tp, ticker=t))
    assert len(all_t) > 0
    for tr in all_t[:20]:
        assert tr.entry_price > 0 and tr.exit_price > 0
    reasons = {tr.exit_reason for tr in all_t}
    assert reasons <= {EXIT_TP, EXIT_SL, EXIT_END}