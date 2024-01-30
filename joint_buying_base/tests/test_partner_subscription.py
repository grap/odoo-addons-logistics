# Copyright (C) 2021 - Today: GRAP (http://www.grap.coop)
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo.tests import tagged

from .test_abstract import TestAbstract


@tagged("post_install", "-at_install")
class TestModule(TestAbstract):

    # Test Section
    def test_501_create_partner_subscription_by_company(self):
        self.env.user.company_id.joint_buying_auto_subscribe = False
        supplier = self._create_supplier()
        self.assertFalse(supplier.joint_buying_is_subscribed)

        self.env.user.company_id.joint_buying_auto_subscribe = True
        supplier = self._create_supplier()
        self.assertTrue(supplier.joint_buying_is_subscribed)

        supplier.toggle_joint_buying_is_subscribed()
        self.assertFalse(supplier.joint_buying_is_subscribed)

    def test_502_create_partner_subscription_by_user(self):
        self.env.user.joint_buying_auto_subscribe = False
        supplier = self._create_supplier()
        self.assertFalse(supplier.joint_buying_is_subscribed)

        self.env.user.joint_buying_auto_subscribe = True
        supplier = self._create_supplier()
        self.assertTrue(supplier.joint_buying_is_subscribed)

        supplier.toggle_joint_buying_is_subscribed()
        self.assertFalse(supplier.joint_buying_is_subscribed)

    def test_503_create_supplier_company_generate_subscription(self):
        # Set 1GG as auto subscribable
        self.company_3PP.joint_buying_auto_subscribe = True

        # Create New company set as 'Joint Buying Supplier'
        new_company = self.ResCompany.create(
            {
                "name": "New Company",
                "is_joint_buying_supplier": True,
            }
        )

        self.assertIn(
            new_company.joint_buying_partner_id,
            self.company_3PP.joint_buying_subscribed_partner_ids,
        )

    def test_504_update_supplier_company_generate_subscription(self):
        # Set 1GG as autosubscribable
        self.company_3PP.joint_buying_auto_subscribe = True

        # Set CDA as a supplier (was not before)
        self.company_CDA.is_joint_buying_supplier = True

        self.assertIn(
            self.company_CDA.joint_buying_partner_id,
            self.company_3PP.joint_buying_subscribed_partner_ids,
        )
