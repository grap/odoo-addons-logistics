# Copyright (C) 2023 - Today: GRAP (http://www.grap.coop)
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).


from odoo.tests import tagged

from odoo.addons.joint_buying_product.tests import (
    test_joint_buying_transport_request_compute,
)


@tagged("post_install", "-at_install")
class TestJointBuyingTransportRequest(
    test_joint_buying_transport_request_compute.TestJointBuyingTransportRequest
):
    def setUp(self):
        super().setUp()
        self.sale_order = self.env.ref("joint_buying_sale.sale_order_1")
        self.sale_order_line = self.env.ref("joint_buying_sale.sale_order_1_line_1")

    def test_create_transport_request_sale(self):
        request = self.sale_order.joint_buying_transport_request_id

        # Check that transport request is created
        self.assertTrue(request)
        self.assertEqual(request.request_type, "sale")

        # Check can change values
        self.assertTrue(request.can_change_date)
        self.assertFalse(request.can_change_extra_data)
        self.assertTrue(request.can_change_partners)

        # Check computation
        first_description = request.description
        first_amount_untaxed = request.amount_untaxed
        first_total_weight = request.total_weight

        # (The order contains Agila x 80 and Charlotte x 60)
        self.assertIn("(3", first_description)
        self.assertNotIn("(2222", first_description)

        self.assertAlmostEqual(first_amount_untaxed, self.sale_order.amount_untaxed)

        self.assertAlmostEqual(first_total_weight, self.sale_order.total_ordered_weight)

        # Change value of order line qty and check recomputation
        self.sale_order_line.product_uom_qty = 2222

        self.assertNotIn("(3", request.description)
        self.assertIn("(2222", request.description)
        self.assertNotEqual(first_amount_untaxed, request.description)

        self.assertAlmostEqual(request.amount_untaxed, self.sale_order.amount_untaxed)
        self.assertNotEqual(first_amount_untaxed, request.amount_untaxed)

        first_total_weight = first_total_weight
        self.assertAlmostEqual(
            request.total_weight, self.sale_order.total_ordered_weight
        )
        self.assertNotEqual(first_total_weight, request.total_weight)
