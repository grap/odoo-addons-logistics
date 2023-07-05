# Copyright (C) 2021-Today: GRAP (http://www.grap.coop)
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from datetime import timedelta

from odoo import _, api, fields, models

from .res_partner import _JOINT_BUYING_PARTNER_CONTEXT


class JointBuyingTour(models.Model):
    _name = "joint.buying.tour"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _description = "Joint buying tour"
    _order = "start_date, name"

    name = fields.Char(required=True)

    calendar_description = fields.Char(
        compute="_compute_calendar_description", store=True
    )

    distance = fields.Float(
        compute="_compute_distance",
        store=True,
    )

    carrier_id = fields.Many2one(
        comodel_name="joint.buying.carrier", string="Carrier", required=True
    )

    start_date = fields.Datetime(required=True, track_visibility=True)

    end_date = fields.Datetime(
        compute="_compute_end_fields", store=True, track_visibility=True
    )

    duration = fields.Float(compute="_compute_end_fields", store=True)

    starting_point_id = fields.Many2one(
        comodel_name="res.partner",
        compute="_compute_points",
        store=True,
        context=_JOINT_BUYING_PARTNER_CONTEXT,
    )

    arrival_point_id = fields.Many2one(
        comodel_name="res.partner",
        compute="_compute_points",
        store=True,
        context=_JOINT_BUYING_PARTNER_CONTEXT,
    )

    line_ids = fields.One2many(
        comodel_name="joint.buying.tour.line",
        inverse_name="tour_id",
        readonly=True,
        copy=True,
        auto_join=True,
    )

    stop_qty = fields.Integer(
        string="Stop Quantity", compute="_compute_stop_qty", store=True
    )

    is_loop = fields.Boolean(string="Is a Loop", compute="_compute_is_loop", store=True)

    # Compute Section
    @api.depends("line_ids")
    def _compute_stop_qty(self):
        for tour in self:
            tour.stop_qty = max(
                0,
                len(tour.line_ids.filtered(lambda x: x.sequence_type == "journey")) - 1,
            )

    @api.depends("carrier_id.name", "stop_qty")
    def _compute_calendar_description(self):
        for tour in self:
            tour.calendar_description = "(%s - %d Stop)" % (
                tour.carrier_id.name,
                tour.stop_qty,
            )

    @api.depends("starting_point_id", "arrival_point_id")
    def _compute_is_loop(self):
        for tour in self:
            tour.is_loop = tour.starting_point_id == tour.arrival_point_id

    @api.depends("line_ids.distance")
    def _compute_distance(self):
        for tour in self:
            tour.distance = sum(tour.mapped("line_ids.distance"))

    @api.depends("line_ids.duration", "start_date")
    def _compute_end_fields(self):
        for tour in self:
            tour.duration = sum(tour.mapped("line_ids.duration"))
            tour.end_date = tour.start_date + timedelta(hours=tour.duration or 1)

    @api.depends(
        "line_ids.starting_point_id", "line_ids.sequence", "line_ids.arrival_point_id"
    )
    def _compute_points(self):
        for tour in self:
            journey_lines = tour.line_ids.filtered(
                lambda x: x.sequence_type == "journey"
            )
            if not journey_lines:
                continue
            tour.starting_point_id = journey_lines[0].starting_point_id
            tour.arrival_point_id = journey_lines[-1].arrival_point_id

    # Overload Section
    @api.multi
    def copy(self, default=None):
        self.ensure_one()
        default = default or {}
        default["name"] = _("%s (copy)") % self.name
        return super().copy(default)

    def estimate_route(self):
        self.mapped("line_ids").estimate_route()
