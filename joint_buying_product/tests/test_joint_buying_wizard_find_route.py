# Copyright (C) 2023 - Today: GRAP (http://www.grap.coop)
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).


from odoo.tests import tagged

from .test_abstract import TestAbstract


@tagged("post_install", "-at_install")
class TestJointBuyingWizardFindRoute(TestAbstract):
    def setUp(self):
        super().setUp()

    def test_20_transport_request_vev_cda_week_1(self):
        """simplest case: direct route"""
        self._verify_tour_lines_computation(
            "joint_buying_product.request_vev_cda_week_1",
            ["joint_buying_base.tour_lyon_loire_1_line_4"],
            "computed",
        )

    def test_21_transport_request_vev_che_week_1(self):
        """Classic case: 1 change"""
        self._verify_tour_lines_computation(
            "joint_buying_product.request_vev_che_week_1",
            [
                "joint_buying_base.tour_lyon_loire_1_line_4",
                "joint_buying_base.tour_lyon_loire_1_line_6",
                "joint_buying_base.tour_lyon_drome_1_line_2",
                "joint_buying_base.tour_lyon_drome_1_line_4",
            ],
            "computed",
        )

    def test_22_transport_request_vev_edc_1(self):
        """Classic case: 2 change"""
        self._verify_tour_lines_computation(
            "joint_buying_product.request_vev_edc_week_1",
            [
                "joint_buying_base.tour_lyon_loire_1_line_4",
                "joint_buying_base.tour_lyon_loire_1_line_6",
                "joint_buying_base.tour_lyon_savoie_1_line_2",
                "joint_buying_base.tours_savoie_1_line_2",
            ],
            "computed",
        )

    def test_23_transport_request_vev_fumet_week_1(self):
        """Use case: No route available"""
        self._verify_tour_lines_computation(
            "joint_buying_product.request_vev_fumet_dombes_week_1", [], "not_computable"
        )

    def _verify_tour_lines_computation(
        self, request_xml_id, tour_line_xml_ids, expected_state
    ):
        transport_request = self.env.ref(request_xml_id)
        wizard = (
            self.env["joint.buying.wizard.find.route"]
            .with_context(active_id=transport_request.id)
            .create({})
        )
        wizard.button_apply()

        tour_line_ids = []
        for line_xml_id in tour_line_xml_ids:
            tour_line_ids.append(self.env.ref(line_xml_id).id)

        self.assertEqual(transport_request.tour_line_ids.ids, tour_line_ids)
        self.assertEqual(transport_request.state, expected_state)
