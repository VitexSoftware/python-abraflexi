Detail levels, relations and includes
========================================

Detail level
------------

Controls how much data is returned per record — from just the ID to the
full record, or a custom field projection:

.. code-block:: python

   client.set_detail("id")                     # ?detail=id
   client.set_detail("summary")                 # ?detail=summary
   client.set_detail("full")                     # ?detail=full
   client.set_detail("custom:kod,nazev,email")   # ?detail=custom:kod,nazev,email

Custom detail also supports projecting into sub-evidences:

.. code-block:: python

   client.set_detail(
       "custom:id,email,kontakty(primarni,email,odesilatFak)"
   )
   client.set_relations("kontakty")

Relations (sub-evidences)
----------------------------

Every evidence may have sub-evidences (relations) — e.g. invoice lines or
address book contacts. List what is available and include it in a
response:

.. code-block:: python

   client.get_relations_list()               # GET {evidence}/relations
   client.set_relations("polozkyFaktury", "prilohy")  # ?relations=polozkyFaktury,prilohy

Includes
--------

Pull in a related object's fields directly into the response:

.. code-block:: python

   client.set_includes("faktura-vydana/stredisko")  # ?includes=faktura-vydana/stredisko

Evidence metadata
-------------------

.. code-block:: python

   client.get_properties()  # GET {evidence}/properties - supported fields
   client.get_reports()     # GET {evidence}/reports    - available PDF/XLSX reports
