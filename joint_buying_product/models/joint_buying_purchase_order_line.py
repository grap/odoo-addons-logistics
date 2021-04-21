# Copyright (C) 2021-Today: GRAP (http://www.grap.coop)
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class JointBuyingPurchaseOrderLine(models.Model):
    _name = "joint.buying.purchase.order.line"
    _description = "Joint Buying Purchase Order"

    order_id = fields.Many2one(
        comodel_name="joint.buying.purchase.order",
        string="Purchase Order",
        required=True,
        ondelete="cascade",
    )

    grouped_order_id = fields.Many2one(
        comodel_name="res.partner",
        related="order_id.grouped_order_id",
        string="Grouped Purchase Order",
        required=True,
        store=True,
    )

    supplier_id = fields.Many2one(
        comodel_name="res.partner",
        related="order_id.grouped_order_id.supplier_id",
        string="Supplier",
        required=True,
        store=True,
    )

    customer_id = fields.Many2one(
        comodel_name="res.partner",
        related="order_id.customer_id",
        string="Customer",
        required=True,
        store=True,
    )
