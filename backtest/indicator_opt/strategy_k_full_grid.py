"""전략 K 전체 파라미터 그리드 탐색 (window 조합 + 이격도/각도/기울기창/ATR배수).

1단계 window 그리드(strategy_k_grid.py)에서 PF>=1.35 & n_trades>=20을 만족한
장단기 조합만 후보로 남기고, 그 각각에 대해 나머지 파라미터를 전부 조합하여
멀티프로세스로 백테스트한다.
"""

from __future__ import annotations

import argparse
import itertools
from concurrent.futures import ProcessPoolExecutor, as_completed
from pathlib import Path

import pandas as pd

from ..data.loader import load_all
from .run import RESULTS_DIR
from .strategy_k import StrategyKParams, run_strategy_k_backtest

# 1단계 window 그리드에서 PF>=1.35, n_trades>=20을 만족한 (long, short) 후보
CANDIDATE_WINDOWS: tuple[tuple[int, int], ...] = (
    (60, 20), (60, 5), (60, 10), (60, 40),
    (100, 60), (120, 60), (100, 40), (100, 10),
    (120, 10), (40, 20), (200, 3), (200, 40),
)

DEVIATION_PCT_GRID = (3.0, 5.0, 7.0)
LONG_ANGLE_MAX_GRID = (1.0, 2.0, 3.0)
SLOPE_WINDOW_GRID = (3, 5, 10)
TP_ATR_GRID = (2.0, 3.0, 4.0)
SL_ATR_GRID = (1.5, 2.0, 3.0)
LONG_ANGLE_MIN = 0.1  # 고정: "작은 각도"의 하한 (0에 가까운 최소 우상향)

_SHARED: dict = {}


def _init_worker(shared: dict) -> None:
    global _SHARED
    _SHARED = shared


def _run_one(
    long_w: int, short_w: int, deviation_pct: float, long_angle_max: float,
    slope_window: int, tp_atr: float, sl_atr: float,
) -> dict[str, object]:
    params = StrategyKParams(
        long_window=long_w,
        short_window=short_w,
        long_angle_bars=min(5, short_w),
        long_angle_min=LONG_ANGLE_MIN,
        long_angle_max=long_angle_max,
        deviation_pct=deviation_pct,
        slope_window=min(slope_window, short_w) if slope_window >= 2 else 2,
        tp_atr=tp_atr,
        sl_atr=sl_atr,
    )
    result = run_strategy_k_backtest(data=_SHARED["data"], params=params)
    return {
        "long_window": long_w,
        "short_window": short_w,
        "deviation_pct": deviation_pct,
        "long_angle_max": long_angle_max,
        "slope_window": params.slope_window,
        "tp_atr": tp_atr,
        "sl_atr": sl_atr,
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


def _all_combos(windows: tuple[tuple[int, int], ...]) -> list[tuple]:
    return [
        (long_w, short_w, dev, amax, sw, tp, sl)
        for (long_w, short_w) in windows
        for dev in DEVIATION_PCT_GRID
        for amax in LONG_ANGLE_MAX_GRID
        for sw in SLOPE_WINDOW_GRID
        for tp in TP_ATR_GRID
        for sl in SL_ATR_GRID
    ]


def main() -> None:
    parser = argparse.ArgumentParser(description="전략 K 전체 파라미터 그리드 탐색")
    parser.add_argument("--workers", type=int, default=6)
    parser.add_argument("--min-trades", type=int, default=20)
    parser.add_argument(
        "--output", type=Path,
        default=RESULTS_DIR / "strategy_k_full_grid.csv",
    )
    args = parser.parse_args()

    combos = _all_combos(CANDIDATE_WINDOWS)
    print(f"조합 수: {len(combos)}, 워커: {args.workers}")

    data = load_all()
    shared = {"data": data}

    rows: list[dict[str, object]] = []
    done = 0
    with ProcessPoolExecutor(
        max_workers=args.workers, initializer=_init_worker, initargs=(shared,)
    ) as ex:
        futs = {ex.submit(_run_one, *c): c for c in combos}
        for fut in as_completed(futs):
            rows.append(fut.result())
            done += 1
            if done % 200 == 0 or done == len(combos):
                print(f"진행 {done}/{len(combos)}")

    df = pd.DataFrame(rows)
    df["meets_min_trades"] = df["n_trades"] >= args.min_trades
    df = df.sort_values(
        ["meets_min_trades", "profit_factor", "win_rate"], ascending=False
    ).reset_index(drop=True)

    args.output.parent.mkdir(parents=True, exist_ok=True)
    df.to_csv(args.output, index=False)
    print(f"\n총 {len(df)}개 조합 완료. 저장: {args.output}")

    qualifying = df[df["meets_min_trades"]]
    top = qualifying.head(15) if not qualifying.empty else df.head(15)
    print(f"\n=== 상위 15 (PF·승률 순, 최소거래 {args.min_trades}건 {'충족' if not qualifying.empty else '미충족 - 전체 기준'}) ===")
    print(
        top[
            [
                "long_window", "short_window", "deviation_pct", "long_angle_max",
                "slope_window", "tp_atr", "sl_atr",
                "n_trades", "win_rate", "profit_factor", "avg_return", "cum_return",
            ]
        ].to_string(index=False)
    )


if __name__ == "__main__":
    main()
