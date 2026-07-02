Česká dokumentace
==================

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

Přehled
-------

``python-abraflexi`` je Python klient pro REST API systému AbraFlexi
(pouze formát JSON), postavený na dvou základních třídách:

- :class:`python_abraflexi.ReadOnly` — správa připojení, sestavování URL,
  provádění požadavků a zpracování odpovědí.
- :class:`python_abraflexi.ReadWrite` — přidává vkládání/aktualizaci/
  mazání záznamů, akce, dávkové operace, přílohy a binární exporty.

Nad těmito třídami jsou k dispozici dvě hotové evidenční třídy,
:class:`python_abraflexi.FakturaVydana` (faktura vydaná) a
:class:`python_abraflexi.Adresar` (adresář), které slouží i jako vzor pro
vytvoření vlastních evidenčních tříd kombinací
:class:`~python_abraflexi.read_write.ReadWrite` se znovupoužitelnými
mixiny v modulu :mod:`python_abraflexi.mixins`.

Instalace
---------

.. code-block:: bash

   pip install python-abraflexi

Rychlý start
------------

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

Připojovací údaje lze zadat i pomocí proměnných prostředí:
``ABRAFLEXI_URL``, ``ABRAFLEXI_COMPANY``, ``ABRAFLEXI_LOGIN``,
``ABRAFLEXI_PASSWORD``, ``ABRAFLEXI_AUTHSESSID``, ``ABRAFLEXI_TIMEOUT``,
``ABRAFLEXI_EXCEPTIONS``.
