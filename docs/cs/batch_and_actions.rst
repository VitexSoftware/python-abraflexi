Dávkové operace, akce a zamykání
====================================

Akce
----

Smazání, storno či zamknutí záznamu řeší AbraFlexi pomocí atributu
``@action`` na úrovni těla požadavku, nikoliv jinou HTTP metodou. Třída
``ReadWrite`` nabízí přímo ty nejběžnější:

.. code-block:: python

   record.lock()               # @action=lock
   record.unlock()             # @action=unlock
   record.lock_for_ucetni()    # @action=lock-for-ucetni
   record.storno()             # @action=storno (stornování dokladu)

Pro evidenčně specifické obchodní akce dostupné na vyhrazené URL
(``{id}/{action}.json``) použijte metodu
:meth:`~python_abraflexi.read_write.ReadWrite.perform_action`:

.. code-block:: python

   invoice.perform_action("pay", {"castka": 1000})

Dávkové úpravy podle filtru
-------------------------------

Aktualizaci, nebo vyvolání akce, lze najednou provést nad všemi
záznamy odpovídajícími filtru:

.. code-block:: python

   # Přidá štítek VIP všem položkám ceníku od dodavatele FIRMA
   pricelist.mass_update("dodavatel = 'code:FIRMA'", {"stitky": "VIP"})

   # Zamkne všechny faktury už označené jako ověřené
   invoices.mass_update("stitky = 'code:OVERENO'", action="lock")

Dávkové vložení/aktualizace
---------------------------------

Odeslání seznamu záznamů v jednom požadavku:

.. code-block:: python

   client.batch_insert([{"nazev": "Položka 1"}, {"nazev": "Položka 2"}])
   client.batch_update([{"id": "1", "nazev": "..."}, {"id": "2", "nazev": "..."}])

Transakční zpracování
-------------------------

Ve výchozím stavu proběhne celý import v jedné databázové transakci
(vše, nebo nic). Nastavením ``atomic`` se každá položka uloží ve
vlastní transakci — vhodné pro velmi rozsáhlé importy, kde je přijatelné,
že se ojedinělý řádek neuloží:

.. code-block:: python

   client.set_atomic(True)

Pomocí ``dry-run`` lze data ověřit bez jejich skutečného uložení:

.. code-block:: python

   client.set_dry_run(True)
