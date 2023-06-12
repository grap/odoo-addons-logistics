# Copyright (C) 2021 - Today: GRAP (http://www.grap.coop)
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from datetime import timedelta

from odoo import fields
from odoo.exceptions import ValidationError
from odoo.tests import tagged

from .test_abstract import TestAbstract


@tagged("post_install", "-at_install")
class TestProduct(TestAbstract):
    def setUp(self):
        super().setUp()

        self.pricelist_ELD = self.env.ref("joint_buying_product.pricelist_10_percent")
        self.product_ELD_orangettes = self.env.ref(
            "joint_buying_product.product_ELD_orangettes"
        )

        self.partner_supplier_fumet_dombes = self.env.ref(
            "joint_buying_base.supplier_fumet_dombes"
        )

        self.category_all = self.env.ref("product.product_category_all")

        self.new_product_day = int(
            self.IrConfigParameter.get_param("joint_buying_product.new_product_day")
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

    def test_02_A_local_global_links_supplier_context(self):
        self.env.user.company_id = self.company_ELD

        new_local_product = self.ProductProduct.create(
            {
                "name": "A New Chocolate @ELD",
                "company_id": self.company_ELD.id,
                "categ_id": self.category_all.id,
                "lst_price": 100.0,
            }
        )
        # Create a chocolate and propagate the information should success
        # because Elodie D is a supplier
        new_global_product = new_local_product.create_joint_buying_product()
        self.assertNotEqual(new_global_product.id, False)

        # Update the information should success because
        # the global product "is mine"
        new_local_product.update_joint_buying_product()

        # Try to set new local product for the glocal product
        with self.assertRaises(ValidationError):
            new_global_product.set_joint_buying_local_product_id(
                self.product_ELD_orangettes
            )
        with self.assertRaises(ValidationError):
            new_global_product.set_joint_buying_local_product_id(False)

    def test_02_B_local_global_links_not_supplier_context(self):
        self.env.user.company_id = self.company_3PP

        new_local_product = self.ProductProduct.create(
            {
                "name": "A New Chocolate @3PP",
                "company_id": self.company_3PP.id,
                "categ_id": self.category_all.id,
                "lst_price": 100.0,
            }
        )
        # Create a chocolate and propagate the information should fail
        # because 3PP is not a supplier
        new_global_product = new_local_product.create_joint_buying_product()
        self.assertEqual(new_global_product.id, False)

    def test_03_joint_buying_product_creation(self):
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
