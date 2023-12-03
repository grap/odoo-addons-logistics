# Copyright (C) 2023-Today: GRAP (http://www.grap.coop)
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import models


class JointBuyingTour(models.Model):
    _inherit = "joint.buying.tour"

    def get_report_tour_category_url(self, category):
        return f"/joint_buying_product_food/static/description/{category}.png"
