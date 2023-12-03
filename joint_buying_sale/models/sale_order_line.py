# Copyright (C) 2023-Today: GRAP (http://www.grap.coop)
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import models


class SaleOrderLine(models.Model):
    _inherit = "sale.order.line"

    def _get_report_tour_data(self):
        self.ensure_one()
        return {
            "product_category": self.product_id._get_report_tour_category(),
            "supplier_partner": self.order_id.company_id.joint_buying_partner_id,
            "description": (
                f"{self.product_id.name}"
                "<span style='color:#888;'>"
                f" ({self.product_uom_qty} x {self.product_uom.name}) "
                "</span>"
            ),
        }
