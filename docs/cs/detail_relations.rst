Úrovně detailu, relace a includes
====================================

Úroveň detailu
------------------

Určuje, kolik dat se pro každý záznam vrátí — od pouhého ID až po plný
záznam, nebo vlastní výběr polí:

.. code-block:: python

   client.set_detail("id")                     # ?detail=id
   client.set_detail("summary")                 # ?detail=summary
   client.set_detail("full")                     # ?detail=full
   client.set_detail("custom:kod,nazev,email")   # ?detail=custom:kod,nazev,email

Vlastní detail umožňuje promítnout i pole z podevidencí:

.. code-block:: python

   client.set_detail(
       "custom:id,email,kontakty(primarni,email,odesilatFak)"
   )
   client.set_relations("kontakty")

Relace (podevidence)
------------------------

Každá evidence může mít podevidence (relace) — např. položky faktury
nebo kontakty adresáře. Přehled dostupných relací a jejich zahrnutí do
odpovědi:

.. code-block:: python

   client.get_relations_list()               # GET {evidence}/relations
   client.set_relations("polozkyFaktury", "prilohy")  # ?relations=polozkyFaktury,prilohy

Includes
--------

Zahrnutí polí souvisejícího objektu přímo do odpovědi:

.. code-block:: python

   client.set_includes("faktura-vydana/stredisko")  # ?includes=faktura-vydana/stredisko

Metadata evidence
---------------------

.. code-block:: python

   client.get_properties()  # GET {evidence}/properties - podporovaná pole
   client.get_reports()     # GET {evidence}/reports    - dostupné tiskové sestavy PDF/XLSX
