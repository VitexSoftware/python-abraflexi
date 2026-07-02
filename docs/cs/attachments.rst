Přílohy
=======

Nahrání přílohy
-------------------

.. code-block:: python

   attachment_id = record.add_attachment("faktura.pdf", pdf_bytes, "application/pdf")
   attachment_id = record.add_attachment_from_file("/cesta/k/faktura.pdf")

Výpis a metadata
--------------------

.. code-block:: python

   record.list_attachments()          # GET {id}/prilohy
   record.get_attachment(attach_id)   # GET {id}/prilohy/{attach_id}

Stažení
-------

.. code-block:: python

   raw_bytes = record.download_attachment(attach_id)
   thumbnail_bytes = record.get_attachment_thumbnail(attach_id, width=200, height=200)

Smazání
-------

.. code-block:: python

   record.delete_attachment(attach_id)

Přílohy nastavení firmy (logo, podpis)
-------------------------------------------

Přílohy loga a podpisu/razítka na záznamu nastavení firmy (``nastaveni``)
používají v AbraFlexi vyhrazený, nevýpisový endpoint (``GET``/``PUT``/
``DELETE`` na ``nastaveni/1/logo`` nebo ``nastaveni/1/podpis-razitko``)
namísto výše uvedených obecných endpointů pro přílohy; pro tento případ
použijte přímo metodu
:meth:`~python_abraflexi.read_only.ReadOnly.perform_request`.
