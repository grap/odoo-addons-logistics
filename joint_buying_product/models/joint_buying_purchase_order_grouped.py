# Copyright (C) 2021-Today: GRAP (http://www.grap.coop)
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from datetime import datetime, time

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError

from odoo.addons import decimal_precision as dp
from odoo.addons.joint_buying_base.models.res_partner import (
    _JOINT_BUYING_PARTNER_CONTEXT,
)


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
        domain="[('supplier', '=', True)]",
        context=_JOINT_BUYING_PARTNER_CONTEXT,
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

    is_mail_sent = fields.Boolean(string="Mail Sent", default=False)

    minimum_amount = fields.Float(string="Minimum Amount")

    minimum_unit_amount = fields.Float(string="Minimum Unit Amount")

    amount_untaxed = fields.Float(
        string="Amount Subtotal",
        compute="_compute_amount",
        store=True,
        digits=dp.get_precision("Product Price"),
    )

    total_weight = fields.Float(
        string="Total Weight",
        compute="_compute_total_weight",
        store=True,
        digits=dp.get_precision("Stock Weight"),
    )

    summary_line_ids = fields.One2many(
        comodel_name="joint.buying.purchase.order.grouped.line",
        compute="_compute_summary_line_ids",
    )

    current_order_id = fields.Many2one(
        comodel_name="joint.buying.purchase.order", compute="_compute_current_order_id"
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

    @api.depends("order_ids.amount_untaxed")
    def _compute_amount(self):
        for grouped_order in self:
            grouped_order.amount_untaxed = sum(
                grouped_order.mapped("order_ids.amount_untaxed")
            )

    @api.depends("order_ids.total_weight")
    def _compute_total_weight(self):
        for grouped_order in self:
            grouped_order.total_weight = sum(
                grouped_order.mapped("order_ids.total_weight")
            )

    # On the Fly Compute Section
    def _compute_summary_line_ids(self):
        def _get_keys(line):
            return tuple(
                [
                    line.product_id.id,
                    line.product_uom_id.id,
                    line.product_weight,
                    line.product_uom_package_id.id,
                    line.price_unit,
                ]
            )

        for grouped_order in self:
            res = {}
            lines = grouped_order.mapped("order_ids.line_ids").filtered(lambda x: x.qty)
            for line in lines:
                key = _get_keys(line)
                if key not in res:
                    res[key] = {
                        "product_id": line.product_id.id,
                        "product_uom_id": line.product_uom_id.id,
                        "product_weight": line.product_weight,
                        "product_uom_package_id": line.product_uom_package_id.id,
                        "product_uom_package_qty": 0.0,
                        "price_unit": line.price_unit,
                        "product_uom_qty": 0.0,
                        "amount_untaxed": 0.0,
                    }
                res[key].update(
                    {
                        "product_uom_package_qty": res[key]["product_uom_package_qty"]
                        + line.product_uom_package_qty,
                        "product_uom_qty": res[key]["product_uom_qty"] + line.qty,
                        "amount_untaxed": res[key]["amount_untaxed"]
                        + line.amount_untaxed,
                    }
                )
            grouped_order.summary_line_ids = [(0, 0, v) for k, v in res.items()]

    def _compute_current_order_id(self):
        for grouped_order in self:
            grouped_order.current_order_id = grouped_order.order_ids.filtered(
                lambda x: x.is_my_purchase
            )

    # Overload Section
    def create(self, vals):
        if datetime.combine(vals["start_date"], time(0, 0)) > datetime.now():
            vals.update({"state": "futur"})
        elif vals["end_date"] > datetime.now():
            vals.update({"state": "in_progress"})
        else:
            raise ValidationError(
                _("You can not create a closed Grouped Purchase order")
            )
        return super().create(vals)

    @api.multi
    @api.returns("mail.message", lambda value: value.id)
    def message_post(self, **kwargs):
        if self.env.context.get("mark_as_sent"):
            self.write({"is_mail_sent": True})
        return super(
            JointBuyingPurchaseOrderGrouped,
            self.with_context(mail_post_autofollow=True),
        ).message_post(**kwargs)

    # Custom Section
    @api.model
    def cron_check_state(self):
        pass

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
        minimum_amount=False,
        minimum_unit_amount=False,
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
            "minimum_amount": minimum_amount,
            "minimum_unit_amount": minimum_unit_amount,
            "order_ids": [],
        }
        if not customers:
            customers = supplier.mapped(
                "joint_buying_subscribed_company_ids.joint_buying_partner_id"
            )
        for customer in customers:
            vals["order_ids"].append(
                (0, 0, Order._prepare_order_vals(supplier, customer))
            )
        return vals

    @api.multi
    def action_send_email_for_supplier(self):
        self.ensure_one()
        IrModelData = self.env["ir.model.data"]
        template_id = IrModelData.get_object_reference(
            "joint_buying_product", "email_template_purchase_order_grouped_for_supplier"
        )[1]
        compose_form_id = IrModelData.get_object_reference(
            "mail", "email_compose_message_wizard_form"
        )[1]
        ctx = dict(self.env.context) or {}
        ctx.update(
            {
                "model_description": _("Grouped Purchase Order"),
                "default_model": "joint.buying.purchase.order.grouped",
                "default_res_id": self.ids[0],
                "default_use_template": True,
                "default_template_id": template_id,
                "default_composition_mode": "comment",
                "force_email": True,
                "mark_as_sent": True,
            }
        )

        return {
            "name": _("Compose Email"),
            "type": "ir.actions.act_window",
            "view_type": "form",
            "view_mode": "form",
            "res_model": "mail.compose.message",
            "views": [(compose_form_id, "form")],
            "view_id": compose_form_id,
            "target": "new",
            "context": ctx,
        }

    def action_send_email_for_pivot(self):
        self.ensure_one()
        IrModelData = self.env["ir.model.data"]
        template_id = IrModelData.get_object_reference(
            "joint_buying_product",
            "email_template_purchase_order_grouped_for_pivot_company",
        )[1]
        compose_form_id = IrModelData.get_object_reference(
            "mail", "email_compose_message_wizard_form"
        )[1]
        ctx = dict(self.env.context) or {}
        ctx.update(
            {
                "model_description": _("Grouped Purchase Order"),
                "default_model": "joint.buying.purchase.order.grouped",
                "default_res_id": self.ids[0],
                "default_use_template": True,
                "default_template_id": template_id,
                "default_composition_mode": "comment",
                "force_email": True,
            }
        )
        return {
            "name": _("Compose Email"),
            "type": "ir.actions.act_window",
            "view_type": "form",
            "view_mode": "form",
            "res_model": "mail.compose.message",
            "views": [(compose_form_id, "form")],
            "view_id": compose_form_id,
            "target": "new",
            "context": ctx,
        }

    def see_current_order(self):
        result = self.env.ref(
            "joint_buying_product.action_joint_buying_purchase_order_my_purchase_orders"
        ).read()[0]
        form_view = self.env.ref(
            "joint_buying_product.view_joint_buying_purchase_order_form"
        ).id
        order_ids = self.mapped("current_order_id").ids
        if len(order_ids) == 1:
            result.update({"views": [(form_view, "form")], "res_id": order_ids[0]})
        else:
            result["domain"] = "[('id','in',%s)]" % (order_ids)
        result["context"] = {
            "form_view_initial_mode": "edit",
            "force_detailed_view": "true",
        }
        return result

    def create_current_order(self):
        self.ensure_one()
        Order = self.env["joint.buying.purchase.order"]
        current_customer_partner = self.env.user.company_id.joint_buying_partner_id

        vals = Order._prepare_order_vals(self.supplier_id, current_customer_partner)
        vals.update({"grouped_order_id": self.id})
        Order.create(vals)
        return self.see_current_order()

    def get_mail_url(self):
        self.ensure_one()
        # res = self.env["ir.config_parameter"].sudo().get_param("web.base.url")
        # action = self.env(
        #     "joint_buying_product.action_joint_buying_purchase_order_grouped"
        # )
