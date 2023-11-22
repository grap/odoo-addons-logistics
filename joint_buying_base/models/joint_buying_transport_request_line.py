# Copyright (C) 2023-Today: GRAP (http://www.grap.coop)
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models

from .res_partner import _JOINT_BUYING_PARTNER_CONTEXT


class JointBuyingTransportRequestLine(models.Model):
    _name = "joint.buying.transport.request.line"
    _description = "Joint Buying Transport Line"

    request_id = fields.Many2one(
        comodel_name="joint.buying.transport.request",
        ondelete="cascade",
        required=True,
    )

    tour_line_id = fields.Many2one(
        comodel_name="joint.buying.tour.line",
        required=True,
    )

    start_action_type = fields.Selection(
        selection=[
            ("no", "🠢🠢🠢"),
            ("loading", "🠡🠡 Loading 🠡🠡"),
        ],
        required=True,
    )

    arrival_action_type = fields.Selection(
        selection=[
            ("no", "🠢🠢🠢"),
            ("unloading", "🠣🠣 Unloading 🠣🠣"),
        ],
        required=True,
    )

    start_date = fields.Datetime(related="tour_line_id.start_date")

    arrival_date = fields.Datetime(related="tour_line_id.arrival_date")

    starting_point_id = fields.Many2one(
        comodel_name="res.partner",
        related="tour_line_id.starting_point_id",
        context=_JOINT_BUYING_PARTNER_CONTEXT,
    )

    arrival_point_id = fields.Many2one(
        comodel_name="res.partner",
        related="tour_line_id.arrival_point_id",
        context=_JOINT_BUYING_PARTNER_CONTEXT,
    )

    distance = fields.Float(related="tour_line_id.distance")

    # def get_report_information(self):
    #     self.ensure_one()
    #     if self.request_id.order_id:
    #         order_lines = self.mapped("request_id.order_id.line_ids").filtered(
    #             lambda x: x.qty != 0
    #         )
    #         return {
    #             "all": [
    #                 (x.product_id, f"{x.qty} x {x.uom_id.name}") for x in order_lines
    #             ]
    #         }
