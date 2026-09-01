from math import inf, nan

from domain.candidate_selection import select_candidates


def test_sorts_by_trading_value_then_ticker_and_normalizes_values():
    result = select_candidates([
        {"ticker": "002", "name": "B", "trading_value": "10"},
        {"ticker": "001", "name": "A", "trading_value": 10},
        {"ticker": "003", "trading_value": 20},
    ])
    assert [c.ticker for c in result.candidates] == ["003", "001", "002"]
    assert result.candidates[1].trading_value == 10.0


def test_excludes_missing_and_nonfinite_values_and_empty_is_successful_selection():
    result = select_candidates([{"ticker": "001", "trading_value": nan}, {"ticker": "002", "trading_value": inf}, {"trading_value": 1}])
    assert result.candidates == ()
    assert result.original_count == 3
    assert result.excluded_count == 3
    assert select_candidates([]).metadata["candidate_count"] == 0


def test_caps_at_150_and_reports_truncated_count():
    result = select_candidates([{"ticker": f"{i:03d}", "trading_value": i} for i in range(151)])
    assert len(result.candidates) == 150
    assert result.candidates[0].ticker == "150"
    assert result.truncated_count == 1
    assert result.candidates[-1].ticker == "001"
    assert [c.ticker for c in result.truncated_candidates] == ["000"]


def test_hash_and_selection_are_independent_of_input_order():
    first = [{"ticker": "002", "trading_value": 2}, {"ticker": "001", "trading_value": 1}]
    second = list(reversed(first))
    left, right = select_candidates(first), select_candidates(second)
    assert left.selection_input_hash == right.selection_input_hash
    assert left.candidates == right.candidates


def test_supports_t1859_shape_and_deduplicates_ticker():
    result = select_candidates([
        {"shcode": "000001", "hname": "A", "price": 100, "volume": 5},
        {"shcode": "000001", "hname": "A", "price": 90, "volume": 5},
    ])
    assert [(c.ticker, c.name, c.trading_value) for c in result.candidates] == [("000001", "A", 500.0)]
    assert result.excluded_count == 1
