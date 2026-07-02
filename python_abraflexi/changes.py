"""
Company-wide Changes API for AbraFlexi.

See "Changes API" (podpora.flexibee.eu/cs/articles/4744362-changes-api):
tracks create/update/delete operations across all evidences under a
monotonically increasing global version number, useful for incremental
synchronization of external systems.

For per-record change history use the ``RecordChangesMixin`` mixin
instead (``{evidence}/{id}/zmeny.json``), which is a different endpoint.
"""

from typing import Any, Dict, List, Optional, Union

from .read_write import ReadWrite


class Changes(ReadWrite):
    """Client for the company-wide AbraFlexi Changes API."""

    def __init__(
        self,
        init: Optional[Union[int, str, Dict]] = None,
        options: Optional[Dict[str, Any]] = None,
    ):
        """
        Initialize the Changes client.

        Args:
            init: Unused, kept for constructor compatibility
            options: Configuration options (see :class:`ReadOnly`)
        """
        if options is None:
            options = {}
        options = {**options, "evidence": "changes", "autoload": False}
        super().__init__(init, options)

    def get_changes(
        self,
        start: Optional[int] = None,
        limit: Optional[int] = None,
        evidences: Optional[List[str]] = None,
    ) -> Dict[str, Any]:
        """
        Get a page of recorded changes.

        Args:
            start: Global version to start listing from (inclusive);
                defaults to the beginning of tracked history
            limit: Maximum number of changes to return (server default 100,
                maximum 1000)
            evidences: Restrict the listing to these evidence names; all
                evidences are included if omitted

        Returns:
            Dict with ``changes`` (list of change records), ``next`` (the
            version to continue from, or ``None`` if there are no further
            changes) and ``global_version``.
        """
        previous_params = dict(self.default_url_params)
        try:
            if start is not None:
                self.default_url_params["start"] = start
            if limit is not None:
                self.default_url_params["limit"] = limit
            if evidences:
                self.default_url_params["evidence"] = list(evidences)
            raw = self.perform_request()
        finally:
            self.default_url_params = previous_params

        namespace = raw.get(self.NAMESPACE, {}) if isinstance(raw, dict) else {}
        return {
            "changes": namespace.get("changes", []),
            "next": namespace.get("next"),
            "global_version": namespace.get("@globalVersion"),
        }

    def enable(self) -> bool:
        """Enable change tracking for the current company."""
        return bool(self.perform_request("enable.json", "PUT"))

    def disable(self) -> bool:
        """Disable change tracking for the current company."""
        return bool(self.perform_request("disable.json", "PUT"))

    def get_status(self) -> bool:
        """Check whether change tracking is currently enabled."""
        result = self.perform_request("status.json")
        if isinstance(result, bool):
            return result
        if isinstance(result, str):
            return result.strip().lower() == "true"
        return bool(result)
