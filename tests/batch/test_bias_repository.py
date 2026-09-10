from datetime import date
from uuid import uuid4

import pytest

from apps.batch.bias_metrics import compute_bias_metrics
from apps.batch.bias_repository import SupabaseBiasRepository
from apps.batch.run_state import RunStateError


class Rpc:
    def __init__(self, replies):
        self.replies = iter(replies)
        self.calls = []

    def rpc(self, name, params):
        self.calls.append((name, params))
        return next(self.replies)


def test_population_unwraps_envelope_and_preserves_canonical_contributions():
    rpc = Rpc([{"data": [{"ticker": "005930", "strategies": ["A", "F"],
                          "sources": [{"source": "t1859", "weight": 2}]}]}])
    rows = SupabaseBiasRepository(rpc).fetch_population("run", 7, "lease")
    assert rows[0].strategies == ("A", "F")
    assert rows[0].sources[0].weight == 2
    assert rpc.calls[0] == ("get_bias_population", {
        "p_run_id": "run", "p_fence_token": 7, "p_lease_token": "lease"})


def test_as_rows_keys_match_append_sql_recordset_contract():
    from apps.batch.bias_metrics import SourceBiasMetrics
    metrics = compute_bias_metrics(date(2026, 9, 10), [], None)
    assert metrics.as_rows()[0] == {
        "source": "t1859",
        "candidate_pop_signal_count": 0,
        "backtest_universe_signal_count": 0,
        "intersection_count": 0,
        "diff_count": 0,
        "missed_opportunity_count": 0,
    }
    # 202609100200 append_bias_event의 jsonb_to_recordset 컬럼과 정확히 일치해야 한다.
    assert set(SourceBiasMetrics("t1852", 0, 0, 0, 0, 0).as_dict()) == {
        "source", "candidate_pop_signal_count", "backtest_universe_signal_count",
        "intersection_count", "diff_count", "missed_opportunity_count",
    }


def test_transport_retry_preserves_event_uuid_and_payload():
    rpc = Rpc([{"error": {"code": "NETWORK", "retryable": True}}, {"data": {"replayed": True}}])
    event = uuid4()
    result = SupabaseBiasRepository(rpc).append("run", 1, "lease", event,
                                             compute_bias_metrics(date(2026, 9, 10), [], None), "partial")
    assert result == {"replayed": True}
    assert rpc.calls[0] == rpc.calls[1]
    assert rpc.calls[0][1]["p_event_id"] == str(event)
    assert len(rpc.calls[0][1]["p_rows"]) == 3


def test_nonretryable_append_error_is_not_retried():
    rpc = Rpc([{"error": {"code": "INVALID_BIAS", "retryable": False}}])
    with pytest.raises(RunStateError):
        SupabaseBiasRepository(rpc).append("run", 1, "lease", uuid4(),
                                          compute_bias_metrics(date(2026, 9, 10), [], None), "partial")
    assert len(rpc.calls) == 1
