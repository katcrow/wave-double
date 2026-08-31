"""성과 지표 모듈"""

from __future__ import annotations

from dataclasses import dataclass, field

import numpy as np

from ..engine import Trade


@dataclass
class Performance:
    """트레이드 시퀀스 성과 요약"""

    n_trades: int = 0
    n_win: int = 0
    n_loss: int = 0
    win_rate: float = 0.0
    avg_return: float = 0.0  # 평균 수익률 (%)
    total_return: float = 0.0  # 단리 누적 수익률 (%)
    cum_return: float = 0.0  # 복리 누적 (기하) 수익률 (%)
    profit_factor: float = 0.0
    avg_win: float = 0.0
    avg_loss: float = 0.0
    max_drawdown: float = 0.0  # 트레이드 등가 커브 기준 (%)
    avg_holding_bars: float = 0.0
    best_return: float = 0.0
    worst_return: float = 0.0
    exit_counts: dict[str, int] = field(default_factory=dict)
    tickers_hit: int = 0

    def to_dict(self) -> dict:
        return {
            "n_trades": self.n_trades,
            "n_win": self.n_win,
            "n_loss": self.n_loss,
            "win_rate": round(self.win_rate, 4),
            "avg_return": round(self.avg_return, 4),
            "total_return": round(self.total_return, 4),
            "cum_return": round(self.cum_return, 4),
            "profit_factor": round(self.profit_factor, 4),
            "avg_win": round(self.avg_win, 4),
            "avg_loss": round(self.avg_loss, 4),
            "max_drawdown": round(self.max_drawdown, 4),
            "avg_holding_bars": round(self.avg_holding_bars, 2),
            "best_return": round(self.best_return, 4),
            "worst_return": round(self.worst_return, 4),
            "exit_counts": self.exit_counts,
            "tickers_hit": self.tickers_hit,
        }


def _max_drawdown_pct(equity: np.ndarray) -> float:
    if len(equity) == 0:
        return 0.0
    peak = np.maximum.accumulate(equity)
    dd = equity / peak - 1.0
    return float(dd.min() * 100.0)


def summarize(trades: list[Trade]) -> Performance:
    """트레이드 리스트로 성과 지표 계산. 비용은 이미 return_pct에 반영됨."""
    p = Performance()
    if not trades:
        return p

    rets = np.array([t.return_pct for t in trades])
    p.n_trades = len(rets)
    p.n_win = int((rets > 0).sum())
    p.n_loss = int((rets < 0).sum())
    p.win_rate = p.n_win / p.n_trades
    p.avg_return = float(rets.mean())
    p.total_return = float(rets.sum())  # 단리
    p.cum_return = float((np.prod(1.0 + rets / 100.0) - 1.0) * 100.0)  # 복리
    p.avg_holding_bars = float(np.mean([t.holding_bars for t in trades]))
    p.best_return = float(rets.max())
    p.worst_return = float(rets.min())

    wins = rets[rets > 0]
    losses = rets[rets < 0]
    p.avg_win = float(wins.mean()) if len(wins) else 0.0
    p.avg_loss = float(losses.mean()) if len(losses) else 0.0
    gross = wins.sum()
    gross_loss = abs(losses.sum())
    p.profit_factor = float(gross / gross_loss) if gross_loss > 0 else float("inf")

    equity = np.cumprod(1.0 + rets / 100.0)
    p.max_drawdown = _max_drawdown_pct(equity)

    reasons = {}
    for t in trades:
        reasons[t.exit_reason] = reasons.get(t.exit_reason, 0) + 1
    p.exit_counts = reasons
    p.tickers_hit = len({t.ticker for t in trades})
    return p