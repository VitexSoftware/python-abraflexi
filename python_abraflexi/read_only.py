"""
ReadOnly class for reading data from AbraFlexi REST API.

This is the base class for all AbraFlexi operations.
"""

import os
import json
import logging
from typing import Optional, Dict, Any, Union, List
from datetime import datetime, date
from urllib.parse import urlencode, urlparse, parse_qs
import requests
from requests.auth import HTTPBasicAuth

from .exceptions import (
    AbraFlexiException,
    ConnectionException,
    AuthenticationException,
    NotFoundException,
    ValidationException,
)
from .relation import Relation


class ReadOnly:
    """
    Base class for read-only interaction with AbraFlexi API.

    This class handles HTTP communication, authentication, and data parsing.
    """

    # Library version
    LIB_VERSION = "1.0.0"

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
        self.session.headers.update({
            "User-Agent": f"python-abraflexi v{self.LIB_VERSION} https://github.com/VitexSoftware/python-abraflexi"
        })

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
    ) -> Union[Dict, List, bool]:
        """
        Perform HTTP request.

        Args:
            url_suffix: URL suffix
            method: HTTP method
            format_type: Response format

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

        # Add default URL parameters
        if self.default_url_params:
            separator = "&" if "?" in url else "?"
            url += separator + urlencode(self.default_url_params)

        # Add filter
        if self.filter:
            separator = "&" if "?" in url else "?"
            url += separator + urlencode({"filter": self.filter})

        # Prepare headers
        headers = self.default_http_headers.copy()

        # Perform request
        try:
            self.logger.debug(f"{method} {url}")

            if method == "GET":
                response = self.session.get(url, headers=headers, timeout=self.timeout)
            elif method == "POST":
                response = self.session.post(
                    url,
                    data=self.post_fields,
                    headers={**headers, "Content-Type": "application/json"},
                    timeout=self.timeout,
                )
            elif method == "PUT":
                response = self.session.put(
                    url,
                    data=self.post_fields,
                    headers={**headers, "Content-Type": "application/json"},
                    timeout=self.timeout,
                )
            elif method == "DELETE":
                response = self.session.delete(url, headers=headers, timeout=self.timeout)
            else:
                raise ValueError(f"Unsupported HTTP method: {method}")

            self.last_response = response
            self.last_response_code = response.status_code

            # Handle response
            return self._parse_http_response(response)

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

    def _parse_http_response(self, response: requests.Response) -> Union[Dict, List, bool]:
        """
        Parse HTTP response.

        Args:
            response: Response object

        Returns:
            Parsed response data
        """
        # Handle status codes
        if response.status_code == 200:
            # Success - parse response
            return self._parse_response_body(response)
        elif response.status_code == 201:
            # Created
            return self._parse_response_body(response)
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
        elif response.status_code >= 400:
            self.logger.error(f"HTTP {response.status_code}: {response.text}")
            if self.throw_exception:
                raise AbraFlexiException(f"HTTP {response.status_code}: {response.text}")
            return False

        return True

    def _parse_response_body(self, response: requests.Response) -> Union[Dict, List, bool]:
        """
        Parse response body.

        Args:
            response: Response object

        Returns:
            Parsed data
        """
        if not response.content:
            return True

        try:
            data = response.json()

            # Extract results
            if self.NAMESPACE in data:
                namespace_data = data[self.NAMESPACE]

                # Check for errors
                if "success" in namespace_data and namespace_data["success"] == "false":
                    self._parse_errors(namespace_data)
                    if self.throw_exception:
                        error_msg = "; ".join([e.get("message", str(e)) for e in self.errors])
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
                            converted[key] = datetime.fromisoformat(value.replace("Z", ""))
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

    def __str__(self) -> str:
        """String representation."""
        ident = self.get_record_ident()
        return ident if ident else f"<{self.__class__.__name__}>"

    def __repr__(self) -> str:
        """Developer representation."""
        return f"{self.__class__.__name__}(evidence={self.evidence!r}, id={self.get_record_id()})"
