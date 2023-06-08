# Copyright (C) 2023 - Today: GRAP (http://www.grap.coop)
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).


from odoo.addons.joint_buying_product.tests.test_abstract import TestAbstract


class TestModule(TestAbstract):
    def setUp(self):
        super().setUp()

    def test_local_product_qty(self):
        self.env.user.company_id = self.company_LSE
        order = self._get_order_benoit_ronzon(customer_code="LSE")
        line_patatoe_agila = order.line_ids.filtered(
            lambda x: x.product_id == self.product_ronzon_patatoe_agila
        )
        # No regression test
        self.assertEqual(
            line_patatoe_agila.local_product_id, self.product_LSE_patatoe_agila
        )
        self.assertEqual(line_patatoe_agila.local_product_qty_description, "(0.0 kg)")
