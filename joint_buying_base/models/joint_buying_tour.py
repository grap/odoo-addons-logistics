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

    name = fields.Char(compute="_compute_name", store=True)

    calendar_description = fields.Char(
        compute="_compute_calendar_description", store=True
    )

    distance = fields.Float(
        compute="_compute_distance",
        store=True,
    )

    carrier_id = fields.Many2one(comodel_name="joint.buying.carrier", required=True)

    type_id = fields.Many2one(
        comodel_name="joint.buying.tour.type",
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

    hourly_cost = fields.Monetary(currency_field="currency_id")

    kilometer_cost = fields.Monetary(currency_field="currency_id")

    cost = fields.Monetary(
        compute="_compute_cost", store=True, currency_field="currency_id"
    )

    currency_id = fields.Many2one(
        comodel_name="res.currency", related="carrier_id.currency_id"
    )

    @api.onchange("type_id")
    def _onchange_type_id(self):
        if self.type_id and self.type_id.carrier_id:
            self.carrier_id = self.type_id.carrier_id

    @api.onchange("carrier_id")
    def _onchange_carrier_id(self):
        if self.carrier_id:
            self.payload = self.carrier_id.payload
            self.hourly_cost = self.carrier_id.hourly_cost
            self.kilometer_cost = self.carrier_id.kilometer_cost

    # Compute Section
    @api.depends("start_date", "type_id")
    def _compute_name(self):
        for tour in self:
            tour.name = f"{tour.start_date.strftime('%Y-%m-%d')}"
            if tour.type_id:
                tour.name += f" - {tour.type_id.name}"

    @api.depends("hourly_cost", "kilometer_cost", "duration", "distance")
    def _compute_cost(self):
        for tour in self:
            tour.cost = (tour.duration * tour.hourly_cost) + (
                tour.distance * tour.kilometer_cost
            )

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

    def see_steps(self):
        self.ensure_one()
        action = self.env["ir.actions.act_window"].for_xml_id(
            "joint_buying_base", "action_res_partner_stage"
        )
        steps = self.mapped("line_ids.starting_point_id") | self.mapped(
            "line_ids.arrival_point_id"
        )
        action["view_mode"] = "leaflet_map,tree,form"
        action["domain"] = [("id", "in", steps.ids)]
        return action
