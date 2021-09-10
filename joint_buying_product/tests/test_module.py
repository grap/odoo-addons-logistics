# Copyright (C) 2021 - Today: GRAP (http://www.grap.coop)
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from datetime import timedelta

from odoo import fields
from odoo.exceptions import ValidationError
from odoo.tests.common import TransactionCase, at_install, post_install


@at_install(False)
@post_install(True)
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

        self.company_ELD = self.env.ref("joint_buying_base.company_ELD")
        self.company_CHE = self.env.ref("joint_buying_base.company_CHE")
        self.company_3PP = self.env.ref("joint_buying_base.company_3PP")
        self.partner_supplier_fumet_dombes = self.env.ref(
            "joint_buying_base.supplier_fumet_dombes"
        )
        self.salaison_devidal = self.JointBuyingResPartner.browse(
            self.env.ref("joint_buying_base.supplier_salaison_devidal").id
        )
        self.category_all = self.env.ref("product.product_category_all")

        self.near_setting = self.IrConfigParameter.get_param(
            "joint_buying_product.end_date_near_day"
        )
        self.imminent_setting = self.IrConfigParameter.get_param(
            "joint_buying_product.end_date_imminent_day"
        )

    def test_01_search_and_propagate(self):
        len_local_before_local_creation = len(self.ProductProduct.search([]))
        len_joint_buying_before_local_creation = len(
            self.JointBuyingProductProduct.search([])
        )

        # Create a new local product
        new_local_product = self.ProductProduct.create(
            {
                "name": "Some Chocolate",
                "company_id": self.company_ELD.id,
                "categ_id": self.category_all.id,
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
        new_local_product.create_joint_buying_product()

        len_joint_buying_after_joint_buying_creation = len(
            self.JointBuyingProductProduct.search([])
        )
        self.assertEqual(
            len_joint_buying_before_local_creation + 1,
            len_joint_buying_after_joint_buying_creation,
            "Set a local product as Joint buying should increase the number"
            " of joint buying products",
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
            self.company_ELD.id,
            self.company_3PP.id,
            self.company_CHE.id,
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
            }
        )

        res = wizard.create_order_grouped()
        order_grouped = self.OrderGrouped.browse(res["res_id"])
        self.assertEqual(order_grouped.order_qty, 3)

        # Create an order for the main_company
        res = order_grouped.create_current_order()
        self.assertEqual(order_grouped.order_qty, 4)
        order = self.Order.browse(res["res_id"])

        # Create an order for the current company should automatically subscribe
        # to the supplier
        self.assertEqual(
            len(self.salaison_devidal.joint_buying_subscribed_company_ids), 4
        )

        # Order should contain only purchasable product
        purchasable_products = self.salaison_devidal.joint_buying_product_ids.filtered(
            lambda x: x.purchase_ok
        )
        self.assertEqual(order.line_qty, len(purchasable_products))

        # Check state "futur"
        self.assertEqual(order.state, "futur")

        # Check state "in_progress"
        order_grouped.start_date = fields.datetime.now() + timedelta(days=-1)
        self.assertEqual(order.state, "in_progress")
