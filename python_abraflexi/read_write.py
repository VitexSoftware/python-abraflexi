"""
ReadWrite class for writing data to AbraFlexi REST API.

Extends ReadOnly with insert, update, and delete operations.
"""

import json
from typing import Optional, Dict, Any, Union, List

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

    def update(self, data: Optional[Dict[str, Any]] = None) -> Union[Dict, bool]:
        """
        Update existing record in AbraFlexi.

        Args:
            data: Data to update (uses self.data if None)

        Returns:
            Response data or False on error
        """
        if data is None:
            data = self.get_data()

        # Ensure we have an identifier
        if not self.get_record_ident() and "id" not in data:
            raise ValueError("Cannot update without record identifier")

        # Prepare JSON data
        self.post_fields = self._get_jsonized_data(data)

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

    def save(self, data: Optional[Dict[str, Any]] = None) -> Union[Dict, bool]:
        """
        Save record (insert or update).

        Args:
            data: Data to save

        Returns:
            Response data or False on error
        """
        if data is None:
            data = self.get_data()

        # Determine if insert or update
        if self.get_record_id() or "id" in data:
            return self.update(data)
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
        self,
        source_id: Union[int, str],
        dest_data: Optional[Dict] = None
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

    def _get_jsonized_data(
        self, data: Union[Dict, List], pretty: bool = False
    ) -> str:
        """
        Convert data to JSON format for API.

        Args:
            data: Data to convert
            pretty: Pretty print JSON

        Returns:
            JSON string
        """
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
