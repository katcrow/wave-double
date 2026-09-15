"""탐색용: 거래량 돌파 양봉 + 음봉 풀백(1~3회) + 풀백 고가 돌파 전략.

진입 조건 (Neo 요청, 2026-09-15):
1. 5거래일 이내에 5이평 거래량을 돌파하는 7% 이상 양봉 발생 (돌파봉)
2. 그 이후 음봉이 1회, 2회 또는 3회 연속 발생 (풀백)
3. 풀백 음봉들 중 가장 높은 고가를 오늘 종가가 돌파 + 거래량은 전일 대비 증가 → 진입

청산은 ATR 기반 TP/SL (engine.run_backtest 재사용).
탐색적 실행이므로 결과는 backtest/results/scratch/ 아래에 저장한다 (results_dir 격리 규약).
"""

from __future__ import annotations

import argparse
from dataclasses import asdict, dataclass

import numpy as np
import pandas as pd

from ..data.loader import load_all
from ..engine import Trade, TradeParams, run_backtest
from ..metrics import summarize
from ..results_dir import scratch_root
from ._signals import SimpleSignal

RESULTS_DIR = scratch_root()


@dataclass
class VolBreakoutPullbackParams:
    min_gain_pct: float = 7.0  # 돌파봉 최소 양봉 상승률 (%), (Close-Open)/Open
    vol_sma_window: int = 5  # 거래량 이평 기간
    max_pullback: int = 3  # 허용 풀백 음봉 최대 개수
    tp_atr: float = 3.0
    sl_atr: float = 2.0
    atr_window: int = 14
    cost_rate: float = 0.0005
    max_holding_bars: int | None = None

    def as_dict(self) -> dict:
        return asdict(self)


DEFAULT_PARAMS = VolBreakoutPullbackParams()


def _breakout_pullback_mask(
    open_: np.ndarray,
    high: np.ndarray,
    close: np.ndarray,
    volume: np.ndarray,
    vol_sma: np.ndarray,
    min_gain_pct: float,
    max_pullback: int,
) -> np.ndarray:
    """돌파봉→음봉 풀백(1~max_pullback)→풀백고가 돌파 패턴을 forward 순회로 검출."""
    n = len(close)
    sig = np.zeros(n, dtype=bool)
    t = 0
    while t < n:
        if np.isnan(vol_sma[t]) or open_[t] <= 0:
            t += 1
            continue
        candle_gain = (close[t] - open_[t]) / open_[t] * 100.0
        is_breakout = candle_gain >= min_gain_pct and volume[t] > vol_sma[t]
        if not is_breakout:
            t += 1
            continue

        # 돌파봉 확정 → 음봉 풀백(1~max_pullback) 탐색
        j = t + 1
        count = 0
        pullback_high = -np.inf
        while j < n:
            if count < max_pullback and close[j] < open_[j]:
                count += 1
                pullback_high = max(pullback_high, high[j])
                j += 1
                continue
            # 풀백 종료(비음봉 또는 상한 도달) → 이 봉이 진입 후보
            if count >= 1 and close[j] > pullback_high and volume[j] > volume[j - 1]:
                sig[j] = True
            break
        t = j + 1

    return sig


def detect_signals(
    df: pd.DataFrame,
    ticker: str = "",
    params: VolBreakoutPullbackParams = DEFAULT_PARAMS,
) -> list[SimpleSignal]:
    if len(df) < params.vol_sma_window + params.max_pullback + 2:
        return []

    open_ = df["Open"].to_numpy(dtype=float)
    high = df["High"].to_numpy(dtype=float)
    close = df["Close"].to_numpy(dtype=float)
    volume = df["Volume"].to_numpy(dtype=float)
    vol_sma = (
        df["Volume"]
        .rolling(params.vol_sma_window, min_periods=params.vol_sma_window)
        .mean()
        .shift(1)
        .to_numpy(dtype=float)
    )

    mask = _breakout_pullback_mask(
        open_, high, close, volume, vol_sma, params.min_gain_pct, params.max_pullback
    )

    return [
        SimpleSignal(ticker=ticker, date=df.index[i], price=float(close[i]))
        for i in np.flatnonzero(mask)
    ]


