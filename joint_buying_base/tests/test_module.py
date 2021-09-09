# Copyright (C) 2021 - Today: GRAP (http://www.grap.coop)
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from datetime import timedelta

from odoo import fields
from odoo.exceptions import AccessError, ValidationError
from odoo.tests.common import TransactionCase, at_install, post_install


@at_install(False)
@post_install(True)
class TestModule(TransactionCase):
    def setUp(self):
        super().setUp()
        self.company_3PP = self.env.ref("joint_buying_base.company_3PP")
        self.user_3PP = self.env.ref("joint_buying_base.user_joint_buying_user")
        self.ResCompany = self.env["res.company"]
        self.TourWizard = self.env["joint.buying.wizard.set.tour"]
        self.JointBuyingTour = self.env["joint.buying.tour"]
        self.ResPartner = self.env["res.partner"].with_context(
            mail_create_nosubscribe=True
        )
        self.joint_buying_supplier = self.env.ref(
            "joint_buying_base.supplier_fumet_dombes"
        )
        self.company_ELD = self.env.ref("joint_buying_base.company_ELD")
        self.company_CHE = self.env.ref("joint_buying_base.company_CHE")
        self.company_3PP = self.env.ref("joint_buying_base.company_3PP")
        self.carrier = self.env.ref("joint_buying_base.carrier_coolivri_lyon")

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
        partner_id = self.company_ELD.joint_buying_partner_id.id
        vals = {
            "name": "Test Elodie-D @ CHE",
            "company_id": self.company_CHE.id,
            "supplier": True,
            "joint_buying_global_partner_id": partner_id,
        }
        self.ResPartner.create(vals)

        with self.assertRaises(ValidationError):

            # We should not have the possibility to link two suppliers
            # to the same joint buying supplier for the same company
            vals.update(
                {"name": "Test Elodie-D @ 3PP", "company_id": self.company_3PP.id}
            )
            self.ResPartner.create(vals)

    def test_06_create_partner_subscription(self):
        self.env.user.company_id.joint_buying_auto_subscribe = False
        supplier = self._create_supplier()
        self.assertFalse(supplier.joint_buying_is_subscribed)

        self.env.user.company_id.joint_buying_auto_subscribe = True
        supplier = self._create_supplier()
        self.assertTrue(supplier.joint_buying_is_subscribed)

        supplier.toggle_joint_buying_is_subscribed()
        self.assertFalse(supplier.joint_buying_is_subscribed)

    def test_07_check_access_mixin_user(self):
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

        # write a supplier. (pivot company = current company) should fail
        partner = self.ResPartner.sudo(user=self.user_3PP).browse(partner_id)
        with self.assertRaises(AccessError):
            partner.write({"name": "Altered name"})

        # unlink a supplier. (pivot company = current company) should fail
        with self.assertRaises(AccessError):
            partner.unlink()

    def test_08_check_access_mixin_manager(self):
        # create a supplier. (pivot company != current company) should success
        self._create_supplier(
            extra_vals={"joint_buying_pivot_company_id": self.company_CHE.id}
        )

        # create a supplier. (pivot company = current company) should success
        self._create_supplier(
            extra_vals={"joint_buying_pivot_company_id": self.company_3PP.id}
        )

    def test_09_set_tour_via_wizard(self):
        tour = self._create_tour()
        self.assertEqual(tour.distance, 0)
        self.assertEqual(tour.line_qty, 0)

    # Custom Functions
    def _create_supplier(self, user=False, extra_vals=False):
        if not user:
            user = self.env.user
        vals = {"name": "My supplier", "supplier": True, "customer": False}
        vals.update(extra_vals or {})
        supplier = (
            self.ResPartner.sudo(user).with_context(joint_buying=True).create(vals)
        )
        return supplier

    def _create_tour(self, user=False, extra_vals=False):
        if not user:
            user = self.env.user
        vals = {
            "name": "My Tour",
            "carrier_id": self.carrier.id,
            "start_date": fields.datetime.now(),
            "end_date": fields.datetime.now() + timedelta(hours=4),
        }
        vals.update(extra_vals or {})
        tour = self.JointBuyingTour.sudo(user).create(vals)
        return tour
