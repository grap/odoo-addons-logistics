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
        ("no_minimum_weight", "Minimum Weight Not reached"),
        ("null_amount", "Null Amount"),
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

    supplier_comment = fields.Text(related="supplier_id.comment")

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

    minimum_unit_weight = fields.Float(
        string="Minimum Unit Weight",
        related="grouped_order_id.minimum_unit_weight",
        store=True,
    )

    purchase_ok = fields.Selection(
        string="Purchase OK ?",
        selection=_PURCHASE_OK_SELECTION,
        compute="_compute_purchase_ok",
        store=True,
    )

    line_ids = fields.One2many(
        "joint.buying.purchase.order.line", inverse_name="order_id"
    )

    line_qty = fields.Integer(
        string="Lines Quantity", compute="_compute_line_qty", store=True
    )

    amount_untaxed = fields.Float(
        string="Total Untaxed Amount",
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

    is_mine = fields.Boolean(compute="_compute_is_mine", search="_search_is_mine")

    has_image = fields.Boolean(compute="_compute_has_image")

    # Compute Section
    @api.depends("line_ids.product_id.image")
    def _compute_has_image(self):
        for order in self:
            order.has_image = any(order.mapped("line_ids.product_id.image"))

    @api.depends(
        "amount_untaxed",
        "minimum_unit_amount",
        "minimum_unit_weight",
        "total_weight",
        "line_qty",
    )
    def _compute_purchase_ok(self):
        for order in self:
            if not order.line_qty:
                order.purchase_ok = "no_line"
            elif order.amount_untaxed == 0.0:
                order.purchase_ok = "null_amount"
            elif (
                order.minimum_unit_amount
                and order.minimum_unit_amount > order.amount_untaxed
            ):
                order.purchase_ok = "no_minimum_amount"
            elif (
                order.minimum_unit_weight
                and order.minimum_unit_weight > order.total_weight
            ):
                order.purchase_ok = "no_minimum_weight"
            else:
                order.purchase_ok = "ok"

    @api.depends("grouped_order_id", "customer_id")
    def _compute_name(self):
        for order in self:
            order.name = "{}-{}".format(
                order.grouped_order_id.name,
                order.customer_id.joint_buying_company_id.code,
            )

    def _compute_is_mine(self):
        current_customer_partner = self.env.user.company_id.joint_buying_partner_id
        for order in self:
            order.is_mine = order.customer_id == current_customer_partner

    def _search_is_mine(self, operator, value):
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
    def _prepare_order_vals(self, supplier, customer, categories):
        OrderLine = self.env["joint.buying.purchase.order.line"]
        res = {"customer_id": customer.id, "line_ids": []}
        for product in supplier._get_joint_buying_products(categories):
            vals = OrderLine._prepare_line_vals(product)
            res["line_ids"].append((0, 0, vals))
        return res

    def action_confirm_purchase(self):
        for order in self.filtered(lambda x: x.purchase_state == "draft"):
            if order.purchase_ok == "no_line":
                raise ValidationError(
                    _("You can not confirm an order without any lines.")
                )
            elif order.purchase_ok == "null_amount":
                raise ValidationError(
                    _("You can not confirm an order with null amount.")
                )
            elif order.purchase_ok == "no_minimum_amount":
                raise ValidationError(
                    _(
                        "you cannot confirm an order for which you have"
                        " not reached the minimum purchase amount."
                    )
                )
            elif order.purchase_ok == "no_minimum_weight":
                raise ValidationError(
                    _(
                        "you cannot confirm an order for which you have"
                        " not reached the minimum weight."
                    )
                )
            order.purchase_state = "done"

    def action_draft_purchase(self):
        for order in self.filtered(lambda x: x.purchase_state == "done"):
            order.purchase_state = "draft"

    def button_see_order(self):
        self.ensure_one()
        form = self.env.ref(
            "joint_buying_product.view_joint_buying_purchase_order_form"
        )
        action = self.env.ref(
            "joint_buying_product.action_joint_buying_purchase_order_all"
        ).read()[0]
        action.update({"res_id": self.id, "views": [(form.id, "form")]})
        return action
