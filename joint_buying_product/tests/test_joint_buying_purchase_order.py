# Copyright (C) 2021 - Today: GRAP (http://www.grap.coop)
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import time
from datetime import timedelta

from odoo import fields
from odoo.tests import tagged

from .test_abstract import TestAbstract


@tagged("post_install", "-at_install")
class TestJointBuyingPurchaseOrder(TestAbstract):
    def setUp(self):
        super().setUp()

        self.supplier_oscar_morell = self.JointBuyingResPartner.browse(
            self.env.ref("joint_buying_base.supplier_oscar_morell").id
        )
        self.partner_supplier_PZI = self.env.ref(
            "joint_buying_base.company_PZI"
        ).joint_buying_partner_id
        self.end_date_near_day = int(
            self.IrConfigParameter.get_param("joint_buying_product.end_date_near_day")
        )
        self.end_date_imminent_day = int(
            self.IrConfigParameter.get_param(
                "joint_buying_product.end_date_imminent_day"
            )
        )
        self.grouped_order_report = self.env.ref(
            "joint_buying_product.action_report_joint_buying_purchase_order_grouped"
        )

    def test_01_order_grouped_full_workflow(self):
        order_grouped = self._create_order_grouped_salaison_devidal_by_wizard()

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

        # Case 1) company_LSE orders 24 units of rillette
        # Minimum amount is reached (24*8 > 150)
        # but not minimum weight (24*0.5 < 14)
        order_LSE = order_grouped.order_ids.filtered(
            lambda x: x.customer_id.joint_buying_company_id.code == "LSE"
        )
        line_LSE_rillette = self.OrderLine.search(
            [
                ("order_id", "=", order_LSE.id),
                (
                    "product_id",
                    "=",
                    self.env.ref("joint_buying_product.product_devidal_rillette").id,
                ),
            ]
        )

        line_LSE_rillette.qty = 24.0
        self.assertEqual(order_LSE.purchase_ok, "no_minimum_weight")

        # Case 2) company_CDA orders 15 liters of olive oil
        # Minimum weight is reached (15*0.950 > 14)
        # but not minimum amount (15*8 < 150)
        order_CDA = order_grouped.order_ids.filtered(
            lambda x: x.customer_id.joint_buying_company_id.code == "CDA"
        )
        line_CDA_olive = self.OrderLine.search(
            [
                ("order_id", "=", order_CDA.id),
                (
                    "product_id",
                    "=",
                    self.env.ref("joint_buying_product.product_devidal_huile_olive").id,
                ),
            ]
        )

        line_CDA_olive.qty = 15.0
        self.assertEqual(order_CDA.purchase_ok, "no_minimum_amount")

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
        self.assertEqual(order_LSE.purchase_state, "draft")
        self.assertEqual(order_CDA.purchase_state, "draft")
        self.assertEqual(order_3PP.purchase_state, "skipped")

        # Generate report to make sure the syntax is correct
        self.grouped_order_report.render_qweb_html(order_grouped.ids)

    def test_10_joint_buying_purchase_order_grouped_check_date(self):
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
            "minimum_amount": 100,
            "minimum_weight": 10,
            "minimum_unit_amount": 20,
            "minimum_unit_weight": 2,
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
        # Check dates
        self.assertEqual(order_grouped.start_date, now + timedelta(days=-1))
        self.assertEqual(order_grouped.end_date, now + timedelta(days=+8))
        self.assertEqual(order_grouped.deposit_date, now + timedelta(days=+12))

        # Check Minimum Values
        self.assertEqual(order_grouped.minimum_amount, 100)
        self.assertEqual(order_grouped.minimum_weight, 10)
        self.assertEqual(order_grouped.minimum_unit_amount, 20)
        self.assertEqual(order_grouped.minimum_unit_weight, 2)

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

    def test_11_joint_buying_grouped_order_update_product_list(self):

        grouped_order = self._get_grouped_order_benoit_ronzon()

        # Check 0 : we check that the order is correctly set

        # We check if the product product_ronzon_patatoe_charlotte is sold
        filtered_lines = self._get_order_benoit_ronzon().line_ids.filtered(
            lambda x: x.product_id.id == self.product_ronzon_patatoe_charlotte.id
        )
        self.assertEqual(len(filtered_lines), 1)

        # We check if the product product_ronzon_patatoe_cephora is not sold
        filtered_lines = self._get_order_benoit_ronzon().line_ids.filtered(
            lambda x: x.product_id.id == self.product_ronzon_patatoe_cephora.id
        )
        self.assertEqual(len(filtered_lines), 0)

        # We check if the product product_ronzon_patatoe_cephora is not sold
        filtered_lines = self._get_order_benoit_ronzon().line_ids.filtered(
            lambda x: x.product_id.id == self.product_ronzon_patatoe_agila.id
        )
        self.assertEqual(filtered_lines.price_unit, 1.50)

        initial_count = len(self._get_order_benoit_ronzon().line_ids)
        self.assertEqual(initial_count, 2)

        # CHECK 1 : product purchase_ok True -> False
        self.product_ronzon_patatoe_charlotte.purchase_ok = False
        grouped_order.update_product_list()
        filtered_lines = self._get_order_benoit_ronzon().line_ids.filtered(
            lambda x: x.product_id.id == self.product_ronzon_patatoe_charlotte.id
        )
        self.assertEqual(len(filtered_lines), 0)
        self.assertEqual(
            len(self._get_order_benoit_ronzon().line_ids), initial_count - 1
        )

        # CHECK 2 : product purchase_ok False -> True
        self.product_ronzon_patatoe_cephora.purchase_ok = True
        grouped_order.update_product_list()
        filtered_lines = self._get_order_benoit_ronzon().line_ids.filtered(
            lambda x: x.product_id.id == self.product_ronzon_patatoe_cephora.id
        )
        self.assertEqual(len(filtered_lines), 1)
        self.assertEqual(len(self._get_order_benoit_ronzon().line_ids), initial_count)

        # CHECK 3 : Change price 1.5 -> 1.99
        self.product_ronzon_patatoe_agila.lst_price = 1.99
        grouped_order.update_product_list()
        filtered_lines = self._get_order_benoit_ronzon().line_ids.filtered(
            lambda x: x.product_id.id == self.product_ronzon_patatoe_agila.id
        )
        self.assertEqual(len(filtered_lines), 1)
        self.assertEqual(filtered_lines.price_unit, 1.99)
        self.assertEqual(len(self._get_order_benoit_ronzon().line_ids), initial_count)

    def test_12_joint_buying_grouped_order_with_categories(self):
        now = fields.datetime.now()

        orders_grouped_step_1 = self.OrderGrouped.search(
            [("supplier_id", "=", self.partner_supplier_PZI.id)]
        )

        # no regression
        self.OrderGrouped.cron_create_purchase_order_grouped()
        orders_grouped_step_2 = self.OrderGrouped.search(
            [("supplier_id", "=", self.partner_supplier_PZI.id)]
        )

        self.assertEqual(
            len(orders_grouped_step_1),
            len(orders_grouped_step_2),
            "Creation of Grouped Order should not be launched"
            " if start date is not reached",
        )

        # Launch Oil Order
        self.env.ref(
            "joint_buying_product.frequency_oil_PZI"
        ).next_start_date = now + timedelta(days=-1)
        self.OrderGrouped.cron_create_purchase_order_grouped()

        orders_grouped_step_3 = self.OrderGrouped.search(
            [("supplier_id", "=", self.partner_supplier_PZI.id)]
        )

        self.assertEqual(
            len(orders_grouped_step_2) + 1,
            len(orders_grouped_step_3),
            "Creation of Grouped Order should be launched" " if start date is reached",
        )

        oil_orders_grouped = self.OrderGrouped.search(
            [("supplier_id", "=", self.partner_supplier_PZI.id)],
            order="id desc",
            limit=1,
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

    def test_13_joint_buying_grouped_order_local_product(self):
        self.env.user.company_id = self.company_LSE
        order = self._get_order_benoit_ronzon(customer_code="LSE")
        line_patatoe_agila = order.line_ids.filtered(
            lambda x: x.product_id == self.product_ronzon_patatoe_agila
        )
        line_patatoe_charlotte = order.line_ids.filtered(
            lambda x: x.product_id == self.product_ronzon_patatoe_charlotte
        )

        self.assertEqual(
            line_patatoe_agila.local_product_id, self.product_LSE_patatoe_agila
        )
        self.assertFalse(line_patatoe_charlotte.local_product_id)

    def test_20_joint_buying_grouped_send_mail(self):
        # Create a grouped order, with one not null order
        order_grouped = self._create_order_grouped_salaison_devidal_by_wizard()
        order_grouped.order_ids[0].line_ids[0].qty = 10

        MailWizard = self.env["mail.compose.message.purchase.order.grouped"]
        wizard = MailWizard.with_context(active_ids=[order_grouped.id]).create({})

        wizard.onchange_include_empty_orders()
        self.assertEqual(len(wizard.partner_ids), 1)

        wizard.include_empty_orders = True
        wizard.onchange_include_empty_orders()
        self.assertEqual(len(wizard.partner_ids), order_grouped.order_qty)
