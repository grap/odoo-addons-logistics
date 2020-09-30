* Add a new menu entry named "Global Transactions"

* Add a new mixin model, that adds a field ``is_global``.
  ``is_global`` is computed, based on the ``company_id`` field. (enable if no company is defined)
  global items are available, only if the key ``only_global`` is present in the context.
