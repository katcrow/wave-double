"""다바스 박스(Nicolas Darvas) 전략 계산 및 백테스트.

박스 정의 (Neo 합의, 2026-10-15):
    - 상단(Ceiling): ``high_lookback``봉 신고가를 만든 봉의 고가가, 이후
      ``confirm_days``일 연속으로 그 고가보다 낮은 고가를 기록하면 상단 확정.
    - 하단(Floor): 상단 확정일부터 시작해 최저 저가를 추적하고, 이후
      ``confirm_days``일 연속으로 그 저가보다 높은 저가를 기록하면 하단 확정.
    - 하단 확정 전에 상단을 위로 뚫으면 박스는 폐기되고 상단 탐색을 다시 시작한다.
    - 상단·하단이 모두 확정되면 박스가 성립하고, 상단을 뚫거나 하단을 (종가로)
      깨질 때까지 우측으로 연장된다.

진입 신호 2종 (독립):
    - 전략 1 ``breakout``: 확정된 박스 상단을 뚫은 봉(고가 > 상단)의 종가 매수.
    - 전략 2 ``rebound``: 확정된 박스 하단을 저가로 이탈했지만 종가가 하단 이상으로
      되돌린 봉(저가 < 하단 ≤ 종가)의 종가 매수 — 속임수 이탈 반등.
    - 전략 3 ``combined``: 위 두 신호의 합집합. 엔진이 종목당 1포지션만 허용하므로
      같은 종목 중복보유가 자동으로 금지된다.

진입 필터:
    - ``min_box_width`` (기본 0=비활성): (천장-바닥)/바닥 < 이 값인 박스의 신호는
      무시한다. 너무 좁은(휩소가 잦은) 박스를 걸러낸다.

청산 (``DarvasParams``의 exit 플래그로 조합):
    - ``exit_atr_tp`` (기본 True): 익절 = entry + tp_atr * ATR(진입봉)
    - ``exit_atr_sl`` (기본 True): 손절 = entry - sl_atr * ATR(진입봉)
    - ``exit_floor`` (기본 False): 원전식 — 진입 시 박스 하단을 이탈하면 청산.
      진입 봉의 유효 박스 하단(``floor``)을 정적 손절선으로 사용한다.
    같은 봉에서 손절선(들)과 익절이 동시 도달하면 손절 우선(보수적). 손절선이
    둘 이상 걸리면(ATR SL·박스 하단) 먼저 닿는(=더 높은) 선으로 청산한다.
    세 청산 중 최소 하나는 활성이어야 한다(그 외엔 데이터 끝/최대보유만 남음).
"""

from __future__ import annotations

import argparse
from dataclasses import asdict, dataclass, replace
from numbers import Integral, Real
from pathlib import Path

import numpy as np
import pandas as pd

from ..data.loader import load_all
from ..engine import (
    EXIT_END, EXIT_MAX_HOLD, EXIT_SL, EXIT_TP, Trade,
)
from ..indicators import atr
from ..metrics import summarize
from ..results_dir import scratch_root
from ._signals import SimpleSignal

RESULTS_DIR = scratch_root()

EXIT_FLOOR = "floor"
EXIT_TRAIL = "trail"

_OHLCV_COLUMNS = ("Open", "High", "Low", "Close", "Volume")
_PRICE_COLUMNS = ("Open", "High", "Low", "Close")
_MAX_WINDOW = 100_000
_TRADE_COLUMNS = (
    "ticker", "entry_date", "exit_date", "entry_price", "exit_price",
    "return_pct", "holding_bars", "exit_reason",
)
BASELINE_START = pd.Timestamp("2020-08-03")
BASELINE_END = pd.Timestamp("2026-09-15")

BREAKOUT = "breakout"
REBOUND = "rebound"
COMBINED = "combined"
MODES = (BREAKOUT, REBOUND, COMBINED)


