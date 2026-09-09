import csv
from decimal import Decimal
from pathlib import Path

from domain.supply_hint import SupplyHintStatus, compute_supply_hint


FIXTURE = Path(__file__).parents[1] / "fixtures" / "supply_hint_cases.csv"
SQL_FIXTURE = Path(__file__).parents[1] / "sql" / "test_supply_hints.sql"


def _number(value: str) -> Decimal | None:
    return Decimal(value) if value.strip() else None


def test_shared_fixture_covers_every_supply_hint_boundary():
    with FIXTURE.open(newline="", encoding="utf-8") as stream:
        cases = list(csv.DictReader(stream))

    assert len(cases) == 10
    for case in cases:
        actual = compute_supply_hint(
            case["batch_kind"].strip(),
            case["investor_net_status"],
            _number(case["foreign_net"]),
            _number(case["institution_net"]),
            _number(case["individual_net"]),
            _number(case["program_net"]),
            case["slot"],
        )
        assert actual is SupplyHintStatus(case["expected"]), case["case_id"]


def test_slot_is_required_at_call_sites():
    assert compute_supply_hint("close", "confirmed", 1, 1, 1, 1, "D0") is SupplyHintStatus.GOOD


def test_sql_fixture_loads_the_csv_with_psql():
    with FIXTURE.open(newline="", encoding="utf-8") as stream:
        fieldnames = csv.DictReader(stream).fieldnames

    sql = SQL_FIXTURE.read_text(encoding="utf-8")
    assert "\\copy supply_hint_fixture" in sql
    assert "tests/fixtures/supply_hint_cases.csv" in sql
    assert fieldnames == [
        "case_id", "batch_kind", "slot", "investor_net_status", "foreign_net",
        "institution_net", "individual_net", "program_net", "expected",
    ]


def test_individual_net_does_not_change_the_hint_threshold():
    assert compute_supply_hint("close", "confirmed", 1, 1, -999, 1, "D0") is SupplyHintStatus.GOOD


def test_unknown_status_or_batch_kind_is_undetermined():
    assert compute_supply_hint("close", "unexpected", 1, 1, 1, 1, "D0") is SupplyHintStatus.UNDETERMINED
    assert compute_supply_hint("premarket", "confirmed", 1, 1, 1, 1, "D0") is SupplyHintStatus.UNDETERMINED


def test_decimal_and_non_finite_inputs_are_undetermined():
    assert compute_supply_hint("close", "confirmed", Decimal("NaN"), Decimal("1"), Decimal("1"), Decimal("1"), "D0") is SupplyHintStatus.UNDETERMINED
    assert compute_supply_hint("close", "confirmed", Decimal("Infinity"), Decimal("1"), Decimal("1"), Decimal("1"), "D0") is SupplyHintStatus.UNDETERMINED
    assert compute_supply_hint("close", "confirmed", float("nan"), 1, 1, 1, "D0") is SupplyHintStatus.UNDETERMINED
    assert compute_supply_hint("close", "confirmed", float("inf"), 1, 1, 1, "D0") is SupplyHintStatus.UNDETERMINED
