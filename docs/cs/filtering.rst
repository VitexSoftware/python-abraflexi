Filtrování
==========

Filtr nastavíte přes ``client.filter`` jako výraz AbraFlexi; do URL se
vkládá jako závorkovaný segment cesty (AbraFlexi ignoruje filtr zadaný
jako query parametr — musí být součástí cesty URL):

.. code-block:: python

   client.filter = "nazev = 'ACME'"
   results = client.get_all_from_abraflexi()
   # GET /c/demo/adresar/(nazev='ACME').json

Operátory
---------

.. list-table::
   :header-rows: 1
   :widths: 25 35 20

   * - Operátor
     - Význam
     - Příklad
   * - ``=`` / ``==`` / ``eq``
     - rovnost
     - ``a = 1``
   * - ``<>`` / ``!=`` / ``ne``
     - nerovnost
     - ``a != 1``
   * - ``<`` / ``lt``
     - menší než
     - ``a < 1``
   * - ``<=`` / ``lte``
     - menší nebo rovno
     - ``a <= 1``
   * - ``>`` / ``gt``
     - větší než
     - ``a > 1``
   * - ``>=`` / ``gte``
     - větší nebo rovno
     - ``a >= 1``
   * - ``like``
     - obsahuje
     - ``a like 'x'``
   * - ``like similar``
     - obsahuje bez háčků/čárek
     - ``a like similar 'x'``
   * - ``between``
     - je v rozsahu
     - ``vek between 18 100``
   * - ``begins`` / ``begins similar``
     - začíná na
     - ``a begins 'Win'``
   * - ``ends``
     - končí na
     - ``a ends 'x'``
   * - ``in``
     - je prvkem výčtu
     - ``a in (1, 2, 3)``
   * - ``in subtree``
     - patří do podstromu ceníku
     - ``in subtree 3``
   * - ``is true`` / ``is false``
     - porovnání logické hodnoty
     - ``a is true``
   * - ``is [not] null``
     - je (není) vyplněno
     - ``a is null``
   * - ``is [not] empty``
     - je (není) prázdné (null/0/false/"")
     - ``a is not empty``

Podmínky lze kombinovat pomocí ``and``, ``or``, ``not`` a závorek
(obvyklá priorita: základní operátory, pak ``not``, pak ``and``, nakonec
``or`` — v případě nejistoty použijte závorky). Negativní operátory jako
``<>`` nelze použít uvnitř podfiltru přes relaci
(``firma.skupFir <> ...``) — AbraFlexi vrátí chybu *„OR logical subselect
filter not supported“*; místo toho použijte zápis ``not(... eq ...)``.

Filtrování přes relace
-------------------------

Tečková notace umožňuje filtrovat i podle atributů 1:1 relací, a to do
libovolné hloubky zanoření:

.. code-block:: text

   firma = 'code:FIRMA'
   firma.skupFir = 'code:ODBERATEL-STANDARD'

Filtrování podle štítku:

.. code-block:: text

   stitky = 'code:VIP'
   stitky = 'code:VIP' or stitky = 'code:DULEZITE'

Speciální hodnoty
--------------------

Jako pravou stranu podmínky lze použít funkce ``now()``,
``currentYear()`` a ``me()``, např. ``datSplat < now()`` nebo
``uzivatel = me()``.

Potlačení filtru platnosti
------------------------------

Evidence s poli ``platiOd``/``platiDo`` jsou ve výchozím stavu filtrovány
podle aktuálního účetního období. Přidáním parametru
``filtrovat-platnost=false`` do URL zobrazíte i záznamy mimo něj:

.. code-block:: python

   client.default_url_params["filtrovat-platnost"] = "false"
