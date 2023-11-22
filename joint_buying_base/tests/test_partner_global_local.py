# Copyright (C) 2021 - Today: GRAP (http://www.grap.coop)
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo.exceptions import ValidationError
from odoo.tests import tagged

from .test_abstract import TestAbstract


@tagged("post_install", "-at_install")
class TestModule(TestAbstract):

    # Test Section
    def test_601_double_link_supplier_to_joint_buying_partner(self):
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
