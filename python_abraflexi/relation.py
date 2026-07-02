"""
Relation handling for AbraFlexi.

Relations represent links to other evidence records.
"""

from typing import Union, Optional


class Relation:
    """
    Represents a relation to another evidence record.

    Relations can be specified using any of the identifier prefixes
    documented in "Identifikátory záznamů":

    - Integer ID: 123
    - Code: code:ABC123
    - External ID: ext:DB:232
    - EAN: ean:4710937332698
    - PLU: plu:4020
    - VAT ID: vatid:CZ28019920
    - Company ID (IČO): in:28019920
    - IBAN: iban:CZ1201000002801992
    - Internal key (UUID): key:550e8400e29b41d4a716
    - Hybrid identifier: ws:8ee0a075-67fa-4f92-880e-a7d65ab3c6e3:66
    """

    _PREFIXES = {
        "code": "_code",
        "ext": "_ext",
        "ean": "_ean",
        "plu": "_plu",
        "vatid": "_vat_id",
        "in": "_ico",
        "iban": "_iban",
        "key": "_key",
        "ws": "_hybrid",
    }

    def __init__(self, value: Union[int, str]):
        """
        Initialize relation.

        Args:
            value: Relation value (id, code:..., ext:..., ean:..., plu:...,
                vatid:..., in:..., iban:..., key:..., uuid:...)
        """
        self.value = value
        self._id: Optional[int] = None
        self._code: Optional[str] = None
        self._ext: Optional[str] = None
        self._ean: Optional[str] = None
        self._plu: Optional[str] = None
        self._vat_id: Optional[str] = None
        self._ico: Optional[str] = None
        self._iban: Optional[str] = None
        self._key: Optional[str] = None
        self._hybrid: Optional[str] = None

        self._parse_value()

    def _parse_value(self):
        """Parse relation value into components."""
        if isinstance(self.value, int):
            self._id = self.value
        elif isinstance(self.value, str):
            for prefix, attr in self._PREFIXES.items():
                if self.value.startswith(f"{prefix}:"):
                    setattr(self, attr, self.value[len(prefix) + 1 :])
                    return
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

    @property
    def ean(self) -> Optional[str]:
        """Get relation EAN (barcode) identifier."""
        return self._ean

    @property
    def plu(self) -> Optional[str]:
        """Get relation PLU identifier."""
        return self._plu

    @property
    def vat_id(self) -> Optional[str]:
        """Get relation VAT ID (DIČ/IČ DPH) identifier."""
        return self._vat_id

    @property
    def ico(self) -> Optional[str]:
        """Get relation company registration number (IČO) identifier."""
        return self._ico

    @property
    def iban(self) -> Optional[str]:
        """Get relation IBAN identifier."""
        return self._iban

    @property
    def key(self) -> Optional[str]:
        """Get relation internal key (UUID assigned by AbraFlexi) identifier."""
        return self._key

    @property
    def hybrid(self) -> Optional[str]:
        """Get relation hybrid identifier value ({company UUID}:{internal ID})."""
        return self._hybrid

    def __str__(self) -> str:
        """String representation of relation."""
        return str(self.value)

    def __repr__(self) -> str:
        """Developer representation of relation."""
        return f"Relation({self.value!r})"

    def to_dict(self) -> Union[int, str]:
        """Convert relation to API format."""
        return self.value
