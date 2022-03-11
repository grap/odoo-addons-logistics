# Copyright (C) 2021-Today: GRAP (http://www.grap.coop)
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class JointBuyingWizardUpdateOrderGrouped(models.TransientModel):
    _name = "joint.buying.wizard.update.order.grouped"
    _description = "Joint Buying Wizard Update Order Grouped"

    line_ids = fields.Many2many(
        comodel_name="joint.buying.purchase.order.line",
        default=lambda x: x._default_line_ids(),
        relation="joint_buying_wizard_update_order_grouped_line_rel",
    )

    def _default_line_ids(self):
        grouped_order = self.env["joint.buying.purchase.order.grouped"].browse(
            self.env.context.get("active_id")
        )
        ordered_lines = grouped_order.mapped("order_ids.line_ids").filtered(
            lambda x: x.qty > 0
        )
        ordered_product_ids = ordered_lines.mapped("product_id").ids
        not_null_orders = grouped_order.mapped("order_ids").filtered(
            lambda x: x.amount_untaxed > 0
        )
        return not_null_orders.mapped("line_ids").filtered(
            lambda x: x.product_id.id in ordered_product_ids
        )

    def save_close(self):
        return
