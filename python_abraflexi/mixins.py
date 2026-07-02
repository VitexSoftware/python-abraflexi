"""
Reusable mixins for AbraFlexi evidence classes.

These are Python ports of the shared traits used by the reference PHP
AbraFlexi library (``stitky``, ``subItems``, ``sum``, ``getChanges``,
``lock``, ``firma`` and ``email``). Each mixin is meant to be combined with
:class:`python_abraflexi.read_write.ReadWrite` (directly or via a further
subclass) — they rely on ``get_data_value``/``set_data_value``/
``get_record_ident``/``perform_request``/``get_connection_options`` being
available on ``self``.
"""

from typing import Any, Dict, List, Optional, Union


class LabelsMixin:
    """Adds label ("štítky") handling to an evidence class."""

    @staticmethod
    def _labels_to_list(labels: Union[None, str, List[str]]) -> List[str]:
        """Normalize a labels value (comma-separated string or list) to a list."""
        if not labels:
            return []
        if isinstance(labels, list):
            return labels
        return [label.strip() for label in str(labels).split(",") if label.strip()]

    def get_labels(self) -> List[str]:
        """Get all labels currently assigned to this record."""
        return self._labels_to_list(self.get_data_value("stitky"))

    def set_label(self, label: str) -> bool:
        """
        Add one of the labels available in the "Štítky" evidence to this
        record.

        Args:
            label: Label code to assign (e.g. "code:VIP")

        Returns:
            True on success
        """
        self.insert_to_abraflexi({"id": self.get_record_ident(), "stitky": label})
        return self.last_response_code == 201

    def unset_label(self, labels_to_remove: Union[str, List[str]]) -> bool:
        """
        Remove the given label(s) from this record, keeping the rest.

        Args:
            labels_to_remove: Label(s) to remove

        Returns:
            True on success
        """
        to_remove = set(self._labels_to_list(labels_to_remove))
        remaining = [label for label in self.get_labels() if label not in to_remove]
        self.insert_to_abraflexi(
            {
                "id": self.get_record_ident(),
                "stitky@removeAll": "true",
                "stitky": remaining,
            }
        )
        return self.last_response_code == 201

    def unset_labels(self) -> bool:
        """Remove all labels from this record."""
        self.insert_to_abraflexi(
            {"id": self.get_record_ident(), "stitky@removeAll": "true"}
        )
        return self.last_response_code == 201


class SubItemsMixin:
    """Adds document sub-item ("položky") handling to an evidence class."""

    _SUB_MENU_NAMES = ("polozkyFaktury", "polozkyDokladu")

    def get_sub_menu_name(self) -> Optional[str]:
        """Get the name of the sub-item collection field present on this record, if any."""
        data = self.get_data()
        for name in self._SUB_MENU_NAMES:
            if name in data:
                return name
        return None

    def get_sub_items(self) -> List[Dict[str, Any]]:
        """Get the sub-items (e.g. invoice lines) of this record."""
        menu_name = self.get_sub_menu_name()
        return self.get_data_value(menu_name, []) if menu_name else []

    def set_sub_items(self, subitems: List[Dict[str, Any]]) -> bool:
        """Replace the sub-items of this record."""
        menu_name = self.get_sub_menu_name() or "polozkyDokladu"
        self.set_data_value(menu_name, subitems)
        return True

    def add_array_to_branch(
        self,
        data: Dict[str, Any],
        relation_path: Optional[str] = None,
        remove_all: bool = False,
    ) -> bool:
        """
        Append a single item to a sub-item collection (without saving).

        Args:
            data: Item data to append
            relation_path: Sub-item field name; defaults to the field
                already present on this record, or "polozkyDokladu"
            remove_all: If True, mark the whole collection for replacement
                (``@removeAll``) instead of appending to what the server
                already has

        Returns:
            True
        """
        relation_path = relation_path or self.get_sub_menu_name() or "polozkyDokladu"
        branch_data = list(self.get_data_value(relation_path, []))
        branch_data.append(data)

        if remove_all:
            self.set_data_value(f"{relation_path}@removeAll", "true")

        self.set_data_value(relation_path, branch_data)
        return True


