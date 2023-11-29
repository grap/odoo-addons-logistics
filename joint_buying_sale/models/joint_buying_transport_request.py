# Copyright (C) 2022-Today: GRAP (http://www.grap.coop)
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class JointBuyingTransportRequest(models.Model):
    _inherit = "joint.buying.transport.request"

    request_type = fields.Selection(selection_add=[("sale", "Sale Order")])

    sale_order_id = fields.Many2one(
        comodel_name="sale.order",
        help="Sale order in the local database of the"
        " company that requires transport.",
        ondelete="cascade",
    )

    def _get_depends_request_type(self):
        res = super()._get_depends_request_type()
        res.append("sale_order_id")
        return res

    def _get_depends_amount_untaxed(self):
        res = super()._get_depends_amount_untaxed()
        res.append("sale_order_id.amount_untaxed")
        return res

    def _get_depends_total_weight(self):
        res = super()._get_depends_total_weight()
        res.append("sale_order_id.total_ordered_weight")
        return res

    def _get_depends_description(self):
        res = super()._get_depends_description()
        res += [
            "sale_order_id.order_line.product_id",
            "sale_order_id.order_line.product_uom",
            "sale_order_id.order_line.product_uom_qty",
        ]
        return res

    def _get_depends_can_change(self):
        res = super()._get_depends_can_change()
        res += ["sale_order_id"]
        return res

    def _compute_request_type(self):
        super(
            JointBuyingTransportRequest, self.filtered(lambda x: not x.sale_order_id)
        )._compute_request_type()

        for request in self.filtered(lambda x: x.sale_order_id):
            request.request_type = "sale"

    def _compute_amount_untaxed(self):
        super(
            JointBuyingTransportRequest, self.filtered(lambda x: not x.sale_order_id)
        )._compute_amount_untaxed()

        for request in self.filtered(lambda x: x.sale_order_id):
            request.amount_untaxed = request.sale_order_id.amount_untaxed

    def _compute_total_weight(self):
        super(
            JointBuyingTransportRequest, self.filtered(lambda x: not x.sale_order_id)
        )._compute_total_weight()

        for request in self.filtered(lambda x: x.sale_order_id):
            request.total_weight = request.sale_order_id.total_ordered_weight

    def _compute_description(self):
        super(
            JointBuyingTransportRequest, self.filtered(lambda x: not x.sale_order_id)
        )._compute_description()

        for request in self.filtered(lambda x: x.sale_order_id):
            description = ""
            for line in request.sale_order_id.order_line:
                description += (
                    f"{line.product_id.name}"
                    "<span style='color:#888;'>"
                    f" ({line.product_uom_qty} x {line.product_uom.name}) "
                    "</span>"
                )
            request.description = description

    def _compute_can_change(self):
        super(
            JointBuyingTransportRequest, self.filtered(lambda x: not x.sale_order_id)
        )._compute_can_change()

        for request in self.filtered(lambda x: x.sale_order_id):
            request.can_change_date = True
            request.can_change_extra_data = False
            request.can_change_partners = True
