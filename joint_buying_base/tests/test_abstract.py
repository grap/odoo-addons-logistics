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

        self.user_3PP = self.env.ref("joint_buying_base.user_joint_buying_user_3PP")

        self.company_1GG = self.env.ref("joint_buying_base.company_1GG")
        self.company_3PP = self.env.ref("joint_buying_base.company_3PP")
        self.company_CDA = self.env.ref("joint_buying_base.company_CDA")
        self.company_CHE = self.env.ref("joint_buying_base.company_CHE")
        self.company_ELD = self.env.ref("joint_buying_base.company_ELD")
        self.company_LSE = self.env.ref("joint_buying_base.company_LSE")
        self.company_VEV = self.env.ref("joint_buying_base.company_VEV")

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
