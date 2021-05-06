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
        readonly=True,
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

    purchase_qty = fields.Float(
        string="Purchase Quantity",
        digits=dp.get_precision("Product Unit of Measure"),
        required=True,
    )

    product_uom_package_id = fields.Many2one(
        comodel_name="uom.uom", string="Package UoM", readonly=True
    )

    product_uom_package_qty = fields.Float(
        string="Package Quantity",
        digits=dp.get_precision("Product Unit of Measure"),
        readonly=True,
        required=True,
    )

    qty = fields.Float(
        string="Quantity",
        compute="_compute_qty",
        digits=dp.get_precision("Product Unit of Measure"),
        store=True,
    )

    product_uom_id = fields.Many2one(
        comodel_name="uom.uom", string="UoM", required=True, readonly=True
    )

    product_weight = fields.Float(string="Product Weight", required=True, readonly=True)

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

    total_weight = fields.Float(
        string="Total Weight", compute="_compute_total_weight", store=True
    )

    # Compute Section
    @api.depends(
        "purchase_qty",
        "product_uom_id",
        "product_uom_package_qty",
        "product_uom_package_id",
    )
    def _compute_qty(self):
        ProductTemplate = self.env["product.template"]
        for line in self:
            line.qty = ProductTemplate._counvert_package_qty(
                line.purchase_qty, line.product_uom_package_id, line.product_uom_id
            )

    @api.depends("qty", "product_uom_id", "product_weight")
    def _compute_total_weight(self):
        for line in self:
            product_weight = (
                line.product_id.uom_measure_type == "unit"
                and line.product_weight
                or 1.0
            )
            line.total_weight = line.qty * product_weight

    @api.depends("product_uom_package_id", "product_uom_id")
    def _compute_has_same_uom(self):
        for line in self:
            line.has_same_uom = line.product_uom_package_id == line.product_uom_id

    @api.depends("qty", "price_unit")
    def _compute_amount(self):
        for line in self:
            line.amount_untaxed = line.qty * line.price_unit

    @api.onchange("purchase_qty")
    def onchange_purchase_qty(self):
        res = {}
        ProductTemplate = self.env["product.template"]
        if self.purchase_qty:
            result = ProductTemplate._round_package_quantity(
                self.purchase_qty,
                self.product_uom_package_qty,
                self.product_uom_package_id,
                self.product_uom_id,
            )
            if result["warning"]:
                res["warning"] = result["warning"]
            self.purchase_qty = result["qty"]
        return res

    @api.onchange("product_id")
    def onchange_product_id(self):
        if not self.product_id:
            self.product_uom_package_id = False
            self.product_uom_package_qty = False
            self.product_uom_id = False
            self.price_unit = 0.0
            self.purchase_qty = 0.0
            self.product_weight = 0.0
        else:
            self.product_uom_package_id = (
                self.product_id.uom_package_id.id or self.product_id.uom_id.id
            )
            self.product_uom_package_qty = self.product_id.uom_package_qty
            self.product_uom_id = self.product_id.uom_id.id
            self.product_weight = self.product_id.weight
            self.price_unit = self.product_id.lst_price
