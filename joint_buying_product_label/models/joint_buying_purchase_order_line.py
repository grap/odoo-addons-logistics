# Copyright (C) 2023-Today: GRAP (http://www.grap.coop)
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class JointBuyingPurchaseOrderLine(models.Model):
    _inherit = "joint.buying.purchase.order.line"

    label_ids = fields.Many2many(
        comodel_name="product.label",
        related="product_id.label_ids",
        store=False,
    )