@dataclass(frozen=True)
class DarvasParams:
    """다바스 박스의 박스 구조·진입·청산 파라미터."""

    confirm_days: int = 3         # 상/하단 확정에 필요한 미돌파 일수 (탐색 핵심 변수)
    high_lookback: int = 60       # 상단 후보가 되어야 하는 "신고가" 기준 봉수
    tp_atr: float = 3.0           # 익절 = entry + tp_atr * ATR(진입봉)
    sl_atr: float = 2.0           # 손절 = entry - sl_atr * ATR(진입봉)
    atr_window: int = 14
    max_holding_bars: int | None = None  # None이면 청산 규칙/데이터끝까지 보유
    cost_rate: float = 0.0005     # 편도 수수료+슬리피지
    tp_first: bool = False        # 같은 봉 TP·SL 동시 도달 시 익절 우선 여부
    exit_atr_tp: bool = True      # ATR 익절 사용
    exit_atr_sl: bool = True      # ATR 손절 사용
    exit_floor: bool = False      # 원전식 박스 하단 이탈 청산 사용
    min_box_width: float = 0.0    # (천장-바닥)/바닥 최소 박스 폭 (0=필터 없음)
    trail_atr: float | None = None  # ATR 트레일링 스톱 배수 (None=비활성)

    def as_dict(self) -> dict[str, int | float | bool | None]:
        return asdict(self)


DARVAS_PARAMS = DarvasParams()


def _validate_finite_real(name: str, value: object) -> float:
    if isinstance(value, bool) or not isinstance(value, Real):
        raise ValueError(f"{name}은 유한한 실수여야 합니다")
    value = float(value)
    if not np.isfinite(value):
        raise ValueError(f"{name}은 유한한 실수여야 합니다")
    return value


def _validate_positive_integer(
    name: str, value: object, *, minimum: int = 1
) -> int:
    if isinstance(value, bool) or not isinstance(value, Integral):
        raise ValueError(f"{name}은 정수여야 합니다")
    value = int(value)
    if not minimum <= value <= _MAX_WINDOW:
        raise ValueError(f"{name}은 {minimum}~{_MAX_WINDOW} 범위여야 합니다")
    return value


def _validate_params(params: DarvasParams) -> None:
    if not isinstance(params, DarvasParams):
        raise ValueError("params는 DarvasParams여야 합니다")

    _validate_positive_integer("confirm_days", params.confirm_days)
    _validate_positive_integer("high_lookback", params.high_lookback, minimum=2)

    tp_atr = _validate_finite_real("tp_atr", params.tp_atr)
    sl_atr = _validate_finite_real("sl_atr", params.sl_atr)
    if tp_atr <= 0.0:
        raise ValueError("tp_atr은 0보다 커야 합니다")
    if sl_atr <= 0.0:
        raise ValueError("sl_atr은 0보다 커야 합니다")

    _validate_positive_integer("atr_window", params.atr_window)
    if params.max_holding_bars is not None:
        _validate_positive_integer("max_holding_bars", params.max_holding_bars)

    cost_rate = _validate_finite_real("cost_rate", params.cost_rate)
    if not 0.0 <= cost_rate < 1.0:
        raise ValueError("cost_rate은 [0, 1) 범위여야 합니다")

    min_box_width = _validate_finite_real("min_box_width", params.min_box_width)
    if min_box_width < 0.0:
        raise ValueError("min_box_width는 0 이상이어야 합니다")

    if params.trail_atr is not None:
        trail_atr = _validate_finite_real("trail_atr", params.trail_atr)
        if trail_atr <= 0.0:
            raise ValueError("trail_atr은 0보다 커야 합니다")

    if not isinstance(params.tp_first, bool):
        raise ValueError("tp_first는 bool이어야 합니다")

    for name in ("exit_atr_tp", "exit_atr_sl", "exit_floor"):
        if not isinstance(getattr(params, name), bool):
            raise ValueError(f"{name}는 bool이어야 합니다")
    if not any(
        (params.exit_atr_tp, params.exit_atr_sl, params.exit_floor,
         params.trail_atr is not None)
    ):
        raise ValueError(
            "청산 규칙이 최소 하나는 활성이어야 합니다 "
            "(exit_atr_tp / exit_atr_sl / exit_floor / trail_atr)"
        )


def validate_darvas_params(params: DarvasParams) -> None:
    """다바스 파라미터 계약을 외부 검증 코드에서도 사용할 수 있게 노출한다."""

    _validate_params(params)


def _validate_mode(mode: str) -> str:
    if mode not in MODES:
        raise ValueError(f"mode는 {MODES} 중 하나여야 합니다")
    return mode


