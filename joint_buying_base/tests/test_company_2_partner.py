# Copyright (C) 2021 - Today: GRAP (http://www.grap.coop)
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo.exceptions import AccessError
from odoo.tests import tagged
from odoo.tests.common import TransactionCase


@tagged("post_install", "-at_install")
class TestModule(TransactionCase):
    def setUp(self):
        super().setUp()
        self.company_3PP = self.env.ref("joint_buying_base.company_3PP")
        self.ResCompany = self.env["res.company"]
        self.suffixParameter = self.env.ref("joint_buying_base.parameter_group_name")

    # Test Section
    def test_01_write_company_to_partner_info(self):
        company_name = "Demo Company for Joint Buying"
        new_company = self.ResCompany.create({"name": company_name})

        self.assertEqual(
            new_company.joint_buying_partner_id.name,
            f"{company_name} ({self.suffixParameter.value})",
            "Create a company should create a related joint buying partner",
        )

    def test_02_write_company_to_partner_info(self):
        company_email = "etouais@monpetit.pote"
        self.company_3PP.write({"email": company_email})

        self.assertEqual(
            self.company_3PP.joint_buying_partner_id.email,
            company_email,
            "Update company should update related joint buying partner",
        )

    def test_03_write_joint_buying_partner(self):
        with self.assertRaises(AccessError):
            self.company_3PP.joint_buying_partner_id.email = "nonnon@non.non"

    def test_04_change_config_parameter(self):
        self.suffixParameter.value = "NEW SUFFIX"

        for company in self.ResCompany.search([]):
            self.assertEqual(
                company.joint_buying_partner_id.name,
                f"{company.name} ({self.suffixParameter.value})",
                "Update the config parameter should update all the joint buying partner names",
            )
