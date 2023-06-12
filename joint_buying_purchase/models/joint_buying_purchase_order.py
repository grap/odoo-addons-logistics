# Copyright (C) 2023-Today: GRAP (http://www.grap.coop)
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class JointBuyingPurchaseOrder(models.Model):
    _inherit = "joint.buying.purchase.order"

    purchase_order_id = fields.Many2one(
        comodel_name="purchase.order",
        help="Related purchase order in the local database of the"
        " customer for the related supplier.",
    )
