"""
Tests for ReadWrite class attachment handling.
"""

import json
from unittest.mock import MagicMock

import pytest

from python_abraflexi import ReadWrite


def _fake_response(status_code=201, payload=None):
    """Build a MagicMock standing in for a requests.Response."""
    if payload is None:
        payload = {
            "winstrom": {
                "@version": "1.0",
                "success": "true",
                "results": [{"id": "123", "ref": "/c/demo/cenik/1/prilohy/123.json"}],
            }
        }
    response = MagicMock()
    response.status_code = status_code
    response.content = json.dumps(payload).encode("utf-8")
    response.json.return_value = payload
    return response


class TestAttachments:
    """Test ReadWrite attachment upload."""

    def _client(self):
        return ReadWrite(
            1,
            {
                "url": "https://demo.flexibee.eu",
                "company": "demo",
                "user": "winstrom",
                "password": "winstrom",
                "evidence": "cenik",
                "offline": True,
                "autoload": False,
            },
        )

    def test_add_attachment_requires_record_identifier(self):
        rw = ReadWrite(
            None,
            {
                "url": "https://demo.flexibee.eu",
                "company": "demo",
                "evidence": "cenik",
                "offline": True,
            },
        )
        with pytest.raises(ValueError):
            rw.add_attachment("photo.jpg", b"binarydata", "image/jpeg")

    def test_add_attachment_builds_correct_url_and_headers(self):
        rw = self._client()
        rw.my_key = 1
        rw.session.put = MagicMock(return_value=_fake_response())

        attach_id = rw.add_attachment("photo.jpg", b"binarydata", "image/jpeg")

        assert attach_id == 123
        called_url = rw.session.put.call_args.args[0]
        assert called_url == "https://demo.flexibee.eu/c/demo/cenik/1/prilohy/new/photo.jpg"

        called_kwargs = rw.session.put.call_args.kwargs
        assert called_kwargs["data"] == b"binarydata"
        assert called_kwargs["headers"]["Content-Type"] == "image/jpeg"
        assert called_kwargs["headers"]["Accept"] == "application/json"

    def test_add_attachment_url_encodes_filename(self):
        rw = self._client()
        rw.my_key = 1
        rw.session.put = MagicMock(return_value=_fake_response())

        rw.add_attachment("my photo (1).jpg", b"data", "image/jpeg")

        called_url = rw.session.put.call_args.args[0]
        assert " " not in called_url
        assert called_url.endswith("prilohy/new/my%20photo%20%281%29.jpg")

    def test_add_attachment_returns_none_on_failure_when_not_throwing(self):
        rw = self._client()
        rw.my_key = 1
        rw.throw_exception = False
        rw.session.put = MagicMock(
            return_value=_fake_response(
                status_code=400,
                payload={
                    "winstrom": {
                        "success": "false",
                        "results": [{"errors": [{"message": "bad request"}]}],
                    }
                },
            )
        )

        assert rw.add_attachment("photo.jpg", b"data", "image/jpeg") is None

    def test_add_attachment_from_file_guesses_mime_type(self, tmp_path):
        rw = self._client()
        rw.my_key = 1
        rw.session.put = MagicMock(return_value=_fake_response())

        filepath = tmp_path / "component.jpg"
        filepath.write_bytes(b"fake-jpeg-bytes")

        attach_id = rw.add_attachment_from_file(str(filepath))

        assert attach_id == 123
        called_kwargs = rw.session.put.call_args.kwargs
        assert called_kwargs["headers"]["Content-Type"] == "image/jpeg"
        assert called_kwargs["data"] == b"fake-jpeg-bytes"

    def test_add_attachment_from_file_unknown_type_falls_back(self, tmp_path):
        rw = self._client()
        rw.my_key = 1
        rw.session.put = MagicMock(return_value=_fake_response())

        filepath = tmp_path / "data.unknownext"
        filepath.write_bytes(b"bytes")

        rw.add_attachment_from_file(str(filepath))

        called_kwargs = rw.session.put.call_args.kwargs
        assert called_kwargs["headers"]["Content-Type"] == "application/octet-stream"
