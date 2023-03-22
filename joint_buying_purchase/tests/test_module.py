# Copyright (C) 2023 - Today: GRAP (http://www.grap.coop)
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from datetime import datetime, timedelta

from odoo import fields
from odoo.exceptions import ValidationError
from odoo.tests.common import TransactionCase


class TestModule(TransactionCase):
    def setUp(self):
        super().setUp()
        self.GroupedOrder = self.env["joint.buying.purchase.order.grouped"]
        self.GroupedOrderWizard = self.env["joint.buying.wizard.create.order"]
        self.CreatePurchaseOrderWizard = self.env[
            "joint.buying.create.purchase.order.wizard"
        ]

        # Supplier information
        self.global_supplier_company = self.env.ref("joint_buying_base.company_ELD")
        self.product_ELD_orangettes = self.env.ref(
            "joint_buying_product.product_ELD_orangettes"
        )

        # customer information
        self.supplier_ELD_at_3PP = self.env.ref("joint_buying_base.supplier_ELD_at_3PP")
        self.company_3PP = self.env.ref("joint_buying_base.company_3PP")
        self.product_3PP_orangettes = self.env.ref(
            "joint_buying_product.product_3PP_orangettes"
        )
        self.product_3PP_gingembrettes = self.env.ref(
            "joint_buying_product.product_3PP_gingembrettes"
        )
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

        # We switch to a customer company
        self.env.user.company_id = self.company_3PP.id

    def _get_wizard_create_purchase_order(self):
        """return a wizard to create local purchase order with all the data
        initialized. This wizard should be ready to validate"""
        wizard = self.CreatePurchaseOrderWizard.with_context(
            active_id=self.order_3PP.id,
        ).create({})
        wizard.date_planned = fields.datetime.now()
        return wizard

    def test_01_create_purchase_order_not_local_partner(self):
        self.supplier_ELD_at_3PP.joint_buying_global_partner_id = False
        wizard = self._get_wizard_create_purchase_order()

        with self.assertRaises(ValidationError):
            wizard.create_purchase_order()

    def test_02_create_purchase_order_not_local_product(self):
        self.product_3PP_orangettes.joint_buying_product_id = False
        wizard = self._get_wizard_create_purchase_order()

        with self.assertRaises(ValidationError):
            wizard.create_purchase_order()

    def test_03_create_purchase_order_set_local_product(self):
        self.product_3PP_orangettes.joint_buying_product_id = False

        wizard = self._get_wizard_create_purchase_order()

        line_orangettes = wizard.line_ids.filtered(
            lambda x: x.joint_buying_global_product_id.default_code == "ELD-ORANGETTE"
        )
        line_orangettes.joint_buying_local_product_id = self.product_3PP_orangettes

        wizard.create_purchase_order()

        # Check that the local product has been linked to the global one
        self.assertEqual(
            self.product_3PP_orangettes.joint_buying_product_id,
            self.product_ELD_orangettes.joint_buying_product_id,
        )

    def test_10_create_purchase_order(self):

        # Create purchase orders for associated supplier
        wizard = self._get_wizard_create_purchase_order()

        # Check that the local supplier has been guessed correctly
        self.assertEqual(
            wizard.joint_buying_local_supplier_id,
            self.supplier_ELD_at_3PP,
        )

        # Check that the local products has been guessed correctly
        line_orangettes = wizard.line_ids.filtered(
            lambda x: x.joint_buying_global_product_id.default_code == "ELD-ORANGETTE"
        )
        line_gingembrettes = wizard.line_ids.filtered(
            lambda x: x.joint_buying_global_product_id.default_code
            == "ELD-GINGEMBRETTE"
        )

        self.assertEqual(
            line_orangettes.joint_buying_local_product_id,
            self.product_3PP_orangettes,
        )
        self.assertEqual(
            line_gingembrettes.joint_buying_local_product_id,
            self.product_3PP_gingembrettes,
        )

        result = wizard.create_purchase_order()

        purchase_order = self.env["purchase.order"].browse(result["res_id"])

        self.assertEqual(
            len(purchase_order.order_line),
            2,
            "A Joint Buying Purchase Order with two not null lines"
            " should generate a Purchase Order with 2 lines",
        )

        purchase_order_line_orangettes = purchase_order.order_line.filtered(
            lambda x: x.product_id == self.product_3PP_orangettes
        )

        self.assertEqual(
            len(purchase_order_line_orangettes),
            1,
            "Orangette Line not found in purchase order",
        )

        # self.assertEqual(purchase_order_line_orangettes.product_qty, 20)
        # self.assertEqual(purchase_order_line_orangettes.price_unit, 4.44)
