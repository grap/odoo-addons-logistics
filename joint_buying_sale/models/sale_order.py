# Copyright (C) 2022-Today: GRAP (http://www.grap.coop)
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import fields, models


class SaleOrder(models.Model):
    _inherit = "sale.order"

    joint_buying_has_transport_request = fields.Boolean(
        compute="_compute_joint_buying_has_transport_request",
        store=False,
        help="Technical field, used to know if the sale order"
        " has a related joint buying transport request created.",
    )

    joint_buying_transport_request_ids = fields.One2many(
        comodel_name="joint.buying.transport.request",
        inverse_name="sale_order_id",
        help="Technical field, used to know if the sale order"
        " has a related joint buying transport request created."
        " It can contain only 0 or one transport request.",
    )

    def _compute_joint_buying_has_transport_request(self):
        for order in self:
            order.joint_buying_has_transport_request = len(
                order.joint_buying_transport_request_ids
            )
