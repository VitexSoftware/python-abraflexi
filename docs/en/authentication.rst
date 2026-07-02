Authentication
==============

AbraFlexi supports HTTP Basic authentication and a JSON session-token
login. ``python-abraflexi`` supports both.

HTTP Basic authentication
--------------------------

The simplest method — pass ``user``/``password`` in the options dict (or
``ABRAFLEXI_LOGIN``/``ABRAFLEXI_PASSWORD`` environment variables). Every
request is then sent with an ``Authorization: Basic ...`` header:

.. code-block:: python

   from python_abraflexi import ReadOnly

   client = ReadOnly(None, {
       "url": "https://demo.flexibee.eu",
       "company": "demo",
       "user": "winstrom",
       "password": "winstrom",
       "evidence": "adresar",
   })

JSON session authentication
----------------------------

Call :meth:`~python_abraflexi.read_only.ReadOnly.login` to obtain a session
token (``authSessionId``) via ``POST /login-logout/login.json``. The token
is stored on the object and automatically sent as the ``X-authSessionId``
header on subsequent requests:

.. code-block:: python

   client = ReadOnly(None, {"url": "https://demo.flexibee.eu", "company": "demo"})
   client.login("winstrom", "winstrom")
   # client.auth_session_id is now set and reused automatically

Session tokens expire after a period of inactivity. Call
:meth:`~python_abraflexi.read_only.ReadOnly.keep_alive` periodically (e.g.
every 60 seconds) on a long-running connection to keep the session valid:

.. code-block:: python

   client.keep_alive()  # GET /login-logout/session-keep-alive.js

To end a session, call :meth:`~python_abraflexi.read_only.ReadOnly.logout`
(``POST /status/user/{username}/logout.json``). It defaults to the
currently configured user, but another username can be passed to force a
different user to be signed off:

.. code-block:: python

   client.logout()

Existing session tokens can also be supplied directly (e.g. when
integrating with an AbraFlexi web application that already authenticated
the user), via the ``authSessionId`` option or the
``ABRAFLEXI_AUTHSESSID`` environment variable.

Configuration precedence
-------------------------

Connection settings are resolved in this order:

1. Constructor ``options`` dict (highest priority)
2. Environment variables (``ABRAFLEXI_URL``, ``ABRAFLEXI_COMPANY``,
   ``ABRAFLEXI_LOGIN``, ``ABRAFLEXI_PASSWORD``, ``ABRAFLEXI_AUTHSESSID``,
   ``ABRAFLEXI_TIMEOUT``, ``ABRAFLEXI_EXCEPTIONS``)
3. Library defaults (300s timeout, JSON format, ``/c/`` prefix)

Use :meth:`~python_abraflexi.read_only.ReadOnly.get_connection_options` on
an existing object to get a dict of its current connection settings,
suitable for constructing another object bound to the same company (this
is how :class:`~python_abraflexi.mixins.FirmaMixin` and
:class:`~python_abraflexi.mixins.EmailMixin` follow the ``firma``
relation).
