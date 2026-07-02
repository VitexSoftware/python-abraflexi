"""
Regression tests for response-body unwrapping and filter-based conditions.

AbraFlexi wraps write-operation responses (create/update/delete/actions)
under the generic "results" key, but wraps plain read/listing responses
under the evidence or sub-resource name itself (e.g. "adresar", "priloha",
"zmeny") instead. _parse_response_body must unwrap both shapes.
"""

import json
from unittest.mock import MagicMock

from python_abraflexi import ReadOnly
from python_abraflexi.evidences.adresar import Adresar


def _fake_response(payload, status_code=200):
    response = MagicMock()
    response.status_code = status_code
    response.content = json.dumps(payload).encode("utf-8")
    response.json.return_value = payload
    return response


def _base_options(**overrides):
    options = {
        "url": "https://demo.flexibee.eu",
        "company": "demo",
        "user": "winstrom",
        "password": "winstrom",
    }
    options.update(overrides)
    return options


class TestEvidenceKeyedResponseUnwrapping:
    """A listing response wrapped under the evidence name must unwrap to a plain list."""

    def test_listing_response_wrapped_under_evidence_name(self):
        ro = ReadOnly(None, {**_base_options(), "evidence": "adresar"})
        ro.session.get = MagicMock(
            return_value=_fake_response(
                {
                    "winstrom": {
                        "@version": "1.0",
                        "adresar": [{"id": "1", "kod": "ACME", "nazev": "ACME s.r.o."}],
                    }
                }
            )
        )
        result = ro.get_all_from_abraflexi()
        assert result == [{"id": "1", "kod": "ACME", "nazev": "ACME s.r.o."}]

    def test_sub_resource_response_wrapped_under_its_own_name(self):
        ro = ReadOnly(880, {**_base_options(), "evidence": "cenik", "autoload": False})
        ro.my_key = 880
        ro.session.get = MagicMock(
            return_value=_fake_response(
                {
                    "winstrom": {
                        "@version": "1.0",
                        "priloha": [{"id": "1", "nazSoub": "photo.jpg"}],
                    }
                }
            )
        )
        result = ro.perform_request("880/prilohy.json")
        assert result == [{"id": "1", "nazSoub": "photo.jpg"}]

    def test_create_response_still_uses_results_field(self):
        """Write-operation responses (genuinely wrapped under "results") must
        still unwrap the same way as before this fix."""
        ro = ReadOnly(None, {**_base_options(), "evidence": "cenik"})
        ro.session.get = MagicMock(
            return_value=_fake_response(
                {
                    "winstrom": {
                        "@version": "1.0",
                        "success": "true",
                        "stats": {"created": "1"},
                        "results": [{"id": "880", "ref": "/c/demo/cenik/880.json"}],
                    }
                }
            )
        )
        result = ro.perform_request()
        assert result == [{"id": "880", "ref": "/c/demo/cenik/880.json"}]

    def test_unrecognized_multi_key_shape_falls_back_to_raw_dict(self):
        """If more than one non-metadata key is present, there's no safe
        single key to unwrap - fall back to returning the raw dict rather
        than guessing."""
        ro = ReadOnly(None, {**_base_options(), "evidence": "cenik"})
        ro.session.get = MagicMock(
            return_value=_fake_response(
                {
                    "winstrom": {
                        "@version": "1.0",
                        "cenik": [{"id": "1"}],
                        "adresar": [{"id": "2"}],
                    }
                }
            )
        )
        result = ro.perform_request()
        assert result == {
            "winstrom": {
                "@version": "1.0",
                "cenik": [{"id": "1"}],
                "adresar": [{"id": "2"}],
            }
        }


class TestGetColumnsFilterConditions:
    """conditions must become a real AbraFlexi filter, not an ignored URL param."""

    def test_conditions_are_applied_as_a_filter_expression(self):
        ro = ReadOnly(None, {**_base_options(), "evidence": "cenik"})
        ro.session.get = MagicMock(
            return_value=_fake_response(
                {"winstrom": {"@version": "1.0", "adresar-bankovni-ucet": []}}
            )
        )
        ro.get_columns(["buc"], conditions={"firma": "code:110"}, evidence="adresar-bankovni-ucet")

        called_url = ro.session.get.call_args.args[0]
        assert "firma" in called_url and "code%3A110" in called_url
        # The filter must be part of the URL path (parenthesized segment),
        # never a bare "firma=" query parameter - AbraFlexi silently
        # ignores query-string filters.
        assert "&firma=" not in called_url and "?firma=" not in called_url

    def test_numeric_conditions_are_not_quoted(self):
        ro = ReadOnly(None, {**_base_options(), "evidence": "cenik"})
        ro.session.get = MagicMock(
            return_value=_fake_response({"winstrom": {"@version": "1.0", "cenik": []}})
        )
        ro.get_columns(["kod"], conditions={"id": 42})

        called_url = ro.session.get.call_args.args[0]
        assert "id" in called_url and "42" in called_url and "'42'" not in called_url


class TestGetBankAccountNumberResolvesKod:
    """firma on adresar-bankovni-ucet is stored as code:<kod>, not code:<id>."""

    def test_defaults_to_loaded_record_kod(self):
        adresar = Adresar(
            None, {**_base_options(), "evidence": "adresar", "autoload": False}
        )
        adresar.take_data({"id": "844", "kod": "RPISHOPCZ"})
        adresar.session.get = MagicMock(
            return_value=_fake_response(
                {"winstrom": {"@version": "1.0", "adresar-bankovni-ucet": []}}
            )
        )

        adresar.get_bank_account_number()

        called_url = adresar.session.get.call_args.args[0]
        assert "firma" in called_url and "code%3ARPISHOPCZ" in called_url

    def test_falls_back_to_my_key_when_kod_unknown(self):
        """Preserves the old fallback for callers that never loaded a full
        record (e.g. my_key set directly without fetching kod)."""
        adresar = Adresar(
            None, {**_base_options(), "evidence": "adresar", "autoload": False}
        )
        adresar.my_key = 1
        adresar.session.get = MagicMock(
            return_value=_fake_response(
                {"winstrom": {"@version": "1.0", "adresar-bankovni-ucet": []}}
            )
        )

        result = adresar.get_bank_account_number()

        assert result == []
        called_url = adresar.session.get.call_args.args[0]
        assert "adresar-bankovni-ucet" in called_url
