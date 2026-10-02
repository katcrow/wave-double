from apps.batch.ls_client import LsResponse
from apps.batch.theme_enrichment import enrich_candidate_themes, parse_theme_response


def test_parse_theme_response_sorts_by_average_change_and_deduplicates_code():
    result = parse_theme_response(LsResponse(data={
        "t1532OutBlock": [
            {"tmcode": "002", "tmname": "전고체", "avgdiff": "2.20"},
            {"tmcode": "001", "tmname": "반도체", "avgdiff": "4.80"},
            {"tmcode": "001", "tmname": "반도체(중복)", "avgdiff": "4.80"},
        ],
    }))
    assert [(theme.theme_code, theme.theme_name) for theme in result] == [
        ("001", "반도체(중복)"),
        ("002", "전고체"),
    ]


def test_enrichment_isolates_failed_ticker_and_keeps_empty_ticker():
    class FakeThemeClient:
        def request(self, tr_code, params):
            assert tr_code == "t1532"
            ticker = params["t1532InBlock"]["shcode"]
            if ticker == "000002":
                raise RuntimeError("temporary LS failure")
            if ticker == "000003":
                return LsResponse(data={"t1532OutBlock": []})
            return LsResponse(data={"t1532OutBlock": [{"tmcode": "001", "tmname": "반도체", "avgdiff": 3.1}]})

    result = enrich_candidate_themes(["000001", "000002", "000003"], FakeThemeClient())

    assert result.requested_count == 3
    assert result.success_count == 1
    assert result.empty_count == 1
    assert result.failed_count == 1
    assert result.themes_by_ticker["000001"][0].theme_name == "반도체"


def test_non_ok_response_is_counted_as_failure_not_empty_source():
    class FailedThemeClient:
        def request(self, tr_code, params):
            return LsResponse(result_code="HTTP_ERROR")

    result = enrich_candidate_themes(["000001"], FailedThemeClient())

    assert result.empty_count == 0
    assert result.failed_count == 1
    assert result.failed_tickers == ("000001",)


def test_malformed_theme_row_and_provider_error_code_are_candidate_failures():
    class MalformedThemeClient:
        def request(self, tr_code, params):
            ticker = params["t1532InBlock"]["shcode"]
            if ticker == "000001":
                return LsResponse(data={"rsp_cd": "00000", "t1532OutBlock": [{"tmcode": "001", "tmname": None, "avgdiff": 1}]})
            return LsResponse(data={"rsp_cd": "00123", "t1532OutBlock": []})

    result = enrich_candidate_themes(["000001", "000002"], MalformedThemeClient())

    assert result.empty_count == 0
    assert result.failed_count == 2


def test_malformed_success_response_is_failure_not_authoritative_empty_source():
    class MalformedThemeClient:
        def request(self, tr_code, params):
            return LsResponse(data={"unexpected": []})

    result = enrich_candidate_themes(["000001"], MalformedThemeClient())

    assert result.empty_count == 0
    assert result.failed_count == 1
