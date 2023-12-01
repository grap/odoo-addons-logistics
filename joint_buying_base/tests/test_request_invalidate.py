# Copyright (C) 2023 - Today: GRAP (http://www.grap.coop)
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from datetime import timedelta

from .test_abstract import TestAbstract


class TestModule(TestAbstract):
    def setUp(self):
        super().setUp()
        self.request_vev_cda_week_1 = self.env.ref(
            "joint_buying_base.request_vev_cda_week_1"
        )
        self.tour_lyon_loire_1 = self.env.ref("joint_buying_base.tour_lyon_loire_1")
        self.tour_lyon_loire_3 = self.env.ref("joint_buying_base.tour_lyon_loire_3")

    def test_change_tour_invalidate_requests(self):
        initial_loire_1_request_qty = self.tour_lyon_loire_1.transport_request_qty
        initial_loire_3_request_qty = self.tour_lyon_loire_3.transport_request_qty
        loire_1_requests = self.tour_lyon_loire_1.mapped(
            "line_ids.transport_request_line_ids.request_id"
        )
        loire_3_requests = self.tour_lyon_loire_3.mapped(
            "line_ids.transport_request_line_ids.request_id"
        )

        # Ensure that initial data are correct
        self.assertNotEqual(initial_loire_1_request_qty, 0)
        self.assertNotEqual(initial_loire_3_request_qty, 0)

        # Change date of tour should invalidate all related transport requests
        self.tour_lyon_loire_1.start_date += timedelta(seconds=1)
        self.assertEqual(self.tour_lyon_loire_1.transport_request_qty, 0)

        # Change date of tour should invalidate all futur transport requests
        self.assertEqual(self.tour_lyon_loire_3.transport_request_qty, 0)

        # Recompute route should reaffect all the requests to the same tour
        loire_1_requests.button_compute_tour()
        self.assertEqual(
            self.tour_lyon_loire_1.transport_request_qty, initial_loire_1_request_qty
        )
        self.assertEqual(self.tour_lyon_loire_3.transport_request_qty, 0)

        loire_3_requests.button_compute_tour()
        self.assertEqual(
            self.tour_lyon_loire_1.transport_request_qty, initial_loire_1_request_qty
        )
        self.assertEqual(
            self.tour_lyon_loire_3.transport_request_qty, initial_loire_3_request_qty
        )

        # Unlink a tour should invalidate all the futur transport requests
        self.tour_lyon_loire_1.unlink()
        self.assertEqual(self.tour_lyon_loire_3.transport_request_qty, 0)

    def test_change_request_invalidate_request(self):
        # Ensure that initial data are correct
        self.assertEqual(self.request_vev_cda_week_1.state, "computed")

        # Change key fields should invalidate transport request
        self.request_vev_cda_week_1.manual_availability_date += timedelta(seconds=1)
        self.assertEqual(self.request_vev_cda_week_1.state, "to_compute")
