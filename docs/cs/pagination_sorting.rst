Stránkování a řazení
=======================

Stránkování
-----------

.. code-block:: python

   client.set_limit(100)   # ?limit=100
   client.set_start(200)   # ?start=200
   page = client.get_all_from_abraflexi()

   client.set_add_row_count(True)  # ?add-row-count=true - vrátí i celkový počet záznamů
   client.row_count  # naplní se po dokončení požadavku

Automatické stránkování
---------------------------

Metoda :meth:`~python_abraflexi.read_only.ReadOnly.iterate_all`
transparentně prochází celou evidenci po stránkách a postupně vrací
jednotlivé záznamy:

.. code-block:: python

   for record in client.iterate_all(page_size=100):
       print(record["nazev"])

Řazení
------

.. code-block:: python

   client.set_order("nazev")        # ?order=nazev@A  (vzestupně)
   client.set_order("nazev", "D")   # ?order=nazev@D  (sestupně)
