# Copyright (C) 2021-Today: GRAP (http://www.grap.coop)
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from datetime import timedelta
from math import pi

import pandas as pd
from bokeh.embed import components
from bokeh.palettes import Category20c
from bokeh.plotting import figure
from bokeh.transform import cumsum

from odoo import _, api, fields, models

from .res_partner import _JOINT_BUYING_PARTNER_CONTEXT


class JointBuyingTour(models.Model):
    _name = "joint.buying.tour"
    _inherit = ["mail.thread", "mail.activity.mixin"]
    _description = "Joint buying tour"
    _order = "start_date, name"

    name = fields.Char(compute="_compute_name", store=True)

    summary = fields.Text(compute="_compute_summary", store=True)

    description = fields.Html(compute="_compute_description")

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

    toll_cost = fields.Monetary(currency_field="currency_id")

    cost = fields.Monetary(
        compute="_compute_cost", store=True, currency_field="currency_id"
    )

    salary_cost = fields.Monetary(
        compute="_compute_salary_cost", store=True, currency_field="currency_id"
    )

    vehicle_cost = fields.Monetary(
        compute="_compute_vehicle_cost", store=True, currency_field="currency_id"
    )

    currency_id = fields.Many2one(
        comodel_name="res.currency", related="carrier_id.currency_id"
    )

    cost_chart = fields.Text(compute="_compute_cost_chart")

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

    @api.depends("salary_cost", "toll_cost", "vehicle_cost")
    def _compute_cost(self):
        for tour in self:
            tour.cost = tour.salary_cost + tour.toll_cost + tour.vehicle_cost

    @api.depends("line_ids.salary_cost")
    def _compute_salary_cost(self):
        for tour in self:
            tour.salary_cost = sum(tour.mapped("line_ids.salary_cost"))

    @api.depends("line_ids.vehicle_cost")
    def _compute_vehicle_cost(self):
        for tour in self:
            tour.vehicle_cost = sum(tour.mapped("line_ids.vehicle_cost"))

    @api.depends("vehicle_cost", "salary_cost", "toll_cost")
    def _compute_cost_chart(self):
        for rec in self:
            x = {
                _("Salary"): rec.salary_cost,
                _("Vehicle"): rec.vehicle_cost,
                _("Toll"): rec.toll_cost,
            }
            data = (
                pd.Series(x)
                .reset_index(name="value")
                .rename(columns={"index": "cost_type"})
            )
            data["angle"] = data["value"] / data["value"].sum() * 2 * pi
            data["color"] = Category20c[len(x)]

            p = figure(
                height=300,
                width=300,
                toolbar_location=None,
                tools="hover",
                tooltips="@cost_type: @value",
            )

            p.wedge(
                x=0,
                y=1,
                radius=0.4,
                start_angle=cumsum("angle", include_zero=True),
                end_angle=cumsum("angle"),
                line_color="white",
                fill_color="color",
                source=data,
            )

            p.axis.axis_label = None
            p.axis.visible = False
            p.grid.grid_line_color = None

            script, div = components(p)
            rec.cost_chart = f"{div}{script}"

    @api.depends("line_ids")
    def _compute_stop_qty(self):
        for tour in self:
            tour.stop_qty = max(
                0,
                len(tour.line_ids.filtered(lambda x: x.sequence_type == "journey")) - 1,
            )

    @api.depends("line_ids.starting_point_id", "line_ids.arrival_point_id")
    def _compute_summary(self):
        for tour in self:
            codes = []
            for line in tour.line_ids.filtered(lambda x: x.sequence_type == "journey"):
                if not codes:
                    codes = [
                        line.starting_point_id.joint_buying_company_id
                        and line.starting_point_id.joint_buying_company_id.code
                        or line.starting_point_id.name,
                        line.arrival_point_id.joint_buying_company_id
                        and line.arrival_point_id.joint_buying_company_id.code
                        or line.arrival_point_id.name,
                    ]
                else:
                    codes.append(
                        line.arrival_point_id.joint_buying_company_id
                        and line.arrival_point_id.joint_buying_company_id.code
                        or line.arrival_point_id.name,
                    )
            tour.summary = f"{' -> '.join(codes)}"

    def _compute_description(self):
        def _float_to_strtime(float_value):
            return f"{int(float_value):02d}:{int(60 * (float_value % 1)):02d}"

        for tour in self:
            description = ""
            for i, line in enumerate(tour.line_ids):
                if line.sequence_type == "journey":
                    line_name = _(
                        f"Journey from {line.starting_point_id.name}"
                        f" to {line.arrival_point_id.name}"
                    )
                elif line.sequence_type == "pause":
                    line_name = f"<span style='color: green'><b>{_('Pause')}</b></span>"
                else:
                    if i == 0:
                        line_name = f"<i>{_('Truck loading')}</i>"
                    elif i == len(tour.line_ids) - 1:
                        line_name = f"<i>{_('Truck unloading')}</i>"
                    else:
                        line_name = f"<i>{_('Delivery and pick-up')}</i>"
                description += (
                    f"<b>{_float_to_strtime(line.start_hour)} - "
                    f"{_float_to_strtime(line.arrival_hour)}</b> : {line_name}"
                    "<br/>"
                )
        tour.description = description

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

    @api.multi
    def write(self, vals):
        res = super().write(vals)
        if "start_date" in vals:
            self.recompute_start_hours()
        return res

    def estimate_route(self):
        self.mapped("line_ids").estimate_route()
        self.recompute_start_hours()

    def recompute_start_hours(self):
        def _time_to_float(time):
            return time.hour + time.minute / 60

        for tour in self:
            if not tour.line_ids:
                continue
            date_tz = fields.Datetime.context_timestamp(self, tour.start_date)
            start_hour = _time_to_float(date_tz.time())
            for line in tour.line_ids:
                line.start_hour = start_hour
                line.arrival_hour = start_hour + line.duration
                start_hour += line.duration

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
