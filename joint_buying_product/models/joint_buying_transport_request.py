# Copyright (C) 2021-Today: GRAP (http://www.grap.coop)
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models

from odoo.addons import decimal_precision as dp
from odoo.addons.joint_buying_base.models.res_partner import (
    _JOINT_BUYING_PARTNER_CONTEXT,
)


class JointBuyingTransportRequest(models.Model):
    _name = "joint.buying.transport.request"
    _description = "Joint Buying Transport Request"

    name = fields.Char(readonly=True, compute="_compute_name", store=True)

    state = fields.Selection(
        selection=[
            ("to_compute", "To Compute"),
            ("computed", "Computed"),
            ("not_computable", "Not Computable"),
        ],
        required=True,
        readonly=True,
        default="to_compute",
    )

    order_id = fields.Many2one(
        comodel_name="joint.buying.purchase.order",
        string="Order",
        readonly=True,
        ondelete="cascade",
    )

    manual_start_date = fields.Datetime(
        string="Start Date (Manual)",
    )

    start_date = fields.Datetime(
        string="Start Date",
        compute="_compute_start_date",
        store=True,
    )

    manual_origin_partner_id = fields.Many2one(
        comodel_name="res.partner",
        string="Origin (Manual)",
        context=_JOINT_BUYING_PARTNER_CONTEXT,
        domain="[('is_joint_buying_stage', '=', True)]",
    )

    origin_partner_id = fields.Many2one(
        comodel_name="res.partner",
        compute="_compute_origin_partner_id",
        string="Origin",
        store=True,
        context=_JOINT_BUYING_PARTNER_CONTEXT,
    )

    manual_destination_partner_id = fields.Many2one(
        comodel_name="res.partner",
        string="Destination (Manual)",
        context=_JOINT_BUYING_PARTNER_CONTEXT,
        domain="[('is_joint_buying_stage', '=', True)]",
    )

    destination_partner_id = fields.Many2one(
        comodel_name="res.partner",
        compute="_compute_destination_partner_id",
        string="Destination",
        store=True,
        context=_JOINT_BUYING_PARTNER_CONTEXT,
    )

    manual_amount_untaxed = fields.Float(
        string="Untaxed Amount (Manual)",
        digits=dp.get_precision("Product Price"),
    )

    amount_untaxed = fields.Float(
        string="Untaxed Amount",
        compute="_compute_amount_untaxed",
        store=True,
        digits=dp.get_precision("Product Price"),
    )

    manual_total_weight = fields.Float(
        string="Weight (Manual)",
        digits=dp.get_precision("Stock Weight"),
    )

    total_weight = fields.Float(
        string="Weight",
        compute="_compute_weight",
        store=True,
        digits=dp.get_precision("Stock Weight"),
    )

    tour_line_ids = fields.Many2many(
        comodel_name="joint.buying.tour.line",
        string="Route Lines",
    )

    arrival_date = fields.Datetime(string="Arrival Date", readonly=True)

    # Compute Section
    @api.depends("origin_partner_id", "destination_partner_id", "start_date")
    def _compute_name(self):
        for request in self:
            request.name = (
                f"{request.origin_partner_id.joint_buying_code}"
                f" -> {request.destination_partner_id.joint_buying_code}"
                f" ({request.start_date})"
            )

    @api.depends("manual_start_date", "order_id.deposit_date")
    def _compute_start_date(self):
        for request in self.filtered(lambda x: x.manual_start_date):
            request.start_date = request.manual_start_date
        for request in self.filtered(lambda x: not x.manual_start_date):
            request.start_date = request.order_id.deposit_date

    @api.depends("manual_origin_partner_id", "order_id.deposit_partner_id")
    def _compute_origin_partner_id(self):
        for request in self.filtered(lambda x: x.manual_origin_partner_id):
            request.origin_partner_id = request.manual_origin_partner_id
        for request in self.filtered(lambda x: not x.manual_origin_partner_id):
            request.origin_partner_id = request.order_id.deposit_partner_id

    @api.depends("manual_destination_partner_id", "order_id.deposit_partner_id")
    def _compute_destination_partner_id(self):
        for request in self.filtered(lambda x: x.manual_destination_partner_id):
            request.destination_partner_id = request.manual_destination_partner_id
        for request in self.filtered(lambda x: not x.manual_destination_partner_id):
            request.destination_partner_id = request.order_id.customer_id

    @api.depends("manual_amount_untaxed", "order_id.amount_untaxed")
    def _compute_amount_untaxed(self):
        for request in self.filtered(lambda x: x.manual_amount_untaxed):
            request.amount_untaxed = request.manual_amount_untaxed
        for request in self.filtered(lambda x: not x.manual_amount_untaxed):
            request.amount_untaxed = request.order_id.amount_untaxed

    @api.depends("manual_total_weight", "order_id.total_weight")
    def _compute_weight(self):
        for request in self.filtered(lambda x: x.manual_total_weight):
            request.total_weight = request.manual_total_weight
        for request in self.filtered(lambda x: not x.manual_total_weight):
            request.total_weight = request.order_id.total_weight

    def _set_tour_lines(self, tour_line_ids):
        self.ensure_one()
        # If lines are valid
        if (
            tour_line_ids
            and tour_line_ids[-1].arrival_point_id == self.destination_partner_id
        ):
            vals = {
                "arrival_date": max(tour_line_ids.mapped("arrival_date")),
                "tour_line_ids": [(6, 0, tour_line_ids.ids)],
                "state": "computed",
            }
        else:
            vals = {
                "tour_line_ids": [],
                "state": "not_computable",
                "arrival_date": False,
            }
        self.write(vals)
