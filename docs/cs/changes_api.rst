Changes API
===========

Firemní přehled změn
------------------------

AbraFlexi umí zaznamenávat všechny operace vytvoření/aktualizace/smazání
napříč všemi evidencemi pod stále rostoucím číslem globální verze, což je
ideální pro inkrementální synchronizaci. Použijte třídu
:class:`python_abraflexi.Changes`:

.. code-block:: python

   from python_abraflexi import Changes

   changes = Changes(None, {"url": "...", "company": "demo", "user": "...", "password": "..."})

   changes.enable()
   changes.get_status()  # True

   page = changes.get_changes(start=0, limit=500, evidences=["faktura-vydana"])
   page["changes"]         # seznam záznamů o změnách
   page["next"]            # verze, od které pokračovat, nebo None
   page["global_version"]  # aktuální globální verze

   changes.disable()

Postup synchronizace
------------------------

1. Počáteční načtení: stáhněte potřebná data a zapamatujte si aktuální
   ``global_version`` (u běžného čtení ji lze získat spolu s daty
   přidáním ``add-global-version=true`` do ``default_url_params``).
2. Rozdílová synchronizace: zavolejte ``get_changes(start=<poslední verze>)``,
   aplikujte změny (vytvoření/aktualizace/smazání dle atributu
   ``@operation`` každého záznamu) a zapamatujte si ``next`` jako nový
   výchozí bod.
3. Krok 2 opakujte v pravidelných intervalech.

Přehled změn jednotlivého záznamu
--------------------------------------

Jiný, na záznam vázaný endpoint (``{evidence}/{id}/zmeny.json``)
zobrazuje historii změn jednoho konkrétního záznamu. Přimíchejte
:class:`~python_abraflexi.mixins.RecordChangesMixin` do evidenční třídy,
abyste jej zpřístupnili:

.. code-block:: python

   invoice.get_record_changes()
