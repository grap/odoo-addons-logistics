# Copyright (C) 2021-Today: GRAP (http://www.grap.coop)
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models


class JointBuyingWizardUpdateOrderGrouped(models.TransientModel):
    _name = "joint.buying.wizard.update.order.grouped"
    _description = "Joint Buying Wizard Update Order Grouped"

    show_all_orders = fields.Boolean(help="Include empty orders.")

    show_all_products = fields.Boolean(
        help="Include products that have not been ordered."
    )

    line_ids = fields.Many2many(
        comodel_name="joint.buying.purchase.order.line",
        default=lambda x: x._default_line_ids(),
        relation="joint_buying_wizard_update_order_grouped_line_rel",
    )

    @api.onchange("show_all_products", "show_all_orders")
    def onchange_show_settings(self):
        self.ensure_one()
        self.line_ids = self._default_line_ids()

    def _default_line_ids(self):
        grouped_order = self.env["joint.buying.purchase.order.grouped"].browse(
            self.env.context.get("active_id")
        )
        # Compute Ordered Products
        ordered_product_ids = (
            grouped_order.mapped("order_ids.line_ids")
            .filtered(lambda x: x.qty > 0)
            .mapped("product_id")
            .ids
        )

        # Compute Not Null Orders
        not_null_order_ids = (
            grouped_order.mapped("order_ids")
            .filtered(lambda x: x.amount_untaxed > 0)
            .ids
        )

        return grouped_order.mapped("order_ids.line_ids").filtered(
            lambda x: (self.show_all_orders or x.order_id.id in not_null_order_ids)
            and (self.show_all_products or x.product_id.id in ordered_product_ids)
        )

    def save_close(self):
        return
