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

    order_ids = fields.One2many(
        "joint.buying.purchase.order", inverse_name="grouped_order_id"
    )

    @api.model
    def _prepare_order_grouped_vals(self, supplier, customers):
        Order = self.env["joint.buying.purchase.order"]
        vals = {"supplier_id": supplier.id, "order_ids": []}
        for customer in customers:
            vals["order_ids"].append((0, 0, Order._prepare_order_vals(customer)))

        return vals
