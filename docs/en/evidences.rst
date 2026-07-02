Evidence classes and mixins
=============================

``python_abraflexi.evidences`` contains concrete, ready-to-use classes for
specific AbraFlexi evidences, built by combining
:class:`~python_abraflexi.read_write.ReadWrite` with reusable mixins from
:mod:`python_abraflexi.mixins`. Use them as-is, or as a template for your
own evidence classes.

Building your own evidence class
------------------------------------

.. code-block:: python

   from python_abraflexi import ReadWrite

   class FakturaPrijata(ReadWrite):
       def __init__(self, init=None, options=None):
           if options is None:
               options = {}
           options = {**options, "evidence": "faktura-prijata"}
           super().__init__(init, options)

Mix in shared behaviour as needed:

.. code-block:: python

   from python_abraflexi import ReadWrite
   from python_abraflexi.mixins import LabelsMixin, SumMixin, LockMixin

   class FakturaPrijata(LabelsMixin, SumMixin, LockMixin, ReadWrite):
       def __init__(self, init=None, options=None):
           if options is None:
               options = {}
           options = {**options, "evidence": "faktura-prijata"}
           super().__init__(init, options)

Available mixins
--------------------

``LabelsMixin``
   ``get_labels()``, ``set_label(label)``, ``unset_label(labels)``,
   ``unset_labels()`` — manage the "štítky" (labels) field.

``SubItemsMixin``
   ``get_sub_items()``, ``set_sub_items(items)``, ``get_sub_menu_name()``,
   ``add_array_to_branch(data, relation_path=None, remove_all=False)`` —
   work with a document's line items (``polozkyFaktury`` /
   ``polozkyDokladu``).

``SumMixin``
   ``get_sum_from_abraflexi(conditions=None)`` — evidence summation.

``RecordChangesMixin``
   ``get_record_changes()`` — this record's change history.

``LockMixin``
   ``is_locked()``, ``get_lock_type()`` — inspect the ``zamekK`` field
   (locking/unlocking itself is provided by ``ReadWrite``).

``FirmaMixin``
   ``get_firma_object(options=None)`` — lazily resolve the ``firma``
   relation to an :class:`~python_abraflexi.Adresar` instance.

``EmailMixin``
   ``get_email()``, ``get_recipients(purpose="")`` — resolve the best
   recipient email address(es) for a document, falling back through the
   related company's contacts.

FakturaVydana (issued invoice)
----------------------------------

.. code-block:: python

   from python_abraflexi import FakturaVydana

   invoice = FakturaVydana(123, options)

   invoice.match_payment(bank_document, zbytek="zauctovat")
   invoice.cash_payment(1500, pokladna="code:POKLADNA")
   invoice.deduct_advance(advance_invoice)
   invoice.deduct_zdd(zdd_invoice)
   invoice.link_zdd(income_document)
   invoice.unlink_zdd()

   FakturaVydana.overdue_days(invoice.get_data_value("datSplat"))

   # inherited from ReadWrite
   invoice.get_qr_code_base64()
   invoice.export_report(report_name="dodaciList")

   # inherited from the mixins
   invoice.get_labels()
   invoice.get_firma_object().get_notification_email_address()
   invoice.get_email()
   invoice.get_record_changes()
   invoice.lock()

Adresar (address book)
---------------------------

.. code-block:: python

   from python_abraflexi import Adresar

   customer = Adresar(123, options)

   customer.get_notification_email_address()          # primary contact, falls back to firm email
   customer.get_notification_email_address("Obj")      # contact flagged for order notifications
   customer.get_cell_phone_number()
   customer.get_any_phone_number()
   customer.get_bank_account_number()                  # rows from adresar-bankovni-ucet
