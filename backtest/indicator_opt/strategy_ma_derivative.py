"""전략 G(MA 미분 전환) — 이동평균선의 미분값 하락→상승 전환 매수

진입 조건:
1. 이동평균선(SMA)의 미분값(전일차분)이 음수에서 0 또는 양수로 전환되는 최초 봉
2. 해당 봉 종가로 매수

청산 규칙 (익절 우선):
- 익절: entry * 1.03 (3%)
- 손절: 매수일 기준 최근 3일(매수봉 포함) 최저가로 고정, -4% 하한 캡
  - 매수금액 == 최저가이면 → entry * 0.96 (-4%)
  - 손절선이 -4%보다 깊으면 → entry * 0.96 (-4%)
- 같은 봉에 TP·SL 동시 도달 시 익절 우선

보유 규칙:
- 한 종목당 동시 1포지션
- 청산 전 중복 매수 금지
"""

from __future__ import annotations

import argparse
from dataclasses import asdict, dataclass
from pathlib import Path

import numpy as np
import pandas as pd

from ..data.loader import load_all
from ..indicators import sma
from ..metrics import summarize
from ..results_dir import results_root

BASELINE_START = pd.Timestamp("2020-08-03")
BASELINE_END = pd.Timestamp("2026-08-27")
RESULTS_DIR = results_root()

_OHLCV_COLUMNS = ("Open", "High", "Low", "Close", "Volume")
_PRICE_COLUMNS = ("Open", "High", "Low", "Close")
_TRADE_COLUMNS = (
    "ticker", "entry_date", "exit_date", "entry_price", "exit_price",
    "return_pct", "holding_bars", "exit_reason",
)


@dataclass(frozen=True)
class StrategyGParams:
    """전략 G 파라미터"""

    ma_window: int = 20          # 이동평균 기간
    take_profit_pct: float = 3.0 # 익절 %
    sl_lookback: int = 3         # 손절: 최근 N일 최저가 기준
    sl_fallback_pct: float = 4.0 # 매수금 == 최저가일 때 손절 %
    cost_rate: float = 0.0005   # 편도 수수료+슬리피지
    max_holding_bars: int | None = None  # 최대 보유 봉수 (None이면 무제한)
    volume_filter: bool = False  # 진입일 거래량 > 전일·전전일 조건

    def as_dict(self) -> dict[str, object]:
        return asdict(self)


def _compute_ma_derivative_signals(
    df: pd.DataFrame,
    ma_window: int = 20,
    volume_filter: bool = False,
) -> list[int]:
    """이동평균선 미분값 하락·평행→상승 전환 시그널 인덱스 반환.

    미분 = 전일차분 (MA[t] - MA[t-1])
    전환: 미분[t-1] <= 0 AND 미분[t] > 0
    volume_filter=True면 당일 거래량 > 전일 AND 전전일 조건 추가.
    """
    close = df["Close"].astype(float)
    ma = sma(close, ma_window)
    ma_arr = ma.to_numpy()

    # 전일차분 (미분 근사)
    diff = np.full(len(ma_arr), np.nan)
    diff[1:] = ma_arr[1:] - ma_arr[:-1]

    # 전환 조건: 직전 미분 < 0, 당 미분 >= 0
    prev_diff = np.full(len(diff), np.nan)
    prev_diff[1:] = diff[:-1]

    cond = np.full(len(df), False)
    valid = ~np.isnan(diff) & ~np.isnan(prev_diff)
    cond[valid] = (prev_diff[valid] <= 0) & (diff[valid] > 0)

    # 당일 거래량 > 전일 AND > 전전일 필터
    if volume_filter:
        vol_arr = df["Volume"].to_numpy(dtype=float)
        prev1 = np.full(len(vol_arr), np.nan)
        prev2 = np.full(len(vol_arr), np.nan)
        prev1[1:] = vol_arr[:-1]
        prev2[2:] = vol_arr[:-2]
        cond = cond & (vol_arr > prev1) & (vol_arr > prev2)

    # 진입 후 최소 1봉은 판단 가능해야 함
    cond &= np.arange(len(df)) < len(df) - 1

    return list(np.flatnonzero(cond))


@dataclass
class Trade:
    ticker: str
    entry_date: pd.Timestamp
    exit_date: pd.Timestamp
    entry_price: float
    exit_price: float
    return_pct: float
    holding_bars: int
    exit_reason: str

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
        }


