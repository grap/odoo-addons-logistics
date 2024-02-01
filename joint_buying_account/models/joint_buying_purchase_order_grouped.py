# Copyright (C) 2024-Today: GRAP (http://www.grap.coop)
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class JointBuyingPurchaseOrderGrouped(models.Model):
    _inherit = "joint.buying.purchase.order.grouped"

    invoice_line_id = fields.Many2one(comodel_name="account.invoice.line")
