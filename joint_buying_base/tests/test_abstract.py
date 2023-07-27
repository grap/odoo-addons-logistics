# Copyright (C) 2021 - Today: GRAP (http://www.grap.coop)
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo.tests import tagged
from odoo.tests.common import TransactionCase


@tagged("post_install", "-at_install")
class TestAbstract(TransactionCase):
    def setUp(self):
        super().setUp()
        self.ResPartner = self.env["res.partner"].with_context(
            mail_create_nosubscribe=True
        )

    # Custom Functions
    def _create_supplier(self, user=False, extra_vals=False):
        if not user:
            user = self.env.user
        vals = {"name": "My supplier", "supplier": True, "customer": False}
        vals.update(extra_vals or {})
        supplier = (
            self.ResPartner.sudo(user).with_context(joint_buying=True).create(vals)
        )
        return supplier
