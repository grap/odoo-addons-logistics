# Copyright (C) 2023-Today: GRAP (http://www.grap.coop)
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class JointBuyingTransportRequest(models.Model):
    _inherit = "joint.buying.transport.request"

    order_id = fields.Many2one(
        comodel_name="joint.buying.purchase.order",
        string="Order",
        readonly=True,
        ondelete="cascade",
    )

    def _get_depends_start_date(self):
        res = super()._get_depends_start_date()
        res.append("order_id.deposit_date")
        return res

    def _get_depends_origin_partner_id(self):
        res = super()._get_depends_origin_partner_id()
        res.append("order_id.deposit_partner_id")
        return res

    def _get_depends_destination_partner_id(self):
        res = super()._get_depends_destination_partner_id()
        res.append("order_id.deposit_partner_id")
        return res

    def _get_depends_amount_untaxed(self):
        res = super()._get_depends_amount_untaxed()
        res.append("order_id.amount_untaxed")
        return res

    def _get_depends_total_weight(self):
        res = super()._get_depends_total_weight()
        res.append("order_id.total_weight")
        return res

    def _compute_start_date(self):
        super(
            JointBuyingTransportRequest, self.filtered(lambda x: not x.order_id)
        )._compute_start_date()

        for request in self.filtered(lambda x: x.order_id):
            request.start_date = request.order_id.deposit_date

    def _compute_origin_partner_id(self):
        super(
            JointBuyingTransportRequest, self.filtered(lambda x: not x.order_id)
        )._compute_origin_partner_id()

        for request in self.filtered(lambda x: x.order_id):
            request.origin_partner_id = request.order_id.deposit_partner_id

    def _compute_destination_partner_id(self):
        super(
            JointBuyingTransportRequest, self.filtered(lambda x: not x.order_id)
        )._compute_destination_partner_id()

        for request in self.filtered(lambda x: x.order_id):
            request.destination_partner_id = request.order_id.customer_id

    def _compute_amount_untaxed(self):
        super(
            JointBuyingTransportRequest, self.filtered(lambda x: not x.order_id)
        )._compute_amount_untaxed()

        for request in self.filtered(lambda x: x.order_id):
            request.amount_untaxed = request.order_id.amount_untaxed

    def _compute_weight(self):
        super(
            JointBuyingTransportRequest, self.filtered(lambda x: not x.order_id)
        )._compute_weight()

        for request in self.filtered(lambda x: x.order_id):
            request.total_weight = request.order_id.total_weight
