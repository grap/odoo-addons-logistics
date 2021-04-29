# Copyright (C) 2021-Today: GRAP (http://www.grap.coop)
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models

from odoo.addons import decimal_precision as dp


class JointBuyingPurchaseOrderLine(models.Model):
    _name = "joint.buying.purchase.order.line"
    _description = "Joint Buying Purchase Order"

    _sql_constraints = [
        (
            "order_product_uniq",
            "unique (order_id,product_id)",
            "You can not select the same product many times for the same Order !",
        )
    ]

    order_id = fields.Many2one(
        comodel_name="joint.buying.purchase.order",
        string="Purchase Order",
        required=True,
        index=True,
        ondelete="cascade",
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

    product_uom_package_id = fields.Many2one(
        comodel_name="uom.uom", string="Package UoM", readonly=True
    )

    product_package_qty = fields.Float(
        string="Package Quantity",
        digits=dp.get_precision("Product Unit of Measure"),
        required=True,
    )

    product_qty = fields.Float(
        string="Quantity",
        compute="_compute_product_qty",
        digits=dp.get_precision("Product Unit of Measure"),
    )

    product_uom_id = fields.Many2one(
        comodel_name="uom.uom", string="UoM", required=True, readonly=True
    )

    has_same_uom = fields.Boolean(compute="_compute_has_same_uom", store="True")

    price_unit = fields.Float(
        string="Unit Price",
        digits=dp.get_precision("Product Price"),
        required=True,
        readonly=True,
    )

    amount_untaxed = fields.Float(
        string="Amount Untaxed",
        compute="_compute_amount",
        store=True,
        digits=dp.get_precision("Product Price"),
    )

    # Compute Section
    @api.depends("product_package_qty", "product_uom_id", "product_uom_package_id")
    def _compute_product_qty(self):
        for line in self:
            # TODO, handle package_qty
            line.product_qty = line.product_package_qty

    @api.depends("product_uom_package_id", "product_uom_id")
    def _compute_has_same_uom(self):
        for line in self:
            line.has_same_uom = line.product_uom_package_id == line.product_uom_id

    @api.depends("product_qty", "price_unit")
    def _compute_amount(self):
        for line in self:
            line.amount_untaxed = line.product_qty * line.price_unit

    @api.onchange("product_id")
    def onchange_product_id(self):
        if not self.product_id:
            self.product_uom_package_id = False
            self.product_uom_id = False
            self.price_unit = 0.0
        else:
            self.product_uom_package_id = (
                self.product_id.uom_package_id.id or self.product_id.uom_id.id
            )
            self.product_uom_id = self.product_id.uom_id.id
            self.price_unit = self.product_id.lst_price
