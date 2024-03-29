# Copyright (C) 2017 - Today: GRAP (http://www.grap.coop)
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).
from datetime import datetime, timedelta

from odoo import _, api, fields, models
from odoo.exceptions import ValidationError

from odoo.addons.joint_buying_base.models.res_partner import (
    _JOINT_BUYING_PARTNER_CONTEXT,
)


class JointbuyingInvoiceCommissionWizardLine(models.TransientModel):
    _name = "joint.buying.invoice.commission.wizard.line"
    _description = "Invoice Line Commission Wizard"

    # Columns Section
    wizard_id = fields.Many2one(
        comodel_name="joint.buying.invoice.commission.wizard",
        required=True,
        ondelete="cascade",
    )

    partner_id = fields.Many2one(
        string="Supplier",
        comodel_name="res.partner",
        required=True,
        readonly=True,
        context=_JOINT_BUYING_PARTNER_CONTEXT,
        domain=[("supplier", "=", True)],
    )

    local_partner_id = fields.Many2one(
        string="Local Partner",
        comodel_name="res.partner",
    )

    commission_rate = fields.Float(
        string="Commission Rate",
        related="partner_id.joint_buying_commission_rate",
        readonly=False,
    )

    grouped_order_qty = fields.Integer(
        string="Quantity", compute="_compute_grouped_order_info"
    )

    grouped_order_detail = fields.Text(
        string="Detail", compute="_compute_grouped_order_info"
    )

    @api.depends("wizard_id.max_deposit_date", "partner_id")
    def _compute_grouped_order_info(self):
        for line in self:
            grouped_orders = self._compute_grouped_order_ids_model(
                line.wizard_id.max_deposit_date, line.partner_id
            )
            line.grouped_order_qty = len(grouped_orders)
            all_data = grouped_orders.search_read(
                [("id", "in", grouped_orders.ids)],
                ["name", "deposit_date", "amount_untaxed"],
            )
            line.grouped_order_detail = "\n".join(
                [
                    f"- {x['name']} - {x['deposit_date'].strftime('%m/%d/%Y')}"
                    f" - {x['amount_untaxed']:.2f} €"
                    for x in all_data
                ]
            )

    @api.model
    def _compute_grouped_order_ids_model(self, max_deposit_date, partner):
        max_deposit_date = datetime(
            max_deposit_date.year, max_deposit_date.month, max_deposit_date.day
        ) + timedelta(days=1)
        return self.env["joint.buying.purchase.order.grouped"].search(
            [
                ("supplier_id", "=", partner.id),
                ("invoice_line_id", "=", False),
                ("deposit_date", "<", max_deposit_date),
                ("amount_untaxed", ">", 0.0),
                ("state", "=", "deposited"),
            ],
            order="deposit_date",
        )

    # Prepare Section
    @api.multi
    def _create_invoice(self):
        AccountInvoice = self.env["account.invoice"]
        AccountInvoiceLine = self.env["account.invoice.line"]
        self.ensure_one()
        # Save local supplier
        self.partner_id.set_joint_buying_local_partner_id(self.local_partner_id)

        invoice_vals = self._prepare_invoice()
        invoice = AccountInvoice.create(invoice_vals)

        for grouped_order in self._compute_grouped_order_ids_model(
            self.wizard_id.max_deposit_date, self.partner_id
        ):
            invoice_line_vals = self._prepare_invoice_line(invoice, grouped_order)
            if not invoice_line_vals:
                continue
            line = AccountInvoiceLine.create(invoice_line_vals)

            grouped_order.invoice_line_id = line.id

            # We try to compute correctly taxes, check vat included, etc...
            price_unit = line.price_unit
            line_name = line.name
            line._onchange_product_id()
            taxes = line.invoice_line_tax_ids
            if taxes:
                if len(taxes) != 1:
                    raise ValidationError(
                        _(
                            "Incorrect fiscal settings block the possibility"
                            " to generate commission invoices : Too many taxes %s"
                        )
                        % (", ".join(taxes.mapped("name")))
                    )

                tax = taxes[0]
                if tax.amount_type != "percent":
                    raise ValidationError(
                        _(
                            "Incorrect fiscal settings block the possibility"
                            " to generate commission invoices : Incorrect tax type"
                            " on the tax %s"
                        )
                        % (tax.name)
                    )

                # Rewrite name and price_unit, because on change erased correct values
                if tax.price_include:
                    line.price_unit = price_unit * (100 + tax.amount) / 100
                else:
                    line.price_unit = price_unit
            else:
                line.price_unit = price_unit

            line.name = line_name
        return invoice

    @api.multi
    def _prepare_invoice(self):
        self.ensure_one()
        return {
            "partner_id": self.local_partner_id.id,
            "date_invoice": self.wizard_id.max_deposit_date,
            "type": "out_invoice",
        }

    @api.multi
    def _prepare_invoice_line(self, invoice, grouped_order):
        self.ensure_one()

        valid_orders = grouped_order.order_ids.filtered(
            lambda x: x.customer_id != x.grouped_order_id.deposit_partner_id
            and x.amount_untaxed != 0.0
        )
        deposit_order = grouped_order.order_ids.filtered(
            lambda x: x.customer_id == x.grouped_order_id.deposit_partner_id
            and x.amount_untaxed != 0.0
        )
        base = sum(valid_orders.mapped("amount_untaxed"))
        description = _(
            "Commission on %s deposited on %s\n"
            "- Ordered Amount : %.2f €\n"
            "- %d Customers: %s\n"
            "- Rate : %.2f %%"
        ) % (
            grouped_order.name,
            grouped_order.deposit_date.strftime("%m/%d/%Y"),
            base,
            len(valid_orders),
            "-".join(valid_orders.mapped("customer_id.joint_buying_code")),
            self.partner_id.joint_buying_commission_rate,
        )
        if deposit_order:
            description += _("\n" "- Non-commissioned sale: %s ; %.2f €") % (
                deposit_order.customer_id.joint_buying_code,
                deposit_order.amount_untaxed,
            )
        product = self.local_partner_id.company_id.joint_buying_commission_product_id
        return {
            "invoice_id": invoice.id,
            "product_id": product.id,
            "account_id": product.property_account_income_id.id,
            "quantity": 1,
            "name": description,
            "price_unit": base * self.partner_id.joint_buying_commission_rate / 100,
        }

    def _check_values(self):
        for line in self.filtered(lambda x: not x.local_partner_id):
            raise ValidationError(
                _("You should define a local partner for the supplier %s.")
                % line.partner_id.name
            )
