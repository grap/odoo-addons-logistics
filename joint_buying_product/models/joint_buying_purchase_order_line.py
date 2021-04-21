# Copyright (C) 2021-Today: GRAP (http://www.grap.coop)
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models

from odoo.addons import decimal_precision as dp


class JointBuyingPurchaseOrderLine(models.Model):
    _name = "joint.buying.purchase.order.line"
    _description = "Joint Buying Purchase Order"

    order_id = fields.Many2one(
        comodel_name="joint.buying.purchase.order",
        string="Purchase Order",
        required=True,
        index=True,
        ondelete="cascade",
    )

    currency_id = fields.Many2one(
        related="order_id.currency_id", store=True, string="Currency", readonly=True
    )

    sequence = fields.Integer(string="Sequence", default=10)

    product_id = fields.Many2one(
        comodel_name="product.product",
        string="Product",
        domain="["
        "('joint_buying_partner_id', '=', parent.supplier_id),"
        " ('purchase_ok', '=', True)"
        "]",
        required=True,
    )

    product_qty = fields.Float(
        string="Quantity",
        digits=dp.get_precision("Product Unit of Measure"),
        required=True,
    )

    product_uom_id = fields.Many2one(
        comodel_name="uom.uom", string="UoM", required=True, readonly=True
    )

    price_unit = fields.Float(
        string="Unit Price",
        digits=dp.get_precision("Product Price"),
        required=True,
        readonly=True,
    )

    price_subtotal = fields.Monetary(
        string="Subtotal", compute="_compute_amount", store=True
    )

    @api.depends("product_qty", "price_unit")
    def _compute_amount(self):
        for line in self:
            line.price_subtotal = line.product_qty * line.price_unit

    @api.onchange("product_id")
    def onchange_product_id(self):
        if not self.product_id:
            self.product_uom_id = False
            self.price_unit = 0.0
        else:
            self.price_unit = self.product_id.lst_price
            self.product_uom_id = self.product_id.uom_id.id
