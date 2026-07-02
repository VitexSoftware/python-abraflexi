Error handling
==============

Exception hierarchy
--------------------

All exceptions derive from :class:`python_abraflexi.AbraFlexiException`:

- :class:`~python_abraflexi.ConnectionException` — network/timeout errors
- :class:`~python_abraflexi.AuthenticationException` — HTTP 401
- :class:`~python_abraflexi.PermissionException` — HTTP 402 (write API not
  licensed) or 403 (insufficient rights)
- :class:`~python_abraflexi.NotFoundException` — HTTP 404
- :class:`~python_abraflexi.ValidationException` — AbraFlexi-level
  validation failure (``success: false`` in the response body); carries
  the parsed ``.errors`` list

Set ``throwException`` (option) / ``ABRAFLEXI_EXCEPTIONS`` (env var) to
``False`` to make failed calls return ``False`` instead of raising.

HTTP status codes
--------------------

==========  ========================================================
Code        Meaning
==========  ========================================================
200         Success
201         Record created (``Location`` header + id in body)
304         Not modified (used with ``If-Modified-Since``)
400         Bad request (e.g. PUT referencing a non-existent object)
401         Authentication required
402         Write REST API not licensed for this company
403         Insufficient permissions (or license doesn't allow the
            operation)
404         Not found
405         Method not allowed
406         Requested output format not supported for this resource
500         AbraFlexi internal server error
==========  ========================================================

Inspecting a failed call
----------------------------

.. code-block:: python

   client.throw_exception = False
   result = client.insert_to_abraflexi()
   if result is False:
       print(client.last_response_code)
       print(client.errors)  # list of {"message": ..., ...} dicts