def _run_backtest_single(
    df: pd.DataFrame,
    signal_indices: list[int],
    params: StrategyGParams,
    ticker: str = "",
) -> list[Trade]:
    """한 종목의 백테스트 실행. 동적 SL 지원."""
    close_arr = df["Close"].to_numpy(dtype=float)
    high_arr = df["High"].to_numpy(dtype=float)
    low_arr = df["Low"].to_numpy(dtype=float)
    n = len(df)

    trades: list[Trade] = []
    last_exit_idx = -1

    for e in signal_indices:
        # 중복 매수 방지
        if e <= last_exit_idx:
            continue
        if e >= n - 1:
            continue

        entry_price = close_arr[e]
        tp_price = entry_price * (1.0 + params.take_profit_pct / 100.0)

        # 손절선: 매수일 기준 최근 sl_lookback일 최저가로 고정 (매수봉 포함).
        # -sl_fallback_pct보다 깊으면 -sl_fallback_pct로 캡 (대형 손실 방지)
        sl_low_start = max(0, e - (params.sl_lookback - 1))
        recent_low = float(low_arr[sl_low_start:e + 1].min())
        sl_cap = entry_price * (1.0 - params.sl_fallback_pct / 100.0)
        if entry_price <= recent_low or recent_low < sl_cap:
            # 매수금액 == 최저가 (또는 지지선 역전) 또는 손절선이 캡보다 깊음 → -4% 고정
            sl_price = sl_cap
        else:
            sl_price = recent_low

        exit_price: float | None = None
        exit_reason = ""
        exit_idx = e

        last_eval_idx = n - 1
        if params.max_holding_bars is not None:
            last_eval_idx = min(last_eval_idx, e + params.max_holding_bars)

        for t in range(e + 1, last_eval_idx + 1):
            # 익절 우선 (tp_first=True): 같은 봉 TP·SL 동시 도달 시 익절
            if high_arr[t] >= tp_price:
                exit_price = tp_price
                exit_reason = "tp"
                exit_idx = t
                break
            if low_arr[t] <= sl_price:
                exit_price = sl_price
                exit_reason = "sl"
                exit_idx = t
                break

            if (
                params.max_holding_bars is not None
                and t - e >= params.max_holding_bars
            ):
                exit_price = close_arr[t]
                exit_reason = "max_hold"
                exit_idx = t
                break

        if exit_price is None:
            exit_price = close_arr[-1]
            exit_reason = "end"
            exit_idx = n - 1

        gross = (exit_price / entry_price - 1.0) * 100.0
        net = gross - params.cost_rate * 200.0

        trades.append(
            Trade(
                ticker=ticker,
                entry_date=df.index[e],
                exit_date=df.index[exit_idx],
                entry_price=entry_price,
                exit_price=float(exit_price),
                return_pct=round(net, 4),
                holding_bars=exit_idx - e,
                exit_reason=exit_reason,
            )
        )
        last_exit_idx = exit_idx

    return trades


