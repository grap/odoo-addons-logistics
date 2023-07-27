# Copyright (C) 2021 - Today: GRAP (http://www.grap.coop)
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo.exceptions import AccessError
from odoo.tests import tagged

from .test_abstract import TestAbstract


@tagged("post_install", "-at_install")
class TestModule(TestAbstract):
    def setUp(self):
        super().setUp()
        self.user_3PP = self.env.ref("joint_buying_base.user_joint_buying_user")
        self.company_CHE = self.env.ref("joint_buying_base.company_CHE")
        self.company_3PP = self.env.ref("joint_buying_base.company_3PP")

    # Test Section
    def test_301_check_access_mixin_user(self):
        # create a supplier. (pivot company != current company) should fail
        with self.assertRaises(AccessError):
            self._create_supplier(
                user=self.user_3PP,
                extra_vals={"joint_buying_pivot_company_id": self.company_CHE.id},
            )

        # create a supplier. (pivot company = current company) should success
        partner = self._create_supplier(
            user=self.user_3PP,
            extra_vals={"joint_buying_pivot_company_id": self.company_3PP.id},
        )

        # write a supplier. (pivot company = current company) should success
        partner.write({"name": "Altered name"})

        # unlink a supplier. (pivot company = current company) should success
        partner.unlink()

        # Check write and unlink()
        partner_id = self._create_supplier(
            extra_vals={"joint_buying_pivot_company_id": self.company_CHE.id}
        ).id

        # write a supplier. (pivot company != current company) should fail
        partner = self.ResPartner.sudo(user=self.user_3PP).browse(partner_id)
        with self.assertRaises(AccessError):
            partner.write({"name": "Altered name"})

        # write a supplier (pivot company != current company)
        # for specific allowed fields should success
        partner.joint_buying_is_subscribed = True

        # unlink a supplier. (pivot company != current company) should fail
        with self.assertRaises(AccessError):
            partner.unlink()

    def test_302_check_access_mixin_manager(self):
        # create a supplier. (pivot company != current company) should success
        self._create_supplier(
            extra_vals={"joint_buying_pivot_company_id": self.company_CHE.id}
        )

        # create a supplier. (pivot company = current company) should success
        self._create_supplier(
            extra_vals={"joint_buying_pivot_company_id": self.company_3PP.id}
        )
