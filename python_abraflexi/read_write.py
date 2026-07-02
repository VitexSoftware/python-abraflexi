"""
ReadWrite class for writing data to AbraFlexi REST API.

Extends ReadOnly with insert, update, and delete operations.
"""

import base64
import json
import mimetypes
import os
from typing import Optional, Dict, Any, Union, List
from urllib.parse import quote

import requests

from .exceptions import ConnectionException
from .read_only import ReadOnly


class ReadWrite(ReadOnly):
    """
    Class for read-write interaction with AbraFlexi API.

    Adds insert, update, delete, and transaction support.
    """

    def __init__(
        self,
        init: Optional[Union[int, str, Dict]] = None,
        options: Optional[Dict[str, Any]] = None,
    ):
        """
        Initialize ReadWrite object.

        Args:
            init: Record ID, code, or initial data
            options: Configuration options
        """
        # Initialize write-specific attributes
        self.atomic: bool = False
        self.dry_run: bool = False
        self.post_fields: Optional[str] = None

        # Call parent constructor
        super().__init__(init, options)

    def _setup(self, options: Dict[str, Any]) -> None:
        """
        Set up object with configuration options.

        Args:
            options: Configuration dict
        """
        # Handle write-specific options
        self.atomic = options.get("atomic", False)
        self.dry_run = options.get("dry-run", False)

        if self.dry_run:
            self.default_url_params["dry-run"] = "true"

        # Call parent setup
        super()._setup(options)

    def insert_to_abraflexi(
        self, data: Optional[Dict[str, Any]] = None
    ) -> Union[Dict, bool]:
        """
        Insert record to AbraFlexi.

        Args:
            data: Data to insert (uses self.data if None)

        Returns:
            Response data or False on error
        """
        if data is None:
            data = self.get_data()

        # Prepare JSON data
        self.post_fields = self._get_jsonized_data(data)

        # Perform PUT request
        result = self.perform_request("", "PUT")

        # Extract inserted ID
        if result and isinstance(result, list) and len(result) > 0:
            if "id" in result[0]:
                self.last_inserted_id = int(result[0]["id"])
                self.my_key = self.last_inserted_id

        return result

    def update(
        self,
        data: Optional[Dict[str, Any]] = None,
        remove_external_ids: Optional[str] = None,
    ) -> Union[Dict, bool]:
        """
        Update existing record in AbraFlexi.

        Args:
            data: Data to update (uses self.data if None)
            remove_external_ids: If given, remove external identifiers
                starting with this prefix (empty string removes all of
                them) as part of the update, per "Identifikátory záznamů".

        Returns:
            Response data or False on error
        """
        if data is None:
            data = self.get_data()

        # Ensure we have an identifier
        if not self.get_record_ident() and "id" not in data:
            raise ValueError("Cannot update without record identifier")

        # Prepare JSON data
        self.post_fields = self._get_jsonized_data(
            data, remove_external_ids=remove_external_ids
        )

        # Perform POST request
        return self.perform_request("", "POST")

    def delete(self, identifier: Optional[Union[int, str]] = None) -> bool:
        """
        Delete record from AbraFlexi.

        Args:
            identifier: Record ID or code (uses current if None)

        Returns:
            Success status
        """
        if identifier:
            self.my_key = identifier
            self._update_api_url()

        if not self.get_record_ident():
            raise ValueError("Cannot delete without record identifier")

        # Perform DELETE request
        result = self.perform_request("", "DELETE")
        return bool(result)

    def save(
        self,
        data: Optional[Dict[str, Any]] = None,
        remove_external_ids: Optional[str] = None,
    ) -> Union[Dict, bool]:
        """
        Save record (insert or update).

        Args:
            data: Data to save
            remove_external_ids: If given, remove external identifiers
                starting with this prefix as part of the save (only takes
                effect on update; see :meth:`update`).

        Returns:
            Response data or False on error
        """
        if data is None:
            data = self.get_data()

        # Determine if insert or update
        if self.get_record_id() or "id" in data:
            return self.update(data, remove_external_ids=remove_external_ids)
        else:
            return self.insert_to_abraflexi(data)

    def perform_action(
        self, action: str, params: Optional[Dict] = None
    ) -> Union[Dict, bool]:
        """
        Perform action on record.

        Args:
            action: Action name
            params: Action parameters

        Returns:
            Response data or False on error
        """
        if not self.get_record_ident():
            raise ValueError("Cannot perform action without record identifier")

        # Build URL suffix
        url_suffix = f"{self.get_record_ident()}/{action}.json"

        # Add parameters if provided
        if params:
            self.post_fields = json.dumps({self.evidence: params})
            return self.perform_request(url_suffix, "POST")
        else:
            return self.perform_request(url_suffix, "POST")

    def copy(
        self, source_id: Union[int, str], dest_data: Optional[Dict] = None
    ) -> Union[Dict, bool]:
        """
        Copy existing record.

        Args:
            source_id: Source record ID
            dest_data: Additional data for new record

        Returns:
            Response data or False on error
        """
        # Load source record
        source = self.__class__(source_id, self.options)

        if not source.get_data():
            return False

        # Get source data
        data = source.get_data().copy()

        # Remove ID and other auto-generated fields
        if "id" in data:
            del data["id"]
        if "lastUpdate" in data:
            del data["lastUpdate"]

        # Merge with destination data
        if dest_data:
            data.update(dest_data)

        # Insert new record
        return self.insert_to_abraflexi(data)

    def _send_evidence_action(
        self,
        action: str,
        extra_data: Optional[Dict[str, Any]] = None,
        filter_str: Optional[str] = None,
    ) -> Union[Dict, bool]:
        """
        Send a body-level ``action`` attribute to the evidence (as opposed
        to :meth:`perform_action`, which calls a dedicated
        ``{id}/{action}.json`` URL for custom business actions).

        This is how AbraFlexi implements record deletion/storno/locking as
        part of an ordinary JSON import, per "Provádění akcí" and
        "Zamykání a odemykání záznamů". It can also target every record
        matching a filter at once ("Dávkové operace") when ``filter_str``
        is given instead of relying on the current record identifier.

        Args:
            action: Action name (e.g. "lock", "unlock", "delete", "storno")
            extra_data: Additional fields to send alongside the action
            filter_str: If given, apply the action to every record matching
                this filter instead of the current record

        Returns:
            Response data or False on error
        """
        body: Dict[str, Any] = dict(extra_data or {})
        if filter_str:
            body["@filter"] = filter_str
        else:
            if not self.get_record_ident():
                raise ValueError(
                    "Cannot perform action without record identifier or filter"
                )
            body["id"] = self.get_record_ident()
        body["@action"] = action

        self.post_fields = self._get_jsonized_data(body)
        return self.perform_request("", "POST")

    def lock(self) -> Union[Dict, bool]:
        """Lock the current record, preventing further changes until unlocked."""
        return self._send_evidence_action("lock")

    def unlock(self) -> Union[Dict, bool]:
        """Unlock the current record."""
        return self._send_evidence_action("unlock")

    def lock_for_ucetni(self) -> Union[Dict, bool]:
        """Lock the current record for the accountant (``lock-for-ucetni``)."""
        return self._send_evidence_action("lock-for-ucetni")

    def storno(self) -> Union[Dict, bool]:
        """Cancel (storno) the current document record."""
        return self._send_evidence_action("storno")

    def mass_update(
        self,
        filter_str: str,
        data: Optional[Dict[str, Any]] = None,
        action: Optional[str] = None,
    ) -> Union[Dict, bool]:
        """
        Update, or perform an action on, every record of the current
        evidence matching ``filter_str`` in a single request
        ("Dávkové operace").

        Args:
            filter_str: Filter selecting the records to affect
            data: Fields to set on every matching record
            action: If given, perform this action (e.g. "lock") on every
                matching record instead of (or in addition to) updating
                fields

        Returns:
            Response data or False on error
        """
        if action:
            return self._send_evidence_action(
                action, extra_data=data, filter_str=filter_str
            )

        body: Dict[str, Any] = dict(data or {})
        body["@filter"] = filter_str
        self.post_fields = self._get_jsonized_data(body)
        return self.perform_request("", "POST")

    def _get_jsonized_data(
        self,
        data: Union[Dict, List],
        pretty: bool = False,
        remove_external_ids: Optional[str] = None,
    ) -> str:
        """
        Convert data to JSON format for API.

        Args:
            data: Data to convert
            pretty: Pretty print JSON
            remove_external_ids: If given, add ``@removeExternalIds`` with
                this value to a single-record payload

        Returns:
            JSON string
        """
        if remove_external_ids is not None and isinstance(data, dict):
            data = {**data, "@removeExternalIds": remove_external_ids}

        # Wrap in evidence namespace
        if isinstance(data, dict):
            payload = {self.NAMESPACE: {self.evidence: data}}
        elif isinstance(data, list):
            payload = {self.NAMESPACE: {self.evidence: data}}
        else:
            payload = {self.NAMESPACE: {self.evidence: [data]}}

        # Convert to JSON
        if pretty or self.debug:
            return json.dumps(payload, indent=2, ensure_ascii=False)
        else:
            return json.dumps(payload, ensure_ascii=False)

    def set_atomic(self, atomic: bool = True) -> None:
        """
        Enable/disable atomic transaction mode.

        Args:
            atomic: Atomic mode flag
        """
        self.atomic = atomic
        if atomic:
            self.default_url_params["atomic"] = "true"
        elif "atomic" in self.default_url_params:
            del self.default_url_params["atomic"]

    def set_dry_run(self, dry_run: bool = True) -> None:
        """
        Enable/disable dry-run mode.

        Args:
            dry_run: Dry-run mode flag
        """
        self.dry_run = dry_run
        if dry_run:
            self.default_url_params["dry-run"] = "true"
        else:
            if "dry-run" in self.default_url_params:
                del self.default_url_params["dry-run"]

    def batch_insert(self, records: List[Dict]) -> Union[List, bool]:
        """
        Insert multiple records in batch.

        Args:
            records: List of records to insert

        Returns:
            Response data or False on error
        """
        # Prepare JSON data
        self.post_fields = self._get_jsonized_data(records)

        # Perform PUT request
        return self.perform_request("", "PUT")

    def batch_update(self, records: List[Dict]) -> Union[List, bool]:
        """
        Update multiple records in batch.

        Args:
            records: List of records to update

        Returns:
            Response data or False on error
        """
        # Prepare JSON data
        self.post_fields = self._get_jsonized_data(records)

        # Perform POST request
        return self.perform_request("", "POST")

    def add_attachment(
        self, filename: str, content: bytes, content_type: str
    ) -> Optional[int]:
        """
        Attach a file to the current record.

        Uses AbraFlexi's dedicated attachment endpoint
        (``{evidence}/{id}/prilohy/new/{filename}``), which takes the raw
        file bytes as the request body directly rather than a base64-wrapped
        JSON field nested in the parent record (AbraFlexi supports the latter
        too, but this is the endpoint the official PHP client uses).

        This endpoint answers in XML unless explicitly asked for JSON via
        the ``Accept`` header, so that header is always sent to keep parsing
        consistent with the rest of this client.

        Args:
            filename: Name to store the attachment as
            content: Raw file content
            content_type: MIME type of the content

        Returns:
            ID of the created attachment record, or None on failure

        Raises:
            ValueError: If the record has no identifier yet (must be saved first)
            ConnectionException: On network/timeout errors
            AbraFlexiException: On unexpected AbraFlexi errors
        """
        if not self.get_record_ident():
            raise ValueError("Cannot add attachment without record identifier")

        url = (
            f"{self.get_evidence_url()}/{self.get_record_ident()}"
            f"/prilohy/new/{quote(filename)}"
        )

        try:
            self.logger.debug(f"PUT {url}")
            response = self.session.put(
                url,
                data=content,
                headers={
                    **self.default_http_headers,
                    "Content-Type": content_type,
                    "Accept": "application/json",
                },
                timeout=self.timeout,
            )
            self.last_response = response
            self.last_response_code = response.status_code
        except requests.exceptions.Timeout:
            self.last_curl_error = f"Request timeout after {self.timeout}s"
            if self.throw_exception:
                raise ConnectionException(self.last_curl_error)
            return None
        except requests.exceptions.RequestException as e:
            self.last_curl_error = str(e)
            if self.throw_exception:
                raise ConnectionException(self.last_curl_error)
            return None

        result = self._parse_http_response(response)

        if (
            result
            and isinstance(result, list)
            and len(result) > 0
            and "id" in result[0]
        ):
            return int(result[0]["id"])
        return None

    def add_attachment_from_file(self, filepath: str) -> Optional[int]:
        """
        Attach a local file to the current record, auto-detecting its MIME type.

        Args:
            filepath: Path to the file to attach

        Returns:
            ID of the created attachment record, or None on failure
        """
        with open(filepath, "rb") as fh:
            content = fh.read()

        content_type, _ = mimetypes.guess_type(filepath)
        if not content_type:
            content_type = "application/octet-stream"

        return self.add_attachment(os.path.basename(filepath), content, content_type)

    def list_attachments(self) -> Union[List, bool]:
        """List attachments (``přílohy``) of the current record."""
        if not self.get_record_ident():
            raise ValueError("Cannot list attachments without record identifier")
        return self.perform_request(f"{self.get_record_ident()}/prilohy.json")

    def get_attachment(self, attachment_id: Union[int, str]) -> Union[Dict, bool]:
        """Get metadata for a single attachment of the current record."""
        if not self.get_record_ident():
            raise ValueError("Cannot get attachment without record identifier")
        return self.perform_request(
            f"{self.get_record_ident()}/prilohy/{attachment_id}.json"
        )

    def download_attachment(self, attachment_id: Union[int, str]) -> Union[bytes, bool]:
        """Download the raw binary content of an attachment."""
        if not self.get_record_ident():
            raise ValueError("Cannot download attachment without record identifier")
        return self.perform_request(
            f"{self.get_record_ident()}/prilohy/{attachment_id}/content", binary=True
        )

    def get_attachment_thumbnail(
        self,
        attachment_id: Union[int, str],
        width: Optional[int] = None,
        height: Optional[int] = None,
    ) -> Union[bytes, bool]:
        """
        Download the thumbnail of an image attachment.

        Args:
            attachment_id: Attachment record identifier
            width: Requested thumbnail width in pixels
            height: Requested thumbnail height in pixels

        Returns:
            Raw thumbnail image bytes, or False (404) if none exists
        """
        if not self.get_record_ident():
            raise ValueError("Cannot get thumbnail without record identifier")
        suffix = f"{self.get_record_ident()}/prilohy/{attachment_id}/thumbnail"
        params = {}
        if width:
            params["w"] = width
        if height:
            params["h"] = height
        if params:
            suffix += "?" + "&".join(f"{k}={v}" for k, v in params.items())
        return self.perform_request(suffix, binary=True)

    def delete_attachment(self, attachment_id: Union[int, str]) -> bool:
        """Delete an attachment from the current record."""
        if not self.get_record_ident():
            raise ValueError("Cannot delete attachment without record identifier")
        result = self.perform_request(
            f"{self.get_record_ident()}/prilohy/{attachment_id}.json", "DELETE"
        )
        return bool(result)

    def export_report(
        self,
        record_id: Optional[Union[int, str]] = None,
        report_format: str = "pdf",
        report_name: Optional[str] = None,
        report_lang: Optional[str] = None,
        report_sign: bool = False,
    ) -> Union[bytes, bool]:
        """
        Export a printable report for the current evidence (or a specific
        record) as PDF or XLSX ("Export tiskových sestav").

        Args:
            record_id: Record to export a report for; the whole evidence
                listing is exported if omitted
            report_format: "pdf" or "xls"
            report_name: Specific report identifier (see :meth:`get_reports`)
            report_lang: Report language ("cs", "sk", "en" or "de")
            report_sign: Whether to electronically sign the exported PDF

        Returns:
            Raw report bytes
        """
        extension = "xls" if report_format == "xls" else "pdf"
        previous_format = self.format
        previous_key = self.my_key
        previous_params = dict(self.default_url_params)
        try:
            self.format = extension
            if record_id is not None:
                self.my_key = record_id
            self._update_api_url()
            if report_name:
                self.default_url_params["report-name"] = report_name
            if report_lang:
                self.default_url_params["report-lang"] = report_lang
            if report_sign:
                self.default_url_params["report-sign"] = "true"
            return self.perform_request("", binary=True)
        finally:
            self.format = previous_format
            self.my_key = previous_key
            self.default_url_params = previous_params
            self._update_api_url()

    def get_qr_code_image(self, size: int = 140) -> Union[bytes, bool]:
        """
        Get the payment QR code for the current document as a raw PNG image.

        Args:
            size: Requested image size in pixels

        Returns:
            Raw PNG bytes
        """
        if not self.get_record_ident():
            raise ValueError("Cannot get QR code without record identifier")
        return self.perform_request(
            f"{self.get_record_ident()}/qrcode.png?size={size}", binary=True
        )

    def get_qr_code_base64(self, size: int = 140) -> str:
        """
        Get the payment QR code for the current document as a base64 data URI.

        Args:
            size: Requested image size in pixels

        Returns:
            ``data:image/png;base64,...`` string
        """
        image = self.get_qr_code_image(size)
        encoded = base64.b64encode(image).decode("ascii") if image else ""
        return f"data:image/png;base64,{encoded}"
