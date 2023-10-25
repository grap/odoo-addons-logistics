# Copyright (C) 2023-Today: GRAP (http://www.grap.coop)
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models

from odoo.addons.joint_buying_base.models.res_partner import (
    _JOINT_BUYING_PARTNER_CONTEXT,
)


class JointBuyingWizardFindRoute(models.TransientModel):
    _name = "joint.buying.wizard.find.route"
    _description = "Joint Buying Wizard Find Route"

    transport_request_id = fields.Many2one(
        string="Transport Request",
        comodel_name="joint.buying.transport.request",
        default=lambda x: x._default_transport_reqquest_id(),
        readonly=True,
        required=True,
    )

    start_date = fields.Datetime(
        related="transport_request_id.start_date", readonly=True
    )

    origin_partner_id = fields.Many2one(
        comodel_name="res.partner",
        string="Origin",
        related="transport_request_id.origin_partner_id",
        context=_JOINT_BUYING_PARTNER_CONTEXT,
        readonly=True,
    )

    destination_partner_id = fields.Many2one(
        comodel_name="res.partner",
        string="Destination",
        context=_JOINT_BUYING_PARTNER_CONTEXT,
        related="transport_request_id.destination_partner_id",
        readonly=True,
    )

    simulation = fields.Text(
        compute="_compute_simulation",
    )

    # Default Section
    def _default_transport_reqquest_id(self):
        return self.env.context.get("active_id")

    @api.depends("transport_request_id")
    def _compute_simulation(self):
        self.ensure_one()
        self.compute_results(self)

    def compute_results(self, transport_requests):
        """Endtry point to compute the best way for a RecordSet of Transport Requests"""
        sections = self.env["joint.buying.tour.line"].search_read(
            domain=[
                ("sequence_type", "=", "journey"),
                ("start_date", ">=", min(transport_requests.mapped("start_date"))),
            ],
            fields=[
                "starting_point_id",
                "tour_id",
                "distance",
                "start_date",
                "arrival_date",
                "arrival_point_id",
            ],
            order="start_date",
        )
        sections = sections

    def button_apply(self):
        self.ensure_one()
        raise NotImplementedError()