def run_strategy_g_backtest(
    data: dict[str, pd.DataFrame] | None = None,
    params: StrategyGParams | None = None,
    start: pd.Timestamp | str | None = BASELINE_START,
    end: pd.Timestamp | str | None = BASELINE_END,
) -> dict[str, object]:
    """전략 G 전체 백테스트 실행."""

    params = params or StrategyGParams()
    data = load_all() if data is None else data

    start_ts = pd.Timestamp(start) if start is not None else None
    end_ts = pd.Timestamp(end) if end is not None else None

    all_trades: list[Trade] = []
    signal_count = 0
    n_tickers = 0
    months = set()

    for ticker in sorted(data):
        frame = data[ticker]
        if len(frame) < params.ma_window + 2:
            continue

        # 유효 행 필터
        numeric = frame.loc[:, _OHLCV_COLUMNS].apply(pd.to_numeric, errors="coerce")
        prices = numeric.loc[:, _PRICE_COLUMNS]
        valid_rows = (
            np.isfinite(numeric.to_numpy(dtype=float)).all(axis=1)
            & (prices > 0).all(axis=1).to_numpy()
            & (numeric["Volume"] >= 0).to_numpy()
            & (numeric["High"] >= numeric["Low"]).to_numpy()
        )

        # 유효 구간 분리
        valid_mask = valid_rows.astype(bool) if not isinstance(valid_rows, np.ndarray) else valid_rows.astype(bool)
        positions = np.flatnonzero(valid_mask)
        if len(positions) == 0:
            continue
        split_points = np.flatnonzero(np.diff(positions) > 1) + 1
        groups = np.split(positions, split_points)

        n_tickers += 1
        months.update(frame.index[valid_mask].to_period("M"))

        for group in groups:
            segment = frame.iloc[group[0]:group[-1] + 1]
            if len(segment) < params.ma_window + 2:
                continue

            signal_indices = _compute_ma_derivative_signals(
                segment, params.ma_window, params.volume_filter
            )

            # 기간 필터
            if start_ts is not None:
                signal_indices = [
                    i for i in signal_indices
                    if segment.index[i] >= start_ts
                ]
            if end_ts is not None:
                signal_indices = [
                    i for i in signal_indices
                    if segment.index[i] <= end_ts
                ]

            signal_count += len(signal_indices)

            segment_trades = _run_backtest_single(
                segment, signal_indices, params, ticker=ticker
            )

            # 진입일 기간 필터
            all_trades.extend(
                trade for trade in segment_trades
                if (start_ts is None or trade.entry_date >= start_ts)
                and (end_ts is None or trade.entry_date <= end_ts)
            )

    all_trades.sort(
        key=lambda trade: (trade.entry_date, trade.ticker, trade.exit_date)
    )

    performance = summarize(all_trades)
    result = {
        "strategy": "G",
        "params": params.as_dict(),
        "data_window_start": str(start_ts.date()) if start_ts is not None else None,
        "data_window_end": str(end_ts.date()) if end_ts is not None else None,
        "n_tickers": n_tickers,
        "n_signals": signal_count,
        "monthly_frequency": round(len(all_trades) / len(months), 4) if months else 0.0,
        "trades": [trade.to_dict() for trade in all_trades],
        **performance.to_dict(),
    }
    result["max_hold_exits"] = sum(
        1 for trade in all_trades if trade.exit_reason == "max_hold"
    )
    return result


def _format_result(result: dict[str, object]) -> str:
    return (
        f"전략 G(MA 미분전환) | 시그널 {result['n_signals']} | 거래 {result['n_trades']} "
        f"({result['n_win']}승/{result['n_loss']}패) | "
        f"승률 {result['win_rate'] * 100:.1f}% | PF {result['profit_factor']:.2f} | "
        f"평균 {result['avg_return']:+.3f}% | 최대보유 청산 {result['max_hold_exits']}건"
    )


def main() -> None:
    parser = argparse.ArgumentParser(
        description="전략 G(MA 미분 전환) baseline 백테스트"
    )
    parser.add_argument(
        "--output", type=Path,
        default=RESULTS_DIR / "strategy_g_baseline.csv",
        help="요약 CSV 출력 경로",
    )
    parser.add_argument("--start", default=BASELINE_START.date().isoformat())
    parser.add_argument("--end", default=BASELINE_END.date().isoformat())
    parser.add_argument("--ma-window", type=int, default=20)
    parser.add_argument("--tp-pct", type=float, default=3.0)
    parser.add_argument("--sl-lookback", type=int, default=3)
    parser.add_argument("--sl-fallback-pct", type=float, default=4.0)
    parser.add_argument("--volume-filter", action="store_true")
    args = parser.parse_args()

    params = StrategyGParams(
        ma_window=args.ma_window,
        take_profit_pct=args.tp_pct,
        sl_lookback=args.sl_lookback,
        sl_fallback_pct=args.sl_fallback_pct,
        volume_filter=args.volume_filter,
    )
    result = run_strategy_g_backtest(params=params, start=args.start, end=args.end)
    print("=== 전략 G(MA 미분 전환) ===")
    print(f"관측창: {result['data_window_start']} ~ {result['data_window_end']}")
    print(f"파라미터: {result['params']}")
    print(_format_result(result))

    args.output.parent.mkdir(parents=True, exist_ok=True)
    pd.DataFrame([{k: v for k, v in result.items() if k != "trades"}]).to_csv(
        args.output, index=False
    )
    trades_output = args.output.with_name(f"{args.output.stem}_trades.csv")
    pd.DataFrame(result["trades"], columns=_TRADE_COLUMNS).to_csv(
        trades_output, index=False
    )
    print(f"저장: {args.output}")
    print(f"거래 상세 저장: {trades_output}")


if __name__ == "__main__":
    main()
