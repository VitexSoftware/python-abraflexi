CRUD operace a identifikátory
================================

Čtení záznamů
--------------

.. code-block:: python

   from python_abraflexi import ReadOnly

   record = ReadOnly(123, {"url": "...", "company": "demo", "evidence": "adresar"})
   print(record.get_data_value("nazev"))

   listing = ReadOnly(None, {"url": "...", "company": "demo", "evidence": "adresar"})
   rows = listing.get_all_from_abraflexi()

Zápis záznamů
--------------

Pro vkládání/aktualizaci/mazání použijte třídu
:class:`~python_abraflexi.ReadWrite`:

.. code-block:: python

   from python_abraflexi import ReadWrite

   record = ReadWrite(None, {"url": "...", "company": "demo", "evidence": "adresar"})
   record.set_data_value("nazev", "ACME s.r.o.")
   record.insert_to_abraflexi()          # PUT

   record.set_data_value("nazev", "ACME a.s.")
   record.update()                       # POST

   record.delete()                       # DELETE

   # vloží nový záznam, nebo aktualizuje existující podle přítomnosti id
   record.save()

Režimy ``atomic`` a ``dry-run``
-----------------------------------

.. code-block:: python

   record.set_atomic(True)    # ?atomic=true - každá položka ve vlastní transakci
   record.set_dry_run(True)   # ?dry-run=true - ověří data bez uložení

Odstranění externích identifikátorů
---------------------------------------

Metody ``update``/``save`` přijímají parametr ``remove_external_ids``,
který odpovídá atributu AbraFlexi ``@removeExternalIds``:

.. code-block:: python

   # Odstraní všechny externí identifikátory začínající na "SYSTEM"
   record.update(remove_external_ids="SYSTEM")

   # Odstraní všechny externí identifikátory
   record.update(remove_external_ids="")

Identifikátory záznamů
--------------------------

Záznamy AbraFlexi lze adresovat kterýmkoliv z následujících typů
identifikátorů — zadejte je přímo jako argument ``init`` konstruktoru,
nebo použijte třídu :class:`~python_abraflexi.Relation` pro jejich
sestavení či rozbor:

============  =========================  ================================
Prefix        Příklad                    Význam
============  =========================  ================================
*(žádný)*     ``123``                    Interní číselné ID (přiděluje
                                          AbraFlexi, nelze měnit)
``code:``     ``code:CZK``               Uživatelský kód/zkratka
``ext:``      ``ext:SHOP:123``           Externí identifikátor
                                          (``systém:hodnota``)
``ean:``      ``ean:4710937332698``      Čárový kód EAN
``plu:``      ``plu:4020``               Kód PLU
``vatid:``    ``vatid:CZ28019920``       DIČ / IČ DPH
``in:``       ``in:28019920``            IČO
``iban:``     ``iban:CZ1201...``         IBAN
``key:``      ``key:550e8400e2...``      Interní klíč (UUID)
``ws:``       ``ws:{uuid firmy}:66``     Hybridní identifikátor
============  =========================  ================================

.. code-block:: python

   from python_abraflexi import Relation

   rel = Relation("code:CZK")
   rel.code   # "CZK"

   rel = Relation("vatid:CZ28019920")
   rel.vat_id  # "CZ28019920"

Více identifikátorů lze zkombinovat (užitečné při inkrementální
synchronizaci z externího systému) pomocí hranatých závorek přímo v
řetězcové hodnotě: ``"[123][code:CZK][ext:SHOP:abc]"``.
