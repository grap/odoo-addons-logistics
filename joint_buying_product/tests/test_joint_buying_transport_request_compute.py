# Copyright (C) 2021 - Today: GRAP (http://www.grap.coop)
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from datetime import datetime, timedelta

from odoo.tests import tagged

from .test_abstract import TestAbstract


@tagged("post_install", "-at_install")
class TestJointBuyingTransportRequest(TestAbstract):
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

    def test_joint_buying_order_change_delivery_partner(self):
        # This demo grouped order is delivered in 1GG
        order_VEV = self.env.ref("joint_buying_product.order_ronzon_VEV_past")

        self.assertTrue(order_VEV.transport_request_id)
        request = order_VEV.transport_request_id
        self.assertEqual(request.start_partner_id.joint_buying_code, "1GG")
        self.assertEqual(request.arrival_partner_id.joint_buying_code, "VEV")

        # check initial computation
        request.button_compute_tour()
        self.assertEqual(request.state, "computed")
        self.assertEqual(len(request.line_ids), 2)
        self.assertEqual(request.line_ids[0].starting_point_id.joint_buying_code, "1GG")
        self.assertEqual(request.line_ids[0].arrival_point_id.joint_buying_code, "LSE")
        self.assertEqual(request.line_ids[1].starting_point_id.joint_buying_code, "LSE")
        self.assertEqual(request.line_ids[1].arrival_point_id.joint_buying_code, "VEV")

        # Change delivery_partner_id to the deposit_partner_id
        # should delete the transport request
        order_VEV.delivery_partner_id = self.company_1GG.joint_buying_partner_id
        self.assertFalse(order_VEV.transport_request_id)

        # Change delivery_partner_id to a third partner
        # should recrate the transport request
        order_VEV.delivery_partner_id = self.company_CDA.joint_buying_partner_id
        self.assertTrue(order_VEV.transport_request_id)
        request = order_VEV.transport_request_id
        self.assertEqual(request.start_partner_id.joint_buying_code, "1GG")
        self.assertEqual(request.arrival_partner_id.joint_buying_code, "CDA")
        self.assertEqual(request.state, "to_compute")

        request.button_compute_tour()
        self.assertEqual(request.state, "computed")
        self.assertEqual(len(request.line_ids), 3)
        self.assertEqual(request.line_ids[0].starting_point_id.joint_buying_code, "1GG")
        self.assertEqual(request.line_ids[0].arrival_point_id.joint_buying_code, "LSE")
        self.assertEqual(request.line_ids[1].starting_point_id.joint_buying_code, "LSE")
        self.assertEqual(request.line_ids[1].arrival_point_id.joint_buying_code, "VEV")
        self.assertEqual(request.line_ids[2].starting_point_id.joint_buying_code, "VEV")
        self.assertEqual(request.line_ids[2].arrival_point_id.joint_buying_code, "CDA")

    def test_joint_buying_order_grouped_change_deposit_partner(self):

        grouped_order = self.env.ref("joint_buying_product.grouped_order_ronzon_past")
        order_LSE = grouped_order.order_ids.filtered(
            lambda x: x.customer_id.joint_buying_code == "LSE"
        )
        self.assertTrue(order_LSE.transport_request_id)

        # Change the deposit partner should delete the order
        # of the customer which is in the deposit place
        grouped_order.deposit_partner_id = self.company_LSE.joint_buying_partner_id
        self.assertFalse(order_LSE.transport_request_id)

        # Change the deposit partner should create the order
        # of the customer which is not in the deposit place
        grouped_order.deposit_partner_id = self.company_1GG.joint_buying_partner_id
        self.assertTrue(order_LSE.transport_request_id)
