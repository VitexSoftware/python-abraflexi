"""
Tests for binary (non-JSON) response handling used by attachment
downloads, thumbnails, report export and QR codes.
"""

from unittest.mock import MagicMock

from python_abraflexi import ReadWrite


def _binary_response(content=b"\x89PNGfakebytes", status_code=200):
    response = MagicMock()
    response.status_code = status_code
    response.content = content
    return response


def _client():
    return ReadWrite(
        1,
        {
            "url": "https://demo.flexibee.eu",
            "company": "demo",
            "user": "winstrom",
            "password": "winstrom",
            "evidence": "faktura-vydana",
            "offline": True,
            "autoload": False,
        },
    )


class TestBinaryResponses:
    def test_perform_request_binary_returns_raw_bytes(self):
        rw = _client()
        rw.offline = False
        rw.session.get = MagicMock(return_value=_binary_response(b"raw-bytes"))

        result = rw.perform_request("some/binary/path", binary=True)

        assert result == b"raw-bytes"
        rw.session.get.return_value.json.assert_not_called()

    def test_download_attachment_returns_bytes(self):
        rw = _client()
        rw.offline = False
        rw.my_key = 1
        rw.session.get = MagicMock(return_value=_binary_response(b"attachment-bytes"))

        assert rw.download_attachment(42) == b"attachment-bytes"
        called_url = rw.session.get.call_args.args[0]
        assert called_url.endswith("/faktura-vydana/1/prilohy/42/content")

    def test_get_attachment_thumbnail_returns_bytes(self):
        rw = _client()
        rw.offline = False
        rw.my_key = 1
        rw.session.get = MagicMock(return_value=_binary_response(b"thumb-bytes"))

        assert rw.get_attachment_thumbnail(42, width=100, height=50) == b"thumb-bytes"
        called_url = rw.session.get.call_args.args[0]
        assert "prilohy/42/thumbnail" in called_url
        assert "w=100" in called_url
        assert "h=50" in called_url

    def test_get_qr_code_image_returns_bytes(self):
        rw = _client()
        rw.offline = False
        rw.my_key = 1
        rw.session.get = MagicMock(return_value=_binary_response(b"\x89PNG"))

        image = rw.get_qr_code_image(size=200)

        assert image == b"\x89PNG"
        called_url = rw.session.get.call_args.args[0]
        assert called_url.endswith("/faktura-vydana/1/qrcode.png?size=200")

    def test_get_qr_code_base64_encodes_image(self):
        rw = _client()
        rw.offline = False
        rw.my_key = 1
        rw.session.get = MagicMock(return_value=_binary_response(b"hello"))

        data_uri = rw.get_qr_code_base64()

        assert data_uri.startswith("data:image/png;base64,")
        assert data_uri.endswith("aGVsbG8=")  # base64("hello")

    def test_export_report_sets_format_and_params(self):
        rw = _client()
        rw.offline = False
        rw.my_key = 1
        rw.session.get = MagicMock(return_value=_binary_response(b"%PDF-1.4"))

        pdf_bytes = rw.export_report(
            record_id=1, report_name="dodaciList", report_lang="en"
        )

        assert pdf_bytes == b"%PDF-1.4"
        called_url = rw.session.get.call_args.args[0]
        assert called_url.endswith(".pdf") or ".pdf?" in called_url
        assert "report-name=dodaciList" in called_url
        assert "report-lang=en" in called_url
        # Format/key must be restored after the call.
        assert rw.format == "json"
