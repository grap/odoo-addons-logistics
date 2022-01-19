# Copyright (C) 2021-Today: GRAP (http://www.grap.coop)
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from geopy.distance import geodesic

from odoo import api, fields, models

from .res_partner import _JOINT_BUYING_PARTNER_CONTEXT


class JointBuyingTourLine(models.Model):
    _name = "joint.buying.tour.line"
    _description = "Joint Buying Tour Lines"
    _order = "sequence"

    sequence = fields.Integer()

    distance = fields.Float(
        compute="_compute_distance",
        store=True,
        help="Distance as the crow flies, in kilometer",
    )

    tour_id = fields.Many2one(
        comodel_name="joint.buying.tour", required=True, ondelete="cascade"
    )

    starting_point_id = fields.Many2one(
        comodel_name="res.partner", context=_JOINT_BUYING_PARTNER_CONTEXT, required=True
    )

    arrival_point_id = fields.Many2one(
        comodel_name="res.partner", context=_JOINT_BUYING_PARTNER_CONTEXT, required=True
    )

    # @api.depends(
    #     "tour_id.starting_point_id",
    #     "tour_id.line_ids.sequence",
    #     "tour_id.line_ids.arrival_point_id",
    # )
    # def _compute_starting_point_id(self):
    #     # This check prevent recompute on the fly,
    #     # when editing a tour, because the recompute is partial.
    #     # only the edited line, and so it is not possible to computed
    #     # the starting_point, based on the arrival of the previous line
    #     if len(self) == 1 and isinstance(self.id, models.NewId):
    #         return
    #     previous_point = self.mapped("tour_id").starting_point_id
    #     for line in self.sorted("sequence"):
    #         line.starting_point_id = previous_point.id
    #         previous_point = line.arrival_point_id

    @api.depends(
        "starting_point_id.partner_latitude",
        "starting_point_id.partner_longitude",
        "arrival_point_id.partner_latitude",
        "arrival_point_id.partner_longitude",
    )
    def _compute_distance(self):
        for line in self:
            C1 = (
                line.starting_point_id.partner_latitude,
                line.starting_point_id.partner_longitude,
            )
            C2 = (
                line.arrival_point_id.partner_latitude,
                line.arrival_point_id.partner_longitude,
            )
            if C1 != (0, 0) and C2 != (0, 0):
                line.distance = geodesic(C1, C2).km
