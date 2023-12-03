# Copyright (C) 2023-Today: GRAP (http://www.grap.coop)
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import models


class ProductProduct(models.Model):
    _inherit = "product.product"

    def _get_report_tour_category(self):
        """Overload in other module, to return category that
        will impact order in the joint.buying.tour report"""
        self.ensure_one()
        return self.storage_method or "normal"
