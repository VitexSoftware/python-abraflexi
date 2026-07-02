Filtering
=========

Set ``client.filter`` to an AbraFlexi filter expression; it is applied as
a parenthesized path segment (AbraFlexi ignores a ``filter`` query-string
parameter — the filter must be part of the URL path):

.. code-block:: python

   client.filter = "nazev = 'ACME'"
   results = client.get_all_from_abraflexi()
   # GET /c/demo/adresar/(nazev='ACME').json

Operators
---------

.. list-table::
   :header-rows: 1
   :widths: 25 35 20

   * - Operator
     - Meaning
     - Example
   * - ``=`` / ``==`` / ``eq``
     - equals
     - ``a = 1``
   * - ``<>`` / ``!=`` / ``ne``
     - not equal
     - ``a != 1``
   * - ``<`` / ``lt``
     - less than
     - ``a < 1``
   * - ``<=`` / ``lte``
     - less than or equal
     - ``a <= 1``
   * - ``>`` / ``gt``
     - greater than
     - ``a > 1``
   * - ``>=`` / ``gte``
     - greater than or equal
     - ``a >= 1``
   * - ``like``
     - contains
     - ``a like 'x'``
   * - ``like similar``
     - contains, accent-insensitive
     - ``a like similar 'x'``
   * - ``between``
     - range
     - ``vek between 18 100``
   * - ``begins`` / ``begins similar``
     - starts with
     - ``a begins 'Win'``
   * - ``ends``
     - ends with
     - ``a ends 'x'``
   * - ``in``
     - set membership
     - ``a in (1, 2, 3)``
   * - ``in subtree``
     - price-list tree membership
     - ``in subtree 3``
   * - ``is true`` / ``is false``
     - boolean comparison
     - ``a is true``
   * - ``is [not] null``
     - filled / empty check
     - ``a is null``
   * - ``is [not] empty``
     - empty (null/0/false/"")
     - ``a is not empty``

Combine conditions with ``and``, ``or``, ``not`` and parentheses (usual
precedence: comparisons, then ``not``, then ``and``, then ``or`` — use
parentheses when unsure). Negative operators such as ``<>`` cannot be used
inside a relation sub-filter (``firma.skupFir <> ...``) — AbraFlexi
raises *"OR logical subselect filter not supported"*; rewrite using
``not(... eq ...)`` instead.

Filtering through relations
------------------------------

Dot notation reaches into 1:1 relations at unlimited depth:

.. code-block:: text

   firma = 'code:FIRMA'
   firma.skupFir = 'code:ODBERATEL-STANDARD'

Filtering by label:

.. code-block:: text

   stitky = 'code:VIP'
   stitky = 'code:VIP' or stitky = 'code:DULEZITE'

Special values
-----------------

``now()``, ``currentYear()`` and ``me()`` can be used as right-hand
values, e.g. ``datSplat < now()`` or ``uzivatel = me()``.

Suppressing the validity filter
----------------------------------

Evidences with ``platiOd``/``platiDo`` fields are filtered to the current
accounting period by default. Add ``filtrovat-platnost=false`` to the URL
parameters to see records outside of it:

.. code-block:: python

   client.default_url_params["filtrovat-platnost"] = "false"
