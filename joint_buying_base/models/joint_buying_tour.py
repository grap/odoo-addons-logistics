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
from dateutil.relativedelta import relativedelta

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

    transport_request_qty = fields.Integer(compute="_compute_transport_request_qty")

    is_on_my_way = fields.Boolean(
        compute="_compute_is_on_my_way",
        search="_search_is_on_my_way",
        help="Technical field that indicates that the tour"
        " passes through the current company.",
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
            tour.name = ""
            if tour.start_date:
                tour.name = f"{tour.start_date.strftime('%Y-%m-%d')}"
            if tour.type_id:
                tour.name += f" - {tour.type_id.name}"
            if not tour.name:
                tour.name = _("Draft Tour")

    @api.depends("line_ids.transport_request_line_ids.request_id")
    def _compute_transport_request_qty(self):
        for request in self:
            request.transport_request_qty = len(
                request.mapped("line_ids.transport_request_line_ids.request_id")
            )

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
                        line.starting_point_id.joint_buying_code,
                        line.arrival_point_id.joint_buying_code,
                    ]
                else:
                    codes.append(line.arrival_point_id.joint_buying_code)
            tour.summary = f"{' -> '.join(codes)}"

    def _compute_description(self):
        def _float_to_strtime(float_value):
            return f"{int(float_value):02d}:{int(60 * (float_value % 1)):02d}"

        for tour in self:
            description = ""
            for i, line in enumerate(tour.line_ids):
                if line.sequence_type == "journey":
                    line_name = _("Journey from %s to %s") % (
                        line.starting_point_id.name,
                        line.arrival_point_id.name,
                    )
                elif line.sequence_type == "pause":
                    line_name = _("<span style='color: green'><b>Pause</b></span>")
                else:
                    if i == 0:
                        line_name = _("<i>Truck loading</i>")
                    elif i == len(tour.line_ids) - 1:
                        line_name = _("<i>Truck unloading</i>")
                    else:
                        line_name = _("<i>Delivery and pick-up</i>")
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
            if tour.start_date:
                tour.duration = sum(tour.mapped("line_ids.duration"))
                tour.end_date = tour.start_date + timedelta(hours=tour.duration or 1)
            else:
                tour.end_date = False

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

    @api.depends("line_ids.starting_point_id", "line_ids.arrival_point_id")
    def _compute_is_on_my_way(self):
        current_partner = self.env.user.company_id.joint_buying_partner_id
        for tour in self:
            tour.is_on_my_way = current_partner in self.mapped(
                "line_ids.starting_point_id"
            ) or current_partner in self.mapped("line_ids.arrival_point_id")

    # Search Section
    def _search_is_on_my_way(self, operator, value):
        current_partner = self.env.user.company_id.joint_buying_partner_id
        if (operator == "=" and value) or (operator == "!=" and not value):
            search_operator = "in"
        else:
            search_operator = "not in"
        tour_lines = self.env["joint.buying.tour.line"].search(
            [
                "|",
                ("starting_point_id", "=", current_partner.id),
                ("arrival_point_id", "=", current_partner.id),
            ]
        )
        return [("id", search_operator, tour_lines.mapped("tour_id").ids)]

    # Overload Section
    @api.multi
    def copy(self, default=None):
        self.ensure_one()
        default = default or {}
        default["name"] = _("%s (copy)") % self.name
        return super().copy(default)

    @api.multi
    def write(self, vals):
        min_date = min(self.mapped("start_date"))
        res = super().write(vals)
        if {"start_date", "line_ids"}.intersection(vals.keys()):
            self.recompute_dates()
        min_date = min([min_date] + self.mapped("start_date"))
        self._invalidate_transport_requests(min_date)
        return res

    @api.multi
    def unlink(self):
        min_date = min(self.mapped("start_date"))
        self._invalidate_transport_requests(min_date)
        return super().unlink()

    @api.model
    def _invalidate_transport_requests(self, min_date):
        requests = self.env["joint.buying.transport.request"].search(
            [("state", "=", "computed"), ("arrival_date", ">", min_date)]
        )
        requests._invalidate()

    def estimate_route(self):
        self.mapped("line_ids")._estimate_route()
        self.recompute_dates()

    def recompute_dates(self):
        for tour in self:
            start_date = tour.start_date
            for line in tour.line_ids:
                arrival_date = start_date + relativedelta(hours=line.duration)
                line.write(
                    {
                        "start_date": start_date,
                        "arrival_date": arrival_date,
                    }
                )
                start_date = arrival_date

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

    @api.multi
    def display_time(self, time):
        return (
            f"{str(int(time)).rjust(2, '0')}"
            f":{str(int((time % 1) * 60)).rjust(2, '0')}"
        )

    @api.multi
    def button_see_transport_requests(self):
        self.ensure_one()
        res = self.env["ir.actions.act_window"].for_xml_id(
            "joint_buying_base", "action_joint_buying_transport_request"
        )
        requests = self.mapped("line_ids.transport_request_line_ids.request_id")
        res["domain"] = [("id", "in", requests.ids)]
        return res

    def get_report_data(self):
        def key(item):
            return (
                str(item["handling_sequence"])
                + "-"
                + str(item["action_type"])
                + "-"
                + str(item["product_category"])
                + "-"
                + str(item["recipient_partner"])
            )

        def _prepare_base_data(transport_request_line):
            return {
                "request_line_id": transport_request_line.id,
            }

        self.ensure_one()
        res = []
        sequence = 0
        for tour_line in self.line_ids.filtered(lambda x: x.sequence_type == "journey"):
            sequence += 1
            for transport_request_line in tour_line.transport_request_line_ids:
                # Loading data
                if transport_request_line.start_action_type == "loading":
                    base_data = _prepare_base_data(transport_request_line)
                    base_data.update(
                        {
                            "handling_sequence": sequence,
                            "handling_partner": transport_request_line.starting_point_id,
                            "action_type": "2_loading",
                        }
                    )
                    lines_data = (
                        transport_request_line.request_id._get_report_tour_data()
                    )
                    for line_data in lines_data:
                        line_data.update(base_data)
                        res.append(line_data)
                if transport_request_line.arrival_action_type == "unloading":
                    base_data = _prepare_base_data(transport_request_line)
                    base_data.update(
                        {
                            "handling_sequence": sequence + 1,
                            "handling_partner": transport_request_line.arrival_point_id,
                            "action_type": "1_unloading",
                        }
                    )
                    lines_data = (
                        transport_request_line.request_id._get_report_tour_data()
                    )
                    for line_data in lines_data:
                        line_data.update(base_data)
                        res.append(line_data)

        res = sorted(res, key=key)
        return res

    def get_report_tour_category_url(self, category):
        """Overload in other module, to return the path to an image
        for the given category"""
        return ""
