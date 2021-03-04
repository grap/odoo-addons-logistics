Add a new menu entry named "Joint Buyings"

Add a new mixin model ``joint.buying.mixin``, that adds a field ``is_joint_buying``.

* "Joint Buying" item have a ``company_id`` set to ``False``.

* Joint Buying" items are available, only if the key ``joint_buying`` is present in the context.


Add the possibility to have "Joint Buying" partners in a specific menu entry.
