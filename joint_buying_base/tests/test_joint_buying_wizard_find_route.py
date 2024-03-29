# Copyright (C) 2023 - Today: GRAP (http://www.grap.coop)
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from datetime import timedelta

from odoo.tests import tagged

from .test_abstract import TestAbstract


@tagged("post_install", "-at_install", "find_route")
class TestJointBuyingWizardFindRoute(TestAbstract):
    def setUp(self):
        super().setUp()
        self.IrConfigParameter = self.env["ir.config_parameter"].sudo()
        self.max_duration = int(
            self.IrConfigParameter.get_param("joint_buying_base.tour_max_duration", 0)
        )

    def test_20_transport_request_vev_cda_week_1(self):
        """simplest case: direct route"""
        self._verify_tour_lines_computation(
            "joint_buying_base.request_vev_cda_week_1",
            [
                "joint_buying_base.tour_lyon_loire_1_line_4",  # VEV->CDA
            ],
            "computed",
        )

    def test_21_transport_request_vev_che_week_1(self):
        """Classic case: 1 change"""
        self._verify_tour_lines_computation(
            "joint_buying_base.request_vev_che_week_1",
            [
                "joint_buying_base.tour_lyon_loire_1_line_4",  # VEV->CDA
                "joint_buying_base.tour_lyon_loire_1_line_6",  # CDA->LSE
                "joint_buying_base.tour_lyon_drome_1_line_2",  # LSE->C3P
                "joint_buying_base.tour_lyon_drome_1_line_4",  # C3P->CHE
            ],
            "computed",
        )

    def test_22_transport_request_vev_edc_1(self):
        """Classic case: 2 change"""
        self._verify_tour_lines_computation(
            "joint_buying_base.request_vev_edc_week_1",
            [
                "joint_buying_base.tour_lyon_loire_1_line_4",  # VEV->CDA
                "joint_buying_base.tour_lyon_loire_1_line_6",  # CDA->LSE
                "joint_buying_base.tour_lyon_savoie_1_line_2",  # LSE->Cognin
                "joint_buying_base.tours_savoie_1_line_2",  # Cognin->EDC
            ],
            "computed",
        )

    def test_23_transport_request_vev_fumet_week_1(self):
        """Use case: No route available"""
        self._verify_tour_lines_computation(
            "joint_buying_base.request_vev_fumet_dombes_week_1", [], "not_computable"
        )

    def test_24_transport_request_vev_che_week_2(self):
        """Complex case: a later start arrives earlier"""
        self._verify_tour_lines_computation(
            "joint_buying_base.request_vev_che_week_2",
            [
                "joint_buying_base.tour_lyon_loire_3_line_2",  # VEV->LSE
                "joint_buying_base.tour_lyon_drome_2_line_2",  # LSE->C3P
                "joint_buying_base.tour_lyon_drome_2_line_4",  # C3P->CHE
            ],
            "computed",
        )

    def test_25_transport_request_vev_lse_week_1(self):
        """Complex case: product availability is after the truck has left,
        but before it passes through"""
        self._verify_tour_lines_computation(
            "joint_buying_base.request_vev_lse_week_1",
            [
                "joint_buying_base.tour_lyon_loire_1_line_4",  # VEV->CDA
                "joint_buying_base.tour_lyon_loire_1_line_6",  # CDA->LSE
            ],
            "computed",
        )

    def test_26_transport_request_vev_cda_week_1(self):
        """Simple case: Check maximum duration to deliver"""
        request = self.env.ref("joint_buying_base.request_vev_lse_week_1")
        tour = self.env.ref("joint_buying_base.tour_lyon_loire_1")

        # Max duration - 1 should success
        request.manual_availability_date = tour.start_date - timedelta(
            days=self.max_duration - 1
        )
        self._verify_tour_lines_computation(
            "joint_buying_base.request_vev_lse_week_1",
            [
                "joint_buying_base.tour_lyon_loire_1_line_4",  # VEV->CDA
                "joint_buying_base.tour_lyon_loire_1_line_6",  # CDA->LSE
            ],
            "computed",
        )

        # Max duration + 1 should fail
        request.manual_availability_date = tour.start_date - timedelta(
            days=self.max_duration + 1
        )
        self._verify_tour_lines_computation(
            "joint_buying_base.request_vev_lse_week_1", [], "not_computable"
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

        self.assertEqual(
            transport_request.mapped("line_ids.tour_line_id").ids, tour_line_ids
        )
        self.assertEqual(transport_request.state, expected_state)
