# Copyright (C) 2021-Today: GRAP (http://www.grap.coop)
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models


class JointBuyingWizardCreateOrder(models.TransientModel):
    _name = "joint.buying.wizard.create.order"
    _description = "Joint Buying Wizard Create Order"

    partner_id = fields.Many2one(
        required=True,
        string="Supplier",
        comodel_name="res.partner",
        domain="[('is_joint_buying', '=', True), ('supplier', '=', True)]",
        default=lambda x: x._default_partner_id(),
    )

    line_ids = fields.One2many(
        comodel_name="joint.buying.wizard.create.order.line",
        required=True,
        default=lambda x: x._default_line_ids(),
        inverse_name="wizard_id",
    )

    def _default_partner_id(self):
        return self.env.context.get("active_id")

    def _default_line_ids(self):
        partner = self.env["res.partner"].browse(self.env.context.get("active_id"))
        line_vals = []
        for partner in partner.mapped(
            "joint_buying_favorite_company_ids.joint_buying_partner_id"
        ):
            line_vals.append((0, 0, {"partner_id": partner.id}))
        return line_vals

    @api.multi
    def create_orders_grouped(self):
        for wizard in self:
            wizard._create_order_grouped()

    def _create_order_grouped(self):
        self.ensure_one()
        pass
