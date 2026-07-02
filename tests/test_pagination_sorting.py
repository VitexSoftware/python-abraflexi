"""
Tests for pagination, sorting and listing helpers on ReadOnly.
"""

import json
from unittest.mock import MagicMock

from python_abraflexi import ReadOnly


def _fake_response(payload, status_code=200):
    response = MagicMock()
    response.status_code = status_code
    response.content = json.dumps(payload).encode("utf-8")
    response.json.return_value = payload
    return response


def _client(**overrides):
    options = {
        "url": "https://demo.flexibee.eu",
        "company": "demo",
        "evidence": "cenik",
        "offline": False,
        "autoload": False,
    }
    options.update(overrides)
    return ReadOnly(None, options)


class TestListingSetters:
    def test_set_limit_and_start(self):
        ro = _client()
        ro.set_limit(50)
        ro.set_start(10)
        assert ro.default_url_params["limit"] == 50
        assert ro.default_url_params["start"] == 10

    def test_set_order_default_ascending(self):
        ro = _client()
        ro.set_order("nazev")
        assert ro.default_url_params["order"] == "nazev@A"

    def test_set_order_descending(self):
        ro = _client()
        ro.set_order("nazev", "D")
        assert ro.default_url_params["order"] == "nazev@D"

    def test_set_add_row_count_toggle(self):
        ro = _client()
        ro.set_add_row_count(True)
        assert ro.default_url_params["add-row-count"] == "true"
        ro.set_add_row_count(False)
        assert "add-row-count" not in ro.default_url_params

    def test_set_detail_relations_includes(self):
        ro = _client()
        ro.set_detail("custom:kod,nazev")
        ro.set_relations("polozkyFaktury", "prilohy")
        ro.set_includes("faktura-vydana/stredisko")
        assert ro.default_url_params["detail"] == "custom:kod,nazev"
        assert ro.default_url_params["relations"] == "polozkyFaktury,prilohy"
        assert ro.default_url_params["includes"] == "faktura-vydana/stredisko"

    def test_limit_start_order_appear_in_request_url(self):
        ro = _client()
        ro.set_limit(50)
        ro.set_start(10)
        ro.set_order("nazev", "D")
        ro.session.get = MagicMock(
            return_value=_fake_response(
                {"winstrom": {"success": "true", "results": []}}
            )
        )
        ro.perform_request()
        called_url = ro.session.get.call_args.args[0]
        assert "limit=50" in called_url
        assert "start=10" in called_url
        assert "order=nazev%40D" in called_url


class TestLoadFromAbraflexiParamsBug:
    def test_params_are_merged_into_default_url_params(self):
        ro = _client(offline=True)
        ro.load_from_abraflexi(123, params={"detail": "full"})
        assert ro.default_url_params["detail"] == "full"


class TestIterateAll:
    def test_pages_through_results_until_short_page(self):
        ro = _client()
        pages = [
            [{"id": "1"}, {"id": "2"}],
            [{"id": "3"}],
        ]
        calls = []

        def fake_get_all(params=None):
            calls.append(dict(ro.default_url_params))
            return pages.pop(0) if pages else []

        ro.get_all_from_abraflexi = fake_get_all

        records = list(ro.iterate_all(page_size=2))

        assert [r["id"] for r in records] == ["1", "2", "3"]
        assert calls[0]["start"] == 0
        assert calls[0]["limit"] == 2
        assert calls[1]["start"] == 2
        assert calls[1]["limit"] == 2

    def test_stops_immediately_on_empty_first_page(self):
        ro = _client()
        ro.get_all_from_abraflexi = lambda params=None: []
        assert list(ro.iterate_all(page_size=10)) == []
