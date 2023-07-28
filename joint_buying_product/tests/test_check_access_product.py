# Copyright (C) 2021 - Today: GRAP (http://www.grap.coop)
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo.exceptions import AccessError
from odoo.tests import tagged

from .test_abstract import TestAbstract


@tagged("post_install", "-at_install")
class TestCheckAccessProduct(TestAbstract):
    def setUp(self):
        super().setUp()
        # Note LSE is the pivot of benoit_ronzon

        self.user_3PP = self.env.ref("joint_buying_base.user_joint_buying_user_3PP")
        self.user_LSE = self.env.ref("joint_buying_base.user_joint_buying_user_LSE")

    # Custom Functions
    def _create_product(self, user=False, extra_vals=False, joint_buying=True):
        if not user:
            user = self.env.user
        vals = {"name": "My product"}
        vals.update(extra_vals or {})
        return (
            self.ProductProduct.sudo(user)
            .with_context(joint_buying=joint_buying)
            .create(vals)
        )

    # Test Section
    def test_301_product_check_access_mixin_manager(self):
        # create a product. (pivot company != current company) should success
        self._create_product(
            extra_vals={
                "joint_buying_partner_id": self.partner_supplier_benoit_ronzon.id
            }
        )

        # create a product. (pivot company = current company) should success
        self._create_product(
            extra_vals={
                "joint_buying_partner_id": self.partner_supplier_benoit_ronzon.id
            }
        )

    def test_302_product_check_access_mixin_user(self):
        # create a product. (pivot company != current company) should fail
        with self.assertRaises(AccessError):
            self._create_product(
                user=self.user_3PP,
                extra_vals={
                    "joint_buying_partner_id": self.partner_supplier_benoit_ronzon.id
                },
            )

        # # ###############################
        # # Create a partner pivot = LSE
        # # ###############################

        # create a product. (pivot company = current company) should success
        product_LSE = self._create_product(
            user=self.user_LSE,
            extra_vals={
                "joint_buying_partner_id": self.partner_supplier_benoit_ronzon.id
            },
        )

        # # ###############################
        # # Check context 3PP (non pivot)
        # # ###############################

        context_3PP_product_LSE = self.ProductProduct.sudo(user=self.user_3PP).browse(
            product_LSE.id
        )

        # write a product. (pivot company != current company) should fail
        with self.assertRaises(AccessError):
            context_3PP_product_LSE.write({"name": "Altered name"})

        # unlink a product. (pivot company != current company) should fail
        with self.assertRaises(AccessError):
            context_3PP_product_LSE.unlink()

        # # ###############################
        # # Check context LSE (pivot)
        # # ###############################

        context_LSE_product_LSE = self.ProductProduct.sudo(user=self.user_LSE).browse(
            product_LSE.id
        )

        # write a product. (pivot company != current company) should success
        context_LSE_product_LSE.write({"name": "Altered name"})

        # unlink a product. (pivot company != current company) should success
        context_LSE_product_LSE.unlink()