@dataclass
class PartialExitParams:
    """수익우선 분할청산: 진입 다음 거래일 하루만 보유.

    - 당일 고가가 tp2(4%) 도달 → 절반은 tp1(2%)가, 나머지 절반은 tp2가로 청산
    - 당일 고가가 tp1(2%)만 도달 → 절반은 tp1가, 나머지 절반은 당일 종가로 청산
    - 둘 다 미도달 → stop_loss_pct 지정 시 당일 저가가 손절가 이하면 전량 손절가 청산, 아니면 전량 종가청산
    - 익절 우선: 같은 날 고가가 tp1/tp2에 닿았으면(저가의 손절선 접촉 여부와 무관) 익절을 적용한다
    """

    tp1_pct: float = 2.0
    tp2_pct: float = 4.0
    stop_loss_pct: float | None = None  # None이면 손절 없음. 지정 시 저가 도달 우선 청산(보수적)
    cost_rate: float = 0.0005

    def as_dict(self) -> dict:
        return asdict(self)


DEFAULT_PARTIAL_EXIT_PARAMS = PartialExitParams()


def run_partial_exit_backtest(
    df: pd.DataFrame,
    signals: list[SimpleSignal],
    params: PartialExitParams = DEFAULT_PARTIAL_EXIT_PARAMS,
    ticker: str = "",
) -> list[Trade]:
    if not signals or len(df) < 2:
        return []

    high = df["High"].to_numpy(dtype=float)
    low = df["Low"].to_numpy(dtype=float)
    close = df["Close"].to_numpy(dtype=float)
    date_to_pos = {ts: i for i, ts in enumerate(df.index)}

    trades: list[Trade] = []
    last_exit_idx = -1
    for sig in signals:
        if sig.ticker and ticker and sig.ticker != ticker:
            continue
        if sig.date not in date_to_pos:
            continue
        e = date_to_pos[sig.date]
        if e <= last_exit_idx or e >= len(df) - 1:
            continue

        entry_price = sig.price
        t = e + 1
        tp1_px = entry_price * (1.0 + params.tp1_pct / 100.0)
        tp2_px = entry_price * (1.0 + params.tp2_pct / 100.0)

        sl_px = (
            entry_price * (1.0 - params.stop_loss_pct / 100.0)
            if params.stop_loss_pct is not None
            else None
        )

        if high[t] >= tp2_px:
            leg1_px, leg2_px, reason = tp1_px, tp2_px, "tp1_tp2"
        elif high[t] >= tp1_px:
            leg1_px, leg2_px, reason = tp1_px, close[t], "tp1_close"
        elif sl_px is not None and low[t] <= sl_px:
            leg1_px, leg2_px, reason = sl_px, sl_px, "sl"
        else:
            leg1_px, leg2_px, reason = close[t], close[t], "close"

        leg1_ret = (leg1_px / entry_price - 1.0) * 100.0 - params.cost_rate * 200.0
        leg2_ret = (leg2_px / entry_price - 1.0) * 100.0 - params.cost_rate * 200.0
        blended_ret = (leg1_ret + leg2_ret) / 2.0

        trades.append(
            Trade(
                ticker=sig.ticker or ticker,
                entry_date=sig.date,
                exit_date=df.index[t],
                entry_price=entry_price,
                exit_price=(leg1_px + leg2_px) / 2.0,
                return_pct=round(blended_ret, 4),
                holding_bars=1,
                exit_reason=reason,
            )
        )
        last_exit_idx = t

    return trades


