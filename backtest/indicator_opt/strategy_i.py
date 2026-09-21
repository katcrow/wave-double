"""전략 I(20일 박스권 돌파) 계산 및 재현 백테스트.

박스 정의 (당일 제외 직전 ``box_window``(기본 20)봉):
    box_top    = 직전 box_window봉 고가의 최댓값
    box_bottom = 직전 box_window봉 저가의 최솟값
    유효 박스(횡보 콘솔리데이션) 요건 (전부 충족 시에만 박스로 인정):
      1. 박스폭율: (box_top - box_bottom)/box_bottom <= box_width_ratio_max(기본 0.20)
      2. 정규화 slope: N봉 종가 선형회귀 기울기 × (N-1) ÷ 구간 평균 종가
         (= 구간 전체 드리프트 %), 절댓값 <= box_drift_max(기본 0.03)
      3. (선택 box_touches_required=True) 터치 검증:
         상단터치(고가 >= 상단 - 존산) >= box_touches_min(기본 2) 그리고
         하단터치(저가 <= 하단 + 존산) >= box_touches_min, 단 존산 = 박스폭 × box_touch_zone_pct(기본 0.20)
      4. 기간: N(= box_window) >= min_box_bars(기본 10)

진입 조건 (전부 만족):
    1. 종가가 box_top을 상향 돌파하고 box_top보다 높은 금액으로 마감
    2. (strict_cross=True 기본) 전일 종가는 어제 박스(bottom~top) 안에 정착 — 첫 돌파 봉만 신호
    3. (max_entry_over_top_pct 기본 +10%) 종가가 box_top 대비 이 %를 초과하면 추격 금지
    4. 당일 거래량 > 전일 거래량

청산:
    - 익절: 진입 종가 대비 take_profit_pct%(기본 4.0, 3~5% 범위) 수익
    - 손절: 매수일의 box_top 대비 stop_loss_pct%(기본 5.0) 아래로 하락
    - 최대보유 지정 시 해당 봉 종가 강제 청산 (기본 None = TP/SL만)
"""

from __future__ import annotations

import argparse
import hashlib
from dataclasses import asdict, dataclass
from numbers import Integral, Real
from pathlib import Path

import numpy as np
import pandas as pd

from ..data.loader import load_all
from ..engine import EXIT_MAX_HOLD, TradeParams, run_backtest
from ..metrics import summarize
from ._signals import SimpleSignal
from .run import RESULTS_DIR

_OHLCV_COLUMNS = ("Open", "High", "Low", "Close", "Volume")
_PRICE_COLUMNS = ("Open", "High", "Low", "Close")
_MAX_WINDOW = 100_000
_TRADE_COLUMNS = (
    "ticker", "entry_date", "exit_date", "entry_price", "exit_price",
    "return_pct", "holding_bars", "exit_reason",
)
BASELINE_START = pd.Timestamp("2020-08-03")
BASELINE_END = pd.Timestamp("2026-08-26")


@dataclass(frozen=True)
class StrategyIParams:
    """전략 I 후보 A의 진입·청산 파라미터."""

    box_window: int = 20                 # 박스 관측 window (봉)
    min_box_bars: int = 10               # 최소 콘솔리데이션 기간 N (봉)
    box_width_ratio_max: float = 0.20    # 박스폭율 (box_top-box_bottom)/box_bottom 상한
    box_drift_max: float = 0.03          # |정규화 slope| 상한 (종가 선형회귀 총 드리프트/평균종가)
    box_touch_zone_pct: float = 0.20     # 터치 존 = 박스폭의 이 비율
    box_touches_min: int = 2             # 상단/하단 각 최소 터치 수
    box_touches_required: bool = True    # 터치 조건 적용 여부 (False면 선택 해제)
    strict_cross: bool = True            # True: 전일 종가가 어제 박스 안에 정착 후 금일 상단 돌파
    max_entry_over_top_pct: float | None = 10.0  # 추격 금지: 진입 종가가 box_top 대비 이 % 초과 시 제외
    take_profit_pct: float = 4.0         # 익절: 진입 종가 대비 %
    stop_loss_pct: float = 5.0           # 손절: 매수일 box_top 대비 % 하락
    max_holding_bars: int | None = None  # None이면 TP/SL에만 의존
    cost_rate: float = 0.0005            # 편도 수수료+슬리피지

    def as_dict(self) -> dict[str, int | float | None]:
        return asdict(self)


