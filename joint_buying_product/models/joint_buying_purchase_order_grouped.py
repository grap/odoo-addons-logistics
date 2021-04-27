# Copyright (C) 2021-Today: GRAP (http://www.grap.coop)
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from datetime import datetime, time

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError

from odoo.addons import decimal_precision as dp


class JointBuyingPurchaseOrderGrouped(models.Model):
    _name = "joint.buying.purchase.order.grouped"
    _description = "Joint Buying Grouped Purchase Order"
    _inherit = ["mail.thread", "mail.activity.mixin"]

    _STATE_SELECTION = [
        ("futur", "Futur"),
        ("in_progress", "In Progress"),
        ("closed", "Closed"),
        ("deposited", "Deposited Products"),
    ]

    name = fields.Char(
        string="Number", required=True, copy=False, default=lambda x: x._default_name()
    )

    supplier_id = fields.Many2one(
        comodel_name="res.partner",
        string="Supplier",
        required=True,
        domain="[('is_joint_buying', '=', True), ('supplier', '=', True)]",
    )

    state = fields.Selection(
        selection=_STATE_SELECTION, string="State", required=True, readonly=True
    )

    pivot_company_id = fields.Many2one(
        comodel_name="res.company", string="Pivot Company", required=True
    )

    deposit_company_id = fields.Many2one(
        comodel_name="res.company", string="Deposit Company", required=True
    )

    start_date = fields.Date(string="Start Date", required=True)

    end_date = fields.Datetime(string="End Date", required=True)

    deposit_date = fields.Date(string="Deposit Date", required=True)

    order_ids = fields.One2many(
        "joint.buying.purchase.order", inverse_name="grouped_order_id", readonly=True
    )

    order_qty = fields.Integer(
        string="Orders Quantity", compute="_compute_order_qty", store=True
    )

    amount_subtotal = fields.Float(
        string="Amount Subtotal",
        compute="_compute_amount",
        store=True,
        digits=dp.get_precision("Product Price"),
    )

    summary_line_ids = fields.One2many(
        comodel_name="joint.buying.purchase.order.grouped.line",
        compute="_compute_summary_line_ids",
    )

    # Default Section
    def _default_name(self):
        return self.env["ir.sequence"].next_by_code(
            "joint.buying.purchase.order.grouped"
        )

    # Compute Section
    @api.depends("order_ids")
    def _compute_order_qty(self):
        for grouped_order in self:
            grouped_order.order_qty = len(grouped_order.order_ids)

    @api.depends("order_ids.amount_subtotal")
    def _compute_amount(self):
        for order in self:
            order.amount_subtotal = sum(order.mapped("order_ids.amount_subtotal"))

    def _compute_summary_line_ids(self):
        for grouped_order in self:
            res = []
            res = {
                x.id: {"product_id": x.id, "product_qty": 0, "price_subtotal": 0}
                for x in grouped_order.mapped("order_ids.line_ids")
                .filtered(lambda line: line.product_qty)
                .mapped("product_id")
                .sorted(lambda x: x.name)
            }
            lines = grouped_order.mapped("order_ids.line_ids").filtered(
                lambda x: x.product_qty
            )
            for line in lines:
                res[line.product_id.id].update(
                    {
                        "price_unit": line.price_unit,
                        "product_qty": res[line.product_id.id]["product_qty"]
                        + line.product_qty,
                        "price_subtotal": res[line.product_id.id]["price_subtotal"]
                        + line.price_subtotal,
                    }
                )
            grouped_order.summary_line_ids = [(0, 0, v) for k, v in res.items()]

    # Overload Section
    def create(self, vals):
        if datetime.combine(vals["start_date"], time(0, 0)) > datetime.now():
            vals.update({"state": "planned"})
        elif vals["end_date"] > datetime.now():
            vals.update({"state": "in_progress"})
        else:
            raise ValidationError(
                _("You can not create a closed Grouped Purchase order")
            )
        return super().create(vals)

    # Custom Section
    @api.model
    def _prepare_order_grouped_vals(
        self,
        supplier,
        customers=False,
        start_date=False,
        end_date=False,
        deposit_date=False,
        deposit_company=False,
        pivot_company=False,
    ):
        Order = self.env["joint.buying.purchase.order"]
        vals = {
            "supplier_id": supplier.id,
            "deposit_company_id": deposit_company.id
            or supplier.joint_buying_deposit_company_id.id,
            "pivot_company_id": pivot_company.id
            or supplier.joint_buying_pivot_company_id.id,
            "start_date": start_date or supplier.joint_buying_next_start_date,
            "end_date": end_date or supplier.joint_buying_next_end_date,
            "deposit_date": deposit_date or supplier.joint_buying_next_deposit_date,
            "order_ids": [],
        }
        if not customers:
            customers = supplier.mapped(
                "joint_buying_favorite_company_ids.joint_buying_partner_id"
            )
        for customer in customers:
            vals["order_ids"].append(
                (0, 0, Order._prepare_order_vals(supplier, customer))
            )
        return vals
