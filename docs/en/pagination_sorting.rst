Pagination and sorting
=======================

Pagination
----------

.. code-block:: python

   client.set_limit(100)   # ?limit=100
   client.set_start(200)   # ?start=200
   page = client.get_all_from_abraflexi()

   client.set_add_row_count(True)  # ?add-row-count=true - include total in response
   client.row_count  # populated after the request completes

Automatic paging
-------------------

:meth:`~python_abraflexi.read_only.ReadOnly.iterate_all` transparently
pages through an entire evidence, yielding one record at a time:

.. code-block:: python

   for record in client.iterate_all(page_size=100):
       print(record["nazev"])

Sorting
-------

.. code-block:: python

   client.set_order("nazev")        # ?order=nazev@A  (ascending)
   client.set_order("nazev", "D")   # ?order=nazev@D  (descending)
