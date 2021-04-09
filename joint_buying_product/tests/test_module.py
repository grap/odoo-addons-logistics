# Copyright (C) 2021 - Today: GRAP (http://www.grap.coop)
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

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
        self.JointBuyingProductProduct = self.env["product.product"].with_context(
            mail_create_nosubscribe=True, joint_buying=True
        )
        self.company_ELD = self.env.ref("joint_buying_base.company_ELD")
        self.partner_supplier_fumet_dombes = self.env.ref(
            "joint_buying_base.supplier_fumet_dombes"
        )
        self.partner_supplier_salaison_devidal = self.env.ref(
            "joint_buying_base.supplier_salaison_devidal"
        )
        self.category_all = self.env.ref("product.product_category_all")

    def test_search_and_propagate(self):
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

    def test_joint_buying_product_creation(self):
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
            product.joint_buying_partner_id = self.partner_supplier_salaison_devidal.id
