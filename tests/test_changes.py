"""
Tests for the company-wide Changes API client.
"""

import json
from unittest.mock import MagicMock

from python_abraflexi.changes import Changes


def _fake_response(payload, status_code=200):
    response = MagicMock()
    response.status_code = status_code
    response.content = json.dumps(payload).encode("utf-8")
    response.json.return_value = payload
    return response


def _client():
    return Changes(
        None,
        {
            "url": "https://demo.flexibee.eu",
            "company": "demo",
            "user": "winstrom",
            "password": "winstrom",
        },
    )


class TestChanges:
    def test_evidence_is_changes(self):
        assert _client().evidence == "changes"

    def test_get_changes_builds_params_and_unwraps_response(self):
        changes = _client()
        payload = {
            "winstrom": {
                "@globalVersion": "8",
                "changes": [
                    {"@evidence": "faktura-vydana", "@operation": "create", "id": "1"}
                ],
                "next": "9",
            }
        }
        changes.session.get = MagicMock(return_value=_fake_response(payload))

        result = changes.get_changes(start=5, limit=10, evidences=["faktura-vydana"])

        called_url = changes.session.get.call_args.args[0]
        assert "start=5" in called_url
        assert "limit=10" in called_url
        assert "evidence=faktura-vydana" in called_url
        assert result["changes"][0]["id"] == "1"
        assert result["next"] == "9"
        assert result["global_version"] == "8"
        # Temporary params used for this call must not leak into the object.
        assert "start" not in changes.default_url_params
        assert "limit" not in changes.default_url_params

    def test_enable_and_disable_hit_correct_urls(self):
        changes = _client()
        changes.session.put = MagicMock(
            return_value=_fake_response({"winstrom": {"success": "true"}})
        )

        assert changes.enable() is True
        assert changes.session.put.call_args.args[0].endswith("/changes/enable.json")

        assert changes.disable() is True
        assert changes.session.put.call_args.args[0].endswith("/changes/disable.json")

    def test_get_status_true(self):
        changes = _client()
        response = MagicMock()
        response.status_code = 200
        response.content = b"true"
        response.json.return_value = True
        changes.session.get = MagicMock(return_value=response)

        assert changes.get_status() is True
        assert changes.session.get.call_args.args[0].endswith("/changes/status.json")

    def test_get_status_false(self):
        changes = _client()
        response = MagicMock()
        response.status_code = 200
        response.content = b"false"
        response.json.return_value = False
        changes.session.get = MagicMock(return_value=response)

        assert changes.get_status() is False
