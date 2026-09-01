from math import inf, nan

from domain.candidate_selection import merge_candidate_sources, select_candidates


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


def test_merge_single_source_matches_select_candidates_with_full_weight():
    result = merge_candidate_sources({"t1859": [{"ticker": "001", "trading_value": 10}]})
    assert len(result.candidates) == 1
    candidate = result.candidates[0]
    assert candidate.ticker == "001" and candidate.trading_value == 10.0
    assert [s.source for s in candidate.sources] == ["t1859"]
    assert [s.weight for s in candidate.sources] == [1.0]


def test_merge_takes_max_value_and_primary_matches_max_source():
    result = merge_candidate_sources({
        "t1859": [{"ticker": "001", "trading_value": 100}],
        "t1856": [{"ticker": "001", "trading_value": 200}],
    })
    assert len(result.candidates) == 1
    candidate = result.candidates[0]
    assert candidate.trading_value == 200.0
    assert [s.source for s in candidate.sources] == ["t1856"]
    assert sum(s.weight for s in candidate.sources) == 1.0


def test_merge_equal_values_split_weight_and_priority_breaks_primary_tie():
    result = merge_candidate_sources({
        "t1856": [{"ticker": "001", "trading_value": 100}],
        "t1859": [{"ticker": "001", "trading_value": 100}],
    })
    candidate = result.candidates[0]
    contributors = {s.source: s.weight for s in candidate.sources}
    assert contributors == {"t1859": 0.5, "t1856": 0.5}
    assert sum(contributors.values()) == 1.0
    # t1859 > t1852 > t1856 우선순위이므로 동률이면 t1859가 primary(첫 기여자)여야 한다.
    assert candidate.sources[0].source == "t1859"


def test_merge_invalid_value_in_one_source_does_not_exclude_the_ticker():
    result = merge_candidate_sources({
        "t1859": [{"ticker": "001", "trading_value": nan}],
        "t1856": [{"ticker": "001", "trading_value": 50}],
    })
    assert len(result.candidates) == 1
    candidate = result.candidates[0]
    assert candidate.trading_value == 50.0
    assert [s.source for s in candidate.sources] == ["t1856"]
    assert result.excluded_count == 1


def test_merge_all_sources_invalid_excludes_the_ticker():
    result = merge_candidate_sources({
        "t1859": [{"ticker": "001", "trading_value": nan}],
        "t1856": [{"ticker": "001", "trading_value": inf}],
    })
    assert result.candidates == ()
    assert result.excluded_count == 2


def test_merge_hash_is_independent_of_source_iteration_order():
    left = merge_candidate_sources({
        "t1859": [{"ticker": "001", "trading_value": 1}],
        "t1856": [{"ticker": "002", "trading_value": 2}],
    })
    right = merge_candidate_sources({
        "t1856": [{"ticker": "002", "trading_value": 2}],
        "t1859": [{"ticker": "001", "trading_value": 1}],
    })
    assert left.selection_input_hash == right.selection_input_hash


def test_merge_deduplicates_repeated_ticker_within_a_single_source():
    result = merge_candidate_sources({
        "t1859": [
            {"ticker": "001", "trading_value": 100},
            {"ticker": "001", "trading_value": 500},
        ],
    })
    assert len(result.candidates) == 1
    candidate = result.candidates[0]
    assert candidate.trading_value == 500.0
    assert [s.source for s in candidate.sources] == ["t1859"]
    assert [s.weight for s in candidate.sources] == [1.0]
    assert result.excluded_count == 1


def test_merge_excludes_cross_source_losing_contribution_from_excluded_count():
    result = merge_candidate_sources({
        "t1859": [{"ticker": "001", "trading_value": 100}],
        "t1856": [{"ticker": "001", "trading_value": 200}],
    })
    assert result.original_count == 2
    assert result.excluded_count == 1
    assert len(result.candidates) + result.excluded_count + result.truncated_count == result.original_count
