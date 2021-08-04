# Copyright (C) 2021-Today: GRAP (http://www.grap.coop)
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models

from odoo.addons import decimal_precision as dp
from odoo.addons.joint_buying_base.models.res_partner import (
    _JOINT_BUYING_PARTNER_CONTEXT,
)

from .product_product import _JOINT_BUYING_PRODUCT_CONTEXT


class JointBuyingPurchaseOrderLine(models.Model):
    _name = "joint.buying.purchase.order.line"
    _description = "Joint Buying Purchase Order"
    _order = "supplier_id, product_id"

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

    supplier_id = fields.Many2one(
        related="order_id.supplier_id",
        comodel_name="res.partner",
        string="Supplier",
        readonly=True,
        index=True,
        store=True,
        context=_JOINT_BUYING_PARTNER_CONTEXT,
    )

    customer_id = fields.Many2one(
        related="order_id.customer_id",
        comodel_name="res.partner",
        string="Customer",
        readonly=True,
        index=True,
        store=True,
        context=_JOINT_BUYING_PARTNER_CONTEXT,
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
        context=_JOINT_BUYING_PRODUCT_CONTEXT,
        readonly=True,
    )

    uom_id = fields.Many2one(comodel_name="uom.uom", string="UoM", readonly=True)

    product_uom_package_qty = fields.Float(
        string="Package Quantity",
        digits=dp.get_precision("Product Unit of Measure"),
        readonly=True,
        required=True,
    )

    qty = fields.Float(
        string="Quantity",
        digits=dp.get_precision("Product Unit of Measure"),
        required=True,
    )

    product_brut_weight = fields.Float(
        string="Brut Weight",
        required=True,
        readonly=True,
        digits=dp.get_precision("Stock Weight"),
    )

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

    total_brut_weight = fields.Float(
        string="Total Weight", compute="_compute_total_brut_weight", store=True
    )

    is_my_purchase = fields.Boolean(
        string="Is My Purchase",
        compute="_compute_is_my_purchase",
        search="_search_is_my_purchase",
    )

    # Compute Section
    @api.depends("qty", "product_brut_weight")
    def _compute_total_brut_weight(self):
        for line in self:
            line.total_brut_weight = line.qty * line.product_brut_weight

    @api.depends("qty", "price_unit")
    def _compute_amount(self):
        for line in self:
            line.amount_untaxed = line.qty * line.price_unit

    def _compute_is_my_purchase(self):
        current_customer_partner = self.env.user.company_id.joint_buying_partner_id
        for line in self:
            line.is_my_purchase = line.customer_id == current_customer_partner

    def _search_is_my_purchase(self, operator, value):
        current_customer_partner = self.env.user.company_id.joint_buying_partner_id
        if (operator == "=" and value) or (operator == "!=" and not value):
            search_operator = "in"
        else:
            search_operator = "not in"
        return [
            (
                "id",
                search_operator,
                self.search([("customer_id", "=", current_customer_partner.id)]).ids,
            )
        ]

    @api.onchange("qty")
    def onchange_qty(self):
        res = {}
        ProductTemplate = self.env["product.template"]
        if self.qty:
            result = ProductTemplate._round_package_quantity(
                self.qty, self.product_uom_package_qty, False, self.uom_id
            )
            if result["warning"]:
                res["warning"] = result["warning"]
            self.qty = result["qty"]
        return res

    @api.onchange("product_id")
    def onchange_product_id(self):
        if not self.product_id:
            self.product_uom_package_qty = False
            self.uom_id = False
            self.price_unit = 0.0
            self.qty = 0.0
            self.product_brut_weight = 0.0
        else:
            self.product_uom_package_qty = self.product_id.uom_package_qty
            self.uom_id = self.product_id.uom_id.id
            self.product_brut_weight = self.product_id.weight
            self.price_unit = self.product_id.lst_price
