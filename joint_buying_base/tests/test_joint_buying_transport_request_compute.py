# Copyright (C) 2021 - Today: GRAP (http://www.grap.coop)
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from datetime import datetime

from odoo.tests import tagged

from .test_abstract import TestAbstract


@tagged("post_install", "-at_install")
class TestJointBuyingTransportRequest(TestAbstract):
    def setUp(self):
        super().setUp()
        self.TransportRequest = self.env["joint.buying.transport.request"]

    def test_create_transport_request_manual(self):
        request = self.TransportRequest.create(
            {
                "manual_origin_partner_id": self.company_CDA.joint_buying_partner_id.id,
                "manual_destination_partner_id": self.company_CHE.joint_buying_partner_id.id,
                "manual_description": "manual_description",
                "manual_start_date": datetime.today(),
                "manual_amount_untaxed": 999,
                "manual_total_weight": 111,
            }
        )
        # Check Type
        self.assertEqual(request.request_type, "manual")

        # Check can change values
        self.assertTrue(request.can_change_date)
        self.assertTrue(request.can_change_extra_data)
        self.assertTrue(request.can_change_partners)

        # Check computation
        request.manual_description = "bob"
        self.assertEqual(request.description, "<p>bob</p>")
        request.manual_amount_untaxed = 888
        self.assertEqual(request.amount_untaxed, 888)
        request.manual_total_weight = 222
        self.assertEqual(request.total_weight, 222)
