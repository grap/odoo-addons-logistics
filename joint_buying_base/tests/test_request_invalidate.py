# Copyright (C) 2023 - Today: GRAP (http://www.grap.coop)
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from datetime import timedelta

from .test_abstract import TestAbstract


class TestModule(TestAbstract):
    def setUp(self):
        super().setUp()
        self.WizardTour = self.env["joint.buying.wizard.set.tour"]
        self.request_vev_cda_week_1 = self.env.ref(
            "joint_buying_base.request_vev_cda_week_1"
        )
        self.tour_lyon_loire_1 = self.env.ref("joint_buying_base.tour_lyon_loire_1")
        self.tour_lyon_loire_3 = self.env.ref("joint_buying_base.tour_lyon_loire_3")

    def test_01_change_tour_start_date_invalidate_requests(self):
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

    def test_02_change_tour_line_ids_invalidate_requests(self):
        # Ensure that initial data are correct
        requests = self.tour_lyon_loire_1.mapped(
            "line_ids.transport_request_line_ids.request_id"
        )
        initial_request_qty = len(requests)
        self.assertNotEqual(initial_request_qty, 0)

        # Change steps duration should unlink related transport requests
        wizard = self.WizardTour.with_context(
            active_id=self.tour_lyon_loire_1.id
        ).create({})
        wizard.line_ids.filtered(lambda x: x.sequence_type == "journey").write(
            {"duration": 2}
        )
        wizard.set_tour()
        self.assertEqual(self.tour_lyon_loire_1.transport_request_qty, 0)
        self.assertTrue(set(requests.mapped("state")), {"to_compute"})

        # Recompute requests must return to the original situation
        requests.button_compute_tour()
        self.assertEqual(
            self.tour_lyon_loire_1.transport_request_qty, initial_request_qty
        )
        self.assertTrue(set(requests.mapped("state")), {"computed"})

    def test_10_change_request_invalidate_request(self):
        # Ensure that initial data are correct
        self.assertEqual(self.request_vev_cda_week_1.state, "computed")

        # Change key fields should invalidate transport request
        self.request_vev_cda_week_1.manual_availability_date += timedelta(seconds=1)
        self.assertEqual(self.request_vev_cda_week_1.state, "to_compute")

    def test_100_execute_cron(self):
        # Ensure that initial data are correct
        self.assertEqual(self.request_vev_cda_week_1.state, "computed")

        self.request_vev_cda_week_1._invalidate()
        self.assertEqual(self.request_vev_cda_week_1.state, "to_compute")

        # Execute cron without changing delay should not recompute
        self.request_vev_cda_week_1.cron_compute_tour(10)
        self.assertEqual(self.request_vev_cda_week_1.state, "to_compute")

        # Execute cron without changing delay should not recompute
        self.request_vev_cda_week_1.cron_compute_tour(-1)
        self.assertEqual(self.request_vev_cda_week_1.state, "computed")
