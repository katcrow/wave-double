"""포트폴리오 시뮬레이션 — 실전에 가까운 자본·캐시·동시 보유 관리

기존 엔진(run_backtest)이 종목별 독립 트레이드를 생성한다면,
이 모듈은 이를 날짜축으로 병합해 하나의 계좌를 시뮬레이션한다:
- 매 진입: 현재 계좌 평가액의 position_pct %를 투입 (나머지는 현금)
- 현금 부족이면 시그널 스킵
- 미실현 손익 포함 일별 계좌 평가 → MDD/CAGR 산출
- 유니버스 동일비중 지수(buy&hold)와 비교

단순화 가정:
- 시그널 발생일 종가에 진입, 청산은 엔진 판정(TP/SL) 종가 기준
- 슬리피지/수수료는 트레이드 return_pct(엔진)에 반영된 것을 사용
- 동일 종목 중복 보유는 엔진이 이미 차단한 시퀀스를 사용
"""

from __future__ import annotations

import argparse
import json
from dataclasses import dataclass
from pathlib import Path

import matplotlib

matplotlib.use("Agg")
import matplotlib.pyplot as plt
import pandas as pd

from .compare import equal_weight_index
from .data.loader import load_all
from .engine import Trade, TradeParams, run_backtest
from .signals import DoubleWaveParams, detect_entries

plt.rcParams.update({
    "font.family": "IPAGothic",
    "axes.unicode_minus": False,
    "figure.dpi": 110,
})
OUT = Path(__file__).parent / "results"


@dataclass
class PortfolioResult:
    equity: pd.Series
    cash: pd.Series
    n_entries: int
    n_skips: int
    max_positions: int
    summary: dict


def simulate_portfolio(
    data: dict[str, pd.DataFrame],
    sigs_map: dict[str, list],
    trade_params: TradeParams,
    initial_capital: float = 100_000_000,
    position_pct: float = 0.25,
    max_positions: int | None = None,
) -> PortfolioResult:
    """날짜축 포트폴리오 시뮬레이션.

    position_pct: 0~1, 진입 시점 계좌 평가액의 해당 비율만큼 투입.
    max_positions: 동시 보유 상한 (None = 자금에 의한 자동 제한만).
    """
    close_of = {t: df["Close"] for t, df in data.items()}
    dates = next(iter(data.values())).index

    trades_by_t: dict[str, list[Trade]] = {}
    for ticker, df in data.items():
        trades_by_t[ticker] = run_backtest(
            df, sigs_map.get(ticker, []), trade_params, ticker=ticker
        )

    # 날짜순 진입 이벤트 (같은 종목의 시퀀스는 이미 겹침 스킵됨)
    events = sorted(
        ((tr.entry_date, tr) for ts in trades_by_t.values() for tr in ts),
        key=lambda x: x[0],
    )

    # open_pos: {id(trade): {"tr": trade, "invested": 액수, "ticker": ...}}
    open_pos: dict[int, dict] = {}
    realized = 0.0
    cash_hist: list[float] = []
    equity_hist: list[float] = []
    max_pos = 0
    n_skips = 0
    qi = 0  # events 인덱스 (날짜 오름차순 전진)

    def current_equity() -> float:
        """현재 계좌 평가 = 초기 + 실현 손익 + 미실현(경과분)"""
        return initial_capital + realized + sum(
            op["mark"] for op in open_pos.values()
        )

    for date in dates:
        # ── 이 날짜 진입 이벤트 처리 ──────────────────────────────
        while qi < len(events) and events[qi][0] == date:
            tr = events[qi][1]
            qi += 1
            if any(op["ticker"] == tr.ticker for op in open_pos.values()):
                continue  # 실전 방어 (시퀀스상 불가하지만 안전망)
            if max_positions is not None and len(open_pos) >= max_positions:
                n_skips += 1
                continue
            invested = current_equity() * position_pct
            if invested <= 0:
                n_skips += 1
                continue
            open_pos[id(tr)] = {"tr": tr, "ticker": tr.ticker, "invested": invested, "mark": 0.0}

        # ── 이 날짜 청산 + 미실현 평가 갱신 ─────────────────────────
        for key, op in list(open_pos.items()):
            tr = op["tr"]
            if date >= tr.exit_date:
                op["mark"] = op["invested"] * tr.return_pct / 100.0
            else:
                p0 = close_of[tr.ticker].loc[tr.entry_date]
                p1 = close_of[tr.ticker].loc[date]
                op["mark"] = op["invested"] * (p1 / p0 - 1.0)
        # 청산 처리 (exit_date 당일은 확정 수익으로 반영 후 포지션 제거)
        for key, op in list(open_pos.items()):
            if date >= op["tr"].exit_date:
                realized += op["mark"]
                del open_pos[key]

        cash = initial_capital + realized - sum(op["invested"] for op in open_pos.values())
        cash_hist.append(cash)
        equity_hist.append(initial_capital + realized + sum(op["mark"] for op in open_pos.values()))
        max_pos = max(max_pos, len(open_pos))

    equity = pd.Series(equity_hist, index=dates)
    cash_s = pd.Series(cash_hist, index=dates)

    def _mdd(series):
        dd = (series - series.cummax()) / series.cummax()
        return dd.min() * 100.0

    years = len(dates) / 252.0
    end_eq = float(equity.iloc[-1])
    total_ret = (end_eq / initial_capital - 1.0) * 100.0
    summary = {
        "initial_capital": initial_capital,
        "position_pct": position_pct,
        "final_equity": round(end_eq),
        "total_return_pct": round(total_ret, 2),
        "cagr_pct": round(((end_eq / initial_capital) ** (1 / years) - 1.0) * 100.0, 2),
        "max_drawdown_pct": round(_mdd(equity), 2),
        "n_entries": len(events) - n_skips,
        "n_skips": n_skips,
        "max_positions": max_pos,
        "avg_cash_ratio": round(float((cash_s / equity).mean()), 3),
    }
    return PortfolioResult(equity, cash_s, summary["n_entries"], n_skips, max_pos, summary)


