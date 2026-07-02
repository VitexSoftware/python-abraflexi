Obsluha chyb
============

Hierarchie výjimek
----------------------

Všechny výjimky dědí z :class:`python_abraflexi.AbraFlexiException`:

- :class:`~python_abraflexi.ConnectionException` — chyby sítě/timeoutu
- :class:`~python_abraflexi.AuthenticationException` — HTTP 401
- :class:`~python_abraflexi.PermissionException` — HTTP 402 (zápisové
  REST API není licencováno) nebo 403 (nedostatečná oprávnění)
- :class:`~python_abraflexi.NotFoundException` — HTTP 404
- :class:`~python_abraflexi.ValidationException` — chyba validace na
  úrovni AbraFlexi (``success: false`` v těle odpovědi); obsahuje
  rozparsovaný seznam ``.errors``

Nastavením volby ``throwException`` (případně proměnné prostředí
``ABRAFLEXI_EXCEPTIONS``) na ``False`` způsobíte, že neúspěšná volání
vrátí ``False`` namísto vyvolání výjimky.

HTTP stavové kódy
---------------------

==========  ========================================================
Kód         Význam
==========  ========================================================
200         Úspěch
201         Záznam byl vytvořen (hlavička ``Location`` + id v těle)
304         Nezměněno (v kombinaci s hlavičkou ``If-Modified-Since``)
400         Špatný požadavek (např. PUT odkazující na neexistující
            objekt)
401         Je vyžadováno přihlášení
402         Zápisové REST API není pro tuto firmu licencováno
403         Nedostatečná oprávnění (nebo to neumožňuje licence)
404         Nenalezeno
405         Nepovolená metoda
406         Požadovaný výstupní formát není pro tento zdroj podporován
500         Vnitřní chyba serveru AbraFlexi
==========  ========================================================

Zjištění příčiny neúspěšného volání
----------------------------------------

.. code-block:: python

   client.throw_exception = False
   result = client.insert_to_abraflexi()
   if result is False:
       print(client.last_response_code)
       print(client.errors)  # seznam slovníků {"message": ..., ...}
