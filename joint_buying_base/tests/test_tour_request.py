# Copyright (C) 2023 - Today: GRAP (http://www.grap.coop)
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from datetime import timedelta

from odoo.tests import tagged

from .test_abstract import TestAbstract


@tagged("post_install", "-at_install")
class TestModule(TestAbstract):
    def setUp(self):
        super().setUp()
        self.tour_lyon_loire = self.env.ref("joint_buying_base.tour_lyon_loire_1")
        self.tour_lyon_drome = self.env.ref("joint_buying_base.tour_lyon_drome_1")

    def _TODO_test_change_tour_invalidate_requests(self):
        initial_loire_request_qty = self.tour_lyon_loire.transport_request_qty
        initial_drome_request_qty = self.tour_lyon_drome.transport_request_qty
        loire_requests = self.tour_lyon_loire.mapped(
            "line_ids.transport_request_line_ids.request_id"
        )
        drome_requests = self.tour_lyon_drome.mapped(
            "line_ids.transport_request_line_ids.request_id"
        )

        # Ensure that initial data are correct
        self.assertNotEqual(initial_loire_request_qty, 0)
        self.assertNotEqual(initial_drome_request_qty, 0)

        # Change date of tour should invalidate all related transport requests
        self.tour_lyon_loire.start_date = self.tour_lyon_loire.start_date + timedelta(
            seconds=1
        )
        self.assertEqual(self.tour_lyon_loire.transport_request_qty, 0)

        # Change date of tour should invalidate all futur transport requests
        self.assertEqual(self.tour_lyon_drome.transport_request_qty, 0)

        # Recompute route should reaffect all the requests to the same tour
        loire_requests.button_compute_tour()
        self.assertEqual(
            self.tour_lyon_loire.transport_request_qty, initial_loire_request_qty
        )
        self.assertEqual(self.tour_lyon_drome.transport_request_qty, 0)

        drome_requests.button_compute_tour()
        self.assertEqual(
            self.tour_lyon_loire.transport_request_qty, initial_loire_request_qty
        )
        self.assertEqual(
            self.tour_lyon_drome.transport_request_qty, initial_drome_request_qty
        )

        # Unlink a tour should invalidate all the futur transport requests
        self.tour_lyon_loire.unlink()
        self.assertEqual(self.tour_lyon_drome.transport_request_qty, 0)