STRATEGY_I_PARAMS = StrategyIParams()
CANDIDATE_A = STRATEGY_I_PARAMS


def _validate_finite_real(name: str, value: object) -> float:
    if isinstance(value, bool) or not isinstance(value, Real):
        raise ValueError(f"{name}은 유한한 실수여야 합니다")
    value = float(value)
    if not np.isfinite(value):
        raise ValueError(f"{name}은 유한한 실수여야 합니다")
    return value


def _validate_positive_integer(name: str, value: object) -> int:
    if isinstance(value, bool) or not isinstance(value, Integral):
        raise ValueError(f"{name}은 정수여야 합니다")
    value = int(value)
    if not 1 <= value <= _MAX_WINDOW:
        raise ValueError(f"{name}은 1~{_MAX_WINDOW} 범위여야 합니다")
    return value


def _validate_params(params: StrategyIParams) -> None:
    if not isinstance(params, StrategyIParams):
        raise ValueError("params는 StrategyIParams여야 합니다")
    _validate_positive_integer("box_window", params.box_window)
    _validate_positive_integer("min_box_bars", params.min_box_bars)
    if params.min_box_bars > params.box_window:
        raise ValueError("min_box_bars는 box_window보다 클 수 없습니다")

    max_entry_over_top_pct = params.max_entry_over_top_pct
    if max_entry_over_top_pct is not None:
        max_entry_over_top_pct = _validate_finite_real(
            "max_entry_over_top_pct", max_entry_over_top_pct
        )
        if not 0.0 < max_entry_over_top_pct <= 100.0:
            raise ValueError("max_entry_over_top_pct은 (0, 100] 범위여야 합니다")

    box_width_ratio_max = _validate_finite_real(
        "box_width_ratio_max", params.box_width_ratio_max
    )
    if not 0.0 < box_width_ratio_max <= 1.0:
        raise ValueError("box_width_ratio_max는 (0, 1] 범위여야 합니다")

    box_drift_max = _validate_finite_real("box_drift_max", params.box_drift_max)
    if not 0.0 < box_drift_max <= 1.0:
        raise ValueError("box_drift_max는 (0, 1] 범위여야 합니다")

    box_touch_zone_pct = _validate_finite_real(
        "box_touch_zone_pct", params.box_touch_zone_pct
    )
    if not 0.0 < box_touch_zone_pct < 1.0:
        raise ValueError("box_touch_zone_pct는 (0, 1) 범위여야 합니다")

    _validate_positive_integer("box_touches_min", params.box_touches_min)
    if not isinstance(params.box_touches_required, bool):
        raise ValueError("box_touches_required은 bool이어야 합니다")

    if not isinstance(params.strict_cross, bool):
        raise ValueError("strict_cross은 bool이어야 합니다")

    take_profit_pct = _validate_finite_real(
        "take_profit_pct", params.take_profit_pct
    )
    stop_loss_pct = _validate_finite_real("stop_loss_pct", params.stop_loss_pct)
    if not 0.0 < take_profit_pct <= 100.0:
        raise ValueError("take_profit_pct은 (0, 100] 범위여야 합니다")
    if not 0.0 < stop_loss_pct <= 100.0:
        raise ValueError("stop_loss_pct은 (0, 100] 범위여야 합니다")

    if params.max_holding_bars is not None:
        _validate_positive_integer(
            "max_holding_bars", params.max_holding_bars
        )

    cost_rate = _validate_finite_real("cost_rate", params.cost_rate)
    if not 0.0 <= cost_rate < 1.0:
        raise ValueError("cost_rate은 [0, 1) 범위여야 합니다")


def validate_strategy_i_params(params: StrategyIParams) -> None:
    """전략 I 파라미터 계약을 외부 검증 코드에서도 사용할 수 있게 노출한다."""

    _validate_params(params)


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


