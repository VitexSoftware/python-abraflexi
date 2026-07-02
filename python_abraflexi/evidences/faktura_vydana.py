"""
AbraFlexi - Issued invoice ("faktura vydaná") evidence.
"""

from datetime import date, datetime
from typing import Any, Dict, Optional, Union

from ..mixins import (
    EmailMixin,
    FirmaMixin,
    LabelsMixin,
    LockMixin,
    RecordChangesMixin,
    SubItemsMixin,
    SumMixin,
)
from ..read_write import ReadWrite


def _as_code(value: str) -> str:
    """Ensure a bare code is passed as a "code:" identifier."""
    return value if ":" in value else f"code:{value}"


class FakturaVydana(
    LabelsMixin,
    FirmaMixin,
    SumMixin,
    SubItemsMixin,
    EmailMixin,
    RecordChangesMixin,
    LockMixin,
    ReadWrite,
):
    """Issued invoice."""

    def __init__(
        self,
        init: Optional[Union[int, str, Dict]] = None,
        options: Optional[Dict[str, Any]] = None,
    ):
        """
        Initialize a FakturaVydana instance.

        Args:
            init: Record ID, code, or initial data
            options: Configuration options (see :class:`ReadOnly`)
        """
        if options is None:
            options = {}
        options = {**options, "evidence": "faktura-vydana"}
        super().__init__(init, options)

    def match_payment(
        self, doklad: ReadWrite, zbytek: str = "ignorovat", overpay_to: str = ""
    ) -> bool:
        """
        Match this invoice against a payment document ("Párování plateb").

        Args:
            doklad: The paying document (Banka, InterniDoklad or
                PokladniPohyb instance)
            zbytek: How to handle any remainder - one of ne|zauctovat|
                ignorovat|castecnaUhrada|castecnaUhradaNeboZauctovat|
                castecnaUhradaNeboIgnorovat
            overpay_to: Document type code to use for an overpayment, if any

        Returns:
            True on success
        """
        sparovani: Dict[str, Any] = {
            "uhrazovanaFak": self.get_record_ident(),
            "uhrazovanaFak@type": self.evidence,
            "zbytek": zbytek,
        }
        match: Dict[str, Any] = {
            "id": doklad.get_record_ident(),
            "sparovani": sparovani,
        }
        if overpay_to:
            match["preplatek"] = {"typDokl": _as_code(overpay_to)}

        doklad.insert_to_abraflexi(match)
        return doklad.last_response_code == 201

    def cash_payment(self, value: float, **uhrada: Any) -> bool:
        """
        Pay this invoice in cash ("Hotovostní úhrada").

        Args:
            value: Amount to pay
            **uhrada: Optional payment properties: "pokladna" (cash
                register identifier, default "code:POKLADNA KČ"), "typDokl"
                (cash document type code, default "code:STANDARD"),
                "kurzKDatuUhrady" (bool, default False), "uhrazujiciDokl",
                "rada" (document series), "datumUhrady" (default today)

        Returns:
            True on success
        """
        uhrada.setdefault("pokladna", "code:POKLADNA KČ")
        uhrada.setdefault("typDokl", "code:STANDARD")
        uhrada.setdefault("kurzKDatuUhrady", False)
        uhrada.setdefault("datumUhrady", date.today().isoformat())
        uhrada["castka"] = value

        self.set_data_value("hotovostni-uhrada", uhrada)
        self.insert_to_abraflexi()
        return self.last_response_code == 201

    def deduct_advance(self, invoice: "FakturaVydana", **odpocet: Any) -> bool:
        """
        Deduct an advance invoice from this (tax document) invoice
        ("Odpočet záloh a ZDD").

        Args:
            invoice: The advance ("zálohová") invoice being deducted
            **odpocet: Deduction properties; "castkaMen" defaults to the
                advance invoice's total

        Returns:
            True on success
        """
        odpocet.setdefault("castkaMen", invoice.get_data_value("sumCelkem"))
        odpocet["doklad"] = invoice.get_record_ident()

        self.set_data_value("odpocty-zaloh", {"odpocet": odpocet})
        self.insert_to_abraflexi()
        return self.last_response_code == 201

    def deduct_zdd(self, invoice: "FakturaVydana", **odpocet: Any) -> bool:
        """
        Deduct an advance tax document (ZDD) from this invoice
        ("Odpočet záloh a ZDD").

        Args:
            invoice: The ZDD invoice being deducted
            **odpocet: Deduction properties; the "castka*Men" fields default
                to the ZDD invoice's corresponding totals

        Returns:
            True on success
        """
        odpocet.setdefault("castkaZaklMen", invoice.get_data_value("sumZklZakl"))
        odpocet.setdefault("castkaSnizMen", invoice.get_data_value("sumZklSniz"))
        odpocet.setdefault("castkaSniz2Men", invoice.get_data_value("sumZklSniz2"))
        odpocet.setdefault("castkaOsvMen", invoice.get_data_value("sumOsv"))
        odpocet.setdefault("id", "ext:odpocet1")
        odpocet["doklad"] = invoice.get_record_ident()

        self.set_data_value("odpocty-zaloh", {"odpocet": odpocet})
        self.insert_to_abraflexi()
        return self.last_response_code == 201

    def link_zdd(self, income: ReadWrite) -> bool:
        """
        Link an advance tax document (ZDD) to an income payment
        ("Vazby ZDD").

        Args:
            income: The income payment document (Banka or PokladniPohyb)

        Returns:
            True on success
        """
        bond_request = {
            "id": self.get_record_ident(),
            "vytvor-vazbu-zdd": {
                "uhrada": income.get_record_ident(),
                "uhrada@type": income.evidence,
            },
        }
        self.insert_to_abraflexi(bond_request)
        return self.last_response_code == 201

    def unlink_zdd(self, record_id: Optional[Union[int, str]] = None) -> bool:
        """
        Remove an advance tax document (ZDD) bonding ("Vazby ZDD").

        Args:
            record_id: Invoice record identifier; defaults to this record

        Returns:
            True on success
        """
        unbond_request = {
            "id": self.get_record_ident() if record_id is None else record_id,
            "zrus-vazbu-zdd": "true",
        }
        self.insert_to_abraflexi(unbond_request)
        return self.last_response_code == 201

    @staticmethod
    def overdue_days(due_date: Union[str, date, datetime]) -> int:
        """
        Get the number of days this invoice is overdue by.

        Args:
            due_date: Due date, as a date/datetime or "YYYY-MM-DD" string

        Returns:
            Positive number of days overdue, or a negative number of days
            remaining until due
        """
        if isinstance(due_date, datetime):
            due = due_date.date()
        elif isinstance(due_date, date):
            due = due_date
        elif isinstance(due_date, str):
            due = datetime.strptime(due_date[:10], "%Y-%m-%d").date()
        else:
            raise ValueError("due_date must be a date, datetime or ISO date string")

        return (date.today() - due).days
