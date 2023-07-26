# Copyright (C) 2021 - Today: GRAP (http://www.grap.coop)
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields
from odoo.tests import tagged
from odoo.tests.common import TransactionCase


@tagged("post_install", "-at_install")
class TestModule(TransactionCase):
    def setUp(self):
        super().setUp()
        self.JointBuyingTour = self.env["joint.buying.tour"]
        self.WizardTour = self.env["joint.buying.wizard.set.tour"]
        self.carrier = self.env.ref("joint_buying_base.carrier_coolivri_grap")
        self.point_romagnieu = self.env.ref("joint_buying_base.place_romagnieu")
        self.point_3PP = self.env.ref(
            "joint_buying_base.company_3PP"
        ).joint_buying_partner_id
        self.tour_lyon_savoie = self.env.ref("joint_buying_base.tour_lyon_savoie_1")

    # Test Section
    def test_101_set_tour_via_wizard(self):
        tour = self.JointBuyingTour.create(
            {
                "name": "My Test Tour",
                "carrier_id": self.carrier.id,
                "start_date": fields.datetime.now(),
            }
        )
        self.assertEqual(tour.distance, 0)
        self.assertEqual(tour.duration, 0)
        self.assertEqual(tour.stop_qty, 0)

        wizard = self.WizardTour.create(
            {"starting_point_id": self.point_romagnieu.id, "tour_id": tour.id}
        )
        line_vals = [
            {
                "sequence_type": "handling",
                "duration": 30 / 60,
            },
            {
                "sequence_type": "journey",
                "point_id": self.point_3PP.id,
            },
            {
                "sequence_type": "handling",
                "duration": 10 / 60,
            },
            {
                "sequence_type": "journey",
                "point_id": self.point_3PP.id,
            },
            {
                "sequence_type": "handling",
                "duration": 30 / 60,
            },
        ]
        wizard.write({"line_ids": [(0, 0, x) for x in line_vals]})
        wizard.set_tour()
        self.assertEqual(len(tour.line_ids), 5)
        self.assertEqual(tour.distance, 0)
        self.assertEqual(tour.stop_qty, 1)
        self.assertAlmostEqual(tour.duration, 70 / 60)

    def _assert_not_very_differrent(self, value_1, value_2):
        if value_1 == 0 or value_2 == 0:
            return self.assertEqual(value_1, value_2)
        ratio = (value_2 - value_1) / value_1
        self.assertTrue(ratio < 0.1, f"{value_1} is too different than {value_2}")

    def test_102_estimate_route(self):
        self.tour_lyon_savoie.line_ids.filtered(
            lambda x: x.sequence_type == "journey"
        ).write(
            {
                "distance": 0,
                "duration": 0,
            }
        )
        self.assertEqual(self.tour_lyon_savoie.distance, 0)
        self.assertAlmostEqual(self.tour_lyon_savoie.duration, 105 / 60)
        self.tour_lyon_savoie.estimate_route()

        self._assert_not_very_differrent(self.tour_lyon_savoie.distance, 80 * 2)
        self._assert_not_very_differrent(
            self.tour_lyon_savoie.duration, (55 + 55 + 105) / 60
        )