def _validate_frame_layout(frame: pd.DataFrame) -> None:
    if not isinstance(frame, pd.DataFrame):
        raise ValueError("OHLCV 입력은 DataFrame이어야 합니다")
    if frame.columns.has_duplicates:
        raise ValueError("OHLCV 컬럼명은 중복될 수 없습니다")
    missing = [column for column in _OHLCV_COLUMNS if column not in frame.columns]
    if missing:
        raise ValueError(f"OHLCV 컬럼이 없습니다: {', '.join(missing)}")
    if not isinstance(frame.index, pd.DatetimeIndex):
        raise ValueError("OHLCV 인덱스는 DatetimeIndex여야 합니다")
    if not frame.index.is_monotonic_increasing or not frame.index.is_unique:
        raise ValueError("OHLCV 인덱스는 중복 없는 오름차순이어야 합니다")


def _validate_frame(frame: pd.DataFrame) -> None:
    _validate_frame_layout(frame)
    values = frame.loc[:, _OHLCV_COLUMNS].to_numpy(dtype=float)
    if not np.isfinite(values).all():
        raise ValueError("OHLCV에 유한하지 않은 값이 있습니다")
    prices = frame.loc[:, _PRICE_COLUMNS]
    if (prices <= 0).any().any():
        raise ValueError("OHLC 가격은 양수여야 합니다")
    if (frame["Volume"] < 0).any():
        raise ValueError("거래량은 음수일 수 없습니다")
    if (frame["High"] < frame["Low"]).any():
        raise ValueError("고가는 저가보다 작을 수 없습니다")
    if (
        (frame["High"] < frame["Open"])
        | (frame["High"] < frame["Close"])
        | (frame["Low"] > frame["Open"])
        | (frame["Low"] > frame["Close"])
    ).any():
        raise ValueError("OHLC 가격 관계가 유효하지 않습니다")


def _valid_ohlcv_rows(frame: pd.DataFrame) -> pd.Series:
    """baseline 입력에서 계산에 사용할 수 있는 행을 표시한다."""

    prices = frame.loc[:, _PRICE_COLUMNS]
    valid = (
        np.isfinite(frame.loc[:, _OHLCV_COLUMNS].to_numpy(dtype=float)).all(axis=1)
        & (prices > 0).all(axis=1).to_numpy()
        & (frame["Volume"] >= 0).to_numpy()
        & (frame["High"] >= frame["Low"]).to_numpy()
        & (frame["High"] >= frame["Open"]).to_numpy()
        & (frame["High"] >= frame["Close"]).to_numpy()
        & (frame["Low"] <= frame["Open"]).to_numpy()
        & (frame["Low"] <= frame["Close"]).to_numpy()
    )
    return pd.Series(valid, index=frame.index, dtype=bool)


def _valid_segments(
    frame: pd.DataFrame, valid_rows: pd.Series
) -> list[pd.DataFrame]:
    """유효 행만 이어지는 구간을 분리해 invalid 행을 봉 연결로 취급하지 않는다."""

    positions = np.flatnonzero(valid_rows.to_numpy(dtype=bool))
    if len(positions) == 0:
        return []
    split_points = np.flatnonzero(np.diff(positions) > 1) + 1
    groups = np.split(positions, split_points)
    return [frame.iloc[group[0] : group[-1] + 1] for group in groups]


# ── 박스 탐지 상태기계 (lookahead 없는 forward 순회) ───────────────────────────

_ST_SEARCH, _ST_CEIL, _ST_FLOOR, _ST_ACTIVE = 0, 1, 2, 3


