English documentation
======================

.. toctree::
   :maxdepth: 2

   authentication
   crud
   filtering
   pagination_sorting
   detail_relations
   batch_and_actions
   attachments
   changes_api
   reports_and_queries
   evidences
   error_handling
   api_reference

Overview
--------

``python-abraflexi`` wraps the AbraFlexi REST API (JSON only) behind two
base classes:

- :class:`python_abraflexi.ReadOnly` — connection handling, URL building,
  request execution and response parsing.
- :class:`python_abraflexi.ReadWrite` — adds insert/update/delete, actions,
  batch operations, attachments and binary exports.

Two ready-made evidence classes are provided on top of these,
:class:`python_abraflexi.FakturaVydana` (issued invoices) and
:class:`python_abraflexi.Adresar` (address book), demonstrating how to
build your own by combining :class:`~python_abraflexi.read_write.ReadWrite`
with the reusable mixins in :mod:`python_abraflexi.mixins`.

Installation
------------

.. code-block:: bash

   pip install python-abraflexi

Quick start
-----------

.. code-block:: python

   from python_abraflexi import ReadWrite

   options = {
       "url": "https://demo.flexibee.eu",
       "company": "demo",
       "user": "winstrom",
       "password": "winstrom",
       "evidence": "adresar",
   }

   record = ReadWrite(None, options)
   record.set_data_value("nazev", "ACME s.r.o.")
   record.set_data_value("ic", "12345678")
   record.insert_to_abraflexi()

Connection options can also be supplied via environment variables:
``ABRAFLEXI_URL``, ``ABRAFLEXI_COMPANY``, ``ABRAFLEXI_LOGIN``,
``ABRAFLEXI_PASSWORD``, ``ABRAFLEXI_AUTHSESSID``, ``ABRAFLEXI_TIMEOUT``,
``ABRAFLEXI_EXCEPTIONS``.
