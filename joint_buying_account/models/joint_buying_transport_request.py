# Copyright (C) 2024-Today: GRAP (http://www.grap.coop)
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class JointBuyingTransportRequest(models.Model):
    _inherit = "joint.buying.transport.request"

    invoice_line_id = fields.Many2one(
        string="Commission Invoice Line",
        comodel_name="account.invoice.line",
        readonly=True,
    )

    invoice_id = fields.Many2one(
        string="Commission Invoice",
        comodel_name="account.invoice",
        related="invoice_line_id.invoice_id",
    )
