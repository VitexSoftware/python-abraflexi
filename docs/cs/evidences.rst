Evidenční třídy a mixiny
===========================

Balíček ``python_abraflexi.evidences`` obsahuje konkrétní, hotové třídy
pro vybrané evidence AbraFlexi, sestavené kombinací
:class:`~python_abraflexi.read_write.ReadWrite` se znovupoužitelnými
mixiny z modulu :mod:`python_abraflexi.mixins`. Můžete je použít přímo,
nebo jako vzor pro vlastní evidenční třídy.

Vytvoření vlastní evidenční třídy
--------------------------------------

.. code-block:: python

   from python_abraflexi import ReadWrite

   class FakturaPrijata(ReadWrite):
       def __init__(self, init=None, options=None):
           if options is None:
               options = {}
           options = {**options, "evidence": "faktura-prijata"}
           super().__init__(init, options)

Podle potřeby přimíchejte sdílené chování:

.. code-block:: python

   from python_abraflexi import ReadWrite
   from python_abraflexi.mixins import LabelsMixin, SumMixin, LockMixin

   class FakturaPrijata(LabelsMixin, SumMixin, LockMixin, ReadWrite):
       def __init__(self, init=None, options=None):
           if options is None:
               options = {}
           options = {**options, "evidence": "faktura-prijata"}
           super().__init__(init, options)

Dostupné mixiny
-------------------

``LabelsMixin``
   ``get_labels()``, ``set_label(label)``, ``unset_label(labels)``,
   ``unset_labels()`` — správa pole "štítky".

``SubItemsMixin``
   ``get_sub_items()``, ``set_sub_items(items)``, ``get_sub_menu_name()``,
   ``add_array_to_branch(data, relation_path=None, remove_all=False)`` —
   práce s položkami dokladu (``polozkyFaktury`` / ``polozkyDokladu``).

``SumMixin``
   ``get_sum_from_abraflexi(conditions=None)`` — sumace evidence.

``RecordChangesMixin``
   ``get_record_changes()`` — historie změn tohoto záznamu.

``LockMixin``
   ``is_locked()``, ``get_lock_type()`` — čtení pole ``zamekK`` (samotné
   zamykání/odemykání poskytuje třída ``ReadWrite``).

``FirmaMixin``
   ``get_firma_object(options=None)`` — líné načtení relace ``firma`` do
   instance :class:`~python_abraflexi.Adresar`.

``EmailMixin``
   ``get_email()``, ``get_recipients(purpose="")`` — zjištění
   nejvhodnější e-mailové adresy (adres) příjemce pro doklad, s
   fallbackem na kontakty přiřazené firmy.

FakturaVydana (faktura vydaná)
------------------------------------

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

   # zděděno z ReadWrite
   invoice.get_qr_code_base64()
   invoice.export_report(report_name="dodaciList")

   # zděděno z mixinů
   invoice.get_labels()
   invoice.get_firma_object().get_notification_email_address()
   invoice.get_email()
   invoice.get_record_changes()
   invoice.lock()

Adresar (adresář)
----------------------

.. code-block:: python

   from python_abraflexi import Adresar

   customer = Adresar(123, options)

   customer.get_notification_email_address()          # primární kontakt, jinak e-mail firmy
   customer.get_notification_email_address("Obj")      # kontakt určený pro objednávky
   customer.get_cell_phone_number()
   customer.get_any_phone_number()
   customer.get_bank_account_number()                  # řádky z adresar-bankovni-ucet
