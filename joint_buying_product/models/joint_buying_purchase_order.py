# Copyright (C) 2021-Today: GRAP (http://www.grap.coop)
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models


class JointBuyingPurchaseOrder(models.Model):
    _name = "joint.buying.purchase.order"
    _description = "Joint Buying Purchase Order"
    _inherit = ["mail.thread", "mail.activity.mixin"]

    grouped_order_id = fields.Many2one(
        comodel_name="joint.buying.purchase.order.grouped",
        string="Grouped Purchase Order",
        required=True,
        index=True,
        ondelete="cascade",
    )

    currency_id = fields.Many2one(
        related="grouped_order_id.currency_id",
        store=True,
        string="Currency",
        readonly=True,
    )

    start_date = fields.Date(
        related="grouped_order_id.start_date", string="Start Date", store=True
    )

    end_date = fields.Datetime(
        related="grouped_order_id.end_date", string="End Date", store=True
    )

    deposit_date = fields.Date(
        related="grouped_order_id.deposit_date", string="Deposit Date", store=True
    )

    supplier_id = fields.Many2one(
        comodel_name="res.partner",
        related="grouped_order_id.supplier_id",
        string="Supplier",
        readonly=True,
        store=True,
    )

    customer_id = fields.Many2one(
        comodel_name="res.partner",
        string="Customer",
        required=True,
        readonly=True,
        # domain="[('is_joint_buying', '=', True), ('customer', '=', True)]",
    )

    line_ids = fields.One2many(
        "joint.buying.purchase.order.line", inverse_name="order_id"
    )

    line_qty = fields.Integer(
        string="Lines Quantity", compute="_compute_line_qty", store=True
    )

    @api.depends("line_ids")
    def _compute_line_qty(self):
        for order in self:
            order.order_qty = len(order.line_ids)

    @api.model
    def _prepare_order_vals(self, customer):
        vals = {"customer_id": customer.id}
        return vals
