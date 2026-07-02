"""
ReadOnly class for reading data from AbraFlexi REST API.

This is the base class for all AbraFlexi operations.
"""

import os
import json
import logging
from typing import Optional, Dict, Any, Union, List, Iterator
from datetime import datetime, date
from urllib.parse import urlencode, quote
import requests
from requests.auth import HTTPBasicAuth

from .exceptions import (
    AbraFlexiException,
    ConnectionException,
    AuthenticationException,
    NotFoundException,
    PermissionException,
    ValidationException,
)
from .relation import Relation


class ReadOnly:
    """
    Base class for read-only interaction with AbraFlexi API.

    This class handles HTTP communication, authentication, and data parsing.
    """

    # Library version
    LIB_VERSION = "1.1.1"

    # Default configuration
    DEFAULT_TIMEOUT = 300
    DEFAULT_FORMAT = "json"
    DEFAULT_PREFIX = "/c/"
    NAMESPACE = "winstrom"
    RESULT_FIELD = "results"

    def __init__(
        self,
        init: Optional[Union[int, str, Dict]] = None,
        options: Optional[Dict[str, Any]] = None,
    ):
        """
        Initialize ReadOnly object.

        Args:
            init: Record ID, code, or initial data
            options: Configuration options
        """
        self.logger = logging.getLogger(self.__class__.__name__)
        self.options = options or {}

        # Connection settings
        self.url: Optional[str] = None
        self.company: Optional[str] = None
        self.user: Optional[str] = None
        self.password: Optional[str] = None
        self.auth_session_id: Optional[str] = None

        # API settings
        self.evidence: Optional[str] = None
        self.format: str = self.DEFAULT_FORMAT
        self.response_format: str = self.DEFAULT_FORMAT
        self.prefix: str = self.DEFAULT_PREFIX
        self.api_url: Optional[str] = None

        # Request settings
        self.timeout: int = self.DEFAULT_TIMEOUT
        self.default_url_params: Dict[str, Any] = {}
        self.default_http_headers: Dict[str, str] = {}
        self.filter: Optional[str] = None

        # Data storage
        self.data: Dict[str, Any] = {}
        self.last_response: Optional[requests.Response] = None
        self.last_response_code: Optional[int] = None
        self.last_result: Optional[Any] = None
        self.last_curl_error: Optional[str] = None
        self.errors: List[Dict] = []
        self.row_count: Optional[int] = None
        self.global_version: Optional[int] = None

        # Behavior flags
        self.debug: bool = False
        self.offline: bool = False
        self.autoload: bool = True
        self.native_types: bool = True
        self.throw_exception: bool = True
        self.ignore_not_found: bool = False

        # Record identification
        self.my_key: Optional[Union[int, str]] = None
        self.last_inserted_id: Optional[int] = None

        # Session
        self.session = requests.Session()

        # Setup
        self._setup(self.options)

        # Process init parameter
        if init is not None:
            self._process_init(init)

    def _setup(self, options: Dict[str, Any]) -> None:
        """
        Set up object with configuration options.

        Args:
            options: Configuration dict
        """
        # Load from environment or options
        self.url = options.get("url", os.getenv("ABRAFLEXI_URL"))
        self.company = options.get("company", os.getenv("ABRAFLEXI_COMPANY"))
        self.user = options.get("user", os.getenv("ABRAFLEXI_LOGIN"))
        self.password = options.get("password", os.getenv("ABRAFLEXI_PASSWORD"))
        self.auth_session_id = options.get(
            "authSessionId", os.getenv("ABRAFLEXI_AUTHSESSID")
        )

        # Timeout
        if "timeout" in options:
            self.timeout = int(options["timeout"])
        elif os.getenv("ABRAFLEXI_TIMEOUT"):
            self.timeout = int(os.getenv("ABRAFLEXI_TIMEOUT"))

        # Behavior flags
        self.debug = options.get("debug", False)
        self.offline = options.get("offline", False)
        self.autoload = options.get("autoload", True)
        self.native_types = options.get("native_types", True)
        self.throw_exception = options.get(
            "throwException",
            os.getenv("ABRAFLEXI_EXCEPTIONS", "true").lower() == "true",
        )
        self.ignore_not_found = options.get("ignore404", False)

        # URL parameters
        if "defaultUrlParams" in options:
            self.default_url_params.update(options["defaultUrlParams"])

        if "detail" in options:
            self.default_url_params["detail"] = options["detail"]

        if "filter" in options:
            self.filter = options["filter"]

        # Prefix
        if "prefix" in options:
            self.set_prefix(options["prefix"])

        # Evidence
        if "evidence" in options:
            self.set_evidence(options["evidence"])
        elif self.evidence:
            self.set_evidence(self.evidence)

        # Authentication setup
        if self.auth_session_id:
            self.default_http_headers["X-authSessionId"] = self.auth_session_id
        elif self.user and self.password:
            self.session.auth = HTTPBasicAuth(self.user, self.password)

        # SSL verification (AbraFlexi uses self-signed certs by default)
        self.session.verify = False
        if not self.session.verify:
            import urllib3

            urllib3.disable_warnings(urllib3.exceptions.InsecureRequestWarning)

        # User agent
        self.session.headers.update(
            {
                "User-Agent": f"python-abraflexi v{self.LIB_VERSION} https://github.com/VitexSoftware/python-abraflexi"
            }
        )

    def _process_init(self, init: Union[int, str, Dict]) -> None:
        """
        Process initialization parameter.

        Args:
            init: Record ID, code, or data dict
        """
        if isinstance(init, int) and self.autoload:
            self.load_from_abraflexi(init)
        elif isinstance(init, dict):
            self.take_data(init)
        elif isinstance(init, str):
            if init.startswith("code:"):
                if self.autoload:
                    self.load_from_abraflexi(init)
                else:
                    self.my_key = init
            else:
                if self.autoload:
                    self.load_from_abraflexi(init)
                else:
                    self.my_key = init

    def set_evidence(self, evidence: str) -> bool:
        """
        Set evidence for communication.

        Args:
            evidence: Evidence name

        Returns:
            Success status
        """
        self.evidence = evidence
        self._update_api_url()
        return True

    def get_evidence(self) -> Optional[str]:
        """Get current evidence."""
        return self.evidence

    def set_company(self, company: str) -> None:
        """Set company."""
        self.company = company
        self._update_api_url()

    def get_company(self) -> Optional[str]:
        """Get current company."""
        return self.company

    def set_prefix(self, prefix: str) -> None:
        """
        Set URL prefix.

        Args:
            prefix: Prefix (a, c, u, g, admin, status, login-logout)
        """
        valid_prefixes = ["a", "c", "u", "g", "admin", "status", "login-logout"]
        if prefix in valid_prefixes:
            self.prefix = f"/{prefix}/"
        elif prefix in [None, "", "/"]:
            self.prefix = ""
        else:
            raise ValueError(f"Unknown prefix: {prefix}")
        self._update_api_url()

    def set_format(self, format_type: str) -> bool:
        """
        Set communication format.

        Args:
            format_type: Format (json, xml, csv, pdf, etc.)

        Returns:
            Success status
        """
        self.format = format_type
        self._update_api_url()
        return True

    def get_evidence_url(self) -> str:
        """
        Get base URL for current evidence.

        Returns:
            Evidence URL
        """
        evidence_url = f"{self.url}{self.prefix}{self.company}"
        if self.evidence:
            evidence_url += f"/{self.evidence}"
        return evidence_url

    def _update_api_url(self) -> None:
        """Update API URL based on current settings."""
        self.api_url = self.get_evidence_url()

        # Add record identifier if present
        row_identifier = self.get_record_ident()
        if row_identifier:
            self.api_url += f"/{row_identifier}"

        self.api_url += f".{self.format}"

    def get_record_ident(self) -> Optional[str]:
        """Get record identifier."""
        if self.my_key:
            return str(self.my_key)
        return None

    def get_record_id(self) -> Optional[int]:
        """Get record ID."""
        if isinstance(self.my_key, int):
            return self.my_key
        if "id" in self.data:
            return int(self.data["id"])
        return None

    def get_record_code(self) -> Optional[str]:
        """Get record code."""
        if isinstance(self.my_key, str) and self.my_key.startswith("code:"):
            return self.my_key[5:]
        if "kod" in self.data:
            return self.data["kod"]
        return None

    def take_data(self, data: Dict[str, Any]) -> None:
        """
        Load data into object.

        Args:
            data: Data dictionary
        """
        self.data = data
        if "id" in data:
            self.my_key = int(data["id"])

    def get_data(self) -> Dict[str, Any]:
        """Get current data."""
        return self.data

    def get_connection_options(self) -> Dict[str, Any]:
        """
        Get the connection options (url/company/credentials/...) of this
        object, suitable for constructing another object bound to the same
        AbraFlexi company (e.g. following a "firma" relation).

        Returns:
            Options dict usable as the ``options`` constructor argument
        """
        return {
            "url": self.url,
            "company": self.company,
            "user": self.user,
            "password": self.password,
            "authSessionId": self.auth_session_id,
            "timeout": self.timeout,
            "offline": self.offline,
            "throwException": self.throw_exception,
        }

    def get_data_value(self, key: str, default: Any = None) -> Any:
        """
        Get data value by key.

        Args:
            key: Data key
            default: Default value if key not found

        Returns:
            Data value
        """
        return self.data.get(key, default)

    def set_data_value(self, key: str, value: Any) -> None:
        """
        Set data value.

        Args:
            key: Data key
            value: Data value
        """
        # Handle datetime objects
        if isinstance(value, datetime):
            value = value.strftime("%Y-%m-%dT%H:%M:%S.%f")[:-3]
        elif isinstance(value, date):
            value = value.strftime("%Y-%m-%d")
        elif isinstance(value, Relation):
            value = value.to_dict()

        self.data[key] = value

    def perform_request(
        self,
        url_suffix: str = "",
        method: str = "GET",
        format_type: Optional[str] = None,
        binary: bool = False,
    ) -> Union[Dict, List, bytes, bool]:
        """
        Perform HTTP request against the current evidence.

        Args:
            url_suffix: URL suffix
            method: HTTP method
            format_type: Response format
            binary: If True, the response body is returned as raw bytes
                instead of being parsed as JSON (used for attachment
                content/thumbnails, PDF/XLSX reports and QR codes).

        Returns:
            Response data or False on error
        """
        if self.offline:
            self.logger.warning("Offline mode - no request performed")
            return False

        # Build URL
        if url_suffix:
            url = self.get_evidence_url() + "/" + url_suffix.lstrip("/")
        else:
            url = self.api_url or self.get_evidence_url() + f".{self.format}"

        # Add filter as a parenthesized path segment (AbraFlexi only honors
        # filters this way; a "filter" query-string parameter is silently
        # ignored by the server).
        if self.filter:
            suffix = f".{self.format}"
            encoded_filter = quote(self.filter, safe="()='*,<>!")
            if url.endswith(suffix):
                url = url[: -len(suffix)] + f"/({encoded_filter}){suffix}"
            else:
                url += f"/({encoded_filter})"

        # Add default URL parameters
        if self.default_url_params:
            separator = "&" if "?" in url else "?"
            url += separator + urlencode(self.default_url_params, doseq=True)

        return self._execute(
            url, method, getattr(self, "post_fields", None), binary=binary
        )

    def _perform_root_request(
        self,
        path: str,
        method: str = "GET",
        data: Optional[str] = None,
        binary: bool = False,
    ) -> Union[Dict, List, bytes, bool]:
        """
        Perform HTTP request against the server root (not scoped to a
        company/evidence), e.g. ``/login-logout/*`` endpoints.

        Args:
            path: Path relative to the server root
            method: HTTP method
            data: Raw request body (JSON string)
            binary: If True, return raw response bytes instead of JSON

        Returns:
            Response data or False on error
        """
        if self.offline:
            self.logger.warning("Offline mode - no request performed")
            return False

        url = f"{self.url}/{path.lstrip('/')}"
        return self._execute(url, method, data, binary=binary)

    def _execute(
        self,
        url: str,
        method: str,
        data: Optional[str] = None,
        binary: bool = False,
    ) -> Union[Dict, List, bytes, bool]:
        """
        Perform the actual HTTP call for a fully-built URL and parse the
        response.

        Args:
            url: Fully-built request URL
            method: HTTP method
            data: Raw request body (JSON string) for POST/PUT
            binary: If True, return raw response bytes instead of JSON

        Returns:
            Response data or False on error
        """
        headers = self.default_http_headers.copy()

        try:
            self.logger.debug(f"{method} {url}")

            if method == "GET":
                response = self.session.get(url, headers=headers, timeout=self.timeout)
            elif method == "POST":
                response = self.session.post(
                    url,
                    data=data,
                    headers={**headers, "Content-Type": "application/json"},
                    timeout=self.timeout,
                )
            elif method == "PUT":
                response = self.session.put(
                    url,
                    data=data,
                    headers={**headers, "Content-Type": "application/json"},
                    timeout=self.timeout,
                )
            elif method == "DELETE":
                response = self.session.delete(
                    url, headers=headers, timeout=self.timeout
                )
            else:
                raise ValueError(f"Unsupported HTTP method: {method}")

            self.last_response = response
            self.last_response_code = response.status_code

            # Handle response
            return self._parse_http_response(response, binary=binary)

        except requests.exceptions.Timeout:
            self.last_curl_error = f"Request timeout after {self.timeout}s"
            if self.throw_exception:
                raise ConnectionException(self.last_curl_error)
            return False
        except requests.exceptions.RequestException as e:
            self.last_curl_error = str(e)
            if self.throw_exception:
                raise ConnectionException(self.last_curl_error)
            return False

    def _parse_http_response(
        self, response: requests.Response, binary: bool = False
    ) -> Union[Dict, List, bytes, bool]:
        """
        Parse HTTP response.

        Args:
            response: Response object
            binary: If True, a successful response returns raw bytes

        Returns:
            Parsed response data
        """
        # Handle status codes
        if response.status_code in (200, 201):
            return self._parse_response_body(response, binary=binary)
        elif response.status_code == 304:
            return False
        elif response.status_code == 404:
            if not self.ignore_not_found:
                self.logger.error(f"Not found: {response.url}")
                if self.throw_exception:
                    raise NotFoundException(f"Resource not found: {response.url}")
            return False
        elif response.status_code == 401:
            if self.throw_exception:
                raise AuthenticationException("Authentication failed")
            return False
        elif response.status_code == 402:
            if self.throw_exception:
                raise PermissionException(
                    "Write REST API is not licensed for this AbraFlexi company"
                )
            return False
        elif response.status_code == 403:
            if self.throw_exception:
                raise PermissionException(
                    "User is not authorized to perform this operation"
                )
            return False
        elif response.status_code == 405:
            if self.throw_exception:
                method = response.request.method if response.request else ""
                raise AbraFlexiException(f"Method {method} not allowed")
            return False
        elif response.status_code == 406:
            if self.throw_exception:
                raise AbraFlexiException(
                    "Requested output format is not supported for this resource"
                )
            return False
        elif response.status_code == 500:
            if self.throw_exception:
                raise AbraFlexiException(
                    f"AbraFlexi internal server error: {response.text}"
                )
            return False
        elif response.status_code >= 400:
            self.logger.error(f"HTTP {response.status_code}: {response.text}")
            if self.throw_exception:
                raise AbraFlexiException(
                    f"HTTP {response.status_code}: {response.text}"
                )
            return False

        return True

    def _parse_response_body(
        self, response: requests.Response, binary: bool = False
    ) -> Union[Dict, List, bytes, bool]:
        """
        Parse response body.

        Args:
            response: Response object
            binary: If True, return the raw response bytes unparsed

        Returns:
            Parsed data
        """
        if not response.content:
            return True

        if binary:
            return response.content

        try:
            data = response.json()

            # Extract results
            if isinstance(data, dict) and self.NAMESPACE in data:
                namespace_data = data[self.NAMESPACE]

                # Check for errors
                if "success" in namespace_data and namespace_data["success"] == "false":
                    self._parse_errors(namespace_data)
                    if self.throw_exception:
                        error_msg = "; ".join(
                            [e.get("message", str(e)) for e in self.errors]
                        )
                        raise ValidationException(error_msg, self.errors)
                    return False

                # Extract metadata
                if "@rowCount" in namespace_data:
                    self.row_count = int(namespace_data["@rowCount"])
                if "@globalVersion" in namespace_data:
                    self.global_version = int(namespace_data["@globalVersion"])

                # Extract results
                if self.RESULT_FIELD in namespace_data:
                    results = namespace_data[self.RESULT_FIELD]
                    self.last_result = results

                    # Convert native types
                    if self.native_types and isinstance(results, list):
                        results = [self._convert_types(r) for r in results]
                    elif self.native_types and isinstance(results, dict):
                        results = self._convert_types(results)

                    return results

            return data

        except json.JSONDecodeError as e:
            self.logger.error(f"JSON decode error: {e}")
            if self.throw_exception:
                raise AbraFlexiException(f"Invalid JSON response: {e}")
            return False

    def _parse_errors(self, data: Dict) -> None:
        """
        Parse errors from response.

        Args:
            data: Response data
        """
        self.errors = []
        if self.RESULT_FIELD in data:
            results = data[self.RESULT_FIELD]
            if isinstance(results, list):
                for result in results:
                    if "errors" in result:
                        for error in result["errors"]:
                            self.errors.append(error)

    def _convert_types(self, data: Dict[str, Any]) -> Dict[str, Any]:
        """
        Convert AbraFlexi types to Python native types.

        Args:
            data: Data dictionary

        Returns:
            Converted data
        """
        converted = {}
        for key, value in data.items():
            if isinstance(value, str):
                # Try to convert date/datetime
                if "datum" in key.lower() or "date" in key.lower():
                    try:
                        if "T" in value:
                            converted[key] = datetime.fromisoformat(
                                value.replace("Z", "")
                            )
                        else:
                            converted[key] = datetime.strptime(value, "%Y-%m-%d").date()
                        continue
                    except (ValueError, AttributeError):
                        pass
            converted[key] = value
        return converted

    def load_from_abraflexi(
        self, identifier: Union[int, str], params: Optional[Dict] = None
    ) -> bool:
        """
        Load record from AbraFlexi.

        Args:
            identifier: Record ID or code
            params: Additional URL parameters

        Returns:
            Success status
        """
        self.my_key = identifier
        self._update_api_url()

        if params:
            self.default_url_params.update(params)

        result = self.perform_request()
        if result:
            if isinstance(result, list) and len(result) > 0:
                self.take_data(result[0])
                return True
            elif isinstance(result, dict):
                self.take_data(result)
                return True

        return False

    def get_all_from_abraflexi(
        self, params: Optional[Dict] = None
    ) -> Union[List[Dict], bool]:
        """
        Get all records from evidence.

        Args:
            params: URL parameters

        Returns:
            List of records or False
        """
        if params:
            self.default_url_params.update(params)

        result = self.perform_request()
        return result if result else []

    def get_flexi_data(self, url: Optional[str] = None) -> Union[Dict, List, bool]:
        """
        Get data from AbraFlexi.

        Args:
            url: Optional URL to fetch from

        Returns:
            Response data
        """
        if url:
            # Parse URL and perform request
            return self.perform_request(url)
        else:
            return self.perform_request()

    # ------------------------------------------------------------------
    # Pagination, sorting and listing helpers
    # ------------------------------------------------------------------

    def set_limit(self, limit: int) -> None:
        """
        Limit the number of records returned by evidence listing.

        Args:
            limit: Maximum number of records to return
        """
        self.default_url_params["limit"] = limit

    def set_start(self, start: int) -> None:
        """
        Set the offset for evidence listing (paired with :meth:`set_limit`).

        Args:
            start: Zero-based index of the first record to return
        """
        self.default_url_params["start"] = start

    def set_order(self, column: str, direction: str = "A") -> None:
        """
        Set sort order for evidence listing.

        Args:
            column: Column name to sort by
            direction: "A" for ascending (default) or "D" for descending
        """
        self.default_url_params["order"] = f"{column}@{direction}"

    def set_add_row_count(self, enabled: bool = True) -> None:
        """
        Include the total number of matching records in the response
        (``@rowCount``), useful together with pagination.

        Args:
            enabled: Whether to request the row count
        """
        if enabled:
            self.default_url_params["add-row-count"] = "true"
        else:
            self.default_url_params.pop("add-row-count", None)

    def set_detail(self, level: str) -> None:
        """
        Set the response detail level (e.g. "id", "summary", "full",
        "custom:kod,nazev").

        Args:
            level: Detail level identifier
        """
        self.default_url_params["detail"] = level

    def set_relations(self, *names: str) -> None:
        """
        Include the given sub-evidences (relations) in the response, e.g.
        ``set_relations("polozkyFaktury", "prilohy")``.

        Args:
            names: Relation/sub-evidence names to include
        """
        self.default_url_params["relations"] = ",".join(names)

    def set_includes(self, *paths: str) -> None:
        """
        Include the given related objects in the response, e.g.
        ``set_includes("faktura-vydana/stredisko")``.

        Args:
            paths: Include paths
        """
        self.default_url_params["includes"] = ",".join(paths)

    def iterate_all(self, page_size: int = 100) -> Iterator[Dict[str, Any]]:
        """
        Iterate over all records of the current evidence, transparently
        paging through the results using ``limit``/``start``.

        Args:
            page_size: Number of records to fetch per page

        Yields:
            Individual records
        """
        start = 0
        while True:
            self.set_limit(page_size)
            self.set_start(start)
            page = self.get_all_from_abraflexi()
            if not page:
                return
            for record in page:
                yield record
            if len(page) < page_size:
                return
            start += page_size

    # ------------------------------------------------------------------
    # Evidence metadata & summation
    # ------------------------------------------------------------------

    def get_properties(self) -> Union[Dict, List, bool]:
        """Get the list of properties (fields) supported by the current evidence."""
        return self.perform_request("properties.json")

    def get_reports(self) -> Union[Dict, List, bool]:
        """Get the list of printable reports available for the current evidence."""
        return self.perform_request("reports.json")

    def get_relations_list(self) -> Union[Dict, List, bool]:
        """Get the list of sub-evidences (relations) available for the current evidence."""
        return self.perform_request("relations.json")

    def get_sum(self, conditions: Optional[Dict[str, Any]] = None) -> Union[Dict, bool]:
        """
        Get summation (totals) for the current evidence, optionally
        combined with the currently-set filter.

        Args:
            conditions: Additional URL parameters to apply to the request

        Returns:
            Summation dictionary, or False on error
        """
        previous_params = dict(self.default_url_params)
        previous_filter = self.filter
        suffix = "$sum.json"
        if self.filter:
            # $sum must be combined as /(filter)/$sum; perform_request's
            # generic filter handling would append it after $sum instead,
            # so build the suffix explicitly and suppress the automatic
            # filter application for this one request.
            encoded_filter = quote(self.filter, safe="()='*,<>!")
            suffix = f"({encoded_filter})/$sum.json"
        if conditions:
            self.default_url_params.update(conditions)
        try:
            self.filter = None
            result = self.perform_request(suffix)
        finally:
            self.default_url_params = previous_params
            self.filter = previous_filter
        namespace = (
            result.get(self.NAMESPACE, result) if isinstance(result, dict) else result
        )
        if isinstance(namespace, dict):
            return namespace.get("sum", namespace)
        return namespace

    def get_columns(
        self,
        columns: List[str],
        conditions: Optional[Dict[str, Any]] = None,
        evidence: Optional[str] = None,
    ) -> List[Dict[str, Any]]:
        """
        Fetch a projection of specific columns from an evidence, optionally
        a different one than the object is currently bound to.

        Args:
            columns: Column names to fetch
            conditions: Filter conditions applied as URL parameters
                (e.g. ``{"firma": "code:FIRMA"}``)
            evidence: Evidence to query instead of the current one

        Returns:
            List of matching rows (each a dict of the requested columns)
        """
        previous_evidence = self.evidence
        previous_params = dict(self.default_url_params)
        previous_filter = self.filter
        previous_key = self.my_key
        try:
            # This is always a listing/filter query, never a detail fetch
            # of the object's own currently-loaded record - clear the
            # identifier so it can't leak into an unrelated evidence.
            self.my_key = None
            if evidence:
                self.set_evidence(evidence)
            else:
                self._update_api_url()
            self.default_url_params["detail"] = "custom:" + ",".join(columns)
            if conditions:
                self.default_url_params.update(conditions)
            result = self.get_all_from_abraflexi()
        finally:
            self.default_url_params = previous_params
            self.filter = previous_filter
            self.my_key = previous_key
            if evidence:
                self.set_evidence(previous_evidence)
            else:
                self._update_api_url()
        return result if isinstance(result, list) else []

    # ------------------------------------------------------------------
    # Session authentication
    # ------------------------------------------------------------------

    def login(self, username: str, password: str, otp: Optional[str] = None) -> bool:
        """
        Authenticate against AbraFlexi and obtain a session token
        (``authSessionId``), storing it for use in subsequent requests.

        Args:
            username: AbraFlexi username
            password: AbraFlexi password
            otp: One-time password, if two-factor auth is enabled

        Returns:
            True on successful authentication
        """
        payload = {"username": username, "password": password}
        if otp:
            payload["otp"] = otp

        result = self._perform_root_request(
            "login-logout/login.json", "POST", json.dumps(payload)
        )

        if isinstance(result, dict) and result.get("authSessionId"):
            self.auth_session_id = result["authSessionId"]
            self.default_http_headers["X-authSessionId"] = self.auth_session_id
            return True
        return False

    def logout(self, username: Optional[str] = None) -> bool:
        """
        Terminate an AbraFlexi user session.

        Args:
            username: Username to sign off; defaults to the currently
                configured user

        Returns:
            True on success
        """
        target_user = username or self.user
        result = self._perform_root_request(
            f"status/user/{target_user}/logout.json", "POST"
        )
        if target_user == self.user:
            self.default_http_headers.pop("X-authSessionId", None)
            self.auth_session_id = None
        return bool(result)

    def keep_alive(self) -> bool:
        """
        Keep the current session token alive. AbraFlexi session tokens
        expire after a period of inactivity; call this periodically
        (e.g. every 60 seconds) to keep a long-lived session usable.

        Returns:
            True on success
        """
        return bool(
            self._perform_root_request("login-logout/session-keep-alive.js", "GET")
        )

    # ------------------------------------------------------------------
    # User-defined queries
    # ------------------------------------------------------------------

    def call_user_query(
        self,
        query_id: Union[int, str],
        params: Optional[Dict[str, Union[str, List[str]]]] = None,
        method: str = "GET",
    ) -> Union[Dict, List, bool]:
        """
        Call a saved user-defined query ("uživatelský dotaz").

        Args:
            query_id: Identifier of the saved query
            params: Query parameters; a list value repeats the parameter in
                the URL, matching AbraFlexi's N-arity query parameter syntax
            method: HTTP method to use (GET or POST)

        Returns:
            Query result rows
        """
        query_params: List[tuple] = []
        for key, value in (params or {}).items():
            if isinstance(value, list):
                query_params.extend((key, v) for v in value)
            else:
                query_params.append((key, value))

        suffix = f"uzivatelsky-dotaz/{query_id}/call.json"
        if query_params:
            suffix += "?" + urlencode(query_params)

        # This endpoint hangs off the company root, not the current
        # evidence, so temporarily clear it while building the URL.
        previous_evidence = self.evidence
        self.evidence = None
        try:
            return self.perform_request(suffix, method)
        finally:
            self.evidence = previous_evidence

    def __str__(self) -> str:
        """String representation."""
        ident = self.get_record_ident()
        return ident if ident else f"<{self.__class__.__name__}>"

    def __repr__(self) -> str:
        """Developer representation."""
        return f"{self.__class__.__name__}(evidence={self.evidence!r}, id={self.get_record_id()})"
