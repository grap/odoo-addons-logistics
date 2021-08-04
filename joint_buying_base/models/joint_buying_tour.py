# Copyright (C) 2021-Today: GRAP (http://www.grap.coop)
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models


class JointBuyingTour(models.Model):
    _name = "joint.buying.tour"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _description = "Joint buying tour"
    _order = "date_tour desc, name"

    name = fields.Char(required=True)

    distance = fields.Float(
        compute="_compute_distance",
        store=True,
        help="Distance as the crow flies, in kilometer",
    )

    date_tour = fields.Date(required=True, track_visibility=True)

    starting_point_id = fields.Many2one(
        comodel_name="res.partner", compute="_compute_points", store=True
    )

    arrival_point_id = fields.Many2one(
        comodel_name="res.partner", compute="_compute_points", store=True
    )

    complete_name = fields.Char(compute="_compute_complete_name")

    line_ids = fields.One2many(
        comodel_name="joint.buying.tour.line", inverse_name="tour_id", readonly=True
    )

    @api.depends("name", "date_tour")
    def _compute_complete_name(self):
        for tour in self:
            tour.complete_name = "{} - {}".format(tour.date_tour, tour.name)

    @api.depends("line_ids.distance")
    def _compute_distance(self):
        for tour in self:
            tour.distance = sum(tour.mapped("line_ids.distance"))

    @api.depends(
        "line_ids.starting_point_id", "line_ids.sequence", "line_ids.arrival_point_id"
    )
    def _compute_points(self):
        # TODO
        pass
