# Copyright (C) 2021-Today: GRAP (http://www.grap.coop)
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models

from odoo.addons import decimal_precision as dp


class JointBuyingPurchaseOrder(models.Model):
    _name = "joint.buying.purchase.order"
    _description = "Joint Buying Purchase Order"
    _inherit = ["mail.thread", "mail.activity.mixin"]

    _sql_constraints = [
        (
            "group_order_customer_uniq",
            "unique (grouped_order_id,customer_id)",
            "Customer can have only on purchase for this grouped order !",
        )
    ]

    name = fields.Char(string="Number", compute="_compute_name", store=True)

    grouped_order_id = fields.Many2one(
        comodel_name="joint.buying.purchase.order.grouped",
        string="Grouped Purchase Order",
        required=True,
        index=True,
        ondelete="cascade",
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
        comodel_name="res.partner", string="Customer", required=True, readonly=True
    )

    line_ids = fields.One2many(
        "joint.buying.purchase.order.line", inverse_name="order_id"
    )

    line_qty = fields.Integer(
        string="Lines Quantity", compute="_compute_line_qty", store=True
    )

    amount_untaxed = fields.Float(
        string="Amount Subtotal",
        compute="_compute_amount",
        store=True,
        digits=dp.get_precision("Product Price"),
    )

    total_weight = fields.Float(
        string="Total Weight", compute="_compute_total_weight", store=True
    )

    # Compute Section
    @api.depends("grouped_order_id", "customer_id")
    def _compute_name(self):
        for order in self:
            order.name = "{}-{}".format(
                order.grouped_order_id.name,
                order.customer_id.joint_buying_company_id.code,
            )

    @api.depends("line_ids")
    def _compute_line_qty(self):
        for order in self:
            order.order_qty = len(order.line_ids)

    @api.depends("line_ids.amount_untaxed")
    def _compute_amount(self):
        for order in self:
            order.amount_untaxed = sum(order.mapped("line_ids.amount_untaxed"))

    @api.depends("line_ids.total_weight")
    def _compute_total_weight(self):
        for order in self:
            order.total_weight = sum(order.mapped("line_ids.total_weight"))

    # Custom Section
    @api.model
    def _prepare_order_vals(self, supplier, customer):
        res = {"customer_id": customer.id, "line_ids": []}
        for product in supplier._get_joint_buying_products():
            vals = {
                "product_id": product.id,
                "product_package_qty": 0.0,
                "product_uom_package_id": product.uom_package_id.id
                or product.uom_id.id,
                "product_qty": 0.0,
                "product_uom_id": product.uom_id.id,
                "price_unit": product.lst_price,
            }
            res["line_ids"].append((0, 0, vals))
        return res
