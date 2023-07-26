# Copyright (C) 2021-Today: GRAP (http://www.grap.coop)
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

import requests

from odoo import _, api, fields, models
from odoo.exceptions import UserError

from .res_partner import _JOINT_BUYING_PARTNER_CONTEXT

_TOUR_LINE_SEQUENCE_TYPES = [
    ("journey", "Journey"),
    ("handling", "Handling"),
    ("pause", "Pause"),
]


class JointBuyingTourLine(models.Model):
    _name = "joint.buying.tour.line"
    _description = "Joint Buying Tour Lines"
    _order = "sequence"

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

    start_hour = fields.Float()

    arrival_hour = fields.Float()

    starting_point_id = fields.Many2one(
        comodel_name="res.partner", context=_JOINT_BUYING_PARTNER_CONTEXT
    )

    arrival_point_id = fields.Many2one(
        comodel_name="res.partner", context=_JOINT_BUYING_PARTNER_CONTEXT
    )

    currency_id = fields.Many2one(
        comodel_name="res.currency", related="tour_id.carrier_id.currency_id"
    )

    cost = fields.Monetary(
        compute="_compute_cost", store=True, currency_field="currency_id"
    )

    @api.depends(
        "tour_id.hourly_cost", "tour_id.kilometer_cost", "duration", "distance"
    )
    def _compute_cost(self):
        for line in self:
            line.cost = (line.duration * line.tour_id.hourly_cost) + (
                line.distance * line.tour_id.kilometer_cost
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
                    f" Status Code : {response.status_code}"
                    f" Reason : {response.reason}"
                )
            )
        result = response.json().get("routes")[0]
        return {
            "distance": result.get("distance") / 1000,
            "duration": result.get("duration") / 3600,
        }

    def estimate_route(self):
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
                    f"- {'<br/>- '.join([x.name for x in no_coordinate_partners])}"
                ),
                sticky=True,
            )
