Attachments
===========

Uploading
---------

.. code-block:: python

   attachment_id = record.add_attachment("invoice.pdf", pdf_bytes, "application/pdf")
   attachment_id = record.add_attachment_from_file("/path/to/invoice.pdf")

Listing and metadata
------------------------

.. code-block:: python

   record.list_attachments()          # GET {id}/prilohy
   record.get_attachment(attach_id)   # GET {id}/prilohy/{attach_id}

Downloading
-----------

.. code-block:: python

   raw_bytes = record.download_attachment(attach_id)
   thumbnail_bytes = record.get_attachment_thumbnail(attach_id, width=200, height=200)

Deleting
--------

.. code-block:: python

   record.delete_attachment(attach_id)

Company settings attachments (logo, signature)
---------------------------------------------------

Logo and signature/stamp attachments on the company settings
(``nastaveni``) record use a dedicated, non-listable endpoint in
AbraFlexi (``GET``/``PUT``/``DELETE`` on ``nastaveni/1/logo`` or
``nastaveni/1/podpis-razitko``) rather than the generic attachment
endpoints above; use
:meth:`~python_abraflexi.read_only.ReadOnly.perform_request` directly for
that case.