def run_strategy_partial_exit(
    data: dict[str, pd.DataFrame] | None = None,
    entry_params: VolBreakoutPullbackParams = DEFAULT_PARAMS,
    exit_params: PartialExitParams = DEFAULT_PARTIAL_EXIT_PARAMS,
) -> dict[str, object]:
    data = load_all() if data is None else data
    all_trades: list[Trade] = []
    signal_count = 0
    for ticker in sorted(data):
        frame = data[ticker]
        signals = detect_signals(frame, ticker=ticker, params=entry_params)
        signal_count += len(signals)
        all_trades.extend(
            run_partial_exit_backtest(frame, signals, exit_params, ticker=ticker)
        )

    all_trades.sort(key=lambda t: (t.entry_date, t.ticker, t.exit_date))
    perf = summarize(all_trades)
    return {
        "entry_params": entry_params.as_dict(),
        "exit_params": exit_params.as_dict(),
        "n_tickers": len(data),
        "n_signals": signal_count,
        "trades": all_trades,
        **perf.to_dict(),
    }


def run_strategy(
    data: dict[str, pd.DataFrame] | None = None,
    params: VolBreakoutPullbackParams = DEFAULT_PARAMS,
) -> dict[str, object]:
    data = load_all() if data is None else data
    trade_params = TradeParams(
        tp_atr=params.tp_atr,
        sl_atr=params.sl_atr,
        atr_window=params.atr_window,
        cost_rate=params.cost_rate,
        max_holding_bars=params.max_holding_bars,
    )

    all_trades = []
    signal_count = 0
    for ticker in sorted(data):
        frame = data[ticker]
        signals = detect_signals(frame, ticker=ticker, params=params)
        signal_count += len(signals)
        all_trades.extend(run_backtest(frame, signals, trade_params, ticker=ticker))

    all_trades.sort(key=lambda t: (t.entry_date, t.ticker, t.exit_date))
    perf = summarize(all_trades)
    return {
        "params": params.as_dict(),
        "n_tickers": len(data),
        "n_signals": signal_count,
        "trades": all_trades,
        **perf.to_dict(),
    }


def _format_result(result: dict[str, object]) -> str:
    return (
        f"시그널 {result['n_signals']} | 거래 {result['n_trades']} "
        f"({result['n_win']}승/{result['n_loss']}패) | "
        f"승률 {result['win_rate'] * 100:.1f}% | PF {result['profit_factor']:.2f} | "
        f"평균 {result['avg_return']:+.3f}% | 복리누적 {result['cum_return']:.2f}% | "
        f"MDD {result['max_drawdown']:.2f}% | 청산사유 {result['exit_counts']}"
    )


def parse_args() -> argparse.Namespace:
    ap = argparse.ArgumentParser(description="거래량돌파+음봉풀백 전략 백테스트 (탐색용)")
    ap.add_argument("--min-gain-pct", type=float, default=DEFAULT_PARAMS.min_gain_pct)
    ap.add_argument("--vol-sma-window", type=int, default=DEFAULT_PARAMS.vol_sma_window)
    ap.add_argument("--max-pullback", type=int, default=DEFAULT_PARAMS.max_pullback)
    ap.add_argument("--tp-atr", type=float, default=DEFAULT_PARAMS.tp_atr)
    ap.add_argument("--sl-atr", type=float, default=DEFAULT_PARAMS.sl_atr)
    ap.add_argument("--max-holding-bars", type=int, default=DEFAULT_PARAMS.max_holding_bars)
    return ap.parse_args()


def main() -> None:
    args = parse_args()
    params = VolBreakoutPullbackParams(
        min_gain_pct=args.min_gain_pct,
        vol_sma_window=args.vol_sma_window,
        max_pullback=args.max_pullback,
        tp_atr=args.tp_atr,
        sl_atr=args.sl_atr,
        max_holding_bars=args.max_holding_bars,
    )
    print(f"파라미터: {params.as_dict()}")
    result = run_strategy(params=params)
    print(_format_result(result))

    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    trades_df = pd.DataFrame([t.to_dict() for t in result["trades"]])
    if not trades_df.empty:
        trades_df.to_csv(RESULTS_DIR / "vol_breakout_pullback_trades.csv", index=False)
    summary_row = {k: v for k, v in result.items() if k != "trades"}
    pd.DataFrame([summary_row]).to_csv(
        RESULTS_DIR / "vol_breakout_pullback_summary.csv", index=False
    )
    print(f"\n결과 저장: {RESULTS_DIR}")


if __name__ == "__main__":
    main()
