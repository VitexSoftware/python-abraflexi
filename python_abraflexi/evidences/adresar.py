"""
AbraFlexi - Address book ("adresář") evidence.
"""

from typing import Any, Dict, List, Optional, Union

from ..mixins import LabelsMixin, RecordChangesMixin, SubItemsMixin
from ..read_write import ReadWrite

_CONTACT_PURPOSE_FIELDS = (
    "odesilatFak",
    "odesilatObj",
    "odesilatNab",
    "odesilatPpt",
    "odesilatSkl",
    "odesilatPok",
)


class Adresar(LabelsMixin, SubItemsMixin, RecordChangesMixin, ReadWrite):
    """Address book entry (company or person)."""

    def __init__(
        self,
        init: Optional[Union[int, str, Dict]] = None,
        options: Optional[Dict[str, Any]] = None,
    ):
        """
        Initialize an Adresar instance.

        Args:
            init: Record ID, code, or initial data
            options: Configuration options (see :class:`ReadOnly`)
        """
        if options is None:
            options = {}
        options = {**options, "evidence": "adresar"}
        super().__init__(init, options)

    def _fetch_contact_projection(self, fields: List[str]) -> Dict[str, Any]:
        """
        Fetch this record together with its contacts, projected to just
        ``fields`` (plus the purpose flags needed to pick the right
        contact).

        Args:
            fields: Top-level/contact field names to project (e.g. ["email"])

        Returns:
            The first matching row, or an empty dict if none was found
        """
        contact_fields = ",".join(("primarni", *fields, *_CONTACT_PURPOSE_FIELDS))
        detail = f"custom:id,{','.join(fields)},kontakty({contact_fields})"

        previous_params = dict(self.default_url_params)
        previous_ignore = self.ignore_not_found
        try:
            self.default_url_params["detail"] = detail
            self.default_url_params["relations"] = "kontakty"
            self.ignore_not_found = True
            raw = self.perform_request()
        finally:
            self.default_url_params = previous_params
            self.ignore_not_found = previous_ignore

        if isinstance(raw, list):
            return raw[0] if raw else {}
        if isinstance(raw, dict):
            return raw
        return {}

    def get_notification_email_address(self, purpose: str = "") -> str:
        """
        Get the email address to notify, preferring a primary (or
        purpose-matching) contact over the address's own email.

        Args:
            purpose: Contact purpose - one of Fak|Obj|Nab|Ppt|Skl|Pok

        Returns:
            Email address of the primary contact, the address's own email,
            or an empty string if none is usable
        """
        email = ""
        record = self._fetch_contact_projection(["email"])

        if str(record.get("email", "")).strip():
            email = record["email"]

        contacts = record.get("kontakty") or []
        candidates: List[str] = []
        for kontakt in contacts:
            if purpose:
                flag = f"odesilat{purpose[:1].upper()}{purpose[1:]}"
                if kontakt.get(flag) == "true" and kontakt.get("email"):
                    candidates.append(kontakt["email"])
            else:
                if (
                    kontakt.get("primarni") == "true"
                    and str(kontakt.get("email", "")).strip()
                ):
                    candidates.append(kontakt["email"])
                    break

        if candidates:
            email = ",".join(dict.fromkeys(candidates))

        return email

    def get_cell_phone_number(self, purpose: str = "") -> Optional[str]:
        """
        Get the cell phone number to use, preferring a primary (or
        purpose-matching) contact over the address's own number.

        Args:
            purpose: Contact purpose - one of Fak|Obj|Nab|Ppt|Skl|Pok

        Returns:
            Cell phone number, or None if none is usable
        """
        mobil = None
        record = self._fetch_contact_projection(["mobil"])

        if str(record.get("mobil", "")).strip():
            mobil = record["mobil"]

        contacts = record.get("kontakty") or []
        candidates: List[str] = []
        for kontakt in contacts:
            if purpose:
                flag = f"odesilat{purpose[:1].upper()}{purpose[1:]}"
                if kontakt.get(flag) == "true" and kontakt.get("mobil"):
                    candidates.append(kontakt["mobil"])
            else:
                if (
                    kontakt.get("primarni") == "true"
                    and str(kontakt.get("mobil", "")).strip()
                ):
                    candidates.append(kontakt["mobil"])
                    break

        if candidates:
            mobil = ",".join(dict.fromkeys(candidates))

        return mobil

    def get_any_phone_number(self, purpose: str = "") -> Optional[str]:
        """
        Get any usable phone number, preferring mobile over landline and a
        primary contact over the address's own number.

        Args:
            purpose: Contact purpose - one of Fak|Obj|Nab|Ppt|Skl|Pok

        Returns:
            Phone number, or None if none is usable
        """
        phone_no = None
        record = self._fetch_contact_projection(["mobil", "tel"])

        if str(record.get("mobil", "")).strip():
            phone_no = record["mobil"]
        if str(record.get("tel", "")).strip():
            phone_no = record["tel"]

        contacts = record.get("kontakty") or []
        if contacts:
            for kontakt in contacts:
                if (
                    kontakt.get("primarni") == "true"
                    and str(kontakt.get("mobil", "")).strip()
                ):
                    phone_no = kontakt["mobil"]
                    break

            if phone_no is None:
                for kontakt in contacts:
                    if str(kontakt.get("mobil", "")).strip():
                        phone_no = kontakt["mobil"]
                        break

        return phone_no

    def get_bank_account_number(
        self, address: Optional[Union[int, str]] = None
    ) -> List[Dict[str, Any]]:
        """
        Get the bank account(s) registered for this (or another) address.

        Args:
            address: Address identifier to look up; defaults to this record

        Returns:
            List of rows with "buc" (account number) and "smerKod" (bank code)
        """
        if address is None:
            address = self.my_key
        return self.get_columns(
            ["buc", "smerKod"],
            conditions={"firma": address},
            evidence="adresar-bankovni-ucet",
        )

    def get_email(self) -> str:
        """Get the address's notification email address."""
        return self.get_notification_email_address()

    def get_sum_from_abraflexi(
        self, conditions: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Address book entries have no summation support."""
        return {}
