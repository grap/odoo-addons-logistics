# Copyright (C) 2021 - Today: GRAP (http://www.grap.coop)
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo.exceptions import AccessError
from odoo.tests import tagged

from .test_abstract import TestAbstract


@tagged("post_install", "-at_install")
class TestCheckAccessJointBuyingPurchase(TestAbstract):
    def setUp(self):
        super().setUp()
        # Note CDA is the pivot of Salaison Devidal
        self.user_3PP = self.env.ref("joint_buying_base.user_joint_buying_user_3PP")
        self.user_CDA = self.env.ref("joint_buying_base.user_joint_buying_user_CDA")
        self.user_LSE = self.env.ref("joint_buying_base.user_joint_buying_user_LSE")

    # Test Section
    def test_501_purchase_order_grouped_check_access_mixin_manager(self):
        # create a purchase Order grouped. with manager should success
        self._create_order_grouped_salaison_devidal_by_wizard()

    def test_502_purchase_order_grouped_check_access_mixin_user(self):
        # create a purchase order grouped. (pivot company != current company) should fail
        with self.assertRaises(AccessError):
            self._create_order_grouped_salaison_devidal_by_wizard(
                user=self.user_3PP,
            )

        # ###############################
        # Create a purchase order grouped pivot = CDA
        # ###############################

        # create a purchase order grouped. (pivot company = current company) should success
        order_grouped = self._create_order_grouped_salaison_devidal_by_wizard(
            user=self.user_CDA,
        )

        # ###############################
        # Check context CDA (Pivot)
        # ###############################

        # delete a purchase order grouped. (pivot company = current company) should fail
        with self.assertRaises(AccessError):
            order_grouped.sudo(self.user_CDA).unlink()

        # ###############################
        # Check context 3PP (non pivot)
        # ###############################

        # delete a purchase order grouped. (pivot company != current company) should fail
        with self.assertRaises(AccessError):
            order_grouped.sudo(self.user_CDA).unlink()

    def test_503_purchase_order_check_access_mixin_user(self):
        # create a joint buying purchase order grouped
        order_grouped = self._create_order_grouped_salaison_devidal_by_wizard()

        order_LSE = order_grouped.order_ids.filtered(
            lambda x: x.customer_id.joint_buying_company_id.code == "LSE"
        )

        # ###############################
        # Check context 3PP (non pivot)
        # ###############################
        with self.assertRaises(AccessError):
            order_LSE.sudo(self.user_3PP).action_skip_purchase()

        # ###############################
        # Check context CDA (Pivot)
        # ###############################
        order_LSE.sudo(self.user_CDA).action_skip_purchase()

        # ###############################
        # Check context LSE (Customer)
        # ###############################
        order_LSE.sudo(self.user_LSE).action_skip_purchase()

    def test_504_purchase_order_line_check_access_mixin_user(self):
        # create a joint buying purchase order grouped
        order_grouped = self._create_order_grouped_salaison_devidal_by_wizard()

        line_LSE = order_grouped.order_ids.filtered(
            lambda x: x.customer_id.joint_buying_company_id.code == "LSE"
        ).line_ids[0]

        # ###############################
        # Check context 3PP (non pivot)
        # ###############################
        with self.assertRaises(AccessError):
            line_LSE.sudo(self.user_3PP).write({"qty": 60})

        # ###############################
        # Check context CDA (Pivot)
        # ###############################
        line_LSE.sudo(self.user_CDA).write({"qty": 120})

        # ###############################
        # Check context LSE (Customer)
        # ###############################
        line_LSE.sudo(self.user_LSE).write({"qty": 180})
