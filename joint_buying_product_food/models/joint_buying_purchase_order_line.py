# Copyright (C) 2023-Today: GRAP (http://www.grap.coop)
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import math

from odoo import api, fields, models


class JointBuyingPurchaseOrderLine(models.Model):
    _inherit = "joint.buying.purchase.order.line"

    residual_use_by_date = fields.Integer(compute="_compute_residual_use_by_date")

    @api.depends(
        "product_id.use_by_date_day",
        "order_id.request_arrival_date",
        "order_id.deposit_date",
    )
    def _compute_residual_use_by_date(self):
        for line in self.filtered(
            lambda x: not x.product_id.use_by_date_day
            or not x.order_id.request_arrival_date
        ):
            line.residual_use_by_date = -999
        for line in self.filtered(
            lambda x: x.product_id.use_by_date_day and x.order_id.request_arrival_date
        ):
            line.residual_use_by_date = line.product_id.use_by_date_day - math.ceil(
                (
                    line.order_id.request_arrival_date - line.order_id.deposit_date
                ).total_seconds()
                / 3600
                / 24
            )
