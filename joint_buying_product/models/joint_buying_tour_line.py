# Copyright (C) 2023-Today: GRAP (http://www.grap.coop)
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models

from odoo.addons import decimal_precision as dp


class JointBuyingTourLine(models.Model):
    _inherit = "joint.buying.tour.line"

    transport_request_ids = fields.Many2many(
        comodel_name="joint.buying.transport.request",
        string="Transport Requests",
    )

    load = fields.Float(
        compute="_compute_load",
        digits=dp.get_precision("Stock Weight"),
    )

    def _compute_load(self):
        for tour_line in self:
            tour_line.load = sum(
                tour_line.mapped("transport_request_line_ids.request_id.total_weight")
            )