def _box_range(
    frame: pd.DataFrame, box_window: int
) -> tuple[pd.Series, pd.Series]:
    """직전(box_window)봉의 고가 최댓값/저가 최솟값 박스. 당일 봉은 제외한다."""

    box_top = frame["High"].shift(1).rolling(
        box_window, min_periods=box_window
    ).max()
    box_bottom = frame["Low"].shift(1).rolling(
        box_window, min_periods=box_window
    ).min()
    return box_top, box_bottom


def _box_analysis(
    frame: pd.DataFrame, params: StrategyIParams
) -> tuple[pd.Series, pd.Series, pd.Series]:
    """직전 box_window봉 박스의 상단/하단과 유효 박스 여부를 계산한다.

    i번 봉의 박스는 [i-box_window, i) 구간으로 정의하고, 유효 박스 요건
    (박스폭율·정규화 slope·터치 검증·최소 기간)을 모두 충족할 때만 True를
    반환한다. window가 불완전한 구간은 NaN/False로 둔다.
    """

    box_window = params.box_window
    n_rows = len(frame)
    if n_rows < box_window:
        index = frame.index
        nan = pd.Series(np.nan, index=index)
        return nan, nan, pd.Series(False, index=index)

    close = frame["Close"].to_numpy(dtype=float)
    high = frame["High"].to_numpy(dtype=float)
    low = frame["Low"].to_numpy(dtype=float)

    view = np.lib.stride_tricks.sliding_window_view
    high_w = view(high, box_window)
    low_w = view(low, box_window)
    close_w = view(close, box_window)

    top = high_w.max(axis=1)
    bottom = low_w.min(axis=1)
    width = top - bottom
    width_ratio = width / bottom

    x = np.arange(box_window, dtype=float)
    xm = x.mean()
    denom = float(((x - xm) ** 2).sum())
    mean_close = close_w.mean(axis=1)
    slope = ((x - xm)[None, :] * (close_w - mean_close[:, None])).sum(axis=1) / denom
    drift = slope * (box_window - 1) / mean_close

    width_ok = width_ratio <= params.box_width_ratio_max
    drift_ok = np.abs(drift) <= params.box_drift_max
    if params.box_touches_required:
        zone = params.box_touch_zone_pct * width
        top_zone = top - zone
        bottom_zone = bottom + zone
        top_touches = (high_w >= top_zone[:, None]).sum(axis=1)
        bottom_touches = (low_w <= bottom_zone[:, None]).sum(axis=1)
        touches_ok = (
            (top_touches >= params.box_touches_min)
            & (bottom_touches >= params.box_touches_min)
        )
    else:
        touches_ok = np.ones(len(width), dtype=bool)
    valid = width_ok & drift_ok & touches_ok

    index = frame.index
    top_s = pd.Series(np.nan, index=index)
    bottom_s = pd.Series(np.nan, index=index)
    valid_s = pd.Series(False, index=index)
    count = n_rows - box_window  # 오늘 인덱스 i = r+box_window에 대응하는 행 수
    top_s.iloc[box_window:] = top[:count]
    bottom_s.iloc[box_window:] = bottom[:count]
    valid_s.iloc[box_window:] = valid[:count]
    return top_s, bottom_s, valid_s


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


def _timezone_label(timezone: object) -> str | None:
    return None if timezone is None else str(timezone)


def _validate_bound_timezones(
    frame: pd.DataFrame,
    start: pd.Timestamp | None,
    end: pd.Timestamp | None,
) -> None:
    index_timezone = _timezone_label(frame.index.tz)
    for name, bound in (("start", start), ("end", end)):
        if bound is None:
            continue
        bound_timezone = _timezone_label(bound.tz)
        if bound_timezone != index_timezone:
            raise ValueError(
                f"{name}과 OHLCV 인덱스의 timezone이 일치하지 않습니다"
            )


def _validate_bound_pair_timezones(
    start: pd.Timestamp | None,
    end: pd.Timestamp | None,
) -> None:
    if start is not None and end is not None:
        if _timezone_label(start.tz) != _timezone_label(end.tz):
            raise ValueError("start와 end의 timezone이 일치하지 않습니다")


def _in_bounds(
    value: pd.Timestamp,
    start: pd.Timestamp | None,
    end: pd.Timestamp | None,
) -> bool:
    return (
        (start is None or value >= start)
        and (end is None or value <= end)
    )