def _darvas_masks(
    high: pd.Series,
    low: pd.Series,
    close: pd.Series,
    confirm_days: int,
    high_lookback: int,
) -> tuple[np.ndarray, np.ndarray, np.ndarray, np.ndarray]:
    """상단 돌파·하단 반등 마스크와 진입봉의 유효 박스 하단/상단을 계산한다.

    반환 floor[i]/ceil[i]는 i봉이 활성 박스 안일 때 그 박스의 하단/상단, 아니면 NaN.
    """

    h = high.to_numpy(dtype=float)
    l = low.to_numpy(dtype=float)
    c = close.to_numpy(dtype=float)
    n = len(h)
    brk = np.zeros(n, dtype=bool)
    reb = np.zeros(n, dtype=bool)
    floor_arr = np.full(n, np.nan)
    ceil_arr = np.full(n, np.nan)
    if n == 0:
        return brk, reb, floor_arr, ceil_arr

    # 상단 후보가 될 수 있는 "신고가" 봉: 직전 high_lookback봉(당일 포함) 최고가.
    roll_max = (
        high.rolling(high_lookback, min_periods=high_lookback).max().to_numpy()
    )

    mode = _ST_SEARCH
    hc = -1            # 상단 후보 봉 위치
    count = 0          # 상단 확정 카운터 (고가 < 후보 고가 연속 일수)
    ceiling = np.nan   # 확정된 박스 상단
    floor = np.nan     # 하단 후보/확정 저가
    floor_count = 0    # 하단 확정 카운터 (저가 > 후보 저가 연속 일수)

    i = 0
    while i < n:
        if mode == _ST_SEARCH:
            if not np.isnan(roll_max[i]) and h[i] >= roll_max[i]:
                hc = i
                count = 0
                mode = _ST_CEIL
            i += 1

        elif mode == _ST_CEIL:
            if h[i] >= h[hc]:
                hc = i
                count = 0
            else:
                count += 1
                if count >= confirm_days:
                    ceiling = h[hc]
                    floor = l[i]
                    floor_count = 0
                    mode = _ST_FLOOR
            i += 1

        elif mode == _ST_FLOOR:
            if h[i] > ceiling:
                # 하단 확정 전 상단 돌파 → 박스 폐기, 이 봉을 새 상단 후보로 재평가
                mode = _ST_SEARCH
                continue
            if l[i] <= floor:
                floor = l[i]
                floor_count = 0
            else:
                floor_count += 1
                if floor_count >= confirm_days:
                    mode = _ST_ACTIVE
            i += 1

        else:  # _ST_ACTIVE
            floor_arr[i] = floor  # 진입봉의 유효 박스 하단
            ceil_arr[i] = ceiling  # 진입봉의 유효 박스 상단
            if h[i] > ceiling:
                brk[i] = True
                mode = _ST_SEARCH  # 박스 상향 이탈 → 새 박스 탐색
                continue
            if l[i] < floor:
                if c[i] >= floor:
                    reb[i] = True  # 저가 이탈 후 종가 회복 = 속임수 이탈 반등
                else:
                    mode = _ST_SEARCH  # 종가로 하단 이탈 → 박스 하향 무효
                    i += 1
                    continue
            i += 1

    return brk, reb, floor_arr, ceil_arr


def darvas_masks(
    frame: pd.DataFrame, params: DarvasParams = DARVAS_PARAMS
) -> tuple[pd.Series, pd.Series]:
    """(상단 돌파 마스크, 하단 반등 마스크)를 동일 인덱스 bool Series로 반환한다."""

    brk, reb, _, _ = darvas_masks_full(frame, params)
    return brk, reb


def darvas_masks_full(
    frame: pd.DataFrame, params: DarvasParams = DARVAS_PARAMS
) -> tuple[pd.Series, pd.Series, pd.Series, pd.Series]:
    """상단/하단 마스크 + 진입봉의 유효 박스 하단/상단을 반환한다."""

    _validate_frame(frame)
    _validate_params(params)
    brk, reb, floor_arr, ceil_arr = _darvas_masks(
        frame["High"], frame["Low"], frame["Close"],
        params.confirm_days, params.high_lookback,
    )
    return (
        pd.Series(brk, index=frame.index, dtype=bool),
        pd.Series(reb, index=frame.index, dtype=bool),
        pd.Series(floor_arr, index=frame.index, dtype=float),
        pd.Series(ceil_arr, index=frame.index, dtype=float),
    )


def darvas_signals(
    frame: pd.DataFrame,
    ticker: str = "",
    params: DarvasParams = DARVAS_PARAMS,
    mode: str = COMBINED,
) -> list[SimpleSignal]:
    """모드별 매수 마스크를 종가 진입 신호로 변환한다.

    stop_price/take_profit을 지정하지 않으므로 ``engine.run_backtest``가 ATR
    기반 TP/SL(entry ± tp_atr/sl_atr * ATR)로 청산을 계산한다.
    """

    mode = _validate_mode(mode)
    brk, reb, floor, ceiling = darvas_masks_full(frame, params)
    if mode == BREAKOUT:
        mask = brk
    elif mode == REBOUND:
        mask = reb
    else:
        mask = brk | reb
    floor_arr = floor.to_numpy()
    ceil_arr = ceiling.to_numpy()
    close_arr = frame["Close"].to_numpy(dtype=float)
    return [
        SimpleSignal(
            ticker=ticker,
            date=frame.index[position],
            price=float(close_arr[position]),
        )
        for position in np.flatnonzero(mask.to_numpy())
        if _box_width_ok(ceil_arr[position], floor_arr[position], params.min_box_width)
    ]


