# Copyright (C) 2021 - Today: GRAP (http://www.grap.coop)
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import time
from datetime import timedelta

from odoo import fields
from odoo.exceptions import ValidationError
from odoo.tests import tagged
from odoo.tests.common import TransactionCase


@tagged("post_install", "-at_install")
class TestModule(TransactionCase):
    def setUp(self):
        super().setUp()
        self.ProductProduct = self.env["product.product"].with_context(
            mail_create_nosubscribe=True
        )
        self.IrConfigParameter = self.env["ir.config_parameter"].sudo()

        self.JointBuyingProductProduct = self.env["product.product"].with_context(
            mail_create_nosubscribe=True, joint_buying=True
        )

        self.JointBuyingResPartner = self.env["res.partner"].with_context(
            joint_buying=True
        )

        self.JointBuyingWizardCreateOrder = self.env["joint.buying.wizard.create.order"]
        self.OrderGrouped = self.env["joint.buying.purchase.order.grouped"]
        self.Order = self.env["joint.buying.purchase.order"]
        self.OrderLine = self.env["joint.buying.purchase.order.line"]

        self.company_ELD = self.env.ref("joint_buying_base.company_ELD")
        self.company_CDA = self.env.ref("joint_buying_base.company_CDA")
        self.company_CHE = self.env.ref("joint_buying_base.company_CHE")
        self.company_3PP = self.env.ref("joint_buying_base.company_3PP")
        self.company_LSE = self.env.ref("joint_buying_base.company_LSE")

        self.pricelist_ELD = self.env.ref("joint_buying_product.pricelist_10_percent")

        self.partner_supplier_fumet_dombes = self.env.ref(
            "joint_buying_base.supplier_fumet_dombes"
        )
        self.partner_supplier_benoit_ronzon = self.env.ref(
            "joint_buying_base.supplier_benoit_ronzon"
        )
        self.salaison_devidal = self.JointBuyingResPartner.browse(
            self.env.ref("joint_buying_base.supplier_salaison_devidal").id
        )
        self.supplier_oscar_morell = self.JointBuyingResPartner.browse(
            self.env.ref("joint_buying_base.supplier_oscar_morell").id
        )
        self.partner_supplier_PZI = self.env.ref(
            "joint_buying_base.company_PZI"
        ).joint_buying_partner_id
        self.category_all = self.env.ref("product.product_category_all")
        self.end_date_near_day = int(
            self.IrConfigParameter.get_param("joint_buying_product.end_date_near_day")
        )
        self.end_date_imminent_day = int(
            self.IrConfigParameter.get_param(
                "joint_buying_product.end_date_imminent_day"
            )
        )
        self.new_product_day = int(
            self.IrConfigParameter.get_param("joint_buying_product.new_product_day")
        )

        self.grouped_order_report = self.env.ref(
            "joint_buying_product.action_report_joint_buying_purchase_order_grouped"
        )

    def test_01_search_and_propagate(self):
        len_local_before_local_creation = len(self.ProductProduct.search([]))
        len_joint_buying_before_local_creation = len(
            self.JointBuyingProductProduct.search([])
        )

        # Create a new local product
        product_name = "Some Chocolate"
        new_local_product = self.ProductProduct.create(
            {
                "name": product_name,
                "company_id": self.company_ELD.id,
                "categ_id": self.category_all.id,
                "lst_price": 100.0,
            }
        )

        # Test if the new product is searchable locally
        len_local_after_local_creation = len(self.ProductProduct.search([]))
        self.assertEqual(
            len_local_before_local_creation + 1,
            len_local_after_local_creation,
            "Create a new local product should increase the number of local products",
        )

        # Test if the new product is not searchable in a joint buying context
        len_joint_buying_after_local_creation = len(
            self.JointBuyingProductProduct.search([])
        )
        self.assertEqual(
            len_joint_buying_before_local_creation,
            len_joint_buying_after_local_creation,
            "Create a new local product should not increase the number"
            " of joint buying products",
        )

        # Test the possibility to offer the local product to the joint buying catalog
        # Without pricelist
        new_global_product = new_local_product.create_joint_buying_product()

        len_joint_buying_after_joint_buying_creation = len(
            self.JointBuyingProductProduct.search([])
        )
        self.assertEqual(
            len_joint_buying_before_local_creation + 1,
            len_joint_buying_after_joint_buying_creation,
            "Set a local product as Joint buying should increase the number"
            " of joint buying products",
        )

        # Check created global product
        self.assertNotEqual(new_global_product.id, new_local_product.id)

        self.assertEqual(
            new_global_product.default_code, new_local_product.default_code
        )

        self.assertEqual(
            new_global_product.lst_price,
            new_local_product.lst_price,
            "Global Product should has same price as the local product.",
        )

        # Check that update name on local product update name on global product
        new_product_name = "Some Chocolate Updated"
        new_local_product.name = new_product_name
        self.assertEqual(new_global_product.name, product_name)
        new_local_product.update_joint_buying_product()
        self.assertEqual(new_global_product.name, new_product_name)

        # Check that set a joint buying pricelist update the price of the global product
        self.company_ELD.joint_buying_pricelist_id = self.pricelist_ELD
        new_local_product.update_joint_buying_product()

        self.assertEqual(
            new_global_product.lst_price,
            new_local_product.lst_price * 0.9,
            "Global Product should has a price depending on joint buying pricelist.",
        )

    def test_02_joint_buying_product_creation(self):
        vals = {
            "name": "Some Product",
            "categ_id": self.category_all.id,
            "joint_buying_partner_id": self.company_ELD.joint_buying_partner_id.id,
            "company_id": False,
        }

        # create a product for a supplier that is a seller in odoo
        # should fail
        with self.assertRaises(ValidationError):
            self.JointBuyingProductProduct.create(vals)

        # create a product for a supplier that is not a seller in odoo
        # should success
        vals.update(
            {
                "name": "Some Product 2",
                "joint_buying_partner_id": self.partner_supplier_fumet_dombes.id,
            }
        )
        product = self.JointBuyingProductProduct.create(vals)

        # Change partner of a joint buying product should fail
        with self.assertRaises(ValidationError):
            product.joint_buying_partner_id = self.salaison_devidal.id

    def test_03_order_grouped_full_workflow(self):
        # configure subscription
        self.salaison_devidal.joint_buying_subscribed_company_ids = [
            (6, 0, [self.company_ELD.id, self.company_3PP.id, self.company_CHE.id])
        ]

        # Use Wizard to create grouped order
        start_date = fields.datetime.now() + timedelta(days=1)
        end_date = fields.datetime.now() + timedelta(days=7)
        deposit_date = fields.datetime.now() + timedelta(days=14)

        wizard = self.JointBuyingWizardCreateOrder.with_context(
            active_id=self.salaison_devidal.id
        ).create(
            {
                "start_date": start_date,
                "end_date": end_date,
                "deposit_date": deposit_date,
                "deposit_partner_id": self.company_CDA.joint_buying_partner_id.id,
            }
        )

        res = wizard.create_order_grouped()
        order_grouped = self.OrderGrouped.browse(res["res_id"])
        self.assertEqual(order_grouped.order_qty, 3)

        # Create an order for the main_company
        res = order_grouped.create_current_order()
        self.assertEqual(order_grouped.order_qty, 4)
        order_main = self.Order.browse(res["res_id"])

        # Create an order for the current company should automatically subscribe
        # to the supplier
        self.assertEqual(
            len(self.salaison_devidal.joint_buying_subscribed_company_ids), 4
        )

        # ## Check Product
        # Order should contain only purchasable product
        purchasable_products = self.salaison_devidal.joint_buying_product_ids.filtered(
            lambda x: x.purchase_ok
        )
        self.assertEqual(order_main.line_qty, len(purchasable_products))

        # ## Check lines

        # Case 1) Simple case (uom_id = uom_po_id ; uom_package_id = False)
        # We want to buy 12 Rillette
        # Price : 8€ / Unit
        # Weight : 0.5 kg / the unit
        line_main_rillette = self.OrderLine.search(
            [
                ("order_id", "=", order_main.id),
                (
                    "product_id",
                    "=",
                    self.env.ref("joint_buying_product.product_devidal_rillette").id,
                ),
            ]
        )

        line_main_rillette.qty = 12.0
        self.assertEqual(line_main_rillette.amount_untaxed, 12 * 8)
        self.assertEqual(line_main_rillette.total_weight, 12 * 0.5)

        # Case 2) Checking when the uom_id is the product.uom_po_id
        # We want to buy 3 Olive Oil bag of 5L
        # Price : 8€ / Liter
        # Weight : 1L of oil weight 0.950 kg
        line_main_olive = self.OrderLine.search(
            [
                ("order_id", "=", order_main.id),
                (
                    "product_id",
                    "=",
                    self.env.ref("joint_buying_product.product_devidal_huile_olive").id,
                ),
            ]
        )

        line_main_olive.qty = 15.0
        self.assertEqual(line_main_olive.amount_untaxed, 3 * 5 * 8)
        self.assertEqual(line_main_olive.total_weight, 3 * 5 * 0.95)

        # Case 3) Checking when the Purchase unit is the product.uom_package_id
        # We want to buy 5 Caillette of 0.300 kg / piece
        # Price is 13.00€ / kg
        line_main_caillette = self.OrderLine.search(
            [
                ("order_id", "=", order_main.id),
                (
                    "product_id",
                    "=",
                    self.env.ref("joint_buying_product.product_devidal_caillette").id,
                ),
            ]
        )

        line_main_caillette.qty = 5.0
        self.assertEqual(line_main_caillette.amount_untaxed, 5 * 0.3 * 13.0)
        self.assertEqual(line_main_caillette.total_weight, 5 * 0.3)

        # ## Check purchase state
        self.assertEqual(order_main.purchase_state, "draft")

        # Set minimum weight and amount for grouped order
        order_grouped.minimum_unit_amount = 150
        order_grouped.minimum_unit_weight = 14

        # Case 1) company_ELD orders 24 units of rillette
        # Minimum amount is reached (24*8 > 150)
        # but not minimum weight (24*0.5 < 14)
        order_ELD = order_grouped.order_ids.filtered(
            lambda x: x.customer_id.joint_buying_company_id.code == "ELD"
        )
        line_ELD_rillette = self.OrderLine.search(
            [
                ("order_id", "=", order_ELD.id),
                (
                    "product_id",
                    "=",
                    self.env.ref("joint_buying_product.product_devidal_rillette").id,
                ),
            ]
        )

        line_ELD_rillette.qty = 24.0
        self.assertEqual(order_ELD.purchase_ok, "no_minimum_weight")

        # Case 2) company_CHE orders 15 liters of olive oil
        # Minimum weight is reached (15*0.950 > 14)
        # but not minimum amount (15*8 < 150)
        order_CHE = order_grouped.order_ids.filtered(
            lambda x: x.customer_id.joint_buying_company_id.code == "CHE"
        )
        line_CHE_olive = self.OrderLine.search(
            [
                ("order_id", "=", order_CHE.id),
                (
                    "product_id",
                    "=",
                    self.env.ref("joint_buying_product.product_devidal_huile_olive").id,
                ),
            ]
        )

        line_CHE_olive.qty = 15.0
        self.assertEqual(order_CHE.purchase_ok, "no_minimum_amount")

        # Case 3) company_3PP orders nothing
        order_3PP = order_grouped.order_ids.filtered(
            lambda x: x.customer_id.joint_buying_company_id.code == "3PP"
        )
        self.assertEqual(order_3PP.purchase_ok, "null_amount")

        # ## Check state
        # Check state "futur" (+1d / +7d / +14d)
        self.assertEqual(order_main.state, "futur")

        # Check state "in_progress" (-1d / +7d / +14d)
        order_grouped.start_date = fields.datetime.now() + timedelta(days=-1)
        self.assertEqual(order_main.state, "in_progress")

        # Check state "in_progress_near" (-1d / +3d-- / +14d)
        order_grouped.end_date = fields.datetime.now() + timedelta(
            days=self.end_date_near_day, seconds=-1
        )
        self.assertEqual(order_main.state, "in_progress_near")

        # Check state "in_progress_imminent" (-1d / +1d-- / +14d)
        order_grouped.end_date = fields.datetime.now() + timedelta(
            days=self.end_date_imminent_day, seconds=-1
        )
        self.assertEqual(order_main.state, "in_progress_imminent")

        # Check state "closed" (-8d / -5d / +14d)
        order_grouped.start_date = fields.datetime.now() + timedelta(days=-8)
        order_grouped.end_date = fields.datetime.now() + timedelta(days=-5)
        self.assertEqual(order_main.state, "closed")

        # Check state "deposited" (-8d / -5d / -2d)
        order_grouped.deposit_date = fields.datetime.now() + timedelta(days=-2)

        # Reset to imminent (-8d / +1s / +15d)
        order_grouped.write(
            {
                "start_date": fields.datetime.now() + timedelta(days=-8),
                "end_date": fields.datetime.now() + timedelta(seconds=1),
                "deposit_date": fields.datetime.now() + timedelta(days=+15),
            }
        )
        self.assertEqual(order_main.state, "in_progress_imminent")

        # Check Cron (-8d / -0.1s / +15d)
        time.sleep(1.1)
        self.OrderGrouped.cron_check_state()
        self.assertEqual(order_main.state, "closed", "Cron doesn't work.")

        # Cron also corrects purchase state after grouped order is closed
        #     if orders are still as draft
        # They become done if purchase_ok = ok, skipped if null amount,
        # and stay draft if minimum amount or weight isn't reached
        self.assertEqual(order_main.purchase_state, "done")
        self.assertEqual(order_ELD.purchase_state, "draft")
        self.assertEqual(order_CHE.purchase_state, "draft")
        self.assertEqual(order_3PP.purchase_state, "skipped")

        # Generate report to make sure the syntax is correct
        self.grouped_order_report.render_qweb_html(order_grouped.ids)

    def test_04_product_new(self):
        # Check that new created product are marked as new by default
        product = self.JointBuyingProductProduct.create(
            {
                "name": "Some Product",
                "categ_id": self.category_all.id,
                "joint_buying_partner_id": self.partner_supplier_fumet_dombes.id,
                "company_id": False,
            }
        )
        self.assertTrue(
            product.joint_buying_is_new,
            "New Joint buying product should be marked as new",
        )

        # We hard change product create_date to make it old
        create_date = fields.datetime.now() + timedelta(
            days=-(self.new_product_day + 1)
        )
        sql = "UPDATE product_product SET create_date=%s WHERE id=%s;"
        self.env.cr.execute(sql, (create_date, product.id))

        # Check that cron is working to mark product old
        product.joint_byuing_cron_check_new()
        self.assertFalse(
            product.joint_buying_is_new,
            "Old Joint buying product should not be marked as new",
        )

    def test_05_joint_buying_purchase_order_grouped_check_date(self):
        now = fields.datetime.now()

        self.OrderGrouped.cron_create_purchase_order_grouped()
        order_grouped = self.OrderGrouped.search(
            [("supplier_id", "=", self.supplier_oscar_morell.id)]
        )

        self.assertEqual(
            len(order_grouped),
            0,
            "Creation of Grouped Order should not be launched for manual supplier",
        )

        # We create an automatic purchase_order_grouped with Morell Supplier
        frequency_vals = {
            "frequency": 14,
            "deposit_partner_id": self.company_LSE.joint_buying_partner_id.id,
            "next_start_date": now + timedelta(days=-1),
            "next_end_date": now + timedelta(days=+8),
            "next_deposit_date": now + timedelta(days=+12),
        }
        self.supplier_oscar_morell.write(
            {
                "joint_buying_subscribed_company_ids": [
                    (6, 0, [self.company_3PP.id, self.company_CHE.id])
                ],
                "joint_buying_frequency_ids": [(0, 0, frequency_vals)],
            }
        )

        self.OrderGrouped.cron_create_purchase_order_grouped()

        # Check that the automatic purchase order has been correctly created
        order_grouped = self.OrderGrouped.search(
            [("supplier_id", "=", self.supplier_oscar_morell.id)]
        )
        self.assertEqual(
            len(order_grouped), 1, "Creation of Grouped Order by cron failed"
        )
        self.assertEqual(order_grouped.start_date, now + timedelta(days=-1))
        self.assertEqual(order_grouped.end_date, now + timedelta(days=+8))
        self.assertEqual(order_grouped.deposit_date, now + timedelta(days=+12))

        # Check that supplier dateds has been correctly incremented
        self.assertEqual(
            self.supplier_oscar_morell.joint_buying_frequency_ids[0].next_start_date,
            now + timedelta(days=+13),
        )
        self.assertEqual(
            self.supplier_oscar_morell.joint_buying_frequency_ids[0].next_end_date,
            now + timedelta(days=+22),
        )
        self.assertEqual(
            self.supplier_oscar_morell.joint_buying_frequency_ids[0].next_deposit_date,
            now + timedelta(days=+26),
        )

    def test_06_joint_buying_grouped_order_update_product_list(self):
        def _get_grouped_order():
            return self.partner_supplier_benoit_ronzon.joint_buying_grouped_order_ids[0]

        def _get_order():
            return _get_grouped_order().order_ids[0]

        self.product_ronzon_patatoe_charlotte = self.env.ref(
            "joint_buying_product.product_ronzon_patatoe_charlotte"
        )
        self.product_ronzon_patatoe_cephora = self.env.ref(
            "joint_buying_product.product_ronzon_patatoe_cephora"
        )
        self.product_ronzon_patatoe_agila = self.env.ref(
            "joint_buying_product.product_ronzon_patatoe_agila"
        )

        if not self.partner_supplier_benoit_ronzon.joint_buying_grouped_order_ids:
            self.OrderGrouped.cron_create_purchase_order_grouped()
        grouped_order = _get_grouped_order()

        # Check 0 : we check that the order is correctly set

        # We check if the product product_ronzon_patatoe_charlotte is sold
        filtered_lines = _get_order().line_ids.filtered(
            lambda x: x.product_id.id == self.product_ronzon_patatoe_charlotte.id
        )
        self.assertEqual(len(filtered_lines), 1)

        # We check if the product product_ronzon_patatoe_cephora is not sold
        filtered_lines = _get_order().line_ids.filtered(
            lambda x: x.product_id.id == self.product_ronzon_patatoe_cephora.id
        )
        self.assertEqual(len(filtered_lines), 0)

        # We check if the product product_ronzon_patatoe_cephora is not sold
        filtered_lines = _get_order().line_ids.filtered(
            lambda x: x.product_id.id == self.product_ronzon_patatoe_agila.id
        )
        self.assertEqual(filtered_lines.price_unit, 1.50)

        initial_count = len(_get_order().line_ids)
        self.assertEqual(initial_count, 2)

        # CHECK 1 : product purchase_ok True -> False
        self.product_ronzon_patatoe_charlotte.purchase_ok = False
        grouped_order.update_product_list()
        filtered_lines = _get_order().line_ids.filtered(
            lambda x: x.product_id.id == self.product_ronzon_patatoe_charlotte.id
        )
        self.assertEqual(len(filtered_lines), 0)
        self.assertEqual(len(_get_order().line_ids), initial_count - 1)

        # CHECK 2 : product purchase_ok False -> True
        self.product_ronzon_patatoe_cephora.purchase_ok = True
        grouped_order.update_product_list()
        filtered_lines = _get_order().line_ids.filtered(
            lambda x: x.product_id.id == self.product_ronzon_patatoe_cephora.id
        )
        self.assertEqual(len(filtered_lines), 1)
        self.assertEqual(len(_get_order().line_ids), initial_count)

        # CHECK 3 : Change price 1.5 -> 1.99
        self.product_ronzon_patatoe_agila.lst_price = 1.99
        grouped_order.update_product_list()
        filtered_lines = _get_order().line_ids.filtered(
            lambda x: x.product_id.id == self.product_ronzon_patatoe_agila.id
        )
        self.assertEqual(len(filtered_lines), 1)
        self.assertEqual(filtered_lines.price_unit, 1.99)
        self.assertEqual(len(_get_order().line_ids), initial_count)

    def test_07_joint_buying_grouped_order_with_categories(self):
        now = fields.datetime.now()

        # no regression
        self.OrderGrouped.cron_create_purchase_order_grouped()
        orders_grouped = self.OrderGrouped.search(
            [("supplier_id", "=", self.partner_supplier_PZI.id)]
        )

        self.assertEqual(
            len(orders_grouped),
            0,
            "Creation of Grouped Order should not be launched"
            " if start date is not reached",
        )

        # Launch Oil Order
        self.env.ref(
            "joint_buying_product.frequency_oil_PZI"
        ).next_start_date = now + timedelta(days=-1)
        self.OrderGrouped.cron_create_purchase_order_grouped()
        oil_orders_grouped = self.OrderGrouped.search(
            [("supplier_id", "=", self.partner_supplier_PZI.id)]
        )
        self.assertEqual(
            len(oil_orders_grouped),
            1,
            "Creation of Grouped Order should be launched if start date is reached",
        )

        self.assertEqual(
            oil_orders_grouped.mapped("category_ids").ids,
            [self.env.ref("joint_buying_product.category_oil_PZI").id],
        )

        oil_orders_grouped.create_current_order()

        correct_products = self.partner_supplier_PZI.with_context(
            joint_buying=True
        ).joint_buying_product_ids.filtered(
            lambda x: x.joint_buying_category_id.id
            in [self.env.ref("joint_buying_product.category_oil_PZI").id, False]
        )
        self.assertEqual(
            sorted(oil_orders_grouped.mapped("order_ids.line_ids.product_id").ids),
            sorted(correct_products.ids),
            "Create order for a category should select product for this category"
            " or product allways available.",
        )