def compute_strategy_i(
    frame: pd.DataFrame,
    params: StrategyIParams = STRATEGY_I_PARAMS,
) -> pd.Series:
    """전략 I 진입 조건(유효 박스권 돌파)을 동일 인덱스의 bool 마스크로 계산한다."""

    _validate_frame(frame)
    _validate_params(params)
    close = frame["Close"]
    volume = frame["Volume"]
    box_top, box_bottom, box_valid = _box_analysis(frame, params)

    # 1) 종가가 (유효 박스의) 상단을 돌파하고 상단보다 높은 금액으로 마감.
    #    strict_cross=True면 "전일 종가가 어제 박스(bottom~top) 안에 정착" 후 금일
    #    돌파한 교차 봉만 잡는다 — 추세 장세에서 매 신고가마다 반복 발화를 막는다.
    above_top = (close > box_top) & box_top.notna() & (box_top > 0)
    if params.strict_cross:
        prev_contained = (
            (close.shift(1) >= box_bottom.shift(1))
            & (close.shift(1) <= box_top.shift(1))
        ).fillna(False)
    else:
        prev_contained = pd.Series(True, index=frame.index)
    breakout = above_top & prev_contained
    # 추격 금지: 진입 종가가 박스상단 대비 max_entry_over_top_pct%를 초과하면 제외
    if params.max_entry_over_top_pct is not None:
        close_to_top = (
            close <= box_top * (1.0 + params.max_entry_over_top_pct / 100.0)
        ).fillna(False)
    else:
        close_to_top = pd.Series(True, index=frame.index)
    breakout = breakout & close_to_top
    # 2) 당일 거래량 > 전일 거래량
    volume_up = (volume > volume.shift(1)).fillna(False)

    mask = breakout & volume_up & box_valid.fillna(False)
    return mask.fillna(False).astype(bool)


def strategy_i_signals(
    frame: pd.DataFrame,
    ticker: str = "",
    params: StrategyIParams = STRATEGY_I_PARAMS,
) -> list[SimpleSignal]:
    """전략 I 마스크를 종가 진입용 신호로 변환한다.

    종가 진입, 익절은 진입 종가 대비 take_profit_pct%, 손절가는 매수일의
    (유효 박스의) box_top 대비 stop_loss_pct% 아래로 고정한다.
    """

    box_top, _, _ = _box_analysis(frame, params)
    mask = compute_strategy_i(frame, params)
    return [
        SimpleSignal(
            ticker=ticker,
            date=frame.index[position],
            price=float(frame["Close"].iloc[position]),
            take_profit_pct=params.take_profit_pct,
            stop_price=float(box_top.iloc[position] * (1.0 - params.stop_loss_pct / 100.0)),
        )
        for position in np.flatnonzero(mask.to_numpy())
    ]


