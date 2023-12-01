# Copyright (C) 2023-Today: GRAP (http://www.grap.coop)
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class JointBuyingTransportRequest(models.Model):
    _inherit = "joint.buying.transport.request"

    request_type = fields.Selection(
        selection_add=[("joint_buying", "Joint Buying Grouped Order")]
    )

    order_id = fields.Many2one(
        comodel_name="joint.buying.purchase.order",
        string="Order",
        ondelete="cascade",
        readonly=True,
    )

    def _get_depends_request_type(self):
        res = super()._get_depends_request_type()
        res.append("order_id")
        return res

    def _get_depends_availability_date(self):
        res = super()._get_depends_availability_date()
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

    def _get_depends_description(self):
        res = super()._get_depends_description()
        res += [
            "order_id.line_ids.product_id",
            "order_id.line_ids.qty",
            "order_id.line_ids.uom_id.name",
        ]
        return res

    def _get_depends_can_change(self):
        res = super()._get_depends_can_change()
        res += ["order_id"]
        return res

    def _compute_request_type(self):
        super(
            JointBuyingTransportRequest, self.filtered(lambda x: not x.order_id)
        )._compute_request_type()

        for request in self.filtered(lambda x: x.order_id):
            request.request_type = "joint_buying"

    def _compute_availability_date(self):
        super(
            JointBuyingTransportRequest, self.filtered(lambda x: not x.order_id)
        )._compute_availability_date()

        for request in self.filtered(lambda x: x.order_id):
            request.availability_date = request.order_id.deposit_date

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

    def _compute_total_weight(self):
        super(
            JointBuyingTransportRequest, self.filtered(lambda x: not x.order_id)
        )._compute_total_weight()

        for request in self.filtered(lambda x: x.order_id):
            request.total_weight = request.order_id.total_weight

    def _compute_description(self):
        super(
            JointBuyingTransportRequest, self.filtered(lambda x: not x.order_id)
        )._compute_description()

        for request in self.filtered(lambda x: x.order_id):
            description = ""
            for line in request.order_id.line_ids.filtered(lambda x: x.qty != 0):
                description += (
                    f"{line.product_id.name}"
                    "<span style='color:#888;'>"
                    f" ({line.qty} x {line.uom_id.name}) "
                    "</span>"
                )
            request.description = description

    def _compute_can_change(self):
        super(
            JointBuyingTransportRequest, self.filtered(lambda x: not x.order_id)
        )._compute_can_change()

        for request in self.filtered(lambda x: x.order_id):
            request.can_change_date = False
            request.can_change_extra_data = False
            request.can_change_partners = False
