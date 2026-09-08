import csv
from decimal import Decimal
from pathlib import Path

from domain.supply_hint import SupplyHintStatus, compute_supply_hint


FIXTURE = Path(__file__).parents[1] / "fixtures" / "supply_hint_cases.csv"


def _number(value: str) -> Decimal | None:
    return Decimal(value) if value.strip() else None


def test_shared_fixture_covers_every_supply_hint_boundary():
    with FIXTURE.open(newline="", encoding="utf-8") as stream:
        cases = list(csv.DictReader(stream))

    assert len(cases) == 7
    for case in cases:
        actual = compute_supply_hint(
            case["batch_kind"].strip(),
            case["investor_net_status"],
            _number(case["foreign_net"]),
            _number(case["institution_net"]),
            _number(case["individual_net"]),
            _number(case["program_net"]),
        )
        assert actual is SupplyHintStatus(case["expected"]), case["case_id"]


def test_individual_net_does_not_change_the_hint_threshold():
    assert compute_supply_hint("close", "confirmed", 1, 1, -999, 1) is SupplyHintStatus.GOOD


def test_unknown_status_or_batch_kind_is_undetermined():
    assert compute_supply_hint("close", "unexpected", 1, 1, 1, 1) is SupplyHintStatus.UNDETERMINED
    assert compute_supply_hint("premarket", "confirmed", 1, 1, 1, 1) is SupplyHintStatus.UNDETERMINED
