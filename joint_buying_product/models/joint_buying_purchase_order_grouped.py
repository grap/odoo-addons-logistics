# Copyright (C) 2021-Today: GRAP (http://www.grap.coop)
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models


class JointBuyingPurchaseOrderGrouped(models.Model):
    _name = "joint.buying.purchase.order.grouped"
    _description = "Joint Buying Grouped Purchase Order"
    _inherit = ["mail.thread", "mail.activity.mixin"]

    supplier_id = fields.Many2one(
        comodel_name="res.partner",
        string="Supplier",
        required=True,
        domain="[('is_joint_buying', '=', True), ('supplier', '=', True)]",
    )

    start_date = fields.Date(string="Start Date", required=True)

    end_date = fields.Datetime(string="End Date", required=True)

    deposit_date = fields.Date(string="Deposit Date", required=True)

    order_ids = fields.One2many(
        "joint.buying.purchase.order", inverse_name="grouped_order_id"
    )

    order_qty = fields.Integer(
        string="Orders Quantity", compute="_compute_order_qty", store=True
    )

    @api.depends("order_ids")
    def _compute_order_qty(self):
        for grouped_order in self:
            grouped_order.order_qty = len(grouped_order.order_ids)

    @api.model
    def _prepare_order_grouped_vals(
        self, supplier, customers, start_date=False, end_date=False, deposit_date=False
    ):
        Order = self.env["joint.buying.purchase.order"]
        vals = {
            "supplier_id": supplier.id,
            "start_date": start_date or supplier.joint_buying_next_start_date,
            "end_date": end_date or supplier.joint_buying_next_end_date,
            "deposit_date": deposit_date or supplier.joint_buying_next_deposit_date,
            "order_ids": [],
        }
        for customer in customers:
            vals["order_ids"].append((0, 0, Order._prepare_order_vals(customer)))
        return vals
