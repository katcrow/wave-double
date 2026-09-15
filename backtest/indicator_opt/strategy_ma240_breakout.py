"""탐색용: 240이평 양봉 돌파 전략 (동적 손절: 이격도에 따라 MA선 or 고정 5%).

진입 조건 (Neo 요청, 2026-09-15):
- 오늘 종가가 240일 이동평균(SMA240)을 상향 돌파하는 양봉(종가>시가) 발생
  (전일 종가 <= 전일 SMA240 → 당일 종가 > 당일 SMA240, 당일 종가>시가)
- 60이평 우상향 필터: 오늘 SMA60 > 어제 SMA60 (아주 조금이라도 우상향)
→ 오늘 종가에 매수

청산 조건:
1. 손절 — 진입일 이격도(진입가 대비 SMA240 괴리율)로 방식이 갈린다
   - 이격도 >= 5% → 손절선 = SMA240 (매일 갱신되는 추적 손절, 종가가 SMA240 아래로 마감하면 손절)
   - 이격도 < 5%  → 손절선 = 진입가 -5% (고정)
2. 익절 — 분할: +2% 도달 시 절반 매도, +4% 도달 시 나머지 절반 매도
   - 목표/손절 모두 도달하지 않으면 계속 보유 (다음날로 이월, ATR형과 달리 1일 한정 아님)
   - 데이터 끝까지 미청산 시 마지막 종가로 잔여 물량 강제 청산
   - 같은 날 익절선과 손절선에 모두 닿으면 **익절 우선** (기존 두 전략과 동일 원칙)

탐색적 실행이므로 결과는 backtest/results/scratch/ 아래에 저장한다 (results_dir 격리 규약).
"""

from __future__ import annotations

import argparse
from dataclasses import asdict, dataclass

import numpy as np
import pandas as pd

from ..data.loader import load_all
from ..indicators import sma
from ..metrics import summarize
from ..results_dir import scratch_root
from ._signals import SimpleSignal

RESULTS_DIR = scratch_root()


@dataclass
class Ma240BreakoutParams:
    ma_window: int = 240
    gap_threshold_pct: float = 5.0  # 이격도 기준 (이 이상이면 MA선 손절, 미만이면 고정 손절)
    fixed_stop_pct: float = 5.0  # 이격도 미달 시 고정 손절 폭 (%)
    slope_ma_window: int = 60  # 우상향 필터 기준 이평 기간
    tp1_pct: float = 2.0
    tp2_pct: float = 4.0
    cost_rate: float = 0.0005

    def as_dict(self) -> dict:
        return asdict(self)


DEFAULT_PARAMS = Ma240BreakoutParams()


@dataclass
class PartialTrade:
    """분할청산 결과 1건 (두 다리 합산 평균 청산가/수익률)."""

    ticker: str
    entry_date: pd.Timestamp
    exit_date: pd.Timestamp
    entry_price: float
    exit_price: float
    return_pct: float
    holding_bars: int
    exit_reason: str
    stop_mode: str  # "ma" | "fixed"
    gap_pct_at_entry: float

    def to_dict(self) -> dict:
        return {
            "ticker": self.ticker,
            "entry_date": str(self.entry_date.date()),
            "exit_date": str(self.exit_date.date()),
            "entry_price": round(self.entry_price, 4),
            "exit_price": round(self.exit_price, 4),
            "return_pct": round(self.return_pct, 4),
            "holding_bars": self.holding_bars,
            "exit_reason": self.exit_reason,
            "stop_mode": self.stop_mode,
            "gap_pct_at_entry": round(self.gap_pct_at_entry, 4),
        }


def detect_signals(
    df: pd.DataFrame,
    ticker: str = "",
    params: Ma240BreakoutParams = DEFAULT_PARAMS,
) -> list[SimpleSignal]:
    if len(df) < params.ma_window + 2:
        return []

    ma = sma(df["Close"], params.ma_window)
    close = df["Close"]
    open_ = df["Open"]

    cross_up = (close > ma) & (close.shift(1) <= ma.shift(1))
    bullish = close > open_
    ma_slope = sma(close, params.slope_ma_window)
    slope_up = ma_slope > ma_slope.shift(1)
    cond = (cross_up & bullish & slope_up).fillna(False)

    close_np = close.to_numpy(dtype=float)
    return [
        SimpleSignal(ticker=ticker, date=df.index[i], price=float(close_np[i]))
        for i in np.flatnonzero(cond.to_numpy())
    ]


