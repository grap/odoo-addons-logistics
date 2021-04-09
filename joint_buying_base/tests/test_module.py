# Copyright (C) 2021 - Today: GRAP (http://www.grap.coop)
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo.exceptions import AccessError, ValidationError
from odoo.tests.common import TransactionCase, at_install, post_install


@at_install(False)
@post_install(True)
class TestModule(TransactionCase):

    def setUp(self):
        super().setUp()
        self.company_3PP = self.env.ref("joint_buying_base.company_3PP")
        self.ResCompany = self.env["res.company"]
        self.ResPartner = self.env["res.partner"].with_context(mail_create_nosubscribe=True)
        self.joint_buying_supplier = self.env.ref(
            "joint_buying_base.supplier_fumer_dombes"
        )
        self.company_CHO = self.env.ref("joint_buying_base.company_CHO")
        self.company_CHE = self.env.ref("joint_buying_base.company_CHE")
        self.company_3PP = self.env.ref("joint_buying_base.company_3PP")

    # Test Section
    def test_01_write_company_to_partner_info(self):
        company_name = "Demo Company for Joint Buying"
        new_company = self.ResCompany.create({"name": company_name})

        self.assertEqual(
            new_company.joint_buying_partner_id.name,
            "{} (Joint Buyings)".format(company_name),
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

    def test_04_search_partner(self):
        # Check access without context (by search)
        result = self.ResPartner.search(
            [("name", "=", self.joint_buying_supplier.name)]
        )
        self.assertEqual(
            len(result),
            0,
            "Search joint buying partner should not return result without context",
        )

        # Check access without context (by name_search)
        result = self.ResPartner.name_search(self.joint_buying_supplier.name)
        self.assertEqual(
            len(result),
            0,
            "Name Search joint buying partner should not return result without context",
        )

        # Check access with context (by search)
        result = self.ResPartner.with_context(joint_buying=True).search(
            [("name", "=", self.joint_buying_supplier.name)]
        )
        self.assertEqual(
            len(result),
            1,
            "Search joint buying partner should return result with context",
        )

        # Check access with context (by name_search)
        result = self.ResPartner.with_context(joint_buying=True).name_search(
            self.joint_buying_supplier.name
        )
        self.assertEqual(
            len(result),
            1,
            "Name Search joint buying partner should return result with context",
        )

    def test_05_double_link_supplier_to_joint_buying_partner(self):
        # Create a new supplier in a company linked to a joint buying partner should
        # success
        vals = {
            "name": "Test Chocolate-Lala @ CHE",
            "company_id": self.company_CHE.id,
            "supplier": True,
            "joint_buying_partner_id": self.company_CHO.joint_buying_partner_id.id,
        }
        self.ResPartner.create(vals)

        with self.assertRaises(ValidationError):

            # We should not have the possibility to link two suppliers
            # to the same joint buying supplier for the same company
            vals.update({
                "name": "Test Chocolate-Lala @ 3PP",
                "company_id": self.company_3PP.id,
            })
            self.ResPartner.create(vals)