class SumMixin:
    """Adds summation ("sumace") support to an evidence class."""

    def get_sum_from_abraflexi(
        self, conditions: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """
        Get summation (totals) for this evidence, optionally filtered.

        Args:
            conditions: Additional URL parameters applied to the request

        Returns:
            Summation dictionary
        """
        return self.get_sum(conditions)


class RecordChangesMixin:
    """Adds per-record change history to an evidence class."""

    def get_record_changes(self) -> List[Dict[str, Any]]:
        """
        Get the change history ("Přehled změn záznamu") for this record.

        Returns:
            List of change entries
        """
        if not self.get_record_ident():
            raise ValueError("Cannot get record changes without record identifier")
        result = self.perform_request(f"{self.get_record_ident()}/zmeny.json")
        if isinstance(result, dict):
            namespace = result.get(self.NAMESPACE, result)
            if isinstance(namespace, dict):
                return namespace.get("zmeny", [])
        return result if isinstance(result, list) else []


class LockMixin:
    """Adds lock-state inspection to an evidence class.

    Locking/unlocking itself (``lock()``/``unlock()``/``lock_for_ucetni()``)
    is provided by :class:`~python_abraflexi.read_write.ReadWrite`; this
    mixin adds convenience read accessors for the ``zamekK`` field.
    """

    def is_locked(self) -> bool:
        """Check whether this record is currently locked."""
        lock_value = self.get_data_value("zamekK")
        if lock_value is None:
            raise ValueError("zamekK is not set on this record")
        return lock_value != "zamek.otevreno"

    def get_lock_type(self) -> str:
        """Get the lock type (``zamekK`` without the ``zamek.`` prefix)."""
        lock_value = self.get_data_value("zamekK")
        if lock_value is None:
            raise ValueError("zamekK is not set on this record")
        return lock_value.replace("zamek.", "", 1)


class FirmaMixin:
    """Adds lazy access to the related company ("firma") record."""

    def get_firma_object(self, options: Optional[Dict[str, Any]] = None) -> Any:
        """
        Get an :class:`~python_abraflexi.evidences.adresar.Adresar` instance
        for this record's ``firma`` relation, loading it on first access.

        Args:
            options: Extra options merged into the connection options used
                to construct the ``Adresar`` instance

        Returns:
            Adresar instance
        """
        if getattr(self, "_firma_object", None) is None:
            from .evidences.adresar import Adresar

            merged_options = {**self.get_connection_options(), **(options or {})}
            self._firma_object = Adresar(self.get_data_value("firma"), merged_options)
        return self._firma_object


class EmailMixin:
    """
    Adds recipient-email resolution to a document evidence class.

    Resolution order: the document's own "kontaktEmail" field, then its
    related company's email, falling back to the company's primary (or
    purpose-matching) contact email.
    """

    _PURPOSE_CODES = ("Fak", "Obj", "Nab", "Ppt", "Skl", "Pok")

    def get_email(self) -> str:
        """Get the single best recipient email address for this document."""
        contact_email = self.get_data_value("kontaktEmail")
        if contact_email:
            return contact_email

        addresser = self._load_addresser()
        email = addresser.get_data_value("email")
        if not email:
            email = addresser.get_notification_email_address()
        return email or ""

    def get_recipients(self, purpose: str = "") -> str:
        """
        Get a comma-separated list of recipient email addresses for this
        document.

        Args:
            purpose: Contact purpose (Fak|Obj|Nab|Ppt|Skl|Pok); auto-detected
                from the evidence class name if omitted

        Returns:
            Comma-separated list of unique email addresses
        """
        recipients: List[str] = []

        contact_email = self.get_data_value("kontaktEmail")
        if contact_email:
            recipients.append(contact_email)

        email = self.get_data_value("email")
        if email:
            recipients.append(email)

        firma = self.get_data_value("firma")
        if firma:
            addresser = self._load_addresser()
            contacts = addresser.get_notification_email_address(
                purpose or self._doc_type_to_purpose()
            )
            if contacts:
                recipients.extend(c for c in contacts.split(",") if c)

        seen: List[str] = []
        for recipient in recipients:
            if recipient not in seen:
                seen.append(recipient)
        return ",".join(seen)

    def _load_addresser(self) -> Any:
        from .evidences.adresar import Adresar

        options = {**self.get_connection_options(), "detail": "custom:email"}
        return Adresar(self.get_data_value("firma"), options)

    def _doc_type_to_purpose(self) -> str:
        """Map the evidence class name to a Fak|Obj|Nab|Ppt|Skl|Pok contact purpose."""
        class_name = self.__class__.__name__
        prefix = "Ppt" if class_name.startswith("Poptavka") else class_name[:3]
        return prefix if prefix in self._PURPOSE_CODES else ""