def run_ma240_backtest(
    df: pd.DataFrame,
    signals: list[SimpleSignal],
    params: Ma240BreakoutParams = DEFAULT_PARAMS,
    ticker: str = "",
) -> list[PartialTrade]:
    if not signals or len(df) < 2:
        return []

    ma = sma(df["Close"], params.ma_window).to_numpy(dtype=float)
    high = df["High"].to_numpy(dtype=float)
    low = df["Low"].to_numpy(dtype=float)
    close = df["Close"].to_numpy(dtype=float)
    date_to_pos = {ts: i for i, ts in enumerate(df.index)}

    trades: list[PartialTrade] = []
    last_exit_idx = -1

    for sig in signals:
        if sig.ticker and ticker and sig.ticker != ticker:
            continue
        if sig.date not in date_to_pos:
            continue
        e = date_to_pos[sig.date]
        if e <= last_exit_idx or e >= len(df) - 1:
            continue
        if not np.isfinite(ma[e]) or ma[e] <= 0:
            continue

        entry_price = sig.price
        gap_pct = (entry_price / ma[e] - 1.0) * 100.0
        use_ma_stop = gap_pct >= params.gap_threshold_pct
        stop_mode = "ma" if use_ma_stop else "fixed"
        fixed_stop_price = entry_price * (1.0 - params.fixed_stop_pct / 100.0)
        tp1_price = entry_price * (1.0 + params.tp1_pct / 100.0)
        tp2_price = entry_price * (1.0 + params.tp2_pct / 100.0)

        half1_sold = False
        half1_exit_price: float | None = None
        exit_idx = e
        exit_reason = ""
        remaining_exit_price: float | None = None

        for t in range(e + 1, len(df)):
            stop_price_t = ma[t] if use_ma_stop else fixed_stop_price
            if not np.isfinite(stop_price_t):
                stop_price_t = fixed_stop_price

            if not half1_sold:
                if high[t] >= tp2_price:
                    half1_exit_price = tp1_price
                    remaining_exit_price = tp2_price
                    exit_reason = "tp1_tp2"
                    exit_idx = t
                    break
                if high[t] >= tp1_price:
                    half1_sold = True
                    half1_exit_price = tp1_price
                    continue
                if low[t] <= stop_price_t:
                    half1_exit_price = stop_price_t
                    remaining_exit_price = stop_price_t
                    exit_reason = "sl"
                    exit_idx = t
                    break
            else:
                if high[t] >= tp2_price:
                    remaining_exit_price = tp2_price
                    exit_reason = "tp1_then_tp2"
                    exit_idx = t
                    break
                if low[t] <= stop_price_t:
                    remaining_exit_price = stop_price_t
                    exit_reason = "tp1_then_sl"
                    exit_idx = t
                    break
        else:
            # 루프 정상 종료(break 없음) → 데이터 끝까지 미청산, 마지막 종가로 강제청산
            exit_idx = len(df) - 1
            if half1_sold:
                remaining_exit_price = close[-1]
                exit_reason = "tp1_then_end"
            else:
                half1_exit_price = close[-1]
                remaining_exit_price = close[-1]
                exit_reason = "end"

        leg1_ret = (half1_exit_price / entry_price - 1.0) * 100.0 - params.cost_rate * 200.0
        leg2_ret = (
            remaining_exit_price / entry_price - 1.0
        ) * 100.0 - params.cost_rate * 200.0
        blended_ret = (leg1_ret + leg2_ret) / 2.0

        trades.append(
            PartialTrade(
                ticker=sig.ticker or ticker,
                entry_date=sig.date,
                exit_date=df.index[exit_idx],
                entry_price=entry_price,
                exit_price=(half1_exit_price + remaining_exit_price) / 2.0,
                return_pct=round(blended_ret, 4),
                holding_bars=exit_idx - e,
                exit_reason=exit_reason,
                stop_mode=stop_mode,
                gap_pct_at_entry=gap_pct,
            )
        )
        last_exit_idx = exit_idx

    return trades


