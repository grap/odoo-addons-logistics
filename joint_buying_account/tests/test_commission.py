# Copyright (C) 2022 - Today: GRAP (http://www.grap.coop)
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from datetime import timedelta

from odoo.exceptions import Warning as UserError
from odoo.tests.common import TransactionCase


class TestCommission(TransactionCase):
    def setUp(self):
        super().setUp()
        self.company_LOG = self.env.ref("joint_buying_base.company_LOG")
        self.benoit_ronzon = self.env.ref("joint_buying_base.supplier_benoit_ronzon")
        self.CommissionWizard = self.env[
            "joint.buying.invoice.commission.wizard"
        ].with_context(active_ids=self.benoit_ronzon.ids)
        self.AccountInvoice = self.env["account.invoice"]
        self.grouped_orders = self.benoit_ronzon.joint_buying_grouped_order_ids
        self.env.user.company_id = self.company_LOG

    def test_01_create_commission(self):
        # Wizard in a date BEFORE the delivery of grouped orders, should fail
        day_before_deposit = min(
            self.grouped_orders.mapped("deposit_date")
        ) + timedelta(days=-1)
        wizard = self.CommissionWizard.create({"max_deposit_date": day_before_deposit})
        self.assertEqual(len(wizard.line_ids), 1)
        self.assertEqual(wizard.line_ids[0].grouped_order_qty, 0)
        with self.assertRaises(UserError):
            wizard.invoice_commission()

        # Wizard in a date AFTER the delivery of grouped orders, should success
        day_after_deposit = max(self.grouped_orders.mapped("deposit_date"))
        wizard = self.CommissionWizard.create({"max_deposit_date": day_after_deposit})
        self.assertEqual(len(wizard.line_ids), 1)
        self.assertEqual(wizard.line_ids[0].grouped_order_qty, len(self.grouped_orders))
        result = wizard.invoice_commission()

        # Check invoice content
        invoice = self.AccountInvoice.browse(result.get("res_id", False))
        self.assertEqual(len(invoice), 1)
        self.assertEqual(
            set(self.grouped_orders.mapped("invoice_line_id").ids),
            set(invoice.mapped("invoice_line_ids").ids),
        )

        # Try to re create invoices, should fail
        wizard = self.CommissionWizard.create({"max_deposit_date": day_after_deposit})
        with self.assertRaises(UserError):
            wizard.invoice_commission()
