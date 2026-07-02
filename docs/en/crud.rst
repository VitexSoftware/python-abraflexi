CRUD and identifiers
=====================

Reading records
----------------

.. code-block:: python

   from python_abraflexi import ReadOnly

   record = ReadOnly(123, {"url": "...", "company": "demo", "evidence": "adresar"})
   print(record.get_data_value("nazev"))

   listing = ReadOnly(None, {"url": "...", "company": "demo", "evidence": "adresar"})
   rows = listing.get_all_from_abraflexi()

Writing records
-----------------

Use :class:`~python_abraflexi.ReadWrite` for insert/update/delete:

.. code-block:: python

   from python_abraflexi import ReadWrite

   record = ReadWrite(None, {"url": "...", "company": "demo", "evidence": "adresar"})
   record.set_data_value("nazev", "ACME s.r.o.")
   record.insert_to_abraflexi()          # PUT

   record.set_data_value("nazev", "ACME a.s.")
   record.update()                       # POST

   record.delete()                       # DELETE

   # insert-or-update depending on whether the record already has an id
   record.save()

``atomic`` and ``dry-run`` modes
-----------------------------------

.. code-block:: python

   record.set_atomic(True)    # ?atomic=true - each item its own transaction
   record.set_dry_run(True)   # ?dry-run=true - validate without saving

Removing external identifiers
-------------------------------

``update``/``save`` accept ``remove_external_ids``, matching AbraFlexi's
``@removeExternalIds`` attribute:

.. code-block:: python

   # Remove every external id starting with "SYSTEM"
   record.update(remove_external_ids="SYSTEM")

   # Remove all external ids
   record.update(remove_external_ids="")

Record identifiers
--------------------

AbraFlexi records can be addressed by any of the following identifier
forms — pass them directly as the ``init`` constructor argument, or use
:class:`~python_abraflexi.Relation` to build/parse one:

============  =========================  ================================
Prefix        Example                    Meaning
============  =========================  ================================
*(none)*      ``123``                    Internal numeric ID (assigned by
                                          AbraFlexi, cannot be changed)
``code:``     ``code:CZK``               User-assigned code/abbreviation
``ext:``      ``ext:SHOP:123``           External identifier
                                          (``system:value``)
``ean:``      ``ean:4710937332698``      EAN barcode
``plu:``      ``plu:4020``               PLU code
``vatid:``    ``vatid:CZ28019920``       VAT ID (DIČ / IČ DPH)
``in:``       ``in:28019920``            Company registration number (IČO)
``iban:``     ``iban:CZ1201...``         IBAN
``key:``      ``key:550e8400e2...``      Internal UUID key
``ws:``       ``ws:{company-uuid}:66``   Hybrid identifier
============  =========================  ================================

.. code-block:: python

   from python_abraflexi import Relation

   rel = Relation("code:CZK")
   rel.code   # "CZK"

   rel = Relation("vatid:CZ28019920")
   rel.vat_id  # "CZ28019920"

Multiple identifiers can be combined (useful for incremental sync from an
external system) using the bracket syntax directly in a string value:
``"[123][code:CZK][ext:SHOP:abc]"``.
