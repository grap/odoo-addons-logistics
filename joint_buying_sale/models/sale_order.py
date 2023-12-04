# Copyright (C) 2022-Today: GRAP (http://www.grap.coop)
# @author: Sylvain LE GAL (https://twitter.com/legalsylvain)
# License AGPL-3.0 or later (http://www.gnu.org/licenses/agpl.html).

from odoo import api, fields, models


class SaleOrder(models.Model):
    _inherit = "sale.order"

    joint_buying_transport_request_id = fields.Many2one(
        comodel_name="joint.buying.transport.request",
        compute="_compute_joint_buying_transport_request_id",
    )

    joint_buying_transport_request_ids = fields.One2many(
        string="Joint Buying Transport Requests",
        comodel_name="joint.buying.transport.request",
        inverse_name="sale_order_id",
        help="Technical field, used to know if the sale order"
        " has a related joint buying transport request created."
        " It can contain only 0 or one transport request.",
    )

    @api.depends("joint_buying_transport_request_ids")
    def _compute_joint_buying_transport_request_id(self):
        for order in self:
            sudo_order = order.sudo()
            order.joint_buying_transport_request_id = (
                sudo_order.joint_buying_transport_request_ids
                and sudo_order.joint_buying_transport_request_ids[0]
                or False
            )