# ── 백테스트 ──────────────────────────────────────────────────────────────────

def _parse_bound(name: str, value: pd.Timestamp | str | None) -> pd.Timestamp | None:
    if value is None:
        return None
    try:
        parsed = pd.Timestamp(value)
    except (TypeError, ValueError) as exc:
        raise ValueError(f"{name}은 유효한 timestamp여야 합니다") from exc
    if pd.isna(parsed):
        raise ValueError(f"{name}은 유효한 timestamp여야 합니다")
    return parsed


def _in_bounds(
    value: pd.Timestamp, start: pd.Timestamp | None, end: pd.Timestamp | None
) -> bool:
    return (start is None or value >= start) and (end is None or value <= end)


def _box_width_ok(ceiling: float, floor: float, min_box_width: float) -> bool:
    """(천장-바닥)/바닥이 min_box_width 이상인지. 0이면 항상 True."""

    if min_box_width <= 0.0:
        return True
    if not (np.isfinite(ceiling) and np.isfinite(floor)) or floor <= 0.0:
        return False
    return (ceiling - floor) / floor >= min_box_width


def _simulate_segment(
    frame: pd.DataFrame,
    signals: list[SimpleSignal],
    floor_by_date: dict[pd.Timestamp, float],
    params: DarvasParams,
    ticker: str,
) -> list[Trade]:
    """다바스 청산(ATR TP/SL + 박스 하단)을 포함한 종목별 트레이드 시뮬레이터.

    ``exit_floor``가 꺼져 있고 ``exit_atr_tp``/``exit_atr_sl``가 켜져 있으면
    ``engine.run_backtest``와 동일한 결과를 낸다(보수적 손절 우선).
    """

    if not signals or len(frame) < 2:
        return []

    high_arr = frame["High"].to_numpy(dtype=float)
    low_arr = frame["Low"].to_numpy(dtype=float)
    close_arr = frame["Close"].to_numpy(dtype=float)
    atr_arr = atr(
        frame["High"], frame["Low"], frame["Close"], window=params.atr_window
    ).to_numpy(dtype=float)
    date_to_pos = {ts: i for i, ts in enumerate(frame.index)}
    use_atr = (
        params.exit_atr_tp or params.exit_atr_sl or params.trail_atr is not None
    )
    max_hold = params.max_holding_bars

    trades: list[Trade] = []
    last_exit_idx = -1
    for sig in signals:
        if sig.ticker and ticker and sig.ticker != ticker:
            continue
        e = date_to_pos.get(sig.date)
        if e is None or e <= last_exit_idx or e >= len(frame) - 1:
            continue
        if use_atr and (not np.isfinite(atr_arr[e]) or atr_arr[e] <= 0):
            continue

        entry = sig.price
        tp = entry + params.tp_atr * atr_arr[e] if params.exit_atr_tp else None
        sl = entry - params.sl_atr * atr_arr[e] if params.exit_atr_sl else None
        floor = floor_by_date.get(sig.date) if params.exit_floor else None
        if floor is not None and not np.isfinite(floor):
            floor = None

        last_eval = len(frame) - 1
        if max_hold is not None:
            last_eval = min(last_eval, e + max_hold)

        trail_mult = params.trail_atr
        running_high = high_arr[e]
        exit_price: float | None = None
        reason = ""
        exit_idx = e
        for t in range(e + 1, last_eval + 1):
            stops: list[tuple[float, str]] = []
            if sl is not None and low_arr[t] <= sl:
                stops.append((sl, EXIT_SL))
            if floor is not None and low_arr[t] <= floor:
                stops.append((floor, EXIT_FLOOR))
            if trail_mult is not None:
                trail = running_high - trail_mult * atr_arr[e]
                if low_arr[t] <= trail:
                    stops.append((trail, EXIT_TRAIL))
            if stops:
                # 하락 중 먼저 닿는(=더 높은) 손절선으로 체결
                exit_price, reason = max(stops, key=lambda s: s[0])
                exit_idx = t
                break
            if tp is not None and high_arr[t] >= tp:
                exit_price, reason = tp, EXIT_TP
                exit_idx = t
                break
            if max_hold is not None and t - e >= max_hold:
                exit_price, reason = close_arr[t], EXIT_MAX_HOLD
                exit_idx = t
                break
            # 봉 종료 후 트레일 기준(러닝 하이) 갱신 — 같은 봉 내 룩어헤드 방지
            if high_arr[t] > running_high:
                running_high = high_arr[t]

        if exit_price is None:
            exit_price, reason, exit_idx = close_arr[-1], EXIT_END, len(frame) - 1

        gross = (exit_price / entry - 1.0) * 100.0
        net = gross - params.cost_rate * 200.0
        trades.append(
            Trade(
                ticker=sig.ticker or ticker,
                entry_date=sig.date,
                exit_date=frame.index[exit_idx],
                entry_price=entry,
                exit_price=float(exit_price),
                return_pct=round(net, 4),
                holding_bars=exit_idx - e,
                exit_reason=reason,
            )
        )
        last_exit_idx = exit_idx

    return trades


