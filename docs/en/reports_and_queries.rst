Reports, QR codes and user queries
=====================================

PDF / XLSX report export
----------------------------

.. code-block:: python

   pdf_bytes = invoice.export_report(record_id=1, report_name="dodaciList")
   pdf_bytes_en = invoice.export_report(record_id=1, report_name="dodaciList", report_lang="en")
   signed_pdf = invoice.export_report(record_id=1, report_name="dodaciList", report_sign=True)

   xlsx_bytes = invoice.export_report(report_format="xls")  # whole listing, no record_id

``report_lang`` accepts ``cs``, ``sk``, ``en`` or ``de``. Available report
names for an evidence can be discovered with
:meth:`~python_abraflexi.read_only.ReadOnly.get_reports`.

QR codes
--------

Every document evidence gets a payment QR code:

.. code-block:: python

   png_bytes = invoice.get_qr_code_image(size=200)
   data_uri = invoice.get_qr_code_base64(size=200)  # "data:image/png;base64,..."

User-defined queries
------------------------

Call a saved user query ("uživatelský dotaz") by ID:

.. code-block:: python

   rows = client.call_user_query(1)
   rows = client.call_user_query(1, params={"datum": "2024-01-01"})
   # N-arity parameters: pass a list to repeat the query param
   rows = client.call_user_query(1, params={"firma": ["code:F1", "code:F2"]})

Summation
---------

.. code-block:: python

   totals = client.get_sum()                              # GET {evidence}/$sum
   totals = client.get_sum({"detail": "custom:sumCelkem"})  # combined with extra params

   client.filter = "stitky = 'code:VIP'"
   totals = client.get_sum()  # GET {evidence}/(filter)/$sum
