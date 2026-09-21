"""전략 K 장단기 이평 window 조합 그리드 탐색.

long_window/short_window 후보값 전 조합(short < long)에 대해 나머지 파라미터는
기본값(StrategyKParams 기본값)으로 고정하고 백테스트 성과를 비교한다.
"""

from __future__ import annotations

import argparse
from pathlib import Path

import pandas as pd

from ..data.loader import load_all
from .run import RESULTS_DIR
from .strategy_k import STRATEGY_K_PARAMS, StrategyKParams, run_strategy_k_backtest

_DEFAULT_WINDOWS = (3, 5, 10, 20, 40, 60, 100, 120, 200, 240)


def _window_combos(windows: tuple[int, ...]) -> list[tuple[int, int]]:
    return [
        (long_w, short_w)
        for long_w in windows
        for short_w in windows
        if short_w < long_w
    ]


def run_grid(
    windows: tuple[int, ...] = _DEFAULT_WINDOWS,
    min_trades: int = 20,
) -> pd.DataFrame:
    data = load_all()
    combos = _window_combos(windows)
    rows: list[dict[str, object]] = []

    for long_w, short_w in combos:
        params = StrategyKParams(
            **{
                **STRATEGY_K_PARAMS.as_dict(),
                "long_window": long_w,
                "short_window": short_w,
                "long_angle_bars": min(5, short_w),
                "slope_window": min(STRATEGY_K_PARAMS.slope_window, short_w),
            }
        )
        result = run_strategy_k_backtest(data=data, params=params)
        rows.append(
            {
                "long_window": long_w,
                "short_window": short_w,
                "n_signals": result["n_signals"],
                "n_trades": result["n_trades"],
                "n_win": result["n_win"],
                "n_loss": result["n_loss"],
                "win_rate": result["win_rate"],
                "profit_factor": result["profit_factor"],
                "avg_return": result["avg_return"],
                "cum_return": result["cum_return"],
                "monthly_frequency": result["monthly_frequency"],
            }
        )
        print(
            f"long={long_w:>3} short={short_w:>3} | "
            f"시그널 {result['n_signals']:>5} 거래 {result['n_trades']:>5} | "
            f"승률 {result['win_rate'] * 100:5.1f}% | PF {result['profit_factor']:6.2f} | "
            f"평균 {result['avg_return']:+7.3f}% | 복리 {result['cum_return']:+10.1f}%"
        )

    df = pd.DataFrame(rows)
    df["meets_min_trades"] = df["n_trades"] >= min_trades
    return df.sort_values(
        ["meets_min_trades", "profit_factor", "win_rate"], ascending=False
    ).reset_index(drop=True)


def main() -> None:
    parser = argparse.ArgumentParser(description="전략 K 장단기 이평 window 그리드 탐색")
    parser.add_argument(
        "--windows", type=int, nargs="+", default=list(_DEFAULT_WINDOWS),
        help="테스트할 이평 기간 목록 (기본: 3 5 10 20 40 60 100 120 200 240)",
    )
    parser.add_argument("--min-trades", type=int, default=20)
    parser.add_argument(
        "--output", type=Path,
        default=RESULTS_DIR / "strategy_k_window_grid.csv",
    )
    args = parser.parse_args()

    df = run_grid(windows=tuple(args.windows), min_trades=args.min_trades)
    args.output.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(args.output, index=False)

    print(f"\n총 {len(df)}개 조합 완료. 저장: {args.output}")
    qualifying = df[df["meets_min_trades"]]
    top = qualifying.head(10) if not qualifying.empty else df.head(10)
    print(f"\n=== 상위 10 (PF·승률 순, 최소거래 {args.min_trades}건 {'충족' if not qualifying.empty else '미충족 - 전체 기준'}) ===")
    print(
        top[
            [
                "long_window", "short_window", "n_signals", "n_trades",
                "win_rate", "profit_factor", "avg_return", "cum_return",
            ]
        ].to_string(index=False)
    )


if __name__ == "__main__":
    main()
