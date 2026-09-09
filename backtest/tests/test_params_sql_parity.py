"""backtest 파라미터와 SQL outcome_strategy_rules의 parity를 회귀망으로 고정한다.

epic-6 회고 F2: TP/SL/cutoff 파라미터가 Python dataclass, `_STRATEGY_PARAMS`,
SQL `outcome_strategy_rules`에 각각 존재하며 상호 연결 테스트가 없었다.
이 모듈은 운영 SQL 규칙의 기대값을 문서화된 fixture로 고정해 Python 쪽 파라미터가
그 계약과 어긋나면 즉시 드리프트를 드러낸다.

SQL 기대값은 운영 `public.outcome_strategy_rules`(tp_pct/sl_pct/cutoff_n)를
2026-09-09에 조회한 실제 값에서 가져왔다. SQL 스키마가 바뀌면 이 파일의
SQL_RULES도 함께 갱신해야 한다.
"""

from __future__ import annotations

from backtest.strategy_api import _STRATEGY_PARAMS

# 운영 public.outcome_strategy_rules 기대 계약 (strategy -> (tp_pct, sl_pct, cutoff_n))
# cutoff_n=999999는 Python의 max_holding_bars=None(무기한)에 대응한다.
SQL_RULES: dict[str, tuple[float, float, int]] = {
    "A": (3.0, 3.0, 30),
    "B": (3.0, 3.0, 30),
    "C": (3.0, 3.0, 30),
    "D": (3.0, 5.0, 20),
    "E": (2.0, 5.0, 30),
    "F": (3.0, 4.0, 999999),
}

_SQL_UNBOUNDED_CUTOFF = 999999


def _tp_sl_cutoff(
    params: dict[str, int | float | bool | None],
) -> tuple[float, float, int]:
    tp = float(params["take_profit_pct"])
    sl = float(params["stop_loss_pct"])
    max_holding = params.get("max_holding_bars")
    cutoff = _SQL_UNBOUNDED_CUTOFF if max_holding is None else int(max_holding)
    return tp, sl, cutoff


def test_all_strategies_have_expected_sql_parity() -> None:
    expected_keys = set(SQL_RULES)
    actual_keys = set(_STRATEGY_PARAMS)
    assert actual_keys == expected_keys, f"전략 키 불일치: {actual_keys ^ expected_keys}"

    for strategy, expected in SQL_RULES.items():
        _tp, _sl, cutoff = _tp_sl_cutoff(_STRATEGY_PARAMS[strategy])
        assert strategy in _STRATEGY_PARAMS
        assert _tp == expected[0], f"{strategy} tp 불일치: {_tp} != {expected[0]}"
        assert _sl == expected[1], f"{strategy} sl 불일치: {_sl} != {expected[1]}"
        assert cutoff == expected[2], f"{strategy} cutoff 불일치: {cutoff} != {expected[2]}"


def test_d_e_f_params_come_from_their_dataclasses() -> None:
    from backtest.indicator_opt.strategy_d import STRATEGY_D_PARAMS
    from backtest.indicator_opt.strategy_e import STRATEGY_E_PARAMS
    from backtest.indicator_opt.strategy_f import STRATEGY_F_PARAMS

    assert _STRATEGY_PARAMS["D"] == STRATEGY_D_PARAMS.as_dict()
    assert _STRATEGY_PARAMS["E"] == STRATEGY_E_PARAMS.as_dict()
    assert _STRATEGY_PARAMS["F"] == STRATEGY_F_PARAMS.as_dict()
