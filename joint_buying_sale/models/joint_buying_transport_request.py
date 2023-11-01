# Copyright (C) 2022-Today: GRAP (http://www.grap.coop)
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class JointBuyingTransportRequest(models.Model):
    _inherit = "joint.buying.transport.request"

    sale_order_id = fields.Many2one(
        comodel_name="sale.order",
        readonly=True,
        help="Sale order in the local database of the"
        " company that requires transport.",
    )
