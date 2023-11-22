# Copyright (C) 2023 - Today: GRAP (http://www.grap.coop)
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo.tests import tagged

from odoo.addons.joint_buying_base.tests import test_tour_report


@tagged("post_install", "-at_install")
class TestTourReportProduct(test_tour_report.TestTourReportBase):
    pass
