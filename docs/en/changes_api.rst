Changes API
===========

Company-wide changes
------------------------

AbraFlexi can track every create/update/delete across all evidences under
a monotonically increasing global version number, ideal for incremental
synchronization. Use :class:`python_abraflexi.Changes`:

.. code-block:: python

   from python_abraflexi import Changes

   changes = Changes(None, {"url": "...", "company": "demo", "user": "...", "password": "..."})

   changes.enable()
   changes.get_status()  # True

   page = changes.get_changes(start=0, limit=500, evidences=["faktura-vydana"])
   page["changes"]         # list of change entries
   page["next"]            # version to continue from, or None
   page["global_version"]  # current global version

   changes.disable()

Synchronization pattern
---------------------------

1. Initial load: fetch the data you need, remembering the current
   ``global_version`` (pass ``add-global-version=true`` in
   ``default_url_params`` on a normal read to get it alongside the data).
2. Incremental sync: call ``get_changes(start=<last version>)``, apply the
   changes (create/update/delete as indicated by each entry's
   ``@operation``), and remember ``next`` as the new starting point.
3. Repeat step 2 periodically.

Per-record change history
-----------------------------

A different, per-record endpoint (``{evidence}/{id}/zmeny.json``) lists
the change history of a single record. Mix
:class:`~python_abraflexi.mixins.RecordChangesMixin` into an evidence
class to expose it:

.. code-block:: python

   invoice.get_record_changes()