def _collect_trades(
    data: dict[str, pd.DataFrame],
    params: DarvasParams,
    mode: str,
    start_ts: pd.Timestamp | None,
    end_ts: pd.Timestamp | None,
) -> tuple[list, int]:
    all_trades: list = []
    signal_count = 0
    for ticker in sorted(data):
        frame = data[ticker]
        _validate_frame_layout(frame)
        valid_rows = _valid_ohlcv_rows(frame)
        for segment in _valid_segments(frame, valid_rows):
            brk, reb, floor, ceiling = darvas_masks_full(segment, params)
            if mode == BREAKOUT:
                mask = brk
            elif mode == REBOUND:
                mask = reb
            else:
                mask = brk | reb
            floor_arr = floor.to_numpy()
            ceil_arr = ceiling.to_numpy()
            observed = [
                (p, float(floor_arr[p]))
                for p in np.flatnonzero(mask.to_numpy())
                if _in_bounds(segment.index[p], start_ts, end_ts)
                and _box_width_ok(ceil_arr[p], floor_arr[p], params.min_box_width)
            ]
            signal_count += len(observed)
            signals = [
                SimpleSignal(
                    ticker=ticker,
                    date=segment.index[p],
                    price=float(segment["Close"].iloc[p]),
                )
                for p, _ in observed
            ]
            floor_by_date = {segment.index[p]: f for p, f in observed}
            trades = _simulate_segment(
                segment, signals, floor_by_date, params, ticker
            )
            all_trades.extend(
                trade
                for trade in trades
                if _in_bounds(trade.entry_date, start_ts, end_ts)
            )
    all_trades.sort(key=lambda t: (t.entry_date, t.ticker, t.exit_date))
    return all_trades, signal_count


def run_darvas_backtest(
    data: dict[str, pd.DataFrame] | None = None,
    params: DarvasParams = DARVAS_PARAMS,
    mode: str = COMBINED,
    start: pd.Timestamp | str | None = BASELINE_START,
    end: pd.Timestamp | str | None = BASELINE_END,
) -> dict[str, object]:
    """단일 모드(개별/결합)로 다바스 백테스트를 실행한다."""

    mode = _validate_mode(mode)
    _validate_params(params)
    data = load_all() if data is None else data
    start_ts = _parse_bound("start", start)
    end_ts = _parse_bound("end", end)
    if start_ts is not None and end_ts is not None and start_ts > end_ts:
        raise ValueError("start는 end보다 늦을 수 없습니다")

    all_trades, signal_count = _collect_trades(data, params, mode, start_ts, end_ts)
    performance = summarize(all_trades)
    return {
        "strategy": "DARVAS",
        "mode": mode,
        "params": params.as_dict(),
        "data_window_start": str(start_ts.date()) if start_ts is not None else None,
        "data_window_end": str(end_ts.date()) if end_ts is not None else None,
        "n_tickers": len(data),
        "n_signals": signal_count,
        "trades": [trade.to_dict() for trade in all_trades],
        **performance.to_dict(),
    }


