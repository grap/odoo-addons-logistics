# Copyright (C) 2021-Today: GRAP (http://www.grap.coop)
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import requests

from odoo import _, api, fields, models
from odoo.exceptions import UserError

from odoo.addons import decimal_precision as dp

from .res_partner import _JOINT_BUYING_PARTNER_CONTEXT

_TOUR_LINE_SEQUENCE_TYPES = [
    ("journey", "Journey"),
    ("handling", "Handling"),
    ("pause", "Pause"),
]


class JointBuyingTourLine(models.Model):
    _name = "joint.buying.tour.line"
    _description = "Joint Buying Tour Lines"
    _order = "start_date, sequence"

    sequence = fields.Integer()

    sequence_type = fields.Selection(
        selection=_TOUR_LINE_SEQUENCE_TYPES,
        required=True,
    )

    tour_id = fields.Many2one(
        comodel_name="joint.buying.tour", required=True, ondelete="cascade"
    )

    duration = fields.Float()

    distance = fields.Float()

    start_date = fields.Datetime()

    arrival_date = fields.Datetime()

    start_hour = fields.Float(compute="_compute_hours")

    arrival_hour = fields.Float(compute="_compute_hours")

    starting_point_id = fields.Many2one(
        comodel_name="res.partner", context=_JOINT_BUYING_PARTNER_CONTEXT
    )

    arrival_point_id = fields.Many2one(
        comodel_name="res.partner", context=_JOINT_BUYING_PARTNER_CONTEXT
    )

    currency_id = fields.Many2one(
        comodel_name="res.currency", related="tour_id.carrier_id.currency_id"
    )

    salary_cost = fields.Monetary(
        compute="_compute_costs", store=True, currency_field="currency_id"
    )

    vehicle_cost = fields.Monetary(
        compute="_compute_costs", store=True, currency_field="currency_id"
    )

    transport_request_line_ids = fields.One2many(
        comodel_name="joint.buying.transport.request.line",
        string="Transport Lines",
        inverse_name="tour_line_id",
    )

    load = fields.Float(
        compute="_compute_load",
        digits=dp.get_precision("Stock Weight"),
    )

    @api.depends("start_date", "arrival_date")
    def _compute_hours(self):
        for line in self:
            start_date = fields.Datetime.context_timestamp(self, line.start_date)
            arrival_date = fields.Datetime.context_timestamp(self, line.arrival_date)
            line.start_hour = (
                start_date.hour + start_date.minute / 60 + start_date.second / 3600
            )
            line.arrival_hour = (
                arrival_date.hour
                + arrival_date.minute / 60
                + arrival_date.second / 3600
            )

    @api.depends(
        "tour_id.hourly_cost", "tour_id.kilometer_cost", "duration", "distance"
    )
    def _compute_costs(self):
        for line in self:
            line.salary_cost = line.duration * line.tour_id.hourly_cost
            line.vehicle_cost = +line.distance * line.tour_id.kilometer_cost

    def _compute_load(self):
        for tour_line in self:
            tour_line.load = sum(
                tour_line.mapped("transport_request_line_ids.request_id.total_weight")
            )

    def _estimate_route_project_osrm(self):
        self.ensure_one()
        url = (
            "http://router.project-osrm.org/route/v1/car/"
            f"{self.starting_point_id.partner_longitude}"
            f",{self.starting_point_id.partner_latitude}"
            ";"
            f"{self.arrival_point_id.partner_longitude}"
            f",{self.arrival_point_id.partner_latitude}"
            "?alternatives=false&overview=false"
        )
        try:
            response = requests.get(url)
        except requests.exceptions.ConnectionError:
            raise UserError(_("Unable to reach the service 'router.project-osrm.org'."))
        if response.status_code != 200:
            raise UserError(
                _(
                    "Calling 'router.project-osrm.org' returned the following error"
                    " Status Code : %s"
                    " Reason : %s"
                )
                % (response.status_code, response.reason)
            )
        result = response.json().get("routes")[0]
        return {
            "distance": result.get("distance") / 1000,
            "duration": result.get("duration") / 3600,
        }

    def _estimate_route(self):
        no_coordinate_partners = self.env["res.partner"]
        for line in self.filtered(lambda x: x.sequence_type == "journey"):
            if (
                not line.starting_point_id.partner_longitude
                or not line.starting_point_id.partner_latitude
            ):
                no_coordinate_partners |= line.starting_point_id
                continue
            if (
                not line.arrival_point_id.partner_longitude
                or not line.arrival_point_id.partner_latitude
            ):
                no_coordinate_partners |= line.arrival_point_id
                continue

            line.write(line._estimate_route_project_osrm())

        if no_coordinate_partners:
            self.env.user.notify_warning(
                message=_(
                    "Unable to estimate a route because the following stages"
                    " has no defined geographic coordinates. <br/>"
                    "- %s"
                )
                % ("<br/>- ".join([x.name for x in no_coordinate_partners])),
                sticky=True,
            )

    def get_report_request_lines(self, action_type):
        """Return a a dict {key: value}
        where value are a list of transport.request.line,
        and key is a dict of caracteristics that describe the type of request lines
        """
        self.ensure_one()
        if action_type == "loading":

            def line_filter(x):
                return x.start_action_type == action_type

        else:

            def line_filter(x):
                return x.arrival_action_type == action_type

        return [
            {
                "key": {"action_type": action_type},
                "request_lines": self.mapped("transport_request_line_ids")
                .filtered(line_filter)
                .sorted(
                    key=lambda r: (
                        r.request_id.arrival_partner_id.joint_buying_code,
                        r.request_id.start_partner_id.joint_buying_code,
                    )
                ),
            }
        ]
