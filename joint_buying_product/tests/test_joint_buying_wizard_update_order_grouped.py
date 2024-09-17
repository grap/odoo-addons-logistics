# Copyright (C) 2024 - Today: GRAP (http://www.grap.coop)
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).


from odoo.tests import tagged

from .test_abstract import TestAbstract


@tagged("post_install", "-at_install")
class TestJointBuyingWizardUpdateOrderGrouped(TestAbstract):
    def setUp(self):
        super().setUp()

    def test_01_wizard_update_order_grouped(self):

        wizard = self.JointBuyingWizardUpdateOrderGrouped.with_context(
            active_id=self.grouped_order_ronzon_past.id
        ).create({})
        wizard.show_all_orders = True
        wizard.show_all_products = True
        wizard.onchange_show_settings()

        wizard.line_ids.write({"qty": 0})

        self.assertEqual(
            len(
                self.grouped_order_ronzon_past.mapped("order_ids.transport_request_id")
            ),
            0,
        )

        wizard.line_ids.write({"qty": 100})

        self.assertEqual(
            len(
                self.grouped_order_ronzon_past.mapped("order_ids.transport_request_id")
            ),
            len(
                self.grouped_order_ronzon_past.mapped("order_ids").filtered(
                    lambda x: x.deposit_partner_id != x.delivery_partner_id
                )
            ),
        )