def _summarize_partial(trades: list[PartialTrade]) -> dict[str, object]:
    """PartialTrade는 engine.Trade와 필드가 달라 metrics.summarize를 직접 못 쓰므로
    필요한 필드만 뽑아 동일 인터페이스로 감싼다."""
    from ..engine import Trade as _Trade

    wrapped = [
        _Trade(
            ticker=t.ticker,
            entry_date=t.entry_date,
            exit_date=t.exit_date,
            entry_price=t.entry_price,
            exit_price=t.exit_price,
            return_pct=t.return_pct,
            holding_bars=t.holding_bars,
            exit_reason=t.exit_reason,
        )
        for t in trades
    ]
    return summarize(wrapped).to_dict()


def run_strategy(
    data: dict[str, pd.DataFrame] | None = None,
    params: Ma240BreakoutParams = DEFAULT_PARAMS,
) -> dict[str, object]:
    data = load_all() if data is None else data
    all_trades: list[PartialTrade] = []
    signal_count = 0
    for ticker in sorted(data):
        frame = data[ticker]
        signals = detect_signals(frame, ticker=ticker, params=params)
        signal_count += len(signals)
        all_trades.extend(run_ma240_backtest(frame, signals, params, ticker=ticker))

    all_trades.sort(key=lambda t: (t.entry_date, t.ticker, t.exit_date))
    perf = _summarize_partial(all_trades)
    return {
        "params": params.as_dict(),
        "n_tickers": len(data),
        "n_signals": signal_count,
        "trades": all_trades,
        **perf,
    }


def _format_result(result: dict[str, object]) -> str:
    return (
        f"시그널 {result['n_signals']} | 거래 {result['n_trades']} "
        f"({result['n_win']}승/{result['n_loss']}패) | "
        f"승률 {result['win_rate'] * 100:.1f}% | PF {result['profit_factor']:.2f} | "
        f"평균 {result['avg_return']:+.3f}% | 단리누적 {result['total_return']:.2f}% | "
        f"복리누적 {result['cum_return']:.2f}% | MDD {result['max_drawdown']:.2f}% | "
        f"평균보유 {result['avg_holding_bars']:.1f}봉 | 청산사유 {result['exit_counts']}"
    )


def parse_args() -> argparse.Namespace:
    ap = argparse.ArgumentParser(description="240이평 양봉돌파 전략 백테스트 (탐색용)")
    ap.add_argument("--gap-threshold-pct", type=float, default=DEFAULT_PARAMS.gap_threshold_pct)
    ap.add_argument("--fixed-stop-pct", type=float, default=DEFAULT_PARAMS.fixed_stop_pct)
    ap.add_argument("--tp1-pct", type=float, default=DEFAULT_PARAMS.tp1_pct)
    ap.add_argument("--tp2-pct", type=float, default=DEFAULT_PARAMS.tp2_pct)
    return ap.parse_args()


def main() -> None:
    args = parse_args()
    params = Ma240BreakoutParams(
        gap_threshold_pct=args.gap_threshold_pct,
        fixed_stop_pct=args.fixed_stop_pct,
        tp1_pct=args.tp1_pct,
        tp2_pct=args.tp2_pct,
    )
    print(f"파라미터: {params.as_dict()}")
    result = run_strategy(params=params)
    print(_format_result(result))

    RESULTS_DIR.mkdir(parents=True, exist_ok=True)
    trades_df = pd.DataFrame([t.to_dict() for t in result["trades"]])
    if not trades_df.empty:
        trades_df.to_csv(RESULTS_DIR / "ma240_breakout_trades.csv", index=False)
    summary_row = {k: v for k, v in result.items() if k != "trades"}
    pd.DataFrame([summary_row]).to_csv(RESULTS_DIR / "ma240_breakout_summary.csv", index=False)
    print(f"\n결과 저장: {RESULTS_DIR}")


if __name__ == "__main__":
    main()
