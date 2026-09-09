"""후보별 좋은 수급 힌트의 순수 판정 규칙."""

from __future__ import annotations

import math
from decimal import Decimal, InvalidOperation
from enum import StrEnum
from typing import TypeAlias


class SupplyHintStatus(StrEnum):
    """저장·전송에 사용하는 안정적인 힌트 상태 코드."""

    GOOD = "good"
    NOT_MET = "not_met"
    UNDETERMINED = "undetermined"


Numeric: TypeAlias = int | float | Decimal


def _is_finite(value: Numeric) -> bool:
    try:
        if isinstance(value, Decimal):
            return value.is_finite()
        if isinstance(value, int):
            return True
        return math.isfinite(value)
    except (InvalidOperation, OverflowError, TypeError, ValueError):
        return False


def compute_supply_hint(
    batch_kind: str,
    investor_net_status: str,
    foreign_net: Numeric | None,
    institution_net: Numeric | None,
    individual_net: Numeric | None,
    program_net: Numeric | None,
    slot: str = "D0",
) -> SupplyHintStatus:
    """close 확정 D0의 외인·기관·프로그램 순매수만 엄격하게 판정한다.

    개인 순매수는 행의 confirmed 상태 정합성에 필요한 값이지만 힌트 임계값에는
    포함하지 않는다. 장중 행, 미확정/미수집 행, 미완성 confirmed 행은 모두
    ``undetermined``로 보존한다.
    """

    if slot != "D0" or batch_kind != "close" or investor_net_status != "confirmed":
        return SupplyHintStatus.UNDETERMINED

    values = (foreign_net, institution_net, individual_net, program_net)
    if any(value is None or not _is_finite(value) for value in values):
        return SupplyHintStatus.UNDETERMINED

    try:
        if foreign_net > 0 and institution_net > 0 and program_net > 0:
            return SupplyHintStatus.GOOD
    except (InvalidOperation, TypeError, ValueError):
        return SupplyHintStatus.UNDETERMINED
    return SupplyHintStatus.NOT_MET


__all__ = ["SupplyHintStatus", "compute_supply_hint"]
