# Copyright (C) 2021-Today: GRAP (http://www.grap.coop)
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError

from odoo.addons import decimal_precision as dp
from odoo.addons.joint_buying_base.models.res_partner import (
    _JOINT_BUYING_PARTNER_CONTEXT,
)


class JointBuyingPurchaseOrder(models.Model):
    _name = "joint.buying.purchase.order"
    _description = "Joint Buying Purchase Order"
    _inherit = ["mail.thread", "mail.activity.mixin"]

    _PURCHASE_STATE = [("draft", "To Enter"), ("done", "Confirmed")]

    _PURCHASE_OK_SELECTION = [
        ("no_line", "No Lines"),
        ("no_minimum_amount", "Minimum Amount Not reached"),
        ("no_qty", "No Quantity"),
        ("ok", "OK"),
    ]

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
        string="Grouped Order",
        required=True,
        readonly=True,
        index=True,
        ondelete="cascade",
    )

    start_date = fields.Datetime(
        related="grouped_order_id.start_date", string="Start Date", store=True
    )

    end_date = fields.Datetime(
        related="grouped_order_id.end_date", string="End Date", store=True
    )

    deposit_date = fields.Datetime(
        related="grouped_order_id.deposit_date", string="Deposit Date", store=True
    )

    supplier_id = fields.Many2one(
        comodel_name="res.partner",
        related="grouped_order_id.supplier_id",
        string="Supplier",
        readonly=True,
        store=True,
        index=True,
        context=_JOINT_BUYING_PARTNER_CONTEXT,
    )

    customer_id = fields.Many2one(
        comodel_name="res.partner",
        string="Customer",
        required=True,
        readonly=True,
        index=True,
        context=_JOINT_BUYING_PARTNER_CONTEXT,
    )

    state = fields.Selection(
        related="grouped_order_id.state", string="State", store=True
    )

    purchase_state = fields.Selection(
        selection=_PURCHASE_STATE, required=True, default="draft", track_visibility=True
    )

    minimum_unit_amount = fields.Float(
        string="Minimum amount",
        related="grouped_order_id.minimum_unit_amount",
        store=True,
    )

    purchase_ok = fields.Selection(
        selection=_PURCHASE_OK_SELECTION, compute="_compute_purchase_ok", store=True
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
        string="Total Brut Weight",
        compute="_compute_total_weight",
        store=True,
        digits=dp.get_precision("Stock Weight"),
    )

    is_my_purchase = fields.Boolean(
        string="Is My Purchase",
        compute="_compute_is_my_purchase",
        search="_search_is_my_purchase",
    )

    @api.depends("amount_untaxed", "minimum_unit_amount", "line_ids")
    def _compute_purchase_ok(self):
        for order in self:
            if not order.line_qty:
                order.purchase_ok = "no_line"
            elif order.minimum_unit_amount > order.amount_untaxed:
                order.purchase_ok = "no_minimum_amount"
            elif order.amount_untaxed == 0.0:
                order.purchase_ok = "no_qty"
            else:
                order.purchase_ok = "ok"

    @api.depends("grouped_order_id", "customer_id")
    def _compute_name(self):
        for order in self:
            order.name = "{}-{}".format(
                order.grouped_order_id.name,
                order.customer_id.joint_buying_company_id.code,
            )

    def _compute_is_my_purchase(self):
        current_customer_partner = self.env.user.company_id.joint_buying_partner_id
        for order in self:
            order.is_my_purchase = order.customer_id == current_customer_partner

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

    @api.depends("line_ids")
    def _compute_line_qty(self):
        for order in self:
            order.line_qty = len(order.line_ids)

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
                "qty": 0.0,
                "uom_id": product.uom_id.id,
                "product_uom_package_qty": product.uom_package_qty,
                "product_weight": product.weight,
                "price_unit": product.lst_price,
            }
            res["line_ids"].append((0, 0, vals))
        return res

    def action_confirm_purchase(self):
        for order in self.filtered(lambda x: x.purchase_state == "draft"):
            if not order.line_qty:
                raise ValidationError(
                    _("You can not confirm an order without any lines.")
                )
            elif not order.amount_untaxed:
                raise ValidationError(
                    _("You can not confirm an order with null amount.")
                )
            elif order.minimum_unit_amount > order.amount_untaxed:
                raise ValidationError(
                    _(
                        "you cannot confirm an order for which you have"
                        " not reached the minimum purchase amount."
                    )
                )
            order.purchase_state = "done"

    def action_draft_purchase(self):
        for order in self.filtered(lambda x: x.purchase_state == "done"):
            order.purchase_state = "draft"
