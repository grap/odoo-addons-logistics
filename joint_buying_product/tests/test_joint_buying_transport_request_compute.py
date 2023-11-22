# Copyright (C) 2021 - Today: GRAP (http://www.grap.coop)
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from datetime import datetime, timedelta

from odoo.tests import tagged

from odoo.addons.joint_buying_base.tests import (
    test_joint_buying_transport_request_compute,
)


@tagged("post_install", "-at_install")
class TestJointBuyingTransportRequest(
    test_joint_buying_transport_request_compute.TestJointBuyingTransportRequest
):
    def setUp(self):
        super().setUp()

    def test_create_transport_request_joint_buying(self):
        grouped_order = self.env.ref(
            "joint_buying_product.grouped_order_ronzon_past"
        ).copy(
            default={
                "start_date": datetime.today(),
                "end_date": datetime.today() + timedelta(days=10),
                "deposit_date": datetime.today() + timedelta(days=20),
            }
        )

        order_VEV = grouped_order.order_ids.filtered(
            lambda x: x.customer_id.joint_buying_code == "VEV"
        )
        request = order_VEV.transport_request_id

        # Check that transport request is created
        self.assertTrue(request)
        self.assertEqual(request.request_type, "joint_buying")

        # Check can change values
        self.assertFalse(request.can_change_date)
        self.assertFalse(request.can_change_extra_data)
        self.assertFalse(request.can_change_partners)

        # Check computation
        # (The order contains Agila x 80 and Charlotte x 60)
        self.assertIn("(80", request.description)
        self.assertNotIn("(990", request.description)

        self.assertEqual(request.amount_untaxed, order_VEV.amount_untaxed)
        self.assertEqual(request.total_weight, order_VEV.total_weight)

        # Change value of order line qty and check recomputation
        # (Set Agila from 80 -> 990)
        order_VEV.line_ids.filtered(lambda x: x.qty == 80).qty = 990

        self.assertIn("(990", request.description)
        self.assertNotIn("(80", request.description)

        self.assertEqual(request.amount_untaxed, order_VEV.amount_untaxed)
        self.assertEqual(request.total_weight, order_VEV.total_weight)
