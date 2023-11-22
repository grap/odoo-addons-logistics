# Copyright (C) 2021 - Today: GRAP (http://www.grap.coop)
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo.tests import tagged

from .test_abstract import TestAbstract


@tagged("post_install", "-at_install")
class TestTourReportBase(TestAbstract):
    def setUp(self):
        super().setUp()
        self.JointBuyingTour = self.env["joint.buying.tour"]
        self.tour_report = self.env.ref(
            "joint_buying_base.action_report_joint_buying_tour"
        )

    # Test Section
    def test_tour_report(self):
        # Generate report to make sure the syntax is correct
        tours = self.JointBuyingTour.search([])
        self.tour_report.render_qweb_html(tours.ids)