def main() -> None:
    ap = argparse.ArgumentParser()
    ap.add_argument("--L", type=int, default=7)
    ap.add_argument("--S", type=int, default=3)
    ap.add_argument("--W", type=int, default=7)
    ap.add_argument("--k", type=int, default=3)
    ap.add_argument("--eps", type=float, default=0.05)
    ap.add_argument("--rise", type=float, default=0.0)
    ap.add_argument("--max-rise", type=float, default=10.0)
    ap.add_argument("--tp-atr", type=float, default=6.0)
    ap.add_argument("--sl-atr", type=float, default=1.5)
    ap.add_argument("--capital", type=float, default=100_000_000)
    ap.add_argument("--position-pct", type=float, default=0.25)
    ap.add_argument("--max-positions", type=int, default=None)
    args = ap.parse_args()

    data = load_all()
    sig_p = DoubleWaveParams(
        long_window=args.L, short_window=args.S, w_period=args.W,
        k=args.k, eps=args.eps, adjust_eps=args.eps,
        pullback_rise_pct=args.rise, max_rise_pct=args.max_rise,
    )
    tr_p = TradeParams(tp_atr=args.tp_atr, sl_atr=args.sl_atr)
    print("시그널 검출 중...")
    sigs_map = {t: detect_entries(df, sig_p, ticker=t) for t, df in data.items()}

    res = simulate_portfolio(
        data, sigs_map, tr_p,
        initial_capital=args.capital,
        position_pct=args.position_pct,
        max_positions=args.max_positions,
    )
    s = res.summary
    ew = equal_weight_index(data)
    bh_ret = (ew.iloc[-1] - 1.0) * 100.0

    print(f"전략: 총수익 {s['total_return_pct']:+.2f}% | CAGR {s['cagr_pct']:+.2f}% | MDD {s['max_drawdown_pct']:.2f}%")
    print(f"진입 {s['n_entries']}회 (스킵 {s['n_skips']}) | 최대 동시 보유 {s['max_positions']} | 평균 현금비중 {s['avg_cash_ratio']*100:.0f}%")
    print(f"최종 계좌: {s['final_equity']:,.0f}원")
    print(f"동일비중 지수(buy&hold): {bh_ret:+.2f}% | 전략 초과: {s['total_return_pct'] - bh_ret:+.2f}%p")

    out_dir = OUT / "portfolio"
    out_dir.mkdir(parents=True, exist_ok=True)
    fig, ax = plt.subplots(figsize=(11, 5))
    ax.plot(res.equity.index, res.equity / args.capital, label=f"전략 ({args.position_pct*100:.0f}% 진입)", color="#d62728")
    ax.plot(ew.index, ew, label="동일비중 지수", color="#1f77b4")
    ax.set_title(f"포트폴리오 시뮬레이션 (L{args.L}·S{args.S}·k{args.k}·e{args.eps}·TP{args.tp_atr}·SL{args.sl_atr})")
    ax.set_ylabel("배수")
    ax.legend()
    plt.tight_layout()
    fname = out_dir / f"equity_L{args.L}_S{args.S}_k{args.k}_e{args.eps}_TP{args.tp_atr}_SL{args.sl_atr}.png"
    fig.savefig(fname)
    plt.close(fig)
    (out_dir / "summary.json").write_text(json.dumps(s, indent=2, ensure_ascii=False))
    print(f"차트: {fname}")


if __name__ == "__main__":
    main()