def run_strategy_i_backtest(
    data: dict[str, pd.DataFrame] | None = None,
    params: StrategyIParams = STRATEGY_I_PARAMS,
    start: pd.Timestamp | str | None = BASELINE_START,
    end: pd.Timestamp | str | None = BASELINE_END,
) -> dict[str, object]:
    """고정 관측창의 parquet 유니버스에서 전략 I를 재현 실행한다."""

    data = load_all() if data is None else data
    _validate_params(params)
    start_ts = _parse_bound("start", start)
    end_ts = _parse_bound("end", end)
    _validate_bound_pair_timezones(start_ts, end_ts)
    if start_ts is not None and end_ts is not None and start_ts > end_ts:
        raise ValueError("start는 end보다 늦을 수 없습니다")

    trade_params = TradeParams(
        cost_rate=params.cost_rate,
        max_holding_bars=params.max_holding_bars,
    )
    all_trades = []
    signal_count = 0
    digest = hashlib.sha256()
    n_tickers = 0
    invalid_ohlcv_rows = 0
    months = set()
    for ticker in sorted(data):
        frame = data[ticker]
        _validate_frame_layout(frame)
        _validate_bound_timezones(frame, start_ts, end_ts)
        valid_rows = _valid_ohlcv_rows(frame)
        invalid_ohlcv_rows += int((~valid_rows).sum())
        ticker_bytes = ticker.encode("utf-8")
        digest.update(len(ticker_bytes).to_bytes(4, "big"))
        digest.update(ticker_bytes)
        digest.update(pd.util.hash_pandas_object(frame, index=True).to_numpy().tobytes())

        observed_rows = valid_rows.copy()
        if start_ts is not None:
            observed_rows &= frame.index >= start_ts
        if end_ts is not None:
            observed_rows &= frame.index <= end_ts
        if observed_rows.any():
            n_tickers += 1
            months.update(frame.index[observed_rows].to_period("M"))

        for segment in _valid_segments(frame, valid_rows):
            signals = strategy_i_signals(segment, ticker=ticker, params=params)
            observed_signals = [
                signal
                for signal in signals
                if _in_bounds(signal.date, start_ts, end_ts)
            ]
            signal_count += len(observed_signals)
            segment_trades = run_backtest(
                segment, observed_signals, trade_params, ticker=ticker
            )
            all_trades.extend(
                trade
                for trade in segment_trades
                if _in_bounds(trade.entry_date, start_ts, end_ts)
            )

    all_trades.sort(
        key=lambda trade: (trade.entry_date, trade.ticker, trade.exit_date)
    )

    performance = summarize(all_trades)
    result = {
        "strategy": "I",
        "params": params.as_dict(),
        "data_window_start": str(start_ts.date()) if start_ts is not None else None,
        "data_window_end": str(end_ts.date()) if end_ts is not None else None,
        "n_tickers": n_tickers,
        "invalid_ohlcv_rows": invalid_ohlcv_rows,
        "data_fingerprint": digest.hexdigest(),
        "n_signals": signal_count,
        "monthly_frequency": round(len(all_trades) / len(months), 4) if months else 0.0,
        "trades": [trade.to_dict() for trade in all_trades],
        **performance.to_dict(),
    }
    result["max_hold_exits"] = sum(
        1 for trade in all_trades if trade.exit_reason == EXIT_MAX_HOLD
    )
    return result


def _baseline_row(result: dict[str, object]) -> dict[str, object]:
    """결과 CSV에 성과와 전략 파라미터를 함께 평탄화한다."""

    params = result["params"]
    if not isinstance(params, dict):
        raise ValueError("baseline 결과의 params가 dict가 아닙니다")
    row = {key: value for key, value in result.items() if key not in {"params", "trades"}}
    row.update({f"param_{key}": value for key, value in params.items()})
    return row


def _format_result(result: dict[str, object]) -> str:
    return (
        f"전략 I | 시그널 {result['n_signals']} | 거래 {result['n_trades']} "
        f"({result['n_win']}승/{result['n_loss']}패) | "
        f"승률 {result['win_rate'] * 100:.1f}% | PF {result['profit_factor']:.2f} | "
        f"평균 {result['avg_return']:+.3f}% | 복리 {result['cum_return']:+.1f}% | "
        f"최대보유 청산 {result['max_hold_exits']}건"
    )


def main() -> None:
    parser = argparse.ArgumentParser(description="전략 I(20일 박스권 돌파) baseline 백테스트")
    parser.add_argument(
        "--output", type=Path,
        default=RESULTS_DIR / "strategy_i_baseline.csv",
        help="요약 CSV 출력 경로",
    )
    parser.add_argument("--start", default=BASELINE_START.date().isoformat())
    parser.add_argument("--end", default=BASELINE_END.date().isoformat())
    args = parser.parse_args()
    result = run_strategy_i_backtest(start=args.start, end=args.end)
    print("=== 전략 I(20일 박스권 돌파) 후보 A ===")
    print(f"관측창: {result['data_window_start']} ~ {result['data_window_end']}")
    print(f"파라미터: {result['params']}")
    print(_format_result(result))
    args.output.parent.mkdir(parents=True, exist_ok=True)
    pd.DataFrame([_baseline_row(result)]).to_csv(args.output, index=False)
    trades_output = args.output.with_name(f"{args.output.stem}_trades.csv")
    pd.DataFrame(result["trades"], columns=_TRADE_COLUMNS).to_csv(
        trades_output, index=False
    )
    print(f"저장: {args.output}")
    print(f"거래 상세 저장: {trades_output}")


if __name__ == "__main__":
    main()