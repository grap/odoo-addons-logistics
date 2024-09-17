# Copyright (C) 2021 - Today: GRAP (http://www.grap.coop)
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from datetime import datetime, timedelta

from odoo import fields
from odoo.tests import tagged
from odoo.tests.common import TransactionCase


@tagged("post_install", "-at_install")
class TestAbstract(TransactionCase):
    def setUp(self):
        super().setUp()
        self.IrConfigParameter = self.env["ir.config_parameter"].sudo()

        self.JointBuyingResPartner = self.env["res.partner"].with_context(
            joint_buying=True
        )
        self.ProductProduct = self.env["product.product"].with_context(
            mail_create_nosubscribe=True
        )

        self.JointBuyingProductProduct = self.env["product.product"].with_context(
            mail_create_nosubscribe=True, joint_buying=True
        )

        self.OrderGrouped = self.env["joint.buying.purchase.order.grouped"]
        self.Order = self.env["joint.buying.purchase.order"]
        self.OrderLine = self.env["joint.buying.purchase.order.line"]
        self.JointBuyingWizardCreateOrder = self.env["joint.buying.wizard.create.order"]

        self.company_ELD = self.env.ref("joint_buying_base.company_ELD")
        self.company_CDA = self.env.ref("joint_buying_base.company_CDA")
        self.company_CHE = self.env.ref("joint_buying_base.company_CHE")
        self.company_3PP = self.env.ref("joint_buying_base.company_3PP")
        self.company_LSE = self.env.ref("joint_buying_base.company_LSE")
        self.company_1GG = self.env.ref("joint_buying_base.company_1GG")

        self.salaison_devidal = self.JointBuyingResPartner.browse(
            self.env.ref("joint_buying_base.supplier_salaison_devidal").id
        )

        self.partner_supplier_benoit_ronzon = self.env.ref(
            "joint_buying_base.supplier_benoit_ronzon"
        )
        self.product_ronzon_patatoe_charlotte = self.env.ref(
            "joint_buying_product.product_ronzon_patatoe_charlotte"
        )
        self.product_ronzon_patatoe_cephora = self.env.ref(
            "joint_buying_product.product_ronzon_patatoe_cephora"
        )
        self.product_ronzon_patatoe_agila = self.env.ref(
            "joint_buying_product.product_ronzon_patatoe_agila"
        )
        self.product_LSE_patatoe_agila = self.env.ref(
            "joint_buying_product.product_LSE_patatoe_agila"
        )

    def _create_order_grouped_salaison_devidal_by_wizard(self, user=False):
        # Use Wizard to create grouped order
        start_date = fields.datetime.now() + timedelta(days=1)
        end_date = fields.datetime.now() + timedelta(days=7)
        deposit_date = fields.datetime.now() + timedelta(days=14)

        if user:
            WizardObj = self.JointBuyingWizardCreateOrder.sudo(user=user)
        else:
            WizardObj = self.JointBuyingWizardCreateOrder

        wizard = WizardObj.with_context(active_id=self.salaison_devidal.id).create(
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
        return order_grouped

    def _get_grouped_order_benoit_ronzon(self):
        if not self.partner_supplier_benoit_ronzon.joint_buying_grouped_order_ids.filtered(
            lambda x: x.deposit_date > datetime.now()
        ):
            self.OrderGrouped.cron_create_purchase_order_grouped()
        return self.partner_supplier_benoit_ronzon.joint_buying_grouped_order_ids[0]

    def _get_order_benoit_ronzon(self, customer_code=False):
        grouped_order = self._get_grouped_order_benoit_ronzon()
        if not customer_code:
            return grouped_order.order_ids[0]
        return grouped_order.order_ids.filtered(
            lambda x: "-%s" % customer_code in x.name
        )
