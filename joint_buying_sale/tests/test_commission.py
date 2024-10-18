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
        self.elodie_d = self.env.ref(
            "joint_buying_base.company_ELD"
        ).joint_buying_partner_id
        self.CommissionWizardElodieD = self.env[
            "joint.buying.invoice.commission.wizard"
        ].with_context(active_ids=self.elodie_d.ids)
        self.AccountInvoice = self.env["account.invoice"]
        self.TransportRequest = self.env["joint.buying.transport.request"]
        self.transport_requests = self.TransportRequest.search(
            [("supplier_id", "=", self.elodie_d.id)]
        )
        self.env.user.company_id = self.company_LOG

    def test_01_create_commission_from_transport_requests_sale(self):
        # Wizard in a date BEFORE the availability date of transport Requests, should fail
        day_before_availability = min(
            self.transport_requests.mapped("availability_date")
        ) + timedelta(days=-1)
        wizard = self.CommissionWizardElodieD.create(
            {"max_deposit_date": day_before_availability}
        )
        self.assertEqual(len(wizard.line_ids), 1)
        self.assertEqual(wizard.line_ids[0].grouped_order_qty, 0)
        self.assertEqual(wizard.line_ids[0].transport_request_qty, 0)
        with self.assertRaises(UserError):
            wizard.invoice_commission()

        # Wizard in a date AFTER the delivery of grouped orders, should success
        day_after_availability = max(
            self.transport_requests.mapped("availability_date")
        )
        wizard = self.CommissionWizardElodieD.create(
            {"max_deposit_date": day_after_availability}
        )
        self.assertEqual(len(wizard.line_ids), 1)
        self.assertEqual(wizard.line_ids[0].grouped_order_qty, 0)
        self.assertEqual(
            wizard.line_ids[0].transport_request_qty, len(self.transport_requests)
        )

        result = wizard.invoice_commission()

        # Check invoice content
        invoice = self.AccountInvoice.browse(result.get("res_id", False))
        self.assertEqual(len(invoice), 1)
        self.assertEqual(
            set(self.transport_requests.mapped("invoice_line_id").ids),
            set(invoice.mapped("invoice_line_ids").ids),
        )

        # Try to re create invoices, should fail
        wizard = self.CommissionWizardElodieD.create(
            {"max_deposit_date": day_after_availability}
        )
        with self.assertRaises(UserError):
            wizard.invoice_commission()
