Autentizace
===========

AbraFlexi podporuje jednoduchou HTTP autentizaci a přihlášení pomocí
JSON autentizačního tokenu (sezení). ``python-abraflexi`` podporuje obě
varianty.

HTTP autentizace
-----------------

Nejjednodušší způsob — zadejte ``user``/``password`` do slovníku options
(případně proměnné prostředí ``ABRAFLEXI_LOGIN``/``ABRAFLEXI_PASSWORD``).
Každý požadavek je pak odeslán s hlavičkou ``Authorization: Basic ...``:

.. code-block:: python

   from python_abraflexi import ReadOnly

   client = ReadOnly(None, {
       "url": "https://demo.flexibee.eu",
       "company": "demo",
       "user": "winstrom",
       "password": "winstrom",
       "evidence": "adresar",
   })

JSON autentizace (autentizační sezení)
------------------------------------------

Zavoláním :meth:`~python_abraflexi.read_only.ReadOnly.login` získáte
autentizační token (``authSessionId``) pomocí
``POST /login-logout/login.json``. Token se uloží do objektu a
automaticky se odesílá v hlavičce ``X-authSessionId`` u dalších
požadavků:

.. code-block:: python

   client = ReadOnly(None, {"url": "https://demo.flexibee.eu", "company": "demo"})
   client.login("winstrom", "winstrom")
   # client.auth_session_id je nyní nastaveno a automaticky se používá

Autentizační token po určité době neaktivity vyprší. U dlouhotrvajícího
spojení proto pravidelně (např. každých 60 vteřin) volejte
:meth:`~python_abraflexi.read_only.ReadOnly.keep_alive`, aby zůstalo
sezení platné:

.. code-block:: python

   client.keep_alive()  # GET /login-logout/session-keep-alive.js

Pro ukončení sezení použijte
:meth:`~python_abraflexi.read_only.ReadOnly.logout`
(``POST /status/user/{username}/logout.json``). Ve výchozím stavu se
odhlásí aktuálně nastavený uživatel, lze však zadat i jiné uživatelské
jméno a odhlásit tak jiného uživatele:

.. code-block:: python

   client.logout()

Existující autentizační token lze zadat i přímo (např. při integraci s
webovou aplikací AbraFlexi, kde už byl uživatel přihlášen) pomocí volby
``authSessionId``, případně proměnné prostředí ``ABRAFLEXI_AUTHSESSID``.

Priorita konfigurace
----------------------

Připojovací nastavení se vyhodnocuje v tomto pořadí:

1. Slovník ``options`` v konstruktoru (nejvyšší priorita)
2. Proměnné prostředí (``ABRAFLEXI_URL``, ``ABRAFLEXI_COMPANY``,
   ``ABRAFLEXI_LOGIN``, ``ABRAFLEXI_PASSWORD``, ``ABRAFLEXI_AUTHSESSID``,
   ``ABRAFLEXI_TIMEOUT``, ``ABRAFLEXI_EXCEPTIONS``)
3. Výchozí hodnoty knihovny (timeout 300 s, formát JSON, prefix ``/c/``)

Metoda :meth:`~python_abraflexi.read_only.ReadOnly.get_connection_options`
vrátí slovník aktuálního připojení daného objektu, který lze použít pro
vytvoření dalšího objektu připojeného ke stejné firmě (takto sledují
relaci ``firma`` mixiny :class:`~python_abraflexi.mixins.FirmaMixin` a
:class:`~python_abraflexi.mixins.EmailMixin`).
