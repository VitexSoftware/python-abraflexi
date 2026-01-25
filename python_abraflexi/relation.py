"""
Relation handling for AbraFlexi.

Relations represent links to other evidence records.
"""

from typing import Union, Optional


class Relation:
    """
    Represents a relation to another evidence record.

    Relations can be specified as:
    - Integer ID: 123
    - Code: code:ABC123
    - External ID: ext:DB:232
    """

    def __init__(self, value: Union[int, str]):
        """
        Initialize relation.

        Args:
            value: Relation value (id, code:..., ext:...)
        """
        self.value = value
        self._id: Optional[int] = None
        self._code: Optional[str] = None
        self._ext: Optional[str] = None

        self._parse_value()

    def _parse_value(self):
        """Parse relation value into components."""
        if isinstance(self.value, int):
            self._id = self.value
        elif isinstance(self.value, str):
            if self.value.startswith("code:"):
                self._code = self.value[5:]
            elif self.value.startswith("ext:"):
                self._ext = self.value[4:]
            else:
                try:
                    self._id = int(self.value)
                except ValueError:
                    self._code = self.value

    @property
    def id(self) -> Optional[int]:
        """Get relation ID."""
        return self._id

    @property
    def code(self) -> Optional[str]:
        """Get relation code."""
        return self._code

    @property
    def ext(self) -> Optional[str]:
        """Get relation external ID."""
        return self._ext

    def __str__(self) -> str:
        """String representation of relation."""
        return str(self.value)

    def __repr__(self) -> str:
        """Developer representation of relation."""
        return f"Relation({self.value!r})"

    def to_dict(self) -> Union[int, str]:
        """Convert relation to API format."""
        return self.value
