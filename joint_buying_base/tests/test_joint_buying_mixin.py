# Copyright (C) 2021 - Today: GRAP (http://www.grap.coop)
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo.tests import tagged

from .test_abstract import TestAbstract


@tagged("post_install", "-at_install")
class TestModule(TestAbstract):
    def setUp(self):
        super().setUp()
        self.joint_buying_supplier = self.env.ref(
            "joint_buying_base.supplier_fumet_dombes"
        )

    # Test Section
    def test_201_search_partner(self):
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
