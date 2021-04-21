# Copyright (C) 2021-Today: GRAP (http://www.grap.coop)
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models


class JointBuyingWizardCreateOrder(models.TransientModel):
    _name = "joint.buying.wizard.create.order"
    _description = "Joint Buying Wizard Create Order"

    supplier_id = fields.Many2one(
        required=True,
        string="Supplier",
        comodel_name="res.partner",
        domain="[('is_joint_buying', '=', True), ('supplier', '=', True)]",
        default=lambda x: x._default_partner_id(),
    )

    start_date = fields.Date(
        string="Start Date", required=True, default=lambda x: x._default_start_date()
    )

    end_date = fields.Datetime(
        string="End Date", required=True, default=lambda x: x._default_end_date()
    )

    deposit_date = fields.Date(
        string="Deposit Date",
        required=True,
        default=lambda x: x._default_deposit_date(),
    )

    line_ids = fields.One2many(
        comodel_name="joint.buying.wizard.create.order.line",
        required=True,
        default=lambda x: x._default_line_ids(),
        inverse_name="wizard_id",
    )

    def _default_partner_id(self):
        return self.env.context.get("active_id")

    def _default_start_date(self):
        partner = self.env["res.partner"].browse(self.env.context.get("active_id"))
        if partner.joint_buying_frequency:
            return partner.joint_buying_next_start_date

    def _default_end_date(self):
        partner = self.env["res.partner"].browse(self.env.context.get("active_id"))
        if partner.joint_buying_frequency:
            return partner.joint_buying_next_end_date

    def _default_deposit_date(self):
        partner = self.env["res.partner"].browse(self.env.context.get("active_id"))
        if partner.joint_buying_frequency:
            return partner.joint_buying_next_deposit_date

    def _default_line_ids(self):
        partner = self.env["res.partner"].browse(self.env.context.get("active_id"))
        line_vals = []
        for partner in partner.mapped(
            "joint_buying_favorite_company_ids.joint_buying_partner_id"
        ):
            line_vals.append((0, 0, {"customer_id": partner.id}))
        return line_vals

    @api.multi
    def create_orders_grouped(self):
        self.ensure_one()
        OrderGrouped = self.env["joint.buying.purchase.order.grouped"]
        group_order = OrderGrouped.create(
            OrderGrouped._prepare_order_grouped_vals(
                self.supplier_id, self.mapped("line_ids.customer_id")
            )
        )

        form_view = self.env.ref(
            "joint_buying_product.view_joint_buying_purchase_order_grouped_form"
        )

        action = self.env.ref(
            "joint_buying_product.action_joint_buying_purchase_order_grouped"
        ).read()[0]
        action.update({"res_id": group_order.id, "views": [(form_view.id, "form")]})
        return action
