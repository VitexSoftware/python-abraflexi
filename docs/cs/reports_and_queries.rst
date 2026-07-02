Tiskové sestavy, QR kódy a uživatelské dotazy
=================================================

Export tiskových sestav PDF / XLSX
---------------------------------------

.. code-block:: python

   pdf_bytes = invoice.export_report(record_id=1, report_name="dodaciList")
   pdf_bytes_en = invoice.export_report(record_id=1, report_name="dodaciList", report_lang="en")
   signed_pdf = invoice.export_report(record_id=1, report_name="dodaciList", report_sign=True)

   xlsx_bytes = invoice.export_report(report_format="xls")  # celý seznam, bez record_id

Parametr ``report_lang`` přijímá hodnoty ``cs``, ``sk``, ``en`` nebo
``de``. Dostupné názvy sestav pro danou evidenci lze zjistit pomocí
:meth:`~python_abraflexi.read_only.ReadOnly.get_reports`.

QR kódy
-------

Ke každému dokladu lze získat platební QR kód:

.. code-block:: python

   png_bytes = invoice.get_qr_code_image(size=200)
   data_uri = invoice.get_qr_code_base64(size=200)  # "data:image/png;base64,..."

Uživatelské dotazy
----------------------

Zavolání uloženého uživatelského dotazu podle ID:

.. code-block:: python

   rows = client.call_user_query(1)
   rows = client.call_user_query(1, params={"datum": "2024-01-01"})
   # parametry s mohutností N: zadejte seznam pro opakování parametru v URL
   rows = client.call_user_query(1, params={"firma": ["code:F1", "code:F2"]})

Sumace
------

.. code-block:: python

   totals = client.get_sum()                              # GET {evidence}/$sum
   totals = client.get_sum({"detail": "custom:sumCelkem"})  # kombinace s dalšími parametry

   client.filter = "stitky = 'code:VIP'"
   totals = client.get_sum()  # GET {evidence}/(filtr)/$sum
