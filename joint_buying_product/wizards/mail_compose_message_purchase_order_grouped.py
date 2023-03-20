# Copyright (C) 2021-Today: GRAP (http://www.grap.coop)
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import _, api, fields, models


class MailComposeMessagePurchaseOrderGrouped(models.TransientModel):
    _name = "mail.compose.message.purchase.order.grouped"
    _inherits = {"mail.compose.message": "composer_id"}
    _description = "Mail Composer for Purchase Order Grouped"

    include_empty_orders = fields.Boolean(
        help="Check this box if you want to send an email to"
        " customers that doesn't ordered any products."
    )

    grouped_order_id = fields.Many2one(
        comodel_name="joint.buying.purchase.order.grouped",
        string="Grouped Order",
        required=True,
        readonly=True,
        ondelete="cascade",
    )

    composer_id = fields.Many2one(
        comodel_name="mail.compose.message",
        string="Composer",
        required=True,
        ondelete="cascade",
    )

    @api.onchange("include_empty_orders")
    def onchange_include_empty_orders(self):
        partner_ids = self._get_default_partner_ids(
            self.grouped_order_id, self.include_empty_orders
        )
        self.partner_ids = [(6, 0, partner_ids)]

    @api.model
    def default_get(self, fields):
        res = super().default_get(fields)
        # Initialize Composer
        composer = self.env["mail.compose.message"].create(
            self._prepare_composer_vals()
        )
        res.update(
            {
                "grouped_order_id": self._context.get("active_ids")[0],
                "composer_id": composer.id,
            }
        )
        return res

    @api.multi
    def action_send_mail(self):
        self.ensure_one()
        self.composer_id.with_context(do_not_send_copy=True).send_mail()
        return {"type": "ir.actions.act_window_close", "infos": "mail_sent"}

    @api.model
    def _prepare_composer_vals(self):
        # Get current grouped order
        grouped_order = self.env["joint.buying.purchase.order.grouped"].browse(
            self._context.get("active_ids")[0]
        )
        return {
            "composition_mode": "comment",
            "partner_ids": self._get_default_partner_ids(grouped_order),
            "subject": _("About the Grouped Order %s (Supplier %s)")
            % (
                grouped_order.name,
                grouped_order.supplier_id.name,
            ),
        }

    def _get_default_partner_ids(self, grouped_order, include_empty_orders=False):
        if not grouped_order:
            return
        if include_empty_orders:
            return grouped_order.mapped("order_ids.customer_id").ids
        return (
            grouped_order.mapped("order_ids")
            .filtered(lambda x: x.amount_untaxed != 0)
            .mapped("customer_id")
            .ids
        )
