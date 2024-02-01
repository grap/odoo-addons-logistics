# Copyright (C) 2017 - Today: GRAP (http://www.grap.coop)
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from datetime import timedelta

from odoo import _, api, fields, models
from odoo.exceptions import Warning as UserError


class JointBuyingInvoiceCommissionWizard(models.TransientModel):
    _name = "joint.buying.invoice.commission.wizard"
    _description = "Joint Buying Invoice Commission Wizard"

    # Columns Section
    max_deposit_date = fields.Date(
        string="Max Deposit Date",
        required=True,
        default=lambda x: x._default_max_deposit_date(),
        help="The commission will be computed for the grouped order"
        " deposited by the suppliers until this date included.",
    )

    line_ids = fields.One2many(
        comodel_name="joint.buying.invoice.commission.wizard.line",
        inverse_name="wizard_id",
        default=lambda x: x._default_line_ids(),
    )

    # Default values Section
    def _default_line_ids(self):
        res = []
        ResPartner = self.env["res.partner"]
        WizardLine = self.env["joint.buying.invoice.commission.wizard.line"]
        partners = ResPartner.browse(self.env.context.get("active_ids", []))
        for partner in partners:
            local_partner = partner.get_joint_buying_local_partner_id()
            line_vals = {
                "partner_id": partner.id,
                "local_partner_id": local_partner and local_partner.id,
                "commission_rate": partner.joint_buying_commission_rate,
                "grouped_order_qty": len(
                    WizardLine._compute_grouped_order_ids_model(
                        self._default_max_deposit_date(), partner
                    )
                ),
            }
            res.append([0, 0, line_vals])
        return res

    def _default_max_deposit_date(self):
        today = fields.date.today()
        return fields.date(today.year, today.month, 1) - timedelta(days=1)

    # Action Section
    @api.multi
    def invoice_commission(self):
        self.ensure_one()
        self._check_values()
        invoices = self.env["account.invoice"]

        for wizard_line in self.line_ids.filtered(lambda x: x.grouped_order_qty):
            invoice = wizard_line._create_invoice()
            invoices |= invoice

        if not invoices:
            raise UserError(
                _(
                    "No Grouped Order to invoice for the"
                    " selected suppliers and the selected date."
                )
            )

        # Recompute Taxes
        invoices.compute_taxes()

        action = self.env.ref("account.action_invoice_tree1").read()[0]

        if len(invoices) > 1:
            action["domain"] = (
                "[('id', 'in', [" + ",".join(map(str, invoices.ids)) + "])]"
            )
        else:
            form_view = [(self.env.ref("account.invoice_form").id, "form")]
            action["views"] = form_view + [
                (state, view)
                for state, view in action.get("views", [])
                if view != "form"
            ]
            action["res_id"] = invoices.ids[0]

        return action

    def _check_values(self):
        self.mapped("line_ids")._check_values()
