Batch operations, actions and locking
========================================

Actions
-------

AbraFlexi records a delete/cancel/lock as a body-level ``@action``
attribute rather than a different HTTP verb. ``ReadWrite`` exposes the
common ones directly:

.. code-block:: python

   record.lock()               # @action=lock
   record.unlock()             # @action=unlock
   record.lock_for_ucetni()    # @action=lock-for-ucetni
   record.storno()             # @action=storno (cancel a document)

For evidence-specific business actions exposed under a dedicated URL
(``{id}/{action}.json``), use
:meth:`~python_abraflexi.read_write.ReadWrite.perform_action`:

.. code-block:: python

   invoice.perform_action("pay", {"castka": 1000})

Mass (filter-scoped) updates
--------------------------------

Update, or invoke an action on, every record matching a filter in a
single request:

.. code-block:: python

   # Add the VIP label to every price-list item supplied by FIRMA
   pricelist.mass_update("dodavatel = 'code:FIRMA'", {"stitky": "VIP"})

   # Lock every invoice already tagged as verified
   invoices.mass_update("stitky = 'code:OVERENO'", action="lock")

Batch insert/update
-----------------------

Send a list of records in one request:

.. code-block:: python

   client.batch_insert([{"nazev": "Item 1"}, {"nazev": "Item 2"}])
   client.batch_update([{"id": "1", "nazev": "..."}, {"id": "2", "nazev": "..."}])

Transactions
------------

By default a whole import is one database transaction (all-or-nothing).
Set ``atomic`` to commit each item independently — useful for very large
imports where an occasional failed row is acceptable:

.. code-block:: python

   client.set_atomic(True)

Use ``dry-run`` to validate without persisting anything:

.. code-block:: python

   client.set_dry_run(True)
