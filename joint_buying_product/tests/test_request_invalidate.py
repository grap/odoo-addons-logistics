# Copyright (C) 2023 - Today: GRAP (http://www.grap.coop)
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from datetime import timedelta

from odoo.addons.joint_buying_base.tests import test_request_invalidate


class TestModule(test_request_invalidate.TestModule):
    def setUp(self):
        super().setUp()
        self.order = self.env.ref("joint_buying_product.order_ronzon_LSE_past")
        self.main_company = self.env.ref("base.main_company")

    def test_20_change_joint_buying_order_invalidate_requests(self):
        deposit_partner = self.order.grouped_order_id.deposit_partner_id
        # Ensure that initial data are correct
        self.assertEqual(self.order.transport_request_id.state, "computed")

        # change start date / end date should not invalidate requests
        self.order.grouped_order_id.start_date += timedelta(seconds=1)
        self.order.grouped_order_id.end_date += timedelta(seconds=1)
        self.assertEqual(self.order.transport_request_id.state, "computed")

        # change deposit partner should invalidate requests
        self.order.grouped_order_id.deposit_partner_id = (
            self.main_company.joint_buying_partner_id
        )
        self.assertEqual(self.order.transport_request_id.state, "to_compute")

        self.order.grouped_order_id.deposit_partner_id = deposit_partner
        self.order.transport_request_id.button_compute_tour()
        self.assertEqual(self.order.transport_request_id.state, "computed")

        # change deposit date should invalidate requests
        self.order.grouped_order_id.deposit_date += timedelta(seconds=1)
        self.assertEqual(self.order.transport_request_id.state, "to_compute")
