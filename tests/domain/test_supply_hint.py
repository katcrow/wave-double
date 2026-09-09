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


def test_sql_fixture_shared_cases_match_csv():
    with FIXTURE.open(newline="", encoding="utf-8") as stream:
        cases = list(csv.DictReader(stream))

    sql = SQL_FIXTURE.read_text(encoding="utf-8")
    start = "-- SHARED_SUPPLY_HINT_FIXTURE_BEGIN\n"
    end = "-- SHARED_SUPPLY_HINT_FIXTURE_END\n"
    assert start in sql and end in sql
    block = sql.split(start, 1)[1].split(end, 1)[0]
    sql_cases = [line[3:].split("|") for line in block.splitlines() if line.startswith("-- ")]
    csv_cases = [
        [
            case["case_id"], case["batch_kind"], case["slot"], case["investor_net_status"],
            case["foreign_net"], case["institution_net"], case["individual_net"],
            case["program_net"], case["expected"],
        ]
        for case in cases
    ]
    assert sql_cases == csv_cases


def test_individual_net_does_not_change_the_hint_threshold():
    assert compute_supply_hint("close", "confirmed", 1, 1, -999, 1) is SupplyHintStatus.GOOD


def test_unknown_status_or_batch_kind_is_undetermined():
    assert compute_supply_hint("close", "unexpected", 1, 1, 1, 1) is SupplyHintStatus.UNDETERMINED
    assert compute_supply_hint("premarket", "confirmed", 1, 1, 1, 1) is SupplyHintStatus.UNDETERMINED


def test_decimal_and_non_finite_inputs_are_undetermined():
    assert compute_supply_hint("close", "confirmed", Decimal("NaN"), Decimal("1"), Decimal("1"), Decimal("1")) is SupplyHintStatus.UNDETERMINED
    assert compute_supply_hint("close", "confirmed", Decimal("Infinity"), Decimal("1"), Decimal("1"), Decimal("1")) is SupplyHintStatus.UNDETERMINED
    assert compute_supply_hint("close", "confirmed", float("nan"), 1, 1, 1) is SupplyHintStatus.UNDETERMINED
    assert compute_supply_hint("close", "confirmed", float("inf"), 1, 1, 1) is SupplyHintStatus.UNDETERMINED
