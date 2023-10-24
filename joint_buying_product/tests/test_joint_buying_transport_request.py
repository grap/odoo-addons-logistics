# Copyright (C) 2021 - Today: GRAP (http://www.grap.coop)
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).


from odoo.tests import tagged

from .test_abstract import TestAbstract


@tagged("post_install", "-at_install")
class TestJointBuyingTransportRequest(TestAbstract):
    def setUp(self):
        super().setUp()

    def test_10_joint_buying_grouped_order_generate_transport_request(self):
        # Creates a grouped order
        # - Deposit company LSE
        # - Subscribed companies : LSE / VEV / CDA
        self._get_grouped_order_benoit_ronzon()

        # Get according orders
        LSE_order = self._get_order_benoit_ronzon("LSE")
        VEV_order = self._get_order_benoit_ronzon("VEV")
        CDA_order = self._get_order_benoit_ronzon("CDA")

        # It should generate transport request for CDA and VEV
        self.assertTrue(CDA_order.request_id)
        self.assertTrue(VEV_order.request_id)

        # It should not create a transport request for LSE
        self.assertFalse(LSE_order.request_id)