def run_darvas_grid(
    confirm_days: tuple[int, ...] = (2, 3, 4, 5),
    modes: tuple[str, ...] = MODES,
    high_lookback: int = 60,
    min_box_width: float = 0.0,
    data: dict[str, pd.DataFrame] | None = None,
    start: pd.Timestamp | str | None = BASELINE_START,
    end: pd.Timestamp | str | None = BASELINE_END,
    min_trades: int = 20,
) -> pd.DataFrame:
    """confirm_days를 변주하며 모드별(개별+결합) 성과를 집계한다."""

    for mode in modes:
        _validate_mode(mode)
    data = load_all() if data is None else data
    start_ts = _parse_bound("start", start)
    end_ts = _parse_bound("end", end)
    if start_ts is not None and end_ts is not None and start_ts > end_ts:
        raise ValueError("start는 end보다 늦을 수 없습니다")

    rows: list[dict[str, object]] = []
    for cd in confirm_days:
        base = replace(
            DARVAS_PARAMS, confirm_days=cd, high_lookback=high_lookback,
            min_box_width=min_box_width,
        )
        _validate_params(base)
        for mode in modes:
            trades, signal_count = _collect_trades(
                data, base, mode, start_ts, end_ts
            )
            perf = summarize(trades)
            rows.append(
                {
                    "confirm_days": cd,
                    "high_lookback": high_lookback,
                    "min_box_width": min_box_width,
                    "mode": mode,
                    "n_signals": signal_count,
                    "n_tickers_hit": perf.tickers_hit,
                    "n_trades": perf.n_trades,
                    "n_win": perf.n_win,
                    "n_loss": perf.n_loss,
                    "win_rate": perf.win_rate,
                    "avg_return": perf.avg_return,
                    "cum_return": perf.cum_return,
                    "profit_factor": perf.profit_factor,
                    "max_drawdown": perf.max_drawdown,
                    "avg_holding_bars": perf.avg_holding_bars,
                    "meets_min_trades": perf.n_trades >= min_trades,
                }
            )
            print(
                f"confirm_days={cd} {mode:<8} | "
                f"시그널 {signal_count:>5} 거래 {perf.n_trades:>5} | "
                f"승률 {perf.win_rate * 100:5.1f}% | PF {perf.profit_factor:6.2f} | "
                f"평균 {perf.avg_return:+7.3f}% | 복리 {perf.cum_return:+9.1f}%"
            )
    return pd.DataFrame(rows)


# ── CLI ───────────────────────────────────────────────────────────────────────

def _format_result(result: dict[str, object]) -> str:
    return (
        f"[{result['mode']}] 시그널 {result['n_signals']} | 거래 {result['n_trades']} "
        f"({result['n_win']}승/{result['n_loss']}패) | "
        f"승률 {result['win_rate'] * 100:.1f}% | PF {result['profit_factor']:.2f} | "
        f"평균 {result['avg_return']:+.3f}% | 복리 {result['cum_return']:+.1f}% | "
        f"MDD {result['max_drawdown']:.2f}%"
    )


def main() -> None:
    parser = argparse.ArgumentParser(description="다바스 박스 전략 백테스트")
    parser.add_argument(
        "--confirm-days", type=int, nargs="+", default=[2, 3, 4, 5],
        help="상/하단 확정 일수 그리드 (기본: 2 3 4 5)",
    )
    parser.add_argument("--high-lookback", type=int, default=60)
    parser.add_argument(
        "--min-box-width", type=float, default=0.0,
        help="(천장-바닥)/바닥 최소 박스 폭 (기본 0=필터 없음)",
    )
    parser.add_argument("--min-trades", type=int, default=20)
    parser.add_argument("--start", default=BASELINE_START.date().isoformat())
    parser.add_argument("--end", default=BASELINE_END.date().isoformat())
    parser.add_argument(
        "--output", type=Path,
        default=RESULTS_DIR / "strategy_darvas_grid.csv",
    )
    args = parser.parse_args()

    grid = run_darvas_grid(
        confirm_days=tuple(args.confirm_days),
        high_lookback=args.high_lookback,
        min_box_width=args.min_box_width,
        start=args.start,
        end=args.end,
        min_trades=args.min_trades,
    )
    args.output.parent.mkdir(parents=True, exist_ok=True)
    grid.to_csv(args.output, index=False)
    print(f"\n저장: {args.output}")


if __name__ == "__main__":
    main()
