# Copyright (C) 2022 - Today: GRAP (http://www.grap.coop)
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from datetime import datetime, timedelta

from odoo import fields
from odoo.exceptions import UserError, ValidationError
from odoo.tests.common import TransactionCase


class TestModule(TransactionCase):
    def setUp(self):
        super().setUp()
        self.GroupedOrder = self.env["joint.buying.purchase.order.grouped"]
        self.GroupedOrderWizard = self.env["joint.buying.wizard.create.order"]
        self.CreateSaleOrderrWizard = self.env["joint.buying.create.sale.order.wizard"]

        self.global_supplier_company = self.env.ref("joint_buying_base.company_ELD")
        self.global_supplier_partner = (
            self.global_supplier_company.joint_buying_partner_id
        )

        self.env.user.company_id = self.global_supplier_company.id
        # Prepare a pending grouped order for ELD
        wizard = self.GroupedOrderWizard.create(
            {
                "supplier_id": self.global_supplier_partner.id,
                "start_date": fields.Datetime.to_string(
                    datetime.today() + timedelta(days=-2)
                ),
                "end_date": fields.Datetime.to_string(
                    datetime.today() + timedelta(days=+2)
                ),
                "deposit_date": fields.Datetime.to_string(
                    datetime.today() + timedelta(days=+4)
                ),
                "pivot_company_id": self.global_supplier_company.id,
                "deposit_partner_id": self.env.ref(
                    "joint_buying_base.company_LSE"
                ).joint_buying_partner_id.id,
            }
        )
        grouped_order_id = wizard.create_order_grouped()["res_id"]
        self.grouped_order = self.GroupedOrder.browse(grouped_order_id)

        # Set Values to 3PP order
        self.order_3PP = self.grouped_order.order_ids.filtered(
            lambda x: "[3PP" in x.customer_id.name
        )
        self.order_3PP.line_ids.filtered(
            lambda x: x.product_id.default_code == "ELD-GINGEMBRETTE"
        ).write(
            {
                "qty": 10,
                "price_unit": 3.33,
            }
        )
        self.order_3PP.line_ids.filtered(
            lambda x: x.product_id.default_code == "ELD-ORANGETTE"
        ).write(
            {
                "qty": 20,
                "price_unit": 4.44,
            }
        )

        # Set Values to 1GG order
        self.order_1GG = self.grouped_order.order_ids.filtered(
            lambda x: "[1GG" in x.customer_id.name
        )
        self.order_1GG.line_ids.filtered(
            lambda x: x.product_id.default_code == "ELD-GINGEMBRETTE"
        ).write(
            {
                "qty": 100,
                "price_unit": 3.33,
            }
        )

        # Set Values to EDC order
        self.order_EDC = self.grouped_order.order_ids.filtered(
            lambda x: "[EDC" in x.customer_id.name
        )
        self.order_EDC.line_ids.filtered(
            lambda x: x.product_id.default_code == "ELD-GINGEMBRETTE"
        ).write(
            {
                "qty": 1000,
                "price_unit": 3.33,
            }
        )
        self.order_EDC.line_ids.filtered(
            lambda x: x.product_id.default_code == "ELD-ORANGETTE"
        ).write(
            {
                "qty": 2000,
                "price_unit": 4.44,
            }
        )

    def _get_wizard_create_sale_order(self):
        wizard = self.CreateSaleOrderrWizard.with_context(
            active_id=self.grouped_order.id,
        ).create({})
        return wizard

    def test_01_create_sale_order_not_local_partner(self):
        wizard = self._get_wizard_create_sale_order()

        with self.assertRaises(ValidationError):
            # 3PP and 1GG have local customer partners but EDC doesn't :
            # cCeate Sale orders should raise an error
            wizard.create_sale_order()

    def test_02_create_sale_orders(self):

        # Create sale orders for associated customer
        wizard = self._get_wizard_create_sale_order()
        wizard.line_ids.filtered(
            lambda x: "[EDC" in x.joint_buying_global_customer_id.name
        ).unlink()
        wizard.create_sale_order()

        self.assertTrue(self.order_1GG.sale_order_id)
        self.assertTrue(self.order_3PP.sale_order_id)
        self.assertFalse(self.order_EDC.sale_order_id)

        # Associate EDC customer
        local_partner_EDC = self.env["res.partner"].create(
            {
                "name": "The Quince Grocery @ Elodia",
                "company_id": self.global_supplier_company.id,
            }
        )
        self.order_EDC.customer_id.set_joint_buying_local_partner_id(local_partner_EDC)
        wizard = self._get_wizard_create_sale_order()
        wizard.create_sale_order()

        self.assertTrue(self.order_EDC.sale_order_id)

        # Try to rerun the wizard should fail because all the sale orders
        # have been created.
        with self.assertRaises(UserError):
            wizard = self._get_wizard_create_sale_order()
